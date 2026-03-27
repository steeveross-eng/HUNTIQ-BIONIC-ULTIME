"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
terrain_router.py — Algorithmes de routage terrain

Algorithmes:
1. A* terrain-weighted: pente, densite, praticabilite, securite
2. Dijkstra terrain-cost: pour zones complexes avec cycles

Regles:
- Interdiction totale des traces geometriques artificiels
- Suivre les chemins existants du graphe
- Distances reelles basees sur le graphe
- Log clair en cas de fallback

STEEVE-MAX: Le routeur ne genere JAMAIS de coordonnees synthetiques.
"""
import math
import heapq
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger("bionic.terrain_nav.router")


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance en metres entre deux points GPS."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def a_star_terrain(
    graph,
    start_id: int,
    end_id: int,
    max_iterations: int = 15000,
) -> Optional[Dict]:
    """
    A* avec couts terrain-weighted.
    
    Heuristique: distance Haversine directe * cout minimum de chemin.
    Couts d'aretes: integrent type de chemin, pente, foret, obstacles.
    
    Retourne:
    {
        "node_path": [int, ...],
        "total_cost": float,
        "total_distance_m": float,
        "segments": [{"from": int, "to": int, "distance_m": float, "highway_type": str}, ...]
    }
    ou None si pas de chemin.
    """
    if start_id not in graph.nodes or end_id not in graph.nodes:
        return None

    end_lat, end_lng = graph.nodes[end_id]

    # Min cost multiplier pour l'heuristique (admissible)
    min_cost_per_m = 0.8

    # Priority queue: (f_score, node_id)
    open_set: List[Tuple[float, int]] = [(0.0, start_id)]
    came_from: Dict[int, int] = {}
    g_score: Dict[int, float] = {start_id: 0.0}
    g_distance: Dict[int, float] = {start_id: 0.0}
    edge_info: Dict[int, Tuple[float, str]] = {}

    visited = set()
    iterations = 0

    while open_set and iterations < max_iterations:
        iterations += 1
        _, current = heapq.heappop(open_set)

        if current == end_id:
            # Reconstruire le chemin
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()

            # Construire les segments
            segments = []
            for i in range(len(path) - 1):
                info = edge_info.get(path[i + 1], (0.0, "unknown"))
                segments.append({
                    "from": path[i],
                    "to": path[i + 1],
                    "distance_m": info[0],
                    "highway_type": info[1],
                })

            return {
                "node_path": path,
                "total_cost": g_score[end_id],
                "total_distance_m": g_distance[end_id],
                "segments": segments,
                "iterations": iterations,
            }

        if current in visited:
            continue
        visited.add(current)

        for neighbor, cost, dist, hw_type in graph.adj.get(current, []):
            if neighbor in visited:
                continue
            if neighbor in graph.obstacle_nodes:
                continue

            tentative_g = g_score[current] + cost
            tentative_dist = g_distance[current] + dist

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                g_distance[neighbor] = tentative_dist
                edge_info[neighbor] = (dist, hw_type)

                n_lat, n_lng = graph.nodes[neighbor]
                h = _haversine(n_lat, n_lng, end_lat, end_lng) * min_cost_per_m
                f = tentative_g + h
                heapq.heappush(open_set, (f, neighbor))

    logger.warning(f"[TNE-ROUTER] A* exhausted after {iterations} iterations")
    return None


def dijkstra_terrain(
    graph,
    start_id: int,
    end_id: int,
    max_iterations: int = 20000,
) -> Optional[Dict]:
    """
    Dijkstra terrain-cost pour zones complexes.
    Plus lent que A* mais garanti optimal dans les graphes avec cycles.
    Utilise en fallback quand A* echoue.
    """
    if start_id not in graph.nodes or end_id not in graph.nodes:
        return None

    dist_map: Dict[int, float] = {start_id: 0.0}
    real_dist: Dict[int, float] = {start_id: 0.0}
    came_from: Dict[int, int] = {}
    edge_info: Dict[int, Tuple[float, str]] = {}
    pq: List[Tuple[float, int]] = [(0.0, start_id)]
    visited = set()
    iterations = 0

    while pq and iterations < max_iterations:
        iterations += 1
        cost_so_far, current = heapq.heappop(pq)

        if current in visited:
            continue
        visited.add(current)

        if current == end_id:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()

            segments = []
            for i in range(len(path) - 1):
                info = edge_info.get(path[i + 1], (0.0, "unknown"))
                segments.append({
                    "from": path[i],
                    "to": path[i + 1],
                    "distance_m": info[0],
                    "highway_type": info[1],
                })

            return {
                "node_path": path,
                "total_cost": dist_map[end_id],
                "total_distance_m": real_dist[end_id],
                "segments": segments,
                "iterations": iterations,
            }

        for neighbor, cost, d, hw_type in graph.adj.get(current, []):
            if neighbor in visited:
                continue
            if neighbor in graph.obstacle_nodes:
                continue

            new_cost = cost_so_far + cost
            if new_cost < dist_map.get(neighbor, float('inf')):
                dist_map[neighbor] = new_cost
                real_dist[neighbor] = real_dist[current] + d
                came_from[neighbor] = current
                edge_info[neighbor] = (d, hw_type)
                heapq.heappush(pq, (new_cost, neighbor))

    logger.warning(f"[TNE-ROUTER] Dijkstra exhausted after {iterations} iterations")
    return None


def route_terrain(
    graph,
    start_lat: float, start_lng: float,
    end_lat: float, end_lng: float,
    max_snap_dist_m: float = 1200.0,
) -> Optional[Dict]:
    """
    Router entre deux points via le graphe terrain.
    
    Strategie:
    1. Snap start/end aux noeuds du graphe les plus proches
    2. A* terrain-weighted
    3. Fallback Dijkstra si A* echoue
    4. Construire le chemin complet avec coordonnees GPS
    
    Retourne:
    {
        "coords": [{"lat": ..., "lng": ...}, ...],
        "distance_m": float,
        "type": "sentier_reel",
        "segments_count": int,
        "routing_algo": "a_star" | "dijkstra",
    }
    ou None si aucun chemin trouve.
    """
    if graph.is_empty:
        logger.warning("[TNE-ROUTER] Graph is empty — no routing possible")
        return None

    # Snap aux noeuds les plus proches
    start_node = graph.nearest_node(start_lat, start_lng, max_dist_m=max_snap_dist_m)
    end_node = graph.nearest_node(end_lat, end_lng, max_dist_m=max_snap_dist_m)

    if start_node is None:
        logger.warning(f"[TNE-ROUTER] No trail node within {max_snap_dist_m}m of start ({start_lat:.4f}, {start_lng:.4f})")
        return None
    if end_node is None:
        logger.warning(f"[TNE-ROUTER] No trail node within {max_snap_dist_m}m of end ({end_lat:.4f}, {end_lng:.4f})")
        return None

    if start_node == end_node:
        s_lat, s_lng = graph.nodes[start_node]
        return {
            "coords": [
                {"lat": round(start_lat, 6), "lng": round(start_lng, 6)},
                {"lat": round(s_lat, 6), "lng": round(s_lng, 6)},
                {"lat": round(end_lat, 6), "lng": round(end_lng, 6)},
            ],
            "distance_m": round(_haversine(start_lat, start_lng, end_lat, end_lng)),
            "type": "sentier_reel",
            "segments_count": 2,
            "routing_algo": "trivial",
        }

    # Tentative 1: A* terrain-weighted
    result = a_star_terrain(graph, start_node, end_node)
    algo = "a_star"

    # Tentative 2: Dijkstra si A* echoue
    if result is None:
        logger.info("[TNE-ROUTER] A* failed, trying Dijkstra")
        result = dijkstra_terrain(graph, start_node, end_node)
        algo = "dijkstra"

    if result is None:
        logger.warning("[TNE-ROUTER] Both A* and Dijkstra failed — no path found")
        return None

    # Construire le chemin GPS
    coords = [{"lat": round(start_lat, 6), "lng": round(start_lng, 6)}]
    for nid in result["node_path"]:
        if nid in graph.nodes:
            nlat, nlng = graph.nodes[nid]
            coords.append({"lat": round(nlat, 6), "lng": round(nlng, 6)})
    coords.append({"lat": round(end_lat, 6), "lng": round(end_lng, 6)})

    # Distance reelle cumulee
    total_dist = 0.0
    for j in range(1, len(coords)):
        total_dist += _haversine(
            coords[j - 1]["lat"], coords[j - 1]["lng"],
            coords[j]["lat"], coords[j]["lng"]
        )

    logger.info(
        f"[TNE-ROUTER] Route OK ({algo}): {round(total_dist)}m, "
        f"{len(coords)} points, {len(result['segments'])} segments, "
        f"{result['iterations']} iterations"
    )

    return {
        "coords": coords,
        "distance_m": round(total_dist),
        "type": "sentier_reel",
        "segments_count": len(result["segments"]),
        "routing_algo": algo,
    }
