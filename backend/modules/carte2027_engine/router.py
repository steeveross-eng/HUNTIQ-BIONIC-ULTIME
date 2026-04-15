"""
CARTE-2027-REBUILD-Omega — Engine cartographique terrain V7
=============================================================
Endpoints pour generation de donnees cartographiques:
- Grille heatmap comportementale V7
- POI agregation
- Cameras terrain
- Corridors + zones

Derive de TERRITOIRE (L1) et INTELLIGENCE (L2).
Hierarchie: TERRITOIRE -> INTELLIGENCE -> CARTE 2027 (L3).
"""
import math
import time
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

logger = logging.getLogger("bionic.carte2027")
router = APIRouter(prefix="/api/v1/carte2027", tags=["Carte 2027 V7"])


def _moon_phase(doy: int) -> float:
    return abs(((doy % 29.53) / 29.53) * 2 - 1)


def _compute_v7_score_fast(lat: float, lon: float, species: str, month: int, day: int, hour: int, temp_c: float, wind_kmh: float):
    """Calcul rapide du score V7 pour un point de grille."""
    doy = (month - 1) * 30 + day
    crepuscular = species in ["cerf", "orignal", "wapiti", "caribou"]

    temporal = 90 if (5 <= hour <= 8 or 16 <= hour <= 19) and crepuscular else 50
    phase = _moon_phase(doy)
    lunar = 85 if phase < 0.1 else 60 if 0.4 < phase < 0.6 else 70
    meteo = max(20, 80 - abs(temp_c - 10) * 2 - wind_kmh * 0.5)
    rut_peaks = {"cerf": 310, "orignal": 275, "wapiti": 280}
    peak = rut_peaks.get(species, 300)
    rut = max(20, 100 - abs(doy - peak) * 2)

    # Habitat variance basee sur lat/lon
    lat_var = math.sin(lat * 7.3) * 15
    lon_var = math.cos(lon * 5.1) * 12
    habitat = max(20, min(95, 65 + lat_var + lon_var))

    weights = {"temporal": 0.20, "lunar": 0.10, "meteo": 0.15, "habitat": 0.20, "rut": 0.20, "pressure": 0.15}
    pressure = 40 if month in [9, 10, 11] else 70
    scores = {"temporal": temporal, "lunar": lunar, "meteo": meteo, "habitat": habitat, "rut": rut, "pressure": pressure}

    return round(min(100, max(0, sum(scores[k] * w for k, w in weights.items()))), 1)


@router.get("/heatmap-grid")
async def carte2027_heatmap_grid(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(10), day: int = Query(15),
    hour: int = Query(8), temp_c: float = Query(8), wind_kmh: float = Query(12),
    grid_size: int = Query(12, ge=5, le=25),
    radius_km: float = Query(15, ge=5, le=50),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Genere grille heatmap comportementale V7 pour carte terrain."""
    start = time.time()
    points = []
    step_deg = (radius_km / 111.0) / (grid_size / 2)

    for i in range(grid_size):
        for j in range(grid_size):
            pt_lat = lat + (i - grid_size / 2) * step_deg
            pt_lon = lon + (j - grid_size / 2) * step_deg * (1.0 / math.cos(math.radians(lat)))
            score = _compute_v7_score_fast(pt_lat, pt_lon, species, month, day, hour, temp_c, wind_kmh)
            points.append({"lat": round(pt_lat, 5), "lng": round(pt_lon, 5), "score": score, "probability": round(score / 100, 2)})

    elapsed = round((time.time() - start) * 1000)
    return {
        "points": points,
        "center": {"lat": lat, "lng": lon},
        "grid_size": grid_size,
        "radius_km": radius_km,
        "species": species,
        "compute_ms": elapsed,
        "engine": "CARTE-2027-HEATMAP-V7",
    }


@router.get("/poi")
async def carte2027_poi(
    lat: float = Query(...), lon: float = Query(...),
    radius_km: float = Query(20, ge=1, le=100),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Agregation POI terrain: cameras, waypoints, salines."""
    pois = []

    # Cameras
    cameras = await db["cameras"].find(
        {"user_id": user.user_id},
        {"_id": 0, "name": 1, "brand": 1, "lat": 1, "lng": 1, "status": 1}
    ).to_list(200)
    for cam in cameras:
        if cam.get("lat") and cam.get("lng"):
            pois.append({
                "type": "camera",
                "name": cam.get("name", "Camera"),
                "lat": cam["lat"], "lng": cam["lng"],
                "meta": {"brand": cam.get("brand", ""), "status": cam.get("status", "active")},
            })

    # Waypoints
    waypoints = await db["waypoints"].find(
        {"user_id": user.user_id},
        {"_id": 0, "name": 1, "lat": 1, "lng": 1, "type": 1, "notes": 1}
    ).to_list(500)
    for wp in waypoints:
        if wp.get("lat") and wp.get("lng"):
            pois.append({
                "type": "waypoint",
                "name": wp.get("name", "Point"),
                "lat": wp["lat"], "lng": wp["lng"],
                "meta": {"wp_type": wp.get("type", ""), "notes": wp.get("notes", "")},
            })

    # Salines
    salines = await db["salines"].find(
        {"user_id": user.user_id},
        {"_id": 0, "name": 1, "lat": 1, "lng": 1, "type": 1, "score": 1}
    ).to_list(200)
    for sal in salines:
        if sal.get("lat") and sal.get("lng"):
            pois.append({
                "type": "saline",
                "name": sal.get("name", "Saline"),
                "lat": sal["lat"], "lng": sal["lng"],
                "meta": {"sal_type": sal.get("type", ""), "score": sal.get("score", 0)},
            })

    return {
        "pois": pois,
        "total": len(pois),
        "center": {"lat": lat, "lng": lon},
        "engine": "CARTE-2027-POI-V7",
    }


@router.get("/wind")
async def carte2027_wind(
    lat: float = Query(...), lon: float = Query(...),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Donnees vent pour carte terrain."""
    # Simulation basee sur heure et position
    import random
    random.seed(int(lat * 100) + int(lon * 100))
    direction = random.randint(0, 359)
    speed = round(random.uniform(5, 30), 1)
    gusts = round(speed * random.uniform(1.2, 1.8), 1)

    return {
        "direction_deg": direction,
        "speed_kmh": speed,
        "gusts_kmh": gusts,
        "compass": ["N", "NE", "E", "SE", "S", "SO", "O", "NO"][direction // 45 % 8],
        "hunting_impact": "favorable" if speed < 15 else "moderee" if speed < 25 else "defavorable",
        "engine": "CARTE-2027-WIND-V7",
    }


@router.get("/corridors-overlay")
async def carte2027_corridors(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    radius_km: float = Query(10),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Corridors de mouvement pour overlay carte."""
    corridors = []
    step = radius_km / 111.0 / 4

    for i in range(6):
        angle = i * 60
        rad = math.radians(angle)
        start_lat = lat + math.sin(rad) * step * 0.5
        start_lon = lon + math.cos(rad) * step * 0.5 / math.cos(math.radians(lat))
        end_lat = lat + math.sin(rad) * step * 2
        end_lon = lon + math.cos(rad) * step * 2 / math.cos(math.radians(lat))

        intensity = 0.3 + abs(math.sin(angle * 0.05 + lat)) * 0.7
        corridors.append({
            "id": f"corridor_{i}",
            "start": {"lat": round(start_lat, 5), "lng": round(start_lon, 5)},
            "end": {"lat": round(end_lat, 5), "lng": round(end_lon, 5)},
            "intensity": round(intensity, 2),
            "species": species,
            "type": "primary" if intensity > 0.6 else "secondary",
        })

    return {
        "corridors": corridors,
        "total": len(corridors),
        "species": species,
        "engine": "CARTE-2027-CORRIDORS-V7",
    }


@router.get("/zones-legales")
async def carte2027_zones_legales(
    province: str = Query("qc"),
    species: str = Query("cerf"),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Zones legales de chasse par province."""
    zones_db = {
        "qc": [
            {"id": "zone1", "name": "Zone 1 - Bas-Saint-Laurent", "bounds": [[47.0, -69.5], [48.5, -67.0]], "status": "ouverte", "quota": "illimite"},
            {"id": "zone2", "name": "Zone 2 - Saguenay", "bounds": [[47.5, -72.0], [49.0, -70.0]], "status": "ouverte", "quota": "contingente"},
            {"id": "zone3", "name": "Zone 3 - Capitale-Nationale", "bounds": [[46.5, -72.0], [47.5, -70.5]], "status": "ouverte", "quota": "illimite"},
            {"id": "zone6", "name": "Zone 6 - Outaouais", "bounds": [[45.5, -77.0], [47.0, -75.0]], "status": "ouverte", "quota": "contingente"},
            {"id": "zone7", "name": "Zone 7 - Laurentides", "bounds": [[45.8, -75.5], [47.5, -73.5]], "status": "ouverte", "quota": "illimite"},
            {"id": "zone9", "name": "Zone 9 - Mauricie", "bounds": [[46.0, -73.5], [47.5, -72.0]], "status": "ouverte", "quota": "illimite"},
            {"id": "zone10", "name": "Zone 10 - Lanaudiere", "bounds": [[46.0, -74.0], [47.0, -73.0]], "status": "ouverte", "quota": "contingente"},
        ],
        "on": [
            {"id": "wmu65", "name": "WMU 65 - Simcoe", "bounds": [[44.0, -80.5], [45.0, -79.0]], "status": "ouverte", "quota": "illimite"},
            {"id": "wmu49", "name": "WMU 49 - Algonquin", "bounds": [[45.0, -79.0], [46.5, -77.5]], "status": "ouverte", "quota": "contingente"},
        ],
    }

    zones = zones_db.get(province, [])
    return {
        "zones": zones,
        "province": province,
        "species": species,
        "total": len(zones),
        "engine": "CARTE-2027-ZONES-LEGALES-V7",
    }
