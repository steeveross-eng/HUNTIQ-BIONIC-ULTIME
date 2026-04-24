"""
cache_diagnostic_router.py — PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0
======================================================================================
Phase     : PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0 (§E5)
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Endpoint LECTURE SEULE de diagnostic du cache (SW + LRU/Disk/Redis bundle).
Expose la version courante du cache Service Worker, les stats du cache
bundle V20, et renvoie les instructions de bust.
"""
from __future__ import annotations

import hashlib
import os
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_CORRIDORS_CACHE_Ω"])

# Waypoint officiel BCE-4X (référence géographique institutionnelle unique)
OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422

SW_FILE_PATH = Path("/app/frontend/public/sw.js")
SW_VERSION_MARKER = "bionic-hunt-cache-v"


def _parse_sw_version() -> Dict[str, Any]:
    """Extrait la version du CACHE_NAME depuis /public/sw.js."""
    if not SW_FILE_PATH.exists():
        return {"found": False, "error": "sw.js introuvable"}
    try:
        content = SW_FILE_PATH.read_text(encoding="utf-8")
    except Exception as e:
        return {"found": False, "error": str(e)}
    import re
    m = re.search(r"CACHE_NAME\s*=\s*'(bionic-hunt-cache-[^']+)'", content)
    if not m:
        return {"found": False, "error": "CACHE_NAME introuvable"}
    name = m.group(1)
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    mtime = os.path.getmtime(SW_FILE_PATH)
    return {
        "found": True,
        "sw_cache_name": name,
        "sw_file_sha256_head": sha,
        "sw_file_mtime": mtime,
        "sw_file_mtime_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime)),
        "sw_bypass_routes": [
            "/api/v30/corridors/*",
            "/api/v20/territoire/bundle*",
        ],
    }


@router.get("/cache-diagnostic")
async def cache_diagnostic():
    """Diagnostic complet du cache — SW + bundle LRU + instructions de bust."""
    try:
        from engines.v8_institutional.v20_performance_bundle import _STATS as BUNDLE_STATS
    except Exception:
        BUNDLE_STATS = {"misses": 0, "hits": 0}

    return JSONResponse({
        "phase": "PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0",
        "service_worker": _parse_sw_version(),
        "bundle_cache_stats": dict(BUNDLE_STATS),
        "client_bust_instructions": {
            "hard_reload": "Ctrl+Shift+R (Windows/Linux) ou Cmd+Shift+R (macOS)",
            "clear_sw_cache": "DevTools → Application → Storage → Clear site data",
            "force_sw_skip_waiting": "DevTools → Application → Service Workers → skipWaiting",
            "programmatic": "navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister()))",
            "sw_kill_endpoint": "/api/v30/corridors/sw-kill",
        },
        "server_purge_endpoints": {
            "POST /api/v20/territoire/bundle/purge": "purge LRU/Disk/Redis backend",
        },
        "cache_policy": {
            "v30_corridors_routes": "bypass_sw_no_cache",
            "v20_territoire_bundle": "bypass_sw_no_cache (INTERZONE live)",
            "static_js_css": "network_first",
            "static_assets": "cache_first",
        },
        "v30_locked": True,
        "diagnostic_corridors_omega_activated": False,
    })


# ═══════════════════════════════════════════════════════════════════════
# PHASE α — TERMINATOR SW : page HTML auto-exécutante qui unregister le SW
# ═══════════════════════════════════════════════════════════════════════
from fastapi.responses import HTMLResponse  # noqa: E402


SW_KILL_HTML = """<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">
<title>PURGE SW — PHASE_XII_SUPRA_TERRITOIRE_RENDERING_RECOVERY_Ω</title>
<style>
body { font: 14px/1.6 ui-monospace,Menlo,Monaco,Consolas,monospace;
       background: #0b1220; color: #e8eef5; padding: 32px; max-width: 780px; margin: 0 auto; }
h1 { color: #ff8f00; border-bottom: 2px solid #ff8f00; padding-bottom: 8px; }
.ok { color: #16a34a; font-weight: 700; }
.log { background: #121c2b; border: 1px solid #1c2735; border-radius: 6px;
       padding: 16px; margin: 14px 0; font-size: 12px; white-space: pre-wrap;
       max-height: 360px; overflow-y: auto; }
.btn { background: #ff8f00; color: #0b1220; padding: 12px 20px; border-radius: 6px;
       border: 0; font-weight: 700; cursor: pointer; letter-spacing: 0.04em;
       text-decoration: none; display: inline-block; margin-top: 14px; }
</style>
</head><body>
<h1>PROTOCOLE BCE-4X · SW TERMINATOR Ω</h1>
<p>Séquence de purge totale Service Worker + caches client en cours.
Vous serez redirigé vers la carte TERRITOIRE automatiquement après nettoyage.</p>
<div id="log" class="log">[RECOVERY_Ω] init...</div>
<a id="back" class="btn" href="/mon-territoire-bionic?lat=48.206657&lng=-68.382422" style="display:none">
  → Retour à la carte TERRITOIRE
</a>
<script>
(async function () {
  const log = (msg) => {
    const el = document.getElementById('log');
    el.textContent += '\\n' + msg;
    el.scrollTop = el.scrollHeight;
  };
  try {
    log('[1/4] Unregister Service Workers...');
    if ('serviceWorker' in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      for (const r of regs) {
        try { await r.unregister(); log('   ✓ unregistered: ' + (r.scope || '?')); }
        catch (e) { log('   ✗ fail: ' + e); }
      }
      log('[1/4] OK ' + regs.length + ' SW(s) éliminé(s)');
    } else {
      log('[1/4] SW API absent');
    }

    log('[2/4] Purge Cache Storage...');
    if ('caches' in window) {
      const keys = await caches.keys();
      for (const k of keys) {
        try { await caches.delete(k); log('   ✓ cache deleted: ' + k); }
        catch (e) { log('   ✗ fail: ' + e); }
      }
      log('[2/4] OK ' + keys.length + ' cache(s) purgé(s)');
    }

    log('[3/4] Clear sessionStorage + select localStorage keys...');
    try {
      sessionStorage.clear();
      Object.keys(localStorage).filter(k => /^sw_|^renduomega|^territoire|^bundle|^v30/i.test(k))
        .forEach(k => { localStorage.removeItem(k); log('   ✓ localStorage removed: ' + k); });
      log('[3/4] OK');
    } catch (e) { log('[3/4] WARN: ' + e); }

    log('[4/4] Reload dans 2s...');
    document.getElementById('back').style.display = 'inline-block';
    setTimeout(() => {
      window.location.replace('/mon-territoire-bionic?lat=48.206657&lng=-68.382422&_t=' + Date.now());
    }, 2000);
  } catch (e) {
    log('✗ FATAL: ' + e);
    document.getElementById('back').style.display = 'inline-block';
  }
})();
</script>
</body></html>"""


@router.get("/sw-kill", response_class=HTMLResponse)
async def sw_kill():
    """Page HTML auto-exécutante : unregister tous les SW + purge caches client."""
    return HTMLResponse(
        SW_KILL_HTML,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# ═══════════════════════════════════════════════════════════════════════
# PHASE γ — DIAGNOSTIC LAYER-BY-LAYER : count de chaque couche du bundle
# ═══════════════════════════════════════════════════════════════════════
@router.get("/layer-diagnostic")
async def layer_diagnostic(
    species: str = Query("orignal"),
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """Diagnostic précis : COUNT de chaque couche du bundle TERRITOIRE.

    Permet à l'UI de détecter instantanément toute couche manquante
    (zones, corridors, salines, hotspots, affuts, contamination, vent).
    """
    try:
        from fastapi import Response as FResp
        from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
    except Exception as e:
        return JSONResponse(
            {"error": f"v20_performance_bundle unavailable: {e}"},
            status_code=500,
        )
    try:
        resp = FResp()
        bundle = await v20_territoire_bundle(
            response=resp, lat=lat, lon=lon, species=species,
            month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    def _count(key: str) -> int:
        v = bundle.get(key)
        if isinstance(v, list):
            return len(v)
        if isinstance(v, dict):
            return len(v)
        return 0

    corridors = bundle.get("corridors") or []
    interzone_count = sum(1 for c in corridors if c.get("interzone_generated"))
    entering_count = sum(1 for c in corridors if c.get("entering_corridor"))
    v30_count = len(corridors) - interzone_count - entering_count

    # PHASE_XII_SUPRA_TERRITOIRE_RERENDER_Ω_ULTIME §3 — détection vent robuste.
    # Le bundle expose la télémétrie vent via plusieurs canaux : `sensoriel_vent_odeurs`
    # (engine_vent), `wind_vectors` (V8 particles) ou les clefs legacy `vent`/`wind`.
    _sens = bundle.get("sensoriel_vent_odeurs") or {}
    _wind_vecs = bundle.get("wind_vectors") or []
    vent = bundle.get("vent") or bundle.get("wind") or {}
    has_vent = bool(
        (vent and (vent.get("speed_kmh") is not None or vent.get("direction_deg") is not None))
        or (isinstance(_sens, dict) and (_sens.get("wind_speed_kmh") is not None
                                          or _sens.get("wind_deg") is not None))
        or (isinstance(_wind_vecs, list) and len(_wind_vecs) > 0)
    )

    layers = {
        "zones": _count("zones"),
        "corridors_total": len(corridors),
        "corridors_v30": max(0, v30_count),
        "corridors_interzone": interzone_count,
        "corridors_entering": entering_count,
        "salines": _count("salines"),
        "hotspots": _count("hotspots"),
        "affuts": _count("affuts"),
        "contamination_zones": _count("contamination_zones"),
        "vent_ok": has_vent,
        "waypoint_ok": bool(bundle.get("waypoint")),
    }

    # Sentinels : couches vides sont CRITIQUES
    missing = [k for k, v in layers.items() if isinstance(v, int) and v == 0
               and k not in ("corridors_entering", "corridors_interzone")]

    return JSONResponse({
        "phase": "PHASE_XII_SUPRA_TERRITOIRE_LAYER_DIAGNOSTIC_Ω",
        "waypoint": {"lat": lat, "lng": lon},
        "species": species,
        "month": month,
        "hour": hour,
        "layers": layers,
        "missing_critical_layers": missing,
        "all_layers_ok": len(missing) == 0,
        "veineux_applied": bool(bundle.get("veineux_omega_applied_at_bundle")),
        "interzone_applied": bool(bundle.get("interzone_omega_applied")),
        "renduomega_applied": bool(bundle.get("renduomega_applied_at_bundle")),
        "v30_locked": True,
    })
