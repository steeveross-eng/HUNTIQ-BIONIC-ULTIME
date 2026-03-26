"""
API Router — Nutrition Intelligence ×5000 SUPRA
Endpoints pour tous les moteurs ×5100-×5900.
BCE-4X / STEEVE-MAX V6
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from engines.nutrition_intelligence import (
    compute_mineral_score,
    compute_recommendations,
    generate_order,
    compute_energy_protein,
    generate_site_guide,
    compute_costs,
    compare_substrates,
    generate_recipe,
    get_evidence,
    get_evidence_for_recipe,
)

router = APIRouter(prefix="/api/v6/nutrition-intelligence", tags=["Nutrition Intelligence x5000"])


class NutritionRequest(BaseModel):
    species: str = "chevreuil"
    season: str = "printemps"
    soil_type: str = "mixte"
    site_minerals: Optional[dict] = None


class OrderRequest(BaseModel):
    species: str = "chevreuil"
    season: str = "printemps"
    soil_type: str = "mixte"
    mineral_key: Optional[str] = None
    site_minerals: Optional[dict] = None


class RecipeRequest(BaseModel):
    species: str = "chevreuil"
    season: str = "printemps"
    soil_type: str = "mixte"
    substrate: str = "bois_mou"
    site_minerals: Optional[dict] = None


class CostRequest(BaseModel):
    species: str = "chevreuil"
    season: str = "printemps"
    soil_type: str = "mixte"
    substrate: str = "bois_mou"
    site_minerals: Optional[dict] = None


# ×5100 — Score mineral
@router.post("/score")
async def mineral_score(req: NutritionRequest):
    return compute_mineral_score(req.species, req.season, req.soil_type, req.site_minerals)


# ×5200 — Recommandations
@router.post("/recommendations")
async def mineral_recommendations(req: NutritionRequest):
    return compute_recommendations(req.species, req.season, req.soil_type, req.site_minerals)


# ×5300 — Commande
@router.post("/order")
async def order(req: OrderRequest):
    return generate_order(req.species, req.season, req.soil_type, req.mineral_key, req.site_minerals)


# ×5500 — Energie/Proteines
@router.post("/energy-protein")
async def energy_protein(req: NutritionRequest):
    return compute_energy_protein(req.species, req.season)


# ×5600 — Guide site
@router.post("/site-guide")
async def site_guide(req: NutritionRequest):
    return generate_site_guide(req.species, req.season, req.soil_type)


# ×5700 — Couts
@router.post("/costs")
async def costs(req: CostRequest):
    return compute_costs(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)


# ×5700 — Comparaison substrats
@router.post("/costs/compare")
async def costs_compare(req: NutritionRequest):
    return compare_substrates(req.species, req.season, req.soil_type, req.site_minerals)


# ×5800 — Recette
@router.post("/recipe")
async def recipe(req: RecipeRequest):
    r = generate_recipe(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)
    evidence = get_evidence_for_recipe(r)
    r["evidence"] = evidence
    return r


# ×5900 — Preuves scientifiques
@router.get("/evidence")
async def evidence(mineral: str = None, category: str = None):
    return get_evidence(mineral, category)


# Endpoint complet — tout en un
@router.post("/full-analysis")
async def full_analysis(req: RecipeRequest):
    recipe_data = generate_recipe(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)
    evidence = get_evidence_for_recipe(recipe_data)
    substrate_comparison = compare_substrates(req.species, req.season, req.soil_type, req.site_minerals)
    return {
        "recipe": recipe_data,
        "evidence": evidence,
        "substrate_comparison": substrate_comparison,
    }
