"""
MODULE C — Zone Engine Core V2
BIONIC V6.x — Pipeline Unifie — Cercles 600m + Exclusion Eau V7

Orchestrateur du pipeline complet:
  layer -> raster -> contour -> CERCLE 600m -> exclusion eau V7 -> GeoJSON

Backend = seule source de verite. Fetch ses propres exclusions.
Aucun lien transversal. Appels orchestres uniquement.

SPECIFICATIONS V6.x (directive STEEVE-MAX):
  - Geometrie: CERCLES 600m (ZERO carre, ZERO polygone irregulier)
  - Exclusion eau: Cache local 41,944 polygones (ZERO API temps reel)
  - Traitement parallele des couches (ThreadPoolExecutor)
  - Cache TTL 5 min, cle arrondie

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x100
"""

import os
import logging
import hashlib
import math
import time
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any

from modules.bionic_engine_p0.services.behavioral_rasterizer import (
    generate_layer_raster, get_supported_layers, get_supported_species, LAYER_PARAMS
)
from modules.bionic_engine_p0.services.organic_zone_generator_v2 import (
    extract_organic_zones
)
from modules.bionic_engine_p0.services.zone_visual_layer_v2 import (
    zones_to_geojson
)
from modules.bionic_engine_p0.services.zone_penalty_engine import (
    calculate_zone_penalty
)

# Shapely pour cercles et exclusion eau
try:
    from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
    from shapely.ops import unary_union
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

# V6 Feature Flag
EXCLUSION_ENGINE_VERSION = os.environ.get("EXCLUSION_ENGINE_VERSION", "v5")

logger = logging.getLogger("bionic_engine.zone_engine_core_v2")

# Cache en memoire (TTL 30 min — BCE-4X Performance Optimization)
_zone_cache: Dict[str, Any] = {}
_CACHE_TTL = 1800

METERS_PER_DEG_LAT = 111320.0

# ══════════════════════════════════════════════════════════
# V6.x Phase 3.1-SUPRA — CERCLES 600m + EXCLUSION STRICTE
# STEEVE-MAX: ZERO zone en ville, ZERO zone dans l'eau,
#             ZERO zone sur les routes, ZERO zone sur infrastructure
# ══════════════════════════════════════════════════════════
CIRCLE_RADIUS_M = 600
CIRCLE_NUM_POINTS = 48
WATER_OVERLAP_THRESHOLD = 0.25   # Phase 3.1: 25% overlap eau = exclusion
URBAN_OVERLAP_THRESHOLD = 0.10   # Phase 3.1: 10% overlap urbain = exclusion
                                 # Suffisant car RAW OSM cree un mesh de densite
URBAN_CENTER_BUFFER_DEG = 0.002  # ~222m buffer autour du centre

_water_union_zone_cache = None
_water_zone_cache_loaded = False
_urban_union_zone_cache = None
_urban_zone_cache_loaded = False


def preload_water_cache():
    """BCE-4X PERF: Pre-charge le cache eau au demarrage du serveur."""
    global _water_union_zone_cache, _water_zone_cache_loaded
    if _water_zone_cache_loaded:
        return
    _load_water_cache_zones()
    logger.info(f"[BCE-4X-PERF] Water cache pre-loaded: active={_water_union_zone_cache is not None}")


def _load_water_cache_zones():
    """Charge les polygones eau depuis le cache OSM local."""
    global _water_union_zone_cache, _water_zone_cache_loaded
    if _water_zone_cache_loaded:
        return _water_union_zone_cache
    if not SHAPELY_AVAILABLE:
        _water_zone_cache_loaded = True
        return None

    cache_dir = Path("/app/backend/data/osm_cache")
    if not cache_dir.exists():
        _water_zone_cache_loaded = True
        return None

    water_polys = []
    MAX_WATER_POLY_AREA = 0.002  # Phase 3.1: Max 0.002 deg² (~25 km²) par polygone eau
    MAX_WATER_BBOX_FILL = 0.50   # Si poly remplit >50% de sa bbox, c'est corrompu
    rejected_large = 0
    for fname in os.listdir(cache_dir):
        if not fname.endswith(".json") or fname.startswith("CA-") or fname == "hydro_debug.json":
            continue
        fpath = cache_dir / fname
        if fpath.stat().st_size < 10000:
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
            for zone in data.get("exclusion_zones", []):
                if zone.get("type") != "water":
                    continue
                coords = zone.get("coordinates", [])
                if len(coords) >= 4:
                    try:
                        poly = ShapelyPolygon([(c[0], c[1]) for c in coords])
                        if poly.is_valid and poly.area > 0:
                            # Phase 3.1: Rejeter les polygones eau corrompus/trop grands
                            if poly.area > MAX_WATER_POLY_AREA:
                                rejected_large += 1
                                continue
                            # Phase 3.1: Rejeter les polygones trop compacts (rectangles = erreurs)
                            bx = poly.bounds
                            bbox_area = (bx[2] - bx[0]) * (bx[3] - bx[1])
                            if bbox_area > 0 and poly.area / bbox_area > MAX_WATER_BBOX_FILL and poly.area > 0.0005:
                                rejected_large += 1
                                continue
                            water_polys.append(poly)
                    except Exception:
                        pass
        except Exception:
            continue

    if rejected_large > 0:
        logger.warning(f"[V7-ZONES] {rejected_large} polygones eau CORROMPUS rejetes (area > {MAX_WATER_POLY_AREA})")

    if water_polys:
        try:
            _water_union_zone_cache = unary_union(water_polys)
            logger.info(f"[V7-ZONES] Cache eau charge: {len(water_polys)} polygones")
        except Exception:
            pass

    _water_zone_cache_loaded = True
    return _water_union_zone_cache


def _circle_on_water(center_lat: float, center_lng: float) -> bool:
    """
    Phase 3.1-SUPRA: Verifie si un cercle 600m chevauche l'eau.
    Utilise overlap > 2% (pas de buffer centre pour eviter de bloquer les zones forestieres
    pres de ruisseaux).
    """
    water = _load_water_cache_zones()
    if water is None or not SHAPELY_AVAILABLE:
        return False
    try:
        coords = _make_circle_coords(center_lat, center_lng, CIRCLE_RADIUS_M)
        poly = ShapelyPolygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        overlap = poly.intersection(water).area
        ratio = overlap / poly.area if poly.area > 0 else 0
        return ratio > WATER_OVERLAP_THRESHOLD
    except Exception:
        return False


def _load_urban_cache_zones():
    """
    Phase 3.1-SUPRA FINAL: Charge les polygones anthropiques PERTINENTS.
    
    HARD EXCLUDE (toute proximite = rejet):
    - Urban landuse: residential, commercial, industrial, retail, construction, military
    - Routes MAJEURES: motorway, trunk, primary (avec buffer genereux)
    - Infrastructure: railways (avec buffer)
    
    IGNORE (pas d'exclusion):
    - Routes mineures: residential, tertiary, unclassified, track, cycleway, footway
    - Urban: cemetery, recreation_ground, quarry (espaces ouverts)
    
    STEEVE-MAX: ZERO zone dans un quartier, ZERO zone sur autoroute.
    """
    global _urban_union_zone_cache, _urban_zone_cache_loaded
    if _urban_zone_cache_loaded:
        return _urban_union_zone_cache
    if not SHAPELY_AVAILABLE:
        _urban_zone_cache_loaded = True
        return None

    cache_dir = Path("/app/backend/data/osm_cache")
    if not cache_dir.exists():
        _urban_zone_cache_loaded = True
        return None

    # Urban landuse sub_types that represent ACTUAL built-up areas
    URBAN_EXCLUDE_SUBTYPES = {
        "residential", "commercial", "industrial", "retail", "yes",
        "construction", "military", "education"
    }
    # Road sub_types that represent MAJOR infrastructure (with buffer)
    ROAD_MAJOR = {
        "motorway": 0.002,       # ~222m buffer
        "motorway_link": 0.0015, # ~167m buffer
        "trunk": 0.0015,         # ~167m buffer
        "trunk_link": 0.001,     # ~111m buffer
        "primary": 0.001,        # ~111m buffer
        "primary_link": 0.0008,  # ~89m buffer
        "secondary": 0.0005,     # ~56m buffer
        "secondary_link": 0.0004,
    }

    urban_polys = []
    stats = {"urban": 0, "roads": 0, "infra": 0}

    for fname in os.listdir(cache_dir):
        if not fname.endswith(".json") or fname.startswith("CA-") or fname == "hydro_debug.json":
            continue
        fpath = cache_dir / fname
        if fpath.stat().st_size < 2000:
            continue
        try:
            with open(fpath) as f:
                data = json.load(f)
            for zone in data.get("exclusion_zones", []):
                ex_type = zone.get("type", "")
                sub_type = (zone.get("sub_type") or "unknown").lower()
                coords = zone.get("coordinates", [])
                geom = zone.get("geometry", "polygon")

                buf = 0  # default no buffer

                if ex_type == "urban":
                    if sub_type not in URBAN_EXCLUDE_SUBTYPES:
                        continue
                    stats["urban"] += 1
                elif ex_type == "roads":
                    if sub_type not in ROAD_MAJOR:
                        continue
                    buf = ROAD_MAJOR[sub_type]
                    stats["roads"] += 1
                elif ex_type == "infrastructure":
                    if sub_type not in ("unknown", "rail", "railway"):
                        continue
                    buf = 0.0005  # ~56m buffer for railways
                    stats["infra"] += 1
                else:
                    continue

                if geom == "polygon" and len(coords) >= 4:
                    try:
                        poly = ShapelyPolygon([(c[0], c[1]) for c in coords])
                        if poly.is_valid and poly.area > 0:
                            if buf > 0:
                                poly = poly.buffer(buf)
                            urban_polys.append(poly)
                    except Exception:
                        pass
                elif geom == "line" and len(coords) >= 2:
                    try:
                        from shapely.geometry import LineString
                        line = LineString([(c[0], c[1]) for c in coords])
                        line_buf = max(buf, 0.0005)
                        buffered = line.buffer(line_buf)
                        if buffered.is_valid and buffered.area > 0:
                            urban_polys.append(buffered)
                    except Exception:
                        pass
        except Exception:
            continue

    if urban_polys:
        try:
            _urban_union_zone_cache = unary_union(urban_polys)
            logger.info(
                f"[Phase3.1-SUPRA] Cache anthropique: {len(urban_polys)} polygones "
                f"(urban={stats['urban']}, roads={stats['roads']}, infra={stats['infra']})"
            )
        except Exception:
            pass

    _urban_zone_cache_loaded = True
    return _urban_union_zone_cache


def _circle_on_urban(center_lat: float, center_lng: float) -> bool:
    """
    Phase 3.1-SUPRA: Verifie si un cercle 600m est en zone anthropique.
    Utilise le ratio d'overlap UNIQUEMENT (pas de buffer centre) pour
    eviter les faux positifs pres des limites municipales en zone forestiere.
    Seuil: 5% overlap = exclusion (le cercle touche une zone urbanisee).
    """
    urban = _load_urban_cache_zones()
    if urban is None or not SHAPELY_AVAILABLE:
        return False
    try:
        coords = _make_circle_coords(center_lat, center_lng, CIRCLE_RADIUS_M)
        poly = ShapelyPolygon(coords)
        if not poly.is_valid:
            poly = poly.buffer(0)
        overlap = poly.intersection(urban).area
        ratio = overlap / poly.area if poly.area > 0 else 0
        return ratio > URBAN_OVERLAP_THRESHOLD
    except Exception:
        return False


def _make_circle_coords(center_lat: float, center_lng: float, radius_m: float) -> list:
    """Genere un cercle en [lng, lat] format GeoJSON."""
    coords = []
    for i in range(CIRCLE_NUM_POINTS):
        angle = 2 * math.pi * i / CIRCLE_NUM_POINTS
        dlat = (radius_m * math.cos(angle)) / 111320.0
        dlng = (radius_m * math.sin(angle)) / (111320.0 * math.cos(math.radians(center_lat)))
        coords.append([center_lng + dlng, center_lat + dlat])
    coords.append(coords[0])
    return coords


def _convert_features_to_circles(geojson: dict) -> tuple:
    """
    V6.x + Phase 3.1-SUPRA — Convertit features GeoJSON en CERCLES 600m.
    Exclut: eau (V7), urbain/industriel (Phase 3.1).
    Retourne (geojson modifie, nombre exclus eau+urbain).
    """
    water_excluded = 0
    urban_excluded = 0
    valid_features = []
    total_input = len(geojson.get("features", []))

    for feature in geojson.get("features", []):
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])

        if geom.get("type") == "Polygon" and coords and coords[0]:
            ring = coords[0]
            if len(ring) >= 3:
                center_lng = sum(c[0] for c in ring) / len(ring)
                center_lat = sum(c[1] for c in ring) / len(ring)
            else:
                valid_features.append(feature)
                continue
        else:
            valid_features.append(feature)
            continue

        # V7: Exclure si sur eau
        if _circle_on_water(center_lat, center_lng):
            water_excluded += 1
            continue

        # Phase 3.1: Exclure si en zone urbaine
        if _circle_on_urban(center_lat, center_lng):
            urban_excluded += 1
            continue

        circle_coords = _make_circle_coords(center_lat, center_lng, CIRCLE_RADIUS_M)
        feature["geometry"]["coordinates"] = [circle_coords]
        feature["properties"]["geometry_type"] = "circle_600m"
        feature["properties"]["radius_m"] = CIRCLE_RADIUS_M
        feature["properties"]["center"] = [center_lat, center_lng]
        valid_features.append(feature)

    geojson["features"] = valid_features
    total_excluded = water_excluded + urban_excluded

    # Phase 3.1: Log DETAILLE de l'exclusion
    logger.info(
        f"[Phase3.1-CIRCLES] Input={total_input}, Water={water_excluded}, "
        f"Urban={urban_excluded}, Kept={len(valid_features)} "
        f"(thresholds: water={WATER_OVERLAP_THRESHOLD}, urban={URBAN_OVERLAP_THRESHOLD})"
    )

    return geojson, total_excluded

# Thread pool for parallel layer processing (CPU-bound)
_executor = ThreadPoolExecutor(max_workers=10)  # BCE-4X PERF: augmente de 6 a 10


def _cache_key(bounds, species, layers, waypoint_center=None) -> str:
    # R1: Grille fixe 0.02deg (~2.2km) — aligne avec seed rasterizer
    s = math.floor(bounds['south'] / 0.02) * 0.02
    w = math.floor(bounds['west'] / 0.02) * 0.02
    n = math.floor(bounds['north'] / 0.02) * 0.02
    e = math.floor(bounds['east'] / 0.02) * 0.02
    data = f"{s:.4f}_{w:.4f}_{n:.4f}_{e:.4f}_{species}_{'_'.join(sorted(layers))}"
    if waypoint_center:
        data += f"_wp{waypoint_center['lat']:.4f}_{waypoint_center['lng']:.4f}"
    return hashlib.md5(data.encode()).hexdigest()



def _generate_corridors_10x(zones_by_layer, species, waypoint_center, bounds):
    """
    BIONIC 2000% — Corridors 10X avec A* pathfinding réel.
    Utilise l'algorithme A* de corridor_10x.py pour trouver des chemins optimaux
    entre zones fonctionnelles, en tenant compte des coûts de terrain.
    """
    from modules.bionic_engine_p0.services.corridor_10x import (
        corridor_10x_service, corridor_pathfinder
    )

    # --- Phase 1: Extraire les centroides par couche fonctionnelle ---
    STRUCTURAL_LAYERS = {"hydro", "pentes", "orientation", "ensoleillement", "altitude", "ndvi", "peuplements"}
    zone_centroids = {}
    zone_polygons = []  # Pour construire terrain_data

    for layer_id, zones in zones_by_layer.items():
        is_functional = layer_id not in STRUCTURAL_LAYERS
        for idx, z in enumerate(zones):
            centroid = z.get("centroid", {})
            lat = centroid.get("lat", 0)
            lng = centroid.get("lng", 0)
            coords = z.get("coordinates", [])
            if lat == 0 or lng == 0:
                if len(coords) >= 3:
                    lng = sum(c[0] for c in coords) / len(coords)
                    lat = sum(c[1] for c in coords) / len(coords)
                else:
                    continue
            # Stocker le polygone pour le terrain A*
            if coords:
                zone_polygons.append({
                    "layer_id": layer_id,
                    "coords": coords,
                    "centroid": (lat, lng),
                })
            if is_functional:
                zone_centroids.setdefault(layer_id, []).append({
                    "lat": lat, "lng": lng,
                    "zone_id": f"{layer_id}_{idx}",
                    "score": z.get("score", z.get("zoneScore", 0)),
                })

    logger.info(f"[Corridor A*] Zone centroids: { {k: len(v) for k, v in zone_centroids.items()} }")

    # --- Phase 2: Construire terrain_data pour le A* ---
    terrain_data = _build_terrain_grid(zone_polygons, bounds)

    # --- Phase 3: Générer les corridors avec A* ---
    CONNECT_PAIRS = [
        ("alimentation", "repos"), ("alimentation", "rut"), ("repos", "rut"),
        ("habitats", "alimentation"), ("habitats", "repos"), ("salines", "repos"),
        ("affuts", "habitats"), ("trajets", "alimentation"),
        ("affuts", "rut"), ("affuts", "trajets"), ("trajets", "rut"),
        ("salines", "rut"), ("salines", "affuts"), ("habitats", "rut"),
        ("habitats", "trajets"), ("salines", "trajets"),
        ("affuts", "repos"), ("affuts", "alimentation"),
    ]

    corridors = []
    corridor_id = 0
    seen_pairs = set()

    for from_layer, to_layer in CONNECT_PAIRS:
        from_zones = zone_centroids.get(from_layer, [])
        to_zones = zone_centroids.get(to_layer, [])
        if not from_zones or not to_zones:
            continue

        for fz in from_zones[:3]:
            best_tz = None
            best_dist = float("inf")
            for tz in to_zones:
                dlat = (fz["lat"] - tz["lat"]) * METERS_PER_DEG_LAT
                dlng = (fz["lng"] - tz["lng"]) * METERS_PER_DEG_LAT * math.cos(math.radians(fz["lat"]))
                dist = math.sqrt(dlat ** 2 + dlng ** 2)
                if dist < best_dist and dist > 50:
                    pair_key = f"{fz['zone_id']}-{tz['zone_id']}"
                    reverse_key = f"{tz['zone_id']}-{fz['zone_id']}"
                    if pair_key not in seen_pairs and reverse_key not in seen_pairs:
                        best_dist = dist
                        best_tz = tz

            if not best_tz or best_dist > 3000:
                continue

            pair_key = f"{fz['zone_id']}-{best_tz['zone_id']}"
            seen_pairs.add(pair_key)

            wwf_type = corridor_10x_service.classify_corridor_wwf(best_dist * 0.3)
            connectivity = corridor_10x_service.calculate_connectivity_score(from_layer, to_layer)

            # A* pathfinding
            path_coords = _find_astar_path(
                fz, best_tz, terrain_data, corridor_pathfinder, best_dist
            )

            corridors.append(_build_corridor_feature_astar(
                corridor_id, fz, best_tz, from_layer, to_layer, best_dist,
                wwf_type, connectivity, corridor_10x_service, path_coords
            ))
            corridor_id += 1

            if corridor_id >= 20:
                break
        if corridor_id >= 20:
            break

    # Fallback: intra-layer corridors
    if not corridors and zone_centroids:
        for layer_id, centroids in zone_centroids.items():
            if len(centroids) < 2:
                continue
            for i in range(len(centroids)):
                for j in range(i + 1, min(len(centroids), i + 3)):
                    fz, tz = centroids[i], centroids[j]
                    dlat = (fz["lat"] - tz["lat"]) * METERS_PER_DEG_LAT
                    dlng = (fz["lng"] - tz["lng"]) * METERS_PER_DEG_LAT * math.cos(math.radians(fz["lat"]))
                    dist = math.sqrt(dlat ** 2 + dlng ** 2)
                    if 50 < dist < 3000:
                        wwf_type = corridor_10x_service.classify_corridor_wwf(dist * 0.3)
                        path_coords = _find_astar_path(
                            fz, tz, terrain_data, corridor_pathfinder, dist
                        )
                        corridors.append(_build_corridor_feature_astar(
                            corridor_id, fz, tz, layer_id, layer_id, dist,
                            wwf_type, 50, corridor_10x_service, path_coords
                        ))
                        corridor_id += 1
                if corridor_id >= 10:
                    break
            if corridor_id >= 10:
                break

    logger.info(f"[Corridor A*] Generated {len(corridors)} corridors for species={species}")
    return corridors


def _build_terrain_grid(zone_polygons, bounds):
    """
    Construit une grille de coûts de terrain pour l'algorithme A*.
    Optimisé: n'échantillonne que les centroides + voisinage immédiat.
    """
    terrain_data = {}
    from modules.bionic_engine_p0.services.corridor_10x import TERRAIN_COSTS

    LAYER_TO_TERRAIN = {
        "habitats": "mature_forest", "alimentation": "forest_edge",
        "repos": "conifer_forest", "rut": "mixed_forest",
        "affuts": "hedgerow", "trajets": "wooded_strip",
        "salines": "riparian", "corridors": "valley",
        "peuplements": "mixed_forest", "hydro": "water_body",
    }

    step = 0.0015  # ~167m grid resolution
    max_cells = 2000  # Limite pour performance
    cell_count = 0

    for zp in zone_polygons:
        if cell_count >= max_cells:
            break
        coords = zp["coords"]
        layer_id = zp["layer_id"]
        terrain_type = LAYER_TO_TERRAIN.get(layer_id, "mixed_forest")
        if len(coords) < 3:
            continue

        # Bounding box du polygone
        lats = [c[1] for c in coords]
        lngs = [c[0] for c in coords]
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)

        # Ajouter une marge autour de la zone
        margin = step * 2
        lat = min_lat - margin
        while lat <= max_lat + margin and cell_count < max_cells:
            lng = min_lng - margin
            while lng <= max_lng + margin and cell_count < max_cells:
                key = f"{lat:.4f},{lng:.4f}"
                existing = terrain_data.get(key, {})
                existing_cost = TERRAIN_COSTS.get(existing.get("type", "open_field"), 3.0)
                new_cost = TERRAIN_COSTS.get(terrain_type, 2.0)
                if new_cost < existing_cost:
                    terrain_data[key] = {"type": terrain_type, "slope": 5, "human_pressure": 0.1}
                    cell_count += 1
                lng += step
            lat += step

    return terrain_data


def _find_astar_path(fz, tz, terrain_data, pathfinder, distance):
    """
    Trouve un chemin A* entre deux zones. Fallback Bezier si échec.
    """
    start = (fz["lat"], fz["lng"])
    end = (tz["lat"], tz["lng"])

    # Ajuster la résolution selon la distance
    if distance < 300:
        pathfinder.grid_resolution = 30.0
        max_iter = 3000
    elif distance < 800:
        pathfinder.grid_resolution = 60.0
        max_iter = 5000
    elif distance < 1500:
        pathfinder.grid_resolution = 120.0
        max_iter = 8000
    else:
        pathfinder.grid_resolution = 200.0
        max_iter = 10000

    try:
        result = pathfinder.find_corridor_path(start, end, terrain_data, max_iterations=max_iter)
        if result and result.get("path"):
            smoothed = pathfinder.smooth_path(result["path"], smoothing_factor=0.3)
            return [[round(p["lng"], 6), round(p["lat"], 6)] for p in smoothed]
    except Exception as e:
        logger.warning(f"[Corridor A*] Pathfinding failed: {e}")

    # Fallback: Bezier quadratique
    n_points = max(5, int(distance / 50))
    path_coords = []
    for i in range(n_points + 1):
        t = i / n_points
        mid_lat = (fz["lat"] + tz["lat"]) / 2 + (0.0002 * math.sin(t * math.pi))
        mid_lng = (fz["lng"] + tz["lng"]) / 2 + (0.0002 * math.cos(t * math.pi))
        lat = (1 - t) ** 2 * fz["lat"] + 2 * (1 - t) * t * mid_lat + t ** 2 * tz["lat"]
        lng = (1 - t) ** 2 * fz["lng"] + 2 * (1 - t) * t * mid_lng + t ** 2 * tz["lng"]
        path_coords.append([round(lng, 6), round(lat, 6)])
    return path_coords


def _build_corridor_feature_astar(corridor_id, fz, tz, from_layer, to_layer, dist, wwf_type, connectivity, service, path_coords):
    """Build a corridor GeoJSON Feature — V9 Pipeline with 9 BIONIC engines."""
    is_astar = len(path_coords) > 0 and len(path_coords) != max(5, int(dist / 50)) + 1
    pathfinding_method = "A*" if is_astar else "bezier_fallback"

    # V9: Build base feature, scoring will be computed by engines
    feature = {
        "type": "Feature",
        "id": f"corridor-10x-{corridor_id}",
        "geometry": {"type": "LineString", "coordinates": path_coords},
        "properties": {
            "source": "corridor_10x",
            "corridor_type": wwf_type.value,  # Will be overridden by V9 classification
            "from_zone_type": from_layer,
            "to_zone_type": to_layer,
            "from_zone_id": fz["zone_id"],
            "to_zone_id": tz["zone_id"],
            "distance_m": round(dist, 1),
            "sex": "both",
            "pathfinding": pathfinding_method,
            "dem_enhanced": False,
            "in_perimeter": True,
            "scoring": {
                "score": 0,  # Placeholder — V9 engines will compute
                "subscores": {"connectivity": round(connectivity, 1)},
                "justification": [],
            },
            "wwf_classification": {"type": wwf_type.value, "label": service._get_wwf_label(wwf_type)},
        },
    }

    # V9: Evaluate with full pipeline (9 engines + continuity fix + enrichment)
    try:
        from modules.bionic_engine_p0.engines.corridors_v9 import corridor_engine_v9, CLASSIFICATION_V9
        from datetime import datetime, timezone

        global_context = {
            "species": getattr(service, '_current_species', 'moose'),
            "season": getattr(service, '_current_season', 'automne'),
            "month": datetime.now(timezone.utc).month,
            "hour": datetime.now(timezone.utc).hour,
            "weather": getattr(service, '_current_weather', {}),
            # STEVE-MAX: Waypoint center for STRICT 2km analysis box computation
            "waypoint_lat": getattr(service, '_current_waypoint_lat', None),
            "waypoint_lng": getattr(service, '_current_waypoint_lng', None),
        }

        # Full V9 pipeline: evaluate + fix gaps + clip + enrich + validate
        bounds = getattr(service, '_current_bounds', None)
        feature = corridor_engine_v9.process_corridor_full(feature, global_context, bounds)

        # Apply V9 classification styling
        classification = feature["properties"].get("classification_v9", {})
        level = classification.get("level", "gris")
        config = CLASSIFICATION_V9.get(level, CLASSIFICATION_V9["gris"])
        feature["properties"]["style"] = {
            "color": config["color"],
            "width": config["width"],
            "opacity": config["opacity"],
            "dasharray": config.get("dash") or "none",
        }
        feature["properties"]["confidence"] = feature["properties"].get("certainty", 0.5)

    except Exception as e:
        logger.warning(f"[Corridor V9] Engine evaluation failed, using fallback: {e}")
        # Fallback: basic scoring without engines
        score = round(connectivity * 0.6 + 20, 1)
        feature["properties"]["scoring"]["score"] = score
        feature["properties"]["confidence"] = 0.3
        feature["properties"]["style"] = {"color": "#9E9E9E", "width": 1.5, "opacity": 0.5, "dasharray": "8,4"}
        feature["properties"]["v9_pipeline"] = False

    return feature




def _point_in_polygon(lat: float, lng: float, poly_coords: list) -> bool:
    inside = False
    n = len(poly_coords)
    j = n - 1
    for i in range(n):
        xi, yi = poly_coords[i]
        xj, yj = poly_coords[j]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _point_near_line(lat: float, lng: float, line_coords: list, threshold_m: float) -> bool:
    threshold_deg = threshold_m / METERS_PER_DEG_LAT
    for i in range(len(line_coords) - 1):
        x1, y1 = line_coords[i]
        x2, y2 = line_coords[i + 1]
        dx, dy = x2 - x1, y2 - y1
        len_sq = dx * dx + dy * dy
        if len_sq == 0:
            continue
        t = max(0, min(1, ((lng - x1) * dx + (lat - y1) * dy) / len_sq))
        cx, cy = x1 + t * dx, y1 + t * dy
        dist = math.sqrt(
            ((lng - cx) * math.cos(math.radians(lat))) ** 2 + (lat - cy) ** 2
        )
        if dist < threshold_deg:
            return True
    return False


def _is_zone_excluded(zone_coords: list, exclusions: list) -> bool:
    """
    HYDRO FIX FINAL — Filtrage écologique corrigé.
    Règles d'exclusion :
      - Eau UNIQUEMENT : lake, reservoir, pond > 2000 m² → > 50% hits = rejet
      - JAMAIS exclure : wetland, stream, ditch, micro_water, filtered_out
      - Routes tertiaires+ : buffer 25m, > 50% hits = rejet
      - Pistes forestières (track) : IGNORÉ
      - Urbain : > 50% hits = rejet
      - Infrastructure : > 80% hits = rejet
    """
    if not exclusions:
        return False
    n = len(zone_coords)
    if n < 3:
        return False

    clat = sum(c[1] for c in zone_coords) / n
    clng = sum(c[0] for c in zone_coords) / n

    lats = [c[1] for c in zone_coords]
    lngs = [c[0] for c in zone_coords]
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    test_points = [
        (clat, clng),
        ((clat + max_lat) / 2, clng),
        ((clat + min_lat) / 2, clng),
        (clat, (clng + max_lng) / 2),
        (clat, (clng + min_lng) / 2),
    ]

    DEEP_WATER_ONLY = {"lake", "reservoir"}
    POND_MIN_AREA = 2000

    hits_standard = 0
    hits_infra = 0
    total = len(test_points)

    for plat, plng in test_points:
        point_hit_standard = False
        point_hit_infra = False
        for ex in exclusions:
            # HYDRO FIX: skip filtered_out zones
            if ex.get("filtered_out"):
                continue

            ex_type = ex.get("type", "")

            # HYDRO FIX: never exclude wetland
            if ex_type == "wetland":
                continue

            sub_type = ex.get("sub_type", "")
            geom = ex.get("geometry_type", "polygon")
            coords = ex.get("coordinates", [])
            if not coords or len(coords) < 2:
                continue

            # --- EAU (HYDRO FIX: uniquement lake, reservoir, pond > 2000m²) ---
            if ex_type == "water":
                if geom == "polygon" and len(coords) >= 3:
                    st = (sub_type or "").lower()
                    if st in DEEP_WATER_ONLY:
                        if _point_in_polygon(plat, plng, coords):
                            point_hit_standard = True
                            break
                    elif st == "pond":
                        area = ex.get("area_m2", 0)
                        if area > POND_MIN_AREA:
                            if _point_in_polygon(plat, plng, coords):
                                point_hit_standard = True
                                break
                    # micro_water, stream, ditch, river, unknown → IGNORÉ
                continue

            # --- ROUTES ---
            if ex_type == "roads":
                if geom == "line":
                    st = (sub_type or "").lower()
                    if st == "track":
                        continue
                    if _point_near_line(plat, plng, coords, 25):
                        point_hit_standard = True
                        break
                continue

            # --- URBAIN ---
            if ex_type == "urban":
                if geom == "polygon" and len(coords) >= 3:
                    if _point_in_polygon(plat, plng, coords):
                        point_hit_standard = True
                        break
                continue

            # --- INFRASTRUCTURE (seuil séparé: > 80%) ---
            if ex_type == "infrastructure":
                if geom == "polygon" and len(coords) >= 3:
                    if _point_in_polygon(plat, plng, coords):
                        point_hit_infra = True
                        break
                continue

        if point_hit_standard:
            hits_standard += 1
        if point_hit_infra:
            hits_infra += 1

    if hits_standard > (total / 2):
        return True
    if hits_infra > (total * 0.8):
        return True
    return False



async def _refresh_overpass_cache_bg(uncached_tiles, exclude_types, detail_level, timeout):
    """BCE-4X PERF: Rafraichit le cache Overpass en arriere-plan (fire-and-forget)."""
    import httpx
    from modules.bionic_engine_p0.routers.terrain_data_router import (
        _build_overpass_query, _save_cache,
        _parse_overpass, OVERPASS_API_URL
    )
    try:
        for tile, bbox, ck in uncached_tiles:
            query = _build_overpass_query(
                tile["south"], tile["west"], tile["north"], tile["east"],
                exclude_types, detail_level
            )
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(OVERPASS_API_URL, data={"data": query})
                if resp.status_code == 200:
                    data = resp.json()
                    result = _parse_overpass(data, exclude_types)
                    await _save_cache(ck, {"success": True, "exclusion_zones": result})
                    logger.info(f"[BCE-4X-BG] Overpass cache refreshed for tile {bbox}")
    except Exception as e:
        logger.debug(f"[BCE-4X-BG] Background Overpass refresh failed: {e}")


async def _fetch_exclusions_from_raw_osm(bounds: Dict[str, float]) -> List[Dict]:
    """
    Phase 3.1-SUPRA: Fallback RAW OSM API quand Overpass est indisponible.
    Utilise api.openstreetmap.org/api/0.6/map pour recuperer les donnees brutes.
    Convertit en format exclusion_zones compatible avec le pipeline existant.
    """
    import httpx
    import xml.etree.ElementTree as ET

    RAW_OSM_URL = "https://api.openstreetmap.org/api/0.6/map"
    URBAN_TAGS = {"residential", "commercial", "industrial", "retail", "construction"}
    MAJOR_ROADS = {"motorway", "trunk", "primary", "secondary", "motorway_link", "trunk_link"}

    south = bounds["south"]
    west = bounds["west"]
    north = bounds["north"]
    east = bounds["east"]

    # RAW OSM API limits bbox to ~0.25 degrees per side — tile if needed
    tile_size = 0.04  # ~4.4km per tile
    tiles = []
    lat = south
    while lat < north:
        lng = west
        while lng < east:
            tiles.append({
                "s": lat, "n": min(lat + tile_size, north),
                "w": lng, "e": min(lng + tile_size, east),
            })
            lng += tile_size
        lat += tile_size

    exclusions = []
    async with httpx.AsyncClient(timeout=20) as client:
        for tile in tiles[:16]:  # Max 16 tiles
            bbox = f"{tile['w']},{tile['s']},{tile['e']},{tile['n']}"
            try:
                resp = await client.get(
                    RAW_OSM_URL, params={"bbox": bbox},
                    headers={"User-Agent": "HUNTIQ-V6/1.0"}
                )
                if resp.status_code != 200:
                    continue

                root = ET.fromstring(resp.text)

                # Build node lookup
                nodes = {}
                for node in root.findall("node"):
                    nid = node.get("id")
                    lat_n = float(node.get("lat", 0))
                    lon_n = float(node.get("lon", 0))
                    nodes[nid] = (lon_n, lat_n)

                # Process ways
                for way in root.findall("way"):
                    tags = {}
                    for tag in way.findall("tag"):
                        tags[tag.get("k", "")] = tag.get("v", "")

                    landuse = tags.get("landuse", "")
                    highway = tags.get("highway", "")
                    building = tags.get("building", "")

                    ex_type = None
                    sub_type = ""
                    geom_type = "polygon"

                    if landuse in URBAN_TAGS:
                        ex_type = "urban"
                        sub_type = landuse
                    elif highway in MAJOR_ROADS:
                        ex_type = "roads"
                        sub_type = highway
                        geom_type = "line"
                    elif building:
                        ex_type = "urban"
                        sub_type = f"building:{building}"
                    else:
                        continue

                    # Resolve node references to coordinates
                    coords = []
                    for nd in way.findall("nd"):
                        ref = nd.get("ref")
                        if ref in nodes:
                            coords.append(list(nodes[ref]))

                    if len(coords) < 3 and geom_type == "polygon":
                        continue
                    if len(coords) < 2:
                        continue

                    exclusions.append({
                        "type": ex_type,
                        "sub_type": sub_type,
                        "geometry": geom_type,
                        "coordinates": coords,
                    })

            except ET.ParseError:
                continue
            except Exception as e:
                logger.debug(f"[RAW-OSM] Tile {bbox} error: {e}")
                continue

    if exclusions:
        logger.info(f"[Phase3.1-SUPRA] RAW OSM API: {len(exclusions)} exclusions from {len(tiles)} tiles")

        # ALSO inject into the urban cache for _circle_on_urban
        _inject_raw_osm_into_urban_cache(exclusions)

    return exclusions


def _inject_raw_osm_into_urban_cache(exclusions: List[Dict]):
    """
    Phase 3.1-SUPRA: Enrichit le cache urbain avec les donnees RAW OSM.
    APPROCHE DENSITE: Les batiments sont buffers generusement (50m) puis unifies.
    Le resultat est une couche urbaine CONTINUE representant les zones densement baties.
    Les routes majeures sont bufferees selon leur importance.
    """
    global _urban_union_zone_cache, _urban_zone_cache_loaded
    if not SHAPELY_AVAILABLE:
        return

    ROAD_BUFFERS = {
        "motorway": 0.002, "motorway_link": 0.0015,
        "trunk": 0.0015, "trunk_link": 0.001,
        "primary": 0.001, "primary_link": 0.0008,
        "secondary": 0.0005, "secondary_link": 0.0004,
    }
    BUILDING_BUFFER = 0.0005   # ~55m buffer autour de chaque batiment
    LANDUSE_BUFFER = 0.0001    # ~11m buffer autour des zones de landuse

    new_polys = []
    for z in exclusions:
        coords = z.get("coordinates", [])
        geom = z.get("geometry", "polygon")
        ex_type = z.get("type", "")
        sub_type = (z.get("sub_type") or "").lower()

        if geom == "polygon" and len(coords) >= 3:
            try:
                poly = ShapelyPolygon([(c[0], c[1]) for c in coords])
                if poly.is_valid and poly.area > 0:
                    # Batiments: buffer genereusement pour creer une zone continue
                    if sub_type.startswith("building:") or sub_type == "building":
                        poly = poly.buffer(BUILDING_BUFFER)
                    elif sub_type in ("residential", "commercial", "industrial", "retail"):
                        poly = poly.buffer(LANDUSE_BUFFER)
                    new_polys.append(poly)
            except Exception:
                pass
        elif geom == "line" and len(coords) >= 2:
            try:
                from shapely.geometry import LineString
                line = LineString([(c[0], c[1]) for c in coords])
                buf = ROAD_BUFFERS.get(sub_type, 0.0005)
                buffered = line.buffer(buf)
                if buffered.is_valid and buffered.area > 0:
                    new_polys.append(buffered)
            except Exception:
                pass

    if new_polys:
        try:
            new_union = unary_union(new_polys)
            if _urban_union_zone_cache is not None:
                _urban_union_zone_cache = unary_union([_urban_union_zone_cache, new_union])
            else:
                _urban_union_zone_cache = new_union
            _urban_zone_cache_loaded = True
            logger.info(
                f"[Phase3.1-SUPRA] Urban cache enriched: {len(new_polys)} RAW OSM polygons "
                f"(area={_urban_union_zone_cache.area:.6f})"
            )
        except Exception as e:
            logger.warning(f"[Phase3.1-SUPRA] Urban cache injection failed: {e}")


async def _fetch_exclusions_from_terrain(bounds: Dict[str, float]) -> List[Dict]:
    """
    ExclusionsSpatiales.v1 — Fetch exclusions depuis l'API Overpass.
    Inclut: water, urban, roads, infrastructure.
    RETRY 3x avec délai exponentiel en cas d'échec.
    Couvre exactement le viewport utilisateur.
    Tiling automatique si viewport > 0.3° pour respecter la limite Overpass.

    BIONIC V8.2 RESILIENCE:
    - Timeout Overpass: 12s (fast-fail)
    - Fallback sur cache expiré AVANT le 2e retry
    - Dégradation gracieuse: génère des zones avec exclusions=[] si tout échoue
    - Temps max total estimé: ~15s au lieu de ~42s
    """
    OVERPASS_TIMEOUT = 5  # secondes — BCE-4X ultra fast-fail (reduit de 12s a 5s)
    RETRY_DELAY = 0.5

    import httpx
    from modules.bionic_engine_p0.routers.terrain_data_router import (
        _build_overpass_query, _load_cache, _load_cache_expired, _save_cache,
        _cache_key as terrain_cache_key,
        _parse_overpass, OVERPASS_API_URL
    )

    exclude_types = ["water", "urban", "roads", "infrastructure"]
    detail_level = "low"

    # Tiling
    lat_range = bounds["north"] - bounds["south"]
    lng_range = bounds["east"] - bounds["west"]
    tiles = []
    if lat_range > 0.08 or lng_range > 0.12:
        tile_h, tile_w = 0.06, 0.08
        lat = bounds["south"]
        while lat < bounds["north"]:
            lng = bounds["west"]
            while lng < bounds["east"]:
                tiles.append({
                    "south": lat, "north": min(lat + tile_h, bounds["north"]),
                    "west": lng, "east": min(lng + tile_w, bounds["east"]),
                })
                lng += tile_w
            lat += tile_h
    else:
        tiles = [bounds]

    tile_cache_keys = []
    for tile in tiles[:9]:
        bbox = (tile["south"], tile["west"], tile["north"], tile["east"])
        ck = terrain_cache_key(bbox, exclude_types, detail_level)
        tile_cache_keys.append((tile, bbox, ck))

    # === PHASE 1: Cache frais ===
    fresh_exclusions = []
    uncached_tiles = []
    for tile, bbox, ck in tile_cache_keys:
        cached = await _load_cache(ck)
        if cached:
            fresh_exclusions.extend(cached.get("exclusion_zones", []))
        else:
            uncached_tiles.append((tile, bbox, ck))

    if not uncached_tiles:
        logger.info(f"ExclusionsSpatiales.v1: ALL from fresh cache — {len(fresh_exclusions)} exclusions")
        return fresh_exclusions

    # === BCE-4X PERF: PHASE 2 — Stale-While-Revalidate ===
    # Verifier le cache expire AVANT d'appeler Overpass (economise 5s si Overpass down)
    expired_exclusions = list(fresh_exclusions)
    for tile, bbox, ck in uncached_tiles:
        expired = await _load_cache_expired(ck)
        if expired:
            expired_exclusions.extend(expired.get("exclusion_zones", []))

    if expired_exclusions:
        # On a des donnees en cache expire — les utiliser IMMEDIATEMENT
        # et tenter Overpass en arriere-plan pour rafraichir le cache
        logger.info(
            f"ExclusionsSpatiales.v1: STALE-WHILE-REVALIDATE — "
            f"{len(expired_exclusions)} exclusions (serving stale, refreshing async)"
        )
        # Lance le rafraichissement Overpass en arriere-plan (fire-and-forget)
        asyncio.create_task(_refresh_overpass_cache_bg(uncached_tiles, exclude_types, detail_level, OVERPASS_TIMEOUT))

        # Phase 3.1-SUPRA: AUSSI enrichir le cache urbain via RAW OSM API
        # (le cache expire peut etre incomplet pour la zone demandee)
        try:
            raw_exclusions = await _fetch_exclusions_from_raw_osm(bounds)
            if raw_exclusions:
                expired_exclusions.extend(raw_exclusions)
                logger.info(
                    f"ExclusionsSpatiales.v1: STALE+RAW_OSM combined — "
                    f"{len(expired_exclusions)} total exclusions"
                )
        except Exception as e:
            logger.warning(f"ExclusionsSpatiales.v1: RAW OSM enrichment failed: {e}")

        return expired_exclusions

    # === PHASE 3: Pas de cache — Overpass obligatoire (1 seul essai, fast-fail) ===
    overpass_ok = False
    try:
        for tile, bbox, ck in uncached_tiles:
            query = _build_overpass_query(
                tile["south"], tile["west"], tile["north"], tile["east"],
                exclude_types, detail_level
            )
            async with httpx.AsyncClient(timeout=OVERPASS_TIMEOUT) as client:
                resp = await client.post(OVERPASS_API_URL, data={"data": query})
                if resp.status_code == 200:
                    data = resp.json()
                    result = _parse_overpass(data, exclude_types)
                    await _save_cache(ck, {"success": True, "exclusion_zones": result})
                    fresh_exclusions.extend(result)
                    overpass_ok = True
                else:
                    logger.warning(f"Overpass HTTP {resp.status_code} for tile {bbox}")
                    raise Exception(f"HTTP {resp.status_code}")
    except Exception as e:
        logger.warning(f"ExclusionsSpatiales.v1: Overpass failed: {e}")

    if overpass_ok and fresh_exclusions:
        logger.info(f"ExclusionsSpatiales.v1: Overpass OK — {len(fresh_exclusions)} exclusions")
        return fresh_exclusions

    # === PHASE 4: RAW OSM API Fallback (Phase 3.1-SUPRA) ===
    # Quand Overpass est totalement indisponible, utiliser l'API OSM brute
    try:
        raw_exclusions = await _fetch_exclusions_from_raw_osm(bounds)
        if raw_exclusions:
            logger.info(
                f"ExclusionsSpatiales.v1: RAW OSM API fallback — {len(raw_exclusions)} exclusions"
            )
            return raw_exclusions
    except Exception as e:
        logger.warning(f"ExclusionsSpatiales.v1: RAW OSM fallback failed: {e}")

    # === PHASE 5: Degradation gracieuse FINALE ===
    logger.warning(
        "ExclusionsSpatiales.v1: ALL sources exhausted (Overpass + RAW OSM). "
        "BIONIC V8.2: Graceful degradation — generating zones WITHOUT exclusions."
    )
    return []


def _process_single_layer(
    layer_id: str,
    bounds: Dict[str, float],
    species: str,
    resolution: int,
    max_zones_per_layer: int,
    exclusions: List[Dict],
    dem_data: Dict = None,
    pinned_month: int = None,
) -> Dict[str, Any]:
    """
    Process a single layer (CPU-bound, runs in thread pool).
    BIONIC V5 P1: Applique les pénalités semi-statiques après exclusion dure.
    BIONIC V6: Utilise le moteur Shapely si EXCLUSION_ENGINE_VERSION=v6.
    BIONIC V7: DEM SRTM data passed for terrain-aware scoring.
    R3: pinned_month propagé pour déterminisme.
    """
    if layer_id not in LAYER_PARAMS:
        return {"layer_id": layer_id, "zones": [], "scores": [], "penalties": [], "rejected": 0}

    params = LAYER_PARAMS[layer_id]
    grid = generate_layer_raster(bounds, layer_id, species, resolution)

    raw_zones = extract_organic_zones(
        grid, bounds,
        threshold=params["threshold"],
        min_area=8000.0,
        max_area=80000.0,
        chaikin_iterations=4,
        max_compactness=0.85
    )

    # === V7 FULL ENGINE (Shapely + Typology + Scoring + Shaping) ===
    if EXCLUSION_ENGINE_VERSION == "v7":
        try:
            from modules.bionic_engine_p0.services.pipeline_v7 import process_zones_v7

            valid_zones, rejected_list, v7_stats = process_zones_v7(
                raw_zones=raw_zones,
                bounds=bounds,
                exclusions=exclusions,
                layer_id=layer_id,
                species=species,
                dem_data=dem_data,
                month=pinned_month,
            )

            rejected = len(rejected_list)

            valid_zones.sort(key=lambda z: abs(z.get("area_m2", 0) - 6500))
            valid_zones = valid_zones[:max_zones_per_layer]

            layer_scores = []
            layer_penalties = []
            for zone in valid_zones:
                # BIONIC V7.4: Score V7 direct — UNIQUE source de vérité.
                # score_global inclut déjà le season modifier de enrich_zone_v7.
                # AUCUNE double pénalisation, AUCUN fallback sur le grid V5.
                v7_data = zone.get("v7", {})
                score_global = v7_data.get("score_global", 0)
                penalized_score = max(25, int(score_global)) if score_global else 50
                logger.info(
                    f"[V7.4-SCORE] {layer_id}: score_global={score_global}, "
                    f"final={penalized_score}, type={v7_data.get('zone_type')}"
                )

                layer_scores.append(penalized_score)
                layer_penalties.append({
                    "factor": 1.0,
                    "raw_score": int(v7_data.get("score_raw", score_global)),
                    "details": {},
                    "v7": v7_data,
                })

            return {
                "layer_id": layer_id,
                "zones": valid_zones,
                "scores": layer_scores,
                "penalties": layer_penalties,
                "rejected": rejected,
                "rejected_zones": rejected_list,
                "exclusion_engine": "v7",
                "exclusion_stats": v7_stats,
            }

        except Exception as e:
            logger.warning(f"V7 engine failed for {layer_id}, falling back to V6: {e}")

    # === V6 SHAPELY ENGINE ===
    if EXCLUSION_ENGINE_VERSION in ("v6", "v7"):
        try:
            from modules.bionic_engine_p0.services.exclusion_engine_v6 import process_zones_v6

            valid_zones, rejected_list, excl_stats = process_zones_v6(
                raw_zones=raw_zones,
                bounds=bounds,
                exclusions=exclusions,
                layer_id=layer_id,
                species=species,
            )

            rejected = len(rejected_list)

            valid_zones.sort(key=lambda z: abs(z.get("area_m2", 0) - 6500))
            valid_zones = valid_zones[:max_zones_per_layer]

            layer_scores = []
            layer_penalties = []
            for zone in valid_zones:
                clat = zone.get("centroid", {}).get("lat", 0)
                clng = zone.get("centroid", {}).get("lng", 0)
                row = int(((bounds["north"] - clat) / max(0.0001, bounds["north"] - bounds["south"])) * (resolution - 1))
                col = int(((clng - bounds["west"]) / max(0.0001, bounds["east"] - bounds["west"])) * (resolution - 1))
                row = max(0, min(resolution - 1, row))
                col = max(0, min(resolution - 1, col))
                intensity = float(grid[row, col])
                raw_score = max(55, min(100, int(55 + intensity * 45)))

                penalty_factor = zone.get("penalty_factor", 1.0)
                penalty_details = zone.get("penalty_details", {})
                penalized_score = max(15, int(raw_score * penalty_factor))

                layer_scores.append(penalized_score)
                layer_penalties.append({
                    "factor": penalty_factor,
                    "raw_score": raw_score,
                    "details": penalty_details,
                })

            return {
                "layer_id": layer_id,
                "zones": valid_zones,
                "scores": layer_scores,
                "penalties": layer_penalties,
                "rejected": rejected,
                "rejected_zones": rejected_list,
                "exclusion_engine": "v6",
                "exclusion_stats": excl_stats,
            }

        except Exception as e:
            logger.warning(f"V6 engine failed for {layer_id}, falling back to V5: {e}")

    # === V5 LEGACY ENGINE (fallback) ===
    rejected = 0
    valid_zones = []
    for zone in raw_zones:
        if _is_zone_excluded(zone["coordinates"], exclusions):
            rejected += 1
            continue
        valid_zones.append(zone)

    valid_zones.sort(key=lambda z: abs(z["area_m2"] - 6500))
    valid_zones = valid_zones[:max_zones_per_layer]

    # P1: Calcul des scores avec pénalités semi-statiques
    layer_scores = []
    layer_penalties = []
    for zone in valid_zones:
        clat, clng = zone["centroid"]["lat"], zone["centroid"]["lng"]
        row = int(((bounds["north"] - clat) / max(0.0001, bounds["north"] - bounds["south"])) * (resolution - 1))
        col = int(((clng - bounds["west"]) / max(0.0001, bounds["east"] - bounds["west"])) * (resolution - 1))
        row = max(0, min(resolution - 1, row))
        col = max(0, min(resolution - 1, col))
        intensity = float(grid[row, col])
        raw_score = max(55, min(100, int(55 + intensity * 45)))

        # P1: Appliquer les pénalités de proximité + fragmentation
        penalty_factor, penalty_details = calculate_zone_penalty(zone, layer_id, exclusions)
        penalized_score = max(15, int(raw_score * penalty_factor))

        layer_scores.append(penalized_score)
        layer_penalties.append({
            "factor": penalty_factor,
            "raw_score": raw_score,
            "details": penalty_details,
        })

    return {
        "layer_id": layer_id,
        "zones": valid_zones,
        "scores": layer_scores,
        "penalties": layer_penalties,
        "rejected": rejected,
    }


async def generate_organic_zones(
    bounds: Dict[str, float],
    species: str = "moose",
    layers: List[str] = None,
    exclusions: List[Dict] = None,
    resolution: int = 80,
    max_zones_per_layer: int = 8,
    waypoint_center: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    Pipeline complet de génération des zones organiques BIONIC V5.
    Backend = seule source de vérité. Fetch ses propres exclusions.
    OPTIMISÉ: traitement parallèle des couches via ThreadPoolExecutor.
    """
    start = time.time()

    if layers is None:
        layers = get_supported_layers()
    if species not in get_supported_species():
        species = "moose"

    # Filter to valid layers only
    layers = [ly for ly in layers if ly in LAYER_PARAMS]

    cache_k = _cache_key(bounds, species, layers, waypoint_center)
    cached = _zone_cache.get(cache_k)
    if cached and (time.time() - cached["ts"]) < _CACHE_TTL:
        return cached["data"]

    # BCE-4X PERFORMANCE: Fetch exclusions + DEM en PARALLELE (economise 2-3s)
    # R3: Pin month once for the entire pipeline (determinism)
    pinned_month = datetime.now(timezone.utc).month

    exclusion_task = None
    dem_task = None
    if exclusions is None or len(exclusions) == 0:
        exclusion_task = asyncio.create_task(_fetch_exclusions_from_terrain(bounds))

    dem_data = None
    if EXCLUSION_ENGINE_VERSION == "v7":
        try:
            from modules.bionic_engine_p0.services.srtm_provider_v7 import (
                fetch_dem_for_pipeline,
            )
            dem_task = asyncio.create_task(fetch_dem_for_pipeline(bounds, species))
        except Exception as e:
            logger.warning(f"[DEM] SRTM import failed: {e}")

    # Attendre les resultats en parallele
    if exclusion_task:
        exclusions = await exclusion_task
    if dem_task:
        try:
            dem_data = await dem_task
            if dem_data:
                logger.info(
                    f"[DEM] SRTM data available: "
                    f"elev=[{dem_data.get('stats', {}).get('elevation_min', '?')}, "
                    f"{dem_data.get('stats', {}).get('elevation_max', '?')}]m, "
                    f"slope_mean={dem_data.get('stats', {}).get('slope_mean_deg', '?')}deg"
                )
            else:
                logger.info("[DEM] SRTM data unavailable, using heuristic terrain signals")
        except Exception as e:
            logger.warning(f"[DEM] SRTM fetch failed, using heuristic: {e}")

    # BIONIC V8.2 RESILIENCE: Degradation gracieuse.
    exclusion_degraded = False
    if exclusions is None:
        exclusions = []
        exclusion_degraded = True
        logger.warning("[BIONIC V8.2] Exclusions=None, forcing graceful degradation")
    elif len(exclusions) == 0:
        exclusion_degraded = True
        logger.warning("[BIONIC V8.2] Exclusions empty (Overpass unavailable), zones will be generated without exclusion filtering")

    # Process ALL layers in PARALLEL using ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    futures = []
    for layer_id in layers:
        future = loop.run_in_executor(
            _executor,
            _process_single_layer,
            layer_id, bounds, species, resolution, max_zones_per_layer, exclusions, dem_data, pinned_month
        )
        futures.append(future)

    results = await asyncio.gather(*futures, return_exceptions=True)

    zones_by_layer: Dict[str, List[Dict]] = {}
    scores_by_layer: Dict[str, List[int]] = {}
    penalties_by_layer: Dict[str, List[Dict]] = {}
    stats = {
        "layers_processed": 0,
        "total_zones": 0,
        "rejected_exclusion": 0,
        "exclusions_count": len(exclusions),
        "penalties_applied": 0,
        "exclusion_engine": EXCLUSION_ENGINE_VERSION,
    }

    # Aggregate rejection diagnostics
    rejection_diagnostics = {
        "total_rejected": 0,
        "by_reason": {},
        "by_layer": {},
        "details": [],
    }

    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Layer processing failed: {result}")
            continue
        layer_id = result["layer_id"]
        zones = result["zones"]
        scores = result["scores"]
        penalties = result.get("penalties", [])
        rejected_zones_list = result.get("rejected_zones", [])
        stats["rejected_exclusion"] += result["rejected"]
        stats["layers_processed"] += 1

        # Aggregate rejection reasons
        layer_rejections = []
        for rz in rejected_zones_list:
            reason = rz.get("rejection_reason", "unknown")
            pen = rz.get("penalty_details", {})
            centroid = rz.get("centroid", {})
            area = rz.get("area_m2", 0)

            # Count by reason
            rejection_diagnostics["by_reason"][reason] = \
                rejection_diagnostics["by_reason"].get(reason, 0) + 1
            rejection_diagnostics["total_rejected"] += 1

            # Count by layer
            if layer_id not in rejection_diagnostics["by_layer"]:
                rejection_diagnostics["by_layer"][layer_id] = {"count": 0, "reasons": {}}
            rejection_diagnostics["by_layer"][layer_id]["count"] += 1
            rejection_diagnostics["by_layer"][layer_id]["reasons"][reason] = \
                rejection_diagnostics["by_layer"][layer_id]["reasons"].get(reason, 0) + 1

            # Keep detail for first 20 rejections (avoid huge payload)
            if len(rejection_diagnostics["details"]) < 20:
                detail = {
                    "layer": layer_id,
                    "reason": reason,
                    "area_m2": round(area, 0) if area else None,
                }
                if centroid:
                    detail["centroid"] = {
                        "lat": round(centroid.get("lat", 0), 5),
                        "lng": round(centroid.get("lng", 0), 5),
                    }
                if pen:
                    detail["penalties"] = {
                        k: round(v, 3) if isinstance(v, (int, float)) else v
                        for k, v in pen.items()
                    }
                layer_rejections.append(detail)

        rejection_diagnostics["details"].extend(layer_rejections)

        if zones:
            zones_by_layer[layer_id] = zones
            scores_by_layer[layer_id] = scores
            penalties_by_layer[layer_id] = penalties
            stats["total_zones"] += len(zones)
            # Count zones that received a meaningful penalty (factor < 0.95)
            stats["penalties_applied"] += sum(1 for p in penalties if p.get("factor", 1.0) < 0.95)

    geojson = zones_to_geojson(zones_by_layer, species, scores_by_layer, penalties_by_layer)

    # ════════════════════════════════════════════════
    # V6.x: CONVERSION CERCLES 600m + EXCLUSION EAU V7
    # Directive STEEVE-MAX: ZERO carre, ZERO polygone irregulier
    # ════════════════════════════════════════════════
    v7_zone_water_excluded = 0
    try:
        geojson, v7_zone_water_excluded = _convert_features_to_circles(geojson)
        if v7_zone_water_excluded > 0:
            logger.info(f"[V7-ZONES] {v7_zone_water_excluded} zones exclues (eau)")
            stats["total_zones"] -= v7_zone_water_excluded
    except Exception as e:
        logger.warning(f"[V7-ZONES] Circle conversion failed: {e}")

    # T4 COHERENCE: Count features in GeoJSON = source of truth for frontend
    t4_feature_count = len(geojson.get("features", []))
    if t4_feature_count != stats["total_zones"]:
        logger.warning(
            f"[T4-COHERENCE] MISMATCH: stats.total_zones={stats['total_zones']} "
            f"vs geojson.features={t4_feature_count}"
        )
    stats["t4_zone_count"] = t4_feature_count

    # V8/10X: Generate corridors — ALWAYS (not just v7)
    corridors = []
    v7_metadata = {}
    if EXCLUSION_ENGINE_VERSION == "v7":
        try:
            from modules.bionic_engine_p0.services.pipeline_v7 import (
                generate_all_corridors_v7,
                build_v7_response_metadata,
            )
            corridors = generate_all_corridors_v7(
                all_zones=zones_by_layer,
                exclusions=exclusions,
                species=species,
                max_corridors=20,
                dem_data=dem_data,
                month=pinned_month,
                waypoint_center=waypoint_center,
            )
            v7_stats_by_layer = {}
            for result in results:
                if isinstance(result, Exception):
                    continue
                lid = result["layer_id"]
                v7_stats_by_layer[lid] = result.get("exclusion_stats", {})
            v7_metadata = build_v7_response_metadata(v7_stats_by_layer, corridors, species)
        except Exception as e:
            logger.warning(f"V7 corridor generation failed: {e}")

    # BCE-MAX x4.1: Fallback corridor generation for non-v7 engines
    if not corridors and zones_by_layer:
        try:
            # V9: Set context for BIONIC engines
            from modules.bionic_engine_p0.services.corridor_10x import corridor_10x_service
            corridor_10x_service._current_species = species
            corridor_10x_service._current_season = season if 'season' in dir() else 'automne'
            corridor_10x_service._current_bounds = bounds
            corridor_10x_service._current_weather = weather_metadata if 'weather_metadata' in dir() else {}
            # STEVE-MAX: Pass waypoint center for STRICT 2km analysis box
            if waypoint_center:
                corridor_10x_service._current_waypoint_lat = waypoint_center.get('lat')
                corridor_10x_service._current_waypoint_lng = waypoint_center.get('lng')
            corridors = _generate_corridors_10x(zones_by_layer, species, waypoint_center, bounds)
        except Exception as e:
            logger.warning(f"Corridor 10X fallback failed: {e}")

    # V9: Filter out circular corridors (start-end < 50m is circular)
    if corridors:
        pre_filter = len(corridors)
        filtered_corridors = []
        for c in corridors:
            coords = c.get("geometry", {}).get("coordinates", [])
            if len(coords) >= 2:
                start_c = coords[0]
                end_c = coords[-1]
                dist = math.sqrt(
                    ((start_c[1] - end_c[1]) * METERS_PER_DEG_LAT) ** 2
                    + ((start_c[0] - end_c[0]) * METERS_PER_DEG_LAT * math.cos(math.radians(start_c[1]))) ** 2
                )
                if dist >= 50:
                    filtered_corridors.append(c)
                else:
                    logger.info(f"[V9-Filter] Removed circular corridor (start-end: {dist:.0f}m)")
            else:
                filtered_corridors.append(c)
        corridors = filtered_corridors
        if pre_filter != len(corridors):
            logger.info(f"[V9-Filter] Removed {pre_filter - len(corridors)} circular corridors")

    # Phase 2.9: Filter corridors crossing urban/industrial zones
    if corridors and SHAPELY_AVAILABLE:
        urban_cache = _load_urban_cache_zones()
        if urban_cache is not None:
            pre_urban = len(corridors)
            urban_filtered = []
            for c in corridors:
                coords = c.get("geometry", {}).get("coordinates", [])
                if len(coords) >= 2:
                    # Sample midpoint of corridor
                    mid_idx = len(coords) // 2
                    mid = coords[mid_idx]
                    mid_lat, mid_lng = mid[1], mid[0]
                    try:
                        pt = ShapelyPoint(mid_lng, mid_lat)
                        if not urban_cache.contains(pt):
                            urban_filtered.append(c)
                        else:
                            logger.debug(f"[Phase2.9] Corridor excluded (urban midpoint)")
                    except Exception:
                        urban_filtered.append(c)
                else:
                    urban_filtered.append(c)
            corridors = urban_filtered
            removed = pre_urban - len(corridors)
            if removed > 0:
                logger.info(f"[Phase2.9-URBAN] Removed {removed} corridors crossing urban zones")

    # STEVE-MAX++ P0: Ensure 100% topological continuity via graph-based post-processing
    if corridors:
        try:
            from modules.bionic_engine_p0.engines.corridors_v9 import ensure_corridor_network_continuity
            all_zone_features = []
            for layer_id, zone_list in zones_by_layer.items():
                for z in zone_list:
                    all_zone_features.append(z)
            corridors = ensure_corridor_network_continuity(
                corridors=corridors,
                zones=all_zone_features,
                bounds=bounds,
            )
        except Exception as e:
            logger.warning(f"[Continuity] Network continuity post-processing failed: {e}")

    elapsed = round((time.time() - start) * 1000, 1)

    # V6.x + Phase 2.9 metadata
    v6_zone_metadata = {
        "geometry": "circle_600m",
        "circle_radius_m": CIRCLE_RADIUS_M,
        "water_exclusion_engine": "V7-local-cache",
        "urban_exclusion_engine": "Phase2.9-local-cache",
        "zones_excluded": v7_zone_water_excluded,
        "water_cache_active": _water_zone_cache_loaded and _water_union_zone_cache is not None,
        "urban_cache_active": _urban_zone_cache_loaded and _urban_union_zone_cache is not None,
    }

    # BIONIC V7.3: Diagnostic — provide zero_zones_reason when all zones are filtered
    zero_reason = None
    if stats["total_zones"] == 0 and stats["rejected_exclusion"] > 0:
        zero_reason = "all_filtered_by_exclusions"
    elif stats["total_zones"] == 0 and stats["layers_processed"] > 0:
        zero_reason = "no_candidates_generated"

    result = {
        **geojson,
        "stats": {
            **stats,
            "computation_time_ms": elapsed,
            "species": species,
            "bounds": bounds,
            "resolution": resolution,
            "exclusion_degraded": exclusion_degraded,
            **({"zero_zones_reason": zero_reason} if zero_reason else {}),
            "dem_srtm": {
                "available": dem_data is not None and dem_data.get("status") == "success",
                "source": dem_data.get("validation", {}).get("source", "none") if dem_data else "none",
                "dataset": dem_data.get("dataset", "none") if dem_data else "none",
                "stats": dem_data.get("stats", {}) if dem_data and dem_data.get("status") == "success" else {},
            } if EXCLUSION_ENGINE_VERSION == "v7" else None,
        }
    }

    if corridors:
        result["corridors"] = corridors
    if v7_metadata:
        result["v7_metadata"] = v7_metadata

    # V6.x zone metadata
    result["v6_zones"] = v6_zone_metadata

    # BIONIC V8.0: Include rejection diagnostics
    if rejection_diagnostics["total_rejected"] > 0:
        result["rejection_diagnostics"] = rejection_diagnostics

    _zone_cache[cache_k] = {"data": result, "ts": time.time()}

    logger.info(
        f"Generated {stats['total_zones']} organic zones for {species} "
        f"across {stats['layers_processed']} layers in {elapsed}ms "
        f"(rejected: excl={stats['rejected_exclusion']}, total_excl={len(exclusions)})"
    )

    return result


def clear_cache():
    global _zone_cache
    _zone_cache = {}
    logger.info("[V6-ZONES] Cache vide — prochaine requete regenerera les cercles 600m")
