"""
habitat_fusion_registry_omega.py — Loader & API HABITAT-FUSION_P0_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_IA_HABITAT_FUSION_P0_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (loader read-only, ne modifie aucun engine existant).

DOCTRINE
--------
Loader read-only du manifeste maître `HABITAT_FUSION_P0_REGISTRY_Ω.json`.
Cache mémoire + soft-fail strict. Consommé par :
  - habitat_fusion_engine_p0.py (engine principal)
  - routes/habitat_fusion_p0_router.py (router institutionnel)

API publique
------------
  get_master_registry() -> dict
  get_status() -> str
  get_axes() -> dict
  get_axis(name: str) -> dict
  is_ready() -> bool
  get_species_list() -> list[str]
  get_seasons_list() -> list[str]
  get_completion_ratio() -> float
  reset_cache() -> None
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger("bionic.habitat_fusion_registry")

_DATA_DIR = Path("/app/backend/data/habitat_fusion_p0")
_MASTER_FILE = _DATA_DIR / "HABITAT_FUSION_P0_REGISTRY_Ω.json"

_cache: dict = {}


def _load_json(path: Path, key: str) -> dict:
    if key in _cache:
        return _cache[key]
    try:
        if not path.is_file():
            logger.warning(
                f"[HABITAT_FUSION_P0_REGISTRY] {path.name} absent · "
                f"run: python3 /app/backend/tools/gen_habitat_fusion_p0_registry_omega.py"
            )
            _cache[key] = {}
            return {}
        with open(path) as f:
            _cache[key] = json.load(f)
        return _cache[key]
    except Exception as e:
        logger.warning(f"[HABITAT_FUSION_P0_REGISTRY] load {path.name} failed: {e}")
        _cache[key] = {}
        return {}


def get_master_registry() -> dict:
    return _load_json(_MASTER_FILE, "master")


def get_status() -> str:
    if not _MASTER_FILE.is_file():
        return "UNAVAILABLE"
    return get_master_registry().get("_status", "UNKNOWN")


def get_axes() -> dict:
    return get_master_registry().get("fusion_axes_p0", {})


def get_axis(name: str) -> dict:
    return get_axes().get(name, {})


def is_ready() -> bool:
    """True si manifeste présent et au moins 1 axe READY."""
    if not _MASTER_FILE.is_file():
        return False
    return get_master_registry().get("axes_ready", 0) >= 1


def get_species_list() -> list[str]:
    return get_master_registry().get(
        "species_targeted",
        ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"],
    )


def get_seasons_list() -> list[str]:
    return get_master_registry().get(
        "seasons_targeted", ["printemps", "ete", "automne", "hiver"]
    )


def get_completion_ratio() -> float:
    return float(get_master_registry().get("completion_ratio_p0", 0.0))


def reset_cache() -> None:
    _cache.clear()


# ─── Auto-status log au premier import ───────────────────────────────────────
def _log_status() -> None:
    if not _MASTER_FILE.is_file():
        if os.environ.get("HABITAT_FUSION_P0_LOG_MISSING", "1") == "1":
            logger.warning(
                "[HABITAT_FUSION_P0_REGISTRY] manifeste maître absent · "
                "run: python3 /app/backend/tools/gen_habitat_fusion_p0_registry_omega.py"
            )
        return
    reg = get_master_registry()
    n_ready = reg.get("axes_ready", 0)
    n_pre = reg.get("axes_pre_ingestion", 0)
    n_total = reg.get("axes_total", 0)
    logger.info(
        f"[HABITAT_FUSION_P0_REGISTRY] status={get_status()} · "
        f"axes={n_ready}/{n_total} READY · {n_pre} PRE_INGESTION · "
        f"completion={get_completion_ratio():.2f}"
    )


_log_status()
