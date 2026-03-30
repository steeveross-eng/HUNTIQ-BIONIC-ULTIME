"""
SHARE ENGINE — BCE-4X GOLDEN V6+ Module PARTAGER
=================================================
Tracking Premium: clics, partages, conversions, engagement, scoring.
Intégration ADMIN PREMIUM: attribution, campagnes, optimisation.

Endpoints:
  POST /api/share/track    — Enregistre un événement de partage
  GET  /api/share/stats     — Statistiques de partage (Admin Premium)
  GET  /api/share/status    — Status du module
"""
import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("share_engine")
router = APIRouter(prefix="/api/share", tags=["SHARE-BIONIC"])

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "huntiq_v6")


def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DB_NAME]


class ShareTrackEvent(BaseModel):
    channel: str
    template: str
    url: Optional[str] = None
    timestamp: Optional[str] = None
    hasWeather: Optional[bool] = False


class ShareStatsResponse(BaseModel):
    total_shares: int
    by_channel: dict
    by_template: dict
    last_24h: int


@router.post("/track")
async def track_share(event: ShareTrackEvent):
    """Enregistre un événement de partage pour le tracking Premium."""
    db = get_db()
    doc = {
        "channel": event.channel,
        "template": event.template,
        "url": event.url,
        "has_weather": event.hasWeather,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "client_timestamp": event.timestamp,
    }
    await db.share_events.insert_one(doc)
    return {"status": "tracked", "channel": event.channel}


@router.get("/stats")
async def share_stats():
    """Statistiques de partage — Admin Premium."""
    db = get_db()
    total = await db.share_events.count_documents({})

    pipeline_channel = [
        {"$group": {"_id": "$channel", "count": {"$sum": 1}}}
    ]
    by_channel = {}
    async for doc in db.share_events.aggregate(pipeline_channel):
        by_channel[doc["_id"]] = doc["count"]

    pipeline_template = [
        {"$group": {"_id": "$template", "count": {"$sum": 1}}}
    ]
    by_template = {}
    async for doc in db.share_events.aggregate(pipeline_template):
        by_template[doc["_id"]] = doc["count"]

    cutoff = datetime.now(timezone.utc).isoformat()
    last_24h = await db.share_events.count_documents({
        "created_at": {"$gte": cutoff[:10]}
    })

    return {
        "total_shares": total,
        "by_channel": by_channel,
        "by_template": by_template,
        "last_24h": last_24h,
    }


@router.get("/status")
async def share_status():
    """Status du module SHARE BIONIC."""
    return {
        "module": "share_engine",
        "version": "1.0.0",
        "protocol": "BCE-4X GOLDEN V6+",
        "status": "OPERATIONAL",
        "channels": ["native", "facebook", "messenger", "whatsapp", "instagram", "tiktok", "sms", "copy"],
        "templates": ["territoire", "premium", "viral"],
        "tracking": "ACTIVE",
        "admin_premium_ready": True,
    }
