"""
ENGINE 16 — VISIBILITE
PILIER: SYSTEME SENSORIEL
SOURCES FUSIONNEES: visibility_v1, vfe_engine (Visual Fusion)
"""
from engines.v8_national.phase_b_engines import _terrain_profile, _seed
import math

def compute_visibilite(lat, lon, observer_height_m=1.7):
    terrain = _terrain_profile(lat, lon)
    canopy_block = terrain["canopy"] * 0.7
    strate_block = terrain["strate_1_3m"] * 0.3
    pente_factor = max(0, 1 - terrain["pente_deg"] / 45)
    visibility_score = (1 - canopy_block - strate_block) * pente_factor * 100
    range_m = max(10, (1 - terrain["canopy"]) * 300 + pente_factor * 100)
    return {"visibility_score": round(max(0, min(100, visibility_score)), 1), "effective_range_m": round(range_m), "canopy_obstruction": round(canopy_block * 100, 1), "terrain": terrain}
