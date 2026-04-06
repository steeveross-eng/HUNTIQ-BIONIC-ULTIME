"""
BCE-4X BLOC 1 — CORRIDOR_UNIFIED MODEL
=========================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Modele de donnees unifie pour les corridors.
Fusion corridors VISIBLES (sentiers OSM) + corridors BDRE INTERNES.

Classification:
  CRITIQUE : Sentier OSM + BDRE score > 80 + noeud haut degre
  MAJEUR   : Sentier OSM OU BDRE score > 50
  MINEUR   : BDRE score < 50 OU segment isole

Attributs obligatoires:
  intensite, direction, saisonnalite, espece, largeur, zone_tampon, risque
"""
import math
import hashlib
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bionic.corridor_unified.model")

# Seuils de classification institutionnels STEEVE-MAX
THRESHOLD_CRITIQUE_BDRE = 80
THRESHOLD_MAJEUR_BDRE = 50
THRESHOLD_CRITIQUE_INTENSITE = 75
THRESHOLD_MAJEUR_INTENSITE_LO = 40
THRESHOLD_MAJEUR_INTENSITE_HI = 75

# Zones tampon par type
ZONE_TAMPON = {"CRITIQUE": 100, "MAJEUR": 50, "MINEUR": 25}
LARGEUR_SEUILS = {"CRITIQUE": 3.0, "MAJEUR": 1.5, "MINEUR": 0.5}


def _haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p)
        * math.sin((lng2 - lng1) * p / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _seed_float(lat, lng, salt=""):
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def classify_corridor(
    bdre_score: float,
    has_osm_trail: bool,
    connectivity: int = 1,
    intensite: float = 50,
) -> str:
    """
    Classifier un segment de corridor.
    CRITIQUE: OSM + BDRE > 80 + connectivity >= 3
    MAJEUR: OSM OU BDRE > 50
    MINEUR: reste
    """
    if has_osm_trail and bdre_score > THRESHOLD_CRITIQUE_BDRE and connectivity >= 3:
        return "CRITIQUE"
    if has_osm_trail or bdre_score > THRESHOLD_MAJEUR_BDRE:
        return "MAJEUR"
    return "MINEUR"


def build_corridor_segment(
    segment_id: str,
    coords: List[Dict[str, float]],
    bdre_score: float,
    has_osm_trail: bool,
    connectivity: int,
    species: str = "ORIGNAL",
    season: str = "automne",
    source: str = "hybrid",
) -> Dict[str, Any]:
    """
    Construire un CorridorSegment unifie avec tous les attributs obligatoires.
    """
    corridor_type = classify_corridor(bdre_score, has_osm_trail, connectivity)

    # Calculer la longueur totale
    length_m = 0.0
    for i in range(len(coords) - 1):
        length_m += _haversine_m(
            coords[i]["lat"], coords[i]["lng"],
            coords[i + 1]["lat"], coords[i + 1]["lng"],
        )

    # Direction dominante (bearing du premier au dernier point)
    if len(coords) >= 2:
        dlat = coords[-1]["lat"] - coords[0]["lat"]
        dlng = coords[-1]["lng"] - coords[0]["lng"]
        direction_deg = (math.degrees(math.atan2(dlng, dlat)) + 360) % 360
    else:
        direction_deg = 0.0

    # Intensite: derivee du BDRE score + connectivity
    intensite = min(100, bdre_score * 0.7 + connectivity * 8)

    # Risque BDRE: inverse de l'intensite (corridor a forte intensite = faible risque de derangement)
    risque_bdre = max(0, 100 - intensite * 0.8)

    # Largeur estimee basee sur le type
    largeur_m = LARGEUR_SEUILS[corridor_type]
    if has_osm_trail:
        largeur_m = max(largeur_m, 2.0)

    # Zone tampon
    zone_tampon_m = ZONE_TAMPON[corridor_type]

    # Score unifie composite
    score_unified = _compute_unified_score(
        bdre_score, has_osm_trail, connectivity, intensite, corridor_type,
    )

    return {
        "id": segment_id,
        "type": corridor_type,
        "coords": coords,
        "length_m": round(length_m, 1),
        "intensite": round(intensite, 1),
        "direction_deg": round(direction_deg, 1),
        "saisonnalite": season,
        "espece_principale": species.upper(),
        "risque_bdre": round(risque_bdre, 1),
        "largeur_m": round(largeur_m, 1),
        "zone_tampon_m": zone_tampon_m,
        "source": source,
        "has_osm_trail": has_osm_trail,
        "connectivity": connectivity,
        "bdre_score_raw": round(bdre_score, 1),
        "score_unified": round(score_unified, 1),
    }


def _compute_unified_score(
    bdre_score: float,
    has_osm_trail: bool,
    connectivity: int,
    intensite: float,
    corridor_type: str,
) -> float:
    """
    Score unifie composite 0-100.
    Ponderations:
      BDRE raw: 40%
      OSM trail presence: 20%
      Connectivity: 20%
      Intensite: 20%
    """
    osm_bonus = 100 if has_osm_trail else 0
    conn_score = min(100, connectivity * 25)

    score = (
        bdre_score * 0.40
        + osm_bonus * 0.20
        + conn_score * 0.20
        + intensite * 0.20
    )
    return min(100, score)


def find_nearest_corridor(
    lat: float,
    lng: float,
    corridors: List[Dict[str, Any]],
    max_dist_m: float = 500,
) -> Optional[Dict[str, Any]]:
    """
    Trouver le corridor UNIFIED le plus proche d'un point donne.
    Retourne le corridor avec sa distance, ou None si aucun dans le rayon.
    """
    best = None
    best_dist = max_dist_m

    for corridor in corridors:
        for coord in corridor.get("coords", []):
            d = _haversine_m(lat, lng, coord["lat"], coord["lng"])
            if d < best_dist:
                best_dist = d
                best = {
                    "corridor": corridor,
                    "distance_m": round(d),
                    "nearest_point": coord,
                }

    return best


def filter_corridors_by_type(
    corridors: List[Dict[str, Any]],
    types: List[str],
) -> List[Dict[str, Any]]:
    """Filtrer les corridors par type (CRITIQUE, MAJEUR, MINEUR)."""
    return [c for c in corridors if c.get("type") in types]
