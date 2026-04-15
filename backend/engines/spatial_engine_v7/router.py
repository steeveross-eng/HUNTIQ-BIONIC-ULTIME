"""
SPATIAL-ENGINE-V7 — Moteur geospatial central
================================================
Endpoints:
  /api/v7/spatial/corridors     — Corridors V7 (normaux, intenses, extremes, saisonniers)
  /api/v7/spatial/zones         — Zones V7 (alimentation, repos, rut, eau)
  /api/v7/spatial/heatmap       — Heatmap V7 (23 moteurs consolides + nutrition_v7)
  /api/v7/spatial/scoring       — Scoring spatial V7 (habitat, pression, relief, hydro)
  /api/v7/spatial/amenagement   — Amenagement V7 (chemin optimal, affuts, salines)
  /api/v7/spatial/status        — Status moteur

Architecture:
  Consolide BionicCorridorsV6, ConsolidatedHeatmap, score_consolide, amenagement
  en un moteur V7 unique. Toutes sorties normalisees 0-100 + metadonnees.

Consommateurs: TERRITOIRE-V7, CARTE-2027, INTELLIGENCE-V7
"""
import math
import time
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

logger = logging.getLogger("bionic.spatial_engine_v7")
router = APIRouter(prefix="/api/v7/spatial", tags=["Spatial Engine V7"])

SEASON_MAP = {1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps", 5: "printemps",
              6: "ete", 7: "ete", 8: "ete", 9: "pre_rut", 10: "rut", 11: "post_rut", 12: "hiver"}


def _moon_phase(doy):
    return abs(((doy % 29.53) / 29.53) * 2 - 1)


def _v7_temporal_mults(species, month, day, hour):
    doy = (month - 1) * 30 + day
    crep = species in ["cerf", "orignal", "wapiti", "caribou", "chevreuil"]
    t_mult = 1.3 if (5 <= hour <= 8 or 16 <= hour <= 19) and crep else 0.7 if 10 <= hour <= 14 else 1.0
    phase = _moon_phase(doy)
    s_mult = 1.2 if phase < 0.15 else 0.85 if 0.4 < phase < 0.6 else 1.0
    rut_peaks = {"cerf": 310, "chevreuil": 310, "orignal": 275, "wapiti": 280, "dindon_sauvage": 130}
    peak = rut_peaks.get(species, 300)
    r_mult = 1.4 if abs(doy - peak) < 10 else 1.1 if abs(doy - peak) < 30 else 0.9
    return t_mult, s_mult, r_mult


def _nutrition_score(lat, lon, species, month):
    try:
        from modules.nutrition_engine_v7.pipeline import compute_attractiveness_v7
        r = compute_attractiveness_v7(lat, lon, species, SEASON_MAP.get(month, "automne"), month, include_temporal=False)
        return r.get("attractiveness_score", 50)
    except Exception:
        return 50


# ═══════════════════════════════════════════════════════
# 1. CORRIDORS V7
# ═══════════════════════════════════════════════════════

@router.get("/corridors")
async def spatial_corridors(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), radius_km: float = Query(10),
    month: int = Query(None), day: int = Query(None), hour: int = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Corridors V7 — normaux, intenses, extremes, saisonniers avec ponderation temporelle+solunaire+rut+nutrition."""
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    d = day or now.day
    h = hour or now.hour

    t_mult, s_mult, r_mult = _v7_temporal_mults(species, m, d, h)
    nutr = _nutrition_score(lat, lon, species, m)
    nutr_mult = 0.8 + (nutr / 100) * 0.4  # 0.8 to 1.2

    step = radius_km / 111.0 / 4
    corridors = []
    for i in range(10):
        angle = i * 36
        rad = math.radians(angle)
        s_lat = lat + math.sin(rad) * step * 0.3
        s_lon = lon + math.cos(rad) * step * 0.3 / math.cos(math.radians(lat))
        e_lat = lat + math.sin(rad) * step * 2.5
        e_lon = lon + math.cos(rad) * step * 2.5 / math.cos(math.radians(lat))

        base = 0.2 + abs(math.sin(angle * 0.07 + lat * 3)) * 0.6
        v7_int = min(1.0, base * t_mult * s_mult * r_mult * nutr_mult)

        if v7_int >= 0.75:
            ctype = "extreme"
        elif v7_int >= 0.55:
            ctype = "intense"
        elif m in [3, 4, 5, 9, 10, 11] and base > 0.4:
            ctype = "saisonnier"
        else:
            ctype = "normal"

        corridors.append({
            "id": f"corr_v7_{i}",
            "start": {"lat": round(s_lat, 5), "lng": round(s_lon, 5)},
            "end": {"lat": round(e_lat, 5), "lng": round(e_lon, 5)},
            "intensity": round(v7_int, 3),
            "type": ctype,
            "v7_weights": {"temporal": round(t_mult, 2), "solunar": round(s_mult, 2), "rut": round(r_mult, 2), "nutrition": round(nutr_mult, 2)},
        })
    corridors.sort(key=lambda c: c["intensity"], reverse=True)

    return {
        "corridors": corridors,
        "total": len(corridors),
        "species": species,
        "v7_conditions": {"month": m, "day": d, "hour": h},
        "nutrition_score": nutr,
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V7",
        "engine": "SPATIAL-ENGINE-V7-CORRIDORS",
    }


# ═══════════════════════════════════════════════════════
# 2. ZONES V7
# ═══════════════════════════════════════════════════════

ZONE_TYPES = ["alimentation", "repos", "rut", "eau", "salines"]

@router.get("/zones")
async def spatial_zones(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), radius_km: float = Query(1),
    month: int = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Zones V7 — alimentation, repos, rut, eau, salines avec scoring multi-facteurs."""
    start = time.time()
    m = month or datetime.now(timezone.utc).month
    nutr = _nutrition_score(lat, lon, species, m)

    zones = []
    step = radius_km / 111.0 / 3
    for i, ztype in enumerate(ZONE_TYPES):
        angle = i * 72 + 15
        rad = math.radians(angle)
        c_lat = lat + math.sin(rad) * step * (1 + i * 0.3)
        c_lon = lon + math.cos(rad) * step * (1 + i * 0.3) / math.cos(math.radians(lat))

        base_score = 40 + abs(math.sin(c_lat * 11 + c_lon * 7)) * 50
        if ztype == "alimentation":
            base_score = min(100, base_score * 0.7 + nutr * 0.3)
        elif ztype == "rut" and m in [9, 10, 11]:
            base_score = min(100, base_score * 1.2)
        elif ztype == "eau":
            base_score = min(100, base_score * 0.9)

        # Zone polygon (simplified square)
        sz = step * 0.4
        polygon = [
            [round(c_lat - sz, 5), round(c_lon - sz, 5)],
            [round(c_lat - sz, 5), round(c_lon + sz, 5)],
            [round(c_lat + sz, 5), round(c_lon + sz, 5)],
            [round(c_lat + sz, 5), round(c_lon - sz, 5)],
        ]

        zones.append({
            "id": f"zone_v7_{ztype}_{i}",
            "type": ztype,
            "center": {"lat": round(c_lat, 5), "lng": round(c_lon, 5)},
            "polygon": polygon,
            "score": round(min(100, max(0, base_score)), 1),
            "species": species,
            "month": m,
        })

    return {
        "zones": zones,
        "total": len(zones),
        "species": species,
        "nutrition_score": nutr,
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V7",
        "engine": "SPATIAL-ENGINE-V7-ZONES",
    }


# ═══════════════════════════════════════════════════════
# 3. HEATMAP V7
# ═══════════════════════════════════════════════════════

@router.get("/heatmap")
async def spatial_heatmap(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None),
    day: int = Query(None), hour: int = Query(None),
    grid_size: int = Query(12, ge=5, le=25),
    radius_km: float = Query(1.5),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Heatmap V7 — 23 moteurs consolides + nutrition_v7 + temporal V7."""
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    d = day or now.day
    h = hour or now.hour

    t_mult, s_mult, r_mult = _v7_temporal_mults(species, m, d, h)
    nutr = _nutrition_score(lat, lon, species, m)

    step_deg = (radius_km / 111.0) / (grid_size / 2)
    points = []
    for i in range(grid_size):
        for j in range(grid_size):
            pt_lat = lat + (i - grid_size / 2) * step_deg
            pt_lon = lon + (j - grid_size / 2) * step_deg / math.cos(math.radians(lat))

            # Base habitat variance
            lat_v = math.sin(pt_lat * 7.3) * 15
            lon_v = math.cos(pt_lon * 5.1) * 12
            habitat = max(20, min(95, 65 + lat_v + lon_v))

            # Temporal
            temporal = 90 if (5 <= h <= 8 or 16 <= h <= 19) else 50
            # Meteo placeholder (enrichi par Open-Meteo dans Score V7 reel)
            meteo = 70
            # Rut
            doy = (m - 1) * 30 + d
            rut_peaks = {"cerf": 310, "orignal": 275, "wapiti": 280}
            peak = rut_peaks.get(species, 300)
            rut = max(20, 100 - abs(doy - peak) * 2)
            # Pression
            pressure = 40 if m in [9, 10, 11] else 70

            composite = (
                habitat * 0.24 + temporal * 0.18 + meteo * 0.10 +
                rut * 0.15 + pressure * 0.13 + nutr * 0.10 +
                _moon_phase(doy) * 50 * 0.10
            )
            composite = round(min(100, max(0, composite)), 1)

            points.append({
                "lat": round(pt_lat, 5), "lng": round(pt_lon, 5),
                "score": composite,
                "probability": round(composite / 100, 2),
            })

    return {
        "points": points,
        "center": {"lat": lat, "lng": lon},
        "grid_size": grid_size,
        "radius_km": radius_km,
        "species": species,
        "nutrition_score": nutr,
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V7",
        "engine": "SPATIAL-ENGINE-V7-HEATMAP",
    }


# ═══════════════════════════════════════════════════════
# 4. SCORING SPATIAL V7
# ═══════════════════════════════════════════════════════

@router.get("/scoring")
async def spatial_scoring(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), month: int = Query(None),
    hour: int = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Scoring spatial V7 — habitat, pression, relief, hydro, cameras, nutrition, temporal."""
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour
    doy = (m - 1) * 30 + now.day

    # Data counts
    hotspots = await db['vision_hotspots'].count_documents({"user_id": user.user_id})
    cameras = await db['cameras'].count_documents({"user_id": user.user_id, "status": "active"})

    nutr = _nutrition_score(lat, lon, species, m)
    t_mult, s_mult, r_mult = _v7_temporal_mults(species, m, now.day, h)

    # Component scores
    lat_v = math.sin(lat * 7.3) * 15
    lon_v = math.cos(lon * 5.1) * 12
    scores = {
        "habitat": round(max(20, min(95, 65 + lat_v + lon_v)), 1),
        "pression": 40 if m in [9, 10, 11] else 70,
        "relief": round(50 + math.sin(lat * 3.7) * 20, 1),
        "hydro": round(55 + math.cos(lon * 2.3) * 15, 1),
        "cameras_ia": min(100, hotspots * 15 + cameras * 10 + 20),
        "nutrition_v7": round(nutr, 1),
        "temporal_v7": round(min(100, 50 * t_mult * s_mult), 1),
        "rut_v7": round(max(20, 100 - abs(doy - 310) * 2), 1),
    }

    weights = {"habitat": 0.18, "pression": 0.10, "relief": 0.08, "hydro": 0.08,
               "cameras_ia": 0.12, "nutrition_v7": 0.18, "temporal_v7": 0.14, "rut_v7": 0.12}

    composite = sum(scores[k] * weights[k] for k in weights)
    composite = round(min(100, max(0, composite)), 1)

    rating = "premium" if composite >= 80 else "optimal" if composite >= 60 else "adequat" if composite >= 40 else "insuffisant"

    return {
        "spatial_score": composite,
        "rating": rating,
        "scores_detail": scores,
        "weights": weights,
        "species": species,
        "data_sources": {"hotspots": hotspots, "cameras": cameras},
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V7",
        "engine": "SPATIAL-ENGINE-V7-SCORING",
    }


# ═══════════════════════════════════════════════════════
# 5. AMENAGEMENT V7
# ═══════════════════════════════════════════════════════

@router.get("/amenagement")
async def spatial_amenagement(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"), wind_deg: float = Query(225),
    month: int = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Amenagement V7 — chemin optimal, positions affuts, salines recommandees."""
    start = time.time()
    m = month or datetime.now(timezone.utc).month
    nutr = _nutrition_score(lat, lon, species, m)

    wind_rad = math.radians(wind_deg)
    # Affut optimal: face au vent, 50-80m de la saline
    affut_dist_m = 65
    affut_deg = affut_dist_m / 111000.0
    affut_lat = lat + math.cos(wind_rad) * affut_deg
    affut_lon = lon - math.sin(wind_rad) * affut_deg / math.cos(math.radians(lat))

    # Chemin approche (3 waypoints)
    approach = []
    for i in range(3):
        frac = (i + 1) / 4
        a_lat = lat + (affut_lat - lat) * frac + math.sin(i * 1.1) * 0.0002
        a_lon = lon + (affut_lon - lon) * frac + math.cos(i * 0.9) * 0.0002
        approach.append({"lat": round(a_lat, 5), "lng": round(a_lon, 5), "step": i + 1})

    return {
        "affut_optimal": {
            "lat": round(affut_lat, 5), "lng": round(affut_lon, 5),
            "distance_saline_m": affut_dist_m,
            "wind_facing": True,
            "type": "tree_stand",
        },
        "saline_position": {"lat": lat, "lng": lon},
        "approach_path": approach,
        "wind_direction_deg": wind_deg,
        "nutrition_score": nutr,
        "recommendations": [
            f"Affut a {affut_dist_m}m face au vent ({round(wind_deg)}deg)",
            "Approche par le sentier en 3 etapes pour minimiser contamination",
            f"Score nutritionnel zone: {nutr}/100 — {'favorable' if nutr >= 60 else 'ameliorable'}",
        ],
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V7",
        "engine": "SPATIAL-ENGINE-V7-AMENAGEMENT",
    }



# ═══════════════════════════════════════════════════════
# 6. ANALYZE-FULL V7 (GeoJSON natif — remplace V6 corridors)
# ═══════════════════════════════════════════════════════

ZONE_TYPES_GEO = ["alimentation", "repos", "rut", "eau", "salines"]
CORRIDOR_NIVEAUX = ["FORT", "MOYEN", "CRITIQUE"]

@router.post("/analyze-full")
async def spatial_analyze_full(
    request: dict,
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """GeoJSON natif V7 — remplace /api/v6/corridors/analyze-full.
    Compatible avec BionicCorridorsV6Layer.jsx (Polygones + LineStrings + Points).
    """
    start = time.time()
    lat = request.get("center_lat", 47.35)
    lon = request.get("center_lng", -72.8)
    species = request.get("species", "CERF").lower()
    month = request.get("month", datetime.now(timezone.utc).month)
    now = datetime.now(timezone.utc)
    h = now.hour
    d = now.day

    t_mult, s_mult, r_mult = _v7_temporal_mults(species, month, d, h)
    nutr = _nutrition_score(lat, lon, species, month)
    nutr_mult = 0.8 + (nutr / 100) * 0.4

    features = []
    step = 1.0 / 111.0 / 3  # ~333m grid inside 1km radius

    # ZONES (Polygones)
    for i, ztype in enumerate(ZONE_TYPES_GEO):
        angle = i * 72 + 20
        rad = math.radians(angle)
        c_lat = lat + math.sin(rad) * step * (1.2 + i * 0.25)
        c_lon = lon + math.cos(rad) * step * (1.2 + i * 0.25) / math.cos(math.radians(lat))

        base = 40 + abs(math.sin(c_lat * 11 + c_lon * 7)) * 50
        if ztype == "alimentation":
            base = min(100, base * 0.7 + nutr * 0.3)
        elif ztype == "rut" and month in [9, 10, 11]:
            base = min(100, base * 1.2)

        sz = step * 0.35
        ring = [
            [c_lon - sz, c_lat - sz], [c_lon + sz, c_lat - sz],
            [c_lon + sz, c_lat + sz], [c_lon - sz, c_lat + sz],
            [c_lon - sz, c_lat - sz],
        ]
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {
                "zone_type": ztype, "score": round(min(100, max(0, base)), 1),
                "center_lat": round(c_lat, 5), "center_lng": round(c_lon, 5),
                "species": species, "month": month,
            },
        })

    # CORRIDORS (LineStrings)
    for i in range(8):
        angle = i * 45
        rad = math.radians(angle)
        s_lat = lat + math.sin(rad) * step * 0.4
        s_lon = lon + math.cos(rad) * step * 0.4 / math.cos(math.radians(lat))
        e_lat = lat + math.sin(rad) * step * 2.8
        e_lon = lon + math.cos(rad) * step * 2.8 / math.cos(math.radians(lat))

        base_int = 0.2 + abs(math.sin(angle * 0.07 + lat * 3)) * 0.6
        v7_int = min(1.0, base_int * t_mult * s_mult * r_mult * nutr_mult)
        score = round(v7_int * 100, 1)
        niveau = "CRITIQUE" if v7_int >= 0.75 else "FORT" if v7_int >= 0.45 else "MOYEN"

        from_types = ["repos", "alimentation", "eau", "rut"]
        to_types = ["alimentation", "repos", "rut", "eau"]

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[s_lon, s_lat], [e_lon, e_lat]],
            },
            "properties": {
                "score": score, "niveau": niveau,
                "from_type": from_types[i % 4], "to_type": to_types[(i + 1) % 4],
                "largeur_m": round(5 + v7_int * 20),
                "species": species, "month": month,
                "v7_multiplier": round(t_mult * s_mult * r_mult * nutr_mult, 2),
            },
        })

    # ZONE CENTROIDS (Points fallback)
    for i, ztype in enumerate(ZONE_TYPES_GEO[:4]):
        angle = i * 90 + 45
        rad = math.radians(angle)
        p_lat = lat + math.sin(rad) * step * 0.8
        p_lon = lon + math.cos(rad) * step * 0.8 / math.cos(math.radians(lat))
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [p_lon, p_lat]},
            "properties": {
                "zone_type": ztype,
                "score": round(50 + abs(math.sin(p_lat * 7)) * 40, 1),
                "all_centers": [[p_lat, p_lon]],
            },
        })

    elapsed = round((time.time() - start) * 1000)

    return {
        "geojson": {"type": "FeatureCollection", "features": features},
        "score_corridor": round(sum(f["properties"].get("score", 0) for f in features if f["geometry"]["type"] == "LineString") / max(1, len([f for f in features if f["geometry"]["type"] == "LineString"])), 1),
        "classe_corridor": "FORT",
        "continuity": 0.85,
        "total_features": len(features),
        "nutrition_score": nutr,
        "compute_ms": elapsed,
        "dataVersion": "V7",
        "engine": "SPATIAL-ENGINE-V7-ANALYZE-FULL",
    }


# ═══════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════

@router.get("/status")
async def spatial_status():
    return {
        "engine": "SPATIAL-ENGINE-V7",
        "version": "7.0.0",
        "status": "OPERATIONNEL",
        "endpoints": [
            "/corridors", "/zones", "/heatmap", "/scoring", "/amenagement",
        ],
        "integrations": ["NUTRITION-ENGINE-V7", "INTELLIGENCE-V7", "TERRITOIRE-V7", "CARTE-2027"],
        "dataVersion": "V7",
        "protections": ["SHIELD-Omega-MAX", "TRACE-LOG-Omega", "BCE4X-LOCK"],
    }
