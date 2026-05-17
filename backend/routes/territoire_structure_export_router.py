"""
P22ΩΩ_TERRITOIRE_STRUCTURE_EXPORT · 2026-05-17 · COMMANDANT STEEVE-MAX
======================================================================
Endpoint exposant le JSON maître de la structure TERRITOIRE Ω.
Téléchargeable directement via GET /api/export/territoire-structure.

Source de vérité : /app/memory/TERRITOIRE_STRUCTURE_OMEGA.json
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

router = APIRouter(prefix="/api/export", tags=["export"])

JSON_PATH = Path("/app/memory/TERRITOIRE_STRUCTURE_OMEGA.json")


@router.get("/territoire-structure")
async def export_territoire_structure(download: bool = True):
    """Retourne le JSON maître structure TERRITOIRE Ω.

    Query params:
      download=true  (par défaut) → FileResponse attachment (téléchargeable)
      download=false → JSONResponse inline (visualisation)
    """
    if not JSON_PATH.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "TERRITOIRE_STRUCTURE_OMEGA.json not found", "path": str(JSON_PATH)},
        )
    if download:
        return FileResponse(
            path=str(JSON_PATH),
            media_type="application/json",
            filename="TERRITOIRE_STRUCTURE_OMEGA.json",
        )
    import json
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


@router.get("/territoire-structure/meta")
async def territoire_structure_meta():
    """Retourne uniquement les métadonnées du JSON maître (taille, date, etc.)."""
    if not JSON_PATH.exists():
        return JSONResponse(status_code=404, content={"error": "not found"})
    import json
    stat = JSON_PATH.stat()
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {
        "filename": "TERRITOIRE_STRUCTURE_OMEGA.json",
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 2),
        "metadata": data.get("_metadata", {}),
        "download_url": "/api/export/territoire-structure?download=true",
        "inline_url": "/api/export/territoire-structure?download=false",
    }
