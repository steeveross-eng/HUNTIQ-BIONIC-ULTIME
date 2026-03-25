"""
HABITAT ENGINE V1 — Scoring de qualite d'habitat
====================================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Qualite globale de l'habitat pour chaque espece.
Combine structure forestiere, diversite, effets de bordure,
connectivite locale et capacite de support du milieu.

Facteurs de scoring (0-100):
  STRUCTURE (0-25)     Complexite structurale (strates, age, densite)
  HETEROGENEITE (0-25) Mosaique paysagere (nombre de patches, diversite)
  BORDURE (0-20)       Effets de lisiere (ratio perimetre/surface)
  CONNECTIVITE (0-15)  Continuite habitat, fragmentation
  CAPACITE (0-15)      Capacite de support (nourriture, eau, refuge)

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season

ENGINE_NAME = "HABITAT-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.08

SPECIES_HABITAT = {
    "CERF":    {"pref_mosaique": 0.8, "pref_lisiere": 0.9, "besoin_foret": 0.6, "domaine_vital_km2": 2.5},
    "ORIGNAL": {"pref_mosaique": 0.6, "pref_lisiere": 0.5, "besoin_foret": 0.7, "domaine_vital_km2": 15.0},
    "OURS":    {"pref_mosaique": 0.7, "pref_lisiere": 0.4, "besoin_foret": 0.8, "domaine_vital_km2": 50.0},
    "DINDON":  {"pref_mosaique": 0.9, "pref_lisiere": 0.8, "besoin_foret": 0.5, "domaine_vital_km2": 4.0},
    "WAPITI":  {"pref_mosaique": 0.7, "pref_lisiere": 0.7, "besoin_foret": 0.5, "domaine_vital_km2": 20.0},
}


def _compute_habitat_score(lat, lng, species, month):
    p = SPECIES_HABITAT.get(species.upper(), SPECIES_HABITAT["CERF"])

    canopy = 0.2 + 0.7 * _seed(lat, lng, "hab_canopy")
    n_patches = max(1, int(_seed(lat, lng, "hab_patch") * 8))
    diversite_ess = max(1, int(_seed(lat, lng, "hab_div") * 7))
    lisiere_prox = _seed(lat, lng, "hab_lisiere") < 0.35
    connectivite = 0.3 + 0.6 * _seed(lat, lng, "hab_connect")
    eau_prox = _seed(lat, lng, "hab_eau") < 0.3
    strate_count = max(1, int(_seed(lat, lng, "hab_strate") * 4))

    # STRUCTURE (0-25)
    structure = strate_count * 4 + canopy * 10 + (diversite_ess / 7) * 5
    structure = min(25, structure)

    # HETEROGENEITE (0-25)
    heterogeneite = n_patches * 2.5 * p["pref_mosaique"] + diversite_ess * 1.5
    heterogeneite = min(25, heterogeneite)

    # BORDURE (0-20)
    bordure = 0
    if lisiere_prox:
        bordure = 14 * p["pref_lisiere"]
    if 0.3 < canopy < 0.7:
        bordure += 6
    bordure = min(20, bordure)

    # CONNECTIVITE (0-15)
    conn_score = connectivite * 15
    conn_score = min(15, conn_score)

    # CAPACITE (0-15)
    capacite = canopy * p["besoin_foret"] * 7
    if eau_prox:
        capacite += 4
    capacite += (n_patches / 8) * 4
    capacite = min(15, capacite)

    score = structure + heterogeneite + bordure + conn_score + capacite
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_habitat_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_habitat_score(lat, lng, species, month))
