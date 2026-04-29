"""
bio_reacteur_router_omega.py — Router FastAPI BIO-REACTEUR_Ω runtime
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XIII

Endpoints (tous READ-ONLY, sous /api/v30/especes/bio-reacteur) :
  GET  /list                        → 5 BIO_REACTEURS chargés (metadata).
  GET  /integrity                   → audit intégrité runtime (SHA-256).
  GET  /{species_id}                → BIO_REACTEUR_Ω complet d'une espèce.
  GET  /{species_id}/{engine_name}  → paramètres d'un ENGINE output.
  POST /compute                     → pipeline COMBINÉ engines + BIO-REACTEUR.

Aucune écriture, aucune modification d'état.
V30 INVIOLÉ — engines existants intouchés.
"""
from __future__ import annotations
from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
    BioReacteurError,
    ESPECES_SUPPORTEES, ENGINE_OUTPUTS,
    load_bio_reacteur, list_loaded, integrity_report, get_bio_reacteur_outputs,
    attach_bio_reacteur_to_compute_result,
)
from engines.v8_institutional.especes.engine_especes_omega import (
    ENGINES_ESPECES_Ω, execute_pipeline_stage,
)
from engines.v8_institutional.especes.audit_especes_omega import (
    get_audit_status, is_validated,
)


router = APIRouter(prefix="/api/v30/especes/bio-reacteur", tags=["bio_reacteur_omega"])


@router.get("/list")
async def bio_reacteur_list():
    return JSONResponse(content={
        "phase": "PHASE_XIII_BIO_REACTEURS_Ω_RUNTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "audit_status": get_audit_status(),
        "engines_especes_omega_actives": is_validated(),
        "loaded": list_loaded(),
    })


@router.get("/integrity")
async def bio_reacteur_integrity():
    return JSONResponse(content=integrity_report())


@router.get("/{species_id}")
async def bio_reacteur_get_one(species_id: str):
    species_id = species_id.upper()
    if species_id not in ESPECES_SUPPORTEES:
        return JSONResponse(
            status_code=404,
            content={
                "error": f"espèce non supportée: {species_id}",
                "available": ESPECES_SUPPORTEES,
            },
        )
    try:
        reacteur = load_bio_reacteur(species_id)
    except BioReacteurError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return JSONResponse(content=reacteur)


@router.get("/{species_id}/{engine_name}")
async def bio_reacteur_get_engine(species_id: str, engine_name: str):
    species_id = species_id.upper()
    engine_name = engine_name.upper()
    if not engine_name.startswith("ENGINE_"):
        engine_name = "ENGINE_" + engine_name
    if species_id not in ESPECES_SUPPORTEES:
        return JSONResponse(
            status_code=404,
            content={"error": f"espèce non supportée: {species_id}",
                     "available": ESPECES_SUPPORTEES},
        )
    if engine_name not in ENGINE_OUTPUTS:
        return JSONResponse(
            status_code=404,
            content={"error": f"engine non défini: {engine_name}",
                     "available": ENGINE_OUTPUTS},
        )
    try:
        params = get_bio_reacteur_outputs(species_id, engine_name)
    except BioReacteurError as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    return JSONResponse(content={
        "phase": "PHASE_XIII_BIO_REACTEURS_Ω_RUNTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "espece_id": species_id,
        "engine_name": engine_name,
        "parametres": params,
    })


@router.post("/compute")
async def bio_reacteur_compute(body: Optional[Dict[str, Any]] = Body(default=None)):
    """Pipeline combiné : engine.compute(env) + BIO-REACTEUR_Ω attaché."""
    body = body or {}
    env = body.get("env") or {
        "temperature_c": 18.0, "snow_depth_cm": 25.0, "summer_avg_temp_c": 22.0,
        "predation_index": 0.6, "routes_density": 0.85, "urbanisation_pct": 12.0,
        "agriculture_pct": 18.0, "forest_patches_count": 15, "largest_patch_index": 62.0,
        "edge_density": 85.0, "cwd_prevalence_pct": 0.5, "lpdv_prevalence_pct": 1.5,
        "connectivity_index": 0.62, "waste_proximity_pct": 8.0, "crops_attractive_pct": 14.0,
        "mast_availability_index": 65.0, "understory_density_pct": 58.0,
        "forest_agri_mosaic_index": 0.55,
    }
    filt: Optional[List[str]] = body.get("filter")

    pipeline = execute_pipeline_stage(env, filter_especes=filt)
    decorated = {}
    for esp_id, result in pipeline["results_per_species"].items():
        decorated[esp_id] = attach_bio_reacteur_to_compute_result(result, esp_id)
    pipeline["results_per_species"] = decorated
    pipeline["bio_reacteur_runtime_attached"] = True
    pipeline["phase_xiii"] = "BIO_REACTEURS_Ω_RUNTIME"
    return JSONResponse(content=pipeline)


__all__ = ["router"]
