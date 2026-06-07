"""
mffp_p1_full.py — STUB Phase B (refonte CKAN Données Québec)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_MFFP_PHASE_B_STUB_Ω · 2026-06-07 · BCE-4X · Verrou Phase III

Stub explicite : la voie moderne pour MFFP Forêt Ouverte / LiDAR Québec en
2026 est l'API CKAN Données Québec :
  GET https://www.donneesquebec.ca/recherche/api/3/action/package_show?id=produits-derives-de-base-du-lidar

Cela retourne la liste des resources downloadables (tuiles 1/20 000 par feuillet
SNRC). Chaque resource a une URL directe vers les fichiers LAS/LAZ.

Refonte planifiée pour PHASE_B (session séparée).
"""
from __future__ import annotations

import os
from typing import Any, Optional

CLIENT_KEY = "mffp_foret_ouverte"
CLIENT_NAME = "MFFP-LIDAR-QC-P1-FULL-CLIENT"
CLIENT_VERSION = "V0.0-PHASE-B-STUB"
DATA_TYPE = "LIDAR_FORET_QC_0.5m"


def get_p1_full_status() -> dict[str, Any]:
    return {
        "client_key": CLIENT_KEY,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "data_type": DATA_TYPE,
        "phase": "P1_FULL_PHASE_B_PLANNED",
        "phase_b_voice": "CKAN Données Québec package_show",
        "armed_for_ingestion": os.environ.get("INGESTION_P1_ARMED") == "1",
        "disk_authorized": os.environ.get("INGESTION_P1_DISK_AUTHORIZED") == "1",
        "available": False,
    }


def download_mffp_tiles(
    tile_names: list[str],
    destination_dir: Optional[str] = None,
    sync_r2: bool = True,
    job_id: Optional[str] = None,
    max_tiles: Optional[int] = None,
) -> dict[str, Any]:
    """Stub Phase B — refonte vers CKAN Données Québec API session séparée."""
    raise NotImplementedError(
        "MFFP Forêt Ouverte P1_FULL est planifié pour PHASE B (refonte CKAN "
        "Données Québec package_show api). Voie 2026 : "
        "https://www.donneesquebec.ca/recherche/api/3/action/package_show?id="
        "produits-derives-de-base-du-lidar. Activation hors directive actuelle."
    )


__all__ = ["download_mffp_tiles", "get_p1_full_status", "CLIENT_KEY", "CLIENT_NAME", "CLIENT_VERSION"]
