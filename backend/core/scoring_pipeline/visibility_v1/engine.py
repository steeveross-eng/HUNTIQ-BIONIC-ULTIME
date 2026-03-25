"""
VISIBILITY ENGINE V1 — Scoring de visibilite / bassin visuel
================================================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Analyse de visibilite et de champ de vision.
Evalue la capacite d'observation et de detection depuis un point,
en tenant compte du relief, de la canopee et de la vegetation.

Facteurs de scoring (0-100):
  CHAMP_VISUEL (0-30)    Ouverture, obstacles visuels, relief
  COUVERT_APPROCHE (0-25) Capacite a approcher sans etre vu
  LISIERES (0-20)        Proximite et qualite des zones de transition
  ELEVATION (0-15)       Avantage topographique (cretes, replats)
  CONTRASTE (0-10)       Contraste lumineux, fond visuel

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "VISIBILITY-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.05

SPECIES_VISIBILITY = {
    "CERF":    {"besoin_couvert": 0.7, "pref_lisiere": 0.8, "sensibilite_visuelle": 0.6},
    "ORIGNAL": {"besoin_couvert": 0.5, "pref_lisiere": 0.6, "sensibilite_visuelle": 0.4},
    "OURS":    {"besoin_couvert": 0.8, "pref_lisiere": 0.5, "sensibilite_visuelle": 0.7},
    "DINDON":  {"besoin_couvert": 0.6, "pref_lisiere": 0.9, "sensibilite_visuelle": 0.8},
    "WAPITI":  {"besoin_couvert": 0.4, "pref_lisiere": 0.7, "sensibilite_visuelle": 0.5},
}

NDVI_MONTH = {
    1: 0.10, 2: 0.12, 3: 0.35, 4: 0.55, 5: 0.75, 6: 0.90,
    7: 1.00, 8: 0.95, 9: 0.80, 10: 0.60, 11: 0.30, 12: 0.15,
}


def _compute_visibility_score(lat, lng, species, month):
    p = SPECIES_VISIBILITY.get(species.upper(), SPECIES_VISIBILITY["CERF"])
    ndvi = NDVI_MONTH.get(month, 0.6)

    canopy = 0.2 + 0.7 * _seed(lat, lng, "vis_canopy")
    pente = _seed(lat, lng, "vis_pente") * 30
    crete = _seed(lat, lng, "vis_crete") < 0.15
    lisiere = _seed(lat, lng, "vis_lisiere") < 0.3
    ouverture = 1.0 - canopy * ndvi

    # CHAMP VISUEL (0-30)
    champ = ouverture * 20
    if crete:
        champ += 10
    champ = min(30, champ)

    # COUVERT APPROCHE (0-25)
    couvert = canopy * ndvi * p["besoin_couvert"] * 25
    couvert = min(25, couvert)

    # LISIERES (0-20)
    lisiere_score = 0
    if lisiere:
        lisiere_score = 15 * p["pref_lisiere"]
    if 0.3 < canopy < 0.7:
        lisiere_score += 5
    lisiere_score = min(20, lisiere_score)

    # ELEVATION (0-15)
    if crete:
        elevation = 15
    elif pente < 5:
        elevation = 5
    else:
        elevation = min(15, 5 + pente * 0.4)

    # CONTRASTE (0-10)
    contraste = (1.0 - p["sensibilite_visuelle"]) * 5 + (1.0 - ndvi) * 5
    contraste = min(10, contraste)

    score = champ + couvert + lisiere_score + elevation + contraste
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_visibility_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_visibility_score(lat, lng, species, month))
