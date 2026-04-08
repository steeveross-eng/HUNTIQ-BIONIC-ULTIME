"""
RSF ENGINE — Moteur principal Resource Selection Function
==========================================================
BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX
MS-2: Calcul du score RSF par espece avec 13 covariables.
Integre les 11 couches ecologiques (MS-3) et parametres comportementaux (MS-4).
"""
import math
from core.scoring_pipeline.common.hash import deterministic_hash_a as _h
from core.scoring_pipeline.rsf_engine.coefficients import (
    RSF_COEFFICIENTS,
    BREEDING_PERIODS,
    SPECIES_DISTURBANCE_TOLERANCE,
    SPECIES_WATER_DEPENDENCY,
    SPECIES_THERMAL_PREFERENCE,
    SPECIES_CIRCADIAN,
    SALINE_POSITIONING_PROFILES,
)


def _extract_covariables(lat, lng, species, month):
    """Extrait les 13 covariables d'habitat pour un point (lat, lng).
    Phase transitoire: simulation calibree par hash perlin ameliore.
    Phase finale: remplacement par donnees reelles (DEM, SIEF, etc.)."""
    seed_lat = round(lat * 1000) / 1000
    seed_lng = round(lng * 1000) / 1000
    base_elevation = 100 + 500 * _h(seed_lat, seed_lng, "dem_elev")
    base_pente = 35 * _h(seed_lat, seed_lng, "dem_pente")
    south_exposure = _h(seed_lat, seed_lng, "dem_expo")

    conifere_pct = _h(lat, lng, "eco_conifere")
    feuillu_pct = _h(lat, lng, "eco_feuillu")
    mixte_pct = max(0, 1.0 - conifere_pct - feuillu_pct)

    lisiere_dist = _h(lat, lng, "eco_lisiere") * 500
    friche_score = _h(lat, lng, "eco_friche")
    culture_dist = _h(lat, lng, "eco_culture") * 2000
    eau_dist = 20 + _h(lat, lng, "hydro_dist") * 500
    route_dist = 50 + _h(lat, lng, "infra_route") * 1000
    marecage_score = _h(lat, lng, "eco_marecage")

    routes_grid = _h(lat, lng, "infra_densite_route")
    route_density = routes_grid * 5.0

    return {
        "couvert_conifere": conifere_pct,
        "couvert_feuillu": feuillu_pct,
        "couvert_mixte": mixte_pct,
        "lisiere_100m": max(0, 1.0 - lisiere_dist / 100),
        "friche_regeneration": friche_score,
        "culture_proximite": max(0, 1.0 - culture_dist / 1000),
        "distance_eau_log": math.log(max(1, eau_dist)),
        "distance_route_log": math.log(max(1, route_dist)),
        "pente_deg": base_pente,
        "altitude_m": base_elevation,
        "densite_route_km2": route_density,
        "marecage": marecage_score,
        "exposition_sud": south_exposure,
    }


def _get_breeding_modifier(species, month):
    """Retourne un modificateur de mobilite/alimentation selon la periode reproductive."""
    sp = species.upper()
    periods = BREEDING_PERIODS.get(sp, {})
    for period_name, period_data in periods.items():
        if month in period_data.get("mois", []):
            return {
                "period": period_name,
                "mobilite": period_data.get("mobilite", 1.0),
                "alimentation": period_data.get("alimentation", 1.0),
            }
    return {"period": "normal", "mobilite": 1.0, "alimentation": 1.0}


def _apply_disturbance_penalty(base_score, lat, lng, species):
    """Applique une penalite selon la tolerance au derangement de l'espece."""
    sp = species.upper()
    tol = SPECIES_DISTURBANCE_TOLERANCE.get(sp, {"sensibilite": 0.7})
    route_dist = 50 + _h(lat, lng, "infra_route") * 1000
    buffer = tol.get("route_buffer_m", 200)
    if route_dist < buffer:
        penalty = tol["sensibilite"] * (1.0 - route_dist / buffer) * 30
        return max(0, base_score - penalty)
    return base_score


def _apply_water_bonus(base_score, lat, lng, species):
    """Applique un bonus/malus selon la dependance a l'eau de l'espece."""
    sp = species.upper()
    dep = SPECIES_WATER_DEPENDENCY.get(sp, {"affinite": 0.5, "distance_optimale_m": 200})
    eau_dist = 20 + _h(lat, lng, "hydro_dist") * 500
    dist_opt = dep["distance_optimale_m"]
    affinite = dep["affinite"]
    if eau_dist <= dist_opt:
        bonus = affinite * 15 * (1.0 - eau_dist / dist_opt)
    else:
        penalty_range = dist_opt * 3
        over = min(eau_dist - dist_opt, penalty_range)
        bonus = -affinite * 10 * (over / penalty_range)
    return max(0, min(100, base_score + bonus))


def compute_rsf_score(lat, lng, species="CERF", month=10):
    """Calcule le score RSF pour un point (lat, lng) et une espece donnee.
    Retourne un score 0-100."""
    sp = species.upper()
    coefficients = RSF_COEFFICIENTS.get(sp, RSF_COEFFICIENTS["CERF"])
    covariables = _extract_covariables(lat, lng, sp, month)

    linear_predictor = sum(
        coefficients.get(key, 0) * covariables.get(key, 0)
        for key in coefficients
    )

    rsf_raw = math.exp(max(-5, min(5, linear_predictor)))
    rsf_max = math.exp(5)
    rsf_normalized = (rsf_raw / rsf_max) * 100

    breeding = _get_breeding_modifier(sp, month)
    rsf_normalized *= breeding["mobilite"]

    rsf_normalized = _apply_disturbance_penalty(rsf_normalized, lat, lng, sp)
    rsf_normalized = _apply_water_bonus(rsf_normalized, lat, lng, sp)

    return max(0, min(100, round(rsf_normalized, 1)))


def compute_rsf_profile(lat, lng, species="CERF", month=10):
    """Retourne le profil RSF complet avec toutes les covariables et le score."""
    sp = species.upper()
    coefficients = RSF_COEFFICIENTS.get(sp, RSF_COEFFICIENTS["CERF"])
    covariables = _extract_covariables(lat, lng, sp, month)
    breeding = _get_breeding_modifier(sp, month)
    score = compute_rsf_score(lat, lng, sp, month)
    return {
        "score": score,
        "species": sp,
        "month": month,
        "covariables": covariables,
        "coefficients": coefficients,
        "breeding": breeding,
        "disturbance": SPECIES_DISTURBANCE_TOLERANCE.get(sp, {}),
        "water": SPECIES_WATER_DEPENDENCY.get(sp, {}),
        "thermal": SPECIES_THERMAL_PREFERENCE.get(sp, {}),
        "circadian": SPECIES_CIRCADIAN.get(sp, {}),
    }


def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    """Interface compatible avec le score consolide (22 moteurs).
    Remplace les moteurs hash generiques."""
    return compute_rsf_score(lat, lng, species, month)
