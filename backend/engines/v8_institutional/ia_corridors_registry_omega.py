"""
ia_corridors_registry_omega.py — Loader & API IA-CORRIDORS_P0_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_IA_CORRIDORS_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (loader read-only, ne modifie aucun engine existant).

DOCTRINE
--------
Module d'accès aux 4 datasets IA-CORRIDORS_P0_Ω générés depuis les sources
scientifiques réelles du codebase. Importable par les 4 engines consommateurs :

  - engine_ia_corridors_organic_omega.py
  - engine_connectivite_ecologique_omega.py
  - corridors_vitaux_omega.py
  - ecological_orchestrator_omega.py

API
---
  get_behavior_profile(species: str) -> dict
  get_temporal_signature(species: str, season: str | None = None) -> dict
  get_fragmentation_index(species: str, lat: float, lon: float) -> float | None
  get_corridors_species_schema() -> dict
  get_registry() -> dict
  is_ready() -> bool
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("bionic.ia_corridors_registry")

_DATA_DIR = Path("/app/backend/data/ia_corridors")
_REGISTRY_FILE = _DATA_DIR / "IA_CORRIDORS_REGISTRY_Ω.json"
_BEHAVIOR_FILE = _DATA_DIR / "corridors_behavior_profiles.json"
_TEMPORAL_FILE = _DATA_DIR / "corridors_temporal_signatures.json"
_SPECIES_FILE = _DATA_DIR / "corridors_species.geojson"
_RASTER_FILE = _DATA_DIR / "corridors_fragmentation_index.tif"

_cache: dict = {}


def _load_json(path: Path, key: str) -> dict:
    if key in _cache:
        return _cache[key]
    try:
        if not path.is_file():
            logger.warning(f"[IA_CORRIDORS_REGISTRY] {path.name} absent (run gen_ia_corridors_p0_omega.py)")
            _cache[key] = {}
            return {}
        with open(path) as f:
            _cache[key] = json.load(f)
        return _cache[key]
    except Exception as e:
        logger.warning(f"[IA_CORRIDORS_REGISTRY] load {path.name} failed: {e}")
        _cache[key] = {}
        return {}


def get_registry() -> dict:
    return _load_json(_REGISTRY_FILE, "registry")


def is_ready() -> bool:
    return all(p.is_file() for p in (_BEHAVIOR_FILE, _TEMPORAL_FILE, _SPECIES_FILE, _RASTER_FILE))


def get_behavior_profile(species: str) -> dict:
    """Profil comportemental complet pour une espèce (ou {} si inconnue)."""
    data = _load_json(_BEHAVIOR_FILE, "behavior")
    profiles = data.get("profiles", {})
    return profiles.get((species or "").lower(), {})


def get_temporal_signature(species: str, season: Optional[str] = None) -> dict:
    """Signature temporelle (saisonnalité + phénologie + biogéographie)."""
    data = _load_json(_TEMPORAL_FILE, "temporal")
    sigs = data.get("signatures", {})
    sig = sigs.get((species or "").lower(), {})
    if season:
        return sig.get("saisonnalite", {}).get(season.lower(), {})
    return sig


def get_corridors_species_schema() -> dict:
    """Schéma GeoJSON des corridors (geometries runtime-dynamic)."""
    return _load_json(_SPECIES_FILE, "schema")


def get_fragmentation_index(species: str, lat: float, lon: float) -> Optional[float]:
    """Index de fragmentation 0.0-1.0 (None hors bbox prototype Mauricie).

    Le raster prototype couvre uniquement la bbox sample Mauricie centre.
    Pour bbox externes : retourne None (le caller doit fallback sur sensibilite_pression
    issue de get_behavior_profile['pression_humaine']['sensibilite_pression']).
    """
    if not _RASTER_FILE.is_file():
        return None
    try:
        # Lazy import rasterio (lourd)
        import rasterio
        species_list = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]
        sp = (species or "").lower()
        if sp not in species_list:
            return None
        band_idx = species_list.index(sp) + 1
        with rasterio.open(str(_RASTER_FILE)) as ds:
            # Convertir lat/lon en EPSG:3857
            import math
            x = lon * 20037508.34 / 180.0
            y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
            y = y * 20037508.34 / 180.0
            try:
                row, col = ds.index(x, y)
            except Exception:
                return None
            if row < 0 or row >= ds.height or col < 0 or col >= ds.width:
                return None
            window = rasterio.windows.Window(col, row, 1, 1)
            v = ds.read(band_idx, window=window)
            return float(v[0, 0]) if v.size else None
    except Exception as e:
        logger.debug(f"[IA_CORRIDORS_REGISTRY] raster read failed at ({lat},{lon}): {e}")
        return None


def get_species_list() -> list[str]:
    return ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]


# ─── Disable cache for test/dev ──────────────────────────────────────────────
def reset_cache() -> None:
    _cache.clear()


# ─── Auto-status log au premier import ───────────────────────────────────────
def _log_status() -> None:
    ready = is_ready()
    if ready:
        reg = get_registry()
        n_datasets = len(reg.get("datasets", {}))
        logger.info(f"[IA_CORRIDORS_REGISTRY] ready · {n_datasets} datasets · 5 species")
    elif os.environ.get("IA_CORRIDORS_REGISTRY_LOG_MISSING", "1") == "1":
        logger.warning(
            "[IA_CORRIDORS_REGISTRY] datasets non générés · "
            "run: python3 /app/backend/tools/gen_ia_corridors_p0_omega.py"
        )


_log_status()
