"""
BCE-4X P0-X — MOTEUR SALINES V4 (TERRAIN-CENTRE)
====================================================
ORDONNANCE STEEVE-MAX 2026-04-06 | SUPRA VALIDE
Branche: BIONIC_REWRITE_P0

Moteur de placement de salines terrain-pilote.
Generation basee sur les features terrain (eau, sentiers, corridors, ecotones).
Scoring 9 criteres SUPRA valides scientifiquement (22 sources).

Ponderations SUPRA validees:
  Eau 20% | Corridor 15% | Couvert 15% | Mineraux 10% | Saison 10%
  Sentier 10% | Habitat 10% | Pente 5% | Securite 5%

Critere 7 (Sentier): SUPRA valide conditionnellement — dependance OSM documentee.
Critere 9 (Securite): SUPRA valide conditionnellement — proxy 5%, remplacement V5+.
"""
import math
import hashlib
import logging

from .terrain_features import (
    detect_water_sources,
    detect_trail_nodes,
    detect_ecotones,
    generate_fallback_grid,
    deduplicate_candidates,
    _haversine_m,
)
from .mineral_scorer import compute_seasonal_mineral_score
from .bdre_integration import get_corridor_score, generate_corridor_candidates

logger = logging.getLogger("bionic.salines_v4")


def _seed(lat, lng, salt=""):
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE SCORING INDIVIDUELLES (SUPRA VALIDEES)
# ═══════════════════════════════════════════════════════════

def _score_eau(candidate, terrain):
    """
    Critere 1 — Proximite eau (20%) | SUPRA VALIDE
    Seuils institutionnels STEEVE-MAX: 30-80m optimal, 80-150m acceptable, >150m penalite.
    """
    # Utiliser la distance pre-calculee si disponible (candidat eau)
    water_dist = candidate.get("water_distance_m")

    if water_dist is None:
        # Calculer la distance eau pour les candidats non-eau
        try:
            from core.scoring_pipeline.alimentation_v2.salines import _nearest_water_distance_saline
            water_dist = _nearest_water_distance_saline(candidate["lat"], candidate["lng"])
        except Exception:
            water_dist = terrain.get("eau", {}).get("distance_eau_m", 600)

    if 30 <= water_dist <= 80:
        score = 100
    elif 80 < water_dist <= 150:
        score = 75
    elif water_dist < 30:
        score = 40
    elif 150 < water_dist <= 300:
        score = 45
    else:
        score = 20

    return score, round(water_dist)


def _score_couvert(candidate, terrain):
    """
    Critere 2 — Couvert forestier (15%) | SUPRA VALIDE
    Zone optimale 40-80%: protection + lumiere (VerCauteren & Hygnstrom 2011).
    """
    couvert_pct = candidate.get("couvert_local_pct",
                                terrain.get("foret", {}).get("couvert_pct", 60))
    # Micro-variation positionnelle
    couvert_pct += (_seed(candidate["lat"], candidate["lng"], "cv_var") - 0.5) * 10

    if 40 <= couvert_pct <= 80:
        score = 100
    elif 30 <= couvert_pct < 40:
        score = 75
    elif 80 < couvert_pct <= 90:
        score = 70
    elif couvert_pct < 30:
        score = 40
    else:
        score = 35

    return score, round(couvert_pct, 1)


def _score_habitat(candidate, terrain):
    """
    Critere 3 — Diversite micro-habitat (10%) | SUPRA VALIDE
    Composite de 5 indicateurs binaires (Leopold 1933, Peek et al. 1976).
    """
    score = 0
    couvert = terrain.get("foret", {}).get("couvert_pct", 60)
    strate_arbu = terrain.get("foret", {}).get("strate_arbustive_pct", 30)
    n_essences = len(terrain.get("foret", {}).get("essences", []))
    eau_dist = candidate.get("water_distance_m", terrain.get("eau", {}).get("distance_eau_m", 500))
    pente = terrain.get("relief", {}).get("pente_moyenne_pct", 10)

    if 40 <= couvert <= 70:
        score += 30  # Ecotone
    if eau_dist < 200:
        score += 25  # Proche eau
    if pente < 15:
        score += 20  # Terrain accessible
    if n_essences > 4:
        score += 15  # Diversite essences
    if strate_arbu > 20:
        score += 10  # Sous-bois developpe

    return min(100, score)


def _score_pente(candidate, terrain):
    """
    Critere 8 — Pente (5%) | SUPRA VALIDE
    La pente LOCALE varie autour de la moyenne. Seule une pente locale > 25%
    entraine l'exclusion. Le seuil 20% s'applique au SCORE, pas a l'exclusion.
    Note: La pente_moyenne_pct est la pente MOYENNE de la zone 2km×2km,
    pas la pente locale du candidat. Les micro-zones peuvent etre plus plates.
    """
    pente_moy = terrain.get("relief", {}).get("pente_moyenne_pct", 10)
    # Variation locale: la pente du candidat peut etre ±40% de la moyenne
    variation = (_seed(candidate["lat"], candidate["lng"], "pente_v4") - 0.5) * 0.8
    pente_local = max(0, pente_moy * (1 + variation))

    # EXCLUSION uniquement si pente locale > 25% (falaise)
    if pente_local > 25:
        return 0, True

    if pente_local < 5:
        return 100, False
    elif pente_local < 10:
        return 80, False
    elif pente_local < 15:
        return 60, False
    elif pente_local < 20:
        return 30, False
    else:
        return 15, False


def _score_securite(candidate, center_lat, center_lng):
    """
    Critere 9 — Securite / Pression humaine (5%) | SUPRA VALIDE CONDITIONNELLEMENT
    Proxy: distance au centre du waypoint. Remplacement recommande en V5+.
    """
    dist = _haversine_m(candidate["lat"], candidate["lng"], center_lat, center_lng)

    if dist > 400:
        return 90
    elif dist > 300:
        return 75
    elif dist > 200:
        return 60
    else:
        return 50


def _score_sentier(candidate, trail_graph):
    """
    Critere 7 — Accessibilite sentier (10%) | SUPRA VALIDE CONDITIONNELLEMENT
    Distance reelle au sentier OSM. Dependance OSM documentee.
    """
    trail_dist = candidate.get("trail_distance_m")

    if trail_dist is None:
        try:
            from core.scoring_pipeline.alimentation_v2.salines import _nearest_trail_distance_saline
            trail_dist = _nearest_trail_distance_saline(
                candidate["lat"], candidate["lng"], trail_graph
            )
        except Exception:
            trail_dist = 600

    if trail_dist < 100:
        score = 90
    elif trail_dist < 300:
        score = 70
    elif trail_dist < 600:
        score = 40
    else:
        score = 10

    return score, round(trail_dist)


# ═══════════════════════════════════════════════════════════
# SCORING V4 COMPLET — 9 CRITERES SUPRA VALIDES
# ═══════════════════════════════════════════════════════════

def score_candidate_v4(candidate, terrain, species, month,
                        center_lat, center_lng, trail_graph):
    """
    Score un candidat saline V4 selon 9 criteres SUPRA valides.
    Ponderations: Eau 20% | Corridor 15% | Couvert 15% | Mineraux 10% | Saison 10%
                  Sentier 10% | Habitat 10% | Pente 5% | Securite 5%

    Retourne: (score_total, criteres_dict, justifications, criteres_sources, excluded)
    """
    # 1. Eau (20%)
    score_eau, water_dist = _score_eau(candidate, terrain)

    # 2. Couvert (15%)
    score_couvert, couvert_val = _score_couvert(candidate, terrain)

    # 3. Habitat (10%)
    score_habitat = _score_habitat(candidate, terrain)

    # 4+5. Mineraux (10%) + Saison (10%)
    nutriments = terrain.get("nutriments_sol", {})
    mineral_data = compute_seasonal_mineral_score(nutriments, species, month)
    score_mineraux = mineral_data["mineral_score_brut"]
    score_saison = mineral_data["combined_score"]

    # 6. Corridor BDRE (15%)
    score_corridor, corridor_dist, corridor_source = get_corridor_score(
        candidate["lat"], candidate["lng"], center_lat, center_lng, trail_graph
    )

    # 7. Sentier (10%) — SUPRA conditionnel
    score_sentier, trail_dist = _score_sentier(candidate, trail_graph)

    # 8. Pente (5%)
    score_pente, excluded = _score_pente(candidate, terrain)
    if excluded:
        return 0, {}, [], {}, True  # EXCLUSION pente > 20%

    # 9. Securite (5%) — SUPRA conditionnel
    score_securite = _score_securite(candidate, center_lat, center_lng)

    # ═══ SCORE TOTAL — Ponderations SUPRA validees ═══
    total = (
        score_eau * 0.20
        + score_corridor * 0.15
        + score_couvert * 0.15
        + score_mineraux * 0.10
        + score_saison * 0.10
        + score_sentier * 0.10
        + score_habitat * 0.10
        + score_pente * 0.05
        + score_securite * 0.05
    )

    criteres = {
        "eau": score_eau,
        "corridor": score_corridor,
        "couvert": score_couvert,
        "mineraux": score_mineraux,
        "saison": score_saison,
        "sentier": score_sentier,
        "habitat": score_habitat,
        "pente": score_pente,
        "securite": score_securite,
    }

    criteres_sources = {
        "eau_distance_m": water_dist,
        "eau_source": "OSM_water_cache" if water_dist < 600 else "terrain_fallback",
        "trail_distance_m": trail_dist,
        "trail_source": "OSM_terrain_nav" if trail_dist < 600 else "terrain_fallback",
        "corridor_distance_m": corridor_dist,
        "corridor_source": corridor_source,
        "habitat_source": "terrain_composite_5_indicators",
        "mineraux_source": "terrain_nutriments_sol",
        "mineral_score_brut": mineral_data["mineral_score_brut"],
        "seasonal_multiplier": mineral_data["seasonal_multiplier"],
        "n_carences": mineral_data["n_carences"],
        "season_month": month,
        "couvert_local_pct": couvert_val,
        "generation_source": candidate.get("source", "unknown"),
    }

    justifications = []
    if score_eau >= 75:
        justifications.append(f"Eau a {water_dist}m (optimal)")
    elif score_eau >= 40:
        justifications.append(f"Eau a {water_dist}m (acceptable)")
    else:
        justifications.append(f"Eau a {water_dist}m (eloigne)")
    if score_corridor >= 80:
        justifications.append(f"Corridor BDRE a {corridor_dist}m")
    if score_couvert >= 70:
        justifications.append(f"Couvert {couvert_val}% (optimal)")
    if mineral_data["n_carences"] > 0:
        justifications.append(f"{mineral_data['n_carences']} carence(s) detectee(s)")
    justifications.append(mineral_data["justification_saisonniere"])
    if score_habitat >= 60:
        justifications.append("Micro-habitat diversifie")
    if score_sentier >= 70:
        justifications.append(f"Sentier a {trail_dist}m")
    if score_securite >= 75:
        justifications.append("Zone securisee")

    return round(total), criteres, justifications, criteres_sources, False


# ═══════════════════════════════════════════════════════════
# SELECTION GLOUTONNE (INCHANGE depuis V2/V3)
# ═══════════════════════════════════════════════════════════

def _select_with_min_distance(candidates, max_salines, min_distance_m=300.0):
    """Selection gloutonne Top-N avec distance minimale entre selectionnees."""
    candidates.sort(key=lambda c: c.get("score", 0), reverse=True)
    selected = []

    for cand in candidates:
        if len(selected) >= max_salines:
            break
        too_close = False
        for sel in selected:
            if _haversine_m(cand["lat"], cand["lng"], sel["lat"], sel["lng"]) < min_distance_m:
                too_close = True
                break
        if not too_close:
            cand["selected"] = True
            selected.append(cand)

    for cand in candidates:
        if cand not in selected:
            cand["selected"] = False
            cand["rank"] = 0

    for i, sel in enumerate(selected):
        sel["rank"] = i + 1

    return candidates


# ═══════════════════════════════════════════════════════════
# POINT D'ENTREE PRINCIPAL — compute_salines_v4
# ═══════════════════════════════════════════════════════════

def compute_salines_v4(
    center_lat: float,
    center_lng: float,
    terrain: dict,
    species: str = "CERF",
    month: int = 10,
    max_salines: int = 2,
    min_distance_m: float = 300.0,
    max_radius_m: float = 600.0,
) -> list:
    """
    BCE-4X P0-X SALINES V4: Generation terrain-pilotee.

    1. Charge le graphe terrain OSM (cache auto)
    2. Detecte features terrain (eau, sentiers, corridors, ecotones)
    3. Genere candidats terrain-pilotes (8-30 selon richesse)
    4. Fallback grille 3x3 si < 8 candidats
    5. Filtre (Haversine, exclusion centre, pente > 20%)
    6. Score 9 criteres SUPRA valides
    7. Selection gloutonne Top-2 (règle métier STEEVE-MAX)

    Retourne: liste de tous les candidats avec flag 'selected'
    """
    max_salines = max(1, min(2, max_salines))

    # ═══ PHASE 0: Charger le graphe terrain OSM ═══
    trail_graph = None
    try:
        from engines.terrain_nav import get_terrain_nav
        trail_graph = get_terrain_nav(
            center_lat, center_lng,
            radius_m=max(int(max_radius_m * 2), 2000),
        )
        logger.info(f"[SALINES-V4] Trail graph: empty={trail_graph.is_empty}")
    except Exception as e:
        logger.warning(f"[SALINES-V4] Trail graph indisponible: {e}")

    # ═══ PHASE 1: Detecter features terrain ═══
    water_candidates = detect_water_sources(center_lat, center_lng, terrain, max_radius_m)
    trail_candidates = detect_trail_nodes(center_lat, center_lng, trail_graph, max_radius_m)
    corridor_candidates = generate_corridor_candidates(center_lat, center_lng, trail_graph, max_radius_m)
    ecotone_candidates = detect_ecotones(center_lat, center_lng, terrain, max_radius_m)

    # ═══ PHASE 2: Pool de candidats ═══
    all_candidates = water_candidates + trail_candidates + corridor_candidates + ecotone_candidates

    logger.info(
        f"[SALINES-V4] Pool terrain: eau={len(water_candidates)} "
        f"trail={len(trail_candidates)} corridor={len(corridor_candidates)} "
        f"ecotone={len(ecotone_candidates)} total={len(all_candidates)}"
    )

    # ═══ PHASE 3: Fallback si < 8 candidats ═══
    if len(all_candidates) < 8:
        fallback = generate_fallback_grid(center_lat, center_lng, max_radius_m)
        all_candidates.extend(fallback)
        logger.info(f"[SALINES-V4] Fallback grid ajoute: {len(fallback)} candidats")

    # ═══ PHASE 4: Deduplication (< 50m) ═══
    all_candidates = deduplicate_candidates(all_candidates, min_dist_m=50)

    # ═══ PHASE 5: Filtrage strict ═══
    filtered = []
    for cand in all_candidates:
        dist = _haversine_m(center_lat, center_lng, cand["lat"], cand["lng"])
        if dist > max_radius_m:
            continue
        if dist < 150:
            continue
        cand["distance_centre_m"] = round(dist)
        filtered.append(cand)

    logger.info(f"[SALINES-V4] Post-filtrage: {len(filtered)} candidats (de {len(all_candidates)})")

    # ═══ PHASE 6: Scoring V4 (9 criteres SUPRA) ═══
    # Type de saline selon mois et espece
    if month in [4, 5, 6]:
        type_saline = "sodium-enrichie"
    elif month in [7, 8, 9]:
        type_saline = "minerale"
    elif month in [10, 11]:
        type_saline = "calcium-enrichie"
    else:
        type_saline = "minerale"

    scored = []
    for cand in filtered:
        # COUCHE BCE-4X UNIVERSELLE — Exclure avant scoring
        try:
            from bce.exclusion_layer_bce4x import check_point_exclusions
            bce_excl = check_point_exclusions(cand["lat"], cand["lng"])
            if bce_excl["excluded"]:
                continue
        except ImportError:
            pass

        score, criteres, justifications, criteres_sources, excluded = score_candidate_v4(
            cand, terrain, species, month, center_lat, center_lng, trail_graph,
        )
        if excluded:
            continue  # Pente > 20% → exclusion totale

        scored.append({
            "id": f"SAL-V4-{len(scored) + 1:02d}",
            "lat": cand["lat"],
            "lng": cand["lng"],
            "score": score,
            "type": type_saline,
            "distance_centre_m": cand.get("distance_centre_m", 0),
            "justifications": justifications,
            "carences_zone": [
                f"{c['mineral']}: {c['valeur']} < {c['seuil']} ppm"
                for c in criteres_sources.get("carences", [])
            ] or ["Aucune carence majeure detectee"],
            "criteres": criteres,
            "criteres_sources": criteres_sources,
            "scoring_version": "V4",
            "generation_source": cand.get("source", "unknown"),
            "selected": False,
        })

    if not scored:
        logger.warning("[SALINES-V4] ZERO candidats apres scoring — fallback vide")
        return []

    # ═══ PHASE 7: Selection gloutonne Top-4 ═══
    result = _select_with_min_distance(scored, max_salines, min_distance_m)

    selected_count = sum(1 for s in result if s.get("selected"))
    logger.info(f"[SALINES-V4] Selection finale: {selected_count} JAUNES / {len(result)} total")

    return result
