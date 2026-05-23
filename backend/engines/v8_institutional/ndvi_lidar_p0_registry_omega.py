"""
ndvi_lidar_p0_registry_omega.py — Loader & API NDVI+LIDAR P0
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (loader read-only, ne modifie aucun engine existant).

DOCTRINE
--------
Module d'accès aux placeholders structurels NDVI HR + LiDAR Pan-Canada P0.
Importable par les 7 engines HR-ready :
  - engine_ia_vision_ecologique_omega.py
  - engine_ia_vision_registry_omega.py
  - lidar_irda_v11.py (mode étendu HR)
  - engine_terrain_v10_supra.py (mode HR-ready)
  - engine_canopee_thermique_omega.py
  - ecological_orchestrator_omega.py
  - habitat_fusion_engine_p0.py

API publique
------------
  get_status() -> str
  has_ndvi_hr() -> bool
  has_lidar_pancanada() -> bool
  is_hr_ingested() -> bool
  get_ndvi_hr_registry() -> dict
  get_lidar_pancanada_registry() -> dict
  get_habitat_fusion_manifest() -> dict
  get_master_registry() -> dict
  get_ndvi_hr_placeholder_path() -> Path
  get_lidar_pancanada_placeholder_path() -> Path
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("bionic.ndvi_lidar_p0_registry")

_DATA_DIR = Path("/app/backend/data/ndvi_lidar_p0")
_MASTER_FILE = _DATA_DIR / "NDVI_LIDAR_P0_REGISTRY_Ω.json"
_NDVI_REG_FILE = _DATA_DIR / "ndvi_hr_registry_Ω.json"
_LIDAR_REG_FILE = _DATA_DIR / "lidar_pancanada_registry_Ω.json"
_HABITAT_MANIFEST_FILE = _DATA_DIR / "habitat_fusion_sources_manifest.json"
_NDVI_PLACEHOLDER = _DATA_DIR / "ndvi_hr_placeholder.tif"
_LIDAR_PLACEHOLDER = _DATA_DIR / "lidar_pancanada_placeholder.las"

_cache: dict = {}


def _load_json(path: Path, key: str) -> dict:
    if key in _cache:
        return _cache[key]
    try:
        if not path.is_file():
            logger.warning(
                f"[NDVI_LIDAR_P0_REGISTRY] {path.name} absent · "
                f"run: python3 /app/backend/tools/gen_ndvi_lidar_p0_omega.py"
            )
            _cache[key] = {}
            return {}
        with open(path) as f:
            _cache[key] = json.load(f)
        return _cache[key]
    except Exception as e:
        logger.warning(f"[NDVI_LIDAR_P0_REGISTRY] load {path.name} failed: {e}")
        _cache[key] = {}
        return {}


def get_master_registry() -> dict:
    return _load_json(_MASTER_FILE, "master")


def get_ndvi_hr_registry() -> dict:
    return _load_json(_NDVI_REG_FILE, "ndvi")


def get_lidar_pancanada_registry() -> dict:
    return _load_json(_LIDAR_REG_FILE, "lidar")


def get_habitat_fusion_manifest() -> dict:
    return _load_json(_HABITAT_MANIFEST_FILE, "habitat")


def get_status() -> str:
    """Status global · STRUCTURAL_ACTIVATED_PRE_INGESTION | HR_INGESTED | UNAVAILABLE."""
    if not _MASTER_FILE.is_file():
        return "UNAVAILABLE"
    return get_master_registry().get("_status", "UNKNOWN")


def has_ndvi_hr() -> bool:
    return _NDVI_REG_FILE.is_file() and _NDVI_PLACEHOLDER.is_file()


def has_lidar_pancanada() -> bool:
    return _LIDAR_REG_FILE.is_file() and _LIDAR_PLACEHOLDER.is_file()


def is_hr_ingested() -> bool:
    """True si données réelles ingérées (post P1), False en mode placeholder P0."""
    return get_status() == "HR_INGESTED"


def get_ndvi_hr_placeholder_path() -> Path:
    return _NDVI_PLACEHOLDER


def get_lidar_pancanada_placeholder_path() -> Path:
    return _LIDAR_PLACEHOLDER


def reset_cache() -> None:
    _cache.clear()


# ─── Auto-status log au premier import ───────────────────────────────────────
def _log_status() -> None:
    if not _MASTER_FILE.is_file():
        if os.environ.get("NDVI_LIDAR_P0_LOG_MISSING", "1") == "1":
            logger.warning(
                "[NDVI_LIDAR_P0_REGISTRY] datasets non générés · "
                "run: python3 /app/backend/tools/gen_ndvi_lidar_p0_omega.py"
            )
        return
    status = get_status()
    n_ndvi = "ready" if has_ndvi_hr() else "missing"
    n_lidar = "ready" if has_lidar_pancanada() else "missing"
    logger.info(
        f"[NDVI_LIDAR_P0_REGISTRY] status={status} · ndvi_hr={n_ndvi} · "
        f"lidar_pancanada={n_lidar}"
    )


_log_status()
