"""
ENGINE 02 — CORRIDORS V9-x20
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: phase_b_engines.generate_corridors_ta V9-x20, corridor_10x (A*), cme_engine, trajets_v1
OPTIMISATIONS PRESERVEES: Catmull-Rom terrain-aware, 20 contraintes/favorisations, multi-especes, cost surface V9
"""
from engines.v8_national.phase_b_engines import generate_corridors_ta, _cost_surface_score, _corridor_intensity_x20

def compute_corridors(lat, lon, species, month, hour, wind_deg=225, zones=None):
    return generate_corridors_ta(lat, lon, species, month, hour, wind_deg=wind_deg, zones=zones)
