"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
terrain_costs.py — Calcul des couts de traversee terrain

CORRECTION STEEVE-MAX 2026-04-06 — EXCLUSIONS TERRITORIALES BCE-4X:
- Routes, highways, residentiel, zones urbaines = INTERDIT (1 000 000)
- Eau, rivieres, ruisseaux, marecages, zones inondables = INTERDIT (1 000 000)
- Zones ecologiques sensibles = INTERDIT (1 000 000)
- SEULS corridors autorises: sentiers forestiers, chemins forestiers,
  berges de ruisseau, clairieres.

Modele de couts (ACCES AFFUTS UNIQUEMENT):
- Sentiers forestiers (track, path, footway, bridleway) = CORRIDOR PREFERE
- Berges de ruisseau (stream bank) = CORRIDOR NATUREL
- Clairieres = CORRIDOR SECONDAIRE
- Foret ouverte = PENALISE (dernier recours 5% max)
- Foret dense = QUASI-INTERDIT (5% max)
- Routes, residentiel, eau, marecages = INTERDIT ABSOLU (1 000 000)

STEEVE-MAX: Aucun trajet geometrique artificiel.
Le cout determine l'itineraire reel.
"""
import math
import logging
from typing import Dict, Tuple, Optional, Set

logger = logging.getLogger("bionic.terrain_nav.costs")


# ============================================================================
# BCE-4X EXCLUSIONS TERRITORIALES — TYPES INTERDITS (ACCES AFFUTS)
# ============================================================================
# Types OSM INTERDITS pour les acces affuts.
# Un noeud sur ces types sera EXCLUS du graphe de routage.
# CONTEXTE TERRITORIAL: En zone forestiere de chasse (Bas-Saint-Laurent),
# les "unclassified" et "service" sont des chemins forestiers de debardage,
# PAS des routes urbaines. Ils sont AUTORISES comme corridors secondaires.
BCE4X_EXCLUDED_HIGHWAY_TYPES = {
    "motorway", "motorway_link",
    "trunk", "trunk_link",
    "primary", "primary_link",
    "secondary", "secondary_link",
    "tertiary", "tertiary_link",
    "residential",
    "living_street",
    "pedestrian",
    "bus_guideway",
    "road",
}

# Types OSM AUTORISES pour les acces affuts (corridors forestiers)
# Priorite: track > path > footway > bridleway > cycleway > unclassified > service
BCE4X_ALLOWED_HIGHWAY_TYPES = {
    "track",       # Chemin forestier praticable — CORRIDOR PRINCIPAL
    "path",        # Sentier pieton forestier — CORRIDOR OPTIMAL
    "footway",     # Sentier de randonnee — CORRIDOR VALIDE
    "bridleway",   # Sentier equestre — CORRIDOR VALIDE
    "cycleway",    # Piste cyclable forestiere — CORRIDOR SECONDAIRE
    "unclassified", # Chemin de debardage forestier — CORRIDOR SECONDAIRE
    "service",      # Chemin de service forestier — CORRIDOR TERTIAIRE
}

# Cout INTERDIT ABSOLU pour tout type exclu
EXCLUDED_COST = 1_000_000.0


# ============================================================================
# COUTS CORRIDORS FORESTIERS (ACCES AFFUTS UNIQUEMENT)
# ============================================================================
# BCE-4X CORRIDOR-FIRST X1 000 000%: sentiers forestiers = voie PREFEREE ABSOLUE
HIGHWAY_COST_MULTIPLIER = {
    "track": 0.11,          # Chemin forestier praticable — CORRIDOR PRINCIPAL
    "bridleway": 0.13,      # Sentier equestre — CORRIDOR VALIDE
    "path": 0.15,           # Sentier pieton forestier — CORRIDOR OPTIMAL
    "footway": 0.16,        # Sentier de randonnee — CORRIDOR VALIDE
    "cycleway": 0.12,       # Piste cyclable forestiere — CORRIDOR SECONDAIRE
    "unclassified": 0.18,   # Chemin de debardage forestier — CORRIDOR SECONDAIRE
    "service": 0.20,        # Chemin de service forestier — CORRIDOR TERTIAIRE
}

# Cout pour traversee hors-sentier
# BCE-4X CORRIDOR-FIRST X1 000 000% (STEEVE-MAX):
# 95% du trajet = corridors existants. Foret dense = 5% max (dernier segment).
OFF_TRAIL_COST = 200.0       # Foret ouverte sans sentier (x50 vs initial)
DENSE_FOREST_COST = 400.0   # Foret dense hors sentier (x50 vs initial)
WETLAND_COST = EXCLUDED_COST  # Zone humide = INTERDIT ABSOLU
WATER_COST = EXCLUDED_COST    # Eau = INTERDIT ABSOLU

# Corridors naturels (BCE-4X CORRIDOR-FIRST X1 000 000%)
STREAM_BANK_COST = 0.12     # Bord de ruisseau = CORRIDOR NATUREL (berge, PAS l'eau)
CLEARING_EDGE_COST = 0.14   # Bordure de clairiere = CORRIDOR NATUREL
CLEARING_INTERIOR_COST = 0.2  # Interieur clairiere = CORRIDOR SECONDAIRE
SCENT_ZONE_PENALTY = 15.0  # Penalite contamination olfactive

# Seuils de pente
SLOPE_THRESHOLD_EASY = 10.0
SLOPE_THRESHOLD_MODERATE = 20.0
SLOPE_THRESHOLD_HARD = 35.0
SLOPE_THRESHOLD_IMPASSABLE = 50.0

# Penalites de pente
SLOPE_PENALTY_MODERATE = 1.5
SLOPE_PENALTY_HARD = 3.0
SLOPE_PENALTY_IMPASSABLE = 50.0


def is_excluded_highway(highway_type: str) -> bool:
    """
    BCE-4X: Verifier si un type de chemin OSM est EXCLU pour les acces affuts.
    Retourne True si le type est interdit (routes, residentiel, urbain).
    """
    if not highway_type:
        return False
    return highway_type.lower() in BCE4X_EXCLUDED_HIGHWAY_TYPES


def is_allowed_highway(highway_type: str) -> bool:
    """
    BCE-4X: Verifier si un type de chemin OSM est AUTORISE pour les acces affuts.
    Retourne True si le type est un corridor forestier valide.
    """
    if not highway_type:
        return False
    return highway_type.lower() in BCE4X_ALLOWED_HIGHWAY_TYPES


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
    """
    Cout de base pour un type de chemin OSM.
    BCE-4X: Les types exclus retournent EXCLUDED_COST (1 000 000).
    """
    if is_excluded_highway(highway_type):
        return EXCLUDED_COST
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
