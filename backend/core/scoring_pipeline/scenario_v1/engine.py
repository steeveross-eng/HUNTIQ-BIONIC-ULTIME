"""
SCENARIO ENGINE V1 — Moteur de planification de scenarios
=============================================================
Directive x4000-SUPRA PHASE 3 (BIONIC OS)
Domaine: Analyse what-if et planification de scenarios.
Evalue l'impact de modifications hypothetiques du territoire
(coupe forestiere, restauration, nouvelle route, saline artificielle)
sur le score ecologique du site.

Scenarios supportes:
  COUPE_FORESTIERE   Reduction canopy et perturbation
  RESTAURATION       Augmentation couvert et regeneration
  NOUVELLE_ROUTE     Ajout perturbation lineaire
  SALINE             Ajout attracteur mineral
  STATU_QUO          Etat actuel (reference)

Sortie:
  score_statu_quo: Score actuel
  scenarios: {nom: score_projete, delta, impact}
  meilleur_scenario: Scenario avec le delta le plus positif

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "SCENARIO-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.03

SCENARIOS = {
    "STATU_QUO": {"canopy_delta": 0, "route_delta": 0, "mineral_delta": 0, "regen_delta": 0},
    "COUPE_FORESTIERE": {"canopy_delta": -0.35, "route_delta": 0.1, "mineral_delta": 0, "regen_delta": -0.2},
    "RESTAURATION": {"canopy_delta": 0.15, "route_delta": -0.05, "mineral_delta": 0, "regen_delta": 0.3},
    "NOUVELLE_ROUTE": {"canopy_delta": -0.05, "route_delta": 0.4, "mineral_delta": 0, "regen_delta": -0.05},
    "SALINE": {"canopy_delta": 0, "route_delta": 0.05, "mineral_delta": 0.5, "regen_delta": 0},
}

SPECIES_SENSITIVITY = {
    "CERF":    {"canopy": 0.6, "route": 0.8, "mineral": 0.7, "regen": 0.5},
    "ORIGNAL": {"canopy": 0.5, "route": 0.9, "mineral": 0.6, "regen": 0.7},
    "OURS":    {"canopy": 0.7, "route": 0.7, "mineral": 0.3, "regen": 0.4},
    "DINDON":  {"canopy": 0.5, "route": 0.5, "mineral": 0.2, "regen": 0.3},
    "WAPITI":  {"canopy": 0.4, "route": 0.8, "mineral": 0.8, "regen": 0.6},
}


def _base_score(lat, lng, species, month):
    canopy = 0.2 + 0.7 * _seed(lat, lng, "scen_canopy")
    dist_route = 20 + 480 * _seed(lat, lng, "scen_route")
    mineral = _seed(lat, lng, "scen_mineral")
    regen = _seed(lat, lng, "scen_regen")
    eau = _seed(lat, lng, "scen_eau") < 0.3
    calme = _seed(lat, lng, "scen_calme")

    base = canopy * 25 + min(1.0, dist_route / 500) * 25 + calme * 20
    base += regen * 15 + (10 if eau else 5) + mineral * 5
    return max(0, min(100, base)), canopy, dist_route, mineral, regen


def _apply_scenario(base, canopy, dist_route, mineral, regen, scenario, sensitivity):
    s = SCENARIOS[scenario]
    delta = 0
    new_canopy = max(0, min(1, canopy + s["canopy_delta"]))
    delta += (new_canopy - canopy) * 25 * sensitivity["canopy"]

    route_factor = s["route_delta"]
    delta -= route_factor * 25 * sensitivity["route"]

    delta += s["mineral_delta"] * 10 * sensitivity["mineral"]
    delta += s["regen_delta"] * 15 * sensitivity["regen"]

    projected = max(0, min(100, base + delta))
    return round(projected, 1), round(projected - base, 1)


def analyze_point(lat, lng, species="CERF", month=10):
    sens = SPECIES_SENSITIVITY.get(species.upper(), SPECIES_SENSITIVITY["CERF"])
    base, canopy, dist_route, mineral, regen = _base_score(lat, lng, species, month)
    base_r = round(base, 1)

    results = {}
    best_name, best_delta = "STATU_QUO", 0
    for name in SCENARIOS:
        projected, delta = _apply_scenario(base, canopy, dist_route, mineral, regen, name, sens)
        impact = "positif" if delta > 1 else ("negatif" if delta < -1 else "neutre")
        results[name] = {"score_projete": projected, "delta": delta, "impact": impact}
        if delta > best_delta:
            best_name, best_delta = name, delta

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": base_r,
        "species": species.upper(), "month": month, "season": get_season(month),
        "score_statu_quo": base_r,
        "scenarios": results,
        "meilleur_scenario": best_name,
        "meilleur_delta": best_delta,
    }


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    base, *_ = _base_score(lat, lng, species, month)
    return float(round(base, 1))
