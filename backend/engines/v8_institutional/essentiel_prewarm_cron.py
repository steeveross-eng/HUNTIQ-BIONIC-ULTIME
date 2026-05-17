"""
P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER — Cron pré-calcul 2000 membres
================================================================
COMMANDANT STEEVE-MAX · 2026-05-18 · BCE-4X ULTIME ABSOLU

Tâche planifiée qui :
  - parcourt la liste des membres actifs (jusqu'à 2 000)
  - calcule/rafraîchit leur bundle ESSENTIEL pour leur waypoint favori × espèces préférées
  - alimente le cache backend (LRU + disque) → garantit un cache CHAUD

Activation : export P22OMEGA_PREWARM_MEMBERS_CRON=1
Fréquence par défaut : toutes les 4 heures (configurable via P22OMEGA_PREWARM_INTERVAL_SEC)
Throttle : 3 secondes entre chaque bundle (pour ne pas saturer le single worker)
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import List, Dict, Any

logger = logging.getLogger("bionic.essentiel_prewarm_cron")

# Espèces canoniques de fallback si user.profile.species est vide
DEFAULT_TOP_SPECIES = ["chevreuil", "orignal", "ours_noir"]

# Waypoint Québec par défaut si user n'a pas de waypoint favori
DEFAULT_LAT = 48.206657
DEFAULT_LON = -68.382422

# Limite max de members traités par cycle (protection single-worker)
MAX_MEMBERS_PER_CYCLE = int(os.environ.get("P22OMEGA_PREWARM_MAX_MEMBERS", "2000"))

# Throttle entre chaque bundle (secondes)
THROTTLE_SEC = float(os.environ.get("P22OMEGA_PREWARM_THROTTLE_SEC", "3.0"))

# Intervalle entre 2 cycles (secondes)
INTERVAL_SEC = int(os.environ.get("P22OMEGA_PREWARM_INTERVAL_SEC", str(4 * 3600)))

_CRON_STATE: Dict[str, Any] = {
    "started_at": None,
    "cycles_completed": 0,
    "last_cycle_at": None,
    "last_cycle_duration_sec": 0,
    "last_cycle_members_warmed": 0,
    "last_cycle_errors": 0,
    "running": False,
}


def _is_cron_enabled() -> bool:
    return os.environ.get("P22OMEGA_PREWARM_MEMBERS_CRON", "0") == "1"


async def _fetch_active_members(db) -> List[Dict[str, Any]]:
    """Récupère les 2000 membres les plus récemment actifs depuis MongoDB."""
    try:
        cursor = (
            db.users.find(
                {"deleted": {"$ne": True}},
                {
                    "_id": 0,
                    "email": 1,
                    "favorite_waypoint": 1,
                    "favorite_species": 1,
                    "profile": 1,
                    "premium_tier": 1,
                    "last_seen_at": 1,
                },
            )
            .sort("last_seen_at", -1)
            .limit(MAX_MEMBERS_PER_CYCLE)
        )
        members = []
        async for doc in cursor:
            members.append(doc)
        return members
    except Exception as e:
        logger.warning(f"[ESSENTIEL_PREWARM_CRON] _fetch_active_members error: {e}")
        return []


def _resolve_waypoint(member: Dict[str, Any]) -> tuple:
    """Extrait (lat, lon) du waypoint favori du membre, ou défaut."""
    wp = member.get("favorite_waypoint") or {}
    lat = wp.get("lat") or wp.get("latitude") or DEFAULT_LAT
    lon = wp.get("lng") or wp.get("longitude") or DEFAULT_LON
    try:
        return float(lat), float(lon)
    except (TypeError, ValueError):
        return DEFAULT_LAT, DEFAULT_LON


def _resolve_species(member: Dict[str, Any]) -> List[str]:
    """Extrait les 3 espèces préférées du membre, ou défaut."""
    raw = (
        member.get("favorite_species")
        or (member.get("profile") or {}).get("species")
        or []
    )
    if isinstance(raw, str):
        raw = [raw]
    # Normalisation simple
    species = []
    for s in raw[:3]:
        s_norm = str(s).lower().strip()
        if s_norm in ("cerf", "cerf_virginie", "white_tailed_deer"):
            s_norm = "chevreuil"
        elif s_norm in ("ours", "black_bear"):
            s_norm = "ours_noir"
        elif s_norm in ("dindon", "turkey"):
            s_norm = "dindon_sauvage"
        elif s_norm in ("loup",):
            s_norm = "coyote"
        if s_norm:
            species.append(s_norm)
    if len(species) < 3:
        for fb in DEFAULT_TOP_SPECIES:
            if fb not in species:
                species.append(fb)
            if len(species) >= 3:
                break
    return species[:3]


async def _prewarm_single_bundle(lat: float, lon: float, species: str) -> bool:
    """Précharge un bundle pour un (waypoint, espèce). Renvoie True si succès."""
    try:
        from fastapi import Response as _FastAPIResponse
        from engines.v8_institutional.v20_performance_bundle import (
            v20_territoire_bundle,
            _WARMUP_CONTEXT,
        )
        now = time.localtime()
        month = now.tm_mon
        hour = now.tm_hour
        wind_deg = 225.0
        _token = _WARMUP_CONTEXT.set(True)
        try:
            await v20_territoire_bundle(
                response=_FastAPIResponse(),
                lat=lat,
                lon=lon,
                species=species,
                month=month,
                hour=hour,
                wind_deg=wind_deg,
                wind_speed=15.0,
            )
        finally:
            _WARMUP_CONTEXT.reset(_token)
        return True
    except Exception as e:
        logger.debug(f"[ESSENTIEL_PREWARM_CRON] _prewarm_single error: {e}")
        return False


async def _run_one_cycle(db) -> None:
    """Exécute un cycle complet de prewarm."""
    if _CRON_STATE["running"]:
        logger.info("[ESSENTIEL_PREWARM_CRON] Cycle déjà en cours, skip")
        return
    _CRON_STATE["running"] = True
    cycle_t0 = time.time()
    try:
        members = await _fetch_active_members(db)
        logger.info(f"[ESSENTIEL_PREWARM_CRON] Démarrage cycle · {len(members)} membres")
        warmed = 0
        errors = 0
        for member in members:
            lat, lon = _resolve_waypoint(member)
            species_list = _resolve_species(member)
            for sp in species_list:
                ok = await _prewarm_single_bundle(lat, lon, sp)
                if ok:
                    warmed += 1
                else:
                    errors += 1
                # Throttle pour ne pas saturer le single worker
                await asyncio.sleep(THROTTLE_SEC)
        # Persist disk après le cycle
        try:
            from engines.v8_institutional.v20_performance_bundle import _cache_save_disk
            n = _cache_save_disk()
            logger.info(f"[ESSENTIEL_PREWARM_CRON] Disk persist: {n} entries")
        except Exception:
            pass
        cycle_duration = time.time() - cycle_t0
        _CRON_STATE["cycles_completed"] += 1
        _CRON_STATE["last_cycle_at"] = time.time()
        _CRON_STATE["last_cycle_duration_sec"] = round(cycle_duration, 1)
        _CRON_STATE["last_cycle_members_warmed"] = warmed
        _CRON_STATE["last_cycle_errors"] = errors
        logger.info(
            f"[ESSENTIEL_PREWARM_CRON] Cycle DONE · warmed={warmed} errors={errors} "
            f"duration={cycle_duration:.1f}s"
        )
    finally:
        _CRON_STATE["running"] = False


async def essentiel_prewarm_cron_daemon():
    """Daemon principal : boucle infinie qui exécute un cycle puis dort INTERVAL_SEC."""
    if not _is_cron_enabled():
        logger.info("[ESSENTIEL_PREWARM_CRON] DISABLED (env P22OMEGA_PREWARM_MEMBERS_CRON != 1)")
        return
    from database import db as mongo_db
    _CRON_STATE["started_at"] = time.time()
    logger.info(
        f"[ESSENTIEL_PREWARM_CRON] ENABLED · max_members={MAX_MEMBERS_PER_CYCLE} "
        f"throttle={THROTTLE_SEC}s · interval={INTERVAL_SEC}s"
    )
    # Premier cycle après un délai initial pour laisser le boot finir
    await asyncio.sleep(30)
    while True:
        try:
            await _run_one_cycle(mongo_db)
        except Exception as e:
            logger.error(f"[ESSENTIEL_PREWARM_CRON] Cycle exception: {e}")
        await asyncio.sleep(INTERVAL_SEC)


def get_cron_state() -> Dict[str, Any]:
    """État du cron pour endpoint admin."""
    return {
        "enabled": _is_cron_enabled(),
        "max_members_per_cycle": MAX_MEMBERS_PER_CYCLE,
        "throttle_sec": THROTTLE_SEC,
        "interval_sec": INTERVAL_SEC,
        **_CRON_STATE,
    }
