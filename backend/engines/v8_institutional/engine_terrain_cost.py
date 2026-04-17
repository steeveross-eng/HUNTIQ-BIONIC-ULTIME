"""
ENGINE 15 — TERRAIN-COST
PILIER: SYSTEME SENSORIEL
SOURCES FUSIONNEES: phase_b._cost_surface_score, sse_engine, tcve_engine, hydro_v1, p1_pipelines
"""
from engines.v8_national.phase_b_engines import _terrain_profile, _cost_surface_score

def compute_terrain_cost(lat, lon):
    terrain = _terrain_profile(lat, lon)
    cost = _cost_surface_score(terrain)
    traversability = round((1 - cost) * 100, 1)
    return {"cost_surface": cost, "traversability": traversability, "terrain": terrain, "classification": "facile" if cost < 0.3 else "modere" if cost < 0.6 else "difficile"}
