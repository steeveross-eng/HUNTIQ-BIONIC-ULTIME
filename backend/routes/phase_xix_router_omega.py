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



# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°53 — Couplage direct SUPER_ENGINES ↔ BIO_PROFILE_OMEGA_135
# ═════════════════════════════════════════════════════════════════════════
import os
from fastapi import Header
from typing import Optional


def _verify_commandant_token(x_commandant_token: Optional[str]) -> None:
    expected = os.environ.get("GIS_RECEPTION_COMMANDANT_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="GIS_RECEPTION_COMMANDANT_TOKEN_NOT_CONFIGURED")
    if (not x_commandant_token
            or x_commandant_token.strip() != expected.strip()):
        raise HTTPException(status_code=401, detail="ADMIN_PREMIUM_ONLY")


@router.post("/bp135-coupling-execute")
async def bp135_coupling_execute(
    mode: str = "fusion",
    weight_bio_reacteur: float = 0.5,
    weight_bp135: float = 0.5,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°53 + N°53-BIS · Couplage SUPER_ENGINES ↔ BP135.

    Modes :
      · `direct`         → 6 scores BP135 directs
      · `fusion`         → fusion pondérée BIO_REACTEUR × BP135
      · `audit`          → drift report forensique
      · `overlay_scan`   → scan registry-aware des 6 sources externes
      · `overlay_fusion` → recouplage POST-overlay BP135→BR + persistance audit

    Token Commandant requis (X-Commandant-Token).
    Garde-fous : V30_LOCK SHA-256 vérifié, FUSION ADD-ONLY strict.
    """
    _verify_commandant_token(x_commandant_token)

    valid_modes = {"direct", "fusion", "audit",
                   "overlay_fusion", "overlay_scan"}
    if mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"MODE_INVALIDE::{mode} :: valides={sorted(valid_modes)}")

    from engines.v8_institutional.especes.super_engines_bp135_coupling_omega import (  # noqa: E501
        compute_all_masters_direct_bp135,
        compute_super_engines_bp135_fusion,
        audit_bp135_vs_bioreacteur_drift,
        CouplingError,
    )

    try:
        if mode == "direct":
            payload = compute_all_masters_direct_bp135()
        elif mode == "fusion":
            payload = compute_super_engines_bp135_fusion(
                weights={
                    "bio_reacteur": weight_bio_reacteur,
                    "bp135": weight_bp135,
                })
        elif mode == "audit":
            payload = audit_bp135_vs_bioreacteur_drift()
        elif mode == "overlay_scan":
            from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
                scan_external_sources,
            )
            payload = scan_external_sources()
        else:  # overlay_fusion
            from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
                compute_overlay_fusion, persist_audit,
                scan_external_sources,
            )
            overlay_payload = compute_overlay_fusion(
                weights={
                    "bio_reacteur_overlay": weight_bio_reacteur,
                    "bp135": weight_bp135,
                })
            sources_scan = scan_external_sources()
            payload = {
                **overlay_payload,
                "external_sources_scan": sources_scan,
            }
            audit_meta = persist_audit(payload)
            payload["audit_persisted"] = audit_meta
    except CouplingError as e:
        raise HTTPException(
            status_code=400, detail=f"COUPLING_ERROR::{e}")
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "BP135_COUPLING_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })

    return JSONResponse({
        "manifest_id": "SUPER_ENGINES_BP135_COUPLING_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°53",
        "mode_requested": mode,
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°53-BIS-SUITE — Recompute + Audits list public read-only
# ═════════════════════════════════════════════════════════════════════════
@router.post("/recompute-with-drift-audit")
async def recompute_with_drift_audit_endpoint(
    reason: str = "manual_recompute",
    weight_bio_reacteur: float = 0.5,
    weight_bp135: float = 0.5,
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°53-BIS-SUITE · Recouplage avec audit BEFORE/AFTER dédié.

    Génère un audit forensique avec snapshot avant/après recouplage et
    persiste le résultat dans `/app/backend/data/audits_bp135/`.

    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        recompute_with_drift_audit,
    )
    try:
        payload = recompute_with_drift_audit(
            reason=reason,
            weights={
                "bio_reacteur_overlay": weight_bio_reacteur,
                "bp135": weight_bp135,
            },
            persist=persist,
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "RECOMPUTE_AUDIT_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })

    return JSONResponse({
        "manifest_id": "RECOMPUTE_DRIFT_AUDIT_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°53-BIS-SUITE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/audits-list")
async def audits_list_endpoint(
    page: int = 1,
    page_size: int = 50,
    drift_max_min: Optional[float] = None,
    drift_max_max: Optional[float] = None,
    drift_mean_min: Optional[float] = None,
    drift_mean_max: Optional[float] = None,
    since_utc: Optional[str] = None,
    audit_type: Optional[str] = None,
) -> JSONResponse:
    """ORDRE N°53-BIS-SUITE · Liste paginée et filtrable des audits BP135.

    API PUBLIQUE READ-ONLY · paginée · filtrable.
    Strictement dérivée des fichiers d'audit persistés. Aucune mutation.

    Champs obligatoires retournés par audit :
      · audit_id, timestamp_utc, sha256
      · drift_max, drift_mean, score_global_fusion
      · bp135_sha256

    Filtres optionnels : drift_max_min/max, drift_mean_min/max, since_utc,
    audit_type.
    """
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        list_audits,
    )
    try:
        payload = list_audits(
            page=page, page_size=page_size,
            drift_max_min=drift_max_min,
            drift_max_max=drift_max_max,
            drift_mean_min=drift_mean_min,
            drift_mean_max=drift_mean_max,
            since_utc=since_utc,
            audit_type=audit_type,
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "AUDITS_LIST_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })

    return JSONResponse({
        "manifest_id": "AUDITS_LIST_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°53-BIS-SUITE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })
