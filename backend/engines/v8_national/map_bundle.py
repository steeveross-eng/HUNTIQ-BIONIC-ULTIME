"""
V8-MAP-BUNDLE — Endpoint unique toutes couches territoire
============================================================
MAP-LAYERS-Omega: Chargement <1s via bundle unique + cache 30s.
INDEPENDANT du GOVERNANCE-LOCK (couches TOUJOURS servies).
"""
import time
import math
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db

logger = logging.getLogger("bionic.v8_map_bundle")
router = APIRouter(prefix="/api/v8/map", tags=["V8 Map Bundle"])

_BUNDLE_CACHE = {}
_CACHE_TTL_S = 30

ZONE_TYPES = ["alimentation", "repos", "rut", "affuts", "eau"]


def _cache_key(lat, lon, species, month):
    return f"{round(lat,3)}:{round(lon,3)}:{species}:{month}"


def _organic_polygon(c_lat, c_lon, radius_deg, n_vertices=12, seed=0):
    """Generate organic polygon via spline-like jitter on circle vertices."""
    points = []
    cos_lat = max(0.5, math.cos(math.radians(c_lat)))
    for j in range(n_vertices):
        angle = (j / n_vertices) * 2 * math.pi
        # Organic jitter: pseudo-random deformation per vertex
        jitter = 0.7 + 0.6 * abs(math.sin(seed * 7.3 + j * 2.9 + c_lat * 11.1))
        r = radius_deg * jitter
        p_lat = c_lat + math.sin(angle) * r
        p_lon = c_lon + math.cos(angle) * r / cos_lat
        points.append([round(p_lat, 6), round(p_lon, 6)])
    points.append(points[0])  # Close polygon
    return points


def _generate_zones_inline(lat, lon, species, month, radius_km=1):
    """Generate V8 zones with ORGANIC polygons (spline-like, non-rectangular)."""
    nutr = 50 + abs(math.sin(lat * 3.7 + lon * 2.1)) * 30
    zones = []
    step = radius_km / 111.0 / 2.5
    for i, ztype in enumerate(ZONE_TYPES):
        angle = i * 72 + 15
        rad = math.radians(angle)
        c_lat = lat + math.sin(rad) * step * (0.8 + i * 0.15)
        c_lon = lon + math.cos(rad) * step * (0.8 + i * 0.15) / math.cos(math.radians(lat))
        base_score = 40 + abs(math.sin(c_lat * 11 + c_lon * 7)) * 50
        if ztype == "alimentation":
            base_score = min(100, base_score * 0.7 + nutr * 0.3)
        elif ztype == "rut" and month in [9, 10, 11]:
            base_score = min(100, base_score * 1.2)
        elif ztype == "eau":
            base_score = min(100, base_score * 0.9)
        # Organic polygon ~250-350m radius, 12 vertices, seed unique per zone
        radius_deg = 0.0025 + abs(math.sin(i * 3.7 + lat * 5.1)) * 0.001
        polygon = _organic_polygon(c_lat, c_lon, radius_deg, n_vertices=12, seed=i + lat * 100)
        zones.append({
            "id": f"zone_v8_{ztype}_{i}", "type": ztype,
            "center": {"lat": round(c_lat, 5), "lng": round(c_lon, 5)},
            "polygon": polygon,
            "score": round(min(100, max(0, base_score)), 1),
        })
    return zones


def _bezier_curve(start, end, n_points=8, curvature_seed=0):
    """Generate curved path between two points via quadratic Bezier."""
    s_lat, s_lon = start
    e_lat, e_lon = end
    mid_lat = (s_lat + e_lat) / 2
    mid_lon = (s_lon + e_lon) / 2
    # Perpendicular offset for curvature
    dx = e_lon - s_lon
    dy = e_lat - s_lat
    dist = math.sqrt(dx*dx + dy*dy)
    if dist < 1e-8:
        return [[s_lat, s_lon], [e_lat, e_lon]]
    # Offset perpendicular to the line
    curve_strength = 0.15 + 0.2 * abs(math.sin(curvature_seed * 3.7))
    ctrl_lat = mid_lat + (-dx) * curve_strength * (1 if curvature_seed % 2 == 0 else -1)
    ctrl_lon = mid_lon + (dy) * curve_strength * (1 if curvature_seed % 2 == 0 else -1)
    points = []
    for j in range(n_points + 1):
        t = j / n_points
        inv = 1 - t
        p_lat = inv*inv*s_lat + 2*inv*t*ctrl_lat + t*t*e_lat
        p_lon = inv*inv*s_lon + 2*inv*t*ctrl_lon + t*t*e_lon
        points.append([round(p_lat, 6), round(p_lon, 6)])
    return points


def _generate_corridors_inline(lat, lon, species, month, hour, radius_km=10):
    """Generate V8 corridors with CURVED paths and intensity levels."""
    doy = (month - 1) * 30 + 15
    crep = species in ["cerf", "orignal", "wapiti", "caribou", "chevreuil"]
    t_mult = 1.3 if (5 <= hour <= 8 or 16 <= hour <= 19) and crep else 0.7 if 10 <= hour <= 14 else 1.0
    corridors = []
    for i in range(10):
        angle = i * 36 + 10
        rad = math.radians(angle)
        dist = (i + 1) * radius_km / 11 / 111.0
        s_lat = lat + math.sin(rad) * dist
        s_lon = lon + math.cos(rad) * dist / math.cos(math.radians(lat))
        e_angle = angle + 30 + math.sin(i * 1.7) * 20
        e_rad = math.radians(e_angle)
        e_lat = lat + math.sin(e_rad) * dist * 1.3
        e_lon = lon + math.cos(e_rad) * dist * 1.3 / math.cos(math.radians(lat))
        raw = abs(math.sin(s_lat * 7.3 + s_lon * 5.1 + doy * 0.1)) * 100
        intensity = min(100, max(10, raw * t_mult))
        if intensity > 80:
            ctype = "critique"
        elif intensity > 65:
            ctype = "majeur"
        elif intensity > 50:
            ctype = "fort"
        elif intensity > 30:
            ctype = "modere"
        else:
            ctype = "faible"
        # Bezier curved path (8 intermediate points)
        path = _bezier_curve([s_lat, s_lon], [e_lat, e_lon], n_points=8, curvature_seed=i)
        corridors.append({
            "id": f"corr_v8_{i}", "type": ctype,
            "path": path,
            "start": {"lat": round(s_lat, 5), "lng": round(s_lon, 5)},
            "end": {"lat": round(e_lat, 5), "lng": round(e_lon, 5)},
            "intensity": round(intensity, 1),
        })
    return corridors


def _generate_affuts_inline(lat, lon, species, zones, wind_deg=180):
    """Generate V8 enriched affuts with orientation based on wind + zones."""
    affuts = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    for i, z in enumerate(zones):
        if z["type"] in ("alimentation", "rut", "repos"):
            zc = z["center"]
            # Place affut OUTSIDE zone, opposite wind direction
            wind_rad = math.radians((wind_deg + 180) % 360)
            offset = 0.004 + abs(math.sin(i * 5.3)) * 0.002
            a_lat = zc["lat"] + math.sin(wind_rad) * offset
            a_lon = zc["lng"] + math.cos(wind_rad) * offset / cos_lat
            affuts.append({
                "id": f"affut_v8_{i}",
                "lat": round(a_lat, 6),
                "lng": round(a_lon, 6),
                "orientation_deg": round((wind_deg + 180) % 360, 1),
                "zone_type": z["type"],
                "zone_score": z["score"],
                "quality": "optimal" if z["score"] > 70 else "bon" if z["score"] > 50 else "acceptable",
            })
    return affuts


def _generate_heatmap_inline(lat, lon, species, month, hour, grid_size=12, radius_km=1.5):
    """Generate heatmap inline."""
    doy = (month - 1) * 30 + 15
    crep = species in ["cerf","orignal","wapiti","caribou","chevreuil"]
    t_mult = 1.3 if (5<=hour<=8 or 16<=hour<=19) and crep else 0.7 if 10<=hour<=14 else 1.0

    points = []
    half = grid_size // 2
    step_lat = radius_km / 111.0 / half if half > 0 else 0.001
    step_lon = step_lat / max(0.5, math.cos(math.radians(lat)))
    for gy in range(-half, half + 1):
        for gx in range(-half, half + 1):
            p_lat = lat + gy * step_lat
            p_lon = lon + gx * step_lon
            raw = abs(math.sin(p_lat * 11.3 + p_lon * 7.7 + doy * 0.15))
            prob = min(1.0, max(0.05, raw * t_mult / 1.3))
            if prob > 0.15:
                points.append({
                    "lat": round(p_lat, 5), "lng": round(p_lon, 5),
                    "probability": round(prob, 3),
                })
    return points


@router.get("/bundle")
async def map_bundle(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(None), hour: int = Query(None),
    include_p1: bool = Query(False),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Bundle unique toutes couches — PUBLIC, GOVERNANCE-INDEPENDENT."""
    start = time.time()
    now = datetime.now(timezone.utc)
    m = month or now.month
    h = hour or now.hour

    ck = _cache_key(lat, lon, species, m)
    cached = _BUNDLE_CACHE.get(ck)
    if cached and (time.time() - cached["ts"]) < _CACHE_TTL_S:
        result = {**cached["data"], "from_cache": True, "cache_age_ms": round((time.time() - cached["ts"]) * 1000)}
        return result

    from modules.canada_v72.data import detect_province
    from engines.v8_national.referentials import detect_biome, BIOMES
    province = detect_province(lat, lon)
    biome_code = detect_biome(lat, lon, province)

    from engines.v8_national.exclusion_engine import evaluate_exclusion
    exclusion = evaluate_exclusion(lat, lon, species)

    # Couches geospatiales V8 — TERRAIN-AWARE (Phase B upgrade)
    from engines.v8_national.phase_b_engines import generate_zones_ta, generate_corridors_ta, generate_affuts_ta
    zones = generate_zones_ta(lat, lon, species, m)
    corridors = generate_corridors_ta(lat, lon, species, m, h)
    affuts = generate_affuts_ta(lat, lon, species, zones, corridors, wind_deg=180)

    biome_data = BIOMES.get(biome_code, {})

    # P1 data (optionnel — seulement si include_p1=true)
    p1 = {}
    if include_p1:
        import asyncio
        try:
            from engines.v8_national.p1_pipelines import fetch_lidar_data, fetch_pedology_data
            lidar_task = asyncio.create_task(fetch_lidar_data(lat, lon, province))
            pedo_task = asyncio.create_task(fetch_pedology_data(lat, lon, province))
            lidar, pedo = await asyncio.gather(lidar_task, pedo_task, return_exceptions=True)
            if not isinstance(lidar, Exception):
                p1["lidar"] = lidar
            if not isinstance(pedo, Exception):
                p1["pedology"] = pedo
        except Exception:
            pass

    gov_mode = "LOCKED"
    try:
        from engines.v8_national.governance import _get_governance_state
        gov = await _get_governance_state(db)
        gov_mode = gov.get("mode", "LOCKED")
    except Exception:
        pass

    compute_ms = round((time.time() - start) * 1000)

    result = {
        "zones": zones, "zones_count": len(zones),
        "corridors": corridors, "corridors_count": len(corridors),
        "affuts": affuts, "affuts_count": len(affuts),
        "biome": {"code": biome_code, "name": biome_data.get("name", biome_code), "dominant_species": biome_data.get("dominant_species", [])},
        "exclusion": {"decision": exclusion["decision"], "reasons": exclusion.get("reasons", []), "severity": exclusion.get("severity", "NONE"), "habitat_score": exclusion.get("habitat_score", 0)},
        "governance_mode": gov_mode,
        "p1": p1,
        "context": {"lat": lat, "lon": lon, "species": species, "province": province, "month": m, "hour": h},
        "compute_ms": compute_ms, "from_cache": False, "cache_ttl_s": _CACHE_TTL_S,
        "dataVersion": "V8", "engine": "V8-MAP-BUNDLE",
    }

    _BUNDLE_CACHE[ck] = {"data": result, "ts": time.time()}
    if len(_BUNDLE_CACHE) > 200:
        oldest = min(_BUNDLE_CACHE, key=lambda k: _BUNDLE_CACHE[k]["ts"])
        del _BUNDLE_CACHE[oldest]

    return result


@router.get("/bundle/status")
async def bundle_status():
    return {
        "engine": "V8-MAP-BUNDLE", "version": "8.2.0", "status": "OPERATIONNEL",
        "cache": {"type": "in-memory", "ttl_s": _CACHE_TTL_S, "entries": len(_BUNDLE_CACHE)},
        "layers": ["zones_v7", "corridors_v7", "heatmap_v7", "biome_v8", "exclusion_v8", "p1_lidar", "p1_pedology"],
        "governance_independent": True,
        "target_ttfb_ms": 300, "target_render_ms": 1000,
        "dataVersion": "V8",
    }
