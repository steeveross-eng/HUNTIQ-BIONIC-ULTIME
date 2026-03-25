"""
SIMULATION ENGINE V1 — Moteur de simulation Monte Carlo
===========================================================
Directive x4000-SUPRA PHASE 3 (BIONIC OS)
Domaine: Simulation de scenarios ecologiques multiples.
Execute N iterations deterministiques pour estimer la distribution
des scores possibles sur un site, integrant la variabilite naturelle.

Sorties:
  score_median: Mediane des N simulations
  score_p10/p90: Percentiles 10% et 90%
  stabilite: Ecart-type normalise (0=instable, 100=stable)
  n_iterations: Nombre d'iterations executees

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "SIMULATION-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.03
DEFAULT_ITERATIONS = 25


def _simulate_single(lat, lng, species, month, iteration):
    """Une iteration de simulation avec variation deterministe."""
    seed_tag = f"sim_{species}_{month}_{iteration}"
    base = _seed(lat, lng, f"{seed_tag}_base") * 60 + 20
    variation = (_seed(lat, lng, f"{seed_tag}_var") - 0.5) * 30
    season_bonus = {"printemps": 5, "ete": 8, "automne": 10, "hiver": -5}
    bonus = season_bonus.get(get_season(month), 0)
    return max(0, min(100, base + variation + bonus))


def _compute_simulation_score(lat, lng, species, month, n_iter=DEFAULT_ITERATIONS):
    scores = sorted([_simulate_single(lat, lng, species, month, i) for i in range(n_iter)])
    n = len(scores)
    median = scores[n // 2]
    p10 = scores[max(0, int(n * 0.1))]
    p90 = scores[min(n - 1, int(n * 0.9))]
    avg = sum(scores) / n
    std = (sum((s - avg) ** 2 for s in scores) / n) ** 0.5
    stabilite = max(0, min(100, 100 - std * 3))
    return {
        "score_median": round(median, 1),
        "score_p10": round(p10, 1),
        "score_p90": round(p90, 1),
        "score_avg": round(avg, 1),
        "stabilite": round(stabilite, 1),
        "std": round(std, 2),
        "n_iterations": n_iter,
    }


def analyze_point(lat, lng, species="CERF", month=10, n_iter=DEFAULT_ITERATIONS):
    sim = _compute_simulation_score(lat, lng, species, month, n_iter)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": sim["score_median"],
            "species": species.upper(), "month": month,
            "season": get_season(month), **sim}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    sim = _compute_simulation_score(lat, lng, species, month)
    return float(sim["score_median"])
