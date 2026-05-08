"""territoire_omega_canonical_omega.py — P20_PHASE5 canonical lock.

═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

P20_PHASE5 · CANONICAL LOCK :
  · `territoire_omega_canonical: ENFORCED` — single source of truth
  · `forbid_legacy_paths: PERMANENT`
  · `forbid_analysis_v6: PERMANENT`
  · `forbid_debug_panels: PERMANENT`
  · `unified_panel_mode: PRIMARY_ONLY_PERMANENT`
  · `enforce_zindex_institutionnel: ENABLED`
  · `sync_indicator_sha256: ENABLED` (scope = last force reload)
  · `watchdog_lock: ENFORCED` à 600s

DOCTRINE :
  · Lecture seule des overlays existants (anti-générique)
  · Calcule SHA-256 de l'état canonique courant + timestamp UTC
  · Aucun override autorisé en runtime
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


CANONICAL_LOCK_VERSION = "P20_PHASE5_CANONICAL_LOCK_2026_05_08_2330"
WATCHDOG_LOCK_TIMEOUT_S = 600
LAYER_CATALOG_FROZEN_COUNT = 18

# Forbidden paths/flags (PERMANENT lock)
FORBIDDEN_DOCTRINAL = {
    "legacy_paths": True,
    "analysis_v6": True,
    "debug_panels": True,
    "mini_tables_v6": True,
}

# Reload overlay path (P20_PHASE4) — utilisé pour calculer le sync SHA
RELOAD_OVERLAY_PATH = Path(
    "/app/backend/data/pipelines/territoire_omega_reload/"
    "territoire_omega_reload_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_last_force_reload() -> Dict[str, Any]:
    """Lit le dernier force-reload (anti-générique : pas de fake)."""
    if not RELOAD_OVERLAY_PATH.exists():
        return {
            "available": False,
            "reason": "NO_RELOAD_EVER_EXECUTED",
            "reload_overlay_path": str(RELOAD_OVERLAY_PATH),
        }
    try:
        state = json.loads(
            RELOAD_OVERLAY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "available": False,
            "reason": "OVERLAY_PARSE_ERROR",
        }
    history = state.get("history", []) or []
    if not history:
        return {
            "available": False,
            "reason": "EMPTY_HISTORY",
        }
    last = history[-1]
    return {
        "available": True,
        "last_force_reload_sha256": last.get("reload_sha256"),
        "last_force_reload_at_utc": last.get("executed_at_utc"),
        "last_force_reload_verdict": last.get("verdict"),
        "last_force_reload_n_overlays_scanned": (
            last.get("overlay_scan_summary", {}).get(
                "n_overlays_scanned")),
        "last_force_reload_n_engines_reloaded": (
            last.get("engine_reload_summary", {}).get("n_reloaded")),
        "last_watchdog_timeout_s": (
            last.get("watchdog_state", {}).get(
                "current_timeout_s")),
    }


def get_territoire_omega_canonical_status() -> Dict[str, Any]:
    """État canonique doctrinal (READ-ONLY · PUBLIC)."""
    last_reload = _read_last_force_reload()
    canonical_payload: Dict[str, Any] = {
        "manifest_id": "TERRITOIRE_OMEGA_CANONICAL_STATUS_Ω",
        "ordre": "P20_PHASE5_CANONICAL_LOCK_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "canonical_version": CANONICAL_LOCK_VERSION,
        "single_source_of_truth_enforced": True,
        "territoire_omega_canonical": "ENFORCED",
        "unified_panel_mode": "PRIMARY_ONLY_PERMANENT",
        "forbidden_doctrinal": FORBIDDEN_DOCTRINAL,
        "watchdog_lock": {
            "enforced": True,
            "timeout_s": WATCHDOG_LOCK_TIMEOUT_S,
            "lock_status": "ENFORCED_PERMANENT",
        },
        "layer_catalog": {
            "frozen_count": LAYER_CATALOG_FROZEN_COUNT,
            "groups_count": 6,  # A,B,C,D,E,F
            "zindex_institutional_enforced": True,
        },
        "service_worker_controlled": "PERMANENT",
        "sync_indicator": {
            "enabled": True,
            "scope": "last_force_reload_timestamp_utc",
            "data": last_reload,
        },
        "v30_lock": "INVIOLÉ",
        "anti_generique_strict": True,
        "scanned_at_utc": _utc_now(),
    }
    # Compute canonical SHA-256 of the entire status payload
    canonical_sha256 = hashlib.sha256(
        json.dumps(
            canonical_payload, sort_keys=True,
            ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    canonical_payload["canonical_sha256"] = canonical_sha256
    return canonical_payload


__all__ = [
    "CANONICAL_LOCK_VERSION",
    "WATCHDOG_LOCK_TIMEOUT_S",
    "LAYER_CATALOG_FROZEN_COUNT",
    "FORBIDDEN_DOCTRINAL",
    "RELOAD_OVERLAY_PATH",
    "get_territoire_omega_canonical_status",
]
