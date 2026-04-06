"""
ACCESS ENGINE V6 — Orchestrateur pipeline unique
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Pipeline unique de calcul des chemins d'acces aux affuts.
Phase 1: Trail-First Dijkstra (graphe sentiers OSM)
Phase 2: Terrain Grid A* (grille de couts combinee)
Fusion: Assemblage sentier + terrain → segments classifies
"""
import hashlib
import json
import logging
import math
import time

from .osm_trails import fetch_osm_trails
from .access_cost_grid import build_cost_grid
from .vegetation_analyzer import analyze_vegetation_corridor
from .pathfinder_v6 import (
    dijkstra_trail_graph,
    astar_grid,
    find_nearest_trail_node,
)
from .segment_classifier import classify_path_segments

logger = logging.getLogger("access_engine_v6.engine")

# Cache resultats en memoire — TTL 10 minutes
_result_cache = {}
_CACHE_TTL = 600

WALKING_SPEED_KMH = 3.5  # Vitesse de marche moyenne en foret


def _cache_key(origin: dict, destination: dict, month: int, species: str) -> str:
    raw = json.dumps({"o": origin, "d": destination, "m": month, "s": species}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _check_cache(key: str):
    entry = _result_cache.get(key)
    if entry and time.time() - entry["ts"] < _CACHE_TTL:
        return entry["data"]
    return None


def _store_cache(key: str, data: dict):
    _result_cache[key] = {"ts": time.time(), "data": data}
    # Nettoyage cache expire (max 100 entrees)
    if len(_result_cache) > 100:
        now = time.time()
        expired = [k for k, v in _result_cache.items() if now - v["ts"] > _CACHE_TTL]
        for k in expired:
            del _result_cache[k]


def _latlon_to_grid(lat, lng, center_lat, center_lng, resolution_m, grid_size):
    half = grid_size // 2
    gx = int((lng - center_lng) * 111320 * math.cos(math.radians(center_lat)) / resolution_m) + half
    gy = int((lat - center_lat) * 111320 / resolution_m) + half
    return (gx, gy)


def _grid_to_latlon(gx, gy, center_lat, center_lng, resolution_m, grid_size):
    half = grid_size // 2
    lat = center_lat + (gy - half) * resolution_m / 111320
    lng = center_lng + (gx - half) * resolution_m / (111320 * math.cos(math.radians(center_lat)))
    return (lat, lng)


def _estimate_time_min(distance_m: float, trail_pct: float) -> float:
    """Estime le temps de marche en minutes. Sentier = plus rapide."""
    trail_speed = WALKING_SPEED_KMH * 1000 / 60  # m/min
    offtrail_speed = trail_speed * 0.5
    avg_speed = trail_speed * (trail_pct / 100) + offtrail_speed * (1 - trail_pct / 100)
    if avg_speed <= 0:
        return 0
    return round(distance_m / avg_speed, 1)


async def compute_access_route(
    origin: dict,
    destination: dict,
    month: int = 10,
    species: str = "orignal",
    max_off_trail_km: float = 2.0,
    prefer_trails: bool = True,
    analysis_radius_m: int = 3000,
) -> dict:
    """
    Pipeline unique — Calcul du chemin d'acces optimal.
    Conformite GOLDEN: 1 pipeline, 1 orchestration, 1 source de verite.
    """
    cache_key = _cache_key(origin, destination, month, species)
    cached = _check_cache(cache_key)
    if cached:
        logger.info("Access route cache HIT")
        return {**cached, "cache_hit": True}

    o_lat, o_lng = origin["lat"], origin["lng"]
    d_lat, d_lng = destination["lat"], destination["lng"]

    # Centre d'analyse = milieu entre origin et destination
    center_lat = (o_lat + d_lat) / 2
    center_lng = (o_lng + d_lng) / 2

    # ═══════════════════════════════════════════
    # PHASE 1: Trail-First Dijkstra (graphe OSM)
    # ═══════════════════════════════════════════
    logger.info(f"Phase 1: Fetching OSM trails around {center_lat:.4f},{center_lng:.4f} r={analysis_radius_m}m")
    trail_graph = await fetch_osm_trails(center_lat, center_lng, analysis_radius_m)
    trail_nodes = trail_graph.get("nodes", {})
    trail_edges = trail_graph.get("edges", [])

    trail_path_ids = []
    trail_path_coords = []

    if trail_nodes and trail_edges:
        start_node = find_nearest_trail_node(o_lat, o_lng, trail_nodes)
        goal_node = find_nearest_trail_node(d_lat, d_lng, trail_nodes)

        if start_node and goal_node and start_node != goal_node:
            trail_path_ids = dijkstra_trail_graph(trail_nodes, trail_edges, start_node, goal_node)
            for nid in trail_path_ids:
                node = trail_nodes.get(str(nid))
                if node:
                    trail_path_coords.append([node["lng"], node["lat"]])

    has_trail = len(trail_path_ids) > 1
    logger.info(f"Phase 1 result: {'SUCCESS' if has_trail else 'NO TRAIL'} — {len(trail_path_ids)} nodes")

    # ═══════════════════════════════════════════
    # PHASE 2: Terrain Grid A* (grille de couts)
    # ═══════════════════════════════════════════
    logger.info("Phase 2: Building cost grid + A* pathfinding")
    cost_data = build_cost_grid(
        center_lat, center_lng, analysis_radius_m,
        trail_nodes, trail_edges, resolution_m=10,
    )

    grid = cost_data["grid"]
    grid_size = cost_data["grid_size"]
    resolution_m = cost_data["resolution_m"]

    # Determiner le point de depart Phase 2
    if has_trail and trail_path_coords:
        # Partir du dernier noeud sentier (jonction sentier→terrain)
        last_trail = trail_path_coords[-1]
        p2_start_lat, p2_start_lng = last_trail[1], last_trail[0]
    else:
        p2_start_lat, p2_start_lng = o_lat, o_lng

    start_grid = _latlon_to_grid(p2_start_lat, p2_start_lng, center_lat, center_lng, resolution_m, grid_size)
    goal_grid = _latlon_to_grid(d_lat, d_lng, center_lat, center_lng, resolution_m, grid_size)

    # Trouver cellules valides les plus proches si hors grille
    start_grid = _find_valid_cell(grid, start_grid, grid_size)
    goal_grid = _find_valid_cell(grid, goal_grid, grid_size)

    grid_path = []
    if start_grid and goal_grid and start_grid != goal_grid:
        grid_path = astar_grid(grid, start_grid, goal_grid, grid_size)

    logger.info(f"Phase 2 result: {len(grid_path)} cells in path")

    # ═══════════════════════════════════════════
    # FUSION: Assemblage et classification
    # ═══════════════════════════════════════════
    segments = classify_path_segments(
        grid_path, grid,
        {
            "resolution_m": resolution_m,
            "center_lat": center_lat,
            "center_lng": center_lng,
            "grid_size": grid_size,
        },
        trail_path_ids, trail_nodes,
    )

    # Si Phase 1 a un sentier, l'ajouter en premier segment
    if has_trail and trail_path_coords and len(trail_path_coords) >= 2:
        trail_distance = _compute_path_distance(trail_path_coords)
        trail_segment = {
            "type": "trail",
            "color": "#2ECC71",
            "label": "Sentier reel OSM",
            "style": "solid",
            "coordinates": trail_path_coords,
            "distance_m": round(trail_distance, 1),
            "trail_name": _get_trail_name(trail_path_ids, trail_edges),
            "surface": _get_trail_surface(trail_path_ids, trail_edges),
        }
        segments = [trail_segment] + segments

    # Analyse vegetation pour segments hors-sentier
    for seg in segments:
        if seg["type"] in ("off_trail_optimized", "non_conformant"):
            veg = analyze_vegetation_corridor(
                seg["coordinates"], grid, grid_size, resolution_m, center_lat, center_lng,
            )
            seg["vegetation"] = veg

    # Metriques globales
    total_distance = sum(s.get("distance_m", 0) for s in segments)
    trail_distance = sum(s.get("distance_m", 0) for s in segments if s["type"] == "trail")
    trail_pct = round((trail_distance / max(total_distance, 1)) * 100, 1)
    total_cost = sum(
        sum(grid.get(c, {}).get("cost", 5.0) for c in [])
        for _ in segments
    )

    # Comptage zones vegetation
    fav_zones = sum(1 for s in segments if s.get("vegetation", {}).get("favorable_ratio", 0) > 0.5)
    unfav_zones = sum(1 for s in segments if s.get("vegetation", {}).get("favorable_ratio", 1) <= 0.5 and s["type"] != "trail")

    # Strategie dominante
    if trail_pct > 70:
        dominant_strategy = "Sentier principal — effort minimal"
    elif trail_pct > 30:
        dominant_strategy = f"Sentier principal + traversee foret ({100 - trail_pct:.0f}% hors-sentier)"
    elif segments:
        dominant_strategy = "Hors-sentier predominant — vegetation analysee"
    else:
        dominant_strategy = "Aucun chemin trouve"

    # Warnings
    warnings = []
    for seg in segments:
        if seg["type"] == "non_conformant":
            warnings.append(f"Segment non conforme: {seg.get('distance_m', 0):.0f}m — vegetation dense/pente excessive")
    off_trail_total = sum(s.get("distance_m", 0) for s in segments if s["type"] != "trail")
    if off_trail_total > max_off_trail_km * 1000:
        warnings.append(f"Distance hors-sentier ({off_trail_total:.0f}m) depasse la limite ({max_off_trail_km}km)")

    result = {
        "status": "ok" if segments else "no_route",
        "route": {
            "total_distance_m": round(total_distance, 1),
            "total_cost": round(total_cost, 1),
            "estimated_time_min": _estimate_time_min(total_distance, trail_pct),
            "trail_percentage": trail_pct,
            "segments": segments,
            "vegetation_analysis": {
                "favorable_zones": fav_zones,
                "unfavorable_zones": unfav_zones,
                "dominant_strategy": dominant_strategy,
            },
            "warnings": warnings,
        },
        "cache_hit": False,
    }

    _store_cache(cache_key, result)
    logger.info(f"Access route computed: {total_distance:.0f}m, {trail_pct}% trail, {len(segments)} segments")
    return result


def _find_valid_cell(grid, target, grid_size, max_search=20):
    """Trouve la cellule valide la plus proche de target dans la grille."""
    gx, gy = target
    if target in grid:
        return target
    for r in range(1, max_search):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if abs(dx) != r and abs(dy) != r:
                    continue
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size and (nx, ny) in grid:
                    return (nx, ny)
    return None


def _compute_path_distance(coords):
    """Distance totale d'une liste de [lng, lat]."""
    total = 0
    for i in range(len(coords) - 1):
        lng1, lat1 = coords[i]
        lng2, lat2 = coords[i + 1]
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
        total += 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return total


def _get_trail_name(path_ids, edges):
    """Extrait le nom du sentier le plus frequent."""
    names = {}
    id_set = set(str(x) for x in path_ids)
    for edge in edges:
        if str(edge["from"]) in id_set or str(edge["to"]) in id_set:
            name = edge.get("name", "")
            if name:
                names[name] = names.get(name, 0) + 1
    if names:
        return max(names, key=names.get)
    return ""


def _get_trail_surface(path_ids, edges):
    """Extrait la surface predominante du sentier."""
    surfaces = {}
    id_set = set(str(x) for x in path_ids)
    for edge in edges:
        if str(edge["from"]) in id_set or str(edge["to"]) in id_set:
            s = edge.get("surface", "unknown")
            surfaces[s] = surfaces.get(s, 0) + 1
    if surfaces:
        return max(surfaces, key=surfaces.get)
    return "unknown"
