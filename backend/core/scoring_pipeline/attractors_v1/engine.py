"""
ATTRACTORS ENGINE V1 — Scoring des attracteurs ecologiques
==============================================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Identification et evaluation des points d'attraction ecologiques.
Analyse les sources de nourriture, eau, mineraux, sites de reproduction
et refuges qui attirent la faune vers des zones specifiques.

Facteurs de scoring (0-100):
  ALIMENTAIRE (0-25)    Concentration de ressources alimentaires
  HYDRIQUE (0-20)       Presence et qualite des points d'eau
  MINERAL (0-20)        Salines, suintements, argile minerale
  REPRODUCTION (0-20)   Qualite des sites de rut, nidification, mise-bas
  REFUGE (0-15)         Securite et confort des zones de refuge

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "ATTRACTORS-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.07

SPECIES_ATTRACTORS = {
    "CERF":    {"poids_alim": 0.7, "poids_mineral": 0.8, "poids_rut": 0.6, "saline": True},
    "ORIGNAL": {"poids_alim": 0.8, "poids_mineral": 0.7, "poids_rut": 0.5, "saline": True},
    "OURS":    {"poids_alim": 0.9, "poids_mineral": 0.3, "poids_rut": 0.3, "saline": False},
    "DINDON":  {"poids_alim": 0.8, "poids_mineral": 0.2, "poids_rut": 0.7, "saline": False},
    "WAPITI":  {"poids_alim": 0.7, "poids_mineral": 0.9, "poids_rut": 0.6, "saline": True},
}

SEASONAL_ATTRACTORS = {
    "printemps": {"alim": 0.7, "mineral": 0.9, "repro": 0.3, "refuge": 0.5},
    "ete":       {"alim": 1.0, "mineral": 0.6, "repro": 0.2, "refuge": 0.3},
    "automne":   {"alim": 0.9, "mineral": 0.7, "repro": 0.9, "refuge": 0.6},
    "hiver":     {"alim": 0.4, "mineral": 0.5, "repro": 0.1, "refuge": 0.9},
}


def _compute_attractors_score(lat, lng, species, month):
    p = SPECIES_ATTRACTORS.get(species.upper(), SPECIES_ATTRACTORS["CERF"])
    season = get_season(month)
    s = SEASONAL_ATTRACTORS.get(season, SEASONAL_ATTRACTORS["automne"])

    food_density = _seed(lat, lng, "attr_food")
    water_prox = _seed(lat, lng, "attr_water") < 0.3
    mineral_site = _seed(lat, lng, "attr_mineral") < 0.15
    suintement = _seed(lat, lng, "attr_suint") < 0.1
    canopy = 0.2 + 0.7 * _seed(lat, lng, "attr_canopy")
    rut_terrain = _seed(lat, lng, "attr_rut")
    refuge_quality = _seed(lat, lng, "attr_refuge")

    # ALIMENTAIRE (0-25)
    alimentaire = food_density * p["poids_alim"] * s["alim"] * 25
    alimentaire = min(25, alimentaire)

    # HYDRIQUE (0-20)
    hydrique = 8 if water_prox else 0
    hydrique += _seed(lat, lng, "attr_h2o_qual") * 12
    hydrique = min(20, hydrique)

    # MINERAL (0-20)
    mineral = 0
    if mineral_site and p["saline"]:
        mineral += 12 * p["poids_mineral"] * s["mineral"]
    if suintement:
        mineral += 8
    mineral = min(20, mineral)

    # REPRODUCTION (0-20)
    repro = rut_terrain * p["poids_rut"] * s["repro"] * 15
    if canopy > 0.5 and rut_terrain > 0.4:
        repro += 5
    repro = min(20, repro)

    # REFUGE (0-15)
    refuge = refuge_quality * 8 * s["refuge"]
    if canopy > 0.6:
        refuge += 4
    if water_prox:
        refuge += 3
    refuge = min(15, refuge)

    score = alimentaire + hydrique + mineral + repro + refuge
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_attractors_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_attractors_score(lat, lng, species, month))
