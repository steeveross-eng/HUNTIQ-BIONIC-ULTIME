"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
terrain_sources.py — Acquisition de donnees terrain

Sources:
1. Overpass API (chemins OSM: sentiers, quad, debardage, routes)
2. Overpass API (obstacles: zones humides, cours d'eau, foret dense)
3. Open-Meteo Elevation API (modele d'elevation DEM)

Robustesse:
- 3 miroirs Overpass avec rotation automatique
- Retry exponentiel (3 tentatives)
- Timeout adaptatif selon la taille de la zone
- Cache en memoire par zone (evite les re-fetches)

STEEVE-MAX: Aucun appel live apres le build initial du graphe.
"""
import logging
import time
import hashlib
import requests
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger("bionic.terrain_nav.sources")

# Miroirs Overpass — rotation automatique en cas de timeout
OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]

# Timeout adaptatif: base + rayon/500 secondes
# BCE-4X P0 B1: Reduit de 20/5 a 8/2 — STEEVE-MAX 2026-03-28
BASE_TIMEOUT_S = 8
TIMEOUT_PER_KM = 2

# Rayon de recherche Overpass (metres)
DEFAULT_SEARCH_RADIUS_M = 2000

# Cache global en memoire
_source_cache: Dict[str, Dict] = {}

# Tags OSM pour les chemins praticables
TRAIL_HIGHWAY_TAGS = [
    "track", "path", "footway", "service",
    "bridleway", "cycleway", "unclassified",
    "tertiary", "residential", "secondary",
]


def _zone_key(lat: float, lng: float, radius_m: int) -> str:
    """Cle de cache basee sur le centroide arrondi."""
    # BCE-4X P0 B4: Elargi de 111m (3 decimales) a 1.1km (2 decimales) — STEEVE-MAX 2026-03-28
    rlat = round(lat, 2)
    rlng = round(lng, 2)
    return f"tne:{rlat}:{rlng}:{radius_m}"


def _adaptive_timeout(radius_m: int) -> int:
    """Timeout adaptatif selon le rayon de recherche."""
    return BASE_TIMEOUT_S + int(radius_m / 1000) * TIMEOUT_PER_KM


def _build_combined_query(lat: float, lng: float, radius_m: int) -> str:
    """Requete Overpass UNIQUE combinant chemins + obstacles + foret."""
    tag_filter = "|".join(TRAIL_HIGHWAY_TAGS)
    timeout = _adaptive_timeout(radius_m)
    return f"""
[out:json][timeout:{timeout}];
(
  way["highway"~"^({tag_filter})$"](around:{radius_m},{lat},{lng});
  way["natural"="wetland"](around:{radius_m},{lat},{lng});
  way["natural"="water"](around:{radius_m},{lat},{lng});
  way["waterway"](around:{radius_m},{lat},{lng});
  way["natural"="wood"](around:{radius_m},{lat},{lng});
  way["landuse"="forest"](around:{radius_m},{lat},{lng});
);
out body;
>;
out skel qt;
"""


def _classify_ways(ways: list) -> dict:
    """Classer les ways par categorie: trails, obstacles, forest."""
    trails = []
    obstacles = []
    forest = []

    for way in ways:
        tags = way.get("tags", {})
        highway = tags.get("highway", "")
        natural = tags.get("natural", "")
        landuse = tags.get("landuse", "")
        waterway = tags.get("waterway", "")

        if highway in TRAIL_HIGHWAY_TAGS:
            trails.append(way)
        elif natural in ("water", "wetland") or waterway:
            obstacles.append(way)
        elif natural == "wood" or landuse == "forest":
            forest.append(way)

    return {"trails": trails, "obstacles": obstacles, "forest": forest}


def _fetch_overpass(query: str, timeout_s: int, max_retries: int = 3) -> Optional[Dict]:
    """
    Fetch Overpass avec retry sur miroirs multiples.
    Strategie: essayer chaque miroir, avec retry exponentiel.
    """
    for attempt in range(max_retries):
        mirror = OVERPASS_MIRRORS[attempt % len(OVERPASS_MIRRORS)]
        wait_time = 2 ** attempt if attempt > 0 else 0

        if wait_time > 0:
            logger.info(f"[TNE-SRC] Retry {attempt + 1}/{max_retries}, wait {wait_time}s, mirror: {mirror}")
            time.sleep(wait_time)

        try:
            resp = requests.post(
                mirror,
                data={"data": query},
                timeout=timeout_s + 5
            )
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("elements", [])
                logger.info(f"[TNE-SRC] Overpass OK: {len(elements)} elements from {mirror}")
                return data
            elif resp.status_code == 429:
                logger.warning(f"[TNE-SRC] Rate limited on {mirror}, rotating")
                continue
            elif resp.status_code >= 500:
                logger.warning(f"[TNE-SRC] Server error {resp.status_code} on {mirror}")
                continue
            else:
                logger.error(f"[TNE-SRC] Unexpected {resp.status_code} from {mirror}")
                continue
        except requests.exceptions.Timeout:
            logger.warning(f"[TNE-SRC] Timeout on {mirror} ({timeout_s}s)")
            continue
        except Exception as e:
            logger.error(f"[TNE-SRC] Error on {mirror}: {e}")
            continue

    logger.error(f"[TNE-SRC] ALL {max_retries} attempts FAILED")
    return None


def _parse_osm_elements(data: Dict) -> Tuple[Dict[int, Tuple[float, float]], List[Dict]]:
    """Extraire noeuds et ways depuis la reponse Overpass."""
    node_coords: Dict[int, Tuple[float, float]] = {}
    ways: List[Dict] = []

    for el in data.get("elements", []):
        if el["type"] == "node" and "lat" in el and "lon" in el:
            node_coords[el["id"]] = (el["lat"], el["lon"])
        elif el["type"] == "way":
            ways.append(el)

    return node_coords, ways


def fetch_terrain_data(
    lat: float, lng: float,
    radius_m: int = DEFAULT_SEARCH_RADIUS_M
) -> Dict[str, Any]:
    """
    Acquisition complete des donnees terrain pour une zone.
    UNE SEULE requete Overpass combinee (chemins + obstacles + foret).
    Cache en memoire.

    Retourne:
    {
        "trails": {"node_coords": {...}, "ways": [...]},
        "obstacles": {"node_coords": {...}, "ways": [...]},
        "forest": {"node_coords": {...}, "ways": [...]},
        "source": "overpass" | "cache",
        "has_trails": bool,
        "has_obstacles": bool,
        "has_forest": bool,
    }
    """
    key = _zone_key(lat, lng, radius_m)
    if key in _source_cache:
        logger.info(f"[TNE-SRC] Cache HIT for {key}")
        cached = _source_cache[key]
        cached["source"] = "cache"
        return cached

    logger.info(f"[TNE-SRC] Fetching terrain data for ({lat:.4f}, {lng:.4f}), radius={radius_m}m")
    timeout = _adaptive_timeout(radius_m)

    result: Dict[str, Any] = {
        "trails": {"node_coords": {}, "ways": []},
        "obstacles": {"node_coords": {}, "ways": []},
        "forest": {"node_coords": {}, "ways": []},
        "source": "overpass",
        "has_trails": False,
        "has_obstacles": False,
        "has_forest": False,
    }

    # UNE SEULE requete Overpass combinee
    combined_query = _build_combined_query(lat, lng, radius_m)
    data = _fetch_overpass(combined_query, timeout)

    if data:
        nc, all_ways = _parse_osm_elements(data)
        classified = _classify_ways(all_ways)

        result["trails"] = {"node_coords": nc, "ways": classified["trails"]}
        result["obstacles"] = {"node_coords": nc, "ways": classified["obstacles"]}
        result["forest"] = {"node_coords": nc, "ways": classified["forest"]}
        result["has_trails"] = len(classified["trails"]) > 0
        result["has_obstacles"] = len(classified["obstacles"]) > 0
        result["has_forest"] = len(classified["forest"]) > 0

        logger.info(
            f"[TNE-SRC] Combined fetch: {len(classified['trails'])} trails, "
            f"{len(classified['obstacles'])} obstacles, "
            f"{len(classified['forest'])} forest zones, "
            f"{len(nc)} total nodes"
        )

    _source_cache[key] = result
    return result
