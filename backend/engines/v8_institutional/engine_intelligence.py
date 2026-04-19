"""
ENGINE 23 — INTELLIGENCE
PILIER: PREDICTION-INTELLIGENCE
SOURCES FUSIONNEES: phase_a (relocalisation), learning_v1, governance
Axe NUTRITION-V12-SUPRA ajoute de maniere non invasive (2026-04).
"""
from engines.v8_national.phase_a_engines import _terrain_profile, _score_saline, _score_affut, _score_composite


def compute_intelligence(lat, lon, species, month, wind_deg=225, nutrition_score=None, quality_score=None, uncertainty_score=None, population_score=None):
    terrain = _terrain_profile(lat, lon)
    sal_score, sal_detail = _score_saline(terrain, month, lat, lon)
    aff_score, aff_detail = _score_affut(terrain, wind_deg, lat, lon)
    composite = _score_composite(sal_score, aff_score, terrain, month)

    out = {
        "site_composite": composite,
        "saline_score": sal_score,
        "affut_score": aff_score,
        "terrain": terrain,
        "recommendation": "EXCELLENT" if composite > 75 else "BON" if composite > 55 else "MODERE" if composite > 35 else "FAIBLE",
    }
    breakdown = {"saline": sal_score, "affut": aff_score}
    if nutrition_score is not None:
        out["nutrition_score"] = nutrition_score
        breakdown["nutrition"] = nutrition_score
    if quality_score is not None:
        out["quality_score"] = quality_score
        breakdown["quality"] = quality_score
    if uncertainty_score is not None:
        out["uncertainty_score"] = uncertainty_score
        breakdown["uncertainty"] = uncertainty_score
    if population_score is not None:
        out["population_score"] = population_score
        breakdown["population"] = population_score
    if len(breakdown) > 2:
        out["breakdown"] = breakdown
    return out
