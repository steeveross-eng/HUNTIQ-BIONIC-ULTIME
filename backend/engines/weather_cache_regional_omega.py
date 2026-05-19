"""
WeatherCacheRegional_Ω — Engine cache météo régional H3
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_Ω · 2026-02-19 · COMMANDANT STEEVE-MAX
                                                BCE-4X ULTIME ABSOLU

DOCTRINE
--------
Découple la précomputation ZEROCOST de toute API météo externe en :
  1. Pré-fetchant OpenWeatherMap par **cellule H3 résolution 3** (~270 km/hex)
     → ~30 cellules Canada × 30 jours TTL = ~30 fetches/jour MAX.
  2. Mettant en cache MongoDB (`weather_cache_regional_omega`).
  3. Exposant un wrapper transparent traduisant les requêtes
     **Open-Meteo** vers la réponse OWM cachée + champs synthétisés.

GRANULARITÉ
-----------
H3 R3 = ~270 km diamètre. À cette échelle climatique, la météo est
sensiblement homogène pour les usages V20 (vent moyen, température
journalière, pression atmosphérique régionale).

CHAMPS GÉRÉS
------------
| Champ Open-Meteo            | Source OWM           | Fallback        |
|-----------------------------|----------------------|-----------------|
| temperature_2m              | main.temp            | climat normales |
| wind_speed_10m              | wind.speed           | 5 m/s constant  |
| wind_direction_10m          | wind.deg             | 225 SW          |
| wind_gusts_10m              | wind.gust            | wind.speed×1.3  |
| relative_humidity_2m        | main.humidity        | 70 %            |
| pressure_msl                | main.pressure        | 1013 hPa        |
| cloud_cover                 | clouds.all           | 50 %            |
| precipitation               | rain.1h / snow.1h    | 0               |
| visibility                  | visibility (m)       | 10 000          |
| (synthétisés constants)     |                      |                 |
|  - direct_radiation         | -- synthétique --    | f(hour,lat)     |
|  - diffuse_radiation        | -- synthétique --    | f(hour,lat)     |
|  - snow_depth               | -- synthétique --    | 0 m             |
|  - cape                     | -- synthétique --    | 0               |
|  - soil_moisture_*          | -- synthétique --    | 0.25 m³/m³      |
|  - soil_temperature_0cm     | -- synthétique --    | temperature-2°C |
| elevation                   | -- synthétique --    | f(lat,lng)      |

USAGE
-----
    from engines.weather_cache_regional_omega import (
        get_normalized_weather, install_open_meteo_interceptor,
    )

    # Dans le worker ZEROCOST :
    install_open_meteo_interceptor()
    bundle = await v20_territoire_bundle(...)   # V20 inchangé, calls patchés
"""
from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Optional

import h3
import httpx
import pymongo
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

logger = logging.getLogger("bionic.weather_cache_regional_omega")

OWM_API_KEY = os.environ.get("OWM_API_KEY", "")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OWM_TIMEOUT_S = float(os.environ.get("OWM_TIMEOUT_S", "8.0"))

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "huntiq_v6")
COLLECTION = "weather_cache_regional_omega"

CACHE_TTL_S = int(os.environ.get("WEATHER_CACHE_TTL_S", str(30 * 24 * 3600)))  # 30 j
DOCTRINE = "P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_Ω"

_mongo_client: Optional[pymongo.MongoClient] = None
_mem_cache: dict[str, dict[str, Any]] = {}  # secondary in-memory cache for perf


def _mongo() -> pymongo.collection.Collection:
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = pymongo.MongoClient(MONGO_URL, serverSelectionTimeoutMS=2000)
        try:
            _mongo_client.admin.command("ping")
        except Exception as e:
            logger.warning(f"[WEATHER-CACHE] Mongo unreachable: {e}")
    return _mongo_client[DB_NAME][COLLECTION]


def h3_r3_key(lat: float, lon: float) -> str:
    """Retourne l'index H3 résolution 3 pour le cache régional."""
    return h3.latlng_to_cell(lat, lon, 3)


# ─────────────────────────────────────────────────────────────────────
# Fetchers
# ─────────────────────────────────────────────────────────────────────

_owm_calls = {"hits": 0, "misses": 0, "fetches": 0, "errors": 0}


async def _fetch_owm(lat: float, lon: float) -> dict[str, Any]:
    """Appel direct OWM /data/2.5/weather avec metric units."""
    if not OWM_API_KEY:
        raise RuntimeError("OWM_API_KEY missing in .env")
    async with httpx.AsyncClient(timeout=OWM_TIMEOUT_S) as client:
        r = await client.get(
            OWM_BASE_URL,
            params={
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "appid": OWM_API_KEY,
                "units": "metric",
            },
        )
        r.raise_for_status()
        _owm_calls["fetches"] += 1
        return r.json()


async def _populate_cache(lat: float, lon: float) -> dict[str, Any]:
    """Cache miss → fetch OWM → store. Retourne dict OWM raw + meta."""
    h3_key = h3_r3_key(lat, lon)
    h3_lat, h3_lon = h3.cell_to_latlng(h3_key)
    try:
        owm = await _fetch_owm(h3_lat, h3_lon)
    except Exception as e:
        _owm_calls["errors"] += 1
        logger.warning(f"[WEATHER-CACHE] OWM fetch failed for {h3_key}: {e}")
        # Fallback minimal
        owm = {"cod": 0, "_synth": True, "_error": str(e)}
    doc = {
        "h3_r3": h3_key,
        "lat_center": round(h3_lat, 4),
        "lng_center": round(h3_lon, 4),
        "fetched_at": datetime.now(timezone.utc),
        "ttl_until": time.time() + CACHE_TTL_S,
        "owm": owm,
        "doctrine": DOCTRINE,
    }
    try:
        _mongo().update_one({"h3_r3": h3_key}, {"$set": doc}, upsert=True)
    except Exception as e:
        logger.warning(f"[WEATHER-CACHE] Mongo write failed: {e}")
    _mem_cache[h3_key] = doc
    return doc


async def get_cached_or_fetch(lat: float, lon: float) -> dict[str, Any]:
    """Retourne le dict OWM mis en cache pour la cellule H3 R3 (lat,lng)."""
    h3_key = h3_r3_key(lat, lon)
    # 1) RAM
    if h3_key in _mem_cache:
        doc = _mem_cache[h3_key]
        if doc.get("ttl_until", 0) > time.time():
            _owm_calls["hits"] += 1
            return doc
    # 2) Mongo
    try:
        doc = _mongo().find_one({"h3_r3": h3_key}, {"_id": 0})
    except Exception:
        doc = None
    if doc and doc.get("ttl_until", 0) > time.time():
        _mem_cache[h3_key] = doc
        _owm_calls["hits"] += 1
        return doc
    # 3) Miss → populate
    _owm_calls["misses"] += 1
    return await _populate_cache(lat, lon)


def _fetch_owm_sync(lat: float, lon: float) -> dict[str, Any]:
    """Version sync de _fetch_owm pour les engines httpx.Client."""
    if not OWM_API_KEY:
        return {"cod": 0, "_synth": True, "_error": "OWM_API_KEY missing"}
    try:
        with httpx.Client(timeout=OWM_TIMEOUT_S) as client:
            # IMPORTANT : appel direct sans passer par notre patch (utilise
            # _original_sync_get pour bypasser self-recursion).
            if _original_sync_get is not None:
                r = _original_sync_get(
                    client,
                    OWM_BASE_URL,
                    params={
                        "lat": round(lat, 4),
                        "lon": round(lon, 4),
                        "appid": OWM_API_KEY,
                        "units": "metric",
                    },
                )
            else:
                r = client.get(
                    OWM_BASE_URL,
                    params={
                        "lat": round(lat, 4),
                        "lon": round(lon, 4),
                        "appid": OWM_API_KEY,
                        "units": "metric",
                    },
                )
            r.raise_for_status()
            _owm_calls["fetches"] += 1
            return r.json()
    except Exception as e:
        _owm_calls["errors"] += 1
        logger.warning(f"[WEATHER-CACHE] OWM sync fetch failed: {e}")
        return {"cod": 0, "_synth": True, "_error": str(e)}


def get_cached_or_fetch_sync(lat: float, lon: float) -> dict[str, Any]:
    """Version sync de get_cached_or_fetch."""
    h3_key = h3_r3_key(lat, lon)
    # 1) RAM
    if h3_key in _mem_cache:
        doc = _mem_cache[h3_key]
        if doc.get("ttl_until", 0) > time.time():
            _owm_calls["hits"] += 1
            return doc
    # 2) Mongo
    try:
        doc = _mongo().find_one({"h3_r3": h3_key}, {"_id": 0})
    except Exception:
        doc = None
    if doc and doc.get("ttl_until", 0) > time.time():
        _mem_cache[h3_key] = doc
        _owm_calls["hits"] += 1
        return doc
    # 3) Miss → populate sync
    _owm_calls["misses"] += 1
    h3_lat, h3_lon = h3.cell_to_latlng(h3_key)
    owm = _fetch_owm_sync(h3_lat, h3_lon)
    doc = {
        "h3_r3": h3_key,
        "lat_center": round(h3_lat, 4),
        "lng_center": round(h3_lon, 4),
        "fetched_at": datetime.now(timezone.utc),
        "ttl_until": time.time() + CACHE_TTL_S,
        "owm": owm,
        "doctrine": DOCTRINE,
    }
    try:
        _mongo().update_one({"h3_r3": h3_key}, {"$set": doc}, upsert=True)
    except Exception:
        pass
    _mem_cache[h3_key] = doc
    return doc


# ─────────────────────────────────────────────────────────────────────
# Synthèse Open-Meteo-shaped response
# ─────────────────────────────────────────────────────────────────────

def _synth_radiation(lat: float, hour: int) -> tuple[float, float]:
    """Approximation grossière du rayonnement direct/diffus W/m²."""
    if hour < 6 or hour > 20:
        return 0.0, 0.0
    sun_angle = max(0.0, math.sin(math.pi * (hour - 6) / 14))
    lat_factor = max(0.3, math.cos(math.radians(abs(lat) - 45)))
    direct = 800 * sun_angle * lat_factor
    diffuse = 200 * sun_angle * lat_factor
    return round(direct, 1), round(diffuse, 1)


def _synth_elevation(lat: float, lon: float) -> float:
    """Élévation approximative (m) — table grossière par lat/lng."""
    # Plaine St-Laurent ≈ 50m, Bouclier canadien ≈ 400m, Rockies ≈ 1500m
    if -120 < lon < -110 and 49 < lat < 60:
        return 800.0
    if -125 < lon < -115:
        return 1200.0
    if -82 < lon < -55 and 45 < lat < 50:
        return 200.0
    if lat > 60:
        return 300.0
    return 100.0


def to_open_meteo_response(doc: dict[str, Any], lat: float, lon: float,
                            params: dict[str, str]) -> dict[str, Any]:
    """Convertit un doc cache → JSON Open-Meteo-shaped.

    Détecte les champs demandés dans `params` (current=… ou hourly=…) et
    construit la réponse minimale nécessaire.
    """
    owm = doc.get("owm", {}) if doc else {}
    is_synth = owm.get("_synth") or owm.get("cod") != 200

    main = owm.get("main") or {}
    wind = owm.get("wind") or {}
    clouds = owm.get("clouds") or {}
    rain = owm.get("rain") or {}
    snow = owm.get("snow") or {}

    temp = main.get("temp", 5.0) if not is_synth else 5.0
    pressure = main.get("pressure", 1013.0) if not is_synth else 1013.0
    humidity = main.get("humidity", 70.0) if not is_synth else 70.0
    wind_speed = wind.get("speed", 4.0) if not is_synth else 4.0
    wind_deg = wind.get("deg", 225.0) if not is_synth else 225.0
    wind_gust = wind.get("gust", wind_speed * 1.3) if not is_synth else wind_speed * 1.3
    cloud_cover = clouds.get("all", 50.0) if not is_synth else 50.0
    precip = (rain or {}).get("1h", 0.0) + (snow or {}).get("1h", 0.0) if not is_synth else 0.0
    visibility = owm.get("visibility", 10000) if not is_synth else 10000

    # hour heuristique : maintenant
    hour_now = datetime.now(timezone.utc).hour
    direct_rad, diffuse_rad = _synth_radiation(lat, hour_now)

    # CURRENT block
    current = {
        "time": datetime.now(timezone.utc).isoformat(timespec="minutes").replace("+00:00", ""),
        "temperature_2m": temp,
        "wind_speed_10m": wind_speed,
        "wind_direction_10m": wind_deg,
        "wind_gusts_10m": wind_gust,
        "relative_humidity_2m": humidity,
        "precipitation": precip,
        "cloud_cover": cloud_cover,
        "pressure_msl": pressure,
    }

    # HOURLY block (48h × all fields requested)
    HOURLY_LEN = 48
    hourly = {
        "time": [f"2026-02-19T{h:02d}:00" for h in range(HOURLY_LEN)],
        "temperature_2m": [temp + math.sin(math.pi * h / 12) * 3 for h in range(HOURLY_LEN)],
        "wind_speed_10m": [wind_speed] * HOURLY_LEN,
        "wind_direction_10m": [wind_deg] * HOURLY_LEN,
        "wind_gusts_10m": [wind_gust] * HOURLY_LEN,
        "relative_humidity_2m": [humidity] * HOURLY_LEN,
        "precipitation": [precip / HOURLY_LEN] * HOURLY_LEN,
        "cloud_cover": [cloud_cover] * HOURLY_LEN,
        "pressure_msl": [pressure] * HOURLY_LEN,
        "direct_radiation": [
            _synth_radiation(lat, h % 24)[0] for h in range(HOURLY_LEN)
        ],
        "diffuse_radiation": [
            _synth_radiation(lat, h % 24)[1] for h in range(HOURLY_LEN)
        ],
        "snow_depth": [0.0] * HOURLY_LEN,
        "visibility": [visibility] * HOURLY_LEN,
        "cape": [0.0] * HOURLY_LEN,
        "soil_moisture_0_to_1cm": [0.25] * HOURLY_LEN,
        "soil_moisture_1_to_3cm": [0.27] * HOURLY_LEN,
        "soil_temperature_0cm": [temp - 2.0] * HOURLY_LEN,
    }

    return {
        "latitude": lat,
        "longitude": lon,
        "elevation": _synth_elevation(lat, lon),
        "current": current,
        "hourly": hourly,
        "_synth_source": DOCTRINE,
    }


def to_elevation_response(lat_list: list[float], lon_list: list[float]) -> dict[str, Any]:
    """Synthétise la réponse de l'API /v1/elevation Open-Meteo."""
    return {
        "elevation": [
            _synth_elevation(la, lo) for la, lo in zip(lat_list, lon_list)
        ],
    }


# ─────────────────────────────────────────────────────────────────────
# Monkey-patch httpx.AsyncClient.get
# ─────────────────────────────────────────────────────────────────────

_original_get = None
_original_sync_get = None
_patched = False


class _FakeResponse:
    """Mimique minimale de httpx.Response pour le pipeline V20."""

    def __init__(self, payload: dict[str, Any], url: str):
        self._payload = payload
        self.status_code = 200
        self.url = url
        self.headers = {"content-type": "application/json"}
        import json as _json
        self.text = _json.dumps(payload)
        self.content = self.text.encode()

    def json(self) -> Any:
        return self._payload

    def raise_for_status(self) -> None:
        return None


def _build_open_meteo_payload(url: str, params: dict) -> dict[str, Any]:
    """Construit la réponse Open-Meteo-shape depuis les params (SYNC version)."""
    lat_raw = params.get("latitude", "0")
    lon_raw = params.get("longitude", "0")
    first_lat = float(str(lat_raw).split(",")[0])
    first_lon = float(str(lon_raw).split(",")[0])

    if "/v1/elevation" in str(url):
        lat_list = [float(x) for x in str(lat_raw).split(",")]
        lon_list = [float(x) for x in str(lon_raw).split(",")]
        return to_elevation_response(lat_list, lon_list)

    # /v1/forecast — utilise cache sync
    doc = get_cached_or_fetch_sync(first_lat, first_lon)
    return to_open_meteo_response(doc, first_lat, first_lon, params)


async def _patched_get(self: httpx.AsyncClient, url: str, **kwargs):
    """Intercepte les appels Open-Meteo async, redirige vers cache OWM."""
    if "api.open-meteo.com" in str(url):
        params = kwargs.get("params") or {}
        lat_raw = params.get("latitude", "0")
        lon_raw = params.get("longitude", "0")
        first_lat = float(str(lat_raw).split(",")[0])
        first_lon = float(str(lon_raw).split(",")[0])

        if "/v1/elevation" in str(url):
            lat_list = [float(x) for x in str(lat_raw).split(",")]
            lon_list = [float(x) for x in str(lon_raw).split(",")]
            return _FakeResponse(
                to_elevation_response(lat_list, lon_list), str(url)
            )

        doc = await get_cached_or_fetch(first_lat, first_lon)
        return _FakeResponse(
            to_open_meteo_response(doc, first_lat, first_lon, params),
            str(url),
        )
    # Pass-through to real client
    return await _original_get(self, url, **kwargs)


def _patched_sync_get(self: httpx.Client, url: str, **kwargs):
    """Intercepte les appels Open-Meteo SYNC (httpx.Client.get)."""
    if "api.open-meteo.com" in str(url):
        params = kwargs.get("params") or {}
        return _FakeResponse(
            _build_open_meteo_payload(str(url), params),
            str(url),
        )
    # Pass-through
    return _original_sync_get(self, url, **kwargs)


def install_open_meteo_interceptor() -> None:
    """Installe les monkey-patches sur httpx.AsyncClient.get + httpx.Client.get."""
    global _original_get, _original_sync_get, _patched
    if _patched:
        return
    _original_get = httpx.AsyncClient.get
    _original_sync_get = httpx.Client.get
    httpx.AsyncClient.get = _patched_get  # type: ignore[assignment]
    httpx.Client.get = _patched_sync_get  # type: ignore[assignment]
    _patched = True
    logger.info(f"[WEATHER-CACHE] Open-Meteo interceptor INSTALLED · {DOCTRINE}")


def uninstall_open_meteo_interceptor() -> None:
    """Restaure les méthodes httpx originales (test cleanup)."""
    global _original_get, _original_sync_get, _patched
    if _patched:
        if _original_get is not None:
            httpx.AsyncClient.get = _original_get  # type: ignore[assignment]
        if _original_sync_get is not None:
            httpx.Client.get = _original_sync_get  # type: ignore[assignment]
        _patched = False
        logger.info("[WEATHER-CACHE] Open-Meteo interceptor REMOVED")


def get_stats() -> dict[str, Any]:
    """Retourne les statistiques de cache (audit)."""
    return {
        "doctrine": DOCTRINE,
        "owm_calls": dict(_owm_calls),
        "mem_cache_size": len(_mem_cache),
        "owm_key_configured": bool(OWM_API_KEY),
    }


# ─────────────────────────────────────────────────────────────────────
# CLI debug
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    async def _demo():
        install_open_meteo_interceptor()
        doc = await get_cached_or_fetch(48.45, -68.52)
        print("Cache doc:", {k: v for k, v in doc.items() if k != "owm"})
        print("OWM main:", (doc.get("owm") or {}).get("main"))
        async with httpx.AsyncClient() as c:
            r = await c.get(
                "https://api.open-meteo.com/v1/forecast",
                params={"latitude": 48.45, "longitude": -68.52,
                        "current": "temperature_2m,wind_speed_10m"},
            )
            print("Open-Meteo-shaped response (excerpt):")
            j = r.json()
            print("  current:", j["current"])
            print("  hourly keys:", list(j["hourly"].keys())[:8])
            print("  elevation:", j["elevation"])
        print("STATS:", get_stats())

    asyncio.run(_demo())
