"""
clarity_engine.py — Moteur de guidance optimale access_clarity_engine_v7
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX

Pipeline:
  1. access_engine_v6.compute_access_route (Dijkstra + A* corrige)
  2. Lissage Douglas-Peucker (reduction bruit)
  3. Interpolation naturelle (courbes Catmull-Rom)
  4. Score de clarte (0→100)
  5. Conversion format compatible bionic_stand_recommendation_engine
"""
import logging
import math

from modules.access_engine_v6.engine import compute_access_route
from .smoother import douglas_peucker, interpolate_natural
from .scorer import compute_clarity_score

logger = logging.getLogger("access_clarity_engine_v7")


async def compute_clear_path(
    start_lat: float, start_lng: float,
    stand_lat: float, stand_lng: float,
    month: int = 10,
    species: str = "orignal",
    analysis_radius_m: int = 2000,
) -> dict:
    """
    Pipeline unique de guidance optimale.
    Retourne un trace lisible, naturel et coherent terrain.
    """
    # Phase 1: Calcul via access_engine_v6 (Dijkstra + A* avec fix Overpass)
    route_data = await compute_access_route(
        origin={"lat": start_lat, "lng": start_lng},
        destination={"lat": stand_lat, "lng": stand_lng},
        month=month,
        species=species,
        analysis_radius_m=analysis_radius_m,
    )

    if route_data.get("status") != "ok" or not route_data.get("route", {}).get("segments"):
        logger.warning("clarity_v7: access_engine_v6 returned no route, using direct fallback")
        return _direct_fallback(start_lat, start_lng, stand_lat, stand_lng)

    route = route_data["route"]
    segments = route["segments"]

    # Phase 2: Assembler toutes les coordonnees en une seule liste
    all_coords = []
    for seg in segments:
        for c in seg.get("coordinates", []):
            if isinstance(c, list):
                all_coords.append({"lng": c[0], "lat": c[1]})
            elif isinstance(c, dict):
                all_coords.append(c)

    if len(all_coords) < 2:
        return _direct_fallback(start_lat, start_lng, stand_lat, stand_lng)

    # Phase 3: Lissage Douglas-Peucker (supprimer bruit grille)
    smoothed = douglas_peucker(all_coords, tolerance=0.00003)

    # Phase 4: Interpolation naturelle (courbes entre segments rectilignes)
    if len(smoothed) >= 3:
        natural = interpolate_natural(smoothed, num_interp=2)
    else:
        natural = smoothed

    # Phase 5: Score de clarte
    clarity = compute_clarity_score(route_data)

    # Phase 6: Determiner le type dominant et l'algo de routage
    trail_pct = route.get("trail_percentage", 0)
    if trail_pct > 70:
        routing_algo = "hybrid_trail_terrain"
        trail_type = "sentier_reel"
    elif trail_pct > 20:
        routing_algo = "hybrid_trail_terrain"
        trail_type = "hybride"
    else:
        routing_algo = "terrain_grid_astar"
        trail_type = "terrain_naturel"

    total_distance = route.get("total_distance_m", 0)

    # Phase 7: Construire la reponse au format bionic_stand_recommendation
    coords_list = []
    for c in natural:
        if isinstance(c, dict):
            coords_list.append({"lat": round(c["lat"], 7), "lng": round(c["lng"], 7)})
        else:
            coords_list.append({"lat": round(c[1], 7), "lng": round(c[0], 7)})

    # S'assurer que le premier et dernier point sont origin et destination
    if coords_list:
        coords_list[0] = {"lat": round(start_lat, 7), "lng": round(start_lng, 7)}
        coords_list[-1] = {"lat": round(stand_lat, 7), "lng": round(stand_lng, 7)}

    # Enrichir le premier point avec les metadonnees
    if coords_list:
        coords_list[0]["trail_distance_m"] = round(total_distance)
        coords_list[0]["trail_type"] = trail_type
        coords_list[0]["routing_algo"] = routing_algo
        coords_list[0]["clarity_score"] = clarity["score"]
        coords_list[0]["clarity_grade"] = clarity["grade"]

    # Calculer le point de jonction sentier/terrain si hybride
    junction = None
    phase1_dist = 0
    phase2_dist = 0
    trail_seg_end = 0

    if trail_pct > 0:
        for i, seg in enumerate(segments):
            if seg["type"] == "trail":
                phase1_dist += seg.get("distance_m", 0)
                trail_seg_end += len(seg.get("coordinates", []))
            else:
                phase2_dist += seg.get("distance_m", 0)

        if trail_seg_end > 0 and trail_seg_end < len(coords_list):
            jc = coords_list[min(trail_seg_end, len(coords_list) - 1)]
            junction = {"lat": jc["lat"], "lng": jc["lng"]}

    result = {
        "coords": coords_list,
        "distance_m": round(total_distance),
        "clarity_score": clarity["score"],
        "clarity_grade": clarity["grade"],
        "clarity_components": clarity["components"],
        "trail_percentage": trail_pct,
        "routing_algo": routing_algo,
        "trail_type": trail_type,
        "phase1_distance_m": round(phase1_dist),
        "phase2_distance_m": round(phase2_dist),
        "junction": junction,
        "trail_segment_end_idx": trail_seg_end,
        "segments_count": len(segments),
        "engine": "access_clarity_engine_v7",
    }

    logger.info(
        f"clarity_v7: {total_distance:.0f}m, trail={trail_pct}%, "
        f"clarity={clarity['score']}/{clarity['grade']}, "
        f"coords={len(coords_list)}, algo={routing_algo}"
    )

    return result


def _direct_fallback(start_lat, start_lng, stand_lat, stand_lng) -> dict:
    """Fallback direct quand aucun chemin n'est trouve."""
    dist = _haversine(start_lat, start_lng, stand_lat, stand_lng)
    return {
        "coords": [
            {
                "lat": round(start_lat, 7), "lng": round(start_lng, 7),
                "trail_distance_m": round(dist),
                "trail_type": "estimation",
                "routing_algo": "direct_fallback",
                "clarity_score": 5,
                "clarity_grade": "F",
            },
            {"lat": round(stand_lat, 7), "lng": round(stand_lng, 7)},
        ],
        "distance_m": round(dist),
        "clarity_score": 5,
        "clarity_grade": "F",
        "clarity_components": {"trail_ratio": 0, "smoothness": 5, "directness": 0, "safety": 0},
        "trail_percentage": 0,
        "routing_algo": "direct_fallback",
        "trail_type": "estimation",
        "phase1_distance_m": 0,
        "phase2_distance_m": round(dist),
        "junction": None,
        "trail_segment_end_idx": 0,
        "segments_count": 0,
        "engine": "access_clarity_engine_v7_fallback",
    }


def _haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
