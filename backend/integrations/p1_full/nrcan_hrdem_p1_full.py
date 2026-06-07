"""
nrcan_hrdem_p1_full.py — STUB Phase B (refonte STAC AWS canelevation-dem)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_NRCAN_PHASE_B_STUB_Ω · 2026-06-07 · BCE-4X · Verrou Phase III

Stub explicite : la voie moderne pour NRCan HRDEM en 2026 est le bucket
STAC AWS public `canelevation-dem` (registry.opendata.aws/canelevation-dem)
qui expose 4 produits via boto3 S3 anonymous :
  - hrdem-mosaic-1m  (CONUS 1m pan-Canada)
  - hrdem-mosaic-2m  (2m)
  - hrdem-lidar      (LiDAR raw)
  - hrdem-arcticdem  (Arctic)

Refonte planifiée pour PHASE_B (session séparée).
"""
from __future__ import annotations

import os
from typing import Any, Optional

CLIENT_KEY = "nrcan_hrdem"
CLIENT_NAME = "NRCAN-HRDEM-P1-FULL-CLIENT"
CLIENT_VERSION = "V0.0-PHASE-B-STUB"
DATA_TYPE = "LIDAR_HRDEM_1m"


def get_p1_full_status() -> dict[str, Any]:
    return {
        "client_key": CLIENT_KEY,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "data_type": DATA_TYPE,
        "phase": "P1_FULL_PHASE_B_PLANNED",
        "phase_b_voice": "STAC AWS canelevation-dem",
        "armed_for_ingestion": os.environ.get("INGESTION_P1_ARMED") == "1",
        "disk_authorized": os.environ.get("INGESTION_P1_DISK_AUTHORIZED") == "1",
        "available": False,
    }


def download_hrdem_tiles(
    tile_names: list[str],
    destination_dir: Optional[str] = None,
    sync_r2: bool = True,
    job_id: Optional[str] = None,
    max_tiles: Optional[int] = None,
) -> dict[str, Any]:
    """Stub Phase B — refonte vers STAC AWS canelevation-dem session séparée."""
    raise NotImplementedError(
        "NRCan HRDEM P1_FULL est planifié pour PHASE B (refonte STAC AWS "
        "canelevation-dem bucket). Voie 2026 : boto3 anonymous client S3 sur "
        "registry.opendata.aws/canelevation-dem. Activation hors directive actuelle."
    )


__all__ = ["download_hrdem_tiles", "get_p1_full_status", "CLIENT_KEY", "CLIENT_NAME", "CLIENT_VERSION"]
