"""
LEP-INGESTION-Ω — BIONIC INGESTION-FGDB+GEOJSON-Ω-V1.0 (Phase XI-SUPRA-D)
==========================================================================
Ingestion institutionnelle des données LEP (Critical Habitat) ECCC :
  - Source primaire : FGDB (.gdb / .zip) officielle ECCC CWS_SCF/CriticalHabitat
  - Source secondaire : GeoJSON export optimisé front-end
  - Stockage persistent : /app/data/territoire_omega/
  - Hashes SHA-256 + registry.json institutionnel
  - Signature ESI-Ω automatique

États possibles :
  - NOT_INGESTED : aucune donnée (état initial)
  - INGESTED     : FGDB + GeoJSON présents, hashes validés
  - UNAVAILABLE_NETWORK_BLOCKED : source officielle inaccessible depuis le pod
                                  (interdit tout seed simulé — directive STEEVE-MAX)

Endpoints admin :
  POST /api/v20/territoire/lep/ingest             (upload multipart FGDB zip/gdb)
  POST /api/v20/territoire/lep/ingest-path        (path local déjà présent)
  GET  /api/v20/territoire/lep/status
  GET  /api/v20/territoire/lep/registry
  GET  /api/v20/territoire/lep/geojson/{layer}    (servir GeoJSON vers frontend)
  GET  /api/v20/territoire/lep/geojson-list
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "LEP-INGESTION-Ω",
    "V1.0-PHASE-XI-SUPRA-D-2026-04",
    "INGESTION-FGDB+GEOJSON-Ω-V1.0 — Critical Habitat ECCC (FGDB primaire, GeoJSON secondaire)",
    "GOUVERNANCE",
    ["ECCC_CWS_SCF_CriticalHabitat"],
)

router = APIRouter(prefix="/api/v20/territoire/lep", tags=["V20 LEP Ingestion"])

# ------------------------------------------------------------------
# Stockage persistent institutionnel
# ------------------------------------------------------------------
ROOT = Path("/app/data/territoire_omega")
FGDB_DIR = ROOT / "data_primary_fgdb_lep"
GEOJSON_DIR = ROOT / "data_secondary_geojson_lep"
REGISTRY = ROOT / "registry_lep.json"
INGEST_LOG = ROOT / "ingestion_lep.log"

for d in (FGDB_DIR, GEOJSON_DIR):
    d.mkdir(parents=True, exist_ok=True)

SOURCE_URL = "https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CriticalHabitat/MapServer"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def _log(msg: str):
    try:
        with open(INGEST_LOG, "a") as f:
            f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")
    except Exception:
        pass

def _load_registry() -> dict:
    if REGISTRY.exists():
        try:
            return json.loads(REGISTRY.read_text())
        except Exception:
            pass
    return {
        "source": SOURCE_URL,
        "status": "NOT_INGESTED",
        "fgdb": None,
        "geojson": [],
        "ingested_at": None,
        "esi_signature": None,
    }

def _save_registry(reg: dict):
    REGISTRY.write_text(json.dumps(reg, indent=2, ensure_ascii=False))

def _esi_sign(reg: dict) -> str:
    payload = json.dumps(
        {"fgdb": reg.get("fgdb"), "geojson": reg.get("geojson"), "ingested_at": reg.get("ingested_at")},
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()

# ------------------------------------------------------------------
# FGDB → GeoJSON conversion (pyogrio + OpenFileGDB driver)
# ------------------------------------------------------------------
def _convert_fgdb_to_geojson(fgdb_path: Path) -> list[dict]:
    """Convertit chaque couche de la FGDB en GeoJSON UTF-8, WGS84 EPSG:4326.

    Retourne la liste des manifests de couche :
      [{ "layer": "...", "geojson": "...", "crs": "...", "features": N, "sha256": "..." }]
    """
    try:
        import pyogrio
        import geopandas as gpd
    except ImportError as e:
        raise RuntimeError(f"pyogrio/geopandas indisponibles : {e}")

    manifests = []
    try:
        layers = pyogrio.list_layers(str(fgdb_path))
    except Exception as e:
        raise RuntimeError(f"Impossible de lister les couches FGDB : {e}")

    for lyr in layers:
        layer_name = lyr[0] if isinstance(lyr, (list, tuple)) else str(lyr)
        # Lecture complète (pas de simplification, pas de clip)
        gdf = gpd.read_file(str(fgdb_path), layer=layer_name, engine="pyogrio")
        # Reprojection WGS84 pour rendu Leaflet
        src_crs = str(gdf.crs) if gdf.crs is not None else "UNKNOWN"
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
        safe_name = layer_name.replace("/", "_").replace(" ", "_")
        out_path = GEOJSON_DIR / f"{safe_name}.geojson"
        # driver GeoJSON natif ; encodage UTF-8 par défaut
        gdf.to_file(str(out_path), driver="GeoJSON")
        sha = _sha256_file(out_path)
        manifests.append({
            "layer": layer_name,
            "geojson": str(out_path.relative_to(ROOT)),
            "geojson_abs": str(out_path),
            "crs_src": src_crs,
            "crs_out": "EPSG:4326",
            "features": int(len(gdf)),
            "size_bytes": out_path.stat().st_size,
            "sha256": sha,
        })
    return manifests

# ------------------------------------------------------------------
# Ingestion core
# ------------------------------------------------------------------
def _ingest_from_path(source_path: Path, original_name: str) -> dict:
    mark_call("LEP-INGESTION-Ω")
    t0 = time.time()

    # Cas 1 : archive ZIP → extraire
    target_fgdb: Optional[Path] = None
    staging = tempfile.mkdtemp(prefix="lep_fgdb_")
    try:
        if source_path.suffix.lower() == ".zip":
            with zipfile.ZipFile(source_path) as zf:
                zf.extractall(staging)
            # trouver le .gdb
            for p in Path(staging).rglob("*.gdb"):
                if p.is_dir():
                    target_fgdb = p
                    break
        elif source_path.is_dir() and source_path.suffix.lower() == ".gdb":
            target_fgdb = source_path
        elif source_path.is_file() and source_path.suffix.lower() in (".geojson", ".json"):
            # Cas 3 : GeoJSON direct
            return _ingest_geojson_direct(source_path, original_name)
        else:
            raise HTTPException(
                400,
                "Format non supporté. Attendu : .zip (FGDB), .gdb directory, .geojson/.json",
            )

        if target_fgdb is None:
            raise HTTPException(400, "Aucune FGDB (.gdb) trouvée dans l'archive.")

        # Copier la FGDB vers stockage persistent
        persistent_gdb = FGDB_DIR / target_fgdb.name
        if persistent_gdb.exists():
            shutil.rmtree(persistent_gdb)
        shutil.copytree(target_fgdb, persistent_gdb)

        # Hash agrégé de la FGDB (SHA-256 sur concat triée des fichiers internes)
        gdb_hash = hashlib.sha256()
        sizes = 0
        for f in sorted(persistent_gdb.iterdir()):
            if f.is_file():
                gdb_hash.update(f.name.encode())
                gdb_hash.update(_sha256_file(f).encode())
                sizes += f.stat().st_size
        gdb_sha = gdb_hash.hexdigest()

        # Extraire et convertir vers GeoJSON
        geojson_manifests = _convert_fgdb_to_geojson(persistent_gdb)

        elapsed = round(time.time() - t0, 2)
        reg = {
            "source": SOURCE_URL,
            "status": "INGESTED",
            "fgdb": {
                "path": str(persistent_gdb.relative_to(ROOT)),
                "path_abs": str(persistent_gdb),
                "original_archive": original_name,
                "size_bytes": sizes,
                "sha256": gdb_sha,
            },
            "geojson": geojson_manifests,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_s": elapsed,
            "esi_signature": None,
        }
        reg["esi_signature"] = _esi_sign(reg)
        _save_registry(reg)
        _log(
            f"INGEST OK fgdb_sha={gdb_sha[:16]} layers={len(geojson_manifests)} "
            f"elapsed={elapsed}s esi={reg['esi_signature'][:16]}"
        )
        return reg
    finally:
        shutil.rmtree(staging, ignore_errors=True)

def _ingest_geojson_direct(path: Path, original_name: str) -> dict:
    """Chemin 'GeoJSON direct' : on copie vers DATA-SECONDARY et on marque
    FGDB-absent (ingestion secondaire uniquement)."""
    mark_call("LEP-INGESTION-Ω")
    import geopandas as gpd
    gdf = gpd.read_file(str(path), engine="pyogrio")
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    target = GEOJSON_DIR / f"{path.stem}.geojson"
    gdf.to_file(str(target), driver="GeoJSON")
    sha = _sha256_file(target)
    manifest = [{
        "layer": path.stem,
        "geojson": str(target.relative_to(ROOT)),
        "geojson_abs": str(target),
        "crs_src": "GEOJSON_DIRECT",
        "crs_out": "EPSG:4326",
        "features": int(len(gdf)),
        "size_bytes": target.stat().st_size,
        "sha256": sha,
    }]
    reg = {
        "source": SOURCE_URL,
        "status": "INGESTED",
        "fgdb": None,
        "geojson": manifest,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "mode": "GEOJSON_DIRECT",
        "esi_signature": None,
    }
    reg["esi_signature"] = _esi_sign(reg)
    _save_registry(reg)
    _log(f"INGEST GEOJSON-DIRECT name={original_name} features={manifest[0]['features']}")
    return reg

# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.get("/status")
async def lep_status():
    reg = _load_registry()
    mark_call("LEP-INGESTION-Ω")
    return reg

@router.get("/registry")
async def lep_registry():
    return _load_registry()

@router.post("/ingest")
async def lep_ingest(file: UploadFile = File(...)):
    """Upload direct FGDB zip / .geojson."""
    mark_call("LEP-INGESTION-Ω")
    # Persistence dans /tmp puis handoff à _ingest_from_path
    suffix = Path(file.filename).suffix.lower() or ".zip"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        while True:
            chunk = await file.read(1 << 20)
            if not chunk:
                break
            tmp.write(chunk)
        tmp.flush()
        tmp.close()
        reg = _ingest_from_path(Path(tmp.name), file.filename)
        return reg
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

class IngestPathBody(BaseModel):
    path: str

@router.post("/ingest-path")
async def lep_ingest_path(body: IngestPathBody):
    """Ingest depuis chemin local déjà présent sur le pod."""
    mark_call("LEP-INGESTION-Ω")
    src = Path(body.path)
    if not src.exists():
        raise HTTPException(404, f"Chemin introuvable : {body.path}")
    return _ingest_from_path(src, src.name)

@router.get("/geojson-list")
async def lep_geojson_list():
    mark_call("LEP-INGESTION-Ω")
    reg = _load_registry()
    return {
        "status": reg.get("status"),
        "count": len(reg.get("geojson", [])),
        "layers": [
            {"layer": m["layer"], "features": m["features"], "size_bytes": m["size_bytes"], "sha256": m["sha256"][:16]}
            for m in reg.get("geojson", [])
        ],
    }

@router.get("/geojson/{layer}")
async def lep_geojson(layer: str):
    """Serve a GeoJSON layer to the frontend."""
    mark_call("LEP-INGESTION-Ω")
    safe = layer.replace("/", "_").replace("..", "_")
    path = GEOJSON_DIR / f"{safe}.geojson"
    if not path.exists():
        raise HTTPException(404, f"Couche GeoJSON '{layer}' non ingérée")
    return FileResponse(str(path), media_type="application/geo+json")

@router.post("/purge")
async def lep_purge():
    """Purge totale (reset). Utilisé avant ré-ingestion propre."""
    mark_call("LEP-INGESTION-Ω")
    for d in (FGDB_DIR, GEOJSON_DIR):
        for p in d.iterdir():
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                try: p.unlink()
                except Exception: pass
    if REGISTRY.exists():
        REGISTRY.unlink()
    _log("PURGED")
    return {"status": "PURGED"}


# ------------------------------------------------------------------
# Public getters (utilisés par bundle + frontend via backend proxy)
# ------------------------------------------------------------------
def get_status() -> dict:
    return _load_registry()

def is_ingested() -> bool:
    return _load_registry().get("status") == "INGESTED"
