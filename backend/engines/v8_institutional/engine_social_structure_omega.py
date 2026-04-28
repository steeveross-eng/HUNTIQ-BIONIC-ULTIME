"""
ENGINE_SOCIAL_STRUCTURE_Ω — Structure sociale (grégaire, solitaire, groupe).
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : BIOLOGIE (E45)
RÔLE : SECONDAIRE · PRIORITÉ : SECONDAIRE
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_SOCIAL_STRUCTURE_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

_SOCIAL = {
    "orignal":         {"type": "solitaire_rut_temporaire", "group_avg": 1.2, "rut_months": (9, 10)},
    "chevreuil":       {"type": "semi_gregaire_harem_hiver", "group_avg": 2.5, "rut_months": (11, 12)},
    "cerf":            {"type": "semi_gregaire_harem_hiver", "group_avg": 2.5, "rut_months": (11, 12)},
    "ours_noir":       {"type": "solitaire_sauf_femelle_oursons", "group_avg": 1.3, "rut_months": (6, 7)},
    "ours":            {"type": "solitaire_sauf_femelle_oursons", "group_avg": 1.3, "rut_months": (6, 7)},
    "dindon_sauvage":  {"type": "gregaire_bandes", "group_avg": 8.0, "rut_months": (4, 5)},
    "dindon":          {"type": "gregaire_bandes", "group_avg": 8.0, "rut_months": (4, 5)},
    "wapiti":          {"type": "gregaire_harem_rut", "group_avg": 6.0, "rut_months": (9, 10)},
}


def compute_social(species: str, month: int = 10) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    s = _SOCIAL.get(key, _SOCIAL["orignal"])
    rut_start, rut_end = s["rut_months"]
    in_rut = rut_start <= int(month) <= rut_end
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "BIOLOGIE", "role": "SECONDAIRE",
        "species": key,
        "social_type": s["type"],
        "group_avg_size": s["group_avg"],
        "in_rut_period": in_rut,
        "rut_months": list(s["rut_months"]),
        "data_sources": ["ENGINE_SPECIES_PROFILES_Ω", "MFFP_reference"],
    }
