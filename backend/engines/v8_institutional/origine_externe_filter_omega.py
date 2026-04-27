"""
origine_externe_filter_omega.py — PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω
================================================================================
Phase     : PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

ENGINE ORIGINE_EXTERNE_FILTER Ω — filtre institutionnel d'origine spatiale
des corridors V30 sur la couronne externe 30 % avec validation par densité
GPS réelle (lecture des champs `predictive_omega_v2.metrics`).

═════════════════════════════════════════════════════════════════════════
RÈGLE ORIGINE EXTERNE (§2)
═════════════════════════════════════════════════════════════════════════

§2.1 — Condition spatiale
  - Rayon fonctionnel nominal : 600 m
  - Couronne externe 30 %     : [600 m ; 780 m]
  - Le POINT_ORIGINE (path[0]) DOIT être dans ORIGINE_EXTERNE_30
  - Si distance(WAYPOINT, POINT_ORIGINE) ∉ [600 m ; 780 m]
      → REJET (FILTER_ORIGINE_EXTERNE_FAIL : OUTSIDE_CROWN)

§2.2 — Condition GPS (densité)
  - Lire `corridor.predictive_omega_v2.metrics.gps_density_ratio`
  - Lire `corridor.predictive_omega_v2.metrics.gps_weighted_hits`
  - Seuils par défaut (configurables via env) :
      THRESH_DENSITY_ORIGINE = 0.25
      THRESH_HITS_ORIGINE    = 5
  - Si gps_density_ratio < THRESH_DENSITY_ORIGINE → REJET (LOW_DENSITY)
  - Si gps_weighted_hits  < THRESH_HITS_ORIGINE   → REJET (LOW_HITS)

§2.3 — Placement dans le pipeline
  V30 → species_modulator → predictive_omega_v2(p1) → INTERZONE → VEINEUX
   → predictive_omega_v2(p2)
   → ◆ ORIGINE_EXTERNE_FILTER_Ω (PHASE XIX-P1) ◆
   → ECOLOGICAL_ORCHESTRATOR → CORRIDORS_VITAUX_Ω → RENDUΩ → ANTI-RÉGRESSION

§3 — Métadonnées institutionnelles
  Champs ajoutés à chaque corridor :
    origin_external_filter_phase    = "PHASE_XIX_P1"
    origin_external_passed          = bool
    origin_external_valid           = bool  (alias)
    origin_external_reason          = "OUTSIDE_CROWN" | "LOW_DENSITY" | "LOW_HITS" | None
    origin_external_radius_min_m    = 600
    origin_external_radius_max_m    = 780
    origin_external_density_threshold = THRESH_DENSITY_ORIGINE
    origin_external_hits_threshold    = THRESH_HITS_ORIGINE

§4 — Mode ENFORCE
  ENFORCE par défaut. Les corridors rejetés sont retirés du bundle et
  consignés dans `corridors_rejected_origine_externe_xix` pour audit.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# Constantes institutionnelles (directive Commandant XIX-P1)
# ═══════════════════════════════════════════════════════════════════════
RAYON_FONCTIONNEL_NOMINAL_M = float(
    os.environ.get("XIX_P1_RAYON_FONCTIONNEL_M", "600.0")
)
ORIGINE_EXTERNE_FRACTION = 0.30  # 30 % au-dessus du rayon nominal

# Couronne externe ORIGINE_EXTERNE_30 = [600 m ; 780 m]
ORIGINE_RADIUS_MIN_M = RAYON_FONCTIONNEL_NOMINAL_M
ORIGINE_RADIUS_MAX_M = RAYON_FONCTIONNEL_NOMINAL_M * (1.0 + ORIGINE_EXTERNE_FRACTION)

# Seuils GPS (configurables via env, valeurs par défaut directive)
THRESH_DENSITY_ORIGINE = float(
    os.environ.get("XIX_P1_THRESH_DENSITY_ORIGINE", "0.25")
)
THRESH_HITS_ORIGINE = float(
    os.environ.get("XIX_P1_THRESH_HITS_ORIGINE", "5.0")
)

# Mode ENFORCE (par défaut activé pour P0 PHASE XIX-P1)
ENFORCE_MODE = os.environ.get("XIX_P1_ENFORCE", "1") == "1"

# Métadonnées de phase
PHASE_TAG = "PHASE_XIX_P1"
PHASE_NAME = "PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω"


# ═══════════════════════════════════════════════════════════════════════
# Helper géométrique
# ═══════════════════════════════════════════════════════════════════════
def _dist_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


# ═══════════════════════════════════════════════════════════════════════
# Validation par corridor
# ═══════════════════════════════════════════════════════════════════════
def validate_origin_external(corridor: Dict[str, Any],
                               waypoint: Dict[str, float]) -> Dict[str, Any]:
    """Valide l'origine du corridor selon les règles XIX-P1.

    Retourne un dict avec :
      - origin_external_passed (bool)
      - origin_external_valid (alias bool)
      - origin_external_reason (str | None)
      - distance_origin_m (float)
      - gps_density_ratio (float | None)
      - gps_weighted_hits (float | None)
      - origin_external_radius_min_m / max_m
      - origin_external_density_threshold
      - origin_external_hits_threshold
      - origin_external_filter_phase
    """
    path = corridor.get("path") or []
    wp_lat = float(waypoint.get("lat", 0.0))
    wp_lng = float(waypoint.get("lng") or waypoint.get("lon") or 0.0)

    base = {
        "origin_external_filter_phase": PHASE_TAG,
        "origin_external_radius_min_m": ORIGINE_RADIUS_MIN_M,
        "origin_external_radius_max_m": ORIGINE_RADIUS_MAX_M,
        "origin_external_density_threshold": THRESH_DENSITY_ORIGINE,
        "origin_external_hits_threshold": THRESH_HITS_ORIGINE,
        "phase": PHASE_NAME,
    }

    if not path:
        return {
            **base,
            "origin_external_passed": False,
            "origin_external_valid": False,
            "origin_external_reason": "EMPTY_PATH",
            "distance_origin_m": None,
            "gps_density_ratio": None,
            "gps_weighted_hits": None,
        }

    # ─── §2.1 — Condition spatiale
    origin = path[0]
    d_origin = _dist_m([wp_lat, wp_lng], [origin[0], origin[1]])

    if d_origin < ORIGINE_RADIUS_MIN_M or d_origin > ORIGINE_RADIUS_MAX_M:
        return {
            **base,
            "origin_external_passed": False,
            "origin_external_valid": False,
            "origin_external_reason": "OUTSIDE_CROWN",
            "distance_origin_m": round(d_origin, 1),
            "gps_density_ratio": None,
            "gps_weighted_hits": None,
        }

    # ─── §2.2 — Condition GPS
    pv2 = corridor.get("predictive_omega_v2") or {}
    metrics = pv2.get("metrics") or {}
    gps_density_ratio = metrics.get("gps_density_ratio")
    gps_weighted_hits = metrics.get("gps_weighted_hits")

    # Si predictive_omega_v2 n'a pas annoté → pas de validation GPS possible
    if gps_density_ratio is None or gps_weighted_hits is None:
        return {
            **base,
            "origin_external_passed": False,
            "origin_external_valid": False,
            "origin_external_reason": "MISSING_PREDICTIVE_V2_METRICS",
            "distance_origin_m": round(d_origin, 1),
            "gps_density_ratio": None,
            "gps_weighted_hits": None,
        }

    if float(gps_density_ratio) < THRESH_DENSITY_ORIGINE:
        return {
            **base,
            "origin_external_passed": False,
            "origin_external_valid": False,
            "origin_external_reason": "LOW_DENSITY",
            "distance_origin_m": round(d_origin, 1),
            "gps_density_ratio": float(gps_density_ratio),
            "gps_weighted_hits": float(gps_weighted_hits),
        }

    if float(gps_weighted_hits) < THRESH_HITS_ORIGINE:
        return {
            **base,
            "origin_external_passed": False,
            "origin_external_valid": False,
            "origin_external_reason": "LOW_HITS",
            "distance_origin_m": round(d_origin, 1),
            "gps_density_ratio": float(gps_density_ratio),
            "gps_weighted_hits": float(gps_weighted_hits),
        }

    # ─── PASSE
    return {
        **base,
        "origin_external_passed": True,
        "origin_external_valid": True,
        "origin_external_reason": None,
        "distance_origin_m": round(d_origin, 1),
        "gps_density_ratio": float(gps_density_ratio),
        "gps_weighted_hits": float(gps_weighted_hits),
    }


# ═══════════════════════════════════════════════════════════════════════
# Application au bundle
# ═══════════════════════════════════════════════════════════════════════
def apply_origine_externe_filter_to_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Filtre les corridors selon les règles ORIGINE_EXTERNE_FILTER_Ω."""
    if not isinstance(bundle, dict):
        return bundle
    corridors = bundle.get("corridors") or []
    waypoint = bundle.get("waypoint") or {}

    kept: List[Dict[str, Any]] = []
    rejected_audit: List[Dict[str, Any]] = []
    rejected_reasons: Dict[str, int] = {}

    for c in corridors:
        result = validate_origin_external(c, waypoint=waypoint)
        # Annoter le corridor avec les méta XIX-P1
        c["origin_external_filter_phase"] = PHASE_TAG
        c["origin_external_passed"] = result["origin_external_passed"]
        c["origin_external_valid"] = result["origin_external_valid"]
        c["origin_external_reason"] = result["origin_external_reason"]
        c["origin_external_radius_min_m"] = ORIGINE_RADIUS_MIN_M
        c["origin_external_radius_max_m"] = ORIGINE_RADIUS_MAX_M
        c["origin_external_density_threshold"] = THRESH_DENSITY_ORIGINE
        c["origin_external_hits_threshold"] = THRESH_HITS_ORIGINE
        c["origin_external_validation"] = result

        if result["origin_external_passed"]:
            kept.append(c)
        else:
            r = result["origin_external_reason"] or "UNKNOWN"
            rejected_reasons[r] = rejected_reasons.get(r, 0) + 1
            rejected_audit.append({
                "id": c.get("id"),
                "reason": r,
                "distance_origin_m": result["distance_origin_m"],
                "gps_density_ratio": result["gps_density_ratio"],
                "gps_weighted_hits": result["gps_weighted_hits"],
            })

    if ENFORCE_MODE:
        bundle["corridors"] = kept
        bundle["corridors_rejected_origine_externe_xix"] = rejected_audit
    else:
        # Annotation seule, pas de filtrage destructif
        bundle["corridors_rejected_origine_externe_xix_annotated_only"] = rejected_audit

    bundle["origine_externe_filter_applied"] = True
    bundle["origine_externe_filter_stats"] = {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "total_input": len(corridors),
        "total_kept": len(kept),
        "total_rejected": len(rejected_audit),
        "rate_pct": round(100.0 * len(kept) / max(1, len(corridors)), 1),
        "rejected_reasons": rejected_reasons,
        "config": {
            "rayon_fonctionnel_nominal_m": RAYON_FONCTIONNEL_NOMINAL_M,
            "origine_externe_fraction": ORIGINE_EXTERNE_FRACTION,
            "origin_radius_min_m": ORIGINE_RADIUS_MIN_M,
            "origin_radius_max_m": ORIGINE_RADIUS_MAX_M,
            "thresh_density_origine": THRESH_DENSITY_ORIGINE,
            "thresh_hits_origine": THRESH_HITS_ORIGINE,
        },
    }
    return bundle


def get_filter_status() -> Dict[str, Any]:
    """Audit de la configuration du filtre."""
    return {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "rayon_fonctionnel_nominal_m": RAYON_FONCTIONNEL_NOMINAL_M,
        "origine_externe_fraction": ORIGINE_EXTERNE_FRACTION,
        "origin_radius_min_m": ORIGINE_RADIUS_MIN_M,
        "origin_radius_max_m": ORIGINE_RADIUS_MAX_M,
        "thresh_density_origine": THRESH_DENSITY_ORIGINE,
        "thresh_hits_origine": THRESH_HITS_ORIGINE,
        "rejection_reasons_catalog": [
            "OUTSIDE_CROWN", "LOW_DENSITY", "LOW_HITS",
            "MISSING_PREDICTIVE_V2_METRICS", "EMPTY_PATH",
        ],
    }
