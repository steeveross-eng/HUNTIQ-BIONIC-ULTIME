"""
ENGINE 03 — AFFUTS
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: phase_b_engines.generate_affuts_ta, affut_ia_engine, hunt_orchestrator.choix_affuts, opportunity_v1
OPTIMISATIONS PRESERVEES: vent oppose, corridor proximity bonus, terrain scoring
"""
from engines.v8_national.phase_b_engines import generate_affuts_ta

def compute_affuts(lat, lon, species, zones, corridors, wind_deg=225):
    return generate_affuts_ta(lat, lon, species, zones, corridors, wind_deg)
