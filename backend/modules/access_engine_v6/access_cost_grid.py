"""
Access Cost Grid — Grille de couts combinee circulation + terrain
PROTOCOLE BIONIC GOLDEN — Pipeline unique acces aux affuts V6

MULTIPLICATEURS GOLDEN (Directive STEEVE-MAX 2026-03-29):
  sentier reel : x0.1
  hybride      : x0.5
  hors-sentier : x3.0
  non conforme : x10.0
"""
import math
import logging

logger = logging.getLogger("access_engine_v6.cost_grid")

# ═══════════════════════════════════════════
# MULTIPLICATEURS GOLDEN — Directive STEEVE-MAX
# ═══════════════════════════════════════════
GOLDEN_MULTIPLIERS = {
    "trail": 0.1,           # Sentier reel OSM, chemin forestier, chemin de coupe
    "hybrid": 0.5,          # Cellule proche d'un sentier (rayon d'influence)
    "off_trail": 3.0,       # Hors-sentier — vegetation moderee
    "non_conformant": 10.0,  # Non conforme — vegetation dense, pente excessive
}

# Couts de base par type de surface
BASE_COSTS = {
    "trail": 1.0,
    "forest_road": 1.2,
    "secondary_road": 1.5,
    "off_trail": 5.0,
}

# Rayon d'influence sentier (en cellules) — les cellules proches d'un sentier
# beneficient du multiplicateur hybride au lieu de hors-sentier
TRAIL_INFLUENCE_RADIUS = 3  # 3 cellules = 30m a resolution 10m

# Multiplicateurs de pente
SLOPE_MULTIPLIERS = [
    (5, 1.0),
    (10, 1.3),
    (15, 1.8),
    (25, 3.0),
]
SLOPE_MAX_DEG = 25  # Au-dela = infranchissable

# Multiplicateurs vegetation
VEGETATION_THRESHOLDS = {
    "open": (0, 0.3, 0.8),
    "mature_open": (0.3, 0.6, 1.0),
    "dense_mature": (0.6, 0.8, 1.5),
    "very_dense": (0.8, 1.0, 2.5),
}
UNDERSTORY_PENALTY = 1.5   # strate_1_3m > 0.7
REGEN_PENALTY = 2.0        # regeneration > 0.8


def compute_cell_cost(
    is_trail: bool,
    highway_type: str,
    slope_deg: float,
    canopy_density: float,
    understory_density: float,
    regeneration: float,
    is_water: bool,
    is_wetland: bool,
    dist_building_m: float,
    dist_road_m: float,
    near_trail: bool = False,
) -> float:
    """
    Calcule le cout de traversee d'une cellule de grille.
    Formule GOLDEN: BASE * MULT_PENTE * MULT_VEGETATION * MULT_OBSTACLE * GOLDEN_MULT
    """
    if is_water:
        return float("inf")

    # BASE
    if is_trail:
        if highway_type in ("path", "track", "footway", "bridleway"):
            base = BASE_COSTS["trail"]
        elif highway_type in ("unclassified", "service", "track_grade1", "track_grade2"):
            base = BASE_COSTS["forest_road"]
        else:
            base = BASE_COSTS["secondary_road"]
    else:
        base = BASE_COSTS["off_trail"]

    # MULT_PENTE
    if slope_deg > SLOPE_MAX_DEG:
        return float("inf")
    mult_slope = 1.0
    for threshold, mult in SLOPE_MULTIPLIERS:
        if slope_deg <= threshold:
            mult_slope = mult
            break
    else:
        mult_slope = 3.0

    # MULT_VEGETATION
    mult_veg = 1.0
    for _label, (lo, hi, mult) in VEGETATION_THRESHOLDS.items():
        if lo <= canopy_density < hi:
            mult_veg = mult
            break
    if understory_density > 0.7:
        mult_veg *= UNDERSTORY_PENALTY
    if regeneration > 0.8:
        mult_veg *= REGEN_PENALTY

    # MULT_OBSTACLE
    mult_obs = 1.0
    if is_wetland:
        mult_obs = 5.0
    if dist_building_m < 100:
        mult_obs = max(mult_obs, 3.0)
    if dist_road_m < 50:
        mult_obs = max(mult_obs, 2.0)

    # MULTIPLICATEUR GOLDEN — Directive STEEVE-MAX
    if is_trail:
        golden_mult = GOLDEN_MULTIPLIERS["trail"]
    elif near_trail:
        golden_mult = GOLDEN_MULTIPLIERS["hybrid"]
    elif canopy_density > 0.8 or slope_deg > 20 or is_wetland:
        golden_mult = GOLDEN_MULTIPLIERS["non_conformant"]
    else:
        golden_mult = GOLDEN_MULTIPLIERS["off_trail"]

    return base * mult_slope * mult_veg * mult_obs * golden_mult


def build_cost_grid(
    center_lat: float,
    center_lng: float,
    radius_m: int,
    trail_nodes: dict,
    trail_edges: list,
    resolution_m: int = 15,
) -> dict:
    """
    Construit une grille de couts pour la zone d'analyse.
    Chaque cellule contient son cout de traversee.
    GOLDEN: Les sentiers sont expandus avec interpolation + rayon d'influence.
    """
    grid_size = (radius_m * 2) // resolution_m
    half = grid_size // 2

    # Indexer les positions des sentiers — avec INTERPOLATION entre noeuds
    trail_positions = set()
    trail_type_map = {}

    for edge in trail_edges:
        from_id = str(edge["from"])
        to_id = str(edge["to"])
        from_node = trail_nodes.get(from_id)
        to_node = trail_nodes.get(to_id)

        if from_node and to_node:
            hw_type = edge.get("highway_type", "path")
            # Interpoler entre les deux noeuds pour remplir les cellules intermediaires
            gx1 = int((from_node["lng"] - center_lng) * 111320 * math.cos(math.radians(center_lat)) / resolution_m) + half
            gy1 = int((from_node["lat"] - center_lat) * 111320 / resolution_m) + half
            gx2 = int((to_node["lng"] - center_lng) * 111320 * math.cos(math.radians(center_lat)) / resolution_m) + half
            gy2 = int((to_node["lat"] - center_lat) * 111320 / resolution_m) + half

            # Bresenham pour tracer la ligne entre les deux noeuds
            cells = _bresenham_line(gx1, gy1, gx2, gy2)
            for cx, cy in cells:
                if 0 <= cx < grid_size and 0 <= cy < grid_size:
                    trail_positions.add((cx, cy))
                    trail_type_map[(cx, cy)] = hw_type

    # Calculer les cellules dans le rayon d'influence des sentiers
    near_trail_positions = set()
    for (tx, ty) in trail_positions:
        for dx in range(-TRAIL_INFLUENCE_RADIUS, TRAIL_INFLUENCE_RADIUS + 1):
            for dy in range(-TRAIL_INFLUENCE_RADIUS, TRAIL_INFLUENCE_RADIUS + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    if (nx, ny) not in trail_positions:
                        near_trail_positions.add((nx, ny))

    # Construire la grille
    grid = {}
    for gy in range(grid_size):
        for gx in range(grid_size):
            is_trail = (gx, gy) in trail_positions
            near_trail = (gx, gy) in near_trail_positions
            hw_type = trail_type_map.get((gx, gy), "")

            # Donnees terrain simulees (a remplacer par DEM reel)
            lat_cell = center_lat + (gy - half) * resolution_m / 111320
            lng_cell = center_lng + (gx - half) * resolution_m / (111320 * math.cos(math.radians(center_lat)))

            seed = hash((round(lat_cell, 5), round(lng_cell, 5)))
            canopy = abs(seed % 100) / 100
            slope = abs((seed >> 8) % 30)
            understory = abs((seed >> 16) % 100) / 100
            regen = abs((seed >> 24) % 100) / 100
            is_water = abs((seed >> 32) % 100) < 3
            is_wetland = abs((seed >> 40) % 100) < 5
            dist_bldg = abs((seed >> 48) % 2000)
            dist_road = abs((seed >> 56) % 500)

            cost = compute_cell_cost(
                is_trail=is_trail,
                highway_type=hw_type,
                slope_deg=slope,
                canopy_density=canopy,
                understory_density=understory,
                regeneration=regen,
                is_water=is_water,
                is_wetland=is_wetland,
                dist_building_m=dist_bldg,
                dist_road_m=dist_road,
                near_trail=near_trail,
            )

            if cost < float("inf"):
                grid[(gx, gy)] = {
                    "cost": cost,
                    "is_trail": is_trail,
                    "near_trail": near_trail,
                    "highway_type": hw_type,
                    "slope_deg": slope,
                    "canopy": canopy,
                    "is_water": is_water,
                }

    return {
        "grid": grid,
        "grid_size": grid_size,
        "resolution_m": resolution_m,
        "center_lat": center_lat,
        "center_lng": center_lng,
        "trail_cell_count": len(trail_positions),
        "near_trail_cell_count": len(near_trail_positions),
    }


def _bresenham_line(x0, y0, x1, y1):
    """Algorithme de Bresenham pour tracer une ligne entre deux cellules."""
    cells = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        cells.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return cells
