"""
MAP-PERF-Omega: Server-side in-memory cache and preload endpoint.
Reduces map load time to < 1 second via bundled data + TTL cache.
"""
import time
import hashlib
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/map", tags=["Map Performance"])

# ============================================
# IN-MEMORY CACHE WITH TTL
# ============================================
_CACHE = {}
_CACHE_TTL = 300  # 5 minutes default

def _cache_key(user_id: str, data_type: str) -> str:
    return f"{user_id}:{data_type}"

def _get_cached(key: str, ttl: int = _CACHE_TTL):
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["ts"]) < ttl:
        return entry["data"]
    return None

def _set_cached(key: str, data):
    _CACHE[key] = {"data": data, "ts": time.time()}


# ============================================
# PRELOAD ENDPOINT — Bundles ALL map layers
# ============================================
@router.get("/preload")
async def preload_map_data(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    MAP-PERF-Omega: Single endpoint that returns ALL map data for initial load.
    Replaces N separate API calls with 1 bundled response.
    Cached server-side for 5 minutes per user.
    GZip compressed via middleware.
    """
    cache_key = _cache_key(user.user_id, "preload")
    cached = _get_cached(cache_key)
    if cached:
        return {**cached, "_cached": True}

    start = time.time()

    # 1. Cameras with GPS (lightweight projection)
    cameras_cursor = db['cameras'].find(
        {"user_id": user.user_id, "status": "active"},
        {"_id": 0, "raw_image_url": 0, "api_secret": 0, "external_account": 0}
    ).limit(200)
    cameras = await cameras_cursor.to_list(length=200)

    # 2. Vision hotspots (pre-generated)
    hotspots_cursor = db['vision_hotspots'].find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("score", -1).limit(100)
    hotspots = await hotspots_cursor.to_list(length=100)

    # 3. Trajectories (pre-generated)
    traj_cursor = db['vision_trajectories'].find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(50)
    trajectories = await traj_cursor.to_list(length=50)

    # 4. Camera events summary (species counts, recent activity)
    species_pipeline = [
        {"$match": {"user_id": user.user_id, "species": {"$nin": [None, "", "aucun_animal"]}}},
        {"$group": {"_id": "$species", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20}
    ]
    species_summary = await db['vision_analyses'].aggregate(species_pipeline).to_list(length=20)

    elapsed_ms = round((time.time() - start) * 1000)

    result = {
        "cameras": cameras,
        "hotspots": hotspots,
        "trajectories": trajectories,
        "species_summary": [{"species": s["_id"], "count": s["count"]} for s in species_summary],
        "counts": {
            "cameras": len(cameras),
            "hotspots": len(hotspots),
            "trajectories": len(trajectories)
        },
        "load_ms": elapsed_ms,
        "_cached": False
    }

    _set_cached(cache_key, result)
    logger.info(f"[MAP-PERF] Preload for {user.user_id}: {elapsed_ms}ms, {len(cameras)} cams, {len(hotspots)} hotspots")
    return result


@router.delete("/cache")
async def invalidate_cache(
    user: UserWithRole = Depends(get_current_user_with_role)
):
    """Invalidate user's map cache (after camera update, new photo, etc.)"""
    keys_to_remove = [k for k in _CACHE if k.startswith(f"{user.user_id}:")]
    for k in keys_to_remove:
        del _CACHE[k]
    return {"success": True, "cleared": len(keys_to_remove)}
