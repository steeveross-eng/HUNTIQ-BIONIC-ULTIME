"""
BEHAVIOR ENGINE V1 — Scoring comportemental
================================================
Directive x4000-SUPRA PHASE 2 (CORE+++)
Domaine: Modelisation du comportement animal.
Evalue la distance de fuite, la dynamique de groupe,
les patrons d'alimentation, le comportement territorial
et la vigilance selon l'espece et la saison.

Facteurs de scoring (0-100):
  SECURITE (0-25)    Distance de fuite, couvert, echappatoire
  SOCIAL (0-20)      Adequation pour la taille de groupe typique
  ALIMENTATION (0-20) Patrons de fourragement (brout, paturage, glandee)
  TERRITORIAL (0-20)  Marquage, defense, domaine vital
  VIGILANCE (0-15)    Capacite de detection, hauteur d'observation

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "BEHAVIOR-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.05

SPECIES_BEHAVIOR = {
    "CERF":    {"dist_fuite_m": 80, "taille_groupe": 6, "territorial": 0.4, "vigilance": 0.7, "fourragement": "brout"},
    "ORIGNAL": {"dist_fuite_m": 50, "taille_groupe": 2, "territorial": 0.6, "vigilance": 0.5, "fourragement": "brout_aquatique"},
    "OURS":    {"dist_fuite_m": 40, "taille_groupe": 1, "territorial": 0.8, "vigilance": 0.6, "fourragement": "omnivore"},
    "DINDON":  {"dist_fuite_m": 60, "taille_groupe": 12, "territorial": 0.3, "vigilance": 0.9, "fourragement": "glandee"},
    "WAPITI":  {"dist_fuite_m": 100, "taille_groupe": 15, "territorial": 0.5, "vigilance": 0.6, "fourragement": "paturage"},
}

SEASONAL_BEHAVIOR = {
    "printemps": {"social": 0.7, "territorial": 0.5, "alim_activite": 0.8, "vigilance": 0.6},
    "ete":       {"social": 0.8, "territorial": 0.4, "alim_activite": 1.0, "vigilance": 0.5},
    "automne":   {"social": 0.9, "territorial": 0.9, "alim_activite": 0.9, "vigilance": 0.8},
    "hiver":     {"social": 1.0, "territorial": 0.2, "alim_activite": 0.4, "vigilance": 0.7},
}


def _compute_behavior_score(lat, lng, species, month):
    p = SPECIES_BEHAVIOR.get(species.upper(), SPECIES_BEHAVIOR["CERF"])
    season = get_season(month)
    s = SEASONAL_BEHAVIOR.get(season, SEASONAL_BEHAVIOR["automne"])

    dist_route = 20 + 480 * _seed(lat, lng, "behav_route")
    canopy = 0.2 + 0.7 * _seed(lat, lng, "behav_canopy")
    ouverture = 1.0 - canopy
    lisiere = _seed(lat, lng, "behav_lisiere") < 0.3
    nourriture = _seed(lat, lng, "behav_food")
    espace = _seed(lat, lng, "behav_espace")

    # SECURITE (0-25)
    fuite_ratio = min(1.0, dist_route / (p["dist_fuite_m"] * 2))
    securite = fuite_ratio * 15 + canopy * 10
    securite = min(25, securite)

    # SOCIAL (0-20)
    espace_ok = espace > (p["taille_groupe"] / 20)
    social = 10 * s["social"]
    if espace_ok:
        social += 5
    if ouverture > 0.3 and p["taille_groupe"] > 5:
        social += 5
    social = min(20, social)

    # ALIMENTATION (0-20)
    alimentation = nourriture * s["alim_activite"] * 15
    if lisiere:
        alimentation += 5
    alimentation = min(20, alimentation)

    # TERRITORIAL (0-20)
    territorial = p["territorial"] * s["territorial"] * 15
    if canopy > 0.4:
        territorial += 3
    if dist_route > 200:
        territorial += 2
    territorial = min(20, territorial)

    # VIGILANCE (0-15)
    vigilance = p["vigilance"] * s["vigilance"] * 8
    if lisiere or ouverture > 0.4:
        vigilance += 4
    if canopy > 0.5:
        vigilance += 3
    vigilance = min(15, vigilance)

    score = securite + social + alimentation + territorial + vigilance
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_behavior_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_behavior_score(lat, lng, species, month))
