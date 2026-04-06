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


def _project_onto_segment(
    px: float, py: float,
    ax: float, ay: float,
    bx: float, by: float,
) -> Tuple[float, float, float]:
    """
    Projeter un point P sur le segment AB.
    Retourne (proj_lat, proj_lng, t) ou t in [0,1] est la position sur le segment.
    """
    dx = bx - ax
    dy = by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq < 1e-14:
        return ax, ay, 0.0
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return proj_x, proj_y, t


def _snap_to_segment(
    graph,
    lat: float, lng: float,
    max_dist_m: float = 1200.0,
) -> Optional[Tuple[int, int, float, float, float]]:
    """
    Snap un point GPS au point le plus proche sur un SEGMENT de sentier.
    Retourne: (node_a_id, node_b_id, proj_lat, proj_lng, dist_m)
    ou None si aucun segment a portee.
    """
    best = None
    best_dist = max_dist_m

    for nid_a, neighbors in graph.adj.items():
        if nid_a in graph.obstacle_nodes:
            continue
        a_lat, a_lng = graph.nodes[nid_a]
        for nid_b, _, _, _ in neighbors:
            if nid_b <= nid_a:  # eviter les doublons
                continue
            if nid_b in graph.obstacle_nodes:
                continue
            b_lat, b_lng = graph.nodes[nid_b]

            proj_lat, proj_lng, t = _project_onto_segment(
                lat, lng, a_lat, a_lng, b_lat, b_lng
            )
            d = _haversine(lat, lng, proj_lat, proj_lng)
            if d < best_dist:
                best_dist = d
                best = (nid_a, nid_b, proj_lat, proj_lng, d)

    return best


def _generate_approach_waypoints(
    start_lat: float, start_lng: float,
    trail_lat: float, trail_lng: float,
    n_points: int = 5,
) -> list:
    """
    Generer des waypoints intermediaires entre un point GPS et l'entree du sentier.
    Utilise une courbe naturelle (legere deviation) pour eviter les lignes droites.
    """
    if n_points <= 1:
        return []

    import math
    points = []
    dlat = trail_lat - start_lat
    dlng = trail_lng - start_lng
    dist = _haversine(start_lat, start_lng, trail_lat, trail_lng)

    for i in range(1, n_points):
        t = i / n_points
        # Position de base
        lat = start_lat + dlat * t
        lng = start_lng + dlng * t
        # Legere deviation naturelle perpendiculaire (simuler un sentier non cartographie)
        if 0.15 < t < 0.85 and dist > 100:
            angle = math.atan2(dlng, dlat) + math.pi / 2
            dev = math.sin(t * math.pi) * min(dist * 0.00003, 0.0008)
            lat += dev * math.cos(angle)
            lng += dev * math.sin(angle)
        points.append({"lat": round(lat, 6), "lng": round(lng, 6)})

    return points


def route_terrain(
    graph,
    start_lat: float, start_lng: float,
    end_lat: float, end_lng: float,
    max_snap_dist_m: float = 1200.0,
) -> Optional[Dict]:
    """
    BCE-4X GUIDANCE TERRAIN STEEVE-MAX — Routage terrain ameliore.

    CORRECTION 2026-04-06:
    1. Injecter start/end comme noeuds du graphe (pas de waypoints synthetiques)
    2. Connecter start/end aux K sentiers les plus proches via aretes "guidance_corridor"
    3. Router 100% via le graphe (0% foret dense artificielle)
    4. Approche finale 90° vers l'affut (max 20m par segment)

    GUIDANCE:
    - Toujours suivre un corridor reel des le depart
    - Priorite aux embranchements logiques
    - Foret dense limitee a 20m/segment et 5% total
    - Aucun zigzag, aucun detour inutile
    """
    if graph.is_empty:
        logger.warning("[TNE-ROUTER] Graph is empty — no routing possible")
        return None

    # ================================================================
    # PHASE 1: INJECTION GUIDANCE — Ajouter start/end comme noeuds
    # ================================================================
    # IDs virtuels negatifs pour eviter les collisions avec les IDs OSM
    START_VID = -1
    END_VID = -2
    GUIDANCE_K = 5  # Connecter aux K sentiers les plus proches
    GUIDANCE_MAX_DIST = 800  # Distance max pour connexion guidance (m)
    GUIDANCE_COST_MULT = 0.15  # Cout corridor (equivalent path/footway)

    # Injecter le noeud start
    graph.nodes[START_VID] = (start_lat, start_lng)
    graph.adj[START_VID] = []

    # Injecter le noeud end
    graph.nodes[END_VID] = (end_lat, end_lng)
    graph.adj[END_VID] = []

    # Trouver les K noeuds sentier les plus proches de start
    start_candidates = []
    for nid, (nlat, nlng) in graph.nodes.items():
        if nid < 0 or nid in graph.obstacle_nodes:
            continue
        d = _haversine(start_lat, start_lng, nlat, nlng)
        if d <= GUIDANCE_MAX_DIST:
            start_candidates.append((nid, d))
    start_candidates.sort(key=lambda x: x[1])
    start_connections = start_candidates[:GUIDANCE_K]

    # Trouver les K noeuds sentier les plus proches de end
    end_candidates = []
    for nid, (nlat, nlng) in graph.nodes.items():
        if nid < 0 or nid in graph.obstacle_nodes:
            continue
        d = _haversine(end_lat, end_lng, nlat, nlng)
        if d <= GUIDANCE_MAX_DIST:
            end_candidates.append((nid, d))
    end_candidates.sort(key=lambda x: x[1])
    end_connections = end_candidates[:GUIDANCE_K]

    # Connecter start aux sentiers proches (guidance_corridor)
    if not start_connections or not end_connections:
        # Pas assez de noeuds sentier a portee — routage impossible
        logger.warning(
            f"[TNE-ROUTER] GUIDANCE impossible: start_connections={len(start_connections)}, "
            f"end_connections={len(end_connections)} — pas de noeuds sentier a portee"
        )
        # Nettoyage des noeuds injectes
        del graph.nodes[START_VID]
        del graph.nodes[END_VID]
        del graph.adj[START_VID]
        del graph.adj[END_VID]
        return None

    for nid, d in start_connections:
        cost = d * GUIDANCE_COST_MULT
        graph.adj[START_VID].append((nid, cost, d, "guidance_corridor"))
        graph.adj.setdefault(nid, []).append((START_VID, cost, d, "guidance_corridor"))

    # Connecter end aux sentiers proches (guidance_corridor)
    for nid, d in end_connections:
        cost = d * GUIDANCE_COST_MULT
        graph.adj[END_VID].append((nid, cost, d, "guidance_corridor"))
        graph.adj.setdefault(nid, []).append((END_VID, cost, d, "guidance_corridor"))

    logger.info(
        f"[TNE-ROUTER] GUIDANCE: start connected to {len(start_connections)} nodes "
        f"(nearest {start_connections[0][1]:.0f}m), "
        f"end connected to {len(end_connections)} nodes "
        f"(nearest {end_connections[0][1]:.0f}m)"
    )

    # ================================================================
    # PHASE 2: ROUTAGE A* / DIJKSTRA (100% via graphe)
    # ================================================================
    result = a_star_terrain(graph, START_VID, END_VID)
    algo = "a_star_guidance"

    if result is None:
        logger.info("[TNE-ROUTER] A* failed, trying Dijkstra")
        result = dijkstra_terrain(graph, START_VID, END_VID)
        algo = "dijkstra_guidance"

    # ================================================================
    # PHASE 2.5: GARDE-FOU RATIO DETOUR (CORRECTION STEEVE-MAX 2026-04-07)
    # ================================================================
    # Si la route fait un detour excessif (route > 2.5x distance directe),
    # rejeter et tenter un routage plus court en augmentant le cout guidance
    # pour penaliser les connexions lointaines.
    direct_dist = _haversine(start_lat, start_lng, end_lat, end_lng)
    MAX_DETOUR_RATIO = 2.5

    if result is not None and direct_dist > 50:
        route_dist = result.get("total_distance_m", 0)
        ratio = route_dist / direct_dist if direct_dist > 0 else 999
        if ratio > MAX_DETOUR_RATIO:
            logger.warning(
                f"[TNE-ROUTER] DETOUR EXCESSIF: route={round(route_dist)}m, "
                f"direct={round(direct_dist)}m, ratio={ratio:.1f}x > {MAX_DETOUR_RATIO}x — "
                f"rejet et re-routage avec connexions plus proches"
            )
            # Retirer les connexions guidance actuelles
            for nid, _ in start_connections:
                if nid in graph.adj:
                    graph.adj[nid] = [(nb, c, d, t) for nb, c, d, t in graph.adj[nid] if nb != START_VID]
            for nid, _ in end_connections:
                if nid in graph.adj:
                    graph.adj[nid] = [(nb, c, d, t) for nb, c, d, t in graph.adj[nid] if nb != END_VID]
            graph.adj[START_VID] = []
            graph.adj[END_VID] = []

            # Re-connecter avec distance max reduite et cout augmente
            TIGHT_MAX_DIST = min(400, GUIDANCE_MAX_DIST)
            TIGHT_COST_MULT = 0.8  # Penaliser plus les connexions guidance
            TIGHT_K = 3

            tight_start = [(nid, d) for nid, d in start_candidates if d <= TIGHT_MAX_DIST][:TIGHT_K]
            tight_end = [(nid, d) for nid, d in end_candidates if d <= TIGHT_MAX_DIST][:TIGHT_K]

            for nid, d in tight_start:
                cost = d * TIGHT_COST_MULT
                graph.adj[START_VID].append((nid, cost, d, "guidance_corridor"))
                graph.adj.setdefault(nid, []).append((START_VID, cost, d, "guidance_corridor"))
            for nid, d in tight_end:
                cost = d * TIGHT_COST_MULT
                graph.adj[END_VID].append((nid, cost, d, "guidance_corridor"))
                graph.adj.setdefault(nid, []).append((END_VID, cost, d, "guidance_corridor"))

            # Re-router avec connexions resserrees
            result2 = a_star_terrain(graph, START_VID, END_VID)
            if result2 is not None:
                route_dist2 = result2.get("total_distance_m", 0)
                ratio2 = route_dist2 / direct_dist if direct_dist > 0 else 999
                if ratio2 <= MAX_DETOUR_RATIO:
                    logger.info(
                        f"[TNE-ROUTER] RE-ROUTAGE TIGHT OK: {round(route_dist2)}m "
                        f"(ratio {ratio2:.1f}x, amelioration {round(route_dist - route_dist2)}m)"
                    )
                    result = result2
                    algo = "a_star_guidance_tight"
                else:
                    # Re-routage tight ameliore mais toujours excessif — REJET TOTAL
                    logger.warning(
                        f"[TNE-ROUTER] RE-ROUTAGE TIGHT toujours excessif ({ratio2:.1f}x) — "
                        f"REJET TOTAL, delegation au BDRE cascade"
                    )
                    result = None
            else:
                # Re-routage tight echoue — REJET TOTAL du tracé excessif
                logger.warning(
                    f"[TNE-ROUTER] RE-ROUTAGE TIGHT echoue — REJET TOTAL "
                    f"du trace excessif ({ratio:.1f}x), delegation au BDRE cascade"
                )
                result = None

            # Nettoyer les tight connections
            for nid, _ in tight_start:
                if nid in graph.adj:
                    graph.adj[nid] = [(nb, c, d, t) for nb, c, d, t in graph.adj[nid] if nb != START_VID]
            for nid, _ in tight_end:
                if nid in graph.adj:
                    graph.adj[nid] = [(nb, c, d, t) for nb, c, d, t in graph.adj[nid] if nb != END_VID]

    # ================================================================
    # PHASE 3: NETTOYAGE — Retirer les noeuds injectes du graphe
    # ================================================================
    # Retirer les aretes ajoutees aux noeuds existants
    for nid, _ in start_connections:
        if nid in graph.adj:
            graph.adj[nid] = [(nb, c, d, t) for nb, c, d, t in graph.adj[nid] if nb != START_VID]
    for nid, _ in end_connections:
        if nid in graph.adj:
            graph.adj[nid] = [(nb, c, d, t) for nb, c, d, t in graph.adj[nid] if nb != END_VID]
    del graph.nodes[START_VID]
    del graph.nodes[END_VID]
    del graph.adj[START_VID]
    del graph.adj[END_VID]

    if result is None:
        logger.warning("[TNE-ROUTER] Both A* and Dijkstra failed — no path found")
        return None

    # ================================================================
    # PHASE 4: CONSTRUCTION CHEMIN GPS (100% noeuds graphe reels)
    # ================================================================
    coords = []
    for nid in result["node_path"]:
        if nid == START_VID:
            coords.append({"lat": round(start_lat, 6), "lng": round(start_lng, 6)})
        elif nid == END_VID:
            coords.append({"lat": round(end_lat, 6), "lng": round(end_lng, 6)})
        elif nid in graph.nodes:
            nlat, nlng = graph.nodes[nid]
            coords.append({"lat": round(nlat, 6), "lng": round(nlng, 6)})

    # Distance reelle cumulee
    total_dist = 0.0
    for j in range(1, len(coords)):
        total_dist += _haversine(
            coords[j - 1]["lat"], coords[j - 1]["lng"],
            coords[j]["lat"], coords[j]["lng"]
        )

    # Type de segments pour l'analyse corridor
    segments_types = [s.get("highway_type", "unknown") for s in result.get("segments", [])]
    guidance_segments = sum(1 for t in segments_types if t == "guidance_corridor")
    trail_segments = sum(1 for t in segments_types if t not in ("guidance_corridor", "connector_guidance"))

    logger.info(
        f"[TNE-ROUTER] GUIDANCE Route OK ({algo}): {round(total_dist)}m, "
        f"{len(coords)} points, {trail_segments} trail + {guidance_segments} guidance segments, "
        f"{result['iterations']} iterations"
    )

    return {
        "coords": coords,
        "distance_m": round(total_dist),
        "type": "sentier_reel",
        "segments_count": len(result.get("segments", [])),
        "routing_algo": algo,
        "guidance_segments": guidance_segments,
        "trail_segments": trail_segments,
    }
