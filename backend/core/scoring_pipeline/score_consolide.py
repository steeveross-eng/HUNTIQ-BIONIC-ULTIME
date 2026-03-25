"""
Score consolide BIONIC — Score ecologique multi-moteurs (22 moteurs)
=====================================================================
x4100: Integration scientifique des 17 nouveaux moteurs.
Option C: CORE 60%, Nouveaux 40% (directive STEEVE-MAX).

Integre:
  CORE (60%):
    ALIMENTATION-V1, REPOS-V1, CORRIDORS-V10, ALIMENTATION-V2, PRESSION-V1
  CORE++ (17.14%):
    HYDRO-V1, THERMAL-V1, NDVI-VEGETATION-V1, WEATHER-V1,
    TEMPORAL-V1, HABITAT-V1, ECOSYSTEM-V1
  CORE+++ (11.73%):
    BEHAVIOR-V1, RISK-V1, OPPORTUNITY-V1, ATTRACTORS-V1, SCENARIO-V1
  BIONIC-OS (9.12%):
    SIMULATION-V1, MULTI-SPECIES-V1, TRAJETS-V1, VISIBILITY-V1, LEARNING-V1

BCE-4X: Ponderations Option C certifiees par STEEVE-MAX.
"""
import math

from core.scoring_pipeline.common.constants import ENGINE_WEIGHTS
from core.scoring_pipeline.common.classification import classify, CLASSIFICATION_CONFIGS

# ── Imports directs des moteurs CORE ──
from core.scoring_pipeline.alimentation_v1.engine import analyze_single_point as alim_point
from core.scoring_pipeline.repos_v1.engine import analyze_single_point as repos_point
from core.scoring_pipeline.corridors_v10.engine import score_point_consolidated as corridor_point
from core.scoring_pipeline.alimentation_v2.engine import score_point_consolidated as alim_v2_point
from core.scoring_pipeline.pression_v1.engine import score_from_layers as pression_from_layers

# ── Imports directs des moteurs CORE++ ──
from core.scoring_pipeline.hydro_v1.engine import score_point_consolidated as hydro_point
from core.scoring_pipeline.thermal_v1.engine import score_point_consolidated as thermal_point
from core.scoring_pipeline.ndvi_vegetation_v1.engine import score_point_consolidated as ndvi_point
from core.scoring_pipeline.weather_v1.engine import score_point_consolidated as weather_point
from core.scoring_pipeline.temporal_v1.engine import score_point_consolidated as temporal_point
from core.scoring_pipeline.habitat_v1.engine import score_point_consolidated as habitat_point
from core.scoring_pipeline.ecosystem_v1.engine import score_point_consolidated as ecosystem_point

# ── Imports directs des moteurs CORE+++ ──
from core.scoring_pipeline.behavior_v1.engine import score_point_consolidated as behavior_point
from core.scoring_pipeline.risk_v1.engine import score_point_consolidated as risk_point
from core.scoring_pipeline.opportunity_v1.engine import score_point_consolidated as opportunity_point
from core.scoring_pipeline.attractors_v1.engine import score_point_consolidated as attractors_point
from core.scoring_pipeline.scenario_v1.engine import score_point_consolidated as scenario_point

# ── Imports directs des moteurs BIONIC-OS ──
from core.scoring_pipeline.simulation_v1.engine import score_point_consolidated as simulation_point
from core.scoring_pipeline.multi_species_v1.engine import score_point_consolidated as multi_species_point
from core.scoring_pipeline.trajets_v1.engine import score_point_consolidated as trajets_point
from core.scoring_pipeline.visibility_v1.engine import score_point_consolidated as visibility_point
from core.scoring_pipeline.learning_v1.engine import score_point_consolidated as learning_point

# ── Ponderations normalisees ──
ACTIVE_WEIGHTS = {k: v for k, v in ENGINE_WEIGHTS.items() if v > 0}
_TOTAL = sum(ACTIVE_WEIGHTS.values())
NORMALIZED_WEIGHTS = {k: v / _TOTAL for k, v in ACTIVE_WEIGHTS.items()}

# ── Mapping moteur → fonction de scoring ──
_ENGINE_FUNCTIONS = {
    "hydro": hydro_point,
    "thermal": thermal_point,
    "ndvi_vegetation": ndvi_point,
    "weather": weather_point,
    "temporal": temporal_point,
    "habitat": habitat_point,
    "ecosystem": ecosystem_point,
    "behavior": behavior_point,
    "risk": risk_point,
    "opportunity": opportunity_point,
    "attractors": attractors_point,
    "scenario": scenario_point,
    "simulation": simulation_point,
    "multi_species": multi_species_point,
    "trajets": trajets_point,
    "visibility": visibility_point,
    "learning": learning_point,
}


def compute_consolidated_score(lat, lng, species="CERF", month=10,
                                center_lat=None, center_lng=None,
                                include_corridors=True):
    """
    Score consolide multi-moteurs pour un point.
    x4100: Integre 22 moteurs (5 CORE + 17 nouveaux).
    Option C: CORE 60%, Nouveaux 40%.
    """
    # Appels directs ALIMENTATION-V1 et REPOS-V1
    alim = alim_point(lat, lng, species, month)
    repos = repos_point(lat, lng, species, month)

    c_lat = center_lat or lat
    c_lng = center_lng or lng

    # Extraction layers pour exclusion eau + pression
    layers = alim.get("layers", {})
    hydro_layers = layers.get("hydrographie", {})
    is_water = hydro_layers.get("zone_humide", 0) == 1 and hydro_layers.get("distance_eau_m", 500) < 20

    # Appel direct PRESSION-V1 (via layers pre-chargees)
    pression_score = pression_from_layers(layers)

    # Appel direct CORRIDORS-V10
    corridor_score = corridor_point(lat, lng, c_lat, c_lng, species, month) if include_corridors else 0.0

    # Appel direct ALIMENTATION-V2
    alim_v2_score = alim_v2_point(lat, lng, c_lat, c_lng, species, month)

    # Scores des 5 moteurs CORE
    scores = {
        "alimentation": alim["score_alimentation"],
        "repos": repos["score_repos"],
        "corridors_v10": round(corridor_score, 1),
        "alimentation_v2": round(alim_v2_score, 1),
        "pression": round(pression_score, 1),
    }

    # Scores des 17 nouveaux moteurs
    for engine_key, engine_fn in _ENGINE_FUNCTIONS.items():
        scores[engine_key] = round(engine_fn(lat, lng, c_lat, c_lng, species, month), 1)

    # Ponderations dynamiques
    if include_corridors:
        weights = NORMALIZED_WEIGHTS
    else:
        active = {k: v for k, v in ENGINE_WEIGHTS.items() if k != "corridors_v10" and v > 0}
        total = sum(active.values())
        weights = {k: v / total for k, v in active.items()}

    # Exclusion eau BCE-4X
    if is_water:
        return {
            "score": 0.0, "classe": "EXCLU", "label": "Surface d'eau",
            "color": "#1E3A5F", "species": species.upper(), "month": month,
            "is_water": True,
            "components": {k: 0.0 for k in scores},
            "weights": {k: round(v, 3) for k, v in weights.items()},
            "tracability": {
                "exclusion": "BCE-4X water surface",
                "engines_active": list(weights.keys()),
                "engines_pending": [],
                "corridors_v10_integrated": include_corridors,
                "x4100_integrated": True,
            },
        }

    # Score consolide (22 moteurs)
    consolidated = sum(
        scores.get(k, 0) * weights.get(k, 0)
        for k in weights if k in scores
    )
    consolidated = max(0, min(100, consolidated))

    # Classification via common/classification.py
    cls_result = classify(consolidated, "SCORE_CONSOLIDE")
    classe = cls_result["classe"]
    label = cls_result["label_fr"]
    color = cls_result["color"]

    return {
        "score": round(consolidated, 1),
        "classe": classe, "label": label, "color": color,
        "species": species.upper(), "month": month,
        "components": scores,
        "weights": {k: round(v, 3) for k, v in weights.items()},
        "tracability": {
            **{f"{k}_score": v for k, v in scores.items()},
            "engines_active": list(weights.keys()),
            "engines_pending": [],
            "corridors_v10_integrated": include_corridors,
            "x4100_integrated": True,
            "option": "C — CORE 60% / Nouveaux 40%",
        },
    }


def compute_heatmap_grid(
    center_lat, center_lng,
    species="CERF", month=10,
    grid_size=20, side_m=2000.0,
    include_corridors=True,
):
    """
    Grille de scores consolides pour le heatmap.
    x4100: 22 moteurs integres (Option C).
    """
    half = side_m / 2.0
    lat_step = (side_m / grid_size) / 111320.0
    lng_step = (side_m / grid_size) / (111320.0 * math.cos(math.radians(center_lat)))

    lat_start = center_lat - half / 111320.0
    lng_start = center_lng - half / (111320.0 * math.cos(math.radians(center_lat)))

    points = []
    scores = []

    for r in range(grid_size):
        for c in range(grid_size):
            lat = lat_start + (r + 0.5) * lat_step
            lng = lng_start + (c + 0.5) * lng_step
            result = compute_consolidated_score(
                lat, lng, species, month,
                center_lat=center_lat, center_lng=center_lng,
                include_corridors=include_corridors,
            )
            points.append({
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "score": result["score"],
                "classe": result["classe"],
                "color": result["color"],
            })
            scores.append(result["score"])

    avg_score = sum(scores) / len(scores) if scores else 0
    cls_result = classify(avg_score, "SCORE_CONSOLIDE")

    active_w = NORMALIZED_WEIGHTS if include_corridors else {
        k: v for k, v in NORMALIZED_WEIGHTS.items() if k != "corridors_v10"
    }

    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "species": species.upper(),
        "month": month,
        "grid_size": grid_size,
        "total_points": len(points),
        "score_avg": round(avg_score, 1),
        "score_min": round(min(scores), 1) if scores else 0,
        "score_max": round(max(scores), 1) if scores else 0,
        "overall_classe": cls_result["classe"],
        "overall_label": cls_result["label_fr"],
        "weights": {k: round(v, 3) for k, v in active_w.items()},
        "engines_integrated": list(active_w.keys()),
        "total_engines": len(active_w),
        "x4100_option": "C — CORE 60% / Nouveaux 40%",
        "corridors_v10_included": include_corridors,
        "points": points,
    }
