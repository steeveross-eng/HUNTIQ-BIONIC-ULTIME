"""
Upsell Notifier Service — Interconnexion Freemium → Upsell
===========================================================

Service intermediaire BCE-4X. Notifie upsell_engine quand un quota
est atteint ou une feature est bloquee.

ZERO couplage direct : aucun import de upsell_engine.
Communication exclusivement via MongoDB (collection: upsell_events).

Version: 1.0.0
Directive: x5400-STEEVE_MAX Phase II
"""

import os
import logging
from datetime import datetime, timezone
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


async def notify_quota_reached(
    user_id: str,
    feature: str,
    current_usage: int,
    limit: int
) -> str:
    """
    Notifie que le quota d'une feature a ete atteint.
    Cree un evenement upsell dans MongoDB.
    """
    db = _get_db()

    doc = {
        "user_id": user_id,
        "event_type": "quota_reached",
        "feature": feature,
        "details": {
            "current_usage": current_usage,
            "limit": limit,
            "exceeded_by": current_usage - limit
        },
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = await db.upsell_events.insert_one(doc)
    logger.info(f"Upsell event: quota_reached for user={user_id}, feature={feature}")
    return str(result.inserted_id)


async def notify_feature_blocked(
    user_id: str,
    feature: str,
    required_tier: str
) -> str:
    """
    Notifie qu'une feature est bloquee pour l'utilisateur.
    Cree un evenement upsell dans MongoDB.
    """
    db = _get_db()

    doc = {
        "user_id": user_id,
        "event_type": "feature_blocked",
        "feature": feature,
        "details": {
            "required_tier": required_tier,
            "suggestion": f"Passez au plan {required_tier} pour debloquer {feature}"
        },
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = await db.upsell_events.insert_one(doc)
    logger.info(f"Upsell event: feature_blocked for user={user_id}, feature={feature}")
    return str(result.inserted_id)


async def get_user_upsell_events(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """
    Recupere les evenements upsell pour un utilisateur.
    """
    db = _get_db()

    query = {"user_id": user_id}
    if status:
        query["status"] = status

    cursor = db.upsell_events.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit)

    results = []
    async for doc in cursor:
        results.append(doc)
    return results
