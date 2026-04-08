"""
Freemium Engine Router - V5-ULTIME Monetisation
===============================================

R7: Separe en CRUD subscription + pricing UNIQUEMENT.
La logique d'acces/guard est externalisee dans premium_guard.py.

Niveaux:
- FREE: Acces limite, quotas stricts
- PREMIUM: Acces complet, sans limitations
- PRO: Fonctionnalites avancees + support prioritaire

Version: 2.0.0 (R7 — Separation AUTH/PREMIUM)
Protocol: BCE-4X GOLDEN V6+ | STEEVE-MAX
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
from enum import Enum
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient

# R7: Import source unique depuis premium_guard
from premium_guard import TIER_LIMITS, TIERS, check_quota

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/freemium", tags=["Freemium Engine - Monetisation"])

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ==============================================
# MODELS
# ==============================================

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"

class FeatureAccess(str, Enum):
    FULL = "full"
    LIMITED = "limited"
    LOCKED = "locked"

class UserSubscription(BaseModel):
    user_id: str
    tier: SubscriptionTier = SubscriptionTier.FREE
    expires_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

class FeatureCheckRequest(BaseModel):
    user_id: str
    feature: str

# Feature descriptions for UI
FEATURES = {
    "daily_strategy_generations": {
        "name": "Generations de strategie",
        "description": "Nombre de strategies generees par jour",
        "type": "quota"
    },
    "territory_zones": {
        "name": "Zones de territoire",
        "description": "Nombre de zones de chasse personnalisees",
        "type": "quota"
    },
    "analytics_history_days": {
        "name": "Historique analytics",
        "description": "Jours d'historique disponibles",
        "type": "quota"
    },
    "export_reports": {
        "name": "Export de rapports",
        "description": "Exporter les donnees en PDF/Excel",
        "type": "feature"
    },
    "custom_rules": {
        "name": "Regles personnalisees",
        "description": "Creer vos propres regles de chasse",
        "type": "feature"
    },
    "live_heading": {
        "name": "Live Heading View",
        "description": "Navigation immersive en temps reel",
        "type": "feature"
    },
    "advanced_layers": {
        "name": "Couches avancees",
        "description": "Acces aux couches 3D, simulation, comportement",
        "type": "feature"
    },
    "priority_support": {
        "name": "Support prioritaire",
        "description": "Assistance rapide et dediee",
        "type": "feature"
    }
}

# ==============================================
# MODULE INFO
# ==============================================

@router.get("/")
async def freemium_engine_info():
    """Get freemium engine information"""
    return {
        "module": "freemium_engine",
        "version": "2.0.0",
        "description": "Gestion freemium V5-ULTIME — R7 Separation AUTH/PREMIUM",
        "tiers": list(TIERS),
        "features_count": len(FEATURES),
        "tier_limits": TIER_LIMITS,
        "guard": "premium_guard.py",
    }

# ==============================================
# SUBSCRIPTION MANAGEMENT (PREMIUM CRUD)
# ==============================================

@router.get("/subscription/{user_id}")
async def get_subscription(user_id: str):
    """Get user subscription details"""
    db = get_db()
    sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    if not sub:
        sub = {
            "user_id": user_id,
            "tier": SubscriptionTier.FREE.value,
            "expires_at": None,
            "created_at": datetime.now(timezone.utc)
        }
        await db.subscriptions.insert_one(sub)
        sub.pop("_id", None)
    if sub.get("expires_at") and sub["expires_at"] < datetime.now(timezone.utc):
        sub["tier"] = SubscriptionTier.FREE.value
        sub["expired"] = True
    tier = sub.get("tier", "free")
    sub["limits"] = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    return {"success": True, "subscription": sub}

@router.post("/subscription/upgrade")
async def upgrade_subscription(user_id: str, tier: SubscriptionTier, duration_days: int = 30):
    """Upgrade user subscription (called after payment)"""
    db = get_db()
    expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
    sub_data = {
        "user_id": user_id,
        "tier": tier.value,
        "expires_at": expires_at,
        "upgraded_at": datetime.now(timezone.utc)
    }
    await db.subscriptions.update_one(
        {"user_id": user_id},
        {"$set": sub_data},
        upsert=True
    )
    return {
        "success": True,
        "subscription": sub_data,
        "message": f"Upgraded to {tier.value} until {expires_at.isoformat()}"
    }

# ==============================================
# QUOTA MANAGEMENT — R7: delegue a premium_guard
# ==============================================

@router.get("/quota/{user_id}/{feature}")
async def get_quota_usage(user_id: str, feature: str):
    """Get quota usage for a specific feature — R7: delegue a premium_guard.check_quota"""
    quota = await check_quota(user_id, feature)
    return {"success": True, "quota": quota}

@router.post("/quota/{user_id}/{feature}/increment")
async def increment_quota(user_id: str, feature: str, amount: int = 1):
    """Increment quota usage"""
    db = get_db()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    await db.quota_usage.update_one(
        {"user_id": user_id, "feature": feature, "date": today},
        {"$inc": {"count": amount}},
        upsert=True
    )
    try:
        quota = await check_quota(user_id, feature)
        if not quota.get("unlimited") and quota.get("remaining", 1) <= 0:
            from modules.freemium_engine.services.upsell_notifier import notify_quota_reached
            await notify_quota_reached(user_id, feature, quota["used"], quota["limit"])
    except Exception as e:
        logger.warning(f"Upsell notify failed (non-blocking): {e}")
    return {"success": True, "incremented": amount}

# ==============================================
# FEATURE ACCESS CHECK — R7: delegue a premium_guard
# ==============================================

@router.post("/check-access")
async def check_feature_access(request: FeatureCheckRequest):
    """Check if user has access to a feature — R7: utilise premium_guard"""
    from premium_guard import _get_user_tier
    tier = await _get_user_tier(request.user_id)
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    feature_value = limits.get(request.feature)
    if feature_value is None:
        access = FeatureAccess.LOCKED
        can_access = False
    elif isinstance(feature_value, bool):
        access = FeatureAccess.FULL if feature_value else FeatureAccess.LOCKED
        can_access = feature_value
    elif feature_value == -1:
        access = FeatureAccess.FULL
        can_access = True
    elif feature_value > 0:
        quota = await check_quota(request.user_id, request.feature)
        if quota.get("remaining", 0) > 0 or quota.get("unlimited"):
            access = FeatureAccess.FULL
            can_access = True
        else:
            access = FeatureAccess.LIMITED
            can_access = False
    else:
        access = FeatureAccess.LOCKED
        can_access = False
    return {
        "success": True,
        "feature": request.feature,
        "tier": tier,
        "access": access.value,
        "can_access": can_access,
        "upgrade_required": not can_access and tier == "free"
    }

@router.get("/upsell-events/{user_id}")
async def get_upsell_events(user_id: str):
    """Get upsell events for a user. Phase II x5400 — BCE-4X."""
    from modules.freemium_engine.services.upsell_notifier import get_user_upsell_events
    events = await get_user_upsell_events(user_id)
    return {
        "success": True,
        "user_id": user_id,
        "count": len(events),
        "events": events,
        "source": "upsell_notifier",
        "directive": "x5400-Phase-II"
    }

# ==============================================
# TIER COMPARISON
# ==============================================

@router.get("/tiers/compare")
async def compare_tiers():
    """Get comparison of all tiers — R7: source unique TIER_LIMITS"""
    comparison = []
    for feature_id, feature_info in FEATURES.items():
        feature_comparison = {
            "id": feature_id,
            "name": feature_info["name"],
            "description": feature_info["description"],
            "type": feature_info["type"],
            "tiers": {}
        }
        for tier in TIERS:
            value = TIER_LIMITS[tier].get(feature_id)
            if isinstance(value, bool):
                feature_comparison["tiers"][tier] = "Y" if value else "N"
            elif value == -1:
                feature_comparison["tiers"][tier] = "illimite"
            else:
                feature_comparison["tiers"][tier] = str(value)
        comparison.append(feature_comparison)
    return {
        "success": True,
        "tiers": list(TIERS),
        "features": comparison
    }

# ==============================================
# PRICING
# ==============================================

PRICING = {
    "premium": {
        "monthly": {"amount": 9.99, "currency": "CAD", "stripe_price_id": None},
        "yearly": {"amount": 99.99, "currency": "CAD", "stripe_price_id": None}
    },
    "pro": {
        "monthly": {"amount": 19.99, "currency": "CAD", "stripe_price_id": None},
        "yearly": {"amount": 199.99, "currency": "CAD", "stripe_price_id": None}
    }
}

@router.get("/pricing")
async def get_pricing():
    """Get subscription pricing"""
    return {
        "success": True,
        "currency": "CAD",
        "pricing": {
            "free": {
                "name": "Gratuit",
                "price": 0,
                "description": "Pour decouvrir BIONIC HUNT/Chasse",
                "features": ["3 strategies/jour", "2 zones", "7 jours d'historique"]
            },
            "premium": {
                "name": "Premium",
                "monthly_price": 9.99,
                "yearly_price": 99.99,
                "description": "Pour les chasseurs reguliers",
                "features": ["50 strategies/jour", "10 zones", "90 jours d'historique", "Regles personnalisees", "Export PDF"]
            },
            "pro": {
                "name": "Pro",
                "monthly_price": 19.99,
                "yearly_price": 199.99,
                "description": "Pour les chasseurs experts",
                "features": ["Illimite", "Support prioritaire", "1 an d'historique", "Toutes les fonctionnalites"]
            }
        }
    }

