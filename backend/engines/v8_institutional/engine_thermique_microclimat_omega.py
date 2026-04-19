"""ENGINE-THERMIQUE-MICROCLIMAT-Ω — Stress thermique + microclimat."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call, get_species_profile

ENGINE_NAME = "ENGINE-THERMIQUE-MICROCLIMAT-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Stress thermique/microclimat (temperature, neige, couvert thermique)", "BIO-SYSTEME", ["OPEN_METEO", "NASA_EARTHDATA"])


def compute_thermique_microclimat(terrain_v10: dict, species: str = "cerf") -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}
    thermal_comfort = terrain.get("thermal_comfort", 0.5)
    canopy = terrain.get("canopy", 0.5)

    # Species-specific thermal threshold
    profile = get_species_profile(species)
    tlim = (profile.get("climate", {}) or {}).get("stress_thermique_c") or [20, 25]
    stress_low, stress_high = (tlim if isinstance(tlim, list) and len(tlim) == 2 else [20, 25])

    # Score: thermal_comfort 50%, canopy (refuge) 30%, tolerance species 20%
    tolerance_bonus = 20 if stress_high >= 20 else 10
    score = round(thermal_comfort * 50 + canopy * 30 + tolerance_bonus, 1)
    score = min(100, max(0, score))

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION, "score": score,
        "thermal_comfort": thermal_comfort,
        "canopy_refuge": canopy,
        "stress_threshold_low_c": stress_low,
        "stress_threshold_high_c": stress_high,
        "data_sources": ["OPEN_METEO", "NASA_EARTHDATA"],
    }
