"""
baseline_registry_omega.py — PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0
========================================================================================
Phase     : PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0 (§1.1, §7.2)
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

REGISTRE INSTITUTIONNEL IMMUABLE — BASELINE V30_STATUS_Ω.

Cette baseline est FIGÉE à la valeur officielle observée lors de la phase
`PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω` :

    v30_alignment_score_baseline = 36.70   (NON_CONFORME)
    acceptance_rate_baseline     = 43.18 % (19 / 44)

Règles institutionnelles :
    - Aucune modification rétroactive (lecture seule ABSOLUE).
    - Toute mesure future est comparée à cette baseline.
    - Interdiction de mise en production si v30_alignment_score < BASELINE.
    - Rollback automatique si dégradation sous BASELINE (§7.2).

V30 engine strictement LOCKED — ce module ne touche PAS au V30 engine.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Final

# ═══════════════════════════════════════════════════════════════════════
# BASELINE IMMUABLE — SHA-256 auto-calculé pour détection de tampering
# ═══════════════════════════════════════════════════════════════════════
_BASELINE_PAYLOAD: Final[Dict[str, Any]] = {
    "phase": "PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω",
    "baseline_locked_by": "COMMANDANT_STEEVE-MAX",
    "waypoint_official": {"lat": 48.206657, "lng": -68.382422},
    "v30_alignment_score_baseline": 36.70,
    "alignment_label_baseline": "NON_CONFORME",
    "acceptance_rate_baseline_pct": 43.18,
    "accepted_baseline": 19,
    "total_baseline": 44,
    "thresholds": {
        "partial_below": 70.0,
        "conform_min": 70.0,
        "conform_omega_min": 90.0,
    },
    "forbidden_labels": ["BON", "MODERE", "FAIBLE", "EXCELLENT", "MOYEN", "ACCEPTABLE"],
    "authorized_labels": ["PARTIEL", "CONFORME", "CONFORME_Ω"],
    "locked_at_phase": "PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME_ENFORCEMENT_P0",
}


def _compute_baseline_hash() -> str:
    canon = json.dumps(_BASELINE_PAYLOAD, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canon).hexdigest()


BASELINE_SHA256: Final[str] = _compute_baseline_hash()


def get_baseline() -> Dict[str, Any]:
    """Retourne une COPIE lecture seule de la baseline institutionnelle."""
    return {
        **_BASELINE_PAYLOAD,
        "sha256": BASELINE_SHA256,
        "immutable": True,
    }


def alignment_label_institutional(score: float) -> str:
    """Grille institutionnelle §6.1 :
        < 70  → PARTIEL
        ≥ 70  → CONFORME
        ≥ 90  → CONFORME_Ω
    Le label 'BON' est strictement INTERDIT.
    """
    try:
        s = float(score)
    except (TypeError, ValueError):
        return "PARTIEL"
    if s >= 90.0:
        return "CONFORME_Ω"
    if s >= 70.0:
        return "CONFORME"
    return "PARTIEL"


def compare_to_baseline(current_score: float) -> Dict[str, Any]:
    """Compare un score courant à la baseline. Retourne Δ + verdict de
    rollback (§7.2).
    """
    try:
        cs = float(current_score)
    except (TypeError, ValueError):
        cs = 0.0
    base = float(_BASELINE_PAYLOAD["v30_alignment_score_baseline"])
    delta = round(cs - base, 2)
    below = cs < base
    return {
        "baseline_score": base,
        "current_score": round(cs, 2),
        "delta_score": delta,
        "below_baseline": below,
        "rollback_required": below,
        "current_label": alignment_label_institutional(cs),
        "baseline_label": _BASELINE_PAYLOAD["alignment_label_baseline"],
        "sha256_registry": BASELINE_SHA256,
    }


def assert_label_institutional(label: str) -> None:
    """Lève ValueError si label non institutionnel (§6.2 — interdiction 'BON')."""
    if label not in _BASELINE_PAYLOAD["authorized_labels"]:
        raise ValueError(
            f"Label '{label}' INTERDIT par §6.2 — "
            f"autorisés : {_BASELINE_PAYLOAD['authorized_labels']}"
        )
