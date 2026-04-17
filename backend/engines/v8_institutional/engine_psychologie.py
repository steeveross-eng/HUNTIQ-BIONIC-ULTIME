"""
ENGINE 20 — PSYCHOLOGIE ANIMALE
PILIER: PREDICTION-INTELLIGENCE
ENGINE COMPLET — ZERO STUB
Modele l'etat psychologique de l'animal: stress, vigilance, dominance,
motivation alimentaire, motivation reproductive, familiarite territoire.
"""
import math
from engines.v8_national.phase_b_engines import _seed, _terrain_profile

SPECIES_PSYCHOLOGY = {
    "cerf": {"stress_base": 35, "vigilance_base": 60, "dominance_hierarchy": True, "territorial": True, "flight_threshold": 0.65},
    "orignal": {"stress_base": 25, "vigilance_base": 50, "dominance_hierarchy": False, "territorial": True, "flight_threshold": 0.55},
    "ours": {"stress_base": 20, "vigilance_base": 40, "dominance_hierarchy": True, "territorial": True, "flight_threshold": 0.80},
    "chevreuil": {"stress_base": 45, "vigilance_base": 70, "dominance_hierarchy": False, "territorial": False, "flight_threshold": 0.50},
    "dindon": {"stress_base": 50, "vigilance_base": 75, "dominance_hierarchy": True, "territorial": False, "flight_threshold": 0.40},
}


def _stress_model(lat, lon, species, month, hour, pression_score):
    cfg = SPECIES_PSYCHOLOGY.get(species, SPECIES_PSYCHOLOGY["cerf"])
    terrain = _terrain_profile(lat, lon)
    base = cfg["stress_base"]
    pression_effect = pression_score * 0.3
    cover_relief = terrain["canopy"] * 15
    diurnal = 10 if 10 <= hour <= 14 else -5
    seasonal = 15 if month in [9, 10, 11] and cfg["dominance_hierarchy"] else 0
    stress = base + pression_effect - cover_relief + diurnal + seasonal
    return round(min(100, max(0, stress)), 1)


def _vigilance_model(species, stress, hour, terrain):
    cfg = SPECIES_PSYCHOLOGY.get(species, SPECIES_PSYCHOLOGY["cerf"])
    base = cfg["vigilance_base"]
    stress_effect = stress * 0.25
    nocturnal_drop = -15 if hour < 5 or hour > 21 else 0
    cover_effect = -terrain["canopy"] * 20
    open_effect = (1 - terrain["canopy"]) * 15
    vigilance = base + stress_effect + nocturnal_drop + cover_effect + open_effect
    return round(min(100, max(0, vigilance)), 1)


def _motivation_alimentaire(species, month, hour):
    seasonal = {"hiver": 0.9, "printemps": 0.7, "ete": 0.5, "automne": 0.8}
    saison = "hiver" if month in [12, 1, 2] else "printemps" if month in [3, 4, 5] else "ete" if month in [6, 7, 8] else "automne"
    base = seasonal[saison]
    crepuscular = 1.3 if 5 <= hour <= 8 or 16 <= hour <= 19 else 0.7
    return round(min(100, base * crepuscular * 100), 1)


def _motivation_reproductive(species, month):
    rut_months = {"cerf": [9, 10, 11], "orignal": [9, 10], "ours": [5, 6, 7], "chevreuil": [7, 8], "dindon": [4, 5]}
    months = rut_months.get(species, [10])
    if month in months:
        return 90.0
    elif month in [(m - 1) % 12 or 12 for m in months] + [(m + 1) % 12 or 12 for m in months]:
        return 50.0
    return 15.0


def compute_psychologie(lat, lon, species="cerf", month=10, hour=7, pression_score=30):
    terrain = _terrain_profile(lat, lon)
    stress = _stress_model(lat, lon, species, month, hour, pression_score)
    vigilance = _vigilance_model(species, stress, hour, terrain)
    motiv_alim = _motivation_alimentaire(species, month, hour)
    motiv_repro = _motivation_reproductive(species, month)
    cfg = SPECIES_PSYCHOLOGY.get(species, SPECIES_PSYCHOLOGY["cerf"])

    familiarite = _seed(lat, lon, f"famil_{species}") * 60 + 20
    flight_risk = stress / 100 * (1 - cfg["flight_threshold"])
    predictabilite = round((familiarite * 0.3 + (100 - stress) * 0.3 + motiv_alim * 0.2 + (100 - vigilance) * 0.2), 1)

    return {
        "engine": "V8-PSYCHOLOGIE-ANIMALE",
        "status": "ACTIF",
        "stress": stress,
        "vigilance": vigilance,
        "motivation_alimentaire": motiv_alim,
        "motivation_reproductive": motiv_repro,
        "familiarite_territoire": round(familiarite, 1),
        "flight_risk": round(min(100, max(0, flight_risk * 100)), 1),
        "predictabilite": round(min(100, max(0, predictabilite)), 1),
        "etat_mental": "alerte" if stress > 60 else "vigilant" if vigilance > 60 else "detendu" if stress < 30 else "neutre",
        "species_profile": cfg,
        "terrain": terrain,
    }
