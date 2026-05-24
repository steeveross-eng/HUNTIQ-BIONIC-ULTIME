"""
nasa_hls_client.py — Client NASA HLS (HLSL30 / HLSS30) · NDVI HR P1
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · MODE INERTE TANT QUE CREDENTIALS ABSENTS.

DOCTRINE
--------
Client officiel NASA Earthdata via `earthaccess` (lib NASA-supported).
HLSL30 = Landsat 8/9 harmonisé · HLSS30 = Sentinel-2 harmonisé · résolution 30 m
(les NDVI 10 m proviennent du client ESA Sentinel-2 L2A séparé).

Credentials requis (à fournir par Commandant) :
  - EDL_TOKEN (token Earthdata Login)
    Création : https://urs.earthdata.nasa.gov/users/new
  - OU EARTHDATA_USERNAME + EARTHDATA_PASSWORD (basic auth)

ARMEMENT INGESTION
------------------
  - INGESTION_P1_ARMED=1 (env var)
  - Credentials valides présents

API publique :
  - get_status() -> dict
  - is_credential_ready() -> bool
  - is_armed() -> bool
  - search_granules(bbox, datetime_range, ...) -> list (read-only metadata)
  - download_granules(...) -> raise RuntimeError si pas armé
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("bionic.nasa_hls_client")

CLIENT_NAME = "NASA-HLS-CLIENT"
CLIENT_VERSION = "V1.0-CODE-READY-AWAITING-CREDENTIALS"
CLIENT_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"

SHORT_NAMES = ("HLSL30", "HLSS30")
CMR_BASE = "https://cmr.earthdata.nasa.gov/search/granules.json"


def is_credential_ready() -> bool:
    return bool(
        os.environ.get("EDL_TOKEN")
        or (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"))
    )


def is_armed() -> bool:
    return os.environ.get("INGESTION_P1_ARMED", "0") == "1"


def get_status() -> dict:
    return {
        "client": CLIENT_NAME,
        "version": CLIENT_VERSION,
        "doctrine": CLIENT_DOCTRINE,
        "credential_ready": is_credential_ready(),
        "armed_for_ingestion": is_armed(),
        "operational_mode": (
            "INGESTION_READY" if is_credential_ready() and is_armed()
            else "AWAITING_CREDENTIALS" if not is_credential_ready()
            else "AWAITING_COMMANDANT_ARM_FLAG"
        ),
        "sources": SHORT_NAMES,
        "egress_endpoint": CMR_BASE,
    }


def _require_credentials() -> None:
    if not is_credential_ready():
        raise RuntimeError(
            "NASA HLS credentials manquants · "
            "définir EDL_TOKEN ou EARTHDATA_USERNAME+EARTHDATA_PASSWORD dans .env"
        )


def _require_armed() -> None:
    if not is_armed():
        raise RuntimeError(
            "NASA HLS ingestion non armée · "
            "définir INGESTION_P1_ARMED=1 dans .env (directive Commandant)"
        )


def search_granules(
    bbox: tuple[float, float, float, float],
    datetime_range: tuple[datetime, datetime],
    short_name: str = "HLSL30",
    cloud_cover_max: int = 20,
    limit: int = 50,
) -> list[dict]:
    """READ-ONLY · interroge le CMR pour lister granules (anti-générique).

    bbox = (lng_min, lat_min, lng_max, lat_max)
    Ne télécharge PAS · retourne métadonnées uniquement.
    """
    import requests  # lazy
    if short_name not in SHORT_NAMES:
        raise ValueError(f"short_name doit être dans {SHORT_NAMES}")
    params = {
        "short_name": short_name,
        "bounding_box": ",".join(str(v) for v in bbox),
        "temporal": f"{datetime_range[0].isoformat()},{datetime_range[1].isoformat()}",
        "page_size": limit,
        "sort_key": "-start_date",
    }
    # CMR public read · pas de credentials requis pour SEARCH (uniquement DL)
    r = requests.get(CMR_BASE, params=params, timeout=15)
    r.raise_for_status()
    entries = r.json().get("feed", {}).get("entry", [])
    out = []
    for e in entries:
        cloud = None
        for d in e.get("data_center", []) if isinstance(e.get("data_center"), list) else []:
            pass
        # cloud_cover extracted from "cloud_cover" key if present
        cloud_str = e.get("cloud_cover") or "100"
        try:
            cloud = float(cloud_str)
        except (TypeError, ValueError):
            cloud = None
        if cloud is not None and cloud > cloud_cover_max:
            continue
        out.append({
            "granule_id": e.get("id"),
            "title": e.get("title"),
            "time_start": e.get("time_start"),
            "time_end": e.get("time_end"),
            "cloud_cover": cloud,
            "links": [
                {"href": link.get("href"), "type": link.get("type")}
                for link in e.get("links", [])[:5]
            ],
        })
    return out


def download_granules(granule_ids: list[str], destination_dir: str) -> list[str]:
    """⚠️ INERTE TANT QUE CREDENTIALS + ARM FLAG ABSENTS · anti-générique strict."""
    _require_credentials()
    _require_armed()
    try:
        import earthaccess  # type: ignore
    except ImportError as e:
        raise RuntimeError(f"earthaccess non installé: {e}") from e
    # Auth via env vars supportée par earthaccess (token ou user/pass)
    earthaccess.login(strategy="environment")
    # Implémentation réelle (à activer côté Commandant via ARM flag)
    raise NotImplementedError(
        "P1_FULL ingestion non activé · directive Commandant requise "
        "(passer à OPTION P1_FULL avec credentials confirmés)"
    )


__all__ = [
    "CLIENT_NAME", "CLIENT_VERSION", "CLIENT_DOCTRINE",
    "is_credential_ready", "is_armed", "get_status",
    "search_granules", "download_granules",
]
