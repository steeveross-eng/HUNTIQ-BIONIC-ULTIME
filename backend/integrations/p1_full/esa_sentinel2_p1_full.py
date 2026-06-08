"""
esa_sentinel2_p1_full.py — ESA Sentinel-2 L2A P1_FULL Phase A (NDVI 10m)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_ESA_S2_Ω · COMMANDANT STEEVE-MAX · 2026-06-07
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Wrapper mince pour télécharger les scènes Sentinel-2 L2A via Copernicus Data
Space Ecosystem (CDSE) OAuth2 + STAC. Ne touche PAS le client existant
`esa_sentinel2_client.py` (Phase 0 inerte).

DOCTRINE :
  - OAuth2 password grant : token JWT (cache 9 min, TTL réel ~10min)
  - STAC endpoint : https://catalogue.dataspace.copernicus.eu/stac
  - Download URL : odata/v1/Products(GUID)/$value (avec auth Bearer)
  - download_with_retry() depuis le streamer commun
  - sync_to_r2() différé

P22ΩΩ_ESA_S2_ODATA_SEARCH_BUGFIX_Ω · 2026-06-08 · STEEVE-MAX
═══════════════════════════════════════════════════════════════════════════════
Fix Phase A.2 : Le legacy `esa_sentinel2_client.py` utilise pystac_client sur
`/stac` qui n'expose PAS Sentinel-2 (10 collections CLMS/CCM uniquement, vérifié
2026-06-07). Bascule vers CDSE OData officiel (source canonique Sentinel-2).
Ajouts : is_credential_ready(), is_armed(), search_scenes() utilisant OData.
Le router est repointé vers ce module pour ESA (search + download cohérents).
"""
from __future__ import annotations

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
    P1_MAX_SIZE_MB,
    P1_MAX_TILES,
    P1_TIMEOUT_S,
    TileResult,
    download_with_retry,
    get_job_store,
    sync_to_r2,
)

logger = logging.getLogger("bionic.p1_full.esa_s2")

CLIENT_KEY = "esa_sentinel2_l2a"
CLIENT_NAME = "ESA-S2-L2A-P1-FULL-CLIENT"
CLIENT_VERSION = "V1.0-P1-FULL-PHASE-A"
DATA_TYPE = "NDVI_10m_L2A"

CDSE_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CDSE_DOWNLOAD_BASE = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
CDSE_ODATA_BASE = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Cache token in-memory (TTL ~9min, CDSE token vit 10min)
_TOKEN_CACHE: dict[str, Any] = {"token": None, "expires_at": 0}
_TOKEN_LOCK = threading.Lock()


# ─── P22ΩΩ_ESA_S2_ODATA_SEARCH_BUGFIX_Ω · 2026-06-08 · STEEVE-MAX ─────────────
# Additif strict : pré-requis router pour bascule depuis legacy esa_sentinel2_client.

def is_credential_ready() -> bool:
    """COPERNICUS_USERNAME + COPERNICUS_PASSWORD requis pour download.
    Search OData fonctionne sans auth, mais on garde la sémantique legacy.
    """
    return bool(
        os.environ.get("COPERNICUS_USERNAME") and os.environ.get("COPERNICUS_PASSWORD")
    )


def is_armed() -> bool:
    """Armement ingestion via env (INGESTION_P1_ARMED=1)."""
    return os.environ.get("INGESTION_P1_ARMED", "0") == "1"


def search_scenes(
    bbox: tuple[float, float, float, float],
    datetime_range: tuple[datetime, datetime],
    cloud_cover_max: int = 20,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """READ-ONLY · interroge CDSE OData pour lister Sentinel-2 L2A.

    bbox = (lng_min, lat_min, lng_max, lat_max)
    Ne télécharge PAS · retourne métadonnées uniquement.

    P22ΩΩ_ESA_S2_ODATA_SEARCH_BUGFIX_Ω · 2026-06-08
    Bascule pystac_client (broken — /stac n'expose pas Sentinel-2) → OData
    officiel CDSE. Filtre Collection=SENTINEL-2 + Name~MSIL2A + bbox + dates.
    Le filtre cloud_cover_max est appliqué côté client (Attributes/cloudCover).
    """
    lng_min, lat_min, lng_max, lat_max = bbox
    dt0 = datetime_range[0].strftime("%Y-%m-%dT%H:%M:%S.000Z")
    dt1 = datetime_range[1].strftime("%Y-%m-%dT%H:%M:%S.000Z")
    poly = (
        f"POLYGON(({lng_min} {lat_min},{lng_max} {lat_min},"
        f"{lng_max} {lat_max},{lng_min} {lat_max},{lng_min} {lat_min}))"
    )
    filter_str = (
        f"Collection/Name eq 'SENTINEL-2' and "
        f"contains(Name,'MSIL2A') and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;{poly}') and "
        f"ContentDate/Start gt {dt0} and ContentDate/Start lt {dt1}"
    )
    # On élargit la requête (limit*4) puis on filtre cloud_cover côté client.
    fetch_top = min(max(limit * 4, 20), 200)
    params = {
        "$filter": filter_str,
        "$top": str(fetch_top),
        "$orderby": "ContentDate/Start desc",
        "$expand": "Attributes",
    }
    try:
        with httpx.Client(timeout=30) as cli:
            resp = cli.get(CDSE_ODATA_BASE, params=params)
            if resp.status_code != 200:
                logger.warning(
                    f"[P1_FULL_ESA_SEARCH] OData HTTP {resp.status_code}: {resp.text[:200]}"
                )
                return []
            items = resp.json().get("value", [])
    except Exception as e:
        logger.warning(f"[P1_FULL_ESA_SEARCH] OData query fail: {e}")
        return []

    out: list[dict[str, Any]] = []
    for it in items:
        attrs = {a.get("Name"): a.get("Value") for a in it.get("Attributes", []) if isinstance(a, dict)}
        cloud = attrs.get("cloudCover")
        try:
            cloud_val = float(cloud) if cloud is not None else None
        except (TypeError, ValueError):
            cloud_val = None
        if cloud_val is not None and cloud_val > cloud_cover_max:
            continue
        name = it.get("Name", "")
        scene_id = name.replace(".SAFE", "")
        # Extraction tile code (T18TWQ pattern) depuis le SAFE name.
        tile_id = None
        for part in name.split("_"):
            if len(part) == 6 and part.startswith("T") and part[1:].isalnum():
                tile_id = part
                break
        out.append({
            "scene_id": scene_id,
            "product_id": it.get("Id"),
            "datetime": (it.get("ContentDate") or {}).get("Start"),
            "cloud_cover": cloud_val,
            "tile_id": tile_id,
            "bbox": list(bbox),
            "size_mb": round((it.get("ContentLength") or 0) / 1e6, 1),
            "name_safe": name,
        })
        if len(out) >= limit:
            break
    return out


def get_p1_full_status() -> dict[str, Any]:
    return {
        "client_key": CLIENT_KEY,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "data_type": DATA_TYPE,
        "phase": "P1_FULL_PHASE_A",
        "armed_for_ingestion": os.environ.get("INGESTION_P1_ARMED") == "1",
        "copernicus_username_present": bool(os.environ.get("COPERNICUS_USERNAME")),
        "copernicus_password_present": bool(os.environ.get("COPERNICUS_PASSWORD")),
        "max_tiles_default": P1_MAX_TILES,
        "max_size_mb_default": P1_MAX_SIZE_MB,
    }


def _get_cdse_token(force_refresh: bool = False) -> Optional[str]:
    """Obtient un token CDSE via OAuth2 password grant. Cache 9 minutes."""
    with _TOKEN_LOCK:
        if (
            not force_refresh
            and _TOKEN_CACHE["token"]
            and time.time() < _TOKEN_CACHE["expires_at"]
        ):
            return _TOKEN_CACHE["token"]

        username = os.environ.get("COPERNICUS_USERNAME")
        password = os.environ.get("COPERNICUS_PASSWORD")
        if not (username and password):
            logger.warning("[P1_FULL_ESA] COPERNICUS_USERNAME/PASSWORD manquants")
            return None

        try:
            resp = httpx.post(
                CDSE_TOKEN_URL,
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "client_id": "cdse-public",
                },
                timeout=20,
            )
            if resp.status_code != 200:
                logger.warning(f"[P1_FULL_ESA] token HTTP {resp.status_code}: {resp.text[:200]}")
                return None
            data = resp.json()
            token = data.get("access_token")
            expires_in = data.get("expires_in", 600)
            _TOKEN_CACHE["token"] = token
            _TOKEN_CACHE["expires_at"] = time.time() + min(expires_in - 60, 540)  # marge 1min
            logger.info(f"[P1_FULL_ESA] token acquis · expires_in={expires_in}s")
            return token
        except Exception as e:
            logger.warning(f"[P1_FULL_ESA] token request fail: {e}")
            return None


def _resolve_scene_product_id(scene_id: str, token: str) -> Optional[str]:
    """Résout scene_id (ex S2B_MSIL2A_...) → product GUID via STAC search."""
    try:
        # CDSE OData filter by Name contains scene_id
        url = (
            f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
            f"?$filter=contains(Name,'{scene_id}')&$top=1"
        )
        resp = httpx.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
        if resp.status_code != 200:
            logger.warning(f"[P1_FULL_ESA] product lookup HTTP {resp.status_code}")
            return None
        items = resp.json().get("value", [])
        if not items:
            return None
        return items[0].get("Id")
    except Exception as e:
        logger.warning(f"[P1_FULL_ESA] product lookup fail: {e}")
        return None


def download_s2_tiles(
    scene_ids: list[str],
    destination_dir: Optional[str] = None,
    sync_r2: bool = True,
    job_id: Optional[str] = None,
    bands_filter: Optional[list[str]] = None,
    max_tiles: Optional[int] = None,
) -> dict[str, Any]:
    """Télécharge scènes Sentinel-2 L2A complètes (zip ~700MB-1GB) ou bandes spécifiques."""
    max_tiles = max_tiles or P1_MAX_TILES
    scene_ids = scene_ids[:max_tiles]
    store = get_job_store()

    if not job_id:
        job = store.create(CLIENT_KEY, {"scene_ids": scene_ids, "bands_filter": bands_filter}, len(scene_ids))
        job_id = job.job_id

    dest_base = Path(destination_dir) if destination_dir else (DEFAULT_DEST_BASE / "esa_sentinel2_l2a")
    store.update(job_id, status="running", started_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    token = _get_cdse_token()
    if not token:
        store.update(job_id, status="failed", error="cdse_oauth2_login_failed",
                     completed_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        return {"job_id": job_id, "status": "failed", "error": "cdse_oauth2_login_failed"}

    headers = {"Authorization": f"Bearer {token}"}

    for sid in scene_ids:
        # Résolution product GUID
        product_id = _resolve_scene_product_id(sid, token)
        if not product_id:
            store.append_tile(job_id, TileResult(
                tile_id=sid,
                status="failed",
                error="product_id_not_found",
            ))
            continue

        # URL téléchargement (zip complet · sentinel-2 L2A = ~700MB-1GB)
        download_url = f"{CDSE_DOWNLOAD_BASE}({product_id})/$value"
        file_name = f"{sid}.zip"
        dest = dest_base / file_name

        # Note: CDSE peut imposer refresh token entre downloads
        r = download_with_retry(download_url, dest, headers=headers, timeout_s=P1_TIMEOUT_S)
        # Si 401, retry avec token refresh
        if not r.get("success") and "HTTP 401" in str(r.get("error", "")):
            logger.info("[P1_FULL_ESA] 401 detected, refreshing token")
            token = _get_cdse_token(force_refresh=True)
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                r = download_with_retry(download_url, dest, headers=headers, timeout_s=P1_TIMEOUT_S)

        tile = TileResult(
            tile_id=f"{sid}/product_{product_id[:8]}",
            status="success" if r.get("success") else "failed",
            local_path=r.get("local_path"),
            size_bytes=r.get("size_bytes"),
            sha256=r.get("sha256"),
            elapsed_ms=r.get("elapsed_ms"),
            error=r.get("error"),
        )
        if r.get("success") and sync_r2:
            r2_key = f"ingestion_p1/esa_sentinel2_l2a/{file_name}"
            sync_r = sync_to_r2(dest, r2_key, content_type="application/zip")
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
    "download_s2_tiles", "get_p1_full_status", "search_scenes",
    "is_credential_ready", "is_armed",
    "CLIENT_KEY", "CLIENT_NAME", "CLIENT_VERSION",
]
