"""
BCE-4X Phase 2 — Trail Graph Router
=====================================
Routage REEL sur reseau de chemins forestiers (OSM Overpass).

Strategie:
1. Interroger Overpass UNE SEULE FOIS pour la zone (rayon 1.5km)
2. Construire un graphe local (noeuds + aretes ponderes par distance Haversine)
3. Router via A* local — ZERO requetes live apres le build
4. Cache en memoire par cle de zone (evite les re-fetches)

Tags OSM cibles: track, path, footway, service, bridleway, cycleway
(chemins forestiers, pistes quad, sentiers de debardage)
"""
import math
import heapq
import logging
import hashlib
import requests
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger("bionic.trail_graph")

# Cache global en memoire: { zone_key: TrailGraph }
_graph_cache: Dict[str, "TrailGraph"] = {}

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 15  # secondes

# Rayon de recherche Overpass (metres)
SEARCH_RADIUS_M = 1500

# Tags OSM cibles pour les chemins forestiers
TRAIL_HIGHWAY_TAGS = [
    "track", "path", "footway", "service",
    "bridleway", "cycleway", "unclassified",
    "tertiary", "residential"
]


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance en metres entre deux points GPS."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _zone_key(lat: float, lng: float) -> str:
    """Cle de cache basee sur le centroide arrondi a ~150m."""
    rlat = round(lat, 3)
    rlng = round(lng, 3)
    return f"{rlat}:{rlng}"


class TrailGraph:
    """Graphe de chemins forestiers construit a partir de donnees OSM."""

    def __init__(self):
        # nodes: { node_id: (lat, lng) }
        self.nodes: Dict[int, Tuple[float, float]] = {}
        # adj: { node_id: [(neighbor_id, distance_m)] }
        self.adj: Dict[int, List[Tuple[int, float]]] = {}
        self.is_empty = True

    def add_way(self, node_ids: List[int], node_coords: Dict[int, Tuple[float, float]]):
        """Ajouter un chemin OSM (way) au graphe."""
        for nid in node_ids:
            if nid in node_coords and nid not in self.nodes:
                self.nodes[nid] = node_coords[nid]
                self.adj[nid] = []

        for i in range(len(node_ids) - 1):
            n1 = node_ids[i]
            n2 = node_ids[i + 1]
            if n1 not in self.nodes or n2 not in self.nodes:
                continue
            dist = _haversine(
                self.nodes[n1][0], self.nodes[n1][1],
                self.nodes[n2][0], self.nodes[n2][1]
            )
            self.adj[n1].append((n2, dist))
            self.adj[n2].append((n1, dist))

        if self.nodes:
            self.is_empty = False

    def nearest_node(self, lat: float, lng: float, max_dist_m: float = 500.0) -> Optional[int]:
        """Trouver le noeud du graphe le plus proche d'un point GPS."""
        best_id = None
        best_dist = max_dist_m
        for nid, (nlat, nlng) in self.nodes.items():
            d = _haversine(lat, lng, nlat, nlng)
            if d < best_dist:
                best_dist = d
                best_id = nid
        return best_id

    def a_star(self, start_id: int, end_id: int) -> Optional[List[int]]:
        """A* sur le graphe. Retourne la liste ordonnee de node_ids ou None."""
        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        end_lat, end_lng = self.nodes[end_id]

        # Priority queue: (f_score, node_id)
        open_set = [(0.0, start_id)]
        came_from: Dict[int, int] = {}
        g_score: Dict[int, float] = {start_id: 0.0}

        visited = set()
        max_iterations = 10000

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
                return path

            if current in visited:
                continue
            visited.add(current)

            for neighbor, edge_dist in self.adj.get(current, []):
                if neighbor in visited:
                    continue
                tentative_g = g_score[current] + edge_dist
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    # Heuristique: distance Haversine directe vers la destination
                    n_lat, n_lng = self.nodes[neighbor]
                    h = _haversine(n_lat, n_lng, end_lat, end_lng)
                    f = tentative_g + h
                    heapq.heappush(open_set, (f, neighbor))

        return None

    def path_to_coords(self, node_path: List[int]) -> List[Dict[str, float]]:
        """Convertir une liste de node_ids en coordonnees GPS."""
        coords = []
        for nid in node_path:
            if nid in self.nodes:
                lat, lng = self.nodes[nid]
                coords.append({"lat": round(lat, 6), "lng": round(lng, 6)})
        return coords


def _build_overpass_query(lat: float, lng: float, radius_m: int = SEARCH_RADIUS_M) -> str:
    """Construire la requete Overpass pour les chemins forestiers."""
    tag_filter = "|".join(TRAIL_HIGHWAY_TAGS)
    return f"""
[out:json][timeout:{OVERPASS_TIMEOUT}];
(
  way["highway"~"^({tag_filter})$"](around:{radius_m},{lat},{lng});
);
out body;
>;
out skel qt;
"""


def _fetch_and_build_graph(lat: float, lng: float) -> TrailGraph:
    """Interroger Overpass et construire le graphe. UNE SEULE FOIS par zone."""
    graph = TrailGraph()
    query = _build_overpass_query(lat, lng)

    try:
        logger.info(f"[TRAIL-GRAPH] Overpass query for zone ({lat:.4f}, {lng:.4f}), radius={SEARCH_RADIUS_M}m")
        resp = requests.post(
            OVERPASS_URL,
            data={"data": query},
            timeout=OVERPASS_TIMEOUT + 5
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"[TRAIL-GRAPH] Overpass fetch FAILED: {e}")
        return graph

    elements = data.get("elements", [])

    # Phase 1: Extraire les coordonnees des noeuds
    node_coords: Dict[int, Tuple[float, float]] = {}
    ways = []
    for el in elements:
        if el["type"] == "node":
            node_coords[el["id"]] = (el["lat"], el["lon"])
        elif el["type"] == "way":
            ways.append(el)

    # Phase 2: Construire le graphe
    for way in ways:
        nids = way.get("nodes", [])
        if len(nids) >= 2:
            graph.add_way(nids, node_coords)

    logger.info(f"[TRAIL-GRAPH] Graph built: {len(graph.nodes)} nodes, {len(ways)} ways, empty={graph.is_empty}")
    return graph


def get_trail_graph(lat: float, lng: float) -> TrailGraph:
    """
    Obtenir le graphe de chemins pour une zone.
    Cache en memoire — Overpass interroge UNE SEULE FOIS par zone.
    """
    key = _zone_key(lat, lng)
    if key in _graph_cache:
        logger.info(f"[TRAIL-GRAPH] Cache HIT for zone {key}")
        return _graph_cache[key]

    graph = _fetch_and_build_graph(lat, lng)
    _graph_cache[key] = graph
    return graph


def route_on_trails(
    graph: TrailGraph,
    start_lat: float, start_lng: float,
    end_lat: float, end_lng: float
) -> Optional[Dict]:
    """
    Router entre deux points via le graphe de chemins.
    Retourne: { "coords": [...], "distance_m": float, "type": "sentier_reel" }
    ou None si pas de chemin trouve.
    """
    if graph.is_empty:
        return None

    start_node = graph.nearest_node(start_lat, start_lng, max_dist_m=500)
    end_node = graph.nearest_node(end_lat, end_lng, max_dist_m=500)

    if start_node is None or end_node is None:
        logger.warning(f"[TRAIL-GRAPH] No nearby trail node found (start={start_node}, end={end_node})")
        return None

    if start_node == end_node:
        # Meme noeud — chemin trivial
        slat, slng = graph.nodes[start_node]
        return {
            "coords": [
                {"lat": round(start_lat, 6), "lng": round(start_lng, 6)},
                {"lat": round(slat, 6), "lng": round(slng, 6)},
                {"lat": round(end_lat, 6), "lng": round(end_lng, 6)},
            ],
            "distance_m": _haversine(start_lat, start_lng, end_lat, end_lng),
            "type": "sentier_reel",
        }

    node_path = graph.a_star(start_node, end_node)
    if node_path is None:
        logger.warning("[TRAIL-GRAPH] A* found no path between nodes")
        return None

    # Construire le chemin complet:
    # start_point -> first_trail_node -> ... -> last_trail_node -> end_point
    coords = [{"lat": round(start_lat, 6), "lng": round(start_lng, 6)}]
    trail_coords = graph.path_to_coords(node_path)
    coords.extend(trail_coords)
    coords.append({"lat": round(end_lat, 6), "lng": round(end_lng, 6)})

    # Calculer la distance reelle cumulee
    total_dist = 0.0
    for j in range(1, len(coords)):
        total_dist += _haversine(
            coords[j - 1]["lat"], coords[j - 1]["lng"],
            coords[j]["lat"], coords[j]["lng"]
        )

    return {
        "coords": coords,
        "distance_m": round(total_dist),
        "type": "sentier_reel",
    }
