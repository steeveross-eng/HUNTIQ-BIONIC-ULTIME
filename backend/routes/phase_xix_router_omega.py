"""
phase_xix_router_omega.py — Router FastAPI Phase XIX (ORDRE N°39)
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 (ORDRE N°39)

Endpoints lecture seule pour les 6 SUPER MASTERS optimisés :
  GET /api/v30/super-masters/list
  GET /api/v30/super-masters/{master_id}/optimised
  GET /api/v30/super-masters/sceau/status

master_id ∈ {corridors, nutrition, sensoriel, comportement, gouvernance, territoire}
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/api/v30/super-masters", tags=["v30-super-masters"])

REPORTS_ROOT = Path("/app/frontend/public/reports/purge_master_omega")
SIX_MASTERS_PATH = REPORTS_ROOT / "SIX_MASTERS_Ω_OPTIMISÉS.json"
TERRITOIRE_PATH = REPORTS_ROOT / "TERRITOIRE_MASTER_Ω_FUSION_X4.json"
SCEAU_PATH = Path("/app/backend/institution/sceaux/SCEAU_INSTITUTIONNEL_X4_FINAL_Ω.sha256")

# Mapping URL → identifiant interne canonique
MASTER_ID_MAP = {
    "corridors": "CORRIDORS_MASTER_Ω",
    "nutrition": "NUTRITION_MASTER_Ω",
    "sensoriel": "SENSORIEL_MASTER_Ω",
    "comportement": "COMPORTEMENT_MASTER_Ω",
    "gouvernance": "GOUVERNANCE_MASTER_Ω",
    "territoire": "TERRITOIRE_MASTER_Ω",
}


def _load_six_masters() -> Dict[str, Any]:
    if not SIX_MASTERS_PATH.exists():
        raise HTTPException(status_code=503,
                              detail="SIX_MASTERS_NOT_AVAILABLE")
    with open(SIX_MASTERS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_sceau() -> Dict[str, Any]:
    if not SCEAU_PATH.exists():
        return {"sceau_sha256": None, "status": "ABSENT"}
    txt = SCEAU_PATH.read_text(encoding="utf-8").strip()
    return {"sceau_sha256": txt, "status": "PRESENT"}


def _build_horodatage() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@router.get("/list")
async def list_super_masters() -> JSONResponse:
    """Liste les 6 SUPER MASTERS exposés."""
    data = _load_six_masters()
    sceau = _load_sceau()
    return JSONResponse({
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°39",
        "horodatage_build": _build_horodatage(),
        "masters_disponibles": list(MASTER_ID_MAP.keys()),
        "masters_canonical": list(MASTER_ID_MAP.values()),
        "source": "BIO_PROFILE_Ω_135 + DATASETS_Ω_FUSION_ADDONLY",
        "sceau": sceau,
        "masters_signature_sha256": data.get("masters_signature_sha256"),
    })


@router.get("/sceau/status")
async def sceau_status() -> JSONResponse:
    """Statut du SCEAU_INSTITUTIONNEL_X4_FINAL_Ω."""
    sceau = _load_sceau()
    territoire_score = None
    if TERRITOIRE_PATH.exists():
        try:
            with open(TERRITOIRE_PATH, encoding="utf-8") as f:
                t = json.load(f)
            territoire_score = t.get("territoire_master_x4_score")
        except Exception:
            pass
    return JSONResponse({
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°39",
        "horodatage_build": _build_horodatage(),
        "sceau": sceau,
        "territoire_master_x4_score": territoire_score,
        "decision": "APTE" if (territoire_score and territoire_score >= 70) else "MARGINAL",
    })


@router.get("/{master_id}/optimised")
async def get_master_optimised(master_id: str) -> JSONResponse:
    """Retourne le master optimisé (mode ADD-ONLY x4)."""
    if master_id not in MASTER_ID_MAP:
        raise HTTPException(status_code=404,
                              detail=f"MASTER_INCONNU::{master_id}")
    data = _load_six_masters()
    canonical = MASTER_ID_MAP[master_id]
    payload = data.get("masters_optimises", {}).get(canonical)
    if not payload:
        raise HTTPException(status_code=503,
                              detail=f"MASTER_DATA_MISSING::{canonical}")
    sceau = _load_sceau()
    return JSONResponse({
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°39",
        "horodatage_build": _build_horodatage(),
        "master_id": master_id,
        "master_canonical": canonical,
        "score_baseline": payload["score_baseline_n36"],
        "score_recalcule_via_135": payload["score_recalcule_via_135"],
        "score_optimise": payload["score_optimise_max"],
        "delta": payload["delta"],
        "blocs_consumes": payload["blocs_consumes"],
        "score_par_espece": payload["score_par_espece_recalcule"],
        "mode": payload["mode"],
        "source": "BIO_PROFILE_Ω_135 + DATASETS_Ω_FUSION_ADDONLY",
        "sceau": sceau,
    })
