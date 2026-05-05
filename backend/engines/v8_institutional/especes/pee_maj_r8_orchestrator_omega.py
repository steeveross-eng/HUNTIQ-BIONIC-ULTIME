"""
pee_maj_r8_orchestrator_omega.py — ORDRE N°52-R8 · ORCHESTRATEUR COMPLET
════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · OPTION δ (HYBRIDE α+β)

Orchestrateur 8-phases pour le pipeline PEE_MAJ Voie B post-upload B2 :

  PHASE_0  VALIDATIONS        · ✅ RÉEL · s3/status + list-resumable + SHA-256
  PHASE_1  EXTRACTION         · ⚠ STUB_READY · nécessite geopandas/fiona
                                 + dictionnaires MFFP_CODES
  PHASE_2  STRUCTURATION      · ⚠ STUB_READY · harmonisation codes MFFP
  PHASE_3  DÉRIVATION 9 COUCHES · ⚠ STUB_READY · algorithmes BCE-4X
                                   (fragmentation Dickson 2017, classes_age,
                                    densité canopée, etc.)
  PHASE_4  INDEXATION          · ⚠ STUB_READY · RTree + attribute_index
  PHASE_5  VALIDATION          · ⚠ STUB_READY · topologie + stats inter-layers
  PHASE_6  SCEAUX              · ✅ RÉEL · BCE4X+MFFP+SHA256+V30 sur manifest
  PHASE_7  INTÉGRATION         · ✅ RÉEL · persist_derivatives (filesystem)
                                   + flag engine_ready sur slot
  PHASE_8  RAPPORT SYNTHÈSE    · ✅ RÉEL · BIONIC_SYNTHESIS_REPORT.json

Architecture :
  · Background thread (threading.Thread, daemon=True)
  · State file atomique : /app/backend/data/gis_operational/R8_STATE.json
  · Idempotence : un run R8 à la fois (lock via status=RUNNING)
  · ANTI_GÉNÉRIQUE_STRICT : phases STUB_READY marquées explicitement,
    aucune fausse exécution, dépendances listées.
════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pee_maj_r8_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes et chemins
# ═════════════════════════════════════════════════════════════════════════
R8_STATE_PATH = Path(
    "/app/backend/data/gis_operational/R8_STATE.json")
R8_REPORT_DIR = Path(
    "/app/backend/data/gis_operational/r8_reports")
R8_REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Emplacement /var/cache éphémère pour pull B2 (95 Go libres, wipe pod restart)
PEE_MAJ_LOCAL_PULL_DIR = Path(
    "/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω")
PEE_MAJ_LOCAL_PULL_PATH = PEE_MAJ_LOCAL_PULL_DIR / "pee_maj.gpkg"

SLOT_ID = "FORET_MFFP_PEE_MAJ_Ω"
SLOT_MANIFEST_PATH = Path(
    "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")

# Projection cible confirmée par le Commandant
TARGET_EPSG = 32198  # NAD83 / Québec

# Lock filesystem pour empêcher 2 runs concurrents
_R8_LOCK = threading.Lock()


# ═════════════════════════════════════════════════════════════════════════
# Helpers utilitaires
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_state_atomic(state: Dict[str, Any]) -> None:
    """Écriture atomique du state file (rename)."""
    R8_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["last_update_utc"] = _utc_now()
    tmp = R8_STATE_PATH.with_suffix(".partial")
    tmp.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(R8_STATE_PATH))


def read_state() -> Dict[str, Any]:
    """Lit le state file. Retourne {} si absent."""
    if not R8_STATE_PATH.exists():
        return {}
    try:
        return json.loads(R8_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_running() -> bool:
    s = read_state()
    return s.get("status") == "RUNNING"


def _update_phase(state: Dict[str, Any], phase_id: str,
                  phase_status: str, **kwargs) -> None:
    """Met à jour une phase dans le state et persiste."""
    phase = state["phases"][phase_id]
    phase["status"] = phase_status
    phase["last_update_utc"] = _utc_now()
    phase.update(kwargs)
    _write_state_atomic(state)


def _read_slot_manifest() -> Dict[str, Any]:
    if not SLOT_MANIFEST_PATH.exists():
        return {}
    return json.loads(SLOT_MANIFEST_PATH.read_text(encoding="utf-8"))


def _write_slot_manifest(m: Dict[str, Any]) -> None:
    m["last_updated_utc"] = _utc_now()
    tmp = SLOT_MANIFEST_PATH.with_suffix(".partial")
    tmp.write_text(
        json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(SLOT_MANIFEST_PATH))


# ═════════════════════════════════════════════════════════════════════════
# PHASE 0 · VALIDATIONS PRÉ-EXÉCUTION (RÉEL)
# ═════════════════════════════════════════════════════════════════════════
def phase0_validations(state: Dict[str, Any]) -> Dict[str, Any]:
    """Contrôles pré-exécution. Raise si invariants non respectés."""
    p = "PHASE_0_VALIDATIONS"
    _update_phase(state, p, "RUNNING", started_at_utc=_utc_now())
    t0 = time.time()
    results: Dict[str, Any] = {}

    try:
        manifest = _read_slot_manifest()
        slot = manifest.get("slots", {}).get(SLOT_ID, {})
        slot_status = slot.get("status")
        uploads = slot.get("uploads", [])
        pee_maj_upload = next(
            (u for u in uploads if u.get("filename") == "pee_maj.gpkg"
             and u.get("source") == "BACKBLAZE_B2_MULTIPART"),
            None)

        results["slot_status"] = slot_status
        results["uploads_count"] = len(uploads)
        results["pee_maj_upload_present"] = bool(pee_maj_upload)

        if slot_status != "LOADED":
            raise RuntimeError(
                f"PHASE_0_FAIL · slot.status={slot_status} (attendu LOADED)")
        if not pee_maj_upload:
            raise RuntimeError(
                "PHASE_0_FAIL · Aucun upload BACKBLAZE_B2_MULTIPART "
                "pour pee_maj.gpkg dans le manifest slot")

        results["b2_bucket"] = pee_maj_upload["b2_bucket"]
        results["b2_key"] = pee_maj_upload["b2_key"]
        results["b2_upload_id"] = pee_maj_upload["b2_upload_id"]
        results["expected_sha256"] = pee_maj_upload["sha256"]
        results["expected_size_bytes"] = pee_maj_upload["size_bytes"]

        # Vérification live B2 : HEAD object
        from routes.gis_s3_upload_router_omega import _get_b2_client
        s3, bucket = _get_b2_client()
        head = s3.head_object(Bucket=bucket, Key=pee_maj_upload["b2_key"])
        b2_live_size = head["ContentLength"]
        b2_etag = head["ETag"].strip('"')
        results["b2_live_size_bytes"] = b2_live_size
        results["b2_live_etag"] = b2_etag
        if b2_live_size != pee_maj_upload["size_bytes"]:
            raise RuntimeError(
                f"PHASE_0_FAIL · B2 live size {b2_live_size} != "
                f"manifest {pee_maj_upload['size_bytes']}")
        # ETag format multipart : "<md5>-<N>" où N = parts_count
        if "-" in b2_etag:
            parts_count = int(b2_etag.split("-")[-1])
            results["b2_parts_count"] = parts_count

        # Vérifier qu'aucune session resumable active n'existe
        from routes.gis_s3_upload_router_omega import S3_SESSIONS_DIR
        active_resumable = 0
        if S3_SESSIONS_DIR.exists():
            for sf in S3_SESSIONS_DIR.glob("*.json"):
                try:
                    s = json.loads(sf.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if (s.get("slot_id") == SLOT_ID and
                        s.get("status") == "UPLOADING"):
                    active_resumable += 1
        results["active_resumable_sessions"] = active_resumable
        if active_resumable > 0:
            raise RuntimeError(
                f"PHASE_0_FAIL · {active_resumable} session(s) "
                "UPLOADING active(s). Appeler /s3/cleanup-orphans avant R8.")

        results["elapsed_s"] = round(time.time() - t0, 2)
        _update_phase(state, p, "OK",
                      completed_at_utc=_utc_now(),
                      results=results)
        logger.info("R8_PHASE_0_OK elapsed=%ss results=%s",
                    results["elapsed_s"], results)
        return results
    except Exception as e:
        results["elapsed_s"] = round(time.time() - t0, 2)
        results["error"] = str(e)[:500]
        results["traceback"] = traceback.format_exc()[-1000:]
        _update_phase(state, p, "FAILED",
                      completed_at_utc=_utc_now(),
                      results=results)
        raise


# ═════════════════════════════════════════════════════════════════════════
# PHASE 1 · EXTRACTION (PULL B2 + STUB GIS) — RÉEL POUR LE PULL
# ═════════════════════════════════════════════════════════════════════════
def phase1_pull_b2_and_stub_extraction(state: Dict[str, Any],
                                        do_pull: bool = False) -> Dict[str, Any]:
    """Partie RÉELLE (optionnelle) : pull B2 → /var/cache (streaming SHA-256 live).
    Partie STUB_READY : extraction tables/géométries/attributs (requiert
    geopandas/fiona + dictionnaires MFFP_CODES non encore fournis).

    ORDRE N°52-R8 · Pull désactivé par défaut suite aux pod restarts
    observés pendant le pull de 37 Go. Source de vérité durable = B2.
    Réactivable via query param `?do_pull=true` au POST /r8-execute.
    """
    p = "PHASE_1_EXTRACTION"
    _update_phase(state, p, "RUNNING", started_at_utc=_utc_now())
    t0 = time.time()
    results: Dict[str, Any] = {}
    p0 = state["phases"]["PHASE_0_VALIDATIONS"]["results"]

    try:
        results["do_pull_requested"] = do_pull
        results["local_pull_path_planned"] = str(PEE_MAJ_LOCAL_PULL_PATH)
        results["ephemeral_storage_warning"] = (
            "/var/cache est éphémère (wipe pod restart). Pod restarts "
            "observés pendant le pull de 37 Go. Source de vérité "
            f"durable = Backblaze B2 bucket={p0['b2_bucket']} "
            f"key={p0['b2_key']} sha256={p0['expected_sha256']}.")

        if not do_pull:
            results["pull_performed"] = False
            results["pull_skip_reason"] = (
                "Pull désactivé par défaut : phases 1-5 en STUB_READY "
                "(spécifications métier non fournies). Le pull sera "
                "réactivable via ?do_pull=true quand les modules GIS "
                "(geopandas/fiona/rasterio) seront installés et les "
                "algorithmes BCE-4X spécifiés.")
            results["pull_skipped_to_prevent_waste"] = True
        else:
            # Pull B2 → /var/cache (éphémère)
            PEE_MAJ_LOCAL_PULL_DIR.mkdir(parents=True, exist_ok=True)
            # Skip si fichier déjà présent ET taille+sha correctes (idempotent)
            skip_pull = False
            if PEE_MAJ_LOCAL_PULL_PATH.exists():
                local_size = PEE_MAJ_LOCAL_PULL_PATH.stat().st_size
                if local_size == p0["expected_size_bytes"]:
                    h = hashlib.sha256()
                    with open(PEE_MAJ_LOCAL_PULL_PATH, "rb") as fh:
                        while True:
                            blk = fh.read(8 << 20)
                            if not blk:
                                break
                            h.update(blk)
                    local_sha = h.hexdigest()
                    if local_sha == p0["expected_sha256"]:
                        skip_pull = True
                        results["pull_skipped_idempotent"] = True
                        results["local_sha256"] = local_sha
                        results["local_size_bytes"] = local_size
                        results["pull_elapsed_s"] = 0.0
                        logger.info(
                            "R8_PHASE_1_PULL_SKIP idempotent local=%s sha=%s",
                            PEE_MAJ_LOCAL_PULL_PATH, local_sha)
            if not skip_pull:
                from routes.gis_s3_upload_router_omega import _get_b2_client
                s3, bucket = _get_b2_client()
                logger.info(
                    "R8_PHASE_1_PULL_START b2_key=%s expected_size=%d",
                    p0["b2_key"], p0["expected_size_bytes"])
                obj = s3.get_object(Bucket=bucket, Key=p0["b2_key"])
                h = hashlib.sha256()
                bytes_streamed = 0
                pull_t0 = time.time()
                tmp = PEE_MAJ_LOCAL_PULL_PATH.with_suffix(".pulling.partial")
                with open(tmp, "wb") as out:
                    body = obj["Body"]
                    try:
                        while True:
                            blk = body.read(8 << 20)
                            if not blk:
                                break
                            out.write(blk)
                            h.update(blk)
                            bytes_streamed += len(blk)
                            if bytes_streamed % (500 << 20) < (8 << 20):
                                pct = round(
                                    bytes_streamed / p0["expected_size_bytes"]
                                    * 100, 1)
                                _update_phase(
                                    state, p, "RUNNING",
                                    pull_progress_pct=pct,
                                    pull_bytes=bytes_streamed)
                    finally:
                        try:
                            body.close()
                        except Exception:
                            pass
                os.replace(str(tmp), str(PEE_MAJ_LOCAL_PULL_PATH))
                local_sha = h.hexdigest()
                pull_elapsed = round(time.time() - pull_t0, 2)
                results["pull_performed"] = True
                results["pull_skipped_idempotent"] = False
                results["pull_elapsed_s"] = pull_elapsed
                results["local_sha256"] = local_sha
                results["local_size_bytes"] = bytes_streamed
                if local_sha != p0["expected_sha256"]:
                    raise RuntimeError(
                        f"PHASE_1_PULL_SHA_MISMATCH local={local_sha} "
                        f"expected={p0['expected_sha256']}")
                logger.info(
                    "R8_PHASE_1_PULL_DONE elapsed=%ss bytes=%d sha=%s",
                    pull_elapsed, bytes_streamed, local_sha)

        # ─── Partie STUB_READY : extraction GIS (non implémentée) ────
        results["extraction_stub_ready"] = True
        results["extraction_status"] = "STUB_READY_ANTI_GENERIC_BLOCK"
        results["extraction_dependencies_required"] = [
            "Module Python : geopandas >= 0.14",
            "Module Python : fiona >= 1.9 ou pyogrio >= 0.8",
            "Module Python : pyproj >= 3.6 (pour reprojection EPSG:32198)",
            "Module Python : shapely >= 2.0",
            "DICTIONNAIRES MFFP_CODES non encore fournis par Commandant :",
            "  · codes_essences.json (ERS=érable à sucre, BOP=bouleau à papier, …)",
            "  · classes_age.json (bornes 0-10, 10-30, 30-50, 50-70, 70+)",
            "  · types_couvert.json (FE, FR, FM, RE, RN, …)",
            "  · types_ecologique.json (FE32, RS28, MS22, …)",
            "SPECIFICATION : subset 100 Mo pour validation algorithmique",
        ]
        results["target_epsg"] = TARGET_EPSG
        results["target_epsg_description"] = "NAD83 / Québec Lambert"
        results["elapsed_s"] = round(time.time() - t0, 2)
        _update_phase(state, p, "STUB_READY",
                      completed_at_utc=_utc_now(),
                      results=results)
        return results
    except Exception as e:
        results["elapsed_s"] = round(time.time() - t0, 2)
        results["error"] = str(e)[:500]
        results["traceback"] = traceback.format_exc()[-1000:]
        _update_phase(state, p, "FAILED",
                      completed_at_utc=_utc_now(),
                      results=results)
        raise


# ═════════════════════════════════════════════════════════════════════════
# PHASES 2-5 · STUB_READY (ANTI_GÉNÉRIQUE_STRICT — aucune simulation)
# ═════════════════════════════════════════════════════════════════════════
def _make_stub_phase(phase_id: str, dependencies: List[str],
                     output_artifacts: List[str]) -> Any:
    """Factory pour les phases STUB_READY documentées."""
    def _stub_phase(state: Dict[str, Any]) -> Dict[str, Any]:
        _update_phase(state, phase_id, "RUNNING",
                       started_at_utc=_utc_now())
        t0 = time.time()
        results = {
            "status": "STUB_READY_ANTI_GENERIC_BLOCK",
            "dependencies_required": dependencies,
            "output_artifacts_planned": output_artifacts,
            "anti_generique_note": (
                "Phase NON exécutée · simulation formellement interdite. "
                "Dépendances non satisfaites listées ci-dessus. Fournir "
                "spécifications + algorithmes pour débloquer."),
            "elapsed_s": round(time.time() - t0, 2),
        }
        _update_phase(state, phase_id, "STUB_READY",
                       completed_at_utc=_utc_now(),
                       results=results)
        return results
    return _stub_phase


phase2_structuration = _make_stub_phase(
    "PHASE_2_STRUCTURATION",
    [
        "Dictionnaire HARMONIZE_MFFP_CODES (Commandant à fournir)",
        "Règles FIX_INVALID_GEOMETRIES (shapely.make_valid + buffer(0))",
        "Règles VALIDATE_TOPOLOGY_STRICT (overlaps, gaps, orphans)",
        "Sortie : MFFP_STRUCTURAL_MATRIX.parquet + MFFP_FOREST_TYPE_MATRIX.parquet",
    ],
    [
        "MFFP_STRUCTURAL_MATRIX.parquet",
        "MFFP_FOREST_TYPE_MATRIX.parquet",
    ],
)


phase3_derivation = _make_stub_phase(
    "PHASE_3_DERIVATION_9_COUCHES",
    [
        "Algorithme GIS_STRUCTURE_FORESTIERE (classification couvert/densité)",
        "Algorithme GIS_ESSENCES_DOMINANTES (mode spatial par polygone)",
        "Algorithme GIS_CLASSES_AGE (bins MFFP 0-10,10-30,30-50,50-70,70+)",
        "Algorithme GIS_DENSITE_COUVERT (% canopée rasterisée 100m × 100m)",
        "Algorithme GIS_FRAGMENTATION (Dickson 2017 — fenêtre glissante 250m)",
        "Algorithme GIS_PRODUCTIVITE (indices MFFP classe_age × essence)",
        "Algorithme GIS_HABITAT_BRUT (scoring multi-critères 5 espèces)",
        "Algorithme GIS_STRESS_ANTHROPIQUE_BRUT (distance routes/urbain)",
        "Algorithme GIS_ZONAGE_ECOLOGIQUE_BRUT (clustering écorégions)",
        "Module : rasterio (rasterisation vecteur → GeoTIFF EPSG:32198)",
        "Module : scipy.ndimage (fenêtres glissantes fragmentation)",
        "Module : numpy (calculs matriciels)",
    ],
    [
        "GIS_STRUCTURE_FORESTIERE.tif (raster EPSG:32198, 100m)",
        "GIS_ESSENCES_DOMINANTES.tif (raster catégoriel 100m)",
        "GIS_CLASSES_AGE.tif (raster 250m, 5 classes)",
        "GIS_COUVERT_FORESTIER_DENSITY.tif (raster 100m, 0-100%)",
        "GIS_FRAGMENTATION_INDEX.tif (raster 250m, 0-1 Dickson)",
        "GIS_PRODUCTIVITE.tif (raster 100m, indice MFFP)",
        "GIS_HABITAT_BRUT.tif (raster 250m multi-bandes 5 espèces)",
        "GIS_STRESS_ANTHROPIQUE_BRUT.tif (raster 100m, distance pondérée)",
        "GIS_ZONAGE_ECOLOGIQUE_BRUT.geojson (polygones écorégions)",
    ],
)


phase4_indexation = _make_stub_phase(
    "PHASE_4_INDEXATION",
    [
        "Module : rtree >= 1.0 (index spatial R-tree)",
        "Module : pandas >= 2.0 (attribute index)",
        "Module : pyarrow (colonnar parquet)",
        "Spécification clés d'index attribut (essence, classe_age, densité, …)",
    ],
    [
        "pee_maj_rtree.idx + pee_maj_rtree.dat (spatial)",
        "pee_maj_attr_index.parquet (attr)",
        "pee_maj_corridor_ready.parquet (pré-filtré pour corridors)",
        "pee_maj_behavior_ready.parquet (pré-filtré pour comportement faune)",
    ],
)


phase5_validation = _make_stub_phase(
    "PHASE_5_VALIDATION",
    [
        "Algorithmes VALIDATE_GEOMETRY (is_valid + closure + orientation)",
        "Algorithmes VALIDATE_ATTRIBUTES (schema + ranges + NA rates)",
        "Algorithmes VALIDATE_INTER_LAYERS (cross-layer topology consistency)",
        "Spécifications VALIDATE_STATISTICS (distributions attendues par écorégion)",
    ],
    [
        "pee_maj_validation_report.json (anomalies + métriques)",
        "pee_maj_stats_per_ecoregion.json",
    ],
)


# ═════════════════════════════════════════════════════════════════════════
# PHASE 6 · SCEAUX INSTITUTIONNELS (RÉEL)
# ═════════════════════════════════════════════════════════════════════════
def phase6_seals(state: Dict[str, Any]) -> Dict[str, Any]:
    """Appose les sceaux BCE4X + MFFP + SHA256 + V30 sur le manifest."""
    p = "PHASE_6_SCEAU"
    _update_phase(state, p, "RUNNING", started_at_utc=_utc_now())
    t0 = time.time()
    results: Dict[str, Any] = {}

    try:
        p0 = state["phases"]["PHASE_0_VALIDATIONS"]["results"]
        manifest = _read_slot_manifest()
        slot = manifest.get("slots", {}).get(SLOT_ID, {})

        seal_payload = {
            "slot_id": SLOT_ID,
            "expected_sha256": p0["expected_sha256"],
            "expected_size_bytes": p0["expected_size_bytes"],
            "b2_bucket": p0["b2_bucket"],
            "b2_key": p0["b2_key"],
            "sealed_at_utc": _utc_now(),
        }
        payload_bytes = json.dumps(
            seal_payload, sort_keys=True, ensure_ascii=False
        ).encode("utf-8")
        seal_sha256 = hashlib.sha256(payload_bytes).hexdigest()

        seals = {
            "BCE4X": {
                "protocol": "BCE-4X_ULTIME_ABSOLU",
                "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
                "authority": "COMMANDANT_STEEVE_MAX",
                "version": "x3",
            },
            "MFFP": {
                "organisme": "MFFP — Direction des inventaires forestiers",
                "dataset": "PEE_MAJ",
                "format_source": "gpkg_monolithique",
            },
            "SHA256": {
                "object_sha256": p0["expected_sha256"],
                "composite_sha256": slot.get("composite_sha256"),
                "seal_sha256": seal_sha256,
            },
            "V30": {
                "lock": "INVIOLÉ",
                "freeze_master": "LOCKED",
                "doctrine_version": "V30",
            },
        }
        results["seals"] = seals

        # Persister les sceaux dans le slot manifest
        slot["r8_seals"] = seals
        slot["r8_sealed_at_utc"] = _utc_now()
        _write_slot_manifest(manifest)

        results["elapsed_s"] = round(time.time() - t0, 2)
        _update_phase(state, p, "OK",
                      completed_at_utc=_utc_now(),
                      results=results)
        logger.info("R8_PHASE_6_SEALS_OK seal_sha256=%s", seal_sha256)
        return results
    except Exception as e:
        results["elapsed_s"] = round(time.time() - t0, 2)
        results["error"] = str(e)[:500]
        results["traceback"] = traceback.format_exc()[-1000:]
        _update_phase(state, p, "FAILED",
                      completed_at_utc=_utc_now(),
                      results=results)
        raise


# ═════════════════════════════════════════════════════════════════════════
# PHASE 7 · INTÉGRATION (RÉEL · flag engine_ready)
# ═════════════════════════════════════════════════════════════════════════
def phase7_integration(state: Dict[str, Any]) -> Dict[str, Any]:
    """Active le slot pour les moteurs dépendants + persistance dérivées
    déjà présentes dans /data/gis/ (si applicable)."""
    p = "PHASE_7_INTEGRATION"
    _update_phase(state, p, "RUNNING", started_at_utc=_utc_now())
    t0 = time.time()
    results: Dict[str, Any] = {}

    try:
        # Réutiliser la persistance filesystem existante (FUSION ADD-ONLY)
        try:
            from engines.v8_institutional.especes.engine_corridors_gis_omega \
                import persist_derivatives_to_archive
            persist_result = persist_derivatives_to_archive()
            results["persist_derivatives"] = {
                "persisted_count": persist_result.get("persisted_count"),
                "skipped_count": persist_result.get("skipped_count"),
                "failed_count": persist_result.get("failed_count"),
                "persistent_root": persist_result.get("persistent_root"),
            }
        except Exception as e:
            results["persist_derivatives"] = {"error": str(e)[:200]}

        # Activation flag slot.r8_engine_ready
        manifest = _read_slot_manifest()
        slot = manifest.get("slots", {}).get(SLOT_ID, {})
        slot["r8_engine_ready"] = True
        slot["r8_activated_at_utc"] = _utc_now()
        slot["r8_local_pull_path"] = str(PEE_MAJ_LOCAL_PULL_PATH)
        slot["r8_local_pull_is_ephemeral"] = True
        slot["r8_local_pull_path_note"] = (
            "Stockage /var/cache éphémère. Source durable = B2.")
        _write_slot_manifest(manifest)

        results["slot_r8_engine_ready"] = True
        results["dependent_engines"] = [
            "engine_corridors_gis_omega (ORDRE N°40)",
            "engine_habitat_omega (ORDRE N°53 à venir)",
            "bio_profile_omega_135 (ORDRE N°53 à venir)",
        ]
        results["elapsed_s"] = round(time.time() - t0, 2)
        _update_phase(state, p, "OK",
                      completed_at_utc=_utc_now(),
                      results=results)
        logger.info("R8_PHASE_7_INTEGRATION_OK")
        return results
    except Exception as e:
        results["elapsed_s"] = round(time.time() - t0, 2)
        results["error"] = str(e)[:500]
        results["traceback"] = traceback.format_exc()[-1000:]
        _update_phase(state, p, "FAILED",
                      completed_at_utc=_utc_now(),
                      results=results)
        raise


# ═════════════════════════════════════════════════════════════════════════
# PHASE 8 · RAPPORT SYNTHÈSE BIONIQUE (RÉEL)
# ═════════════════════════════════════════════════════════════════════════
def phase8_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """Génère BIONIC_SYNTHESIS_REPORT.json consolidant toutes les phases."""
    p = "PHASE_8_RAPPORT"
    _update_phase(state, p, "RUNNING", started_at_utc=_utc_now())
    t0 = time.time()
    results: Dict[str, Any] = {}

    try:
        run_id = state["run_id"]
        report = {
            "manifest_id": "BIONIC_SYNTHESIS_REPORT_R8_Ω",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "ordre": "N°52-R8",
            "option": "δ_HYBRIDE_α_β",
            "slot_id": SLOT_ID,
            "run_id": run_id,
            "started_at_utc": state["started_at_utc"],
            "generated_at_utc": _utc_now(),
            "phases_summary": {
                phase_id: {
                    "status": phase["status"],
                    "elapsed_s": (phase.get("results", {}) or {}).get("elapsed_s"),
                    "results_preview": {
                        k: v for k, v in (phase.get("results") or {}).items()
                        if k not in ("traceback", "extraction_dependencies_required",
                                     "dependencies_required",
                                     "output_artifacts_planned")
                    },
                }
                for phase_id, phase in state["phases"].items()
            },
            "phases_stub_ready": [
                phase_id for phase_id, phase in state["phases"].items()
                if phase["status"] == "STUB_READY"
            ],
            "phases_executed_real": [
                phase_id for phase_id, phase in state["phases"].items()
                if phase["status"] == "OK"
            ],
            "phases_failed": [
                phase_id for phase_id, phase in state["phases"].items()
                if phase["status"] == "FAILED"
            ],
            "target_epsg": TARGET_EPSG,
            "ephemeral_storage_notes": {
                "local_pull_path": str(PEE_MAJ_LOCAL_PULL_PATH),
                "storage_layer": "/var/cache (éphémère · wipe pod restart)",
                "durable_source_of_truth": {
                    "b2_bucket": state["phases"].get(
                        "PHASE_0_VALIDATIONS", {}).get("results", {}).get(
                            "b2_bucket"),
                    "b2_key": state["phases"].get(
                        "PHASE_0_VALIDATIONS", {}).get("results", {}).get(
                            "b2_key"),
                    "b2_sha256": state["phases"].get(
                        "PHASE_0_VALIDATIONS", {}).get("results", {}).get(
                            "expected_sha256"),
                },
                "durable_archive_prereq_future": (
                    "Pour archiver pee_maj.gpkg durablement localement, "
                    "prévoir ≥40 Go libres sur /app ext4 (actuellement "
                    "insuffisant). Alternative : compression zstd ciblée "
                    "sur les dérivés calculés (phase 3 future)."),
            },
            "next_steps_to_unlock_phases_1_to_5": [
                "Fournir dictionnaires MFFP_CODES (essences/classes_age/"
                "types_couvert/types_ecologique)",
                "Fournir spécifications algorithmiques BCE-4X par couche",
                "Fournir subset 100 Mo pour validation algorithmique",
                "Installer modules GIS : geopandas, fiona, pyogrio, "
                "rasterio, rtree, pyproj, shapely",
                "Intégrer modules AMPLIFICATEURS : LiDAR, GEM, carte 2D/3D "
                "(phases ultérieures)",
            ],
            "v30_lock": "INVIOLÉ",
        }

        report_path = R8_REPORT_DIR / f"BIONIC_SYNTHESIS_REPORT_{run_id}.json"
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8")

        results["report_path"] = str(report_path)
        results["report_size_bytes"] = report_path.stat().st_size
        results["phases_executed_real_count"] = len(
            report["phases_executed_real"])
        results["phases_stub_ready_count"] = len(report["phases_stub_ready"])
        results["phases_failed_count"] = len(report["phases_failed"])
        results["elapsed_s"] = round(time.time() - t0, 2)
        _update_phase(state, p, "OK",
                      completed_at_utc=_utc_now(),
                      results=results,
                      report=report)
        logger.info("R8_PHASE_8_REPORT_OK path=%s", report_path)
        return results
    except Exception as e:
        results["elapsed_s"] = round(time.time() - t0, 2)
        results["error"] = str(e)[:500]
        results["traceback"] = traceback.format_exc()[-1000:]
        _update_phase(state, p, "FAILED",
                      completed_at_utc=_utc_now(),
                      results=results)
        raise


# ═════════════════════════════════════════════════════════════════════════
# ORCHESTRATEUR PRINCIPAL
# ═════════════════════════════════════════════════════════════════════════
def _run_all_phases(run_id: str, do_pull: bool = False) -> None:
    """Thread background : enchaîne les 8 phases. Écrit le state à chaque étape."""
    state = read_state()
    try:
        try:
            phase0_validations(state)
        except Exception:
            logger.exception("R8 · PHASE_0 a levé — pipeline interrompu")
            state["status"] = "FAILED"
            state["global_error"] = "PHASE_0_FAILED"
            _write_state_atomic(state)
            return

        # Phase 1 (pull B2 optionnel + stub extraction)
        try:
            phase1_pull_b2_and_stub_extraction(state, do_pull=do_pull)
        except Exception:
            logger.exception("R8 · PHASE_1 a levé — arrêt")
            state["status"] = "FAILED"
            state["global_error"] = "PHASE_1_FAILED"
            _write_state_atomic(state)
            return

        # Phases 2-5 : STUB_READY (rapides)
        phase2_structuration(state)
        phase3_derivation(state)
        phase4_indexation(state)
        phase5_validation(state)

        # Phases 6-8 : RÉEL
        try:
            phase6_seals(state)
            phase7_integration(state)
            phase8_report(state)
            state["status"] = "OK_WITH_STUBS"
        except Exception:
            logger.exception("R8 · phases finales ont levé")
            state["status"] = "FAILED"
            state["global_error"] = "FINAL_PHASES_FAILED"

        state["completed_at_utc"] = _utc_now()
        state["total_elapsed_s"] = round(
            time.time()
            - datetime.fromisoformat(
                state["started_at_utc"]).timestamp(), 2)
        _write_state_atomic(state)
        logger.info("R8_ALL_PHASES_DONE run_id=%s status=%s",
                    run_id, state["status"])
    finally:
        try:
            _R8_LOCK.release()
        except RuntimeError:
            pass


def start_r8_background(force: bool = False,
                         do_pull: bool = False) -> Dict[str, Any]:
    """Démarre un run R8 en background. Idempotent : si déjà RUNNING, refuse.

    ORDRE N°52-R8 DURCISSEMENT · Détection automatique des zombies :
    si le state file indique `RUNNING` mais le `last_update_utc` date
    de plus de 2 min (pod restart probable), le run est considéré zombie
    et un nouveau est autorisé.
    """
    current = read_state()
    # Détection zombie : RUNNING + last_update > 120s
    is_zombie = False
    if current.get("status") == "RUNNING":
        try:
            last = datetime.fromisoformat(
                current.get("last_update_utc", ""))
            age_s = (datetime.now(timezone.utc) - last).total_seconds()
            if age_s > 120:
                is_zombie = True
                logger.warning(
                    "R8_ZOMBIE_DETECTED run_id=%s age=%.0fs (pod restart)",
                    current.get("run_id"), age_s)
        except Exception:
            is_zombie = True

    if is_zombie:
        # Libérer le lock s'il est acquis par le thread mort
        try:
            _R8_LOCK.release()
        except RuntimeError:
            pass  # pas acquis
        # Marquer l'ancien run ZOMBIE_POD_RESTART
        current["status"] = "ZOMBIE_POD_RESTART"
        current["zombified_at_utc"] = _utc_now()
        current["zombie_reason"] = (
            "Pod restart détecté (last_update > 120s sans changement). "
            "Le thread background a été tué. /var/cache probablement wipe.")
        _write_state_atomic(current)

    if not _R8_LOCK.acquire(blocking=False):
        return {
            "ok": False, "reason": "ALREADY_RUNNING",
            "current_state": read_state(),
        }
    current = read_state()
    if current.get("status") == "RUNNING" and not force:
        _R8_LOCK.release()
        return {
            "ok": False, "reason": "ALREADY_RUNNING",
            "current_state": current,
        }

    run_id = f"R8_{int(time.time())}_{os.urandom(3).hex()}"
    state = {
        "run_id": run_id,
        "status": "RUNNING",
        "started_at_utc": _utc_now(),
        "last_update_utc": _utc_now(),
        "ordre": "N°52-R8",
        "option": "δ_HYBRIDE_α_β",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "slot_id": SLOT_ID,
        "previous_run_was_zombie": is_zombie,
        "phases": {
            "PHASE_0_VALIDATIONS": {"status": "PENDING"},
            "PHASE_1_EXTRACTION": {"status": "PENDING"},
            "PHASE_2_STRUCTURATION": {"status": "PENDING"},
            "PHASE_3_DERIVATION_9_COUCHES": {"status": "PENDING"},
            "PHASE_4_INDEXATION": {"status": "PENDING"},
            "PHASE_5_VALIDATION": {"status": "PENDING"},
            "PHASE_6_SCEAU": {"status": "PENDING"},
            "PHASE_7_INTEGRATION": {"status": "PENDING"},
            "PHASE_8_RAPPORT": {"status": "PENDING"},
        },
    }
    _write_state_atomic(state)

    t = threading.Thread(
        target=_run_all_phases, args=(run_id, do_pull),
        name=f"R8-{run_id}", daemon=True)
    t.start()
    return {
        "ok": True,
        "run_id": run_id,
        "status": "RUNNING",
        "state_path": str(R8_STATE_PATH),
        "started_at_utc": state["started_at_utc"],
        "previous_run_was_zombie": is_zombie,
        "do_pull": do_pull,
    }


__all__ = [
    "start_r8_background",
    "read_state",
    "R8_STATE_PATH",
    "PEE_MAJ_LOCAL_PULL_PATH",
]
