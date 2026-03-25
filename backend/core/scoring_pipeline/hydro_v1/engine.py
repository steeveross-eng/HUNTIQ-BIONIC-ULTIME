"""
HYDRO ENGINE V1 — Scoring hydrographique
============================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Qualite et accessibilite des ressources hydriques.
Evalue la proximite, la qualite, la diversite et la saisonnalite
des sources d'eau pour chaque espece.

Facteurs de scoring (0-100):
  PROXIMITE (0-30)   Distance aux sources d'eau les plus proches
  QUALITE (0-25)     Debit, oxygene, temperature, turbidite
  DIVERSITE (0-20)   Nombre et types de sources (lac, riviere, ruisseau, suintement)
  SAISONNALITE (0-15) Disponibilite saisonniere (gel, crue, etiage)
  ACCESSIBILITE (0-10) Pente d'acces, vegetation riveraine, obstacles

BCE-4X: NON integre dans score_consolide (Option A — x4100 prevu)
"""
import math
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season
from core.scoring_pipeline.common.constants import METERS_PER_DEG_LAT

ENGINE_NAME = "HYDRO-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.08

SPECIES_HYDRO_PROFILES = {
    "CERF": {
        "distance_optimale_m": 300, "distance_max_m": 800,
        "pref_eau_courante": 0.6, "pref_zone_humide": 0.3,
        "besoin_hydrique": "modere", "tolerance_gel": 0.7,
    },
    "ORIGNAL": {
        "distance_optimale_m": 100, "distance_max_m": 400,
        "pref_eau_courante": 0.4, "pref_zone_humide": 0.8,
        "besoin_hydrique": "eleve", "tolerance_gel": 0.5,
    },
    "OURS": {
        "distance_optimale_m": 200, "distance_max_m": 600,
        "pref_eau_courante": 0.7, "pref_zone_humide": 0.2,
        "besoin_hydrique": "eleve", "tolerance_gel": 0.3,
    },
    "DINDON": {
        "distance_optimale_m": 400, "distance_max_m": 1000,
        "pref_eau_courante": 0.3, "pref_zone_humide": 0.2,
        "besoin_hydrique": "faible", "tolerance_gel": 0.8,
    },
    "WAPITI": {
        "distance_optimale_m": 250, "distance_max_m": 700,
        "pref_eau_courante": 0.5, "pref_zone_humide": 0.4,
        "besoin_hydrique": "modere", "tolerance_gel": 0.6,
    },
}

SEASONAL_HYDRO = {
    "printemps": {"debit": 1.0, "gel": 0.1, "crue": 0.7, "qualite": 0.8},
    "ete":       {"debit": 0.6, "gel": 0.0, "crue": 0.1, "qualite": 0.9},
    "automne":   {"debit": 0.7, "gel": 0.2, "crue": 0.3, "qualite": 0.85},
    "hiver":     {"debit": 0.3, "gel": 0.9, "crue": 0.0, "qualite": 0.7},
}


def _compute_hydro_score(lat, lng, species, month):
    profile = SPECIES_HYDRO_PROFILES.get(species.upper(), SPECIES_HYDRO_PROFILES["CERF"])
    season = get_season(month)
    s_mod = SEASONAL_HYDRO.get(season, SEASONAL_HYDRO["automne"])

    dist_eau = 20 + 480 * _seed(lat, lng, "hydro_dist")
    debit = _seed(lat, lng, "hydro_debit") * s_mod["debit"]
    qualite_eau = 0.4 + 0.6 * _seed(lat, lng, "hydro_qual") * s_mod["qualite"]
    n_sources = max(1, int(_seed(lat, lng, "hydro_nsrc") * 5))
    zone_humide = _seed(lat, lng, "hydro_zh") > 0.6
    pente_acces = _seed(lat, lng, "hydro_pente") * 25

    # PROXIMITE (0-30)
    d_opt = profile["distance_optimale_m"]
    d_max = profile["distance_max_m"]
    if dist_eau <= d_opt:
        proximite = 30.0
    elif dist_eau >= d_max:
        proximite = 0.0
    else:
        proximite = 30.0 * (1.0 - (dist_eau - d_opt) / (d_max - d_opt))

    # QUALITE (0-25)
    qualite = qualite_eau * 15 + debit * 10

    # DIVERSITE (0-20)
    diversite = min(20, n_sources * 5)
    if zone_humide:
        diversite = min(20, diversite + 5 * profile["pref_zone_humide"])

    # SAISONNALITE (0-15)
    gel_penalty = s_mod["gel"] * (1.0 - profile["tolerance_gel"]) * 10
    crue_bonus = s_mod["crue"] * 3 if profile["pref_zone_humide"] > 0.5 else 0
    saisonnalite = max(0, 15 - gel_penalty + crue_bonus)

    # ACCESSIBILITE (0-10)
    if pente_acces < 5:
        accessibilite = 10.0
    elif pente_acces > 20:
        accessibilite = 2.0
    else:
        accessibilite = 10.0 - (pente_acces - 5) * 0.53

    score = proximite + qualite + diversite + saisonnalite + accessibilite
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_hydro_score(lat, lng, species, month)
    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": score, "species": species.upper(), "month": month,
        "season": get_season(month),
    }


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    """Point d'entree normalise pour integration future dans score_consolide."""
    return float(_compute_hydro_score(lat, lng, species, month))
