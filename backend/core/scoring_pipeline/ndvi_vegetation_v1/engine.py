"""
NDVI / VEGETATION ENGINE V1 — Scoring vegetatif
===================================================
Directive x4000-SUPRA PHASE 1 (CORE++)
Domaine: Qualite et diversite de la vegetation.
Analyse le NDVI saisonnier, la diversite des essences, la structure
verticale, la phenologie et la productivite du couvert vegetal.

Facteurs de scoring (0-100):
  NDVI_QUALITE (0-25)    Indice de vegetation normalise saisonnier
  DIVERSITE (0-25)       Nombre et repartition des essences
  STRUCTURE (0-20)       Strates verticales (sol, arbustive, canopee)
  PHENOLOGIE (0-15)      Phase phenologique (bourgeonnement, maturite, senescence)
  PRODUCTIVITE (0-15)    Biomasse disponible, regeneration

BCE-4X: NON integre dans score_consolide (Option A)
"""
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed
from core.scoring_pipeline.common.seasons import get_season
from core.scoring_pipeline.common.constants import NDVI_SEASONAL_MULTIPLIERS

ENGINE_NAME = "NDVI-VEGETATION-V1"
ENGINE_VERSION = "1.0.0"
ENGINE_WEIGHT_PROPOSED = 0.07

SPECIES_VEGETATION = {
    "CERF":    {"pref_feuillus": 0.7, "pref_regeneration": 0.8, "besoin_strate_basse": 0.7},
    "ORIGNAL": {"pref_feuillus": 0.6, "pref_regeneration": 0.9, "besoin_strate_basse": 0.8},
    "OURS":    {"pref_feuillus": 0.8, "pref_regeneration": 0.5, "besoin_strate_basse": 0.6},
    "DINDON":  {"pref_feuillus": 0.9, "pref_regeneration": 0.4, "besoin_strate_basse": 0.5},
    "WAPITI":  {"pref_feuillus": 0.5, "pref_regeneration": 0.7, "besoin_strate_basse": 0.9},
}

PHENOLOGIE = {
    "printemps": {"phase": "bourgeonnement", "productivite": 0.6, "diversite_bonus": 0.3},
    "ete":       {"phase": "maturite",       "productivite": 1.0, "diversite_bonus": 0.5},
    "automne":   {"phase": "senescence",     "productivite": 0.7, "diversite_bonus": 0.4},
    "hiver":     {"phase": "dormance",       "productivite": 0.15, "diversite_bonus": 0.1},
}


def _compute_vegetation_score(lat, lng, species, month):
    p = SPECIES_VEGETATION.get(species.upper(), SPECIES_VEGETATION["CERF"])
    season = get_season(month)
    pheno = PHENOLOGIE.get(season, PHENOLOGIE["automne"])
    ndvi_mult = NDVI_SEASONAL_MULTIPLIERS.get(month, 0.6)

    ndvi_brut = 0.3 + 0.6 * _seed(lat, lng, "veg_ndvi")
    ndvi = ndvi_brut * ndvi_mult
    n_essences = max(1, int(_seed(lat, lng, "veg_ess") * 8))
    feuillus_pct = _seed(lat, lng, "veg_feuil")
    strate_basse = _seed(lat, lng, "veg_strate") * 0.8
    regeneration = _seed(lat, lng, "veg_regen")

    # NDVI QUALITE (0-25)
    ndvi_score = ndvi * 25

    # DIVERSITE (0-25)
    diversite = min(25, n_essences * 3 + feuillus_pct * p["pref_feuillus"] * 5 + pheno["diversite_bonus"] * 5)

    # STRUCTURE (0-20)
    structure = strate_basse * p["besoin_strate_basse"] * 10
    if ndvi > 0.5:
        structure += 5
    if n_essences >= 4:
        structure += 5
    structure = min(20, structure)

    # PHENOLOGIE (0-15)
    phenologie_score = pheno["productivite"] * 15

    # PRODUCTIVITE (0-15)
    productivite = regeneration * p["pref_regeneration"] * 8 + ndvi * pheno["productivite"] * 7
    productivite = min(15, productivite)

    score = ndvi_score + diversite + structure + phenologie_score + productivite
    return max(0, min(100, round(score, 1)))


def analyze_point(lat, lng, species="CERF", month=10):
    score = _compute_vegetation_score(lat, lng, species, month)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "score": score, "species": species.upper(), "month": month,
            "season": get_season(month)}


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    return float(_compute_vegetation_score(lat, lng, species, month))
