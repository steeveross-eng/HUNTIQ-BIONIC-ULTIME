"""
corridor_pipeline_preview_router.py — Preview institutionnel X200-P1 (lecture seule)
======================================================================================
Phase : PHASE_X200_P1_PREVIEW_ET_PREPARATION_Ω
Commandant STEEVE-MAX

Endpoint orchestrateur qui enchaîne les 5 engines P0 pour un waypoint donné.
AUCUNE modification de données, AUCUN impact rendu, AUCUN accès V30 en écriture.

GET  /api/v7-ultime/corridor-pipeline-preview/status
POST /api/v7-ultime/corridor-pipeline-preview
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from engines.wildlife_behavior_omega.router import (
    get_species_profile, locomotion_constraints,
)
from engines.eco_zones_omega.router import (
    get_20_saline_sources, build_vital_zones_hierarchy, classify_habitat,
)
from engines.hydro_topo_omega.router import (
    hydro_attraction_bonus, compute_terrain_aware_boost, fuse_multiscale_dem,
)
from engines.reseau_veineux_omega.router import (
    classify_corridor, validate_functional_radius, enforce_vital_zone_rule,
    CORRIDOR_LEVELS_V7,
)
from engines.bio_scoring_omega.router import score_8_factors, FACTOR_WEIGHTS_V7

router = APIRouter(
    prefix="/api/v7-ultime/corridor-pipeline-preview",
    tags=["CORRIDOR_PIPELINE_PREVIEW_X200_P1_READONLY"],
)


@router.get("/status")
async def preview_status():
    return JSONResponse({
        "phase": "X200-P1-PREVIEW",
        "mode": "READ_ONLY",
        "engines_chained": [
            "wildlife_behavior_omega",
            "eco_zones_omega",
            "hydro_topo_omega",
            "reseau_veineux_omega",
            "bio_scoring_omega",
        ],
        "smoother_touched": False,
        "rendu_modified": False,
        "v30_read_write": False,
        "waypoint_canonique": [48.206657, -68.382422],
    })


@router.post("")
async def preview(payload: Optional[Dict[str, Any]] = None):
    """Enchaîne les 5 engines P0 sur un waypoint et retourne un bundle JSON consolidé."""
    p = payload or {}
    lat = float(p.get("lat", 48.206657))
    lon = float(p.get("lon", -68.382422))
    species = str(p.get("species", "CERF"))
    season = str(p.get("season", "automne"))
    water_points: List[List[float]] = p.get("water_points", []) or []
    raw_vital_zones: List[Dict[str, Any]] = p.get("vital_zones", []) or []
    terrain_signals: Dict[str, bool] = p.get("terrain_signals", {}) or {}
    dem_multiscale: Dict[str, float] = p.get("dem_multiscale", {}) or {}
    radius_m: float = float(p.get("radius_m", 600))

    # ── 1) wildlife_behavior : profil + contraintes locomotion V7
    wb_profile = get_species_profile(species)
    wb_constraints = locomotion_constraints(species, season)
    affinity_hydro = (wb_profile.get("profile", {}) or {}).get("affinite_hydro", 0.6)

    # ── 2) eco_zones : salines hiérarchisées + zones vitales triées
    ez_salines = get_20_saline_sources()
    ez_hierarchy = build_vital_zones_hierarchy(raw_vital_zones)
    # Score habitat heuristique basé sur densité zones vitales fournies
    ez_habitat_score = min(100.0, 20.0 * sum(z["count"] for z in ez_hierarchy
                                             if z.get("count", 0) > 0))
    ez_habitat = classify_habitat(ez_habitat_score)

    # ── 3) hydro_topo : bonus attractif + terrain boost + DEM fused
    ht_hydro_bonus = hydro_attraction_bonus([lat, lon], water_points, affinity_hydro)
    ht_terrain_boost = compute_terrain_aware_boost(terrain_signals)
    ht_dem_fused = fuse_multiscale_dem(dem_multiscale)

    # ── 4) reseau_veineux : validation rayon + règle ≥2 zones
    # Détecte connexions ≥1 zone vitale (simplifié pour preview)
    connections = [z for z in raw_vital_zones if z.get("type") and z.get("lat") is not None]
    rv_radius = validate_functional_radius(radius_m)
    rv_vital_rule = enforce_vital_zone_rule(connections)

    # ── 5) bio_scoring : scoring 8-facteurs V7
    # Les subscores proviennent idéalement de V30 miroir (flag OFF en X200-P0) ;
    # en preview, on accepte ceux fournis explicitement sinon proxy heuristique.
    subscores = p.get("subscores") or {
        "ecl":            p.get("ecl", 0.6),
        "canopy":         p.get("canopy", 0.6),
        "pressure_human": p.get("pressure_human", 0.7),
        "food_refuge":    p.get("food_refuge", 0.6),
        "topo_hydro":     round(min(1.0, (ht_hydro_bonus / 0.35) * 0.5
                                       + (ht_terrain_boost - 1.0) / 0.95 * 0.5), 3),
        "regeneration":   p.get("regeneration", 0.5),
        "cost":           p.get("cost", 0.6),
        "from_type":      p.get("from_type", "salines"),
        "to_type":        p.get("to_type", "repos"),
        "n_cells":        int(p.get("n_cells", 15)),
    }
    bs_result = score_8_factors(subscores)
    rv_classification = classify_corridor(bs_result["score_0_100"])

    # Heuristique ≥2 zones (preview) : on utilise le hierarchy count
    zones_reelles = sum(1 for z in ez_hierarchy if z.get("count", 0) > 0)

    return JSONResponse({
        "phase": "X200-P1-PREVIEW",
        "mode": "READ_ONLY",
        "waypoint": {"lat": lat, "lon": lon},
        "species_requested": species,
        "season": season,
        "wildlife_behavior": {
            "v7_restored": wb_constraints.get("v7_restored", False),
            "species": wb_constraints.get("species"),
            "description": (wb_profile.get("profile", {}) or {}).get("description_corridor"),
            "constraints": wb_constraints,
        },
        "eco_zones": {
            "saline_sources_count": len(ez_salines),
            "saline_scores_distribution": {
                "5_critique": sum(1 for s in ez_salines if s["score"] == 5),
                "4_fort":     sum(1 for s in ez_salines if s["score"] == 4),
                "3_majeur":   sum(1 for s in ez_salines if s["score"] == 3),
                "2_modere":   sum(1 for s in ez_salines if s["score"] == 2),
                "1_faible":   sum(1 for s in ez_salines if s["score"] == 1),
            },
            "vital_zones_hierarchy": ez_hierarchy,
            "vital_zones_present_types": zones_reelles,
            "habitat_classification": ez_habitat,
        },
        "hydro_topo": {
            "inversion_corrected": True,
            "hydro_attraction_bonus": round(ht_hydro_bonus, 4),
            "terrain_aware_boost": round(ht_terrain_boost, 4),
            "dem_fused_multiscale": round(ht_dem_fused, 2),
            "affinity_hydro_applied": affinity_hydro,
        },
        "reseau_veineux": {
            "functional_radius": rv_radius,
            "vital_zone_rule": rv_vital_rule,
            "levels_v7": [l["level"] for l in CORRIDOR_LEVELS_V7],
            "classification": rv_classification,
        },
        "bio_scoring": {
            "score_0_100": bs_result["score_0_100"],
            "weights_v7": FACTOR_WEIGHTS_V7,
            "subscores_used": subscores,
        },
        "preview_contract": {
            "smoother_touched": False,
            "rendu_modified": False,
            "v30_read_write": False,
        },
    })
