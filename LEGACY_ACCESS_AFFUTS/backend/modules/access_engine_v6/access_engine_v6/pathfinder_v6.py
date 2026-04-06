"""
Pathfinder V6 — A* adapte pour acces aux affuts (2 phases)
PROTOCOLE BIONIC GOLDEN — Pipeline unique acces aux affuts V6
"""
import heapq
import math
import logging

logger = logging.getLogger("access_engine_v6.pathfinder")

# Directions 8-voisins avec couts diagonaux
DIRECTIONS = [
    (0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0),
    (1, 1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (-1, -1, 1.414),
]


def _octile_heuristic(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return max(dx, dy) + 0.414 * min(dx, dy)


def astar_grid(
    grid: dict,
    start: tuple,
    goal: tuple,
    grid_size: int,
) -> list:
    """
    A* sur grille de couts. Retourne la liste de cellules (gx, gy) du chemin.
    """
    sx, sy = start
    gx, gy = goal

    if start not in grid or goal not in grid:
        return []

    open_set = [(0, sx, sy)]
    came_from = {}
    g_score = {start: 0}
    closed = set()

    while open_set:
        _, cx, cy = heapq.heappop(open_set)

        if (cx, cy) == goal:
            path = []
            current = goal
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        if (cx, cy) in closed:
            continue
        closed.add((cx, cy))

        for dx, dy, diag_cost in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            if nx < 0 or ny < 0 or nx >= grid_size or ny >= grid_size:
                continue
            neighbor = (nx, ny)
            if neighbor in closed or neighbor not in grid:
                continue

            cell_cost = grid[neighbor]["cost"]
            tentative = g_score[(cx, cy)] + cell_cost * diag_cost

            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = (cx, cy)
                g_score[neighbor] = tentative
                f = tentative + _octile_heuristic(nx, ny, gx, gy)
                heapq.heappush(open_set, (f, nx, ny))

    return []


def dijkstra_trail_graph(
    nodes: dict,
    edges: list,
    start_id: str,
    goal_id: str,
) -> list:
    """
    Dijkstra sur le graphe de sentiers OSM.
    Retourne la liste d'IDs de noeuds du chemin.
    """
    adj = {}
    for edge in edges:
        f, t = str(edge["from"]), str(edge["to"])
        cost = edge["distance_m"] * edge.get("cost_mult", 1.0)
        adj.setdefault(f, []).append((t, cost, edge))
        adj.setdefault(t, []).append((f, cost, edge))

    if start_id not in adj or goal_id not in adj:
        return []

    dist = {start_id: 0}
    came_from = {}
    open_set = [(0, start_id)]
    closed = set()

    while open_set:
        d, current = heapq.heappop(open_set)

        if current == goal_id:
            path = []
            c = goal_id
            while c in came_from:
                path.append(c)
                c = came_from[c]
            path.append(start_id)
            path.reverse()
            return path

        if current in closed:
            continue
        closed.add(current)

        for neighbor, cost, _edge in adj.get(current, []):
            if neighbor in closed:
                continue
            tentative = d + cost
            if tentative < dist.get(neighbor, float("inf")):
                dist[neighbor] = tentative
                came_from[neighbor] = current
                heapq.heappush(open_set, (tentative, neighbor))

    return []


def find_nearest_trail_node(lat: float, lng: float, nodes: dict) -> str:
    """Trouve le noeud sentier le plus proche d'un point."""
    best_id = None
    best_dist = float("inf")
    for nid, node in nodes.items():
        d = math.hypot(
            (node["lat"] - lat) * 111320,
            (node["lng"] - lng) * 111320 * math.cos(math.radians(lat))
        )
        if d < best_dist:
            best_dist = d
            best_id = nid
    return best_id
