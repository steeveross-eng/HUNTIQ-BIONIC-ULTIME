"""
Route dédiée ENGINE_RENDUΩ — validation isolée d'un corridor
==============================================================
Phase : PHASE_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω
Commandant STEEVE-MAX

POST /api/v7-ultime/renduomega/validate   — valide un corridor unique
POST /api/v7-ultime/renduomega/validate-bundle — valide un bundle complet
GET  /api/v7-ultime/renduomega/status     — lecture seule du moteur
"""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from engines.post_smoothing.renduomega import (
    apply_renduomega_to_bundle,
    validate_corridor,
    is_p5_authorized,
    BASE_COLOR_ORANGE_AMBRE,
    OPACITY_MIN,
    MIN_ZOOM,
    WIDTHS_ALLOWED,
    ZINDEX_INSTITUTIONNEL,
    GEOM_MIN_POINTS,
    GEOM_MAX_POINTS,
    GEOM_MAX_SEGMENT_M,
    GEOM_MAX_ANGLE_DEG,
    GEOM_MIN_LENGTH_M,
    TERRAIN_RADIUS_MIN_M,
    TERRAIN_RADIUS_MAX_M,
    TERRAIN_SLOPE_MAX_DEG,
    TERRAIN_WATER_MIN_M,
    SPECIES_COLOR_PALETTE,
    P5_RENDUOMEGA_ENABLED,
)

router = APIRouter(
    prefix="/api/v7-ultime/renduomega",
    tags=["ENGINE_RENDUΩ_X200_P5"],
)


@router.get("/status")
async def renduomega_status():
    auth = is_p5_authorized()
    return JSONResponse({
        "engine_id": "ENGINE_RENDUΩ",
        "phase": "X200-P5-RENDUΩ-INTEGRATION-ULTIME",
        "flag_enabled": P5_RENDUOMEGA_ENABLED,
        "authorization": auth,
        "constants": {
            "base_color": BASE_COLOR_ORANGE_AMBRE,
            "species_palette": SPECIES_COLOR_PALETTE,
            "opacity_min": OPACITY_MIN,
            "min_zoom": MIN_ZOOM,
            "widths_allowed_px": list(WIDTHS_ALLOWED),
            "zindex_institutionnel": ZINDEX_INSTITUTIONNEL,
        },
        "geom_rules": {
            "min_points": GEOM_MIN_POINTS,
            "max_points": GEOM_MAX_POINTS,
            "min_length_m": GEOM_MIN_LENGTH_M,
            "max_segment_m": GEOM_MAX_SEGMENT_M,
            "max_angle_deg": GEOM_MAX_ANGLE_DEG,
        },
        "terrain_rules": {
            "radius_min_m": TERRAIN_RADIUS_MIN_M,
            "radius_max_m": TERRAIN_RADIUS_MAX_M,
            "slope_max_deg": TERRAIN_SLOPE_MAX_DEG,
            "water_min_m": TERRAIN_WATER_MIN_M,
        },
        "v30_modified": False,
        "diagnostic_panel_active": False,
    })


@router.post("/validate")
async def renduomega_validate(payload: Dict[str, Any] = None):
    if not is_p5_authorized()["authorized"]:
        raise HTTPException(status_code=503, detail={
            "error": "p5_not_authorized",
            "phase": "X200-P5",
        })
    p = payload or {}
    corridor = p.get("corridor") or {}
    return JSONResponse(validate_corridor(
        corridor,
        center=p.get("center"),
        terrain_signals=p.get("terrain_signals"),
        contamination_zones=p.get("contamination_zones"),
        affuts=p.get("affuts"),
        bundle_species=p.get("species"),
    ))


@router.post("/validate-bundle")
async def renduomega_validate_bundle(payload: Dict[str, Any] = None):
    if not is_p5_authorized()["authorized"]:
        raise HTTPException(status_code=503, detail={
            "error": "p5_not_authorized",
            "phase": "X200-P5",
        })
    bundle = payload or {}
    result = apply_renduomega_to_bundle(dict(bundle))
    return JSONResponse({
        "renduomega_integration": result.get("renduomega_integration"),
        "smoother_p5_renduomega_applied": result.get("smoother_p5_renduomega_applied", False),
        "corridors_accepted_count": len(result.get("corridors") or []),
        "corridors_rejected_count": len(result.get("corridors_rejected_by_renduomega") or []),
    })
