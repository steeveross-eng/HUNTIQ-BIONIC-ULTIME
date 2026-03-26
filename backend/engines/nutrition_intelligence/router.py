"""
API Router — Nutrition Intelligence x5000 SUPRA + x6000
Endpoints pour tous les moteurs x5100-x6000.
BCE-4X / STEEVE-MAX V6
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from engines.nutrition_intelligence import (
    compute_mineral_score,
    compute_recommendations,
    generate_order,
    compute_energy_protein,
    generate_site_guide,
    get_ecological_zones,
    compute_costs,
    compare_substrates,
    generate_recipe,
    get_evidence,
    get_evidence_for_recipe,
    compute_product_score,
    score_all_products,
    compare_products,
    get_shop_products,
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
    products = score_all_products(req.species, req.season, req.soil_type)
    ecozone = get_ecological_zones(req.species)
    return {
        "recipe": recipe_data,
        "evidence": evidence,
        "substrate_comparison": substrate_comparison,
        "products": products,
        "ecozone": ecozone,
    }


# --- x6000 PRODUCT_SCORE_ENGINE ---

class ProductScoreRequest(BaseModel):
    product_id: str
    species: str = "chevreuil"
    season: str = "printemps"
    soil_type: str = "mixte"


class ProductCompareRequest(BaseModel):
    product_ids: List[str]
    species: str = "chevreuil"
    season: str = "printemps"
    soil_type: str = "mixte"


class ShopRequest(BaseModel):
    species: Optional[str] = None
    season: Optional[str] = None
    soil_type: Optional[str] = None
    min_score: int = 0
    product_type: Optional[str] = None


# x6000 — Score produit
@router.post("/products/score")
async def product_score(req: ProductScoreRequest):
    return compute_product_score(req.product_id, req.species, req.season, req.soil_type)


# x6000 — Classement produits
@router.post("/products/all")
async def products_all(req: NutritionRequest):
    return score_all_products(req.species, req.season, req.soil_type)


# x6000 — Comparaison produits
@router.post("/products/compare")
async def products_compare(req: ProductCompareRequest):
    return compare_products(req.product_ids, req.species, req.season, req.soil_type)


# x6000 — Magasin intelligent
@router.post("/products/shop")
async def products_shop(req: ShopRequest):
    return get_shop_products(req.species, req.season, req.soil_type, req.min_score, req.product_type)


# x5600 — Zones ecologiques
@router.get("/ecozones")
async def ecozones(species: str = None):
    return get_ecological_zones(species)


# Endpoint SUPRA PANEL complet — pour clic sur point nutritionnel
@router.post("/supra-panel")
async def supra_panel(req: RecipeRequest):
    """Endpoint complet pour le SUPRA PANEL declenche par clic carte."""
    score_data = compute_mineral_score(req.species, req.season, req.soil_type, req.site_minerals)
    reco_data = compute_recommendations(req.species, req.season, req.soil_type, req.site_minerals)
    energy = compute_energy_protein(req.species, req.season)
    recipe_data = generate_recipe(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)
    evidence = get_evidence_for_recipe(recipe_data)
    costs = compute_costs(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)
    substrate_comparison = compare_substrates(req.species, req.season, req.soil_type, req.site_minerals)
    products = score_all_products(req.species, req.season, req.soil_type)
    order = generate_order(req.species, req.season, req.soil_type, None, req.site_minerals)
    ecozone = get_ecological_zones(req.species)
    return {
        "score": score_data,
        "recommendations": reco_data,
        "energy_protein": energy,
        "recipe": recipe_data,
        "evidence": evidence,
        "costs": costs,
        "substrate_comparison": substrate_comparison,
        "products": products,
        "order": order,
        "ecozone": ecozone,
    }
