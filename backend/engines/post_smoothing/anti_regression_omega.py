"""
anti_regression_omega.py — PHASE_X200_P6_ANTI_RÉGRESSION_Ω
===========================================================
Phase     : PHASE_X200_P6_ANTI_RÉGRESSION_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Module d'observation continue des 12 sous-normes X150-SUPRA-ARCHITECTONIQUE-Ω
appliquées par ENGINE_RENDUΩ. Ne modifie ni la géométrie, ni les verdicts,
ni le V30 verrouillé : il lit les violations émises par `renduomega.py` et
maintient un registre institutionnel en mémoire — compteurs cumulés,
métriques temporelles (fenêtres glissantes) et audit trail horodaté.

Règles strictes :
- V30 LOCKED intangible.
- Triple verrou P6 (flag + env + token du Commandant).
- Aucun impact sur le pipeline existant (hook append-only, fail-soft).
- Lecture seule vers les clients — aucune mutation exposée.
"""
from __future__ import annotations

import os
from collections import deque
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Deque, Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════
# 1. Triple verrou P6 (flag + env + token)
# ═══════════════════════════════════════════════════════════════════════
P6_ANTI_REGRESSION_ENABLED: bool = True                   # flag statique
P6_ENV_FLAG_NAME: str = "P6_ANTI_REGRESSION_AUTHORIZED_BY_COMMANDANT"
P6_TOKEN_NAME: str = "P6_ANTI_REGRESSION_COMMANDANT_TOKEN"
P6_EXPECTED_TOKEN: str = "STEEVE-MAX-X200-P6-EXPLICIT"


def is_p6_authorized() -> Dict[str, Any]:
    """Retourne l'état d'autorisation triple verrou P6 (sans exception)."""
    env_ok = os.environ.get(P6_ENV_FLAG_NAME, "").strip().lower() == "true"
    token = os.environ.get(P6_TOKEN_NAME, "").strip()
    token_ok = (token == P6_EXPECTED_TOKEN)
    return {
        "authorized": bool(P6_ANTI_REGRESSION_ENABLED and env_ok and token_ok),
        "flag_enabled": P6_ANTI_REGRESSION_ENABLED,
        "env_flag_ok": env_ok,
        "token_ok": token_ok,
        "expected_env_flag": P6_ENV_FLAG_NAME,
        "expected_token_env": P6_TOKEN_NAME,
    }


# ═══════════════════════════════════════════════════════════════════════
# 2. Mapping des violations RenduΩ -> 12 sous-normes X150
# ═══════════════════════════════════════════════════════════════════════
# Les clés suivent STRICTEMENT le contrat frontend runtimeBeaconOmega.js
# (`corridors_x150_probes`). Chaque entrée :
#   - matchers: liste de sous-chaînes recherchées dans `violation_text`
#   - label   : description institutionnelle courte
SUB_NORMES_X150: Dict[str, Dict[str, Any]] = {
    "geometry_catmullrom_25_30": {
        "matchers": ["points_count=", "attendu 25-30"],
        "label": "Géométrie CatmullRom 25-30 points",
    },
    "segment_max_20m": {
        "matchers": ["max_segment_m="],
        "label": "Segments ≤ 20 m",
    },
    "angle_max_45deg": {
        "matchers": ["max_angle_deg="],
        "label": "Angles ≤ 45°",
    },
    "curvature_progressive": {
        # Rattaché à angles et segments (heuristique institutionnelle)
        "matchers": ["curvature", "progressive"],
        "label": "Courbure progressive",
    },
    "no_simplification": {
        "matchers": ["length_m="],
        "label": "Absence de simplification (longueur minimale)",
    },
    "no_artificial_interpolation": {
        "matchers": ["interpolation"],
        "label": "Absence d'interpolation artificielle",
    },
    "no_radial_star_shape": {
        "matchers": ["radial_or_straight_shape_detected", "radial"],
        "label": "Absence de forme radiale/étoilée",
    },
    "terrainaware_functional_radius": {
        "matchers": ["radius_m=", "fonctionnel"],
        "label": "Rayon fonctionnel terrain-aware",
    },
    "no_water_below_20m": {
        "matchers": ["min_dist_water_m="],
        "label": "Eau > 20 m (anti-inondation)",
    },
    "no_slope_above_35deg": {
        "matchers": ["slope_deg="],
        "label": "Pente ≤ 35°",
    },
    "ecological_mosaic_respected": {
        # Mosaïque écologique rattachée à contamination (évitement polyvalent)
        "matchers": ["contamination_violation", "mosaic"],
        "label": "Mosaïque écologique respectée",
    },
    "human_zones_avoided": {
        "matchers": ["human_zone_violation"],
        "label": "Zones humaines évitées",
    },
}

SUB_NORMES_ORDER: Tuple[str, ...] = tuple(SUB_NORMES_X150.keys())


def _classify_violation_text(text: str) -> List[str]:
    """Associe une chaîne de violation brute à une ou plusieurs sous-normes.

    Retourne au minimum ['_uncategorized'] si aucun matcher ne correspond,
    afin qu'aucune violation ne soit perdue de l'audit trail.
    """
    if not isinstance(text, str) or not text:
        return ["_uncategorized"]
    low = text.lower()
    hits: List[str] = []
    for key, spec in SUB_NORMES_X150.items():
        for m in spec["matchers"]:
            if m.lower() in low:
                hits.append(key)
                break
    return hits or ["_uncategorized"]


# ═══════════════════════════════════════════════════════════════════════
# 3. Registre in-memory — thread-safe
# ═══════════════════════════════════════════════════════════════════════
_MAX_EVENTS: int = 2000
_LEDGER_LOCK = RLock()

_COUNTERS: Dict[str, Dict[str, int]] = {
    key: {"violations": 0, "corridors_touched": 0}
    for key in list(SUB_NORMES_X150.keys()) + ["_uncategorized"]
}
_EVENTS: Deque[Dict[str, Any]] = deque(maxlen=_MAX_EVENTS)
_SUMMARY: Dict[str, Any] = {
    "total_corridors_observed": 0,
    "total_accepted": 0,
    "total_rejected": 0,
    "first_seen_at": None,
    "last_seen_at": None,
    "last_bundle_summary": None,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════════
# 4. API de recording (hook non intrusif)
# ═══════════════════════════════════════════════════════════════════════
def _extract_violations(verdict: Dict[str, Any]) -> List[str]:
    """Aplatit toutes les violations d'un verdict validate_corridor()."""
    out: List[str] = []
    for block in ("geometry", "terrain", "ecology", "species"):
        b = verdict.get(block) or {}
        vs = b.get("violations") or []
        if isinstance(vs, list):
            out.extend(str(x) for x in vs)
    return out


def record_corridor_verdict(corridor: Dict[str, Any],
                            verdict: Dict[str, Any],
                            bundle_context: Optional[Dict[str, Any]] = None) -> None:
    """Hook principal appelé par `apply_renduomega_to_bundle` pour chaque
    corridor. Silencieux en cas d'erreur (fail-soft).
    """
    if not is_p6_authorized()["authorized"]:
        return
    try:
        with _LEDGER_LOCK:
            now = _now_iso()
            accepted = bool(verdict.get("accepted"))
            _SUMMARY["total_corridors_observed"] += 1
            if accepted:
                _SUMMARY["total_accepted"] += 1
            else:
                _SUMMARY["total_rejected"] += 1
            if _SUMMARY["first_seen_at"] is None:
                _SUMMARY["first_seen_at"] = now
            _SUMMARY["last_seen_at"] = now

            violations = _extract_violations(verdict)
            # Un corridor incrémente corridors_touched au plus une fois par sous-norme
            touched_keys: set = set()
            for v_text in violations:
                keys = _classify_violation_text(v_text)
                for k in keys:
                    _COUNTERS[k]["violations"] += 1
                    if k not in touched_keys:
                        _COUNTERS[k]["corridors_touched"] += 1
                        touched_keys.add(k)
                    _EVENTS.append({
                        "ts": now,
                        "corridor_id": corridor.get("id"),
                        "sub_norme": k,
                        "violation_text": v_text,
                        "accepted": accepted,
                        "bundle_lat": (bundle_context or {}).get("lat"),
                        "bundle_lng": (bundle_context or {}).get("lng"),
                    })
    except Exception:
        # Fail-soft : jamais perturber le pipeline production
        return


def record_bundle_summary(bundle: Dict[str, Any]) -> None:
    """Appelé UNE FOIS par bundle après traitement — snapshot léger."""
    if not is_p6_authorized()["authorized"]:
        return
    try:
        with _LEDGER_LOCK:
            integration = bundle.get("renduomega_integration") or {}
            totals = integration.get("totals") or {}
            _SUMMARY["last_bundle_summary"] = {
                "ts": _now_iso(),
                "accepted": int(totals.get("accepted") or 0),
                "rejected": int(totals.get("rejected") or 0),
                "total_input": int(totals.get("total_input") or 0),
                "status": integration.get("status"),
            }
    except Exception:
        return


# ═══════════════════════════════════════════════════════════════════════
# 5. API lecture seule
# ═══════════════════════════════════════════════════════════════════════
def get_ledger_snapshot() -> Dict[str, Any]:
    """Snapshot complet pour affichage institutionnel."""
    with _LEDGER_LOCK:
        counters_out = {}
        total_corridors = _SUMMARY["total_corridors_observed"] or 1  # éviter /0 tout en gardant ratio lisible
        for key in list(SUB_NORMES_X150.keys()) + ["_uncategorized"]:
            c = _COUNTERS[key]
            counters_out[key] = {
                "violations": c["violations"],
                "corridors_touched": c["corridors_touched"],
                "violation_rate_per_corridor": round(
                    c["corridors_touched"] / total_corridors, 4
                ) if _SUMMARY["total_corridors_observed"] else 0.0,
                "label": SUB_NORMES_X150.get(key, {}).get("label", key),
            }
        return {
            "summary": dict(_SUMMARY),
            "sub_normes": counters_out,
            "sub_normes_order": list(SUB_NORMES_ORDER),
            "events_kept": len(_EVENTS),
            "events_max": _MAX_EVENTS,
        }


def get_recent_violations(limit: int = 100,
                          sub_norme: Optional[str] = None,
                          corridor_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retourne les violations récentes, filtrables par sous-norme et/ou corridor."""
    limit = max(1, min(int(limit or 100), _MAX_EVENTS))
    with _LEDGER_LOCK:
        # parcours inversé (du plus récent au plus ancien)
        out: List[Dict[str, Any]] = []
        for ev in reversed(_EVENTS):
            if sub_norme and ev.get("sub_norme") != sub_norme:
                continue
            if corridor_id and str(ev.get("corridor_id")) != str(corridor_id):
                continue
            out.append(dict(ev))
            if len(out) >= limit:
                break
        return out


def build_audit_matrix() -> Dict[str, Any]:
    """Matrice compact `corridor × sous-norme` pour P7 verrouillage final.

    Pour chaque corridor observé, liste les sous-normes violées et le nb
    d'occurrences. Utilisable directement comme tableau comparatif P7.
    """
    with _LEDGER_LOCK:
        matrix: Dict[str, Dict[str, int]] = {}
        for ev in _EVENTS:
            cid = str(ev.get("corridor_id") or "unknown")
            sn = ev.get("sub_norme") or "_uncategorized"
            if cid not in matrix:
                matrix[cid] = {}
            matrix[cid][sn] = matrix[cid].get(sn, 0) + 1
        return {
            "matrix": matrix,
            "sub_normes_order": list(SUB_NORMES_ORDER),
            "generated_at": _now_iso(),
            "corridors_count": len(matrix),
        }


def reset_ledger() -> Dict[str, Any]:
    """Remet le registre à zéro (usage Commandant uniquement)."""
    global _SUMMARY
    with _LEDGER_LOCK:
        for key in _COUNTERS:
            _COUNTERS[key]["violations"] = 0
            _COUNTERS[key]["corridors_touched"] = 0
        _EVENTS.clear()
        _SUMMARY = {
            "total_corridors_observed": 0,
            "total_accepted": 0,
            "total_rejected": 0,
            "first_seen_at": None,
            "last_seen_at": None,
            "last_bundle_summary": None,
        }
        return {"reset_at": _now_iso(), "status": "CLEARED"}
