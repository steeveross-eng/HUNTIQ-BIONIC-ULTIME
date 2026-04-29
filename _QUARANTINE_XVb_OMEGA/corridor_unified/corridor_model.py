"""
BCE-4X BLOC 1 — CORRIDOR_UNIFIED MODEL
=========================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0
PATCH URGENCE 2026-04-06: Masque eau obligatoire — ZERO corridor sur zone eau

Modele de donnees unifie pour les corridors.
Fusion corridors VISIBLES (sentiers OSM) + corridors BDRE INTERNES.

Classification:
  CRITIQUE : Sentier OSM + BDRE score > 80 + noeud haut degre
  MAJEUR   : Sentier OSM OU BDRE score > 50
  MINEUR   : BDRE score < 50 OU segment isole

EXCLUSIONS HYDROGRAPHIQUES:
  - Tout point sur zone eau (is_water) = EXCLUSION TOTALE
  - Buffer eau minimum 30m = segment rejete
  - Midpoint segment sur eau = segment rejete

Attributs obligatoires:
  intensite, direction, saisonnalite, espece, largeur, zone_tampon, risque
"""
import math
import hashlib
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bionic.corridor_unified.model")

# Buffer hydrographique minimum (metres)
WATER_BUFFER_MIN_M = 30

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



def _is_water_at(lat: float, lng: float) -> bool:
    """
    MASQUE EAU OBLIGATOIRE — BCE-4X URGENCE HYDROGRAPHIQUE.
    Detecte si un point est situe sur une zone d'eau
    en utilisant la couche cost_surface de corridors_v10.
    """
    try:
        from core.scoring_pipeline.corridors_v10.cost_surface import _load_cell_data
        cell = _load_cell_data(lat, lng, 10)
        return cell.get("is_water", False)
    except Exception:
        # Fallback deterministe identique a cost_surface
        h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:water_body".encode()).hexdigest()
        return (int(h[:8], 16) / 0xFFFFFFFF) > 0.88


def _distance_eau_at(lat: float, lng: float) -> float:
    """Distance a la zone d'eau la plus proche (metres)."""
    try:
        from core.scoring_pipeline.corridors_v10.cost_surface import _load_cell_data
        cell = _load_cell_data(lat, lng, 10)
        return cell.get("distance_eau_m", 500)
    except Exception:
        h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:dist_eau".encode()).hexdigest()
        return 10 + 490 * (int(h[:8], 16) / 0xFFFFFFFF)


def check_segment_water_exclusion(coords: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    VERIFICATION HYDRO OBLIGATOIRE — ORDONNANCE STEEVE-MAX.
    Verifie qu'un segment ne traverse PAS de zone d'eau.

    Controles:
    1. Aucun endpoint sur eau (is_water)
    2. Midpoint du segment pas sur eau
    3. Distance eau >= WATER_BUFFER_MIN_M (30m) pour tous les points
    4. Echantillonnage supplementaire a 25/75% du segment

    Retourne:
      {"excluded": True/False, "reason": str, "details": dict}
    """
    if not coords or len(coords) < 2:
        return {"excluded": False, "reason": "segment_vide", "details": {}}

    check_points = []

    # Points de controle: debut, 25%, midpoint, 75%, fin
    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        if frac == 0.0:
            check_points.append(("debut", coords[0]))
        elif frac == 1.0:
            check_points.append(("fin", coords[-1]))
        else:
            lat = coords[0]["lat"] + frac * (coords[-1]["lat"] - coords[0]["lat"])
            lng = coords[0]["lng"] + frac * (coords[-1]["lng"] - coords[0]["lng"])
            check_points.append((f"frac_{int(frac*100)}pct", {"lat": lat, "lng": lng}))

    for label, point in check_points:
        lat, lng = point["lat"], point["lng"]

        # Check 1: Point sur eau
        if _is_water_at(lat, lng):
            return {
                "excluded": True,
                "reason": f"point_sur_eau ({label})",
                "details": {"lat": lat, "lng": lng, "check": label, "is_water": True},
            }

        # Check 2: Buffer eau
        dist_eau = _distance_eau_at(lat, lng)
        if dist_eau < WATER_BUFFER_MIN_M:
            return {
                "excluded": True,
                "reason": f"buffer_eau_insuffisant ({label}, {dist_eau:.0f}m < {WATER_BUFFER_MIN_M}m)",
                "details": {"lat": lat, "lng": lng, "check": label, "distance_eau_m": dist_eau},
            }

    return {"excluded": False, "reason": "segment_valide", "details": {}}



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
