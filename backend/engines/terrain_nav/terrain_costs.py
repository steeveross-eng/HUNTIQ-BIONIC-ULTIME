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


# Cout de base par type de chemin OSM
# BCE-4X CORRIDOR-FIRST X1 000 000%: sentiers OSM = voie PREFEREE ABSOLUE (/10)
HIGHWAY_COST_MULTIPLIER = {
    "secondary": 0.08,      # Route secondaire (initial: 0.8, /10)
    "tertiary": 0.085,      # Route tertiaire (initial: 0.85, /10)
    "residential": 0.09,    # Route residentielle (initial: 0.9, /10)
    "unclassified": 0.1,    # Route non classee (initial: 1.0, /10)
    "service": 0.1,         # Route de service (initial: 1.0, /10)
    "track": 0.11,          # Chemin forestier praticable (initial: 1.1, /10)
    "cycleway": 0.12,       # Piste cyclable (initial: 1.2, /10)
    "bridleway": 0.13,      # Sentier equestre (initial: 1.3, /10)
    "path": 0.15,           # Sentier pietonne (initial: 1.5, /10)
    "footway": 0.16,        # Sentier de randonnee (initial: 1.6, /10)
}

# Cout pour traversee hors-sentier
# BCE-4X CORRIDOR-FIRST X1 000 000% (STEEVE-MAX):
# 95% du trajet = corridors existants. Foret dense = 5% max (dernier segment).
# Cout foret dense x50 vs calibration initiale. Cout corridor /10.
# Interdiction segments hors-sentier > 5%.
OFF_TRAIL_COST = 200.0       # Foret ouverte sans sentier (initial: 4.0, x50)
DENSE_FOREST_COST = 400.0   # Foret dense hors sentier (initial: 8.0, x50)
WETLAND_COST = 800.0         # Zone humide = INFRANCHISSABLE
WATER_COST = 999.0           # Eau = INFRANCHISSABLE

# Corridors naturels (BCE-4X CORRIDOR-FIRST X1 000 000%)
# Couts divises par 10 vs calibration initiale pour attraction ABSOLUE.
STREAM_BANK_COST = 0.12     # Bord de ruisseau = CORRIDOR ABSOLU (initial: 1.2, /10)
CLEARING_EDGE_COST = 0.14   # Bordure de clairiere = CORRIDOR ABSOLU (initial: 1.4, /10)
CLEARING_INTERIOR_COST = 0.2  # Interieur clairiere (initial: 2.0, /10)
SCENT_ZONE_PENALTY = 15.0  # Penalite contamination olfactive

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
    is_stream_bank: bool = False,
    is_clearing_edge: bool = False,
    is_clearing_interior: bool = False,
    in_scent_zone: bool = False,
) -> float:
    """
    Calculer le cout total d'une arete du graphe terrain.

    Cout = distance * type_terrain * pente * penalites

    BCE-4X CORRIDOR-FIRST X1 000 000% — Priorite ABSOLUE EXTREME:
    1. Routes OSM (0.08-0.1x) — CORRIDOR ABSOLU ZERO COUT
    2. Sentiers OSM (0.11-0.16x) — CORRIDOR OPTIMAL ZERO COUT
    3. Bords de ruisseau (0.12x) — CORRIDOR NATUREL ABSOLU
    4. Bordures de clairiere (0.14x) — CORRIDOR NATUREL PREFERE
    5. Clairiere interieure (0.2x) — CORRIDOR SECONDAIRE
    6. Foret ouverte hors sentier (200.0x) — QUASI-INTERDIT
    7. Foret dense (400.0x) — INTERDIT (5% max)
    8. Zone humide (800x) — INFRANCHISSABLE
    9. Eau (999x) — INFRANCHISSABLE

    RATIO: Route(0.08)/Dense(400) = 0.0002 → corridor 5000x prefere
    """
    if in_water:
        return distance_m * WATER_COST
    if in_wetland:
        return distance_m * WETLAND_COST

    # Cout de base: type de terrain (priorite decroissante)
    if highway_type:
        base_cost = get_highway_cost(highway_type)
    elif is_stream_bank:
        base_cost = STREAM_BANK_COST
    elif is_clearing_edge:
        base_cost = CLEARING_EDGE_COST
    elif is_clearing_interior:
        base_cost = CLEARING_INTERIOR_COST
    elif in_forest:
        base_cost = DENSE_FOREST_COST
    else:
        base_cost = OFF_TRAIL_COST

    # Penalite de pente
    slope_mult = compute_slope_penalty(elevation_diff_m, distance_m)

    # Penalite de contamination olfactive
    scent_mult = SCENT_ZONE_PENALTY if in_scent_zone else 1.0

    return distance_m * base_cost * slope_mult * scent_mult


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

    Classification hydrologique BDRE (DS-8):
    - natural=water/wetland -> OBSTACLE (infranchissable)
    - waterway=river/canal -> OBSTACLE (centre d'eau)
    - waterway=stream/ditch/drain -> CORRIDOR navigable (berges), PAS obstacle
    """
    obstacle_nodes: Set[int] = set()
    for way in obstacle_ways:
        tags = way.get("tags", {})
        natural = tags.get("natural", "")
        waterway = tags.get("waterway", "")

        # natural=water/wetland: toujours obstacle
        if natural in ("water", "wetland"):
            for nid in way.get("nodes", []):
                obstacle_nodes.add(nid)
        # river/canal: obstacles (centre eau profonde)
        elif waterway in ("river", "canal", "riverbank"):
            for nid in way.get("nodes", []):
                obstacle_nodes.add(nid)
        # stream/ditch/drain: corridors navigables — PAS des obstacles (BDRE DS-8)
        elif waterway in ("stream", "ditch", "drain"):
            pass
        # Autre waterway inconnu: obstacle par precaution
        elif waterway:
            for nid in way.get("nodes", []):
                obstacle_nodes.add(nid)

    return obstacle_nodes


def build_waterway_corridor_set(
    waterway_node_coords: Dict[int, Tuple[float, float]],
    waterway_ways: list,
) -> Set[int]:
    """
    BDRE DS-8 — Construire un ensemble de node_ids qui sont des corridors
    navigables (berges de ruisseaux, fosses, drains).
    Ces noeuds seront ajoutes au graphe comme sentiers a faible cout.
    """
    corridor_nodes: Set[int] = set()
    for way in waterway_ways:
        tags = way.get("tags", {})
        waterway = tags.get("waterway", "")
        if waterway in ("stream", "ditch", "drain"):
            for nid in way.get("nodes", []):
                corridor_nodes.add(nid)
    return corridor_nodes


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
