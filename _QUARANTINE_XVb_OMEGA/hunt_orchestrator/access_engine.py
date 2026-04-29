"""
BCE-4X P0 — ENGINE ACCES DYNAMIQUE v2
=======================================
Moteur de routage d'acces aux affuts base sur donnees REELLES.

Donnees REELLES utilisees:
- Reseau de sentiers OSM (via terrain_nav/Overpass API)
- Cours d'eau OSM (bords = corridors naturels preferes)
- Clairières/prairies OSM (edges = corridors secondaires)
- Zones d'eau (cache 41K polygones)
- Foret dense/obstacles (via terrain_nav)
- Contraintes vent/odeurs (via vent_odeurs engine)

Priorite de routage:
1. Sentiers OSM existants (cout 1.0-1.6x)
2. Bords de ruisseau (cout 1.2x)
3. Bordures de clairiere (cout 1.4x)
4. Clairiere degagee (cout 2.0x)
5. Foret ouverte (cout 4.0x)
6. Foret dense (cout 8.0x)
EVITER: marecages (50x), eau (999x), zone contamination (15x)

STEEVE-MAX 2026-03-28 — Standard institutionnel.
"""

import math
import heapq
import logging
from typing import Dict, List, Any, Optional, Tuple, Set

logger = logging.getLogger("bionic.hunt_orchestrator.access_engine")


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _point_in_scent_cone(lat: float, lng: float, scent_zone: Dict) -> bool:
    """Verifier si un point est dans la zone de contamination olfactive."""
    polygon = scent_zone.get("polygon", [])
    if not polygon or len(polygon) < 3:
        return False
    # Ray-casting point-in-polygon
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        pi = polygon[i]
        pj = polygon[j]
        yi, xi = pi["lat"], pi["lng"]
        yj, xj = pj["lat"], pj["lng"]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _build_terrain_grid(
    entry_lat: float, entry_lng: float,
    blind_lat: float, blind_lng: float,
    terrain_data: Optional[Dict],
    scent_zone: Dict,
    feeding_sites: List[Dict],
    grid_spacing_m: float = 35,
) -> Tuple[Dict[int, Tuple[float, float]], Dict[int, Dict[int, float]], Dict[int, str]]:
    """
    Construire une grille de navigation terrain avec couts ponderes.
    Integre cours d'eau, clairieres, foret, obstacles, et contamination.

    Retourne: (nodes, adjacency, node_types)
    """
    from engines.terrain_nav.terrain_costs import (
        STREAM_BANK_COST, CLEARING_EDGE_COST, CLEARING_INTERIOR_COST,
        OFF_TRAIL_COST, DENSE_FOREST_COST, WETLAND_COST, WATER_COST,
        SCENT_ZONE_PENALTY,
    )

    # Bounding box avec marge 15%
    min_lat = min(entry_lat, blind_lat)
    max_lat = max(entry_lat, blind_lat)
    min_lng = min(entry_lng, blind_lng)
    max_lng = max(entry_lng, blind_lng)
    lat_margin = (max_lat - min_lat) * 0.25 + grid_spacing_m / 111320
    lng_margin = (max_lng - min_lng) * 0.25 + grid_spacing_m / (111320 * math.cos(math.radians(entry_lat)))
    min_lat -= lat_margin
    max_lat += lat_margin
    min_lng -= lng_margin
    max_lng += lng_margin

    # Convertir espacement en degres
    dlat = grid_spacing_m / 111320
    dlng = grid_spacing_m / (111320 * math.cos(math.radians(entry_lat)))

    # Extraire les features OSM pour la classification
    waterway_segments: List[List[Tuple[float, float]]] = []
    forest_segments: List[List[Tuple[float, float]]] = []
    obstacle_segments: List[List[Tuple[float, float]]] = []
    clearing_segments: List[List[Tuple[float, float]]] = []

    if terrain_data:
        nc = terrain_data.get("waterways", {}).get("node_coords", {})
        for way in terrain_data.get("waterways", {}).get("ways", []):
            seg = []
            for nid in way.get("nodes", []):
                if nid in nc:
                    seg.append(nc[nid])
            if len(seg) >= 2:
                waterway_segments.append(seg)

        for way in terrain_data.get("forest", {}).get("ways", []):
            seg = []
            for nid in way.get("nodes", []):
                if nid in nc:
                    seg.append(nc[nid])
            if len(seg) >= 2:
                forest_segments.append(seg)

        for way in terrain_data.get("obstacles", {}).get("ways", []):
            seg = []
            for nid in way.get("nodes", []):
                if nid in nc:
                    seg.append(nc[nid])
            if len(seg) >= 2:
                obstacle_segments.append(seg)

        for way in terrain_data.get("clearings", {}).get("ways", []):
            seg = []
            for nid in way.get("nodes", []):
                if nid in nc:
                    seg.append(nc[nid])
            if len(seg) >= 2:
                clearing_segments.append(seg)

    # Classification locale d'un point
    def _classify_point(lat: float, lng: float) -> str:
        """Retourne le type de terrain pour un point."""
        # Distance au plus proche segment de chaque type
        min_water_dist = _min_dist_to_segments(lat, lng, obstacle_segments)
        if min_water_dist < 10:
            return "water"

        min_wetland_dist = min_water_dist  # Les obstacles incluent wetlands
        if min_wetland_dist < 20:
            return "wetland"

        min_stream_dist = _min_dist_to_segments(lat, lng, waterway_segments)
        if min_stream_dist < 25:  # <25m du ruisseau = bord de ruisseau
            return "stream_bank"

        min_clearing_dist = _min_dist_to_segments(lat, lng, clearing_segments)
        if min_clearing_dist < 20:
            return "clearing_edge"
        if min_clearing_dist < 60:
            return "clearing"

        min_forest_dist = _min_dist_to_segments(lat, lng, forest_segments)
        if min_forest_dist < 30:
            return "dense_forest"

        return "open_forest"

    # Generer les noeuds de la grille
    nodes: Dict[int, Tuple[float, float]] = {}
    node_types: Dict[int, str] = {}
    nid = 0

    # Ajouter entry et blind comme noeuds speciaux
    nodes[nid] = (entry_lat, entry_lng)
    node_types[nid] = "entry"
    entry_nid = nid
    nid += 1

    nodes[nid] = (blind_lat, blind_lng)
    node_types[nid] = "blind"
    blind_nid = nid
    nid += 1

    # Ajouter les noeuds le long des cours d'eau (corridors preferes)
    for seg in waterway_segments:
        for pt_lat, pt_lng in seg:
            if min_lat <= pt_lat <= max_lat and min_lng <= pt_lng <= max_lng:
                # Ajouter le point du cours d'eau
                nodes[nid] = (pt_lat, pt_lng)
                node_types[nid] = "stream_bank"
                nid += 1
                # Ajouter des points decales sur les berges (±15m)
                for offset_m in [-15, 15]:
                    b_lat = pt_lat + offset_m / 111320
                    if min_lat <= b_lat <= max_lat:
                        nodes[nid] = (b_lat, pt_lng)
                        node_types[nid] = "stream_bank"
                        nid += 1

    # Ajouter les noeuds le long des clairieres
    for seg in clearing_segments:
        for pt_lat, pt_lng in seg:
            if min_lat <= pt_lat <= max_lat and min_lng <= pt_lng <= max_lng:
                nodes[nid] = (pt_lat, pt_lng)
                node_types[nid] = "clearing_edge"
                nid += 1

    # Ajouter la grille reguliere
    lat = min_lat
    while lat <= max_lat:
        lng = min_lng
        while lng <= max_lng:
            nodes[nid] = (lat, lng)
            cls = _classify_point(lat, lng)
            node_types[nid] = cls
            nid += 1
            lng += dlng
        lat += dlat

    logger.info(f"[ACCESS-GRID] Built terrain grid: {len(nodes)} nodes")

    # Construire les aretes (connecter les voisins proches)
    adjacency: Dict[int, Dict[int, float]] = {n: {} for n in nodes}
    max_edge_dist = grid_spacing_m * 1.6  # ~56m pour espacement 35m

    # Indexer par cellule pour les voisins proches
    node_list = list(nodes.items())
    for i in range(len(node_list)):
        nid_a, (lat_a, lng_a) = node_list[i]
        type_a = node_types[nid_a]
        if type_a == "water":
            continue  # Pas d'aretes depuis l'eau

        for j in range(i + 1, len(node_list)):
            nid_b, (lat_b, lng_b) = node_list[j]
            type_b = node_types[nid_b]
            if type_b == "water":
                continue

            # Distance rapide (approximation)
            dlat_diff = abs(lat_a - lat_b) * 111320
            dlng_diff = abs(lng_a - lng_b) * 111320 * math.cos(math.radians(lat_a))
            approx_dist = math.sqrt(dlat_diff**2 + dlng_diff**2)

            if approx_dist > max_edge_dist:
                continue

            dist = _haversine(lat_a, lng_a, lat_b, lng_b)
            if dist > max_edge_dist:
                continue

            # Calculer le cout de l'arete
            mid_lat = (lat_a + lat_b) / 2
            mid_lng = (lng_a + lng_b) / 2
            in_scent = _point_in_scent_cone(mid_lat, mid_lng, scent_zone)

            # Choisir le type le plus penalisant des deux extremites
            cost_type = _worst_terrain_type(type_a, type_b)

            if cost_type == "water":
                cost = dist * WATER_COST
            elif cost_type == "wetland":
                cost = dist * WETLAND_COST
            elif cost_type == "stream_bank":
                cost = dist * STREAM_BANK_COST
            elif cost_type == "clearing_edge":
                cost = dist * CLEARING_EDGE_COST
            elif cost_type in ("clearing", "clearing_interior"):
                cost = dist * CLEARING_INTERIOR_COST
            elif cost_type == "dense_forest":
                cost = dist * DENSE_FOREST_COST
            elif cost_type in ("entry", "blind"):
                cost = dist * 1.0  # Pas de penalite pour les extremites
            else:
                cost = dist * OFF_TRAIL_COST

            if in_scent:
                cost *= SCENT_ZONE_PENALTY

            adjacency[nid_a][nid_b] = cost
            adjacency[nid_b][nid_a] = cost

    return nodes, adjacency, node_types, entry_nid, blind_nid


def _worst_terrain_type(t1: str, t2: str) -> str:
    """Retourne le type de terrain le plus penalisant."""
    order = ["water", "wetland", "dense_forest", "open_forest",
             "clearing", "clearing_interior", "clearing_edge",
             "stream_bank", "entry", "blind"]
    i1 = order.index(t1) if t1 in order else 3
    i2 = order.index(t2) if t2 in order else 3
    return t1 if i1 < i2 else t2


def _min_dist_to_segments(lat: float, lng: float, segments: List[List[Tuple[float, float]]]) -> float:
    """Distance minimale d'un point aux segments donnés (en metres, approximatif)."""
    min_d = float("inf")
    for seg in segments:
        for pt_lat, pt_lng in seg:
            dlat = (lat - pt_lat) * 111320
            dlng = (lng - pt_lng) * 111320 * math.cos(math.radians(lat))
            d = math.sqrt(dlat**2 + dlng**2)
            if d < min_d:
                min_d = d
    return min_d


def _astar_terrain_grid(
    nodes: Dict[int, Tuple[float, float]],
    adjacency: Dict[int, Dict[int, float]],
    start_nid: int,
    end_nid: int,
    max_iterations: int = 8000,
) -> Optional[List[int]]:
    """A* sur la grille de terrain."""
    end_lat, end_lng = nodes[end_nid]

    open_set = [(0, start_nid)]
    came_from: Dict[int, int] = {}
    g_score: Dict[int, float] = {start_nid: 0}
    closed: Set[int] = set()
    iterations = 0

    while open_set and iterations < max_iterations:
        iterations += 1
        _, current = heapq.heappop(open_set)

        if current == end_nid:
            # Reconstruire le chemin
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            logger.info(f"[ACCESS-GRID] A* found path: {len(path)} nodes, {iterations} iterations")
            return path

        if current in closed:
            continue
        closed.add(current)

        for neighbor, edge_cost in adjacency.get(current, {}).items():
            if neighbor in closed:
                continue
            tentative_g = g_score[current] + edge_cost
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h = _haversine(*nodes[neighbor], end_lat, end_lng) * 1.2
                heapq.heappush(open_set, (tentative_g + h, neighbor))

    logger.warning(f"[ACCESS-GRID] A* exhausted after {iterations} iterations")
    return None


def _find_reachable_closest_to_target(
    trail_graph,
    entry_lat: float, entry_lng: float,
    target_lat: float, target_lng: float,
    min_dist_to_target_m: float = 40.0,
    max_snap_dist_m: float = 1200.0,
) -> Optional[Tuple[int, float, float, float]]:
    """
    CORRECTION STEEVE-MAX 2026-04-07: Recherche junction DIRECTIONNELLE.

    Trouve le noeud sentier OPTIMAL qui minimise le cout TOTAL:
      total = distance_sentier_depuis_chasseur + distance_directe_vers_affut

    Ceci produit le pattern prescrit:
      CORRIDOR REEL → EMBRANCHEMENT → PENETRATION 90° → AFFUT

    Au lieu de chercher le noeud le plus proche de l'affut (qui peut etre
    loin sur le sentier = detour), on cherche le meilleur compromis entre
    "rester sur le sentier" et "minimiser la penetration hors-sentier".

    Retourne: (node_id, node_lat, node_lng, dist_to_target_m) ou None.
    """
    if trail_graph is None or trail_graph.is_empty:
        return None

    entry_node = trail_graph.nearest_node(entry_lat, entry_lng, max_dist_m=max_snap_dist_m)
    if entry_node is None:
        return None

    # Dijkstra BFS pour calculer la distance sentier REELLE depuis entry_node
    import heapq
    trail_distances = {entry_node: 0.0}
    heap = [(0.0, entry_node)]
    visited = set()

    while heap:
        dist, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        for neighbor, _, edge_dist, _ in trail_graph.adj.get(current, []):
            if neighbor in trail_graph.obstacle_nodes:
                continue
            new_dist = dist + edge_dist
            if new_dist < trail_distances.get(neighbor, float("inf")):
                trail_distances[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))

    if not visited:
        return None

    # Distance directe chasseur → affut (pour calculer le ratio de detour)
    direct_hunter_to_blind = _haversine(entry_lat, entry_lng, target_lat, target_lng)

    # Pour chaque noeud accessible, calculer le cout total:
    # total_cost = trail_distance + penetration_distance
    # Selectionner le noeud qui minimise total_cost
    best_node = None
    best_total_cost = float("inf")
    best_penetration = float("inf")

    for nid in visited:
        nlat, nlng = trail_graph.nodes[nid]
        penetration_dist = _haversine(nlat, nlng, target_lat, target_lng)

        if penetration_dist < min_dist_to_target_m:
            continue  # Trop proche de l'affut = inutile pour penetration

        trail_dist = trail_distances.get(nid, float("inf"))
        total_cost = trail_dist + penetration_dist

        # Filtre: rejeter si le total depasse 3x la distance directe
        # (evite les detours excessifs)
        if direct_hunter_to_blind > 50:
            ratio = total_cost / direct_hunter_to_blind
            if ratio > 3.0:
                continue

        if total_cost < best_total_cost:
            best_total_cost = total_cost
            best_penetration = penetration_dist
            best_node = nid

    if best_node is None:
        # Fallback: si aucun noeud ne passe le filtre ratio,
        # prendre le noeud avec la penetration la plus courte
        for nid in visited:
            nlat, nlng = trail_graph.nodes[nid]
            penetration_dist = _haversine(nlat, nlng, target_lat, target_lng)
            if penetration_dist < min_dist_to_target_m:
                continue
            if penetration_dist < best_penetration:
                best_penetration = penetration_dist
                best_node = nid

    if best_node is None:
        return None

    nlat, nlng = trail_graph.nodes[best_node]
    trail_dist = trail_distances.get(best_node, 0)
    logger.info(
        f"[ACCESS-JUNCTION] Optimal: node={best_node}, "
        f"sentier={round(trail_dist)}m + penetration={round(best_penetration)}m = "
        f"total={round(trail_dist + best_penetration)}m "
        f"(direct={round(direct_hunter_to_blind)}m, "
        f"ratio={round((trail_dist + best_penetration) / max(1, direct_hunter_to_blind), 1)}x)"
    )
    return (best_node, nlat, nlng, best_penetration)


def _attempt_hybrid_trail_terrain(
    entry_lat: float, entry_lng: float,
    blind_lat: float, blind_lng: float,
    trail_graph,
    terrain_data: Optional[Dict],
    scent_zone: Dict,
    feeding_sites: List[Dict],
) -> Optional[Dict]:
    """
    BCE-4X Trail-First Routing — Algorithme hybride 2 phases.

    Phase 1 (SENTIER): Entree → noeud sentier OSM le plus proche de l'affut
                        via A* sur graphe de sentiers reels.
    Phase 2 (TERRAIN): Noeud sentier → affut
                        via A* grille terrain (approche finale hors-sentier).

    Retourne un dict route_result ou None si echec.
    """
    from engines.terrain_nav import navigate_terrain

    if trail_graph is None or trail_graph.is_empty:
        return None

    # --- Trouver le noeud sentier ACCESSIBLE le plus proche de l'affut ---
    # BFS depuis l'entree pour trouver les noeuds sur la meme composante connexe
    result = _find_reachable_closest_to_target(
        trail_graph, entry_lat, entry_lng, blind_lat, blind_lng,
        min_dist_to_target_m=40.0, max_snap_dist_m=1200.0,
    )
    if result is None:
        logger.info("[ACCESS-HYBRID] Aucun noeud sentier ACCESSIBLE a proximite de l'affut — hybride impossible")
        return None

    closest_node_id, junction_lat, junction_lng, junction_to_blind_m = result

    # CORRECTION STEEVE-MAX 2026-04-07b: Rejeter si la penetration est
    # PLUS LONGUE que la distance directe chasseur → affut.
    # Cela signifie que le detour par le sentier est INUTILE (on s'eloigne).
    direct_hunter_blind = _haversine(entry_lat, entry_lng, blind_lat, blind_lng)
    if junction_to_blind_m > direct_hunter_blind * 1.2:
        logger.info(
            f"[ACCESS-HYBRID] REJET: penetration={round(junction_to_blind_m)}m > "
            f"direct={round(direct_hunter_blind)}m — detour par sentier inutile, "
            f"delegation au terrain-grid direct"
        )
        return None

    logger.info(
        f"[ACCESS-HYBRID] Phase 1: entree -> noeud sentier #{closest_node_id} "
        f"({junction_lat:.5f},{junction_lng:.5f}), "
        f"Phase 2: noeud sentier -> affut ({junction_to_blind_m:.0f}m)"
    )

    # --- PHASE 1: Entree → noeud sentier via graphe OSM ---
    phase1_result = navigate_terrain(
        trail_graph, entry_lat, entry_lng, junction_lat, junction_lng
    )
    if phase1_result is None:
        logger.info("[ACCESS-HYBRID] Phase 1 echec — pas de sentier entre entree et noeud jonction")
        return None

    phase1_coords = phase1_result["coords"]
    phase1_dist = phase1_result["distance_m"]
    logger.info(
        f"[ACCESS-HYBRID] Phase 1 OK: {len(phase1_coords)} pts, {phase1_dist}m via sentier OSM"
    )

    # --- PHASE 2: Noeud sentier → affut via grille terrain ---
    phase2_coords = []
    phase2_dist = 0.0
    phase2_terrain_types = set()

    try:
        nodes, adjacency, node_types, start_nid, end_nid = _build_terrain_grid(
            junction_lat, junction_lng, blind_lat, blind_lng,
            terrain_data, scent_zone, feeding_sites,
            grid_spacing_m=25,  # Resolution plus fine pour approche finale
        )
        path_nids = _astar_terrain_grid(nodes, adjacency, start_nid, end_nid)

        if path_nids and len(path_nids) >= 2:
            phase2_coords = [{"lat": nodes[nid][0], "lng": nodes[nid][1]} for nid in path_nids]
            for i in range(len(phase2_coords) - 1):
                phase2_dist += _haversine(
                    phase2_coords[i]["lat"], phase2_coords[i]["lng"],
                    phase2_coords[i + 1]["lat"], phase2_coords[i + 1]["lng"]
                )
            for nid in path_nids:
                t = node_types.get(nid, "open_forest")
                if t not in ("entry", "blind"):
                    phase2_terrain_types.add(t)
            logger.info(
                f"[ACCESS-HYBRID] Phase 2 OK: {len(phase2_coords)} pts, {round(phase2_dist)}m, "
                f"types: {phase2_terrain_types}"
            )
        else:
            logger.info("[ACCESS-HYBRID] Phase 2 A* echec — fallback interpolation lineaire")
    except Exception as e:
        logger.error(f"[ACCESS-HYBRID] Phase 2 grille erreur: {e}")

    # Fallback phase 2: interpolation directe noeud sentier → affut
    if not phase2_coords:
        n_pts = max(4, int(junction_to_blind_m / 30))
        phase2_coords = []
        for i in range(n_pts + 1):
            t = i / n_pts
            phase2_coords.append({
                "lat": junction_lat + t * (blind_lat - junction_lat),
                "lng": junction_lng + t * (blind_lng - junction_lng),
            })
        phase2_dist = junction_to_blind_m
        phase2_terrain_types = {"open_forest"}

    # --- COUTURE: Assembler Phase 1 + Phase 2 ---
    # Eviter doublon au point de jonction
    stitched_coords = list(phase1_coords)
    trail_segment_end_idx = len(stitched_coords) - 1

    if phase2_coords:
        # Sauter le premier point de phase2 s'il est < 5m du dernier point de phase1
        first_p2 = phase2_coords[0]
        last_p1 = stitched_coords[-1]
        gap = _haversine(last_p1["lat"], last_p1["lng"], first_p2["lat"], first_p2["lng"])
        start_idx = 1 if gap < 5 else 0
        stitched_coords.extend(phase2_coords[start_idx:])

    total_dist = phase1_dist + phase2_dist

    logger.info(
        f"[ACCESS-HYBRID] COMPLET: {len(stitched_coords)} pts total, "
        f"{round(total_dist)}m (sentier {phase1_dist}m + terrain {round(phase2_dist)}m), "
        f"jonction idx={trail_segment_end_idx}"
    )

    return {
        "coords": stitched_coords,
        "distance_m": total_dist,
        "type": "hybride_sentier_terrain",
        "routing_algo": "hybrid_trail_terrain",
        "segments_count": len(stitched_coords) - 1,
        "trail_segment_end_idx": trail_segment_end_idx,
        "phase1_distance_m": round(phase1_dist),
        "phase2_distance_m": round(phase2_dist),
        "phase2_terrain_types": list(phase2_terrain_types),
        "junction": {"lat": junction_lat, "lng": junction_lng},
    }


def compute_access_route(
    entry_lat: float,
    entry_lng: float,
    blind_lat: float,
    blind_lng: float,
    trail_graph,
    feeding_sites: List[Dict[str, float]],
    scent_zone: Dict[str, Any],
    water_check_fn=None,
    terrain_data: Optional[Dict] = None,
    corridor_lock: bool = True,
) -> Dict[str, Any]:
    """
    BCE-4X Trail-First Routing — Calculer le chemin d'acces optimal vers un affut.

    BDRE Phase 3: Delegation au pipeline hybride 4 niveaux BDRE.
    BCE-4X CORRIDOR-FIRST 500%: corridor_lock=True force 90% corridor.

    Niveaux BDRE:
    0. Source primaire: sentier OSM reel (TNE)
    1. Waterway bank routing (graphe enrichi DS-8)
    2. Hybride trail-terrain (sentier + approche A*)
    3. Terrain-aware A* pur
    4. Estimation enrichie (dernier recours)
    """
    # BDRE Phase 3: Deleguer au pipeline hybride unifie
    try:
        from engines.bdre import get_fallback_chain
        chain = get_fallback_chain()
        route_result = chain.compute_access_route(
            entry_lat, entry_lng, blind_lat, blind_lng,
            trail_graph, terrain_data=terrain_data,
            scent_zone=scent_zone, feeding_sites=feeding_sites,
            corridor_lock=corridor_lock,
        )
        logger.info(
            f"[ACCESS-BDRE] Route calculee: trail_type={route_result.get('trail_type')}, "
            f"level={route_result.get('bdre_fallback_level', '?')}, "
            f"dist={route_result.get('distance_m', 0)}m"
        )
    except Exception as e:
        logger.warning(f"[ACCESS-BDRE] Pipeline BDRE erreur: {e} — fallback cascade legacy")
        # Fallback legacy si BDRE echoue
        route_result = _legacy_cascade(
            entry_lat, entry_lng, blind_lat, blind_lng,
            trail_graph, terrain_data, scent_zone, feeding_sites,
        )

    if route_result.get("routing_algo") == "direct_line" or route_result.get("trail_type") == "hors_sentier":
        # Le BDRE a retourne une estimation — pas de validation supplementaire
        return route_result

    coords = route_result["coords"]
    distance_m = route_result["distance_m"]
    trail_type = route_result.get("type", "sentier_reel")
    algo = route_result.get("routing_algo", "unknown")

    # Etape 2: Verifier la contamination
    from engines.hunt_orchestrator.vent_odeurs import check_path_contamination
    contam = check_path_contamination(coords, feeding_sites, scent_zone)

    # Etape 3: Verifier les zones d'eau traversees
    water_crossings = []
    if water_check_fn:
        for i, c in enumerate(coords):
            if water_check_fn(c["lat"], c["lng"]):
                water_crossings.append({
                    "index": i,
                    "lat": c["lat"],
                    "lng": c["lng"],
                })

    # Etape 4: Verifier proximite aux sites d'alimentation
    # Exclure les points proches de l'affut (derniers 100m): l'approche DOIT
    # etre pres d'un site alimentation, c'est le but du positionnement
    feeding_proximity_violations = []
    blind_lat_check = coords[-1]["lat"] if coords else blind_lat
    blind_lng_check = coords[-1]["lng"] if coords else blind_lng
    for fs in feeding_sites:
        min_dist = float("inf")
        for c in coords:
            # Ignorer les points dans les derniers 100m de l'affut
            if _haversine(c["lat"], c["lng"], blind_lat_check, blind_lng_check) < 120:
                continue
            d = _haversine(c["lat"], c["lng"], fs["lat"], fs["lng"])
            if d < min_dist:
                min_dist = d
        if min_dist < 50:  # Seuil 50m (hors zone approche)
            feeding_proximity_violations.append({
                "feeding_site": fs,
                "min_distance_m": round(min_dist),
                "message": f"Chemin passe a {round(min_dist)}m d'un site alimentation (hors zone approche)",
            })

    # Bilan de faisabilite
    feasible = (
        contam["compliant"]
        and len(water_crossings) == 0
        and len(feeding_proximity_violations) == 0
    )

    # Score de qualite de l'acces (0-100)
    is_hybrid = algo == "hybrid_trail_terrain"
    is_terrain_aware = algo == "terrain_grid_astar"
    if is_hybrid:
        quality_score = 75  # Hybride: sentier + approche terrain
    elif is_terrain_aware:
        quality_score = 65  # Terrain-aware pur
    else:
        quality_score = 80  # Sentier formel complet
    if not contam["compliant"]:
        quality_score -= 40
    if water_crossings:
        quality_score -= 20 * len(water_crossings)
    if feeding_proximity_violations:
        quality_score -= 15 * len(feeding_proximity_violations)
    if distance_m > 1000:
        quality_score -= min(20, (distance_m - 1000) / 100)
    quality_score = max(0, min(100, quality_score))

    # Metadata specifique hybride
    hybrid_meta = {}
    if algo == "hybrid_trail_terrain":
        hybrid_meta = {
            "trail_segment_end_idx": route_result.get("trail_segment_end_idx", 0),
            "phase1_distance_m": route_result.get("phase1_distance_m", 0),
            "phase2_distance_m": route_result.get("phase2_distance_m", 0),
            "phase2_terrain_types": route_result.get("phase2_terrain_types", []),
            "junction": route_result.get("junction", {}),
        }

    result = {
        "status": "ok" if feasible else "violations",
        "coords": coords,
        "distance_m": round(distance_m),
        "trail_type": trail_type,
        "routing_algo": algo,
        "segments_count": route_result.get("segments_count", 0),
        "feasible": feasible,
        "quality_score": round(quality_score, 1),
        "contamination_check": contam,
        "water_crossings": water_crossings,
        "feeding_proximity": feeding_proximity_violations,
        # BCE-4X CORRIDOR-FIRST 500%: Propagation metadonnees BDRE
        "corridor_lock": route_result.get("corridor_lock", True),
        "corridor_pct": route_result.get("corridor_pct"),
        "forest_pct": route_result.get("forest_pct"),
        "bdre_fallback_level": route_result.get("bdre_fallback_level"),
        "bdre_levels_tried": route_result.get("bdre_levels_tried"),
        "bdre_source": route_result.get("bdre_source"),
        "bdre_terrain_score": route_result.get("bdre_terrain_score"),
        **hybrid_meta,
        "message": (
            f"Acces {'CONFORME' if feasible else 'NON CONFORME'}: "
            f"{round(distance_m)}m via {trail_type} ({algo}). "
            + (f"Sentier {hybrid_meta.get('phase1_distance_m', 0)}m + approche {hybrid_meta.get('phase2_distance_m', 0)}m. " if hybrid_meta else "")
            + ("ZERO violation." if feasible else f"{contam['violations_count']} violation(s) vent/odeur.")
            + (f" CORRIDOR-FIRST 500%: {route_result.get('corridor_pct', '?')}% corridor, {route_result.get('forest_pct', '?')}% foret." if route_result.get("corridor_lock") else "")
        ),
    }

    # BCE-4X V7: Appliquer le pipeline de clarte access_clarity_engine_v7
    try:
        from modules.access_clarity_engine_v7.clarity_engine import apply_clarity
        result = apply_clarity(result)
    except Exception as e:
        logger.warning(f"[ACCESS] clarity_v7 application failed: {e}")
        result["clarity_applied"] = False

    return result


def find_best_entry_point(
    blind_lat: float,
    blind_lng: float,
    trail_graph,
    wind_direction_deg: float,
    max_entries: int = 3,
) -> List[Dict[str, Any]]:
    """
    Identifier les meilleurs points d'entree sur le reseau de sentiers.

    Strategie: chercher les noeuds du graphe qui sont:
    1. Accessibles (sur un sentier reel)
    2. En AMONT du vent (upwind) pour minimiser la contamination
    3. A distance raisonnable de l'affut (200-800m)
    """
    if trail_graph.is_empty:
        return []

    # ULTRA-MAX++ FIREWALL: Import du test geometrique anthropique
    _has_anthropic_firewall = False
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import _point_intersects_anthropic
        _has_anthropic_firewall = True
    except ImportError:
        pass

    # Direction upwind (d'ou on doit arriver pour ne pas contaminer)
    upwind_deg = wind_direction_deg  # Le vent vient de cette direction

    candidates = []
    for nid, (nlat, nlng) in trail_graph.nodes.items():
        if nid in trail_graph.obstacle_nodes:
            continue

        # ULTRA-MAX++: Firewall anthropique sur points d'entree
        if _has_anthropic_firewall and _point_intersects_anthropic(nlat, nlng):
            continue

        dist = _haversine(nlat, nlng, blind_lat, blind_lng)
        if dist < 150 or dist > 1200:
            continue

        # Angle d'approche depuis ce noeud
        approach_angle = math.degrees(math.atan2(
            blind_lng - nlng, blind_lat - nlat
        )) % 360

        # Difference avec la direction upwind
        diff = abs(approach_angle - upwind_deg)
        if diff > 180:
            diff = 360 - diff

        # Plus le diff est proche de 0, plus on arrive face au vent (ideal)
        # Score: 0-180 mapped to 100-0
        wind_alignment = max(0, 100 - (diff / 180) * 100)

        # Penaliser les distances extremes
        dist_score = 100 - abs(dist - 400) / 8
        dist_score = max(0, min(100, dist_score))

        # Check connectivity (noeud doit avoir des voisins)
        neighbors = trail_graph.adj.get(nid, [])
        if len(neighbors) < 1:
            continue

        # Score composite
        score = wind_alignment * 0.6 + dist_score * 0.4

        candidates.append({
            "node_id": nid,
            "lat": nlat,
            "lng": nlng,
            "distance_m": round(dist),
            "approach_angle_deg": round(approach_angle, 1),
            "wind_alignment_score": round(wind_alignment, 1),
            "distance_score": round(dist_score, 1),
            "total_score": round(score, 1),
            "connectivity": len(neighbors),
        })

    # Trier par score
    candidates.sort(key=lambda x: x["total_score"], reverse=True)
    return candidates[:max_entries]



def _legacy_cascade(
    entry_lat, entry_lng, blind_lat, blind_lng,
    trail_graph, terrain_data, scent_zone, feeding_sites,
):
    """
    BDRE safety fallback — Cascade legacy si le BDRE echoue.
    Reproduit l'ancien comportement (pre-BDRE Phase 3).
    """
    from engines.terrain_nav import navigate_terrain

    route_result = navigate_terrain(
        trail_graph, entry_lat, entry_lng, blind_lat, blind_lng
    ) if trail_graph and not trail_graph.is_empty else None

    if route_result is None:
        route_result = _attempt_hybrid_trail_terrain(
            entry_lat, entry_lng, blind_lat, blind_lng,
            trail_graph, terrain_data, scent_zone or {}, feeding_sites or [],
        )

    if route_result is None:
        try:
            nodes, adjacency, node_types, start_nid, end_nid = _build_terrain_grid(
                entry_lat, entry_lng, blind_lat, blind_lng,
                terrain_data, scent_zone or {}, feeding_sites or [],
            )
            path_nids = _astar_terrain_grid(nodes, adjacency, start_nid, end_nid)
            if path_nids and len(path_nids) >= 2:
                coords = [{"lat": nodes[nid][0], "lng": nodes[nid][1]} for nid in path_nids]
                total_dist = sum(
                    _haversine(coords[i]["lat"], coords[i]["lng"],
                               coords[i + 1]["lat"], coords[i + 1]["lng"])
                    for i in range(len(coords) - 1)
                )
                route_result = {
                    "coords": coords, "distance_m": total_dist,
                    "type": "terrain_aware", "routing_algo": "terrain_grid_astar",
                    "segments_count": len(coords) - 1,
                }
        except Exception:
            route_result = None

    if route_result is None:
        direct_dist = _haversine(entry_lat, entry_lng, blind_lat, blind_lng)
        n_pts = max(5, int(direct_dist / 50))
        coords = [
            {"lat": entry_lat + (i / n_pts) * (blind_lat - entry_lat),
             "lng": entry_lng + (i / n_pts) * (blind_lng - entry_lng)}
            for i in range(n_pts + 1)
        ]
        return {
            "status": "direct_hors_sentier", "coords": coords,
            "distance_m": round(direct_dist), "trail_type": "hors_sentier",
            "routing_algo": "direct_line", "feasible": True, "quality_score": 20,
            "contamination_check": {"compliant": True, "violations": []},
            "water_crossings": [], "feeding_proximity_violations": [],
        }

    return route_result
