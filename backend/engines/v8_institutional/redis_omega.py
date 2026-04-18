"""
REDIS-Ω — Backend cache partage multi-pod
==========================================
PHASE-REDIS-Omega — Scalabilite >10K utilisateurs.

Comportement:
  - Si REDIS_URL env est defini: utilise Redis (partage cross-pods).
  - Sinon: fallback silencieux sur LRU in-memory (comportement V11-SUPRA actuel).
  - API uniforme: redis_get / redis_set / redis_del / redis_stats.

Cle namespace: "v20:territoire:bundle:<key>"
Serialisation: pickle (meme format que cache disque).
TTL: 24h (86400s).

Aucune regression: si Redis indisponible, logs warning et fallback LRU.
"""
import os
import pickle
import logging
from typing import Any, Optional

logger = logging.getLogger("bionic.redis_omega")

_REDIS_NAMESPACE = "v20:territoire:bundle:"
_REDIS_NAMESPACE_TILES = "v20:territoire:tiles:"
_REDIS_DEFAULT_TTL = 86400

_redis_client = None
_redis_enabled = False
_redis_url = os.environ.get("REDIS_URL")


def _init_redis():
    """Lazy init du client Redis. Idempotent."""
    global _redis_client, _redis_enabled
    if _redis_client is not None:
        return
    if not _redis_url:
        logger.info("[REDIS-Omega] REDIS_URL non defini — fallback LRU in-memory")
        _redis_enabled = False
        return
    try:
        import redis
        _redis_client = redis.from_url(
            _redis_url,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
            retry_on_timeout=False,
            decode_responses=False,  # binary pour pickle
            max_connections=64,
        )
        # Ping test
        _redis_client.ping()
        _redis_enabled = True
        logger.info(f"[REDIS-Omega] CONNECTED — {_redis_url}")
    except Exception as e:
        logger.warning(f"[REDIS-Omega] Connect failed ({e}) — fallback LRU in-memory")
        _redis_client = None
        _redis_enabled = False


def is_redis_enabled() -> bool:
    _init_redis()
    return _redis_enabled


def redis_get(key: str, tiles: bool = False) -> Optional[Any]:
    """Recupere une entree depuis Redis. None si miss ou Redis off."""
    _init_redis()
    if not _redis_enabled:
        return None
    try:
        full_key = (_REDIS_NAMESPACE_TILES if tiles else _REDIS_NAMESPACE) + key
        raw = _redis_client.get(full_key)
        if raw is None:
            return None
        return pickle.loads(raw)
    except Exception as e:
        logger.warning(f"[REDIS-Omega] GET failed for {key}: {e}")
        return None


def redis_set(key: str, value: Any, ttl: int = _REDIS_DEFAULT_TTL, tiles: bool = False) -> bool:
    """Stocke une entree dans Redis avec TTL. False si Redis off."""
    _init_redis()
    if not _redis_enabled:
        return False
    try:
        full_key = (_REDIS_NAMESPACE_TILES if tiles else _REDIS_NAMESPACE) + key
        data = pickle.dumps(value)
        _redis_client.setex(full_key, ttl, data)
        return True
    except Exception as e:
        logger.warning(f"[REDIS-Omega] SET failed for {key}: {e}")
        return False


def redis_del(key: str, tiles: bool = False) -> bool:
    _init_redis()
    if not _redis_enabled:
        return False
    try:
        full_key = (_REDIS_NAMESPACE_TILES if tiles else _REDIS_NAMESPACE) + key
        _redis_client.delete(full_key)
        return True
    except Exception:
        return False


def redis_purge() -> int:
    """Purge tout le namespace v20:territoire:*. Retourne le nombre de cles supprimees."""
    _init_redis()
    if not _redis_enabled:
        return 0
    try:
        deleted = 0
        for prefix in (_REDIS_NAMESPACE, _REDIS_NAMESPACE_TILES):
            for k in _redis_client.scan_iter(match=prefix + "*", count=500):
                _redis_client.delete(k)
                deleted += 1
        return deleted
    except Exception as e:
        logger.warning(f"[REDIS-Omega] PURGE failed: {e}")
        return 0


def redis_stats() -> dict:
    _init_redis()
    if not _redis_enabled:
        return {"enabled": False, "reason": "REDIS_URL non defini ou connect failed"}
    try:
        info = _redis_client.info(section="memory")
        keys_bundle = len(list(_redis_client.scan_iter(match=_REDIS_NAMESPACE + "*", count=500)))
        keys_tiles = len(list(_redis_client.scan_iter(match=_REDIS_NAMESPACE_TILES + "*", count=500)))
        return {
            "enabled": True,
            "url": _redis_url.split("@")[-1] if _redis_url and "@" in _redis_url else _redis_url,
            "bundle_keys": keys_bundle,
            "tile_keys": keys_tiles,
            "memory_used": info.get("used_memory_human"),
            "memory_peak": info.get("used_memory_peak_human"),
        }
    except Exception as e:
        return {"enabled": False, "reason": f"stats failed: {e}"}
