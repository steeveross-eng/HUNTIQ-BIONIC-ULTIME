"""
×5800 — RECIPE_ENGINE
Livre de recettes SUPRA complet.
Genere recettes par saison, espece, carences, besoins energie/proteines.
"""
from .x5200_mineral_recommendation import compute_recommendations
from .x5500_energy_protein import compute_energy_protein
from .x5600_site_guide import generate_site_guide
from .x5700_cost_engine import compute_costs


def generate_recipe(species: str, season: str, soil_type: str, substrate: str = "bois_mou", site_minerals: dict = None) -> dict:
    """Genere une recette complete pour un contexte donne."""
    reco = compute_recommendations(species, season, soil_type, site_minerals)
    energy = compute_energy_protein(species, season)
    site = generate_site_guide(species, season, soil_type)
    costs = compute_costs(species, season, soil_type, substrate, site_minerals)

    critical_minerals = [r for r in reco["recommendations"] if r["priority"] == "CRITIQUE"]
    recommended_minerals = [r for r in reco["recommendations"] if r["priority"] == "RECOMMANDE"]

    ingredients_cles = []
    for r in critical_minerals + recommended_minerals:
        ingredients_cles.append({
            "mineral": r["name"],
            "product": r["brand"],
            "dosage": r["dosage"],
            "priority": r["priority"],
        })

    proteines_cles = []
    for block in energy["protein_blocks"]:
        proteines_cles.append({
            "name": block["name"],
            "brand": block["brand"],
            "duration": f"{block['duration_weeks']} semaines",
        })

    for block in energy["energy_blocks"]:
        proteines_cles.append({
            "name": block["name"],
            "brand": block["brand"],
            "duration": f"{block['duration_weeks']} semaines",
            "type": "energetique",
        })

    SEASON_LABELS = {
        "printemps": "Printemps", "ete": "Ete", "pre_rut": "Pre-rut",
        "rut": "Rut", "post_rut": "Post-rut", "hiver": "Hiver",
    }

    return {
        "title": f"Recette {SEASON_LABELS.get(season, season)} — {species.capitalize()}",
        "subtitle": f"Sol {soil_type} | Substrat {substrate.replace('_', ' ')}",
        "species": species,
        "season": season,
        "season_label": SEASON_LABELS.get(season, season),
        "soil_type": soil_type,
        "substrate": substrate,
        "score": reco["score_data"],
        "phase_physiologique": energy["phase"],
        "ingredients_cles": ingredients_cles,
        "proteines_cles": proteines_cles,
        "melange_saisonnier": energy["seasonal_mix"],
        "lieu": {
            "surface_m2": site["implantation"]["surface_recommandee_m2"],
            "couvert": site["implantation"]["couvert"],
            "exposition": site["implantation"]["exposition"],
            "drainage": site["implantation"]["drainage"],
            "distance_corridor": f"{site['implantation']['distance_corridor_m']}m",
            "distance_eau": f"{site['implantation']['distance_eau_m']}m",
        },
        "construction": site["construction"],
        "couts": {
            "initial_cad": costs["initial_cost_cad"],
            "reactivation_cad": costs["reactivation_cost_cad"],
            "annuel_cad": costs["annual_cost_cad"],
            "par_visite_cad": costs["cost_per_visit_cad"],
            "frequence_reactivation": f"Toutes les {costs['reactivation_frequency_weeks']} semaines",
        },
        "nb_deficits_critiques": len(critical_minerals),
        "nb_recommandes": len(recommended_minerals),
    }
