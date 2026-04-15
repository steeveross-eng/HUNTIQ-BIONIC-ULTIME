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
from datetime import datetime, timezone
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

    # Nutrition V7 enrichissement au centre
    nutrition_v7_center = None
    try:
        from modules.nutrition_engine_v7.pipeline import compute_attractiveness_v7
        _season_map = {1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps", 5: "printemps",
                       6: "ete", 7: "ete", 8: "ete", 9: "pre_rut", 10: "rut", 11: "post_rut", 12: "hiver"}
        nv7 = compute_attractiveness_v7(lat, lon, species, _season_map.get(month, "automne"), month, include_temporal=False)
        nutrition_v7_center = {
            "attractiveness": nv7.get("attractiveness_score"),
            "rating": nv7.get("rating"),
        }
    except Exception:
        pass

    return {
        "points": points,
        "center": {"lat": lat, "lng": lon},
        "grid_size": grid_size,
        "radius_km": radius_km,
        "species": species,
        "nutrition_v7": nutrition_v7_center,
        "compute_ms": elapsed,
        "engine": "CARTE-2027-HEATMAP-V7-NUTRITION",
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
    """Donnees vent temps reel pour carte terrain (ECCC/NOAA via Open-Meteo)."""
    import httpx

    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    try:
        params = {
            "latitude": lat, "longitude": lon,
            "current": "wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,surface_pressure,relative_humidity_2m,precipitation,cloud_cover",
            "timezone": "auto", "forecast_days": 1,
        }
        async with httpx.AsyncClient(timeout=4) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
            raw = resp.json()
        c = raw.get("current", {})
        direction = c.get("wind_direction_10m", 0)
        speed = c.get("wind_speed_10m", 0)
        gusts = c.get("wind_gusts_10m", 0)
        compass_dirs = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
        compass = compass_dirs[int(direction / 45) % 8] if direction is not None else "N"
        impact = "favorable" if speed and speed < 15 else "moderee" if speed and speed < 25 else "defavorable"

        return {
            "direction_deg": round(direction) if direction else 0,
            "speed_kmh": round(speed, 1) if speed else 0,
            "gusts_kmh": round(gusts, 1) if gusts else 0,
            "compass": compass,
            "hunting_impact": impact,
            "temperature_c": c.get("temperature_2m"),
            "pressure_hpa": c.get("surface_pressure"),
            "humidity_pct": c.get("relative_humidity_2m"),
            "precipitation_mm": c.get("precipitation"),
            "cloud_cover_pct": c.get("cloud_cover"),
            "source": "ECCC/NOAA/GFS-realtime",
            "engine": "CARTE-2027-WIND-V7-REALTIME",
        }
    except Exception as e:
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
            "source": "fallback-simulated",
            "engine": "CARTE-2027-WIND-V7-FALLBACK",
        }


@router.get("/corridors-overlay")
async def carte2027_corridors(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    radius_km: float = Query(10),
    month: int = Query(None), day: int = Query(None), hour: int = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Corridors de mouvement V7 avec ponderation temporelle + solunaire."""
    now = datetime.now(timezone.utc)
    m = month if month else now.month
    d = day if day else now.day
    h = hour if hour else now.hour
    doy = (m - 1) * 30 + d

    # V7 temporal weight
    crepuscular = species in ["cerf", "orignal", "wapiti", "caribou"]
    temporal_mult = 1.3 if (5 <= h <= 8 or 16 <= h <= 19) and crepuscular else 0.7 if 10 <= h <= 14 else 1.0

    # V7 solunar weight
    phase = abs(((doy % 29.53) / 29.53) * 2 - 1)
    solunar_mult = 1.2 if phase < 0.15 else 0.85 if 0.4 < phase < 0.6 else 1.0

    # V7 rut weight
    rut_peaks = {"cerf": 310, "orignal": 275, "wapiti": 280, "dindon_sauvage": 130}
    peak = rut_peaks.get(species, 300)
    rut_dist = abs(doy - peak)
    rut_mult = 1.4 if rut_dist < 10 else 1.1 if rut_dist < 30 else 0.9

    corridors = []
    step = radius_km / 111.0 / 4

    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        start_lat = lat + math.sin(rad) * step * 0.3
        start_lon = lon + math.cos(rad) * step * 0.3 / math.cos(math.radians(lat))
        end_lat = lat + math.sin(rad) * step * 2.2
        end_lon = lon + math.cos(rad) * step * 2.2 / math.cos(math.radians(lat))

        base_intensity = 0.25 + abs(math.sin(angle * 0.05 + lat)) * 0.55
        # V7 ponderation multi-facteur
        v7_intensity = min(1.0, base_intensity * temporal_mult * solunar_mult * rut_mult)

        corridors.append({
            "id": f"corridor_v7_{i}",
            "start": {"lat": round(start_lat, 5), "lng": round(start_lon, 5)},
            "end": {"lat": round(end_lat, 5), "lng": round(end_lon, 5)},
            "intensity": round(v7_intensity, 2),
            "base_intensity": round(base_intensity, 2),
            "v7_multiplier": round(temporal_mult * solunar_mult * rut_mult, 2),
            "species": species,
            "type": "primary" if v7_intensity > 0.6 else "secondary",
            "v7_weights": {
                "temporal": round(temporal_mult, 2),
                "solunar": round(solunar_mult, 2),
                "rut": round(rut_mult, 2),
            },
        })

    corridors.sort(key=lambda c: c["intensity"], reverse=True)

    return {
        "corridors": corridors,
        "total": len(corridors),
        "species": species,
        "v7_conditions": {"month": m, "day": d, "hour": h, "doy": doy},
        "engine": "CARTE-2027-CORRIDORS-V7-TEMPORAL",
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
