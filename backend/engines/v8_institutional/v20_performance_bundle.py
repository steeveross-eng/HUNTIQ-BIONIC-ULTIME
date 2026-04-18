"""
V20 PERFORMANCE BUNDLE — PHASE-PERFORMANCE-Omega
=================================================
Endpoint pre-calcule + cache TTL 24h pour Territoire-Omega.
Objectif: < 1s loading (cache hit < 50ms).

Cache strategy:
  - Cle: (lat_snap, lon_snap, species, month, hour, wind_deg_snap)
  - Quantification: 3 decimales lat/lon (precision ~100m), wind_deg arrondi a 15deg
  - TTL: 24h (86400s)
  - LRU soft-cap 256 entrees
  - Browser cache: Cache-Control public max-age=3600, stale-while-revalidate=82800

ZERO recalcul si cache hit. ZERO fallback. ZERO degradation.
"""
import time
import logging
from collections import OrderedDict
from fastapi import APIRouter, Query, Response

logger = logging.getLogger("bionic.v20_performance")
router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Performance Bundle"])

# ═══ CACHE IN-MEMORY TTL 24h ═══
_CACHE: "OrderedDict[str, tuple[float, dict]]" = OrderedDict()
_CACHE_TTL_SEC = 86400  # 24h
_CACHE_MAX = 256

_STATS = {"hits": 0, "misses": 0, "evictions": 0, "total_compute_ms": 0}


def _cache_key(lat: float, lon: float, species: str, month: int, hour: int, wind_deg: float) -> str:
    lat_s = f"{lat:.3f}"
    lon_s = f"{lon:.3f}"
    wd_s = int(round(wind_deg / 15.0) * 15) % 360
    return f"{lat_s}_{lon_s}_{species}_{month}_{hour}_w{wd_s}"


def _cache_get(key: str):
    entry = _CACHE.get(key)
    if not entry:
        return None
    ts, payload = entry
    if time.time() - ts > _CACHE_TTL_SEC:
        try:
            del _CACHE[key]
        except KeyError:
            pass
        return None
    # Move to end (LRU touch)
    _CACHE.move_to_end(key)
    return payload


def _cache_set(key: str, payload: dict):
    _CACHE[key] = (time.time(), payload)
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)
        _STATS["evictions"] += 1


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
    """V20 PERFORMANCE BUNDLE — Cache-first Territoire rendering.

    - Cache hit: <50ms, served from memory.
    - Cache miss: full V20-INSTITUTIONNEL compute, then cached 24h.
    - Browser Cache-Control: public max-age=3600 stale-while-revalidate=82800.
    """
    t0 = time.time()
    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = _cache_get(key)

    if cached is not None:
        _STATS["hits"] += 1
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=82800"
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Age-Sec"] = str(int(time.time() - _CACHE[key][0]))
        response.headers["X-Compute-Ms"] = str(elapsed_ms)
        # Shallow copy with updated meta
        out = dict(cached)
        out["cache"] = "HIT"
        out["cache_age_sec"] = int(time.time() - _CACHE[key][0])
        out["served_ms"] = elapsed_ms
        return out

    # ═══ CACHE MISS — full compute ═══
    _STATS["misses"] += 1
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.esi_omega import validate_bundle, _log_audit

    result = await compute_territoire_v10(lat, lon, species, month, hour, wind_deg, wind_speed)

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

    # Cache store
    _cache_set(key, result)

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    _STATS["total_compute_ms"] += elapsed_ms

    response.headers["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=82800"
    response.headers["X-Cache"] = "MISS"
    response.headers["X-Compute-Ms"] = str(elapsed_ms)

    result["cache"] = "MISS"
    result["served_ms"] = elapsed_ms
    return result


@router.get("/bundle/stats")
async def v20_bundle_stats():
    """Statistiques cache TTL-24h."""
    total = _STATS["hits"] + _STATS["misses"]
    hit_ratio = (_STATS["hits"] / total * 100) if total > 0 else 0.0
    return {
        "cache_size": len(_CACHE),
        "cache_max": _CACHE_MAX,
        "cache_ttl_sec": _CACHE_TTL_SEC,
        "hits": _STATS["hits"],
        "misses": _STATS["misses"],
        "evictions": _STATS["evictions"],
        "hit_ratio_pct": round(hit_ratio, 2),
        "total_compute_ms": _STATS["total_compute_ms"],
    }


@router.post("/bundle/purge")
async def v20_bundle_purge():
    """Purge totale du cache (ops maintenance)."""
    n = len(_CACHE)
    _CACHE.clear()
    return {"purged": n, "ok": True}
