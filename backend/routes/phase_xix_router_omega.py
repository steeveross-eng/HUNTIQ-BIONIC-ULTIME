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

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


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



# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°53-BIS-SUITE-ULTIME — Audits trend + Hooks watcher
# ═════════════════════════════════════════════════════════════════════════
@router.get("/audits-trend")
async def audits_trend_endpoint(
    limit: int = 30,
    since_utc: Optional[str] = None,
    audit_type: Optional[str] = None,
) -> JSONResponse:
    """ORDRE N°53-BIS-SUITE-ULTIME · Série temporelle des N derniers audits.

    API PUBLIQUE READ-ONLY · time series chronologique ascendante.
    Strictement dérivée des audits persistés (aucun recalcul).

    Champs par point de la série :
      · timestamp_utc, drift_max, drift_mean, score_global_fusion, sha256

    Filtres optionnels : `since_utc`, `audit_type`.
    Limit max : 500 (default 30).
    """
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        list_audits_trend,
    )
    try:
        payload = list_audits_trend(
            limit=limit,
            since_utc=since_utc,
            audit_type=audit_type,
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "AUDITS_TREND_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })

    return JSONResponse({
        "manifest_id": "AUDITS_TREND_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°53-BIS-SUITE-ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.post("/hooks-watcher-execute")
async def hooks_watcher_execute_endpoint(
    force: bool = False,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°53-BIS-SUITE-ULTIME · Watcher d'activation hooks externes.

    Détecte les transitions d'état des 6 sources externes et déclenche
    automatiquement un recompute_with_drift_audit doctrinal si une source
    passe de PATHS_ABSENT à AVAILABLE (ou si nouveaux fichiers détectés).

    Token Commandant requis.
    Args:
      force: True → recompute toujours (ignore watcher state).
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        watch_and_recompute_if_hooks_activated,
    )
    try:
        payload = watch_and_recompute_if_hooks_activated(force=force)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "HOOKS_WATCHER_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })

    return JSONResponse({
        "manifest_id": "HOOKS_WATCHER_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°53-BIS-SUITE-ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°54-Ω VAGUE 1 — INGESTION DOCUMENTAIRE INSTITUTIONNELLE
# ═════════════════════════════════════════════════════════════════════════
@router.post("/docs-ingest-execute")
async def docs_ingest_execute_endpoint(
    species_subset: Optional[str] = None,
    resolve_dois: bool = False,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 1 · Ingestion documentaire institutionnelle.

    Pipeline :
      1. Lecture .docx (paragraphes + tables)
      2. Extraction sections GOV / UNI / PR
      3. Extraction DOI (anti-générique strict)
      4. Normalisation tableaux maîtres
      5. Persistance registry_science/<espece>/ +
         registry_master_tables/<espece>_master_table.json
      6. Audit DOC_INGEST/SCIENCE_VAGUE_1 persisté

    AUCUN recalcul moteur. Token Commandant requis.

    Args:
      species_subset: CSV des espèces à ingérer (default = all 5).
      resolve_dois:   True → vérification HTTP 200 des DOI extraites.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.docs_ingest_omega import (
        ingest_all_species_vague_1, ESPECES_VAGUE_1,
    )
    subset = None
    if species_subset:
        subset = [
            s.strip().lower() for s in species_subset.split(",")
            if s.strip()]
        invalid = [s for s in subset if s not in ESPECES_VAGUE_1]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Espèces invalides : {invalid}. "
                    f"Valides : {ESPECES_VAGUE_1}"))
    try:
        payload = ingest_all_species_vague_1(
            species_subset=subset,
            resolve_dois=resolve_dois,
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "DOC_INGEST_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "DOC_INGEST_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-1",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/docs-registry")
async def docs_registry_endpoint(
    species: Optional[str] = None,
) -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 1 · Liste registry documentaire (PUBLIC read-only).

    Strictement dérivée des fichiers persistés. Aucune mutation.
    """
    from engines.v8_institutional.especes.docs_ingest_omega import (
        list_registry_science,
    )
    try:
        payload = list_registry_science(species=species)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "DOCS_REGISTRY_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "DOCS_REGISTRY_LIST_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-1",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/master-table/{species_code}")
async def master_table_endpoint(
    species_code: str,
) -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 1 · Tableau maître consolidé (PUBLIC read-only)."""
    from engines.v8_institutional.especes.docs_ingest_omega import (
        get_master_table,
    )
    try:
        payload = get_master_table(species_code)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "MASTER_TABLE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "MASTER_TABLE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-1",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°54-Ω VAGUE 2 — RECONSTITUTION INSTITUTIONNELLE BP135
# ═════════════════════════════════════════════════════════════════════════
from fastapi.responses import FileResponse  # noqa: E402


@router.post("/bp135-reconstitution-execute")
async def bp135_reconstitution_execute_endpoint(
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 2 · Reconstitution overlay BP135 depuis DOCX.

    Pipeline :
      1. Parse BIO_PROFILE_135.docx institutionnel
      2. Génère 675 entrées BCE-4X (135 paramètres × 5 espèces × 16 champs)
      3. Diff vs JSON existant (audit)
      4. Persiste : overlay + JSON 675 + DOCX consolidé + audit
        DOC_INGEST/BP135_INSTITUTIONAL

    AUCUN recalcul moteur. V30_LOCK INVIOLÉ. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.bp135_reconstitution_omega import (
        execute_reconstitution_pipeline,
    )
    try:
        payload = execute_reconstitution_pipeline(persist=persist)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "BP135_RECONSTITUTION_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "BP135_RECONSTITUTION_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-2",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/bp135-reconstitution-overlay")
async def bp135_reconstitution_overlay_endpoint() -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 2 · Overlay reconstitution BP135 (PUBLIC RO)."""
    from engines.v8_institutional.especes.bp135_reconstitution_omega import (
        OVERLAY_JSON_PATH,
    )
    if not OVERLAY_JSON_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="OVERLAY_NOT_GENERATED_YET")
    import json as _json
    payload = _json.loads(OVERLAY_JSON_PATH.read_text(encoding="utf-8"))
    return JSONResponse({
        "manifest_id": "BP135_RECONSTITUTION_OVERLAY_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-2",
        "horodatage_build": _build_horodatage(),
        "overlay_json_size": OVERLAY_JSON_PATH.stat().st_size,
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/bp135-reconstitution-document")
async def bp135_reconstitution_document_endpoint():
    """ORDRE N°54-Ω VAGUE 2 · Téléchargement document consolidé .docx
    institutionnel (PUBLIC).

    Format : application/vnd.openxmlformats-officedocument.
             wordprocessingml.document
    """
    from engines.v8_institutional.especes.bp135_reconstitution_omega import (
        CONSOLIDATED_DOCX_PATH,
    )
    if not CONSOLIDATED_DOCX_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="CONSOLIDATED_DOCX_NOT_GENERATED_YET")
    return FileResponse(
        path=str(CONSOLIDATED_DOCX_PATH),
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"),
        filename="BIO_PROFILE_OMEGA_135_CONSOLIDATED.docx",
    )


@router.get("/bp135-reconstitution-json")
async def bp135_reconstitution_json_endpoint():
    """ORDRE N°54-Ω VAGUE 2 · Téléchargement JSON 675 entrées (PUBLIC).

    Fichier candidat à validation Commandant pour devenir
    BIO_PROFILE_OMEGA_135.json officiel.
    """
    from engines.v8_institutional.especes.bp135_reconstitution_omega import (
        RECONSTITUTED_JSON_PATH,
    )
    if not RECONSTITUTED_JSON_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="RECONSTITUTED_JSON_NOT_GENERATED_YET")
    return FileResponse(
        path=str(RECONSTITUTED_JSON_PATH),
        media_type="application/json",
        filename="BIO_PROFILE_OMEGA_135_RECONSTITUTED.json",
    )



# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°54-Ω VAGUE 2-BIS — Registry officiel + Validation forensique
# ═════════════════════════════════════════════════════════════════════════
@router.post("/bp135-ingest-official")
async def bp135_ingest_official_endpoint(
    commandant_signature: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 2-BIS · Ingestion officielle BIO_PROFILE_OMEGA_135.

    Copie le JSON 675 reconstitué validé Commandant dans le registry
    officiel `registry_docs/bio_profile_omega_135/` avec SHA-256
    persisté + chain of custody + audit DOC_INGEST/BP135_OFFICIAL_VALIDATED.

    AUCUN recalcul moteur. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.bp135_official_registry_omega import (  # noqa: E501
        ingest_bp135_official,
    )
    try:
        payload = ingest_bp135_official(
            commandant_signature=commandant_signature)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "BP135_INGEST_OFFICIAL_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "BP135_INGEST_OFFICIAL_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/bp135-official-metadata")
async def bp135_official_metadata_endpoint() -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 2-BIS · Metadata officielle (PUBLIC RO)."""
    from engines.v8_institutional.especes.bp135_official_registry_omega import (  # noqa: E501
        get_official_metadata, get_validation_log,
    )
    try:
        metadata = get_official_metadata()
        log = get_validation_log()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return JSONResponse({
        "manifest_id": "BP135_OFFICIAL_METADATA_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "horodatage_build": _build_horodatage(),
        "metadata": metadata,
        "validation_log": log,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/bp135-official-json")
async def bp135_official_json_endpoint():
    """ORDRE N°54-Ω VAGUE 2-BIS · Téléchargement JSON officiel (PUBLIC).

    Fichier : `BIO_PROFILE_OMEGA_135_OFFICIAL.json` (675 entrées validées).
    """
    from engines.v8_institutional.especes.bp135_official_registry_omega import (  # noqa: E501
        BP135_OFFICIAL_JSON_PATH,
    )
    if not BP135_OFFICIAL_JSON_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="OFFICIAL_JSON_NOT_INGESTED_YET")
    return FileResponse(
        path=str(BP135_OFFICIAL_JSON_PATH),
        media_type="application/json",
        filename="BIO_PROFILE_OMEGA_135_OFFICIAL.json",
    )


@router.post("/bp135-validate-against-official")
async def bp135_validate_against_official_endpoint(
    request: Request,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ORDRE N°54-Ω VAGUE 2-BIS · Validation forensique cellule-par-cellule.

    Reçoit en body JSON un candidat (avec `entries` list) et compare
    cellule-par-cellule avec le BIO_PROFILE_OMEGA_135_OFFICIAL.json.

    Retourne deltas (typical/min/max) par paramètre × espèce + verdict
    + audit BP135_VALIDATION persisté.

    AUCUN recalcul moteur. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    try:
        candidate = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"INVALID_JSON_BODY::{str(e)[:200]}")
    if not isinstance(candidate, dict):
        raise HTTPException(
            status_code=400,
            detail="JSON body must be an object with 'entries' list.")

    from engines.v8_institutional.especes.bp135_official_registry_omega import (  # noqa: E501
        validate_against_official,
    )
    try:
        payload = validate_against_official(candidate)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "BP135_VALIDATION_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "BP135_VALIDATE_AGAINST_OFFICIAL_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# ACTIVATION_PIPELINE_NOAA_TERRITOIRE — WOD23 (LOCAL) + CFSv2 (OPeNDAP)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/noaa-pipeline-activate")
async def noaa_pipeline_activate_endpoint(
    sample_yyyymm: str = "201101",
    sample_variable: str = "tavg",
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ACTIVATION_PIPELINE_NOAA_TERRITOIRE · Configuration + probes réels.

    Activation doctrinale du pipeline :
      · WOD23 (LOCAL) : probe paths réels (anti-générique)
      · CFSv2 (OPeNDAP) : génération URLs mensuelles + probe HEAD/DDS
        avec status HTTP réel
      · Audit NOAA_PIPELINE/ACTIVATION persisté
      · AUCUN recalcul moteur (V30_LOCK + DRIFT_ZERO)

    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_noaa_pipeline,
    )
    try:
        payload = activate_noaa_pipeline(
            sample_yyyymm=sample_yyyymm,
            sample_variable=sample_variable,
            persist=persist,
        )
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "NOAA_PIPELINE_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NOAA_PIPELINE_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/noaa-pipeline-status")
async def noaa_pipeline_status_endpoint() -> JSONResponse:
    """ACTIVATION_PIPELINE_NOAA_TERRITOIRE · État pipeline (PUBLIC RO)."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_pipeline_status,
    )
    payload = get_pipeline_status()
    return JSONResponse({
        "manifest_id": "NOAA_PIPELINE_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/noaa-cfsv2-urls")
async def noaa_cfsv2_urls_endpoint(
    start_yyyymm: Optional[str] = None,
    end_yyyymm: Optional[str] = None,
    variable: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
) -> JSONResponse:
    """ACTIVATION_PIPELINE_NOAA_TERRITOIRE · URLs CFSv2 mensuelles paginées
    (PUBLIC RO).

    Params :
      · start_yyyymm: défaut 2011-01
      · end_yyyymm:   défaut mois courant
      · variable:     filtre par variable (ex: tavg, sst...)
      · page/page_size: pagination
    """
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        generate_cfsv2_urls, CFSV2_CONFIG,
    )
    vars_used = (
        [variable] if variable else CFSV2_CONFIG["variables"])
    try:
        full = generate_cfsv2_urls(
            start_yyyymm=start_yyyymm,
            end_yyyymm=end_yyyymm,
            variables=vars_used,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"INVALID_DATE_RANGE::{str(e)[:200]}")
    page = max(1, int(page))
    page_size = max(1, min(1000, int(page_size)))
    start = (page - 1) * page_size
    paged = full["urls"][start:start + page_size]
    return JSONResponse({
        "manifest_id": "NOAA_CFSV2_URLS_LIST_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "horodatage_build": _build_horodatage(),
        "page": page,
        "page_size": page_size,
        "total": full["n_urls_total"],
        "n_returned": len(paged),
        "period_start": full["period_start"],
        "period_end": full["period_end"],
        "variables_filter": vars_used,
        "urls": paged,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# ACTIVATION_HOOK_NOAA_WOD23 — Hook B2 dédié (FUSION ADD-ONLY)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/noaa-wod23-activate")
async def noaa_wod23_activate_endpoint(
    persist: bool = True,
    max_keys: int = 1000,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ACTIVATION_HOOK_NOAA_WOD23 · Active officiellement le hook WOD23.

    Workflow doctrinal :
      1. Probe RÉEL Backblaze B2 avec credentials B2_WOD23_* dédiées
      2. Classification anti-générique des fichiers WOD23 (signatures
         APB/CTD/DRB/GLD/MBT/MRB/OSD/PFL/SUR/UOR/XBT)
      3. Manifest signé SHA-256 pour traçabilité longitudinale
      4. Persistance overlay JSON + audit forensique
         NOAA_PIPELINE/WOD23_HOOK_ACTIVATION
      5. AUCUN recalcul moteur (V30_LOCK + DRIFT_ZERO maintenus)

    Token Commandant requis.
    Anti-générique strict : status RÉEL retourné, zéro fabrication.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_wod23_hook,
    )
    try:
        payload = activate_wod23_hook(
            persist=persist, max_keys=max_keys)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "WOD23_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "WOD23_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_HOOK_NOAA_WOD23",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/noaa-wod23-hook-status")
async def noaa_wod23_hook_status_endpoint() -> JSONResponse:
    """ACTIVATION_HOOK_NOAA_WOD23 · État hook WOD23 (PUBLIC RO)."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_wod23_hook_status,
    )
    payload = get_wod23_hook_status()
    return JSONResponse({
        "manifest_id": "WOD23_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_HOOK_NOAA_WOD23",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.post("/noaa-wod23-probe-only")
async def noaa_wod23_probe_only_endpoint(
    max_keys: int = 100,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ACTIVATION_HOOK_NOAA_WOD23 · Probe seul (sans persistance).

    Probe RÉEL B2_WOD23_* sans persistance d'overlay/audit. Utile pour
    diagnostiquer sans muter le registre. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        probe_wod23_b2_dedicated,
    )
    try:
        payload = probe_wod23_b2_dedicated(
            max_keys=max_keys, classify=True)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "WOD23_PROBE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "WOD23_PROBE_ONLY_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_HOOK_NOAA_WOD23",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# PIPELINE_GUARDRAILS_RESTORE — Endpoints dédiés (FUSION ADD-ONLY)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/pipeline-guardrails-restore")
async def pipeline_guardrails_restore_endpoint(
    activated_by: str = "COMMANDANT_STEVE_MAX",
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """PIPELINE_GUARDRAILS_RESTORE · Active la directive doctrinale.

    Workflow doctrinal :
      1. Persiste l'état des garde-fous (FUSION ADD-ONLY history)
      2. Calcule SHA-256 d'activation (traçabilité longitudinale)
      3. Enregistre événement forensique CONFIG_CHANGES/GUARDRAILS_ACTIVATED
      4. Persiste audit PIPELINE_GUARDRAILS/RESTORE_AND_ENFORCE
      5. AUCUN recalcul moteur (V30_LOCK + DRIFT_ZERO maintenus)

    Token Commandant requis.
    Anti-générique strict : aucune fabrication. État RÉEL persisté.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        restore_and_enforce_guardrails,
    )
    try:
        payload = restore_and_enforce_guardrails(
            persist=persist, activated_by=activated_by)
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "PIPELINE_GUARDRAILS_RESTORE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "PIPELINE_GUARDRAILS_RESTORE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "PIPELINE_GUARDRAILS_RESTORE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/pipeline-guardrails-status")
async def pipeline_guardrails_status_endpoint() -> JSONResponse:
    """PIPELINE_GUARDRAILS_RESTORE · État actuel (PUBLIC RO)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        get_guardrails_state,
    )
    payload = get_guardrails_state()
    return JSONResponse({
        "manifest_id": "PIPELINE_GUARDRAILS_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "PIPELINE_GUARDRAILS_RESTORE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/pipeline-guardrails-forensic-log")
async def pipeline_guardrails_forensic_log_endpoint(
    scope: Optional[str] = None,
    limit: int = 100,
) -> JSONResponse:
    """PIPELINE_GUARDRAILS_RESTORE · Log forensique JSONL (PUBLIC RO).

    Filtres optionnels :
      · scope ∈ {B2_CREDENTIALS, ENDPOINT_PROBES, HOOK_ACTIVATIONS,
                  CONFIG_CHANGES}
      · limit (default 100, max ordre chronologique)
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        list_forensic_events, VALID_FORENSIC_SCOPES,
    )
    if scope and scope not in VALID_FORENSIC_SCOPES:
        raise HTTPException(
            status_code=400,
            detail=f"INVALID_SCOPE::{scope} :: valides="
                   f"{sorted(VALID_FORENSIC_SCOPES)}")
    try:
        payload = list_forensic_events(
            scope=scope, limit=max(1, min(1000, int(limit))))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"FORENSIC_LIST_FAILED::{str(e)[:200]}")
    return JSONResponse({
        "manifest_id": "PIPELINE_GUARDRAILS_FORENSIC_LIST_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "PIPELINE_GUARDRAILS_RESTORE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.post("/noaa-cfsv2-candidate-probe")
async def noaa_cfsv2_candidate_probe_endpoint(
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ACTIVATION_PIPELINE_NOAA_TERRITOIRE · Probe AWS CFSv2 candidates.

    Probe RÉEL HEAD HTTPS sur les 3 buckets AWS publics documentés :
      · noaa-cfsv2-bdp-pds (Big Data Program convention)
      · noaa-cfs-pds       (CFSv1 legacy)
      · noaa-gfs-bdp-pds   (GFS apparenté)

    Pré-requis doctrinal : PIPELINE_GUARDRAILS_RESTORE doit être ENFORCED
    (bloque sinon avec 412 Precondition Failed).

    Anti-générique strict : status HTTP RÉEL retourné.
    Forensic logging ENDPOINT_PROBES pour chaque candidat.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
        GuardrailsNotEnforcedError,
    )
    try:
        require_guardrails_enforced("noaa_cfsv2_candidate_probe")
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))

    import urllib.request
    import urllib.error
    import time as _time

    candidates = [
        {
            "bucket": "noaa-cfsv2-bdp-pds",
            "label": "BDP_CFSV2_BIG_DATA_PROGRAM",
            "test_url": "https://noaa-cfsv2-bdp-pds.s3.amazonaws.com/",
        },
        {
            "bucket": "noaa-cfs-pds",
            "label": "LEGACY_CFSV1",
            "test_url": "https://noaa-cfs-pds.s3.amazonaws.com/",
        },
        {
            "bucket": "noaa-gfs-bdp-pds",
            "label": "GFS_BIG_DATA_PROGRAM_RELATED",
            "test_url": "https://noaa-gfs-bdp-pds.s3.amazonaws.com/",
        },
    ]

    results = []
    for cand in candidates:
        bucket = cand["bucket"]
        url = cand["test_url"] + "?list-type=2&max-keys=3"
        rec: Dict[str, Any] = {
            "bucket": bucket,
            "label": cand["label"],
            "url": url,
            "http_status": None,
            "elapsed_ms": None,
            "exists": False,
            "body_preview_first_500b": None,
            "reason": None,
        }
        t0 = _time.time()
        try:
            req = urllib.request.Request(
                url, method="GET",
                headers={
                    "User-Agent": "BCE-4X-NOAA-CFSV2-CANDIDATE-PROBE/1.0",
                })
            with urllib.request.urlopen(req, timeout=15) as resp:
                rec["http_status"] = resp.status
                preview = resp.read(2048)
                rec["body_preview_first_500b"] = preview[:500].decode(
                    "utf-8", errors="replace")
                # Bucket existe si HTTP 200 et XML ListBucket
                rec["exists"] = (
                    resp.status == 200
                    and ("ListBucketResult" in
                         rec["body_preview_first_500b"]
                         or "<Contents" in
                         rec["body_preview_first_500b"]))
        except urllib.error.HTTPError as e:
            rec["http_status"] = e.code
            rec["reason"] = f"http_error_{e.code}"
            try:
                body = e.read(2048)
                rec["body_preview_first_500b"] = body[:500].decode(
                    "utf-8", errors="replace")
                if "NoSuchBucket" in (
                        rec["body_preview_first_500b"] or ""):
                    rec["reason"] = "NoSuchBucket"
            except Exception:
                pass
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            rec["reason"] = f"network_error::{str(e)[:120]}"
        rec["elapsed_ms"] = round((_time.time() - t0) * 1000, 1)
        results.append(rec)

        # Forensic log ENDPOINT_PROBES
        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event="CFSV2_CANDIDATE_PROBE",
            details={
                "bucket": bucket,
                "label": cand["label"],
                "http_status": rec["http_status"],
                "exists": rec["exists"],
                "reason": rec["reason"],
                "elapsed_ms": rec["elapsed_ms"],
            },
            persist=True,
        )

    n_existing = sum(1 for r in results if r["exists"])
    summary = {
        "n_candidates": len(candidates),
        "n_buckets_existing": n_existing,
        "candidates_existing": [
            r["bucket"] for r in results if r["exists"]],
        "candidates_missing": [
            r["bucket"] for r in results if not r["exists"]],
    }
    return JSONResponse({
        "manifest_id": "NOAA_CFSV2_CANDIDATE_PROBE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "horodatage_build": _build_horodatage(),
        "summary": summary,
        "results": results,
        "guardrails_enforced": True,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# NOAA_CFSV2_P0_DECISION — HEAD_ONLY strict + pivot CANDIDATE_LIST_ONLY
# ═════════════════════════════════════════════════════════════════════════
@router.post("/noaa-cfsv2-verification-p0")
async def noaa_cfsv2_verification_p0_endpoint(
    bucket: str = "noaa-cfs-pds",
    path: str = (
        "cfs.20240101/01/6hrly_grib_01/cfs.tavg.01.2024010100.grb2"),
    expect_format: str = "GRIB2_OR_NETCDF",
    require_no_redirect: bool = True,
    require_http_200: bool = True,
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NOAA_CFSV2_P0_DECISION · Vérification HEAD_ONLY stricte CFSv2.

    Workflow doctrinal :
      1. Vérifier guardrails ENFORCED (412 Precondition Failed sinon)
      2. HEAD HTTP RÉEL sans follow_redirects (anti-générique)
      3. Critères stricts Commandant : HTTP 200 + pas de redirect +
         content-type binaire + content-length > 0
      4. Si VALID → suggestion activation (await Commandant confirm)
      5. Si INVALID → liste pivot CFSV2_PIVOT_CANDIDATE_LIST (mode
         CANDIDATE_LIST_ONLY, require_commandant_confirm=True,
         autonomy=LIMITED)
      6. Forensic log ENDPOINT_PROBES + audit
         NOAA_PIPELINE/CFSV2_VERIFICATION_P0
      7. AUCUN recalcul moteur (V30_LOCK + DRIFT_ZERO)

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_p0_head_only,
    )
    try:
        payload = verify_cfsv2_p0_head_only(
            bucket=bucket, path=path,
            expect_format=expect_format,
            require_no_redirect=require_no_redirect,
            require_http_200=require_http_200,
            persist=persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "NOAA_CFSV2_VERIFICATION_P0_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NOAA_CFSV2_VERIFICATION_P0_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "NOAA_CFSV2_P0_DECISION",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/noaa-cfsv2-pivot-candidates")
async def noaa_cfsv2_pivot_candidates_endpoint() -> JSONResponse:
    """NOAA_CFSV2_P0_DECISION · Liste pivot CFSv2 (PUBLIC RO).

    Mode CANDIDATE_LIST_ONLY · aucun probe automatique ·
    require_commandant_confirm=True.
    """
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        list_cfsv2_pivot_candidates,
    )
    payload = list_cfsv2_pivot_candidates()
    return JSONResponse({
        "manifest_id": "NOAA_CFSV2_PIVOT_LIST_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "NOAA_CFSV2_P0_DECISION",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# NOAA_CFSV2_P0_PIVOT_VERIFY — endpoint pivot HEAD_ONLY (NCEI/Copernicus)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/noaa-cfsv2-pivot-verify")
async def noaa_cfsv2_pivot_verify_endpoint(
    endpoint: str,
    provider: str = "NCEI_THREDDS_CFSR_MONTHLY",
    expect_format: str = "GRIB2_OR_NETCDF",
    expect_opendap: bool = True,
    require_no_redirect: bool = True,
    require_http_200: bool = True,
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NOAA_CFSV2_P0_PIVOT_VERIFY · HEAD_ONLY strict + DDS si OPeNDAP.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. HEAD HTTP RÉEL sur endpoint absolu sans follow_redirects
      3. Si expect_opendap : probe DDS complémentaire (.dds, GET 4KB)
      4. Critères stricts OPeNDAP-aware (HEAD ou DDS valide)
      5. Forensic log ENDPOINT_PROBES + audit doctrinal persisté
      6. AUCUN recalcul moteur (V30_LOCK + DRIFT_ZERO)

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        verify_cfsv2_pivot_head_only,
    )
    try:
        payload = verify_cfsv2_pivot_head_only(
            endpoint=endpoint,
            provider=provider,
            expect_format=expect_format,
            expect_opendap=expect_opendap,
            require_no_redirect=require_no_redirect,
            require_http_200=require_http_200,
            persist=persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "NOAA_CFSV2_PIVOT_VERIFY_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NOAA_CFSV2_PIVOT_VERIFY_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "NOAA_CFSV2_P0_PIVOT_VERIFY",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY — NCEI THREDDS browse XML strict
# ═════════════════════════════════════════════════════════════════════════
@router.post("/noaa-cfsv2-catalogue-cartography")
async def noaa_cfsv2_catalogue_cartography_endpoint(
    root_catalog: str = (
        "https://www.ncei.noaa.gov/thredds/catalog/"
        "cfsr/mon/pgbh/catalog.xml"),
    max_depth: int = 2,
    max_datasets: int = 128,
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY · NCEI THREDDS browse XML.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. GET RÉCURSIF strict sur catalog.xml NCEI (BFS limité)
      3. Contraintes : GET only · application/xml ou text/xml only ·
         forbid_binary_probe · forbid_follow_redirects · max_depth=2 ·
         max_datasets=128
      4. Forensic log ENDPOINT_PROBES par catalogue visité
      5. Persistance overlay + audit doctrinal
      6. AUCUN recalcul moteur · AUCUN binaire téléchargé

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    # Bornes de sécurité doctrinales
    md = max(1, min(2, int(max_depth)))
    mds = max(1, min(128, int(max_datasets)))
    try:
        payload = cartograph_ncei_catalogue(
            root_catalog_url=root_catalog,
            max_depth=md,
            max_datasets=mds,
            persist=persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "NOAA_CFSV2_CATALOGUE_CARTOGRAPHY_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": (
            "NOAA_CFSV2_CATALOGUE_CARTOGRAPHY_EXECUTE_Ω"),
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# COPERNICUS_P0_CATALOGUE_CARTOGRAPHY — Copernicus Marine THREDDS browse
# ═════════════════════════════════════════════════════════════════════════
@router.post("/copernicus-catalogue-cartography")
async def copernicus_catalogue_cartography_endpoint(
    root_catalog: str = (
        "https://my.cmems-du.eu/thredds/catalog/catalog.xml"),
    max_depth: int = 1,
    max_datasets: int = 128,
    persist: bool = True,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """COPERNICUS_P0_CATALOGUE_CARTOGRAPHY · Copernicus Marine THREDDS browse.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. GET RÉCURSIF strict sur catalog.xml Copernicus (BFS limité)
      3. Contraintes Commandant : GET only · application/xml ou text/xml
         only · forbid_binary_probe · forbid_follow_redirects ·
         max_depth=1 (Copernicus default) · max_datasets=128
      4. Forensic log ENDPOINT_PROBES/COPERNICUS_CATALOGUE_CARTOGRAPHY
      5. Persistance overlay + audit doctrinal
      6. AUCUN recalcul moteur · AUCUN binaire téléchargé

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        cartograph_ncei_catalogue,
    )
    md = max(1, min(2, int(max_depth)))
    mds = max(1, min(128, int(max_datasets)))
    try:
        payload = cartograph_ncei_catalogue(
            root_catalog_url=root_catalog,
            max_depth=md,
            max_datasets=mds,
            persist=persist,
            provider="COPERNICUS_MARINE",
            forensic_event="COPERNICUS_CATALOGUE_CARTOGRAPHY",
            ordre="COPERNICUS_P0_CATALOGUE_CARTOGRAPHY",
            base_dodsc_url=(
                "https://my.cmems-du.eu/thredds/dodsC/"),
            base_fileserver_url=(
                "https://my.cmems-du.eu/thredds/fileServer/"),
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "COPERNICUS_CATALOGUE_CARTOGRAPHY_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": (
            "COPERNICUS_CATALOGUE_CARTOGRAPHY_EXECUTE_Ω"),
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "COPERNICUS_P0_CATALOGUE_CARTOGRAPHY",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# COPERNICUS_API_P0_VALIDATE — REST API HEAD_ONLY + détection placeholder
# ═════════════════════════════════════════════════════════════════════════
class CopernicusApiValidateBody(BaseModel):
    endpoint: str = (
        "https://data.marine.copernicus.eu/api/v1/products")
    api_key: Optional[str] = None
    require_http_200: bool = True
    require_no_redirect: bool = True
    expect_content_type: str = "application/json"
    persist: bool = True


@router.post("/copernicus-api-validate")
async def copernicus_api_validate_endpoint(
    body: CopernicusApiValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """COPERNICUS_API_P0_VALIDATE · REST API HEAD_ONLY + placeholder check.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Détection ANTI-GÉNÉRIQUE STRICT du placeholder token
         (VOTRE_TOKEN_ICI, YOUR_TOKEN_HERE, etc.) → si détecté, le token
         n'est JAMAIS envoyé en Bearer ; verdict explicite REJECTED
      3. HEAD HTTP avec Bearer (token masqué dans logs/persistence)
      4. Critères stricts : HTTP 200 + content-type=application/json +
         pas de redirect
      5. Forensic log ENDPOINT_PROBES/COPERNICUS_API_VALIDATE
      6. Persistance overlay + audit doctrinal
      7. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Body POST JSON requis (contient api_key) — token jamais en query string.
    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_copernicus_api_endpoint,
    )
    try:
        payload = validate_copernicus_api_endpoint(
            endpoint=body.endpoint,
            api_key=body.api_key,
            require_http_200=body.require_http_200,
            require_no_redirect=body.require_no_redirect,
            expect_content_type=body.expect_content_type,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "COPERNICUS_API_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "COPERNICUS_API_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "COPERNICUS_API_P0_VALIDATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })

