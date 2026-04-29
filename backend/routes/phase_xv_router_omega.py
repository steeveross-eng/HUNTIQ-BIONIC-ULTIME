"""
phase_xv_router_omega.py — Router FastAPI Phase XV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3

Endpoints (READ-ONLY) :
  /api/v30/scientifique/list                    — liste des 5 + IA
  /api/v30/scientifique/spec/{engine_name}      — spec d'un engine
  /api/v30/scientifique/{engine_name}/{species} — compute d'un engine
  /api/v30/scientifique/ia/run                  — exécute ENGINE_IA_Ω
  /api/v30/scientifique/all/{species}           — exécute les 5 sur une espèce
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from engines.v8_institutional.scientifique_omega import (
    ENGINES_SCIENTIFIQUES_Ω,
    compute_vision, compute_odeur, compute_patterns,
    compute_comportement, compute_sensoriel, compute_ia,
    ENGINE_VISION_SPEC, ENGINE_ODEUR_SPEC, ENGINE_PATTERNS_SPEC,
    ENGINE_COMPORTEMENT_SPEC, ENGINE_SENSORIEL_SPEC, ENGINE_IA_SPEC,
)
from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
    BioReacteurError, ESPECES_SUPPORTEES,
)


router = APIRouter(prefix="/api/v30/scientifique", tags=["phase_xv_scientifique_omega"])

ENGINE_NAME_MAP = {
    "VISION": ("ENGINE_VISION_Ω", compute_vision, ENGINE_VISION_SPEC),
    "ODEUR": ("ENGINE_ODEUR_Ω", compute_odeur, ENGINE_ODEUR_SPEC),
    "PATTERNS": ("ENGINE_PATTERNS_Ω", compute_patterns, ENGINE_PATTERNS_SPEC),
    "COMPORTEMENT": ("ENGINE_COMPORTEMENT_Ω", compute_comportement, ENGINE_COMPORTEMENT_SPEC),
    "SENSORIEL": ("ENGINE_SENSORIEL_Ω", compute_sensoriel, ENGINE_SENSORIEL_SPEC),
}


def _resolve_name(name: str):
    n = name.upper().strip()
    if n.startswith("ENGINE_"):
        n = n[len("ENGINE_"):]
    if n.endswith("_Ω"):
        n = n[:-2]
    if n.endswith("_OMEGA"):
        n = n[:-len("_OMEGA")]
    return n


@router.get("/list")
async def scientifique_list():
    return JSONResponse(content={
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "engines_scientifiques": [
            {"engine_id": v[0], "spec_keys": list(v[2].keys())[:6]}
            for k, v in ENGINE_NAME_MAP.items()
        ],
        "engine_ia": {"engine_id": "ENGINE_IA_Ω", "spec_keys": list(ENGINE_IA_SPEC.keys())[:6]},
        "especes_supportees": list(ESPECES_SUPPORTEES),
        "bio_reacteur_dependency_obligatoire": True,
        "anti_generique_strict": True,
    })


@router.get("/spec/{engine_name}")
async def scientifique_spec(engine_name: str):
    n = _resolve_name(engine_name)
    if n == "IA":
        return JSONResponse(content={"spec": ENGINE_IA_SPEC})
    if n not in ENGINE_NAME_MAP:
        return JSONResponse(status_code=404, content={
            "error": f"engine inconnu: {engine_name}",
            "available": list(ENGINE_NAME_MAP.keys()) + ["IA"],
        })
    return JSONResponse(content={"spec": ENGINE_NAME_MAP[n][2]})


@router.get("/all/{species_id}")
async def scientifique_all(species_id: str):
    sp = species_id.upper()
    if sp not in ESPECES_SUPPORTEES:
        return JSONResponse(status_code=404, content={
            "error": f"espèce non supportée: {species_id}",
            "available": list(ESPECES_SUPPORTEES),
        })
    try:
        results = {
            "ENGINE_VISION_Ω": compute_vision(sp),
            "ENGINE_ODEUR_Ω": compute_odeur(sp),
            "ENGINE_PATTERNS_Ω": compute_patterns(sp),
            "ENGINE_COMPORTEMENT_Ω": compute_comportement(sp),
            "ENGINE_SENSORIEL_Ω": compute_sensoriel(sp),
        }
    except BioReacteurError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return JSONResponse(content={
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω",
        "espece_id": sp,
        "results": results,
    })


@router.post("/ia/run")
async def scientifique_ia_run(body: Optional[Dict[str, Any]] = Body(default=None)):
    body = body or {}
    return JSONResponse(content=compute_ia(body.get("env") or {}))


@router.get("/{engine_name}/{species_id}")
async def scientifique_compute(engine_name: str, species_id: str,
                                env: Optional[Dict[str, Any]] = Body(default=None)):
    n = _resolve_name(engine_name)
    sp = species_id.upper()
    if sp not in ESPECES_SUPPORTEES:
        return JSONResponse(status_code=404, content={
            "error": f"espèce non supportée: {species_id}",
            "available": list(ESPECES_SUPPORTEES),
        })
    if n == "IA":
        return JSONResponse(content=compute_ia(env or {}))
    if n not in ENGINE_NAME_MAP:
        return JSONResponse(status_code=404, content={
            "error": f"engine inconnu: {engine_name}",
            "available": list(ENGINE_NAME_MAP.keys()) + ["IA"],
        })
    _, fn, _ = ENGINE_NAME_MAP[n]
    try:
        result = fn(sp, env or {})
    except BioReacteurError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return JSONResponse(content=result)


__all__ = ["router"]
