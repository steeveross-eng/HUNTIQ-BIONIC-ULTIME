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


# ═══════════════════════════════════════════════════════════════════════
# ÉCHANTILLONNAGE MULTI-POINTS (X200-P3B)
# ═══════════════════════════════════════════════════════════════════════
# Reproductibilité : positions fractionnaires déterministes (pas de RNG).
MULTIPOINT_MIN_SAMPLES = 1
MULTIPOINT_MAX_SAMPLES = 5
MULTIPOINT_LENGTH_THRESHOLD_M = 200.0  # au-delà, on passe de 1→3→5


def _path_length_m(path: List[List[float]]) -> float:
    if not path or len(path) < 2:
        return 0.0
    import math
    R = 6371000.0
    total = 0.0
    for i in range(len(path) - 1):
        lat1 = math.radians(float(path[i][0]))
        lat2 = math.radians(float(path[i + 1][0]))
        dlat = lat2 - lat1
        dlon = math.radians(float(path[i + 1][1]) - float(path[i][1]))
        h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        total += 2 * R * math.asin(math.sqrt(h))
    return total


def _sample_indices(n_points_in_path: int, n_samples: int) -> List[int]:
    """Indices DÉTERMINISTES à positions fractionnaires k/(n_samples+1).

    Exemples :
      n_samples=1 → [mid]
      n_samples=3 → [1/4, 2/4, 3/4]
      n_samples=5 → [1/6, 2/6, 3/6, 4/6, 5/6]
    """
    if n_points_in_path <= 1:
        return [0]
    return [
        max(0, min(n_points_in_path - 1, int(n_points_in_path * k / (n_samples + 1))))
        for k in range(1, n_samples + 1)
    ]


def _choose_n_samples(path: List[List[float]]) -> int:
    """Barème institutionnel X200-P3B — borné 1..5 selon longueur."""
    L = _path_length_m(path)
    if L < MULTIPOINT_LENGTH_THRESHOLD_M:
        return 1
    if L < 2 * MULTIPOINT_LENGTH_THRESHOLD_M:
        return 3
    return MULTIPOINT_MAX_SAMPLES


# Poids d'agrégation (moyenne pondérée "kernel centré")
MULTIPOINT_WEIGHTS = {
    1: [1.0],
    3: [0.25, 0.50, 0.25],
    5: [0.10, 0.20, 0.40, 0.20, 0.10],
}


def _weighted_mean(values: List[float], weights: List[float]) -> float:
    if not values:
        return 0.0
    if len(values) != len(weights):
        return sum(values) / len(values)
    wsum = sum(weights) or 1.0
    return sum(v * w for v, w in zip(values, weights)) / wsum


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
    """Échantillonnage multi-points DÉTERMINISTE le long du path (X200-P3B).

    Retourne la probabilité agrégée + les échantillons individuels pour
    traçabilité institutionnelle.
    """
    if not path:
        return {"probability_0_1": 0.0, "components": {}, "evaluated_at": None,
                "samples": [], "n_samples": 0, "path_length_m": 0.0}
    from engines.predictive_omega.router import compute_predictive

    n_samples = _choose_n_samples(path)
    idxs = _sample_indices(len(path), n_samples)
    weights = MULTIPOINT_WEIGHTS.get(n_samples, [1.0 / n_samples] * n_samples)

    samples = []
    probabilities = []
    last_components = {}
    last_legal_mult = 1.0
    for order, i in enumerate(idxs):
        pt = [float(path[i][0]), float(path[i][1])]
        pred = compute_predictive(
            lat=pt[0], lng=pt[1],
            species=species, iso_date=iso_date, hour=hour,
        )
        probabilities.append(float(pred["probability_0_1"]))
        last_components = pred["components"]
        last_legal_mult = pred.get("legal_multiplier", 1.0)
        samples.append({
            "order": order, "path_index": i,
            "lat": pt[0], "lng": pt[1],
            "probability_0_1": pred["probability_0_1"],
            "weight": weights[order] if order < len(weights) else 0.0,
        })

    aggregated = _weighted_mean(probabilities, weights)
    midpoint_fallback = samples[len(samples)//2] if samples else None

    return {
        "probability_0_1": round(aggregated, 4),
        "components": last_components,
        "legal_multiplier": last_legal_mult,
        "evaluated_at": {"lat": midpoint_fallback["lat"], "lng": midpoint_fallback["lng"]}
                        if midpoint_fallback else None,
        "samples": samples,
        "n_samples": len(samples),
        "path_length_m": round(_path_length_m(path), 2),
        "aggregation_method": "weighted_mean_kernel_centered",
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
        # X200-P3B — multi-points
        "n_samples":             pred.get("n_samples", 1),
        "path_length_m":         pred.get("path_length_m", 0.0),
        "aggregation_method":    pred.get("aggregation_method", "single_point"),
        "samples":               pred.get("samples", []),
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
