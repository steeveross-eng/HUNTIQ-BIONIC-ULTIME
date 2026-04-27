"""
origine_externe_inversion_router.py — PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω
================================================================================
Endpoint d'observabilité institutionnelle pour le module d'inversion XIX-P2.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_ORIGINE_EXTERNE_INVERSION_Ω"])

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@router.get("/origine-inversion")
async def origine_inversion_diagnostic(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Diagnostic du module d'inversion ORIGINE_EXTERNE_INVERSION_Ω."""
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
        from engines.v8_institutional.origine_externe_inversion_omega import get_inversion_status
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
    inverted_sample = []
    for c in corridors[:30]:
        inverted_sample.append({
            "id": c.get("id"),
            "type": ("ENTERING" if c.get("entering_corridor")
                     else "INTERZONE" if c.get("interzone_generated") else "V30"),
            "inversion_applied": c.get("origin_external_inversion_applied"),
            "inversion_reason": c.get("origin_external_inversion_reason"),
            "inversion_audit": c.get("origin_external_inversion_audit"),
            "post_xix_p1_passed": c.get("origin_external_passed"),
            "post_xix_p1_reason": c.get("origin_external_reason"),
        })

    return JSONResponse({
        "phase": "PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω",
        "subphase": "PHASE_XIX_P2",
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "month": month,
        "hour": hour,
        "inversion_status": get_inversion_status(),
        "stats": bundle.get("origine_externe_inversion_stats") or {},
        "xix_p1_downstream_stats": bundle.get("origine_externe_filter_stats") or {},
        "corridors_sample": inverted_sample,
        "v30_locked": True,
    })
