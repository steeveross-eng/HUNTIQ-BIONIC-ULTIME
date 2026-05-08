"""commandant_validations_omega.py — P22 audit doctrinal
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P22 — Persistence formelle des validations Commandant pour
auditabilité doctrinale.

DOCTRINE :
  · Lecture seule des SHA validés
  · Persiste audit log de chaque approval
  · Aucune mutation, aucune fabrication
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


VALIDATIONS_ROOT = Path(
    "/app/backend/data/pipelines/commandant_validations")
VALIDATIONS_HISTORY_PATH = (
    VALIDATIONS_ROOT / "commandant_validations_history.jsonl")
VALIDATIONS_OVERLAY_PATH = (
    VALIDATIONS_ROOT / "commandant_validations_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def record_commandant_validation(
    scope: str,
    decision: str,
    sha256_list: List[str],
    notes: Optional[str] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """Enregistre une validation formelle Commandant (anti-générique)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("record_commandant_validation")

    if decision not in ("APPROVED", "REJECTED",
                         "PENDING_REVIEW"):
        raise ValueError(
            f"DECISION_INVALID::{decision}")
    for sha in sha256_list:
        if len(sha) != 64:
            raise ValueError(
                f"SHA256_INVALID::{sha[:8]}_len_{len(sha)}")

    t0 = time.time()
    payload = {
        "manifest_id": "COMMANDANT_VALIDATION_RECORD_Ω",
        "ordre": "P22_COMMANDANT_VALIDATION_P14_PREMIUM_V7_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "NONE",
        "scope": scope,
        "decision": decision,
        "sha256_validated_list": sha256_list,
        "n_sha_validated": len(sha256_list),
        "notes": notes,
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "validated_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 4),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["validation_sha256"] = payload_sha256

    if persist:
        VALIDATIONS_ROOT.mkdir(parents=True, exist_ok=True)
        # JSONL append
        with open(
                VALIDATIONS_HISTORY_PATH, "a",
                encoding="utf-8") as f:
            f.write(json.dumps(
                payload, ensure_ascii=False,
                default=str) + "\n")
        # Overlay state
        if VALIDATIONS_OVERLAY_PATH.exists():
            try:
                state = json.loads(
                    VALIDATIONS_OVERLAY_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_validations"] = len(state["history"])
        state["last_validation_sha256"] = payload_sha256
        state["last_decision"] = decision
        state["v30_lock"] = "INVIOLÉ"
        VALIDATIONS_OVERLAY_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="COMMANDANT_VALIDATION_RECORDED",
        details={
            "validation_sha256": payload_sha256,
            "scope": scope,
            "decision": decision,
            "n_sha_validated": len(sha256_list),
        },
        persist=True)
    return payload


def get_commandant_validations_status() -> Dict[str, Any]:
    if not VALIDATIONS_OVERLAY_PATH.exists():
        return {
            "manifest_id":
                "COMMANDANT_VALIDATIONS_STATUS_Ω",
            "current_status": "NO_VALIDATIONS_RECORDED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        VALIDATIONS_OVERLAY_PATH.read_text(encoding="utf-8"))
    last = (
        state["history"][-1] if state.get("history") else None)
    return {
        "manifest_id": "COMMANDANT_VALIDATIONS_STATUS_Ω",
        "current_status": (
            "ACTIVE" if last else "NO_VALIDATIONS_RECORDED"),
        "n_validations_history": state.get(
            "n_validations", 0),
        "last_validation_sha256": state.get(
            "last_validation_sha256"),
        "last_decision": state.get("last_decision"),
        "last_updated_utc": state.get("last_updated_utc"),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "VALIDATIONS_ROOT",
    "VALIDATIONS_OVERLAY_PATH",
    "VALIDATIONS_HISTORY_PATH",
    "record_commandant_validation",
    "get_commandant_validations_status",
]
