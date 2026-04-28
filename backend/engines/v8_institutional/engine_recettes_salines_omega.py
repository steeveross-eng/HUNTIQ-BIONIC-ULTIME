"""
ENGINE_RECETTES_SALINES_Ω — Formulations de salines adaptées espèce+carence.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : FUSION (E40)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any, List

ENGINE_NAME = "ENGINE_RECETTES_SALINES_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

_RECIPES = {
    "orignal": [
        {"name": "Saline canonique orignal", "Na": 0.55, "Ca": 0.20, "P": 0.10, "trace": 0.15,
         "rationale": "pic Na requis pour ramure, Ca pour ossification"},
        {"name": "Saline humide boisée",    "Na": 0.45, "Ca": 0.25, "Mg": 0.10, "trace": 0.20,
         "rationale": "zones humides + argileuses"},
    ],
    "chevreuil": [
        {"name": "Saline cerf standard",    "Na": 0.50, "Ca": 0.25, "P": 0.10, "trace": 0.15,
         "rationale": "attractivité cerf sud-Québec"},
    ],
    "ours_noir": [
        {"name": "Saline bord d'eau ours",  "Na": 0.25, "Ca": 0.40, "P": 0.20, "trace": 0.15,
         "rationale": "Ca élevé pour ours"},
    ],
    "wapiti": [
        {"name": "Saline minérale wapiti",  "Na": 0.55, "Ca": 0.20, "P": 0.10, "Mg": 0.05, "trace": 0.10},
    ],
    "dindon_sauvage": [
        {"name": "Saline oiseau grain+Ca",  "Na": 0.15, "Ca": 0.55, "grit": 0.20, "trace": 0.10,
         "rationale": "besoins calciques galliformes"},
    ],
}


def compute_recettes(species: str, carence: Dict[str, Any] | None) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    base = _RECIPES.get(key) or _RECIPES["orignal"]
    # Boost spécifique si carence
    deficits = (carence or {}).get("deficits_vs_needs", {})
    recommended = []
    for r in base:
        boost = round(sum(d for d in deficits.values()), 2) if deficits else 0.0
        recommended.append({**r, "priority_boost": boost,
                            "carence_context": (carence or {}).get("carence_risk")})
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "FUSION", "role": "SECONDAIRE",
        "species": key,
        "recipes": recommended,
        "data_sources": ["ENGINE_CARENCE_NUTRITIONNELLE_Ω"],
    }
