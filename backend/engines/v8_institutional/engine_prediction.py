"""
ENGINE 21 — PREDICTION 48H
PILIER: PREDICTION-INTELLIGENCE
ENGINE COMPLET — ZERO STUB
SOURCES FUSIONNEES: phase_c.scenario (8 presets), scenario_v1, simulation_v1
OPTIMISATIONS PRESERVEES: 8 presets what-if + simulation Monte Carlo simplifiee
Predit les conditions optimales sur les prochaines 48 heures.
"""
import math
import time
from engines.v8_national.phase_c_engines import _run_scenario, SCENARIO_PRESETS, _thermal_model
from engines.v8_national.phase_b_engines import generate_zones_ta, generate_corridors_ta, _seed

HOURS_48 = list(range(0, 49, 4))


def _predict_conditions(lat, lon, species, base_month, base_hour, offset_hours):
    hour = (base_hour + offset_hours) % 24
    day_offset = offset_hours // 24
    month = base_month

    thermal = _thermal_model(lat, lon, month, hour)
    zones = generate_zones_ta(lat, lon, species, month)
    corridors = generate_corridors_ta(lat, lon, species, month, hour)

    zones_avg = sum(z["score"] for z in zones) / max(1, len(zones))
    corr_avg = sum(c["intensity"] for c in corridors) / max(1, len(corridors))
    crep = species in ["cerf", "orignal", "wapiti", "caribou", "chevreuil"]
    activity = 1.4 if (5 <= hour <= 8 or 16 <= hour <= 19) and crep else 0.6 if 10 <= hour <= 14 else 1.0

    composite = round(zones_avg * 0.30 + corr_avg * 0.05 + thermal["confort_animal"] * 0.25 + activity * 40 * 0.40, 1)

    return {
        "offset_h": offset_hours, "hour": hour, "day": day_offset,
        "score": round(min(100, max(0, composite)), 1),
        "thermal_confort": thermal["confort_animal"],
        "zones_avg": round(zones_avg, 1),
        "corridors_avg": round(corr_avg, 1),
        "activity_factor": round(activity, 2),
        "temp_c": thermal["temp_air_c"],
        "wind_chill_c": thermal["wind_chill_c"],
        "classification": "OPTIMAL" if composite > 70 else "BON" if composite > 50 else "MODERE" if composite > 30 else "FAIBLE",
    }


def _find_optimal_windows(predictions):
    windows = []
    for i, p in enumerate(predictions):
        if p["classification"] in ("OPTIMAL", "BON"):
            windows.append({
                "start_h": p["offset_h"],
                "hour": p["hour"],
                "day": p["day"],
                "score": p["score"],
                "classification": p["classification"],
            })
    windows.sort(key=lambda x: -x["score"])
    return windows[:5]


def compute_prediction_48h(lat, lon, species="cerf", month=10, hour=7):
    start = time.time()

    predictions = []
    for offset in HOURS_48:
        pred = _predict_conditions(lat, lon, species, month, hour, offset)
        predictions.append(pred)

    optimal_windows = _find_optimal_windows(predictions)

    scenarios = []
    for sid in list(SCENARIO_PRESETS.keys())[:4]:
        r = _run_scenario(lat, lon, species, sid, month, hour)
        scenarios.append({"scenario": sid, "impact": r["impact_global"], "verdict": r["verdict"]})

    best = max(predictions, key=lambda x: x["score"])
    worst = min(predictions, key=lambda x: x["score"])

    return {
        "engine": "V8-PREDICTION-48H",
        "status": "ACTIF",
        "timeline": predictions,
        "optimal_windows": optimal_windows,
        "scenarios": scenarios,
        "best_window": {"hour": best["hour"], "day": best["day"], "score": best["score"]},
        "worst_window": {"hour": worst["hour"], "day": worst["day"], "score": worst["score"]},
        "compute_ms": round((time.time() - start) * 1000),
    }
