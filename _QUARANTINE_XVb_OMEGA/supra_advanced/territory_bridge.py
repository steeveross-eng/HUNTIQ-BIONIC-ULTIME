"""
SUPRA-REACT-Omega: Territory IA Data Provider for SUPRA v2
============================================================
Fournit les donnees IA Vision, cameras et affuts au moteur SUPRA.
Reconnexion TERRITOIRE + Analyse Territoire + CARTE → SUPRA.
"""
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("bionic.supra_territory_bridge")

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


async def get_territory_ia_data(lat: float, lng: float, species: str, user_id: str = None) -> Dict:
    """
    SUPRA-REACT-Omega: Charge TOUTES les donnees territoriales IA pour un point.
    Retourne un bloc enrichi contenant:
    - Cameras proches
    - Analyses IA Vision
    - Hotspots IA
    - Trajectoires IA
    - Affuts IA
    - Observations
    - Waypoints proches
    """
    db = _get_db()
    result = {
        "cameras": [],
        "vision_analyses": [],
        "hotspots": [],
        "trajectories": [],
        "affuts_ia": [],
        "observations_count": 0,
        "nearby_waypoints": [],
        "species_detections": [],
        "territory_score": None,
    }

    try:
        # 1. Cameras dans un rayon de 5km
        cameras_cursor = db['cameras'].find(
            {"status": "active",
             "location": {
                 "$near": {
                     "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                     "$maxDistance": 5000
                 }
             }},
            {"_id": 0, "id": 1, "name": 1, "manufacturer": 1, "model": 1,
             "camera_type": 1, "gps_lat": 1, "gps_lon": 1, "photo_count": 1, "status": 1}
        ).limit(20)
        try:
            result["cameras"] = await cameras_cursor.to_list(length=20)
        except Exception:
            # Fallback si pas de 2dsphere index ou pas de cameras
            if user_id:
                cam_cursor = db['cameras'].find(
                    {"user_id": user_id, "status": "active"},
                    {"_id": 0, "id": 1, "name": 1, "manufacturer": 1, "model": 1,
                     "camera_type": 1, "gps_lat": 1, "gps_lon": 1, "photo_count": 1}
                ).limit(20)
                result["cameras"] = await cam_cursor.to_list(length=20)

        # 2. Analyses IA Vision recentes
        vision_query = {}
        if user_id:
            vision_query["user_id"] = user_id
        if species:
            vision_query["species"] = species

        analyses_cursor = db['vision_analyses'].find(
            vision_query,
            {"_id": 0, "species": 1, "alpha_score": 1, "camera_id": 1,
             "analyzed_at": 1, "gps_lat": 1, "gps_lon": 1, "confidence": 1}
        ).sort("analyzed_at", -1).limit(50)
        result["vision_analyses"] = await analyses_cursor.to_list(length=50)

        # 3. Hotspots IA
        hotspots_query = {}
        if user_id:
            hotspots_query["user_id"] = user_id
        hotspots_cursor = db['vision_hotspots'].find(
            hotspots_query,
            {"_id": 0, "id": 1, "score": 1, "dominant_species": 1, "species": 1,
             "gps_lat": 1, "gps_lon": 1, "total_sightings": 1, "activity_level": 1}
        ).sort("score", -1).limit(20)
        result["hotspots"] = await hotspots_cursor.to_list(length=20)

        # 4. Trajectoires IA
        traj_query = {}
        if user_id:
            traj_query["user_id"] = user_id
        traj_cursor = db['vision_trajectories'].find(
            traj_query,
            {"_id": 0, "id": 1, "species": 1, "points": 1, "confidence": 1, "created_at": 1}
        ).sort("created_at", -1).limit(10)
        result["trajectories"] = await traj_cursor.to_list(length=10)

        # 5. Affuts IA generes
        affuts_query = {"score": {"$gte": 30}}
        if user_id:
            affuts_query["user_id"] = user_id
        affuts_cursor = db['affuts_ia'].find(
            affuts_query,
            {"_id": 0, "id": 1, "lat": 1, "lon": 1, "score": 1, "stand_name_fr": 1,
             "species": 1, "saline_distance_m": 1, "justification": 1}
        ).sort("score", -1).limit(10)
        result["affuts_ia"] = await affuts_cursor.to_list(length=10)

        # 6. Detections especes (aggregation)
        species_pipeline = [
            {"$match": {**({} if not user_id else {"user_id": user_id}), "species": {"$nin": [None, "", "aucun_animal"]}}},
            {"$group": {"_id": "$species", "count": {"$sum": 1}, "last_seen": {"$max": "$analyzed_at"}, "avg_alpha": {"$avg": "$alpha_score"}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        species_agg = await db['vision_analyses'].aggregate(species_pipeline).to_list(length=10)
        result["species_detections"] = [
            {"species": s["_id"], "count": s["count"], "last_seen": s.get("last_seen"), "avg_alpha": round(s.get("avg_alpha") or 0, 1)}
            for s in species_agg
        ]

        # 7. Nombre d'observations (events)
        if user_id:
            result["observations_count"] = await db['camera_events'].count_documents({"user_id": user_id})

    except Exception as e:
        logger.warning(f"[SUPRA-TERRITORY] Error loading territory IA data: {e}")

    return result
