"""
ENGINE-SCIENCE-Ω — Registry institutionnel des dépendances scientifiques
=========================================================================
Catalogue les sources de données et leurs provenances pour usage partagé
par tous les engines SUPRA-Ω. Expose aussi le registry des engines
actifs (nom, version, description, statut).

Utilisation:
  from engines.v8_institutional.engine_science_omega import (
      register_engine, get_catalog, DATA_SOURCES,
  )
"""
from __future__ import annotations

import time
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
}


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
    """Met a jour metadata d'un engine apres invocation."""
    with _LOCK:
        if name in _REGISTRY:
            _REGISTRY[name]["last_called_at"] = time.time()
            _REGISTRY[name]["call_count"] += 1


def get_catalog() -> list:
    """Retourne le catalog complet."""
    with _LOCK:
        return [dict(e) for e in _REGISTRY.values()]


def get_data_sources() -> dict:
    return dict(DATA_SOURCES)


# Auto-register SCIENCE-Ω itself
register_engine(
    name="ENGINE-SCIENCE-Ω",
    version="V1-SUPRA-2026-04",
    description="Registry central des engines + sources de donnees",
    pillar="GOUVERNANCE",
    dependencies=[],
)
