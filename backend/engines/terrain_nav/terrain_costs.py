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
# BCE-4X CORRIDOR-FIRST X1000: sentiers OSM = voie PREFEREE absolue
HIGHWAY_COST_MULTIPLIER = {
    "secondary": 0.6,       # Route secondaire (ancien: 0.8)
    "tertiary": 0.65,       # Route tertiaire (ancien: 0.85)
    "residential": 0.7,     # Route residentielle (ancien: 0.9)
    "unclassified": 0.8,    # Route non classee (ancien: 1.0)
    "service": 0.8,         # Route de service (ancien: 1.0)
    "track": 0.85,          # Chemin forestier praticable (ancien: 1.1)
    "cycleway": 0.9,        # Piste cyclable (ancien: 1.2)
    "bridleway": 1.0,       # Sentier equestre (ancien: 1.3)
    "path": 1.1,            # Sentier pietonne (ancien: 1.5)
    "footway": 1.2,         # Sentier de randonnee (ancien: 1.6)
}

# Cout pour traversee hors-sentier
# BCE-4X CORRIDOR-FIRST X1000 (STEEVE-MAX):
# Maximiser l'utilisation des corridors, sentiers, chemins.
# Minimiser la marche en foret dense (cout x3 augmente).
OFF_TRAIL_COST = 12.0       # Foret ouverte sans sentier (ancien: 4.0, CORRIDOR-FIRST: x3)
DENSE_FOREST_COST = 25.0    # Foret dense hors sentier (ancien: 8.0, CORRIDOR-FIRST: x3.1)
WETLAND_COST = 50.0          # Zone humide = quasi-infranchissable
WATER_COST = 999.0           # Eau = infranchissable

# Corridors naturels (BCE-4X CORRIDOR-FIRST X1000)
# Couts reduits pour favoriser les corridors naturels.
STREAM_BANK_COST = 0.9      # Bord de ruisseau = corridor OPTIMAL (ancien: 1.2)
CLEARING_EDGE_COST = 1.0    # Bordure de clairiere = corridor PREFERE (ancien: 1.4)
CLEARING_INTERIOR_COST = 1.5  # Interieur clairiere (ancien: 2.0)
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

    BCE-4X CORRIDOR-FIRST X1000 — Priorite des corridors:
    1. Routes OSM (0.6-0.8x) — VOIE PREFEREE ABSOLUE
    2. Sentiers OSM (0.85-1.2x) — CORRIDORS OPTIMAUX
    3. Bords de ruisseau (0.9x) — CORRIDORS NATURELS PRIORITAIRES
    4. Bordures de clairiere (1.0x) — CORRIDORS PREFERES
    5. Clairiere interieure (1.5x) — CORRIDOR SECONDAIRE
    6. Foret ouverte hors sentier (12.0x) — PENALISE
    7. Foret dense (25.0x) — FORTEMENT PENALISE
    8. Zone humide (50x) — QUASI-INFRANCHISSABLE
    9. Eau (999x) — INFRANCHISSABLE
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
