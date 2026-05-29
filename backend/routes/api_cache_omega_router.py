"""
api_cache_omega_router.py — Router status cache LRU APIs
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_APIS_CACHE_SAFE_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III · LECTURE SEULE STRICTE · expose métriques cache uniquement.

ENDPOINTS
---------
  GET /api/v30/api-cache/status         → métriques live (hits/misses/hit_rate)
  POST /api/v30/api-cache/purge-expired → purge entries expirées (idempotent)
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

logger = logging.getLogger("bionic.api_cache_omega_router")

router = APIRouter(prefix="/api/v30/api-cache", tags=["api-cache"])

try:
    from integrations import api_cache_omega as CACHE
except ImportError as e:
    logger.error(f"[API_CACHE_Ω_ROUTER] import failed: {e}")
    CACHE = None  # type: ignore


@router.get("/status")
def status_endpoint() -> Dict[str, Any]:
    if CACHE is None:
        raise HTTPException(status_code=503, detail="api_cache_omega unavailable")
    return {"served_by": "API-CACHE-Ω-ROUTER", **CACHE.get_stats()}


@router.post("/purge-expired")
def purge_expired_endpoint() -> Dict[str, Any]:
    if CACHE is None:
        raise HTTPException(status_code=503, detail="api_cache_omega unavailable")
    n = CACHE.purge_expired()
    return {
        "served_by": "API-CACHE-Ω-ROUTER",
        "purged_count": n,
        "stats_after": CACHE.get_stats(),
    }
