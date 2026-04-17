"""
ENGINE 13 — COMPORTEMENT
PILIER: COMPORTEMENT HUMAIN
SOURCES FUSIONNEES: behavior_v1, ssvl_engine (Species-Specific Visual Logic)
"""
from engines.v8_national.phase_b_engines import _seed

SPECIES_BEHAVIOR = {
    "cerf": {"fuite_m": 80, "groupe_max": 12, "territorialite": 0.6, "nocturne": 0.7},
    "orignal": {"fuite_m": 50, "groupe_max": 3, "territorialite": 0.8, "nocturne": 0.5},
    "chevreuil": {"fuite_m": 60, "groupe_max": 6, "territorialite": 0.5, "nocturne": 0.6},
    "ours": {"fuite_m": 100, "groupe_max": 1, "territorialite": 0.9, "nocturne": 0.4},
    "dindon": {"fuite_m": 40, "groupe_max": 20, "territorialite": 0.3, "nocturne": 0.1},
}

def compute_comportement(lat, lon, species, month, hour):
    cfg = SPECIES_BEHAVIOR.get(species, SPECIES_BEHAVIOR["cerf"])
    stress = _seed(lat, lon, "stress") * 30 + (1 if 10 <= hour <= 14 else 0) * 20
    activity = cfg["nocturne"] * 80 if hour < 6 or hour > 19 else (1 - cfg["nocturne"]) * 60
    return {"species": species, "distance_fuite_m": cfg["fuite_m"], "groupe_max": cfg["groupe_max"], "territorialite": cfg["territorialite"], "stress_level": round(min(100, stress), 1), "activity_level": round(min(100, activity), 1)}
