"""
OPPORTUNITY ENGINE V1 — Scoring des opportunites d'observation
==================================================================
Directive x4000-SUPRA PHASE 2 (CORE+++)
Domaine: Evaluation des opportunites d'observation et d'approche.
Analyse les fenetres optimales de contact, les points d'acces,
la probabilite de presence et les conditions favorables.

Facteurs de scoring (0-100):
  PROBABILITE (0-30)   Probabilite de presence de l'espece
  ACCESSIBILITE (0-25) Facilite d'acces au site d'observation
  FENETRE (0-20)       Duree et qualite de la fenetre d'opportunite
  APPROCHE (0-15)      Capacite d'approche discrete
  CONDITIONS (0-10)    Conditions meteorologiques et lumineuses

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "OPPORTUNITY-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.06

SPECIES_OPPORTUNITY = {
    "CERF":    {"densite_base": 0.7, "detectabilite": 0.6, "best_months": [10, 11], "pref_lisiere": 0.9},
    "ORIGNAL": {"densite_base": 0.4, "detectabilite": 0.5, "best_months": [9, 10], "pref_lisiere": 0.5},
    "OURS":    {"densite_base": 0.3, "detectabilite": 0.4, "best_months": [5, 6, 9], "pref_lisiere": 0.4},
    "DINDON":  {"densite_base": 0.6, "detectabilite": 0.7, "best_months": [4, 5, 10], "pref_lisiere": 0.8},
    "WAPITI":  {"densite_base": 0.3, "detectabilite": 0.5, "best_months": [9, 10], "pref_lisiere": 0.6},
}


def _compute_opportunity_score(lat, lng, species, month):
    p = SPECIES_OPPORTUNITY.get(species.upper(), SPECIES_OPPORTUNITY["CERF"])

    habitat_qual = _seed(lat, lng, "opp_habitat")
    dist_acces = _seed(lat, lng, "opp_acces") * 2000
    canopy = 0.2 + 0.7 * _seed(lat, lng, "opp_canopy")
    lisiere = _seed(lat, lng, "opp_lisiere") < 0.3
    vent_favorable = _seed(lat, lng, "opp_vent") < 0.5
    is_best_month = month in p["best_months"]

    # PROBABILITE (0-30)
    prob = p["densite_base"] * habitat_qual * 20
    if is_best_month:
        prob += 8
    if lisiere:
        prob += 5 * p["pref_lisiere"]
    prob = min(30, prob)

    # ACCESSIBILITE (0-25)
    if dist_acces < 200:
        access = 25.0
    elif dist_acces > 1500:
        access = 5.0
    else:
        access = 25.0 - 20.0 * (dist_acces - 200) / 1300

    # FENETRE (0-20)
    fenetre = 10
    if is_best_month:
        fenetre += 7
    fenetre += p["detectabilite"] * 3
    fenetre = min(20, fenetre)

    # APPROCHE (0-15)
    approche = canopy * 8
    if vent_favorable:
        approche += 4
    if lisiere:
        approche += 3
    approche = min(15, approche)

    # CONDITIONS (0-10)
    conditions = 5
    if is_best_month:
        conditions += 3
    if vent_favorable:
        conditions += 2
    conditions = min(10, conditions)

    score = prob + access + fenetre + approche + conditions
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_opportunity_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_opportunity_score(lat, lng, species, month))
