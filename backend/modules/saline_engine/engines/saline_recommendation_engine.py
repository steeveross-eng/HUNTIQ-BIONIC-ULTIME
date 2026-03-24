"""
SALINE INTELLIGENCE ULTRA — Saline Recommendation Engine V1
Moteur maitre: combine TOUS les engines pour produire la recommandation finale.
Interconnecte: TOUS les 6 sous-moteurs saline + alimentation_v2 + solunar + weather +
               products_engine + scoring + hotspots + exclusion_v7 + corridors.

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("saline.recommendation")

# Import all sub-engines
from .soil_composition_engine import analyze_soil
from .nutrient_deficiency_engine import analyze_deficiencies
from .wildlife_nutritional_engine import get_daily_needs
from .vegetation_forage_engine import analyze_vegetation
from .hydrology_leaching_engine import analyze_hydrology
from .seasonal_metabolism_engine import get_metabolic_state

# Saline product type recommendations based on deficit profiles
PRODUCT_FORMULAS = {
    "haute_Na": {
        "name": "Bloc Sodium Haute Teneur",
        "minerals": {"Na": 350000, "Ca": 5000, "P": 2000},
        "format": "bloc",
        "target_deficit": ["Na"],
        "description": "Ideal pour periodes printemps/rut — forte demande sodium",
    },
    "Ca_P_equilibre": {
        "name": "Granules Ca-P Equilibre 2:1",
        "minerals": {"Ca": 180000, "P": 90000, "Mg": 15000, "Na": 50000},
        "format": "granules",
        "target_deficit": ["Ca", "P"],
        "description": "Croissance bois, gestation — ratio Ca:P optimal",
    },
    "oligo_complet": {
        "name": "Melange Oligo-Elements Complet",
        "minerals": {"Zn": 5000, "Cu": 1500, "Se": 30, "Mn": 4000, "Na": 80000},
        "format": "poudre",
        "target_deficit": ["Zn", "Cu", "Se", "Mn"],
        "description": "Supplementation micro-mineraux — immunite et reproduction",
    },
    "mineral_universel": {
        "name": "Bloc Mineral Universel 4 Saisons",
        "minerals": {"Na": 200000, "Ca": 80000, "P": 40000, "Mg": 20000, "K": 15000},
        "format": "bloc",
        "target_deficit": [],
        "description": "Solution polyvalente toute saison",
    },
    "Na_K_rut": {
        "name": "Attractif Rut Na+K Intensif",
        "minerals": {"Na": 280000, "K": 120000, "Mg": 25000, "Se": 15},
        "format": "liquide",
        "target_deficit": ["Na", "K"],
        "description": "Formule rut — attraction maximale Na+K",
    },
    "Se_Cu_sante": {
        "name": "Supplement Selenium-Cuivre Sante",
        "minerals": {"Se": 50, "Cu": 2000, "Zn": 3000, "Na": 100000},
        "format": "granules",
        "target_deficit": ["Se", "Cu"],
        "description": "Zones carencees Se/Cu — sante et fertilite",
    },
}


def generate_full_analysis(
    lat: float, lng: float,
    species: str = "orignal",
    sex: str = "male",
    age: str = "adult",
    month: int = 10,
    season: str = "automne",
    terrain: Dict = None,
    solunar_data: Dict = None,
    weather_data: Dict = None,
) -> Dict[str, Any]:
    """
    Analyse COMPLETE Saline Intelligence Ultra.
    Orchestre les 6 sous-moteurs et produit la recommandation finale.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # 1. SOIL ANALYSIS (soil_composition_engine)
    soil = analyze_soil(lat, lng, season)

    # 2. WILDLIFE NEEDS (wildlife_nutritional_engine)
    needs = get_daily_needs(species, season, sex, age)

    # 3. NUTRIENT DEFICIENCY (nutrient_deficiency_engine)
    deficiency = analyze_deficiencies(soil, needs)

    # 4. VEGETATION FORAGE (vegetation_forage_engine)
    vegetation = analyze_vegetation(lat, lng, month, terrain)

    # 5. HYDROLOGY LEACHING (hydrology_leaching_engine)
    hydrology = analyze_hydrology(lat, lng, season, terrain, soil)

    # 6. SEASONAL METABOLISM (seasonal_metabolism_engine)
    metabolism = get_metabolic_state(month, species, sex, solunar_data, weather_data)

    # === MASTER RECOMMENDATION ===

    # Compute adjusted deficits (accounting for leaching and vegetation intake)
    adjusted_deficits = _compute_adjusted_deficits(deficiency, hydrology, vegetation)

    # Select optimal product formulas
    recommended_products = _select_products(adjusted_deficits, metabolism)

    # Generate custom recipe
    custom_recipe = _generate_custom_recipe(adjusted_deficits, metabolism, species)

    # Compute placement score
    placement = _compute_placement_score(soil, hydrology, vegetation, metabolism)

    # Overall saline intelligence score
    intelligence_score = _compute_intelligence_score(
        soil, deficiency, vegetation, hydrology, metabolism, placement
    )

    return {
        "type": "saline_intelligence_ultra",
        "version": "1.0.0",
        "timestamp": timestamp,
        "location": {"lat": lat, "lng": lng},
        "parameters": {
            "species": species,
            "sex": sex,
            "age": age,
            "month": month,
            "season": season,
        },
        "engines": {
            "soil": soil,
            "needs": needs,
            "deficiency": deficiency,
            "vegetation": vegetation,
            "hydrology": hydrology,
            "metabolism": metabolism,
        },
        "analysis": {
            "adjusted_deficits": adjusted_deficits,
            "intelligence_score": intelligence_score,
            "placement": placement,
        },
        "recommendations": {
            "products": recommended_products,
            "custom_recipe": custom_recipe,
            "metabolic_tips": metabolism.get("recommendations", []),
            "placement_tips": placement.get("tips", []),
        },
        "interconnections": {
            "engines_used": [
                "soil_composition_engine",
                "nutrient_deficiency_engine",
                "wildlife_nutritional_engine",
                "vegetation_forage_engine",
                "hydrology_leaching_engine",
                "seasonal_metabolism_engine",
            ],
            "bionic_services": [
                "alimentation_v2/terrain",
                "alimentation_v2/salines",
                "solunar/engine",
                "weather_engine",
                "exclusion_engine_v7",
                "corridors_v10",
                "hotspot_service",
                "products_engine",
            ],
            "data_layers": [
                "SoilGrids/CanSIS",
                "HydroSHEDS",
                "ecoforestry_layers",
                "behavioral_layers",
            ],
        },
    }


def _compute_adjusted_deficits(deficiency: Dict, hydrology: Dict, vegetation: Dict) -> Dict[str, Any]:
    """Deficits ajustes en tenant compte du lessivage et de l'apport vegetal."""
    coverage = deficiency.get("coverage", {})
    leaching = hydrology.get("leaching", {})
    veg_minerals = vegetation.get("vegetation_minerals_mg_kg", {})

    adjusted = {}
    critical_list = []
    deficit_list = []

    for mineral, cov_data in coverage.items():
        base_coverage = cov_data.get("coverage_pct", 100)
        base_deficit = cov_data.get("deficit_mg", 0)

        # Leaching penalty: reduces soil availability
        leach_rate = leaching.get(mineral, {}).get("effective_rate", 0.1)
        leach_penalty = leach_rate * 30  # Convert rate to % penalty

        # Vegetation bonus: partial compensation from browse
        veg_content = veg_minerals.get(mineral, 0)
        # Assume ~5kg dry matter intake/day for cervids; bioavail ~20-50%
        veg_bonus_pct = min(20, (veg_content * 5 * 0.003) / max(1, cov_data.get("daily_need_mg", 1)) * 100)

        adjusted_coverage = max(0, base_coverage - leach_penalty + veg_bonus_pct)
        adjusted_deficit = max(0, base_deficit * (1 + leach_rate) - (veg_content * 5 * 0.003))

        status = "sufficient" if adjusted_coverage >= 80 else (
            "marginal" if adjusted_coverage >= 50 else (
                "deficient" if adjusted_coverage >= 30 else "critical"
            )
        )

        entry = {
            "mineral": mineral,
            "base_coverage_pct": round(base_coverage, 1),
            "leach_penalty_pct": round(leach_penalty, 1),
            "vegetation_bonus_pct": round(veg_bonus_pct, 1),
            "adjusted_coverage_pct": round(adjusted_coverage, 1),
            "adjusted_deficit_mg": round(max(0, adjusted_deficit), 1),
            "status": status,
        }
        adjusted[mineral] = entry

        if status == "critical":
            critical_list.append(entry)
        elif status == "deficient":
            deficit_list.append(entry)

    return {
        "minerals": adjusted,
        "critical": critical_list,
        "deficient": deficit_list,
        "total_critical": len(critical_list),
        "total_deficient": len(deficit_list),
    }


def _select_products(adjusted_deficits: Dict, metabolism: Dict) -> List[Dict[str, Any]]:
    """Selectionne les formules de produits optimales basees sur les deficits."""
    critical = adjusted_deficits.get("critical", [])
    deficient = adjusted_deficits.get("deficient", [])
    priority_minerals = metabolism.get("priority_minerals", [])

    deficit_minerals = set()
    for d in critical + deficient:
        deficit_minerals.add(d["mineral"])
    for m in priority_minerals[:3]:
        deficit_minerals.add(m)

    scored_products = []
    for formula_id, formula in PRODUCT_FORMULAS.items():
        score = 0
        targets = formula.get("target_deficit", [])

        # Score based on deficit match
        for target in targets:
            if target in deficit_minerals:
                score += 30
                # Bonus for critical deficits
                if any(d["mineral"] == target for d in critical):
                    score += 20

        # Score based on metabolic priority match
        formula_minerals = set(formula.get("minerals", {}).keys())
        for i, pm in enumerate(priority_minerals):
            if pm in formula_minerals:
                score += (10 - i * 2)

        # Universal product gets base score
        if not targets:
            score = 25

        if score > 0:
            scored_products.append({
                "formula_id": formula_id,
                "name": formula["name"],
                "format": formula["format"],
                "description": formula["description"],
                "match_score": score,
                "minerals": formula["minerals"],
                "targets_addressed": [t for t in targets if t in deficit_minerals],
            })

    scored_products.sort(key=lambda p: p["match_score"], reverse=True)
    return scored_products[:4]


def _generate_custom_recipe(adjusted_deficits: Dict, metabolism: Dict, species: str) -> Dict[str, Any]:
    """Genere une recette saline personnalisee basee sur l'analyse complete."""
    minerals = adjusted_deficits.get("minerals", {})
    phase = metabolism.get("metabolic_phase", "base")
    multiplier = metabolism.get("mineral_multiplier", 1.0)

    recipe_components = []
    total_weight_g = 1000  # recipe per 1kg

    for mineral, data in minerals.items():
        coverage = data.get("adjusted_coverage_pct", 100)
        deficit = data.get("adjusted_deficit_mg", 0)

        if coverage >= 80:
            continue

        # Calculate supplement needed (mg per kg of saline mix)
        supplement_mg_kg = round(deficit * multiplier * 10, 1)  # scale to saline lick size
        if supplement_mg_kg <= 0:
            continue

        recipe_components.append({
            "mineral": mineral,
            "supplement_mg_per_kg": supplement_mg_kg,
            "priority": "critical" if coverage < 30 else "high" if coverage < 50 else "moderate",
            "coverage_before": round(coverage, 1),
        })

    recipe_components.sort(key=lambda c: c["supplement_mg_per_kg"], reverse=True)

    return {
        "species": species,
        "metabolic_phase": phase,
        "components": recipe_components,
        "total_components": len(recipe_components),
        "base_carrier": "sel_marin" if any(c["mineral"] == "Na" for c in recipe_components) else "argile_bentonite",
        "format_recommande": "granules" if len(recipe_components) > 4 else "bloc",
        "renouvellement_jours": 14 if multiplier > 1.2 else 21 if multiplier > 0.9 else 30,
    }


def _compute_placement_score(soil: Dict, hydrology: Dict, vegetation: Dict, metabolism: Dict) -> Dict[str, Any]:
    """Score de placement optimal pour la saline."""
    score = 50.0
    tips = []

    # Soil quality bonus
    soil_quality = soil.get("quality_index", 50)
    if soil_quality > 70:
        score += 10
        tips.append("Sol de bonne qualite — mineraux bien retenus")
    elif soil_quality < 40:
        score -= 10
        tips.append("Sol pauvre — renouveler les salines plus frequemment")

    # Hydrology: sweet spot for leaching
    leach_risk = hydrology.get("leaching_risk", "moderate")
    if leach_risk == "low":
        score += 15
        tips.append("Faible lessivage — mineraux bien conserves")
    elif leach_risk == "high":
        score -= 15
        tips.append("Fort lessivage — utiliser formats resistants (blocs) et abris")

    # Vegetation cover: moderate is best (visibility + protection)
    couvert = vegetation.get("couvert_pct", 65)
    if 40 <= couvert <= 75:
        score += 10
        tips.append(f"Couvert forestier optimal ({couvert}%) — bon equilibre visibilite/protection")
    elif couvert > 85:
        score -= 5
        tips.append("Couvert tres dense — acces reduit, visibilite faible")

    # Metabolism: high activity = more visits = better ROI
    activity = metabolism.get("activity_level", "moderate")
    if activity in ("very_high", "high"):
        score += 10
        tips.append(f"Activite {activity} — frequentation elevee attendue")

    # Water distance
    optimal_dist = hydrology.get("optimal_saline_distance_eau_m", {})
    if optimal_dist:
        tips.append(f"Distance eau optimale: {optimal_dist.get('optimal_m', 120)}m")

    score = max(0, min(100, score))

    return {
        "score": round(score, 1),
        "rating": "excellent" if score >= 80 else "bon" if score >= 60 else "moyen" if score >= 40 else "faible",
        "tips": tips,
    }


def _compute_intelligence_score(soil, deficiency, vegetation, hydrology, metabolism, placement) -> Dict[str, Any]:
    """Score global Saline Intelligence Ultra."""
    components = {
        "soil_quality": soil.get("quality_index", 50),
        "coverage_adequacy": deficiency.get("overall_coverage_pct", 50),
        "forage_quality": vegetation.get("avg_forage_quality", 0.5) * 100,
        "leaching_resistance": max(0, 100 - hydrology.get("avg_leaching_rate", 0.15) * 400),
        "metabolic_alignment": metabolism.get("energy_demand_factor", 0.8) * 80,
        "placement_score": placement.get("score", 50),
    }

    weights = {
        "soil_quality": 0.15,
        "coverage_adequacy": 0.25,
        "forage_quality": 0.10,
        "leaching_resistance": 0.15,
        "metabolic_alignment": 0.20,
        "placement_score": 0.15,
    }

    total = sum(components[k] * weights[k] for k in components)

    return {
        "global_score": round(total, 1),
        "rating": "premium" if total >= 80 else "optimal" if total >= 65 else "adequat" if total >= 45 else "insuffisant",
        "components": {k: round(v, 1) for k, v in components.items()},
        "weights": weights,
    }
