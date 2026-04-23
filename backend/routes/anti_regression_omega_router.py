"""
Route dédiée ANTI_REGRESSION_Ω — observation continue des 12 sous-normes X150
=============================================================================
Phase : PHASE_X200_P6_ANTI_RÉGRESSION_Ω
Commandant STEEVE-MAX

GET  /api/v7-ultime/anti-regression/status       — état triple verrou + vue globale
GET  /api/v7-ultime/anti-regression/metrics      — compteurs cumulés par sous-norme
GET  /api/v7-ultime/anti-regression/violations   — violations horodatées (filtres)
GET  /api/v7-ultime/anti-regression/audit-matrix — matrice corridor × sous-norme (pour P7)
POST /api/v7-ultime/anti-regression/reset        — purge (ordre explicite du Commandant)
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import JSONResponse

from engines.post_smoothing.anti_regression_omega import (
    is_p6_authorized,
    get_ledger_snapshot,
    get_recent_violations,
    build_audit_matrix,
    reset_ledger,
    SUB_NORMES_X150,
    P6_EXPECTED_TOKEN,
)

router = APIRouter(
    prefix="/api/v7-ultime/anti-regression",
    tags=["ANTI_REGRESSION_Ω_X200_P6"],
)


@router.get("/status")
async def anti_regression_status():
    auth = is_p6_authorized()
    snap = get_ledger_snapshot()
    return JSONResponse({
        "engine_id": "ANTI_REGRESSION_Ω",
        "phase": "X200-P6-ANTI_REGRESSION_Ω",
        "authorization": auth,
        "sub_normes_count": len(SUB_NORMES_X150),
        "sub_normes": {
            k: {"label": v["label"]}
            for k, v in SUB_NORMES_X150.items()
        },
        "summary": snap["summary"],
        "events_kept": snap["events_kept"],
        "events_max": snap["events_max"],
        "v30_modified": False,
        "diagnostic_panel_active": False,
    })


@router.get("/metrics")
async def anti_regression_metrics():
    if not is_p6_authorized()["authorized"]:
        raise HTTPException(status_code=503, detail={
            "error": "p6_not_authorized",
            "phase": "X200-P6",
        })
    return JSONResponse(get_ledger_snapshot())


@router.get("/violations")
async def anti_regression_violations(
    limit: int = Query(100, ge=1, le=2000),
    sub_norme: Optional[str] = Query(None),
    corridor_id: Optional[str] = Query(None),
):
    if not is_p6_authorized()["authorized"]:
        raise HTTPException(status_code=503, detail={
            "error": "p6_not_authorized",
            "phase": "X200-P6",
        })
    return JSONResponse({
        "violations": get_recent_violations(
            limit=limit,
            sub_norme=sub_norme,
            corridor_id=corridor_id,
        ),
        "filters": {
            "limit": limit,
            "sub_norme": sub_norme,
            "corridor_id": corridor_id,
        },
    })


@router.get("/audit-matrix")
async def anti_regression_audit_matrix():
    if not is_p6_authorized()["authorized"]:
        raise HTTPException(status_code=503, detail={
            "error": "p6_not_authorized",
            "phase": "X200-P6",
        })
    return JSONResponse(build_audit_matrix())


@router.post("/reset")
async def anti_regression_reset(
    x_commandant_token: Optional[str] = Header(None, alias="X-Commandant-Token"),
):
    """Purge le registre. Requiert entête `X-Commandant-Token` == token P6."""
    if not is_p6_authorized()["authorized"]:
        raise HTTPException(status_code=503, detail={
            "error": "p6_not_authorized",
            "phase": "X200-P6",
        })
    if (x_commandant_token or "").strip() != P6_EXPECTED_TOKEN:
        raise HTTPException(status_code=403, detail={
            "error": "commandant_token_required",
            "phase": "X200-P6",
        })
    return JSONResponse(reset_ledger())
