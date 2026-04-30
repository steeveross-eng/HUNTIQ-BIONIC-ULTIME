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
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Path as FPath
from fastapi.responses import JSONResponse

from engines.v8_institutional.especes.gis_reception_validators_omega import (
    SLOTS_GIS_PROTÉGÉS_SPEC,
    SLOT_BY_ID,
    list_slots,
    validate_upload,
)


router = APIRouter(
    prefix="/api/v30/admin-premium/gis",
    tags=["v30-admin-premium-gis-reception"],
)

# ═════════════════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════════════════
RECEPTION_ROOT = Path("/app/backend/data/gis_operational")
INCOMING_DIR = RECEPTION_ROOT / "incoming"
QUARANTINE_DIR = RECEPTION_ROOT / "quarantine"
MANIFEST_PATH = RECEPTION_ROOT / "GIS_RECEPTION_INTAKE_Ω.json"

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
    if not x_commandant_token or x_commandant_token != expected:
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
    slot["uploads"].append(entry)
    if passed:
        slot["status"] = "LOADED"
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


@router.post("/upload/{slot_id}")
async def upload_layer(
    slot_id: str = FPath(..., description="Identifiant du SLOT cible"),
    file: UploadFile = File(...),
    x_commandant_token: str | None = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """Upload d'une couche RÉELLE pour un slot protégé.
    ADMIN_PREMIUM_ONLY · token requis.
    """
    _verify_token(x_commandant_token)

    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404,
                              detail=f"SLOT_INCONNU::{slot_id}")

    fname = (file.filename or "uploaded.bin").strip()
    if not SAFE_FILENAME.match(fname) or len(fname) > 200:
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
            "intake_stats": {
                "total_slots": len(manifest["slots"]),
                "loaded": sum(1 for s in manifest["slots"].values()
                                if s.get("status") == "LOADED"),
            },
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
            "v30_lock": "INVIOLÉ",
        },
    )
