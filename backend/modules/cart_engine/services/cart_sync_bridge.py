"""
Cart Sync Bridge — Synchronisation inter-modules
==================================================
Directive x5400-F STEEVE-MAX — Phase P5-C
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ZERO couplage direct : aucun import de payment_engine, freemium_engine,
upsell_engine. Communication exclusivement via MongoDB.

Fonctionnalites:
  - notify_cart_checkout → orders collection
  - sync_upsell_suggestions → lecture upsell_events
  - sync_freemium_quotas → lecture quotas
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List
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


async def notify_cart_checkout(user_id: str, cart: Dict) -> str:
    """Cree une commande dans orders apres checkout."""
    db = _get_db()

    order = {
        "order_id": str(uuid.uuid4()),
        "user_id": user_id,
        "cart_id": cart.get("cart_id"),
        "items": cart.get("items", []),
        "subtotal": cart.get("subtotal", 0),
        "discount_total": cart.get("discount_total", 0),
        "total": cart.get("total", 0),
        "currency": cart.get("currency", "CAD"),
        "promotions_applied": cart.get("promotions_applied", []),
        "status": "pending_payment",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.orders.insert_one({**order, "_id": order["order_id"]})
    logger.info(f"Order created from cart: user={user_id}, order={order['order_id']}")
    return order["order_id"]


async def get_upsell_suggestions(user_id: str, cart: Dict) -> List[Dict]:
    """Genere des suggestions upsell basees sur le contenu du panier."""
    db = _get_db()

    suggestions = []

    cart_product_types = {i.get("product_type") for i in cart.get("items", [])}
    cart_total = cart.get("total", 0)

    if "package" in cart_product_types and cart_total < 100:
        suggestions.append({
            "type": "bundle_upgrade",
            "message": "Ajoutez un addon pour beneficier du tarif bundle",
            "priority": "high"
        })

    pending_events = await db.upsell_events.find(
        {"user_id": user_id, "status": "pending"},
        {"_id": 0}
    ).limit(5).to_list(5)

    for event in pending_events:
        if event.get("event_type") == "quota_reached":
            suggestions.append({
                "type": "quota_upgrade",
                "feature": event.get("feature"),
                "message": f"Votre quota {event.get('feature')} est atteint. Passez au niveau superieur.",
                "priority": "medium"
            })
        elif event.get("event_type") == "feature_blocked":
            suggestions.append({
                "type": "feature_unlock",
                "feature": event.get("feature"),
                "message": event.get("details", {}).get("suggestion", ""),
                "priority": "high"
            })

    return suggestions


async def sync_freemium_status(user_id: str) -> Dict:
    """Synchronise le statut freemium pour le panier."""
    db = _get_db()

    user = await db.users.find_one(
        {"user_id": user_id},
        {"_id": 0, "tier": 1, "quotas": 1}
    )

    if not user:
        return {
            "user_id": user_id,
            "tier": "free",
            "quotas": {},
            "sync_status": "user_not_found"
        }

    return {
        "user_id": user_id,
        "tier": user.get("tier", "free"),
        "quotas": user.get("quotas", {}),
        "sync_status": "synced"
    }
