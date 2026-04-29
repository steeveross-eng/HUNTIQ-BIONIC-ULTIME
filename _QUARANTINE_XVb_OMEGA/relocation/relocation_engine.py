"""
BCE-4X BLOC 3 — RELOCATION ENGINE
====================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Moteur de relocalisation automatique salines/affuts.

Declencheur:
  saline score >= 50 SUPRA (site viable)
  MAIS affut associe IMPOSSIBLE (classification "rejected" ou "a_eviter", score < 50)

Algorithme 6 phases:
  Phase 1: Generation candidats (12-24 en anneaux) via candidate_generator
  Phase 2: Evaluation SALINE (9 criteres V4) pour chaque candidat
  Phase 3: Evaluation AFFUT (4 facteurs V2) pour chaque candidat viable
  Phase 4: Evaluation BDRE (securite + flux via CORRIDOR_UNIFIED)
  Phase 5: Selection (score composite = saline*0.40 + affut*0.35 + bdre*0.25)
  Phase 6: TOP 3 pour choix utilisateur
"""
import math
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bionic.relocation.engine")

# Seuils de declenchement
SALINE_MIN_SCORE = 50    # Saline doit etre viable (pour reloc AFFUT)
AFFUT_IMPOSSIBLE_THRESHOLD = 50  # Affut impossible si score < 50

# BCE-4X ORDONNANCE STEEVE-MAX P0-K:
# Mode SAL-ALT: Si AUCUN affut stable n'est possible (classification a_eviter/rejected),
# declencher la generation de salines alternatives MEME SI score saline < 50.
SALINE_ALT_MODE_ENABLED = True

# Ponderations composite
W_SALINE = 0.40
W_AFFUT = 0.35
W_BDRE = 0.25

# Score minimum candidat saline
CANDIDATE_SALINE_MIN = 40


def _haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p)
        * math.sin((lng2 - lng1) * p / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def evaluate_relocation(
    current_saline: Dict[str, Any],
    current_affut: Dict[str, Any],
    center_lat: float,
    center_lng: float,
    terrain: dict,
    wind_direction_deg: float,
    wind_speed_kmh: float,
    session: str = "matin",
    species: str = "ORIGNAL",
    month: int = 10,
    corridors: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluer si une relocalisation est necessaire et proposer des alternatives.

    Retourne un RelocationResult complet.
    """
    saline_score = current_saline.get("score", 0)
    affut_score = current_affut.get("score", 0)
    affut_class = current_affut.get("classification", "unknown")

    # Diagnostic du site actuel
    diagnostic = _build_diagnostic(current_affut)

    # Verifier si relocalisation necessaire
    # Mode 1 (STANDARD): saline >= 50 ET affut impossible → relocaliser l'AFFUT
    # Mode 2 (SAL-ALT BCE-4X): affut impossible ET saline < 50 → relocaliser la SALINE
    affut_impossible = (
        affut_class in ("rejected", "a_eviter") or affut_score < AFFUT_IMPOSSIBLE_THRESHOLD
    )

    mode = None
    if saline_score >= SALINE_MIN_SCORE and affut_impossible:
        mode = "AFFUT_RELOC"
        needs_relocation = True
    elif SALINE_ALT_MODE_ENABLED and affut_impossible and saline_score < SALINE_MIN_SCORE:
        mode = "SAL_ALT"
        needs_relocation = True
    else:
        needs_relocation = False

    if not needs_relocation:
        return {
            "triggered": False,
            "reason": "site_acceptable",
            "mode": None,
            "current_site": {
                "saline": {
                    "id": current_saline.get("id", "SAL-CURRENT"),
                    "score": saline_score,
                },
                "affut": {
                    "score": affut_score,
                    "classification": affut_class,
                },
                "diagnostic": diagnostic,
            },
            "alternative": None,
            "candidates_evaluated": 0,
            "candidates_viable": 0,
        }

    # Phase 1: Generer les candidats
    from engines.relocation.candidate_generator import generate_relocation_candidates

    # SAL-ALT mode: rayon etendu a 400m minimum
    effective_radius_override = 400 if mode == "SAL_ALT" else None

    candidates = generate_relocation_candidates(
        center_lat=center_lat,
        center_lng=center_lng,
        species=species,
        corridors=corridors or [],
        min_candidates=12,
        radius_override=effective_radius_override,
    )

    # Phases 2-4: Evaluer chaque candidat
    evaluated = []
    for cand in candidates:
        result = _evaluate_candidate(
            cand, terrain, wind_direction_deg, wind_speed_kmh,
            session, species, month, center_lat, center_lng,
            corridors or [],
        )
        if result:
            evaluated.append(result)

    # Phase 5: Trier par score composite decroissant
    evaluated.sort(key=lambda x: x["composite_score"], reverse=True)

    # Phase 6: Selection TOP 3
    top_candidates = evaluated[:3]

    alternative = top_candidates[0] if top_candidates else None

    reason = "affut_impossible" if mode == "AFFUT_RELOC" else "saline_non_viable_affut_impossible"

    return {
        "triggered": True,
        "reason": reason,
        "mode": mode,
        "current_site": {
            "saline": {
                "id": current_saline.get("id", "SAL-CURRENT"),
                "score": saline_score,
            },
            "affut": {
                "score": affut_score,
                "classification": affut_class,
            },
            "diagnostic": diagnostic,
        },
        "alternative": alternative,
        "top_3": top_candidates,
        "candidates_evaluated": len(candidates),
        "candidates_viable": len(evaluated),
    }


def _build_diagnostic(affut: Dict[str, Any]) -> Dict[str, str]:
    """Construire le diagnostic detaille d'un affut."""
    factors = affut.get("factors", {})
    wind_data = factors.get("wind_scent", {})
    trail_data = factors.get("trail_access", {})

    diagnostic = {
        "vent": "contamination_directe" if wind_data.get("contaminated_sites", 0) > 0 else "acceptable",
        "bdre": "hors_corridor" if trail_data.get("score", 0) < 30 else "acceptable",
        "pente": "acceptable",
        "distance": "adequate",
        "securite": "ok",
    }

    # Enrichir le diagnostic
    if wind_data.get("score", 100) < 30:
        diagnostic["vent"] = "contamination_directe"
    elif wind_data.get("score", 100) < 50:
        diagnostic["vent"] = "vent_defavorable"

    if trail_data.get("score", 100) < 30:
        diagnostic["bdre"] = "hors_corridor"
    elif trail_data.get("score", 100) < 50:
        diagnostic["bdre"] = "corridor_eloigne"

    feeding_data = factors.get("feeding_position", {})
    if feeding_data.get("score", 50) < 30:
        diagnostic["distance"] = "trop_pres_ou_trop_loin"

    return diagnostic


def _evaluate_candidate(
    candidate, terrain, wind_direction_deg, wind_speed_kmh,
    session, species, month, center_lat, center_lng, corridors,
) -> Optional[Dict[str, Any]]:
    """
    Evaluer un candidat sur les 3 axes: saline + affut + BDRE.
    Retourne None si le candidat n'est pas viable.
    """
    cand_lat = candidate["lat"]
    cand_lng = candidate["lng"]

    # Phase 2: Score SALINE (9 criteres V4)
    try:
        from core.scoring_pipeline.alimentation_v4.salines_v4 import score_candidate_v4
        saline_score, criteres, justifications, sources, excluded = score_candidate_v4(
            candidate, terrain, species, month, center_lat, center_lng, None,
        )
        if excluded or saline_score < CANDIDATE_SALINE_MIN:
            return None
    except Exception as e:
        logger.warning(f"[RELOCATION] Erreur scoring saline: {e}")
        saline_score = 45
        criteres = {}
        justifications = []

    # Phase 3: Score AFFUT (4 facteurs V2)
    try:
        from engines.hunt_orchestrator.choix_affuts import score_blind_position
        affut_result = score_blind_position(
            cand_lat, cand_lng,
            "ground_blind", False,
            wind_direction_deg, wind_speed_kmh, session,
            [{"lat": center_lat, "lng": center_lng}],
            None, None,
            center_lat, center_lng,
        )
        affut_score = affut_result.get("score", 0)
        affut_class = affut_result.get("classification", "unknown")
        if affut_class == "rejected":
            return None
    except Exception as e:
        logger.warning(f"[RELOCATION] Erreur scoring affut: {e}")
        affut_score = 40
        affut_class = "unknown"
        affut_result = {}

    # Phase 4: Score BDRE via CORRIDOR_UNIFIED
    bdre_score = _compute_bdre_proximity_score(cand_lat, cand_lng, corridors)

    # Score composite
    composite = (
        saline_score * W_SALINE
        + affut_score * W_AFFUT
        + bdre_score * W_BDRE
    )

    # Distance depuis le site original
    dist_from_center = _haversine_m(cand_lat, cand_lng, center_lat, center_lng)

    # Justification
    justification = {
        "supra": ", ".join(justifications[:3]) if justifications else "Score saline viable",
        "affuts": f"Score {affut_score:.0f}/100, classification {affut_class}",
        "bdre": f"Score BDRE {bdre_score:.0f}/100",
    }

    if candidate.get("corridor_type"):
        justification["bdre"] += f", corridor {candidate['corridor_type']}"

    return {
        "saline": {
            "lat": cand_lat,
            "lng": cand_lng,
            "score": round(saline_score),
            "criteres": criteres,
        },
        "affut": {
            "lat": cand_lat,
            "lng": cand_lng,
            "score": round(affut_score, 1),
            "classification": affut_class,
        },
        "corridor_type": candidate.get("corridor_type"),
        "distance_from_original_m": round(dist_from_center),
        "composite_score": round(composite, 1),
        "justification": justification,
        "scores_detail": {
            "saline": round(saline_score),
            "affut": round(affut_score, 1),
            "bdre": round(bdre_score, 1),
        },
    }


def _compute_bdre_proximity_score(lat, lng, corridors):
    """
    Score BDRE base sur la proximite et le type du corridor UNIFIED le plus proche.
    """
    if not corridors:
        return 40  # Neutre sans donnees corridor

    from engines.corridor_unified.corridor_model import find_nearest_corridor

    nearest = find_nearest_corridor(lat, lng, corridors, max_dist_m=500)
    if not nearest:
        return 30

    dist = nearest["distance_m"]
    corridor_type = nearest["corridor"]["type"]

    # Score base sur type + distance
    type_bonus = {"CRITIQUE": 30, "MAJEUR": 15, "MINEUR": 0}
    base_bonus = type_bonus.get(corridor_type, 0)

    if dist < 30:
        return min(100, 90 + base_bonus * 0.1)
    elif dist < 100:
        return min(100, 75 + base_bonus * 0.3)
    elif dist < 200:
        return min(100, 55 + base_bonus * 0.5)
    elif dist < 350:
        return min(100, 40 + base_bonus * 0.5)
    else:
        return 30
