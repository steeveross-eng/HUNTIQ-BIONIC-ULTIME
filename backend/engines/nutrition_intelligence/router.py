"""
API Router — Nutrition Intelligence x5000 SUPRA + x6000 + x6010-x6012
Endpoints pour tous les moteurs x5100-x6012.
BCE-4X / STEEVE-MAX V6
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
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

    # R6.1: Enrichissement produits BATCH — elimination N+1
    # 3 appels batch au lieu de 3*N appels individuels
    all_quality = analyze_all_quality()
    all_availability = get_all_availability("QC")
    all_compliance = compute_all_compliance()

    # Lookup par product_id — O(1) par produit
    quality_map = {q["product_id"]: q for q in all_quality.get("products", [])}
    availability_map = {a["product_id"]: a for a in all_availability.get("products", [])}
    compliance_map = {c["product_id"]: c for c in all_compliance.get("products", [])}

    enriched_products = []
    for p in products.get("products", []):
        pid = p.get("product_id")
        quality = quality_map.get(pid, {})
        availability = availability_map.get(pid, {})
        compliance = compliance_map.get(pid, {})
        p["quality"] = {
            "score": quality.get("score_qualite", 0),
            "grade": quality.get("grade", "N/A"),
            "efficiency_ratio": quality.get("efficiency_ratio", 0),
        } if quality else None
        p["availability"] = {
            "canada_score": availability.get("availability_score", {}).get("canada_score", 0),
            "province_status": availability.get("province_detail", {}).get("status", "inconnu"),
            "usa_available": availability.get("usa", {}).get("available", False),
        } if availability else None
        p["compliance"] = {
            "score": compliance.get("score_compliance", 0),
            "grade": compliance.get("grade", "N/A"),
            "certifications": compliance.get("certifications", []),
        } if compliance else None
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


# R6.2: Endpoint batch unifie — 4 moteurs en 1 appel HTTP
class SupraBatchRequest(BaseModel):
    species: str = "orignal"
    season: str = "printemps"
    soil_type: str = "mixte"
    substrate: str = "bois_mou"
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    saline_score: Optional[int] = None
    site_minerals: Optional[dict] = None
    sex: str = "male"
    age: str = "adult"
    month: int = Field(..., ge=1, le=12)


def _compute_nutrition_v7_block(lat, lng, species, season, month):
    """Bloc NUTRITION-ENGINE-V7 pour injection SUPRA."""
    try:
        from modules.nutrition_engine_v7.pipeline import compute_attractiveness_v7
        result = compute_attractiveness_v7(lat, lng, species, season, month)
        return {
            "attractiveness_score": result.get("attractiveness_score"),
            "rating": result.get("rating"),
            "scores_detail": result.get("scores_detail"),
            "pipeline": result.get("pipeline"),
            "engine": result.get("engine"),
        }
    except Exception as e:
        return {"error": str(e), "engine": "NUTRITION-ENGINE-V7-FALLBACK"}


@router.post("/supra-batch")
async def supra_batch(req: SupraBatchRequest):
    """R6.2: Endpoint batch — SUPRA + ULTRA + FICHE + SOL en 1 appel.
    Remplace 4 requetes HTTP paralleles par 1 seule.
    Structure de sortie identique aux 4 appels individuels.
    BCE-4X GOLDEN V6+ | STEEVE-MAX
    """
    # 1. SUPRA PANEL (reutilise le handler existant)
    supra_req = RecipeRequest(
        species=req.species, season=req.season, soil_type=req.soil_type,
        substrate=req.substrate, lat=req.lat, lng=req.lng,
        saline_score=req.saline_score, site_minerals=req.site_minerals,
    )
    supra_result = await supra_panel(supra_req)

    # 2. ULTRA (saline/analyze)
    from modules.saline_engine.router import full_analysis as _saline_analyze
    from modules.saline_engine.models import SalineAnalysisRequest, SpeciesEnum, SexEnum, AgeEnum, SeasonEnum
    species_enum = SpeciesEnum(req.species) if req.species in SpeciesEnum.__members__.values() else SpeciesEnum.ORIGNAL
    sex_enum = SexEnum(req.sex) if req.sex in SexEnum.__members__.values() else SexEnum.MALE
    age_enum = AgeEnum(req.age) if req.age in AgeEnum.__members__.values() else AgeEnum.ADULT
    season_enum = SeasonEnum(req.season) if req.season in SeasonEnum.__members__.values() else SeasonEnum.AUTOMNE
    saline_req = SalineAnalysisRequest(
        lat=req.lat, lng=req.lng, species=species_enum,
        sex=sex_enum, age=age_enum, month=req.month, season=season_enum,
    )
    ultra_result = await _saline_analyze(saline_req)

    # 3. FICHE (salines-ultime/fiche)
    from modules.salines_ultime_engine.router import generate_fiche as _generate_fiche, FicheRequest
    fiche_req = FicheRequest(lat=req.lat, lng=req.lng, species=req.species, season=req.season)
    fiche_result = await _generate_fiche(fiche_req)

    # 4. SOL (soil/analyze)
    from modules.soil_engine.router import _classify_soil, _compute_soil_score, _grade as _soil_grade, _get_recommendations, SOIL_TYPES
    soil_key = _classify_soil(req.lat, req.lng)
    soil_data = SOIL_TYPES[soil_key]
    soil_score = _compute_soil_score(soil_data)
    soil_grade = _soil_grade(soil_score)
    soil_recs = _get_recommendations(soil_key, req.species)
    seasonal_notes = {
        "printemps": f"Sol {soil_data['nom']}: risque de saturation apres la fonte. Drainage naturel: {soil_data['drainage_naturel']}/100. Verifier l'etat du support apres le gel-degel.",
        "ete": f"Sol {soil_data['nom']}: conditions optimales. Dissolution minerale active. Retention: {soil_data['retention_mineraux']}/100.",
        "automne": f"Sol {soil_data['nom']}: sol ferme, conditions ideales pour maintenance. Preparer le site pour l'hiver.",
        "hiver": f"Sol {soil_data['nom']}: gel en profondeur ({soil_data['profondeur_typique_cm']} cm). Dissolution quasi nulle. Verifier integrite structurelle.",
    }
    soil_result = {
        "soil_type": soil_key, "soil_name": soil_data["nom"],
        "soil_class": soil_data["classe"], "description": soil_data["description"],
        "score": soil_score, "grade": soil_grade,
        "metrics": {
            "retention_mineraux": soil_data["retention_mineraux"],
            "drainage_naturel": soil_data["drainage_naturel"],
            "risque_lessivage": soil_data["risque_lessivage"],
            "capacite_portance": soil_data["capacite_portance"],
            "permeabilite": soil_data["permeabilite"],
            "ph_typique": soil_data["ph_typique"],
            "profondeur_cm": soil_data["profondeur_typique_cm"],
            "matiere_organique_pct": soil_data["matiere_organique_pct"],
        },
        "texture": {
            "argile_pct": soil_data["texture_argile_pct"],
            "sable_pct": soil_data["texture_sable_pct"],
            "limon_pct": soil_data["texture_limon_pct"],
        },
        "recommendations": soil_recs,
        "seasonal_note": seasonal_notes.get(req.season, seasonal_notes["automne"]),
        "coordinates": {"lat": req.lat, "lng": req.lng},
        "species": req.species, "season": req.season,
        "protocol": "BCE-4X GOLDEN V6+", "version": "V1",
    }

    # R8.1: Harmonisation x1000% — Bloc _meta unifie pour chaque moteur
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    meta_base = {
        "species": req.species,
        "season": req.season,
        "coordinates": {"lat": req.lat, "lng": req.lng},
        "protocol": "BCE-4X GOLDEN V6+",
        "timestamp": now,
    }

    def _build_meta(engine_name, score, grade, version="V6"):
        return {**meta_base, "engine": engine_name, "score": score, "grade": grade, "version": version}

    supra_score = supra_result.get("score", {})
    ultra_is = ultra_result.get("analysis", {}).get("intelligence_score", {})
    fiche_gs = fiche_result.get("global_score", {})

    supra_result["_meta"] = _build_meta("SUPRA", supra_score.get("score_global"), supra_score.get("grade"))
    ultra_result["_meta"] = _build_meta("ULTRA", ultra_is.get("global_score"), ultra_is.get("rating"))
    fiche_result["_meta"] = _build_meta("FICHE", fiche_gs.get("score"), fiche_gs.get("grade"))
    soil_result["_meta"] = _build_meta("SOL", soil_result.get("score"), soil_result.get("grade"))

    # K1: Injection knowledge.json — annotations scientifiques ADDITIVES
    from modules.bionic_knowledge_engine.knowledge_provider import (
        get_species_data, get_species_nutrition_needs, get_corridors_for_species,
        get_soil_data, get_all_sources, get_knowledge_meta, get_sources_for_ids,
    )
    k_species = get_species_data(req.species)
    k_nutrition = get_species_nutrition_needs(req.species, req.season)
    k_corridors = get_corridors_for_species(req.species)
    k_meta = get_knowledge_meta()

    # K1 — Bloc _knowledge ADDITIF (ZERO modification des scores existants)
    knowledge_block = {
        "species": {
            "id": k_species["id"] if k_species else None,
            "scientific_name": k_species["scientific_name"] if k_species else None,
            "weight_kg": k_species["weight_kg"] if k_species else None,
            "home_range_km2": k_species["home_range_km2"] if k_species else None,
            "temperature_range": k_species["temperature_range"] if k_species else None,
            "habitat_preferences": k_species["habitat_preferences"] if k_species else [],
            "human_tolerance": k_species["human_tolerance"] if k_species else None,
            "breeding": k_species["breeding"] if k_species else None,
        } if k_species else None,
        "nutrition": k_nutrition if k_nutrition else None,
        "corridors": k_corridors,
        "evidence_levels": {"E1": "PEER_REVIEWED", "E2": "GOVERNMENT", "E3": "UNIVERSITY", "E4": "SPECIALIST", "E5": "EMPIRICAL"},
        "knowledge_meta": k_meta,
    }

    # K5: Activation scientifique — Surcouche Species Engine v3 ADDITIVE
    # ZERO modification des scores. Annotations scientifiques par moteur.
    from modules.species_engine.scientific_overlay import (
        overlay_supra, overlay_ultra, overlay_fiche, overlay_sol,
    )
    supra_result["_scientific"] = overlay_supra(req.species, req.season, req.lat, req.lng)
    ultra_result["_scientific"] = overlay_ultra(req.species, req.season, req.lat, req.lng)
    fiche_result["_scientific"] = overlay_fiche(req.species, req.season, req.lat, req.lng)
    soil_result["_scientific"] = overlay_sol(req.species, req.season, req.lat, req.lng)

    # SUPRA-REACT-Omega: Inject territory IA data (cameras, vision, hotspots, affuts)
    territory_ia = {}
    try:
        from engines.supra_advanced.territory_bridge import get_territory_ia_data
        territory_ia = await get_territory_ia_data(req.lat, req.lng, req.species)
    except Exception as e_tia:
        logger.warning(f"[SUPRA-TERRITORY] Territory IA bridge error: {e_tia}")

    # SUPRA-V7-REINTEGRATION: Inject V7 Intelligence data (temporel, solunaire, provincial, ecosystem)
    v7_intelligence = {}
    try:
        import math
        month = req.month if hasattr(req, 'month') and req.month else 10
        day = 15
        hour = 6
        doy = (month - 1) * 30 + day
        moon_phase = (doy % 29.53) / 29.53
        season_map = {1:"winter",2:"winter",3:"spring",4:"spring",5:"summer",6:"summer",7:"summer",8:"pre_rut",9:"pre_rut",10:"rut",11:"rut",12:"post_rut"}
        season_v7 = season_map.get(month, "pre_rut")

        # Temporal
        crepuscular = req.species in ["cerf", "orignal", "wapiti", "caribou"]
        temporal_score = 90 if (5 <= hour <= 8 or 16 <= hour <= 19) and crepuscular else 50

        # Lunar
        lunar_score = 85 if moon_phase < 0.1 else 60 if 0.4 < moon_phase < 0.6 else 70
        lunar_phase = "nouvelle_lune" if moon_phase < 0.1 else "croissant" if moon_phase < 0.4 else "pleine_lune" if moon_phase < 0.6 else "decroissant"

        # Rut
        rut_peaks = {"cerf": 310, "orignal": 275, "wapiti": 280}
        peak = rut_peaks.get(req.species, 300)
        rut_score = max(20, 100 - abs(doy - peak) * 2)

        # V7 composite
        v7_composite = round(temporal_score * 0.25 + lunar_score * 0.15 + rut_score * 0.20 + supra_score.get("score_global", 50) * 0.40, 1)

        v7_intelligence = {
            "v7_score": min(100, max(0, v7_composite)),
            "temporal": {"score": temporal_score, "pattern": "crepusculaire" if crepuscular else "diurne"},
            "lunar": {"score": lunar_score, "phase": lunar_phase, "moon_phase": round(moon_phase, 2)},
            "rut": {"score": rut_score, "season": season_v7, "days_to_peak": round(peak - doy)},
            "provincial": {"province": "qc", "zones_chasse": 28},
            "ecosystem": {"interactions_documented": 5},
            "solunar_windows": {
                "major_1": "05:30-07:30", "major_2": "17:30-19:30",
                "minor_1": "11:30-12:30", "minor_2": "23:30-00:30"
            },
            "optimal_windows": ["05:30-08:00", "16:30-19:00"] if crepuscular else ["06:00-10:00"],
            "prediction": "excellent" if v7_composite >= 75 else "bon" if v7_composite >= 55 else "moyen" if v7_composite >= 35 else "faible",
        }
    except Exception as e_v7:
        logger.warning(f"[SUPRA-V7] V7 Intelligence injection error: {e_v7}")

    return {
        "supra": supra_result,
        "ultra": ultra_result,
        "fiche": fiche_result,
        "soil": soil_result,
        "territory_ia": territory_ia,
        "v7_intelligence": v7_intelligence,
        "nutrition_v7": _compute_nutrition_v7_block(req.lat, req.lng, req.species, req.season, req.month),
        "_harmonized": True,
        "_knowledge": knowledge_block,
        "_meta": {
            "engines": ["SUPRA", "ULTRA", "FICHE", "SOL", "TERRITORY_IA", "V7_INTELLIGENCE"],
            "k5_activation": True,
            "supra_react_omega": True,
            "supra_v7_reintegration": True,
            "scores": {
                "SUPRA": supra_score.get("score_global"),
                "ULTRA": ultra_is.get("global_score"),
                "FICHE": fiche_gs.get("score"),
                "SOL": soil_result.get("score"),
                "V7": v7_intelligence.get("v7_score"),
            },
            "territory_ia_stats": {
                "cameras": len(territory_ia.get("cameras", [])),
                "analyses": len(territory_ia.get("vision_analyses", [])),
                "hotspots": len(territory_ia.get("hotspots", [])),
                "trajectories": len(territory_ia.get("trajectories", [])),
                "affuts_ia": len(territory_ia.get("affuts_ia", [])),
            },
            "timestamp": now,
            "protocol": "BCE-4X GOLDEN V7",
            "coordinates": {"lat": req.lat, "lng": req.lng},
            "species": req.species,
            "season": req.season,
            "knowledge_version": k_meta.get("version"),
        },
    }


# K1.3: Endpoint Knowledge — consultation directe des donnees scientifiques
@router.get("/knowledge/{species_id}")
async def get_knowledge(species_id: str, season: str = "automne"):
    """K1.3: Retourne les donnees scientifiques annotees pour une espece.
    Inclut: espece, nutrition, corridors, sources, evidence_levels.
    BCE-4X GOLDEN V6+ | STEEVE-MAX | ZERO_INTERPRETATION
    """
    from modules.bionic_knowledge_engine.knowledge_provider import (
        get_species_data, get_species_nutrition_needs, get_corridors_for_species,
        get_all_soils, get_all_sources, get_knowledge_meta,
    )
    k_species = get_species_data(species_id)
    if not k_species:
        return {"error": f"Species '{species_id}' not found", "available": ["orignal", "cerf", "ours", "wapiti"]}
    k_nutrition = get_species_nutrition_needs(species_id, season)
    k_corridors = get_corridors_for_species(species_id)
    k_soils = get_all_soils()
    k_sources = get_all_sources()
    k_meta = get_knowledge_meta()
    return {
        "species": k_species,
        "nutrition": k_nutrition,
        "corridors": k_corridors,
        "soils": k_soils,
        "sources": k_sources,
        "knowledge_meta": k_meta,
        "evidence_levels": {"E1": "PEER_REVIEWED", "E2": "GOVERNMENT", "E3": "UNIVERSITY", "E4": "SPECIALIST", "E5": "EMPIRICAL"},
        "protocol": "BCE-4X GOLDEN V6+",
    }


# R8.2: Export PDF — Rapport complet 4 moteurs
@router.post("/export-pdf")
async def export_pdf(req: SupraBatchRequest):
    """R8.2: Genere un rapport PDF complet SUPRA+ULTRA+FICHE+SOL.
    Retourne le PDF en streaming.
    BCE-4X GOLDEN V6+ | STEEVE-MAX
    """
    import io
    from fpdf import FPDF

    # 1. Fetch all data via batch
    batch_data = await supra_batch(req)
    meta = batch_data.get("_meta", {})
    scores = meta.get("scores", {})

    # 2. Build PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Helper: sanitize text for Helvetica (ASCII only)
    def _s(text):
        return str(text).replace("\u2014", "-").replace("\u2013", "-").replace("\u2019", "'").replace("\u00e9", "e").replace("\u00e8", "e").replace("\u00ea", "e").replace("\u00e0", "a").replace("\u00f4", "o").replace("\u00ee", "i").replace("\u00fb", "u").replace("\u00e7", "c").encode("ascii", "replace").decode("ascii")

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, _s("RAPPORT SUPRA - Analyse Nutritionnelle Complete"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _s(f"Protocole: {meta.get('protocol', 'BCE-4X')} | {meta.get('timestamp', '')}"), ln=True, align="C")
    pdf.cell(0, 6, _s(f"Espece: {meta.get('species', '')} | Saison: {meta.get('season', '')} | Coords: {req.lat}, {req.lng}"), ln=True, align="C")
    pdf.ln(8)

    # Scores Summary
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _s("1. Resume des Scores"), ln=True)
    pdf.set_font("Helvetica", "", 11)
    for engine, score in scores.items():
        grade = batch_data.get(engine.lower(), {}).get("_meta", {}).get("grade", "N/A")
        pdf.cell(0, 7, _s(f"  {engine}: {score}/100 (Grade: {grade})"), ln=True)
    pdf.ln(5)

    # SUPRA Details
    supra = batch_data.get("supra", {})
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _s("2. SUPRA - Score Nutritionnel"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    s_score = supra.get("score", {})
    for mineral, val in s_score.get("scores_par_mineral", {}).items():
        pdf.cell(0, 6, _s(f"  {mineral}: {val}/100"), ln=True)

    # Recommendations
    recs = supra.get("recommendations", {})
    if recs.get("recommendations"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _s("Recommandations:"), ln=True)
        pdf.set_font("Helvetica", "", 9)
        for r in recs["recommendations"][:5]:
            text = _s(f"- {r.get('mineral', '')}: {r.get('recommendation', '')}")
            pdf.set_x(10)
            pdf.multi_cell(190, 5, text)
    pdf.ln(5)

    # ULTRA Details
    ultra = batch_data.get("ultra", {})
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _s("3. ULTRA - Intelligence Score"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    components = ultra.get("analysis", {}).get("intelligence_score", {}).get("components", {})
    for comp, val in components.items():
        pdf.cell(0, 6, _s(f"  {comp}: {val}"), ln=True)

    # Engines
    engines = ultra.get("engines", {})
    if engines:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _s("  Moteurs actifs:"), ln=True)
        pdf.set_font("Helvetica", "", 10)
        for eng_name, eng_data in engines.items():
            if isinstance(eng_data, dict):
                eng_score = eng_data.get("score", eng_data.get("quality_index", "N/A"))
                pdf.cell(0, 6, _s(f"  {eng_name}: {eng_score}"), ln=True)
    pdf.ln(5)

    # FICHE Details
    fiche = batch_data.get("fiche", {})
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _s("4. FICHE SALINE ULTIME"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    fiche_scores = fiche.get("scores", {})
    for cat, cat_data in fiche_scores.items():
        if isinstance(cat_data, dict):
            pdf.cell(0, 6, _s(f"  {cat}: {cat_data.get('score', 'N/A')}/100 (Grade: {cat_data.get('grade', 'N/A')})"), ln=True)
    pdf.ln(5)

    # SOL Details
    sol = batch_data.get("soil", {})
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, _s("5. SOL - Analyse Pedologique"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _s(f"  Type: {sol.get('soil_name', 'N/A')} ({sol.get('soil_class', 'N/A')})"), ln=True)
    metrics = sol.get("metrics", {})
    for m, v in metrics.items():
        label = m.replace("_", " ").capitalize()
        pdf.cell(0, 6, _s(f"  {label}: {v}"), ln=True)
    if sol.get("seasonal_note"):
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_x(10)
        pdf.multi_cell(190, 5, _s(f"Note saisonniere: {sol['seasonal_note']}"))
    pdf.ln(5)

    # Footer
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, _s("BCE-4X GOLDEN V6+ | STEEVE-MAX | ZERO ABSOLU"), ln=True, align="C")

    # 3. Stream PDF
    pdf_bytes = pdf.output()
    buffer = io.BytesIO(pdf_bytes)
    filename = f"SUPRA_rapport_{req.species}_{req.season}_{req.lat}_{req.lng}.pdf"
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


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
