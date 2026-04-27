"""
corridors_vitaux_router.py — PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω
================================================================================
Endpoint d'observabilité institutionnelle pour le filtre CORRIDORS VITAUX Ω.

Retourne :
  - statut du filtre vitaux (rate, rejets, ancrages utilisés)
  - règle institutionnelle appliquée par espèce (groupe)
  - log des rejets (corridors_rejected_vitaux_xviii)
"""
from __future__ import annotations

import json
from pathlib import Path
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_CORRIDORS_VITAUX_Ω"])

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@router.get("/vitaux-omega")
async def corridors_vitaux_diagnostic(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Diagnostic complet du filtre CORRIDORS_VITAUX_Ω sur le bundle live."""
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
        from engines.v8_institutional.corridors_vitaux_omega import (
            ANCHOR_PROXIMITY_M, ENFORCE_MODE, AUDIT_LOG_PATH,
            VITAL_ZONES_MAJOR, VITAL_ZONES_SECONDARY, TRANSITION_ZONES,
            SPECIES_GROUP,
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
        v = c.get("vitaux_validation") or {}
        summary.append({
            "id": c.get("id"),
            "type": ("ENTERING" if c.get("entering_corridor")
                     else "INTERZONE" if c.get("interzone_generated") else "V30"),
            "valid": v.get("valid"),
            "reason": v.get("reason"),
            "anchors_summary": v.get("anchors_summary"),
        })

    rejected = bundle.get("corridors_rejected_vitaux_xviii") or []

    return JSONResponse({
        "phase": "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω",
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "species_group": SPECIES_GROUP.get(species.lower(), "PETITS_MAMMIFERES"),
        "month": month,
        "hour": hour,
        "anchor_proximity_m": ANCHOR_PROXIMITY_M,
        "enforce_mode": ENFORCE_MODE,
        "vital_zones_major": sorted(VITAL_ZONES_MAJOR),
        "vital_zones_secondary": sorted(VITAL_ZONES_SECONDARY),
        "transition_zones": sorted(TRANSITION_ZONES),
        "audit_log_path": str(AUDIT_LOG_PATH),
        "stats": bundle.get("corridors_vitaux_omega_stats") or {},
        "kept_per_corridor_sample": summary,
        "rejected_in_this_run": rejected[:10],
        "v30_locked": True,
    })


@router.get("/vitaux-omega/audit-log")
async def vitaux_audit_log_read():
    """Renvoie le log JSON cumulatif des rejets pour audit institutionnel."""
    try:
        from engines.v8_institutional.corridors_vitaux_omega import AUDIT_LOG_PATH
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    if not AUDIT_LOG_PATH.exists():
        return JSONResponse({"phase": "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω",
                             "log_path": str(AUDIT_LOG_PATH),
                             "entries": [], "entry_count": 0})
    try:
        data = json.loads(AUDIT_LOG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return JSONResponse({"error": f"log_parse_failed: {e}"}, status_code=500)
    return JSONResponse({
        "phase": "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω",
        "log_path": str(AUDIT_LOG_PATH),
        "entry_count": len(data) if isinstance(data, list) else 0,
        "entries_last_20": data[-20:] if isinstance(data, list) else [],
    })
