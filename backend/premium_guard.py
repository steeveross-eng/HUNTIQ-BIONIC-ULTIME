"""
Premium Guard — FastAPI Dependencies for PREMIUM Tier Gating
=============================================================

Separation AUTH / PREMIUM — R7 BCE-4X ULTIME ABSOLU

Usage dans les endpoints:
    from premium_guard import require_premium, require_feature

    @router.get("/premium-data")
    async def get_data(user_id: str = Depends(require_premium)):
        # Accessible uniquement aux utilisateurs PREMIUM ou PRO
        pass

    @router.get("/export")
    async def export_data(user_id: str = Depends(require_feature("export_reports"))):
        # Accessible uniquement si la feature est activee pour le tier
        pass

Version: 1.0.0
Directive: R7 — Externalisation PREMIUM
Protocol: BCE-4X GOLDEN V6+ | STEEVE-MAX
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Callable
from datetime import datetime, timezone, timedelta
import jwt
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# JWT Configuration — reuse les memes clefs que auth_helpers / roles_engine
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "huntiq_default_secret_change_me")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

security = HTTPBearer(auto_error=False)

# Database connection (lazy singleton)
_db: Optional[AsyncIOMotorDatabase] = None


def _get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        _db = client[db_name]
    return _db


# Tier definitions — source unique (importee par freemium_engine)
TIERS = ("free", "premium", "pro")
TIER_HIERARCHY = {"free": 0, "premium": 1, "pro": 2}

# Feature access matrix — source unique
TIER_LIMITS = {
    "free": {
        "daily_strategy_generations": 3,
        "daily_weather_checks": 10,
        "territory_zones": 2,
        "waypoints_per_zone": 5,
        "analytics_history_days": 7,
        "ai_recommendations": 5,
        "plan_maitre_phases": 2,
        "export_reports": False,
        "custom_rules": False,
        "priority_support": False,
        "advanced_layers": False,
        "live_heading": False,
    },
    "premium": {
        "daily_strategy_generations": 50,
        "daily_weather_checks": 100,
        "territory_zones": 10,
        "waypoints_per_zone": 50,
        "analytics_history_days": 90,
        "ai_recommendations": 50,
        "plan_maitre_phases": 5,
        "export_reports": True,
        "custom_rules": True,
        "priority_support": False,
        "advanced_layers": True,
        "live_heading": True,
    },
    "pro": {
        "daily_strategy_generations": -1,
        "daily_weather_checks": -1,
        "territory_zones": -1,
        "waypoints_per_zone": -1,
        "analytics_history_days": 365,
        "ai_recommendations": -1,
        "plan_maitre_phases": 5,
        "export_reports": True,
        "custom_rules": True,
        "priority_support": True,
        "advanced_layers": True,
        "live_heading": True,
    },
}


def _decode_token(token: str) -> Optional[dict]:
    """Decode JWT — meme logique que auth_helpers.decode_token"""
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def _extract_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None,
) -> Optional[str]:
    """Extract token from header, cookie, or query param"""
    if credentials and credentials.credentials:
        return credentials.credentials
    token = request.cookies.get("session_token")
    if token:
        return token
    return request.query_params.get("token")


async def _get_user_tier(user_id: str) -> str:
    """Resolve user subscription tier from DB"""
    db = _get_db()
    sub = await db.subscriptions.find_one({"user_id": user_id}, {"_id": 0})
    if not sub:
        return "free"
    # Check expiration
    expires = sub.get("expires_at")
    if expires and expires < datetime.now(timezone.utc):
        return "free"
    return sub.get("tier", "free")


async def _get_user_id_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Extract and validate user_id from JWT. Raises 401 if invalid."""
    token = _extract_token(request, credentials)
    if not token:
        raise HTTPException(status_code=401, detail="Authentification requise")
    payload = _decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expire")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide: sub manquant")
    return user_id


# ==============================================
# PUBLIC DEPENDENCIES — Utilisation via Depends()
# ==============================================

async def require_premium(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """
    FastAPI Dependency — Require PREMIUM or PRO tier.
    Returns user_id if authorized, raises 403 otherwise.

    Usage:
        @router.get("/premium-endpoint")
        async def endpoint(user_id: str = Depends(require_premium)):
            ...
    """
    user_id = await _get_user_id_from_request(request, credentials)
    tier = await _get_user_tier(user_id)
    if TIER_HIERARCHY.get(tier, 0) < TIER_HIERARCHY["premium"]:
        raise HTTPException(
            status_code=403,
            detail="Abonnement PREMIUM ou PRO requis",
            headers={"X-Required-Tier": "premium"},
        )
    return user_id


async def require_pro(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """
    FastAPI Dependency — Require PRO tier.
    Returns user_id if authorized, raises 403 otherwise.
    """
    user_id = await _get_user_id_from_request(request, credentials)
    tier = await _get_user_tier(user_id)
    if TIER_HIERARCHY.get(tier, 0) < TIER_HIERARCHY["pro"]:
        raise HTTPException(
            status_code=403,
            detail="Abonnement PRO requis",
            headers={"X-Required-Tier": "pro"},
        )
    return user_id


def require_feature(feature_name: str) -> Callable:
    """
    Factory — Returns a FastAPI Dependency that checks feature access.

    Usage:
        @router.get("/export")
        async def export(user_id: str = Depends(require_feature("export_reports"))):
            ...
    """
    async def _guard(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    ) -> str:
        user_id = await _get_user_id_from_request(request, credentials)
        tier = await _get_user_tier(user_id)
        limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
        feature_value = limits.get(feature_name)
        if feature_value is None:
            raise HTTPException(status_code=403, detail=f"Feature inconnue: {feature_name}")
        if isinstance(feature_value, bool) and not feature_value:
            raise HTTPException(
                status_code=403,
                detail=f"Feature '{feature_name}' non disponible pour le tier {tier}",
                headers={"X-Required-Tier": "premium", "X-Feature": feature_name},
            )
        if isinstance(feature_value, int) and feature_value == 0:
            raise HTTPException(
                status_code=403,
                detail=f"Quota epuise pour '{feature_name}'",
                headers={"X-Required-Tier": "premium", "X-Feature": feature_name},
            )
        return user_id

    _guard.__name__ = f"require_feature_{feature_name}"
    return _guard


async def check_quota(user_id: str, feature_name: str) -> dict:
    """
    Utility — Check remaining quota for a feature.
    Non-blocking, returns quota status dict.

    Usage:
        quota = await check_quota(user_id, "daily_strategy_generations")
        if quota["remaining"] == 0:
            ...
    """
    tier = await _get_user_tier(user_id)
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    limit = limits.get(feature_name, 0)
    if limit == -1:
        return {"feature": feature_name, "used": 0, "limit": -1, "remaining": -1, "unlimited": True}
    db = _get_db()
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    usage = await db.quota_usage.find_one(
        {"user_id": user_id, "feature": feature_name, "date": {"$gte": today, "$lt": tomorrow}},
        {"_id": 0},
    )
    used = usage.get("count", 0) if usage else 0
    remaining = max(0, limit - used)
    return {
        "feature": feature_name,
        "used": used,
        "limit": limit,
        "remaining": remaining,
        "unlimited": False,
        "reset_at": tomorrow.isoformat(),
    }
