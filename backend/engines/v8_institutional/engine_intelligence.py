"""
ENGINE 23 — INTELLIGENCE
PILIER: PREDICTION-INTELLIGENCE
SOURCES FUSIONNEES: phase_a (relocalisation), learning_v1, governance
"""
from engines.v8_national.phase_a_engines import _terrain_profile, _score_saline, _score_affut, _score_composite

def compute_intelligence(lat, lon, species, month, wind_deg=225):
    terrain = _terrain_profile(lat, lon)
    sal_score, sal_detail = _score_saline(terrain, month, lat, lon)
    aff_score, aff_detail = _score_affut(terrain, wind_deg, lat, lon)
    composite = _score_composite(sal_score, aff_score, terrain, month)
    return {"site_composite": composite, "saline_score": sal_score, "affut_score": aff_score, "terrain": terrain, "recommendation": "EXCELLENT" if composite > 75 else "BON" if composite > 55 else "MODERE" if composite > 35 else "FAIBLE"}
