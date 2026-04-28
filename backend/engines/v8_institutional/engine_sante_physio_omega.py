"""
ENGINE_SANTÉ_PHYSIO_Ω — Indicateur de santé physiologique estimée.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : BIOLOGIE (E46)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_SANTÉ_PHYSIO_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"


def compute_sante_physio(species: str,
                         forage_quality: Dict[str, Any] | None,
                         carence: Dict[str, Any] | None,
                         stress_anthropique: float | None = None,
                         microclimat: Dict[str, Any] | None = None) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    forage_idx = float((forage_quality or {}).get("forage_quality_index", 0.6))
    deficit = float((carence or {}).get("total_deficit_score", 0.0))
    stress = float(stress_anthropique or 0.3)
    stability = float((microclimat or {}).get("local_stability_index", 0.5))
    # Formule synthèse 0..1 (plus haut = meilleur)
    health = round(
        forage_idx * 0.40
        + (1.0 - min(1.0, deficit)) * 0.30
        + (1.0 - stress) * 0.15
        + stability * 0.15, 3
    )
    health = max(0.0, min(1.0, health))
    band = "EXCELLENT" if health >= 0.80 else ("BON" if health >= 0.60 else ("MOYEN" if health >= 0.40 else "CRITIQUE"))
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "BIOLOGIE", "role": "SECONDAIRE",
        "species": key,
        "health_index_0_1": health,
        "health_band": band,
        "components": {
            "forage": forage_idx, "deficit": deficit,
            "stress": stress, "stability": stability,
        },
        "data_sources": ["ENGINE_FORAGE_QUALITÉ_Ω", "ENGINE_CARENCE_NUTRITIONNELLE_Ω",
                        "ENGINE_STRESS_ANTHROPIQUE_Ω", "ENGINE_MICROCLIMAT_Ω_ADVANCED"],
    }
