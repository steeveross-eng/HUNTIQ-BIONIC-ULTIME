"""
Analytics Feed Service — Interconnexion Marketing → Analytics
==============================================================

Service intermediaire BCE-4X. Alimente analytics_engine avec les
metriques marketing pour le dashboard.

ZERO couplage direct : aucun import de analytics_engine.
Communication exclusivement via MongoDB (collection: marketing_analytics).

Version: 1.0.0
Directive: x5400-STEEVE_MAX Phase III
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
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


async def feed_marketing_event(
    event_type: str,
    channel: str,
    data: Optional[Dict] = None
):
    """
    Enregistre un evenement marketing pour analytics.
    """
    db = _get_db()

    doc = {
        "event_type": event_type,
        "channel": channel,
        "source_module": "marketing_engine",
        "data": data or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.marketing_analytics.insert_one(doc)
    logger.info(f"Marketing analytics: {event_type} via {channel}")


async def get_marketing_analytics(period_days: int = 30) -> Dict:
    """
    Aggrege les metriques marketing sur une periode.
    """
    db = _get_db()

    cutoff = (datetime.now(timezone.utc) - timedelta(days=period_days)).isoformat()

    # Count events by type
    pipeline_type = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
    ]

    # Count events by channel
    pipeline_channel = [
        {"$match": {"created_at": {"$gte": cutoff}}},
        {"$group": {"_id": "$channel", "count": {"$sum": 1}}}
    ]

    total = await db.marketing_analytics.count_documents({"created_at": {"$gte": cutoff}})

    by_type = {}
    async for doc in db.marketing_analytics.aggregate(pipeline_type):
        by_type[doc["_id"]] = doc["count"]

    by_channel = {}
    async for doc in db.marketing_analytics.aggregate(pipeline_channel):
        by_channel[doc["_id"]] = doc["count"]

    contacts_new = await db.marketing_contacts.count_documents({"created_at": {"$gte": cutoff}})

    return {
        "period_days": period_days,
        "total_events": total,
        "contacts_new": contacts_new,
        "by_type": by_type,
        "by_channel": by_channel
    }
