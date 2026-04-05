"""
ENGINE_OSM_LITE — Module leger d'enrichissement terrain OSM
BIONIC OS V8.5 | BCE-4X GOLDEN V6+
Directive STEEVE-MAX: A + F + G

Fonction:
  Fournit des donnees de sentiers/routes/eau reels au pathfinder A* corridor.
  Consomme en LECTURE SEULE:
    - Access Engine V6 trail graph cache (graphe sentiers OSM)
    - OSM cache exclusion zones (data/osm_cache/)

Mapping OSM → HUMAN_TRAJET_COSTS:
  path/footway/bridleway → valley (cout 1.0)
  track (grade1-3)       → wooded_strip (cout 1.0)
  track (grade4-5)       → coulee (cout 1.3)
  cycleway               → hedgerow (cout 1.0)
  service/unclassified   → road_crossing (cout 1.5)
  tertiary               → plateau (cout 1.6)
  secondary              → gentle_ridge (cout 1.8)
  residential            → open_field (cout 1.5)
  water (polygon)        → water_body (cout 999.0)
  stream (line)          → riparian (cout 1.2)

ANTI-DOUBLON:
  Ne recree PAS de pathfinder, PAS de scoring, PAS de rasterisation numpy.
  Produit un dict {key: {type, slope, human_pressure}} compatible _build_terrain_grid.
"""

import gzip
import json
import logging
import math
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("bionic_engine.engine_osm_lite")

# =====================================================================
# MAPPING OSM HIGHWAY → TERRAIN TYPE (compatible HUMAN_TRAJET_COSTS)
# =====================================================================
OSM_HIGHWAY_TO_TERRAIN = {
    "path": "valley",
    "footway": "valley",
    "bridleway": "valley",
    "cycleway": "hedgerow",
    "track": "wooded_strip",
    "service": "road_crossing",
    "unclassified": "road_crossing",
    "tertiary": "plateau",
    "secondary": "gentle_ridge",
    "residential": "open_field",
    "primary": "urban_edge",
    "trunk": "urban",
    "motorway": "highway",
}

# Tracktype override (plus precis que le highway type)
TRACKTYPE_TO_TERRAIN = {
    "grade1": "wooded_strip",
    "grade2": "wooded_strip",
    "grade3": "coulee",
    "grade4": "coulee",
    "grade5": "drainage",
}

# Buffer autour des sentiers (en unites de grille ~167m)
TRAIL_BUFFER_CELLS = 1  # 1 cellule de chaque cote = ~500m de detectabilite

METERS_PER_DEG_LAT = 111320.0


def _haversine_simple(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance Haversine simplifiee en metres."""
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def load_trail_segments_from_access_cache(
    bounds: Dict[str, float],
) -> List[Dict]:
    """
    G — Fusion partielle Access Engine V6.
    Charge les segments de sentiers depuis le cache Access Engine V6
    qui tombent dans les bounds donnes.

    Returns:
        Liste de segments: [{from_lat, from_lng, to_lat, to_lng, terrain_type, cost_mult}]
    """
    cache_dir = Path(__file__).parent.parent.parent / "access_engine_v6" / "cache"
    if not cache_dir.exists():
        logger.debug("[OSM_LITE] Access Engine cache non trouve")
        return []

    segments = []
    north = bounds.get("north", 90)
    south = bounds.get("south", -90)
    east = bounds.get("east", 180)
    west = bounds.get("west", -180)
    margin = 0.01  # ~1km de marge

    for fpath in cache_dir.glob("*.json.gz"):
        try:
            with gzip.open(fpath, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        nodes = data.get("nodes", {})
        edges = data.get("edges", [])
        if not nodes or not edges:
            continue

        for edge in edges:
            from_id = str(edge.get("from", ""))
            to_id = str(edge.get("to", ""))
            n1 = nodes.get(from_id)
            n2 = nodes.get(to_id)
            if not n1 or not n2:
                continue

            lat1, lng1 = n1["lat"], n1["lng"]
            lat2, lng2 = n2["lat"], n2["lng"]

            # Verifier si le segment est dans les bounds (avec marge)
            mid_lat = (lat1 + lat2) / 2
            mid_lng = (lng1 + lng2) / 2
            if not (south - margin <= mid_lat <= north + margin and
                    west - margin <= mid_lng <= east + margin):
                continue

            # Determiner le type de terrain
            hw_type = edge.get("highway_type", "path")
            tracktype = edge.get("tracktype", "")
            if tracktype and tracktype in TRACKTYPE_TO_TERRAIN:
                terrain_type = TRACKTYPE_TO_TERRAIN[tracktype]
            else:
                terrain_type = OSM_HIGHWAY_TO_TERRAIN.get(hw_type, "road_crossing")

            segments.append({
                "from_lat": lat1, "from_lng": lng1,
                "to_lat": lat2, "to_lng": lng2,
                "terrain_type": terrain_type,
                "cost_mult": edge.get("cost_mult", 1.0),
                "hw_type": hw_type,
            })

    logger.info(f"[OSM_LITE] Access Engine: {len(segments)} segments charges dans bounds")
    return segments


def load_exclusions_from_osm_cache(
    bounds: Dict[str, float],
) -> List[Dict]:
    """
    A — Enrichissement avec OSM cache (data/osm_cache/).
    Charge les exclusion zones (eau, routes) depuis le cache OSM principal.

    Returns:
        Liste d'exclusions: [{type, sub_type, coordinates, geometry_type}]
    """
    cache_dir = Path(__file__).parent.parent.parent.parent / "data" / "osm_cache"
    if not cache_dir.exists():
        logger.debug("[OSM_LITE] OSM cache non trouve")
        return []

    exclusions = []
    for fpath in cache_dir.iterdir():
        if not fpath.name.endswith(".json") or fpath.name.startswith("CA-"):
            continue
        if fpath.stat().st_size < 1000:
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
            for zone in data.get("exclusion_zones", []):
                exclusions.append(zone)
        except Exception:
            continue

    logger.info(f"[OSM_LITE] OSM cache: {len(exclusions)} exclusions chargees")
    return exclusions


def enrich_terrain_grid(
    terrain_data: Dict[str, Dict],
    bounds: Dict[str, float],
    grid_step: float = 0.0015,
) -> Dict[str, Dict]:
    """
    F — ENGINE_OSM_LITE principal.
    Enrichit la grille terrain existante avec des donnees OSM reelles.

    Strategie:
    1. Charger les segments sentiers depuis Access Engine V6 (G)
    2. Charger les exclusions depuis OSM cache (A)
    3. Rasteriser les segments comme des cellules basse-cout
    4. Rasteriser les exclusions eau comme cellules haute-cout
    5. NE PAS ecraser les cellules existantes SI le cout actuel est plus bas

    Args:
        terrain_data: Grille existante de _build_terrain_grid()
        bounds: {north, south, east, west}
        grid_step: Resolution de grille (~0.0015 = 167m)

    Returns:
        terrain_data enrichi (meme dict, modifie in-place)
    """
    from modules.bionic_engine_p0.services.corridor_10x import HUMAN_TRAJET_COSTS

    enriched_count = 0
    trail_count = 0
    water_count = 0

    # ─── ETAPE 1: Segments sentiers Access Engine V6 (G) ───
    segments = load_trail_segments_from_access_cache(bounds)
    for seg in segments:
        terrain_type = seg["terrain_type"]
        new_cost = HUMAN_TRAJET_COSTS.get(terrain_type, 2.0)

        # Rasteriser le segment: interpoler entre from et to
        lat1, lng1 = seg["from_lat"], seg["from_lng"]
        lat2, lng2 = seg["to_lat"], seg["to_lng"]
        dist = _haversine_simple(lat1, lng1, lat2, lng2)
        n_steps = max(2, int(dist / (grid_step * METERS_PER_DEG_LAT)) + 1)

        for i in range(n_steps + 1):
            t = i / n_steps
            lat = lat1 + t * (lat2 - lat1)
            lng = lng1 + t * (lng2 - lng1)

            # Cellule principale + buffer
            for blat in range(-TRAIL_BUFFER_CELLS, TRAIL_BUFFER_CELLS + 1):
                for blng in range(-TRAIL_BUFFER_CELLS, TRAIL_BUFFER_CELLS + 1):
                    cell_lat = lat + blat * grid_step
                    cell_lng = lng + blng * grid_step
                    key = f"{cell_lat:.4f},{cell_lng:.4f}"

                    existing = terrain_data.get(key, {})
                    existing_cost = HUMAN_TRAJET_COSTS.get(
                        existing.get("type", "mixed_forest"), 3.5
                    )

                    # Ecrire seulement si le cout est meilleur
                    if new_cost < existing_cost:
                        terrain_data[key] = {
                            "type": terrain_type,
                            "slope": 3,
                            "human_pressure": 0.05,
                            "source": "osm_trail",
                        }
                        enriched_count += 1

        trail_count += 1

    # ─── ETAPE 2: Exclusions OSM cache (A) ───
    exclusions = load_exclusions_from_osm_cache(bounds)
    for ex in exclusions:
        ex_type = ex.get("type", "")
        sub_type = ex.get("sub_type", "")
        coords = ex.get("coordinates", [])
        geom_type = ex.get("geometry_type", "polygon")

        if not coords:
            continue

        if ex_type == "water":
            if sub_type in ("stream", "ditch", "drain"):
                terrain_type = "riparian"
            elif sub_type == "wetland":
                continue
            elif sub_type == "micro_water":
                continue
            else:
                terrain_type = "water_body"

            # Rasteriser les coordonnees
            for coord in coords:
                if len(coord) < 2:
                    continue
                lng_c, lat_c = coord[0], coord[1]
                for blat in range(-1, 2):
                    for blng in range(-1, 2):
                        key = f"{lat_c + blat * grid_step:.4f},{lng_c + blng * grid_step:.4f}"
                        existing = terrain_data.get(key, {})
                        existing_type = existing.get("type", "mixed_forest")
                        if terrain_type == "water_body" or (
                            HUMAN_TRAJET_COSTS.get(terrain_type, 999) <
                            HUMAN_TRAJET_COSTS.get(existing_type, 3.5)
                        ):
                            terrain_data[key] = {
                                "type": terrain_type,
                                "slope": 0,
                                "human_pressure": 0,
                                "source": "osm_exclusion",
                            }
                            water_count += 1

        elif ex_type == "roads":
            # Routes existantes dans le cache OSM
            road_terrain = OSM_HIGHWAY_TO_TERRAIN.get(sub_type, "road_crossing")
            new_cost = HUMAN_TRAJET_COSTS.get(road_terrain, 1.5)
            for coord in coords:
                if len(coord) < 2:
                    continue
                lng_c, lat_c = coord[0], coord[1]
                key = f"{lat_c:.4f},{lng_c:.4f}"
                existing = terrain_data.get(key, {})
                existing_cost = HUMAN_TRAJET_COSTS.get(
                    existing.get("type", "mixed_forest"), 3.5
                )
                if new_cost < existing_cost:
                    terrain_data[key] = {
                        "type": road_terrain,
                        "slope": 2,
                        "human_pressure": 0.2,
                        "source": "osm_road",
                    }
                    enriched_count += 1

    logger.info(
        f"[OSM_LITE] Enrichissement: {trail_count} sentiers, "
        f"{water_count} eau, {enriched_count} cellules modifiees"
    )

    return terrain_data
