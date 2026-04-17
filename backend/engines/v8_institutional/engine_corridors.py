"""
ENGINE 02 — CORRIDORS
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: phase_b_engines.generate_corridors_ta, corridor_10x (A*), cme_engine, trajets_v1
OPTIMISATIONS PRESERVEES: Bezier terrain-aware, exclusion eau<10m/pente>45, cost surface, COR-006
"""
from engines.v8_national.phase_b_engines import generate_corridors_ta, _cost_surface_score, _corridor_intensity

def compute_corridors(lat, lon, species, month, hour, wind_deg=225):
    return generate_corridors_ta(lat, lon, species, month, hour)
