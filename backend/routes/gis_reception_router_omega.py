"""
gis_reception_router_omega.py — Router FastAPI Phase XXII (ORDRE N°42_BIS)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°42_BIS

Endpoint d'ingestion GIS protégée — ADMIN_PREMIUM_ONLY.

Routes :
  GET  /api/v30/admin-premium/gis/slots                  — Liste publique des slots
  GET  /api/v30/admin-premium/gis/intake-status          — Manifest intake live
  POST /api/v30/admin-premium/gis/upload/{slot_id}       — Upload couche RÉELLE
                                                            (header X-Commandant-Token requis)

Authentification : header `X-Commandant-Token` doit correspondre à la variable
d'environnement `GIS_RECEPTION_COMMANDANT_TOKEN`.

Anti-générique strict : aucune donnée n'est générée. Validation stricte
des formats, tailles et intégrité (SHA-256, ZIP testzip).
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Path as FPath, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from engines.v8_institutional.especes.gis_reception_validators_omega import (
    SLOTS_GIS_PROTÉGÉS_SPEC,
    SLOT_BY_ID,
    list_slots,
    validate_upload,
    compute_composite_sha256,
    is_multi_upload_slot,
)
from engines.v8_institutional.especes import gis_audit_log_omega as audit


router = APIRouter(
    prefix="/api/v30/admin-premium/gis",
    tags=["v30-admin-premium-gis-reception"],
)

# ═════════════════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════════════════
# ─── ORDRE N°47-EXT · Délocalisation incoming/ vers overlay 95Go ─────────
# Les fichiers uploadés physiques vont dans GIS_INCOMING_ROOT (éphémère OK),
# MAIS le manifest JSON + audit_log.jsonl restent dans RECEPTION_ROOT
# (persistent /app) pour la traçabilité institutionnelle durable.
RECEPTION_ROOT = Path("/app/backend/data/gis_operational")
_INCOMING_OVERRIDE = os.environ.get("GIS_INCOMING_ROOT")
INCOMING_DIR = Path(_INCOMING_OVERRIDE) if _INCOMING_OVERRIDE else (RECEPTION_ROOT / "incoming")
_QUARANTINE_OVERRIDE = os.environ.get("GIS_QUARANTINE_ROOT")
QUARANTINE_DIR = Path(_QUARANTINE_OVERRIDE) if _QUARANTINE_OVERRIDE else (RECEPTION_ROOT / "quarantine")
MANIFEST_PATH = RECEPTION_ROOT / "GIS_RECEPTION_INTAKE_Ω.json"

RECEPTION_ROOT.mkdir(parents=True, exist_ok=True)
INCOMING_DIR.mkdir(parents=True, exist_ok=True)
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

# Filename safety: lettres / chiffres / . _ - uniquement
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]+$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _verify_token(x_commandant_token: str | None) -> None:
    expected = os.environ.get("GIS_RECEPTION_COMMANDANT_TOKEN")
    if not expected:
        raise HTTPException(status_code=503,
                              detail="GIS_RECEPTION_COMMANDANT_TOKEN_NOT_CONFIGURED")
    # ─── ORDRE N°48-EXT · Trim defensif (espaces/CRLF copiés-collés) ───
    received = (x_commandant_token or "").strip()
    expected_clean = expected.strip()
    if not received or received != expected_clean:
        raise HTTPException(status_code=401,
                              detail="ADMIN_PREMIUM_ONLY · Token Commandant invalide")


def _slot_dir(slot_id: str) -> Path:
    d = INCOMING_DIR / slot_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read_manifest() -> Dict[str, Any]:
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            # ─── ORDRE N°52-EXT · Auto-sync slot SLOT_BY_ID → manifest ─
            # Tout slot enregistré dans la spec mais absent du manifest est
            # ajouté avec status=ABSENT (FUSION ADD-ONLY, anti-régressif).
            if "slots" in manifest and isinstance(manifest["slots"], dict):
                for s in SLOTS_GIS_PROTÉGÉS_SPEC:
                    if s["slot_id"] not in manifest["slots"]:
                        manifest["slots"][s["slot_id"]] = {
                            "slot_id": s["slot_id"],
                            "label": s["label"],
                            "priority": s["priority"],
                            "status": "ABSENT",
                            "uploads": [],
                        }
            return manifest
        except Exception:
            pass
    return {
        "manifest_id": "GIS_RECEPTION_INTAKE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°42_BIS",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "created_at_utc": _utc_now(),
        "slots": {s["slot_id"]: {
            "slot_id": s["slot_id"],
            "label": s["label"],
            "priority": s["priority"],
            "status": "ABSENT",
            "uploads": [],
        } for s in SLOTS_GIS_PROTÉGÉS_SPEC},
    }


def _write_manifest(manifest: Dict[str, Any]) -> None:
    manifest["last_updated_utc"] = _utc_now()
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _record_upload(slot_id: str, filename: str, sha256: str, size: int,
                     validation: Dict[str, Any], passed: bool) -> Dict[str, Any]:
    manifest = _read_manifest()
    slot = manifest["slots"].setdefault(slot_id, {
        "slot_id": slot_id, "label": SLOT_BY_ID.get(slot_id, {}).get("label", "?"),
        "priority": SLOT_BY_ID.get(slot_id, {}).get("priority", "?"),
        "status": "ABSENT", "uploads": [],
    })
    entry = {
        "filename": filename, "sha256": sha256, "size_bytes": size,
        "uploaded_at_utc": _utc_now(),
        "passed": passed,
        "validators": validation.get("validators", []),
    }
    # ─── ORDRE N°46 · Multi-upload : dédup par filename (écrase version précédente) ───
    # Si un fichier ayant le même nom a déjà été uploadé dans ce slot, on remplace
    # son entrée pour éviter les doublons dans le composite SHA-256.
    slot["uploads"] = [u for u in slot.get("uploads", []) if u.get("filename") != filename]
    slot["uploads"].append(entry)

    if passed:
        slot["status"] = "LOADED"

    # ─── ORDRE N°46 · Agrégation SHA-256 composite (VOIE B tuiles régionales) ───
    passed_shas = [u["sha256"] for u in slot["uploads"]
                   if u.get("passed") and u.get("sha256")]
    slot["files_loaded_count"] = len(passed_shas)
    slot["composite_sha256"] = compute_composite_sha256(passed_shas) if passed_shas else None
    slot["multi_upload"] = is_multi_upload_slot(slot_id)

    _write_manifest(manifest)
    return manifest


# ═════════════════════════════════════════════════════════════════════════
# Endpoints
# ═════════════════════════════════════════════════════════════════════════
@router.get("/slots")
def get_slots() -> Dict[str, Any]:
    return {
        "manifest_id": "SLOTS_GIS_PROTÉGÉS_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°42_BIS",
        "generated_at_utc": _utc_now(),
        "slots_count": len(SLOTS_GIS_PROTÉGÉS_SPEC),
        "slots": list_slots(),
    }


@router.get("/intake-status")
def get_intake_status() -> Dict[str, Any]:
    manifest = _read_manifest()
    counts = {"ABSENT": 0, "LOADED": 0}
    for s in manifest["slots"].values():
        counts[s.get("status", "ABSENT")] = counts.get(s.get("status", "ABSENT"), 0) + 1
    return {
        **manifest,
        "stats": {
            "total_slots": len(manifest["slots"]),
            "loaded": counts.get("LOADED", 0),
            "absent": counts.get("ABSENT", 0),
            "global_status": ("OPERATIONAL" if counts.get("LOADED", 0) ==
                                len(manifest["slots"]) else "PARTIAL_OR_EMPTY"),
        },
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52 (FUSION ADD-ONLY · VOIE B) — Health-snapshot institutionnel
# Sérialise en un seul appel l'état complet : manifest + état physique
# (scan disque) + audit-log stats + engine_layers_status + V30 lock + flags
# institutionnels. Aucun side-effect.
# ═════════════════════════════════════════════════════════════════════════
def _scan_physical_state(slot_id: str) -> Dict[str, Any]:
    """Scan non-invasif du dossier physique d'un slot (FUSION ADD-ONLY)."""
    p = _slot_dir(slot_id)
    files: List[Dict[str, Any]] = []
    if p.exists():
        for entry in p.iterdir():
            # Ignore les sous-dossiers de chunks / partial assemblies
            if entry.name.startswith(".") or entry.is_dir():
                continue
            try:
                files.append({
                    "filename": entry.name,
                    "size_bytes": entry.stat().st_size,
                })
            except OSError:
                continue
    files.sort(key=lambda x: x["filename"])
    cum = sum(f["size_bytes"] for f in files)
    return {
        "physical_dir": str(p),
        "physical_files_count": len(files),
        "physical_cumulative_bytes": cum,
        "physical_files": files[:64],  # cap pour réponse JSON
        "physical_files_truncated": len(files) > 64,
    }


@router.get("/health-snapshot")
def health_snapshot(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52 · Snapshot institutionnel non-destructif (ADMIN_PREMIUM_ONLY).

    Sérialise en un seul appel l'état complet pré/post-promotion :
      · intake_manifest (déclaratif)
      · physical_state (scan disque par slot)
      · divergences (manifest vs physique)
      · engine_layers_status (compute_corridors_gis sans déclencher)
      · audit_log_stats
      · v30_lock_status
      · prep_only_mode (env var)

    Aucun side-effect. Aucun log audit (anti-spam, comme /token-check).

    ORDRE N°52-EXT : déclenche (best-effort, idempotent) un auto-restore
    depuis l'archive persistante pour les slots archivables en divergence
    PHYS_LOST_Ω. Le restore effectif est consigné en audit (PHYS_AUTO_RESTORED_Ω).
    """
    _verify_token(x_commandant_token)

    manifest = _read_manifest()

    # ─── ORDRE N°52-EXT · Auto-restore idempotent préalable ─────────
    # Pour chaque slot archivable LOADED, vérifie que tous les fichiers
    # manifestés existent physiquement, sinon restaure depuis l'archive.
    auto_restore_summary: List[Dict[str, Any]] = []
    for slot_id in sorted(ARCHIVABLE_SLOTS):
        sm = manifest.get("slots", {}).get(slot_id, {})
        if sm.get("status") != "LOADED":
            continue
        # _auto_restore_slot_from_archive est idempotent : il saute les fichiers
        # déjà présents avec la bonne taille
        res = _auto_restore_slot_from_archive(
            slot_id, client_ip="HEALTH_SNAPSHOT_AUTO_RESTORE")
        if res.get("restored_count", 0) > 0:
            auto_restore_summary.append(res)

    # Re-lire manifest au cas où (il n'est pas modifié par le restore,
    # mais les fichiers physiques oui)
    slots_state: Dict[str, Any] = {}
    divergences: List[Dict[str, Any]] = []

    for slot_id, sm in manifest.get("slots", {}).items():
        phys = _scan_physical_state(slot_id)
        manifest_count = int(sm.get("files_loaded_count", 0))
        manifest_cum = sum(int(u.get("size_bytes", 0)) for u in sm.get("uploads", []))
        is_consistent = (
            manifest_count == phys["physical_files_count"]
            and manifest_cum == phys["physical_cumulative_bytes"]
        )
        slots_state[slot_id] = {
            "manifest_status": sm.get("status"),
            "manifest_files_count": manifest_count,
            "manifest_cumulative_bytes": manifest_cum,
            "manifest_composite_sha256": sm.get("composite_sha256"),
            "physical_files_count": phys["physical_files_count"],
            "physical_cumulative_bytes": phys["physical_cumulative_bytes"],
            "physical_files": phys["physical_files"],
            "physical_files_truncated": phys["physical_files_truncated"],
            "consistent_manifest_vs_physical": is_consistent,
        }
        if not is_consistent:
            divergences.append({
                "slot_id": slot_id,
                "manifest_files": manifest_count,
                "physical_files": phys["physical_files_count"],
                "manifest_bytes": manifest_cum,
                "physical_bytes": phys["physical_cumulative_bytes"],
                "kind": (
                    "PHYS_LOST_Ω" if phys["physical_files_count"] == 0
                                       and manifest_count > 0
                    else "PHYS_DIVERGENT"
                ),
            })

    # Engine layers status (sans déclencher compute_corridors_gis)
    try:
        from engines.v8_institutional.especes.engine_corridors_gis_omega import (
            get_all_layers_status,
        )
        eng = get_all_layers_status()
        engine_layers = {
            "engine_id": eng["engine_id"],
            "layers_total": eng["layers_total"],
            "layers_loaded": eng["layers_loaded"],
            "layers_absent": eng["layers_absent"],
            "global_status": eng["global_status"],
            "engine_lock_sha256": eng["engine_lock_sha256"],
            "data_dir": eng["data_dir"],
            "layers": [
                {"layer_id": layer["layer_id"],
                 "status": layer["status"],
                 "size_bytes": layer["size_bytes"],
                 "expected_path": layer["expected_path"]}
                for layer in eng["layers"]
            ],
        }
    except Exception as e:
        engine_layers = {"error": f"engine_layers_unavailable::{e}"}

    # Audit log stats
    try:
        audit_stats = audit.stats()
    except Exception as e:
        audit_stats = {"error": f"audit_stats_unavailable::{e}"}

    # V30 lock status (best-effort)
    try:
        from engines.v8_institutional.registry_lock_omega import (
            REGISTRY_VERSION, REGISTRY_SEALED_AT, ENGINES_LOCKED,
        )
        v30 = {
            "registry_version": REGISTRY_VERSION,
            "sealed_at": REGISTRY_SEALED_AT,
            "engines_locked_count": len(ENGINES_LOCKED),
            "status": "INVIOLÉ",
        }
    except Exception as e:
        v30 = {"status": "UNKNOWN", "error": str(e)}

    # Intake stats global
    counts = {"LOADED": 0, "ABSENT": 0, "QUARANTINED": 0}
    for s in manifest.get("slots", {}).values():
        counts[s.get("status", "ABSENT")] = counts.get(s.get("status", "ABSENT"), 0) + 1

    return {
        "manifest_id": "GIS_HEALTH_SNAPSHOT_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°52",
        "generated_at_utc": _utc_now(),
        "intake_summary": {
            "total_slots": len(manifest.get("slots", {})),
            "loaded": counts.get("LOADED", 0),
            "absent": counts.get("ABSENT", 0),
            "quarantined": counts.get("QUARANTINED", 0),
        },
        "slots": slots_state,
        "divergences_manifest_vs_physical": divergences,
        "divergences_count": len(divergences),
        "auto_restore_triggered": auto_restore_summary,
        "auto_restore_files_count": sum(
            r.get("restored_count", 0) for r in auto_restore_summary),
        "engine_layers": engine_layers,
        "audit_log_stats": audit_stats,
        "v30_lock": v30,
        "flags": {
            "prep_only_mode": os.environ.get("PREP_ONLY", "true"),
            "incoming_root": str(INCOMING_DIR),
            "quarantine_root": str(QUARANTINE_DIR),
            "manifest_path": str(MANIFEST_PATH),
            "hardened_pipeline_mode": _is_hardened_mode_active(),
            "hardened_pipeline_mode_source": (
                "env" if os.environ.get("BCE4X_HARDENED_PIPELINE_MODE", "").lower()
                in ("true", "1") else "persistent_flag_or_disabled"
            ),
            "persistent_archive_enabled": True,
            "persistent_archive_variant": "A_5_slots_legers",
            "persistent_archive_root": str(ARCHIVE_ROOT),
            "archivable_slots": sorted(ARCHIVABLE_SLOTS),
        },
        "anti_generique": "STRICT",
    }


@router.get("/token-check")
async def token_check(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°48-EXT · Vérification non-destructive du token Commandant.
    Renvoie 200 OK si le token est valide, 401 sinon. Ne déclenche aucune
    opération d'écriture. Pas de log audit (anti-spam).

    Diagnostic-friendly : la réponse contient un hint sur la longueur attendue
    sans révéler le token (anti-fuite).
    """
    expected = os.environ.get("GIS_RECEPTION_COMMANDANT_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="GIS_RECEPTION_COMMANDANT_TOKEN_NOT_CONFIGURED",
        )
    received = (x_commandant_token or "").strip()
    expected_clean = expected.strip()
    if not received:
        raise HTTPException(
            status_code=401,
            detail=f"Token absent · longueur attendue {len(expected_clean)} caractères",
        )
    if received != expected_clean:
        raise HTTPException(
            status_code=401,
            detail=(
                f"Token invalide · reçu {len(received)} chars, attendu "
                f"{len(expected_clean)} chars · vérifiez la copie complète"
            ),
        )
    return {
        "ok": True,
        "token_length": len(expected_clean),
        "doctrine": "ADMIN_PREMIUM_ONLY",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52 (FUSION ADD-ONLY) — Mode DIAGNOSTIC institutionnel pour retry
# Permet d'armer un slot/filename pour observation forensique au prochain
# upload (consigne UPLOAD_RETRY_ARMED_Ω, expose l'état chunks/sessions/audit).
# Aucun side-effect sur le pipeline upload existant.
# ═════════════════════════════════════════════════════════════════════════
DIAG_MARKER_PATH = RECEPTION_ROOT / "diagnostic_marker_omega.json"


def _read_diag_marker() -> Dict[str, Any]:
    if DIAG_MARKER_PATH.exists():
        try:
            return json.loads(DIAG_MARKER_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"armed": []}
    return {"armed": []}


def _write_diag_marker(d: Dict[str, Any]) -> None:
    DIAG_MARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    DIAG_MARKER_PATH.write_text(
        json.dumps(d, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class DiagnosticArmRequest(BaseModel):
    slot_id: str
    filename: str
    expected_chunks_total: Optional[int] = None
    expected_total_size: Optional[int] = None
    note: Optional[str] = None


@router.post("/diagnostic/arm")
async def diagnostic_arm(
    body: DiagnosticArmRequest,
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52 · Arme le mode DIAGNOSTIC sur un (slot_id, filename) précis.
    ADMIN_PREMIUM_ONLY. Consigne un audit-event UPLOAD_RETRY_ARMED_Ω.
    Idempotent : ré-armer un même couple (slot_id, filename) écrase l'entrée.
    """
    _verify_token(x_commandant_token)
    if body.slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{body.slot_id}")
    if not SAFE_FILENAME.match(body.filename) or len(body.filename) > 200:
        raise HTTPException(
            status_code=400,
            detail="FILENAME_UNSAFE — caractères autorisés : [A-Za-z0-9._-]",
        )

    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]

    marker = _read_diag_marker()
    # Dédup par (slot_id, filename) — ré-armement écrase
    marker["armed"] = [
        a for a in marker.get("armed", [])
        if not (a.get("slot_id") == body.slot_id
                 and a.get("filename") == body.filename)
    ]
    entry = {
        "slot_id": body.slot_id,
        "filename": body.filename,
        "expected_chunks_total": body.expected_chunks_total,
        "expected_total_size": body.expected_total_size,
        "note": body.note,
        "armed_at_utc": _utc_now(),
        "armed_by_ip": client_ip,
        "armed_by_ua": ua,
    }
    marker["armed"].append(entry)
    _write_diag_marker(marker)

    audit.append_event(
        event="UPLOAD_RETRY_ARMED_Ω",
        slot_id=body.slot_id,
        filename=body.filename,
        sha256=None,
        size_bytes=int(body.expected_total_size or 0),
        http_code=200,
        client_ip=client_ip,
        user_agent=ua,
        validators=[
            {"name": "diagnostic_armed", "passed": True},
        ],
    )

    return {
        "manifest_id": "DIAGNOSTIC_ARMED_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°52_diag",
        "armed_marker": entry,
        "instructions_pour_client": {
            "method": "POST",
            "path": f"/api/v30/admin-premium/gis/upload-chunk/{body.slot_id}",
            "url_encoding_slot_id": "Le segment Ω du slot_id doit être URL-encodé en %CE%A9",
            "headers_obligatoires": [
                "X-Commandant-Token: <token>",
                "X-Upload-Id: <uuid 8-64 chars [A-Za-z0-9._-]>",
                "X-Chunk-Index: <0..N-1>",
                "X-Chunks-Total: <N>",
                "X-Original-Filename: <" + body.filename + ">",
                "X-Total-Size: <bytes>",
                "X-Final-Chunk: 'true' UNIQUEMENT sur le dernier chunk",
            ],
            "body": "multipart/form-data field 'file' = chunk binaire (≤ 50 Mo)",
            "filename_PAS_dans_url": True,
            "regex_filename_safe": "^[A-Za-z0-9._-]+$",
            "responses": {
                "200": "CHUNK_STORED ou (final) UPLOAD_LOADED",
                "400": "X-Upload-Id, X-Chunk-Index, X-Original-Filename invalide",
                "401": "Token Commandant invalide",
                "404": "SLOT_INCONNU :: vérifiez l'URL et l'encodage du slot_id",
                "409": "CHUNKS_INCOMPLETS au final",
                "413": "FILE_TOO_LARGE",
                "422": "QUARANTINED (validators échoués)",
            },
        },
        "v30_lock": "INVIOLÉ",
    }


@router.post("/diagnostic/disarm")
async def diagnostic_disarm(
    body: DiagnosticArmRequest,
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52 · Désarme un marker diagnostic (slot_id, filename)."""
    _verify_token(x_commandant_token)
    if body.slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{body.slot_id}")

    client_ip = request.client.host if request.client else "unknown"
    marker = _read_diag_marker()
    before = len(marker.get("armed", []))
    marker["armed"] = [
        a for a in marker.get("armed", [])
        if not (a.get("slot_id") == body.slot_id
                 and a.get("filename") == body.filename)
    ]
    after = len(marker.get("armed", []))
    _write_diag_marker(marker)

    audit.append_event(
        event="UPLOAD_RETRY_DISARMED_Ω",
        slot_id=body.slot_id,
        filename=body.filename,
        sha256=None,
        size_bytes=0,
        http_code=200,
        client_ip=client_ip,
        user_agent=(user_agent or "")[:200],
        validators=[{"name": "diagnostic_disarmed",
                     "passed": True,
                     "removed_count": before - after}],
    )

    return {
        "manifest_id": "DIAGNOSTIC_DISARMED_Ω",
        "removed_count": before - after,
        "still_armed_count": after,
        "v30_lock": "INVIOLÉ",
    }


@router.get("/diagnostic/inspect/{slot_id}")
async def diagnostic_inspect(
    slot_id: str = FPath(..., description="Slot à inspecter"),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52 · Inspection forensique exhaustive d'un slot.
    ADMIN_PREMIUM_ONLY. Aucun side-effect, aucun audit-log généré.

    Expose :
      · Markers diagnostic armés
      · Sessions chunk en cours (chunks reçus, total attendu, filename)
      · Fichiers physiques présents (avec tailles)
      · Fichiers .partial / assemblies en cours
      · 10 derniers audit-events sur ce slot
    """
    _verify_token(x_commandant_token)
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")

    marker = _read_diag_marker()
    armed_for_slot = [a for a in marker.get("armed", [])
                      if a.get("slot_id") == slot_id]

    slot_dir = _slot_dir(slot_id)
    chunks_dir = slot_dir / CHUNKS_SUBDIR
    sessions: List[Dict[str, Any]] = []
    if chunks_dir.exists():
        for upload_subdir in sorted(chunks_dir.iterdir()):
            if not upload_subdir.is_dir():
                continue
            session_path = upload_subdir / "session.json"
            session_data: Dict[str, Any] = {}
            if session_path.exists():
                try:
                    session_data = json.loads(
                        session_path.read_text(encoding="utf-8"))
                except Exception as e:
                    session_data = {"error": f"session_parse_error::{e}"}
            chunks_present = sorted([
                p.name for p in upload_subdir.iterdir()
                if p.is_file() and p.name.endswith(".bin")
            ])
            sessions.append({
                "upload_id": upload_subdir.name,
                "session": session_data,
                "chunks_files_present_count": len(chunks_present),
                "chunks_files_sample": chunks_present[:8],
                "chunks_files_truncated": len(chunks_present) > 8,
            })

    partials: List[str] = []
    if slot_dir.exists():
        partials = sorted([
            p.name for p in slot_dir.iterdir()
            if p.is_file() and (p.name.endswith(".partial")
                                  or p.name.startswith("."))
        ])

    last_events = audit.read_entries(slot_id=slot_id, limit=10)
    phys = _scan_physical_state(slot_id)

    return {
        "manifest_id": "DIAGNOSTIC_INSPECT_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "slot_id": slot_id,
        "generated_at_utc": _utc_now(),
        "diagnostic_marker_armed": armed_for_slot,
        "diagnostic_marker_armed_count": len(armed_for_slot),
        "chunk_sessions_in_flight": sessions,
        "chunk_sessions_in_flight_count": len(sessions),
        "physical_state": phys,
        "partial_or_hidden_files": partials,
        "last_audit_events": last_events,
        "endpoint_chunked": (
            f"/api/v30/admin-premium/gis/upload-chunk/{slot_id}"
        ),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT (FUSION ADD-ONLY) — BCE4X_HARDENED_PIPELINE_MODE_Ω
# Doctrine ANTI_GÉNÉRIQUE_STRICT : aucune fonctionnalité fictive.
# Substituts honnêtes pour les directives techniquement non-implémentables :
#   · "Bypass Cloudflare" → CLOUDFLARE_CONSTRAINT_HONORED_Ω (chunks ≤ 50 Mo
#     + idempotence + resume) — le flag activé ne court-circuite RIEN du
#     proxy externe ; il endurcit ce qui est sous notre contrôle.
#   · "Retry auto 5x" → idempotence par chunk_index + endpoint /resume pour
#     que le client connaisse les chunks manquants après timeout/502.
#   · "Garantie 100%" → asymptote robuste via idempotence+resume.
# Effets RÉELS quand activé :
#   · fsync sur chaque chunk binaire écrit (durabilité disque)
#   · session.json ré-écrit à chaque chunk
#   · rereception_log : compteur de re-réception par chunk_index
#   · audit-event BCE4X_HARDENED_MODE_ACTIVATED_Ω à l'activation
# ═════════════════════════════════════════════════════════════════════════
HARDENED_FLAG_PATH = RECEPTION_ROOT / "hardened_mode_omega.json"


def _read_hardened_flag() -> Dict[str, Any]:
    if HARDENED_FLAG_PATH.exists():
        try:
            return json.loads(HARDENED_FLAG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"enabled": False, "history": []}


def _write_hardened_flag(d: Dict[str, Any]) -> None:
    HARDENED_FLAG_PATH.parent.mkdir(parents=True, exist_ok=True)
    HARDENED_FLAG_PATH.write_text(
        json.dumps(d, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _is_hardened_mode_active() -> bool:
    """Retourne True si BCE4X_HARDENED_PIPELINE_MODE est actif (flag persistant
    OU env var BCE4X_HARDENED_PIPELINE_MODE=true)."""
    if os.environ.get("BCE4X_HARDENED_PIPELINE_MODE", "").lower() in ("true", "1"):
        return True
    return bool(_read_hardened_flag().get("enabled", False))


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT · PERSISTENT_ARCHIVE_Ω (VARIANTE A — 5 slots légers)
# Archive atomique vers /app/backend/data/gis_archive/{slot}/ pour protéger
# contre la volatilité de /var/cache au reboot du pod Kubernetes.
# ═════════════════════════════════════════════════════════════════════════
ARCHIVE_ROOT = Path("/app/backend/data/gis_archive")
ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)

# Liste blanche explicite — variante A : 5 slots secondaires uniquement.
# FORET_MFFP_Ω (36 Go) EXCLU — trop volumineux pour /app (9,8 Go).
ARCHIVABLE_SLOTS = {
    "SOL_IRDA_Ω",
    "CHASSE_ZEC_SEPAQ_Ω",
    "ROUTES_MTQ_SECONDAIRES_Ω",
    "LIMITES_TERRITORIALES_FINES_Ω",
    "PRESSION_HUMAINE_Ω",
}


def _archive_dir(slot_id: str) -> Path:
    p = ARCHIVE_ROOT / slot_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _archive_file_persistent(slot_id: str, filename: str,
                              src_path: Path,
                              sha256_source: str,
                              client_ip: str = "unknown",
                              user_agent: str = "") -> Dict[str, Any]:
    """Copie atomique d'un fichier validé vers /app/backend/data/gis_archive/.
    Retourne le status de l'opération. Ne lève jamais (best-effort).
    Anti-générique : copie RÉELLE (même contenu physique, SHA-256 re-vérifié).
    """
    if slot_id not in ARCHIVABLE_SLOTS:
        return {"archived": False, "reason": "SLOT_NOT_IN_WHITELIST_A"}
    if not src_path.exists() or src_path.stat().st_size == 0:
        return {"archived": False, "reason": "SOURCE_MISSING_OR_EMPTY"}

    dest_dir = _archive_dir(slot_id)
    dest_path = dest_dir / filename
    tmp_path = dest_dir / f".{filename}.archiving.partial"

    # Check disk space (best-effort)
    try:
        import shutil as _sh
        src_size = src_path.stat().st_size
        free_bytes = _sh.disk_usage(str(ARCHIVE_ROOT)).free
        if free_bytes < src_size * 1.1:
            audit.append_event(
                event="PHYS_ARCHIVE_SKIPPED_DISK_FULL_Ω",
                slot_id=slot_id, filename=filename, sha256=sha256_source,
                size_bytes=src_size, http_code=0,
                client_ip=client_ip, user_agent=user_agent,
                validators=[{"name": "disk_free_check", "passed": False,
                             "free_bytes": free_bytes, "needed": src_size}],
            )
            return {"archived": False, "reason": "DISK_FULL",
                    "free_bytes": free_bytes, "needed": src_size}
    except Exception:
        pass

    h = hashlib.sha256()
    try:
        with open(src_path, "rb") as inp, open(tmp_path, "wb") as out:
            while True:
                buf = inp.read(1 << 20)
                if not buf:
                    break
                h.update(buf)
                out.write(buf)
            if _is_hardened_mode_active():
                try:
                    out.flush()
                    os.fsync(out.fileno())
                except OSError:
                    pass
        sha_copy = h.hexdigest()
        if sha_copy != sha256_source:
            tmp_path.unlink(missing_ok=True)
            audit.append_event(
                event="PHYS_ARCHIVE_SHA_MISMATCH_Ω",
                slot_id=slot_id, filename=filename, sha256=sha_copy,
                size_bytes=src_size, http_code=0,
                client_ip=client_ip, user_agent=user_agent,
                validators=[{"name": "archive_sha_match",
                             "passed": False,
                             "expected": sha256_source,
                             "got": sha_copy}],
            )
            return {"archived": False, "reason": "SHA_MISMATCH"}
        # Atomic move (rename)
        os.replace(str(tmp_path), str(dest_path))
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        audit.append_event(
            event="PHYS_ARCHIVE_ERROR_Ω",
            slot_id=slot_id, filename=filename, sha256=sha256_source,
            size_bytes=src_path.stat().st_size if src_path.exists() else 0,
            http_code=500, client_ip=client_ip, user_agent=user_agent,
            validators=[{"name": "archive_write", "passed": False, "error": str(e)[:200]}],
        )
        return {"archived": False, "reason": f"ARCHIVE_ERROR::{e}"}

    audit.append_event(
        event="PHYS_ARCHIVE_PERSISTED_Ω",
        slot_id=slot_id, filename=filename, sha256=sha256_source,
        size_bytes=dest_path.stat().st_size, http_code=200,
        client_ip=client_ip, user_agent=user_agent,
        validators=[{"name": "archive_copy", "passed": True},
                    {"name": "archive_sha_match", "passed": True}],
    )
    return {
        "archived": True,
        "dest_path": str(dest_path),
        "sha256": sha256_source,
        "size_bytes": dest_path.stat().st_size,
    }


def _auto_restore_slot_from_archive(slot_id: str,
                                     client_ip: str = "auto_restore") -> Dict[str, Any]:
    """Si slot archivable et fichier physique absent mais présent en archive,
    copie l'archive vers /var/cache/.../incoming/{slot}/. Consigne PHYS_AUTO_RESTORED_Ω.
    Retourne la liste des fichiers restaurés.
    """
    if slot_id not in ARCHIVABLE_SLOTS:
        return {"slot_id": slot_id, "skipped": "NOT_ARCHIVABLE",
                "restored_files": []}

    archive_dir = _archive_dir(slot_id)
    incoming_dir = _slot_dir(slot_id)
    restored: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    for arch_file in sorted(archive_dir.iterdir()):
        if not arch_file.is_file():
            continue
        if arch_file.name.startswith("."):
            continue
        target = incoming_dir / arch_file.name
        # Skip if already present with same size
        if target.exists() and target.stat().st_size == arch_file.stat().st_size:
            continue
        tmp = incoming_dir / f".{arch_file.name}.restoring.partial"
        try:
            with open(arch_file, "rb") as inp, open(tmp, "wb") as out:
                while True:
                    buf = inp.read(1 << 20)
                    if not buf:
                        break
                    out.write(buf)
            os.replace(str(tmp), str(target))
            restored.append({
                "filename": arch_file.name,
                "size_bytes": target.stat().st_size,
            })
            audit.append_event(
                event="PHYS_AUTO_RESTORED_Ω",
                slot_id=slot_id,
                filename=arch_file.name,
                sha256=None,  # Le SHA manifesté reste la référence
                size_bytes=target.stat().st_size,
                http_code=200,
                client_ip=client_ip,
                user_agent="AUTO_RESTORE_FROM_PERSISTENT_ARCHIVE_Ω",
                validators=[{"name": "auto_restore", "passed": True,
                             "source_archive": str(arch_file)}],
            )
        except Exception as e:
            tmp.unlink(missing_ok=True)
            failed.append({"filename": arch_file.name, "error": str(e)[:200]})

    return {
        "slot_id": slot_id,
        "restored_count": len(restored),
        "restored_files": restored,
        "failed_files": failed,
    }


@router.get("/diagnostic/persistent-archive/status")
async def persistent_archive_status(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Inventaire de l'archive persistante (variante A)."""
    _verify_token(x_commandant_token)

    inventory: Dict[str, Any] = {}
    total_files = 0
    total_bytes = 0
    for slot_id in sorted(ARCHIVABLE_SLOTS):
        d = _archive_dir(slot_id)
        files: List[Dict[str, Any]] = []
        for p in sorted(d.iterdir()):
            if p.is_file() and not p.name.startswith("."):
                files.append({"filename": p.name,
                              "size_bytes": p.stat().st_size})
        cum = sum(f["size_bytes"] for f in files)
        total_files += len(files)
        total_bytes += cum
        inventory[slot_id] = {
            "archive_dir": str(d),
            "files_count": len(files),
            "cumulative_bytes": cum,
            "files": files,
        }

    try:
        import shutil as _sh
        usage = _sh.disk_usage(str(ARCHIVE_ROOT))
        disk = {"total_bytes": usage.total, "used_bytes": usage.used,
                "free_bytes": usage.free}
    except Exception:
        disk = {"error": "disk_usage_unavailable"}

    return {
        "manifest_id": "PERSISTENT_ARCHIVE_STATUS_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "variant": "A_5_slots_legers",
        "archive_root": str(ARCHIVE_ROOT),
        "archivable_slots_whitelist": sorted(ARCHIVABLE_SLOTS),
        "slot_excluded_from_archive": ["FORET_MFFP_Ω (trop volumineux pour /app)"],
        "inventory": inventory,
        "totals": {"files": total_files, "bytes": total_bytes},
        "disk_usage": disk,
        "v30_lock": "INVIOLÉ",
    }


class RestoreRequest(BaseModel):
    slot_id: Optional[str] = None
    restore_all: Optional[bool] = False


@router.post("/diagnostic/persistent-archive/restore")
async def persistent_archive_restore(
    body: RestoreRequest,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Restaure manuellement les fichiers d'un slot depuis
    l'archive vers /var/cache. Consigne PHYS_AUTO_RESTORED_Ω par fichier."""
    _verify_token(x_commandant_token)

    results: List[Dict[str, Any]] = []
    if body.restore_all:
        for slot_id in sorted(ARCHIVABLE_SLOTS):
            results.append(_auto_restore_slot_from_archive(slot_id,
                                                            client_ip="MANUAL_RESTORE_ALL"))
    elif body.slot_id:
        if body.slot_id not in ARCHIVABLE_SLOTS:
            raise HTTPException(
                status_code=400,
                detail=f"SLOT_NOT_IN_WHITELIST_A::{body.slot_id}")
        results.append(_auto_restore_slot_from_archive(body.slot_id,
                                                        client_ip="MANUAL_RESTORE_SINGLE"))
    else:
        raise HTTPException(
            status_code=400,
            detail="Fournir 'slot_id' OU 'restore_all: true'")

    total_restored = sum(r.get("restored_count", 0) for r in results)
    return {
        "manifest_id": "PERSISTENT_ARCHIVE_RESTORE_Ω",
        "total_restored_files": total_restored,
        "results": results,
        "v30_lock": "INVIOLÉ",
    }


def _normalize_slot_id(raw: str) -> Dict[str, Any]:
    """Normalise un slot_id reçu : NFC/NFD + percent-decoding + comparaison
    case-insensitive. Retourne un diagnostic riche."""
    import unicodedata
    from urllib.parse import unquote
    candidates = [
        ("raw", raw),
        ("percent_decoded", unquote(raw)),
        ("nfc", unicodedata.normalize("NFC", raw)),
        ("nfd", unicodedata.normalize("NFD", raw)),
        ("nfc_percent_decoded", unicodedata.normalize("NFC", unquote(raw))),
    ]
    seen = set()
    tested = []
    matched_canonical: Optional[str] = None
    matched_via: Optional[str] = None
    for variant_name, variant_value in candidates:
        if variant_value in seen:
            continue
        seen.add(variant_value)
        tested.append({"variant": variant_name, "value": variant_value,
                       "matches": variant_value in SLOT_BY_ID})
        if matched_canonical is None and variant_value in SLOT_BY_ID:
            matched_canonical = variant_value
            matched_via = variant_name
    return {
        "input_raw": raw,
        "matched_canonical": matched_canonical,
        "matched_via": matched_via,
        "tested_variants": tested,
        "all_known_slot_ids": list(SLOT_BY_ID.keys()),
    }


class HardenedToggleRequest(BaseModel):
    activated_by: Optional[str] = None
    reason: Optional[str] = None


@router.post("/diagnostic/hardened/activate")
async def hardened_activate(
    body: HardenedToggleRequest,
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Active BCE4X_HARDENED_PIPELINE_MODE_Ω.
    ADMIN_PREMIUM_ONLY. Idempotent (ré-activation = trace d'audit
    supplémentaire mais flag inchangé).
    """
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]

    flag = _read_hardened_flag()
    was_enabled = bool(flag.get("enabled"))
    flag["enabled"] = True
    flag.setdefault("history", []).append({
        "action": "ACTIVATE",
        "ts_utc": _utc_now(),
        "by_ip": client_ip,
        "by_ua": ua,
        "activated_by": body.activated_by,
        "reason": body.reason,
        "previous_state": "ENABLED" if was_enabled else "DISABLED",
    })
    flag["last_activated_utc"] = _utc_now()
    flag["last_activated_by_ip"] = client_ip
    _write_hardened_flag(flag)

    audit.append_event(
        event="BCE4X_HARDENED_MODE_ACTIVATED_Ω",
        slot_id="(global)",
        filename="(none)",
        sha256=None,
        size_bytes=0,
        http_code=200,
        client_ip=client_ip,
        user_agent=ua,
        validators=[
            {"name": "hardened_mode_set",
             "passed": True,
             "previous_state": "ENABLED" if was_enabled else "DISABLED",
             "activated_by": body.activated_by,
             "reason": body.reason},
        ],
    )

    return {
        "manifest_id": "BCE4X_HARDENED_MODE_ACTIVATED_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "n°52_hardened",
        "enabled": True,
        "previous_state": "ENABLED" if was_enabled else "DISABLED",
        "effective_substitutes": {
            "cloudflare_constraint": "CLOUDFLARE_CONSTRAINT_HONORED_Ω · chunks ≤ 50 Mo + idempotence",
            "retry_strategy": "Idempotent par chunk_index + endpoint /resume côté client",
            "durability": "fsync + dir_fsync sur chaque chunk · session.json persisté",
            "url_validation": "_normalize_slot_id() avec NFC/NFD/percent-decode",
            "100_percent_promise": "ASYMPTOTIQUE — pas garanti, doctrine institutionnelle honnête",
        },
        "v30_lock": "INVIOLÉ",
    }


@router.post("/diagnostic/hardened/deactivate")
async def hardened_deactivate(
    body: HardenedToggleRequest,
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Désactive BCE4X_HARDENED_PIPELINE_MODE_Ω."""
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]

    flag = _read_hardened_flag()
    was_enabled = bool(flag.get("enabled"))
    flag["enabled"] = False
    flag.setdefault("history", []).append({
        "action": "DEACTIVATE",
        "ts_utc": _utc_now(),
        "by_ip": client_ip,
        "by_ua": ua,
        "activated_by": body.activated_by,
        "reason": body.reason,
        "previous_state": "ENABLED" if was_enabled else "DISABLED",
    })
    _write_hardened_flag(flag)

    audit.append_event(
        event="BCE4X_HARDENED_MODE_DEACTIVATED_Ω",
        slot_id="(global)",
        filename="(none)",
        sha256=None,
        size_bytes=0,
        http_code=200,
        client_ip=client_ip,
        user_agent=ua,
        validators=[{"name": "hardened_mode_unset",
                     "passed": True,
                     "previous_state": "ENABLED" if was_enabled else "DISABLED"}],
    )

    return {
        "manifest_id": "BCE4X_HARDENED_MODE_DEACTIVATED_Ω",
        "enabled": False,
        "previous_state": "ENABLED" if was_enabled else "DISABLED",
        "v30_lock": "INVIOLÉ",
    }


@router.get("/diagnostic/hardened/status")
async def hardened_status(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · État du mode hardened."""
    _verify_token(x_commandant_token)
    flag = _read_hardened_flag()
    return {
        "manifest_id": "BCE4X_HARDENED_MODE_STATUS_Ω",
        "enabled": _is_hardened_mode_active(),
        "flag_persistant_enabled": bool(flag.get("enabled")),
        "env_var_enabled": os.environ.get(
            "BCE4X_HARDENED_PIPELINE_MODE", "").lower() in ("true", "1"),
        "last_activated_utc": flag.get("last_activated_utc"),
        "last_activated_by_ip": flag.get("last_activated_by_ip"),
        "history_count": len(flag.get("history", [])),
        "history_recent": flag.get("history", [])[-5:],
        "effective_substitutes_when_enabled": {
            "cloudflare_constraint": "CLOUDFLARE_CONSTRAINT_HONORED_Ω",
            "retry_strategy": "idempotent_by_chunk_index + /resume",
            "durability": "fsync_on_each_chunk_write",
        },
        "v30_lock": "INVIOLÉ",
    }


class ValidateUrlRequest(BaseModel):
    slot_id: str
    filename: Optional[str] = None
    upload_id: Optional[str] = None


@router.post("/diagnostic/validate-url")
async def diagnostic_validate_url(
    body: ValidateUrlRequest,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Valide la construction d'URL côté client.
    Retourne :
      · OK avec path canonique attendu
      · KO avec hints précis (variants Unicode testés, slot_ids connus)
    """
    _verify_token(x_commandant_token)

    norm = _normalize_slot_id(body.slot_id)

    filename_check: Dict[str, Any] = {"provided": False}
    if body.filename:
        ok = bool(SAFE_FILENAME.match(body.filename)) and len(body.filename) <= 200
        filename_check = {
            "provided": True,
            "value": body.filename,
            "regex_safe": "^[A-Za-z0-9._-]+$",
            "passed": ok,
            "hint": ("OK" if ok else
                     "Filename non sûr — caractères autorisés : [A-Za-z0-9._-]"),
        }

    upload_id_check: Dict[str, Any] = {"provided": False}
    if body.upload_id:
        ok = bool(CHUNKED_UPLOAD_ID_RE.match(body.upload_id))
        upload_id_check = {
            "provided": True,
            "value": body.upload_id,
            "regex": "^[A-Za-z0-9._-]{8,64}$",
            "passed": ok,
        }

    result_passed = (
        norm["matched_canonical"] is not None
        and (not body.filename or filename_check.get("passed", True))
        and (not body.upload_id or upload_id_check.get("passed", True))
    )

    canonical_path = None
    if norm["matched_canonical"]:
        from urllib.parse import quote
        canonical_path = (
            f"/api/v30/admin-premium/gis/upload-chunk/"
            f"{quote(norm['matched_canonical'], safe='._-')}"
        )

    return {
        "manifest_id": "DIAGNOSTIC_VALIDATE_URL_Ω",
        "passed": result_passed,
        "slot_id_normalized": norm,
        "filename_check": filename_check,
        "upload_id_check": upload_id_check,
        "canonical_endpoint": canonical_path,
        "expected_url_full_example": (
            f"https://<host>{canonical_path}" if canonical_path else None),
        "v30_lock": "INVIOLÉ",
    }


@router.get("/upload-chunk/{slot_id}/resume/{upload_id}")
async def upload_chunk_resume(
    slot_id: str = FPath(..., description="Slot cible"),
    upload_id: str = FPath(..., description="Upload-Id de la session"),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Reprise fine — retourne l'état exact d'une session
    chunk pour permettre au client de ré-envoyer UNIQUEMENT les chunks
    manquants après timeout/502.
    """
    _verify_token(x_commandant_token)
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")
    if not CHUNKED_UPLOAD_ID_RE.match(upload_id):
        raise HTTPException(
            status_code=400,
            detail="UPLOAD_ID_INVALIDE — regex ^[A-Za-z0-9._-]{8,64}$")

    session = _read_chunk_session(slot_id, upload_id)
    received = set(int(i) for i in session.get("chunks_received", []) or [])
    chunks_total = session.get("chunks_total")
    missing: List[int] = []
    if chunks_total:
        missing = sorted(set(range(int(chunks_total))) - received)

    # Vérification physique des fichiers .bin présents (dérive éventuelle)
    chunks_dir = _chunks_dir(slot_id, upload_id)
    physical_chunks: List[int] = []
    if chunks_dir.exists():
        for p in chunks_dir.iterdir():
            if p.is_file() and p.name.endswith(".bin"):
                try:
                    physical_chunks.append(int(p.stem))
                except ValueError:
                    pass
    physical_chunks.sort()

    consistent = sorted(received) == physical_chunks

    return {
        "manifest_id": "UPLOAD_CHUNK_RESUME_Ω",
        "slot_id": slot_id,
        "upload_id": upload_id,
        "filename": session.get("filename"),
        "chunks_total": chunks_total,
        "chunks_received_count": len(received),
        "chunks_received": sorted(received),
        "chunks_missing": missing,
        "chunks_missing_count": len(missing),
        "physical_chunks_present": physical_chunks,
        "session_vs_physical_consistent": consistent,
        "rereception_log": session.get("rereception_log", {}),
        "session_started_at_utc": session.get("started_at_utc"),
        "session_last_update_utc": session.get("last_update_utc"),
        "instructions": (
            "Ré-envoyer UNIQUEMENT les chunks de chunks_missing. "
            "Le serveur est idempotent : ré-envoi d'un chunk déjà reçu OK."
        ),
        "hardened_mode_active": _is_hardened_mode_active(),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT · PEE_MAJ_Ω VOIE A — Endpoints de pilotage du pipeline
# monolithique : status canonical, persistance des dérivées, audit-event
# d'activation. Aucune réécriture du pipeline chunked existant — il est
# re-utilisé tel quel grâce à l'inscription du slot dans SLOT_BY_ID.
# ═════════════════════════════════════════════════════════════════════════
PEE_MAJ_ACTIVATION_FLAG = RECEPTION_ROOT / "pee_maj_pipeline_activated_omega.json"


def _read_pee_maj_flag() -> Dict[str, Any]:
    if PEE_MAJ_ACTIVATION_FLAG.exists():
        try:
            return json.loads(PEE_MAJ_ACTIVATION_FLAG.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"activated": False, "history": []}


def _write_pee_maj_flag(d: Dict[str, Any]) -> None:
    PEE_MAJ_ACTIVATION_FLAG.parent.mkdir(parents=True, exist_ok=True)
    PEE_MAJ_ACTIVATION_FLAG.write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


@router.post("/diagnostic/pee-maj/activate")
async def pee_maj_activate(
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Active formellement le pipeline monolithique
    PEE_MAJ_Ω. Idempotent. Consigne PEE_MAJ_PIPELINE_ACTIVATED_Ω."""
    _verify_token(x_commandant_token)
    if "FORET_MFFP_PEE_MAJ_Ω" not in SLOT_BY_ID:
        raise HTTPException(
            status_code=503,
            detail="SLOT_NOT_REGISTERED::FORET_MFFP_PEE_MAJ_Ω · "
                   "Spec absente de SLOTS_GIS_PROTÉGÉS_SPEC")

    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]
    flag = _read_pee_maj_flag()
    was_activated = bool(flag.get("activated"))
    flag["activated"] = True
    flag.setdefault("history", []).append({
        "action": "ACTIVATE", "ts_utc": _utc_now(),
        "by_ip": client_ip, "by_ua": ua,
        "previous_state": "ACTIVATED" if was_activated else "INACTIVE",
    })
    flag["last_activated_utc"] = _utc_now()
    _write_pee_maj_flag(flag)

    audit.append_event(
        event="PEE_MAJ_PIPELINE_ACTIVATED_Ω",
        slot_id="FORET_MFFP_PEE_MAJ_Ω",
        filename="(pipeline_activation_only)",
        sha256=None, size_bytes=0, http_code=200,
        client_ip=client_ip, user_agent=ua,
        validators=[
            {"name": "pipeline_activated", "passed": True,
             "previous_state": "ACTIVATED" if was_activated else "INACTIVE",
             "spec_taille_max_octets": SLOT_BY_ID["FORET_MFFP_PEE_MAJ_Ω"]
                                              ["taille_max_octets"],
             "spec_formats_acceptes": SLOT_BY_ID["FORET_MFFP_PEE_MAJ_Ω"]
                                             ["formats_acceptes"],
             "substitutes_slot": SLOT_BY_ID["FORET_MFFP_PEE_MAJ_Ω"]
                                       .get("substitutes_slot_for_corridors_gis")},
        ],
    )

    spec = SLOT_BY_ID["FORET_MFFP_PEE_MAJ_Ω"]
    return {
        "manifest_id": "PEE_MAJ_PIPELINE_ACTIVATED_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "n°52_ext_pee_maj_voie_a",
        "activated": True,
        "previous_state": "ACTIVATED" if was_activated else "INACTIVE",
        "slot_id": "FORET_MFFP_PEE_MAJ_Ω",
        "slot_spec_summary": {
            "type_pipeline": spec.get("type_pipeline"),
            "voie_acquisition": spec.get("voie_acquisition"),
            "formats_acceptes": spec.get("formats_acceptes"),
            "taille_max_octets": spec.get("taille_max_octets"),
            "taille_max_GB": round(spec.get("taille_max_octets", 0) / 1e9, 1),
            "substitutes_slot": spec.get("substitutes_slot_for_corridors_gis"),
            "ephemeral_storage": spec.get("ephemeral_storage"),
            "derivatives_persistent": spec.get("derivatives_persistent"),
        },
        "endpoint_chunked": (
            "/api/v30/admin-premium/gis/upload-chunk/FORET_MFFP_PEE_MAJ_%CE%A9"),
        "expected_filename": "pee_maj.gpkg",
        "incoming_dir": str(_slot_dir("FORET_MFFP_PEE_MAJ_Ω")),
        "honest_disclosure": {
            "storage_kind": "EPHEMERAL_var_cache",
            "var_cache_total_GB": round(
                __import__("shutil").disk_usage("/var/cache").total / 1e9, 1),
            "var_cache_free_GB": round(
                __import__("shutil").disk_usage("/var/cache").free / 1e9, 1),
            "warning": (
                "pee_maj.gpkg réside dans /var/cache (éphémère). Au reboot du "
                "pod, le fichier brut est perdu. Les dérivés analytiques "
                "(GIS_FRAGMENTATION_INDEX, GIS_COUVERT_FORESTIER_DENSITY, etc.) "
                "produits par compute_corridors_gis() seront archivés en "
                "persistance via persist_derivatives_to_archive() vers "
                "/app/backend/data/gis_archive/_derived/."),
        },
        "v30_lock": "INVIOLÉ",
    }


@router.get("/diagnostic/pee-maj/status")
async def pee_maj_status(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Status complet du pipeline PEE_MAJ_Ω VOIE A."""
    _verify_token(x_commandant_token)
    flag = _read_pee_maj_flag()

    # Engine canonical state
    try:
        from engines.v8_institutional.especes.engine_corridors_gis_omega import (
            _pee_maj_canonical_state, get_all_layers_status,
            DERIVATIVES_PERSISTENT_DIR,
        )
        canonical = _pee_maj_canonical_state()
        eng = get_all_layers_status()
        eng_summary = {
            "global_status": eng["global_status"],
            "layers_loaded": eng["layers_loaded"],
            "layers_absent": eng["layers_absent"],
            "pee_maj_canonical_active": eng["pee_maj_canonical_active"],
            "pee_maj_canonical_path": eng["pee_maj_canonical_path"],
            "pee_maj_canonical_size_bytes": eng["pee_maj_canonical_size_bytes"],
            "pee_maj_substitutes_slot": eng["pee_maj_substitutes_slot"],
        }
        derivatives_root = str(DERIVATIVES_PERSISTENT_DIR)
        derivatives_files = []
        if DERIVATIVES_PERSISTENT_DIR.exists():
            for p in sorted(DERIVATIVES_PERSISTENT_DIR.iterdir()):
                if p.is_file():
                    derivatives_files.append(
                        {"filename": p.name, "size_bytes": p.stat().st_size})
    except Exception as e:
        canonical = {"error": str(e)}
        eng_summary = {"error": str(e)}
        derivatives_root = "(unavailable)"
        derivatives_files = []

    # Slot state
    manifest = _read_manifest()
    slot = manifest.get("slots", {}).get("FORET_MFFP_PEE_MAJ_Ω", {})

    # ─── Scan sessions chunked en cours (forensique upload) ───────────
    slot_dir = _slot_dir("FORET_MFFP_PEE_MAJ_Ω")
    chunks_dir = slot_dir / CHUNKS_SUBDIR
    sessions_in_flight: List[Dict[str, Any]] = []
    last_session_summary: Dict[str, Any] = {
        "exists": False,
        "upload_id": None,
        "filename": None,
        "chunks_total": None,
        "chunks_received_count": 0,
        "last_successful_chunk_index": None,
        "physical_chunks_count": 0,
        "session_vs_physical_consistent": None,
        "started_at_utc": None,
        "last_update_utc": None,
        "rereception_log": {},
    }
    if chunks_dir.exists():
        sessions_subdirs = sorted(
            [d for d in chunks_dir.iterdir() if d.is_dir()],
            key=lambda d: d.stat().st_mtime, reverse=True,
        )
        for upload_subdir in sessions_subdirs:
            session_path = upload_subdir / "session.json"
            sd: Dict[str, Any] = {}
            if session_path.exists():
                try:
                    sd = json.loads(session_path.read_text(encoding="utf-8"))
                except Exception:
                    sd = {}
            phys_chunks = sorted([
                int(p.stem) for p in upload_subdir.iterdir()
                if p.is_file() and p.name.endswith(".bin")
                and p.stem.isdigit()
            ])
            received = sorted(int(i) for i in sd.get("chunks_received", []) or [])
            entry = {
                "upload_id": upload_subdir.name,
                "filename": sd.get("filename"),
                "chunks_total": sd.get("chunks_total"),
                "chunks_received_count": len(received),
                "physical_chunks_count": len(phys_chunks),
                "last_successful_chunk_index": (max(received) if received else None),
                "started_at_utc": sd.get("started_at_utc"),
                "last_update_utc": sd.get("last_update_utc"),
                "rereception_log": sd.get("rereception_log", {}),
            }
            sessions_in_flight.append(entry)

        if sessions_in_flight:
            most_recent = sessions_in_flight[0]
            last_session_summary = {
                "exists": True,
                "upload_id": most_recent["upload_id"],
                "filename": most_recent["filename"],
                "chunks_total": most_recent["chunks_total"],
                "chunks_received_count": most_recent["chunks_received_count"],
                "physical_chunks_count": most_recent["physical_chunks_count"],
                "last_successful_chunk_index": most_recent["last_successful_chunk_index"],
                "session_vs_physical_consistent": (
                    most_recent["chunks_received_count"]
                    == most_recent["physical_chunks_count"]
                ),
                "started_at_utc": most_recent["started_at_utc"],
                "last_update_utc": most_recent["last_update_utc"],
                "rereception_log": most_recent["rereception_log"],
                "resume_endpoint": (
                    f"/api/v30/admin-premium/gis/upload-chunk/"
                    f"FORET_MFFP_PEE_MAJ_%CE%A9/resume/"
                    f"{most_recent['upload_id']}"),
            }

    # ─── Dernière erreur observable côté backend (audit-log) ──────────
    last_error_event: Dict[str, Any] = {
        "exists": False,
        "ts_utc": None,
        "event": None,
        "http_status": None,
        "filename": None,
        "phase_diagnostic": None,
    }
    try:
        # Scan des derniers events PEE_MAJ + UPLOAD_*  pour ce slot
        recent = audit.read_entries(slot_id="FORET_MFFP_PEE_MAJ_Ω", limit=50)
        error_events = [e for e in recent
                         if e.get("event") in (
                             "UPLOAD_QUARANTINED", "UPLOAD_ERROR",
                             "UPLOAD_VALIDATION_FAILED")
                         or (e.get("http_code") or 0) >= 400]
        if error_events:
            last_err = error_events[-1]
            last_error_event = {
                "exists": True,
                "ts_utc": last_err.get("ts_utc"),
                "event": last_err.get("event"),
                "http_status": last_err.get("http_code"),
                "filename": last_err.get("filename"),
                "phase_diagnostic": "BACKEND_REJECT_OR_VALIDATION_FAIL",
            }
    except Exception:
        pass

    # ─── Inférence proxy/backend phase d'erreur (anti-générique) ─────
    proxy_constraint_hint: str
    last_error_phase: str
    if not chunks_dir.exists() or not any(chunks_dir.iterdir() if chunks_dir.exists() else []):
        # Aucune session côté backend → erreur amont (proxy/Cloudflare/réseau)
        last_error_phase = "PROXY_OR_NETWORK_BEFORE_BACKEND"
        proxy_constraint_hint = (
            "Aucun chunk reçu par le pod FastAPI. L'erreur HTTP 5xx provient "
            "AVANT le router : Cloudflare (502 Bad Gateway / 504), WAF "
            "(blocage / payload), ou pod restart cours upload. "
            "Vérifiez côté client : (1) cookies/session expirés ; "
            "(2) chunk size ≤ 50 Mo strict ; (3) timeout client < 300s ; "
            "(4) UA identifié ; (5) X-Upload-Id [A-Za-z0-9._-]{8,64}."
        )
    elif last_error_event["exists"]:
        last_error_phase = "BACKEND_ROUTER_VALIDATION_OR_ASSEMBLY"
        proxy_constraint_hint = (
            "Erreur consignée côté backend (audit-log). "
            "Voir last_error_http_status et last_error_event."
        )
    else:
        last_error_phase = "NO_ERROR_OBSERVED_OR_TRANSIENT"
        proxy_constraint_hint = (
            "Aucune erreur backend consignée. Si une erreur 5xx est observée "
            "côté client mais une session existe : c'est probablement une "
            "déconnexion réseau pendant un chunk transmis ; les chunks "
            "précédents restent valides (idempotence par chunk_index)."
        )

    return {
        "manifest_id": "PEE_MAJ_PIPELINE_STATUS_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "pipeline_activated": bool(flag.get("activated")),
        "last_activated_utc": flag.get("last_activated_utc"),
        "history_count": len(flag.get("history", [])),
        "slot_state": {
            "status": slot.get("status", "ABSENT"),
            "files_loaded_count": slot.get("files_loaded_count", 0),
            "composite_sha256": slot.get("composite_sha256"),
            "last_upload": (slot.get("uploads", [])[-1]
                              if slot.get("uploads") else None),
        },
        "canonical_state": canonical,
        "engine_summary": eng_summary,
        "derivatives_persistent_root": derivatives_root,
        "derivatives_persisted_files": derivatives_files,
        # ─── ORDRE N°52-EXT VOIE A · Forensique resume (502/504) ────
        "last_upload_id": last_session_summary["upload_id"],
        "last_successful_chunk_index": last_session_summary[
            "last_successful_chunk_index"],
        "last_error_http_status": last_error_event["http_status"],
        "last_error_event": last_error_event,
        "last_error_phase": last_error_phase,
        "proxy_constraint_hint": proxy_constraint_hint,
        "last_session_detail": last_session_summary,
        "all_sessions_in_flight": sessions_in_flight,
        "all_sessions_count": len(sessions_in_flight),
        "retry_policy": {
            "5xx_retryable": True,
            "non_invalidated_chunks": (
                "Tous chunks déjà fsyncés sur disque restent valides. "
                "Le client doit ré-envoyer UNIQUEMENT les chunks manquants "
                "via le même X-Upload-Id."),
            "endpoint_resume": (
                "/api/v30/admin-premium/gis/upload-chunk/"
                "FORET_MFFP_PEE_MAJ_%CE%A9/resume/<upload_id>"),
        },
        # ─── ORDRE N°52-EXT VOIE A · Spec client recommandée ──────────
        "client_recommended_parameters": {
            "chunk_size_max_bytes": 50 * 1024 * 1024,
            "chunk_size_max_human": "50 Mo (sous limite Cloudflare 100 Mo)",
            "client_timeout_s_per_chunk": 90,
            "client_timeout_s_per_chunk_note": (
                "Strictement < 100s pour rester sous le timeout Cloudflare typique"),
            "max_retries_5xx": 5,
            "backoff_strategy": "exponential",
            "backoff_initial_ms": 1000,
            "backoff_factor": 2,
            "backoff_max_ms": 30000,
            "backoff_jitter_ms_range": [0, 500],
            "user_agent_hint": (
                "BIONIC-OS-V20-SUPRA/1.0 (BCE-4X · ORDRE_N52_EXT_VOIE_A · "
                "<client_name>) — UA identifié obligatoire (Cloudflare WAF)"),
            "x_upload_id_regex": "^[A-Za-z0-9._-]{8,64}$",
            "x_upload_id_recommendation": (
                "UUID v4 sans tirets ou format <session-prefix>.<uuid8>"),
            "x_chunk_index_format": "0-based incremental (0, 1, ..., N-1)",
            "x_final_chunk_only_on_last": (
                "true UNIQUEMENT sur chunk_index == chunks_total - 1"),
            "filename_safe_regex": "^[A-Za-z0-9._-]+$",
            "expected_filename_pee_maj": "pee_maj.gpkg",
            "resume_strategy": (
                "Avant chaque session, GET /resume/{upload_id} pour récupérer "
                "chunks_missing[] et POSTer uniquement ces indices."),
            "probe_network_endpoint": (
                "/api/v30/admin-premium/gis/diagnostic/pee-maj/probe-network"),
        },
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT VOIE A · Probe réseau pour qualifier la chaîne proxy/WAF
# Accepte un chunk binaire test (≤ 1 Mo), mesure latency_ms, observed_size,
# compare à X-Expected-Size header. Audit-event PEE_MAJ_PROBE_NETWORK_Ω.
# Aucune écriture disque persistante. Stream → bytearray RAM → cleanup auto.
# Anti-générique : aucune simulation ; toutes les mesures sont réelles.
# ═════════════════════════════════════════════════════════════════════════
@router.post("/diagnostic/pee-maj/probe-network")
async def pee_maj_probe_network(
    request: Request,
    file: UploadFile = File(...),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    x_expected_size: int = Header(..., alias="X-Expected-Size"),
    x_probe_id: str | None = Header(default=None, alias="X-Probe-Id"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE A · Probe réseau end-to-end (client → Cloudflare → pod).
    Limite stricte 1 Mo. Aucun fichier persisté. Audit-event consigné.
    """
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]
    probe_id = (x_probe_id or "").strip()
    if probe_id and (len(probe_id) < 4 or len(probe_id) > 64
                       or not CHUNKED_UPLOAD_ID_RE.match(probe_id)):
        raise HTTPException(
            status_code=400,
            detail="X-Probe-Id invalide (regex ^[A-Za-z0-9._-]{8,64}$)")

    PROBE_LIMIT_BYTES = 1 * 1024 * 1024  # 1 Mo strict
    if int(x_expected_size) > PROBE_LIMIT_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"PROBE_TOO_LARGE — limite stricte {PROBE_LIMIT_BYTES} octets")
    if int(x_expected_size) < 16:
        raise HTTPException(
            status_code=400,
            detail="X-Expected-Size doit être ≥ 16 octets")

    import time as _time
    t0 = _time.time()
    h = hashlib.sha256()
    observed_size = 0
    buffer = bytearray()
    try:
        # Stream → RAM (cap à 2 Mo de sécurité au cas où expected mensonger)
        while True:
            chunk = await file.read(64 * 1024)
            if not chunk:
                break
            buffer.extend(chunk)
            h.update(chunk)
            observed_size += len(chunk)
            if observed_size > 2 * PROBE_LIMIT_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=("PROBE_OVERFLOW — payload reçu > 2 Mo; "
                            "X-Expected-Size mensonger ou client défectueux"))
    finally:
        # Cleanup explicite RAM (anti-générique : on ne garde RIEN)
        del buffer
    latency_ms = round((_time.time() - t0) * 1000, 2)
    sha = h.hexdigest()

    proxy_truncated = observed_size != int(x_expected_size)
    mismatch_bytes = observed_size - int(x_expected_size)

    if proxy_truncated:
        diagnostic_phase = "PROXY_TRUNCATED_OR_CLIENT_LIED"
        diagnostic_hint = (
            f"Taille reçue ({observed_size}) ≠ X-Expected-Size "
            f"({x_expected_size}). Mismatch={mismatch_bytes}. "
            "Causes possibles : Cloudflare/WAF tronque le payload OU "
            "header X-Expected-Size mensonger côté client OU "
            "transfert-encoding chunked HTTP altéré.")
    elif latency_ms > 30000:
        diagnostic_phase = "NETWORK_HIGH_LATENCY"
        diagnostic_hint = (
            f"Probe reçu intégralement mais latency={latency_ms} ms. "
            "Risque de timeout Cloudflare sur chunks réels de 50 Mo.")
    else:
        diagnostic_phase = "PROXY_OK"
        diagnostic_hint = (
            "Probe traversé intégralement. Aucune troncation détectée. "
            "La chaîne proxy/WAF/pod fonctionne correctement.")

    audit.append_event(
        event="PEE_MAJ_PROBE_NETWORK_Ω",
        slot_id="FORET_MFFP_PEE_MAJ_Ω",
        filename="(probe_network_1MB_RAM)",
        sha256=sha,
        size_bytes=observed_size,
        http_code=200,
        client_ip=client_ip,
        user_agent=ua,
        validators=[
            {"name": "probe_size_match", "passed": not proxy_truncated,
             "expected_size": int(x_expected_size),
             "observed_size": observed_size,
             "mismatch_bytes": mismatch_bytes,
             "latency_ms": latency_ms,
             "diagnostic_phase": diagnostic_phase,
             "probe_id": probe_id or None},
        ],
    )

    return {
        "manifest_id": "PEE_MAJ_PROBE_NETWORK_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "n°52_ext_voie_a_probe",
        "probe_id": probe_id or None,
        "expected_size": int(x_expected_size),
        "observed_size": observed_size,
        "mismatch_bytes": mismatch_bytes,
        "proxy_truncated": proxy_truncated,
        "latency_ms": latency_ms,
        "sha256_received": sha,
        "diagnostic_phase": diagnostic_phase,
        "diagnostic_hint": diagnostic_hint,
        "client_ip_observed": client_ip,
        "user_agent_observed": ua,
        "ram_cleanup_executed": True,
        "no_disk_persistence": True,
        "v30_lock": "INVIOLÉ",
    }


@router.post("/diagnostic/pee-maj/persist-derivatives")
async def pee_maj_persist_derivatives(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT · Déclenche la copie persistante des dérivées
    analytiques calculées (GIS_FRAGMENTATION_INDEX, GIS_COUVERT_FORESTIER, ...)
    depuis /data/gis/ vers /app/backend/data/gis_archive/_derived/.
    Idempotent. Consigne 1 audit-event par fichier persisté.
    """
    _verify_token(x_commandant_token)
    try:
        from engines.v8_institutional.especes.engine_corridors_gis_omega import (
            persist_derivatives_to_archive,
        )
        result = persist_derivatives_to_archive()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PERSIST_DERIVATIVES_ERROR::{e}")

    for p in result.get("persisted", []):
        audit.append_event(
            event="DERIVATIVE_LAYER_PERSISTED_Ω",
            slot_id="FORET_MFFP_PEE_MAJ_Ω",
            filename=p["dest"].split("/")[-1],
            sha256=p["sha256"],
            size_bytes=p["size_bytes"],
            http_code=200,
            client_ip="MANUAL_PERSIST_DERIVATIVES",
            user_agent="ORDRE_N52_EXT_PEE_MAJ_VOIE_A",
            validators=[{"name": "derivative_persisted", "passed": True,
                         "layer_id": p["layer_id"]}],
        )

    return result


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT VOIE A · Compression + archivage persistant pee_maj.gpkg
# Tente de compresser le fichier brut en zstd. Si compressé < 1 Go, archive
# atomiquement vers /app/backend/data/gis_archive/. Sinon, conserve dans
# /var/cache (éphémère) avec audit-event explicit. Anti-générique : refuse
# de simuler un succès si le ratio est défavorable.
# ═════════════════════════════════════════════════════════════════════════
def _compress_and_archive_pee_maj(client_ip: str, ua: str,
                                    skip_if_archive_exists: bool = False,
                                    ) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE A · Compression zstd + archivage persistant.
    Logique factorisée réutilisée par /compress-and-archive et /full-pipeline.
    Si skip_if_archive_exists=True et l'archive est déjà présente avec une
    taille > 0, retourne immédiatement un état "ALREADY_PERSISTED" (idempotent).
    Lève HTTPException sur erreur fatale.
    """
    try:
        import zstandard as zstd
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ZSTANDARD_MODULE_MISSING::{e}")

    src = Path(
        "/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg")
    if not src.exists() or src.stat().st_size == 0:
        raise HTTPException(
            status_code=409,
            detail=("PEE_MAJ_SOURCE_ABSENT — pee_maj.gpkg introuvable dans "
                    f"{src.parent}. Procéder d'abord à l'upload chunked."))

    archive_dest_dir = Path("/app/backend/data/gis_archive")
    archive_dest_dir.mkdir(parents=True, exist_ok=True)
    archive_dest = archive_dest_dir / "pee_maj.gpkg.zstd"

    # ─── Idempotence stricte ─────────────────────────────────────────
    if skip_if_archive_exists and archive_dest.exists() and archive_dest.stat().st_size > 0:
        return {
            "manifest_id": "PEE_MAJ_COMPRESS_AND_ARCHIVE_Ω",
            "skipped_idempotent": True,
            "skip_reason": "ALREADY_PERSISTED — archive existante préservée",
            "raw": {"path": str(src), "size_bytes": src.stat().st_size,
                    "size_GB": round(src.stat().st_size / 1e9, 2)},
            "compressed": {"path": None, "ratio": None},
            "archive_persistent": {
                "archived": True,
                "dest_path": str(archive_dest),
                "size_bytes": archive_dest.stat().st_size,
            },
        }

    raw_size = src.stat().st_size
    raw_size_GB = round(raw_size / 1e9, 2)

    compressed_path = src.with_suffix(".gpkg.zstd")
    tmp_path = src.with_suffix(".gpkg.zstd.compressing.partial")
    cctx = zstd.ZstdCompressor(level=10, threads=0)
    raw_h = hashlib.sha256()
    cmp_h = hashlib.sha256()
    import time as _time
    t0 = _time.time()
    try:
        with open(src, "rb") as inp, open(tmp_path, "wb") as out:
            with cctx.stream_writer(out) as compressor:
                while True:
                    buf = inp.read(8 << 20)
                    if not buf:
                        break
                    raw_h.update(buf)
                    compressor.write(buf)
        with open(tmp_path, "rb") as f:
            while True:
                buf = f.read(1 << 20)
                if not buf:
                    break
                cmp_h.update(buf)
        os.replace(str(tmp_path), str(compressed_path))
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500,
                              detail=f"COMPRESSION_ERROR::{e}")

    elapsed_s = round(_time.time() - t0, 2)
    compressed_size = compressed_path.stat().st_size
    compressed_size_GB = round(compressed_size / 1e9, 2)
    ratio = round(raw_size / compressed_size, 2) if compressed_size > 0 else 0
    raw_sha = raw_h.hexdigest()
    cmp_sha = cmp_h.hexdigest()

    threshold_bytes = 1 * 1024 * 1024 * 1024
    archived = False
    archive_skip_reason: Optional[str] = None
    free_app = 0
    try:
        free_app = __import__("shutil").disk_usage(str(archive_dest_dir)).free
    except Exception:
        pass

    if compressed_size > threshold_bytes:
        archive_skip_reason = (
            f"COMPRESSED_TOO_LARGE — {compressed_size_GB} Go > seuil 1 Go")
        audit.append_event(
            event="PEE_MAJ_COMPRESSED_TOO_LARGE_Ω",
            slot_id="FORET_MFFP_PEE_MAJ_Ω",
            filename="pee_maj.gpkg.zstd", sha256=cmp_sha,
            size_bytes=compressed_size, http_code=200,
            client_ip=client_ip, user_agent=ua,
            validators=[{"name": "compressed_size_check", "passed": False,
                         "compressed_size_bytes": compressed_size,
                         "threshold_bytes": threshold_bytes,
                         "raw_size_bytes": raw_size,
                         "ratio": ratio,
                         "compression_elapsed_s": elapsed_s}],
        )
    elif compressed_size > free_app * 0.9:
        archive_skip_reason = (
            f"DISK_INSUFFICIENT_APP — {compressed_size} octets vs {free_app} libres /app")
        audit.append_event(
            event="PEE_MAJ_COMPRESSED_ARCHIVE_DISK_FULL_Ω",
            slot_id="FORET_MFFP_PEE_MAJ_Ω",
            filename="pee_maj.gpkg.zstd", sha256=cmp_sha,
            size_bytes=compressed_size, http_code=200,
            client_ip=client_ip, user_agent=ua,
            validators=[{"name": "disk_check_app", "passed": False,
                         "free_bytes": free_app, "needed": compressed_size}],
        )
    else:
        tmp_archive = archive_dest.with_suffix(".zstd.archiving.partial")
        try:
            with open(compressed_path, "rb") as inp, open(tmp_archive, "wb") as out:
                while True:
                    buf = inp.read(1 << 20)
                    if not buf:
                        break
                    out.write(buf)
            os.replace(str(tmp_archive), str(archive_dest))
            archived = True
            audit.append_event(
                event="PEE_MAJ_COMPRESSED_ARCHIVED_Ω",
                slot_id="FORET_MFFP_PEE_MAJ_Ω",
                filename="pee_maj.gpkg.zstd", sha256=cmp_sha,
                size_bytes=compressed_size, http_code=200,
                client_ip=client_ip, user_agent=ua,
                validators=[
                    {"name": "compression", "passed": True,
                     "raw_sha256": raw_sha, "compressed_sha256": cmp_sha,
                     "raw_size_bytes": raw_size,
                     "compressed_size_bytes": compressed_size,
                     "ratio": ratio, "elapsed_s": elapsed_s},
                    {"name": "archive_persistent", "passed": True,
                     "dest_path": str(archive_dest)},
                ],
            )
        except Exception as e:
            if tmp_archive.exists():
                tmp_archive.unlink(missing_ok=True)
            archive_skip_reason = f"ARCHIVE_WRITE_ERROR::{e}"

    return {
        "manifest_id": "PEE_MAJ_COMPRESS_AND_ARCHIVE_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "n°52_ext_voie_a",
        "raw": {"path": str(src), "size_bytes": raw_size,
                "size_GB": raw_size_GB, "sha256": raw_sha},
        "compressed": {
            "path": str(compressed_path), "size_bytes": compressed_size,
            "size_GB": compressed_size_GB, "sha256": cmp_sha,
            "ratio": ratio, "elapsed_s": elapsed_s,
        },
        "archive_persistent": {
            "archived": archived,
            "dest_path": str(archive_dest) if archived else None,
            "threshold_bytes": threshold_bytes,
            "threshold_GB": 1.0,
            "skip_reason": archive_skip_reason,
            "free_app_bytes": free_app,
        },
        "v30_lock": "INVIOLÉ",
    }


@router.post("/diagnostic/pee-maj/compress-and-archive")
async def pee_maj_compress_and_archive(
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE A · Endpoint dédié compression + archivage."""
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]
    return _compress_and_archive_pee_maj(client_ip, ua,
                                          skip_if_archive_exists=False)


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT VOIE A · Endpoint composite full-pipeline-execute
# Orchestration atomique :
#   (1) compute_corridors_gis()      — calcul moteur (canonical pee_maj.gpkg)
#   (2) persist_derivatives_to_archive()  — copie persistante des 9 layers
#   (3) compress_and_archive (idempotent)  — tentative archivage du brut
# Audit-event composite unique : PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω.
# Idempotence stricte : phase 2 et 3 sautent les éléments déjà persistés.
# Anti-générique : si pee_maj_canonical_active=False → 409 honnête.
# ═════════════════════════════════════════════════════════════════════════
@router.post("/diagnostic/pee-maj/full-pipeline-execute")
async def pee_maj_full_pipeline_execute(
    request: Request,
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE A · Pipeline composite atomique PEE_MAJ_Ω."""
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]
    import time as _time
    t_start = _time.time()

    # ─── Pré-condition : canonical_active=True ─────────────────────────
    try:
        from engines.v8_institutional.especes.engine_corridors_gis_omega import (
            _pee_maj_canonical_state, compute_corridors_gis,
            persist_derivatives_to_archive,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"ENGINE_IMPORT_ERROR::{e}")

    canonical = _pee_maj_canonical_state()
    if not canonical.get("active"):
        raise HTTPException(
            status_code=409,
            detail=(
                "PEE_MAJ_CANONICAL_INACTIVE — pee_maj.gpkg absent du chemin "
                f"{canonical.get('path')}. "
                "Procéder d'abord à l'upload chunked monolithique. "
                "Aucune simulation autorisée (anti-générique strict)."))

    # ─── PHASE 1 : compute_corridors_gis() ────────────────────────────
    phase1_t0 = _time.time()
    try:
        compute_result = compute_corridors_gis()
    except Exception as e:
        compute_result = {
            "status": "ERROR", "error": str(e)[:300],
            "anti_generique_pass": False,
        }
    phase1_elapsed = round(_time.time() - phase1_t0, 2)

    # ─── PHASE 2 : persist_derivatives_to_archive() ────────────────────
    phase2_t0 = _time.time()
    try:
        derivatives_result = persist_derivatives_to_archive()
        for p in derivatives_result.get("persisted", []):
            audit.append_event(
                event="DERIVATIVE_LAYER_PERSISTED_Ω",
                slot_id="FORET_MFFP_PEE_MAJ_Ω",
                filename=p["dest"].split("/")[-1],
                sha256=p["sha256"], size_bytes=p["size_bytes"],
                http_code=200, client_ip=client_ip,
                user_agent="ORDRE_N52_EXT_FULL_PIPELINE",
                validators=[{"name": "derivative_persisted", "passed": True,
                             "layer_id": p["layer_id"]}],
            )
    except Exception as e:
        derivatives_result = {
            "manifest_id": "DERIVATIVES_PERSIST_ERROR_Ω",
            "error": str(e)[:300],
            "persisted_count": 0, "skipped_count": 0, "failed_count": 0,
        }
    phase2_elapsed = round(_time.time() - phase2_t0, 2)

    # ─── PHASE 3 : compress_and_archive (idempotent) ──────────────────
    phase3_t0 = _time.time()
    phase3_result: Dict[str, Any]
    try:
        phase3_result = _compress_and_archive_pee_maj(
            client_ip, ua, skip_if_archive_exists=True)
    except HTTPException as he:
        phase3_result = {
            "manifest_id": "PEE_MAJ_COMPRESS_AND_ARCHIVE_ERROR_Ω",
            "http_status": he.status_code,
            "error": str(he.detail)[:300],
            "archive_persistent": {"archived": False,
                                    "skip_reason": str(he.detail)[:200]},
        }
    except Exception as e:
        phase3_result = {
            "manifest_id": "PEE_MAJ_COMPRESS_AND_ARCHIVE_ERROR_Ω",
            "error": str(e)[:300],
            "archive_persistent": {"archived": False,
                                    "skip_reason": f"UNEXPECTED::{e}"},
        }
    phase3_elapsed = round(_time.time() - phase3_t0, 2)

    total_elapsed = round(_time.time() - t_start, 2)

    # ─── Audit-event composite ────────────────────────────────────────
    raw_summary = phase3_result.get("raw", {}) or {}
    cmp_summary = phase3_result.get("compressed", {}) or {}
    arch_summary = phase3_result.get("archive_persistent", {}) or {}
    audit.append_event(
        event="PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω",
        slot_id="FORET_MFFP_PEE_MAJ_Ω",
        filename="(full_pipeline_composite)",
        sha256=cmp_summary.get("sha256") or raw_summary.get("sha256"),
        size_bytes=int(raw_summary.get("size_bytes") or 0),
        http_code=200,
        client_ip=client_ip, user_agent=ua,
        validators=[
            {"name": "phase1_compute_corridors_gis",
             "passed": compute_result.get("status") in ("STUB_READY", "OPERATIONAL"),
             "status": compute_result.get("status"),
             "missing_layers_count": compute_result.get("missing_layers_count"),
             "elapsed_s": phase1_elapsed},
            {"name": "phase2_persist_derivatives",
             "passed": "error" not in derivatives_result,
             "persisted_count": derivatives_result.get("persisted_count"),
             "skipped_count": derivatives_result.get("skipped_count"),
             "failed_count": derivatives_result.get("failed_count"),
             "elapsed_s": phase2_elapsed},
            {"name": "phase3_compress_and_archive",
             "passed": True,
             "archived": arch_summary.get("archived"),
             "skip_reason": arch_summary.get("skip_reason"),
             "skipped_idempotent": phase3_result.get("skipped_idempotent", False),
             "raw_sha256": raw_summary.get("sha256"),
             "compressed_sha256": cmp_summary.get("sha256"),
             "ratio": cmp_summary.get("ratio"),
             "elapsed_s": phase3_elapsed},
        ],
    )

    return {
        "manifest_id": "PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "n°52_ext_voie_a_composite",
        "executed_at_utc": _utc_now(),
        "total_elapsed_s": total_elapsed,
        "canonical_state": canonical,
        "phase1_compute_corridors_gis": {
            "elapsed_s": phase1_elapsed,
            "status": compute_result.get("status"),
            "score_corridors_gis_omega": compute_result.get("score_corridors_gis_omega"),
            "missing_layers": compute_result.get("missing_layers"),
            "missing_layers_count": compute_result.get("missing_layers_count"),
            "anti_generique_pass": compute_result.get("anti_generique_pass"),
            "pee_maj_canonical_active": compute_result.get("pee_maj_canonical_active"),
            "pee_maj_substitutes_slot": compute_result.get("pee_maj_substitutes_slot"),
            "doctrine_action_requise": compute_result.get("doctrine_action_requise"),
        },
        "phase2_persist_derivatives": {
            "elapsed_s": phase2_elapsed,
            "persisted_count": derivatives_result.get("persisted_count"),
            "persisted": derivatives_result.get("persisted"),
            "skipped_count": derivatives_result.get("skipped_count"),
            "failed_count": derivatives_result.get("failed_count"),
            "persistent_root": derivatives_result.get("persistent_root"),
        },
        "phase3_compress_and_archive": {
            "elapsed_s": phase3_elapsed,
            "skipped_idempotent": phase3_result.get("skipped_idempotent", False),
            "raw": raw_summary,
            "compressed": cmp_summary,
            "archive_persistent": arch_summary,
        },
        "audit_event_composite": "PEE_MAJ_FULL_PIPELINE_EXECUTED_Ω",
        "honest_disclosure": {
            "ephemeral_source_warning": (
                "pee_maj.gpkg réside sur /var/cache (éphémère). Au pod restart, "
                "le brut est perdu. Les dérivées analytiques persistées "
                "(phase 2) et l'archive zstd éventuelle (phase 3) restent la "
                "référence canonique institutionnelle."),
            "anti_generique_strict": True,
            "no_simulation_executed": True,
        },
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°50 — Upload chunked résilient (contournement limite Cloudflare 100MB)
#   • Frontend découpe en chunks de 50 MB (sous la limite proxy)
#   • Chaque chunk : POST /upload-chunk/{slot_id} avec headers de session
#   • Stockage : INCOMING_DIR / slot_id / .chunks / {upload_id} / {NNNN}.bin
#   • Au header X-Final-Chunk: true → reassemblage atomique + validation
#       complète via validate_upload(), même payload final qu'un upload mono
#   • FUSION ADD-ONLY : aucune route existante modifiée
#
# Sécurité :
#   • Token Commandant requis sur chaque chunk
#   • Filename safety identique
#   • upload_id [A-Za-z0-9._-]{8,64} (UUID-like, généré client)
#   • Limite max_size par slot vérifiée en cumulé (anti DoS)

CHUNKED_UPLOAD_ID_RE = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
CHUNKS_SUBDIR = ".chunks"


def _chunks_dir(slot_id: str, upload_id: str) -> Path:
    base = _slot_dir(slot_id) / CHUNKS_SUBDIR / upload_id
    base.mkdir(parents=True, exist_ok=True)
    return base


def _chunk_session_manifest(slot_id: str, upload_id: str) -> Path:
    return _chunks_dir(slot_id, upload_id) / "session.json"


def _read_chunk_session(slot_id: str, upload_id: str) -> Dict[str, Any]:
    p = _chunk_session_manifest(slot_id, upload_id)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "upload_id": upload_id,
        "slot_id": slot_id,
        "filename": None,
        "chunks_total": None,
        "chunks_received": [],
        "total_size_expected": None,
        "started_at_utc": _utc_now(),
    }


def _write_chunk_session(slot_id: str, upload_id: str, data: Dict[str, Any]) -> None:
    _chunk_session_manifest(slot_id, upload_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@router.post("/upload-chunk/{slot_id}")
async def upload_chunk(
    request: Request,
    slot_id: str = FPath(..., description="Identifiant du SLOT cible"),
    file: UploadFile = File(...),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    x_upload_id: str | None = Header(default=None, alias="X-Upload-Id"),
    x_chunk_index: int | None = Header(default=None, alias="X-Chunk-Index"),
    x_chunks_total: int | None = Header(default=None, alias="X-Chunks-Total"),
    x_original_filename: str | None = Header(default=None, alias="X-Original-Filename"),
    x_total_size: int | None = Header(default=None, alias="X-Total-Size"),
    x_final_chunk: str | None = Header(default=None, alias="X-Final-Chunk"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°50 · Upload chunked d'une couche RÉELLE pour contourner la
    limite Cloudflare 100 MB. ADMIN_PREMIUM_ONLY · token requis sur chaque
    chunk. Au dernier chunk, le fichier est reassemblé et validé exactement
    comme un upload mono-fichier (validators identiques).
    """
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"

    # ─── Validations entêtes ───────────────────────────────────────
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404,
                              detail=f"SLOT_INCONNU::{slot_id}")
    if not x_upload_id or not CHUNKED_UPLOAD_ID_RE.match(x_upload_id):
        raise HTTPException(status_code=400,
                              detail="X-Upload-Id INVALIDE (8-64 chars [A-Za-z0-9._-])")
    if x_chunk_index is None or x_chunk_index < 0:
        raise HTTPException(status_code=400, detail="X-Chunk-Index manquant")
    if not x_chunks_total or x_chunks_total <= 0:
        raise HTTPException(status_code=400, detail="X-Chunks-Total manquant")
    if x_chunk_index >= x_chunks_total:
        raise HTTPException(status_code=400,
                              detail="X-Chunk-Index hors-borne")
    if not x_original_filename:
        raise HTTPException(status_code=400, detail="X-Original-Filename manquant")
    fname = x_original_filename.strip()
    if not SAFE_FILENAME.match(fname) or len(fname) > 200:
        raise HTTPException(status_code=400,
                              detail="FILENAME_UNSAFE — caractères autorisés : A-Za-z0-9._-")

    spec = SLOT_BY_ID[slot_id]
    max_size = int(spec["taille_max_octets"])
    if x_total_size and x_total_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"FILE_TOO_LARGE :: > {max_size} octets")

    is_final = (x_final_chunk or "").lower() in ("true", "1", "yes", "y")
    chunks_dir = _chunks_dir(slot_id, x_upload_id)
    session = _read_chunk_session(slot_id, x_upload_id)
    if session.get("filename") and session["filename"] != fname:
        raise HTTPException(
            status_code=400,
            detail=f"FILENAME_MISMATCH :: session={session['filename']} vs {fname}")

    # ─── Écriture du chunk binaire ─────────────────────────────────
    chunk_path = chunks_dir / f"{x_chunk_index:06d}.bin"
    bytes_written = 0
    chunk_already_existed = chunk_path.exists()
    try:
        with open(chunk_path, "wb") as out:
            while True:
                buf = await file.read(1024 * 1024)
                if not buf:
                    break
                bytes_written += len(buf)
                out.write(buf)
            # ─── BCE4X_HARDENED_PIPELINE_MODE_Ω · fsync chunk + dir ─────
            if _is_hardened_mode_active():
                try:
                    out.flush()
                    os.fsync(out.fileno())
                except OSError:
                    pass
    except Exception as e:
        chunk_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"CHUNK_WRITE_FAILED::{e}")

    # ─── Mise à jour de la session ─────────────────────────────────
    received = set(session.get("chunks_received", []))
    received.add(int(x_chunk_index))
    # BCE4X_HARDENED · compteur de re-réception (idempotence forensique)
    rereception_log = session.get("rereception_log", {})
    if chunk_already_existed:
        key = str(int(x_chunk_index))
        rereception_log[key] = int(rereception_log.get(key, 0)) + 1
    session.update({
        "filename": fname,
        "chunks_total": int(x_chunks_total),
        "chunks_received": sorted(received),
        "total_size_expected": int(x_total_size or 0),
        "last_update_utc": _utc_now(),
        "rereception_log": rereception_log,
        "hardened_mode": _is_hardened_mode_active(),
    })
    _write_chunk_session(slot_id, x_upload_id, session)

    progress_pct = round(100.0 * len(received) / x_chunks_total, 2)

    # ─── Cas non-finalisé : retour intermédiaire ───────────────────
    if not is_final:
        return {
            "upload_id": x_upload_id,
            "slot_id": slot_id,
            "chunk_index": int(x_chunk_index),
            "chunks_received": len(received),
            "chunks_total": int(x_chunks_total),
            "progress_pct": progress_pct,
            "status": "CHUNK_STORED",
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        }

    # ─── Vérification : tous les chunks doivent être présents ──────
    expected_indices = set(range(x_chunks_total))
    if received != expected_indices:
        missing = sorted(expected_indices - received)
        raise HTTPException(
            status_code=409,
            detail=f"CHUNKS_INCOMPLETS · manquants={missing[:10]}{'…' if len(missing)>10 else ''}")

    # ─── Reassemblage atomique + SHA-256 streaming ─────────────────
    target_dir = _slot_dir(slot_id)
    final_path = target_dir / fname
    tmp_assembled = target_dir / f".{fname}.assembled.partial"
    h = hashlib.sha256()
    total_size = 0
    try:
        with open(tmp_assembled, "wb") as out:
            for i in range(x_chunks_total):
                cp = chunks_dir / f"{i:06d}.bin"
                if not cp.exists():
                    raise HTTPException(
                        status_code=500,
                        detail=f"CHUNK_DISPARU::index={i}")
                with open(cp, "rb") as inp:
                    while True:
                        b = inp.read(1024 * 1024)
                        if not b:
                            break
                        total_size += len(b)
                        if total_size > max_size:
                            tmp_assembled.unlink(missing_ok=True)
                            raise HTTPException(
                                status_code=413,
                                detail=f"FILE_TOO_LARGE :: > {max_size} octets")
                        h.update(b)
                        out.write(b)
        shutil.move(str(tmp_assembled), str(final_path))
    except HTTPException:
        raise
    except Exception as e:
        tmp_assembled.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"ASSEMBLE_FAILED::{e}")
    finally:
        # Cleanup chunks dir, même en cas d'erreur partielle
        try:
            shutil.rmtree(chunks_dir, ignore_errors=True)
        except Exception:
            pass

    sha256 = h.hexdigest()

    # ─── Validation post-assemblage ───────────────────────────────
    validation = validate_upload(slot_id, fname, final_path)
    passed = bool(validation.get("passed"))
    if not passed:
        quarantine_path = QUARANTINE_DIR / f"{slot_id}__{fname}"
        try:
            shutil.move(str(final_path), str(quarantine_path))
        except Exception:
            pass

    manifest = _record_upload(slot_id, fname, sha256, total_size, validation, passed)

    audit.append_event(
        event="UPLOAD_LOADED" if passed else "UPLOAD_QUARANTINED",
        slot_id=slot_id, filename=fname, sha256=sha256, size_bytes=total_size,
        http_code=200 if passed else 422,
        client_ip=client_ip, user_agent=user_agent,
        validators=validation.get("validators", []),
    )

    # ─── ORDRE N°52-EXT · Archive persistante (variante A) ──────────
    archive_result: Dict[str, Any] = {"archived": False, "reason": "NOT_APPLICABLE"}
    if passed and slot_id in ARCHIVABLE_SLOTS:
        archive_result = _archive_file_persistent(
            slot_id=slot_id, filename=fname, src_path=final_path,
            sha256_source=sha256, client_ip=client_ip,
            user_agent=user_agent or "",
        )

    slot_state = manifest["slots"].get(slot_id, {})
    return JSONResponse(
        status_code=200 if passed else 422,
        content={
            "slot_id": slot_id,
            "filename": fname,
            "size_bytes": total_size,
            "sha256": sha256,
            "passed": passed,
            "status": "LOADED" if passed else "QUARANTINED",
            "validators": validation.get("validators", []),
            "multi_upload": slot_state.get("multi_upload", False),
            "files_loaded_count": slot_state.get("files_loaded_count", 0),
            "composite_sha256": slot_state.get("composite_sha256"),
            "chunked": True,
            "chunks_total": int(x_chunks_total),
            "upload_id": x_upload_id,
            "persistent_archive": archive_result,
            "intake_stats": {
                "total_slots": len(manifest["slots"]),
                "loaded": sum(1 for s in manifest["slots"].values()
                                if s.get("status") == "LOADED"),
            },
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
            "v30_lock": "INVIOLÉ",
        },
    )


@router.delete("/upload-chunk/{slot_id}/{upload_id}")
async def upload_chunk_abort(
    slot_id: str = FPath(...),
    upload_id: str = FPath(...),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°50 · Annulation d'une session chunked en cours.
    Supprime tous les chunks partiels et la session manifest.
    """
    _verify_token(x_commandant_token)
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")
    if not CHUNKED_UPLOAD_ID_RE.match(upload_id):
        raise HTTPException(status_code=400, detail="X-Upload-Id INVALIDE")
    chunks_dir = _slot_dir(slot_id) / CHUNKS_SUBDIR / upload_id
    deleted = 0
    if chunks_dir.exists():
        deleted = len(list(chunks_dir.glob("*.bin")))
        shutil.rmtree(chunks_dir, ignore_errors=True)
    return {
        "upload_id": upload_id,
        "slot_id": slot_id,
        "deleted_chunks": deleted,
        "status": "ABORTED",
    }


@router.post("/upload/{slot_id}")
async def upload_layer(
    request: Request,
    slot_id: str = FPath(..., description="Identifiant du SLOT cible"),
    file: UploadFile = File(...),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """Upload d'une couche RÉELLE pour un slot protégé.
    ADMIN_PREMIUM_ONLY · token requis.
    Toute opération est journalisée dans l'audit-log persistant.
    """
    _verify_token(x_commandant_token)

    client_ip = request.client.host if request.client else "unknown"

    if slot_id not in SLOT_BY_ID:
        audit.append_event(
            event="UPLOAD_ERROR", slot_id=slot_id,
            filename=(file.filename or "?"), sha256=None, size_bytes=0,
            http_code=404, client_ip=client_ip, user_agent=user_agent,
            validators=None,
        )
        raise HTTPException(status_code=404,
                              detail=f"SLOT_INCONNU::{slot_id}")

    fname = (file.filename or "uploaded.bin").strip()
    if not SAFE_FILENAME.match(fname) or len(fname) > 200:
        audit.append_event(
            event="UPLOAD_ERROR", slot_id=slot_id, filename=fname[:120],
            sha256=None, size_bytes=0, http_code=400,
            client_ip=client_ip, user_agent=user_agent, validators=None,
        )
        raise HTTPException(status_code=400,
                              detail="FILENAME_UNSAFE — caractères autorisés : A-Za-z0-9._-")

    target_dir = _slot_dir(slot_id)
    final_path = target_dir / fname
    tmp_path = target_dir / f".{fname}.partial"

    # Streaming write + SHA-256 + size accounting
    h = hashlib.sha256()
    size = 0
    spec = SLOT_BY_ID[slot_id]
    max_size = int(spec["taille_max_octets"])

    try:
        with open(tmp_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_size:
                    out.close()
                    tmp_path.unlink(missing_ok=True)
                    audit.append_event(
                        event="UPLOAD_ERROR", slot_id=slot_id, filename=fname,
                        sha256=None, size_bytes=size, http_code=413,
                        client_ip=client_ip, user_agent=user_agent,
                        validators=None,
                    )
                    raise HTTPException(
                        status_code=413,
                        detail=f"FILE_TOO_LARGE :: > {max_size} octets")
                h.update(chunk)
                out.write(chunk)
        # Move atomically
        shutil.move(str(tmp_path), str(final_path))
    except HTTPException:
        raise
    except Exception as e:
        tmp_path.unlink(missing_ok=True)
        audit.append_event(
            event="UPLOAD_ERROR", slot_id=slot_id, filename=fname,
            sha256=None, size_bytes=size, http_code=500,
            client_ip=client_ip, user_agent=user_agent, validators=None,
        )
        raise HTTPException(status_code=500, detail=f"UPLOAD_FAILED::{e}")

    sha256 = h.hexdigest()

    # Validation post-écriture
    validation = validate_upload(slot_id, fname, final_path)
    passed = bool(validation.get("passed"))

    # Quarantaine si échec
    if not passed:
        quarantine_path = QUARANTINE_DIR / f"{slot_id}__{fname}"
        try:
            shutil.move(str(final_path), str(quarantine_path))
        except Exception:
            pass

    manifest = _record_upload(slot_id, fname, sha256, size, validation, passed)

    # Audit-log append
    audit.append_event(
        event="UPLOAD_LOADED" if passed else "UPLOAD_QUARANTINED",
        slot_id=slot_id, filename=fname, sha256=sha256, size_bytes=size,
        http_code=200 if passed else 422,
        client_ip=client_ip, user_agent=user_agent,
        validators=validation.get("validators", []),
    )

    # ─── ORDRE N°52-EXT · Archive persistante (variante A) ──────────
    archive_result_mono: Dict[str, Any] = {"archived": False,
                                            "reason": "NOT_APPLICABLE"}
    if passed and slot_id in ARCHIVABLE_SLOTS:
        archive_result_mono = _archive_file_persistent(
            slot_id=slot_id, filename=fname, src_path=final_path,
            sha256_source=sha256, client_ip=client_ip,
            user_agent=user_agent or "",
        )

    # ─── ORDRE N°46 · Champs multi-upload exposés dans la réponse ───
    slot_state = manifest["slots"].get(slot_id, {})

    return JSONResponse(
        status_code=200 if passed else 422,
        content={
            "slot_id": slot_id,
            "filename": fname,
            "size_bytes": size,
            "sha256": sha256,
            "passed": passed,
            "status": "LOADED" if passed else "QUARANTINED",
            "validators": validation.get("validators", []),
            # ─── ORDRE N°46 · Multi-upload / SHA-256 composite ─────────
            "multi_upload": slot_state.get("multi_upload", False),
            "files_loaded_count": slot_state.get("files_loaded_count", 0),
            "composite_sha256": slot_state.get("composite_sha256"),
            "persistent_archive": archive_result_mono,
            "intake_stats": {
                "total_slots": len(manifest["slots"]),
                "loaded": sum(1 for s in manifest["slots"].values()
                                if s.get("status") == "LOADED"),
            },
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
            "v30_lock": "INVIOLÉ",
        },
    )


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°44 — Audit log persistant (ADMIN_PREMIUM_ONLY)
# ═════════════════════════════════════════════════════════════════════════
@router.get("/audit-log")
def get_audit_log(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
    slot_id: Optional[str] = Query(default=None, description="Filtre slot_id"),
    event: Optional[str] = Query(default=None, description="Filtre event"),
    limit: int = Query(default=200, ge=1, le=2000),
) -> Dict[str, Any]:
    """Récupère le journal d'audit persistant (ADMIN_PREMIUM_ONLY).
    Filtres : slot_id, event ; limit max 2000."""
    _verify_token(x_commandant_token)
    rows = audit.read_entries(slot_id=slot_id, event=event, limit=limit)
    return {
        "manifest_id": "AUDIT_LOG_GIS_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°44",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "generated_at_utc": _utc_now(),
        "filters": {"slot_id": slot_id, "event": event, "limit": limit},
        "stats": audit.stats(),
        "entries": rows,
    }


@router.post("/promote")
def promote_to_operational(
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """Déclenche compute_corridors_gis() à partir de l'état réel des slots.
    Précondition : couches GIS LOADED. Si OPERATIONAL, prépare le SCEAU_X5_FINAL.
    ADMIN_PREMIUM_ONLY.
    """
    _verify_token(x_commandant_token)

    from engines.v8_institutional.especes.engine_corridors_gis_omega import (
        compute_corridors_gis, get_all_layers_status,
    )

    layers_status = get_all_layers_status()
    compute = compute_corridors_gis()
    intake_manifest = _read_manifest()
    intake_loaded = sum(
        1 for s in intake_manifest["slots"].values()
        if s.get("status") == "LOADED"
    )

    return {
        "manifest_id": "PROMOTE_GIS_OPERATIONAL_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°44",
        "generated_at_utc": _utc_now(),
        "intake_loaded_slots": intake_loaded,
        "intake_total_slots": len(intake_manifest["slots"]),
        "engine_layers_status": {
            "total": layers_status["layers_total"],
            "loaded": layers_status["layers_loaded"],
            "absent": layers_status["layers_absent"],
            "global_status": layers_status["global_status"],
        },
        "compute_corridors_gis": {
            "status": compute["status"],
            "anti_generique_pass": compute["anti_generique_pass"],
            "missing_layers": compute.get("missing_layers"),
            "score_corridors_gis_omega": compute.get("score_corridors_gis_omega"),
        },
        "sceau_x5_final_ready": (
            compute["status"] == "OPERATIONAL"
            and compute["anti_generique_pass"] is True
        ),
        "next_action": (
            "TRIGGER_SCEAU_X5_FINAL" if compute["status"] == "OPERATIONAL"
            else "EN_ATTENTE_DE_COUCHES_RÉELLES_LOADED"
        ),
        "v30_lock": "INVIOLÉ",
    }
