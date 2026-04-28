"""
ENGINE_MICROCLIMAT_Ω_ADVANCED — Version avancée microclimat locale.
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : FONDATION (E43)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR

Évolution de E23 (ENGINE_THERMIQUE_MICROCLIMAT_Ω) : agrège les 4 sources
(terrain, canopée, pression, hydro) pour produire une grille microclimatique
consolidée au waypoint.
"""
from typing import Dict, Any

ENGINE_NAME = "ENGINE_MICROCLIMAT_Ω_ADVANCED"
ENGINE_VERSION = "V1-SUPRA-2026-04"


def compute_microclimat_advanced(terrain_v10: Dict[str, Any] | None,
                                 canopee: Dict[str, Any] | None,
                                 pression: Dict[str, Any] | None,
                                 hydrologie: Dict[str, Any] | None,
                                 hour: int = 12, month: int = 10) -> Dict[str, Any]:
    terrain = (terrain_v10 or {}).get("terrain", terrain_v10 or {})
    canopy_buffer = float((canopee or {}).get("thermal_buffer_c", 0.0))
    pression_mbar = float((pression or {}).get("pression", 1013))
    hydro_humid = float((hydrologie or {}).get("humidity_ratio", 0.5)) if isinstance(hydrologie, dict) else 0.5

    slope = float(terrain.get("slope_deg", 5))
    elev = float(terrain.get("elevation", 250))
    # Algorithme empirique : Δ température locale
    base_c = 12 - abs(month - 7) * 2.5  # saison
    correction = canopy_buffer + (slope - 5) * -0.02 + (elev - 250) / 100 * -0.6
    local_c = round(base_c + correction, 2)
    # Stability index (pression + humidité)
    stability = round(((pression_mbar - 1000) / 30) * 0.6 + hydro_humid * 0.4, 3)
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "FONDATION", "role": "SECONDAIRE",
        "local_temperature_c": local_c,
        "local_stability_index": stability,
        "inputs_consumed": {
            "canopy_buffer_c": canopy_buffer,
            "pression_mbar": pression_mbar,
            "humidity_ratio": hydro_humid,
            "slope_deg": slope,
            "elevation_m": elev,
        },
        "data_sources": ["E13", "E15", "E20", "E23", "E42"],
    }
