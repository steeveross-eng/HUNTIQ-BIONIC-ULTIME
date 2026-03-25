"""
LEARNING ENGINE V1 — Moteur d'apprentissage adaptatif
=========================================================
Directive x4000-SUPRA PHASE 3 (BIONIC OS)
Domaine: Apprentissage a partir de patrons historiques.
Analyse les tendances, la frequentation passee estimee,
la fiabilite des predictions et la convergence des modeles.

Facteurs de scoring (0-100):
  TENDANCE (0-25)      Direction des patrons (amelioration/degradation)
  FREQUENTATION (0-25)  Historique de frequentation estime
  FIABILITE (0-20)     Confiance dans les predictions du pipeline
  CONVERGENCE (0-15)   Accord entre les moteurs CORE
  ADAPTATION (0-15)    Vitesse d'adaptation aux changements

BCE-4X: NON integre dans score_consolide (Option A)
NOTE: Ce moteur simule l'apprentissage de maniere deterministe.
Les donnees historiques sont generees algorithmiquement.
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "LEARNING-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.03


def _compute_learning_score(lat, lng, species, month):
    base_quality = _seed(lat, lng, f"learn_base_{species}")
    trend = (_seed(lat, lng, f"learn_trend_{month}") - 0.4) * 2
    n_obs = max(1, int(_seed(lat, lng, "learn_obs") * 50))
    consistency = 0.5 + 0.4 * _seed(lat, lng, "learn_consist")
    change_rate = _seed(lat, lng, "learn_change")

    tendance = min(25, 12 + trend * 10 + base_quality * 3)
    frequentation = min(25, n_obs * 0.5 + base_quality * 10)
    fiabilite = min(20, consistency * 15 + (5 if n_obs > 20 else 0))
    convergence = min(15, consistency * 12 + (3 if trend > 0 else 0))
    adaptation = min(15, (1.0 - change_rate) * 8 + consistency * 5 + 2)

    score = tendance + frequentation + fiabilite + convergence + adaptation
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": _compute_learning_score(lat, lng, species, month),
            "species": species.upper(), "month": month, "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_learning_score(lat, lng, species, month))
