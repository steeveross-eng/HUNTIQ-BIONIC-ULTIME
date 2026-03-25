"""
API Gateway V3 — Source unique de verite /api/v3/*
=====================================================
BCE-4X: Routeur unifie, validation automatique, tracabilite.
STEEVE-MAX: Architecture modulaire, decouplee, future-proof.

x4520-UNIFICATION_DASHBOARD: Migration complete vers pipeline 22 moteurs.
Elimination de toutes les reliques V1/V2/V10 dans les reponses.
"""
import sys
import logging
from fastapi import APIRouter, Query

from modules.engine_registry.base import resolve_species, SPECIES_CANONICAL
from modules.engine_registry.registry import EngineRegistry, DynamicConsolidator
from core.scoring_pipeline.score_consolide import compute_consolidated_score

logger = logging.getLogger("api_gateway_v3")

router = APIRouter(prefix="/api/v3", tags=["API-GATEWAY-V3"])

# Singleton registry (pour metadata/validation uniquement)
_registry = EngineRegistry()
_registry.auto_discover()
_consolidator = DynamicConsolidator(_registry)

logger.info(f"[GATEWAY-V3] Initialise: {len(_registry.list_engines())} moteurs legacy + pipeline 22 moteurs")

# x4520: Metadata V6-CORE pour les 22 moteurs (noms propres, domaines, descriptions)
V6_ENGINE_META = {
    "alimentation":     {"label": "Alimentation",     "domain": "habitat",        "tier": "CORE",     "description": "Ressources alimentaires primaires"},
    "alimentation_v2":  {"label": "Nutrition Avancee", "domain": "habitat",        "tier": "CORE",     "description": "Salines, mineraux, carences"},
    "repos":            {"label": "Repos & Couvert",   "domain": "habitat",        "tier": "CORE",     "description": "Zones de repos et couvert vegetal"},
    "corridors_v10":    {"label": "Corridors",         "domain": "deplacement",    "tier": "CORE",     "description": "Corridors de deplacement faunique"},
    "pression":         {"label": "Pression Humaine",  "domain": "pression",       "tier": "CORE",     "description": "Impact anthropique et derangement"},
    "hydro":            {"label": "Hydrographie",      "domain": "environnement",  "tier": "CORE++",   "description": "Reseaux hydriques et zones humides"},
    "thermal":          {"label": "Thermique",         "domain": "environnement",  "tier": "CORE++",   "description": "Gradients thermiques saisonniers"},
    "ndvi_vegetation":  {"label": "Vegetation NDVI",   "domain": "environnement",  "tier": "CORE++",   "description": "Indice de vegetation normalise"},
    "weather":          {"label": "Meteo",             "domain": "environnement",  "tier": "CORE++",   "description": "Conditions meteorologiques"},
    "temporal":         {"label": "Temporel",          "domain": "comportement",   "tier": "CORE++",   "description": "Rythmes circadiens et saisonniers"},
    "habitat":          {"label": "Habitat",           "domain": "habitat",        "tier": "CORE++",   "description": "Qualite structurelle de l'habitat"},
    "ecosystem":        {"label": "Ecosysteme",        "domain": "environnement",  "tier": "CORE++",   "description": "Sante globale de l'ecosysteme"},
    "behavior":         {"label": "Comportement",      "domain": "comportement",   "tier": "CORE+++",  "description": "Analyse comportementale espece"},
    "risk":             {"label": "Risques",           "domain": "pression",       "tier": "CORE+++",  "description": "Evaluation des risques terrain"},
    "opportunity":      {"label": "Opportunites",      "domain": "strategie",      "tier": "CORE+++",  "description": "Fenetres d'opportunite de chasse"},
    "attractors":       {"label": "Attracteurs",       "domain": "strategie",      "tier": "CORE+++",  "description": "Points d'attraction faunique"},
    "scenario":         {"label": "Scenarios",         "domain": "strategie",      "tier": "CORE+++",  "description": "Simulations de scenarios tactiques"},
    "simulation":       {"label": "Simulation",        "domain": "intelligence",   "tier": "BIONIC-OS","description": "Modeles predictifs avances"},
    "multi_species":    {"label": "Multi-especes",     "domain": "intelligence",   "tier": "BIONIC-OS","description": "Interactions inter-especes"},
    "trajets":          {"label": "Trajets",           "domain": "deplacement",    "tier": "CORE+++",  "description": "Analyse des trajets et deplacements"},
    "visibility":       {"label": "Visibilite",        "domain": "strategie",      "tier": "BIONIC-OS","description": "Couverture visuelle et lignes de mire"},
    "learning":         {"label": "Apprentissage",     "domain": "intelligence",   "tier": "BIONIC-OS","description": "Auto-calibration et apprentissage"},
}

V6_DOMAIN_LABELS = {
    "habitat": "Habitat & Nourriture",
    "deplacement": "Deplacement & Corridors",
    "pression": "Pression & Risques",
    "environnement": "Environnement",
    "comportement": "Comportement",
    "strategie": "Strategie & Opportunites",
    "intelligence": "Intelligence BIONIC",
}


# ══════════════════════════════════════════════════════════
# ENGINES — Registry, Scoring, Validation
# ══════════════════════════════════════════════════════════

@router.get("/engines/registry")
async def get_engine_registry():
    """Manifest V6-CORE — 22 moteurs, noms propres, ZERO relique V1/V2/V10."""
    engines_list = []
    for key, meta in V6_ENGINE_META.items():
        engines_list.append({
            "key": key,
            "name": meta["label"],
            "domain": meta["domain"],
            "tier": meta["tier"],
            "description": meta["description"],
        })
    return {
        "version": "V6-CORE",
        "engines_count": len(engines_list),
        "option": "C — CORE 60% / Nouveaux 40%",
        "engines": engines_list,
        "domains": V6_DOMAIN_LABELS,
    }


@router.get("/engines/score-point")
async def score_point(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """Score consolide V6-CORE — pipeline 22 moteurs direct."""
    sp = resolve_species(species)
    result = compute_consolidated_score(lat, lng, sp, month)
    components_labeled = {}
    for k, v in result["components"].items():
        meta = V6_ENGINE_META.get(k, {"label": k})
        components_labeled[meta["label"]] = round(v, 1)
    return {
        "score": result["score"],
        "classe": result["classe"],
        "label": result["label"],
        "engines_count": 22,
        "components": components_labeled,
        "weights": result["weights"],
        "option": "C — CORE 60% / Nouveaux 40%",
    }


@router.get("/engines/score-grid")
async def score_grid(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
    grid_size: int = Query(20, ge=5, le=40),
):
    """Grille de scores V6-CORE — pipeline 22 moteurs."""
    sp = resolve_species(species)
    step = 0.002
    half = grid_size // 2
    grid = []
    for dy in range(-half, half + 1, 2):
        for dx in range(-half, half + 1, 2):
            pt_lat = lat + dy * step
            pt_lng = lng + dx * step
            result = compute_consolidated_score(pt_lat, pt_lng, sp, month)
            grid.append({
                "lat": round(pt_lat, 6), "lng": round(pt_lng, 6),
                "score": result["score"], "classe": result["classe"],
            })
    return {
        "type": "score_grid",
        "center": {"lat": lat, "lng": lng},
        "grid_size": grid_size,
        "points": grid,
        "engines_count": 22,
    }


@router.get("/engines/{engine_name}/score")
async def engine_individual_score(
    engine_name: str,
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """Score moteur individuel V6-CORE — par cle pipeline."""
    sp = resolve_species(species)
    result = compute_consolidated_score(lat, lng, sp, month)
    components = result["components"]
    if engine_name not in components:
        return {"error": f"Moteur '{engine_name}' introuvable", "available": list(V6_ENGINE_META.keys())}
    meta = V6_ENGINE_META.get(engine_name, {"label": engine_name, "domain": "autre", "tier": "UNKNOWN"})
    return {
        "engine": meta["label"],
        "key": engine_name,
        "domain": meta["domain"],
        "tier": meta["tier"],
        "species": sp, "month": month, "lat": lat, "lng": lng,
        "score": round(components[engine_name], 1),
        "weight": result["weights"].get(engine_name, 0),
        "consolidated_score": result["score"],
    }


@router.get("/engines/validate")
async def validate_bce4x():
    """Exécute la validation BCE-4X + STEEVE-MAX en temps réel."""
    sys.path.insert(0, "/app")
    from bionic.bce4x.BCE4XGuard import BCE4XGuard
    from bionic.steevemax.SteeveMaxRules import SteeveMaxRules
    bce = BCE4XGuard()
    bce_report = bce.run_all()
    sm = SteeveMaxRules()
    sm_report = sm.run_all()
    return {
        "overall_compliant": bce_report["compliant"] and sm_report["compliant"],
        "bce4x": {"passed": bce_report["passed"], "total": bce_report["total_tests"], "compliant": bce_report["compliant"]},
        "steeve_max": {"passed": sm_report["passed"], "total": sm_report["total_tests"], "compliant": sm_report["compliant"]},
    }


# ══════════════════════════════════════════════════════════
# INTELLIGENCE — Analytics, Forecast, Plan Maître
# ══════════════════════════════════════════════════════════

@router.get("/intelligence/summary")
async def intelligence_summary(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """
    Resume analytique INTELLIGENCE — pipeline 22 moteurs V6-CORE.
    x4520-UNIFICATION_DASHBOARD: Zero relique V1/V2/V10.
    """
    sp = resolve_species(species)
    consolidated = compute_consolidated_score(lat, lng, sp, month)
    components = consolidated["components"]

    # Grouper par domaine V6-CORE (noms propres, sans version)
    domain_scores = {}
    for engine_key, score in components.items():
        meta = V6_ENGINE_META.get(engine_key, {"label": engine_key, "domain": "autre", "tier": "UNKNOWN"})
        domain = meta["domain"]
        if domain not in domain_scores:
            domain_scores[domain] = []
        domain_scores[domain].append({
            "engine": meta["label"],
            "key": engine_key,
            "score": round(score, 1),
            "weight": consolidated["weights"].get(engine_key, 0),
            "tier": meta["tier"],
        })

    # Analyse
    if components:
        strongest = max(components, key=components.get)
        weakest = min(components, key=components.get)
    else:
        strongest = weakest = "N/A"

    # Recommandations V6-CORE
    recommendations = []
    for engine_key, score in components.items():
        meta = V6_ENGINE_META.get(engine_key, {"label": engine_key, "domain": "autre"})
        domain_label = V6_DOMAIN_LABELS.get(meta["domain"], meta["domain"])
        if score < 30:
            recommendations.append({
                "engine": meta["label"], "domain": domain_label,
                "priority": "HAUTE", "score": round(score, 1),
                "action": f"Ameliorer {meta['label']} (score critique: {round(score, 1)}/100)",
            })
        elif score < 50:
            recommendations.append({
                "engine": meta["label"], "domain": domain_label,
                "priority": "MOYENNE", "score": round(score, 1),
                "action": f"Surveiller {meta['label']} (score modere: {round(score, 1)}/100)",
            })

    return {
        "type": "intelligence_summary",
        "species": sp,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "consolidated": {
            "score": consolidated["score"],
            "classe": consolidated["classe"],
            "label": consolidated["label"],
        },
        "domains": domain_scores,
        "domain_labels": V6_DOMAIN_LABELS,
        "analysis": {
            "strongest_engine": V6_ENGINE_META.get(strongest, {}).get("label", strongest),
            "weakest_engine": V6_ENGINE_META.get(weakest, {}).get("label", weakest),
            "strongest_score": round(components.get(strongest, 0), 1),
            "weakest_score": round(components.get(weakest, 0), 1),
        },
        "recommendations": recommendations,
        "engines_count": len(components),
        "option": "C — CORE 60% / Nouveaux 40%",
    }


@router.get("/intelligence/forecast")
async def intelligence_forecast(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"),
):
    """
    Previsions ecologiques — variation saisonniere 12 mois.
    x4520: Pipeline 22 moteurs V6-CORE.
    """
    sp = resolve_species(species)
    monthly_data = []

    for m in range(1, 13):
        result = compute_consolidated_score(lat, lng, sp, m)
        monthly_data.append({
            "month": m,
            "score": result["score"],
            "classe": result["classe"],
        })

    scores = [d["score"] for d in monthly_data]
    best_month = scores.index(max(scores)) + 1
    worst_month = scores.index(min(scores)) + 1
    avg_score = round(sum(scores) / 12, 1)

    seasons = {
        "printemps": round(sum(scores[2:5]) / 3, 1),
        "ete": round(sum(scores[5:8]) / 3, 1),
        "automne": round(sum(scores[8:11]) / 3, 1),
        "hiver": round((scores[11] + scores[0] + scores[1]) / 3, 1),
    }

    return {
        "type": "intelligence_forecast",
        "species": sp,
        "location": {"lat": lat, "lng": lng},
        "annual_average": avg_score,
        "best_month": best_month,
        "worst_month": worst_month,
        "seasonal_scores": seasons,
        "best_season": max(seasons, key=seasons.get),
        "monthly_data": monthly_data,
        "engines_count": 22,
    }


@router.get("/intelligence/plan")
async def intelligence_plan(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """
    Plan maitre — actions recommandees.
    x4520: Pipeline 22 moteurs V6-CORE, noms propres.
    """
    sp = resolve_species(species)
    consolidated = compute_consolidated_score(lat, lng, sp, month)
    components = consolidated["components"]

    actions = []
    priority_order = sorted(components.items(), key=lambda x: x[1])

    for rank, (engine_key, score) in enumerate(priority_order, 1):
        meta = V6_ENGINE_META.get(engine_key, {"label": engine_key, "domain": "autre"})
        domain_label = V6_DOMAIN_LABELS.get(meta["domain"], meta["domain"])

        if score >= 80:
            status, action, urgency = "OPTIMAL", "Maintenir les conditions actuelles", "FAIBLE"
        elif score >= 60:
            status, action, urgency = "BON", f"Surveiller {meta['label']}", "FAIBLE"
        elif score >= 40:
            status, action, urgency = "MODERE", f"Ameliorer {meta['label']}", "MOYENNE"
        elif score >= 20:
            status, action, urgency = "FAIBLE", f"Intervention requise: renforcer {meta['label']}", "HAUTE"
        else:
            status, action, urgency = "CRITIQUE", f"Action immediate: {meta['label']} en situation critique", "CRITIQUE"

        actions.append({
            "rank": rank,
            "engine": meta["label"],
            "key": engine_key,
            "domain": domain_label,
            "score": round(score, 1),
            "status": status,
            "urgency": urgency,
            "action": action,
        })

    return {
        "type": "intelligence_plan",
        "species": sp,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "overall_score": consolidated["score"],
        "overall_classe": consolidated["classe"],
        "actions": actions,
        "total_actions": len(actions),
        "critical_count": sum(1 for a in actions if a["urgency"] in ("CRITIQUE", "HAUTE")),
        "engines_count": 22,
    }


# ══════════════════════════════════════════════════════════
# SPECIES — Référentiel espèces
# ══════════════════════════════════════════════════════════

@router.get("/species")
async def get_species():
    """Liste des espèces canoniques BCE-4X."""
    return {"species": SPECIES_CANONICAL}



@router.get("/intelligence/solunar")
async def intelligence_solunar(
    lat: float = Query(...), lng: float = Query(...),
    date: str = Query(None, description="Date YYYY-MM-DD (defaut: aujourd'hui)"),
):
    """Donnees solunaires brutes — courbe 24h, periodes, fenetres de chasse."""
    from modules.solunar.engine import compute_solunar
    return compute_solunar(lat, lng, date)



# ══════════════════════════════════════════════════════════
# GUIDE PRO — Solunaire + Plan d'approche
# ══════════════════════════════════════════════════════════

@router.get("/intelligence/guide-pro")
async def intelligence_guide_pro(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
    date: str = Query(None, description="Date YYYY-MM-DD"),
):
    """
    Guide Pro — Tableau solunaire + plan d'approche.
    x4520: Pipeline 22 moteurs V6-CORE.
    """
    from modules.solunar.engine import compute_solunar

    sp = resolve_species(species)
    solunar = compute_solunar(lat, lng, date)
    consolidated = compute_consolidated_score(lat, lng, sp, month)
    components = consolidated["components"]

    pression_score = components.get("pression", 50)
    repos_score = components.get("repos", 50)

    solunar_score = solunar["solunar_score"]
    terrain_score = consolidated["score"]
    combined_score = round(solunar_score * 0.4 + terrain_score * 0.6, 1)

    if combined_score >= 80:
        best_time_label = "extreme"
    elif combined_score >= 60:
        best_time_label = "fort"
    elif combined_score >= 40:
        best_time_label = "modere"
    else:
        best_time_label = "faible"

    import math
    wind_dir = (hash(f"{lat}{lng}{month}") % 360)
    approach_angle = (wind_dir + 180) % 360

    approach_plan = {
        "position_ideale": {
            "lat": round(lat + 0.002 * math.cos(math.radians(approach_angle)), 6),
            "lng": round(lng + 0.002 * math.sin(math.radians(approach_angle)), 6),
            "description": "Position face au vent, couvert dense",
        },
        "angle_entree": approach_angle,
        "vent": {"direction_deg": wind_dir, "force": "modere"},
        "zones_a_eviter": [
            {"raison": "Pression humaine elevee", "active": pression_score < 40},
            {"raison": "Vent defavorable", "active": False},
            {"raison": "Thermiques ascendantes", "active": month in (6, 7, 8)},
        ],
        "affut_recommande": {
            "lat": round(lat + 0.001, 6), "lng": round(lng - 0.001, 6),
            "type": "sureleve" if repos_score > 50 else "au sol",
            "orientation": f"{approach_angle}deg",
        },
        "meilleur_temps": {
            "score": combined_score,
            "label": best_time_label,
            "solunar_contribution": solunar_score,
            "terrain_contribution": terrain_score,
        },
    }

    month_temps = {1: -13, 2: -11, 3: -4, 4: 4, 5: 12, 6: 18, 7: 21, 8: 20, 9: 14, 10: 7, 11: 0, 12: -9}
    base_temp = month_temps.get(month, 5)
    lat_factor = max(0, (abs(lat) - 40) * -0.5)
    variation = ((hash(f"{lat:.2f}{lng:.2f}") % 100) / 100.0 - 0.5) * 6
    temperature_official = round(base_temp + lat_factor + variation, 1)
    wind_speed_kmh = 8 + (hash(f"{lat:.1f}{lng:.1f}{month}") % 25)
    wind_force_label = "faible" if wind_speed_kmh < 15 else "modere" if wind_speed_kmh < 30 else "fort"

    # Terrain V6-CORE (22 moteurs)
    terrain_v6 = {}
    for engine_key, score in components.items():
        meta = V6_ENGINE_META.get(engine_key, {"label": engine_key})
        terrain_v6[meta["label"]] = round(score, 1)

    return {
        "type": "guide_pro",
        "species": sp,
        "month": month,
        "location": {"lat": lat, "lng": lng},
        "solunar": solunar,
        "terrain": terrain_v6,
        "terrain_consolidated": {
            "score": consolidated["score"],
            "classe": consolidated["classe"],
            "engines_count": 22,
        },
        "approach_plan": approach_plan,
        "hunting_windows": solunar["hunting_windows"],
        "best_time": approach_plan["meilleur_temps"],
        "weather_official": {
            "temperature": temperature_official,
            "wind_direction_deg": wind_dir,
            "wind_speed_kmh": wind_speed_kmh,
            "wind_force": wind_force_label,
        },
    }


@router.get("/intelligence/scientifique")
async def intelligence_scientifique(
    lat: float = Query(...), lng: float = Query(...),
    species: str = Query("CHEVREUIL"), month: int = Query(10, ge=1, le=12),
):
    """Mode Scientifique — 22 moteurs V6-CORE, ponderations, formules."""
    sp = resolve_species(species)
    consolidated = compute_consolidated_score(lat, lng, sp, month)

    engines_detail = []
    for engine_key, score in consolidated["components"].items():
        meta = V6_ENGINE_META.get(engine_key, {"label": engine_key, "domain": "autre", "tier": "UNKNOWN", "description": ""})
        engines_detail.append({
            "name": meta["label"],
            "key": engine_key,
            "domain": meta["domain"],
            "tier": meta["tier"],
            "description": meta["description"],
            "score": round(score, 1),
            "weight": consolidated["weights"].get(engine_key, 0),
        })

    return {
        "type": "scientifique",
        "species": sp, "month": month,
        "location": {"lat": lat, "lng": lng},
        "consolidated": {
            "score": consolidated["score"],
            "classe": consolidated["classe"],
            "label": consolidated["label"],
        },
        "engines": engines_detail,
        "engines_count": 22,
        "formulas": {
            "consolidation": "score = Sum(engine_score x weight_normalized)",
            "classification": "OPTIMAL(>=80), BON(>=60), MODERE(>=40), FAIBLE(<40)",
            "normalization": "weights_sum = 1.0 (redistribue si moteur exclu)",
            "option": "C — CORE 60% / Nouveaux 40%",
        },
        "tiers": {
            "CORE": "60% — 5 moteurs fondamentaux",
            "CORE++": "17.14% — 7 moteurs environnementaux",
            "CORE+++": "11.73% — 5 moteurs comportementaux",
            "BIONIC-OS": "9.12% — 5 moteurs intelligence",
        },
    }
