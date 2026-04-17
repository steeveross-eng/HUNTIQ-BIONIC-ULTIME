"""
ENGINE 21 — PREDICTION 48H
PILIER: PREDICTION-INTELLIGENCE
SOURCES FUSIONNEES: phase_c.scenario (8 presets), scenario_v1, simulation_v1
OPTIMISATIONS PRESERVEES: 8 presets what-if, comparaison baseline/scenario
"""
from engines.v8_national.phase_c_engines import _run_scenario, SCENARIO_PRESETS

def compute_prediction_48h(lat, lon, species, month, hour):
    results = []
    for scenario_id in SCENARIO_PRESETS:
        r = _run_scenario(lat, lon, species, scenario_id, month, hour)
        results.append(r)
    results.sort(key=lambda x: -abs(x["impact_global"]))
    return {"predictions": results, "count": len(results), "engine": "V8-PREDICTION-48H"}
