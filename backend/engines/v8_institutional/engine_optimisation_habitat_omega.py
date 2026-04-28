"""
ENGINE_OPTIMISATION_HABITAT_Ω — Synthèse habitat optimisé (territoire ULTIME).
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : FUSION/SYNTHÈSE (E48)
RÔLE : PRINCIPAL · PRIORITÉ : CRITIQUE
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_OPTIMISATION_HABITAT_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"


def compute_optimisation_habitat(species: str,
                                 attractiveness: Dict[str, Any] | None,
                                 trophic: Dict[str, Any] | None,
                                 social: Dict[str, Any] | None,
                                 sante_physio: Dict[str, Any] | None,
                                 microclimat: Dict[str, Any] | None,
                                 connectivity: Dict[str, Any] | None = None) -> Dict[str, Any]:
    key = str(species or "orignal").lower()
    attract = float((attractiveness or {}).get("attractiveness_score_0_1", 0.5))
    trophic_pressure = float((trophic or {}).get("foraging_pressure_index", 0.5))
    group = float((social or {}).get("group_avg_size", 1.5))
    in_rut = bool((social or {}).get("in_rut_period", False))
    health = float((sante_physio or {}).get("health_index_0_1", 0.5))
    stability = float((microclimat or {}).get("local_stability_index", 0.5))
    connectivity_idx = 0.6
    if isinstance(connectivity, dict):
        connectivity_idx = float(connectivity.get("mean_transition", 0.6))
    # Normalise group → index 0..1
    group_idx = min(1.0, group / 8.0)
    # Composite habitat ULTIME
    composite = round(
        attract * 0.30
        + trophic_pressure * 0.20
        + health * 0.20
        + stability * 0.10
        + connectivity_idx * 0.15
        + (group_idx * 0.05)
        + (0.05 if in_rut else 0.0), 3
    )
    composite = max(0.0, min(1.0, composite))
    band = "ULTIME" if composite >= 0.85 else (
           "HAUT" if composite >= 0.70 else (
           "STANDARD" if composite >= 0.50 else "LIMITÉ"))
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "FUSION", "role": "PRINCIPAL",
        "species": key,
        "habitat_optimisation_score_0_1": composite,
        "habitat_band": band,
        "components": {
            "nutritional_attractiveness": attract,
            "trophic_pressure": trophic_pressure,
            "group_index": group_idx,
            "in_rut_bonus": in_rut,
            "health": health,
            "microclimat_stability": stability,
            "connectivity": connectivity_idx,
        },
        "recommendation": ("TERRITOIRE_ULTIME — propice chasse sélective" if composite >= 0.85
                          else "HAUT POTENTIEL — prospection favorisée" if composite >= 0.70
                          else "STANDARD" if composite >= 0.50
                          else "LIMITÉ — éviter pour cette espèce/saison"),
        "data_sources": ["ENGINE_NUTRITIONAL_ATTRACTIVENESS_Ω", "ENGINE_TROPHIC_BEHAVIOR_Ω",
                        "ENGINE_SOCIAL_STRUCTURE_Ω", "ENGINE_SANTÉ_PHYSIO_Ω",
                        "ENGINE_MICROCLIMAT_Ω_ADVANCED", "ENGINE_CONNECTIVITE_ECOLOGIQUE_Ω"],
    }
