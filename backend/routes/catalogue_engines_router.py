"""
catalogue_engines_router.py — Endpoint HTTPS téléchargement CATALOGUE ENGINES BIONIC
====================================================================================
Expose le fichier CATALOGUE_ENGINES_BIONIC_Ω.md en lecture publique + téléchargement.

Endpoints :
  GET /api/catalogue-engines/view      → Markdown texte (visualisable navigateur)
  GET /api/catalogue-engines/download  → Téléchargement (.md attachment)
  GET /api/catalogue-engines/html      → Rendu HTML simple (lecture browser)
  GET /api/catalogue-engines/status    → Métadonnées (taille, SHA-256)
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse

CATALOGUE_PATH = Path("/app/memory/CATALOGUE_ENGINES_BIONIC_Ω.md")
CATALOGUE_SHA_PATH = Path("/app/memory/CATALOGUE_ENGINES_BIONIC_Ω.md.sha256")

router = APIRouter(prefix="/api/catalogue-engines", tags=["CATALOGUE_ENGINES_BIONIC"])


def _sha256() -> str:
    if CATALOGUE_SHA_PATH.exists():
        return CATALOGUE_SHA_PATH.read_text().strip().split()[0]
    if not CATALOGUE_PATH.exists():
        return ""
    h = hashlib.sha256()
    h.update(CATALOGUE_PATH.read_bytes())
    return h.hexdigest()


@router.get("/status")
async def status():
    if not CATALOGUE_PATH.exists():
        raise HTTPException(status_code=404, detail="Catalogue not found")
    stat = CATALOGUE_PATH.stat()
    return JSONResponse({
        "filename": CATALOGUE_PATH.name,
        "size_bytes": stat.st_size,
        "sha256": _sha256(),
        "endpoints": {
            "view_markdown": "/api/catalogue-engines/view",
            "download": "/api/catalogue-engines/download",
            "view_html": "/api/catalogue-engines/html",
        },
    })


@router.get("/view", response_class=PlainTextResponse)
async def view_markdown():
    if not CATALOGUE_PATH.exists():
        raise HTTPException(status_code=404, detail="Catalogue not found")
    return PlainTextResponse(
        CATALOGUE_PATH.read_text(encoding="utf-8"),
        media_type="text/markdown; charset=utf-8",
    )


@router.get("/download")
async def download():
    if not CATALOGUE_PATH.exists():
        raise HTTPException(status_code=404, detail="Catalogue not found")
    return FileResponse(
        path=str(CATALOGUE_PATH),
        filename="CATALOGUE_ENGINES_BIONIC.md",
        media_type="text/markdown",
        headers={
            "Content-Disposition": 'attachment; filename="CATALOGUE_ENGINES_BIONIC.md"',
            "X-Catalogue-SHA256": _sha256(),
        },
    )


@router.get("/html", response_class=HTMLResponse)
async def view_html():
    """Rendu HTML minimal du Markdown pour lecture navigateur."""
    if not CATALOGUE_PATH.exists():
        raise HTTPException(status_code=404, detail="Catalogue not found")
    md = CATALOGUE_PATH.read_text(encoding="utf-8")
    # Rendu minimal sans dépendance externe
    try:
        import markdown
        body_html = markdown.markdown(md, extensions=["tables", "fenced_code"])
    except Exception:
        # Fallback : <pre> brut
        body_html = f"<pre style='white-space:pre-wrap;font-family:monospace'>{md}</pre>"

    html = f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="utf-8">
<title>CATALOGUE ENGINES BIONIC Ω</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 1200px;
          margin: 2rem auto; padding: 0 2rem; line-height: 1.55; color: #222; }}
  h1, h2, h3 {{ border-bottom: 2px solid #FF8F00; padding-bottom: 4px; }}
  h1 {{ color: #CC0000; }}
  h2 {{ color: #FF6600; margin-top: 2.5rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #222; color: #fff; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
  pre {{ background: #1a1a1a; color: #FFD700; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
  .download {{ display: inline-block; margin: 1rem 0; padding: 10px 20px; background: #FF8F00;
               color: #fff; text-decoration: none; border-radius: 4px; font-weight: bold; }}
  .download:hover {{ background: #CC7000; }}
</style>
</head><body>
<a class="download" href="/api/catalogue-engines/download">⬇ Télécharger CATALOGUE_ENGINES_BIONIC.md</a>
{body_html}
<hr><p style="color:#888;font-size:0.85em;text-align:center">
SHA-256 : {_sha256()}
</p>
</body></html>"""
    return HTMLResponse(html)
