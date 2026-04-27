"""
origine_externe_filter_router.py — PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω
================================================================================
Endpoint d'observabilité institutionnelle pour le filtre ORIGINE_EXTERNE_Ω.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_ORIGINE_EXTERNE_FILTER_Ω"])

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@router.get("/origine-externe")
async def origine_externe_diagnostic(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Diagnostic complet du filtre ORIGINE_EXTERNE_Ω sur le bundle live."""
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
        from engines.v8_institutional.origine_externe_filter_omega import get_filter_status
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
    kept_sample = []
    for c in corridors[:30]:
        ov = c.get("origin_external_validation") or {}
        kept_sample.append({
            "id": c.get("id"),
            "type": ("ENTERING" if c.get("entering_corridor")
                     else "INTERZONE" if c.get("interzone_generated") else "V30"),
            "passed": ov.get("origin_external_passed"),
            "reason": ov.get("origin_external_reason"),
            "distance_origin_m": ov.get("distance_origin_m"),
            "gps_density_ratio": ov.get("gps_density_ratio"),
            "gps_weighted_hits": ov.get("gps_weighted_hits"),
        })

    rejected = bundle.get("corridors_rejected_origine_externe_xix") or []

    return JSONResponse({
        "phase": "PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω",
        "subphase": "PHASE_XIX_P1",
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "month": month,
        "hour": hour,
        "filter_status": get_filter_status(),
        "stats": bundle.get("origine_externe_filter_stats") or {},
        "kept_per_corridor_sample": kept_sample,
        "rejected_in_this_run": rejected[:20],
        "v30_locked": True,
    })
