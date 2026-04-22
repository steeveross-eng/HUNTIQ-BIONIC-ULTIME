"""
ENGINE_3D_TERRAIN_Ω — Router FastAPI squelette (inert)
Feature flag OFF : tous les endpoints renvoient HTTP 503 tant que non activés.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAG — DOIT RESTER FALSE JUSQU'À ORDRE X200
# ═══════════════════════════════════════════════════════════════════════
FEATURE_FLAG_ACTIVE: bool = False

ENGINE_ID = "ENGINE_3D_TERRAIN_Ω"
CATEGORY = "etendu"
ROLE = "DEM 1m/5m/10m, relief 3D, exposition, microrelief vectoriel"
MAX_KB_TARGET = 100

router = APIRouter(prefix="/api/v7-ultime/terrain-3d/compute", tags=["ENGINE_3D_TERRAIN_Ω_X199_PREPARATOIRE"])


@router.get("/status")
async def engine_status():
    """Métadonnées de l'engine (accessible même OFF, lecture seule)."""
    return JSONResponse({
        "engine_id": ENGINE_ID,
        "category": CATEGORY,
        "role": ROLE,
        "max_kb_target": MAX_KB_TARGET,
        "feature_flag_active": FEATURE_FLAG_ACTIVE,
        "phase": "X199-PREPARATOIRE",
        "ready": False,
        "v30_modified": False,
        "diagnostic_panel_active": False,
    })


@router.post("/compute")
async def engine_compute(payload: dict = None):
    """Endpoint principal — INERT jusqu'à activation X200."""
    if not FEATURE_FLAG_ACTIVE:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "feature_flag_off",
                "engine_id": ENGINE_ID,
                "phase": "X199-PREPARATOIRE",
                "message": "Engine squelette — ordre X200 requis pour activation",
            },
        )
    # X200 remplira cette fonction avec la logique réelle
    return JSONResponse({"engine_id": ENGINE_ID, "computed": False,
                         "note": "X200 implementation pending"})
