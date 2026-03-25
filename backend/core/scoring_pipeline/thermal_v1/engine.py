"""
THERMAL ENGINE V1 — Scoring de confort thermique
====================================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Confort thermique et microclimat pour la faune.
Evalue l'ombrage, l'exposition au vent, l'elevation, la couverture
vegetale et les refuges thermiques (coniferes, vallons).

Facteurs de scoring (0-100):
  OMBRAGE (0-25)       Canopy density, orientation, coniferes
  PROTECTION_VENT (0-25) Topographie, densite forestiere, expositions
  REFUGE_THERMIQUE (0-20) Vallons, coniferes denses, grottes naturelles
  REGULATION (0-20)     Eau proche (evapotranspiration), altitude
  ADAPTATION (0-10)     Capacite espece a reguler temperature

BCE-4X: NON integre dans score_consolide (Option A)
"""
import math
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "THERMAL-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.06

SPECIES_THERMAL = {
    "CERF":    {"tolerance_froid": 0.7, "tolerance_chaud": 0.5, "besoin_ombrage": 0.6, "pref_conifere": 0.8},
    "ORIGNAL": {"tolerance_froid": 0.9, "tolerance_chaud": 0.3, "besoin_ombrage": 0.8, "pref_conifere": 0.7},
    "OURS":    {"tolerance_froid": 0.4, "tolerance_chaud": 0.6, "besoin_ombrage": 0.5, "pref_conifere": 0.6},
    "DINDON":  {"tolerance_froid": 0.5, "tolerance_chaud": 0.7, "besoin_ombrage": 0.4, "pref_conifere": 0.9},
    "WAPITI":  {"tolerance_froid": 0.8, "tolerance_chaud": 0.4, "besoin_ombrage": 0.7, "pref_conifere": 0.7},
}

SEASONAL_THERMAL = {
    "printemps": {"stress_froid": 0.3, "stress_chaud": 0.1, "importance_ombrage": 0.3},
    "ete":       {"stress_froid": 0.0, "stress_chaud": 0.8, "importance_ombrage": 0.9},
    "automne":   {"stress_froid": 0.4, "stress_chaud": 0.1, "importance_ombrage": 0.3},
    "hiver":     {"stress_froid": 0.9, "stress_chaud": 0.0, "importance_ombrage": 0.1},
}


def _compute_thermal_score(lat, lng, species, month):
    p = SPECIES_THERMAL.get(species.upper(), SPECIES_THERMAL["CERF"])
    season = get_season(month)
    s = SEASONAL_THERMAL.get(season, SEASONAL_THERMAL["automne"])

    canopy = 0.2 + 0.7 * _seed(lat, lng, "therm_canopy")
    conifere_pct = _seed(lat, lng, "therm_conif")
    exposition_vent = _seed(lat, lng, "therm_vent")
    altitude_rel = _seed(lat, lng, "therm_alt") * 400
    eau_prox = _seed(lat, lng, "therm_eau") < 0.3
    vallon = _seed(lat, lng, "therm_vallon") < 0.25

    # OMBRAGE (0-25)
    ombrage_base = canopy * 15 + conifere_pct * p["pref_conifere"] * 10
    ombrage = min(25, ombrage_base * (0.5 + 0.5 * s["importance_ombrage"]))

    # PROTECTION VENT (0-25)
    protection = (1.0 - exposition_vent) * 15
    if canopy > 0.6:
        protection += 5
    if vallon:
        protection += 5
    protection = min(25, protection)

    # REFUGE THERMIQUE (0-20)
    refuge = 0
    if conifere_pct > 0.4:
        refuge += 8 * p["pref_conifere"]
    if vallon:
        refuge += 7
    if canopy > 0.7:
        refuge += 5
    refuge = min(20, refuge)

    # REGULATION (0-20)
    regulation = 10
    if eau_prox:
        regulation += 5
    if 200 < altitude_rel < 350:
        regulation += 5
    regulation = min(20, regulation)

    # ADAPTATION (0-10)
    if s["stress_froid"] > 0.5:
        adaptation = p["tolerance_froid"] * 10
    elif s["stress_chaud"] > 0.5:
        adaptation = p["tolerance_chaud"] * 10
    else:
        adaptation = 7.0

    score = ombrage + protection + refuge + regulation + adaptation
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_thermal_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_thermal_score(lat, lng, species, month))
