"""
predictive_integration.py — Intégration ENGINE_PREDICTIVE_Ω dans smoother X180
==============================================================================
Phase     : PHASE_X200_P2_PREDICTIVE_INTEGRATION_Ω
Commandant: STEEVE-MAX

Rôle : calculer pour chaque corridor lissé une `corridor_probability_omega`
en combinant :
  1. La probabilité brute `predictive_omega.compute_predictive()` évaluée
     au point médian du path.
  2. Un multiplicateur hiérarchique COMMANDANT (6/4/3/2/1) selon
     `level_commandant` (external inflow) ou `level_v7` (densité P1-a).

FEATURE FLAG : ON par défaut, sous TRIPLE VERROU :
  - `P2_PREDICTIVE_INTEGRATION_ENABLED = True`
  - env `P2_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true`
  - env `P2_COMMANDANT_TOKEN=STEEVE-MAX-X200-P2-EXPLICIT`

V30 INTANGIBLE. Aucun import `engines.v8_institutional.*`. Pas d'impact
sur zones, salines, contamination, nutrition.
"""
from __future__ import annotations

import os
from datetime import date
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAG P2 + TRIPLE VERROU Ω
# ═══════════════════════════════════════════════════════════════════════
P2_PREDICTIVE_INTEGRATION_ENABLED: bool = True
EXPECTED_TOKEN_P2 = "STEEVE-MAX-X200-P2-EXPLICIT"

# ═══════════════════════════════════════════════════════════════════════
# PONDÉRATION HIÉRARCHIQUE COMMANDANT — ordre institutionnel 6/4/3/2/1
# ═══════════════════════════════════════════════════════════════════════
COMMANDANT_WEIGHT_MAP = {
    "CRITIQUE": 6,
    "MAJEUR":   4,
    "FORT":     3,
    "MODERE":   2,
    "FAIBLE":   1,
}
MAX_COMMANDANT_WEIGHT = 6  # normalisation


def is_p2_authorized() -> Dict[str, Any]:
    env_ok = os.environ.get(
        "P2_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_ok = os.environ.get("P2_COMMANDANT_TOKEN", "") == EXPECTED_TOKEN_P2
    return {
        "authorized": P2_PREDICTIVE_INTEGRATION_ENABLED and env_ok and token_ok,
        "flag_enabled": P2_PREDICTIVE_INTEGRATION_ENABLED,
        "env_ok": env_ok,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN_P2,
    }


def _midpoint(path: List[List[float]]) -> Optional[List[float]]:
    if not path or len(path) < 1:
        return None
    return list(path[len(path) // 2])


def _hierarchical_factor(corridor: Dict[str, Any]) -> float:
    """Facteur 0..1 dérivé du niveau COMMANDANT ou V7 du corridor."""
    lvl = corridor.get("level_commandant") or corridor.get("level_v7") or "FAIBLE"
    w = COMMANDANT_WEIGHT_MAP.get(str(lvl).upper(), 1)
    return round(w / MAX_COMMANDANT_WEIGHT, 4)


def _corridor_probability(path: List[List[float]], species: str,
                          hour: int, iso_date: Optional[str]) -> Dict[str, Any]:
    """Appelle predictive_omega sur le point médian. No-op gracieux si
    le path est invalide (retourne 0)."""
    mid = _midpoint(path)
    if not mid:
        return {"probability_0_1": 0.0, "components": {}, "evaluated_at": None}
    # Import différé pour éviter cycle d'imports
    from engines.predictive_omega.router import compute_predictive
    pred = compute_predictive(
        lat=float(mid[0]), lng=float(mid[1]),
        species=species, iso_date=iso_date, hour=hour,
    )
    return {
        "probability_0_1": pred["probability_0_1"],
        "components": pred["components"],
        "legal_multiplier": pred.get("legal_multiplier", 1.0),
        "evaluated_at": {"lat": mid[0], "lng": mid[1]},
    }


def apply_predictive_to_corridor(corridor: Dict[str, Any],
                                 species: str = "orignal",
                                 hour: int = 7,
                                 iso_date: Optional[str] = None
                                 ) -> Dict[str, Any]:
    """Ajoute `corridor_probability_omega` (0..1) + métadonnées.

    Formule institutionnelle Ω :
        corridor_probability_omega = predictive_probability * hierarchical_factor

    `hierarchical_factor` dérive de la pondération COMMANDANT 6/4/3/2/1
    normalisée (max = 6 = CRITIQUE → facteur 1.0).
    """
    out = dict(corridor)
    path = out.get("path") or out.get("polyline") or []
    pred = _corridor_probability(path, species, hour, iso_date)
    h = _hierarchical_factor(out)
    prob = max(0.0, min(1.0, float(pred["probability_0_1"]) * h))
    out["corridor_probability_omega"] = round(prob, 4)
    out["corridor_probability_components"] = {
        "predictive_raw_0_1":    pred["probability_0_1"],
        "hierarchical_factor":   h,
        "commandant_level":      out.get("level_commandant") or out.get("level_v7") or "FAIBLE",
        "commandant_weight":     COMMANDANT_WEIGHT_MAP.get(
            str(out.get("level_commandant") or out.get("level_v7") or "FAIBLE").upper(), 1,
        ),
        "evaluated_at":          pred["evaluated_at"],
        "legal_multiplier":      pred.get("legal_multiplier", 1.0),
        "components_predictive": pred["components"],
    }
    return out


def apply_predictive_to_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Injecte `corridor_probability_omega` sur tous les corridors du bundle.

    No-op si P2 non autorisé. Ne touche ni zones vitales, ni salines,
    ni V30.
    """
    if not isinstance(bundle, dict):
        return bundle
    auth = is_p2_authorized()
    if not auth["authorized"]:
        bundle["p2_predictive_integration"] = {
            "status": "BYPASSED",
            "reason": "P2_NOT_AUTHORIZED",
            "authorization": auth,
        }
        return bundle

    species = str(bundle.get("species") or bundle.get("species_profile") or "orignal").lower()
    hour = int(bundle.get("hour", 7))
    iso_date = bundle.get("date")

    total = 0
    total_prob = 0.0
    distribution: Dict[str, int] = {}
    for key in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
        arr = bundle.get(key)
        if not isinstance(arr, list):
            continue
        new_arr = []
        for c in arr:
            cc = apply_predictive_to_corridor(c, species=species, hour=hour, iso_date=iso_date)
            total += 1
            total_prob += float(cc.get("corridor_probability_omega", 0.0))
            lvl = cc.get("corridor_probability_components", {}).get("commandant_level", "FAIBLE")
            distribution[lvl] = distribution.get(lvl, 0) + 1
            new_arr.append(cc)
        bundle[key] = new_arr

    bundle["p2_predictive_integration"] = {
        "status": "APPLIED",
        "phase": "X200_P2_PREDICTIVE_INTEGRATION_Ω",
        "authorization": auth,
        "species": species, "hour": hour, "date": iso_date,
        "weight_map_commandant": COMMANDANT_WEIGHT_MAP,
        "totals": {
            "corridors_processed": total,
            "mean_probability_omega": round(total_prob / total, 4) if total else 0.0,
        },
        "level_distribution": distribution,
        "v30_engine_touched": False,
        "zones_or_salines_modified": False,
    }
    return bundle
