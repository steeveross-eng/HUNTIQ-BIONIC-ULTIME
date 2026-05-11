"""
CASCADE_CACHE_OMEGA · LATENCE_P22J_OPTIM · TTL 30 min
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Cache LRU avec TTL pour réduire la latence cascade SPECTRAL→TERRAIN_HR→GIS.
- TTL : 30 minutes (commande COMMANDANT 2026-05-10)
- Quantization clef : lat/lon arrondis à 4 décimales (~11m précision)
- Max size : 256 entries (LRU eviction)
- Anti-générique : ne CACHE que des résultats RÉELS calculés (jamais de mock)

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW MODULE
"""

from __future__ import annotations

import logging
import time
from collections import OrderedDict
from threading import Lock
from typing import Any, Callable

logger = logging.getLogger("cascade_cache_omega")

CACHE_TTL_SECONDS = 1800   # 30 minutes
CACHE_MAX_SIZE = 256
CACHE_KEY_PRECISION = 4    # 4 décimales = ~11m précision lat/lon


class TTLCacheOmega:
    """Cache LRU + TTL thread-safe pour cascade et autres pipelines lourds."""

    def __init__(self, max_size: int = CACHE_MAX_SIZE,
                  ttl_seconds: int = CACHE_TTL_SECONDS):
        self._cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def _make_key(self, *args: Any, **kwargs: Any) -> str:
        """Génère une clef stable. Lat/Lon quantizés à 4 décimales."""
        norm_args: list[str] = []
        for a in args:
            if isinstance(a, float):
                norm_args.append(f"{round(a, CACHE_KEY_PRECISION):.4f}")
            else:
                norm_args.append(str(a))
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if isinstance(v, float):
                norm_args.append(f"{k}={round(v, CACHE_KEY_PRECISION):.4f}")
            else:
                norm_args.append(f"{k}={v}")
        return "|".join(norm_args)

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            timestamp, value = self._cache[key]
            if time.time() - timestamp > self._ttl_seconds:
                # Expired
                del self._cache[key]
                self._misses += 1
                return None
            # Hit — move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            self._cache[key] = (time.time(), value)
            if len(self._cache) > self._max_size:
                self._cache.popitem(last=False)
                self._evictions += 1

    def cached(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Décorateur — cache les résultats par signature d'arguments."""
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = self._make_key(fn.__name__, *args, **kwargs)
            cached_val = self.get(key)
            if cached_val is not None:
                logger.debug("[CACHE_HIT] %s", key[:60])
                return cached_val
            result = fn(*args, **kwargs)
            self.set(key, result)
            logger.debug("[CACHE_MISS_STORE] %s", key[:60])
            return result
        return wrapper

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl_seconds,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate_pct": round(hit_rate * 100.0, 1),
                "doctrine": "CASCADE_CACHE_Ω · P22J_LATENCE_OPTIM",
            }

    def clear(self) -> int:
        with self._lock:
            n = len(self._cache)
            self._cache.clear()
            return n


# Cache global singleton
_GLOBAL_CASCADE_CACHE = TTLCacheOmega()


def get_cascade_cache() -> TTLCacheOmega:
    """Retourne le cache singleton."""
    return _GLOBAL_CASCADE_CACHE
