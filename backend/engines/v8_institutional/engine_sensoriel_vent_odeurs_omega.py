"""ENGINE-SENSORIEL-VENT-ODEURS-Ω — Dispersion olfactive + detection vent."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-SENSORIEL-VENT-ODEURS-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Sensoriel vent + dispersion olfactive", "SYSTEME-SENSORIEL", ["OPEN_METEO"])


def compute_sensoriel_vent_odeurs(terrain_v10: dict, wind_deg: float, wind_speed: float) -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}
    olfactive = terrain.get("olfactive_diffusion", 0.5)
    canopy = terrain.get("canopy", 0.5)

    # Score: olfactive diffusion 50% + wind moderation 25% + canopy 25%
    wind_optim = 100 - min(100, abs(wind_speed - 10) * 5)  # optimum ~10 km/h
    score = round(olfactive * 50 + wind_optim * 0.25 + canopy * 25, 1)
    score = min(100, max(0, score))

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION, "score": score,
        "olfactive_diffusion": olfactive,
        "wind_speed_kmh": wind_speed,
        "wind_optim_score": round(wind_optim, 1),
        "wind_deg": wind_deg,
        "data_sources": ["OPEN_METEO"],
    }
