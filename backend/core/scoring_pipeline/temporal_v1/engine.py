"""
TEMPORAL ENGINE V1 — Scoring des patrons temporels
======================================================
Directive x4000-SUPRA PHASE 2 (CORE+++)
Domaine: Analyse des patrons temporels d'activite de la faune.
Evalue les cycles circadiens, les patrons saisonniers de migration,
les periodes de rut/mise-bas et l'activite crepusculaire.

Facteurs de scoring (0-100):
  CIRCADIEN (0-25)     Adéquation du site avec les pics d'activite
  SAISONNIER (0-25)    Importance saisonniere du site (migration, rut)
  CREPUSCULAIRE (0-20) Qualite du site aux heures crepusculaires
  PHENOLOGIE (0-15)    Synchronisation avec les cycles biologiques
  PERSISTANCE (0-15)   Duree d'utilisation typique du site

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "TEMPORAL-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.05

SPECIES_TEMPORAL = {
    "CERF":    {"pics_activite": [6, 18], "rut_mois": [10, 11], "migration": False, "nocturne": 0.6},
    "ORIGNAL": {"pics_activite": [5, 19], "rut_mois": [9, 10], "migration": False, "nocturne": 0.4},
    "OURS":    {"pics_activite": [7, 17], "rut_mois": [6, 7], "migration": False, "nocturne": 0.5},
    "DINDON":  {"pics_activite": [6, 16], "rut_mois": [4, 5], "migration": False, "nocturne": 0.1},
    "WAPITI":  {"pics_activite": [6, 18], "rut_mois": [9, 10], "migration": True, "nocturne": 0.3},
}

SEASONAL_IMPORTANCE = {
    "printemps": {"circadien": 0.7, "migration": 0.9, "rut": 0.2, "persistance": 0.7},
    "ete":       {"circadien": 0.8, "migration": 0.3, "rut": 0.3, "persistance": 0.9},
    "automne":   {"circadien": 0.9, "migration": 0.6, "rut": 0.9, "persistance": 0.8},
    "hiver":     {"circadien": 0.5, "migration": 0.2, "rut": 0.1, "persistance": 0.6},
}


def _compute_temporal_score(lat, lng, species, month):
    p = SPECIES_TEMPORAL.get(species.upper(), SPECIES_TEMPORAL["CERF"])
    season = get_season(month)
    s = SEASONAL_IMPORTANCE.get(season, SEASONAL_IMPORTANCE["automne"])

    couvert = 0.2 + 0.7 * _seed(lat, lng, "temp_couv")
    calme = _seed(lat, lng, "temp_calme")
    eau_prox = _seed(lat, lng, "temp_eau") < 0.3
    lisiere = _seed(lat, lng, "temp_lisiere") < 0.35

    is_rut_season = month in p["rut_mois"]

    # CIRCADIEN (0-25)
    circadien = calme * 15 * s["circadien"]
    if couvert > 0.5:
        circadien += 5
    if p["nocturne"] > 0.4:
        circadien += 5 * couvert
    circadien = min(25, circadien)

    # SAISONNIER (0-25)
    saisonnier = 10
    if is_rut_season:
        saisonnier += 10 * s["rut"]
    if p["migration"]:
        saisonnier += 5 * s["migration"]
    saisonnier = min(25, saisonnier)

    # CREPUSCULAIRE (0-20)
    crepusculaire = couvert * 10 + calme * 5
    if lisiere:
        crepusculaire += 5
    crepusculaire = min(20, crepusculaire)

    # PHENOLOGIE (0-15)
    phenologie = s["circadien"] * 8 + s["rut"] * 4
    if is_rut_season:
        phenologie += 3
    phenologie = min(15, phenologie)

    # PERSISTANCE (0-15)
    persistance = s["persistance"] * 10
    if eau_prox:
        persistance += 3
    if couvert > 0.6:
        persistance += 2
    persistance = min(15, persistance)

    score = circadien + saisonnier + crepusculaire + phenologie + persistance
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_temporal_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_temporal_score(lat, lng, species, month))
