"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
terrain_sources.py — Acquisition de donnees terrain

Sources:
1. Overpass API (chemins OSM: sentiers, quad, debardage, routes)
2. Overpass API (obstacles: zones humides, cours d'eau, foret dense)
3. Open-Meteo Elevation API (modele d'elevation DEM)

Robustesse:
- BCE-4X P1 B2: 3 miroirs Overpass en PARALLELE (premier gagne)
- Timeout adaptatif selon la taille de la zone
- Cache PERSISTANT fichier gzip (ZERO appel Overpass apres 1ere visite)
- Cache memoire par zone (acces ultra-rapide)

STEEVE-MAX: Aucun appel live apres le build initial du graphe.
ULTRA-MAX++: Cache persistant versionne SHA256, TTL 30 jours.
"""
import gzip
import json
import logging
import os
import time
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path

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

# ============================================================================
# CACHE PERSISTANT — ULTRA-MAX++ BCE-4X
# ============================================================================
PERSISTENT_CACHE_DIR = Path("/app/backend/data/terrain_cache")
CACHE_TTL_SECONDS = 30 * 24 * 3600  # 30 jours
CACHE_VERSION = "v1"

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


def _persistent_cache_path(lat: float, lng: float, radius_m: int) -> Path:
    """Chemin fichier cache persistant: {lat}_{lng}_{radius}.json.gz"""
    rlat = round(lat, 2)
    rlng = round(lng, 2)
    filename = f"{rlat}_{rlng}_{radius_m}_{CACHE_VERSION}.json.gz"
    return PERSISTENT_CACHE_DIR / filename


def _ensure_cache_dir():
    """Creer le repertoire de cache s'il n'existe pas."""
    PERSISTENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _save_persistent_cache(lat: float, lng: float, radius_m: int, result: Dict) -> bool:
    """
    Sauvegarder les donnees terrain dans le cache persistant (gzip JSON).
    Inclut metadata: SHA256, timestamp, version.
    """
    try:
        _ensure_cache_dir()
        filepath = _persistent_cache_path(lat, lng, radius_m)

        # Serialiser node_coords: convertir clefs int en str pour JSON
        serializable = _make_json_serializable(result)

        # Ajouter metadata
        payload = {
            "cache_version": CACHE_VERSION,
            "created_at": time.time(),
            "created_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "center_lat": round(lat, 2),
            "center_lng": round(lng, 2),
            "radius_m": radius_m,
            "data": serializable,
        }
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        payload["sha256"] = hashlib.sha256(raw).hexdigest()

        with gzip.open(filepath, "wt", encoding="utf-8", compresslevel=6) as f:
            json.dump(payload, f, separators=(",", ":"))

        size_kb = filepath.stat().st_size / 1024
        logger.info(
            f"[TNE-CACHE-PERSIST] SAVED: {filepath.name} ({size_kb:.1f} KB), "
            f"SHA256={payload['sha256'][:16]}..."
        )
        return True
    except Exception as e:
        logger.error(f"[TNE-CACHE-PERSIST] Save FAILED: {e}")
        return False


def _load_persistent_cache(lat: float, lng: float, radius_m: int) -> Optional[Dict]:
    """
    Charger les donnees terrain depuis le cache persistant.
    Valide TTL et version. Retourne None si invalide.
    """
    filepath = _persistent_cache_path(lat, lng, radius_m)
    if not filepath.exists():
        return None

    try:
        with gzip.open(filepath, "rt", encoding="utf-8") as f:
            payload = json.load(f)

        # Valider version
        if payload.get("cache_version") != CACHE_VERSION:
            logger.info(f"[TNE-CACHE-PERSIST] Version mismatch: {payload.get('cache_version')} != {CACHE_VERSION}")
            filepath.unlink(missing_ok=True)
            return None

        # Valider TTL
        created = payload.get("created_at", 0)
        age_s = time.time() - created
        if age_s > CACHE_TTL_SECONDS:
            age_days = age_s / 86400
            logger.info(f"[TNE-CACHE-PERSIST] TTL expired: {age_days:.1f} days > 30 days")
            filepath.unlink(missing_ok=True)
            return None

        # Valider SHA256
        stored_hash = payload.pop("sha256", None)
        verify_raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        computed_hash = hashlib.sha256(verify_raw).hexdigest()
        if stored_hash and stored_hash != computed_hash:
            logger.warning("[TNE-CACHE-PERSIST] SHA256 MISMATCH — cache corrompu, suppression")
            filepath.unlink(missing_ok=True)
            return None

        # Deserialiser: convertir clefs str back en int pour node_coords
        result = _restore_from_json(payload["data"])
        age_min = age_s / 60

        size_kb = filepath.stat().st_size / 1024
        logger.info(
            f"[TNE-CACHE-PERSIST] HIT: {filepath.name} ({size_kb:.1f} KB), "
            f"age={age_min:.0f}min, SHA256={computed_hash[:16]}..."
        )
        return result
    except Exception as e:
        logger.error(f"[TNE-CACHE-PERSIST] Load FAILED: {e}")
        return None


def _make_json_serializable(result: Dict) -> Dict:
    """Convertir node_coords (clefs int) en clefs string pour JSON."""
    out = {}
    for category in ("trails", "obstacles", "forest", "waterways", "clearings"):
        cat_data = result.get(category, {})
        nc = cat_data.get("node_coords", {})
        out[category] = {
            "node_coords": {str(k): list(v) for k, v in nc.items()},
            "ways": cat_data.get("ways", []),
        }
    for flag in ("has_trails", "has_obstacles", "has_forest", "has_waterways", "has_clearings"):
        out[flag] = result.get(flag, False)
    return out


def _restore_from_json(data: Dict) -> Dict:
    """Restaurer node_coords (clefs string → int) depuis JSON."""
    result = {
        "source": "persistent_cache",
    }
    for category in ("trails", "obstacles", "forest", "waterways", "clearings"):
        cat_data = data.get(category, {})
        nc_raw = cat_data.get("node_coords", {})
        nc = {int(k): tuple(v) for k, v in nc_raw.items()}
        result[category] = {
            "node_coords": nc,
            "ways": cat_data.get("ways", []),
        }
    for flag in ("has_trails", "has_obstacles", "has_forest", "has_waterways", "has_clearings"):
        result[flag] = data.get(flag, False)
    return result


def _adaptive_timeout(radius_m: int) -> int:
    """Timeout adaptatif selon le rayon de recherche."""
    return BASE_TIMEOUT_S + int(radius_m / 1000) * TIMEOUT_PER_KM


def _build_combined_query(lat: float, lng: float, radius_m: int) -> str:
    """Requete Overpass UNIQUE combinant chemins + obstacles + foret + clairières + cours d'eau."""
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
  way["natural"~"^(grassland|scrub|heath)$"](around:{radius_m},{lat},{lng});
  way["landuse"~"^(meadow|farmland|grass)$"](around:{radius_m},{lat},{lng});
);
out body;
>;
out skel qt;
"""


def _classify_ways(ways: list) -> dict:
    """Classer les ways par categorie: trails, obstacles, forest, waterways, clearings."""
    trails = []
    obstacles = []
    forest = []
    waterways = []
    clearings = []

    for way in ways:
        tags = way.get("tags", {})
        highway = tags.get("highway", "")
        natural = tags.get("natural", "")
        landuse = tags.get("landuse", "")
        waterway = tags.get("waterway", "")

        if highway in TRAIL_HIGHWAY_TAGS:
            trails.append(way)
        elif waterway:
            waterways.append(way)
        elif natural in ("water", "wetland"):
            obstacles.append(way)
        elif natural == "wood" or landuse == "forest":
            forest.append(way)
        elif natural in ("grassland", "scrub", "heath") or landuse in ("meadow", "farmland", "grass"):
            clearings.append(way)

    return {"trails": trails, "obstacles": obstacles, "forest": forest,
            "waterways": waterways, "clearings": clearings}


def _fetch_single_mirror(mirror: str, query: str, timeout_s: int) -> Optional[Dict]:
    """Fetch Overpass depuis un seul miroir. Retourne None en cas d'echec."""
    try:
        resp = requests.post(mirror, data={"data": query}, timeout=timeout_s + 5)
        if resp.status_code == 200:
            data = resp.json()
            elements = data.get("elements", [])
            logger.info(f"[TNE-SRC] Overpass OK: {len(elements)} elements from {mirror}")
            return data
        elif resp.status_code == 429:
            logger.warning(f"[TNE-SRC] Rate limited on {mirror}")
        elif resp.status_code >= 500:
            logger.warning(f"[TNE-SRC] Server error {resp.status_code} on {mirror}")
        else:
            logger.warning(f"[TNE-SRC] Unexpected {resp.status_code} from {mirror}")
    except requests.exceptions.Timeout:
        logger.warning(f"[TNE-SRC] Timeout on {mirror} ({timeout_s}s)")
    except Exception as e:
        logger.error(f"[TNE-SRC] Error on {mirror}: {e}")
    return None


def _fetch_overpass(query: str, timeout_s: int, max_retries: int = 3) -> Optional[Dict]:
    """
    BCE-4X P1 B2: Fetch Overpass en PARALLELE sur tous les miroirs.
    Le premier miroir a repondre avec succes gagne.
    """
    logger.info(f"[TNE-SRC] Launching parallel fetch on {len(OVERPASS_MIRRORS)} mirrors (timeout={timeout_s}s)")
    with ThreadPoolExecutor(max_workers=len(OVERPASS_MIRRORS)) as executor:
        futures = {
            executor.submit(_fetch_single_mirror, mirror, query, timeout_s): mirror
            for mirror in OVERPASS_MIRRORS
        }
        for future in as_completed(futures):
            mirror = futures[future]
            try:
                result = future.result()
                if result is not None:
                    logger.info(f"[TNE-SRC] Parallel winner: {mirror}")
                    return result
            except Exception as e:
                logger.error(f"[TNE-SRC] Future error for {mirror}: {e}")

    logger.error(f"[TNE-SRC] ALL {len(OVERPASS_MIRRORS)} parallel mirrors FAILED")
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

    Cascade de cache (priorite decroissante):
    1. Cache MEMOIRE (ultra-rapide, volatile)
    2. Cache PERSISTANT fichier gzip (survit aux redemarrages)
    3. Overpass API (appel reseau, sauvegarde dans les 2 caches)

    ZERO appel Overpass apres la premiere visite.
    Meteo/vent/contamination/scoring restent dynamiques.

    Retourne:
    {
        "trails": {"node_coords": {...}, "ways": [...]},
        "obstacles": {"node_coords": {...}, "ways": [...]},
        "forest": {"node_coords": {...}, "ways": [...]},
        "source": "cache" | "persistent_cache" | "overpass",
        "has_trails": bool,
        "has_obstacles": bool,
        "has_forest": bool,
    }
    """
    t0 = time.time()
    key = _zone_key(lat, lng, radius_m)

    # --- Niveau 1: Cache memoire ---
    if key in _source_cache:
        elapsed = (time.time() - t0) * 1000
        logger.info(f"[TNE-SRC] MEMORY Cache HIT for {key} ({elapsed:.1f}ms)")
        cached = _source_cache[key]
        cached["source"] = "cache"
        cached["cache_level"] = "memory"
        cached["fetch_ms"] = round(elapsed, 1)
        return cached

    # --- Niveau 2: Cache persistant fichier ---
    persistent = _load_persistent_cache(lat, lng, radius_m)
    if persistent is not None:
        elapsed = (time.time() - t0) * 1000
        persistent["cache_level"] = "persistent_file"
        persistent["fetch_ms"] = round(elapsed, 1)
        # Charger en memoire pour acces ultra-rapide suivant
        _source_cache[key] = persistent
        logger.info(f"[TNE-SRC] PERSISTENT Cache HIT for {key} ({elapsed:.1f}ms)")
        return persistent

    # --- Niveau 3: Overpass API (appel reseau) ---
    logger.info(f"[TNE-SRC] CACHE MISS — Fetching terrain data for ({lat:.4f}, {lng:.4f}), radius={radius_m}m")
    timeout = _adaptive_timeout(radius_m)

    result: Dict[str, Any] = {
        "trails": {"node_coords": {}, "ways": []},
        "obstacles": {"node_coords": {}, "ways": []},
        "forest": {"node_coords": {}, "ways": []},
        "waterways": {"node_coords": {}, "ways": []},
        "clearings": {"node_coords": {}, "ways": []},
        "source": "overpass",
        "has_trails": False,
        "has_obstacles": False,
        "has_forest": False,
        "has_waterways": False,
        "has_clearings": False,
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
        result["waterways"] = {"node_coords": nc, "ways": classified["waterways"]}
        result["clearings"] = {"node_coords": nc, "ways": classified["clearings"]}
        result["has_trails"] = len(classified["trails"]) > 0
        result["has_obstacles"] = len(classified["obstacles"]) > 0
        result["has_forest"] = len(classified["forest"]) > 0
        result["has_waterways"] = len(classified["waterways"]) > 0
        result["has_clearings"] = len(classified["clearings"]) > 0

        logger.info(
            f"[TNE-SRC] Combined fetch: {len(classified['trails'])} trails, "
            f"{len(classified['obstacles'])} obstacles, "
            f"{len(classified['forest'])} forest zones, "
            f"{len(classified['waterways'])} waterways, "
            f"{len(classified['clearings'])} clearings, "
            f"{len(nc)} total nodes"
        )

    elapsed = (time.time() - t0) * 1000
    result["cache_level"] = "overpass_fresh"
    result["fetch_ms"] = round(elapsed, 1)

    # Sauvegarder dans les 2 niveaux de cache
    _source_cache[key] = result
    _save_persistent_cache(lat, lng, radius_m, result)

    logger.info(f"[TNE-SRC] Overpass fetch + cache save: {elapsed:.0f}ms")
    return result
