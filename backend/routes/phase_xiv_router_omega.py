"""
phase_xiv_router_omega.py — Router FastAPI Phase XIV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3

Endpoints (READ-ONLY) :
  BLOC 2 — CI HOOK SCEAU :
    GET  /api/v30/sceau-phase-xiii/verify
    GET  /api/v30/sceau-phase-xiii/reference
    GET  /api/v30/sceau-phase-xiii/log

  BLOC 3 — AUDIT LONGITUDINAL :
    GET  /api/v30/audit-longitudinal/snapshot
    GET  /api/v30/audit-longitudinal/diff
    GET  /api/v30/audit-longitudinal/history
    GET  /api/v30/audit-longitudinal/paths
    GET  /api/v30/audit-longitudinal/pipeline-continuity
    GET  /api/v30/audit-longitudinal/full

  BLOC 4 — SUPER ENGINES_Ω (interfaces uniquement) :
    GET  /api/v30/super-engines/list
    GET  /api/v30/super-engines/{super_engine_id}
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from engines.v8_institutional.especes.sceau_phase_xiii_validator_omega import (
    verify_sceau, recompute_sceau_cumulatif, get_sceau_reference,
    SCEAU_LOG_PATH,
)
from engines.v8_institutional.especes.audit_longitudinal_omega import (
    take_snapshot, list_history, diff_against_baseline,
    list_paths_propagation, pipeline_continuity_check,
    full_longitudinal_report,
)
from engines.v8_institutional.especes.super_engines_omega_specs import (
    SUPER_ENGINES_Ω, list_super_engines,
)
from dataclasses import asdict


router = APIRouter(prefix="/api/v30", tags=["phase_xiv_omega"])


# ─────────────────────────────────────────────────────────────────────
# BLOC 2 — CI HOOK SCEAU
# ─────────────────────────────────────────────────────────────────────

@router.get("/sceau-phase-xiii/verify")
async def sceau_verify():
    return JSONResponse(content=verify_sceau())


@router.get("/sceau-phase-xiii/reference")
async def sceau_reference():
    live = recompute_sceau_cumulatif()
    ref = get_sceau_reference()
    return JSONResponse(content={
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_CI_HOOK_SCEAU_VALIDATION",
        "reference": ref,
        "live": {k: v for k, v in live.items() if k != "ok" or live["ok"]},
    })


@router.get("/sceau-phase-xiii/log")
async def sceau_log():
    if not SCEAU_LOG_PATH.exists():
        return PlainTextResponse("# Sceau validation log empty.\n", media_type="text/plain")
    return PlainTextResponse(SCEAU_LOG_PATH.read_text(encoding="utf-8"), media_type="text/plain")


# ─────────────────────────────────────────────────────────────────────
# BLOC 3 — AUDIT LONGITUDINAL
# ─────────────────────────────────────────────────────────────────────

@router.get("/audit-longitudinal/snapshot")
async def audit_snapshot():
    return JSONResponse(content=take_snapshot())


@router.get("/audit-longitudinal/diff")
async def audit_diff():
    return JSONResponse(content=diff_against_baseline())


@router.get("/audit-longitudinal/history")
async def audit_history():
    return JSONResponse(content={
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_AUDIT_LONGITUDINAL_Ω",
        "snapshots_count": len(list_history()),
        "snapshots": list_history(),
    })


@router.get("/audit-longitudinal/paths")
async def audit_paths():
    return JSONResponse(content=list_paths_propagation())


@router.get("/audit-longitudinal/pipeline-continuity")
async def audit_pipeline_continuity():
    return JSONResponse(content=pipeline_continuity_check())


@router.get("/audit-longitudinal/full")
async def audit_full():
    return JSONResponse(content=full_longitudinal_report())


# ─────────────────────────────────────────────────────────────────────
# BLOC 4 — SUPER ENGINES_Ω (pré-activation, interfaces uniquement)
# ─────────────────────────────────────────────────────────────────────

@router.get("/super-engines/list")
async def super_engines_list_endpoint():
    return JSONResponse(content=list_super_engines())


@router.get("/super-engines/{super_engine_id}")
async def super_engine_get(super_engine_id: str):
    sid = super_engine_id
    if not sid.endswith("_Ω"):
        sid = sid + "_Ω"
    if not sid.upper().startswith("ENGINE_"):
        sid = "ENGINE_" + sid
    sid_upper = sid.upper()
    # Recherche flexible
    match = next((k for k in SUPER_ENGINES_Ω if k.upper() == sid_upper or k == sid), None)
    if not match:
        return JSONResponse(
            status_code=404,
            content={"error": f"SUPER_ENGINE inconnu: {super_engine_id}",
                     "available": list(SUPER_ENGINES_Ω.keys())},
        )
    spec = SUPER_ENGINES_Ω[match]
    return JSONResponse(content={
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_PRE_ACTIVATION_SUPER_ENGINES_Ω",
        "super_engine": asdict(spec),
        "activation_logique_disponible_en": "PHASE_XV",
    })


__all__ = ["router"]
