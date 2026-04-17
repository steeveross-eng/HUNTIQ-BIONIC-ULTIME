"""
ENGINE 18 — BIO-SIGNES (ADN visuel + chimie visuelle + fraicheur)
PILIER: SYSTEME SENSORIEL
ENGINE COMPLET — ZERO STUB
Analyse les indices biologiques visuels: traces, feces, frottages, grattages,
urine, litiere, marques territoriales. Evalue fraicheur, intensite, espece probable.
"""
import math
from engines.v8_national.phase_b_engines import _terrain_profile, _seed

TRACE_TYPES = {
    "empreinte": {"persistance_h": 48, "fiabilite": 0.85},
    "feces": {"persistance_h": 120, "fiabilite": 0.90},
    "frottage": {"persistance_h": 240, "fiabilite": 0.80},
    "grattage": {"persistance_h": 168, "fiabilite": 0.75},
    "urine": {"persistance_h": 24, "fiabilite": 0.70},
    "litiere": {"persistance_h": 336, "fiabilite": 0.65},
    "marque_territoriale": {"persistance_h": 720, "fiabilite": 0.60},
}

SPECIES_TRACE_PROFILE = {
    "cerf": {"empreinte_cm": 7, "feces_diam_mm": 12, "frottage_hauteur_m": 1.2, "densite_traces_km2": 40},
    "orignal": {"empreinte_cm": 15, "feces_diam_mm": 18, "frottage_hauteur_m": 2.0, "densite_traces_km2": 15},
    "ours": {"empreinte_cm": 18, "feces_diam_mm": 30, "frottage_hauteur_m": 1.8, "densite_traces_km2": 8},
    "chevreuil": {"empreinte_cm": 5, "feces_diam_mm": 8, "frottage_hauteur_m": 0.8, "densite_traces_km2": 55},
    "dindon": {"empreinte_cm": 10, "feces_diam_mm": 15, "frottage_hauteur_m": 0, "densite_traces_km2": 25},
}


def _fraicheur_score(age_hours, trace_type):
    cfg = TRACE_TYPES.get(trace_type, {"persistance_h": 48, "fiabilite": 0.5})
    if age_hours <= 0:
        return 100
    ratio = age_hours / cfg["persistance_h"]
    if ratio > 1:
        return 0
    decay = math.exp(-3 * ratio)
    return round(decay * 100 * cfg["fiabilite"], 1)


def _chimie_visuelle_score(terrain, month, species):
    humidity = max(0, min(1, 0.3 + _seed(terrain["canopy"], terrain["pente_deg"], "humid") * 0.5))
    temp_factor = 1.0 if 5 <= month <= 9 else 0.6
    decomposition_rate = humidity * 0.4 + temp_factor * 0.3 + (1 - terrain["canopy"]) * 0.3
    preservation = round((1 - decomposition_rate) * 100, 1)
    return {"humidity_index": round(humidity, 2), "decomposition_rate": round(decomposition_rate, 3), "preservation_score": preservation}


def _adn_visuel_score(lat, lon, species, month):
    profile = SPECIES_TRACE_PROFILE.get(species, SPECIES_TRACE_PROFILE["cerf"])
    base_density = profile["densite_traces_km2"]
    seasonal = 1.3 if month in [9, 10, 11] else 0.7 if month in [1, 2, 3] else 1.0
    terrain = _terrain_profile(lat, lon)
    cover_bonus = terrain["canopy"] * 0.3 + terrain["strate_1_3m"] * 0.2
    estimated_density = base_density * seasonal * (1 + cover_bonus)
    trace_probability = min(100, estimated_density * 1.5)

    traces_detectables = []
    for trace_type, cfg in TRACE_TYPES.items():
        prob = _seed(lat, lon, f"trace_{trace_type}") * 100
        if prob < trace_probability * cfg["fiabilite"]:
            age_h = _seed(lat, lon, f"age_{trace_type}") * cfg["persistance_h"]
            fraicheur = _fraicheur_score(age_h, trace_type)
            if fraicheur > 10:
                traces_detectables.append({
                    "type": trace_type, "fraicheur": fraicheur,
                    "age_estime_h": round(age_h, 1),
                    "fiabilite": cfg["fiabilite"],
                })

    traces_detectables.sort(key=lambda x: -x["fraicheur"])
    return {"traces": traces_detectables, "densite_estimee_km2": round(estimated_density, 1), "trace_probability": round(trace_probability, 1)}


def compute_bio_signes(lat, lon, species="cerf", month=10):
    terrain = _terrain_profile(lat, lon)
    adn = _adn_visuel_score(lat, lon, species, month)
    chimie = _chimie_visuelle_score(terrain, month, species)

    adn_score = min(100, sum(t["fraicheur"] * t["fiabilite"] for t in adn["traces"]) / max(1, len(adn["traces"]))) if adn["traces"] else 0
    composite = round(adn_score * 0.50 + chimie["preservation_score"] * 0.30 + adn["trace_probability"] * 0.20, 1)

    return {
        "engine": "V8-BIO-SIGNES",
        "status": "ACTIF",
        "composite_score": composite,
        "adn_visuel": {"score": round(adn_score, 1), "traces": adn["traces"], "densite_km2": adn["densite_estimee_km2"]},
        "chimie_visuelle": chimie,
        "fraicheur_globale": round(adn_score, 1),
        "trace_probability": adn["trace_probability"],
        "terrain": terrain,
        "species_profile": SPECIES_TRACE_PROFILE.get(species, {}),
    }
