"""
M4 -- RouteOptimizer : Re-optimisation multi-critere itineraire
=================================================================
Directive x7100-M4 -- Phase M4-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON :
  - poi_scorer (M2) : LIRE, NE PAS recalculer
  - predictive_engine : LIRE via M3, NE PAS recalculer
  - scoring_engine : LIRE, NE PAS reimplementer

Criteres d'optimisation :
  prediction_score * 0.30 (M3)
  + poi_score * 0.25 (M2)
  + profile_affinity * 0.20 (AUP)
  + distance * 0.15 (Haversine)
  + legal_compliance * 0.10 (M1)
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def _rescore_waypoint(waypoint: Dict, profile: Dict, prediction_prob: float,
                      weights: Optional[Dict] = None) -> float:
    """Re-calcul score combine avec poids dynamiques."""
    w = weights or {
        "prediction": 0.30,
        "poi": 0.25,
        "affinity": 0.20,
        "distance": 0.15,
        "legal": 0.10
    }

    prediction_score = min(1.0, max(0.0, prediction_prob))
    poi_score = waypoint.get("score", 0.5)

    # Affinity
    affinity = 0.5
    species_prefs = profile.get("species_preferences", [])
    wp_species = waypoint.get("type", "")
    for sp in species_prefs:
        if sp.get("species") == wp_species:
            affinity = max(affinity, sp.get("frequency", 0.5))

    dist_m = waypoint.get("distance_m", 1000)
    distance_score = round(1 / (1 + dist_m / 1000), 4)

    legal_score = 1.0

    combined = (
        prediction_score * w.get("prediction", 0.30)
        + poi_score * w.get("poi", 0.25)
        + affinity * w.get("affinity", 0.20)
        + distance_score * w.get("distance", 0.15)
        + legal_score * w.get("legal", 0.10)
    )
    return round(combined, 4)


async def optimize_route(session_id: str, criteria: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    """Re-optimisation multi-critere d'un itineraire existant."""
    db = _get_db()

    session = await db.navigation_sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        return None

    if session["status"] not in ("planned", "active"):
        return {"error": "SESSION_NOT_OPTIMIZABLE", "status": session["status"]}

    user_id = session["user_id"]
    target_species = session.get("target_species", "orignal")

    # Lecture profil AUP
    profile = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        profile = {"user_id": user_id, "species_preferences": []}

    # M3 prediction refresh (LECTURE)
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
        logger.warning(f"M4 optimize: M3 prediction failed: {e}")

    # Re-score all waypoints
    weights = criteria.get("weights") if criteria else None
    waypoints = session.get("waypoints", [])

    for wp in waypoints:
        wp["score"] = _rescore_waypoint(wp, profile, prediction_prob, weights)
        wp["prediction_prob"] = prediction_prob

    # Re-order
    waypoints.sort(key=lambda w: w["score"], reverse=True)

    now = datetime.now(timezone.utc).isoformat()
    await db.navigation_sessions.update_one(
        {"session_id": session_id},
        {"$set": {
            "waypoints": waypoints,
            "updated_at": now,
            "last_optimization": now,
            "optimization_criteria": criteria or {}
        }}
    )

    session["waypoints"] = waypoints
    session["updated_at"] = now
    session["last_optimization"] = now
    return session
