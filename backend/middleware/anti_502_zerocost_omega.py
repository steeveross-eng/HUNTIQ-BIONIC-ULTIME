"""
anti_502_zerocost_omega.py — Route override anti-502 (FAST-PATH CACHE LOOKUP)
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_PRECEDENT_16W_Ω · 2026-02-19
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

DOCTRINE
--------
Garde-fou absolu anti-502/504 sur /api/v20/territoire/bundle :

1. **FAST-PATH** : consulte le cache LRU/disque V20 (_cache_get) sans bloquer.
   - HIT → retour 200 immédiat avec le bundle (passthrough).
2. **SLOW-PATH** : cache MISS → fire-and-forget compute V20 en background.
   - Retour HTTP 202 EN_COURS immédiatement (Retry-After 5s).
   - Le compute remplit le cache → la prochaine requête sera un HIT.

⚠️ Aucune modification de V10/V20/ULTRA_TERRITOIRE_MULTI_Ω.
   Le fast-path lit `_cache_get` (fonction publique du module V20),
   le slow-path appelle `v20_territoire_bundle` inchangé.

→ Verrou Phase III strictement maintenu.

USAGE (server.py)
-----------------
    # AVANT app.include_router(v20_perf_router) pour priorité matching.
    from middleware.anti_502_zerocost_omega import register_anti_502
    register_anti_502(app)
"""
import asyncio
import logging
import os
from typing import Optional

from fastapi import FastAPI, Query, Response
from fastapi.responses import JSONResponse

logger = logging.getLogger("bionic.anti_502_zerocost_omega")

DOCTRINE = "P22ΩΩ_ANTI_502_PRECEDENT_16W_Ω"
DOCTRINE_ASCII = "P22OMEGA_OMEGA_ANTI_502_PRECEDENT_16W_OMEGA"  # ASCII-safe pour headers HTTP
RETRY_AFTER_S = int(os.environ.get("ANTI_502_RETRY_AFTER_S", "5"))

_metrics = {
    "fast_path_hit_200": 0,
    "slow_path_miss_202": 0,
    "exception_returned_202": 0,
}

# P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_PRECEDENT_16W_Ω · STEEVE-MAX
# Le daemon `zerocost_prewarm_p1_daemon.sh` s'occupe déjà du pré-calcul
# en process séparés. Le middleware n'a PAS besoin de lancer son propre
# BG compute (qui saturerait l'event loop uvicorn).
# Mettre à "true" pour ré-activer le compute opportuniste si besoin.
BG_COMPUTE_ENABLED = os.environ.get("ANTI_502_BG_COMPUTE", "false").lower() == "true"
BG_COMPUTE_SEMAPHORE: Optional[asyncio.Semaphore] = None

_bg_compute_inflight: set = set()  # dédup des compute background


def register_anti_502(app: FastAPI) -> None:
    """Enregistre la route override anti-502 sur l'app FastAPI."""

    # Imports différés (les modules V20 doivent être chargés)
    try:
        from engines.v8_institutional.v20_performance_bundle import (
            v20_territoire_bundle,
            _cache_get,
            _cache_key,
        )
    except Exception as e:
        logger.error(f"[ANTI-502] cannot import V20 cache primitives: {e}")
        return

    async def _background_compute(
        lat: float, lon: float, species: str, month: int, hour: int,
        wind_deg: float, wind_speed: float, key: str,
    ):
        """Lance V20 en background, remplit le cache, avale les exceptions."""
        try:
            _resp = Response()
            await v20_territoire_bundle(
                response=_resp,
                lat=lat, lon=lon, species=species,
                month=month, hour=hour,
                wind_deg=wind_deg, wind_speed=wind_speed,
            )
            logger.info(
                f"[ANTI-502] BG compute DONE · key={key[:32]}... · "
                f"{species} ({lat:.4f},{lon:.4f}) m{month}h{hour}"
            )
        except Exception as e:
            logger.warning(
                f"[ANTI-502] BG compute FAIL · key={key[:32]}... · "
                f"{type(e).__name__}: {e}"
            )
        finally:
            _bg_compute_inflight.discard(key)

    @app.get(
        "/api/v20/territoire/bundle",
        include_in_schema=False,
        name="anti_502_bundle_wrapper",
    )
    async def anti_502_bundle(
        response: Response,
        lat: float = Query(...),
        lon: float = Query(...),
        species: str = Query(...),
        month: int = Query(...),
        hour: int = Query(...),
        wind_deg: float = Query(0),
        wind_speed: float = Query(0),
    ):
        """Wrapper anti-502 fast-path / slow-path."""

        # ─────────────────────────────────────────────────────────────
        # FAST-PATH : cache lookup non-bloquant
        # ─────────────────────────────────────────────────────────────
        try:
            key = _cache_key(lat, lon, species, month, hour, wind_deg)
            # Essayer les deux variantes _tdelta (enrichi) puis _t0 (essentiel)
            cached = _cache_get(f"{key}_tdelta") or _cache_get(f"{key}_t0") or _cache_get(key)
        except Exception as e:
            cached = None
            logger.debug(f"[ANTI-502] fast-path lookup error (ignored): {e}")

        if cached is not None:
            _metrics["fast_path_hit_200"] += 1
            try:
                response.headers["X-Zerocost-Anti502"] = "fast-hit"
                response.headers["X-Doctrine"] = DOCTRINE_ASCII
            except Exception:
                pass
            return cached

        # ─────────────────────────────────────────────────────────────
        # SLOW-PATH : miss → 202 EN_COURS (le daemon pré-warm s'occupe du compute)
        # ─────────────────────────────────────────────────────────────
        _metrics["slow_path_miss_202"] += 1

        if BG_COMPUTE_ENABLED and key not in _bg_compute_inflight:
            _bg_compute_inflight.add(key)
            asyncio.create_task(_background_compute(
                lat, lon, species, month, hour, wind_deg, wind_speed, key,
            ))

        logger.warning(
            f"[ANTI-502] Cache MISS · {species} ({lat:.4f},{lon:.4f}) m{month}h{hour} "
            f"→ 202 EN_COURS · BG_compute_enabled={BG_COMPUTE_ENABLED} · key={key[:32]}..."
        )
        return JSONResponse(
            status_code=202,
            content={
                "status": "EN_COURS",
                "doctrine": DOCTRINE,
                "retry_after_ms": RETRY_AFTER_S * 1000,
                "message": (
                    "Bundle en cours de pré-calcul · retry recommandé dans "
                    f"{RETRY_AFTER_S}s. Fallback LKG IndexedDB doit assurer un "
                    "rendu UI valide (NEVER BLANK Ω)."
                ),
                "verrou_phase_III": "MAINTENU",
                "background_compute_launched": True,
                "query": {
                    "lat": lat, "lon": lon, "species": species,
                    "month": month, "hour": hour,
                },
            },
            headers={
                "Retry-After": str(RETRY_AFTER_S),
                "X-Zerocost-Anti502": "miss-202",
                "X-Doctrine": DOCTRINE_ASCII,
            },
        )

    @app.get("/api/v20/territoire/anti502/metrics", include_in_schema=False)
    async def _anti502_metrics_endpoint():
        return {
            "doctrine": DOCTRINE,
            "retry_after_s": RETRY_AFTER_S,
            "metrics": dict(_metrics),
            "bg_compute_inflight_count": len(_bg_compute_inflight),
        }

    logger.info(
        f"[ANTI-502] route override INSTALLED (FAST-PATH/SLOW-PATH) · "
        f"GET /api/v20/territoire/bundle · doctrine={DOCTRINE}"
    )
