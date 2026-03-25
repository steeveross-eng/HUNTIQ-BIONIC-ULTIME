"""
WEATHER ENGINE V1 — Scoring d'impact meteorologique
=======================================================
Directive x4000-SUPRA PHASE 2 (CORE+++)
Domaine: Impact des conditions meteorologiques sur l'activite faunique.
Evalue temperature, precipitations, vent, neige, pression atmospherique
et leur effet sur le comportement de chaque espece.

Facteurs de scoring (0-100):
  TEMPERATURE (0-25)     Adequation thermique pour l'espece
  PRECIPITATIONS (0-20)  Impact pluie/neige sur l'activite
  VENT (0-20)            Exposition et protection au vent
  COUVERTURE_NEIGEUSE (0-20) Epaisseur neige et mobilite
  PRESSION (0-15)        Impact pression barometrique sur activite

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "WEATHER-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.05

MONTHLY_WEATHER_QC = {
    1:  {"temp": -15, "precip": 0.6, "vent": 0.7, "neige_cm": 60, "pression": 0.5},
    2:  {"temp": -13, "precip": 0.5, "vent": 0.7, "neige_cm": 70, "pression": 0.5},
    3:  {"temp": -5,  "precip": 0.6, "vent": 0.6, "neige_cm": 50, "pression": 0.6},
    4:  {"temp": 4,   "precip": 0.5, "vent": 0.5, "neige_cm": 10, "pression": 0.6},
    5:  {"temp": 12,  "precip": 0.5, "vent": 0.4, "neige_cm": 0,  "pression": 0.7},
    6:  {"temp": 18,  "precip": 0.5, "vent": 0.3, "neige_cm": 0,  "pression": 0.7},
    7:  {"temp": 21,  "precip": 0.5, "vent": 0.3, "neige_cm": 0,  "pression": 0.8},
    8:  {"temp": 20,  "precip": 0.5, "vent": 0.3, "neige_cm": 0,  "pression": 0.7},
    9:  {"temp": 14,  "precip": 0.5, "vent": 0.4, "neige_cm": 0,  "pression": 0.7},
    10: {"temp": 7,   "precip": 0.6, "vent": 0.5, "neige_cm": 5,  "pression": 0.6},
    11: {"temp": 0,   "precip": 0.6, "vent": 0.6, "neige_cm": 20, "pression": 0.5},
    12: {"temp": -10, "precip": 0.6, "vent": 0.7, "neige_cm": 45, "pression": 0.5},
}

SPECIES_WEATHER = {
    "CERF":    {"temp_opt": (5, 20), "neige_max_cm": 50, "vent_tolerance": 0.5, "pluie_tolerance": 0.6},
    "ORIGNAL": {"temp_opt": (-5, 15), "neige_max_cm": 80, "vent_tolerance": 0.7, "pluie_tolerance": 0.7},
    "OURS":    {"temp_opt": (5, 25), "neige_max_cm": 30, "vent_tolerance": 0.6, "pluie_tolerance": 0.5},
    "DINDON":  {"temp_opt": (5, 25), "neige_max_cm": 25, "vent_tolerance": 0.4, "pluie_tolerance": 0.4},
    "WAPITI":  {"temp_opt": (0, 18), "neige_max_cm": 60, "vent_tolerance": 0.6, "pluie_tolerance": 0.6},
}


def _compute_weather_score(lat, lng, species, month):
    p = SPECIES_WEATHER.get(species.upper(), SPECIES_WEATHER["CERF"])
    w = MONTHLY_WEATHER_QC.get(month, MONTHLY_WEATHER_QC[10])
    local_var = (_seed(lat, lng, "weather_var") - 0.5) * 6

    temp = w["temp"] + local_var
    canopy = 0.2 + 0.7 * _seed(lat, lng, "weather_canopy")
    exposition = _seed(lat, lng, "weather_expo")

    # TEMPERATURE (0-25)
    t_min, t_max = p["temp_opt"]
    if t_min <= temp <= t_max:
        temperature = 25.0
    elif temp < t_min:
        temperature = max(0, 25 - (t_min - temp) * 1.5)
    else:
        temperature = max(0, 25 - (temp - t_max) * 2.0)

    # PRECIPITATIONS (0-20)
    precip_intensity = w["precip"] * (0.7 + 0.6 * _seed(lat, lng, "weather_precip"))
    precip_score = 20 * (1.0 - precip_intensity * (1.0 - p["pluie_tolerance"]))
    if canopy > 0.6:
        precip_score = min(20, precip_score + 3)
    precip_score = max(0, min(20, precip_score))

    # VENT (0-20)
    vent_local = w["vent"] * exposition
    vent_score = 20 * (1.0 - vent_local * (1.0 - p["vent_tolerance"]))
    if canopy > 0.5:
        vent_score = min(20, vent_score + 4)
    vent_score = max(0, min(20, vent_score))

    # COUVERTURE NEIGEUSE (0-20)
    neige = w["neige_cm"] * (0.8 + 0.4 * _seed(lat, lng, "weather_neige"))
    if neige <= 5:
        neige_score = 20.0
    elif neige >= p["neige_max_cm"]:
        neige_score = 2.0
    else:
        neige_score = 20 * (1.0 - (neige - 5) / (p["neige_max_cm"] - 5))

    # PRESSION (0-15)
    pression = w["pression"] + (_seed(lat, lng, "weather_press") - 0.5) * 0.2
    pression_score = pression * 15
    pression_score = max(0, min(15, pression_score))

    score = temperature + precip_score + vent_score + neige_score + pression_score
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_weather_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_weather_score(lat, lng, species, month))
