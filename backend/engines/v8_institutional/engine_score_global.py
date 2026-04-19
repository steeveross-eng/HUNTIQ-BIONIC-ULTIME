"""
ENGINE 24 — SCORE GLOBAL — MODE REALITE (Phase IX)
====================================================
Fusion complete 20 axes SUPRA-Ω pour refleter la realite ecologique.
Pondérations calibrees sur litterature + SCIENCE-Ω.
"""
from engines.v8_national.phase_c_engines import _multi_engine_score, _thermal_model

# Ponderations mode realite (total = 100%)
# Calibration: NUTRITION + HABITAT + STRESS dominent; INCERTITUDE penalise; CONTAMINATION malus
_WEIGHTS = {
    "nutrition":           0.10,   # Nutrition-V12-SUPRA
    "habitat":             0.08,   # Habitat-SUPRA
    "stress_anthropique":  0.08,   # Stress-Anthropique-Ω
    "population":          0.06,   # Population-Dynamics-Ω
    "hotspots":            0.06,   # Hotspots (bundle)
    "connectivite":        0.06,   # Connectivite-Ecologique-Ω
    "comportement_bio":    0.06,   # Comportement-Biologique-Ω
    "thermique":           0.06,   # Thermique-Microclimat-Ω
    "quality":             0.05,   # Qualite-Donnees-Ω
    "calibration":         0.05,   # Calibration-Ω
    "sensoriel":           0.04,   # Sensoriel-Vent-Odeurs-Ω
    "hydrologie":          0.04,   # Hydrologie-SUPRA
    "sol":                 0.04,   # Sol-SUPRA
    "climat_futur":        0.04,   # Climat-Futur-Ω
    "pression_atmo":       0.04,   # Pression-Atmospherique-Ω
    "zones":               0.03,   # Zones (bundle, proxy count)
    "lunaire":             0.02,   # Influence-Lunaire-Ω
    "ia_vision":           0.02,   # IA-Vision-Ecologique-Ω
    "vent":                0.01,   # Vent (bundle, proxy count)
    "incertitude_inv":     0.04,   # Incertitude-Ω (inverse = certitude)
    "contamination_malus": 0.02,   # Contamination-Ω (penalite, 100=clean)
}
# Total = 1.00 verified


def _safe_score(v, default=50.0) -> float:
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return max(0.0, min(100.0, float(v)))
    return default


def compute_score_global_reality(bundle: dict) -> dict:
    """Compute SCORE GLOBAL mode realite from full V20 bundle.

    Uses 20 axes SUPRA-Ω depuis le bundle.
    """
    # Extract scores
    s = {
        "nutrition":          _safe_score((bundle.get("nutrition") or {}).get("score_nutritionnel")),
        "habitat":            _safe_score((bundle.get("habitat_supra") or {}).get("score")),
        "stress_anthropique": _safe_score((bundle.get("stress_anthropique") or {}).get("score")),
        "population":         _safe_score((bundle.get("population_dynamics") or {}).get("score")),
        "hotspots":           _avg_intensity(bundle.get("hotspots") or []),
        "connectivite":       _safe_score((bundle.get("connectivite_ecologique") or {}).get("score")),
        "comportement_bio":   _safe_score((bundle.get("comportement_biologique") or {}).get("score")),
        "thermique":          _safe_score((bundle.get("thermique_microclimat") or {}).get("score")),
        "quality":            _safe_score((bundle.get("quality_data") or {}).get("score")),
        "calibration":        _safe_score((bundle.get("calibration") or {}).get("score")),
        "sensoriel":          _safe_score((bundle.get("sensoriel_vent_odeurs") or {}).get("score")),
        "hydrologie":         _safe_score((bundle.get("hydrologie_supra") or {}).get("score")),
        "sol":                _safe_score((bundle.get("sol_supra") or {}).get("score")),
        "climat_futur":       _safe_score((bundle.get("climat_futur") or {}).get("score")),
        "pression_atmo":      _safe_score((bundle.get("pression_atmospherique") or {}).get("score")),
        "zones":              _zone_score(bundle.get("zones") or []),
        "lunaire":            _safe_score((bundle.get("influence_lunaire") or {}).get("score")),
        "ia_vision":          _safe_score((bundle.get("ia_vision_ecologique") or {}).get("score")),
        "vent":               _vent_score(bundle.get("wind_vectors") or []),
        "incertitude_inv":    _safe_score((bundle.get("incertitude") or {}).get("certainty_score")),
        "contamination_malus": _contam_malus(bundle.get("contamination") or []),
    }

    composite = round(sum(_WEIGHTS[k] * s[k] for k in _WEIGHTS), 2)

    if composite > 75:
        classification = "EXCELLENT"
    elif composite > 60:
        classification = "BON"
    elif composite > 45:
        classification = "MODERE"
    elif composite > 30:
        classification = "FAIBLE"
    else:
        classification = "CRITIQUE"

    return {
        "engine": "SCORE-GLOBAL-REALITY-Ω",
        "version": "V2-REALITY-2026-04",
        "mode": "REALITE",
        "score_global": composite,
        "classification": classification,
        "axes_scores": s,
        "weights": _WEIGHTS,
        "axes_count": len(_WEIGHTS),
        "note": "Recalibrage 20 axes SUPRA-Ω. Pondérations calibrées via ENGINE-SCIENCE-Ω.",
    }


def _avg_intensity(hotspots: list) -> float:
    if not hotspots:
        return 50.0
    vals = [h.get("intensity_with_nutrition") or h.get("intensity") or 0 for h in hotspots]
    return round(sum(vals) / len(vals), 1) if vals else 50.0


def _zone_score(zones: list) -> float:
    if not zones:
        return 30.0
    vals = [z.get("score") or 50 for z in zones]
    return round(sum(vals) / len(vals), 1) if vals else 30.0


def _vent_score(wv: list) -> float:
    if not wv:
        return 40.0
    return min(100.0, len(wv) * 10.0)


def _contam_malus(contam: list) -> float:
    """100 = propre, 0 = fortement contamine."""
    if not contam:
        return 100.0
    # Plus il y a de cones = plus de contamination
    return max(0.0, 100.0 - len(contam) * 5.0)


# Ancien SCORE GLOBAL V1 (preserve pour retro-compatibilite)
def compute_score_global(lat, lon, species, month, hour, wind_speed_kmh=15, nutrition_score=None, bundle: dict = None):
    """Compatibilité: si bundle fourni → mode REALITE. Sinon → mode V8 legacy."""
    if bundle:
        return compute_score_global_reality(bundle)
    multi = _multi_engine_score(lat, lon, species, month, hour, wind_speed_kmh)
    thermal = _thermal_model(lat, lon, month, hour, wind_speed_kmh)
    out = {
        "score_global": multi["composite_score"],
        "classification": multi["classification"],
        "breakdown": multi["breakdown"],
        "components": multi["components"],
        "thermal": {
            "confort": thermal["confort_animal"],
            "zone": thermal["zone_thermique"],
            "temp": thermal["temp_air_c"],
            "wind_chill": thermal["wind_chill_c"],
        },
        "engine": "V8-SCORE-GLOBAL",
        "mode": "LEGACY",
    }
    if nutrition_score is not None:
        out["nutrition_score"] = nutrition_score
        out["breakdown"] = {**(out["breakdown"] or {}), "nutrition": nutrition_score}
    return out
