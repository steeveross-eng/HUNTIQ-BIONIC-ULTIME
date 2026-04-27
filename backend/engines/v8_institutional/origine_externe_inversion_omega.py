"""
origine_externe_inversion_omega.py — PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω
================================================================================
Phase     : PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

ENGINE ORIGINE_EXTERNE_INVERSION Ω — récupération non destructive des corridors
V30 dont path[-1] (extrémité) tombe dans la couronne externe alors que path[0]
(origine) en est exclue.

═════════════════════════════════════════════════════════════════════════
RÈGLE D'INVERSION (§1 directive Commandant XIX-P2)
═════════════════════════════════════════════════════════════════════════

Pour chaque corridor V30 :
  - SI distance(WP, path[0])  ∉ [600 ; 780 m]
    ET distance(WP, path[-1]) ∈ [600 ; 780 m]
        → path' = reverse(path)
        → re-annotation predictive_omega_v2 sur path' (bearing inversé)
        → corridor.origin_external_inversion_applied = True
        → corridor.origin_external_inversion_reason  = "ENDPOINT_IN_CROWN"
  - SINON : aucune inversion.

Placement dans le pipeline :
  V30 → species_modulator → predictive_v2(p1) → INTERZONE → VEINEUX
   → predictive_v2(p2)
   → ◆ ORIGINE_EXTERNE_INVERSION_Ω (XIX-P2) ◆   ← (CE MODULE)
   → ORIGINE_EXTERNE_FILTER_Ω (XIX-P1)          ← validation finale
   → ECOLOGICAL_ORCHESTRATOR → CORRIDORS_VITAUX_Ω → RENDUΩ

§2 — Conformité institutionnelle
  - XIX-P1 reste la source de vérité pour OUTSIDE_CROWN/LOW_DENSITY/LOW_HITS.
  - XIX-P2 ne modifie QUE l'ordre des points (path).
  - Les contraintes terrain/contamination_v2/affûts/pentes restent valides
    (path géographiquement identique).
  - predictive_omega_v2 est ré-annoté pour mettre à jour les métriques
    sensibles à l'orientation (bearing, direction_score).
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional

# Couronne institutionnelle (lue depuis XIX-P1 pour cohérence)
try:
    from engines.v8_institutional.origine_externe_filter_omega import (
        ORIGINE_RADIUS_MIN_M, ORIGINE_RADIUS_MAX_M,
    )
except Exception:  # pragma: no cover — fallback safe
    ORIGINE_RADIUS_MIN_M = 600.0
    ORIGINE_RADIUS_MAX_M = 780.0

# Mode ENFORCE (par défaut activé)
ENFORCE_MODE = os.environ.get("XIX_P2_ENFORCE", "1") == "1"

PHASE_TAG = "PHASE_XIX_P2"
PHASE_NAME = "PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω"


# ═══════════════════════════════════════════════════════════════════════
# Helper géométrique (cohérent avec XIX-P1)
# ═══════════════════════════════════════════════════════════════════════
def _dist_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


def _in_crown(d: float) -> bool:
    return ORIGINE_RADIUS_MIN_M <= d <= ORIGINE_RADIUS_MAX_M


# ═══════════════════════════════════════════════════════════════════════
# Décision d'inversion par corridor
# ═══════════════════════════════════════════════════════════════════════
def evaluate_inversion(corridor: Dict[str, Any],
                        waypoint: Dict[str, float]) -> Dict[str, Any]:
    """Détermine si le corridor doit être inversé (XIX-P2 §1)."""
    path = corridor.get("path") or []
    wp_lat = float(waypoint.get("lat", 0.0))
    wp_lng = float(waypoint.get("lng") or waypoint.get("lon") or 0.0)

    if len(path) < 2:
        return {
            "should_invert": False,
            "reason": None,
            "distance_origin_m": None,
            "distance_endpoint_m": None,
            "origin_in_crown": False,
            "endpoint_in_crown": False,
        }

    d_origin = _dist_m([wp_lat, wp_lng], [path[0][0], path[0][1]])
    d_end = _dist_m([wp_lat, wp_lng], [path[-1][0], path[-1][1]])
    origin_in = _in_crown(d_origin)
    end_in = _in_crown(d_end)

    # §1 : path[0] ∉ couronne ET path[-1] ∈ couronne → inverser
    should = (not origin_in) and end_in
    return {
        "should_invert": should,
        "reason": "ENDPOINT_IN_CROWN" if should else None,
        "distance_origin_m": round(d_origin, 1),
        "distance_endpoint_m": round(d_end, 1),
        "origin_in_crown": origin_in,
        "endpoint_in_crown": end_in,
    }


# ═══════════════════════════════════════════════════════════════════════
# Application au bundle
# ═══════════════════════════════════════════════════════════════════════
def apply_origine_externe_inversion_to_bundle(
        bundle: Dict[str, Any],
        species: Optional[str] = None,
        month: int = 10, hour: int = 14) -> Dict[str, Any]:
    """Inverse les corridors §1 + ré-annote predictive_omega_v2 sur les inversés."""
    if not isinstance(bundle, dict):
        return bundle
    if not ENFORCE_MODE:
        bundle["origine_externe_inversion_applied"] = False
        bundle["origine_externe_inversion_stats"] = {
            "phase": PHASE_NAME, "subphase": PHASE_TAG,
            "enforce_mode": False, "skipped": True,
        }
        return bundle

    corridors = bundle.get("corridors") or []
    waypoint = bundle.get("waypoint") or {}
    species = species or bundle.get("species") or "orignal"

    inverted_count = 0
    skipped_count = 0
    for c in corridors:
        ev = evaluate_inversion(c, waypoint=waypoint)
        if ev["should_invert"]:
            # §1 : reverse(path)
            path = c.get("path") or []
            c["path"] = list(reversed(path))
            c["origin_external_inversion_applied"] = True
            c["origin_external_inversion_reason"] = "ENDPOINT_IN_CROWN"
            c["origin_external_inversion_audit"] = ev
            c["origin_external_inversion_filter_phase"] = PHASE_TAG
            inverted_count += 1
        else:
            c["origin_external_inversion_applied"] = False
            c["origin_external_inversion_reason"] = None
            c["origin_external_inversion_audit"] = ev
            c["origin_external_inversion_filter_phase"] = PHASE_TAG
            skipped_count += 1

    # §2 — Ré-annoter predictive_omega_v2 SEULEMENT si au moins 1 inversion
    # (le path est géographiquement identique mais le bearing a tourné de 180°).
    if inverted_count > 0:
        try:
            from engines.v8_institutional.predictive_omega_v2 import (
                apply_predictive_omega_v2_to_bundle,
            )
            bundle = apply_predictive_omega_v2_to_bundle(
                bundle, species=species, month=month, hour=hour,
            )
            bundle["predictive_omega_v2_post_inversion_applied"] = True
        except Exception as e:
            bundle["predictive_omega_v2_post_inversion_applied"] = False
            bundle["predictive_omega_v2_post_inversion_error"] = str(e)

    bundle["origine_externe_inversion_applied"] = True
    bundle["origine_externe_inversion_stats"] = {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "total_input": len(corridors),
        "inverted_count": inverted_count,
        "skipped_count": skipped_count,
        "rate_pct": round(100.0 * inverted_count / max(1, len(corridors)), 1),
        "crown_min_m": ORIGINE_RADIUS_MIN_M,
        "crown_max_m": ORIGINE_RADIUS_MAX_M,
        "predictive_v2_reannotated": inverted_count > 0,
    }
    return bundle


def get_inversion_status() -> Dict[str, Any]:
    """Audit de la configuration."""
    return {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "crown_min_m": ORIGINE_RADIUS_MIN_M,
        "crown_max_m": ORIGINE_RADIUS_MAX_M,
        "rule": "Si path[0] ∉ couronne ET path[-1] ∈ couronne → inverser",
    }
