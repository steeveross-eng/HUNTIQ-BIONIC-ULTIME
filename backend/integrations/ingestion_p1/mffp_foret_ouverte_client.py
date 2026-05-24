"""
mffp_foret_ouverte_client.py — Client MFFP Forêt Ouverte (Québec) · LiDAR P1
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · MODE INERTE TANT QUE NON ARMÉ.

DOCTRINE
--------
Client MFFP (Ministère des Forêts, de la Faune et des Parcs · QC).
Données ouvertes Forêt Ouverte — pas de credentials requis.
Couverture LiDAR forestière QC · résolution 0.5-1 m (densité ≥6 pts/m²).

Endpoints :
  - WMS  : https://www.foretouverte.gouv.qc.ca/wms/MFFP_FORET_OUVERTE
  - WFS  : https://www.foretouverte.gouv.qc.ca/wfs/MFFP_FORET_OUVERTE
  - Atlas LiDAR : https://www.foretouverte.gouv.qc.ca/lidar/

ARMEMENT INGESTION
------------------
  - INGESTION_P1_ARMED=1 (Commandant)
  - INGESTION_P1_DISK_AUTHORIZED=1 (extension disque confirmée)

API publique :
  - get_status() -> dict
  - list_lidar_tiles(bbox) -> list (read-only WFS query)
  - download_lidar_las(...) -> raise RuntimeError si pas armé
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("bionic.mffp_foret_ouverte_client")

CLIENT_NAME = "MFFP-FORET-OUVERTE-CLIENT"
CLIENT_VERSION = "V1.0-CODE-READY-OPEN-DATA"
CLIENT_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"

WMS_BASE = "https://www.foretouverte.gouv.qc.ca/wms/MFFP_FORET_OUVERTE"
WFS_BASE = "https://www.foretouverte.gouv.qc.ca/wfs/MFFP_FORET_OUVERTE"
LIDAR_ATLAS_BASE = "https://www.foretouverte.gouv.qc.ca/lidar/"


def is_credential_ready() -> bool:
    return True  # Open data


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
        "license": "Données ouvertes Québec (Licence ouverte 2.0)",
        "source": "MFFP Forêt Ouverte · LiDAR forestier QC",
        "resolution_m": 0.5,
        "density_pts_m2_target": 6.0,
        "wms_endpoint": WMS_BASE,
        "wfs_endpoint": WFS_BASE,
        "atlas_endpoint": LIDAR_ATLAS_BASE,
    }


def _require_armed() -> None:
    if not is_armed():
        raise RuntimeError(
            "MFFP Forêt Ouverte ingestion non armée · "
            "INGESTION_P1_ARMED=1 + INGESTION_P1_DISK_AUTHORIZED=1 requis"
        )


def list_lidar_tiles(bbox: tuple[float, float, float, float]) -> dict:
    """READ-ONLY · WFS GetCapabilities (anti-générique)."""
    import requests
    params = {
        "service": "WFS", "version": "2.0.0", "request": "GetCapabilities",
    }
    r = requests.get(WFS_BASE, params=params, timeout=15)
    return {
        "wfs_endpoint": WFS_BASE,
        "capabilities_status": r.status_code,
        "capabilities_size": len(r.content),
        "bbox_query": bbox,
        "_note": (
            "Listing tuiles LiDAR requires parsing GetCapabilities XML · "
            "non exécuté en mode STRUCTURAL+"
        ),
    }


def download_lidar_las(tile_names: list[str], destination_dir: str) -> list[str]:
    """⚠️ INERTE TANT QUE ARM + DISK AUTH FLAGS ABSENTS · anti-générique strict."""
    _require_armed()
    raise NotImplementedError(
        "P1_FULL ingestion MFFP non activée · "
        "directive Commandant + autorisation extension disque requises"
    )


__all__ = [
    "CLIENT_NAME", "CLIENT_VERSION", "CLIENT_DOCTRINE",
    "is_credential_ready", "is_armed", "get_status",
    "list_lidar_tiles", "download_lidar_las",
]
