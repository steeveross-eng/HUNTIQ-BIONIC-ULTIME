"""ENGINE-IA-VISION-ECOLOGIQUE-Ω — IA Vision structure foret + zones probables."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-IA-VISION-ECOLOGIQUE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "IA Vision structure foret + zones probables", "BIO-SYSTEME", ["NASA_EARTHDATA", "LIDAR_WCS_1M"])


def compute_ia_vision_ecologique(terrain_v10: dict) -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    # IA vision deja dans terrain: zones probables + fiabilite
    zones_probables = {
        "repos": terrain.get("zone_repos_probable", False),
        "alimentation": terrain.get("zone_alimentation_probable", False),
        "thermique": terrain.get("zone_thermique_probable", False),
        "humide": terrain.get("zone_humide_probable", False),
    }
    n_zones = sum(1 for v in zones_probables.values() if v)
    fiabilite = terrain.get("fiabilite", 0.5)

    # Score: richness zones 50% + fiabilite 50%
    score = round((n_zones / 4) * 50 + fiabilite * 50, 1)

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION, "score": min(100, score),
        "zones_probables": zones_probables,
        "zones_count": n_zones,
        "fiabilite_terrain": fiabilite,
        "canopy": terrain.get("canopy"),
        "strate_1_3m": terrain.get("strate_1_3m"),
        "feuillus_ratio": terrain.get("feuillus_ratio"),
        "data_sources": ["NASA_EARTHDATA", "LIDAR_WCS_1M"],
    }
