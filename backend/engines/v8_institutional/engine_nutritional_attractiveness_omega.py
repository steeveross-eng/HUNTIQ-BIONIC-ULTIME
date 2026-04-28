"""
ENGINE_NUTRITIONAL_ATTRACTIVENESS_Ω — Synthèse attractivité nutritionnelle du territoire.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : FUSION/SYNTHÈSE (E47)
RÔLE : PRINCIPAL · PRIORITÉ : CRITIQUE
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_NUTRITIONAL_ATTRACTIVENESS_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"


def compute_nutritional_attractiveness(species: str,
                                       forage_quality: Dict[str, Any] | None,
                                       champs_nourriciers: Dict[str, Any] | None,
                                       sol_nutriments: Dict[str, Any] | None,
                                       recettes_salines: Dict[str, Any] | None,
                                       sante_physio: Dict[str, Any] | None) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    forage_idx = float((forage_quality or {}).get("forage_quality_index", 0.5))
    champs_idx = float((champs_nourriciers or {}).get("mean_attractiveness", 0.0))
    sol_idx = float((sol_nutriments or {}).get("fertility_index", 0.5))
    recipe_boost = 0.0
    if recettes_salines and recettes_salines.get("recipes"):
        recipe_boost = max((r.get("priority_boost", 0.0) for r in recettes_salines["recipes"]), default=0.0)
    health_idx = float((sante_physio or {}).get("health_index_0_1", 0.5))
    # Agrégation pondérée (Σ = 1.0)
    score = round(
        forage_idx * 0.30
        + champs_idx * 0.20
        + sol_idx * 0.15
        + recipe_boost * 0.10
        + health_idx * 0.25, 3
    )
    score = max(0.0, min(1.0, score))
    band = "ULTIME" if score >= 0.85 else (
           "ÉLEVÉE" if score >= 0.70 else (
           "MODÉRÉE" if score >= 0.50 else "FAIBLE"))
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "FUSION", "role": "PRINCIPAL",
        "species": key,
        "attractiveness_score_0_1": score,
        "attractiveness_band": band,
        "components": {
            "forage_quality": forage_idx,
            "champs_nourriciers": champs_idx,
            "sol_fertility": sol_idx,
            "recipes_boost": recipe_boost,
            "sante_physio": health_idx,
        },
        "data_sources": ["ENGINE_FORAGE_QUALITÉ_Ω", "ENGINE_CHAMPS_NOURRICIERS_Ω",
                        "ENGINE_SOL_NUTRIMENTS_Ω", "ENGINE_RECETTES_SALINES_Ω",
                        "ENGINE_SANTÉ_PHYSIO_Ω"],
    }
