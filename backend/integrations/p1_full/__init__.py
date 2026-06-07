"""
p1_full/__init__.py — P1_FULL package init (additif strict)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_PHASE_A_Ω · COMMANDANT STEEVE-MAX · 2026-06-07
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Package P1_FULL · sortie du MODE INERTE Phase 0 → ingestion réelle.

PHASE A (livrée maintenant) :
  - NASA HLS (NDVI HR 30m harmonisé)
  - ESA Sentinel-2 L2A (NDVI 10m)

PHASE B (session séparée · refonte STAC AWS + CKAN Données Québec) :
  - NRCan HRDEM (LiDAR 1m)
  - MFFP Forêt Ouverte (LiDAR 0.5m)

DOCTRINE :
  - 4 wrappers minces (1 par client) + 1 module commun streamer
  - Cible storage : disque local /var/data/p1_ingest/ + sync R2 différé
  - Limites safety configurables via env (P1_MAX_TILES, P1_MAX_SIZE_MB, P1_TIMEOUT_S)
  - Mode async via FastAPI BackgroundTasks · job_id polling
  - Strict additif · Verrou Phase III intact
"""
from .download_streamer_omega import (  # noqa
    JobStatus,
    JobStore,
    get_job_store,
    download_with_retry,
    sync_to_r2,
    DEFAULT_DEST_BASE,
    P1_MAX_TILES,
    P1_MAX_SIZE_MB,
    P1_TIMEOUT_S,
)
from .nasa_hls_p1_full import download_hls_tiles, get_p1_full_status as nasa_p1_status  # noqa
from .esa_sentinel2_p1_full import download_s2_tiles, get_p1_full_status as esa_p1_status  # noqa
from .nrcan_hrdem_p1_full import download_hrdem_tiles, get_p1_full_status as nrcan_p1_status  # noqa
from .mffp_p1_full import download_mffp_tiles, get_p1_full_status as mffp_p1_status  # noqa

__all__ = [
    "JobStatus", "JobStore", "get_job_store",
    "download_with_retry", "sync_to_r2",
    "DEFAULT_DEST_BASE", "P1_MAX_TILES", "P1_MAX_SIZE_MB", "P1_TIMEOUT_S",
    "download_hls_tiles", "download_s2_tiles",
    "download_hrdem_tiles", "download_mffp_tiles",
    "nasa_p1_status", "esa_p1_status", "nrcan_p1_status", "mffp_p1_status",
]
