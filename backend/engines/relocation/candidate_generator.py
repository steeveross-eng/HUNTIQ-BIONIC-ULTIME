"""
BCE-4X BLOC 3 — CANDIDATE GENERATOR
======================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Generation de candidats en anneaux pour la relocalisation automatique.

Algorithme:
  Anneau interieur  (100-150m) : 6 candidats a 60 degres d'intervalle
  Anneau intermediaire (150-200m) : 6 candidats decales 30 degres
  Anneau exterieur (200-rayon_espece) : 6-12 candidats
  Orientation CORRIDOR_UNIFIED : candidats decales vers corridors CRITIQUES puis MAJEURS

Rayons adaptatifs par espece:
  CERF (chevreuil) : 200m
  ORIGNAL           : 300m
  WAPITI            : 400m
"""
import math
import logging
from typing import Dict, List, Any

logger = logging.getLogger("bionic.relocation.candidate_generator")

# Rayons adaptatifs par espece (ordonnance STEEVE-MAX)
SPECIES_RADIUS = {
    "CERF": 200,
    "ORIGNAL": 300,
    "WAPITI": 400,
}

# Configuration des anneaux
RING_CONFIG = [
    {"inner_m": 100, "outer_m": 150, "n_candidates": 6, "offset_deg": 0},
    {"inner_m": 150, "outer_m": 200, "n_candidates": 6, "offset_deg": 30},
    {"inner_m": 200, "outer_m": None, "n_candidates": 12, "offset_deg": 15},
]


def _haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p)
        * math.sin((lng2 - lng1) * p / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def generate_relocation_candidates(
    center_lat: float,
    center_lng: float,
    species: str = "ORIGNAL",
    corridors: List[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Generer 12-24 candidats en anneaux concentriques.

    Les candidats proches de corridors CRITIQUES ou MAJEURS sont
    priorises par un decalage angulaire vers le corridor le plus proche.
    """
    max_radius = SPECIES_RADIUS.get(species.upper(), 300)
    candidates = []

    for ring in RING_CONFIG:
        inner = ring["inner_m"]
        outer = ring["outer_m"] or max_radius
        n = ring["n_candidates"]
        offset = ring["offset_deg"]

        # Ne generer que si l'anneau est dans le rayon de l'espece
        if inner >= max_radius:
            continue

        actual_outer = min(outer, max_radius)
        ring_dist = (inner + actual_outer) / 2

        step_deg = 360 / n

        for i in range(n):
            bearing_deg = (offset + i * step_deg) % 360
            rad = math.radians(bearing_deg)

            cand_lat = center_lat + (ring_dist / 111320) * math.cos(rad)
            cand_lng = center_lng + (ring_dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(rad)

            candidate = {
                "lat": round(cand_lat, 6),
                "lng": round(cand_lng, 6),
                "ring_m": round(ring_dist),
                "bearing_deg": round(bearing_deg, 1),
                "corridor_type": None,
                "corridor_distance_m": None,
            }

            # Enrichir avec le corridor le plus proche
            if corridors:
                candidate = _enrich_with_corridor(candidate, corridors)

            candidates.append(candidate)

    # Ajouter des candidats bonus orientes corridor
    if corridors:
        corridor_candidates = _generate_corridor_oriented(
            center_lat, center_lng, corridors, max_radius,
        )
        candidates.extend(corridor_candidates)

    logger.info(
        f"[RELOCATION-GEN] {len(candidates)} candidats generes "
        f"(espece={species}, rayon={max_radius}m)"
    )
    return candidates


def _enrich_with_corridor(candidate, corridors):
    """Enrichir un candidat avec la distance et le type du corridor le plus proche."""
    from engines.corridor_unified.corridor_model import find_nearest_corridor

    nearest = find_nearest_corridor(
        candidate["lat"], candidate["lng"], corridors, max_dist_m=200,
    )
    if nearest:
        candidate["corridor_type"] = nearest["corridor"]["type"]
        candidate["corridor_distance_m"] = nearest["distance_m"]
        candidate["corridor_id"] = nearest["corridor"]["id"]
    return candidate


def _generate_corridor_oriented(
    center_lat, center_lng, corridors, max_radius,
):
    """
    Generer des candidats supplementaires orientes vers les corridors CRITIQUES
    puis MAJEURS.
    """
    from engines.corridor_unified.corridor_model import filter_corridors_by_type

    extra = []

    # Prioriser CRITIQUE puis MAJEUR
    for corridor_type in ["CRITIQUE", "MAJEUR"]:
        typed = filter_corridors_by_type(corridors, [corridor_type])
        for corridor in typed[:3]:
            for coord in corridor.get("coords", []):
                dist = _haversine_m(center_lat, center_lng, coord["lat"], coord["lng"])
                if 100 < dist < max_radius:
                    extra.append({
                        "lat": coord["lat"],
                        "lng": coord["lng"],
                        "ring_m": round(dist),
                        "bearing_deg": 0,
                        "corridor_type": corridor_type,
                        "corridor_distance_m": 0,
                        "corridor_id": corridor["id"],
                        "source": "corridor_oriented",
                    })
            if len(extra) >= 6:
                break
        if len(extra) >= 6:
            break

    return extra[:6]
