"""
species_presence_mask_router.py — PHASE_XVIII_BIO_PRESENCE_MASK_Ω
================================================================================
Endpoints d'observabilité et d'audit institutionnel pour le masque de présence.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_BIO_PRESENCE_MASK_Ω"])

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@router.get("/presence-mask")
async def presence_mask_diagnostic(
    lat: float = Query(OFFICIAL_LAT),
    lng: float = Query(OFFICIAL_LNG),
):
    """Retourne le masque de présence complet pour TOUTES les espèces officielles."""
    try:
        from engines.v8_institutional.species_presence_mask_omega import (
            get_species_presence_mask, get_registry_audit,
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    mask = get_species_presence_mask(lat, lng)
    mask["registry_audit"] = get_registry_audit()
    return JSONResponse(mask)


@router.get("/presence-mask/per-species")
async def presence_mask_species_diagnostic(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lng: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(16, ge=0, le=23),
):
    """Diagnostic pour une espèce : masque + pipeline court-circuité ou non."""
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
        from engines.v8_institutional.species_presence_mask_omega import get_species_presence
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    presence = get_species_presence(lat, lng, species)
    try:
        resp = FResp()
        bundle = await v20_territoire_bundle(
            response=resp, lat=lat, lon=lng, species=species,
            month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
        )
    except Exception as e:
        return JSONResponse({
            "phase": "PHASE_XVIII_BIO_PRESENCE_MASK_Ω",
            "presence": presence,
            "bundle_error": str(e),
        }, status_code=500)

    return JSONResponse({
        "phase": "PHASE_XVIII_BIO_PRESENCE_MASK_Ω",
        "subphase": "PHASE_XVIII_BIO_PRESENCE_MASK",
        "territoire": {"lat": lat, "lng": lng},
        "species": species,
        "month": month,
        "hour": hour,
        "presence": presence,
        "pipeline_halted_at_mask": bundle.get("bio_presence_mask_halt", False),
        "stats": bundle.get("bio_presence_mask_stats") or {},
        "corridors_in_response": len(bundle.get("corridors") or []),
        "corridors_rejected_bio_presence": bundle.get("corridors_rejected_bio_presence_mask") or [],
        "v30_locked": True,
    })
