"""
especes_omega_router.py — Router FastAPI ENGINE_ESPECES_Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω

Routes :
  GET  /api/v30/especes/list              → 5 espèces metadata BCE-4X
  GET  /api/v30/especes/lock-signature    → SHA-256 institutionnel
  POST /api/v30/especes/compute           → exécute pipeline stage
  GET  /api/v30/especes/{species_id}      → profil + compute par défaut
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from engines.v8_institutional.especes.engine_especes_omega import (
    ENGINES_ESPECES_Ω, Z_ORDRE_Ω_ESPECES,
    list_especes, execute_pipeline_stage, get_lock_signature,
)
from engines.v8_institutional.especes.audit_especes_omega import (
    run_full_audit, get_audit_status, is_validated,
    request_validation, revoke_validation,
)


router = APIRouter(prefix="/api/v30/especes", tags=["especes_omega"])


# Environnement par défaut institutionnel (pour endpoints GET sans body)
DEFAULT_ENV = {
    "temperature_c": 18.0,
    "snow_depth_cm": 25.0,
    "summer_avg_temp_c": 22.0,
    "predation_index": 0.6,
    "routes_density": 0.85,
    "urbanisation_pct": 12.0,
    "agriculture_pct": 18.0,
    "forest_patches_count": 15,
    "largest_patch_index": 62.0,
    "edge_density": 85.0,
    "cwd_prevalence_pct": 0.5,
    "lpdv_prevalence_pct": 1.5,
    "connectivity_index": 0.62,
    "waste_proximity_pct": 8.0,
    "crops_attractive_pct": 14.0,
    "mast_availability_index": 65.0,
    "understory_density_pct": 58.0,
    "forest_agri_mosaic_index": 0.55,
}


@router.get("/list")
async def especes_list():
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        "engines_count": len(ENGINES_ESPECES_Ω),
        "z_ordre": Z_ORDRE_Ω_ESPECES,
        "engines": list_especes(),
    })


@router.get("/lock-signature")
async def especes_lock_signature():
    sig = get_lock_signature()
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        **sig,
    })


@router.get("/audit/status")
async def especes_audit_status():
    """Statut courant de validation de l'audit BCE-4X."""
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω_AUDIT_BCE4X",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        **get_audit_status(),
        "is_validated": is_validated(),
    })


@router.get("/audit/run")
async def especes_audit_run():
    """Exécute l'audit BCE-4X complet (lecture seule) sur les 5 engines."""
    return JSONResponse(content=run_full_audit())


@router.post("/audit/validate")
async def especes_audit_validate(body: Dict[str, Any] = Body(...)):
    """Valide l'audit BCE-4X (Article 4 — verrouillage conditionnel).

    Body : {"token": "STEEVE-MAX-PHASE-XII-AUDIT-BCE4X-VALIDE", "signataire": "STEEVE-MAX"}
    """
    token = body.get("token", "")
    signataire = body.get("signataire", "STEEVE-MAX")
    ok, msg = request_validation(token, signataire)
    if not ok:
        return JSONResponse(
            status_code=403,
            content={
                "phase": "PHASE_XII_ESPECES_Ω_AUDIT_BCE4X",
                "validated": False, "message": msg,
                "audit_status": get_audit_status(),
            },
        )
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω_AUDIT_BCE4X",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        "validated": True, "message": msg,
        "audit_status": get_audit_status(),
    })


@router.post("/audit/revoke")
async def especes_audit_revoke():
    """Révoque la validation (retour EN_ATTENTE)."""
    revoke_validation()
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω_AUDIT_BCE4X",
        "revoked": True,
        "audit_status": get_audit_status(),
    })


@router.post("/compute")
async def especes_compute(
    body: Optional[Dict[str, Any]] = Body(default=None),
):
    """Exécute le pipeline stage ENGINE_ESPECES_Ω.

    Body optionnel :
      {
        "env": { ... }          # surcharge l'environnement par défaut
        "filter": ["CHEVREUIL", "ORIGNAL"]  # liste d'espece_id (None = toutes)
      }
    """
    body = body or {}
    env = {**DEFAULT_ENV, **(body.get("env") or {})}
    filter_especes = body.get("filter")
    out = execute_pipeline_stage(env, filter_especes=filter_especes)
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        "env_used": env,
        **out,
    })


@router.get("/{species_id}")
async def especes_get_one(species_id: str):
    species_id = species_id.upper()
    if species_id not in ENGINES_ESPECES_Ω:
        return JSONResponse(
            status_code=404,
            content={"error": f"espèce inconnue: {species_id}",
                     "available": list(ENGINES_ESPECES_Ω.keys())},
        )
    profile, compute = ENGINES_ESPECES_Ω[species_id]
    result = compute(DEFAULT_ENV)
    return JSONResponse(content={
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        "espece_id": profile.espece_id,
        "nom_scientifique": profile.nom_scientifique,
        "tableau_maitre_ref": profile.tableau_maitre_ref,
        "sources": [
            {"institution": s.institution, "type": s.type, "title": s.title,
             "year": s.year, "doi_or_url": s.doi_or_url}
            for s in profile.sources
        ],
        "seuils": [
            {"metric": s.metric, "valeur": s.valeur, "unite": s.unite,
             "type": s.seuil_type, "source": s.source, "note": s.note}
            for s in profile.seuils
        ],
        "dimensions_scientifiques": profile.dimensions_scientifiques,
        "sorties_territoire": profile.sorties_territoire,
        "style_palette": profile.style_palette,
        "compute_result_default_env": result,
    })
