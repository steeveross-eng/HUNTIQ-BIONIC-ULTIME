"""
OSM Trails — Recuperation graphe sentiers OSM via Overpass API
PROTOCOLE BIONIC GOLDEN — Pipeline unique acces aux affuts V6
"""
import json
import gzip
import hashlib
import logging
import os
import time
from pathlib import Path

import httpx

logger = logging.getLogger("access_engine_v6.osm_trails")

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL_SECONDS = 30 * 24 * 3600  # 30 jours

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HIGHWAY_TYPES = {
    "path": {"cost_mult": 1.0, "label": "Sentier"},
    "track": {"cost_mult": 1.0, "label": "Chemin forestier"},
    "footway": {"cost_mult": 1.2, "label": "Sentier pieton"},
    "unclassified": {"cost_mult": 1.5, "label": "Route non classee"},
    "service": {"cost_mult": 1.5, "label": "Route de service"},
    "secondary": {"cost_mult": 2.0, "label": "Route secondaire"},
    "tertiary": {"cost_mult": 1.8, "label": "Route tertiaire"},
    "residential": {"cost_mult": 2.5, "label": "Route residentielle"},
}

RAILWAY_ADMITTED = {"abandoned", "disused"}


def _cache_key(lat: float, lng: float, radius_m: int) -> str:
    raw = f"trail_graph_{lat:.4f}_{lng:.4f}_{radius_m}"
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json.gz"


def load_cached_trail_graph(lat: float, lng: float, radius_m: int):
    key = _cache_key(lat, lng, radius_m)
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        mtime = path.stat().st_mtime
        if time.time() - mtime > CACHE_TTL_SECONDS:
            return None
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
        return None


def save_trail_graph_cache(lat: float, lng: float, radius_m: int, data: dict):
    key = _cache_key(lat, lng, radius_m)
    path = _cache_path(key)
    try:
        with gzip.open(path, "wt", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        logger.warning(f"Cache write error: {e}")


async def fetch_osm_trails(lat: float, lng: float, radius_m: int = 3000) -> dict:
    """
    Recupere le reseau de sentiers OSM autour d'un point.
    Retourne un graphe {nodes: [...], edges: [...]} pour le routage.
    """
    cached = load_cached_trail_graph(lat, lng, radius_m)
    if cached:
        logger.info(f"Trail graph cache HIT: {lat:.4f},{lng:.4f} r={radius_m}m")
        return cached

    highway_filter = "|".join(HIGHWAY_TYPES.keys())
    query = f"""
    [out:json][timeout:25];
    (
      way["highway"~"^({highway_filter})$"](around:{radius_m},{lat},{lng});
      way["railway"~"^(abandoned|disused)$"](around:{radius_m},{lat},{lng});
    );
    out body;
    >;
    out skel qt;
    """

    nodes = {}
    edges = []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(OVERPASS_URL, data={"data": query})
            resp.raise_for_status()
            data = resp.json()

        for el in data.get("elements", []):
            if el["type"] == "node":
                nodes[el["id"]] = {"lat": el["lat"], "lng": el["lon"]}
            elif el["type"] == "way":
                tags = el.get("tags", {})
                hw = tags.get("highway", tags.get("railway", "path"))
                hw_info = HIGHWAY_TYPES.get(hw, {"cost_mult": 2.0, "label": hw})
                node_ids = el.get("nodes", [])
                surface = tags.get("surface", "unknown")
                name = tags.get("name", "")

                for i in range(len(node_ids) - 1):
                    n1, n2 = node_ids[i], node_ids[i + 1]
                    if n1 in nodes and n2 in nodes:
                        p1, p2 = nodes[n1], nodes[n2]
                        dist = _haversine(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
                        edges.append({
                            "from": n1, "to": n2,
                            "distance_m": round(dist, 1),
                            "highway_type": hw,
                            "cost_mult": hw_info["cost_mult"],
                            "surface": surface,
                            "name": name,
                            "label": hw_info["label"],
                        })

        logger.info(f"OSM trails fetched: {len(nodes)} nodes, {len(edges)} edges for {lat:.4f},{lng:.4f}")
    except Exception as e:
        logger.error(f"Overpass API error: {e}")

    result = {
        "nodes": {str(k): v for k, v in nodes.items()},
        "edges": edges,
        "meta": {"lat": lat, "lng": lng, "radius_m": radius_m, "ts": time.time()},
    }

    save_trail_graph_cache(lat, lng, radius_m, result)
    return result


def _haversine(lat1, lng1, lat2, lng2):
    import math
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
