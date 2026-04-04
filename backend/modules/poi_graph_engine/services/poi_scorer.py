"""
M2 — POI Scorer : Scoring multi-critere des POIs
====================================================
Directive x6900-M2 — Phase M2-B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

Criteres de scoring :
- Accessibilite (distance route, terrain) — poids 0.20
- Activite (frequence observations, cameras) — poids 0.30
- Strategique (position, visibilite, couverture) — poids 0.25
- Nutritionnel (fourrage, sol, attractivite) — poids 0.25 <-- VIA nutrition_v6_interface

ANTI-DOUBLON : NE recree PAS waypoint_scoring_engine.
ANTI-DOUBLON : NE recree PAS scoring_engine.
ANTI-DOUBLON NUTRITIONNEL : Tout enrichissement nutritionnel passe par nutrition_v6_interface.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

# Poids des criteres de scoring
WEIGHTS = {
    "accessibility": 0.20,
    "activity": 0.30,
    "strategic": 0.25,
    "nutrition": 0.25
}


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def _compute_accessibility_score(poi: Dict) -> float:
    """Score d'accessibilite base sur le type et l'altitude."""
    type_scores = {
        "stand": 0.7, "cache": 0.6, "point_eau": 0.5,
        "observation": 0.6, "camera": 0.8, "nourriture": 0.4,
        "ravage": 0.3, "corridor": 0.4, "saline": 0.5
    }
    base = type_scores.get(poi.get("type", ""), 0.5)
    alt = poi.get("altitude_m", 0)
    alt_penalty = min(0.2, alt / 5000.0) if alt > 500 else 0.0
    return max(0.0, min(1.0, base - alt_penalty))


def _compute_activity_score(poi: Dict) -> float:
    """Score d'activite base sur frequence et observations."""
    props = poi.get("properties", {})
    frequency = props.get("frequency", 0)
    confidence = props.get("confidence", 0.0)
    species_count = len(props.get("species_observed", []))

    freq_score = min(1.0, frequency / 50.0)
    species_score = min(1.0, species_count / 5.0)
    return (freq_score * 0.5 + confidence * 0.3 + species_score * 0.2)


def _compute_strategic_score(poi: Dict) -> float:
    """Score strategique base sur position et connexions."""
    connections = len(poi.get("connections", []))
    conn_score = min(1.0, connections / 8.0)

    type_strategic = {
        "stand": 0.9, "corridor": 0.8, "ravage": 0.7,
        "point_eau": 0.7, "cache": 0.6, "observation": 0.5,
        "camera": 0.4, "nourriture": 0.6, "saline": 0.65
    }
    type_score = type_strategic.get(poi.get("type", ""), 0.5)
    return type_score * 0.6 + conn_score * 0.4


def _compute_nutrition_score(poi: Dict) -> float:
    """Score nutritionnel via donnees nutrition_v6_interface (LECTURE SEULE)."""
    nutrition = poi.get("nutrition", {})
    forage = nutrition.get("forage_quality", 0.0)
    mineral = nutrition.get("mineral_richness", 0.0)
    ndvi = nutrition.get("ndvi_index", 0.0)

    attractiveness = nutrition.get("species_attractiveness", {})
    avg_attract = 0.0
    if attractiveness:
        avg_attract = sum(attractiveness.values()) / len(attractiveness)

    return (forage * 0.3 + mineral * 0.2 + ndvi * 0.2 + avg_attract * 0.3)


async def compute_poi_score(poi: Dict) -> Dict[str, Any]:
    """Calcul multi-critere du score POI."""
    accessibility = _compute_accessibility_score(poi)
    activity = _compute_activity_score(poi)
    strategic = _compute_strategic_score(poi)
    nutrition = _compute_nutrition_score(poi)

    global_score = (
        accessibility * WEIGHTS["accessibility"] +
        activity * WEIGHTS["activity"] +
        strategic * WEIGHTS["strategic"] +
        nutrition * WEIGHTS["nutrition"]
    )

    return {
        "global": round(global_score, 4),
        "accessibility": round(accessibility, 4),
        "activity": round(activity, 4),
        "strategic": round(strategic, 4),
        "nutrition": round(nutrition, 4)
    }


async def compute_batch_scores(poi_ids: List[str]) -> List[Dict[str, Any]]:
    """Scoring par lot (batch limit 100)."""
    db = _get_db()
    limited_ids = poi_ids[:100]
    cursor = db.poi_nodes.find(
        {"poi_id": {"$in": limited_ids}},
        {"_id": 0}
    )
    pois = await cursor.to_list(100)

    results = []
    for poi in pois:
        score = await compute_poi_score(poi)
        # Persister le score calcule
        await db.poi_nodes.update_one(
            {"poi_id": poi["poi_id"]},
            {"$set": {"score": score, "updated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}}
        )
        results.append({
            "poi_id": poi["poi_id"],
            "name": poi.get("name", ""),
            "type": poi.get("type", ""),
            "score": score
        })
    return results


async def get_detailed_score(poi_id: str) -> Optional[Dict[str, Any]]:
    """Score detaille avec decomposition pour un POI."""
    db = _get_db()
    poi = await db.poi_nodes.find_one({"poi_id": poi_id}, {"_id": 0})
    if not poi:
        return None

    score = await compute_poi_score(poi)

    # Enrichissement nutritionnel via nutrition_v6_interface (PF-N1 a PF-N4)
    nutrition_detail = {"source": "nutrition_v6_interface"}
    try:
        from modules.nutrition_v6_interface.wrappers.soil_nutrients_layer import analyze_soil_nutrients
        coords = poi.get("location", {}).get("coordinates", [0, 0])
        if len(coords) >= 2:
            soil_data = analyze_soil_nutrients(coords[1], coords[0])
            nutrition_detail["soil_quality"] = soil_data.get("soil_quality_index", 0)
            nutrition_detail["ecozone"] = soil_data.get("ecozone", "unknown")
    except Exception:
        nutrition_detail["enrichment"] = "unavailable"

    # Persister le score
    await db.poi_nodes.update_one(
        {"poi_id": poi_id},
        {"$set": {"score": score}}
    )

    return {
        "poi_id": poi_id,
        "name": poi.get("name", ""),
        "type": poi.get("type", ""),
        "score": score,
        "weights": WEIGHTS,
        "decomposition": {
            "accessibility": {
                "value": score["accessibility"],
                "weight": WEIGHTS["accessibility"],
                "contribution": round(score["accessibility"] * WEIGHTS["accessibility"], 4)
            },
            "activity": {
                "value": score["activity"],
                "weight": WEIGHTS["activity"],
                "contribution": round(score["activity"] * WEIGHTS["activity"], 4)
            },
            "strategic": {
                "value": score["strategic"],
                "weight": WEIGHTS["strategic"],
                "contribution": round(score["strategic"] * WEIGHTS["strategic"], 4)
            },
            "nutrition": {
                "value": score["nutrition"],
                "weight": WEIGHTS["nutrition"],
                "contribution": round(score["nutrition"] * WEIGHTS["nutrition"], 4),
                "detail": nutrition_detail
            }
        },
        "nutrition_source": poi.get("nutrition", {}),
        "connections_count": len(poi.get("connections", []))
    }
