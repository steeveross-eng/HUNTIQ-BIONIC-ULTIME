"""
ENGINE 11 — FREQUENTATION (FAUNE + HUMAIN)
PILIER: COMPORTEMENT HUMAIN
SOURCES FUSIONNEES: learning_v1 (tendances), behavior_v1 (partiel)
"""
from engines.v8_national.phase_b_engines import _seed

def compute_frequentation(lat, lon, species, month, hour):
    crep = species in ["cerf", "orignal", "wapiti", "caribou", "chevreuil"]
    faune_base = _seed(lat, lon, "freq_faune") * 60 + 20
    humain_base = _seed(lat, lon, "freq_hum") * 40 + 10
    if crep and (5 <= hour <= 8 or 16 <= hour <= 19):
        faune_base *= 1.4
    if 9 <= hour <= 16:
        humain_base *= 1.3
    if month in [9, 10, 11]:
        faune_base *= 1.2
        humain_base *= 1.1
    return {"frequentation_faune": round(min(100, faune_base), 1), "frequentation_humain": round(min(100, humain_base), 1), "ratio": round(faune_base / max(1, humain_base), 2)}
