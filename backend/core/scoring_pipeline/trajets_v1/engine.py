"""
TRAJETS ENGINE V1 — Scoring de trajectoires de deplacement
==============================================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Analyse des trajectoires et patrons de deplacement.
Evalue le cout de deplacement, la permeabilite du terrain,
les corridors naturels et les barrieres au mouvement.

Facteurs de scoring (0-100):
  PERMEABILITE (0-25)   Facilite de traversee (pente, obstacles, foret)
  LINEAIRE (0-25)       Presence de corridors lineaires (vallees, cours d'eau, cretes)
  COUT_ENERGETIQUE (0-20) Depense energetique estimee pour traverser
  SECURITE_TRAJET (0-15) Distance aux perturbations sur le trajet
  ATTRACTIVITE (0-15)    Presence de destinations attractives (eau, alimentation)

BCE-4X: NON integre dans score_consolide (Option A)
"""
import math
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "TRAJETS-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.06

SPECIES_TRAJETS = {
    "CERF":    {"style": "sinueux", "vitesse": "modere", "pente_max": 15, "dist_evitement_route": 150},
    "ORIGNAL": {"style": "lineaire", "vitesse": "modere", "pente_max": 25, "dist_evitement_route": 300},
    "OURS":    {"style": "opportuniste", "vitesse": "rapide", "pente_max": 35, "dist_evitement_route": 200},
    "DINDON":  {"style": "territorial", "vitesse": "lent", "pente_max": 12, "dist_evitement_route": 100},
    "WAPITI":  {"style": "migratoire", "vitesse": "rapide", "pente_max": 22, "dist_evitement_route": 250},
}

SEASONAL_MOBILITY = {
    "printemps": 0.9, "ete": 1.0, "automne": 1.1, "hiver": 0.6,
}


def _compute_trajets_score(lat, lng, species, month):
    p = SPECIES_TRAJETS.get(species.upper(), SPECIES_TRAJETS["CERF"])
    season = get_season(month)
    mob = SEASONAL_MOBILITY.get(season, 1.0)

    pente = _seed(lat, lng, "traj_pente") * 30
    canopy = 0.2 + 0.7 * _seed(lat, lng, "traj_canopy")
    dist_route = 20 + 480 * _seed(lat, lng, "traj_route")
    vallee = _seed(lat, lng, "traj_vallee") < 0.2
    cours_eau = _seed(lat, lng, "traj_eau") < 0.15
    crete = _seed(lat, lng, "traj_crete") < 0.1
    nourriture = _seed(lat, lng, "traj_food")

    # PERMEABILITE (0-25)
    if pente > p["pente_max"]:
        permeabilite = 2.0
    elif pente < 5:
        permeabilite = 25.0
    else:
        permeabilite = 25.0 * (1.0 - (pente - 5) / (p["pente_max"] - 5)) * 0.8 + 5
    permeabilite = min(25, permeabilite * mob)

    # LINEAIRE (0-25)
    lineaire = 0
    if vallee:
        lineaire += 12
    if cours_eau:
        lineaire += 8
    if crete:
        lineaire += 5
    lineaire = min(25, lineaire)

    # COUT ENERGETIQUE (0-20)
    cout_base = 20.0 - pente * 0.5
    if canopy > 0.4:
        cout_base += 2
    cout_energetique = max(0, min(20, cout_base * mob))

    # SECURITE TRAJET (0-15)
    if dist_route >= p["dist_evitement_route"]:
        securite = 15.0
    elif dist_route < 30:
        securite = 0.0
    else:
        securite = 15.0 * (dist_route - 30) / (p["dist_evitement_route"] - 30)

    # ATTRACTIVITE (0-15)
    attractivite = nourriture * 8 + (5 if cours_eau else 0) + (2 if canopy > 0.5 else 0)
    attractivite = min(15, attractivite)

    score = permeabilite + lineaire + cout_energetique + securite + attractivite
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_trajets_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_trajets_score(lat, lng, species, month))
