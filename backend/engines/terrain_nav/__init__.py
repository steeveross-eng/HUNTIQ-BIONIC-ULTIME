"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
__init__.py — Interface publique du moteur de navigation terrain

API publique:
- get_terrain_nav(lat, lng) -> TerrainGraph (cache automatique)
- navigate_terrain(graph, start, end) -> route result
- get_terrain_stats(lat, lng) -> stats du graphe

STEEVE-MAX: Ce module est le SEUL point d'entree pour le routage terrain.
Localisation protegee par ULTRA-MAX++ (File Integrity Lock).
"""
import logging
from typing import Dict, Any, Optional, Tuple

from .terrain_sources import fetch_terrain_data
from .terrain_graph import TerrainGraph, build_terrain_graph
from .terrain_router import route_terrain

logger = logging.getLogger("bionic.terrain_nav")

# Cache global: { zone_key: TerrainGraph }
_nav_cache: Dict[str, TerrainGraph] = {}
# Cache terrain_data brut pour le routage terrain-aware
_terrain_data_cache: Dict[str, Dict] = {}


def _cache_key(lat: float, lng: float) -> str:
    # BCE-4X P0 B4: Elargi de 111m (3 decimales) a 1.1km (2 decimales) — STEEVE-MAX 2026-03-28
    return f"tne:{round(lat, 2)}:{round(lng, 2)}"


def get_terrain_nav(lat: float, lng: float, radius_m: int = 2000) -> TerrainGraph:
    """
    Obtenir le graphe de navigation terrain pour une zone.
    
    1. Verifie le cache en memoire
    2. Si absent: fetch Overpass + build graphe + cache
    3. Retourne le graphe (peut etre vide si Overpass echoue)
    
    Le graphe est cache indefiniment en memoire pour la duree du process.
    """
    key = _cache_key(lat, lng)
    if key in _nav_cache:
        logger.info(f"[TNE] Cache HIT: {key}")
        return _nav_cache[key]

    logger.info(f"[TNE] Building terrain graph for ({lat:.4f}, {lng:.4f}), radius={radius_m}m")

    # Fetch terrain data from Overpass (UNE SEULE FOIS)
    terrain_data = fetch_terrain_data(lat, lng, radius_m)

    # Build graph
    graph = build_terrain_graph(terrain_data)

    _nav_cache[key] = graph
    _terrain_data_cache[key] = terrain_data
    return graph


def get_raw_terrain_data(lat: float, lng: float) -> Optional[Dict]:
    """
    Obtenir les donnees terrain brutes (waterways, clearings, forest, obstacles).
    Utilisees par le routage terrain-aware quand pas de sentiers formels.
    """
    key = _cache_key(lat, lng)
    return _terrain_data_cache.get(key)


def navigate_terrain(
    graph: TerrainGraph,
    start_lat: float, start_lng: float,
    end_lat: float, end_lng: float,
) -> Optional[Dict]:
    """
    Router entre deux points via le graphe terrain.
    
    Retourne:
    {
        "coords": [{"lat": ..., "lng": ...}, ...],
        "distance_m": int,
        "type": "sentier_reel",
        "segments_count": int,
        "routing_algo": str,
    }
    ou None si pas de chemin.
    """
    return route_terrain(graph, start_lat, start_lng, end_lat, end_lng)


def get_terrain_stats(lat: float, lng: float) -> Dict[str, Any]:
    """Stats du graphe terrain pour une zone (debug/audit)."""
    key = _cache_key(lat, lng)
    if key in _nav_cache:
        g = _nav_cache[key]
        return {
            "cached": True,
            "empty": g.is_empty,
            **g.stats,
        }
    return {"cached": False, "empty": True}
