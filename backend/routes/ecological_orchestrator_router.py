"""
ecological_orchestrator_router.py — PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω
================================================================================
Endpoint d'observabilité institutionnelle pour l'orchestrateur écologique unifié.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_CORRIDORS_ECOLOGICAL_Ω"])

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@router.get("/ecological-orchestrator")
async def ecological_orchestrator(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Diagnostic complet du consensus écologique pour le bundle live.

    Retourne :
      - heatmaps_status (audit des 5 sources MFFP/SEPAQ/USGS/NOAA/NASA)
      - per-corridor consensus + components
      - rate_pct corridors validant le consensus institutionnel
    """
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
        from engines.v8_institutional.ecological_orchestrator_omega import (
            get_heatmaps_status,
            ECOLOGICAL_CONSENSUS_WEIGHTS,
            EXTERNAL_RING_FRACTION,
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
    consensus_summary = []
    for c in corridors[:30]:  # cap d'observabilité
        eco = c.get("ecological_consensus") or {}
        consensus_summary.append({
            "id": c.get("id"),
            "type": ("ENTERING" if c.get("entering_corridor")
                     else "INTERZONE" if c.get("interzone_generated") else "V30"),
            "valid": eco.get("valid"),
            "reason": eco.get("reason"),
            "consensus_score": (eco.get("consensus") or {}).get("consensus_score"),
            "label": (eco.get("consensus") or {}).get("label"),
            "metrics": eco.get("metrics"),
        })

    return JSONResponse({
        "phase": "PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω",
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "consensus_weights": dict(ECOLOGICAL_CONSENSUS_WEIGHTS),
        "external_ring_fraction": EXTERNAL_RING_FRACTION,
        "stats": bundle.get("ecological_orchestrator_stats") or {},
        "heatmaps_status": get_heatmaps_status(),
        "consensus_per_corridor_sample": consensus_summary,
        "v30_locked": True,
        "diagnostic_corridors_omega_activated": False,
    })
