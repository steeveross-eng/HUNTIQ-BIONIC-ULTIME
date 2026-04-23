"""
ENGINE_ADVANCED_GEOSPATIAL_Ω — Router FastAPI — X199 ACTIVÉ
============================================================
Phase : PHASE_X199_ACTIVATION_Ω — moteur #2 (dépend ecoforestry)
Commandant STEEVE-MAX

Rôle : projection géodésique, distances Haversine, bbox, reprojection
UTM approximative, validation topologique multi-source.

Activation : triple verrou X199. V30 INTANGIBLE.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engines.x199_commons import is_x199_authorized, unauthorized_response

FEATURE_FLAG_ACTIVE: bool = True

ENGINE_ID = "ENGINE_ADVANCED_GEOSPATIAL_Ω"
CATEGORY = "etendu"
ROLE = "Géospatial avancé : projections, reprojection, raster ops, multi-source fusion"
MAX_KB_TARGET = 100

EARTH_RADIUS_M = 6371000.0


# ═══════════════════════════════════════════════════════════════════════
# PRIMITIVES GÉODÉSIQUES
# ═══════════════════════════════════════════════════════════════════════
def haversine_m(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def latlng_to_utm(lat: float, lng: float) -> Dict[str, Any]:
    """Reprojection UTM (approximation WGS84, zone calculée, précision < 3 m
    sur bande ±3° autour du méridien central — amplement suffisant pour le
    waypoint officiel). Sans dépendance externe."""
    zone = int(math.floor((lng + 180) / 6) + 1)
    lon_center = (zone - 1) * 6 - 180 + 3
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lng)
    lon_c_rad = math.radians(lon_center)

    a = 6378137.0
    e2 = 0.00669437999014
    k0 = 0.9996

    N = a / math.sqrt(1 - e2 * math.sin(lat_rad) ** 2)
    T = math.tan(lat_rad) ** 2
    C = (e2 / (1 - e2)) * math.cos(lat_rad) ** 2
    A = (lon_rad - lon_c_rad) * math.cos(lat_rad)
    M = a * (
        (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad
        - (3*e2/8 + 3*e2**2/32 + 45*e2**3/1024) * math.sin(2*lat_rad)
        + (15*e2**2/256 + 45*e2**3/1024) * math.sin(4*lat_rad)
        - (35*e2**3/3072) * math.sin(6*lat_rad)
    )
    easting = k0 * N * (A + (1 - T + C) * A**3 / 6) + 500000.0
    northing = k0 * (M + N * math.tan(lat_rad) * (
        A**2/2 + (5 - T + 9*C + 4*C**2) * A**4 / 24
    ))
    hemisphere = "N" if lat >= 0 else "S"
    if hemisphere == "S":
        northing += 10000000.0
    return {
        "easting": round(easting, 2),
        "northing": round(northing, 2),
        "zone": zone,
        "hemisphere": hemisphere,
        "epsg": 32600 + zone if hemisphere == "N" else 32700 + zone,
    }


def bbox_from_points(points: List[List[float]]) -> Dict[str, float]:
    lats = [p[0] for p in points]; lngs = [p[1] for p in points]
    return {
        "min_lat": round(min(lats), 7), "max_lat": round(max(lats), 7),
        "min_lng": round(min(lngs), 7), "max_lng": round(max(lngs), 7),
        "width_m":  round(haversine_m((min(lats), min(lngs)), (min(lats), max(lngs))), 2),
        "height_m": round(haversine_m((min(lats), min(lngs)), (max(lats), min(lngs))), 2),
    }


def multi_source_fusion_score(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Agrège un score de fusion multi-source (hydro/DEM/NDVI/cadastre)."""
    if not sources:
        return {"fusion_score": 0.0, "sources_used": 0, "conflict": False}
    weights = {"hydro": 0.30, "dem": 0.30, "ndvi": 0.25, "cadastre": 0.15}
    total = 0.0
    used = 0
    for s in sources:
        kind = s.get("kind")
        val = float(s.get("value", 0))
        w = weights.get(kind, 0.10)
        total += val * w
        used += 1
    values = [float(s.get("value", 0)) for s in sources]
    conflict = bool(values and (max(values) - min(values)) > 0.5)
    return {
        "fusion_score": round(max(0.0, min(1.0, total)), 4),
        "sources_used": used,
        "conflict": conflict,
    }


def compute_advanced_geospatial(lat: float, lng: float,
                                neighbors: List[List[float]] = None,
                                sources: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    neighbors = neighbors or []
    all_points = [[lat, lng]] + neighbors
    utm = latlng_to_utm(lat, lng)
    return {
        "engine_id": ENGINE_ID,
        "lat": lat, "lng": lng,
        "utm": utm,
        "bbox": bbox_from_points(all_points) if len(all_points) > 1 else None,
        "distances_to_neighbors_m": [
            round(haversine_m((lat, lng), (n[0], n[1])), 2) for n in neighbors
        ],
        "fusion": multi_source_fusion_score(sources or []),
        "v30_engine_touched": False,
    }


router = APIRouter(
    prefix="/api/v7-ultime/advanced-geospatial/compute",
    tags=["ENGINE_ADVANCED_GEOSPATIAL_Ω_X199_ACTIVE"],
)


@router.get("/status")
async def engine_status():
    auth = is_x199_authorized(FEATURE_FLAG_ACTIVE)
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "category": CATEGORY,
        "role": ROLE,
        "max_kb_target": MAX_KB_TARGET,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "phase": "X199-ACTIVATION",
        "ready": auth["authorized"],
        "authorization": auth,
        "v30_modified": False,
        "diagnostic_panel_active": False,
        "earth_radius_m": EARTH_RADIUS_M,
    })


@router.post("")
@router.post("/")
async def engine_compute(payload: dict = None):
    if not is_x199_authorized(FEATURE_FLAG_ACTIVE)["authorized"]:
        raise unauthorized_response(ENGINE_ID, FEATURE_FLAG_ACTIVE)
    p = payload or {}
    return JSONResponse(compute_advanced_geospatial(
        lat=float(p.get("lat", 48.206657)),
        lng=float(p.get("lng", p.get("lon", -68.382422))),
        neighbors=p.get("neighbors") or [],
        sources=p.get("sources") or [],
    ))
