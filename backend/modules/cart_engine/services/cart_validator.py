"""
Cart Validator — Validation pre-checkout
==========================================
Directive x5400-F STEEVE-MAX — Phase P5-B
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Fonctionnalites:
  - Validation du panier avant checkout
  - Verification eligibilite tier
  - Recalcul totaux
"""

import os
import logging
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


async def validate_cart(cart: Dict) -> Dict:
    """Valide le panier avant checkout."""
    errors = []
    warnings = []

    items = cart.get("items", [])
    if not items:
        errors.append({
            "code": "EMPTY_CART",
            "message": "Le panier est vide"
        })
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "item_count": 0
        }

    for item in items:
        if item.get("quantity", 0) <= 0:
            errors.append({
                "code": "INVALID_QUANTITY",
                "message": f"Quantite invalide pour {item.get('name', 'inconnu')}",
                "item_id": item.get("item_id")
            })
        if item.get("unit_price", 0) < 0:
            errors.append({
                "code": "INVALID_PRICE",
                "message": f"Prix invalide pour {item.get('name', 'inconnu')}",
                "item_id": item.get("item_id")
            })

    total = cart.get("total", 0)
    if total <= 0 and not errors:
        warnings.append({
            "code": "ZERO_TOTAL",
            "message": "Le total du panier est 0"
        })

    for promo in cart.get("promotions_applied", []):
        promo_valid = await _check_promo_still_valid(promo.get("promo_code", ""))
        if not promo_valid:
            warnings.append({
                "code": "PROMO_EXPIRED",
                "message": f"Le code promo {promo.get('promo_code')} a expire",
                "promo_code": promo.get("promo_code")
            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "item_count": len(items),
        "total": cart.get("total", 0),
        "currency": cart.get("currency", "CAD")
    }


async def check_tier_eligibility(user_id: str, items: List[Dict]) -> Dict:
    """Verifie que l'utilisateur peut acheter les items selon son tier."""
    db = _get_db()
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "tier": 1})
    current_tier = user.get("tier", "free") if user else "free"

    eligible_items = []
    blocked_items = []

    for item in items:
        required_tier = item.get("metadata", {}).get("required_tier")
        if required_tier and _tier_rank(current_tier) < _tier_rank(required_tier):
            blocked_items.append({
                "item_id": item.get("item_id"),
                "name": item.get("name"),
                "required_tier": required_tier,
                "current_tier": current_tier
            })
        else:
            eligible_items.append(item.get("item_id"))

    return {
        "user_id": user_id,
        "current_tier": current_tier,
        "all_eligible": len(blocked_items) == 0,
        "eligible_count": len(eligible_items),
        "blocked_count": len(blocked_items),
        "blocked_items": blocked_items
    }


def _tier_rank(tier: str) -> int:
    """Retourne le rang du tier."""
    ranks = {"free": 0, "premium": 1, "pro": 2, "enterprise": 3}
    return ranks.get(tier, 0)


async def _check_promo_still_valid(promo_code: str) -> bool:
    """Verifie si un code promo est encore valide."""
    if not promo_code:
        return False
    db = _get_db()
    promo = await db.cart_promotions.find_one(
        {"promo_code": promo_code, "status": "active"},
        {"_id": 0}
    )
    return promo is not None
