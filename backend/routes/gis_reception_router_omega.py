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
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
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
    """
    _verify_token(x_commandant_token)

    manifest = _read_manifest()
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
        "engine_layers": engine_layers,
        "audit_log_stats": audit_stats,
        "v30_lock": v30,
        "flags": {
            "prep_only_mode": os.environ.get("PREP_ONLY", "true"),
            "incoming_root": str(INCOMING_DIR),
            "quarantine_root": str(QUARANTINE_DIR),
            "manifest_path": str(MANIFEST_PATH),
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
    try:
        with open(chunk_path, "wb") as out:
            while True:
                buf = await file.read(1024 * 1024)
                if not buf:
                    break
                bytes_written += len(buf)
                out.write(buf)
    except Exception as e:
        chunk_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"CHUNK_WRITE_FAILED::{e}")

    # ─── Mise à jour de la session ─────────────────────────────────
    received = set(session.get("chunks_received", []))
    received.add(int(x_chunk_index))
    session.update({
        "filename": fname,
        "chunks_total": int(x_chunks_total),
        "chunks_received": sorted(received),
        "total_size_expected": int(x_total_size or 0),
        "last_update_utc": _utc_now(),
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
