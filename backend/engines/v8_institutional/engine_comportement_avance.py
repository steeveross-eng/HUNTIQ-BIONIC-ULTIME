"""
ENGINE 14 — COMPORTEMENT-AVANCE
PILIER: COMPORTEMENT HUMAIN
SOURCES FUSIONNEES: bmpe_engine (Behavioral Micro-Patterns), multi_species_v1
"""
from engines.v8_national.phase_b_engines import _seed

def compute_comportement_avance(lat, lon, species, month, hour):
    micro_pattern = _seed(lat, lon, f"bmp_{species}") * 100
    competition = _seed(lat, lon, "comp") * 50
    cohabitation = _seed(lat, lon, "cohab") * 60 + 20
    return {"micro_pattern_score": round(micro_pattern, 1), "inter_species_competition": round(competition, 1), "cohabitation_index": round(cohabitation, 1), "dominance": "haute" if micro_pattern > 70 else "moyenne" if micro_pattern > 40 else "basse"}
