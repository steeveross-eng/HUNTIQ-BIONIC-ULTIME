"""
predictive_omega_v2_router.py — PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω
================================================================================
Endpoint d'observabilité institutionnelle pour l'engine predictive_omega V2.

Retourne :
  - statut des datasets GPS USGS / Movebank par espèce
  - score V2 par corridor (direction / speed / density / diurnal)
  - métriques saison / heure / bearing / amplitude
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/predictive", tags=["V30_PREDICTIVE_OMEGA_V2_Ω"])

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@router.get("/omega-v2")
async def predictive_omega_v2_diagnostic(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Diagnostic complet du scoring predictive_omega V2 sur le bundle live."""
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
        from engines.v8_institutional.predictive_omega_v2 import (
            get_gps_dataset_status,
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    try:
        resp = FResp()
        bundle = await v20_territoire_bundle(
            response=resp, lat=lat, lon=lon, species=species,
            month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
        )
    except Exception as e:
        return JSONResponse({"error": f"bundle_unavailable: {e}"}, status_code=500)

    corridors = bundle.get("corridors") or []
    summary = []
    for c in corridors[:30]:
        pv2 = c.get("predictive_omega_v2") or {}
        summary.append({
            "id": c.get("id"),
            "type": ("ENTERING" if c.get("entering_corridor")
                     else "INTERZONE" if c.get("interzone_generated") else "V30"),
            "score": pv2.get("score"),
            "valid": pv2.get("valid"),
            "components": pv2.get("components"),
            "metrics": pv2.get("metrics"),
        })

    return JSONResponse({
        "phase": "PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω",
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "month": month,
        "hour": hour,
        "stats": bundle.get("predictive_omega_v2_stats") or {},
        "gps_dataset_status": get_gps_dataset_status(),
        "predictive_v2_per_corridor_sample": summary,
        "v30_locked": True,
    })
