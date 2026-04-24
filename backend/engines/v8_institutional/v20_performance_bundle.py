"""
V20 PERFORMANCE BUNDLE — V11-SUPRA SCALABILITE 10K
=====================================================
PHASE-PERFORMANCE-Omega V11-SUPRA — 5000-10000 utilisateurs.

UPGRADES:
  - Cache LRU 1024 → 10 000 entrees
  - TTL 24h (inchange)
  - Cache disque persistant (/app/backend/cache/territoire_bundle.pkl)
  - Worker async PRECHAUFFAGE-Omega au startup + daemon refresh horaire
  - CDN-ready: Cache-Control + Vary
"""
import time
import pickle
import asyncio
import logging
import os
from pathlib import Path
from collections import OrderedDict
from fastapi import APIRouter, Query, Response, BackgroundTasks

logger = logging.getLogger("bionic.v20_performance")
router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Performance Bundle"])

# ═══ CACHE IN-MEMORY LRU TTL 24h — V11-SUPRA SCALABILITE 10K ═══
_CACHE: "OrderedDict[str, tuple[float, dict]]" = OrderedDict()
_CACHE_TTL_SEC = 86400
_CACHE_MAX = 10000  # V11-SUPRA: 1024 → 10000

# ═══ DISK PERSISTENCE ═══
_CACHE_DIR = Path("/app/backend/cache")
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CACHE_DISK_FILE = _CACHE_DIR / "territoire_bundle.pkl"

_STATS = {
    "hits": 0, "misses": 0, "evictions": 0, "total_compute_ms": 0,
    "warmup_runs": 0, "warmup_last_count": 0, "warmup_last_ms": 0,
    "disk_loaded": 0, "disk_saved": 0,
}


def _cache_key(lat: float, lon: float, species: str, month: int, hour: int, wind_deg: float) -> str:
    lat_s = f"{lat:.3f}"
    lon_s = f"{lon:.3f}"
    wd_s = int(round(wind_deg / 15.0) * 15) % 360
    return f"{lat_s}_{lon_s}_{species}_{month}_{hour}_w{wd_s}"


def _cache_get(key: str):
    # L2 local LRU
    entry = _CACHE.get(key)
    if entry:
        ts, payload = entry
        if time.time() - ts > _CACHE_TTL_SEC:
            _CACHE.pop(key, None)
        else:
            _CACHE.move_to_end(key)
            return payload
    # L1 Redis partage multi-pod (si disponible)
    try:
        from engines.v8_institutional.redis_omega import redis_get, is_redis_enabled
        if is_redis_enabled():
            val = redis_get(key)
            if val is not None:
                # Warm local LRU avec la valeur Redis
                _CACHE[key] = (time.time(), val)
                _CACHE.move_to_end(key)
                while len(_CACHE) > _CACHE_MAX:
                    _CACHE.popitem(last=False)
                    _STATS["evictions"] += 1
                return val
    except Exception:
        pass
    return None


def _cache_set(key: str, payload: dict):
    _CACHE[key] = (time.time(), payload)
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)
        _STATS["evictions"] += 1
    # Propagate to Redis (fire-and-forget)
    try:
        from engines.v8_institutional.redis_omega import redis_set, is_redis_enabled
        if is_redis_enabled():
            redis_set(key, payload, ttl=_CACHE_TTL_SEC)
    except Exception:
        pass


# ═══ DISK PERSISTENCE ═══
def _cache_save_disk():
    """Persist LRU to disk (called on shutdown + periodic)."""
    try:
        # Serialize only entries not expired
        valid = [(k, v) for k, v in _CACHE.items() if time.time() - v[0] < _CACHE_TTL_SEC]
        with open(_CACHE_DISK_FILE, "wb") as f:
            pickle.dump({"entries": valid, "saved_at": time.time()}, f)
        _STATS["disk_saved"] += 1
        logger.info(f"[V20-CACHE] Disk save: {len(valid)} entries → {_CACHE_DISK_FILE}")
        return len(valid)
    except Exception as e:
        logger.warning(f"[V20-CACHE] Disk save failed: {e}")
        return 0


def _cache_load_disk():
    """Load persisted cache from disk (called at startup)."""
    if not _CACHE_DISK_FILE.exists():
        return 0
    try:
        with open(_CACHE_DISK_FILE, "rb") as f:
            data = pickle.load(f)
        loaded = 0
        for k, (ts, payload) in data.get("entries", []):
            if time.time() - ts < _CACHE_TTL_SEC:
                _CACHE[k] = (ts, payload)
                loaded += 1
        _STATS["disk_loaded"] = loaded
        logger.info(f"[V20-CACHE] Disk load: {loaded} entries restored from {_CACHE_DISK_FILE}")
        return loaded
    except Exception as e:
        logger.warning(f"[V20-CACHE] Disk load failed: {e}")
        return 0


# ═══ PRECHAUFFAGE-Omega WORKER ═══
_WARMUP_LOCK = asyncio.Lock()
_WARMUP_SEMAPHORE = asyncio.Semaphore(8)  # 8 parallel computes max (worker async)


async def _warmup_single(lat: float, lon: float, species: str = "cerf"):
    """Compute + cache un seul waypoint."""
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    try:
        async with _WARMUP_SEMAPHORE:
            now = time.time()
            result = await compute_territoire_v10(lat, lon, species, 10, 7, 225.0, 15.0)
            key = _cache_key(lat, lon, species, 10, 7, 225.0)
            _cache_set(key, result)
            return time.time() - now
    except Exception as e:
        logger.warning(f"[V20-WARMUP] Failed {lat},{lon} {species}: {e}")
        return 0


async def _get_top_waypoints(limit: int = 200):
    """Fetch top waypoints from MongoDB (sorted by most recent activity)."""
    try:
        # Import lazily pour eviter circular import
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME", "hunt_iq_db")
        if not mongo_url:
            return []
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        # Top waypoints: actifs, trie par updated_at / created_at desc
        cursor = db.user_waypoints.find(
            {"active": {"$ne": False}},
            {"_id": 0, "lat": 1, "lng": 1, "latitude": 1, "longitude": 1, "species": 1}
        ).sort("created_at", -1).limit(limit)
        waypoints = []
        async for doc in cursor:
            lat = doc.get("lat") or doc.get("latitude")
            lng = doc.get("lng") or doc.get("longitude")
            sp = doc.get("species") or "cerf"
            if lat is not None and lng is not None:
                waypoints.append((float(lat), float(lng), sp))
        client.close()
        return waypoints
    except Exception as e:
        logger.warning(f"[V20-WARMUP] Top waypoints fetch failed: {e}")
        return []


async def run_prechauffage_omega(limit: int = 200):
    """PRECHAUFFAGE-Omega-INTELLIGENT: preload top N waypoints en parallele."""
    async with _WARMUP_LOCK:
        t0 = time.time()
        waypoints = await _get_top_waypoints(limit)
        if not waypoints:
            logger.info("[V20-WARMUP] Aucun waypoint a precharger")
            return {"warmed": 0, "elapsed_s": 0}
        # Deduplication par cle quantifiee
        seen = set()
        unique = []
        for lat, lon, sp in waypoints:
            k = _cache_key(lat, lon, sp, 10, 7, 225.0)
            if k not in seen and _cache_get(k) is None:
                seen.add(k)
                unique.append((lat, lon, sp))
        logger.info(f"[V20-WARMUP] Demarrage prechauffage: {len(unique)} waypoints (sur {len(waypoints)} retrouves)")
        # Lance en parallele (semaphore limite la concurrence a 8)
        tasks = [_warmup_single(lat, lon, sp) for lat, lon, sp in unique]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - t0
        warmed = sum(1 for r in results if isinstance(r, (int, float)) and r > 0)
        _STATS["warmup_runs"] += 1
        _STATS["warmup_last_count"] = warmed
        _STATS["warmup_last_ms"] = round(elapsed * 1000)
        # Save to disk post-warmup
        _cache_save_disk()
        logger.info(f"[V20-WARMUP] Prechauffage termine: {warmed}/{len(unique)} en {elapsed:.1f}s — Cache: {len(_CACHE)}/{ _CACHE_MAX}")
        return {"warmed": warmed, "attempted": len(unique), "elapsed_s": round(elapsed, 2)}


# ═══ LAZY-INIT GUARD (compatible uvicorn --reload) ═══
_LAZY_INIT_DONE = False
_LAZY_INIT_LOCK = asyncio.Lock()


async def _ensure_lazy_init():
    """Initialise au premier appel (disk load + prechauffage async). Idempotent."""
    global _LAZY_INIT_DONE
    if _LAZY_INIT_DONE:
        return
    async with _LAZY_INIT_LOCK:
        if _LAZY_INIT_DONE:
            return
        _LAZY_INIT_DONE = True
        loaded = _cache_load_disk()
        logger.info(f"[V20-LAZY-INIT] {loaded} entries loaded from disk")
        asyncio.create_task(run_prechauffage_omega(limit=200))
        asyncio.create_task(_periodic_refresh_daemon())


# ═══ LIFESPAN HOOKS (called from server.py startup/shutdown) ═══
async def v20_startup():
    """Called by server.py on app startup."""
    loaded = _cache_load_disk()
    logger.info(f"[V20-PERFORMANCE] Startup: {loaded} entries loaded from disk")
    asyncio.create_task(run_prechauffage_omega(limit=200))
    asyncio.create_task(_periodic_refresh_daemon())


async def v20_shutdown():
    """Called by server.py on app shutdown."""
    _cache_save_disk()


async def _periodic_refresh_daemon():
    """Daemon: rafraichit le cache toutes les 1h + save disk."""
    while True:
        try:
            await asyncio.sleep(3600)
            logger.info("[V20-WARMUP-DAEMON] Tick horaire — refresh + disk save")
            await run_prechauffage_omega(limit=200)
        except Exception as e:
            logger.warning(f"[V20-WARMUP-DAEMON] Error: {e}")


# ═══ ENDPOINTS ═══
@router.get("/bundle")
async def v20_territoire_bundle(
    response: Response,
    lat: float = Query(...),
    lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(10),
    hour: int = Query(7),
    wind_deg: float = Query(225),
    wind_speed: float = Query(15),
):
    """V20 PERFORMANCE BUNDLE — Cache-first Territoire rendering (10K scalabilite).

    - Cache hit: <50ms.
    - Cache miss: full V20-INSTITUTIONNEL compute, cached 24h.
    - Cache size: 10 000 entrees LRU.
    - Disk persistent: survived restart via /app/backend/cache/territoire_bundle.pkl.
    - Prechauffage: 200 top waypoints au startup + refresh horaire.
    """
    await _ensure_lazy_init()
    t0 = time.time()
    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = _cache_get(key)

    if cached is not None:
        _STATS["hits"] += 1
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=82800"
        response.headers["Vary"] = "Accept-Encoding"
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Age-Sec"] = str(int(time.time() - _CACHE[key][0]))
        response.headers["X-Compute-Ms"] = str(elapsed_ms)
        out = dict(cached)
        out["cache"] = "HIT"
        out["cache_age_sec"] = int(time.time() - _CACHE[key][0])
        out["served_ms"] = elapsed_ms
        return out

    _STATS["misses"] += 1
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.esi_omega import validate_bundle, _log_audit
    # PHASE_XII_SUPRA_RAPATRIEMENT_RENDUΩ_V20 — branchement obligatoire RenduΩ
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    # PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME — post-processor amont RenduΩ
    from engines.post_smoothing.veineux_omega import apply_veineux_omega_to_bundle
    # PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_INTERZONE_GENERATION — générateur inter-zones
    from engines.post_smoothing.interzone_omega import apply_interzone_omega_to_bundle

    result = await compute_territoire_v10(lat, lon, species, month, hour, wind_deg, wind_speed)

    # ═══════════════════════════════════════════════════════════════════════
    # RAPATRIEMENT_RENDUΩ_V20 — SECTION 1.1 / 1.2 / 1.3
    # Validation et filtrage ABSOLUS des corridors avant cache & envoi client.
    # Même moteur que POST /api/v7-ultime/renduomega/validate-bundle.
    # V30 LOCKED intact — seules les sorties de compute_territoire_v10 sont
    # filtrées ici ; le moteur institutionnel reste inchangé.
    # ═══════════════════════════════════════════════════════════════════════
    result["waypoint"] = {"lat": lat, "lng": lon}
    result["species"] = species
    # Normalisation `contamination_zones` pour RenduΩ :
    # V30 émet des cônes (polygones) sans lat/lng direct. RenduΩ attend des
    # points {lat,lng}. On dérive ici un point représentatif depuis
    # `affut_source` ou le centroïde du polygone — sans modifier V30.
    _contam_in = result.get("contamination") or []
    _contam_for_rom = []
    for _c in _contam_in:
        if not isinstance(_c, dict):
            continue
        _lat = _c.get("lat")
        _lng = _c.get("lng") or _c.get("lon")
        if _lat is None or _lng is None:
            _src = _c.get("affut_source") or {}
            _lat = _src.get("lat")
            _lng = _src.get("lng") or _src.get("lon")
        if _lat is None or _lng is None:
            _poly = _c.get("polygon") or _c.get("coords") or []
            if isinstance(_poly, list) and _poly:
                try:
                    _lat = sum(p[0] for p in _poly) / len(_poly)
                    _lng = sum(p[1] for p in _poly) / len(_poly)
                except Exception:
                    _lat = _lng = None
        if _lat is not None and _lng is not None:
            _contam_for_rom.append({"lat": float(_lat), "lng": float(_lng),
                                    "intensity": _c.get("intensity"),
                                    "source": "V20_RAPATRIEMENT_NORMALIZED"})
    result["contamination_zones"] = _contam_for_rom
    # ═══ INTERZONE_Ω — AJOUT des corridors inter-zones + entrants (V30 intact) ═══
    # Génère les corridors manquants (§2.3 liaison zones vitales) AVANT
    # le post-processing géométrique veineux.
    result = apply_interzone_omega_to_bundle(result)
    # ═══ VEINEUX_Ω — transformation géométrique amont (V30 intact) ═══
    result = apply_veineux_omega_to_bundle(result)
    result = apply_renduomega_to_bundle(result)

    bv = validate_bundle({
        "zones": result["zones"],
        "corridors": result["corridors"],
        "affuts": result["affuts"],
    })
    _log_audit(
        "V20_TERRITOIRE_BUNDLE_COMPUTE",
        f"{lat},{lon},{species}",
        f"{bv['conformite']} source={result.get('data_source')} fiabilite={result.get('data_fiabilite')}",
    )
    result["esi_omega"] = bv["conformite"]

    _cache_set(key, result)

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    _STATS["total_compute_ms"] += elapsed_ms

    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=82800"
    response.headers["Vary"] = "Accept-Encoding"
    response.headers["X-Cache"] = "MISS"
    response.headers["X-Compute-Ms"] = str(elapsed_ms)

    result["cache"] = "MISS"
    result["served_ms"] = elapsed_ms
    return result


@router.get("/bundle/stats")
async def v20_bundle_stats():
    await _ensure_lazy_init()
    from engines.v8_institutional.redis_omega import redis_stats
    total = _STATS["hits"] + _STATS["misses"]
    hit_ratio = (_STATS["hits"] / total * 100) if total > 0 else 0.0
    return {
        "cache_size": len(_CACHE),
        "cache_max": _CACHE_MAX,
        "cache_ttl_sec": _CACHE_TTL_SEC,
        "disk_file": str(_CACHE_DISK_FILE),
        "disk_exists": _CACHE_DISK_FILE.exists(),
        "disk_loaded_on_startup": _STATS["disk_loaded"],
        "disk_saved_count": _STATS["disk_saved"],
        "hits": _STATS["hits"],
        "misses": _STATS["misses"],
        "evictions": _STATS["evictions"],
        "hit_ratio_pct": round(hit_ratio, 2),
        "total_compute_ms": _STATS["total_compute_ms"],
        "warmup_runs": _STATS["warmup_runs"],
        "warmup_last_count": _STATS["warmup_last_count"],
        "warmup_last_ms": _STATS["warmup_last_ms"],
        "warmup_semaphore_max": 8,
        "redis_omega": redis_stats(),
    }


@router.post("/bundle/purge")
async def v20_bundle_purge():
    from engines.v8_institutional.redis_omega import redis_purge
    n = len(_CACHE)
    _CACHE.clear()
    try:
        if _CACHE_DISK_FILE.exists():
            _CACHE_DISK_FILE.unlink()
    except Exception:
        pass
    redis_deleted = redis_purge()
    return {"purged_lru": n, "disk_cleared": True, "redis_deleted": redis_deleted, "ok": True}


@router.post("/bundle/warmup")
async def v20_bundle_warmup(background: BackgroundTasks, limit: int = Query(200, ge=1, le=500)):
    """Lance manuellement le prechauffage (top N waypoints)."""
    background.add_task(run_prechauffage_omega, limit)
    return {"started": True, "limit": limit, "message": "PRECHAUFFAGE-Omega lance en background"}


@router.post("/bundle/save")
async def v20_bundle_save_disk():
    """Force la sauvegarde du cache en disque."""
    n = _cache_save_disk()
    return {"saved": n, "ok": True}
