"""
OPEN-METEO CIRCUIT BREAKER GLOBAL — P22Σ_OPEN_METEO_CB_GLOBAL_Ω
================================================================
PHASE OMEGA+++ · 2026-05-12T19:00Z · COMMANDANT STEEVE-MAX

Module shared utilisé par TOUS les engines qui appellent Open-Meteo
(lidar_irda_v11, terrain_hr_omega, terrain_v10_supra, supra_donnees,
weather_v3, etc.) pour éviter l'avalanche de 429 Too Many Requests.

Logique :
  - Compte les erreurs récentes (fenêtre 60s)
  - Si seuil atteint (5 erreurs) → OPEN circuit 300s
  - Pendant OPEN → toute requête retourne None immédiatement
  - Après cooldown → réessai automatique
"""
import time
import logging
from typing import Optional

logger = logging.getLogger("bionic.open_meteo_breaker")

_STATE = {
    "errors_recent": [],
    "open_until": 0.0,
    # P22Ω_PHASE1_P1_FIXES (E2) · 2026-05-13 · STEEVE-MAX
    # Renforcement : seuil 5→3 erreurs · cooldown 300s→600s · fenêtre 60s→90s
    # → Évite la cascade 429 + libère le worker plus longtemps après burst
    "error_threshold": 3,
    "window_sec": 90,
    "cooldown_sec": 600,
    "total_blocked": 0,
    "total_errors_recorded": 0,
}


def is_open() -> bool:
    """True si circuit breaker est OPEN (skip API)."""
    now = time.time()
    if now < _STATE["open_until"]:
        _STATE["total_blocked"] += 1
        return True
    # Purger erreurs hors fenêtre
    cutoff = now - _STATE["window_sec"]
    _STATE["errors_recent"] = [t for t in _STATE["errors_recent"] if t > cutoff]
    return False


def record_error() -> None:
    """Enregistre une erreur API et OPEN le circuit si seuil atteint."""
    now = time.time()
    _STATE["errors_recent"].append(now)
    _STATE["total_errors_recorded"] += 1
    cutoff = now - _STATE["window_sec"]
    _STATE["errors_recent"] = [t for t in _STATE["errors_recent"] if t > cutoff]
    if len(_STATE["errors_recent"]) >= _STATE["error_threshold"]:
        _STATE["open_until"] = now + _STATE["cooldown_sec"]
        logger.warning(
            f"[OPEN-METEO-CB] Circuit OPEN for {_STATE['cooldown_sec']}s "
            f"({_STATE['error_threshold']} errors in {_STATE['window_sec']}s)"
        )


def get_state() -> dict:
    """Retourne l'état du circuit breaker (pour audit/monitoring)."""
    now = time.time()
    return {
        "is_open": now < _STATE["open_until"],
        "open_until": _STATE["open_until"],
        "open_remaining_sec": max(0, _STATE["open_until"] - now),
        "errors_in_window": len([t for t in _STATE["errors_recent"] if t > now - _STATE["window_sec"]]),
        "total_blocked": _STATE["total_blocked"],
        "total_errors_recorded": _STATE["total_errors_recorded"],
        "config": {
            "error_threshold": _STATE["error_threshold"],
            "window_sec": _STATE["window_sec"],
            "cooldown_sec": _STATE["cooldown_sec"],
        },
    }


def reset() -> None:
    """Force reset du circuit (admin only)."""
    _STATE["errors_recent"] = []
    _STATE["open_until"] = 0.0
    logger.info("[OPEN-METEO-CB] Circuit RESET (admin force)")


async def safe_get(url: str, params: Optional[dict] = None, timeout: float = 5.0):
    """Wrapper sécurisé pour httpx.AsyncClient.get() avec circuit breaker.

    Retourne None si circuit OPEN ou si erreur (caller doit gérer fallback).
    """
    if is_open():
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params or {})
            r.raise_for_status()
            return r
    except Exception as e:
        record_error()
        logger.warning(f"[OPEN-METEO-CB] {type(e).__name__}: {str(e)[:200]}")
        return None
