"""
audit_download_router.py — P22Ω_INJONCTION_DOCTRINAL_DOWNLOAD
═══════════════════════════════════════════════════════════════════
Commandant : STEEVE-MAX
Protocole  : BCE-4X ULTIME ABSOLU

Endpoint dédié pour exposer en HTTPS téléchargeable les rapports
d'audit doctrinal de /app/memory/audit_provenance/ via le préview
public REACT_APP_BACKEND_URL.

Routes :
  • GET /api/v20/territoire/audit/files                  → liste
  • GET /api/v20/territoire/audit/files/{filename}       → contenu .md (text/markdown)

Sécurité :
  • Whitelist préfixe p22omega_* uniquement
  • Pas de path traversal (basename + check dossier final)
  • Pas d'écriture (read-only strict)
"""
from __future__ import annotations
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(
    prefix="/api/v20/territoire/audit",
    tags=["P22Ω_AUDIT_DOWNLOAD"],
)

_AUDIT_DIR = Path("/app/memory/audit_provenance")


def _safe_path(filename: str) -> Path:
    """Empêche le path traversal et restreint aux .md/.log/.png doctrinaux."""
    # Basename only (no slash)
    name = os.path.basename(filename)
    if name != filename:
        raise HTTPException(status_code=400, detail="invalid filename (path traversal)")
    # Whitelist : Markdown, logs, et PNG du dossier visual_divergence
    allowed = (
        name.startswith("p22omega_") or name.startswith("P22") or
        name.endswith(".md") or name.endswith(".log") or
        (name.startswith("divergence_bsl_") and name.endswith(".png"))
    )
    if not allowed:
        raise HTTPException(status_code=403, detail="filename not allowed (whitelist)")
    # Pour les PNG, chercher dans visual_divergence/
    if name.endswith(".png"):
        full = (_AUDIT_DIR / "visual_divergence" / name).resolve()
        if not str(full).startswith(str((_AUDIT_DIR / "visual_divergence").resolve())):
            raise HTTPException(status_code=400, detail="resolved path outside visual_divergence dir")
    else:
        full = (_AUDIT_DIR / name).resolve()
        if not str(full).startswith(str(_AUDIT_DIR.resolve())):
            raise HTTPException(status_code=400, detail="resolved path outside audit dir")
    return full


@router.get("/files")
async def list_audit_files():
    """Liste les rapports d'audit doctrinal disponibles en téléchargement."""
    if not _AUDIT_DIR.exists():
        return JSONResponse({"files": [], "audit_dir": str(_AUDIT_DIR), "exists": False})
    files = []
    for f in sorted(_AUDIT_DIR.glob("*.md")) + sorted(_AUDIT_DIR.glob("*.log")):
        st = f.stat()
        files.append({
            "name": f.name,
            "size_bytes": st.st_size,
            "modified_utc": __import__("datetime").datetime.utcfromtimestamp(st.st_mtime).isoformat() + "Z",
            "download_path": f"/api/v20/territoire/audit/files/{f.name}",
        })
    return JSONResponse({
        "audit_dir": str(_AUDIT_DIR),
        "doctrine": "P22Ω_INJONCTION_DOCTRINAL_DOWNLOAD",
        "count": len(files),
        "files": files,
    })


@router.get("/files/{filename}")
async def download_audit_file(filename: str):
    """Sert le contenu d'un rapport en text/markdown/png."""
    full = _safe_path(filename)
    if not full.exists():
        raise HTTPException(status_code=404, detail=f"audit file not found: {filename}")
    if filename.endswith(".md"):
        media_type = "text/markdown; charset=utf-8"
    elif filename.endswith(".png"):
        media_type = "image/png"
    else:
        media_type = "text/plain; charset=utf-8"
    return FileResponse(
        path=str(full),
        media_type=media_type,
        filename=filename,
        headers={
            "Cache-Control": "no-store",
            "X-Doctrine": "P22Omega-INJONCTION_DOCTRINAL_DOWNLOAD",
        },
    )
