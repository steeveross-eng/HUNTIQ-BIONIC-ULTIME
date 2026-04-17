"""
ENGINE 10 — RISQUE
PILIER: COMPORTEMENT HUMAIN
SOURCES FUSIONNEES: risk_v1
"""
from engines.v8_national.phase_b_engines import _terrain_profile, _seed

def compute_risque(lat, lon, species, month):
    terrain = _terrain_profile(lat, lon)
    predation = _seed(lat, lon, "pred") * 30 + (1 - terrain["canopy"]) * 20
    perturbation = max(0, 80 - terrain["distance_route_m"] * 0.08)
    mortalite_routiere = max(0, 60 - terrain["distance_route_m"] * 0.06)
    seasonal = 1.2 if month in [9, 10, 11] else 0.8
    total = (predation * 0.30 + perturbation * 0.40 + mortalite_routiere * 0.30) * seasonal
    return {"risque_score": round(min(100, max(0, total)), 1), "predation": round(predation, 1), "perturbation_humaine": round(perturbation, 1), "mortalite_routiere": round(mortalite_routiere, 1), "terrain": terrain}
