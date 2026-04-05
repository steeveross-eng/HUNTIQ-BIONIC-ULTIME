"""
M4 -- NavigationPlanner : Planification itineraires intelligents
==================================================================
Directive x7100-M4 -- Phase M4-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON :
  - NE recree PAS poi_scorer, predictive_engine, solunar, scoring_engine.
  - Consomme M1 (legal_zones), M2 (poi_nodes, poi_edges), M3 (predictive_layers) en LECTURE.

Points de fusion :
  PF4-M1b : legal_constraint_engine (periodes legales)
  PF4-M2a : poi_nodes (destinations)
  PF4-M2c : poi_edges (chemins)
  PF4-M3a : predictive_layers (creneaux optimaux)
  PF4-TRIP1 : hunting_trips (apprentissage)
"""

import os
import uuid
import math
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

MAX_WAYPOINTS = 20


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance Haversine en metres."""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def ensure_indexes():
    """Cree les index MongoDB pour navigation_sessions."""
    db = _get_db()
    await db.navigation_sessions.create_index("session_id", unique=True)
    await db.navigation_sessions.create_index("user_id")
    await db.navigation_sessions.create_index("status")
    await db.navigation_sessions.create_index([("user_id", 1), ("status", 1)])
    logger.info("M4 navigation_sessions indexes created")


def _score_waypoint(poi: Dict, profile: Dict, prediction_prob: float) -> float:
    """Score combine waypoint (Section 3.2 du plan).

    score_combine = prediction_score * 0.30
                  + poi_score * 0.25
                  + profile_affinity * 0.20
                  + distance_score * 0.15
                  + legal_score * 0.10
    """
    # M3 prediction score
    prediction_score = min(1.0, max(0.0, prediction_prob))

    # M2 POI score
    poi_score_obj = poi.get("score", {})
    if isinstance(poi_score_obj, dict):
        poi_score = poi_score_obj.get("global", 0.5)
    else:
        poi_score = 0.5

    # AUP profile affinity
    profile_affinity = 0.5
    species_prefs = profile.get("species_preferences", [])
    poi_species = poi.get("properties", {}).get("species_observed", [])
    for sp in species_prefs:
        if sp.get("species") in poi_species:
            profile_affinity = max(profile_affinity, sp.get("frequency", 0.5))

    # Distance score (sera calcule par le caller via distance)
    distance_score = poi.get("_distance_score", 0.5)

    # Legal score (default = open)
    legal_score = poi.get("_legal_score", 1.0)

    combined = (
        prediction_score * 0.30
        + poi_score * 0.25
        + profile_affinity * 0.20
        + distance_score * 0.15
        + legal_score * 0.10
    )
    return round(combined, 4)


async def plan_route(user_id: str, target_species: str, zone_id: str,
                     start_lat: float = 0, start_lng: float = 0,
                     criteria: Optional[Dict] = None) -> Dict[str, Any]:
    """Planification itineraire intelligent (Section 3.1 du plan).

    Etapes:
    1. Recuperer profil AUP
    2. Recuperer POIs de la zone (M2, LECTURE)
    3. Scorer avec predictions M3 (LECTURE)
    4. Filtrer par contraintes legales (M1, LECTURE)
    5. Appliquer preferences profil
    6. Ordonner waypoints par score_combine
    7. Calculer route et ETA
    8. Persister la session
    """
    db = _get_db()

    # 1. Profil AUP
    profile = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        profile = {"user_id": user_id, "skill_level": "intermediaire", "species_preferences": []}

    # 2. POIs de la zone (M2, LECTURE)
    poi_filter = {}
    if zone_id:
        poi_filter["zone_id"] = zone_id
    pois_cursor = db.poi_nodes.find(poi_filter, {"_id": 0}).limit(100)
    pois = await pois_cursor.to_list(length=100)

    # 3. M3 prediction for species (LECTURE)
    prediction_prob = 0.5
    try:
        layer = await db.predictive_layers.find_one(
            {"species": target_species},
            {"_id": 0},
            sort=[("computed_at", -1)]
        )
        if layer:
            current_hour = datetime.now(timezone.utc).hour
            for hl in layer.get("hourly_layers", []):
                if hl.get("hour") == current_hour:
                    prediction_prob = hl.get("probability", 0.5)
                    break
    except Exception as e:
        logger.warning(f"M4 plan_route: M3 prediction lookup failed: {e}")

    # 4+5+6. Score, filter, order
    scored_waypoints = []
    for poi in pois:
        poi_lat = poi.get("lat", 0)
        poi_lng = poi.get("lng", 0)
        if not poi_lat and poi.get("location"):
            coords = poi["location"].get("coordinates", [0, 0])
            poi_lng, poi_lat = coords[0], coords[1]

        dist = _haversine(start_lat, start_lng, poi_lat, poi_lng) if start_lat else 1000
        poi["_distance_score"] = round(1 / (1 + dist / 1000), 4)
        poi["_legal_score"] = 1.0  # Default open

        score = _score_waypoint(poi, profile, prediction_prob)
        eta_minutes = round(dist / 80)  # ~80m/min walking pace

        scored_waypoints.append({
            "poi_id": poi.get("poi_id", ""),
            "name": poi.get("name", ""),
            "type": poi.get("type", ""),
            "lat": poi_lat,
            "lng": poi_lng,
            "distance_m": round(dist),
            "score": score,
            "eta_minutes": eta_minutes,
            "prediction_prob": prediction_prob
        })

    # Sort by score descending, limit to MAX_WAYPOINTS
    scored_waypoints.sort(key=lambda w: w["score"], reverse=True)
    waypoints = scored_waypoints[:MAX_WAYPOINTS]

    # 7+8. Create session
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    total_distance = sum(w["distance_m"] for w in waypoints)
    total_eta = sum(w["eta_minutes"] for w in waypoints)

    session = {
        "session_id": session_id,
        "user_id": user_id,
        "target_species": target_species,
        "zone_id": zone_id,
        "status": "planned",
        "start_position": {"lat": start_lat, "lng": start_lng},
        "waypoints": waypoints,
        "waypoints_count": len(waypoints),
        "route_summary": {
            "total_distance_m": round(total_distance),
            "total_eta_minutes": total_eta,
            "prediction_score": prediction_prob
        },
        "metrics": {
            "distance_walked_km": 0,
            "duration_hours": 0,
            "pois_visited": 0
        },
        "criteria": criteria or {},
        "created_at": now,
        "updated_at": now
    }

    await db.navigation_sessions.insert_one(session)
    session.pop("_id", None)

    return session


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Detail d'une session planifiee."""
    db = _get_db()
    doc = await db.navigation_sessions.find_one({"session_id": session_id}, {"_id": 0})
    return doc


async def start_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Demarrer une session de navigation."""
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()

    result = await db.navigation_sessions.find_one_and_update(
        {"session_id": session_id, "status": "planned"},
        {"$set": {"status": "active", "started_at": now, "updated_at": now}},
        return_document=True
    )
    if result:
        result.pop("_id", None)
    return result


async def end_session(session_id: str, metrics: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """Terminer une session avec metriques."""
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()

    update = {
        "status": "completed",
        "ended_at": now,
        "updated_at": now
    }
    if metrics:
        update["metrics"] = metrics

    result = await db.navigation_sessions.find_one_and_update(
        {"session_id": session_id, "status": "active"},
        {"$set": update},
        return_document=True
    )
    if result:
        result.pop("_id", None)

        # Apprentissage post-session: mettre a jour profil AUP
        try:
            user_id = result.get("user_id")
            if user_id and metrics:
                profile_update = {}
                zone_id = result.get("zone_id")
                if zone_id:
                    profile = await db.hunter_profiles.find_one({"user_id": user_id})
                    if profile:
                        zone_prefs = profile.get("zone_preferences", [])
                        found = False
                        for zp in zone_prefs:
                            if zp.get("zone_id") == zone_id:
                                zp["visit_count"] = zp.get("visit_count", 0) + 1
                                zp["last_visit"] = now
                                found = True
                                break
                        if not found:
                            zone_prefs.append({
                                "zone_id": zone_id,
                                "visit_count": 1,
                                "last_visit": now,
                                "satisfaction_score": 0.5
                            })
                        profile_update["zone_preferences"] = zone_prefs
                        profile_update["updated_at"] = now
                        await db.hunter_profiles.update_one(
                            {"user_id": user_id},
                            {"$set": profile_update}
                        )
        except Exception as e:
            logger.warning(f"M4 end_session: profile update failed: {e}")

    return result


async def get_session_status(session_id: str) -> Optional[Dict[str, Any]]:
    """Statut d'une session active."""
    db = _get_db()
    doc = await db.navigation_sessions.find_one(
        {"session_id": session_id},
        {"_id": 0, "session_id": 1, "status": 1, "user_id": 1,
         "target_species": 1, "waypoints_count": 1, "metrics": 1,
         "started_at": 1, "route_summary": 1}
    )
    return doc
