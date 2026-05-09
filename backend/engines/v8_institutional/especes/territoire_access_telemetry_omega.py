"""territoire_access_telemetry_omega.py — P22B access diagnostic.

═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

P22B · TERRITOIRE ACCESS DIAGNOSTIC :
  · `expose_territoire_access_status_endpoint: ENABLED`
  · `log_territoire_access_failures: ENABLED`
  · `enforce_route_admin_territoire_enabled: ENFORCED`

DOCTRINE :
  · Lecture seule des routes connues
  · Persistance JSONL des access failures (anti-générique)
  · Aucun fake — chaque entrée = vraie tentative client
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


TELEMETRY_ROOT = Path(
    "/app/backend/data/pipelines/territoire_access_telemetry")
ACCESS_FAILURES_PATH = (
    TELEMETRY_ROOT / "access_failures.jsonl")


# Canonical admin premium routes (P22B)
CANONICAL_ADMIN_ROUTES: List[Dict[str, Any]] = [
    {"path": "/admin/bce-4x-premium",
     "purpose": "Admin Premium Index",
     "component": "AdminPremiumIndexPage"},
    {"path": "/admin/bce-4x-premium/visualizer",
     "purpose": "Visualizer 18 layers",
     "component": "Visualizer18Page"},
    {"path": "/admin/bce-4x-premium/territoire",
     "purpose": "Rapports Ω opérationnels (P15)",
     "component": "TerritoireReportPage"},
    {"path": "/admin/bce-4x-premium/waypoint",
     "purpose": "Field Guides waypoint (P17)",
     "component": "WaypointGuidePage"},
    {"path": "/admin/bce-4x-premium/manual",
     "purpose": "Manuel 18 couches (P18)",
     "component": "LayerManualPage"},
    {"path": "/admin/bce-4x-premium/merkle",
     "purpose": "Merkle Audit + OTS (P14+P24)",
     "component": "MerkleAuditPage"},
    {"path": "/admin/bce-4x-premium/validation",
     "purpose": "Validations Commandant (P22)",
     "component": "ValidationsPage"},
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_access_failure(
    target_path: str,
    failure_reason: str,
    context: Optional[Dict[str, Any]] = None,
    user_agent: Optional[str] = None,
) -> Dict[str, Any]:
    """Persist access failure JSONL (anti-générique strict)."""
    TELEMETRY_ROOT.mkdir(parents=True, exist_ok=True)
    record = {
        "target_path": target_path,
        "failure_reason": failure_reason,
        "context": context or {},
        "user_agent_sha256": (
            hashlib.sha256(user_agent.encode()).hexdigest()[:16]
            if user_agent else None),
        "logged_at_utc": _utc_now(),
    }
    with open(ACCESS_FAILURES_PATH, "a",
              encoding="utf-8") as f:
        f.write(
            json.dumps(record, ensure_ascii=False, default=str)
            + "\n")
    return {
        "logged": True,
        "record_sha256": hashlib.sha256(
            json.dumps(record, sort_keys=True,
                       ensure_ascii=False, default=str
                       ).encode("utf-8")).hexdigest()[:16],
        "logged_at_utc": record["logged_at_utc"],
    }


def get_territoire_access_status() -> Dict[str, Any]:
    """État accès admin/territoire (PUBLIC RO · diagnostic)."""
    n_failures = 0
    last_failures: List[Dict[str, Any]] = []
    if ACCESS_FAILURES_PATH.exists():
        lines = ACCESS_FAILURES_PATH.read_text(
            encoding="utf-8").splitlines()
        n_failures = len(lines)
        last_failures = [
            json.loads(line) for line in lines[-5:]
            if line.strip()
        ]

    return {
        "manifest_id": "TERRITOIRE_ACCESS_STATUS_Ω",
        "ordre": "P22B_RESTORE_TERRITOIRE_ACCESS_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "canonical_admin_routes": CANONICAL_ADMIN_ROUTES,
        "n_canonical_routes": len(CANONICAL_ADMIN_ROUTES),
        "telemetry": {
            "n_access_failures_logged": n_failures,
            "last_failures": last_failures,
            "telemetry_path": str(ACCESS_FAILURES_PATH),
        },
        "auth_requirements": {
            "method": "X-Commandant-Token",
            "storage": "localStorage[bce4x_commandant_token]",
            "verify_endpoint":
                "POST /api/v30/super-masters/messaging-engine-channel-hook-activate",
        },
        "preview_url_template":
            "{REACT_APP_BACKEND_URL}{path}",
        "v30_lock": "INVIOLÉ",
        "anti_generique_strict": True,
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "TELEMETRY_ROOT",
    "ACCESS_FAILURES_PATH",
    "CANONICAL_ADMIN_ROUTES",
    "log_access_failure",
    "get_territoire_access_status",
]
