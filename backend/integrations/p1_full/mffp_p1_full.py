"""
mffp_p1_full.py — MFFP LiDAR Forêt Ouverte P1_FULL Phase B (LiDAR Québec 0.5m)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_MFFP_PHASE_B_Ω · COMMANDANT STEEVE-MAX · 2026-06-08
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Wrapper pour ingestion MFFP LiDAR Québec (Forêt Ouverte) via l'API CKAN
Données Québec et l'index GeoJSON `URL_Lidar.geojson`.

DOCTRINE :
  - CKAN API publique : pas de credentials requis
  - Index : URL_Lidar.geojson (5.7 MB · 2630 feuillets 1/20 000 · CRS84)
  - Chaque feuillet expose : MNT, MHC, MNT_Ombre, Pentes, Courbes_GDB, Courbes_GPKG
  - dry_run = parse GeoJSON, filtre bbox, retourne metadata + URLs (no download)
  - download = streaming HTTPS direct depuis diffusion.mffp.gouv.qc.ca
  - sync_to_r2 différé après téléchargement local

Ne touche PAS le client legacy `mffp_foret_ouverte_client.py` (Verrou Phase III).
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import httpx

from .download_streamer_omega import (
    DEFAULT_DEST_BASE,
    P1_MAX_TILES,
    P1_TIMEOUT_S,
    TileResult,
    download_with_retry,
    get_job_store,
    sync_to_r2,
)

logger = logging.getLogger("bionic.p1_full.mffp")

CLIENT_KEY = "mffp_foret_ouverte"
CLIENT_NAME = "MFFP-LIDAR-QC-P1-FULL-CLIENT"
CLIENT_VERSION = "V1.0-P1-FULL-PHASE-B"
DATA_TYPE = "LIDAR_FORET_QC_0.5m"

CKAN_PACKAGE_URL = (
    "https://www.donneesquebec.ca/recherche/api/3/action/package_show"
    "?id=produits-derives-de-base-du-lidar"
)
INDEX_URL = (
    "https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/IMAGERIE/"
    "Produits_derives_LiDAR/Produit_derive_lidar/03-Telechargement/URL_Lidar.geojson"
)

# Cache d'index : 5.7 MB téléchargé · refresh hebdo (TTL 7j)
_INDEX_CACHE: dict[str, Any] = {"data": None, "loaded_at": 0.0}
_INDEX_LOCK = threading.Lock()
_INDEX_TTL_S = 7 * 24 * 3600  # 7 jours

# Resources LiDAR exposées par feuillet (clés GeoJSON properties)
LIDAR_PRODUCTS = ["MNT", "MHC", "MNT_Ombre", "Pentes", "Courbes_GDB", "Courbes_GPKG"]


def get_p1_full_status() -> dict[str, Any]:
    """Statut du wrapper P1_FULL MFFP (Phase B)."""
    return {
        "client_key": CLIENT_KEY,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "data_type": DATA_TYPE,
        "phase": "P1_FULL_PHASE_B_ACTIVE",
        "phase_b_voice": "CKAN Données Québec · URL_Lidar.geojson (2630 feuillets 1/20 000)",
        "armed_for_ingestion": os.environ.get("INGESTION_P1_ARMED") == "1",
        "disk_authorized": os.environ.get("INGESTION_P1_DISK_AUTHORIZED") == "1",
        "index_cached": _INDEX_CACHE["data"] is not None,
        "available": True,
    }


def is_credential_ready() -> bool:
    """Pas de credentials requis (open data CKAN)."""
    return True


def is_armed() -> bool:
    return os.environ.get("INGESTION_P1_ARMED", "0") == "1"


def _load_index(force_refresh: bool = False) -> dict[str, Any]:
    """Télécharge et cache l'index URL_Lidar.geojson (5.7 MB · refresh hebdo)."""
    with _INDEX_LOCK:
        now = time.time()
        if (
            not force_refresh
            and _INDEX_CACHE["data"] is not None
            and (now - _INDEX_CACHE["loaded_at"]) < _INDEX_TTL_S
        ):
            return _INDEX_CACHE["data"]
        try:
            with httpx.Client(timeout=120) as cli:
                # IMPORTANT : --compressed équivalent (sinon le serveur tronque)
                resp = cli.get(INDEX_URL, headers={"Accept-Encoding": "gzip, deflate"})
                if resp.status_code != 200:
                    logger.warning(f"[MFFP_INDEX] HTTP {resp.status_code}")
                    return {"features": []}
                data = resp.json()
        except Exception as e:
            logger.warning(f"[MFFP_INDEX] fetch fail: {e}")
            return {"features": []}
        _INDEX_CACHE["data"] = data
        _INDEX_CACHE["loaded_at"] = now
        return data


def _feature_bbox(feature: dict[str, Any]) -> Optional[tuple[float, float, float, float]]:
    """Calcule bbox (lng_min, lat_min, lng_max, lat_max) d'une feature Polygon ou MultiPolygon."""
    geom = feature.get("geometry") or {}
    gtype = geom.get("type")
    coords = geom.get("coordinates") or []
    if not coords:
        return None
    xs: list[float] = []
    ys: list[float] = []
    if gtype == "Polygon":
        # coords = [ring0, ring1, ...] · ring = [[x,y], ...]
        for ring in coords:
            for pt in ring:
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    xs.append(pt[0]); ys.append(pt[1])
    elif gtype == "MultiPolygon":
        # coords = [polygon0, polygon1, ...] · polygon = [ring0, ring1, ...]
        for poly in coords:
            for ring in poly:
                for pt in ring:
                    if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                        xs.append(pt[0]); ys.append(pt[1])
    else:
        return None
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def _bbox_intersect(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    """Test intersection de 2 bbox (axis-aligned, CRS84/WGS84)."""
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def search_scenes(
    bbox: tuple[float, float, float, float],
    datetime_range: Optional[tuple[datetime, datetime]] = None,
    cloud_cover_max: Optional[int] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """READ-ONLY · filtre les feuillets MFFP LiDAR par bbox depuis l'index GeoJSON.

    bbox      : (lng_min, lat_min, lng_max, lat_max) en CRS84/WGS84
    datetime_range, cloud_cover_max : ignorés (LiDAR n'a pas ces propriétés)
    limit     : nombre max de feuillets retournés

    Retourne metadata par feuillet (sans download), avec toutes les URLs
    LiDAR exposées (MNT, MHC, MNT_Ombre, Pentes, Courbes_GDB, Courbes_GPKG).
    """
    idx = _load_index()
    feats = idx.get("features", [])
    out: list[dict[str, Any]] = []
    for f in feats:
        fb = _feature_bbox(f)
        if not fb or not _bbox_intersect(bbox, fb):
            continue
        props = f.get("properties") or {}
        feuillet_20k = props.get("Feuillet20K")
        if not feuillet_20k:
            continue
        # Construit le dict de download URLs par produit
        download_urls = {prod: props.get(prod) for prod in LIDAR_PRODUCTS if props.get(prod)}
        out.append({
            "scene_id": feuillet_20k,
            "feuillet_20k": feuillet_20k,
            "feuillet_250k": props.get("Feuillet250K"),
            "region": props.get("Region"),
            "repertoire": props.get("Repertoire"),
            "download_urls": download_urls,
            "products_available": list(download_urls.keys()),
            "bbox": list(fb),
        })
        if len(out) >= limit:
            break
    return out


def download_mffp_tiles(
    tile_names: list[str],
    destination_dir: Optional[str] = None,
    sync_r2: bool = True,
    job_id: Optional[str] = None,
    max_tiles: Optional[int] = None,
    bands_filter: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Download MFFP LiDAR tiles depuis diffusion.mffp.gouv.qc.ca.

    tile_names    : liste des Feuillet20K (ex: "33C15NO")
    bands_filter  : produits à télécharger parmi ['MNT','MHC','MNT_Ombre','Pentes',
                    'Courbes_GDB','Courbes_GPKG'] · défaut ['MNT'] (le plus utile)

    ATTENTION : les fichiers MNT (DEM 1m grille 1/20 000) peuvent atteindre
    plusieurs GB par feuillet. Gate `INGESTION_P1_DISK_AUTHORIZED=1` requis.
    """
    if os.environ.get("INGESTION_P1_DISK_AUTHORIZED") != "1":
        raise PermissionError(
            "MFFP LiDAR download requires INGESTION_P1_DISK_AUTHORIZED=1 in .env "
            "(fichiers multi-GB par feuillet, autorisation explicite COMMANDANT requise)."
        )
    bands_filter = bands_filter or ["MNT"]
    max_tiles = max_tiles or P1_MAX_TILES
    tile_names = tile_names[:max_tiles]
    idx = _load_index()
    feat_map = {
        (f.get("properties") or {}).get("Feuillet20K"): (f.get("properties") or {})
        for f in idx.get("features", [])
        if (f.get("properties") or {}).get("Feuillet20K")
    }
    store = get_job_store()
    # tiles_total = nombre de (feuillet × produit) attendus
    expected_tiles = sum(
        1 for tname in tile_names for product in bands_filter
        if feat_map.get(tname, {}).get(product)
    )
    if not job_id:
        job = store.create(CLIENT_KEY, {"tile_names": tile_names, "bands_filter": bands_filter}, max(expected_tiles, len(tile_names)))
        job_id = job.job_id
    dest_base = Path(destination_dir) if destination_dir else (DEFAULT_DEST_BASE / "mffp_foret_ouverte")
    store.update(job_id, status="running",
                 started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    for tname in tile_names:
        props = feat_map.get(tname)
        if not props:
            store.append_tile(job_id, TileResult(
                tile_id=tname, status="failed", error="feuillet_not_found_in_index"
            ))
            continue
        for product in bands_filter:
            url = props.get(product)
            if not url:
                store.append_tile(job_id, TileResult(
                    tile_id=f"{tname}/{product}", status="failed",
                    error=f"product_{product}_not_available_for_feuillet"
                ))
                continue
            filename = url.split("/")[-1]
            dest = dest_base / filename
            tile_id = f"{tname}/{filename}"
            r = download_with_retry(url, dest, timeout_s=P1_TIMEOUT_S)
            tile = TileResult(
                tile_id=tile_id,
                status="success" if r.get("success") else "failed",
                local_path=r.get("local_path"),
                size_bytes=r.get("size_bytes"),
                sha256=r.get("sha256"),
                elapsed_ms=r.get("elapsed_ms"),
                error=r.get("error"),
            )
            if r.get("success") and sync_r2:
                r2_key = f"ingestion_p1/{CLIENT_KEY}/{filename}"
                sync_r = sync_to_r2(dest, r2_key, content_type="image/tiff")
                if sync_r.get("success"):
                    tile.r2_key = sync_r["r2_key"]
            store.append_tile(job_id, tile)
    job_final = store.get(job_id)
    if job_final:
        final_status = "completed" if job_final.tiles_failed == 0 else "completed_with_errors"
        store.update(job_id, status=final_status,
                     completed_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    job_final = store.get(job_id)
    return {
        "job_id": job_id,
        "status": job_final.status if job_final else "unknown",
        "tiles_total": job_final.tiles_total if job_final else 0,
        "tiles_done": job_final.tiles_done if job_final else 0,
        "tiles_failed": job_final.tiles_failed if job_final else 0,
    }


__all__ = [
    "search_scenes", "download_mffp_tiles", "get_p1_full_status",
    "is_credential_ready", "is_armed",
    "CLIENT_KEY", "CLIENT_NAME", "CLIENT_VERSION",
]
