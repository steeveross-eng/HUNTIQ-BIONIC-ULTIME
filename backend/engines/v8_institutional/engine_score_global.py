"""
ENGINE 24 — SCORE GLOBAL
PILIER: PREDICTION-INTELLIGENCE
SOURCES FUSIONNEES: phase_c.multi_engine_score, rsf_engine, thermal_v1, tfe_engine, Score V8 National
Axe NUTRITION-V12-SUPRA ajoute de maniere non invasive (2026-04).
"""
from engines.v8_national.phase_c_engines import _multi_engine_score, _thermal_model


def compute_score_global(lat, lon, species, month, hour, wind_speed_kmh=15, nutrition_score=None):
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
    }
    # Axe NUTRITION non invasif
    if nutrition_score is not None:
        out["nutrition_score"] = nutrition_score
        out["breakdown"] = {**(out["breakdown"] or {}), "nutrition": nutrition_score}
    return out
