"""
M3 — TimeSeries Collector : Collecte et stockage des series temporelles
=========================================================================
Directive x7000-M3 — Phase M3-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Metriques : observation_count, camera_detection, activity_index, poi_frequency
Sources d'ingestion : POI Graph M2, hunting_trip_logger, saisie manuelle
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

VALID_METRICS = ["observation_count", "camera_detection", "activity_index", "poi_frequency"]
VALID_GRANULARITIES = ["hourly", "daily", "weekly"]
VALID_SOURCES = ["poi_graph", "hunting_trip", "manual"]


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


async def ensure_indexes():
    """Cree les index MongoDB pour timeseries_data et seasonal_trends."""
    db = _get_db()
    await db.timeseries_data.create_index("zone_id")
    await db.timeseries_data.create_index("species")
    await db.timeseries_data.create_index("metric")
    await db.timeseries_data.create_index(
        [("zone_id", 1), ("species", 1), ("metric", 1)],
        unique=True
    )
    await db.seasonal_trends.create_index("species")
    await db.seasonal_trends.create_index("zone_id")
    await db.seasonal_trends.create_index("year")
    await db.seasonal_trends.create_index(
        [("species", 1), ("zone_id", 1), ("year", 1)],
        unique=True
    )
    logger.info("M3 timeseries + seasonal_trends indexes created")


async def record_datapoint(zone_id: str, species: str, metric: str,
                           value: float, source: str = "manual",
                           poi_id: str = "",
                           timestamp: Optional[str] = None) -> Dict[str, Any]:
    """Enregistre un point de donnee dans une serie temporelle."""
    if metric not in VALID_METRICS:
        return {"error": "INVALID_METRIC", "valid_metrics": VALID_METRICS}
    if source not in VALID_SOURCES:
        return {"error": "INVALID_SOURCE", "valid_sources": VALID_SOURCES}

    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    ts = timestamp or now

    datapoint = {
        "timestamp": ts,
        "value": value,
        "source": source,
        "poi_id": poi_id
    }

    result = await db.timeseries_data.update_one(
        {"zone_id": zone_id, "species": species, "metric": metric},
        {
            "$push": {"values": datapoint},
            "$set": {
                "latest_value": value,
                "latest_timestamp": ts,
                "updated_at": now,
                "granularity": "hourly"
            },
            "$inc": {"total_points": 1},
            "$setOnInsert": {
                "ts_id": str(uuid.uuid4()),
                "zone_id": zone_id,
                "species": species,
                "metric": metric,
                "created_at": now
            }
        },
        upsert=True
    )

    return {
        "recorded": True,
        "zone_id": zone_id,
        "species": species,
        "metric": metric,
        "value": value,
        "timestamp": ts,
        "source": source,
        "upserted": result.upserted_id is not None
    }


async def get_timeseries(zone_id: str, species: str,
                         metric: str = "activity_index",
                         limit: int = 100) -> Dict[str, Any]:
    """Recupere une serie temporelle."""
    db = _get_db()
    ts = await db.timeseries_data.find_one(
        {"zone_id": zone_id, "species": species, "metric": metric},
        {"_id": 0}
    )
    if not ts:
        return {
            "zone_id": zone_id,
            "species": species,
            "metric": metric,
            "values": [],
            "total_points": 0,
            "message": "NO_DATA"
        }

    values = ts.get("values", [])[-limit:]
    return {
        "ts_id": ts.get("ts_id"),
        "zone_id": zone_id,
        "species": species,
        "metric": metric,
        "values": values,
        "total_points": ts.get("total_points", len(values)),
        "latest_value": ts.get("latest_value"),
        "latest_timestamp": ts.get("latest_timestamp"),
        "granularity": ts.get("granularity", "hourly")
    }
