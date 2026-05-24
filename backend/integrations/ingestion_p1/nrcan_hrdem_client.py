"""
nrcan_hrdem_client.py — Client NRCan HRDEM (High Resolution DEM) · LiDAR P1
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · MODE INERTE TANT QUE NON ARMÉ.

DOCTRINE
--------
Client NRCan HRDEM — Open Government Licence Canada (PAS de credentials requis).
Couverture pan-Canada · résolution 1 m (parfois 0.5 m sur zones LiDAR récentes).
Format : GeoTIFF (.tif) · tuiles ~50 MB chacune.

Endpoint :
  - https://ftp.maps.canada.ca/pub/elevation/dem_mne/highresolution_hauteresolution/

ARMEMENT INGESTION
------------------
  - INGESTION_P1_ARMED=1 (Commandant)
  - INGESTION_P1_DISK_AUTHORIZED=1 (confirmation extension disque)

API publique :
  - get_status() -> dict
  - is_credential_ready() -> bool (toujours True · open data)
  - is_armed() -> bool
  - list_available_tiles(bbox) -> list (read-only metadata)
  - download_tiles(...) -> raise RuntimeError si pas armé
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("bionic.nrcan_hrdem_client")

CLIENT_NAME = "NRCAN-HRDEM-CLIENT"
CLIENT_VERSION = "V1.0-CODE-READY-OPEN-DATA"
CLIENT_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"

HRDEM_FTP_BASE = "https://ftp.maps.canada.ca/pub/elevation/dem_mne/highresolution_hauteresolution/"
HRDEM_INDEX_URL = f"{HRDEM_FTP_BASE}index.html"


def is_credential_ready() -> bool:
    # Open data NRCan · pas de credentials requis
    return True


def is_armed() -> bool:
    return (
        os.environ.get("INGESTION_P1_ARMED", "0") == "1"
        and os.environ.get("INGESTION_P1_DISK_AUTHORIZED", "0") == "1"
    )


def get_status() -> dict:
    return {
        "client": CLIENT_NAME,
        "version": CLIENT_VERSION,
        "doctrine": CLIENT_DOCTRINE,
        "credential_ready": True,
        "armed_for_ingestion": is_armed(),
        "operational_mode": (
            "INGESTION_READY" if is_armed()
            else "AWAITING_COMMANDANT_ARM_AND_DISK_AUTH"
        ),
        "license": "Open Government Licence — Canada (CC-BY 2.0)",
        "source": "NRCan HRDEM (High Resolution DEM)",
        "resolution_m": 1.0,
        "ftp_endpoint": HRDEM_FTP_BASE,
    }


def _require_armed() -> None:
    if not is_armed():
        raise RuntimeError(
            "NRCan HRDEM ingestion non armée · "
            "INGESTION_P1_ARMED=1 + INGESTION_P1_DISK_AUTHORIZED=1 requis"
        )


def list_available_tiles(bbox: tuple[float, float, float, float]) -> dict:
    """READ-ONLY · retourne l'index HRDEM (HTTP HEAD uniquement, pas de DL)."""
    import requests
    r = requests.head(HRDEM_INDEX_URL, timeout=10, allow_redirects=True)
    return {
        "index_url": HRDEM_INDEX_URL,
        "index_status": r.status_code,
        "bbox_query": bbox,
        "_note": "Listing complet via HTTP GET sur index.html · non exécuté en mode STRUCTURAL+",
    }


def download_tiles(tile_names: list[str], destination_dir: str) -> list[str]:
    """⚠️ INERTE TANT QUE ARM + DISK AUTH FLAGS ABSENTS · anti-générique strict."""
    _require_armed()
    raise NotImplementedError(
        "P1_FULL ingestion NRCan non activée · "
        "directive Commandant + autorisation extension disque requises"
    )


__all__ = [
    "CLIENT_NAME", "CLIENT_VERSION", "CLIENT_DOCTRINE",
    "is_credential_ready", "is_armed", "get_status",
    "list_available_tiles", "download_tiles",
]
