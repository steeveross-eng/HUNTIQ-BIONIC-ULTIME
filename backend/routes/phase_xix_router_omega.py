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



# ═════════════════════════════════════════════════════════════════════════
# OPENWEATHERMAP_P0_VALIDATE — GET_JSON + double placeholder check
# ═════════════════════════════════════════════════════════════════════════
class OpenWeatherMapValidateBody(BaseModel):
    endpoint: str = (
        "https://api.openweathermap.org/data/2.5/weather")
    credentials_api_key: Optional[str] = None
    query_params: Optional[Dict[str, str]] = None
    require_http_200: bool = True
    require_no_redirect: bool = True
    expect_content_type: str = "application/json"
    persist: bool = True


@router.post("/openweathermap-validate")
async def openweathermap_validate_endpoint(
    body: OpenWeatherMapValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENWEATHERMAP_P0_VALIDATE · GET_JSON + double placeholder check.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Détection STRICTE placeholder DOUBLE niveau :
         · credentials_api_key (Bearer header potentiel)
         · query_params['appid'] (auth canonique OpenWeatherMap)
      3. Sélection du token actif anti-générique strict (priorité query
         appid si réel, sinon Bearer header, sinon REJECTED).
      4. GET HTTP RÉEL avec NoRedirectHandler + parsing JSON
      5. Vérification signature OWM canonique (weather + main + name)
      6. Forensic log ENDPOINT_PROBES/OPENWEATHERMAP_VALIDATE
      7. Persistance overlay + audit doctrinal
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Body POST JSON requis (tokens jamais en query string GET du router).
    Token Commandant requis. Anti-générique strict + anti-leakage.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_endpoint,
    )
    try:
        payload = validate_openweathermap_endpoint(
            endpoint=body.endpoint,
            credentials_api_key=body.credentials_api_key,
            query_params=body.query_params,
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
                "reason": "OPENWEATHERMAP_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OPENWEATHERMAP_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "OPENWEATHERMAP_P0_VALIDATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# OPENWEATHERMAP_HOOK_ACTIVATE — activation officielle V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
class OpenWeatherMapHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "owm_hook_activated"
    persist: bool = True


@router.post("/openweathermap-hook-activate")
async def openweathermap_hook_activate_endpoint(
    body: OpenWeatherMapHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENWEATHERMAP_HOOK_ACTIVATE · activation officielle FUSION ADD-ONLY.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Vérification ANTI-GÉNÉRIQUE STRICTE : manifest_sha256 doit
         exister dans OPENWEATHERMAP_VALIDATION_PATH avec valid=True +
         verdict=OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED
      3. Construction manifest activation signé SHA-256
      4. Forensic log HOOK_ACTIVATIONS/OPENWEATHERMAP_HOOK_ACTIVATE
      5. Persistance overlay history (V30_LOCK FUSION ADD-ONLY)
      6. Audit doctrinal NOAA_PIPELINE/OPENWEATHERMAP_HOOK_ACTIVATE
      7. AUCUN recalcul moteur ICI (drift audit séparé via
         /recompute-with-drift-audit)

    Token Commandant requis. Anti-générique strict : refus d'activer
    un manifest fabriqué.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_openweathermap_hook,
    )
    try:
        payload = activate_openweathermap_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "OPENWEATHERMAP_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OPENWEATHERMAP_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/openweathermap-hook-status")
async def openweathermap_hook_status_endpoint() -> JSONResponse:
    """OPENWEATHERMAP_HOOK_ACTIVATE · état actuel (PUBLIC RO)."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_openweathermap_hook_status,
    )
    payload = get_openweathermap_hook_status()
    return JSONResponse({
        "manifest_id": "OPENWEATHERMAP_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# OPENWEATHERMAP_P0_PIVOT_TERRITOIRE — current + forecast + 7 variables
# ═════════════════════════════════════════════════════════════════════════
class OpenWeatherMapZonePivotBody(BaseModel):
    endpoint_current: str = (
        "https://api.openweathermap.org/data/2.5/weather")
    endpoint_forecast: str = (
        "https://api.openweathermap.org/data/2.5/forecast")
    credentials_api_key: Optional[str] = None
    query_params: Optional[Dict[str, Any]] = None
    variables_requested: Optional[Dict[str, bool]] = None
    forensic_event: str = "OPENWEATHERMAP_PIVOT_TERRITOIRE"
    require_http_200: bool = True
    require_no_redirect: bool = True
    expect_content_type: str = "application/json"
    persist: bool = True


@router.post("/openweathermap-zone-pivot")
async def openweathermap_zone_pivot_endpoint(
    body: OpenWeatherMapZonePivotBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENWEATHERMAP_P0_PIVOT_TERRITOIRE · double probe enrichi.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Détection placeholder DOUBLE niveau + auth priority
      3. Probe 1 : current weather (lat/lon, units)
      4. Probe 2 : forecast (mêmes coords)
      5. Extraction stricte des variables OWM RÉELLEMENT présentes
         (anti-générique : variables_missing trace les absentes)
      6. Forensic log ENDPOINT_PROBES/{forensic_event}
      7. Persistance overlay + audit doctrinal
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Body POST JSON requis. Token Commandant requis.
    Anti-générique strict + anti-leakage.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        validate_openweathermap_zone_pivot,
    )
    try:
        payload = validate_openweathermap_zone_pivot(
            endpoint_current=body.endpoint_current,
            endpoint_forecast=body.endpoint_forecast,
            credentials_api_key=body.credentials_api_key,
            query_params=body.query_params,
            variables_requested=body.variables_requested,
            require_http_200=body.require_http_200,
            require_no_redirect=body.require_no_redirect,
            expect_content_type=body.expect_content_type,
            forensic_event=body.forensic_event,
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
                "reason": "OWM_ZONE_PIVOT_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OWM_ZONE_PIVOT_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P0_OPENWEATHERMAP_PIVOT_TERRITOIRE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# OPENWEATHERMAP_BATCH_PROBE_BP135 — batch 5 espèces × 2 endpoints
# ═════════════════════════════════════════════════════════════════════════
class OpenWeatherMapBatchBp135Body(BaseModel):
    endpoint_current: str = (
        "https://api.openweathermap.org/data/2.5/weather")
    endpoint_forecast: str = (
        "https://api.openweathermap.org/data/2.5/forecast")
    credentials_api_key: Optional[str] = None
    species_coordinates: Dict[str, Dict[str, float]]
    units: str = "metric"
    forensic_event: str = "OPENWEATHERMAP_BATCH_BP135"
    persist: bool = True


@router.post("/openweathermap-batch-probe-bp135")
async def openweathermap_batch_probe_bp135_endpoint(
    body: OpenWeatherMapBatchBp135Body,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENWEATHERMAP_BATCH_PROBE_BP135 · batch 5 espèces × 2 endpoints.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Validation lat/lon par espèce
      3. Pour chaque espèce : double probe current + forecast +
         extraction 7 variables (réutilise validate_openweathermap_zone_pivot)
      4. Pause inter-calls anti-rate-limit (200ms × 5 = 1s minimum)
      5. Agrégation statistique (min/max/mean) sur espèces valides
      6. Forensic log ENDPOINT_PROBES/{forensic_event} par sous-probe
      7. Persistance overlay batch + audit doctrinal
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Body POST JSON requis. Token Commandant requis.
    Anti-générique strict + anti-leakage. Quota OWM 60/min respecté.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        batch_probe_owm_bp135,
    )
    try:
        payload = batch_probe_owm_bp135(
            endpoint_current=body.endpoint_current,
            endpoint_forecast=body.endpoint_forecast,
            credentials_api_key=body.credentials_api_key,
            species_coordinates=body.species_coordinates,
            units=body.units,
            forensic_event=body.forensic_event,
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
                "reason": "OWM_BATCH_BP135_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OWM_BATCH_BP135_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_OPENWEATHERMAP_BATCH_PROBE_BP135",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE — activation officielle
# ═════════════════════════════════════════════════════════════════════════
class OpenWeatherMapBatchBp135HookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "owm_batch_bp135_activated"
    persist: bool = True


@router.post("/openweathermap-batch-bp135-hook-activate")
async def openweathermap_batch_bp135_hook_activate_endpoint(
    body: OpenWeatherMapBatchBp135HookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE · activation officielle.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Vérification ANTI-GÉNÉRIQUE STRICTE : manifest_sha256 doit
         exister dans OPENWEATHERMAP_BATCH_BP135_PATH avec n_valid >= 1
      3. Construction manifest activation signé SHA-256 + sommaire
         des espèces validées + stats inherited
      4. Forensic log HOOK_ACTIVATIONS/OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE
      5. Persistance overlay history (V30_LOCK FUSION ADD-ONLY)
      6. Audit doctrinal NOAA_PIPELINE/OWM_BATCH_BP135_HOOK_ACTIVATE
      7. AUCUN recalcul moteur ICI (drift audit séparé)

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        activate_openweathermap_batch_bp135_hook,
    )
    try:
        payload = activate_openweathermap_batch_bp135_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "OWM_BATCH_BP135_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "OWM_BATCH_BP135_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/openweathermap-batch-bp135-hook-status")
async def openweathermap_batch_bp135_hook_status_endpoint() -> JSONResponse:
    """État actuel du hook BATCH BP135 (PUBLIC RO)."""
    from engines.v8_institutional.especes.noaa_pipeline_omega import (
        get_openweathermap_batch_bp135_hook_status,
    )
    payload = get_openweathermap_batch_bp135_hook_status()
    return JSONResponse({
        "manifest_id":
            "OWM_BATCH_BP135_HOOK_STATUS_GET_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# BP135_THERMAL_STRESS_INDEX_ACTIVATE — TSI 0-100 par espèce
# ═════════════════════════════════════════════════════════════════════════
class Bp135ThermalStressActivateBody(BaseModel):
    reason: str = "bp135_thermal_stress_index_activated"
    persist: bool = True
    enable_drift_audit: bool = True


@router.post("/bp135-thermal-stress-index-activate")
async def bp135_thermal_stress_index_activate_endpoint(
    body: Bp135ThermalStressActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """BP135_THERMAL_STRESS_INDEX_ACTIVATE · calcul TSI 0-100 par espèce.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Lecture du dernier hook OWM_BATCH_BP135 ACTIVATED_OPERATIONAL
      3. Lookup BP135_THERMAL_LIMITS_V1 (sources peer-reviewed)
      4. Calcul TSI = base TCZ + modulateurs documentés (humidity, wind,
         précipitation), capped 0-100
      5. Classification LOW/MODERATE/HIGH/CRITICAL selon TSI
      6. Manifest signé SHA-256 + persistance overlay + audit
      7. Drift audit optionnel (reason=bp135_thermal_stress_index_activated)

    Anti-générique strict : refuse si aucun hook OWM batch actif.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        compute_bp135_thermal_stress_index,
    )
    try:
        payload = compute_bp135_thermal_stress_index(
            reason=body.reason,
            persist=body.persist,
            enable_drift_audit=body.enable_drift_audit,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason":
                    "BP135_THERMAL_STRESS_INDEX_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback":
                    traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "BP135_THERMAL_STRESS_INDEX_ACTIVATE_EXECUTE_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "P1_BP135_THERMAL_STRESS_INDEX_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/bp135-thermal-stress-index-status")
async def bp135_thermal_stress_index_status_endpoint() -> JSONResponse:
    """État actuel du module TSI (PUBLIC RO)."""
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        get_bp135_thermal_stress_index_status,
    )
    payload = get_bp135_thermal_stress_index_status()
    return JSONResponse({
        "manifest_id":
            "BP135_THERMAL_STRESS_INDEX_STATUS_GET_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "P1_BP135_THERMAL_STRESS_INDEX_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/bp135-thermal-limits-manifest")
async def bp135_thermal_limits_manifest_endpoint() -> JSONResponse:
    """Lit BP135_THERMAL_LIMITS_V1 manifest (PUBLIC RO).

    Retourne les seuils thermiques documentés avec sources scientifiques.
    """
    from engines.v8_institutional.especes.bp135_thermal_stress_omega import (
        persist_thermal_limits_manifest_if_missing,
        BP135_THERMAL_LIMITS_V1,
    )
    payload = persist_thermal_limits_manifest_if_missing()
    return JSONResponse({
        "manifest_id": "BP135_THERMAL_LIMITS_V1_GET_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "P1_BP135_THERMAL_STRESS_INDEX_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "n_species": len(BP135_THERMAL_LIMITS_V1),
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# NASA_NDVI_P0_VALIDATE_Ω_ULTIME + NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME
# Anti-générique strict : MOD13Q1 contient NDVI/EVI/VI_QUALITY uniquement.
# LAI/FPAR/GPP demandés par directive Commandant → tracés
# BAND_DEFERRED_OTHER_PRODUCT (jamais fabriqués).
# ═════════════════════════════════════════════════════════════════════════
class NasaNdviValidateBody(BaseModel):
    species_coordinates: Dict[str, Dict[str, float]]
    bands_requested_logical: Optional[list] = None
    base_endpoint: str = "https://modis.ornl.gov/rst/api/v1"
    days_lookback: int = 365
    max_points: int = 46
    persist: bool = True


@router.post("/nasa-ndvi-validate")
async def nasa_ndvi_validate_endpoint(
    body: NasaNdviValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NASA_NDVI_P0_VALIDATE_Ω_ULTIME · validation multi-espèces × bandes.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Validation coordonnées espèces (lat/lon)
      3. Probe RÉEL NASA ORNL MODIS Web Service (no creds required)
      4. ANTI-GÉNÉRIQUE STRICT :
         · MOD13Q1 → NDVI/EVI/VI_QUALITY probés
         · LAI/FPAR (MOD15A2H) → DEFERRED, jamais fabriqués
         · GPP (MOD17A2H) → DEFERRED, jamais fabriqué
      5. Calcul stats anti-génériques (rejet nodata, pas d'imputation)
      6. Forensic log ENDPOINT_PROBES/NASA_NDVI_P0_VALIDATE_Ω_ULTIME
      7. Persistance overlay + audit doctrinal NOAA_PIPELINE
      8. AUCUN habitat_output calculé ICI · V30_LOCK + DRIFT_ZERO

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        validate_nasa_ndvi_per_species,
    )
    try:
        payload = validate_nasa_ndvi_per_species(
            species_coordinates=body.species_coordinates,
            bands_requested_logical=body.bands_requested_logical,
            base_endpoint=body.base_endpoint,
            days_lookback=body.days_lookback,
            max_points=body.max_points,
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
                "reason": "NASA_NDVI_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NASA_NDVI_VALIDATE_EXECUTE_Ω_ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_NASA_NDVI_P0_VALIDATE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class NasaNdviHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "nasa_ndvi_ultimate_hook_activated"
    persist: bool = True


@router.post("/nasa-ndvi-hook-activate")
async def nasa_ndvi_hook_activate_endpoint(
    body: NasaNdviHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME · activation officielle.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Vérification ANTI-GÉNÉRIQUE STRICTE : manifest_sha256 doit
         exister dans NASA_NDVI_VALIDATION_PATH avec n_calls_success>=1.
         Refus d'activer un manifest fabriqué.
      3. Construction manifest activation signé activation_sha256
         + sommaire espèces + bandes valides + bandes deferred
      4. Forensic log HOOK_ACTIVATIONS/NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME
      5. Persistance overlay history + audit doctrinal
      6. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        activate_nasa_ndvi_hook,
    )
    try:
        payload = activate_nasa_ndvi_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "NASA_NDVI_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NASA_NDVI_HOOK_ACTIVATE_EXECUTE_Ω_ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/nasa-ndvi-hook-status")
async def nasa_ndvi_hook_status_endpoint() -> JSONResponse:
    """NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME · état hook (PUBLIC RO)."""
    from engines.v8_institutional.especes.nasa_ndvi_omega import (
        get_nasa_ndvi_hook_status,
    )
    payload = get_nasa_ndvi_hook_status()
    return JSONResponse({
        "manifest_id": "NASA_NDVI_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME — 4 outputs calculables + 8 deferred
# Anti-générique strict : refus calcul sur manifest NASA NDVI fabriqué.
# ═════════════════════════════════════════════════════════════════════════
class HabitatOutputsComputeBody(BaseModel):
    nasa_ndvi_manifest_sha256: str
    species_to_threshold_map: Optional[Dict[str, str]] = None
    persist: bool = True


@router.post("/habitat-outputs-compute")
async def habitat_outputs_compute_endpoint(
    body: HabitatOutputsComputeBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME · 4 calculés + 8 deferred.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Lookup manifest_sha256 NASA NDVI validé (anti-générique strict :
         refus si SHA fabriqué/inconnu)
      3. Calcul des 4 outputs CALCULABLES (peer-reviewed sourcing) :
         · food_availability (Pettorelli 2005, Hamel 2009, Borowik 2013)
         · food_quality (Garroutte 2016)
         · food_deficiency (Hamel 2009, Hebblewhite 2008)
         · microhabitat_clusters (ranking ordinal n>=2)
      4. Tracé des 8 outputs DEFERRED avec missing_inputs[] +
         directive_extension_required[] (RSF/SSF/MaxEnt/USGS/canopy/etc.)
      5. Forensic log HABITAT/HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME
      6. Persistance overlay + audit doctrinal
      7. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        compute_habitat_outputs,
    )
    try:
        payload = compute_habitat_outputs(
            nasa_ndvi_manifest_sha256=body.nasa_ndvi_manifest_sha256,
            species_to_threshold_map=body.species_to_threshold_map,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "HABITAT_OUTPUTS_COMPUTE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_COMPUTE_EXECUTE_Ω_ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/habitat-outputs-status")
async def habitat_outputs_status_endpoint() -> JSONResponse:
    """HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        get_habitat_outputs_status,
    )
    payload = get_habitat_outputs_status()
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/habitat-outputs-doctrine-manifest")
async def habitat_outputs_doctrine_manifest_endpoint() -> JSONResponse:
    """HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME · doctrine manifest (PUBLIC RO).

    Expose les 12 outputs demandés, classification 4 calculables /
    8 deferred, références peer-reviewed et seuils espèces-spécifiques.
    """
    from engines.v8_institutional.especes.habitat_outputs_compute_omega import (  # noqa: E501
        OUTPUTS_REQUESTED_BY_COMMANDANT,
        OUTPUTS_COMPUTABLE_FROM_NDVI_EVI,
        OUTPUTS_DEFERRED_MISSING_INPUTS,
        SPECIES_FORAGE_THRESHOLDS_V1,
    )
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_DOCTRINE_MANIFEST_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_HABITAT_OUTPUTS_COMPUTE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "outputs_requested_by_commandant": (
            OUTPUTS_REQUESTED_BY_COMMANDANT),
        "n_outputs_requested": len(
            OUTPUTS_REQUESTED_BY_COMMANDANT),
        "outputs_computable_from_ndvi_evi": (
            OUTPUTS_COMPUTABLE_FROM_NDVI_EVI),
        "n_outputs_computable": len(
            OUTPUTS_COMPUTABLE_FROM_NDVI_EVI),
        "outputs_deferred_missing_inputs": (
            OUTPUTS_DEFERRED_MISSING_INPUTS),
        "n_outputs_deferred": len(
            OUTPUTS_DEFERRED_MISSING_INPUTS),
        "species_forage_thresholds_peer_reviewed": (
            SPECIES_FORAGE_THRESHOLDS_V1),
        "n_species": len(SPECIES_FORAGE_THRESHOLDS_V1),
        "v30_lock": "INVIOLÉ",
    })

# ═════════════════════════════════════════════════════════════════════════
# USGS_SOIL_P0_VALIDATE_Ω + USGS_SOIL_HOOK_ACTIVATE_Ω
# Pivot anti-générique strict : USGS NGS = US only → SoilGrids ISRIC
# (Hengl 2017 PLOS ONE) couvre Québec/Canada. 5/5 sites BP135 valid via
# offset terrestre +0.05° pour 3 sites water_mask St-Laurent.
# ═════════════════════════════════════════════════════════════════════════
class UsgsSoilValidateBody(BaseModel):
    species_coordinates: Dict[str, Dict[str, float]]
    properties: Optional[list] = None
    depth_label: str = "0-5cm"
    persist: bool = True


@router.post("/usgs-soil-validate")
async def usgs_soil_validate_endpoint(
    body: UsgsSoilValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """USGS_SOIL_P0_VALIDATE_Ω · validation multi-sites avec offset.

    Pivot anti-générique : SoilGrids ISRIC (USGS NGS=US only).
    Offset terrestre +0.05° (4 directions cardinales) pour
    récupérer les sites water_mask. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.usgs_soil_omega import (
        validate_usgs_soil_per_species,
    )
    try:
        payload = validate_usgs_soil_per_species(
            species_coordinates=body.species_coordinates,
            properties=body.properties,
            depth_label=body.depth_label,
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
                "reason": "USGS_SOIL_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "USGS_SOIL_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_USGS_SOIL_P0_VALIDATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class UsgsSoilHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "usgs_soil_hook_activated"
    persist: bool = True


@router.post("/usgs-soil-hook-activate")
async def usgs_soil_hook_activate_endpoint(
    body: UsgsSoilHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """USGS_SOIL_HOOK_ACTIVATE_Ω · activation officielle.

    Anti-générique strict : refus SHA fabriqué. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.usgs_soil_omega import (
        activate_usgs_soil_hook,
    )
    try:
        payload = activate_usgs_soil_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "USGS_SOIL_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "USGS_SOIL_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/usgs-soil-hook-status")
async def usgs_soil_hook_status_endpoint() -> JSONResponse:
    """USGS_SOIL_HOOK_ACTIVATE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.usgs_soil_omega import (
        get_usgs_soil_hook_status,
    )
    payload = get_usgs_soil_hook_status()
    return JSONResponse({
        "manifest_id": "USGS_SOIL_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# RSF_SSF_VALIDATE_Ω + RSF_SSF_HOOK_ACTIVATE_Ω
# Pivot anti-générique strict : RSF/SSF authentiques requièrent GPS data.
# Pivot vers MaxEnt-lite presence-only (Phillips 2006) via GBIF.
# ═════════════════════════════════════════════════════════════════════════
class RsfSsfValidateBody(BaseModel):
    species_to_taxon: Optional[Dict[str, int]] = None
    bp135_site_coordinates: Optional[
        Dict[str, Dict[str, float]]] = None
    bbox: Optional[Dict[str, float]] = None
    limit_per_species: int = 300
    persist: bool = True


@router.post("/rsf-ssf-validate")
async def rsf_ssf_validate_endpoint(
    body: RsfSsfValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """RSF_SSF_VALIDATE_Ω · MaxEnt-lite presence-only via GBIF.

    Pivot anti-générique strict : RSF/SSF authentiques requièrent GPS
    use+availability (Manly 2002, Avgar 2016). Pivot transparent vers
    Phillips 2006 envelope-based MaxEnt-lite.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        validate_rsf_ssf_per_species,
    )
    try:
        species_to_taxon_str = body.species_to_taxon
        species_to_taxon = (
            {k: int(v) for k, v in species_to_taxon_str.items()}
            if species_to_taxon_str else None)
        payload = validate_rsf_ssf_per_species(
            species_to_taxon=species_to_taxon,
            bp135_site_coordinates=body.bp135_site_coordinates,
            bbox=body.bbox,
            limit_per_species=body.limit_per_species,
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
                "reason": "RSF_SSF_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "RSF_SSF_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_RSF_SSF_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class RsfSsfHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "rsf_ssf_corridors_activated"
    persist: bool = True


@router.post("/rsf-ssf-hook-activate")
async def rsf_ssf_hook_activate_endpoint(
    body: RsfSsfHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """RSF_SSF_HOOK_ACTIVATE_Ω · activation officielle.

    Anti-générique strict : refus SHA fabriqué. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        activate_rsf_ssf_hook,
    )
    try:
        payload = activate_rsf_ssf_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "RSF_SSF_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "RSF_SSF_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_RSF_SSF_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/rsf-ssf-hook-status")
async def rsf_ssf_hook_status_endpoint() -> JSONResponse:
    """RSF_SSF_HOOK_ACTIVATE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        get_rsf_ssf_hook_status,
    )
    payload = get_rsf_ssf_hook_status()
    return JSONResponse({
        "manifest_id": "RSF_SSF_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_RSF_SSF_HOOK_ACTIVATE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# OPENTOPOGRAPHY_P0_VALIDATE_Ω — DEM elevation + slope per site BP135
# API key sécurisée via os.environ['OPENTOPOGRAPHY_API_KEY'] + masking.
# ═════════════════════════════════════════════════════════════════════════
class OpenTopographyValidateBody(BaseModel):
    site_coordinates: Dict[str, Dict[str, float]]
    demtypes: Optional[list] = None
    half_window_deg: float = 0.01
    persist: bool = True


@router.post("/opentopography-validate")
async def opentopography_validate_endpoint(
    body: OpenTopographyValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENTOPOGRAPHY_P0_VALIDATE_Ω · DEM elevation + slope.

    Probe AAIGrid ASCII parsable depuis OpenTopography globaldem API.
    API key lue depuis env (sécurisée). Anti-générique strict :
    NODATA REJETÉ sans imputation. 6 datasets DEM disponibles
    (SRTMGL3/SRTMGL1/NASADEM/AW3D30/COP30/COP90).
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.opentopography_omega import (
        validate_opentopography_per_site,
    )
    try:
        payload = validate_opentopography_per_site(
            site_coordinates=body.site_coordinates,
            demtypes=body.demtypes,
            half_window_deg=body.half_window_deg,
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
                "reason": "OPENTOPOGRAPHY_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OPENTOPOGRAPHY_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_OPENTOPOGRAPHY_P0_VALIDATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/opentopography-validation-status")
async def opentopography_validation_status_endpoint() -> JSONResponse:
    """OPENTOPOGRAPHY_P0_VALIDATE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        get_opentopography_validation_status,
    )
    payload = get_opentopography_validation_status()
    return JSONResponse({
        "manifest_id": "OPENTOPOGRAPHY_VALIDATION_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_OPENTOPOGRAPHY_P0_VALIDATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω — bedding/corridors/refuge partial unlock
# ═════════════════════════════════════════════════════════════════════════
class OpenTopographyHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "topography_hook_for_corridors_and_bedding"
    persist: bool = True


@router.post("/opentopography-hook-activate")
async def opentopography_hook_activate_endpoint(
    body: OpenTopographyHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω · activation officielle.

    Anti-générique strict : refus SHA fabriqué. Token Commandant requis.
    Débloque partiellement bedding_zones (slope-based), movement_corridors
    (least-cost path DEM), refuge_zones (DEM partial).
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.opentopography_omega import (
        activate_opentopography_hook,
    )
    try:
        payload = activate_opentopography_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "OPENTOPOGRAPHY_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OPENTOPOGRAPHY_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/opentopography-hook-status")
async def opentopography_hook_status_endpoint() -> JSONResponse:
    """OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.opentopography_omega import (
        get_opentopography_hook_status,
    )
    payload = get_opentopography_hook_status()
    return JSONResponse({
        "manifest_id": "OPENTOPOGRAPHY_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_OPENTOPOGRAPHY_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME — agrégation 7 hooks → 8/12 outputs
# ═════════════════════════════════════════════════════════════════════════
class HabitatRecomputeBody(BaseModel):
    species_to_site_map: Optional[Dict[str, str]] = None
    persist: bool = True


@router.post("/habitat-outputs-recompute")
async def habitat_outputs_recompute_endpoint(
    body: HabitatRecomputeBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME · agrégation 7 hooks.

    Charge les dernières validations NASA NDVI, USGS_SOIL, OPENTOPOGRAPHY,
    RSF_SSF + recalcule 8/12 outputs (4 initiaux + 4 nouveaux partiels) :
    food_avail/qual/def + bedding (Mysterud 2001) + refuge (Riley 1999 TRI)
    + saline (Belant 2010 pH+CEC) + habitat_suitability composite +
    corridor_continuity inter-sites (Forman 1986).
    Token Commandant requis. Anti-générique strict.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        recompute_habitat_outputs_with_all_hooks,
    )
    try:
        payload = recompute_habitat_outputs_with_all_hooks(
            species_to_site_map=body.species_to_site_map,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "HABITAT_OUTPUTS_RECOMPUTE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_RECOMPUTE_EXECUTE_Ω_ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/habitat-outputs-recompute-status")
async def habitat_outputs_recompute_status_endpoint() -> JSONResponse:
    """HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_omega import (  # noqa: E501
        get_habitat_recompute_status,
    )
    payload = get_habitat_recompute_status()
    return JSONResponse({
        "manifest_id": "HABITAT_RECOMPUTE_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# CANOPY_P0_VALIDATE_Ω + CANOPY_HOOK_ACTIVATE_Ω
# Forest cover via NASA MOD44B VCF (Hansen 2003, DiMiceli 2017).
# Débloque bedding_zones_FULL + refuge_zones_FULL.
# ═════════════════════════════════════════════════════════════════════════
class CanopyValidateBody(BaseModel):
    site_coordinates: Dict[str, Dict[str, float]]
    bands_logical: Optional[list] = None
    years_lookback: int = 3
    end_year: Optional[int] = None
    persist: bool = True


@router.post("/canopy-validate")
async def canopy_validate_endpoint(
    body: CanopyValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """CANOPY_P0_VALIDATE_Ω · MOD44B Vegetation Continuous Fields.

    Probe NASA MOD44B subset endpoint pour 4 bandes : TREE_COVER,
    NONTREE_VEG, NONVEG, QUALITY (Hansen 2003 + DiMiceli 2017).
    Anti-générique strict : NODATA=200 rejeté. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.canopy_omega import (
        validate_canopy_per_site,
    )
    try:
        payload = validate_canopy_per_site(
            site_coordinates=body.site_coordinates,
            bands_logical=body.bands_logical,
            years_lookback=body.years_lookback,
            end_year=body.end_year,
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
                "reason": "CANOPY_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "CANOPY_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_CANOPY_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class CanopyHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "bedding_refuge_full_via_forest_cover"
    persist: bool = True


@router.post("/canopy-hook-activate")
async def canopy_hook_activate_endpoint(
    body: CanopyHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """CANOPY_HOOK_ACTIVATE_Ω · activation officielle.

    Anti-générique strict : refus SHA fabriqué. Débloque
    bedding_zones_FULL + refuge_zones_FULL. Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.canopy_omega import (
        activate_canopy_hook,
    )
    try:
        payload = activate_canopy_hook(
            manifest_sha256=body.manifest_sha256,
            reason=body.reason,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "CANOPY_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "CANOPY_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_CANOPY_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/canopy-hook-status")
async def canopy_hook_status_endpoint() -> JSONResponse:
    """CANOPY_HOOK_ACTIVATE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.canopy_omega import (
        get_canopy_hook_status,
    )
    payload = get_canopy_hook_status()
    return JSONResponse({
        "manifest_id": "CANOPY_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P1_CANOPY_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# NASA_NDVI_TIMESERIES_DECADE_Ω — multi-saison × multi-année × multi-site
# Débloque feeding_zones (Borowik 2013) + rut_phenology_proxy (Hebblewhite).
# ═════════════════════════════════════════════════════════════════════════
class NasaNdviTimeseriesDecadeBody(BaseModel):
    site_coordinates: Dict[str, Dict[str, float]]
    end_year: Optional[int] = None
    years_lookback: int = 5
    seasonal_windows: Optional[list] = None
    bands_logical: Optional[list] = None
    persist: bool = True


@router.post("/nasa-ndvi-timeseries-validate")
async def nasa_ndvi_timeseries_validate_endpoint(
    body: NasaNdviTimeseriesDecadeBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NASA_NDVI_TIMESERIES_DECADE_Ω · multi-season multi-year.

    Probe MOD13Q1 sur fenêtres été (Borowik 2013) + fall pre-rut
    (Hebblewhite 2008) sur n années consécutives. Anti-générique strict.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        validate_nasa_ndvi_timeseries_decade,
    )
    try:
        payload = validate_nasa_ndvi_timeseries_decade(
            site_coordinates=body.site_coordinates,
            end_year=body.end_year,
            years_lookback=body.years_lookback,
            seasonal_windows=body.seasonal_windows,
            bands_logical=body.bands_logical,
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
                "reason": "NASA_NDVI_TIMESERIES_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NASA_NDVI_TIMESERIES_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P3_NASA_NDVI_TIMESERIES_DECADE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/nasa-ndvi-timeseries-status")
async def nasa_ndvi_timeseries_status_endpoint() -> JSONResponse:
    """NASA_NDVI_TIMESERIES_DECADE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.nasa_ndvi_timeseries_decade_omega import (  # noqa: E501
        get_ndvi_decade_status,
    )
    payload = get_ndvi_decade_status()
    return JSONResponse({
        "manifest_id": "NASA_NDVI_TIMESERIES_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P3_NASA_NDVI_TIMESERIES_DECADE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })

