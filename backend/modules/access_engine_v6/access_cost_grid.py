"""
Access Cost Grid — Grille de couts combinee circulation + terrain
PROTOCOLE BIONIC GOLDEN — Pipeline unique acces aux affuts V6
"""
import math
import logging

logger = logging.getLogger("access_engine_v6.cost_grid")

# Couts de base par type de surface
BASE_COSTS = {
    "trail": 1.0,
    "forest_road": 1.5,
    "secondary_road": 2.0,
    "off_trail": 5.0,
}

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
) -> float:
    """
    Calcule le cout de traversee d'une cellule de grille.
    Formule GOLDEN: BASE * MULT_PENTE * MULT_VEGETATION * MULT_OBSTACLE
    """
    if is_water:
        return float("inf")

    # BASE
    if is_trail:
        if highway_type in ("path", "track", "footway"):
            base = BASE_COSTS["trail"]
        elif highway_type in ("unclassified", "service"):
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

    # BONUS CIRCULATION: sentiers = 0.2x par rapport a hors-sentier
    trail_bonus = 0.2 if is_trail else 1.0

    return base * mult_slope * mult_veg * mult_obs * trail_bonus


def build_cost_grid(
    center_lat: float,
    center_lng: float,
    radius_m: int,
    trail_nodes: dict,
    trail_edges: list,
    resolution_m: int = 10,
) -> dict:
    """
    Construit une grille de couts pour la zone d'analyse.
    Chaque cellule contient son cout de traversee.
    """
    grid_size = (radius_m * 2) // resolution_m
    half = grid_size // 2

    # Indexer les positions des sentiers pour lookup rapide
    trail_positions = set()
    trail_type_map = {}
    for edge in trail_edges:
        from_id = str(edge["from"])
        to_id = str(edge["to"])
        for nid in (from_id, to_id):
            if nid in trail_nodes:
                node = trail_nodes[nid]
                gx = int((node["lng"] - center_lng) * 111320 * math.cos(math.radians(center_lat)) / resolution_m) + half
                gy = int((node["lat"] - center_lat) * 111320 / resolution_m) + half
                if 0 <= gx < grid_size and 0 <= gy < grid_size:
                    trail_positions.add((gx, gy))
                    trail_type_map[(gx, gy)] = edge.get("highway_type", "path")

    # Construire la grille
    grid = {}
    for gy in range(grid_size):
        for gx in range(grid_size):
            is_trail = (gx, gy) in trail_positions
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
            )

            if cost < float("inf"):
                grid[(gx, gy)] = {
                    "cost": cost,
                    "is_trail": is_trail,
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
    }
