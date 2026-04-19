"""
ENGINE 23 — INTELLIGENCE
PILIER: PREDICTION-INTELLIGENCE
SOURCES FUSIONNEES: phase_a (relocalisation), learning_v1, governance
Axe NUTRITION-V12-SUPRA ajoute de maniere non invasive (2026-04).
"""
from engines.v8_national.phase_a_engines import _terrain_profile, _score_saline, _score_affut, _score_composite


def compute_intelligence(lat, lon, species, month, wind_deg=225, nutrition_score=None):
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
    # Axe NUTRITION non invasif: expose dans breakdown sans modifier composite existant
    if nutrition_score is not None:
        out["nutrition_score"] = nutrition_score
        out["breakdown"] = {
            "saline": sal_score,
            "affut": aff_score,
            "nutrition": nutrition_score,
        }
    return out
