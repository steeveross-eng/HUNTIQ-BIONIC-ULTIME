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

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v30/corridors", tags=["V30_CORRIDORS_CACHE_Ω"])

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
