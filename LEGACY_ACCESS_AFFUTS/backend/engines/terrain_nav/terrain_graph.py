"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
terrain_graph.py — Structure de graphe terrain

Responsabilites:
- Construction du graphe a partir des donnees OSM
- Noeuds: points GPS avec metadata (elevation, zone)
- Aretes: segments praticables avec cout terrain
- Integration des zones interdites et difficiles
- Recherche du noeud le plus proche

STEEVE-MAX: Le graphe est la source de verite pour le routage.
"""
import math
import logging
from typing import Dict, List, Tuple, Optional, Set

from .terrain_costs import (
    compute_edge_cost, build_obstacle_set, build_forest_set,
    build_waterway_corridor_set,
    STREAM_BANK_COST, CLEARING_EDGE_COST,
    is_excluded_highway, is_allowed_highway,
)

logger = logging.getLogger("bionic.terrain_nav.graph")


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance en metres entre deux points GPS."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class TerrainGraph:
    """
    Graphe de terrain pondère par les couts de traversee.
    
    Noeuds: { node_id: (lat, lng) }
    Aretes: { node_id: [(neighbor_id, cost, distance_m, highway_type)] }
    """

    def __init__(self):
        self.nodes: Dict[int, Tuple[float, float]] = {}
        self.adj: Dict[int, List[Tuple[int, float, float, str]]] = {}
        self.obstacle_nodes: Set[int] = set()
        self.forest_nodes: Set[int] = set()
        self.is_empty = True
        self.stats = {
            "total_nodes": 0,
            "total_edges": 0,
            "total_ways": 0,
            "obstacle_nodes": 0,
            "forest_nodes": 0,
        }

    def add_way(
        self,
        node_ids: List[int],
        node_coords: Dict[int, Tuple[float, float]],
        highway_type: str = "path",
    ):
        """
        Ajouter un chemin OSM au graphe.
        Chaque segment est pondère par le cout terrain.
        """
        for nid in node_ids:
            if nid in node_coords and nid not in self.nodes:
                self.nodes[nid] = node_coords[nid]
                self.adj[nid] = []

        for i in range(len(node_ids) - 1):
            n1 = node_ids[i]
            n2 = node_ids[i + 1]
            if n1 not in self.nodes or n2 not in self.nodes:
                continue

            # Skip si un des noeuds est en zone infranchissable
            if n1 in self.obstacle_nodes or n2 in self.obstacle_nodes:
                continue

            dist = _haversine(
                self.nodes[n1][0], self.nodes[n1][1],
                self.nodes[n2][0], self.nodes[n2][1]
            )

            # Cout terrain: type de chemin + foret
            in_forest = n1 in self.forest_nodes or n2 in self.forest_nodes
            cost = compute_edge_cost(
                distance_m=dist,
                highway_type=highway_type,
                in_forest=in_forest and highway_type is None,
            )

            self.adj[n1].append((n2, cost, dist, highway_type))
            self.adj[n2].append((n1, cost, dist, highway_type))

        self.is_empty = len(self.nodes) == 0

    def nearest_node(
        self,
        lat: float,
        lng: float,
        max_dist_m: float = 1200.0,
    ) -> Optional[int]:
        """Trouver le noeud du graphe le plus proche d'un point GPS."""
        best_id = None
        best_dist = max_dist_m
        for nid, (nlat, nlng) in self.nodes.items():
            if nid in self.obstacle_nodes:
                continue
            d = _haversine(lat, lng, nlat, nlng)
            if d < best_dist:
                best_dist = d
                best_id = nid
        return best_id

    def finalize_stats(self):
        """Calculer les statistiques finales du graphe."""
        total_edges = sum(len(adj) for adj in self.adj.values()) // 2
        self.stats = {
            "total_nodes": len(self.nodes),
            "total_edges": total_edges,
            "obstacle_nodes": len(self.obstacle_nodes),
            "forest_nodes": len(self.forest_nodes),
        }
        self.is_empty = len(self.nodes) == 0
        logger.info(
            f"[TNE-GRAPH] Finalized: {self.stats['total_nodes']} nodes, "
            f"{self.stats['total_edges']} edges, "
            f"{self.stats['obstacle_nodes']} obstacle nodes, "
            f"{self.stats['forest_nodes']} forest nodes, "
            f"empty={self.is_empty}"
        )


def build_terrain_graph(terrain_data: Dict) -> TerrainGraph:
    """
    Construire un TerrainGraph a partir des donnees terrain brutes.
    
    BDRE Phase 2 — Pipeline enrichi:
    1. Marquer les zones infranchissables (eau, zones humides) — DS-8 BDRE
    2. Marquer les zones forestieres
    3. Identifier les corridors waterway navigables (BDRE Level 1)
    4. Ajouter les chemins OSM avec couts terrain
    5. Ajouter les corridors waterway comme sentiers a faible cout
    6. Ajouter les clairieres comme corridors alternatifs (BDRE Level 2)
    """
    graph = TerrainGraph()

    # Phase 1: Identifier les zones infranchissables (DS-8 BDRE classifie)
    obs_data = terrain_data.get("obstacles", {})
    obs_nc = obs_data.get("node_coords", {})
    obs_ways = obs_data.get("ways", [])
    graph.obstacle_nodes = build_obstacle_set(obs_nc, obs_ways)

    # Phase 2: Identifier les zones forestieres
    forest_data = terrain_data.get("forest", {})
    forest_nc = forest_data.get("node_coords", {})
    forest_ways = forest_data.get("ways", [])
    graph.forest_nodes = build_forest_set(forest_nc, forest_ways)

    # Phase 3: Identifier les corridors waterway navigables (BDRE DS-8)
    waterway_data = terrain_data.get("waterways", {})
    ww_nc = waterway_data.get("node_coords", {})
    ww_ways = waterway_data.get("ways", [])

    # Phase 4: Construire le graphe avec les chemins praticables
    trails_data = terrain_data.get("trails", {})
    trail_nc = trails_data.get("node_coords", {})
    trail_ways = trails_data.get("ways", [])

    for way in trail_ways:
        nids = way.get("nodes", [])
        tags = way.get("tags", {})
        highway_type = tags.get("highway", "path")

        # BCE-4X EXCLUSION TERRITORIALE: Ignorer les ways de type urbain/routier
        if is_excluded_highway(highway_type):
            continue

        if len(nids) >= 2:
            graph.add_way(nids, trail_nc, highway_type=highway_type)

    # Phase 5: Ajouter les corridors waterway comme sentiers (BDRE Level 1)
    ww_corridors_added = 0
    for way in ww_ways:
        tags = way.get("tags", {})
        waterway_type = tags.get("waterway", "")
        if waterway_type not in ("stream", "ditch", "drain"):
            continue

        nids = way.get("nodes", [])
        if len(nids) < 2:
            continue

        for nid in nids:
            if nid in ww_nc and nid not in graph.nodes:
                graph.nodes[nid] = ww_nc[nid]
                graph.adj[nid] = []

        for i in range(len(nids) - 1):
            n1 = nids[i]
            n2 = nids[i + 1]
            if n1 not in graph.nodes or n2 not in graph.nodes:
                continue
            if n1 in graph.obstacle_nodes or n2 in graph.obstacle_nodes:
                continue

            dist = _haversine(
                graph.nodes[n1][0], graph.nodes[n1][1],
                graph.nodes[n2][0], graph.nodes[n2][1]
            )
            cost = dist * STREAM_BANK_COST
            hw_type = f"waterway_{waterway_type}"
            graph.adj[n1].append((n2, cost, dist, hw_type))
            graph.adj[n2].append((n1, cost, dist, hw_type))
            ww_corridors_added += 1

    # Phase 6: Ajouter les clairieres comme corridors (BDRE Level 2)
    clearing_data = terrain_data.get("clearings", {})
    cl_nc = clearing_data.get("node_coords", {})
    cl_ways = clearing_data.get("ways", [])
    cl_edges_added = 0

    for way in cl_ways:
        nids = way.get("nodes", [])
        if len(nids) < 2:
            continue

        for nid in nids:
            if nid in cl_nc and nid not in graph.nodes:
                graph.nodes[nid] = cl_nc[nid]
                graph.adj[nid] = []

        for i in range(len(nids) - 1):
            n1 = nids[i]
            n2 = nids[i + 1]
            if n1 not in graph.nodes or n2 not in graph.nodes:
                continue
            if n1 in graph.obstacle_nodes or n2 in graph.obstacle_nodes:
                continue

            dist = _haversine(
                graph.nodes[n1][0], graph.nodes[n1][1],
                graph.nodes[n2][0], graph.nodes[n2][1]
            )
            cost = dist * CLEARING_EDGE_COST
            graph.adj[n1].append((n2, cost, dist, "clearing_edge"))
            graph.adj[n2].append((n1, cost, dist, "clearing_edge"))
            cl_edges_added += 1

    if ww_corridors_added > 0 or cl_edges_added > 0:
        logger.info(
            f"[TNE-GRAPH] BDRE enrichment: +{ww_corridors_added} waterway edges, "
            f"+{cl_edges_added} clearing edges"
        )

    # ========================================================================
    # Phase 7: CONNECTEUR DE FRAGMENTS — GUIDANCE TERRAIN STEEVE-MAX
    # ========================================================================
    # BCE-4X CORRECTION 2026-04-06: Les sentiers OSM en zone forestiere profonde
    # sont souvent cartographies en fragments deconnectes (ways sans noeuds communs).
    # Ce connecteur identifie les extremites de sentiers proches (< 50m) et
    # cree des aretes virtuelles pour unifier le graphe.
    # Cout = distance * OFF_TRAIL_COST_CONNECTOR (penalise mais pas interdit)
    # Max 20m par segment de connexion (GUIDANCE TERRAIN STEEVE-MAX).
    from .terrain_costs import OFF_TRAIL_COST

    CONNECTOR_MAX_DIST_M = 50  # Distance max pour connexion inter-fragments
    CONNECTOR_COST_MULT = 0.5  # Cout leger (passage inter-sentier < 50m)

    # Trouver les noeuds terminaux (degre = 1 ou isolement de composante)
    terminal_nodes = []
    for nid in graph.nodes:
        if nid in graph.obstacle_nodes:
            continue
        neighbors = graph.adj.get(nid, [])
        degree = len(neighbors)
        if degree <= 1:  # Terminal ou isole
            lat, lng = graph.nodes[nid]
            terminal_nodes.append((nid, lat, lng, degree))

    # Connecter les terminaux proches
    connector_edges = 0
    connected_pairs = set()
    for i, (nid1, lat1, lng1, deg1) in enumerate(terminal_nodes):
        for j in range(i + 1, len(terminal_nodes)):
            nid2, lat2, lng2, deg2 = terminal_nodes[j]
            if nid1 == nid2:
                continue
            pair_key = (min(nid1, nid2), max(nid1, nid2))
            if pair_key in connected_pairs:
                continue

            # Verifier si deja voisins directs
            existing = any(nb == nid2 for nb, _, _, _ in graph.adj.get(nid1, []))
            if existing:
                continue

            dist = _haversine(lat1, lng1, lat2, lng2)
            if dist <= CONNECTOR_MAX_DIST_M:
                cost = dist * CONNECTOR_COST_MULT
                graph.adj[nid1].append((nid2, cost, dist, "connector_guidance"))
                graph.adj[nid2].append((nid1, cost, dist, "connector_guidance"))
                connected_pairs.add(pair_key)
                connector_edges += 1

    if connector_edges > 0:
        logger.info(
            f"[TNE-GRAPH] GUIDANCE TERRAIN: +{connector_edges} connector edges "
            f"({len(terminal_nodes)} terminal nodes scanned, max {CONNECTOR_MAX_DIST_M}m)"
        )

    graph.finalize_stats()
    return graph
