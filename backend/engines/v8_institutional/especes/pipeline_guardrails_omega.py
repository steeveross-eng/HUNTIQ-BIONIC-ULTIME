"""
pipeline_guardrails_omega.py — PIPELINE_GUARDRAILS_RESTORE
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Module de garde-fous doctrinaux pour le pipeline NOAA / NASA / USGS.

Directive PIPELINE_GUARDRAILS_RESTORE :
  · doctrine                : BCE-4X
  · profile                 : STEVE_MAX
  · drift_control           : DRIFT_ZERO_STRICT
  · lock_level              : V30_LOCK_INVIOLABLE
  · anti_regression         : FULL_PYTEST_ENFORCED
  · safety_nets             : NO_AUTO_HOOK_EXPANSION,
                              NO_PARALLEL_HOOKS_WITHOUT_EXPLICIT_DIRECTIVE,
                              NO_ENDPOINT_SWITCH_WITHOUT_COMMANDANT_CONFIRM
  · modularity              : 100_PERCENT_MODULAR
  · logging.audit_level     : FORENSIC
  · logging.scope           : B2_CREDENTIALS, ENDPOINT_PROBES,
                              HOOK_ACTIVATIONS, CONFIG_CHANGES
  · logging.retention       : STRICT
  · execution_mode.autonomy : LIMITED
  · execution_mode.default_posture : STANDBY_STRICT
  · execution_mode.require_token   : X-COMMANDANT-TOKEN

GARDE-FOUS DOCTRINAUX :
  · FUSION ADD-ONLY strict (aucune mutation des modules maîtres)
  · V30_LOCK INVIOLÉ
  · ANTI_GÉNÉRIQUE_STRICT (statuts RÉELS uniquement)
  · Toutes les opérations sensibles tracées avec SHA-256
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


GUARDRAILS_ROOT = Path("/app/backend/data/pipelines/guardrails")
GUARDRAILS_STATE_PATH = GUARDRAILS_ROOT / "guardrails_state.json"
GUARDRAILS_FORENSIC_LOG_PATH = (
    GUARDRAILS_ROOT / "guardrails_forensic_log.jsonl")


# ═════════════════════════════════════════════════════════════════════════
# Doctrine canonique (immuable au runtime)
# ═════════════════════════════════════════════════════════════════════════
GUARDRAILS_DOCTRINE: Dict[str, Any] = {
    "doctrine": "BCE-4X",
    "profile": "STEVE_MAX",
    "protections": {
        "drift_control": "DRIFT_ZERO_STRICT",
        "lock_level": "V30_LOCK_INVIOLABLE",
        "anti_regression": "FULL_PYTEST_ENFORCED",
        "safety_nets": [
            "NO_AUTO_HOOK_EXPANSION",
            "NO_PARALLEL_HOOKS_WITHOUT_EXPLICIT_DIRECTIVE",
            "NO_ENDPOINT_SWITCH_WITHOUT_COMMANDANT_CONFIRM",
        ],
        "modularity": "100_PERCENT_MODULAR",
        "logging": {
            "audit_level": "FORENSIC",
            "scope": [
                "B2_CREDENTIALS",
                "ENDPOINT_PROBES",
                "HOOK_ACTIVATIONS",
                "CONFIG_CHANGES",
            ],
            "retention": "STRICT",
        },
        "execution_mode": {
            "autonomy": "LIMITED",
            "default_posture": "STANDBY_STRICT",
            "require_token": "X-COMMANDANT-TOKEN",
        },
    },
    "status_directive": "RESTORE_AND_ENFORCE_ALL_GUARDRAILS",
}

# Scopes valides pour le forensic logger (anti-générique strict)
VALID_FORENSIC_SCOPES = {
    "B2_CREDENTIALS",
    "ENDPOINT_PROBES",
    "HOOK_ACTIVATIONS",
    "CONFIG_CHANGES",
    "HABITAT",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_of_payload(payload: Any) -> str:
    s = json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ═════════════════════════════════════════════════════════════════════════
# 1. Restore & enforce
# ═════════════════════════════════════════════════════════════════════════
def restore_and_enforce_guardrails(
    persist: bool = True,
    activated_by: str = "COMMANDANT_STEVE_MAX",
) -> Dict[str, Any]:
    """Active la directive PIPELINE_GUARDRAILS_RESTORE.

    Persiste l'état des garde-fous dans guardrails_state.json (FUSION
    ADD-ONLY : ajoute une entrée historique sans écraser les précédentes).

    Anti-générique strict : aucune fabrication. État réel persisté.
    """
    t0 = time.time()
    activation_payload = {
        "manifest_id": "PIPELINE_GUARDRAILS_RESTORE_Ω",
        "doctrine": GUARDRAILS_DOCTRINE,
        "activated": True,
        "activated_by": activated_by,
        "activated_at_utc": _utc_now(),
        "status": "ENFORCED",
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
    }
    activation_sha256 = _sha256_of_payload(activation_payload)
    activation_payload["activation_sha256"] = activation_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        GUARDRAILS_ROOT.mkdir(parents=True, exist_ok=True)
        # FUSION ADD-ONLY : on lit l'historique existant et on append
        if GUARDRAILS_STATE_PATH.exists():
            try:
                state = json.loads(
                    GUARDRAILS_STATE_PATH.read_text(encoding="utf-8"))
                if not isinstance(state, dict) or "history" not in state:
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}

        state["history"].append(activation_payload)
        state["last_updated_utc"] = _utc_now()
        state["n_activations"] = len(state["history"])
        state["current_status"] = "ENFORCED"
        state["current_doctrine"] = GUARDRAILS_DOCTRINE
        state["current_activation_sha256"] = activation_sha256
        state["v30_lock"] = "INVIOLÉ"

        GUARDRAILS_STATE_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["state_path"] = str(GUARDRAILS_STATE_PATH)
        persisted["state_size_bytes"] = (
            GUARDRAILS_STATE_PATH.stat().st_size)
        persisted["n_activations_history"] = state["n_activations"]

        # Audit doctrinal pour traçabilité longitudinale
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "PIPELINE_GUARDRAILS",
            "subtype": "RESTORE_AND_ENFORCE",
            "ordre": "PIPELINE_GUARDRAILS_RESTORE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "activated_by": activated_by,
            "activation_sha256": activation_sha256,
            "n_activations_history": state["n_activations"],
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

        # Premier événement forensique : activation des guardrails
        log_forensic_event(
            scope="CONFIG_CHANGES",
            event="GUARDRAILS_ACTIVATED",
            details={
                "activation_sha256": activation_sha256,
                "activated_by": activated_by,
                "n_activations_history": state["n_activations"],
            },
            persist=True,
        )

    return {
        "manifest_id": "PIPELINE_GUARDRAILS_RESTORE_EXECUTE_Ω",
        "ordre": "PIPELINE_GUARDRAILS_RESTORE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "activated": True,
        "status": "RESTORE_AND_ENFORCE_ALL_GUARDRAILS",
        "activation_sha256": activation_sha256,
        "doctrine_payload": GUARDRAILS_DOCTRINE,
        "persisted_paths": persisted,
        "no_engine_recompute_triggered": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. Status read-only (V30_LOCK respecté)
# ═════════════════════════════════════════════════════════════════════════
def get_guardrails_state() -> Dict[str, Any]:
    """Lit l'état actuel des guardrails (read-only).

    Anti-générique strict : si pas activé, retourne status réel
    NOT_ACTIVATED.
    """
    if not GUARDRAILS_STATE_PATH.exists():
        return {
            "manifest_id": "PIPELINE_GUARDRAILS_STATE_Ω",
            "ordre": "PIPELINE_GUARDRAILS_RESTORE",
            "current_status": "NOT_ACTIVATED",
            "doctrine_canonique": GUARDRAILS_DOCTRINE,
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        GUARDRAILS_STATE_PATH.read_text(encoding="utf-8"))
    last_act = (
        state["history"][-1] if state.get("history") else None)
    return {
        "manifest_id": "PIPELINE_GUARDRAILS_STATE_Ω",
        "ordre": "PIPELINE_GUARDRAILS_RESTORE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "current_status": state.get("current_status"),
        "current_doctrine": state.get("current_doctrine"),
        "current_activation_sha256": state.get(
            "current_activation_sha256"),
        "n_activations_history": state.get("n_activations", 0),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_activation": last_act,
        "state_path": str(GUARDRAILS_STATE_PATH),
        "state_size_bytes": GUARDRAILS_STATE_PATH.stat().st_size,
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. Forensic logger (logging.scope = B2_CREDENTIALS, ENDPOINT_PROBES,
#    HOOK_ACTIVATIONS, CONFIG_CHANGES)
# ═════════════════════════════════════════════════════════════════════════
def log_forensic_event(
    scope: str,
    event: str,
    details: Optional[Dict[str, Any]] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    """Append-only forensic log (JSONL) pour les opérations sensibles.

    Args:
      scope: doit appartenir à VALID_FORENSIC_SCOPES.
      event: nom court de l'événement (e.g., 'B2_PROBE',
        'CFSV2_CANDIDATE_PROBE').
      details: dict de contexte (anti-générique : valeurs réelles).

    Returns:
      Le record forensique persisté.
    """
    if scope not in VALID_FORENSIC_SCOPES:
        raise ValueError(
            f"FORENSIC_SCOPE_INVALID::{scope} :: valides="
            f"{sorted(VALID_FORENSIC_SCOPES)}")
    record = {
        "ts_utc": _utc_now(),
        "ts_unix_ms": int(time.time() * 1000),
        "scope": scope,
        "event": event,
        "details": details or {},
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "v30_lock": "INVIOLÉ",
    }
    record_sha256 = _sha256_of_payload(record)
    record["record_sha256"] = record_sha256
    if persist:
        GUARDRAILS_ROOT.mkdir(parents=True, exist_ok=True)
        with GUARDRAILS_FORENSIC_LOG_PATH.open(
                "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def list_forensic_events(
    scope: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """Liste les événements forensiques persistés (read-only)."""
    if not GUARDRAILS_FORENSIC_LOG_PATH.exists():
        return {
            "manifest_id": "GUARDRAILS_FORENSIC_LIST_Ω",
            "scope_filter": scope,
            "n_total": 0,
            "n_returned": 0,
            "events": [],
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    events: List[Dict[str, Any]] = []
    with GUARDRAILS_FORENSIC_LOG_PATH.open(
            "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if scope and rec.get("scope") != scope:
                continue
            events.append(rec)
    n_total = len(events)
    # Retourne les N derniers (ordre chronologique ascendant)
    events_returned = events[-limit:] if limit > 0 else events
    return {
        "manifest_id": "GUARDRAILS_FORENSIC_LIST_Ω",
        "ordre": "PIPELINE_GUARDRAILS_RESTORE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "scope_filter": scope,
        "limit": limit,
        "n_total_matching": n_total,
        "n_returned": len(events_returned),
        "events": events_returned,
        "log_path": str(GUARDRAILS_FORENSIC_LOG_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. Enforcement check (utilisable par les autres modules)
# ═════════════════════════════════════════════════════════════════════════
def is_guardrails_enforced() -> bool:
    """Retourne True si PIPELINE_GUARDRAILS_RESTORE est actif."""
    if not GUARDRAILS_STATE_PATH.exists():
        return False
    try:
        state = json.loads(
            GUARDRAILS_STATE_PATH.read_text(encoding="utf-8"))
        return state.get("current_status") == "ENFORCED"
    except Exception:
        return False


def require_guardrails_enforced(operation: str) -> None:
    """Raise GuardrailsNotEnforcedError si garde-fous inactifs.

    À utiliser AVANT toute opération sensible (probe candidate
    autonome, switch endpoint, expansion hook).
    """
    if not is_guardrails_enforced():
        raise GuardrailsNotEnforcedError(
            f"OPERATION_BLOCKED::{operation}::"
            "PIPELINE_GUARDRAILS_RESTORE_REQUIRED_FIRST")


class GuardrailsNotEnforcedError(RuntimeError):
    """Levée quand une opération sensible est tentée sans guardrails."""


__all__ = [
    "GUARDRAILS_ROOT",
    "GUARDRAILS_STATE_PATH",
    "GUARDRAILS_FORENSIC_LOG_PATH",
    "GUARDRAILS_DOCTRINE",
    "VALID_FORENSIC_SCOPES",
    "restore_and_enforce_guardrails",
    "get_guardrails_state",
    "log_forensic_event",
    "list_forensic_events",
    "is_guardrails_enforced",
    "require_guardrails_enforced",
    "GuardrailsNotEnforcedError",
]
