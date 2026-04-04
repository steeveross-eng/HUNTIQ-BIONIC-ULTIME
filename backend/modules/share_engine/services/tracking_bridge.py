"""
Tracking Bridge Service — Interconnexion Share → Tracking
==========================================================

Service intermediaire BCE-4X. Notifie tracking_engine des evenements
de partage et clics EASYlead.

ZERO couplage direct : aucun import de tracking_engine.
Communication exclusivement via MongoDB (collection: tracking_events).

Version: 1.0.0
Directive: x5400-STEEVE_MAX Phase III
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
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


async def notify_share_event(
    channel: str,
    template: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """
    Notifie tracking_engine d'un evenement de partage.
    """
    db = _get_db()

    doc = {
        "event_type": "share",
        "source_module": "share_engine",
        "user_id": user_id or "anonymous",
        "channel": channel,
        "template": template,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.tracking_events.insert_one(doc)
    logger.info(f"Tracking event: share via {channel} by {user_id}")


async def notify_click_event(
    share_id: str,
    ref_user_id: str,
    page: str
):
    """
    Notifie tracking_engine d'un clic EASYlead.
    """
    db = _get_db()

    doc = {
        "event_type": "share_click",
        "source_module": "share_engine",
        "user_id": ref_user_id,
        "share_id": share_id,
        "page": page,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.tracking_events.insert_one(doc)
    logger.info(f"Tracking event: click on share={share_id}")
