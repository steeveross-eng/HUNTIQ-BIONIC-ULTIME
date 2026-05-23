"""
ENGINE_CANOPÉE_THERMIQUE_Ω — Effet thermique canopée (ombre/refuge).
PHASE : PHASE_SUPRA_BIO_NUTRITION_Ω · NIVEAU : FONDATION (E42)
RÔLE : SECONDAIRE · PRIORITÉ : MAJEUR
"""
from typing import Dict, Any

# P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω (2026-05-23) — Registry HR-ready (additif read-only).
try:
    from engines.v8_institutional import ndvi_lidar_p0_registry_omega as NDVI_LIDAR_P0  # noqa: F401
except ImportError:
    NDVI_LIDAR_P0 = None  # type: ignore

ENGINE_NAME = "ENGINE_CANOPÉE_THERMIQUE_Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"


def compute_canopee_thermique(terrain_v10: Dict[str, Any] | None, hour: int = 12) -> Dict[str, Any]:
    terrain = (terrain_v10 or {}).get("terrain", terrain_v10 or {})
    canopy = float(terrain.get("canopy", 0.5))
    elevation = float(terrain.get("elevation", 250))
    # Effet d'ombrage diurne (pic à midi)
    sun_intensity = max(0.0, 1.0 - abs(hour - 12) / 7.0)
    shade_buffer_c = round(canopy * 6.0 * sun_intensity, 2)   # °C d'ombre
    nocturnal_loss_c = round((1.0 - canopy) * 3.0, 2)          # °C perte nocturne
    effective_buffer = shade_buffer_c if hour > 7 and hour < 19 else -nocturnal_loss_c
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "level": "FONDATION", "role": "SECONDAIRE",
        "canopy_ratio": canopy,
        "elevation_m": elevation,
        "hour": hour,
        "thermal_buffer_c": effective_buffer,
        "shade_buffer_c_day": shade_buffer_c,
        "nocturnal_loss_c_night": nocturnal_loss_c,
        "data_sources": ["ENGINE_TERRAIN_COST", "microclimat_reference"],
    }
