"""
M2 — POI Relation Resolver : Relations spatiales, clusters, proximite
=======================================================================
Directive x6900-M2 — Phase M2-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : NE recree PAS geospatial_engine, geo_engine.
Utilise uniquement Haversine basique dans M2.
"""

import os
import math
import logging
from typing import Dict, Any, List, Optional
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


def haversine_distance(lat1: float, lng1: float,
                       lat2: float, lng2: float) -> float:
    """Distance Haversine entre 2 points (metres)."""
    R = 6371000  # rayon Terre en metres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


async def find_near(lat: float, lng: float, radius_m: float = 5000,
                    type_filter: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
    """POIs a proximite d'un point avec distances."""
    db = _get_db()

    query = {
        "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": radius_m
            }
        }
    }
    if type_filter:
        query["type"] = type_filter

    cursor = db.poi_nodes.find(query, {"_id": 0}).limit(limit)
    pois = await cursor.to_list(limit)

    results = []
    for poi in pois:
        coords = poi.get("location", {}).get("coordinates", [0, 0])
        dist = haversine_distance(lat, lng, coords[1], coords[0])
        results.append({
            **poi,
            "distance_m": round(dist, 1),
            "bearing_deg": _compute_bearing(lat, lng, coords[1], coords[0])
        })

    results.sort(key=lambda x: x["distance_m"])
    return results


def _compute_bearing(lat1: float, lng1: float,
                     lat2: float, lng2: float) -> float:
    """Calcul de l'azimut entre deux points."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dl = math.radians(lng2 - lng1)
    x = math.sin(dl) * math.cos(phi2)
    y = (math.cos(phi1) * math.sin(phi2) -
         math.sin(phi1) * math.cos(phi2) * math.cos(dl))
    bearing = math.degrees(math.atan2(x, y))
    return round((bearing + 360) % 360, 1)


async def compute_cluster(lat: float, lng: float,
                          radius_m: float = 5000) -> Dict[str, Any]:
    """Analyse de cluster dans un rayon."""
    db = _get_db()

    query = {
        "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": radius_m
            }
        }
    }

    cursor = db.poi_nodes.find(query, {"_id": 0}).limit(100)
    pois = await cursor.to_list(100)

    if not pois:
        return {
            "center": {"lat": lat, "lng": lng},
            "radius_m": radius_m,
            "poi_count": 0,
            "types": {},
            "density": 0.0,
            "avg_score": 0.0,
            "pois": [],
            "isolated_count": 0
        }

    # Analyse par type
    type_counts = {}
    total_score = 0.0
    isolated = 0
    enriched_pois = []

    for poi in pois:
        t = poi.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
        total_score += poi.get("score", {}).get("global", 0.0)
        if not poi.get("connections"):
            isolated += 1

        coords = poi.get("location", {}).get("coordinates", [0, 0])
        dist = haversine_distance(lat, lng, coords[1], coords[0])
        enriched_pois.append({
            "poi_id": poi["poi_id"],
            "name": poi.get("name", ""),
            "type": t,
            "distance_m": round(dist, 1),
            "score_global": poi.get("score", {}).get("global", 0.0),
            "connections": len(poi.get("connections", []))
        })

    enriched_pois.sort(key=lambda x: x["distance_m"])

    area_km2 = math.pi * (radius_m / 1000) ** 2
    density = len(pois) / area_km2 if area_km2 > 0 else 0

    return {
        "center": {"lat": lat, "lng": lng},
        "radius_m": radius_m,
        "poi_count": len(pois),
        "types": type_counts,
        "density_per_km2": round(density, 2),
        "avg_score": round(total_score / len(pois), 4) if pois else 0.0,
        "isolated_count": isolated,
        "pois": enriched_pois
    }


async def resolve_relations(poi_id: str) -> List[Dict[str, Any]]:
    """Relations spatiales d'un POI avec tous ses voisins connectes."""
    db = _get_db()

    poi = await db.poi_nodes.find_one({"poi_id": poi_id}, {"_id": 0})
    if not poi:
        return []

    connections = poi.get("connections", [])
    if not connections:
        return []

    cursor = db.poi_nodes.find(
        {"poi_id": {"$in": connections}},
        {"_id": 0}
    )
    connected_pois = await cursor.to_list(100)

    poi_coords = poi.get("location", {}).get("coordinates", [0, 0])
    relations = []

    for cp in connected_pois:
        cp_coords = cp.get("location", {}).get("coordinates", [0, 0])
        dist = haversine_distance(poi_coords[1], poi_coords[0],
                                  cp_coords[1], cp_coords[0])
        bearing = _compute_bearing(poi_coords[1], poi_coords[0],
                                   cp_coords[1], cp_coords[0])
        relations.append({
            "poi_id": cp["poi_id"],
            "name": cp.get("name", ""),
            "type": cp.get("type", ""),
            "distance_m": round(dist, 1),
            "bearing_deg": bearing,
            "score_global": cp.get("score", {}).get("global", 0.0)
        })

    relations.sort(key=lambda x: x["distance_m"])
    return relations


def compute_distance(poi_a: Dict, poi_b: Dict) -> float:
    """Distance Haversine entre 2 POIs."""
    a_coords = poi_a.get("location", {}).get("coordinates", [0, 0])
    b_coords = poi_b.get("location", {}).get("coordinates", [0, 0])
    return haversine_distance(a_coords[1], a_coords[0],
                              b_coords[1], b_coords[0])
