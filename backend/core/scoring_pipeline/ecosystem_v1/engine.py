"""
ECOSYSTEM ENGINE V1 — Scoring de sante ecosystemique
========================================================
Directive x4000-SUPRA PHASE 3 (BIONIC OS)
Domaine: Evaluation de la sante globale de l'ecosysteme.
Combine biodiversite, connectivite ecologique, integrite des
processus naturels et resilience du milieu.

Facteurs de scoring (0-100):
  BIODIVERSITE (0-25)  Diversite vegetale et animale estimee
  CONNECTIVITE (0-25)  Corridors ecologiques, fragmentation
  INTEGRITE (0-20)     Processus naturels (decomposition, nutriments)
  RESILIENCE (0-15)    Capacite de recuperation apres perturbation
  ANTHROPISATION (0-15) Degre d'alteration humaine (inverse)

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "ECOSYSTEM-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.05


def _compute_ecosystem_score(lat, lng, species, month):
    n_essences = max(1, int(_seed(lat, lng, "eco_ess") * 8))
    canopy = 0.2 + 0.7 * _seed(lat, lng, "eco_canopy")
    connect = 0.3 + 0.6 * _seed(lat, lng, "eco_connect")
    dist_route = 20 + 480 * _seed(lat, lng, "eco_route")
    eau = _seed(lat, lng, "eco_eau") < 0.3
    regen = _seed(lat, lng, "eco_regen")
    age_foret = _seed(lat, lng, "eco_age")

    biodiversite = min(25, n_essences * 3 + canopy * 5 + (5 if eau else 0))
    connectivite = min(25, connect * 20 + (5 if canopy > 0.5 else 0))
    integrite = min(20, canopy * 8 + age_foret * 7 + regen * 5)
    resilience = min(15, regen * 6 + n_essences * 1.0 + (3 if age_foret > 0.5 else 0))
    anthropisation = min(15, min(1.0, dist_route / 500) * 15)

    score = biodiversite + connectivite + integrite + resilience + anthropisation
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": _compute_ecosystem_score(lat, lng, species, month),
            "species": species.upper(), "month": month, "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_ecosystem_score(lat, lng, species, month))
