"""
api_cache_omega.py — Cache LRU disque local 7 jours pour APIs externes
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_APIS_CACHE_SAFE_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · ADDITIF STRICT · ZÉRO IMPACT R2/CDN.

DOCTRINE
--------
Cache disque local SQLite (single-file, atomique, thread-safe natif) avec :
  - TTL configurable (défaut 7 jours = 604 800 s)
  - LRU eviction si taille DB > MAX_DB_BYTES (défaut 500 MB)
  - Keyed par hash(url + sorted_params + method + body_hash)
  - Sérialisation JSON (lecture-seule des réponses)
  - Cible : WorldPop / SoilGrids / Overpass · extensible via ALLOWED_DOMAINS
  - Soft-fail strict : si cache fail → fetch réseau direct (pas de blocage)

EMPLACEMENT
-----------
  /app/backend/cache/api_cache_omega/cache.sqlite3  (créé auto · idempotent)
  /app/backend/cache/api_cache_omega/stats.json     (métriques live · LECTURE SEULE)

API PUBLIQUE
------------
  get_cached(url, method, params, json_body) -> dict | None
  set_cached(url, method, params, json_body, response_data) -> None
  get_stats() -> dict
  purge_expired() -> int
  is_cacheable_url(url) -> bool
  reset_stats() -> None
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("bionic.api_cache_omega")

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════
CACHE_DIR = Path(os.environ.get(
    "API_CACHE_OMEGA_DIR", "/app/backend/cache/api_cache_omega"
))
CACHE_DB = CACHE_DIR / "cache.sqlite3"
STATS_FILE = CACHE_DIR / "stats.json"

DEFAULT_TTL_S = int(os.environ.get("API_CACHE_OMEGA_TTL_S", str(7 * 24 * 3600)))  # 7 jours
MAX_DB_BYTES = int(os.environ.get("API_CACHE_OMEGA_MAX_BYTES", str(500 * 1024 * 1024)))  # 500 MB
PURGE_EVERY_N_SETS = int(os.environ.get("API_CACHE_OMEGA_PURGE_EVERY", "200"))

ENABLED = os.environ.get("API_CACHE_OMEGA_ENABLED", "1") == "1"

# Domaines cibles (ne cache QUE ces APIs · anti-générique strict)
ALLOWED_DOMAINS = {
    "api.worldpop.org",
    "rest.isric.org",
    "overpass.osm.ch",
}

# Stats globales runtime (in-memory · sérialisées périodiquement)
_stats = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "expired_evicted": 0,
    "lru_evicted": 0,
    "errors": 0,
    "since": time.time(),
}
_stats_lock = threading.Lock()
_set_counter = 0
_db_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# INIT SQLITE
# ═══════════════════════════════════════════════════════════════════════════
def _ensure_db() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(CACHE_DB), timeout=10.0) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS api_cache (
                key TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                method TEXT NOT NULL,
                domain TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at REAL NOT NULL,
                last_access_at REAL NOT NULL,
                response_size INTEGER NOT NULL,
                ttl_seconds INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_last_access ON api_cache(last_access_at);
            CREATE INDEX IF NOT EXISTS idx_created ON api_cache(created_at);
            CREATE INDEX IF NOT EXISTS idx_domain ON api_cache(domain);
            """
        )
        conn.commit()


_ensure_db()


# ═══════════════════════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════════════════════
def _domain_of(url: str) -> str:
    try:
        # Skip schéma puis tronquer au premier /
        u = url.split("://", 1)[-1]
        return u.split("/", 1)[0].split("?", 1)[0]
    except Exception:
        return ""


def is_cacheable_url(url: str) -> bool:
    """True ssi URL appartient aux domaines cibles."""
    if not ENABLED:
        return False
    return _domain_of(url) in ALLOWED_DOMAINS


def _make_key(url: str, method: str, params: dict | None, json_body: dict | None) -> str:
    h = hashlib.sha256()
    h.update(method.upper().encode())
    h.update(b"\x00")
    h.update(url.encode())
    if params:
        h.update(b"\x00P\x00")
        h.update(json.dumps(params, sort_keys=True, separators=(",", ":")).encode())
    if json_body is not None:
        h.update(b"\x00J\x00")
        h.update(json.dumps(json_body, sort_keys=True, separators=(",", ":")).encode())
    return h.hexdigest()


def _bump_stat(key: str, n: int = 1) -> None:
    with _stats_lock:
        _stats[key] = _stats.get(key, 0) + n


# ═══════════════════════════════════════════════════════════════════════════
# API PUBLIQUE
# ═══════════════════════════════════════════════════════════════════════════
def get_cached(
    url: str,
    method: str = "GET",
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
) -> Optional[dict]:
    """Cache hit → dict response · cache miss/expired/error → None."""
    if not is_cacheable_url(url):
        return None
    try:
        key = _make_key(url, method, params, json_body)
        now = time.time()
        with _db_lock, sqlite3.connect(str(CACHE_DB), timeout=10.0) as conn:
            row = conn.execute(
                "SELECT response_json, created_at, ttl_seconds FROM api_cache WHERE key = ?",
                (key,),
            ).fetchone()
            if row is None:
                _bump_stat("misses")
                return None
            response_json, created_at, ttl = row
            if now - created_at > ttl:
                # Expired · evict on read
                conn.execute("DELETE FROM api_cache WHERE key = ?", (key,))
                conn.commit()
                _bump_stat("expired_evicted")
                _bump_stat("misses")
                return None
            # Cache hit · update last_access
            conn.execute(
                "UPDATE api_cache SET last_access_at = ? WHERE key = ?", (now, key)
            )
            conn.commit()
            _bump_stat("hits")
            return json.loads(response_json)
    except Exception as e:
        _bump_stat("errors")
        logger.debug(f"[API_CACHE_Ω] get_cached error: {e}")
        return None


def set_cached(
    url: str,
    method: str,
    params: Optional[dict],
    json_body: Optional[dict],
    response_data: dict,
    ttl_seconds: Optional[int] = None,
) -> None:
    """Stocke la réponse pour TTL configurable. Idempotent (UPSERT)."""
    if not is_cacheable_url(url):
        return
    # Ne pas cacher les erreurs
    if isinstance(response_data, dict) and "_error" in response_data:
        return
    try:
        key = _make_key(url, method, params, json_body)
        domain = _domain_of(url)
        ttl = ttl_seconds if ttl_seconds is not None else DEFAULT_TTL_S
        response_blob = json.dumps(response_data, separators=(",", ":"))
        size = len(response_blob.encode())
        now = time.time()
        with _db_lock, sqlite3.connect(str(CACHE_DB), timeout=10.0) as conn:
            conn.execute(
                """
                INSERT INTO api_cache
                    (key, url, method, domain, response_json, created_at, last_access_at, response_size, ttl_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    response_json = excluded.response_json,
                    created_at = excluded.created_at,
                    last_access_at = excluded.last_access_at,
                    response_size = excluded.response_size,
                    ttl_seconds = excluded.ttl_seconds
                """,
                (key, url, method.upper(), domain, response_blob, now, now, size, ttl),
            )
            conn.commit()
        _bump_stat("sets")

        # LRU eviction périodique
        global _set_counter
        _set_counter += 1
        if _set_counter % PURGE_EVERY_N_SETS == 0:
            _enforce_max_size()

    except Exception as e:
        _bump_stat("errors")
        logger.debug(f"[API_CACHE_Ω] set_cached error: {e}")


def _enforce_max_size() -> None:
    """LRU eviction si taille DB > MAX_DB_BYTES."""
    try:
        if not CACHE_DB.is_file():
            return
        size = CACHE_DB.stat().st_size
        if size <= MAX_DB_BYTES:
            return
        # Evict 20 % oldest by last_access_at
        with _db_lock, sqlite3.connect(str(CACHE_DB), timeout=10.0) as conn:
            total = conn.execute("SELECT COUNT(*) FROM api_cache").fetchone()[0]
            n_evict = max(1, total // 5)
            conn.execute(
                """
                DELETE FROM api_cache WHERE key IN (
                    SELECT key FROM api_cache ORDER BY last_access_at ASC LIMIT ?
                )
                """,
                (n_evict,),
            )
            conn.commit()
            conn.execute("VACUUM")
            _bump_stat("lru_evicted", n_evict)
    except Exception as e:
        _bump_stat("errors")
        logger.debug(f"[API_CACHE_Ω] enforce_max_size error: {e}")


def purge_expired() -> int:
    """Purge toutes les entrées expirées (TTL dépassé). Retourne le nombre supprimé."""
    try:
        now = time.time()
        with _db_lock, sqlite3.connect(str(CACHE_DB), timeout=10.0) as conn:
            cur = conn.execute(
                "DELETE FROM api_cache WHERE (created_at + ttl_seconds) < ?", (now,)
            )
            conn.commit()
            n = cur.rowcount
            _bump_stat("expired_evicted", n)
            return n
    except Exception as e:
        _bump_stat("errors")
        logger.debug(f"[API_CACHE_Ω] purge_expired error: {e}")
        return 0


def get_stats() -> dict:
    """Snapshot live des stats (read-only)."""
    try:
        with _db_lock, sqlite3.connect(str(CACHE_DB), timeout=10.0) as conn:
            total = conn.execute("SELECT COUNT(*) FROM api_cache").fetchone()[0]
            by_domain = dict(
                conn.execute(
                    "SELECT domain, COUNT(*) FROM api_cache GROUP BY domain"
                ).fetchall()
            )
            total_size = conn.execute(
                "SELECT COALESCE(SUM(response_size), 0) FROM api_cache"
            ).fetchone()[0]
    except Exception:
        total, by_domain, total_size = 0, {}, 0
    db_size = CACHE_DB.stat().st_size if CACHE_DB.is_file() else 0
    with _stats_lock:
        runtime = {**_stats}
    total_calls = runtime["hits"] + runtime["misses"]
    hit_rate = runtime["hits"] / total_calls if total_calls else 0.0
    return {
        "doctrine": "P22ΩΩ_APIS_CACHE_SAFE_Ω",
        "enabled": ENABLED,
        "ttl_seconds_default": DEFAULT_TTL_S,
        "max_db_bytes": MAX_DB_BYTES,
        "allowed_domains": sorted(ALLOWED_DOMAINS),
        "runtime_stats": runtime,
        "hit_rate": round(hit_rate, 3),
        "db_path": str(CACHE_DB),
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / 1024 / 1024, 2),
        "n_entries": total,
        "entries_by_domain": by_domain,
        "entries_total_size_bytes": total_size,
        "entries_total_size_mb": round(total_size / 1024 / 1024, 2),
    }


def reset_stats() -> None:
    """Reset stats runtime (DB inchangée)."""
    with _stats_lock:
        for k in ("hits", "misses", "sets", "expired_evicted", "lru_evicted", "errors"):
            _stats[k] = 0
        _stats["since"] = time.time()


__all__ = [
    "ENABLED", "DEFAULT_TTL_S", "MAX_DB_BYTES", "ALLOWED_DOMAINS",
    "is_cacheable_url", "get_cached", "set_cached",
    "get_stats", "purge_expired", "reset_stats",
]
