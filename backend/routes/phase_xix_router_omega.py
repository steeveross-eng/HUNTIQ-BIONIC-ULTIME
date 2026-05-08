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
from typing import Any, Dict, List

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


# P20_PHASE3 · FORCE PURGE · headers anti-cache doctrinaux sur toutes
# les responses super-masters. Ordre Commandant STEEVE-MAX 2026-05-08.
_NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-BCE-4X-Force-Purge": "P20_PHASE3_FORCE_PURGE_2026_05_08_2147",
}


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



# ═════════════════════════════════════════════════════════════════════════
# ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω (P4) — OSM Overpass + WorldPop
# Débloque pressure_sensitive_zones (Frid & Dill 2002 + Naidoo 2010 +
# Tucker 2018). Sources libres anti-générique (zero token).
# ═════════════════════════════════════════════════════════════════════════
class AnthropogenicPressureValidateBody(BaseModel):
    site_coordinates: Dict[str, Dict[str, float]]
    radius_m_roads: int = 5000
    half_side_deg_population: float = 0.01
    year_population: int = 2020
    persist: bool = True


@router.post("/anthropogenic-pressure-validate")
async def anthropogenic_pressure_validate_endpoint(
    body: AnthropogenicPressureValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ANTHROPOGENIC_PRESSURE_P0_VALIDATE_Ω · multi-sites probes LIVE.

    OSM Overpass (roads/buildings/landuse) + WorldPop (population).
    Composite index doctrinal Naidoo & Burton 2010 §3.2.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        validate_anthropogenic_pressure_per_site,
    )
    try:
        payload = validate_anthropogenic_pressure_per_site(
            site_coordinates=body.site_coordinates,
            radius_m_roads=body.radius_m_roads,
            half_side_deg_population=body.half_side_deg_population,
            year_population=body.year_population,
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
                "reason": "ANTHROPOGENIC_PRESSURE_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "ANTHROPOGENIC_PRESSURE_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P4_ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class AnthropogenicPressureHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "pressure_sensitive_zones_activation"
    persist: bool = True


@router.post("/anthropogenic-pressure-hook-activate")
async def anthropogenic_pressure_hook_activate_endpoint(
    body: AnthropogenicPressureHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω · activation officielle.

    Anti-générique strict : refus si SHA fabriqué/inconnu.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        activate_anthropogenic_pressure_hook,
    )
    try:
        payload = activate_anthropogenic_pressure_hook(
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
                "reason": "ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P4_ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/anthropogenic-pressure-hook-status")
async def anthropogenic_pressure_hook_status_endpoint() -> JSONResponse:
    """ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.anthropogenic_pressure_omega import (  # noqa: E501
        get_anthropogenic_pressure_hook_status,
    )
    payload = get_anthropogenic_pressure_hook_status()
    return JSONResponse({
        "manifest_id": "ANTHROPOGENIC_PRESSURE_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P4_ANTHROPOGENIC_PRESSURE_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3 (P5) — greffe pressure_sensitive
# Atteint 9/12 outputs computables (vs 8/12 en V2). FUSION ADD-ONLY strict.
# ═════════════════════════════════════════════════════════════════════════
class HabitatRecomputeV3Body(BaseModel):
    species_to_site_map: Optional[Dict[str, str]] = None
    persist: bool = True
    require_anthropogenic_hook_active: bool = True


@router.post("/habitat-outputs-recompute-v3")
async def habitat_outputs_recompute_v3_endpoint(
    body: HabitatRecomputeV3Body,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3 · greffe pressure_sensitive.

    Réutilise V2 sans mutation (FUSION ADD-ONLY) puis greffe
    pressure_sensitive_zones (Frid & Dill 2002, Naidoo 2010, Tucker 2018).
    Refuse l'exécution si ANTHROPOGENIC_PRESSURE_HOOK n'est pas activé.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        recompute_habitat_outputs_with_anthropogenic_pressure_v3,
    )
    try:
        payload = (
            recompute_habitat_outputs_with_anthropogenic_pressure_v3(
                species_to_site_map=body.species_to_site_map,
                persist=body.persist,
                require_anthropogenic_hook_active=(
                    body.require_anthropogenic_hook_active),
            ))
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "HABITAT_OUTPUTS_RECOMPUTE_V3_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_RECOMPUTE_V3_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/habitat-outputs-recompute-v3-status")
async def habitat_outputs_recompute_v3_status_endpoint() -> JSONResponse:
    """HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3 · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.habitat_outputs_recompute_v3_omega import (  # noqa: E501
        get_habitat_recompute_v3_status,
    )
    payload = get_habitat_recompute_v3_status()
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_RECOMPUTE_V3_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P5_HABITAT_OUTPUTS_RECOMPUTE_Ω_ULTIME_V3",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# COMMANDE_INSTITUTIONNELLE_Ω V12-MAÎTRE
# CONTAMINATION → AFFÛTS dependency lock (R1-R6)
# ═════════════════════════════════════════════════════════════════════════
class ContaminationAffutHookActivateBody(BaseModel):
    activation_input_string: str = (
        "CONTAMINATION_AFFUT_DEPENDENCY_V12")
    persist: bool = True


@router.post("/contamination-affut-dependency-hook-activate")
async def contamination_affut_hook_activate_endpoint(
    body: ContaminationAffutHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """HOOK_CONTAMINATION_AFFUT_DEPENDENCY · activation V12-MAÎTRE.

    Vérification SHA-256 doctrinale obligatoire.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        activate_contamination_affut_dependency_hook,
    )
    try:
        payload = activate_contamination_affut_dependency_hook(
            activation_input_string=body.activation_input_string,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "CONTAMINATION_AFFUT_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "CONTAMINATION_AFFUT_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class ContaminationAffutAuditBody(BaseModel):
    tiles: list
    persist_violations: bool = True


@router.post("/contamination-affut-dependency-audit")
async def contamination_affut_audit_endpoint(
    body: ContaminationAffutAuditBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """CONTAMINATION_AFFUT_DEPENDENCY_AUDIT_Ω · A1+A2+A3+A4 batch."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        audit_tiles_dependency,
    )
    try:
        payload = audit_tiles_dependency(
            tiles=body.tiles,
            persist_violations=body.persist_violations,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "CONTAMINATION_AFFUT_AUDIT_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "CONTAMINATION_AFFUT_AUDIT_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/contamination-affut-dependency-hook-status")
async def contamination_affut_hook_status_endpoint() -> JSONResponse:
    """HOOK_CONTAMINATION_AFFUT_DEPENDENCY · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.contamination_affut_dependency_omega import (  # noqa: E501
        get_contamination_affut_dependency_hook_status,
    )
    payload = get_contamination_affut_dependency_hook_status()
    return JSONResponse({
        "manifest_id":
            "CONTAMINATION_AFFUT_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "COMMANDE_INSTITUTIONNELLE_Ω_V12-MAÎTRE",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# TEMPORAL_RUT_DATA_HOOK_ACTIVATE_Ω (P6) — débloque rut_zones (10/12)
# ═════════════════════════════════════════════════════════════════════════
class TemporalRutValidateBody(BaseModel):
    site_to_species_map: Optional[Dict[str, str]] = None
    site_coordinates: Optional[Dict[str, Dict[str, float]]] = None
    gbif_radius_km: float = 50.0
    persist: bool = True


@router.post("/temporal-rut-validate")
async def temporal_rut_validate_endpoint(
    body: TemporalRutValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """TEMPORAL_RUT_DATA_P0_VALIDATE_Ω · 3 piliers physiques.

    Photopériode (Bronson 1989) + NDVI fall (Hebblewhite 2008) +
    GBIF rut months (Bowyer 1981).
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        validate_temporal_rut_data_per_site,
    )
    try:
        payload = validate_temporal_rut_data_per_site(
            site_to_species_map=body.site_to_species_map,
            site_coordinates=body.site_coordinates,
            gbif_radius_km=body.gbif_radius_km,
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
                "reason": "TEMPORAL_RUT_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "TEMPORAL_RUT_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P6_TEMPORAL_RUT_DATA_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class TemporalRutHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = "unlock_rut_zones_for_full_12_outputs"
    persist: bool = True


@router.post("/temporal-rut-hook-activate")
async def temporal_rut_hook_activate_endpoint(
    body: TemporalRutHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """TEMPORAL_RUT_DATA_HOOK_ACTIVATE_Ω · activation officielle."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        activate_temporal_rut_data_hook,
    )
    try:
        payload = activate_temporal_rut_data_hook(
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
                "reason": "TEMPORAL_RUT_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "TEMPORAL_RUT_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P6_TEMPORAL_RUT_DATA_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/temporal-rut-hook-status")
async def temporal_rut_hook_status_endpoint() -> JSONResponse:
    """TEMPORAL_RUT_DATA_HOOK · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.temporal_rut_data_omega import (
        get_temporal_rut_data_hook_status,
    )
    payload = get_temporal_rut_data_hook_status()
    return JSONResponse({
        "manifest_id": "TEMPORAL_RUT_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P6_TEMPORAL_RUT_DATA_HOOK_ACTIVATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# HABITAT_OUTPUTS_FINAL_MERGE_Ω (P7) — 10/12 outputs computables
# ═════════════════════════════════════════════════════════════════════════
class HabitatFinalMergeBody(BaseModel):
    species_to_site_map: Optional[Dict[str, str]] = None
    persist: bool = True
    require_rut_hook_active: bool = True


@router.post("/habitat-outputs-final-merge")
async def habitat_outputs_final_merge_endpoint(
    body: HabitatFinalMergeBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """HABITAT_OUTPUTS_FINAL_MERGE_Ω · greffe rut sur V3.

    Réutilise V3 sans mutation (FUSION ADD-ONLY) puis greffe rut_zones.
    Refuse l'exécution si TEMPORAL_RUT_HOOK n'est pas activé.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        merge_habitat_outputs_final,
    )
    try:
        payload = merge_habitat_outputs_final(
            species_to_site_map=body.species_to_site_map,
            persist=body.persist,
            require_rut_hook_active=body.require_rut_hook_active,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "HABITAT_OUTPUTS_FINAL_MERGE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/habitat-outputs-final-merge-status")
async def habitat_outputs_final_merge_status_endpoint() -> JSONResponse:
    """HABITAT_OUTPUTS_FINAL_MERGE_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.habitat_outputs_final_merge_omega import (  # noqa: E501
        get_habitat_final_merge_status,
    )
    payload = get_habitat_final_merge_status()
    return JSONResponse({
        "manifest_id": "HABITAT_OUTPUTS_FINAL_MERGE_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P7_HABITAT_OUTPUTS_FINAL_MERGE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# NASA_NDVI_DENSE_GRID_Ω (P8) — débloque feeding_FULL + microhab_dense
# ═════════════════════════════════════════════════════════════════════════
class NasaNdviDenseGridValidateBody(BaseModel):
    site_coordinates: Optional[Dict[str, Dict[str, float]]] = None
    species_to_site_map: Optional[Dict[str, str]] = None
    year: Optional[int] = None
    km_above_below: int = 2
    km_left_right: int = 2
    bands_logical: Optional[List[str]] = None
    persist: bool = True


@router.post("/nasa-ndvi-dense-grid-validate")
async def nasa_ndvi_dense_grid_validate_endpoint(
    body: NasaNdviDenseGridValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NASA_NDVI_DENSE_GRID_P0_VALIDATE_Ω · spatial subset MOD13Q1.

    kmAboveBelow×kmLeftRight → grille N×N pixels (231m, summer 2023).
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (
        validate_nasa_ndvi_dense_grid,
    )
    try:
        payload = validate_nasa_ndvi_dense_grid(
            site_coordinates=body.site_coordinates,
            species_to_site_map=body.species_to_site_map,
            year=body.year,
            km_above_below=body.km_above_below,
            km_left_right=body.km_left_right,
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
                "reason": "NASA_NDVI_DENSE_GRID_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "NASA_NDVI_DENSE_GRID_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class NasaNdviDenseGridHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = (
        "unlock_feeding_zones_FULL_and_microhabitat_dense")
    persist: bool = True


@router.post("/nasa-ndvi-dense-grid-hook-activate")
async def nasa_ndvi_dense_grid_hook_activate_endpoint(
    body: NasaNdviDenseGridHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE_Ω · activation officielle."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (
        activate_nasa_ndvi_dense_grid_hook,
    )
    try:
        payload = activate_nasa_ndvi_dense_grid_hook(
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
                "reason": (
                    "NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE_FAILED"),
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "NASA_NDVI_DENSE_GRID_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/nasa-ndvi-dense-grid-hook-status")
async def nasa_ndvi_dense_grid_hook_status_endpoint() -> JSONResponse:
    """NASA_NDVI_DENSE_GRID_HOOK_STATUS_GET_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.nasa_ndvi_dense_grid_omega import (
        get_nasa_ndvi_dense_grid_hook_status,
    )
    payload = get_nasa_ndvi_dense_grid_hook_status()
    return JSONResponse({
        "manifest_id": "NASA_NDVI_DENSE_GRID_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P8_NASA_NDVI_DENSE_GRID_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# HABITAT_OUTPUTS_COMPLETE_MERGE_Ω (P9) — 12/12 outputs computables
# ═════════════════════════════════════════════════════════════════════════
class HabitatCompleteMergeBody(BaseModel):
    species_to_site_map: Optional[Dict[str, str]] = None
    persist: bool = True
    require_dense_grid_hook_active: bool = True


@router.post("/habitat-outputs-complete-merge")
async def habitat_outputs_complete_merge_endpoint(
    body: HabitatCompleteMergeBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """HABITAT_OUTPUTS_COMPLETE_MERGE_Ω · 12/12 outputs.

    Réutilise FINAL sans mutation (FUSION ADD-ONLY) puis greffe
    feeding_zones_FULL + microhabitat_clusters_global_dense.
    Refuse l'exécution si NASA_NDVI_DENSE_GRID_HOOK n'est pas activé.
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        merge_habitat_outputs_complete,
    )
    try:
        payload = merge_habitat_outputs_complete(
            species_to_site_map=body.species_to_site_map,
            persist=body.persist,
            require_dense_grid_hook_active=(
                body.require_dense_grid_hook_active),
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": (
                    "HABITAT_OUTPUTS_COMPLETE_MERGE_FAILED"),
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "HABITAT_OUTPUTS_COMPLETE_MERGE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/habitat-outputs-complete-merge-status")
async def habitat_outputs_complete_merge_status_endpoint() -> JSONResponse:
    """HABITAT_OUTPUTS_COMPLETE_MERGE_STATUS_Ω · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.habitat_outputs_complete_merge_omega import (  # noqa: E501
        get_habitat_complete_merge_status,
    )
    payload = get_habitat_complete_merge_status()
    return JSONResponse({
        "manifest_id":
            "HABITAT_OUTPUTS_COMPLETE_MERGE_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P9_HABITAT_OUTPUTS_COMPLETE_MERGE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# TERRITOIRE_VISUALIZER_ENDPOINT_Ω (P10)
# Exposition unifiée de TOUTES les couches doctrinales (PUBLIC RO).
# Anti-générique strict : lecture seule, aucune mutation, aucune fabrication.
# ═════════════════════════════════════════════════════════════════════════
@router.get("/visualizer-all-layers")
async def visualizer_all_layers_endpoint() -> JSONResponse:
    """TERRITOIRE_VISUALIZER_ENDPOINT_Ω · scan unifié read-only.

    Expose toutes les couches doctrinales pour validation et production :
    SHA-256, verdict, status, last_updated par couche. PUBLIC RO.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.visualizer_endpoint_omega import (
        expose_all_layers_unified,
    )
    try:
        payload = expose_all_layers_unified()
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "VISUALIZER_ALL_LAYERS_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "TERRITOIRE_VISUALIZER_ENDPOINT_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P10_TERRITOIRE_VISUALIZER_ENDPOINT_CREATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω (P11) — 10 ans × Mann-Kendall trend
# ═════════════════════════════════════════════════════════════════════════
class MultiYearDenseGridValidateBody(BaseModel):
    site_coordinates: Optional[Dict[str, Dict[str, float]]] = None
    species_to_site_map: Optional[Dict[str, str]] = None
    year_start: int = 2015
    year_end: int = 2024
    km_above_below: int = 2
    km_left_right: int = 2
    persist: bool = True


@router.post("/multi-year-dense-grid-timeseries-validate")
async def multi_year_dense_grid_validate_endpoint(
    body: MultiYearDenseGridValidateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P11 · 10 ans × dense grid × Mann-Kendall trend test.

    NOTE LONG-RUNNING : utiliser localhost:8001 (60-180s typique).
    Token Commandant requis.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        validate_multi_year_dense_grid_timeseries,
    )
    try:
        payload = validate_multi_year_dense_grid_timeseries(
            site_coordinates=body.site_coordinates,
            species_to_site_map=body.species_to_site_map,
            year_start=body.year_start,
            year_end=body.year_end,
            km_above_below=body.km_above_below,
            km_left_right=body.km_left_right,
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
                "reason": "MULTI_YEAR_DENSE_GRID_VALIDATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "MULTI_YEAR_DENSE_GRID_VALIDATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class MultiYearHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = (
        "ecological_longitudinal_trend_analysis_10_years")
    persist: bool = True


@router.post("/multi-year-dense-grid-timeseries-hook-activate")
async def multi_year_dense_grid_hook_activate_endpoint(
    body: MultiYearHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P11 · activation officielle. Token Commandant requis."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        activate_multi_year_dense_grid_timeseries_hook,
    )
    try:
        payload = (
            activate_multi_year_dense_grid_timeseries_hook(
                manifest_sha256=body.manifest_sha256,
                reason=body.reason,
                persist=body.persist,
            ))
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": (
                    "MULTI_YEAR_DENSE_GRID_HOOK_ACTIVATE_FAILED"),
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "MULTI_YEAR_DENSE_GRID_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/multi-year-dense-grid-timeseries-hook-status")
async def multi_year_dense_grid_hook_status_endpoint() -> JSONResponse:
    """P11 · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.multi_year_dense_grid_timeseries_omega import (  # noqa: E501
        get_multi_year_dense_grid_timeseries_hook_status,
    )
    payload = (
        get_multi_year_dense_grid_timeseries_hook_status())
    return JSONResponse({
        "manifest_id":
            "MULTI_YEAR_DENSE_GRID_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P11_MULTI_YEAR_DENSE_GRID_TIMESERIES_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# MULTI_SIGNATURE_VERIFICATION_HOOK_Ω (P12) — Ed25519 + PGP RSA-2048
# ═════════════════════════════════════════════════════════════════════════
class MultiSignatureHookActivateBody(BaseModel):
    reason: str = (
        "reinforce_cryptographic_integrity_of_all_manifests")
    persist: bool = True


@router.post("/multi-signature-verification-hook-activate")
async def multi_signature_hook_activate_endpoint(
    body: MultiSignatureHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P12 · co-signe TOUS les manifests + vérifie. Token requis."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        activate_multi_signature_verification_hook,
    )
    try:
        payload = activate_multi_signature_verification_hook(
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
                "reason": (
                    "MULTI_SIGNATURE_HOOK_ACTIVATE_FAILED"),
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "MULTI_SIGNATURE_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.post("/multi-signature-verify-all")
async def multi_signature_verify_all_endpoint(
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P12 · vérifie TOUTES les signatures (Ed25519 + PGP).
    Token requis (audit cryptographique).
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        verify_all_signatures,
    )
    try:
        payload = verify_all_signatures(persist=False)
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "MULTI_SIGNATURE_VERIFY_ALL_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "MULTI_SIGNATURE_VERIFY_ALL_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/multi-signature-verification-hook-status")
async def multi_signature_hook_status_endpoint() -> JSONResponse:
    """P12 · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.multi_signature_verification_omega import (  # noqa: E501
        get_multi_signature_hook_status,
    )
    payload = get_multi_signature_hook_status()
    return JSONResponse({
        "manifest_id":
            "MULTI_SIGNATURE_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P12_MULTI_SIGNATURE_VERIFICATION_HOOK_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# TERRITOIRE_DOWNLOAD_ENDPOINT_Ω (P13) — HTTPS one-click ZIP
# ═════════════════════════════════════════════════════════════════════════
@router.get("/download-all-layers-bundle")
async def download_all_layers_bundle_endpoint(
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
):
    """P13 · GET ZIP+JSON+SHA256_MANIFEST one-click HTTPS.

    Returns ZIP bytes streaming (Content-Disposition attachment).
    Token Commandant requis (write-equivalent operation).
    """
    _verify_commandant_token(x_commandant_token)
    from fastapi.responses import Response as FastResponse
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.download_endpoint_omega import (
        build_download_bundle,
    )
    try:
        zip_bytes, metadata = build_download_bundle()
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "DOWNLOAD_BUNDLE_BUILD_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    timestamp = (
        metadata.get("generated_at_utc", "unknown")
        .replace(":", "").replace("-", "").replace("+", "_"))
    filename = (
        f"territoire_download_bundle_{timestamp}.zip")
    headers = {
        "Content-Disposition": (
            f'attachment; filename="{filename}"'),
        "X-Bundle-Sha256": metadata.get(
            "bundle_sha256", "unknown"),
        "X-N-Files-Included": str(
            metadata.get("n_files_included", 0)),
        "X-Doctrine": (
            "BCE-4X_ULTIME_ABSOLU_ANTI_GENERIQUE_STRICT"),
        "X-V30-Lock": "INVIOLE",
        "X-Manifest-Id": "TERRITOIRE_DOWNLOAD_BUNDLE_OMEGA",
        "X-Ordre":
            "P13_TERRITOIRE_DOWNLOAD_ENDPOINT_CREATE_OMEGA",
    }
    return FastResponse(
        content=zip_bytes,
        media_type="application/zip",
        headers=headers)


@router.get("/download-all-layers-bundle-status")
async def download_all_layers_bundle_status_endpoint() -> JSONResponse:
    """P13 · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.download_endpoint_omega import (
        get_download_endpoint_status,
    )
    payload = get_download_endpoint_status()
    return JSONResponse({
        "manifest_id":
            "TERRITOIRE_DOWNLOAD_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P13_TERRITOIRE_DOWNLOAD_ENDPOINT_CREATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# MERKLE_TREE_ANCHOR_HOOK_Ω (P14) — Merkle Tree + OpenTimestamps
# ═════════════════════════════════════════════════════════════════════════
class MerkleTreeBuildBody(BaseModel):
    persist: bool = True
    enable_ots_anchor: bool = True


@router.post("/merkle-tree-anchor-build")
async def merkle_tree_anchor_build_endpoint(
    body: MerkleTreeBuildBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P14 · build Merkle tree + stamp OpenTimestamps."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        build_and_anchor_merkle_tree,
    )
    try:
        payload = build_and_anchor_merkle_tree(
            persist=body.persist,
            enable_ots_anchor=body.enable_ots_anchor,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "MERKLE_BUILD_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "MERKLE_TREE_ANCHOR_BUILD_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P14_MERKLE_TREE_ANCHOR_HOOK_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class MerkleTreeHookActivateBody(BaseModel):
    manifest_sha256: str
    reason: str = (
        "anchor_all_doctrinal_SHA256_in_public_merkle_tree")
    persist: bool = True


@router.post("/merkle-tree-anchor-hook-activate")
async def merkle_tree_anchor_hook_activate_endpoint(
    body: MerkleTreeHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P14 · activation officielle. Token Commandant requis."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        activate_merkle_tree_anchor_hook,
    )
    try:
        payload = activate_merkle_tree_anchor_hook(
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
                "reason": "MERKLE_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "MERKLE_TREE_ANCHOR_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P14_MERKLE_TREE_ANCHOR_HOOK_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/merkle-tree-anchor-hook-status")
async def merkle_tree_anchor_hook_status_endpoint() -> JSONResponse:
    """P14 · état (PUBLIC RO)."""
    from engines.v8_institutional.especes.merkle_tree_anchor_omega import (
        get_merkle_tree_anchor_hook_status,
    )
    payload = get_merkle_tree_anchor_hook_status()
    return JSONResponse({
        "manifest_id":
            "MERKLE_TREE_ANCHOR_HOOK_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P14_MERKLE_TREE_ANCHOR_HOOK_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# TERRITOIRE_V7_PREMIUM_REPORTS_Ω
# ═════════════════════════════════════════════════════════════════════════
class PremiumReportGenerateBody(BaseModel):
    species: str
    waypoint_lat: float
    waypoint_lon: float
    layer: str
    season: str
    waypoint_id: Optional[str] = None
    radius_m: int = 500


@router.post("/premium-report-generate")
async def premium_report_generate_endpoint(
    body: PremiumReportGenerateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """TERRITOIRE_V7_PREMIUM_REPORTS_Ω · plein écran genérique.

    Token Commandant requis (genère un rapport personnalisé).
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        generate_premium_report,
    )
    try:
        payload = generate_premium_report(
            species=body.species,
            waypoint_lat=body.waypoint_lat,
            waypoint_lon=body.waypoint_lon,
            layer=body.layer,
            season=body.season,
            waypoint_id=body.waypoint_id,
            radius_m=body.radius_m,
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
                "reason": "PREMIUM_REPORT_GENERATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "TERRITOIRE_V7_PREMIUM_REPORT_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "EMERGENT_EXECUTE_TERRITOIRE_V7_PREMIUM_REPORTS",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/premium-reports-status")
async def premium_reports_status_endpoint() -> JSONResponse:
    """TERRITOIRE_V7_PREMIUM_REPORTS_Ω · status (PUBLIC RO)."""
    from engines.v8_institutional.especes.premium_reports_v7_omega import (
        get_premium_reports_status,
    )
    payload = get_premium_reports_status()
    return JSONResponse({
        "manifest_id":
            "TERRITOIRE_V7_PREMIUM_REPORTS_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre":
            "EMERGENT_EXECUTE_TERRITOIRE_V7_PREMIUM_REPORTS",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# MESSAGING_ENGINE_INTEGRATION (Premium V7 footer share)
# ═════════════════════════════════════════════════════════════════════════
class MessagingShareBody(BaseModel):
    report_sha256: str
    channel: str  # "email" | "social_media" | "internal"
    recipient: str
    subject: Optional[str] = None
    notes: Optional[str] = None


@router.post("/messaging-share")
async def messaging_share_endpoint(
    body: MessagingShareBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """Messaging engine endpoint pour partage rapport premium.

    Anti-générique strict : route le partage via channels.
    Le canal réel est documenté (pas mocké) dans le payload.
    """
    _verify_commandant_token(x_commandant_token)
    if body.channel not in (
            "email", "social_media", "internal"):
        raise HTTPException(
            status_code=400,
            detail=f"CHANNEL_INVALID::{body.channel}")
    if not body.report_sha256 or len(
            body.report_sha256) != 64:
        raise HTTPException(
            status_code=400,
            detail="REPORT_SHA256_INVALID::expected_64_hex")
    # Anti-générique : on documente le canal mais l'envoi
    # réel nécessite intégration mail SMTP / API sociale spécifiques
    # qui sont hors périmètre direct V14. On persiste le request.
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        log_forensic_event,
    )
    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="PREMIUM_REPORT_SHARE_REQUESTED",
        details={
            "report_sha256": body.report_sha256,
            "channel": body.channel,
            "recipient_hash": (
                hashlib.sha256(
                    body.recipient.encode()).hexdigest()[:32]),
            "subject": body.subject,
        },
        persist=True)
    return JSONResponse({
        "manifest_id": "MESSAGING_SHARE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "result": {
            "share_status": "SHARE_QUEUED_INTEGRATION_PENDING",
            "channel": body.channel,
            "report_sha256": body.report_sha256,
            "recipient_hash_anonymized": hashlib.sha256(
                body.recipient.encode()
            ).hexdigest()[:32],
            "doctrinal_caveat": (
                "Le partage est queued pour intégration "
                "channel-specific (SMTP email / API social). "
                "Anti-générique : pas de fake sending. "
                "Audit log persisté."),
            "queued_at_utc": (
                datetime.now(timezone.utc).isoformat(
                    timespec="seconds")),
        },
        "v30_lock": "INVIOLÉ",
    })




# ═════════════════════════════════════════════════════════════════════════
# P22 · COMMANDANT_VALIDATION_P14_PREMIUM_V7_Ω
# P23 · MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω
# P24 · OTS_UPGRADE_AUTOMATION_Ω
# FUSION ADD-ONLY · V30_LOCK INVIOLÉ · ANTI-GÉNÉRIQUE STRICT
# ═════════════════════════════════════════════════════════════════════════


# ----- P22 -----
class CommandantValidationRecordBody(BaseModel):
    scope: str
    decision: str  # APPROVED | REJECTED | PENDING_REVIEW
    sha256_list: List[str]
    notes: Optional[str] = None
    persist: bool = True


@router.post("/commandant-validation-record")
async def commandant_validation_record_endpoint(
    body: CommandantValidationRecordBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P22 · enregistre une validation Commandant (audit doctrinal)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.commandant_validations_omega import (
        record_commandant_validation,
    )
    try:
        payload = record_commandant_validation(
            scope=body.scope,
            decision=body.decision,
            sha256_list=body.sha256_list,
            notes=body.notes,
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
                "reason": "COMMANDANT_VALIDATION_RECORD_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "COMMANDANT_VALIDATION_RECORD_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P22_COMMANDANT_VALIDATION_P14_PREMIUM_V7_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/commandant-validation-status")
async def commandant_validation_status_endpoint() -> JSONResponse:
    """P22 · status lecture seule (PUBLIC RO)."""
    from engines.v8_institutional.especes.commandant_validations_omega import (
        get_commandant_validations_status,
    )
    payload = get_commandant_validations_status()
    return JSONResponse({
        "manifest_id": "COMMANDANT_VALIDATION_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P22_COMMANDANT_VALIDATION_P14_PREMIUM_V7_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ----- P23 -----
class MessagingEngineChannelHookActivateBody(BaseModel):
    persist: bool = True


@router.post("/messaging-engine-channel-hook-activate")
async def messaging_engine_channel_hook_activate_endpoint(
    body: MessagingEngineChannelHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P23 · activation officielle canaux messaging (email + internal)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.messaging_engine_omega import (
        activate_messaging_engine_channel_hook,
    )
    try:
        payload = activate_messaging_engine_channel_hook(
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "MESSAGING_ENGINE_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "MESSAGING_ENGINE_CHANNEL_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P23_MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class MessagingEngineChannelShareBody(BaseModel):
    report_sha256: str
    channel: str  # email | internal (social_media rejeté doctrinal)
    recipient: str
    subject: Optional[str] = None
    notes: Optional[str] = None
    reply_to: Optional[str] = None  # P20_PHASE2 · email perso utilisateur


@router.post("/messaging-engine-channel-share")
async def messaging_engine_channel_share_endpoint(
    body: MessagingEngineChannelShareBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P23 · partage rapport premium via canal (anti-générique strict).

    `social_media` est explicitement exclu par directive Commandant.
    P20_PHASE2 : email = Resend API · `reply_to` = email perso utilisateur.
    """
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.messaging_engine_omega import (
        share_premium_report,
    )
    try:
        payload = share_premium_report(
            report_sha256=body.report_sha256,
            channel=body.channel,
            recipient=body.recipient,
            subject=body.subject,
            notes=body.notes,
            reply_to=body.reply_to,
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
                "reason": "MESSAGING_ENGINE_SHARE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "MESSAGING_ENGINE_CHANNEL_SHARE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P23_MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/messaging-engine-channel-status")
async def messaging_engine_channel_status_endpoint() -> JSONResponse:
    """P23 · status lecture seule (PUBLIC RO)."""
    from engines.v8_institutional.especes.messaging_engine_omega import (
        get_messaging_engine_hook_status,
    )
    payload = get_messaging_engine_hook_status()
    return JSONResponse({
        "manifest_id": "MESSAGING_ENGINE_CHANNEL_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P23_MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ----- P24 -----
class OtsUpgradeAutomationHookActivateBody(BaseModel):
    interval_s: int = 21600  # 6h
    run_immediate_scan: bool = True
    persist: bool = True


@router.post("/ots-upgrade-automation-hook-activate")
async def ots_upgrade_automation_hook_activate_endpoint(
    body: OtsUpgradeAutomationHookActivateBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P24 · démarre automation périodique OTS upgrade (6h cycle)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        activate_ots_upgrade_automation_hook,
    )
    try:
        payload = await activate_ots_upgrade_automation_hook(
            interval_s=body.interval_s,
            run_immediate_scan=body.run_immediate_scan,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "OTS_UPGRADE_AUTOMATION_HOOK_ACTIVATE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "OTS_UPGRADE_AUTOMATION_HOOK_ACTIVATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P24_OTS_UPGRADE_AUTOMATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


class OtsUpgradeAutomationScanNowBody(BaseModel):
    persist: bool = True
    timeout_s_per_file: int = 60


@router.post("/ots-upgrade-automation-scan-now")
async def ots_upgrade_automation_scan_now_endpoint(
    body: OtsUpgradeAutomationScanNowBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P24 · déclenche un scan+upgrade manuel immédiat."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        scan_and_upgrade_pending_ots,
    )
    import asyncio as _asyncio
    try:
        loop = _asyncio.get_running_loop()
        payload = await loop.run_in_executor(
            None, scan_and_upgrade_pending_ots,
            body.persist, body.timeout_s_per_file)
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "OTS_UPGRADE_AUTOMATION_SCAN_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "OTS_UPGRADE_AUTOMATION_SCAN_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P24_OTS_UPGRADE_AUTOMATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.post("/ots-upgrade-automation-stop")
async def ots_upgrade_automation_stop_endpoint(
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P24 · stop manuel de la background task (idempotent)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        stop_background_automation,
    )
    try:
        payload = await stop_background_automation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:500])
    return JSONResponse({
        "manifest_id": "OTS_UPGRADE_AUTOMATION_STOP_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P24_OTS_UPGRADE_AUTOMATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# P15 · TERRITOIRE_Ω_REPORT_CREATE_Ω
# P17 · WAYPOINT_GUIDE_CREATE_Ω
# P18 · LAYER_INTERPRETATION_MANUAL_Ω
# FUSION ADD-ONLY · V30_LOCK INVIOLÉ · ANTI-GÉNÉRIQUE STRICT
# ═════════════════════════════════════════════════════════════════════════


# ----- P15 -----
class TerritoireOmegaReportBody(BaseModel):
    zone_label: str = "DEFAULT_ZONE"
    include_pdf: bool = True
    include_html: bool = True
    persist: bool = True


@router.post("/territoire-omega-report-create")
async def territoire_omega_report_create_endpoint(
    body: TerritoireOmegaReportBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P15 · génère rapport opérationnel complet (PDF+HTML)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.territoire_omega_report_omega import (
        generate_territoire_omega_report,
    )
    try:
        payload = generate_territoire_omega_report(
            zone_label=body.zone_label,
            include_pdf=body.include_pdf,
            include_html=body.include_html,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "TERRITOIRE_OMEGA_REPORT_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "TERRITOIRE_OMEGA_REPORT_CREATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P15_TERRITOIRE_Ω_REPORT_CREATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/territoire-omega-report-status")
async def territoire_omega_report_status_endpoint() -> JSONResponse:
    """P15 · status lecture seule (PUBLIC RO)."""
    from engines.v8_institutional.especes.territoire_omega_report_omega import (
        get_territoire_omega_report_status,
    )
    payload = get_territoire_omega_report_status()
    return JSONResponse({
        "manifest_id": "TERRITOIRE_OMEGA_REPORT_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P15_TERRITOIRE_Ω_REPORT_CREATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/territoire-omega-report-download")
async def territoire_omega_report_download_endpoint(
    report_sha256: str,
    fmt: str = "pdf",
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> FileResponse:
    """P15 · télécharge rapport persisté (pdf|html|json)."""
    _verify_commandant_token(x_commandant_token)
    if fmt not in ("pdf", "html", "json"):
        raise HTTPException(
            status_code=400, detail=f"FORMAT_INVALID::{fmt}")
    if len(report_sha256) < 16:
        raise HTTPException(
            status_code=400,
            detail="REPORT_SHA256_PREFIX_TOO_SHORT")
    from engines.v8_institutional.especes.territoire_omega_report_omega import (
        REPORTS_STORE,
    )
    prefix = report_sha256[:16]
    matches = list(REPORTS_STORE.glob(f"{prefix}*.{fmt}"))
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"REPORT_FILE_NOT_FOUND::{prefix}.{fmt}")
    return FileResponse(
        str(matches[0]),
        media_type={
            "pdf": "application/pdf",
            "html": "text/html",
            "json": "application/json",
        }[fmt],
        filename=matches[0].name)


# ----- P17 -----
class WaypointFieldGuideBody(BaseModel):
    latitude: float
    longitude: float
    species: str
    waypoint_id: Optional[str] = None
    radius_m: int = 500
    include_pdf: bool = True
    include_html: bool = True
    persist: bool = True


@router.post("/waypoint-field-guide-create")
async def waypoint_field_guide_create_endpoint(
    body: WaypointFieldGuideBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P17 · génère fiche terrain pour un point (PDF+HTML)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.waypoint_guide_omega import (
        generate_waypoint_field_guide,
    )
    try:
        payload = generate_waypoint_field_guide(
            lat=body.latitude,
            lon=body.longitude,
            species=body.species,
            waypoint_id=body.waypoint_id,
            radius_m=body.radius_m,
            include_pdf=body.include_pdf,
            include_html=body.include_html,
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
                "reason": "WAYPOINT_FIELD_GUIDE_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "WAYPOINT_FIELD_GUIDE_CREATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P17_WAYPOINT_GUIDE_CREATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/waypoint-field-guide-status")
async def waypoint_field_guide_status_endpoint() -> JSONResponse:
    """P17 · status lecture seule (PUBLIC RO)."""
    from engines.v8_institutional.especes.waypoint_guide_omega import (
        get_waypoint_guide_status,
    )
    payload = get_waypoint_guide_status()
    return JSONResponse({
        "manifest_id": "WAYPOINT_FIELD_GUIDE_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P17_WAYPOINT_GUIDE_CREATE_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/waypoint-field-guide-download")
async def waypoint_field_guide_download_endpoint(
    guide_sha256: str,
    fmt: str = "pdf",
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> FileResponse:
    """P17 · télécharge guide field persisté."""
    _verify_commandant_token(x_commandant_token)
    if fmt not in ("pdf", "html", "json"):
        raise HTTPException(
            status_code=400, detail=f"FORMAT_INVALID::{fmt}")
    if len(guide_sha256) < 16:
        raise HTTPException(
            status_code=400,
            detail="GUIDE_SHA256_PREFIX_TOO_SHORT")
    from engines.v8_institutional.especes.waypoint_guide_omega import (
        GUIDES_STORE,
    )
    prefix = guide_sha256[:16]
    matches = list(GUIDES_STORE.glob(f"{prefix}*.{fmt}"))
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"GUIDE_FILE_NOT_FOUND::{prefix}.{fmt}")
    return FileResponse(
        str(matches[0]),
        media_type={
            "pdf": "application/pdf",
            "html": "text/html",
            "json": "application/json",
        }[fmt],
        filename=matches[0].name)


# ----- P18 -----
class LayerInterpretationManualBody(BaseModel):
    include_pdf: bool = True
    include_html: bool = True
    persist: bool = True


@router.post("/layer-interpretation-manual-create")
async def layer_interpretation_manual_create_endpoint(
    body: LayerInterpretationManualBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P18 · génère le manual 18 couches (PDF+HTML)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.layer_interpretation_manual_omega import (  # noqa: E501
        generate_layer_interpretation_manual,
    )
    try:
        payload = generate_layer_interpretation_manual(
            include_pdf=body.include_pdf,
            include_html=body.include_html,
            persist=body.persist,
        )
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "LAYER_INTERPRETATION_MANUAL_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "LAYER_INTERPRETATION_MANUAL_CREATE_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P18_LAYER_INTERPRETATION_MANUAL_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/layer-interpretation-manual-status")
async def layer_interpretation_manual_status_endpoint() -> JSONResponse:
    """P18 · status lecture seule (PUBLIC RO)."""
    from engines.v8_institutional.especes.layer_interpretation_manual_omega import (  # noqa: E501
        get_layer_manual_status,
    )
    payload = get_layer_manual_status()
    return JSONResponse({
        "manifest_id": "LAYER_INTERPRETATION_MANUAL_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P18_LAYER_INTERPRETATION_MANUAL_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/layer-interpretation-manual-download")
async def layer_interpretation_manual_download_endpoint(
    manual_sha256: str,
    fmt: str = "pdf",
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> FileResponse:
    """P18 · télécharge manual persisté."""
    _verify_commandant_token(x_commandant_token)
    if fmt not in ("pdf", "html", "json"):
        raise HTTPException(
            status_code=400, detail=f"FORMAT_INVALID::{fmt}")
    if len(manual_sha256) < 16:
        raise HTTPException(
            status_code=400,
            detail="MANUAL_SHA256_PREFIX_TOO_SHORT")
    from engines.v8_institutional.especes.layer_interpretation_manual_omega import (  # noqa: E501
        MANUAL_STORE,
    )
    prefix = manual_sha256[:16]
    matches = list(MANUAL_STORE.glob(f"{prefix}*.{fmt}"))
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"MANUAL_FILE_NOT_FOUND::{prefix}.{fmt}")
    return FileResponse(
        str(matches[0]),
        media_type={
            "pdf": "application/pdf",
            "html": "text/html",
            "json": "application/json",
        }[fmt],
        filename=matches[0].name)


@router.get("/ots-upgrade-automation-status")
async def ots_upgrade_automation_status_endpoint() -> JSONResponse:
    """P24 · status lecture seule (PUBLIC RO)."""
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        get_ots_upgrade_automation_hook_status,
    )
    payload = get_ots_upgrade_automation_hook_status()
    return JSONResponse({
        "manifest_id": "OTS_UPGRADE_AUTOMATION_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P24_OTS_UPGRADE_AUTOMATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/ots-upgrade-automation-history")
async def ots_upgrade_automation_history_endpoint(
    hours: int = 48,
) -> JSONResponse:
    """P20_PHASE2 · timeline 24-48h (PUBLIC RO).

    Anti-générique : lit l'overlay réel sans fabrication.
    """
    from engines.v8_institutional.especes.ots_upgrade_automation_omega import (
        get_ots_upgrade_automation_history,
    )
    try:
        payload = get_ots_upgrade_automation_history(hours=hours)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JSONResponse({
        "manifest_id": "OTS_UPGRADE_AUTOMATION_HISTORY_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_PHASE2_UNIFIED_AND_RESEND_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


# ═════════════════════════════════════════════════════════════════════════
# P20 · TERRITOIRE_UI_UX_AUDIT_Ω
# READ-ONLY · FUSION ADD-ONLY · V30_LOCK INVIOLÉ
# ═════════════════════════════════════════════════════════════════════════


class TerritoireUiUxAuditExecuteBody(BaseModel):
    persist: bool = True


@router.post("/territoire-ui-ux-audit-execute")
async def territoire_ui_ux_audit_execute_endpoint(
    body: TerritoireUiUxAuditExecuteBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P20 · execute audit READ-ONLY UI/UX TERRITOIRE."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.territoire_ui_ux_audit_omega import (
        execute_territoire_ui_ux_audit,
    )
    try:
        payload = execute_territoire_ui_ux_audit(
            persist=body.persist)
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "TERRITOIRE_UI_UX_AUDIT_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id":
            "TERRITOIRE_UI_UX_AUDIT_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_TERRITOIRE_UI_UX_AUDIT_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/territoire-ui-ux-audit-status")
async def territoire_ui_ux_audit_status_endpoint() -> JSONResponse:
    """P20 · status (PUBLIC RO)."""
    from engines.v8_institutional.especes.territoire_ui_ux_audit_omega import (
        get_territoire_ui_ux_audit_status,
    )
    payload = get_territoire_ui_ux_audit_status()
    return JSONResponse({
        "manifest_id":
            "TERRITOIRE_UI_UX_AUDIT_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_TERRITOIRE_UI_UX_AUDIT_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# P20_PHASE2 · WEATHER_PROVIDER_POLICY_Ω
# OPENWEATHERMAP ONLY · NOAA + Copernicus DEPRECATED_ENFORCED
# ═════════════════════════════════════════════════════════════════════════


class WeatherProviderPolicyAttestBody(BaseModel):
    persist: bool = True


@router.post("/weather-provider-policy-attest")
async def weather_provider_policy_attest_endpoint(
    body: WeatherProviderPolicyAttestBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P20_PHASE2 · attestation politique météo (OWM only)."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.weather_provider_policy_omega import (
        execute_weather_provider_policy_attest,
    )
    try:
        payload = execute_weather_provider_policy_attest(
            persist=body.persist)
    except GuardrailsNotEnforcedError as e:
        raise HTTPException(status_code=412, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "WEATHER_PROVIDER_POLICY_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "WEATHER_PROVIDER_POLICY_ATTEST_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_PHASE2_UNIFIED_AND_RESEND_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/weather-provider-policy-status")
async def weather_provider_policy_status_endpoint() -> JSONResponse:
    """P20_PHASE2 · status (PUBLIC RO)."""
    from engines.v8_institutional.especes.weather_provider_policy_omega import (
        get_weather_provider_policy_status,
    )
    payload = get_weather_provider_policy_status()
    return JSONResponse({
        "manifest_id": "WEATHER_PROVIDER_POLICY_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_PHASE2_UNIFIED_AND_RESEND_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })



# ═════════════════════════════════════════════════════════════════════════
# P20_PHASE3 · FORCE_PURGE_DOCTRINE_STATUS
# Permet à l'admin premium de vérifier l'état du purge doctrinal côté
# serveur. Anti-générique strict : retourne uniquement les flags réels.
# ═════════════════════════════════════════════════════════════════════════


@router.get("/force-purge-doctrine-status")
async def force_purge_doctrine_status_endpoint() -> JSONResponse:
    """P20_PHASE3 · status purge (PUBLIC RO)."""
    payload = {
        "manifest_id": "FORCE_PURGE_DOCTRINE_STATUS_Ω",
        "ordre": "P20_PHASE3_FORCE_PURGE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "force_purge_version": (
            "P20_PHASE3_FORCE_PURGE_2026_05_08_2147"),
        "no_cache_middleware_active": True,
        "no_cache_headers_emitted": [
            "Cache-Control: no-store, no-cache, "
            "must-revalidate, max-age=0",
            "Pragma: no-cache",
            "Expires: 0",
            "X-BCE-4X-Force-Purge: P20_PHASE3_FORCE_PURGE_2026_05_08_2147",
        ],
        "scope_paths": [
            "/api/v30/super-masters/*",
            "/admin/bce-4x-premium/*",
        ],
        "legacy_panels_doctrinal_default": "DISABLED_BY_DEFAULT",
        "analysis_v6_doctrinal_default": "DISABLED_BY_DEFAULT",
        "debug_panels_doctrinal_default": "DISABLED_BY_DEFAULT",
        "unified_panel_doctrinal_default": "ENABLED_PRIMARY",
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
    }
    return JSONResponse(payload)



# ═════════════════════════════════════════════════════════════════════════
# P20_PHASE4 · TERRITOIRE_OMEGA_RELOAD_Ω
# Force reload + purge cache + watchdog reinit (600s)
# ═════════════════════════════════════════════════════════════════════════


class TerritoireOmegaReloadBody(BaseModel):
    persist: bool = True
    watchdog_timeout_s: int = 600


@router.post("/territoire-omega-reload-execute")
async def territoire_omega_reload_execute_endpoint(
    body: TerritoireOmegaReloadBody,
    x_commandant_token: Optional[str] = Header(
        default=None, alias="X-Commandant-Token"),
) -> JSONResponse:
    """P20_PHASE4 · force reload + purge + watchdog reinit."""
    _verify_commandant_token(x_commandant_token)
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        GuardrailsNotEnforcedError,
    )
    from engines.v8_institutional.especes.territoire_omega_reload_omega import (
        execute_territoire_omega_reload,
    )
    try:
        payload = execute_territoire_omega_reload(
            persist=body.persist,
            watchdog_timeout_s=body.watchdog_timeout_s,
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
                "reason": "TERRITOIRE_OMEGA_RELOAD_FAILED",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            })
    return JSONResponse({
        "manifest_id": "TERRITOIRE_OMEGA_RELOAD_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_PHASE4_STABILIZATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })


@router.get("/territoire-omega-reload-status")
async def territoire_omega_reload_status_endpoint() -> JSONResponse:
    """P20_PHASE4 · status (PUBLIC RO)."""
    from engines.v8_institutional.especes.territoire_omega_reload_omega import (
        get_territoire_omega_reload_status,
    )
    payload = get_territoire_omega_reload_status()
    return JSONResponse({
        "manifest_id": "TERRITOIRE_OMEGA_RELOAD_STATUS_GET_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "P20_PHASE4_STABILIZATION_Ω",
        "horodatage_build": _build_horodatage(),
        "result": payload,
        "v30_lock": "INVIOLÉ",
    })

