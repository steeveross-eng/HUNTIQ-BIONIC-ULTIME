"""
ENGINE 09 — PRESSION HUMAINE
PILIER: COMPORTEMENT HUMAIN
SOURCES FUSIONNEES: pression_v1, pme_engine (Pressure Memory), exclusion_engine V8 (routes/batiments)
"""
from engines.v8_national.phase_b_engines import _terrain_profile, _seed

def compute_pression(lat, lon):
    terrain = _terrain_profile(lat, lon)
    route_prox = max(0, 100 - terrain["distance_route_m"] * 0.1)
    urban_prox = max(0, 80 - _seed(lat, lon, "urban") * 60)
    trail_prox = _seed(lat, lon, "trail") * 40
    total = route_prox * 0.45 + urban_prox * 0.35 + trail_prox * 0.20
    return {"pression_score": round(min(100, max(0, total)), 1), "route_proximity": round(route_prox, 1), "urban_proximity": round(urban_prox, 1), "trail_density": round(trail_prox, 1), "terrain": terrain}
