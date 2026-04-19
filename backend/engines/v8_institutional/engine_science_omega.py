"""
ENGINE-SCIENCE-Ω — Registry institutionnel + catalog scientifique
===================================================================
V2: catalogue scientifique complet ingéré depuis les 5 rapports BCE-4X
(orignal, chevreuil, wapiti, ours noir, dindon sauvage).

Structures exposées:
  - STUDY_RECORD / DATASET_RECORD / SPECIES_PROFILE / PARAMETER_SET / ENGINE_LINK
  - register_engine(), mark_call(), get_catalog(), get_data_sources()
  - get_species_profile(species), get_studies(), get_datasets(), get_engine_links(engine_name)

Utilisation:
  from engines.v8_institutional.engine_science_omega import (
      register_engine, mark_call, get_catalog, get_species_profile,
      get_studies, get_datasets, get_engine_links,
  )
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from threading import RLock
from typing import Optional

# Registry global des engines actifs (thread-safe)
_REGISTRY: dict[str, dict] = {}
_LOCK = RLock()

# Sources de donnees institutionnelles (reutilisables par tous les engines)
DATA_SOURCES = {
    "LIDAR_WCS_1M": {
        "description": "LiDAR WCS 1m topographie Québec",
        "provider": "MFFP/WCS",
        "realtime": False,
        "precision_m": 1,
    },
    "IRDA_PEDOLOGIE": {
        "description": "IRDA pédologie (drainage, soil_moisture, nappe)",
        "provider": "IRDA",
        "realtime": False,
        "precision_m": 250,
    },
    "OPEN_METEO": {
        "description": "Open-Meteo weather + elevation + radiation",
        "provider": "Open-Meteo",
        "realtime": True,
        "precision_m": 1000,
    },
    "USGS_MOVEMENT": {"description": "USGS telemetry", "provider": "USGS", "realtime": False},
    "NOAA_CLIMATE": {"description": "NOAA climat (neige, temp)", "provider": "NOAA", "realtime": False},
    "NASA_EARTHDATA": {"description": "NASA EarthData NDVI + thermiques", "provider": "NASA", "realtime": False},
    "MFFP_INVENTAIRES": {"description": "MFFP QC faune + forêt", "provider": "MFFP", "realtime": False},
}

# Lazy-loaded catalog from JSON
_CATALOG_FILE = Path("/app/backend/data/science_omega_catalog.json")
_CATALOG_CACHE: Optional[dict] = None


def _load_catalog() -> dict:
    """Charge le catalog scientifique (lazy, cache)."""
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE
    try:
        _CATALOG_CACHE = json.loads(_CATALOG_FILE.read_text())
    except Exception:
        _CATALOG_CACHE = {"species_profiles": {}, "studies": [], "datasets": [], "engine_links": {}, "gaps": []}
    return _CATALOG_CACHE


def register_engine(
    name: str,
    version: str,
    description: str,
    pillar: str = "BIO-SYSTEME",
    dependencies: Optional[list] = None,
):
    """Enregistre un engine dans le catalog."""
    with _LOCK:
        _REGISTRY[name] = {
            "name": name,
            "version": version,
            "description": description,
            "pillar": pillar,
            "dependencies": dependencies or [],
            "registered_at": time.time(),
            "last_called_at": None,
            "call_count": 0,
        }


def mark_call(name: str):
    with _LOCK:
        if name in _REGISTRY:
            _REGISTRY[name]["last_called_at"] = time.time()
            _REGISTRY[name]["call_count"] += 1


def get_catalog() -> list:
    with _LOCK:
        return [dict(e) for e in _REGISTRY.values()]


def get_data_sources() -> dict:
    return dict(DATA_SOURCES)


def get_species_profile(species: str) -> dict:
    cat = _load_catalog()
    # Map communs
    mapping = {
        "cerf": "chevreuil", "deer": "chevreuil", "chevreuil": "chevreuil",
        "orignal": "orignal", "moose": "orignal",
        "wapiti": "wapiti", "elk": "wapiti",
        "ours": "ours_noir", "bear": "ours_noir", "ours_noir": "ours_noir",
        "dindon": "dindon_sauvage", "turkey": "dindon_sauvage",
    }
    key = mapping.get(species.lower(), species.lower())
    return cat.get("species_profiles", {}).get(key, {})


def get_studies() -> list:
    return list(_load_catalog().get("studies", []))


def get_datasets() -> list:
    return list(_load_catalog().get("datasets", []))


def get_engine_links(engine_name: Optional[str] = None) -> dict | list:
    links = _load_catalog().get("engine_links", {})
    if engine_name:
        return links.get(engine_name, [])
    return dict(links)


def get_science_gaps() -> list:
    return list(_load_catalog().get("gaps", []))


def get_catalog_summary() -> dict:
    cat = _load_catalog()
    return {
        "version": cat.get("meta", {}).get("version"),
        "species_count": len(cat.get("species_profiles", {})),
        "species_list": list(cat.get("species_profiles", {}).keys()),
        "studies_count": len(cat.get("studies", [])),
        "datasets_count": len(cat.get("datasets", [])),
        "engine_links_count": len(cat.get("engine_links", {})),
        "gaps_count": len(cat.get("gaps", [])),
    }


# Auto-register SCIENCE-Ω itself
register_engine(
    name="ENGINE-SCIENCE-Ω",
    version="V2-SUPRA-2026-04",
    description="Registry central engines + catalogue scientifique (5 espèces, studies, datasets, engine_links)",
    pillar="GOUVERNANCE",
    dependencies=list(DATA_SOURCES.keys()),
)
