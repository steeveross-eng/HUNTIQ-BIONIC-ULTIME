"""
Predictive Layer Engine — Router M3
=============================================================
Directive x7000-M3 — Phase M3 MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : predictive_engine, solunar, weather_fauna_simulation_engine
               consommes en LECTURE. NE recree PAS leurs fonctionnalites.
ANTI-DOUBLON NUTRITIONNEL : enrichissement nutritionnel via nutrition_v6_interface.

22 Points de fusion : SUPRA (PF3-S1/S2/S3/S4) / Solunaire (PF3-LUN1/LUN2/LUN3) /
    Meteo (PF3-MET1/MET2/MET3) / M1 (PF3-M1a/M1b/M1c) / M2 (PF3-M2a/M2b/M2c) /
    Chasse (PF3-TRIP1/TRIP2) / Nutrition V6 (PF3-N1/N2/N3/N4) / Retour (PF3-RET1)

10 Endpoints (0 health + 9 fonctionnels) :
  0. GET  /health
  1. GET  /zone/{zone_id}/species/{species}
  2. GET  /at/{lat}/{lng}/species/{species}
  3. GET  /heatmap/{zone_id}
  4. GET  /best-times/{zone_id}/{species}
  5. GET  /timeseries/{zone_id}/{species}
  6. POST /timeseries/record
  7. GET  /trends/{species}
  8. GET  /correlation/meteo/{zone_id}
  9. POST /compute/{zone_id}
"""

from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any

from .services.predictive_layer_computer import (
    compute_layer,
    compute_at_point,
    get_heatmap,
    get_best_times,
    ensure_indexes as ensure_layer_indexes
)
from .services.timeseries_collector import (
    record_datapoint,
    get_timeseries,
    ensure_indexes as ensure_ts_indexes
)
from .services.seasonal_trend_analyzer import analyze_trends
from .services.meteo_fauna_correlator import correlate_zone

router = APIRouter(prefix="/api/v1/predict-layer", tags=["M3 Predictive Layer Engine"])

_indexes_created = False


async def _ensure_indexes_once():
    global _indexes_created
    if not _indexes_created:
        try:
            await ensure_layer_indexes()
            await ensure_ts_indexes()
            _indexes_created = True
        except Exception:
            pass


# ==============================================
# HEALTH (0)
# ==============================================

@router.get("/health")
async def health():
    await _ensure_indexes_once()
    return {
        "status": "operational",
        "engine": "predictive_layer_engine",
        "version": "1.0.0",
        "phase": "M3-MAP-INTELLIGENCE",
        "directive": "x7000-M3",
        "endpoints": 10,
        "fusion_points": 22,
        "services": [
            "PredictiveLayerComputer",
            "TimeSeriesCollector",
            "SeasonalTrendAnalyzer",
            "MeteoFaunaCorrelator"
        ],
        "collections": ["timeseries_data", "predictive_layers", "seasonal_trends"],
        "anti_doublon": [
            "predictive_engine", "solunar",
            "weather_fauna_simulation_engine",
            "scoring_engine", "territory_engine", "poi_scorer"
        ],
        "factor_weights": {
            "base_activity": 0.25,
            "season": 0.15,
            "solunar": 0.15,
            "meteo": 0.20,
            "historical": 0.15,
            "nutrition": 0.10
        }
    }


# ==============================================
# PREDICTIVE LAYER — M3-A (1-4)
# ==============================================

@router.get("/zone/{zone_id}/species/{species}")
async def predictive_layer_zone(zone_id: str, species: str,
                                target_date: Optional[str] = Query(None),
                                lat: float = Query(46.85),
                                lng: float = Query(-71.25)):
    """M3-1: Couche predictive 24h pour une zone/espece."""
    await _ensure_indexes_once()
    result = await compute_layer(zone_id, species, target_date, lat, lng)
    if "error" in result:
        return {"success": False, **result}
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.get("/at/{lat}/{lng}/species/{species}")
async def predictive_at_point(lat: float, lng: float, species: str,
                              target_date: Optional[str] = Query(None)):
    """M3-2: Prediction au point GPS."""
    await _ensure_indexes_once()
    result = await compute_at_point(lat, lng, species, target_date)
    if "error" in result:
        return {"success": False, **result}
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.get("/heatmap/{zone_id}")
async def heatmap(zone_id: str,
                  species: str = Query("orignal"),
                  target_date: Optional[str] = Query(None)):
    """M3-3: Heatmap de probabilite multi-POI pour une zone."""
    await _ensure_indexes_once()
    result = await get_heatmap(zone_id, species, target_date)
    if "error" in result:
        return {"success": False, **result}
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.get("/best-times/{zone_id}/{species}")
async def best_times(zone_id: str, species: str,
                     target_date: Optional[str] = Query(None),
                     lat: float = Query(46.85),
                     lng: float = Query(-71.25)):
    """M3-4: Meilleurs creneaux horaires combines."""
    await _ensure_indexes_once()
    result = await get_best_times(zone_id, species, target_date, lat, lng)
    if "error" in result:
        return {"success": False, **result}
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


# ==============================================
# TIMESERIES + CORRELATION — M3-B (5-9)
# ==============================================

@router.get("/timeseries/{zone_id}/{species}")
async def timeseries(zone_id: str, species: str,
                     metric: str = Query("activity_index"),
                     limit: int = Query(100, ge=1, le=1000)):
    """M3-5: Serie temporelle brute."""
    await _ensure_indexes_once()
    result = await get_timeseries(zone_id, species, metric, limit)
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.post("/timeseries/record")
async def record_ts(payload: Dict[str, Any] = Body(...)):
    """M3-6: Enregistrer un point de serie temporelle."""
    await _ensure_indexes_once()

    required = ["zone_id", "species", "metric", "value"]
    missing = [f for f in required if f not in payload]
    if missing:
        return {"success": False, "error": "MISSING_FIELDS", "fields": missing}

    result = await record_datapoint(
        zone_id=payload["zone_id"],
        species=payload["species"],
        metric=payload["metric"],
        value=float(payload["value"]),
        source=payload.get("source", "manual"),
        poi_id=payload.get("poi_id", ""),
        timestamp=payload.get("timestamp")
    )

    if "error" in result:
        return {"success": False, **result}

    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.get("/trends/{species}")
async def trends(species: str,
                 zone_id: str = Query(""),
                 year: int = Query(2026)):
    """M3-7: Tendances saisonnieres par espece."""
    await _ensure_indexes_once()
    result = await analyze_trends(species, zone_id, year)
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.get("/correlation/meteo/{zone_id}")
async def meteo_correlation(zone_id: str,
                            species: str = Query("orignal"),
                            lat: float = Query(46.85),
                            lng: float = Query(-71.25)):
    """M3-8: Correlations meteo-faune."""
    await _ensure_indexes_once()
    result = await correlate_zone(zone_id, species, lat, lng)
    return {
        "success": True,
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }


@router.post("/compute/{zone_id}")
async def admin_compute(zone_id: str, payload: Dict[str, Any] = Body(...)):
    """M3-9: Admin — forcer le recalcul d'une couche predictive."""
    await _ensure_indexes_once()

    species = payload.get("species", "orignal")
    target_date = payload.get("target_date")
    lat = payload.get("lat", 46.85)
    lng = payload.get("lng", -71.25)

    result = await compute_layer(zone_id, species, target_date, lat, lng)
    if "error" in result:
        return {"success": False, **result}

    return {
        "success": True,
        "action": "FORCE_RECOMPUTE",
        **result,
        "source": "predictive_layer_engine",
        "directive": "x7000-M3"
    }
