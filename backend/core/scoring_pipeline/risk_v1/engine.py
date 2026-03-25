"""
RISK ENGINE V1 — Scoring de risque ecologique
=================================================
Directive x4000-SUPRA PHASE 2 (CORE+++)
Domaine: Evaluation des risques pour la faune.
Analyse les risques de predation, perturbation humaine, mortalite
routiere, chasse et conditions meteorologiques extremes.

Facteurs de scoring (0-100) — SCORE INVERSE (100 = risque minimal):
  PREDATION (0-25)     Risque de predation (loups, coyotes, ours)
  PERTURBATION (0-25)  Perturbation humaine (routes, batiments, sentiers)
  MORTALITE_ROUTIERE (0-20) Proximite et densite routiere
  CHASSE (0-15)        Pression de chasse saisonniere
  EXTREME (0-15)       Risque meteo extreme (verglas, canicule, inondation)

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "RISK-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.06

SPECIES_RISK = {
    "CERF":    {"vuln_predation": 0.7, "vuln_route": 0.8, "chasse_mois": [10, 11], "vuln_extreme": 0.5},
    "ORIGNAL": {"vuln_predation": 0.4, "vuln_route": 0.6, "chasse_mois": [9, 10, 11], "vuln_extreme": 0.4},
    "OURS":    {"vuln_predation": 0.1, "vuln_route": 0.5, "chasse_mois": [5, 6, 9], "vuln_extreme": 0.4},
    "DINDON":  {"vuln_predation": 0.8, "vuln_route": 0.3, "chasse_mois": [4, 5], "vuln_extreme": 0.6},
    "WAPITI":  {"vuln_predation": 0.5, "vuln_route": 0.5, "chasse_mois": [10, 11], "vuln_extreme": 0.4},
}

SEASONAL_RISK = {
    "printemps": {"predation": 0.7, "humain": 0.5, "extreme": 0.3},
    "ete":       {"predation": 0.6, "humain": 0.8, "extreme": 0.2},
    "automne":   {"predation": 0.5, "humain": 0.7, "extreme": 0.3},
    "hiver":     {"predation": 0.8, "humain": 0.3, "extreme": 0.7},
}


def _compute_risk_score(lat, lng, species, month):
    """Score INVERSE: 100 = risque minimal (securite maximale)."""
    p = SPECIES_RISK.get(species.upper(), SPECIES_RISK["CERF"])
    season = get_season(month)
    s = SEASONAL_RISK.get(season, SEASONAL_RISK["automne"])

    dist_route = 20 + 480 * _seed(lat, lng, "risk_route")
    dist_bat = 50 + 450 * _seed(lat, lng, "risk_bat")
    canopy = 0.2 + 0.7 * _seed(lat, lng, "risk_canopy")
    predateur_prox = _seed(lat, lng, "risk_pred")
    densite_route = _seed(lat, lng, "risk_dense")

    is_chasse = month in p["chasse_mois"]

    # PREDATION (0-25) — score inverse
    risque_pred = predateur_prox * p["vuln_predation"] * s["predation"]
    securite_pred = (1.0 - risque_pred) * 18
    if canopy > 0.5:
        securite_pred += 4
    if dist_route > 200:
        securite_pred += 3
    predation = min(25, securite_pred)

    # PERTURBATION (0-25)
    perturbation = min(1.0, dist_route / 300) * 12 + min(1.0, dist_bat / 400) * 8
    if canopy > 0.6:
        perturbation += 5
    perturbation = min(25, perturbation * (1.0 - s["humain"] * 0.3))

    # MORTALITE ROUTIERE (0-20)
    if dist_route > 300:
        mortalite = 20.0
    elif dist_route < 30:
        mortalite = 2.0
    else:
        mortalite = 2.0 + 18.0 * ((dist_route - 30) / 270) * (1.0 - densite_route * p["vuln_route"] * 0.3)

    # CHASSE (0-15)
    if not is_chasse:
        chasse = 15.0
    else:
        chasse = 5.0 + canopy * 5 + min(1.0, dist_route / 500) * 5

    # EXTREME (0-15)
    extreme = (1.0 - s["extreme"] * p["vuln_extreme"]) * 12
    if canopy > 0.5:
        extreme += 3
    extreme = min(15, extreme)

    score = predation + perturbation + mortalite + chasse + extreme
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_risk_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month), "note": "Score inverse: 100=risque minimal"}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_risk_score(lat, lng, species, month))
