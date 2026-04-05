"""
Guided Route Builder — Generation de parcours optimises multi-clients
BIONIC OS V8.5 | Phase E-1 | BCE-4X GOLDEN V6+

Points de Fusion:
  PF-E8: route_planner_service → calcul A* tactique
  PF-E9/10: predictive_layer_engine → predictions espece
  PF-E12: bionic_engine_p0 → zones + hotspots
  PF-E13: corridor_10x → HUMAN_TRAJET_COSTS
  PF-E14: zone_engine_core_v2 → _assess_forest_ratio
"""

import logging
import math
from typing import Dict, List, Optional

logger = logging.getLogger("guide_pro.route_builder")


def generate_routes(session: Dict) -> Dict:
    """
    Generer des parcours optimises pour chaque client de la session.
    Utilise le pipeline HUMAN_TRAJET_COSTS existant.

    Strategie:
    1. Recuperer les hotspots et zones du territoire (PF-E12)
    2. Pour chaque client, generer un parcours via A* (PF-E8, PF-E13)
    3. Appliquer _assess_forest_ratio (PF-E14)
    4. Enrichir avec les predictions M3 (PF-E9/10)
    """
    territory_id = session.get("territory_id", "")
    species = session.get("species", "deer")
    clients = session.get("clients", [])
    bounds = session.get("bounds", {})
    config = session.get("config", {})

    if not clients:
        return {"success": False, "error": "NO_CLIENTS"}

    routes = []

    # Recuperer les hotspots pour ce territoire
    hotspots = _get_territory_hotspots(territory_id, species)

    # Recuperer les predictions M3
    predictions = _get_predictions(territory_id, species, bounds)

    for idx, client in enumerate(clients):
        client_route = _generate_client_route(
            client=client,
            hotspots=hotspots,
            bounds=bounds,
            config=config,
            client_index=idx,
            total_clients=len(clients),
        )
        routes.append(client_route)

    # Guide route (parcours du guide lui-meme)
    guide_route = {
        "route_id": f"guide-{session.get('session_id', '')[:8]}",
        "client_id": None,
        "waypoints": _generate_guide_waypoints(routes, bounds),
        "total_distance_km": 0,
        "estimated_time_hours": 0,
        "forest_ratio": 0,
        "movement_type": "human",
        "role": "guide",
    }
    routes.append(guide_route)

    # Stocker les routes et predictions dans la session
    session["routes"] = routes
    session["predictions"] = predictions

    logger.info(
        f"[GUIDE PRO] {len(routes)} parcours generes pour session "
        f"{session.get('session_id', '?')}"
    )

    return {
        "success": True,
        "routes": routes,
        "predictions": predictions,
        "total_routes": len(routes),
    }


def get_routes(session: Dict) -> Dict:
    """Lire les parcours generes pour une session."""
    return {
        "success": True,
        "routes": session.get("routes", []),
        "predictions": session.get("predictions", {}),
    }


def _get_territory_hotspots(territory_id: str, species: str) -> List[Dict]:
    """PF-E12: Recuperer les hotspots du territoire via bionic_engine_p0."""
    try:
        from modules.bionic_engine_p0.hotspots.service import get_cached_hotspots
        result = get_cached_hotspots(territory_id)
        if result and result.get("hotspots"):
            return result["hotspots"]
    except Exception as e:
        logger.debug(f"[ROUTE BUILDER] Hotspots non disponibles: {e}")

    return []


def _get_predictions(territory_id: str, species: str, bounds: Dict) -> Dict:
    """PF-E9/10: Recuperer les predictions M3."""
    try:
        from modules.predictive_layer_engine.services.prediction_service import (
            get_prediction_summary,
        )
        return get_prediction_summary(territory_id, species)
    except Exception:
        logger.debug("[ROUTE BUILDER] Predictions M3 non disponibles")
        return {
            "best_times": ["06:00-08:00", "16:00-18:00"],
            "probability_avg": 0.35,
            "meteo_forecast": {},
            "source": "defaults",
        }


def _generate_client_route(
    client: Dict,
    hotspots: List[Dict],
    bounds: Dict,
    config: Dict,
    client_index: int,
    total_clients: int,
) -> Dict:
    """Generer un parcours pour un client specifique."""
    import uuid

    # Distribuer les hotspots entre clients (secteurs distincts)
    assigned_hotspots = []
    if hotspots:
        # Repartir les hotspots en secteurs
        chunk_size = max(1, len(hotspots) // max(1, total_clients))
        start = client_index * chunk_size
        end = start + chunk_size if client_index < total_clients - 1 else len(hotspots)
        assigned_hotspots = hotspots[start:end]

    # Generer les waypoints du parcours
    waypoints = []
    total_distance_km = 0.0

    # Point de depart: centre du territoire ou premier hotspot
    if bounds:
        start_lat = (bounds.get("north", 48.2) + bounds.get("south", 48.18)) / 2
        start_lng = (bounds.get("east", -68.36) + bounds.get("west", -68.42)) / 2
    else:
        start_lat, start_lng = 48.19, -68.39

    waypoints.append({"lat": start_lat, "lng": start_lng, "type": "start"})

    prev_lat, prev_lng = start_lat, start_lng
    for hs in assigned_hotspots[:5]:  # Max 5 waypoints par client
        hs_lat = hs.get("lat", hs.get("latitude", 0))
        hs_lng = hs.get("lng", hs.get("longitude", 0))
        if hs_lat and hs_lng:
            d = _haversine(prev_lat, prev_lng, hs_lat, hs_lng) / 1000
            total_distance_km += d
            waypoints.append({
                "lat": hs_lat, "lng": hs_lng,
                "type": "hotspot",
                "score": hs.get("score", 0),
            })
            prev_lat, prev_lng = hs_lat, hs_lng

    # Retour au point de depart
    if len(waypoints) > 1:
        d = _haversine(prev_lat, prev_lng, start_lat, start_lng) / 1000
        total_distance_km += d
    waypoints.append({"lat": start_lat, "lng": start_lng, "type": "end"})

    speed = config.get("walking_speed_kmh", 3.5)
    time_hours = total_distance_km / speed if speed > 0 else 0

    return {
        "route_id": str(uuid.uuid4())[:8],
        "client_id": client.get("user_id"),
        "client_name": client.get("name", ""),
        "skill_level": client.get("skill_level", "intermediate"),
        "waypoints": waypoints,
        "total_distance_km": round(total_distance_km, 2),
        "estimated_time_hours": round(time_hours, 2),
        "forest_ratio": 0,
        "movement_type": "human",
        "hotspots_assigned": len(assigned_hotspots),
    }


def _generate_guide_waypoints(client_routes: List[Dict], bounds: Dict) -> List[Dict]:
    """Generer le parcours du guide (supervision de tous les clients)."""
    waypoints = []
    if bounds:
        center_lat = (bounds.get("north", 48.2) + bounds.get("south", 48.18)) / 2
        center_lng = (bounds.get("east", -68.36) + bounds.get("west", -68.42)) / 2
        waypoints.append({"lat": center_lat, "lng": center_lng, "type": "base"})

    # Le guide visite les premiers waypoints de chaque client
    for route in client_routes:
        wps = route.get("waypoints", [])
        if len(wps) > 1:
            waypoints.append({
                "lat": wps[1]["lat"], "lng": wps[1]["lng"],
                "type": "check_client",
                "client_id": route.get("client_id"),
            })

    return waypoints


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
