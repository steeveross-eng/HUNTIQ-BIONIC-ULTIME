"""AUDIT_SUPRA_CORRIDORS_REPORT_Ω · Endpoint HTTPS téléchargeable
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · FUSION ADD-ONLY · V30_LOCK

Sert le rapport supra-détaillé (Markdown brut) en HTTPS public, sans
authentification, sans compression, sans troncature.

Endpoints :
  GET /api/v20/audit/corridors-supra-report.md  → text/markdown brut
  GET /api/v20/audit/corridors-supra-report.txt → text/plain (alias)
  GET /api/v20/audit/corridors-supra-report     → JSON {url, size, sha256, generated_at}
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response

router = APIRouter(prefix="/api/v20/audit", tags=["AUDIT_SUPRA_CORRIDORS_Ω"])

REPORT_PATH = Path("/app/memory/AUDIT_SUPRA_CORRIDORS_V90.md")


def _read_report() -> bytes:
    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Rapport non trouvé : {REPORT_PATH}",
        )
    return REPORT_PATH.read_bytes()


@router.get("/corridors-supra-report.md")
async def get_report_markdown() -> Response:
    """Sert le rapport en text/markdown brut (téléchargeable directement)."""
    data = _read_report()
    return Response(
        content=data,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Length": str(len(data)),
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="AUDIT_SUPRA_CORRIDORS_V90.md"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/corridors-supra-report.txt")
async def get_report_text() -> PlainTextResponse:
    """Alias text/plain pour clients ne supportant pas text/markdown."""
    data = _read_report().decode("utf-8")
    return PlainTextResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="AUDIT_SUPRA_CORRIDORS_V90.txt"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/corridors-supra-report")
async def get_report_meta() -> dict:
    """Métadonnées JSON : URL téléchargement, taille, SHA256, date."""
    data = _read_report()
    stat = REPORT_PATH.stat()
    sha = hashlib.sha256(data).hexdigest()
    return {
        "ok": True,
        "engine": "AUDIT_SUPRA_CORRIDORS_Ω",
        "report_path": str(REPORT_PATH),
        "size_bytes": len(data),
        "size_kb": round(len(data) / 1024, 2),
        "sha256": sha,
        "mtime": stat.st_mtime,
        "download_url_md":   "/api/v20/audit/corridors-supra-report.md",
        "download_url_txt":  "/api/v20/audit/corridors-supra-report.txt",
        "media_type":        "text/markdown; charset=utf-8",
        "encoding":          "UTF-8",
        "compression":       "none",
        "authentication":    "none (audit institutionnel ouvert)",
        "doctrine":          "V90 · BCE-4X ULTIME ABSOLU",
    }
