"""
BDRE — Source Registry (F1/F2)
BCE-4X GOLDEN V6+ | Phase 1
Registre des 8 sources externes + 8 sources internes.
Maintient l'etat de sante de chaque source.
"""
import logging
import time
from typing import Dict, Optional

logger = logging.getLogger("bionic.bdre.registry")


# Definition des sources externes
EXTERNAL_SOURCES = {
    "SRC-01": {
        "name": "OpenStreetMap Overpass (trails)",
        "type": "external_api",
        "endpoint": "4 miroirs paralleles",
        "cache_dir": "data/terrain_cache/",
        "ttl_seconds": 7 * 24 * 3600,
        "category": "trails",
    },
    "SRC-02": {
        "name": "OpenStreetMap Overpass (eau/obstacles)",
        "type": "external_api",
        "endpoint": "Via TNE",
        "cache_dir": "data/terrain_cache/",
        "ttl_seconds": 7 * 24 * 3600,
        "category": "obstacles",
    },
    "SRC-03": {
        "name": "Access Engine V6 OSM trail graph",
        "type": "internal_cache",
        "endpoint": "modules/access_engine_v6/cache/",
        "cache_dir": "modules/access_engine_v6/cache/",
        "ttl_seconds": 7 * 24 * 3600,
        "category": "trails",
    },
    "SRC-04": {
        "name": "Foret Ouverte (MFFP Quebec)",
        "type": "external_api",
        "endpoint": "WMS/WFS Quebec",
        "cache_dir": None,
        "ttl_seconds": None,
        "category": "vegetation",
        "connected": False,
    },
    "SRC-05": {
        "name": "VGO (Vegetal Quebec)",
        "type": "external_api",
        "endpoint": "API MFFP",
        "cache_dir": None,
        "ttl_seconds": None,
        "category": "vegetation",
        "connected": False,
    },
    "SRC-06": {
        "name": "DEM/SRTM Elevation",
        "type": "external_api",
        "endpoint": "Via dem_router",
        "cache_dir": "data/elevation_cache/",
        "ttl_seconds": 30 * 24 * 3600,
        "category": "elevation",
        "connected": False,
    },
    "SRC-07": {
        "name": "WeatherAPI",
        "type": "external_api",
        "endpoint": "https://api.weatherapi.com/v1/",
        "cache_dir": None,
        "ttl_seconds": 3600,
        "category": "meteo",
    },
    "SRC-08": {
        "name": "GPS Tracks (import utilisateur)",
        "type": "user_data",
        "endpoint": "MongoDB",
        "cache_dir": None,
        "ttl_seconds": None,
        "category": "gps",
        "connected": False,
    },
}

# Definition des sources internes
INTERNAL_SOURCES = {
    "INT-01": {
        "name": "TERRAIN_COSTS",
        "type": "hardcoded",
        "reference": "corridor_10x.py:TERRAIN_COSTS",
        "category": "costs_animal",
        "mutable": False,
    },
    "INT-02": {
        "name": "HUMAN_TRAJET_COSTS",
        "type": "hardcoded",
        "reference": "corridor_10x.py:HUMAN_TRAJET_COSTS",
        "category": "costs_human",
        "mutable": False,
    },
    "INT-03": {
        "name": "LAYER_TO_TERRAIN",
        "type": "hardcoded",
        "reference": "zone_engine_core_v2.py:LAYER_TO_TERRAIN",
        "category": "mapping",
        "mutable": False,
    },
    "INT-04": {
        "name": "Ecological DB V8",
        "type": "hardcoded",
        "reference": "ecological_database_v8.py:EcologicalDB",
        "category": "ecology",
        "mutable": False,
    },
    "INT-05": {
        "name": "Species Rules",
        "type": "hardcoded",
        "reference": "knowledge/species/*.py",
        "category": "species",
        "mutable": False,
    },
    "INT-06": {
        "name": "Water Exclusion DB",
        "type": "hardcoded",
        "reference": "knowledge/terrain/water_exclusion.py",
        "category": "water",
        "mutable": False,
    },
    "INT-07": {
        "name": "OSM_HIGHWAY_TO_TERRAIN",
        "type": "hardcoded",
        "reference": "engine_osm_lite.py:OSM_HIGHWAY_TO_TERRAIN",
        "category": "mapping_osm",
        "mutable": False,
    },
    "INT-08": {
        "name": "ROAD_COSTS",
        "type": "hardcoded",
        "reference": "trail_cost_grid_v7.py:ROAD_COSTS",
        "category": "costs_road",
        "mutable": False,
    },
}


class SourceRegistry:
    """
    Registre central de toutes les sources de donnees BDRE.
    Maintient l'etat de sante (DC-BDRE-01) pour chaque source.
    """

    def __init__(self):
        self._health: Dict[str, dict] = {}
        self._init_sources()
        logger.info(
            f"[BDRE-REGISTRY] Initialise: {len(EXTERNAL_SOURCES)} externes, "
            f"{len(INTERNAL_SOURCES)} internes"
        )

    def _init_sources(self):
        """Initialiser le registre de sante pour toutes les sources."""
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        for src_id, src_def in EXTERNAL_SOURCES.items():
            connected = src_def.get("connected", True)
            self._health[src_id] = {
                "source_id": src_id,
                "name": src_def["name"],
                "type": src_def["type"],
                "category": src_def["category"],
                "status": "healthy" if connected else "not_connected",
                "latency_ms": 0.0,
                "last_check": now,
                "score": 0.0 if not connected else 0.5,
                "checks_24h": 0,
                "failures_24h": 0,
                "availability_pct": 100.0 if connected else 0.0,
            }

        for src_id, src_def in INTERNAL_SOURCES.items():
            self._health[src_id] = {
                "source_id": src_id,
                "name": src_def["name"],
                "type": src_def["type"],
                "category": src_def["category"],
                "status": "healthy",
                "latency_ms": 0.0,
                "last_check": now,
                "score": 0.90,
                "checks_24h": 0,
                "failures_24h": 0,
                "availability_pct": 100.0,
            }

    def get_health(self, source_id: str) -> dict:
        """Obtenir l'etat de sante d'une source (DC-BDRE-01)."""
        if source_id not in self._health:
            return {
                "source_id": source_id,
                "status": "unknown",
                "latency_ms": 0.0,
                "last_check": "",
                "score": 0.0,
                "checks_24h": 0,
                "failures_24h": 0,
                "availability_pct": 0.0,
            }
        return dict(self._health[source_id])

    def update_status(self, source_id: str, status: str, latency_ms: float = 0.0) -> None:
        """Mettre a jour le statut d'une source."""
        if source_id not in self._health:
            return
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        h = self._health[source_id]
        h["status"] = status
        h["latency_ms"] = latency_ms
        h["last_check"] = now
        h["checks_24h"] += 1
        if status in ("down", "empty"):
            h["failures_24h"] += 1
        if h["checks_24h"] > 0:
            h["availability_pct"] = round(
                (1.0 - h["failures_24h"] / h["checks_24h"]) * 100, 2
            )

    def update_score(self, source_id: str, score: float) -> None:
        """Mettre a jour le score de fiabilite d'une source."""
        if source_id in self._health:
            self._health[source_id]["score"] = round(score, 4)

    def get_all_sources(self) -> list:
        """Obtenir le registre complet."""
        return [dict(h) for h in self._health.values()]

    def get_external_sources(self) -> list:
        """Sources externes uniquement."""
        return [dict(self._health[sid]) for sid in EXTERNAL_SOURCES if sid in self._health]

    def get_internal_sources(self) -> list:
        """Sources internes uniquement."""
        return [dict(self._health[sid]) for sid in INTERNAL_SOURCES if sid in self._health]

    def get_source_definition(self, source_id: str) -> Optional[dict]:
        """Obtenir la definition d'une source."""
        if source_id in EXTERNAL_SOURCES:
            return dict(EXTERNAL_SOURCES[source_id])
        if source_id in INTERNAL_SOURCES:
            return dict(INTERNAL_SOURCES[source_id])
        return None
