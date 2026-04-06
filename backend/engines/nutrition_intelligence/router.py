"""
API Router — Nutrition Intelligence x5000 SUPRA + x6000 + x6010-x6012
Endpoints pour tous les moteurs x5100-x6012.
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
    analyze_product_quality,
    analyze_all_quality,
    get_product_availability,
    get_all_availability,
    get_provincial_restrictions,
    compute_compliance_score,
    compute_all_compliance,
    get_compliance_by_organism,
    get_solutions_for_deficits,
    get_all_terrain_solutions,
    get_product_ecosystem,
    get_all_ecosystems,
    get_product_tracability,
    submit_product,
    review_submission,
    activate_product,
    get_submission,
    get_all_submissions,
    get_pipeline_stats,
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
    lat: Optional[float] = None
    lng: Optional[float] = None
    saline_score: Optional[int] = None


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
    """Endpoint complet pour le SUPRA PANEL declenche par clic carte.
    BCE-4X UNIFIED: Si saline_score est fourni (score carte), il devient le score_global principal.
    Le score mineral x5100 devient score_mineral (complementaire).
    """
    score_data = compute_mineral_score(req.species, req.season, req.soil_type, req.site_minerals)

    # BCE-4X SUPRA_SCORE UNIFIE: score carte = score principal
    if req.saline_score is not None:
        score_data["score_mineral"] = score_data.get("score_global", 0)
        score_data["score_global"] = req.saline_score
        score_data["score_source"] = "SUPRA_UNIFIED"
    else:
        score_data["score_mineral"] = score_data.get("score_global", 0)
        score_data["score_source"] = "x5100_mineral"

    if req.lat is not None and req.lng is not None:
        score_data["location"] = {"lat": req.lat, "lng": req.lng}

    reco_data = compute_recommendations(req.species, req.season, req.soil_type, req.site_minerals)
    energy = compute_energy_protein(req.species, req.season)
    recipe_data = generate_recipe(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)
    evidence = get_evidence_for_recipe(recipe_data)
    costs = compute_costs(req.species, req.season, req.soil_type, req.substrate, req.site_minerals)
    substrate_comparison = compare_substrates(req.species, req.season, req.soil_type, req.site_minerals)
    products = score_all_products(req.species, req.season, req.soil_type)
    order = generate_order(req.species, req.season, req.soil_type, None, req.site_minerals)
    ecozone = get_ecological_zones(req.species)

    # x6010-x6012: Enrichissement produits (qualite, dispo, conformite)
    enriched_products = []
    for p in products.get("products", []):
        pid = p.get("product_id")
        quality = analyze_product_quality(pid) if pid else {}
        availability = get_product_availability(pid, "QC") if pid else {}
        compliance = compute_compliance_score(pid) if pid else {}
        p["quality"] = {
            "score": quality.get("score_qualite", 0),
            "grade": quality.get("grade", "N/A"),
            "efficiency_ratio": quality.get("efficiency_ratio", 0),
        } if "error" not in quality else None
        p["availability"] = {
            "canada_score": availability.get("availability_score", {}).get("canada_score", 0),
            "province_status": availability.get("province_detail", {}).get("status", "inconnu"),
            "usa_available": availability.get("usa", {}).get("available", False),
        } if "error" not in availability else None
        p["compliance"] = {
            "score": compliance.get("score_compliance", 0),
            "grade": compliance.get("grade", "N/A"),
            "certifications": compliance.get("certifications", []),
        } if "error" not in compliance else None
        enriched_products.append(p)

    products["products"] = enriched_products

    # x6020: Solutions terrain associees aux deficits
    terrain_solutions = get_solutions_for_deficits(
        score_data.get("scores_par_mineral", {}),
        energy.get("energy_need"),
        energy.get("protein_need"),
    )

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
        "terrain_solutions": terrain_solutions,
    }


# --- x6010 PRODUCT_QUALITY_ANALYZER ---

class QualityRequest(BaseModel):
    product_id: str


# x6010 — Analyse qualite produit (12 criteres)
@router.post("/products/quality")
async def product_quality(req: QualityRequest):
    return analyze_product_quality(req.product_id)


# x6010 — Analyse qualite tous les produits
@router.get("/products/quality/all")
async def products_quality_all():
    return analyze_all_quality()


# --- x6011 MARKET_AVAILABILITY_ENGINE ---

class AvailabilityRequest(BaseModel):
    product_id: str
    province: Optional[str] = None


# x6011 — Disponibilite produit
@router.post("/products/availability")
async def product_availability(req: AvailabilityRequest):
    return get_product_availability(req.product_id, req.province)


# x6011 — Disponibilite tous les produits
@router.get("/products/availability/all")
async def products_availability_all(province: Optional[str] = None):
    return get_all_availability(province)


# x6011 — Restrictions provinciales
@router.get("/products/restrictions/{province}")
async def province_restrictions(province: str):
    return get_provincial_restrictions(province)


# --- x6012 REGULATORY_COMPLIANCE_ENGINE ---

class ComplianceRequest(BaseModel):
    product_id: str


# x6012 — Conformite reglementaire produit
@router.post("/products/compliance")
async def product_compliance(req: ComplianceRequest):
    return compute_compliance_score(req.product_id)


# x6012 — Conformite tous les produits
@router.get("/products/compliance/all")
async def products_compliance_all():
    return compute_all_compliance()


# x6012 — Conformite par organisme
@router.get("/products/compliance/{organism}")
async def compliance_by_organism(organism: str):
    return get_compliance_by_organism(organism)


# --- x6020 TERRAIN_SOLUTIONS_ENGINE ---

# x6020 — Catalogue complet des solutions terrain
@router.get("/terrain/solutions")
async def terrain_solutions_catalog():
    return get_all_terrain_solutions()


# x6020 — Solutions terrain pour un contexte specifique
@router.post("/terrain/solutions/compute")
async def terrain_solutions_compute(req: RecipeRequest):
    score_data = compute_mineral_score(req.species, req.season, req.soil_type, req.site_minerals)
    energy = compute_energy_protein(req.species, req.season)
    return get_solutions_for_deficits(
        score_data.get("scores_par_mineral", {}),
        energy.get("energy_need"),
        energy.get("protein_need"),
    )


# --- x6030 PRODUCT_ECOSYSTEM_CONNECTOR ---

class EcosystemRequest(BaseModel):
    product_id: str


# x6030 — Ecosysteme complet d'un produit
@router.post("/products/ecosystem")
async def product_ecosystem(req: EcosystemRequest):
    return get_product_ecosystem(req.product_id)


# x6030 — Ecosysteme de tous les produits
@router.get("/products/ecosystem/all")
async def products_ecosystem_all():
    return get_all_ecosystems()


# x6030 — Tracabilite d'un produit
@router.post("/products/tracability")
async def product_tracability(req: EcosystemRequest):
    return get_product_tracability(req.product_id)


# --- x7000 SUPPLIER_PRODUCT_ENGINE ---

class SupplierProductSubmission(BaseModel):
    supplier_name: str
    product_name: str
    description: str
    category: str
    price_cad: float
    weight_kg: float
    minerals: List[str] = []
    certifications: List[str] = []
    species_target: List[str] = []
    brand: str = ""


class ReviewRequest(BaseModel):
    submission_id: str
    approved: bool
    reviewer_notes: str = ""


class ActivateRequest(BaseModel):
    submission_id: str


# x7000 — Soumission produit fournisseur
@router.post("/supplier/submit")
async def supplier_submit(req: SupplierProductSubmission):
    return submit_product(req.model_dump())


# x7000 — Revue humaine
@router.post("/supplier/review")
async def supplier_review(req: ReviewRequest):
    return review_submission(req.submission_id, req.approved, req.reviewer_notes)


# x7000 — Activation magasin
@router.post("/supplier/activate")
async def supplier_activate(req: ActivateRequest):
    return activate_product(req.submission_id)


# x7000 — Recuperer une soumission
@router.get("/supplier/submission/{submission_id}")
async def supplier_get_submission(submission_id: str):
    return get_submission(submission_id)


# x7000 — Liste des soumissions
@router.get("/supplier/submissions")
async def supplier_list_submissions(status: Optional[str] = None):
    return get_all_submissions(status)


# x7000 — Statistiques du pipeline
@router.get("/supplier/pipeline/stats")
async def supplier_pipeline_stats():
    return get_pipeline_stats()
