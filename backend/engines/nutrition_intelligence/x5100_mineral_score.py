"""
×5100 — MINERAL_SCORE_ENGINE
Score 0-100 base sur carences minerales, saison, espece, type de sol.
Pipeline BCE-4X / STEEVE-MAX V6
"""

# --- Donnees de reference scientifique ---

MINERAL_NEEDS_BY_SPECIES = {
    "chevreuil": {
        "Na": {"base_need": 85, "unit": "mg/kg/j"},
        "Ca": {"base_need": 70, "unit": "mg/kg/j"},
        "P": {"base_need": 55, "unit": "mg/kg/j"},
        "K": {"base_need": 40, "unit": "mg/kg/j"},
        "Mg": {"base_need": 30, "unit": "mg/kg/j"},
        "Zn": {"base_need": 25, "unit": "mg/kg/j"},
        "Se": {"base_need": 15, "unit": "ug/kg/j"},
        "Fe": {"base_need": 50, "unit": "mg/kg/j"},
    },
    "orignal": {
        "Na": {"base_need": 120, "unit": "mg/kg/j"},
        "Ca": {"base_need": 95, "unit": "mg/kg/j"},
        "P": {"base_need": 75, "unit": "mg/kg/j"},
        "K": {"base_need": 55, "unit": "mg/kg/j"},
        "Mg": {"base_need": 45, "unit": "mg/kg/j"},
        "Zn": {"base_need": 35, "unit": "mg/kg/j"},
        "Se": {"base_need": 20, "unit": "ug/kg/j"},
        "Fe": {"base_need": 65, "unit": "mg/kg/j"},
    },
    "wapiti": {
        "Na": {"base_need": 110, "unit": "mg/kg/j"},
        "Ca": {"base_need": 90, "unit": "mg/kg/j"},
        "P": {"base_need": 70, "unit": "mg/kg/j"},
        "K": {"base_need": 50, "unit": "mg/kg/j"},
        "Mg": {"base_need": 40, "unit": "mg/kg/j"},
        "Zn": {"base_need": 30, "unit": "mg/kg/j"},
        "Se": {"base_need": 18, "unit": "ug/kg/j"},
        "Fe": {"base_need": 60, "unit": "mg/kg/j"},
    },
}

SEASON_MULTIPLIERS = {
    "printemps": {"Na": 1.3, "Ca": 1.4, "P": 1.5, "K": 1.1, "Mg": 1.2, "Zn": 1.3, "Se": 1.2, "Fe": 1.1},
    "ete": {"Na": 1.1, "Ca": 1.0, "P": 1.0, "K": 1.0, "Mg": 1.0, "Zn": 1.0, "Se": 1.0, "Fe": 1.0},
    "pre_rut": {"Na": 1.4, "Ca": 1.5, "P": 1.6, "K": 1.2, "Mg": 1.3, "Zn": 1.5, "Se": 1.4, "Fe": 1.2},
    "rut": {"Na": 1.2, "Ca": 1.3, "P": 1.4, "K": 1.1, "Mg": 1.2, "Zn": 1.4, "Se": 1.3, "Fe": 1.1},
    "post_rut": {"Na": 1.5, "Ca": 1.2, "P": 1.1, "K": 1.3, "Mg": 1.1, "Zn": 1.2, "Se": 1.3, "Fe": 1.2},
    "hiver": {"Na": 1.6, "Ca": 1.1, "P": 1.0, "K": 1.4, "Mg": 1.0, "Zn": 1.1, "Se": 1.5, "Fe": 1.3},
}

SOIL_AVAILABILITY = {
    "acide": {"Na": 0.3, "Ca": 0.25, "P": 0.2, "K": 0.5, "Mg": 0.35, "Zn": 0.4, "Se": 0.15, "Fe": 0.7},
    "loam": {"Na": 0.5, "Ca": 0.6, "P": 0.5, "K": 0.6, "Mg": 0.55, "Zn": 0.5, "Se": 0.4, "Fe": 0.6},
    "coniferes": {"Na": 0.25, "Ca": 0.2, "P": 0.15, "K": 0.4, "Mg": 0.3, "Zn": 0.35, "Se": 0.1, "Fe": 0.65},
    "mixte": {"Na": 0.4, "Ca": 0.45, "P": 0.35, "K": 0.55, "Mg": 0.45, "Zn": 0.45, "Se": 0.25, "Fe": 0.6},
    "sableux": {"Na": 0.35, "Ca": 0.3, "P": 0.25, "K": 0.45, "Mg": 0.35, "Zn": 0.3, "Se": 0.2, "Fe": 0.5},
}

MINERAL_NAMES = {
    "Na": "Sodium", "Ca": "Calcium", "P": "Phosphore", "K": "Potassium",
    "Mg": "Magnesium", "Zn": "Zinc", "Se": "Selenium", "Fe": "Fer",
}


def compute_mineral_score(species: str, season: str, soil_type: str, site_minerals: dict = None) -> dict:
    """
    Calcule le score mineral 0-100 pour un site donne.
    
    Args:
        species: chevreuil, orignal, wapiti
        season: printemps, ete, pre_rut, rut, post_rut, hiver
        soil_type: acide, loam, coniferes, mixte, sableux
        site_minerals: dict optionnel {mineral: pct_disponible} override
    
    Returns:
        dict avec score_global, scores_par_mineral, zones, details
    """
    sp = MINERAL_NEEDS_BY_SPECIES.get(species, MINERAL_NEEDS_BY_SPECIES["chevreuil"])
    sm = SEASON_MULTIPLIERS.get(season, SEASON_MULTIPLIERS["ete"])
    sa = SOIL_AVAILABILITY.get(soil_type, SOIL_AVAILABILITY["mixte"])

    mineral_scores = {}
    weighted_total = 0
    total_weight = 0

    for mineral, need_data in sp.items():
        base_need = need_data["base_need"]
        seasonal_need = base_need * sm.get(mineral, 1.0)

        if site_minerals and mineral in site_minerals:
            availability = site_minerals[mineral] / 100.0
        else:
            availability = sa.get(mineral, 0.4)

        coverage_ratio = availability / (seasonal_need / 100.0) if seasonal_need > 0 else 1.0
        score = min(100, max(0, int(coverage_ratio * 100)))

        if score >= 70:
            zone = "vert"
        elif score >= 40:
            zone = "jaune"
        else:
            zone = "rouge"

        weight = seasonal_need / 50.0
        weighted_total += score * weight
        total_weight += weight

        mineral_scores[mineral] = {
            "name": MINERAL_NAMES.get(mineral, mineral),
            "score": score,
            "zone": zone,
            "besoin_saisonnier": round(seasonal_need, 1),
            "disponibilite_sol": round(availability * 100, 1),
            "unite": need_data["unit"],
        }

    global_score = int(weighted_total / total_weight) if total_weight > 0 else 50

    return {
        "score_global": min(100, max(0, global_score)),
        "grade": "EXCELLENT" if global_score >= 80 else "BON" if global_score >= 65 else "MODERE" if global_score >= 50 else "FAIBLE",
        "species": species,
        "season": season,
        "soil_type": soil_type,
        "scores_par_mineral": mineral_scores,
        "zones_resume": {
            "vert": sum(1 for m in mineral_scores.values() if m["zone"] == "vert"),
            "jaune": sum(1 for m in mineral_scores.values() if m["zone"] == "jaune"),
            "rouge": sum(1 for m in mineral_scores.values() if m["zone"] == "rouge"),
        },
    }
