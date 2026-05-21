"""
MULTI-SPECIES ENGINE V1 — Moteur d'interaction multi-especes
================================================================
Directive x4000-SUPRA PHASE 3 (BIONIC OS)
Domaine: Analyse des interactions entre especes sur un site.
Evalue la competition, la cohabitation, la predation, le partage
temporel et la capacite de support multi-especes du milieu.

Facteurs de scoring (0-100):
  COHABITATION (0-25)    Compatibilite des especes presentes
  COMPETITION (0-20)     Pression competitive pour les ressources
  PARTAGE_TEMPOREL (0-20) Separation temporelle des activites
  CAPACITE (0-20)        Capacite de support du milieu pour N especes
  PREDATION (0-15)       Risque de predation inter-especes

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season
from core.scoring_pipeline.common.species import SPECIES_LIST

ENGINE_NAME = "MULTI-SPECIES-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.04

# Matrice de compatibilite inter-especes (0=incompatible, 1=parfait)
COMPATIBILITY_MATRIX = {
    ("CERF", "ORIGNAL"):  0.6,
    ("CERF", "OURS"):     0.3,
    ("CERF", "DINDON"):   0.8,
    ("CERF", "WAPITI"):   0.5,
    ("ORIGNAL", "OURS"):  0.4,
    ("ORIGNAL", "DINDON"): 0.7,
    ("ORIGNAL", "WAPITI"): 0.5,
    ("OURS", "DINDON"):   0.3,
    ("OURS", "WAPITI"):   0.4,
    ("DINDON", "WAPITI"):  0.7,
    # P22ΩΩ_ADD_COYOTE_TO_MULTI_SPECIES_Ω (2026-05-21 · STEEVE-MAX)
    # Coyote prédateur : compatibilité faible avec ongulés (prédation faons),
    # incompatibilité forte avec gibier à plumes (dindon), neutralité avec ours.
    ("COYOTE", "CERF"):    0.25,   # prédation faons + pression chronique
    ("COYOTE", "ORIGNAL"): 0.30,   # rare prédation veaux nouveau-nés
    ("COYOTE", "OURS"):    0.40,   # cohabitation neutre (compétition charogne)
    ("COYOTE", "DINDON"):  0.15,   # prédation directe poussins + adultes
    ("COYOTE", "WAPITI"):  0.30,   # prédation faons
}

# Competition pour les ressources (0=pas de competition, 1=forte)
COMPETITION_MATRIX = {
    ("CERF", "ORIGNAL"):  0.4,
    ("CERF", "WAPITI"):   0.7,
    ("ORIGNAL", "WAPITI"): 0.5,
    ("OURS", "CERF"):     0.2,
    ("DINDON", "CERF"):   0.1,
    # P22ΩΩ_ADD_COYOTE_TO_MULTI_SPECIES_Ω
    # Coyote : compétition charogne avec ours (modérée), micromammifères
    # nuls avec ongulés (pas de chevauchement régime).
    ("COYOTE", "OURS"):    0.50,   # charogne grosse partagée
    ("COYOTE", "CERF"):    0.10,   # régimes disjoints (prédation ≠ compétition)
    ("COYOTE", "ORIGNAL"): 0.05,
    ("COYOTE", "DINDON"):  0.20,   # micromammifères / petits gibiers partagés
}

SPECIES_CAPACITY = {
    "CERF": 8, "ORIGNAL": 2, "OURS": 1, "DINDON": 15, "WAPITI": 5,
    # P22ΩΩ_ADD_COYOTE_TO_MULTI_SPECIES_Ω : meutes ~5-7 ind. / 100 km²
    "COYOTE": 7,
}

SEASONAL_INTERACTION = {
    "printemps": {"competition": 0.6, "partage": 0.7, "predation": 0.5},
    "ete":       {"competition": 0.5, "partage": 0.8, "predation": 0.4},
    "automne":   {"competition": 0.8, "partage": 0.6, "predation": 0.6},
    "hiver":     {"competition": 0.9, "partage": 0.5, "predation": 0.7},
}


def _get_compatibility(sp1, sp2):
    key = (sp1, sp2) if (sp1, sp2) in COMPATIBILITY_MATRIX else (sp2, sp1)
    return COMPATIBILITY_MATRIX.get(key, 0.5)


def _get_competition(sp1, sp2):
    key = (sp1, sp2) if (sp1, sp2) in COMPETITION_MATRIX else (sp2, sp1)
    return COMPETITION_MATRIX.get(key, 0.2)


def _compute_multi_species_score(lat, lng, species, month):
    season = get_season(month)
    s = SEASONAL_INTERACTION.get(season, SEASONAL_INTERACTION["automne"])

    canopy = 0.2 + 0.7 * _seed(lat, lng, "multi_canopy")
    eau = _seed(lat, lng, "multi_eau") < 0.3
    nourriture = _seed(lat, lng, "multi_food")
    espace = _seed(lat, lng, "multi_espace")
    diversite_hab = max(1, int(_seed(lat, lng, "multi_div") * 5))

    other_species = [sp for sp in SPECIES_LIST if sp != species.upper()]

    # COHABITATION (0-25)
    avg_compat = sum(_get_compatibility(species.upper(), sp) for sp in other_species) / max(1, len(other_species))
    cohabitation = min(25, avg_compat * 20 + diversite_hab * 1.5)

    # COMPETITION (0-20) — score inverse (20 = pas de competition)
    avg_comp = sum(_get_competition(species.upper(), sp) for sp in other_species) / max(1, len(other_species))
    competition = min(20, (1.0 - avg_comp * s["competition"]) * 15 + nourriture * 5)

    # PARTAGE TEMPOREL (0-20)
    partage = s["partage"] * 12 + canopy * 4
    if diversite_hab >= 3:
        partage += 4
    partage = min(20, partage)

    # CAPACITE (0-20)
    cap = SPECIES_CAPACITY.get(species.upper(), 5)
    capacite = min(20, espace * cap * 1.5 + nourriture * 5 + (3 if eau else 0))

    # PREDATION (0-15) — score inverse (15 = pas de risque)
    pred_risk = 0
    if species.upper() in ("CERF", "DINDON", "WAPITI"):
        if "OURS" in other_species:
            pred_risk += 0.3
    predation = min(15, (1.0 - pred_risk * s["predation"]) * 12 + canopy * 3)

    score = cohabitation + competition + partage + capacite + predation
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_multi_species_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def analyze_multi(lat, lng, month=10):
    """Analyse pour les 5 especes simultanement."""
    results = {}
    for sp in SPECIES_LIST:
        results[sp] = _compute_multi_species_score(lat, lng, sp, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "month": month, "season": get_season(month),
            "scores": results, "best_species": max(results, key=results.get)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_multi_species_score(lat, lng, species, month))
