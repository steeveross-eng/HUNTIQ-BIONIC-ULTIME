"""
Cart Promotions — Gestion des codes promo
===========================================
Directive x5400-F STEEVE-MAX — Phase P5-B
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Fonctionnalites:
  - Appliquer / retirer un code promo
  - Valider un code (usages, dates, montant min)
  - Creer une promotion (admin)

Collection MongoDB: cart_promotions
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


async def validate_promo_code(promo_code: str, cart_total: float = 0) -> Dict:
    """Valide un code promo."""
    db = _get_db()
    promo = await db.cart_promotions.find_one(
        {"promo_code": promo_code},
        {"_id": 0}
    )

    if not promo:
        return {"valid": False, "error": "CODE_NOT_FOUND",
                "message": "Code promo introuvable"}

    if promo.get("status") != "active":
        return {"valid": False, "error": "CODE_INACTIVE",
                "message": "Ce code promo n'est plus actif"}

    now = datetime.now(timezone.utc).isoformat()
    if promo.get("valid_until") and now > promo["valid_until"]:
        return {"valid": False, "error": "CODE_EXPIRED",
                "message": "Ce code promo a expire"}

    if promo.get("valid_from") and now < promo["valid_from"]:
        return {"valid": False, "error": "CODE_NOT_YET_VALID",
                "message": "Ce code promo n'est pas encore actif"}

    max_uses = promo.get("max_uses", 0)
    if max_uses > 0 and promo.get("current_uses", 0) >= max_uses:
        return {"valid": False, "error": "CODE_DEPLETED",
                "message": "Ce code promo a atteint son nombre max d'utilisations"}

    min_total = promo.get("min_cart_total", 0)
    if min_total > 0 and cart_total < min_total:
        return {"valid": False, "error": "MIN_TOTAL_NOT_MET",
                "message": f"Montant minimum requis: {min_total} CAD"}

    return {
        "valid": True,
        "promo_code": promo_code,
        "discount_type": promo.get("discount_type"),
        "discount_value": promo.get("discount_value"),
        "applicable_products": promo.get("applicable_products", [])
    }


async def apply_promotion(user_id: str, promo_code: str) -> Dict:
    """Applique un code promo au panier."""
    db = _get_db()

    cart = await db.carts.find_one(
        {"user_id": user_id, "status": "active"},
        {"_id": 0}
    )
    if not cart:
        return {"success": False, "error": "NO_CART",
                "message": "Aucun panier actif"}

    for promo in cart.get("promotions_applied", []):
        if promo.get("promo_code") == promo_code:
            return {"success": False, "error": "ALREADY_APPLIED",
                    "message": "Ce code promo est deja applique"}

    validation = await validate_promo_code(promo_code, cart.get("subtotal", 0))
    if not validation["valid"]:
        return {"success": False, **validation}

    promo_entry = {
        "promo_code": promo_code,
        "discount_type": validation["discount_type"],
        "discount_value": validation["discount_value"],
        "applied_to": "cart"
    }

    await db.carts.update_one(
        {"cart_id": cart["cart_id"]},
        {"$push": {"promotions_applied": promo_entry},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    await db.cart_promotions.update_one(
        {"promo_code": promo_code},
        {"$inc": {"current_uses": 1}}
    )

    logger.info(f"Promo {promo_code} applied to cart of user {user_id}")
    return {"success": True, "promo_code": promo_code,
            "discount_type": validation["discount_type"],
            "discount_value": validation["discount_value"]}


async def remove_promotion(user_id: str, promo_code: str) -> Dict:
    """Retire un code promo du panier."""
    db = _get_db()

    cart = await db.carts.find_one(
        {"user_id": user_id, "status": "active"},
        {"_id": 0, "promotions_applied": 1, "cart_id": 1}
    )
    if not cart:
        return {"success": False, "error": "NO_CART",
                "message": "Aucun panier actif"}

    promos = cart.get("promotions_applied", [])
    if not any(p.get("promo_code") == promo_code for p in promos):
        return {"success": False, "error": "PROMO_NOT_FOUND",
                "message": "Code promo non trouve dans le panier"}

    await db.carts.update_one(
        {"cart_id": cart["cart_id"]},
        {"$pull": {"promotions_applied": {"promo_code": promo_code}},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    await db.cart_promotions.update_one(
        {"promo_code": promo_code, "current_uses": {"$gt": 0}},
        {"$inc": {"current_uses": -1}}
    )

    return {"success": True, "promo_code": promo_code, "removed": True}


async def create_promotion(promo_data: Dict) -> Dict:
    """Admin: cree une promotion."""
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "promo_code": promo_data["promo_code"],
        "discount_type": promo_data.get("discount_type", "percentage"),
        "discount_value": promo_data.get("discount_value", 10),
        "applicable_products": promo_data.get("applicable_products", []),
        "min_cart_total": promo_data.get("min_cart_total", 0),
        "max_uses": promo_data.get("max_uses", 0),
        "current_uses": 0,
        "valid_from": promo_data.get("valid_from", now),
        "valid_until": promo_data.get("valid_until"),
        "status": "active",
        "created_at": now
    }

    await db.cart_promotions.insert_one({**doc, "_id": doc["promo_code"]})
    return {k: v for k, v in doc.items() if k != "_id"}
