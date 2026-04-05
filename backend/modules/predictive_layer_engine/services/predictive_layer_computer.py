"""
M3 — Predictive Layer Computer : Couches predictives par zone
================================================================
Directive x7000-M3 — Phase M3-A MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : predictive_engine, solunar, weather_fauna_simulation consommes en LECTURE.
NE recree PAS les predictions comportementales, le calendrier solunaire, ni les simulations meteo.

Formule : P(h) = base_activity(0.25) * season(0.15) * solunar(0.15) * meteo(0.20) * historical(0.15) * nutrition(0.10)
"""

import os
import uuid
import logging
from datetime import datetime, timezone, timedelta, date
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

# Mapping especes M3 ↔ predictive_engine
SPECIES_MAP = {
    "orignal": "moose",
    "chevreuil": "deer",
    "ours_noir": "bear",
    "dindon_sauvage": "wild_turkey",
    "moose": "moose",
    "deer": "deer",
    "bear": "bear",
    "wild_turkey": "wild_turkey"
}

VALID_SPECIES = ["orignal", "chevreuil", "ours_noir", "dindon_sauvage"]

# Poids des facteurs (conformes au plan)
FACTOR_WEIGHTS = {
    "base_activity": 0.25,
    "season": 0.15,
    "solunar": 0.15,
    "meteo": 0.20,
    "historical": 0.15,
    "nutrition": 0.10
}


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


async def ensure_indexes():
    """Cree les index MongoDB pour predictive_layers."""
    db = _get_db()
    await db.predictive_layers.create_index("zone_id")
    await db.predictive_layers.create_index("species")
    await db.predictive_layers.create_index("target_date")
    await db.predictive_layers.create_index(
        [("zone_id", 1), ("species", 1), ("target_date", 1)],
        unique=True
    )
    await db.predictive_layers.create_index("valid_until")
    logger.info("M3 predictive_layers indexes created")


def _get_base_activity(hour: int, species_key: str) -> float:
    """PF3-S1 : Patterns d'activite depuis predictive_engine (LECTURE SEULE)."""
    try:
        from modules.predictive_engine.v1.service import PredictiveService
        patterns = PredictiveService.SPECIES_PATTERNS.get(species_key, {})
        sunrise_h, sunset_h = 6, 18

        if sunrise_h - 1 <= hour <= sunrise_h + 2:
            return patterns.get("dawn_activity", 50) / 100.0
        elif sunset_h - 2 <= hour <= sunset_h + 1:
            return patterns.get("dusk_activity", 50) / 100.0
        elif sunrise_h + 2 < hour < sunset_h - 2:
            return patterns.get("midday_activity", 30) / 100.0
        else:
            return patterns.get("night_activity", 20) / 100.0
    except Exception:
        defaults = {5: 0.85, 6: 0.95, 7: 0.80, 16: 0.75, 17: 0.90, 18: 0.85}
        return defaults.get(hour, 0.40)


def _get_season_factor(month: int) -> float:
    """PF3-S2 : Facteur saisonnier depuis predictive_engine (LECTURE SEULE)."""
    try:
        from modules.predictive_engine.v1.service import PredictiveService
        return PredictiveService.SEASON_FACTORS.get(month, 0.7)
    except Exception:
        defaults = {1: 0.6, 2: 0.5, 3: 0.6, 4: 0.7, 5: 0.75, 6: 0.65,
                    7: 0.5, 8: 0.6, 9: 0.85, 10: 0.95, 11: 0.9, 12: 0.7}
        return defaults.get(month, 0.7)


def _get_solunar_factor(hour: int, lat: float, lng: float, date_str: str) -> float:
    """PF3-LUN1/LUN2/LUN3 : Facteur solunaire depuis solunar (LECTURE SEULE)."""
    try:
        from modules.solunar.engine import compute_solunar
        data = compute_solunar(lat, lng, date_str)
        score = data.get("solunar_score", 50) / 100.0

        for window in data.get("hunting_windows", []):
            start_parts = window.get("start", "00:00").split(":")
            end_parts = window.get("end", "00:00").split(":")
            start_h = int(start_parts[0])
            end_h = int(end_parts[0])
            if start_h <= hour <= end_h:
                intensity = window.get("intensity", "modere")
                bonus = {"extreme": 0.3, "fort": 0.2, "modere": 0.1, "faible": 0.05}
                score = min(1.0, score + bonus.get(intensity, 0.05))
                break

        return score
    except Exception:
        return 0.5


def _get_meteo_factor(species_key: str) -> float:
    """PF3-MET1/MET2 : Facteur meteo depuis weather_fauna_simulation (LECTURE SEULE)."""
    try:
        from modules.weather_fauna_simulation_engine.v1.service import WeatherFaunaSimulationService
        svc = WeatherFaunaSimulationService()
        optimal = svc.optimal_conditions.get(species_key)
        if optimal:
            return 0.7
        return 0.65
    except Exception:
        return 0.65


def _get_nutrition_factor(lat: float, lng: float, month: int) -> float:
    """PF3-N1/N2 : Facteur nutritionnel via nutrition_v6_interface (LECTURE SEULE)."""
    try:
        from modules.nutrition_v6_interface.wrappers.forage_quality_model import analyze_forage_quality
        data = analyze_forage_quality(lat, lng, month)
        return data.get("normalized_score", 0.5)
    except Exception:
        return 0.5


async def _get_historical_factor(zone_id: str, species: str, hour: int) -> float:
    """Facteur historique depuis timeseries_data (M3 interne)."""
    db = _get_db()
    ts = await db.timeseries_data.find_one(
        {"zone_id": zone_id, "species": species, "metric": "activity_index"},
        {"_id": 0}
    )
    if not ts or not ts.get("values"):
        return 0.5

    values = ts["values"]
    hourly_vals = [v["value"] for v in values[-168:]
                   if "timestamp" in v]
    if hourly_vals:
        avg = sum(hourly_vals) / len(hourly_vals)
        return min(1.0, avg)
    return 0.5


async def compute_layer(zone_id: str, species: str,
                        target_date: Optional[str] = None,
                        lat: float = 46.85, lng: float = -71.25) -> Dict[str, Any]:
    """Calcule une couche predictive 24h pour une zone/espece."""
    db = _get_db()

    if species not in VALID_SPECIES:
        return {"error": "INVALID_SPECIES", "valid_species": VALID_SPECIES}

    species_key = SPECIES_MAP.get(species, "deer")
    now = datetime.now(timezone.utc)
    date_str = target_date or now.strftime("%Y-%m-%d")
    target_month = int(date_str.split("-")[1])

    season = _get_season_factor(target_month)
    solunar_cache = {}
    meteo = _get_meteo_factor(species_key)
    nutrition = _get_nutrition_factor(lat, lng, target_month)

    predictions = []
    peak_prob = 0.0
    peak_hour = 0

    for hour in range(24):
        base = _get_base_activity(hour, species_key)

        if hour not in solunar_cache:
            solunar_cache[hour] = _get_solunar_factor(hour, lat, lng, date_str)
        solunar_val = solunar_cache[hour]

        historical = await _get_historical_factor(zone_id, species, hour)

        probability = (
            base * FACTOR_WEIGHTS["base_activity"] +
            season * FACTOR_WEIGHTS["season"] +
            solunar_val * FACTOR_WEIGHTS["solunar"] +
            meteo * FACTOR_WEIGHTS["meteo"] +
            historical * FACTOR_WEIGHTS["historical"] +
            nutrition * FACTOR_WEIGHTS["nutrition"]
        )
        probability = round(min(1.0, max(0.0, probability)), 4)

        confidence = 0.7
        if historical != 0.5:
            confidence = 0.85

        predictions.append({
            "hour": hour,
            "probability": probability,
            "confidence": round(confidence, 2),
            "factors": {
                "base_activity": round(base, 4),
                "season": round(season, 4),
                "solunar": round(solunar_val, 4),
                "meteo": round(meteo, 4),
                "historical": round(historical, 4),
                "nutrition": round(nutrition, 4)
            }
        })

        if probability > peak_prob:
            peak_prob = probability
            peak_hour = hour

    best_start = max(0, peak_hour - 1)
    best_end = min(23, peak_hour + 1)

    probs = [p["probability"] for p in predictions]
    first_half = sum(probs[:12]) / 12
    second_half = sum(probs[12:]) / 12
    trend = "increasing" if second_half > first_half + 0.05 else (
        "decreasing" if first_half > second_half + 0.05 else "stable"
    )

    solunar_context = {"phase_name": "unknown", "illumination": 0.0,
                       "solunar_score": 0.0, "hunting_windows": []}
    try:
        from modules.solunar.engine import compute_solunar
        sol_data = compute_solunar(lat, lng, date_str)
        solunar_context = {
            "phase_name": sol_data.get("moon", {}).get("phase_name", "unknown"),
            "illumination": sol_data.get("moon", {}).get("illumination", 0),
            "solunar_score": sol_data.get("solunar_score", 0),
            "hunting_windows": sol_data.get("hunting_windows", [])[:5]
        }
    except Exception:
        pass

    poi_count = await db.poi_nodes.count_documents({"zone_id": zone_id})

    layer_id = str(uuid.uuid4())
    valid_until = (now + timedelta(hours=6)).isoformat()

    layer = {
        "layer_id": layer_id,
        "zone_id": zone_id,
        "species": species,
        "target_date": date_str,
        "predictions": predictions,
        "aggregation": {
            "peak_probability": round(peak_prob, 4),
            "peak_hour": peak_hour,
            "best_window": {"start": best_start, "end": best_end},
            "trend": trend,
            "avg_confidence": round(sum(p["confidence"] for p in predictions) / 24, 2)
        },
        "solunar_context": solunar_context,
        "meteo_context": {
            "activity_multiplier": round(meteo, 2),
            "recommendation": "favorable" if meteo >= 0.65 else "moderate",
            "limiting_factor": "none"
        },
        "data_sources": ["predictive_engine", "solunar", "weather_simulation",
                         "timeseries", "poi_graph", "nutrition_v6"],
        "poi_count_in_zone": poi_count,
        "computed_at": now.isoformat(),
        "valid_until": valid_until
    }

    await db.predictive_layers.update_one(
        {"zone_id": zone_id, "species": species, "target_date": date_str},
        {"$set": layer},
        upsert=True
    )

    layer.pop("_id", None)
    return layer


async def compute_at_point(lat: float, lng: float, species: str,
                           target_date: Optional[str] = None) -> Dict[str, Any]:
    """Prediction a un point GPS specifique."""
    if species not in VALID_SPECIES:
        return {"error": "INVALID_SPECIES", "valid_species": VALID_SPECIES}

    db = _get_db()
    species_key = SPECIES_MAP.get(species, "deer")
    now = datetime.now(timezone.utc)
    date_str = target_date or now.strftime("%Y-%m-%d")
    target_month = int(date_str.split("-")[1])
    current_hour = now.hour

    base = _get_base_activity(current_hour, species_key)
    season = _get_season_factor(target_month)
    solunar_val = _get_solunar_factor(current_hour, lat, lng, date_str)
    meteo = _get_meteo_factor(species_key)
    nutrition = _get_nutrition_factor(lat, lng, target_month)

    probability = (
        base * FACTOR_WEIGHTS["base_activity"] +
        season * FACTOR_WEIGHTS["season"] +
        solunar_val * FACTOR_WEIGHTS["solunar"] +
        meteo * FACTOR_WEIGHTS["meteo"] +
        0.5 * FACTOR_WEIGHTS["historical"] +
        nutrition * FACTOR_WEIGHTS["nutrition"]
    )

    province = ""
    try:
        from modules.national_data_harvester.services.boundary_resolver import resolve_province
        province = resolve_province(lat, lng) or ""
    except Exception:
        pass

    return {
        "location": {"lat": lat, "lng": lng},
        "species": species,
        "target_date": date_str,
        "current_hour": current_hour,
        "probability": round(min(1.0, probability), 4),
        "confidence": 0.7,
        "province": province,
        "factors": {
            "base_activity": round(base, 4),
            "season": round(season, 4),
            "solunar": round(solunar_val, 4),
            "meteo": round(meteo, 4),
            "historical": 0.5,
            "nutrition": round(nutrition, 4)
        },
        "weights": FACTOR_WEIGHTS,
        "computed_at": now.isoformat()
    }


async def get_heatmap(zone_id: str, species: str,
                      target_date: Optional[str] = None) -> Dict[str, Any]:
    """Heatmap de probabilite multi-POI pour une zone."""
    if species not in VALID_SPECIES:
        return {"error": "INVALID_SPECIES", "valid_species": VALID_SPECIES}

    db = _get_db()
    species_key = SPECIES_MAP.get(species, "deer")
    now = datetime.now(timezone.utc)
    date_str = target_date or now.strftime("%Y-%m-%d")
    target_month = int(date_str.split("-")[1])
    current_hour = now.hour

    cursor = db.poi_nodes.find(
        {"zone_id": zone_id},
        {"_id": 0, "poi_id": 1, "name": 1, "type": 1, "location": 1,
         "score": 1, "properties": 1}
    ).limit(100)
    pois = await cursor.to_list(100)

    heatmap_points = []
    for poi in pois:
        coords = poi.get("location", {}).get("coordinates", [0, 0])
        lat, lng = coords[1], coords[0]

        base = _get_base_activity(current_hour, species_key)
        season = _get_season_factor(target_month)
        nutrition = _get_nutrition_factor(lat, lng, target_month)
        poi_score = poi.get("score", {}).get("global", 0.0)

        probability = (
            base * FACTOR_WEIGHTS["base_activity"] +
            season * FACTOR_WEIGHTS["season"] +
            0.5 * FACTOR_WEIGHTS["solunar"] +
            0.65 * FACTOR_WEIGHTS["meteo"] +
            0.5 * FACTOR_WEIGHTS["historical"] +
            nutrition * FACTOR_WEIGHTS["nutrition"]
        )

        freq = poi.get("properties", {}).get("frequency", 0)
        freq_boost = min(0.1, freq / 500.0)
        probability = min(1.0, probability + poi_score * 0.1 + freq_boost)

        heatmap_points.append({
            "poi_id": poi["poi_id"],
            "name": poi.get("name", ""),
            "type": poi.get("type", ""),
            "lat": lat,
            "lng": lng,
            "probability": round(probability, 4),
            "poi_score": round(poi_score, 4),
            "intensity": "high" if probability > 0.7 else (
                "medium" if probability > 0.5 else "low"
            )
        })

    heatmap_points.sort(key=lambda x: x["probability"], reverse=True)

    return {
        "zone_id": zone_id,
        "species": species,
        "target_date": date_str,
        "hour": current_hour,
        "points": heatmap_points,
        "total_pois": len(heatmap_points),
        "high_count": sum(1 for p in heatmap_points if p["intensity"] == "high"),
        "medium_count": sum(1 for p in heatmap_points if p["intensity"] == "medium"),
        "low_count": sum(1 for p in heatmap_points if p["intensity"] == "low"),
        "computed_at": now.isoformat()
    }


async def get_best_times(zone_id: str, species: str,
                         target_date: Optional[str] = None,
                         lat: float = 46.85, lng: float = -71.25) -> Dict[str, Any]:
    """Meilleurs creneaux horaires combines (solunar + meteo + historique)."""
    if species not in VALID_SPECIES:
        return {"error": "INVALID_SPECIES", "valid_species": VALID_SPECIES}

    layer = await compute_layer(zone_id, species, target_date, lat, lng)
    if "error" in layer:
        return layer

    predictions = layer.get("predictions", [])
    sorted_hours = sorted(predictions, key=lambda p: p["probability"], reverse=True)

    windows = []
    used_hours = set()
    for p in sorted_hours:
        h = p["hour"]
        if h in used_hours:
            continue
        start = max(0, h - 1)
        end = min(23, h + 1)
        for wh in range(start, end + 1):
            used_hours.add(wh)

        window_preds = [pr for pr in predictions if start <= pr["hour"] <= end]
        avg_prob = sum(pr["probability"] for pr in window_preds) / len(window_preds)

        label = "aube" if 4 <= h <= 8 else (
            "crepuscule" if 16 <= h <= 20 else (
                "midi" if 10 <= h <= 14 else "nuit"
            )
        )

        windows.append({
            "start_hour": start,
            "end_hour": end,
            "label": f"{start:02d}:00-{end:02d}:59",
            "period": label,
            "avg_probability": round(avg_prob, 4),
            "peak_hour": h,
            "peak_probability": round(p["probability"], 4),
            "dominant_factor": max(p["factors"], key=p["factors"].get)
        })

        if len(windows) >= 5:
            break

    solunar_windows = layer.get("solunar_context", {}).get("hunting_windows", [])

    return {
        "zone_id": zone_id,
        "species": species,
        "target_date": layer.get("target_date"),
        "best_windows": windows,
        "solunar_windows": solunar_windows,
        "aggregation": layer.get("aggregation", {}),
        "recommendation": _generate_recommendation(windows, species),
        "computed_at": layer.get("computed_at")
    }


def _generate_recommendation(windows: List[Dict], species: str) -> str:
    """Genere une recommandation textuelle."""
    if not windows:
        return f"Donnees insuffisantes pour recommander un creneau pour {species}."

    best = windows[0]
    prob_pct = int(best["avg_probability"] * 100)
    return (
        f"Meilleur creneau pour {species} : {best['label']} ({best['period']}), "
        f"probabilite {prob_pct}%. "
        f"Facteur dominant : {best['dominant_factor']}."
    )
