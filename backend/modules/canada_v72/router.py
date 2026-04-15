"""
CANADA-V7.2 — Router API national pancanadien
================================================
Endpoints:
  /api/v7/canada/ndvi        — NDVI Sentinel-2 national
  /api/v7/canada/lidar       — LiDAR multi-provincial
  /api/v7/canada/soil        — Pédologie CanSIS + SoilGrids
  /api/v7/canada/profile     — Profil complet point (NDVI+LiDAR+Sol+Écozone)
  /api/v7/canada/provinces   — 13 provinces/territoires metadata
  /api/v7/canada/status      — Statut module national
"""
import time
import logging
from fastapi import APIRouter, Query

from .data import (
    PROVINCES, ECOZONES, LIDAR_SOURCES, CANSIS_SOIL_ORDERS,
    detect_province, detect_ecozone,
    get_ndvi_national, get_lidar_national, get_soil_national,
)

logger = logging.getLogger("bionic.canada_v72")
router = APIRouter(prefix="/api/v7/canada", tags=["Canada V7.2"])


@router.get("/ndvi")
async def canada_ndvi(
    lat: float = Query(...), lng: float = Query(...),
    month: int = Query(None),
):
    """NDVI Sentinel-2 national avec fallback ET0 régionalisé."""
    from datetime import datetime, timezone
    start = time.time()
    m = month or datetime.now(timezone.utc).month
    prov = detect_province(lat, lng)
    ndvi = get_ndvi_national(lat, lng, m, prov)
    return {
        **ndvi,
        "province": prov,
        "month": m,
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "CANADA-V7.2-NDVI",
    }


@router.get("/lidar")
async def canada_lidar(
    lat: float = Query(...), lng: float = Query(...),
):
    """LiDAR multi-provincial (canopy, slope, relief)."""
    start = time.time()
    prov = detect_province(lat, lng)
    ndvi_data = get_ndvi_national(lat, lng, 7, prov)  # summer reference
    lidar = get_lidar_national(lat, lng, prov, ndvi_data["value"])
    return {
        **lidar,
        "province": prov,
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "CANADA-V7.2-LIDAR",
    }


@router.get("/soil")
async def canada_soil(
    lat: float = Query(...), lng: float = Query(...),
):
    """Pédologie nationale CanSIS SLC v3.2 + SoilGrids ISRIC."""
    start = time.time()
    prov = detect_province(lat, lng)
    soil = get_soil_national(lat, lng, prov)
    return {
        **soil,
        "province": prov,
        "compute_ms": round((time.time() - start) * 1000),
        "engine": "CANADA-V7.2-SOIL",
    }


@router.get("/profile")
async def canada_profile(
    lat: float = Query(...), lng: float = Query(...),
    month: int = Query(None),
):
    """Profil complet national (NDVI + LiDAR + Sol + Écozone)."""
    from datetime import datetime, timezone
    start = time.time()
    m = month or datetime.now(timezone.utc).month
    prov = detect_province(lat, lng)
    ecozone = detect_ecozone(lat, lng, prov)

    ndvi = get_ndvi_national(lat, lng, m, prov)
    lidar = get_lidar_national(lat, lng, prov, ndvi["value"])
    soil = get_soil_national(lat, lng, prov)

    eco = ECOZONES.get(ecozone, {})
    prov_data = PROVINCES.get(prov, {})

    return {
        "province": {"code": prov, "name": prov_data.get("name", prov), "area_km2": prov_data.get("area_km2")},
        "ecozone": {"code": ecozone, "ndvi_summer_avg": eco.get("ndvi_summer_avg"), "canopy_avg_m": eco.get("canopy_avg_m"), "soil_class": eco.get("soil_class"), "fertility": eco.get("fertility")},
        "ndvi": ndvi,
        "lidar": lidar,
        "soil": soil,
        "compute_ms": round((time.time() - start) * 1000),
        "dataVersion": "V7.2",
        "engine": "CANADA-V7.2-PROFILE",
    }


@router.get("/provinces")
async def canada_provinces():
    """13 provinces/territoires — métadonnées complètes."""
    return {
        "provinces": {k: {**v, "lidar": LIDAR_SOURCES.get(k, {})} for k, v in PROVINCES.items()},
        "ecozones": {k: v for k, v in ECOZONES.items()},
        "soil_orders": list(CANSIS_SOIL_ORDERS.keys()),
        "total_provinces": len(PROVINCES),
        "total_ecozones": len(ECOZONES),
        "engine": "CANADA-V7.2-PROVINCES",
    }


@router.get("/status")
async def canada_status():
    return {
        "engine": "CANADA-V7.2",
        "version": "7.2.0",
        "status": "OPERATIONNEL",
        "endpoints": ["/ndvi", "/lidar", "/soil", "/profile", "/provinces", "/status"],
        "coverage": {
            "provinces": 13,
            "ecozones": len(ECOZONES),
            "soil_orders": len(CANSIS_SOIL_ORDERS),
            "lidar_sources": len(LIDAR_SOURCES),
        },
        "data_sources": [
            "Sentinel-2_L2A_Copernicus", "Open-Meteo_ET0",
            "CanSIS_SLC_v3.2", "SoilGrids_ISRIC",
            "MRNF_QC", "BC_LidarBC", "AB_OpenData", "ON_GeoHub",
            "GeoNB", "GeoNova", "ECCC_national",
        ],
        "dataVersion": "V7.2",
    }
