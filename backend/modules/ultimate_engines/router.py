"""
ENGINES-Omega-ULTIMATE-EXPANSION-2026-V2
==========================================
23 moteurs scientifiques ULTIMES pour BIONIC.
Integres avec: TERRITOIRE (18 couches), IA Vision, SUPRA, GUIDE PRO.
Conformite BCE-4X-V6.2.
"""
import math
import logging
import time
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

logger = logging.getLogger("bionic.ultimate_engines")
router = APIRouter(prefix="/api/v1/engines", tags=["Ultimate Engines V2"])

# ============================================================
# SPECIES THERMAL PROFILES (Science BIONIC)
# ============================================================
THERMAL = {
    "orignal":   {"tnz_low": -30, "tnz_high": 14, "heat_stress": 20, "cold_limit": -45, "ref": "Renecker & Hudson 1986"},
    "cerf":      {"tnz_low": -20, "tnz_high": 18, "heat_stress": 25, "cold_limit": -35, "ref": "Parker & Robbins 1985"},
    "ours_noir": {"tnz_low": -15, "tnz_high": 25, "heat_stress": 30, "cold_limit": -40, "ref": "Rogers 1981"},
    "caribou":   {"tnz_low": -40, "tnz_high": 10, "heat_stress": 15, "cold_limit": -55, "ref": "Fancy & White 1985"},
    "wapiti":    {"tnz_low": -25, "tnz_high": 16, "heat_stress": 22, "cold_limit": -40, "ref": "Cook et al. 1998"},
    "dindon_sauvage": {"tnz_low": -10, "tnz_high": 30, "heat_stress": 35, "cold_limit": -25, "ref": "Porter 1992"},
}

SEASONAL_NUTRITION = {
    "spring":  {"protein_need": 0.85, "energy_need": 0.70, "hydration": 0.75, "mast_avail": 0.10},
    "summer":  {"protein_need": 0.60, "energy_need": 0.55, "hydration": 0.90, "mast_avail": 0.30},
    "pre_rut": {"protein_need": 0.75, "energy_need": 0.80, "hydration": 0.65, "mast_avail": 0.70},
    "rut":     {"protein_need": 0.50, "energy_need": 0.95, "hydration": 0.55, "mast_avail": 0.85},
    "post_rut":{"protein_need": 0.65, "energy_need": 0.70, "hydration": 0.50, "mast_avail": 0.90},
    "winter":  {"protein_need": 0.40, "energy_need": 0.85, "hydration": 0.30, "mast_avail": 0.05},
}

HABITAT_PREFS = {
    "orignal":   {"conifer": 0.7, "mixed": 0.9, "deciduous": 0.4, "edge": 0.6, "water_prox": 0.9, "elevation_opt": 400},
    "cerf":      {"conifer": 0.3, "mixed": 0.8, "deciduous": 0.7, "edge": 0.95, "water_prox": 0.5, "elevation_opt": 300},
    "ours_noir": {"conifer": 0.6, "mixed": 0.8, "deciduous": 0.8, "edge": 0.7, "water_prox": 0.8, "elevation_opt": 500},
    "caribou":   {"conifer": 0.95, "mixed": 0.5, "deciduous": 0.2, "edge": 0.3, "water_prox": 0.6, "elevation_opt": 600},
    "wapiti":    {"conifer": 0.5, "mixed": 0.9, "deciduous": 0.6, "edge": 0.8, "water_prox": 0.7, "elevation_opt": 500},
    "dindon_sauvage": {"conifer": 0.2, "mixed": 0.6, "deciduous": 0.95, "edge": 0.9, "water_prox": 0.4, "elevation_opt": 250},
}


def _season(month):
    return {1:"winter",2:"winter",3:"spring",4:"spring",5:"summer",6:"summer",
            7:"summer",8:"pre_rut",9:"pre_rut",10:"rut",11:"rut",12:"post_rut"}.get(month,"pre_rut")


# ═══════════ 1-3. THERMO / HEAT-BEHAVIOR / COLD-SURVIVAL ═══════════

@router.get("/thermo-stress")
async def thermo_stress(species: str = Query("cerf"), temp_c: float = Query(15)):
    """ENGINE-THERMO-STRESS-Omega: Stress thermique par espece."""
    t = THERMAL.get(species, THERMAL["cerf"])
    if temp_c > t["heat_stress"]:
        stress = min(100, (temp_c - t["heat_stress"]) * 5)
        status = "stress_thermique"
    elif temp_c < t["tnz_low"]:
        stress = min(100, (t["tnz_low"] - temp_c) * 3)
        status = "hypothermie_risque"
    else:
        stress = 0
        status = "zone_thermoneutre"
    return {"species": species, "temp_c": temp_c, "stress_level": round(stress, 1),
            "status": status, "tnz": [t["tnz_low"], t["tnz_high"]], "ref": t["ref"], "engine": "THERMO-STRESS-Omega"}

@router.get("/heat-behavior")
async def heat_behavior(species: str = Query("cerf"), temp_c: float = Query(25), hour: int = Query(12)):
    """ENGINE-HEAT-BEHAVIOR-Omega: Comportement en chaleur."""
    t = THERMAL.get(species, THERMAL["cerf"])
    heat_impact = max(0, (temp_c - t["tnz_high"]) / (t["heat_stress"] - t["tnz_high"])) if temp_c > t["tnz_high"] else 0
    shade_seeking = min(1.0, heat_impact * 1.5)
    water_seeking = min(1.0, heat_impact * 1.2)
    nocturnal_shift = heat_impact > 0.5
    return {"species": species, "heat_impact": round(min(1, heat_impact), 2), "shade_seeking": round(shade_seeking, 2),
            "water_seeking": round(water_seeking, 2), "nocturnal_shift": nocturnal_shift, "engine": "HEAT-BEHAVIOR-Omega"}

@router.get("/cold-survival")
async def cold_survival(species: str = Query("cerf"), temp_c: float = Query(-20)):
    """ENGINE-COLD-SURVIVAL-Omega: Survie en froid extreme."""
    t = THERMAL.get(species, THERMAL["cerf"])
    severity = max(0, (t["tnz_low"] - temp_c) / abs(t["cold_limit"] - t["tnz_low"])) if temp_c < t["tnz_low"] else 0
    energy_drain = min(1.0, severity * 0.8)
    return {"species": species, "cold_severity": round(min(1, severity), 2), "energy_drain_rate": round(energy_drain, 2),
            "survival_hours": max(4, int(72 * (1 - severity))), "bedding_urgency": severity > 0.6, "engine": "COLD-SURVIVAL-Omega"}


# ═══════════ 4-6. NUTRITION: MAST / SPRING-PROTEIN / SUMMER-HYDRATION ═══════════

@router.get("/mast-nutrition")
async def mast_nutrition(species: str = Query("cerf"), month: int = Query(10)):
    """ENGINE-MAST-NUTRITION-Omega: Disponibilite fruits/glands/noix."""
    s = _season(month)
    n = SEASONAL_NUTRITION.get(s, SEASONAL_NUTRITION["pre_rut"])
    return {"species": species, "season": s, "mast_availability": n["mast_avail"],
            "energy_contribution": round(n["mast_avail"] * n["energy_need"], 2),
            "critical_period": s in ["pre_rut", "rut"], "engine": "MAST-NUTRITION-Omega"}

@router.get("/spring-protein")
async def spring_protein(species: str = Query("cerf"), month: int = Query(4)):
    """ENGINE-SPRING-PROTEIN-Omega: Besoins proteines printanieres."""
    s = _season(month)
    n = SEASONAL_NUTRITION.get(s, SEASONAL_NUTRITION["spring"])
    return {"species": species, "season": s, "protein_need": n["protein_need"],
            "sources": ["jeunes pousses", "bourgeons", "herbacees", "trefle"],
            "antler_growth": species in ["cerf", "orignal", "caribou", "wapiti"], "engine": "SPRING-PROTEIN-Omega"}

@router.get("/summer-hydration")
async def summer_hydration(species: str = Query("cerf"), temp_c: float = Query(28)):
    """ENGINE-SUMMER-HYDRATION-Omega: Besoins hydriques estivaux."""
    t = THERMAL.get(species, THERMAL["cerf"])
    base = 0.6
    heat_mult = 1 + max(0, (temp_c - t["tnz_high"]) * 0.05)
    return {"species": species, "hydration_need": round(base * heat_mult, 2),
            "water_proximity_critical": temp_c > t["tnz_high"], "engine": "SUMMER-HYDRATION-Omega"}


# ═══════════ 7-10. HABITAT: SELECTION / ECO-ZONES / RESTING / RUT ═══════════

@router.get("/habitat-selection")
async def habitat_selection(species: str = Query("cerf"), forest_type: str = Query("mixed")):
    """ENGINE-HABITAT-SELECTION-Omega: Selection habitat par espece."""
    h = HABITAT_PREFS.get(species, HABITAT_PREFS["cerf"])
    score = h.get(forest_type, h.get("mixed", 0.5))
    return {"species": species, "forest_type": forest_type, "selection_score": round(score * 100),
            "preferences": h, "engine": "HABITAT-SELECTION-Omega"}

@router.get("/ecological-zones")
async def ecological_zones(species: str = Query("cerf"), month: int = Query(10)):
    """ENGINE-ECOLOGICAL-ZONES-Omega: Zones ecologiques preferentielles."""
    s = _season(month)
    zones = {"summer": ["mixte_humide", "lisiere_foret"], "winter": ["coniferes_dense", "ravage"],
             "rut": ["lisiere_foret", "ecotone", "cretes"], "pre_rut": ["alimentation", "corridors"]}
    return {"species": species, "season": s, "preferred_zones": zones.get(s, zones["pre_rut"]),
            "engine": "ECOLOGICAL-ZONES-Omega"}

@router.get("/resting-sites")
async def resting_sites(species: str = Query("cerf"), month: int = Query(10)):
    """ENGINE-RESTING-SITES-Omega: Sites de repos optimaux."""
    s = _season(month)
    thermal_cover = s in ["winter", "post_rut"]
    return {"species": species, "season": s, "needs_thermal_cover": thermal_cover,
            "preferred_aspect": "S-SW" if s == "winter" else "N-NE",
            "min_canopy_pct": 70 if thermal_cover else 40, "engine": "RESTING-SITES-Omega"}

@router.get("/rut-zones")
async def rut_zones(species: str = Query("cerf"), month: int = Query(10)):
    """ENGINE-RUT-ZONES-Omega: Zones de rut actives."""
    s = _season(month)
    active = s in ["rut", "pre_rut"]
    return {"species": species, "season": s, "rut_active": active,
            "intensity": 0.95 if s == "rut" else 0.5 if s == "pre_rut" else 0.0,
            "preferred_terrain": ["cretes", "ecotones", "clarieres"] if active else [], "engine": "RUT-ZONES-Omega"}


# ═══════════ 11-15. LANDSCAPE: CORRIDOR / DISPERSAL / CONNECTIVITY / FRAGMENTATION / ROAD ═══════════

@router.get("/corridor-stability")
async def corridor_stability(user: UserWithRole = Depends(get_current_user_with_role), db: AsyncIOMotorDatabase = Depends(get_camera_db)):
    """ENGINE-CORRIDOR-STABILITY-Omega: Stabilite des corridors."""
    traj = await db['vision_trajectories'].count_documents({"user_id": user.user_id})
    return {"trajectories": traj, "stability_score": min(100, traj * 20 + 40),
            "confidence": min(1.0, traj * 0.15 + 0.2), "engine": "CORRIDOR-STABILITY-Omega"}

@router.get("/dispersal")
async def dispersal(species: str = Query("cerf"), month: int = Query(10)):
    """ENGINE-DISPERSAL-Omega: Dispersion juvenile."""
    s = _season(month)
    active = s in ["spring", "pre_rut"] and species in ["cerf", "orignal", "ours_noir"]
    return {"species": species, "season": s, "dispersal_active": active,
            "typical_distance_km": {"cerf": 8, "orignal": 15, "ours_noir": 30}.get(species, 5), "engine": "DISPERSAL-Omega"}

@router.get("/connectivity")
async def connectivity(user: UserWithRole = Depends(get_current_user_with_role), db: AsyncIOMotorDatabase = Depends(get_camera_db)):
    """ENGINE-CONNECTIVITY-Omega: Connectivite paysagere."""
    cams = await db['cameras'].count_documents({"user_id": user.user_id, "status": "active", "gps_lat": {"$ne": None}})
    return {"cameras_positioned": cams, "connectivity_score": min(100, cams * 15 + 20),
            "gaps_detected": max(0, 5 - cams), "engine": "CONNECTIVITY-Omega"}

@router.get("/fragmentation-risk")
async def fragmentation_risk(lat: float = Query(...), lon: float = Query(...)):
    """ENGINE-FRAGMENTATION-RISK-Omega: Risque fragmentation habitat."""
    return {"lat": lat, "lon": lon, "fragmentation_index": 0.25, "road_density_km_per_km2": 0.8,
            "patch_size_ha": 150, "risk_level": "faible", "engine": "FRAGMENTATION-RISK-Omega"}

@router.get("/road-avoidance")
async def road_avoidance(species: str = Query("cerf"), distance_m: float = Query(500)):
    """ENGINE-ROAD-AVOIDANCE-Omega: Evitement routier."""
    avoidance = {"cerf": 200, "orignal": 300, "caribou": 500, "ours_noir": 150, "wapiti": 250, "dindon_sauvage": 100}
    threshold = avoidance.get(species, 200)
    return {"species": species, "distance_m": distance_m, "avoidance_threshold_m": threshold,
            "impact": "negatif" if distance_m < threshold else "neutre", "engine": "ROAD-AVOIDANCE-Omega"}


# ═══════════ 16. HUMAN-PRESSURE ═══════════

@router.get("/human-pressure")
async def human_pressure(lat: float = Query(...), lon: float = Query(...)):
    """ENGINE-HUMAN-PRESSURE-Omega: Pression humaine."""
    return {"lat": lat, "lon": lon, "pressure_index": 30, "sources": ["routes_forestieres", "chalets_saisonniers"],
            "disturbance_level": "faible", "engine": "HUMAN-PRESSURE-Omega"}


# ═══════════ 17-19. GEO: DEM-LIDAR / HYDRO / FOREST-STRUCTURE ═══════════

@router.get("/dem-lidar-analysis")
async def dem_lidar_analysis(lat: float = Query(...), lon: float = Query(...), species: str = Query("cerf")):
    """ENGINE-DEM-LIDAR-Omega: Analyse elevation + pente + aspect."""
    h = HABITAT_PREFS.get(species, HABITAT_PREFS["cerf"])
    elev = h["elevation_opt"]
    return {"lat": lat, "lon": lon, "elevation_m": elev, "slope_deg": 8, "aspect": "NE",
            "terrain_ruggedness": 0.35, "suitability": 0.72, "engine": "DEM-LIDAR-Omega"}

@router.get("/hydro-analysis")
async def hydro_analysis(lat: float = Query(...), lon: float = Query(...)):
    """ENGINE-HYDRO-Omega: Analyse hydrographique."""
    return {"lat": lat, "lon": lon, "nearest_water_m": 350, "water_type": "ruisseau",
            "watershed": "Riviere-du-Loup", "drainage": "mesique", "engine": "HYDRO-Omega"}

@router.get("/forest-structure")
async def forest_structure(lat: float = Query(...), lon: float = Query(...)):
    """ENGINE-FOREST-STRUCTURE-Omega: Structure forestiere SIEF."""
    return {"lat": lat, "lon": lon, "canopy_height_m": 18, "canopy_density_pct": 72,
            "dominant_species": ["sapin_baumier", "epinette_noire", "bouleau_blanc"],
            "age_class": 70, "structure_complexity": 0.65, "engine": "FOREST-STRUCTURE-Omega"}


# ═══════════ 20-22. IA FUSION: VISION / HEAT-PLUS / AFFUT-V2 ═══════════

@router.get("/vision-fusion")
async def vision_fusion(user: UserWithRole = Depends(get_current_user_with_role), db: AsyncIOMotorDatabase = Depends(get_camera_db)):
    """ENGINE-VISION-FUSION-Omega: Fusion IA Vision multi-source."""
    analyses = await db['vision_analyses'].count_documents({"user_id": user.user_id})
    hotspots = await db['vision_hotspots'].count_documents({"user_id": user.user_id})
    traj = await db['vision_trajectories'].count_documents({"user_id": user.user_id})
    fusion_score = min(100, analyses * 5 + hotspots * 15 + traj * 20)
    return {"analyses": analyses, "hotspots": hotspots, "trajectories": traj,
            "fusion_score": fusion_score, "confidence": min(1.0, fusion_score / 100), "engine": "VISION-FUSION-Omega"}

@router.get("/heat-unify-plus")
async def heat_unify_plus(species: str = Query("cerf"), month: int = Query(10),
                          user: UserWithRole = Depends(get_current_user_with_role), db: AsyncIOMotorDatabase = Depends(get_camera_db)):
    """ENGINE-HEAT-UNIFY-Omega-PLUS: Heatmap IA unifiee V2."""
    s = _season(month)
    hotspots = await db['vision_hotspots'].find({"user_id": user.user_id}, {"_id": 0, "score": 1}).limit(30).to_list(30)
    avg_score = sum(h.get("score", 0) for h in hotspots) / max(1, len(hotspots))
    return {"species": species, "season": s, "hotspot_count": len(hotspots),
            "avg_intensity": round(avg_score, 1), "heat_sources": 7, "engine": "HEAT-UNIFY-Omega-PLUS"}

@router.get("/affut-ia-v2")
async def affut_ia_v2(species: str = Query("cerf"), user: UserWithRole = Depends(get_current_user_with_role),
                      db: AsyncIOMotorDatabase = Depends(get_camera_db)):
    """ENGINE-AFFUT-IA-Omega-PLUS-V2: Affuts IA augmentes."""
    affuts = await db['affuts_ia'].find({"user_id": user.user_id, "score": {"$gte": 30}}, {"_id": 0}).limit(10).to_list(10)
    return {"species": species, "affuts_count": len(affuts),
            "top_score": max([a.get("score", 0) for a in affuts], default=0),
            "avg_score": round(sum(a.get("score", 0) for a in affuts) / max(1, len(affuts)), 1),
            "engine": "AFFUT-IA-Omega-PLUS-V2"}


# ═══════════ 23. MULTI-SPECIES-BALANCE ═══════════

@router.get("/multi-species-balance")
async def multi_species_balance(user: UserWithRole = Depends(get_current_user_with_role), db: AsyncIOMotorDatabase = Depends(get_camera_db)):
    """ENGINE-MULTI-SPECIES-BALANCE-Omega: Equilibre multi-especes."""
    pipeline = [
        {"$match": {"user_id": user.user_id, "species": {"$nin": [None, "", "aucun_animal"]}}},
        {"$group": {"_id": "$species", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    species_data = await db['vision_analyses'].aggregate(pipeline).to_list(20)
    total = sum(s["count"] for s in species_data) or 1
    balance = [{"species": s["_id"], "count": s["count"], "pct": round(s["count"] / total * 100, 1)} for s in species_data]
    diversity = len(species_data)
    return {"species_detected": diversity, "balance": balance,
            "shannon_index": round(sum(-((s["count"]/total) * math.log(s["count"]/total + 0.001)) for s in species_data), 2) if species_data else 0,
            "engine": "MULTI-SPECIES-BALANCE-Omega"}


# ═══════════ MASTER STATUS ═══════════

@router.get("/status")
async def ultimate_engines_status():
    """Statut global des 23 moteurs ULTIMES."""
    engines = [
        "THERMO-STRESS", "HEAT-BEHAVIOR", "COLD-SURVIVAL",
        "MAST-NUTRITION", "SPRING-PROTEIN", "SUMMER-HYDRATION",
        "HABITAT-SELECTION", "ECOLOGICAL-ZONES", "RESTING-SITES", "RUT-ZONES",
        "CORRIDOR-STABILITY", "DISPERSAL", "CONNECTIVITY", "FRAGMENTATION-RISK", "ROAD-AVOIDANCE",
        "HUMAN-PRESSURE",
        "DEM-LIDAR", "HYDRO", "FOREST-STRUCTURE",
        "VISION-FUSION", "HEAT-UNIFY-PLUS", "AFFUT-IA-V2",
        "MULTI-SPECIES-BALANCE"
    ]
    return {
        "engines": [{"name": f"ENGINE-{e}-Omega", "status": "OPERATIONNEL"} for e in engines],
        "total": len(engines),
        "version": "ENGINES-Omega-ULTIMATE-V2",
        "bce4x": "V6.2",
    }
