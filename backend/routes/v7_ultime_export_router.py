"""
v7_ultime_export_router.py — Endpoint HTTPS de téléchargement V7 ULTIME
========================================================================
PHASE_XI_SUPRA_RAPATRIEMENT_TERRITOIRE_V7_ULTIME_Ω
VERSION_X195-SUPRA-EXTRACTION-INTÉGRALE-Ω — AMENDEMENT-ABSOLU

Expose les artefacts rapatriés de TERRITOIRE V7 ULTIME par HTTPS :
  - GET /api/v7-ultime-export/manifest       → lit MANIFEST.txt
  - GET /api/v7-ultime-export/download       → sert V7_ULTIME_FULL.tar.gz
  - GET /api/v7-ultime-export/sha256         → sert V7_ULTIME_FULL.tar.gz.sha256
  - GET /api/v7-ultime-export/list           → liste du contenu de l'archive
  - GET /api/v7-ultime-export/status         → métadonnées du rapatriement

Aucune transformation. Contenu brut. Signature SHA-256.
Commandant STEEVE-MAX — directive X195 §2.
"""
from __future__ import annotations

import hashlib
import os
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

EXPORT_DIR = Path("/app/memory/V7_ULTIME_EXPORT")
ARCHIVE_FILE = EXPORT_DIR / "V7_ULTIME_FULL.tar.gz"
SHA256_FILE = EXPORT_DIR / "V7_ULTIME_FULL.tar.gz.sha256"
MANIFEST_FILE = EXPORT_DIR / "MANIFEST.txt"

router = APIRouter(prefix="/api/v7-ultime-export", tags=["V7_ULTIME_EXPORT_X195"])


def _read_sha256() -> str:
    if SHA256_FILE.exists():
        txt = SHA256_FILE.read_text().strip()
        return txt.split()[0] if txt else ""
    if not ARCHIVE_FILE.exists():
        return ""
    # Calcul si fichier de signature absent
    h = hashlib.sha256()
    with ARCHIVE_FILE.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@router.get("/status")
async def v7_export_status():
    """Métadonnées du rapatriement V7 ULTIME."""
    if not ARCHIVE_FILE.exists():
        raise HTTPException(status_code=404, detail="V7 ULTIME archive not found")
    stat = ARCHIVE_FILE.stat()
    return JSONResponse({
        "phase": "PHASE_XI_SUPRA_RAPATRIEMENT_TERRITOIRE_V7_ULTIME_Ω",
        "version": "X195-SUPRA-EXTRACTION-INTÉGRALE-Ω-AMENDEMENT-ABSOLU",
        "commandant": "STEEVE-MAX",
        "archive_filename": ARCHIVE_FILE.name,
        "archive_size_bytes": stat.st_size,
        "archive_size_mb": round(stat.st_size / (1024 * 1024), 3),
        "sha256": _read_sha256(),
        "generated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "download_url": "/api/v7-ultime-export/download",
        "sha256_url": "/api/v7-ultime-export/sha256",
        "manifest_url": "/api/v7-ultime-export/manifest",
        "list_url": "/api/v7-ultime-export/list",
        "waypoint_canonique": [48.206657, -68.382422],
        "non_transformation": True,
        "non_filtering": True,
        "content_raw": True,
    })


@router.get("/manifest", response_class=PlainTextResponse)
async def v7_export_manifest():
    if not MANIFEST_FILE.exists():
        raise HTTPException(status_code=404, detail="MANIFEST.txt not found")
    return PlainTextResponse(MANIFEST_FILE.read_text(encoding="utf-8"))


@router.get("/sha256", response_class=PlainTextResponse)
async def v7_export_sha256():
    if not SHA256_FILE.exists():
        raise HTTPException(status_code=404, detail="SHA256 signature not found")
    return PlainTextResponse(SHA256_FILE.read_text(encoding="utf-8"))


@router.get("/download")
async def v7_export_download():
    if not ARCHIVE_FILE.exists():
        raise HTTPException(status_code=404, detail="V7 ULTIME archive not available")
    return FileResponse(
        path=str(ARCHIVE_FILE),
        filename=ARCHIVE_FILE.name,
        media_type="application/gzip",
        headers={
            "Content-Disposition": f'attachment; filename="{ARCHIVE_FILE.name}"',
            "X-V7-Ultime-SHA256": _read_sha256(),
            "X-Phase": "X195-SUPRA-EXTRACTION-INTÉGRALE-Ω",
        },
    )


@router.get("/list")
async def v7_export_list():
    """Liste exhaustive du contenu de l'archive (non filtré)."""
    if not ARCHIVE_FILE.exists():
        raise HTTPException(status_code=404, detail="V7 ULTIME archive not available")
    entries: List[str] = []
    try:
        with tarfile.open(ARCHIVE_FILE, "r:gz") as tf:
            for m in tf.getmembers():
                entries.append(m.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Archive read error: {e}")
    return JSONResponse({
        "archive": ARCHIVE_FILE.name,
        "total_entries": len(entries),
        "sha256": _read_sha256(),
        "entries": entries,
    })
