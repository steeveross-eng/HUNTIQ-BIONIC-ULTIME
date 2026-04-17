"""
ENGINE 01 — ZONES
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: phase_b_engines.generate_zones_ta, zone_engine_core_v2, habitat_v1, ndvi_vegetation_v1, repos_v1, osg_engine
OPTIMISATIONS PRESERVEES: terrain-aware scoring, organic polygons 14-20 vertices, exclusion eau/pente
"""
from engines.v8_national.phase_b_engines import generate_zones_ta, _terrain_profile, _organic_polygon, _seed

def compute_zones(lat, lon, species, month, wind_deg=225):
    return generate_zones_ta(lat, lon, species, month)
