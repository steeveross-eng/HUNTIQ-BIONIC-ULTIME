"""
nasa_hls_p1_full.py — NASA HLS P1_FULL Phase A (NDVI HR 30m)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_NASA_HLS_Ω · COMMANDANT STEEVE-MAX · 2026-06-07
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Wrapper mince pour télécharger les granules NASA HLS via earthaccess + streaming
direct. Ne touche PAS le client `nasa_hls_client.py` existant (Phase 0 inerte).

DOCTRINE :
  - Auth via EARTHDATA_TOKEN (déjà chargé dans env via .env)
  - earthaccess.login(strategy="environment") puis earthaccess.search_data()
    pour résoudre granule_id → URL .tif HLS
  - download_with_retry() depuis le streamer commun
  - sync_to_r2() différé après téléchargement local
  - Job state tracking via JobStore
"""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

from .download_streamer_omega import (
    DEFAULT_DEST_BASE,
    JobStore,
    P1_MAX_SIZE_MB,
    P1_MAX_TILES,
    P1_TIMEOUT_S,
    TileResult,
    download_with_retry,
    get_job_store,
    sync_to_r2,
)

logger = logging.getLogger("bionic.p1_full.nasa_hls")

CLIENT_KEY = "nasa_hls"
CLIENT_NAME = "NASA-HLS-P1-FULL-CLIENT"
CLIENT_VERSION = "V1.0-P1-FULL-PHASE-A"
DATA_TYPE = "NDVI_HR_30m"


def get_p1_full_status() -> dict[str, Any]:
    """Statut du wrapper P1_FULL NASA HLS."""
    edl = os.environ.get("EARTHDATA_TOKEN") or os.environ.get("EDL_TOKEN")
    return {
        "client_key": CLIENT_KEY,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "data_type": DATA_TYPE,
        "phase": "P1_FULL_PHASE_A",
        "armed_for_ingestion": os.environ.get("INGESTION_P1_ARMED") == "1",
        "earthdata_token_present": bool(edl),
        "max_tiles_default": P1_MAX_TILES,
        "max_size_mb_default": P1_MAX_SIZE_MB,
    }


def _earthaccess_login() -> bool:
    """Login earthaccess via env (EARTHDATA_TOKEN)."""
    try:
        import earthaccess
        auth = earthaccess.login(strategy="environment", persist=False)
        return bool(auth and getattr(auth, "authenticated", False))
    except Exception as e:
        logger.warning(f"[P1_FULL_NASA] login fail: {e}")
        return False


def _resolve_granule_urls(scene_ids: list[str]) -> list[dict[str, Any]]:
    """Résout granule_id (concept_id CMR) → liste URLs .tif via earthaccess.
    Retourne [{granule_id, urls: [url, url], ...}, ...].

    P22ΩΩ_NASA_HLS_RESOLVE_BUGFIX_Ω · 2026-06-07 · STEEVE-MAX
    Le dry_run NASA expose des `granule_id` au format concept_id CMR (G... -LPCLOUD).
    L'ancien code utilisait `granule_name` qui attendait le `title` (HLS.L30...).
    Fix : utiliser `concept_id` qui matche exactement le format retourné par dry_run.
    """
    try:
        import earthaccess
        results = []
        for granule_id in scene_ids:
            # Recherche par concept_id CMR (format G..-LPCLOUD)
            granules = earthaccess.search_data(
                concept_id=granule_id,
                count=1,
            )
            if not granules:
                # Fallback : tenter granule_ur si concept_id échoue
                try:
                    granules = earthaccess.search_data(
                        short_name=["HLSL30", "HLSS30"],
                        granule_ur=granule_id,
                        count=1,
                    )
                except Exception:
                    granules = []
            if not granules:
                results.append({"granule_id": granule_id, "urls": [], "error": "not_found"})
                continue
            granule = granules[0]
            urls = []
            try:
                links = granule.data_links() if hasattr(granule, "data_links") else []
                urls = [u for u in links if u.lower().endswith(".tif")]
            except Exception as e:
                logger.warning(f"[P1_FULL_NASA] links extract fail {granule_id}: {e}")
            results.append({
                "granule_id": granule_id,
                "urls": urls,
                "n_urls": len(urls),
            })
        return results
    except Exception as e:
        logger.warning(f"[P1_FULL_NASA] resolve fail: {e}")
        return [{"granule_id": gid, "urls": [], "error": str(e)} for gid in scene_ids]


def download_hls_tiles(
    scene_ids: list[str],
    destination_dir: Optional[str] = None,
    sync_r2: bool = True,
    job_id: Optional[str] = None,
    bands_filter: Optional[list[str]] = None,
    max_tiles: Optional[int] = None,
) -> dict[str, Any]:
    """Télécharge les granules NASA HLS (NDVI HR 30m) en P1_FULL mode.

    Args:
        scene_ids: Liste granule_ids HLS (résolus via earthaccess search)
        destination_dir: Dir local cible (défaut /var/data/p1_ingest/nasa_hls/)
        sync_r2: Si True, upload R2 après download local
        job_id: Job ID pour tracking (créé si None)
        bands_filter: Bandes spécifiques (ex ['B04', 'B05'] pour NDVI) · défaut toutes
        max_tiles: Override P1_MAX_TILES env

    Returns:
        dict de résumé exécution {job_id, status, tiles_done, ...}
    """
    max_tiles = max_tiles or P1_MAX_TILES
    scene_ids = scene_ids[:max_tiles]
    store = get_job_store()

    if not job_id:
        job = store.create(CLIENT_KEY, {"scene_ids": scene_ids, "bands_filter": bands_filter}, len(scene_ids))
        job_id = job.job_id

    dest_base = Path(destination_dir) if destination_dir else (DEFAULT_DEST_BASE / "nasa_hls")
    store.update(job_id, status="running", started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    # Auth
    if not _earthaccess_login():
        store.update(job_id, status="failed",
                     error="earthaccess_login_failed",
                     completed_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        return {"job_id": job_id, "status": "failed", "error": "earthaccess_login_failed"}

    # Auth header pour streaming direct
    edl = os.environ.get("EARTHDATA_TOKEN") or os.environ.get("EDL_TOKEN")
    headers = {"Authorization": f"Bearer {edl}"} if edl else {}

    # Resolve URLs
    granule_meta = _resolve_granule_urls(scene_ids)

    for meta in granule_meta:
        gid = meta["granule_id"]
        urls = meta.get("urls", [])
        if not urls:
            store.append_tile(job_id, TileResult(
                tile_id=gid,
                status="failed",
                error=meta.get("error", "no_urls_resolved"),
            ))
            continue

        # Filter bands si demandé
        if bands_filter:
            urls = [u for u in urls if any(f".{b}." in u or f"_{b}." in u for b in bands_filter)]

        # Download chaque URL séparément (HLS = 1 fichier par bande)
        for url in urls:
            file_name = url.split("/")[-1]
            tile_id = f"{gid}/{file_name}"
            dest = dest_base / file_name
            r = download_with_retry(url, dest, headers=headers, timeout_s=P1_TIMEOUT_S)
            tile = TileResult(
                tile_id=tile_id,
                status="success" if r.get("success") else "failed",
                local_path=r.get("local_path"),
                size_bytes=r.get("size_bytes"),
                sha256=r.get("sha256"),
                elapsed_ms=r.get("elapsed_ms"),
                error=r.get("error"),
            )
            # R2 sync différé
            if r.get("success") and sync_r2:
                r2_key = f"ingestion_p1/nasa_hls/{file_name}"
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


__all__ = ["download_hls_tiles", "get_p1_full_status", "CLIENT_KEY", "CLIENT_NAME", "CLIENT_VERSION"]
