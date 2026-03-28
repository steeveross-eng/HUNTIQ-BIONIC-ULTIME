"""
BCE-4X P0 — ENGINE CHOIX DES AFFUTS v1
========================================
Recommandation d'affuts basee sur donnees REELLES.

Donnees REELLES:
- Vent V3 (Open-Meteo) via engine vent_odeurs
- Sentiers OSM (terrain_nav)
- Zones d'eau (cache backend)
- Zones d'alimentation (organic zones)
- Waypoints utilisateur (affuts fixes)

ZERO donnee simulee (corridor, topographie, cover, pressure = SUPPRIMES).
Scoring base UNIQUEMENT sur:
1. Wind/scent score (contamination des sites alimentation)
2. Trail accessibility score (acces reel via sentier OSM)
3. Water proximity (distance au point d'eau reel)
4. Feeding site positioning (distance et angle aux sites alimentation)

STEEVE-MAX 2026-03-28 — Standard institutionnel.
"""

import math
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("bionic.hunt_orchestrator.choix_affuts")

# Types d'affuts
STAND_TYPES = {
    "tree_stand": {"name_fr": "Mirador (arbre)", "height_m": 4.5, "concealment": "high", "mobility": "fixed"},
    "ground_blind": {"name_fr": "Cache au sol", "height_m": 1.2, "concealment": "high", "mobility": "mobile"},
    "elevated_blind": {"name_fr": "Cache sureleve", "height_m": 3.0, "concealment": "high", "mobility": "fixed"},
    "natural_hide": {"name_fr": "Cache naturel", "height_m": 0, "concealment": "moderate", "mobility": "mobile"},
    "saddle_platform": {"name_fr": "Plateforme saddle", "height_m": 5.0, "concealment": "moderate", "mobility": "fixed"},
}


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _nearest_trail_distance(lat: float, lng: float, trail_graph) -> float:
    """Distance au sentier OSM le plus proche."""
    if trail_graph.is_empty:
        return float("inf")
    nearest = trail_graph.nearest_node(lat, lng, max_dist_m=2000)
    if nearest is None:
        return float("inf")
    n_lat, n_lng = trail_graph.nodes[nearest]
    return _haversine(lat, lng, n_lat, n_lng)


def _nearest_water_distance(lat: float, lng: float, water_check_fn) -> float:
    """Distance approximative a la zone d'eau la plus proche.
    Teste sur une grille de 100m autour du point."""
    if water_check_fn is None:
        return float("inf")
    for radius_m in [50, 100, 200, 300, 500]:
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            test_lat = lat + (radius_m / 111320) * math.cos(rad)
            test_lng = lng + (radius_m / (111320 * math.cos(math.radians(lat)))) * math.sin(rad)
            if water_check_fn(test_lat, test_lng):
                return radius_m
    return 600  # Au-dela de 500m, considere eloigne


def score_blind_position(
    blind_lat: float,
    blind_lng: float,
    blind_type: str,
    is_fixed: bool,
    wind_direction_deg: float,
    wind_speed_kmh: float,
    session: str,
    feeding_sites: List[Dict[str, float]],
    trail_graph,
    water_check_fn=None,
    center_lat: float = 0,
    center_lng: float = 0,
) -> Dict[str, Any]:
    """
    Scorer un affut avec UNIQUEMENT des donnees reelles.

    Facteurs de score:
    1. Wind/scent (40%) — contamination des sites alimentation
    2. Trail access (25%) — proximite d'un sentier OSM reel
    3. Feeding positioning (20%) — distance/angle optimal aux sites alimentation
    4. Water proximity (15%) — distance aux points d'eau reels
    """
    from engines.hunt_orchestrator.vent_odeurs import evaluate_blind_wind_score

    # 1. Score vent/odeur (40%)
    wind_result = evaluate_blind_wind_score(
        blind_lat, blind_lng,
        feeding_sites, wind_direction_deg, wind_speed_kmh, session
    )
    wind_score = wind_result["score"]

    # 2. Score acces sentier (25%)
    trail_dist = _nearest_trail_distance(blind_lat, blind_lng, trail_graph)
    if trail_dist < 30:
        trail_score = 100  # Directement sur un sentier
    elif trail_dist < 100:
        trail_score = 90 - (trail_dist - 30) * 0.3
    elif trail_dist < 300:
        trail_score = 70 - (trail_dist - 100) * 0.2
    elif trail_dist < 600:
        trail_score = 30 - (trail_dist - 300) * 0.1
    else:
        trail_score = 0  # Trop loin de tout sentier

    # 3. Score positionnement alimentation (20%)
    feeding_score = 50  # Neutre par defaut
    if feeding_sites:
        feeding_dists = []
        for fs in feeding_sites:
            d = _haversine(blind_lat, blind_lng, fs["lat"], fs["lng"])
            feeding_dists.append(d)

        min_feeding_dist = min(feeding_dists)
        # Distance optimale: 150-400m (assez pres pour intercepter, assez loin pour ne pas deranger)
        if 150 <= min_feeding_dist <= 400:
            feeding_score = 90
        elif 100 <= min_feeding_dist < 150:
            feeding_score = 70
        elif 400 < min_feeding_dist <= 600:
            feeding_score = 65
        elif min_feeding_dist < 100:
            feeding_score = 30  # Trop pres, risque de derangement
        else:
            feeding_score = 40  # Trop loin

    # 4. Score eau (15%)
    water_dist = _nearest_water_distance(blind_lat, blind_lng, water_check_fn)
    if 50 <= water_dist <= 200:
        water_score = 90
    elif 200 < water_dist <= 400:
        water_score = 70
    elif water_dist < 50:
        water_score = 50  # Trop pres (bruit, terrain mou)
    else:
        water_score = 40

    # Score total pondere
    total = (
        wind_score * 0.40 +
        trail_score * 0.25 +
        feeding_score * 0.20 +
        water_score * 0.15
    )

    # Distance au centre
    dist_center = _haversine(blind_lat, blind_lng, center_lat, center_lng)

    blind_info = STAND_TYPES.get(blind_type, STAND_TYPES["ground_blind"])

    return {
        "lat": blind_lat,
        "lng": blind_lng,
        "type_key": blind_type,
        "type_name": blind_info["name_fr"],
        "height_m": blind_info["height_m"],
        "concealment": blind_info["concealment"],
        "is_fixed": is_fixed,
        "score": round(total, 1),
        "factors": {
            "wind_scent": {
                "score": round(wind_score, 1),
                "weight": 0.40,
                "contaminated_sites": wind_result["contamination_count"],
                "message": wind_result["message"],
            },
            "trail_access": {
                "score": round(trail_score, 1),
                "weight": 0.25,
                "nearest_trail_m": round(trail_dist) if trail_dist < 10000 else None,
                "source": "osm_real",
            },
            "feeding_position": {
                "score": round(feeding_score, 1),
                "weight": 0.20,
                "nearest_feeding_m": round(min(feeding_dists)) if feeding_sites and feeding_dists else None,
                "source": "organic_zones",
            },
            "water_proximity": {
                "score": round(water_score, 1),
                "weight": 0.15,
                "nearest_water_m": round(water_dist) if water_dist < 10000 else None,
                "source": "osm_cache",
            },
        },
        "distance_to_center_m": round(dist_center),
        "session": session,
        "scent_zone": wind_result.get("scent_zone"),
    }


def recommend_blinds(
    center_lat: float,
    center_lng: float,
    wind_direction_deg: float,
    wind_speed_kmh: float,
    session: str,
    feeding_sites: List[Dict[str, float]],
    trail_graph,
    fixed_blinds: List[Dict[str, Any]] = None,
    water_check_fn=None,
    radius_m: int = 600,
    species: str = "orignal",
    max_blinds: int = 5,
) -> List[Dict[str, Any]]:
    """
    Recommander les meilleurs affuts pour une session.

    1. Scorer les affuts fixes (positions connues, non deplacables)
    2. Identifier des positions mobiles optimales sur le reseau de sentiers
    3. Trier par score total
    """
    all_blinds = []

    # 1. Scorer les affuts fixes de l'utilisateur
    if fixed_blinds:
        for fb in fixed_blinds:
            dist = _haversine(fb["lat"], fb["lng"], center_lat, center_lng)
            if dist > radius_m * 1.5:
                continue
            result = score_blind_position(
                fb["lat"], fb["lng"],
                fb.get("type_key", "tree_stand"), True,
                wind_direction_deg, wind_speed_kmh, session,
                feeding_sites, trail_graph, water_check_fn,
                center_lat, center_lng,
            )
            result["id"] = fb.get("id", f"fixed-{fb['lat']:.4f}")
            result["name"] = fb.get("name", "Affut fixe")
            all_blinds.append(result)

    # 2. Generer des positions mobiles sur les noeuds du reseau de sentiers
    if trail_graph and not trail_graph.is_empty:
        candidate_nodes = []
        for nid, (nlat, nlng) in trail_graph.nodes.items():
            if nid in trail_graph.obstacle_nodes:
                continue
            dist = _haversine(nlat, nlng, center_lat, center_lng)
            if dist < 100 or dist > radius_m:
                continue
            # Verifier connectivite (au moins 2 voisins = intersection)
            neighbors = trail_graph.adj.get(nid, [])
            candidate_nodes.append((nid, nlat, nlng, dist, len(neighbors)))

        # Prioriser les intersections de sentiers (plus de voisins)
        candidate_nodes.sort(key=lambda x: (-x[4], x[3]))

        # Scorer les meilleurs candidats
        tested = 0
        for nid, nlat, nlng, dist, connectivity in candidate_nodes:
            if tested >= max_blinds * 3:
                break
            # Eviter les positions trop proches d'un affut deja selectionne
            too_close = False
            for existing in all_blinds:
                if _haversine(nlat, nlng, existing["lat"], existing["lng"]) < 80:
                    too_close = True
                    break
            if too_close:
                continue

            # Type d'affut mobile
            mobile_type = "ground_blind" if connectivity <= 2 else "natural_hide"

            result = score_blind_position(
                nlat, nlng,
                mobile_type, False,
                wind_direction_deg, wind_speed_kmh, session,
                feeding_sites, trail_graph, water_check_fn,
                center_lat, center_lng,
            )
            result["id"] = f"mobile-{nid}"
            result["name"] = f"Position mobile ({round(dist)}m)"
            result["trail_node_id"] = nid
            result["trail_connectivity"] = connectivity
            all_blinds.append(result)
            tested += 1

    # Trier par score
    all_blinds.sort(key=lambda x: x["score"], reverse=True)
    return all_blinds[:max_blinds]
