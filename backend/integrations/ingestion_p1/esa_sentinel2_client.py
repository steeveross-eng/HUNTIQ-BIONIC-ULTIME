"""
esa_sentinel2_client.py — Client ESA Sentinel-2 L2A · NDVI 10 m P1
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · MODE INERTE TANT QUE CREDENTIALS ABSENTS.

DOCTRINE
--------
Client ESA Copernicus Data Space Ecosystem (CDSE) pour Sentinel-2 L2A.
Bandes B04 (Red) + B08 (NIR) à 10 m → NDVI = (B08-B04)/(B08+B04).

Credentials requis :
  - COPERNICUS_USERNAME + COPERNICUS_PASSWORD
    Création : https://dataspace.copernicus.eu

Lib utilisée :
  - sentinelhub (officiel ESA, déjà installée 3.11.5)
  - pystac_client (CDSE expose endpoint STAC compatible)

API publique :
  - get_status() -> dict
  - is_credential_ready() -> bool
  - search_scenes(bbox, datetime_range, ...) -> list (read-only metadata)
  - download_scenes(...) -> raise RuntimeError si pas armé
"""
from __future__ import annotations

import logging
import os
from datetime import datetime

logger = logging.getLogger("bionic.esa_sentinel2_client")

CLIENT_NAME = "ESA-SENTINEL2-L2A-CLIENT"
CLIENT_VERSION = "V1.0-CODE-READY-AWAITING-CREDENTIALS"
CLIENT_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"

CDSE_STAC_ENDPOINT = "https://catalogue.dataspace.copernicus.eu/stac"
CDSE_AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


def is_credential_ready() -> bool:
    return bool(
        os.environ.get("COPERNICUS_USERNAME") and os.environ.get("COPERNICUS_PASSWORD")
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
        "source": "Sentinel-2 L2A (B04 Red + B08 NIR · 10 m)",
        "stac_endpoint": CDSE_STAC_ENDPOINT,
        "auth_endpoint": CDSE_AUTH_URL,
    }


def _require_credentials() -> None:
    if not is_credential_ready():
        raise RuntimeError(
            "ESA Copernicus credentials manquants · "
            "définir COPERNICUS_USERNAME + COPERNICUS_PASSWORD dans .env"
        )


def _require_armed() -> None:
    if not os.environ.get("INGESTION_P1_ARMED", "0") == "1":
        raise RuntimeError(
            "ESA ingestion non armée · INGESTION_P1_ARMED=1 requis (directive Commandant)"
        )


def search_scenes(
    bbox: tuple[float, float, float, float],
    datetime_range: tuple[datetime, datetime],
    cloud_cover_max: int = 20,
    limit: int = 50,
) -> list[dict]:
    """READ-ONLY · interroge l'endpoint STAC CDSE (anti-générique).

    bbox = (lng_min, lat_min, lng_max, lat_max)
    Ne télécharge PAS · retourne métadonnées uniquement.
    """
    try:
        from pystac_client import Client  # type: ignore
    except ImportError as e:
        raise RuntimeError(f"pystac_client non installé: {e}") from e

    cli = Client.open(CDSE_STAC_ENDPOINT)
    search = cli.search(
        collections=["SENTINEL-2"],
        bbox=bbox,
        datetime=f"{datetime_range[0].isoformat()}/{datetime_range[1].isoformat()}",
        query={
            "s2:processing_level": {"eq": "L2A"},
            "eo:cloud_cover": {"lt": cloud_cover_max},
        },
        limit=limit,
    )
    items = list(search.items())
    out = []
    for it in items[:limit]:
        out.append({
            "scene_id": it.id,
            "datetime": it.datetime.isoformat() if it.datetime else None,
            "cloud_cover": it.properties.get("eo:cloud_cover"),
            "tile_id": it.properties.get("grid:code"),
            "bbox": list(it.bbox) if it.bbox else None,
            "assets_count": len(it.assets),
        })
    return out


def download_scenes(scene_ids: list[str], bands: list[str], destination_dir: str) -> list[str]:
    """⚠️ INERTE TANT QUE CREDENTIALS + ARM FLAG ABSENTS · anti-générique strict."""
    _require_credentials()
    _require_armed()
    raise NotImplementedError(
        "P1_FULL ingestion non activée · directive Commandant requise "
        "(passer à OPTION P1_FULL avec credentials confirmés)"
    )


__all__ = [
    "CLIENT_NAME", "CLIENT_VERSION", "CLIENT_DOCTRINE",
    "is_credential_ready", "is_armed", "get_status",
    "search_scenes", "download_scenes",
]
