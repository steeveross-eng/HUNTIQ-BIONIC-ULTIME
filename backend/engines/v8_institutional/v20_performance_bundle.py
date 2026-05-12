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

# ═══════════════════════════════════════════════════════════════════════
# P22Σ_SPECIES_NORMALIZATION_Ω · 2026-05-12T18:25Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Normalisation des noms d'espèces côté backend pour accepter tous les
# alias frontend (wild_turkey, dindon, dindon_sauvage, moose, deer, etc.)
# et router vers le nom canonique attendu par chaque engine.
# ═══════════════════════════════════════════════════════════════════════
SPECIES_ALIAS_TO_CANONICAL = {
    # Canoniques (passthrough)
    "orignal": "orignal",     "chevreuil": "chevreuil",
    "ours_noir": "ours_noir", "wapiti": "wapiti",
    "dindon_sauvage": "dindon_sauvage",
    # Alias FR courts
    "ours": "ours_noir",      "dindon": "dindon_sauvage",
    "cerf": "chevreuil",
    # Alias EN (frontend BionicZoneService)
    "moose": "orignal",       "deer": "chevreuil",
    "bear": "ours_noir",      "elk": "wapiti",
    "wild_turkey": "dindon_sauvage",
}


def normalize_species(s: str) -> str:
    """Normalise un nom d'espèce vers le nom canonique backend (V5)."""
    if not s:
        return "chevreuil"
    return SPECIES_ALIAS_TO_CANONICAL.get(s.lower().strip(), s)


# ═══════════════════════════════════════════════════════════════════════
# P22Σ_V5_BUNDLE_REWIRE_Ω — MAPPING HELPER (réutilisé par bundle + audit)
# ═══════════════════════════════════════════════════════════════════════
_HIER_COLOR_V5 = {
    "veine_principale": "#FF4500",   # backbone — rouge orangé
    "veine_secondaire": "#FF8F00",   # subnet — orange
    "capillaire":       "#FFB347",   # isolated — pêche
    "connector":        "#FFEE99",   # connector — jaune pâle
}


def map_v5_corridors_to_ui(v5_corridors_raw: list[dict]) -> list[dict]:
    """Map V5 organic corridors -> format UI (color + source + fusion_doctrine).

    Fonction réutilisée par /api/v20/territoire/bundle ET /api/v20/audit/v5-compliance-live
    pour garantir la même provenance V5 dans les deux endpoints.
    """
    mapped: list[dict] = []
    for _i, _c in enumerate(v5_corridors_raw or []):
        _hier = _c.get("hierarchy", "capillaire")
        _m = dict(_c)
        _m["id"] = _c.get("id") or f"corr_v5_{_i:03d}"
        _m["color"] = _c.get("color") or _HIER_COLOR_V5.get(_hier, "#FF8F00")
        _m["source"] = "ENGINE-IA-CORRIDORS-ORGANIC-Ω (V5_BUNDLE_REWIRE)"
        _m["fusion_doctrine"] = "P22Σ_V5_CAP_GLOBAL_TERRITOIRE"
        if "subnet_role" not in _m:
            _m["subnet_role"] = (
                "backbone" if _hier == "veine_principale" else
                "subnet" if _hier == "veine_secondaire" else
                "connector" if _m.get("type") == "connector" else
                "isolated"
            )
        mapped.append(_m)
    return mapped


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
    """P22Σ_CACHE_KEY_TOLERANT_Ω · 2026-05-12T23:55Z · COMMANDANT STEEVE-MAX

    Cache key tolérant : omet `hour` (le bundle V5 corridors ne dépend pas
    significativement de l'heure — la topologie réseau veineux est calculée
    sur terrain+zones vitales+écologie statique, pas l'heure du jour).
    Réduction cardinalité × 24 → 24× moins de MISS pour utilisateurs
    actifs dans des fuseaux horaires différents (UTC vs local Québec EDT).

    NOTE: `hour` reste accepté en paramètre pour compatibilité ABI mais
    n'est plus inclus dans la key (ignoré silencieusement).
    """
    _ = hour  # explicitly unused
    lat_s = f"{lat:.3f}"
    lon_s = f"{lon:.3f}"
    wd_s = int(round(wind_deg / 15.0) * 15) % 360
    return f"{lat_s}_{lon_s}_{species}_{month}_w{wd_s}"


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
# P22Σ_PRECHAUFFAGE_Ω_PROGRESSIF · 2026-05-12T18:55Z · COMMANDANT STEEVE-MAX
# Préchauffage progressif réactivé : 50 waypoints, semaphore 4
# (vs 500/16 antérieur qui saturait Open-Meteo)
_WARMUP_SEMAPHORE = asyncio.Semaphore(4)  # 4 parallel computes max


async def _warmup_single(lat: float, lon: float, species: str = "cerf"):
    """Compute + cache un seul waypoint avec params temporels DYNAMIQUES.

    P22Σ_V5_PRECHAUFFAGE_DYNAMIQUE_Ω · 2026-05-12T21:40Z · COMMANDANT STEEVE-MAX
    Utilise month/hour ACTUELS au lieu de hardcoded (10, 7) pour que la cache
    key match les requêtes frontend (qui envoient month/hour actuels via
    new Date().getUTCMonth()+1 et getUTCHours()).
    """
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    try:
        async with _WARMUP_SEMAPHORE:
            now = time.time()
            from datetime import datetime, timezone as _tz
            _dt = datetime.now(_tz.utc)
            _month = _dt.month
            _hour = _dt.hour
            # Normalize species pour aligner avec le frontend (cerf → chevreuil)
            _species = SPECIES_ALIAS_TO_CANONICAL.get(species.lower(), species)
            result = await compute_territoire_v10(lat, lon, _species, _month, _hour, 225.0, 15.0)
            key = _cache_key(lat, lon, _species, _month, _hour, 225.0)
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
        # Deduplication par cle quantifiee (params temporels DYNAMIQUES)
        from datetime import datetime, timezone as _tz
        _dt_now = datetime.now(_tz.utc)
        _m_now = _dt_now.month
        _h_now = _dt_now.hour
        seen = set()
        unique = []
        for lat, lon, sp in waypoints:
            sp_norm = SPECIES_ALIAS_TO_CANONICAL.get(sp.lower(), sp)
            k = _cache_key(lat, lon, sp_norm, _m_now, _h_now, 225.0)
            if k not in seen and _cache_get(k) is None:
                seen.add(k)
                unique.append((lat, lon, sp_norm))
        logger.info(f"[V20-WARMUP] Demarrage prechauffage: {len(unique)} waypoints (sur {len(waypoints)} retrouves) — month={_m_now} hour={_h_now}")
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
        # P22Σ_STABILISATION_Ω_PROGRESSIF · 50 waypoints + semaphore 4 + circuit breaker
        asyncio.create_task(run_prechauffage_omega(limit=50))
        asyncio.create_task(_periodic_refresh_daemon())
        # P22Ω.V5_COMPLIANCE_MONITOR_Ω · cron horaire alerte Resend
        asyncio.create_task(_v5_compliance_monitor_daemon())
        logger.info("[V20-LAZY-INIT] PROGRESSIF MODE: warmup 50 sem=4 + monitor scheduled")


# ═══ LIFESPAN HOOKS (called from server.py startup/shutdown) ═══
async def v20_startup():
    """Called by server.py on app startup."""
    loaded = _cache_load_disk()
    logger.info(f"[V20-PERFORMANCE] Startup: {loaded} entries loaded from disk")
    # P22Σ_STABILISATION_Ω_PROGRESSIF · daemons réactivés mode progressif
    asyncio.create_task(run_prechauffage_omega(limit=50))
    asyncio.create_task(_periodic_refresh_daemon())
    asyncio.create_task(_v5_compliance_monitor_daemon())
    logger.info("[V20-PERFORMANCE] PROGRESSIF MODE: warmup 50 + monitor scheduled")


async def v20_shutdown():
    """Called by server.py on app shutdown."""
    _cache_save_disk()


async def _periodic_refresh_daemon():
    """Daemon: rafraichit le cache toutes les 1h + save disk."""
    while True:
        try:
            await asyncio.sleep(3600)
            logger.info("[V20-WARMUP-DAEMON] Tick horaire — refresh + disk save")
            # P22Σ_PRECHAUFFAGE_Ω_PROGRESSIF · 50 waypoints
            await run_prechauffage_omega(limit=50)
        except Exception as e:
            logger.warning(f"[V20-WARMUP-DAEMON] Error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_COMPLIANCE_MONITOR_Ω · 2026-05-12T14:45Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Cron horaire : check audit V5 + alerte Resend si status=FAIL
# + journalisation persistante /app/memory/v5_compliance_log.jsonl
# (append-only, lu par /api/v20/audit/v5-daily-report).
# ═══════════════════════════════════════════════════════════════════════
_V5_MONITOR_INTERVAL_SEC = 3600  # 1h
_V5_MONITOR_LOG_FILE = Path("/app/memory/v5_compliance_log.jsonl")
_V5_MONITOR_WAYPOINTS = [
    # (lat, lon, species, label) — waypoints canoniques surveillés
    (48.206657, -68.382422, "orignal",   "BSL"),
    (46.5,      -71.5,      "cerf",      "Lotbinière"),
    (48.4,      -71.05,     "orignal",   "Saguenay"),
]
_V5_MONITOR_STATS: dict = {
    "runs": 0, "pass": 0, "fail": 0, "last_status": None,
    "last_run_utc": None, "last_violations_total": 0,
    "alerts_sent": 0, "alert_errors": 0,
}


async def _v5_compliance_check_single(lat: float, lon: float, species: str) -> dict:
    """Exécute un check V5 compliance sur un waypoint (utilise même logique audit)."""
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.engine_ia_corridors_organic_omega import (
        generate_organic_corridors,
    )
    try:
        bundle_data = await compute_territoire_v10(lat, lon, species, 10, 7, 225.0, 15.0)
        v5 = await generate_organic_corridors(
            lat=lat, lon=lon, species=species, month=10, hour=7,
            wind_deg=225, wind_speed=15, anchor_mode="TERRITORY_CONTINUOUS",
            bundle_pre_computed=bundle_data,
        )
        corridors = map_v5_corridors_to_ui(v5.get("corridors", []))
        hier = v5.get("hierarchy_counts", {}) or {}
        n = len(corridors)
        violations = []
        if not (5 <= n <= 7):
            violations.append("n_corridors_out_of_range")
        n_missing = sum(1 for c in corridors if not c.get("subnet_role"))
        if n_missing:
            violations.append(f"subnet_role_missing_{n_missing}")
        return {
            "lat": lat, "lon": lon, "species": species,
            "n_corridors": n,
            "n_backbones": hier.get("veine_principale", 0),
            "n_subnets": hier.get("veine_secondaire", 0),
            "violations": violations,
            "status": "PASS" if not violations else "FAIL",
        }
    except Exception as e:
        return {
            "lat": lat, "lon": lon, "species": species,
            "n_corridors": 0, "n_backbones": 0, "n_subnets": 0,
            "violations": [f"exception:{type(e).__name__}"],
            "status": "FAIL",
            "error": str(e),
        }


async def _v5_send_alert_resend(failed_checks: list[dict]) -> bool:
    """Envoie une alerte Resend si conformité V5 dégradée."""
    try:
        import os
        api_key = os.environ.get("RESEND_API_KEY")
        from_addr = os.environ.get("RESEND_FROM_EMAIL") or os.environ.get("RESEND_FROM")
        to_addr = os.environ.get("RESEND_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL")
        if not (api_key and from_addr and to_addr):
            logger.warning("[V5_MONITOR] Resend env vars manquantes → alerte non envoyée")
            return False
        import httpx
        body_lines = [
            "PROTOCOLE BCE-4X — ALERTE CONFORMITÉ V5",
            f"Date UTC: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
            f"Waypoints en échec: {len(failed_checks)}",
            "",
        ]
        for c in failed_checks:
            body_lines.append(
                f"  • {c.get('species')} @ ({c.get('lat')},{c.get('lon')}) → "
                f"status={c.get('status')} n_corridors={c.get('n_corridors')} "
                f"backbones={c.get('n_backbones')} subnets={c.get('n_subnets')} "
                f"violations={c.get('violations')}"
            )
        body_lines.append("")
        body_lines.append("Action: vérifier /api/v20/audit/v5-compliance-live et déployer correctif si besoin.")
        body_text = "\n".join(body_lines)
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}",
                          "Content-Type": "application/json"},
                json={
                    "from": from_addr,
                    "to": [to_addr],
                    "subject": f"[BCE-4X] V5 NON-CONFORME · {len(failed_checks)} waypoint(s) FAIL",
                    "text": body_text,
                },
            )
            ok = r.status_code in (200, 202)
            if ok:
                _V5_MONITOR_STATS["alerts_sent"] += 1
            else:
                _V5_MONITOR_STATS["alert_errors"] += 1
                logger.warning(f"[V5_MONITOR] Resend HTTP {r.status_code}: {r.text[:200]}")
            return ok
    except Exception as e:
        _V5_MONITOR_STATS["alert_errors"] += 1
        logger.warning(f"[V5_MONITOR] Resend alert failed: {e}")
        return False


def _v5_journal_append(entry: dict) -> None:
    """Append-only log JSONL du monitoring V5."""
    try:
        _V5_MONITOR_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_V5_MONITOR_LOG_FILE, "a", encoding="utf-8") as f:
            import json as _json
            f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"[V5_MONITOR] Journal append failed: {e}")


async def _v5_compliance_monitor_daemon():
    """Daemon: vérifie la conformité V5 toutes les heures + alerte si FAIL."""
    # P22Σ_STABILISATION_Ω_PROGRESSIF · Délai initial 1h pour ne pas saturer
    # le worker async au démarrage. Premier tick = startup + 1h.
    # Le COMMANDANT peut forcer un tick immédiat via POST /v5-monitor-tick.
    await asyncio.sleep(_V5_MONITOR_INTERVAL_SEC)
    while True:
        try:
            t0 = time.time()
            results = []
            for (lat, lon, sp, _label) in _V5_MONITOR_WAYPOINTS:
                results.append(await _v5_compliance_check_single(lat, lon, sp))
            failed = [r for r in results if r.get("status") == "FAIL"]
            n_violations_total = sum(len(r.get("violations", [])) for r in results)
            _V5_MONITOR_STATS["runs"] += 1
            _V5_MONITOR_STATS["last_run_utc"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(),
            )
            _V5_MONITOR_STATS["last_violations_total"] = n_violations_total
            if failed:
                _V5_MONITOR_STATS["fail"] += 1
                _V5_MONITOR_STATS["last_status"] = "FAIL"
                # Alerte Resend
                await _v5_send_alert_resend(failed)
            else:
                _V5_MONITOR_STATS["pass"] += 1
                _V5_MONITOR_STATS["last_status"] = "PASS"
            elapsed = round(time.time() - t0, 2)
            journal_entry = {
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_s": elapsed,
                "n_failed": len(failed),
                "n_total": len(results),
                "n_violations_total": n_violations_total,
                "results": results,
                "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
            }
            _v5_journal_append(journal_entry)
            logger.info(
                f"[V5_MONITOR] Tick: {len(results)} checks · "
                f"{len(failed)} FAIL · {elapsed}s",
            )
        except Exception as e:
            logger.warning(f"[V5_MONITOR] Daemon error: {e}")
        # Sleep 1h
        await asyncio.sleep(_V5_MONITOR_INTERVAL_SEC)


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
    # P22Σ_SPECIES_NORMALIZATION_Ω — normalisation alias frontend (wild_turkey, etc.)
    species = normalize_species(species)
    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = _cache_get(key)

    if cached is not None:
        _STATS["hits"] += 1
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        # P22Ω.TRANSITION_V5 · 2026-05-12 · max-age réduit de 3600s → 300s
        # Évite Cloudflare cache d'un bundle legacy 23h pendant la transition V5.
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=900"
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
    # P22Σ_V5_BUNDLE_REWIRE_Ω — pipeline V5 organic en parallèle (2026-05-12)
    from engines.v8_institutional.engine_ia_corridors_organic_omega import (
        generate_organic_corridors,
    )

    # ═══════════════════════════════════════════════════════════════════════
    # OPTIMISATION P22Σ_V5_REWIRE_OPTIM (2026-05-12 · COMMANDANT STEEVE-MAX)
    # ═══════════════════════════════════════════════════════════════════════
    # V10 calculé une seule fois puis passé à V5 organic via bundle_pre_computed
    # → -44% latence cache MISS (50s → ~22s) vs ancienne parallélisation
    # asyncio.gather qui faisait V10 DEUX fois en concurrence.
    # ═══════════════════════════════════════════════════════════════════════
    result = await compute_territoire_v10(lat, lon, species, month, hour, wind_deg, wind_speed)
    try:
        v5_bundle = await generate_organic_corridors(
            lat=lat, lon=lon, species=species,
            month=month, hour=hour,
            wind_deg=int(wind_deg), wind_speed=int(wind_speed),
            anchor_mode="TERRITORY_CONTINUOUS",
            bundle_pre_computed=result,  # ← évite le double appel compute_territoire_v10
        )
        v5_error = None
    except Exception as _e_v5:
        v5_bundle = None
        v5_error = str(_e_v5)
    _V5_REWIRE_ACTIVE = v5_bundle is not None
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE_XVIII_BIO_PRESENCE_MASK_Ω — COURT-CIRCUIT en amont
    # Si l'espèce est ABSENTE du territoire (registre MFFP + SEPAQ + Atlas),
    # on vide les corridors avant tout le pipeline XIX / VITAUX / RENDUΩ.
    # ═══════════════════════════════════════════════════════════════════════
    result["waypoint"] = {"lat": lat, "lng": lon}
    result["species"] = species
    try:
        from engines.v8_institutional.species_presence_mask_omega import (
            apply_presence_mask_to_bundle,
        )
        result = apply_presence_mask_to_bundle(result, species=species, lat=lat, lng=lon)
    except Exception as _e_pres:
        result["bio_presence_mask_applied"] = False
        result["bio_presence_mask_error"] = str(_e_pres)
    if result.get("bio_presence_mask_halt") is True:
        # Pipeline court-circuité : corridors vides, on renvoie le bundle tel quel
        # (zones vitales, salines, hotspots restent affichés pour audit écologique).
        return result

    # ═══════════════════════════════════════════════════════════════════════
    # RAPATRIEMENT_RENDUΩ_V20 — SECTION 1.1 / 1.2 / 1.3
    # Validation et filtrage ABSOLUS des corridors avant cache & envoi client.
    # Même moteur que POST /api/v7-ultime/renduomega/validate-bundle.
    # V30 LOCKED intact — seules les sorties de compute_territoire_v10 sont
    # filtrées ici ; le moteur institutionnel reste inchangé.
    # ═══════════════════════════════════════════════════════════════════════    # Normalisation `contamination_zones` pour RenduΩ :
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
    # ═══ PHASE_XVIII (GPS) — PREDICTIVE_OMEGA_V2 (passe 1) ═══
    # Annotation V30 d'origine avec scoring comportemental GPS USGS/Movebank.
    # P22Σ_V5_REWIRE : skip si V5 actif (corridors seront overridés)
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.predictive_omega_v2 import apply_predictive_omega_v2_to_bundle
            result = apply_predictive_omega_v2_to_bundle(result, species=species, month=month, hour=hour)
        except Exception as _e_xviii:
            result["predictive_omega_v2_applied"] = False
            result["predictive_omega_v2_error"] = str(_e_xviii)
    # ═══ INTERZONE_Ω — AJOUT des corridors inter-zones + entrants (V30 intact) ═══
    if not _V5_REWIRE_ACTIVE:
        result = apply_interzone_omega_to_bundle(result)
    # ═══ VEINEUX_Ω — transformation géométrique amont (V30 intact) ═══
    if not _V5_REWIRE_ACTIVE:
        result = apply_veineux_omega_to_bundle(result)
    # ═══ PHASE_XVIII (GPS) — PREDICTIVE_OMEGA_V2 (passe 2) ═══
    # Re-annotation des corridors entrants/interzone ajoutés.
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.predictive_omega_v2 import apply_predictive_omega_v2_to_bundle
            result = apply_predictive_omega_v2_to_bundle(result, species=species, month=month, hour=hour)
        except Exception as _e_xviii_2:
            result["predictive_omega_v2_post_veineux_applied"] = False
            result["predictive_omega_v2_post_veineux_error"] = str(_e_xviii_2)
    # ═══ PHASE_XIX-P2 — ORIGINE_EXTERNE_INVERSION_Ω : inversion conditionnelle ═══
    # Si path[0] hors couronne ET path[-1] dans couronne → reverse(path).
    # Ré-annotation predictive_omega_v2 automatique sur les corridors inversés.
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.origine_externe_inversion_omega import (
                apply_origine_externe_inversion_to_bundle,
            )
            result = apply_origine_externe_inversion_to_bundle(
                result, species=species, month=month, hour=hour,
            )
        except Exception as _e_xix_p2:
            result["origine_externe_inversion_applied"] = False
            result["origine_externe_inversion_error"] = str(_e_xix_p2)
    # ═══ PHASE_XIX-P1 — ORIGINE_EXTERNE_FILTER_Ω : DÉSACTIVÉ ═══
    # P22Ω.PURGE_LEGACY · 2026-05-12T14:30Z · directive COMMANDANT STEEVE-MAX :
    # filtre couronne 30% retiré du bundle (était skippé en V5 mais pollue le
    # fallback V10). Décision V90 finale : POINT_ORIGINE n'est plus filtré au
    # niveau du bundle ; cette logique vit dans V5 organic uniquement.
    # Le filtre demeure disponible via son endpoint dédié si besoin scientifique.
    # if not _V5_REWIRE_ACTIVE:
    #     try:
    #         from engines.v8_institutional.origine_externe_filter_omega import (
    #             apply_origine_externe_filter_to_bundle,
    #         )
    #         result = apply_origine_externe_filter_to_bundle(result)
    #     except Exception as _e_xix:
    #         result["origine_externe_filter_applied"] = False
    #         result["origine_externe_filter_error"] = str(_e_xix)
    result["origine_externe_filter_disabled"] = "P22Ω.PURGE_LEGACY · 2026-05-12"
    # ═══ PHASE_XVII — ÉCOLOGIQUE_Ω : annotation consensus écologique ═══
    # GARDÉ même en V5 — affecte zones, pas corridors.
    try:
        from engines.v8_institutional.ecological_orchestrator_omega import orchestrate_bundle
        result = orchestrate_bundle(result, species=species)
    except Exception as _e:
        result["ecological_orchestrator_applied"] = False
        result["ecological_orchestrator_error"] = str(_e)
    # ═══ PHASE_XVIII (VITAUX) — CORRIDORS_VITAUX_Ω : ancrage zones vitales ═══
    # Filtre INSTITUTIONNEL : un corridor n'est admis QUE s'il est ancré sur
    # ≥ 1 zone vitale officielle dans 150 m, avec règles différenciées par
    # groupe d'espèces (grands mammifères vs petits mammifères).
    # P22Σ_V5_REWIRE : skip — V5 a sa propre logique d'ancrage zones vitales.
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.corridors_vitaux_omega import apply_corridors_vitaux_to_bundle
            result = apply_corridors_vitaux_to_bundle(result, species=species)
        except Exception as _e_vitaux:
            result["corridors_vitaux_omega_applied"] = False
            result["corridors_vitaux_omega_error"] = str(_e_vitaux)
    # ═══ RENDUΩ — validation géométrique stricte (FIN de pipeline) ═══
    # P22Σ_V5_REWIRE : skip pour corridors V5 (déjà smoothed X180 + cap validé)
    if not _V5_REWIRE_ACTIVE:
        result = apply_renduomega_to_bundle(result)

    # ═══════════════════════════════════════════════════════════════════════
    # P22Σ_V5_BUNDLE_REWIRE_Ω  (2026-05-12 · COMMANDANT STEEVE-MAX)
    # ═══════════════════════════════════════════════════════════════════════
    # FUSION ADD-ONLY · V30_LOCK INTACT
    # Override final des corridors V10 par les corridors V5 organic
    # (cap global 5-7 + backbones + subnets + hierarchy).
    # `v5_bundle` est déjà calculé en amont via asyncio.gather().
    # ═══════════════════════════════════════════════════════════════════════
    if _V5_REWIRE_ACTIVE:
        v5_corridors_raw = v5_bundle.get("corridors", []) or []
        v5_mapped = map_v5_corridors_to_ui(v5_corridors_raw)
        result["corridors"] = v5_mapped
        result["p22sigma_v5_bundle_rewire"] = {
            "applied": True,
            "anchor_mode": "TERRITORY_CONTINUOUS",
            "n_corridors": len(v5_mapped),
            "hierarchy_counts": v5_bundle.get("hierarchy_counts"),
            "cap_global_doctrine": v5_bundle.get("p22sigma_v5_cap_global_doctrine"),
            "engine": v5_bundle.get("engine"),
            "engine_version": v5_bundle.get("version"),
            "doctrine": "P22Σ_V5_BUNDLE_REWIRE_Ω",
            "wired_at": "v20_performance_bundle.v20_territoire_bundle",
            "optim": "V10_SINGLE_CALL_THEN_V5_REUSE",
        }
    else:
        # Fallback V10 : on garde le pipeline legacy + signal d'échec
        result["p22sigma_v5_bundle_rewire"] = {
            "applied": False,
            "error": v5_error or "v5_bundle unavailable",
            "fallback": "V10_SUPRA_LEGACY",
        }
        # Appliquer RENDUΩ uniquement en fallback V10
        result = apply_renduomega_to_bundle(result)
    # ═══════════════════════════════════════════════════════════════════════
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

    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=900"
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
        "warmup_semaphore_max": 4,
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



# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_COMPLIANCE_LIVE_Ω · 2026-05-12T14:30Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Endpoint d'audit continu : vérifie en temps réel la conformité V5 du
# bundle UI pour un waypoint donné. Critères :
#   - n_corridors ∈ [5, 7]
#   - subnet_role présent sur chaque corridor
#   - hierarchy ∈ {veine_principale, veine_secondaire}
#   - fusion_doctrine == "P22Σ_V5_CAP_GLOBAL_TERRITOIRE"
#   - source contient "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
# Statut renvoyé : "PASS" / "FAIL" + détails non-conformités.
# ═══════════════════════════════════════════════════════════════════════
audit_router = APIRouter(prefix="/api/v20/audit", tags=["V20 Audit V5"])


@audit_router.get("/v5-compliance-live")
async def v20_audit_v5_compliance_live(
    response: Response,
    lat: float = Query(48.206657),
    lon: float = Query(-68.382422),
    species: str = Query("orignal"),
    month: int = Query(10),
    hour: int = Query(7),
    wind_deg: float = Query(225),
    wind_speed: float = Query(15),
):
    """Audit live conformité V5 sur le bundle UI (P22Ω.V5_COMPLIANCE_LIVE_Ω)."""
    await _ensure_lazy_init()
    # Normalisation alias frontend (wild_turkey → dindon_sauvage, etc.)
    species = normalize_species(species)

    # Re-fetch live du bundle via la même logique que /bundle
    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = _cache_get(key)
    if cached is not None:
        bundle_data = cached
        cache_status = "HIT"
    else:
        # Calcul à la volée via la même logique que /bundle (mapping V5 inclus)
        from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
        from engines.v8_institutional.engine_ia_corridors_organic_omega import (
            generate_organic_corridors,
        )
        bundle_data = await compute_territoire_v10(
            lat, lon, species, month, hour, wind_deg, wind_speed,
        )
        try:
            v5 = await generate_organic_corridors(
                lat=lat, lon=lon, species=species,
                month=month, hour=hour,
                wind_deg=int(wind_deg), wind_speed=int(wind_speed),
                anchor_mode="TERRITORY_CONTINUOUS",
                bundle_pre_computed=bundle_data,
            )
            # Mapping V5 IDENTIQUE au bundle pour garantir provenance cohérente
            bundle_data["corridors"] = map_v5_corridors_to_ui(v5.get("corridors", []))
            bundle_data["p22sigma_v5_bundle_rewire"] = {
                "applied": True,
                "hierarchy_counts": v5.get("hierarchy_counts"),
                "cap_global_doctrine": v5.get("p22sigma_v5_cap_global_doctrine"),
            }
        except Exception as _e:
            bundle_data["p22sigma_v5_bundle_rewire"] = {
                "applied": False, "error": str(_e),
            }
        cache_status = "LIVE"

    corridors = bundle_data.get("corridors", []) or []
    n = len(corridors)

    # Critères de conformité V5
    violations: list[dict] = []

    # Critère 1 : n_corridors ∈ [5, 7]
    if not (5 <= n <= 7):
        violations.append({
            "rule": "n_corridors_in_5_to_7",
            "expected": "5..7",
            "observed": n,
            "severity": "CRITICAL",
        })

    # Critère 2 : subnet_role présent sur chaque corridor
    n_missing_role = sum(1 for c in corridors if not c.get("subnet_role"))
    if n_missing_role > 0:
        violations.append({
            "rule": "subnet_role_present_on_each_corridor",
            "expected": 0,
            "observed_missing": n_missing_role,
            "severity": "HIGH",
        })

    # Critère 3 : hierarchy ∈ {veine_principale, veine_secondaire, capillaire, connector}
    bad_hier = [c.get("id") for c in corridors
                if c.get("hierarchy") not in {"veine_principale", "veine_secondaire",
                                                "capillaire", "connector"}]
    if bad_hier:
        violations.append({
            "rule": "hierarchy_valid",
            "expected": "{veine_principale, veine_secondaire, capillaire, connector}",
            "observed_bad": bad_hier,
            "severity": "HIGH",
        })

    # Critère 4 : fusion_doctrine == P22Σ_V5_CAP_GLOBAL_TERRITOIRE
    bad_doctrine = [c.get("id") for c in corridors
                    if c.get("fusion_doctrine") != "P22Σ_V5_CAP_GLOBAL_TERRITOIRE"]
    if bad_doctrine:
        violations.append({
            "rule": "fusion_doctrine_v5",
            "expected": "P22Σ_V5_CAP_GLOBAL_TERRITOIRE",
            "observed_bad": bad_doctrine,
            "severity": "MEDIUM",
        })

    # Critère 5 : source contient "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
    bad_source = [c.get("id") for c in corridors
                  if "ENGINE-IA-CORRIDORS-ORGANIC-Ω" not in (c.get("source") or "")]
    if bad_source:
        violations.append({
            "rule": "source_field_v5_organic",
            "expected": "contains ENGINE-IA-CORRIDORS-ORGANIC-Ω",
            "observed_bad": bad_source,
            "severity": "HIGH",
        })

    # Comptage backbones/subnets
    rw = bundle_data.get("p22sigma_v5_bundle_rewire", {}) or {}
    hcounts = rw.get("hierarchy_counts", {}) or {}
    n_backbones = hcounts.get("veine_principale", 0)
    n_subnets = hcounts.get("veine_secondaire", 0)

    status = "PASS" if not violations else "FAIL"
    response.headers["Cache-Control"] = "no-cache, no-store"

    return {
        "status": status,
        "doctrine": "P22Ω.V5_COMPLIANCE_LIVE_Ω",
        "audit_date_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc,
        ).isoformat(),
        "waypoint": {"lat": lat, "lon": lon, "species": species,
                     "month": month, "hour": hour,
                     "wind_deg": wind_deg, "wind_speed": wind_speed},
        "cache_status": cache_status,
        "metrics": {
            "n_corridors": n,
            "n_backbones": n_backbones,
            "n_subnets": n_subnets,
            "v5_rewire_applied": bool(rw.get("applied")),
        },
        "criteria_targets": {
            "n_corridors": "5..7",
            "n_backbones": "1..2",
            "n_subnets": "3..5",
            "fusion_doctrine": "P22Σ_V5_CAP_GLOBAL_TERRITOIRE",
        },
        "violations": violations,
        "violation_count": len(violations),
    }



# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_MONITOR_STATS — Snapshot du monitoring V5 cron horaire
# ═══════════════════════════════════════════════════════════════════════
@audit_router.get("/v5-monitor-stats")
async def v20_audit_v5_monitor_stats(response: Response):
    """État du monitoring V5 (cron horaire)."""
    response.headers["Cache-Control"] = "no-cache, no-store"
    # P22Σ_CIRCUIT_BREAKER_Ω · état Open-Meteo circuit breaker
    try:
        from engines.v8_institutional.lidar_irda_v11 import get_circuit_breaker_state
        cb = get_circuit_breaker_state()
    except Exception:
        cb = None
    return {
        "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
        "interval_sec": _V5_MONITOR_INTERVAL_SEC,
        "waypoints_watched": [
            {"lat": lat, "lon": lon, "species": sp, "label": label}
            for (lat, lon, sp, label) in _V5_MONITOR_WAYPOINTS
        ],
        "journal_file": str(_V5_MONITOR_LOG_FILE),
        "journal_exists": _V5_MONITOR_LOG_FILE.exists(),
        "stats": _V5_MONITOR_STATS,
        "open_meteo_circuit_breaker": cb,
    }


# ═══════════════════════════════════════════════════════════════════════
# Déclenchement manuel d'un tick du monitor (utile pour tests + force-check)
# ═══════════════════════════════════════════════════════════════════════
@audit_router.post("/v5-monitor-tick")
async def v20_audit_v5_monitor_tick(response: Response, background: BackgroundTasks):
    """Déclenche manuellement un tick du V5 compliance monitor en background."""
    response.headers["Cache-Control"] = "no-cache, no-store"

    async def _single_tick():
        try:
            t0 = time.time()
            results = []
            for (lat, lon, sp, _label) in _V5_MONITOR_WAYPOINTS:
                results.append(await _v5_compliance_check_single(lat, lon, sp))
            failed = [r for r in results if r.get("status") == "FAIL"]
            n_violations_total = sum(len(r.get("violations", [])) for r in results)
            _V5_MONITOR_STATS["runs"] += 1
            _V5_MONITOR_STATS["last_run_utc"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(),
            )
            _V5_MONITOR_STATS["last_violations_total"] = n_violations_total
            if failed:
                _V5_MONITOR_STATS["fail"] += 1
                _V5_MONITOR_STATS["last_status"] = "FAIL"
                await _v5_send_alert_resend(failed)
            else:
                _V5_MONITOR_STATS["pass"] += 1
                _V5_MONITOR_STATS["last_status"] = "PASS"
            elapsed = round(time.time() - t0, 2)
            _v5_journal_append({
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_s": elapsed,
                "n_failed": len(failed),
                "n_total": len(results),
                "n_violations_total": n_violations_total,
                "results": results,
                "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
                "trigger": "MANUAL_TICK",
            })
            logger.info(f"[V5_MONITOR] Manual tick: {len(failed)} FAIL / {len(results)} · {elapsed}s")
        except Exception as e:
            logger.warning(f"[V5_MONITOR] Manual tick error: {e}")

    background.add_task(_single_tick)
    return {
        "started": True,
        "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
        "message": "Tick lancé en background — consulter /v5-monitor-stats dans ~60s",
    }


# ═══════════════════════════════════════════════════════════════════════
# Test d'alerte Resend (simulation) — COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
@audit_router.post("/v5-alert-test")
async def v20_audit_v5_alert_test(response: Response, to: str | None = Query(None)):
    """Envoie une alerte Resend SIMULÉE pour valider la configuration.

    Utilise un faux corridor en échec → déclenche `_v5_send_alert_resend()`.
    Paramètre optionnel `?to=email@domain.com` pour override le destinataire
    (utile si le domaine ADMIN_EMAIL n'est pas encore vérifié chez Resend).
    """
    response.headers["Cache-Control"] = "no-cache, no-store"
    import os

    # Override temporaire du ADMIN_EMAIL pour ce test uniquement
    original_admin = os.environ.get("ADMIN_EMAIL")
    if to:
        os.environ["ADMIN_EMAIL"] = to

    env_diag = {
        "RESEND_API_KEY_present": bool(os.environ.get("RESEND_API_KEY")),
        "RESEND_FROM_present": bool(
            os.environ.get("RESEND_FROM_EMAIL") or os.environ.get("RESEND_FROM"),
        ),
        "ADMIN_EMAIL_present": bool(
            os.environ.get("RESEND_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL"),
        ),
        "ADMIN_EMAIL_value_used": os.environ.get("RESEND_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL"),
        "RESEND_FROM_value": os.environ.get("RESEND_FROM_EMAIL") or os.environ.get("RESEND_FROM"),
        "override_to_used": to,
    }

    # Construction d'un faux check FAIL pour simuler une non-conformité
    fake_failed = [{
        "lat": 48.206657, "lon": -68.382422, "species": "orignal",
        "n_corridors": 2, "n_backbones": 0, "n_subnets": 2,
        "violations": [
            "[SIMULATION] n_corridors_out_of_range",
            "[SIMULATION] subnet_role_missing_2",
        ],
        "status": "FAIL",
        "_simulation": True,
    }]

    ok = await _v5_send_alert_resend(fake_failed)

    # Restaurer ADMIN_EMAIL original
    if to:
        if original_admin is None:
            os.environ.pop("ADMIN_EMAIL", None)
        else:
            os.environ["ADMIN_EMAIL"] = original_admin

    return {
        "doctrine": "P22Ω.V5_ALERT_TEST_Ω",
        "test_type": "SIMULATION",
        "alert_sent_ok": ok,
        "env_diagnostic": env_diag,
        "monitor_stats": {
            "alerts_sent_total": _V5_MONITOR_STATS["alerts_sent"],
            "alert_errors_total": _V5_MONITOR_STATS["alert_errors"],
        },
        "note": ("Si alert_sent_ok=true, vérifier la boîte de réception "
                  "ADMIN_EMAIL pour le message [BCE-4X] V5 NON-CONFORME · 1 waypoint(s) FAIL"),
        "production_setup": ("Pour activer l'envoi vers steeve@bionichunt.com en PROD : "
                              "vérifier le domaine bionichunt.com chez Resend "
                              "(DNS DKIM/SPF). En attendant, utiliser "
                              "?to=steeve.ross@gmail.com pour tester."),
    }


# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_DAILY_REPORT — Rapport quotidien 24h
# ═══════════════════════════════════════════════════════════════════════
@audit_router.get("/v5-daily-report")
async def v20_audit_v5_daily_report(
    response: Response,
    hours: int = Query(24, ge=1, le=168),
    format: str = Query("json", regex="^(json|md)$"),
):
    """Agrège les checks V5 sur les dernières N heures (default 24h).

    - Taux de conformité V5 (PASS/FAIL ratio)
    - Taux de fallback V10
    - Latence HIT/MISS (depuis _STATS)
    - Dérives doctrinales détectées (violations rules counts)
    """
    response.headers["Cache-Control"] = "no-cache, no-store"
    import json as _json
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td

    cutoff = _dt.now(_tz.utc) - _td(hours=hours)
    entries: list[dict] = []
    if _V5_MONITOR_LOG_FILE.exists():
        try:
            with open(_V5_MONITOR_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = _json.loads(line)
                        ts_str = e.get("ts_utc")
                        if not ts_str:
                            continue
                        e_dt = _dt.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_tz.utc)
                        if e_dt >= cutoff:
                            entries.append(e)
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"[V5_DAILY] read journal failed: {e}")

    # Agrégations
    n_ticks = len(entries)
    n_total_checks = sum(e.get("n_total", 0) for e in entries)
    n_failed_checks = sum(e.get("n_failed", 0) for e in entries)
    n_violations = sum(e.get("n_violations_total", 0) for e in entries)
    pass_ratio = ((n_total_checks - n_failed_checks) / n_total_checks * 100) if n_total_checks else 0.0

    # Dérives doctrinales (violations groupées par rule)
    rule_counts: dict = {}
    for e in entries:
        for r in e.get("results", []):
            for v in r.get("violations", []):
                rule_counts[v] = rule_counts.get(v, 0) + 1

    # Stats latence (depuis _STATS courant)
    total_lat = _STATS["hits"] + _STATS["misses"]
    hit_ratio = (_STATS["hits"] / total_lat * 100) if total_lat else 0.0
    avg_compute_ms = (_STATS["total_compute_ms"] / _STATS["misses"]) if _STATS["misses"] else 0

    # Fallback V10 detection (chercher fallback dans les entries — non collecté actuellement)
    # Ici on retourne la valeur courante du monitor stats (FAIL = potentiel fallback)
    fallback_ratio = (_V5_MONITOR_STATS["fail"] / _V5_MONITOR_STATS["runs"] * 100) \
                     if _V5_MONITOR_STATS["runs"] else 0.0

    report = {
        "doctrine": "P22Ω.V5_DAILY_REPORT",
        "period_hours": hours,
        "generated_utc": _dt.now(_tz.utc).isoformat(),
        "summary": {
            "n_ticks": n_ticks,
            "n_total_checks": n_total_checks,
            "n_failed_checks": n_failed_checks,
            "v5_conformity_pct": round(pass_ratio, 2),
            "v10_fallback_pct": round(fallback_ratio, 2),
            "n_violations_total": n_violations,
        },
        "latency": {
            "cache_hits": _STATS["hits"],
            "cache_misses": _STATS["misses"],
            "hit_ratio_pct": round(hit_ratio, 2),
            "avg_compute_ms": round(avg_compute_ms, 2),
        },
        "derives_doctrinales": rule_counts,
        "waypoints_watched": [
            {"lat": lat, "lon": lon, "species": sp, "label": label}
            for (lat, lon, sp, label) in _V5_MONITOR_WAYPOINTS
        ],
        "monitor_stats": _V5_MONITOR_STATS,
    }

    if format == "md":
        lines = [
            f"# RAPPORT QUOTIDIEN V5 — {hours}h",
            "**Doctrine** : `P22Ω.V5_DAILY_REPORT`",
            f"**Généré UTC** : {report['generated_utc']}",
            "",
            "## Conformité V5",
            f"- Ticks monitorés : **{n_ticks}**",
            f"- Checks totaux : **{n_total_checks}**",
            f"- Checks en échec : **{n_failed_checks}**",
            f"- Taux de conformité V5 : **{round(pass_ratio, 2)}%**",
            f"- Taux de fallback V10 : **{round(fallback_ratio, 2)}%**",
            f"- Violations cumulées : **{n_violations}**",
            "",
            "## Latence cache",
            f"- Cache HIT : {_STATS['hits']}",
            f"- Cache MISS : {_STATS['misses']}",
            f"- Hit ratio : **{round(hit_ratio, 2)}%**",
            f"- Latence moyenne MISS : **{round(avg_compute_ms, 2)}ms**",
            "",
            "## Dérives doctrinales détectées",
        ]
        if rule_counts:
            for rule, cnt in sorted(rule_counts.items(), key=lambda x: -x[1]):
                lines.append(f"- `{rule}` : {cnt} occurrences")
        else:
            lines.append("- Aucune dérive détectée ✅")
        lines.extend([
            "",
            "## Waypoints monitorés",
        ])
        for (lat, lon, sp, label) in _V5_MONITOR_WAYPOINTS:
            lines.append(f"- {label} ({sp}) : ({lat}, {lon})")
        lines.extend([
            "",
            "_Fin du rapport BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX_",
        ])
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("\n".join(lines), media_type="text/markdown; charset=utf-8")

    return report
