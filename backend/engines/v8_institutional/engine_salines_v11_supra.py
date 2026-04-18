"""
ENGINE SALINES-V11-SUPRA — ACTIVATION TOTALE
================================================================
Axes : biologique, terrain, nutritionnel (600m profile fin), reseau,
       accoutumance, interdictions.

Entree : liste de salines (sortie de compute_salines_omega), terrain_v10,
         corridors_v10, affuts_v10, contamination_v10, species, month.

Sortie : meme liste enrichie avec:
  - score_bio_species (dict par espece)
  - score_bio_global (0-100)
  - score_terrain (0-100)
  - score_reseau (0-100)
  - score_nutrition (0-100)
  - score_accoutumance (0-100)
  - interdit (bool), motif_interdiction
  - nutrient_target_profile (dict familles a renforcer)
  - score_global_v11 (0-100, ponderation institutionnelle)
  - statut_institutionnel (conforme / a_optimiser / non_conforme / interdite)
  - recommandations (list[str])
  - source: "SALINES-V11-SUPRA"
"""
from __future__ import annotations
import math
from typing import Any

# ═══ CONSTANTES ESPECES ═══
SPECIES_PROFILES = {
    "cerf": {
        "rayon_attraction_m": 650,
        "fenetres_saisonnieres": {
            "hiver": [12, 1, 2], "pre_rut": [9, 10], "rut": [10, 11],
            "post_rut": [12], "printemps": [3, 4, 5], "ete": [6, 7, 8],
        },
        "accoutumance_days": 45,
        "rythmes_activite_heures": [(5, 9), (17, 21)],
    },
    "orignal": {
        "rayon_attraction_m": 900,
        "fenetres_saisonnieres": {
            "hiver": [12, 1, 2], "pre_rut": [8, 9], "rut": [9, 10],
            "post_rut": [11], "printemps": [4, 5, 6], "ete": [6, 7, 8],
        },
        "accoutumance_days": 60,
        "rythmes_activite_heures": [(4, 9), (18, 22)],
    },
    "wapiti": {
        "rayon_attraction_m": 1100,
        "fenetres_saisonnieres": {
            "hiver": [12, 1, 2], "pre_rut": [8, 9], "rut": [9, 10],
            "post_rut": [11], "printemps": [3, 4, 5], "ete": [6, 7, 8],
        },
        "accoutumance_days": 55,
        "rythmes_activite_heures": [(5, 10), (17, 21)],
    },
}

# ═══ BESOINS NUTRITIONNELS (conceptuel, pas de produits/dosages) ═══
# Matrice saison × classe physiologique → familles de nutriments cibles
NUTRIENT_NEEDS = {
    "hiver":     {"energie", "proteines", "Na", "Ca", "Mg"},
    "pre_rut":   {"proteines", "P", "Ca", "oligo_elements"},
    "rut":       {"energie", "Na", "Mg", "oligo_elements"},
    "post_rut":  {"energie", "proteines", "Na", "P"},
    "printemps": {"Na", "Ca", "P", "proteines", "oligo_elements"},
    "ete":       {"Na", "Ca", "oligo_elements"},
}

CLASS_NEEDS = {
    "femelle_allaitement": {"Ca", "P", "proteines", "energie"},
    "femelle_gestation":   {"Ca", "P", "proteines", "Mg"},
    "male_croissance_bois": {"Ca", "P", "proteines", "Mg", "oligo_elements"},
    "male_dominant":        {"Na", "energie", "proteines", "oligo_elements"},
}

# ═══ HELPERS ═══

def _season_from_month(month: int) -> str:
    if month in (12, 1, 2): return "hiver"
    if month in (3, 4, 5): return "printemps"
    if month in (6, 7, 8): return "ete"
    if month in (9,):       return "pre_rut"
    if month in (10, 11):   return "rut"
    return "post_rut"


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def _clamp(v: float, lo=0.0, hi=100.0) -> float:
    return max(lo, min(hi, v))


# ═══ AXE 1 — BIOLOGIQUE / COMPORTEMENTAL ═══

def _score_bio(saline: dict, species: str, month: int) -> int:
    """Score biologique par espece (0-100)."""
    prof = SPECIES_PROFILES.get(species, SPECIES_PROFILES["cerf"])
    score = 50.0
    season = _season_from_month(month)
    saisons_peak = ["printemps", "pre_rut"]
    if season in saisons_peak:
        score += 20
    elif season == "ete":
        score += 12
    elif season == "rut":
        score += 8
    elif season in ("hiver", "post_rut"):
        score -= 5
    # Terrain modulator via saline detail already if present
    eau = saline.get("eau_distance_m", 200)
    corr = saline.get("corridor_distance_m", 200)
    if 30 <= eau <= 100: score += 8
    if 30 <= corr <= 100: score += 8
    return int(_clamp(score))


def _score_bio_multi(saline: dict, month: int) -> dict:
    """Score bio dict par espece + global."""
    out = {sp: _score_bio(saline, sp, month) for sp in SPECIES_PROFILES}
    out["global"] = int(sum(out.values()) / max(1, len(out)))
    return out


# ═══ AXE 2 — TERRAIN RULES Omega ═══

def _score_terrain(saline: dict, terrain_v10: dict) -> tuple[int, bool, str | None]:
    """Score terrain (0-100) + flag interdiction + motif eventuel."""
    score = 60.0
    interdit = False
    motif = None

    pente = terrain_v10.get("pente_deg", 10)
    canopy = terrain_v10.get("canopy", 0.5)
    drainage = terrain_v10.get("drainage_class", 3)
    hydro = terrain_v10.get("hydro_index", 0.5)
    humain_proche = terrain_v10.get("distance_habitation_m", 500) or 500

    # Penalites terrain
    if pente > 35:
        interdit = True
        motif = "Pente >35deg (impraticable)"
        score -= 40
    elif pente > 22:
        score -= 15
    elif pente > 12:
        score -= 5

    # Couvert forestier
    score += (canopy - 0.3) * 30  # canopy 0 → -9, canopy 1 → +21

    # Drainage (mauvais = proche eau, bon = sec)
    if drainage >= 5:
        score -= 12  # trop satur e, pas viable
    elif 2 <= drainage <= 3:
        score += 10

    # Hydro
    score += (hydro - 0.3) * 15

    # Contraintes humaines (sans pression de chasse)
    if humain_proche < 150:
        interdit = True
        motif = f"Habitation a {int(humain_proche)}m (<150m interdit)"
    elif humain_proche < 300:
        score -= 20

    return int(_clamp(score)), interdit, motif


# ═══ AXE 3 — NUTRITIONNEL 600m ═══

def _analyze_nutrition_600m(saline: dict, terrain_v10: dict, species: str, month: int) -> dict:
    """Analyse alimentation 600m + profil nutritionnel cible."""
    canopy = terrain_v10.get("canopy", 0.5)
    hydro = terrain_v10.get("hydro_index", 0.5)
    drainage = terrain_v10.get("drainage_class", 3)
    foret_mixte = canopy > 0.4
    cultures_proches = drainage in (2, 3) and hydro < 0.5  # zones ouvertes drainees
    bord_eau = hydro > 0.6

    # Types de vegetation detectes (heuristique)
    vegetation_types = []
    if foret_mixte: vegetation_types.append("foret_mixte")
    if cultures_proches: vegetation_types.append("cultures_cereales")
    if bord_eau: vegetation_types.append("hydrophytes")
    if not vegetation_types: vegetation_types.append("zone_ouverte")

    # Densite / diversite (heuristique)
    diversity = len(vegetation_types)
    density_index = min(1.0, canopy * 0.6 + hydro * 0.4)

    # Deficits probables (inversement proportionnel a la presence des sources)
    season = _season_from_month(month)
    needs = set(NUTRIENT_NEEDS.get(season, set()))

    # Classes physiologiques probables selon saison/espece
    classes_active = []
    if season == "printemps": classes_active = ["femelle_gestation", "male_croissance_bois"]
    elif season == "ete":     classes_active = ["femelle_allaitement", "male_croissance_bois"]
    elif season in ("pre_rut", "rut"): classes_active = ["male_dominant"]
    elif season == "hiver":   classes_active = ["femelle_gestation"]
    else:                     classes_active = ["male_dominant"]

    for cls in classes_active:
        needs |= CLASS_NEEDS.get(cls, set())

    # Correction par vegetation disponible
    nutrients_suffisants = set()
    if "cultures_cereales" in vegetation_types:
        nutrients_suffisants |= {"energie", "proteines"}
    if "foret_mixte" in vegetation_types:
        nutrients_suffisants |= {"Ca", "oligo_elements"}
    if "hydrophytes" in vegetation_types:
        nutrients_suffisants |= {"Na", "Mg"}

    deficits_probables = needs - nutrients_suffisants

    # Score nutritionnel (0-100)
    score = 50.0
    score += diversity * 10
    score += density_index * 20
    score -= len(deficits_probables) * 5
    if not deficits_probables:
        score += 15
    score = int(_clamp(score))

    return {
        "vegetation_types": vegetation_types,
        "diversity": diversity,
        "density_index": round(density_index, 2),
        "season": season,
        "classes_actives": classes_active,
        "besoins_saisonniers": sorted(needs),
        "nutrients_suffisants": sorted(nutrients_suffisants),
        "deficits_probables": sorted(deficits_probables),
        "nutrient_target_profile": {
            "a_renforcer": sorted(deficits_probables),
            "deja_suffisants": sorted(nutrients_suffisants),
        },
        "score_nutrition": score,
    }


# ═══ AXE 4 — RESEAU (corridors/zones/contamination) ═══
# INTERDICTION FORMELLE V12 (Commandant STEEVE-MAX):
# SALINES-V12-FEEDBACK-AFFUTS est interdit. Les salines restent 100% autonomes
# du positionnement des affuts. Rationale: chasse a l'arc/arbalete distance ethique 40m,
# toute penalite saline <80m affut serait contraire a la pratique reelle de chasse.
# Le parametre `affuts` est conserve pour compatibilite mais IGNORE dans le scoring.

def _score_reseau(saline: dict, corridors: list, affuts: list, contamination: list) -> tuple[int, list[str]]:
    """Score reseau + alertes. SANS feedback affuts (autonomie biologique stricte).

    Inputs effectivement utilises: corridors (via distance pre-calculee), contamination.
    Param `affuts` IGNORE par directive institutionnelle.
    """
    alertes: list[str] = []
    score = 50.0

    corr_dist = saline.get("corridor_distance_m", 200)
    if corr_dist <= 100:
        score += 20
    elif corr_dist <= 200:
        score += 10
    else:
        score -= 10
        alertes.append(f"Corridor distant ({corr_dist}m)")

    # INTERDICTION SALINES-V12-FEEDBACK-AFFUTS: AUCUNE logique de proximite affut.
    # Maintien autonomie biologique. Compatibilite chasse arc/arbalete (40m).
    # Le parametre `affuts` n'est PAS consomme.
    _ = affuts  # explicit no-op — interdiction formelle documentee

    lat_s = saline.get("lat"); lon_s = saline.get("lon") or saline.get("lng")

    # Contamination: si dans un cone contamination, alerte (independant des affuts)
    if lat_s and lon_s and contamination:
        cones = contamination if isinstance(contamination, list) else [contamination]
        in_cone_count = 0
        for cone in cones:
            poly = cone.get("polygon", [])
            if poly and _point_in_polygon(lat_s, lon_s, poly):
                in_cone_count += 1
        if in_cone_count > 0:
            score -= in_cone_count * 8
            alertes.append(f"Dans {in_cone_count} cone(s) contamination")

    return int(_clamp(score)), alertes


def _point_in_polygon(lat: float, lon: float, poly: list) -> bool:
    """Ray casting simple."""
    if len(poly) < 3: return False
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        pi_lat = poly[i][0] if isinstance(poly[i], (list, tuple)) else poly[i].get("lat")
        pi_lon = poly[i][1] if isinstance(poly[i], (list, tuple)) else (poly[i].get("lng") or poly[i].get("lon"))
        pj_lat = poly[j][0] if isinstance(poly[j], (list, tuple)) else poly[j].get("lat")
        pj_lon = poly[j][1] if isinstance(poly[j], (list, tuple)) else (poly[j].get("lng") or poly[j].get("lon"))
        if pi_lat is None or pj_lat is None: continue
        if ((pi_lat > lat) != (pj_lat > lat)) and (lon < (pj_lon - pi_lon) * (lat - pi_lat) / max(1e-9, (pj_lat - pi_lat)) + pi_lon):
            inside = not inside
        j = i
    return inside


# ═══ AXE 5 — ACCOUTUMANCE / PERMANENCE ═══

def _score_accoutumance(saline: dict, species: str) -> int:
    """Score base sur permanence + rayon attraction espece."""
    prof = SPECIES_PROFILES.get(species, SPECIES_PROFILES["cerf"])
    # Accoutumance augmente avec la permanence (etant une fixture institutionnelle)
    # Base 70 si VALIDEE, 40 si A-REPOSITIONNER
    if saline.get("status") == "SALINE-VALIDEE-Omega":
        base = 70
    else:
        base = 40
    # Modulation par score base existant
    base += (saline.get("score", 50) - 50) * 0.3
    return int(_clamp(base))


# ═══ ASSEMBLEUR V11-SUPRA ═══

def enrich_salines_v11_supra(
    salines: list[dict],
    terrain_v10: dict,
    corridors: list[dict],
    affuts: list[dict],
    contamination: Any,
    species: str,
    month: int,
) -> list[dict]:
    """Enrichit les salines existantes avec scoring multi-axe V11-SUPRA."""
    out = []
    for s in salines:
        lat_s = s.get("lat")
        lon_s = s.get("lon") or s.get("lng")

        # Axe 1: bio
        bio = _score_bio_multi(s, month)

        # Axe 2: terrain
        terr_score, interdit, motif_int = _score_terrain(s, terrain_v10)

        # Axe 3: nutrition 600m
        nutri = _analyze_nutrition_600m(s, terrain_v10, species, month)

        # Axe 4: reseau
        net_score, alertes_reseau = _score_reseau(s, corridors, affuts, contamination)

        # Axe 5: accoutumance
        acc_score = _score_accoutumance(s, species)

        # Score global V11 — ponderation institutionnelle
        score_global = int(_clamp(
            0.22 * bio["global"] +
            0.18 * terr_score +
            0.22 * nutri["score_nutrition"] +
            0.22 * net_score +
            0.16 * acc_score
        ))

        # Statut institutionnel
        if interdit:
            statut = "interdite"
        elif score_global >= 75 and s.get("status") == "SALINE-VALIDEE-Omega":
            statut = "conforme"
        elif score_global >= 55:
            statut = "a_optimiser"
        else:
            statut = "non_conforme"

        # Recommandations
        reco: list[str] = []
        if statut == "interdite":
            reco.append(f"SUPPRIMER: {motif_int}")
        else:
            if nutri["deficits_probables"]:
                reco.append(f"Renforcer apports: {', '.join(nutri['deficits_probables'])}")
            if alertes_reseau:
                reco.append("Reseau: " + " / ".join(alertes_reseau))
            if s.get("status") == "SALINE-A-REPOSITIONNER-Omega":
                reco.append("Deplacer vers position suggeree")
            if bio["global"] < 50:
                reco.append(f"Bio sous-optimal pour {species} (score {bio['global']})")
            if terr_score < 50 and not interdit:
                reco.append("Terrain sous-optimal: drainage/pente a verifier")
            if not reco:
                reco.append("Conserver: conforme V11-SUPRA")

        out.append({
            **s,
            "score_bio_species": bio,
            "score_bio_global": bio["global"],
            "score_terrain": terr_score,
            "score_reseau": net_score,
            "score_nutrition": nutri["score_nutrition"],
            "score_accoutumance": acc_score,
            "score_global_v11": score_global,
            "interdit": interdit,
            "motif_interdiction": motif_int,
            "nutrient_target_profile": nutri["nutrient_target_profile"],
            "nutrition_analysis_600m": {
                "vegetation_types": nutri["vegetation_types"],
                "diversity": nutri["diversity"],
                "density_index": nutri["density_index"],
                "deficits_probables": nutri["deficits_probables"],
                "besoins_saisonniers": nutri["besoins_saisonniers"],
                "classes_actives": nutri["classes_actives"],
            },
            "alertes_reseau": alertes_reseau,
            "statut_institutionnel": statut,
            "recommandations": reco,
            "source_v11": "SALINES-V11-SUPRA",
        })

    # Trier: conformes > a_optimiser > non_conforme > interdite ; puis score_global_v11
    statut_order = {"conforme": 0, "a_optimiser": 1, "non_conforme": 2, "interdite": 3}
    out.sort(key=lambda x: (statut_order.get(x.get("statut_institutionnel", "a_optimiser"), 2), -x.get("score_global_v11", 0)))
    return out
