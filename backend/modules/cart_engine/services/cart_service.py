"""
Cart Service V2 — Panier persistant utilisateur
=================================================
Directive x5400-F STEEVE-MAX — Phase P5-A
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Fonctionnalites:
  - Panier par user_id (persistent MongoDB)
  - CRUD: create, get, add_item, update_qty, remove_item, clear
  - Calcul automatique des totaux
  - Expiration 24h
  - Merge si article deja present

Collection MongoDB: carts
"""

import os
import uuid
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


def _compute_totals(cart: Dict) -> Dict:
    """Recalcule subtotal, discount_total, total."""
    items = cart.get("items", [])
    subtotal = sum(i.get("unit_price", 0) * i.get("quantity", 1) for i in items)

    discount_total = 0.0
    for promo in cart.get("promotions_applied", []):
        if promo.get("discount_type") == "percentage":
            discount_total += subtotal * (promo.get("discount_value", 0) / 100)
        elif promo.get("discount_type") == "fixed":
            discount_total += promo.get("discount_value", 0)

    discount_total = min(discount_total, subtotal)
    total = round(subtotal - discount_total, 2)

    cart["subtotal"] = round(subtotal, 2)
    cart["discount_total"] = round(discount_total, 2)
    cart["total"] = total
    cart["item_count"] = len(items)
    cart["updated_at"] = datetime.now(timezone.utc).isoformat()
    return cart


async def get_or_create_cart(user_id: str) -> Dict:
    """Recupere le panier actif ou en cree un nouveau."""
    db = _get_db()

    cart = await db.carts.find_one(
        {"user_id": user_id, "status": "active"},
        {"_id": 0}
    )

    if cart:
        return _compute_totals(cart)

    now = datetime.now(timezone.utc)
    cart = {
        "cart_id": str(uuid.uuid4()),
        "user_id": user_id,
        "status": "active",
        "items": [],
        "promotions_applied": [],
        "subtotal": 0.0,
        "discount_total": 0.0,
        "total": 0.0,
        "item_count": 0,
        "currency": "CAD",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=24)).isoformat()
    }

    await db.carts.insert_one({**cart, "_id": cart["cart_id"]})
    return cart


async def add_item(user_id: str, product_type: str, product_id: str,
                   name: str, unit_price: float, quantity: int = 1,
                   description: str = "", metadata: Optional[Dict] = None) -> Dict:
    """Ajoute un article au panier. Merge si deja present."""
    db = _get_db()
    cart = await get_or_create_cart(user_id)

    for item in cart["items"]:
        if item["product_id"] == product_id and item["product_type"] == product_type:
            item["quantity"] += quantity
            await db.carts.update_one(
                {"cart_id": cart["cart_id"]},
                {"$set": {"items": cart["items"],
                          "updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            return _compute_totals(cart)

    new_item = {
        "item_id": str(uuid.uuid4()),
        "product_type": product_type,
        "product_id": product_id,
        "name": name,
        "description": description,
        "quantity": quantity,
        "unit_price": round(unit_price, 2),
        "currency": "CAD",
        "metadata": metadata or {}
    }

    await db.carts.update_one(
        {"cart_id": cart["cart_id"]},
        {"$push": {"items": new_item},
         "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    cart["items"].append(new_item)
    return _compute_totals(cart)


async def update_quantity(user_id: str, item_id: str, quantity: int) -> Optional[Dict]:
    """Met a jour la quantite. Supprime si quantity <= 0."""
    db = _get_db()
    cart = await get_or_create_cart(user_id)

    if quantity <= 0:
        return await remove_item(user_id, item_id)

    found = False
    for item in cart["items"]:
        if item["item_id"] == item_id:
            item["quantity"] = quantity
            found = True
            break

    if not found:
        return None

    await db.carts.update_one(
        {"cart_id": cart["cart_id"]},
        {"$set": {"items": cart["items"],
                  "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return _compute_totals(cart)


async def remove_item(user_id: str, item_id: str) -> Optional[Dict]:
    """Supprime un article du panier."""
    db = _get_db()
    cart = await get_or_create_cart(user_id)

    original_len = len(cart["items"])
    cart["items"] = [i for i in cart["items"] if i["item_id"] != item_id]

    if len(cart["items"]) == original_len:
        return None

    await db.carts.update_one(
        {"cart_id": cart["cart_id"]},
        {"$set": {"items": cart["items"],
                  "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    return _compute_totals(cart)


async def clear_cart(user_id: str) -> Dict:
    """Vide le panier."""
    db = _get_db()
    cart = await get_or_create_cart(user_id)

    await db.carts.update_one(
        {"cart_id": cart["cart_id"]},
        {"$set": {"items": [], "promotions_applied": [],
                  "subtotal": 0.0, "discount_total": 0.0, "total": 0.0,
                  "item_count": 0,
                  "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    cart["items"] = []
    cart["promotions_applied"] = []
    return _compute_totals(cart)


async def get_cart_summary(user_id: str) -> Dict:
    """Resume du panier avec totaux."""
    cart = await get_or_create_cart(user_id)
    return {
        "cart_id": cart["cart_id"],
        "user_id": user_id,
        "item_count": cart.get("item_count", 0),
        "subtotal": cart.get("subtotal", 0),
        "discount_total": cart.get("discount_total", 0),
        "total": cart.get("total", 0),
        "currency": cart.get("currency", "CAD"),
        "promotions_count": len(cart.get("promotions_applied", [])),
        "status": cart.get("status", "active")
    }


async def set_cart_status(user_id: str, status: str) -> Optional[Dict]:
    """Change le statut du panier (checked_out, abandoned, etc.)."""
    db = _get_db()
    result = await db.carts.find_one_and_update(
        {"user_id": user_id, "status": "active"},
        {"$set": {"status": status,
                  "updated_at": datetime.now(timezone.utc).isoformat()}},
    )
    if not result:
        return None
    cart = await db.carts.find_one({"cart_id": result["cart_id"]}, {"_id": 0})
    return cart
