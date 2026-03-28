"""
Weather Engine v3 — BCE-4X / STEEVE-MAX
========================================
Moteur meteorologique avance pour BIONIC.

Fonctionnalites v3:
  - Donnees enrichies (rafales, humidite, pression, visibilite, point de rosee, UV)
  - Prevision courte duree (nowcasting 3h)
  - Normalisation des unites
  - Scoring meteo intelligent multi-criteres
  - Source unique pour TERRITOIRE, SUPRA, INTELLIGENCE, COMMANDER

Endpoint: /api/v3/weather
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone
import httpx
import logging
import math

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/weather", tags=["weather-v3"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Scoring weights for hunting conditions
HUNTING_WEATHER_WEIGHTS = {
    "wind": 0.30,
    "pressure": 0.20,
    "temperature": 0.15,
    "humidity": 0.10,
    "cloud_cover": 0.10,
    "precipitation": 0.15,
}


def _dew_point(temp_c, humidity_pct):
    """Calcul du point de rosee (Magnus formula)."""
    if temp_c is None or humidity_pct is None:
        return None
    a, b = 17.27, 237.7
    alpha = (a * temp_c) / (b + temp_c) + math.log(max(humidity_pct, 1) / 100.0)
    return round((b * alpha) / (a - alpha), 1)


def _score_wind(speed_kmh, gusts_kmh):
    """Score vent pour la chasse (0-100)."""
    s = speed_kmh or 0
    g = gusts_kmh or 0
    # Vent leger (5-15 km/h) = optimal pour disperser l'odeur
    if 5 <= s <= 15 and g < 30:
        return 90
    if s < 5:
        return 70  # Trop calme, odeur stagnante
    if s <= 25:
        return 60
    if s <= 35:
        return 35
    return 15  # Tempete


def _score_pressure(hpa):
    """Score pression (0-100). Hausse = activite animale accrue."""
    if hpa is None:
        return 50
    if hpa >= 1020:
        return 90  # Haute pression = excellent
    if hpa >= 1010:
        return 75
    if hpa >= 1000:
        return 55
    return 35  # Basse pression = faible activite


def _score_temperature(temp_c, month):
    """Score temperature (0-100). Varie selon la saison."""
    if temp_c is None:
        return 50
    # Automne/hiver (sept-mars): froid = bon
    if month in [9, 10, 11, 12, 1, 2, 3]:
        if -5 <= temp_c <= 5:
            return 90
        if -10 <= temp_c <= 10:
            return 70
        return 40
    # Printemps/ete: tempere = bon
    if 10 <= temp_c <= 22:
        return 80
    return 50


def _score_humidity(pct):
    """Score humidite (0-100)."""
    if pct is None:
        return 50
    if 40 <= pct <= 70:
        return 85
    if 30 <= pct <= 85:
        return 65
    return 40


def _score_cloud_cover(pct):
    """Score couverture nuageuse (0-100)."""
    if pct is None:
        return 50
    if 30 <= pct <= 70:
        return 85  # Partiellement nuageux = optimal
    if pct < 30:
        return 65  # Ciel clair
    return 50  # Tres nuageux


def _score_precipitation(mm):
    """Score precipitations (0-100)."""
    if mm is None:
        return 70
    if mm == 0:
        return 90
    if mm < 1:
        return 70  # Bruine legere
    if mm < 5:
        return 40
    return 15  # Forte pluie


def _compute_hunting_score(data, month):
    """Score meteo intelligent multi-criteres pour la chasse."""
    wind_score = _score_wind(data.get("wind_speed_kmh"), data.get("wind_gust_kmh"))
    pressure_score = _score_pressure(data.get("pressure_hpa"))
    temp_score = _score_temperature(data.get("temperature_c"), month)
    humidity_score = _score_humidity(data.get("humidity_pct"))
    cloud_score = _score_cloud_cover(data.get("cloud_cover_pct"))
    precip_score = _score_precipitation(data.get("precipitation_mm"))

    weighted = (
        wind_score * HUNTING_WEATHER_WEIGHTS["wind"]
        + pressure_score * HUNTING_WEATHER_WEIGHTS["pressure"]
        + temp_score * HUNTING_WEATHER_WEIGHTS["temperature"]
        + humidity_score * HUNTING_WEATHER_WEIGHTS["humidity"]
        + cloud_score * HUNTING_WEATHER_WEIGHTS["cloud_cover"]
        + precip_score * HUNTING_WEATHER_WEIGHTS["precipitation"]
    )

    return {
        "overall": round(weighted, 1),
        "components": {
            "wind": wind_score,
            "pressure": pressure_score,
            "temperature": temp_score,
            "humidity": humidity_score,
            "cloud_cover": cloud_score,
            "precipitation": precip_score,
        },
        "label": (
            "Exceptionnel" if weighted >= 80 else
            "Excellent" if weighted >= 65 else
            "Bon" if weighted >= 50 else
            "Modere" if weighted >= 35 else
            "Defavorable"
        ),
    }


@router.get("/current")
async def get_current_weather(
    lat: float = Query(...),
    lng: float = Query(...),
):
    """Donnees meteo actuelles enrichies (v3)."""
    try:
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": ",".join([
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "precipitation", "weather_code", "cloud_cover", "surface_pressure",
                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
                "visibility", "uv_index",
            ]),
            "daily": "sunrise,sunset",
            "timezone": "America/Toronto",
            "forecast_days": 1,
        }
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
            raw = resp.json()

        c = raw.get("current", {})
        d = raw.get("daily", {})
        month = datetime.now(timezone.utc).month

        data = {
            "temperature_c": c.get("temperature_2m"),
            "apparent_temperature_c": c.get("apparent_temperature"),
            "humidity_pct": c.get("relative_humidity_2m"),
            "pressure_hpa": c.get("surface_pressure"),
            "wind_speed_kmh": c.get("wind_speed_10m"),
            "wind_direction_deg": c.get("wind_direction_10m"),
            "wind_gust_kmh": c.get("wind_gusts_10m"),
            "precipitation_mm": c.get("precipitation"),
            "cloud_cover_pct": c.get("cloud_cover"),
            "weather_code": c.get("weather_code"),
            "visibility_m": c.get("visibility"),
            "uv_index": c.get("uv_index"),
            "dew_point_c": _dew_point(c.get("temperature_2m"), c.get("relative_humidity_2m")),
            "sunrise": d.get("sunrise", [None])[0],
            "sunset": d.get("sunset", [None])[0],
        }

        data["hunting_score"] = _compute_hunting_score(data, month)
        data["engine_version"] = "v3"
        data["timestamp"] = datetime.now(timezone.utc).isoformat()

        return data

    except Exception as e:
        logger.error(f"[Weather v3] Error: {e}")
        return {"error": str(e), "engine_version": "v3"}


@router.get("/nowcast")
async def get_nowcast(
    lat: float = Query(...),
    lng: float = Query(...),
):
    """Prevision courte duree (nowcasting 3h, pas de 15min)."""
    try:
        params = {
            "latitude": lat,
            "longitude": lng,
            "minutely_15": ",".join([
                "temperature_2m", "precipitation", "wind_speed_10m",
                "wind_direction_10m", "wind_gusts_10m",
            ]),
            "timezone": "America/Toronto",
            "forecast_days": 1,
        }
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
            raw = resp.json()

        m15 = raw.get("minutely_15", {})
        times = m15.get("time", [])
        month = datetime.now(timezone.utc).month

        # Extract next 3h (12 intervals of 15min)
        nowcast = []
        for i in range(min(12, len(times))):
            point = {
                "time": times[i],
                "temperature_c": (m15.get("temperature_2m") or [])[i] if i < len(m15.get("temperature_2m") or []) else None,
                "precipitation_mm": (m15.get("precipitation") or [])[i] if i < len(m15.get("precipitation") or []) else None,
                "wind_speed_kmh": (m15.get("wind_speed_10m") or [])[i] if i < len(m15.get("wind_speed_10m") or []) else None,
                "wind_direction_deg": (m15.get("wind_direction_10m") or [])[i] if i < len(m15.get("wind_direction_10m") or []) else None,
                "wind_gust_kmh": (m15.get("wind_gusts_10m") or [])[i] if i < len(m15.get("wind_gusts_10m") or []) else None,
            }
            nowcast.append(point)

        return {
            "nowcast": nowcast,
            "count": len(nowcast),
            "engine_version": "v3",
        }

    except Exception as e:
        logger.error(f"[Weather v3 nowcast] Error: {e}")
        return {"error": str(e), "engine_version": "v3"}


@router.get("/hunting-score")
async def get_hunting_score(
    lat: float = Query(...),
    lng: float = Query(...),
):
    """Score meteo intelligent pour la chasse."""
    current = await get_current_weather(lat, lng)
    if "error" in current:
        return current
    return {
        "hunting_score": current.get("hunting_score"),
        "conditions": {
            "temperature_c": current.get("temperature_c"),
            "wind_speed_kmh": current.get("wind_speed_kmh"),
            "pressure_hpa": current.get("pressure_hpa"),
        },
        "engine_version": "v3",
    }



# ============================================================
# BCE-4X P0: WIND GRID ENDPOINT — Champ de vent griddé
# ============================================================

from engines.weather_v3.wind_model_provider import get_wind_provider

# Cache simple en mémoire pour le windgrid (clé = bounds arrondies)
_windgrid_cache = {}
_CACHE_TTL_SECONDS = 600  # 10 min


@router.get("/windgrid")
async def get_wind_grid(
    south: float = Query(..., description="Latitude sud du viewport"),
    north: float = Query(..., description="Latitude nord du viewport"),
    west: float = Query(..., description="Longitude ouest du viewport"),
    east: float = Query(..., description="Longitude est du viewport"),
    resolution: float = Query(0.25, description="Résolution en degrés (paramétrable)"),
    provider: str = Query("open-meteo", description="Fournisseur de données vent"),
):
    """
    Retourne un champ de vent griddé couvrant le viewport demandé.
    Format normalisé indépendant du fournisseur.
    
    Le frontend utilise ce champ pour l'interpolation bilinéaire
    des particules terrain-lockées.
    """
    import time

    # Arrondir les bounds pour le cache (éviter trop de requêtes)
    cache_res = max(resolution, 0.1)
    cache_key = (
        round(south / cache_res) * cache_res,
        round(north / cache_res) * cache_res,
        round(west / cache_res) * cache_res,
        round(east / cache_res) * cache_res,
        resolution,
        provider,
    )

    now = time.time()
    if cache_key in _windgrid_cache:
        cached_time, cached_data = _windgrid_cache[cache_key]
        if now - cached_time < _CACHE_TTL_SECONDS:
            return cached_data

    try:
        wind_provider = get_wind_provider(provider)

        # Ajouter une marge de 20% pour couvrir les bords
        lat_margin = (north - south) * 0.2
        lng_margin = (east - west) * 0.2

        grid_data = await wind_provider.fetch_wind_grid(
            south=south - lat_margin,
            north=north + lat_margin,
            west=west - lng_margin,
            east=east + lng_margin,
            resolution_deg=resolution,
        )

        result = grid_data.to_dict()
        _windgrid_cache[cache_key] = (now, result)

        # Nettoyer les anciennes entrées du cache
        expired = [k for k, (t, _) in _windgrid_cache.items() if now - t > _CACHE_TTL_SECONDS * 2]
        for k in expired:
            del _windgrid_cache[k]

        return result

    except Exception as e:
        logger.error(f"WindGrid fetch error ({provider}): {e}")
        return {
            "error": str(e),
            "provider": provider,
            "fallback": True,
            "grid": None,
        }
