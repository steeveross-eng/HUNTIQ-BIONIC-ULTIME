"""ENGINE-CONNECTIVITE-ECOLOGIQUE-Ω — Connectivité corridors + evitement routes."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-CONNECTIVITE-ECOLOGIQUE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Connectivite ecologique (corridors, continuity, isolation)", "BIO-SYSTEME", ["LIDAR_WCS_1M"])


def compute_connectivite_ecologique(terrain_v10: dict, corridors: list) -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}
    connectivity_base = terrain.get("connectivity", 0.5) * 100

    n_corridors = len([c for c in (corridors or []) if c.get("path")])
    corridor_richness = min(100, n_corridors * 5)  # 20 corridors = max

    # Composite: connectivity terrain 60% + richness corridors 40%
    score = round(connectivity_base * 0.6 + corridor_richness * 0.4, 1)

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION, "score": score,
        "connectivity_terrain": round(connectivity_base, 1),
        "corridor_richness": round(corridor_richness, 1),
        "corridors_count": n_corridors,
        "data_sources": ["LIDAR_WCS_1M"],
    }
