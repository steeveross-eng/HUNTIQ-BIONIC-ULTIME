"""
nrcan_hrdem_p1_full.py — NRCan HRDEM P1_FULL Phase B (LiDAR-derived DSM/DTM 1m/2m)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_NRCAN_PHASE_B_Ω · COMMANDANT STEEVE-MAX · 2026-06-08
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Wrapper pour ingestion NRCan HRDEM via le bucket S3 public AWS
`canelevation-dem` (registry.opendata.aws/canelevation-dem).

DOCTRINE :
  - Anonymous S3 listing (pas de credentials AWS requis)
  - 4 produits exposés : hrdem-mosaic-1m, hrdem-mosaic-2m, hrdem-lidar,
    hrdem-arcticdem.
  - Indexation par grille `{col}_{row}` (ex: 10_2, 11_3, 21_5...)
  - dry_run = list S3 objects + meta (no download)
  - download = streaming HTTPS direct depuis S3 (peut être MULTI-GIGA, gating
    explicite par INGESTION_P1_DISK_AUTHORIZED requis)
  - sync_to_r2 différé après téléchargement local

Ne touche PAS le client legacy `nrcan_hrdem_client.py` (Verrou Phase III).
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
import os
import re
import xml.etree.ElementTree as ET
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

logger = logging.getLogger("bionic.p1_full.nrcan_hrdem")

CLIENT_KEY = "nrcan_hrdem"
CLIENT_NAME = "NRCAN-HRDEM-P1-FULL-CLIENT"
CLIENT_VERSION = "V1.0-P1-FULL-PHASE-B"
DATA_TYPE = "LIDAR_HRDEM_1m"

S3_BASE = "https://canelevation-dem.s3.amazonaws.com"
NS_S3 = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
DEFAULT_DATA_PRODUCT = "hrdem-mosaic-1m"  # alt: hrdem-mosaic-2m, hrdem-lidar, hrdem-arcticdem
DEFAULT_FILE_PATTERN = "-dsm.tif"  # alt: -dsm_hillshade.tif, -coverage.gpkg, -dsm.vrt


def get_p1_full_status() -> dict[str, Any]:
    """Statut du wrapper P1_FULL NRCan HRDEM (Phase B)."""
    return {
        "client_key": CLIENT_KEY,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "data_type": DATA_TYPE,
        "phase": "P1_FULL_PHASE_B_ACTIVE",
        "phase_b_voice": "STAC AWS canelevation-dem (anonymous S3 listing)",
        "armed_for_ingestion": os.environ.get("INGESTION_P1_ARMED") == "1",
        "disk_authorized": os.environ.get("INGESTION_P1_DISK_AUTHORIZED") == "1",
        "available": True,
    }


def is_credential_ready() -> bool:
    """Pas de credentials AWS requis (anonymous S3 listing)."""
    return True


def is_armed() -> bool:
    return os.environ.get("INGESTION_P1_ARMED", "0") == "1"


def _list_s3_keys(prefix: str, max_keys: int = 1000) -> list[dict[str, Any]]:
    """List S3 objects under prefix, paginate via continuation token if needed."""
    out: list[dict[str, Any]] = []
    continuation: Optional[str] = None
    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": str(min(max_keys, 1000))}
        if continuation:
            params["continuation-token"] = continuation
        try:
            with httpx.Client(timeout=30) as cli:
                resp = cli.get(S3_BASE, params=params)
                if resp.status_code != 200:
                    logger.warning(f"[NRCAN_S3_LIST] HTTP {resp.status_code} prefix={prefix}")
                    break
                root = ET.fromstring(resp.text)
        except Exception as e:
            logger.warning(f"[NRCAN_S3_LIST] fail prefix={prefix}: {e}")
            break
        for c in root.findall("s3:Contents", NS_S3):
            k_el = c.find("s3:Key", NS_S3)
            size_el = c.find("s3:Size", NS_S3)
            lm_el = c.find("s3:LastModified", NS_S3)
            etag_el = c.find("s3:ETag", NS_S3)
            key = k_el.text if k_el is not None and k_el.text else ""
            out.append({
                "key": key,
                "size_bytes": int(size_el.text) if size_el is not None and size_el.text else 0,
                "last_modified": lm_el.text if lm_el is not None else None,
                "etag": (etag_el.text or "").strip('"') if etag_el is not None and etag_el.text else None,
            })
            if len(out) >= max_keys:
                return out
        truncated_el = root.find("s3:IsTruncated", NS_S3)
        if truncated_el is None or (truncated_el.text or "").lower() != "true":
            break
        tok_el = root.find("s3:NextContinuationToken", NS_S3)
        continuation = tok_el.text if tok_el is not None else None
        if not continuation:
            break
    return out


def search_scenes(
    bbox: tuple[float, float, float, float],
    datetime_range: Optional[tuple[datetime, datetime]] = None,
    cloud_cover_max: Optional[int] = None,
    limit: int = 50,
    data_product: str = DEFAULT_DATA_PRODUCT,
    file_pattern: str = DEFAULT_FILE_PATTERN,
) -> list[dict[str, Any]]:
    """READ-ONLY · liste les tuiles HRDEM disponibles dans le bucket S3 canelevation-dem.

    bbox     : utilisé comme hint pour le filtrage par grille NTS-like {col}_{row}
               (best-effort · le bucket utilise une grille AWS personnalisée, non
               strictement alignée NTS). Pour filtrage géographique exact,
               télécharger le `coverage.gpkg` correspondant et l'intersecter.
    datetime_range, cloud_cover_max : ignorés (HRDEM n'a pas ces propriétés).
    data_product : hrdem-mosaic-1m | hrdem-mosaic-2m | hrdem-lidar | hrdem-arcticdem
    file_pattern : suffix de filtrage (-dsm.tif par défaut, alt -coverage.gpkg).

    Retourne metadata par tuile (sans download).
    """
    prefix = f"{data_product}/"
    files = _list_s3_keys(prefix, max_keys=max(limit * 4, 200))

    # Filtrage par pattern
    candidates = [f for f in files if f["key"].endswith(file_pattern)]

    # Best-effort bbox→NTS filter (simple heuristic sur grid code prefix)
    # Pour bbox QC limitrophes (-79..-74, 45..50), les grilles AWS pertinentes
    # sont à entrées multiples — on accepte tout par défaut et signale le hint.
    nts_pattern = re.compile(r"^([0-9a-zA-Z_]+)-")

    out: list[dict[str, Any]] = []
    for f in candidates:
        key = f["key"]
        filename = key.split("/")[-1]
        m = nts_pattern.match(filename)
        nts_code = m.group(1) if m else None
        out.append({
            "scene_id": filename.replace(file_pattern, ""),
            "s3_key": key,
            "download_url": f"{S3_BASE}/{key}",
            "size_mb": round(f["size_bytes"] / 1e6, 1),
            "last_modified": f["last_modified"],
            "etag": f["etag"],
            "nts_grid_code": nts_code,
            "data_product": data_product,
            "bbox": list(bbox),
        })
        if len(out) >= limit:
            break
    return out


def download_hrdem_tiles(
    tile_names: list[str],
    destination_dir: Optional[str] = None,
    sync_r2: bool = True,
    job_id: Optional[str] = None,
    max_tiles: Optional[int] = None,
    data_product: str = DEFAULT_DATA_PRODUCT,
    file_pattern: str = DEFAULT_FILE_PATTERN,
    bands_filter: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Download HRDEM tiles depuis S3 canelevation-dem.

    ATTENTION : Les fichiers DSM 1m peuvent atteindre 40 GB par tuile.
    Gate explicite : `INGESTION_P1_DISK_AUTHORIZED=1` requis pour activer.
    """
    import time
    if os.environ.get("INGESTION_P1_DISK_AUTHORIZED") != "1":
        raise PermissionError(
            "NRCan HRDEM download requires INGESTION_P1_DISK_AUTHORIZED=1 in .env "
            "(fichiers multi-GB par tuile, autorisation explicite COMMANDANT requise)."
        )
    max_tiles = max_tiles or P1_MAX_TILES
    tile_names = tile_names[:max_tiles]
    store = get_job_store()
    if not job_id:
        job = store.create(CLIENT_KEY, {"tile_names": tile_names, "data_product": data_product}, len(tile_names))
        job_id = job.job_id
    dest_base = Path(destination_dir) if destination_dir else (DEFAULT_DEST_BASE / "nrcan_hrdem")
    store.update(job_id, status="running",
                 started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    for tname in tile_names:
        s3_key = f"{data_product}/{tname}{file_pattern}"
        url = f"{S3_BASE}/{s3_key}"
        filename = f"{tname}{file_pattern}"
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
    "search_scenes", "download_hrdem_tiles", "get_p1_full_status",
    "is_credential_ready", "is_armed",
    "CLIENT_KEY", "CLIENT_NAME", "CLIENT_VERSION",
]
