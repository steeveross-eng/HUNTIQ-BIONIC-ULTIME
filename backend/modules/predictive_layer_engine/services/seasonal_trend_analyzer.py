"""
M3 — Seasonal Trend Analyzer : Tendances saisonnieres
========================================================
Directive x7000-M3 — Phase M3-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : predictive_engine.SEASON_FACTORS consomme en LECTURE comme baseline.
NE recree PAS la logique saisonniere de predictive_engine.
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def _get_baseline_season_factors() -> Dict[int, float]:
    """PF3-S2 : Baseline saisonniere depuis predictive_engine (LECTURE SEULE)."""
    try:
        from modules.predictive_engine.v1.service import PredictiveService
        return dict(PredictiveService.SEASON_FACTORS)
    except Exception:
        return {1: 0.6, 2: 0.5, 3: 0.6, 4: 0.7, 5: 0.75, 6: 0.65,
                7: 0.5, 8: 0.6, 9: 0.85, 10: 0.95, 11: 0.9, 12: 0.7}


async def analyze_trends(species: str, zone_id: str = "",
                         year: int = 2026) -> Dict[str, Any]:
    """Analyse des tendances saisonnieres pour une espece/zone."""
    db = _get_db()

    existing = await db.seasonal_trends.find_one(
        {"species": species, "zone_id": zone_id, "year": year},
        {"_id": 0}
    )
    if existing:
        return existing

    baseline = _get_baseline_season_factors()

    ts_data = {}
    cursor = db.timeseries_data.find(
        {"species": species, "zone_id": zone_id} if zone_id else {"species": species},
        {"_id": 0}
    )
    async for ts in cursor:
        for v in ts.get("values", []):
            try:
                ts_str = v.get("timestamp", "")
                month = int(ts_str[5:7]) if len(ts_str) >= 7 else 0
                if 1 <= month <= 12:
                    if month not in ts_data:
                        ts_data[month] = []
                    ts_data[month].append(v.get("value", 0))
            except (ValueError, IndexError):
                continue

    monthly_patterns = []
    peak_month = 10
    peak_activity = 0.0
    low_month = 7
    low_activity = 1.0
    total_obs = 0

    for month in range(1, 13):
        base_activity = baseline.get(month, 0.7)

        obs_values = ts_data.get(month, [])
        obs_count = len(obs_values)
        total_obs += obs_count

        if obs_values:
            measured_activity = sum(obs_values) / len(obs_values)
            activity_index = (base_activity * 0.5 + measured_activity * 0.5)
        else:
            activity_index = base_activity

        peak_hours = [6, 7, 17, 18]
        if month in [10, 11]:
            peak_hours = [5, 6, 7, 16, 17, 18]
        elif month in [6, 7]:
            peak_hours = [5, 6, 19, 20]

        confidence = min(0.95, 0.5 + obs_count * 0.05)

        monthly_patterns.append({
            "month": month,
            "activity_index": round(activity_index, 4),
            "peak_hours": peak_hours,
            "observation_count": obs_count,
            "trend_vs_previous": "stable",
            "confidence": round(confidence, 2),
            "baseline_factor": round(base_activity, 4)
        })

        if activity_index > peak_activity:
            peak_activity = activity_index
            peak_month = month
        if activity_index < low_activity:
            low_activity = activity_index
            low_month = month

    for i in range(1, 12):
        diff = monthly_patterns[i]["activity_index"] - monthly_patterns[i - 1]["activity_index"]
        monthly_patterns[i]["trend_vs_previous"] = (
            "up" if diff > 0.05 else ("down" if diff < -0.05 else "stable")
        )

    all_activities = [mp["activity_index"] for mp in monthly_patterns]
    avg_activity = sum(all_activities) / len(all_activities)

    trend_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    trend_doc = {
        "trend_id": trend_id,
        "species": species,
        "zone_id": zone_id,
        "year": year,
        "monthly_patterns": monthly_patterns,
        "annual_summary": {
            "peak_month": peak_month,
            "peak_activity": round(peak_activity, 4),
            "low_month": low_month,
            "low_activity": round(low_activity, 4),
            "total_observations": total_obs,
            "avg_activity": round(avg_activity, 4)
        },
        "computed_at": now
    }

    await db.seasonal_trends.update_one(
        {"species": species, "zone_id": zone_id, "year": year},
        {"$set": trend_doc},
        upsert=True
    )

    trend_doc.pop("_id", None)
    return trend_doc
