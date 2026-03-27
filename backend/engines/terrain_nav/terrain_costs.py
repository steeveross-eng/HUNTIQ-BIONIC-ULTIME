"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
terrain_costs.py — Calcul des couts de traversee terrain

Modele de couts:
- Type de chemin OSM (track, path, footway, etc.)
- Pente (penalite exponentielle au-dessus de 15%)
- Densite forestiere (penalite pour hors-sentier en foret dense)
- Zones humides (cout prohibitif = infranchissable)
- Praticabilite (surface, largeur, obstacles)

STEEVE-MAX: Aucun trajet geometrique artificiel.
Le cout determine l'itineraire reel.
"""
import math
import logging
from typing import Dict, Tuple, Optional, Set

logger = logging.getLogger("bionic.terrain_nav.costs")


# Cout de base par type de chemin OSM (1.0 = optimal, >5.0 = tres difficile)
HIGHWAY_COST_MULTIPLIER = {
    "secondary": 0.8,
    "tertiary": 0.85,
    "residential": 0.9,
    "unclassified": 1.0,
    "service": 1.0,
    "track": 1.1,         # Chemin forestier praticable
    "cycleway": 1.2,
    "bridleway": 1.3,     # Sentier equestre
    "path": 1.5,          # Sentier pietonne
    "footway": 1.6,       # Sentier de randonnee
}

# Cout pour traversee hors-sentier
OFF_TRAIL_COST = 4.0       # Foret ouverte sans sentier
DENSE_FOREST_COST = 8.0    # Foret dense (hors sentier)
WETLAND_COST = 50.0         # Zone humide = quasi-infranchissable
WATER_COST = 999.0          # Eau = infranchissable

# Seuils de pente
SLOPE_THRESHOLD_EASY = 10.0     # % — pas de penalite
SLOPE_THRESHOLD_MODERATE = 20.0  # % — penalite lineaire
SLOPE_THRESHOLD_HARD = 35.0     # % — penalite exponentielle
SLOPE_THRESHOLD_IMPASSABLE = 50.0  # % — infranchissable

# Penalites de pente
SLOPE_PENALTY_MODERATE = 1.5
SLOPE_PENALTY_HARD = 3.0
SLOPE_PENALTY_IMPASSABLE = 50.0


def compute_slope_penalty(elevation_diff_m: float, distance_m: float) -> float:
    """
    Calculer la penalite de pente.
    Retourne un multiplicateur de cout (1.0 = plat, >1.0 = penalise).
    """
    if distance_m < 1.0:
        return 1.0

    slope_pct = abs(elevation_diff_m / distance_m) * 100.0

    if slope_pct <= SLOPE_THRESHOLD_EASY:
        return 1.0
    elif slope_pct <= SLOPE_THRESHOLD_MODERATE:
        t = (slope_pct - SLOPE_THRESHOLD_EASY) / (SLOPE_THRESHOLD_MODERATE - SLOPE_THRESHOLD_EASY)
        return 1.0 + t * (SLOPE_PENALTY_MODERATE - 1.0)
    elif slope_pct <= SLOPE_THRESHOLD_HARD:
        t = (slope_pct - SLOPE_THRESHOLD_MODERATE) / (SLOPE_THRESHOLD_HARD - SLOPE_THRESHOLD_MODERATE)
        return SLOPE_PENALTY_MODERATE + t * (SLOPE_PENALTY_HARD - SLOPE_PENALTY_MODERATE)
    elif slope_pct <= SLOPE_THRESHOLD_IMPASSABLE:
        return SLOPE_PENALTY_HARD * 2.0
    else:
        return SLOPE_PENALTY_IMPASSABLE


def get_highway_cost(highway_type: str) -> float:
    """Cout de base pour un type de chemin OSM."""
    return HIGHWAY_COST_MULTIPLIER.get(highway_type, OFF_TRAIL_COST)


def compute_edge_cost(
    distance_m: float,
    highway_type: Optional[str] = None,
    elevation_diff_m: float = 0.0,
    in_forest: bool = False,
    in_wetland: bool = False,
    in_water: bool = False,
) -> float:
    """
    Calculer le cout total d'une arete du graphe terrain.
    
    Cout = distance * type_chemin * pente * terrain
    
    Un cout eleve = chemin moins desirable.
    Un cout de 999 * distance = infranchissable.
    """
    if in_water:
        return distance_m * WATER_COST
    if in_wetland:
        return distance_m * WETLAND_COST

    # Cout de base: type de chemin
    if highway_type:
        base_cost = get_highway_cost(highway_type)
    elif in_forest:
        base_cost = DENSE_FOREST_COST
    else:
        base_cost = OFF_TRAIL_COST

    # Penalite de pente
    slope_mult = compute_slope_penalty(elevation_diff_m, distance_m)

    return distance_m * base_cost * slope_mult


def classify_zone(
    lat: float, lng: float,
    obstacle_polygons: list,
    forest_polygons: list,
) -> str:
    """
    Classifier un point en zone:
    - "passable" : chemin libre
    - "forest" : en foret (hors sentier penalise)
    - "wetland" : zone humide (quasi-infranchissable)
    - "water" : eau (infranchissable)
    """
    from shapely.geometry import Point
    point = Point(lng, lat)

    for poly_data in obstacle_polygons:
        poly = poly_data.get("geometry")
        if poly and point.within(poly):
            obs_type = poly_data.get("type", "wetland")
            if obs_type == "water":
                return "water"
            return "wetland"

    for poly_data in forest_polygons:
        poly = poly_data.get("geometry")
        if poly and point.within(poly):
            return "forest"

    return "passable"


def build_obstacle_set(
    obstacle_node_coords: Dict[int, Tuple[float, float]],
    obstacle_ways: list,
) -> Set[int]:
    """
    Construire un ensemble de node_ids qui sont dans des zones infranchissables.
    Approche simplifiee: tous les noeuds des ways obstacle sont marques.
    """
    obstacle_nodes: Set[int] = set()
    for way in obstacle_ways:
        tags = way.get("tags", {})
        natural = tags.get("natural", "")
        waterway = tags.get("waterway", "")
        if natural in ("water", "wetland") or waterway:
            for nid in way.get("nodes", []):
                obstacle_nodes.add(nid)
    return obstacle_nodes


def build_forest_set(
    forest_node_coords: Dict[int, Tuple[float, float]],
    forest_ways: list,
) -> Set[int]:
    """
    Construire un ensemble de node_ids qui sont en zone forestiere.
    """
    forest_nodes: Set[int] = set()
    for way in forest_ways:
        for nid in way.get("nodes", []):
            forest_nodes.add(nid)
    return forest_nodes
