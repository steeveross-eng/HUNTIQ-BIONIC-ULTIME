"""
Strategy Recommender — Bridge IA → Strategie
=============================================

Service intermediaire BCE-4X. Genere des recommandations strategiques
basees sur l'historique des analyses SUPRA (pipeline_results).

ZERO couplage direct : aucun import de strategy_master_engine.
Communication exclusivement via MongoDB.

Version: 1.0.0
Directive: x5400-STEEVE_MAX Phase I
"""

import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


async def generate_recommendations(
    user_id: str,
    species: str
) -> List[Dict]:
    """
    Genere des recommandations strategiques basees sur l'historique
    des analyses SUPRA stockees dans pipeline_results.
    """
    db = _get_db()

    # Recuperer les dernieres analyses
    cursor = db.pipeline_results.find(
        {"user_id": user_id, "species": species},
        {"_id": 0}
    ).sort("created_at", -1).limit(5)

    analyses = []
    async for doc in cursor:
        analyses.append(doc)

    if not analyses:
        return [{
            "recommendation_type": "no_data",
            "content": "Aucune analyse SUPRA disponible. Effectuez une analyse de territoire pour recevoir des recommandations.",
            "confidence": 0,
            "species": species
        }]

    recommendations = []
    latest = analyses[0]

    # Recommandation basee sur les timings
    timings = latest.get("module_timings_ms", {})
    total_time = latest.get("total_computation_time_ms", 0)
    if total_time > 0:
        recommendations.append({
            "recommendation_type": "analysis_quality",
            "content": f"Analyse completee en {total_time:.0f}ms — {latest.get('module_count', 10)} modules executes.",
            "confidence": 90,
            "species": species,
            "source_data": {"total_time_ms": total_time, "module_count": latest.get("module_count")}
        })

    # Recommandation basee sur les corridors
    corridor_count = latest.get("corridor_count", 0)
    if corridor_count > 3:
        recommendations.append({
            "recommendation_type": "corridor_strategy",
            "content": f"{corridor_count} corridors detectes. Privilegiez l'affut aux intersections de corridors pour maximiser vos chances.",
            "confidence": 75,
            "species": species,
            "source_data": {"corridor_count": corridor_count}
        })
    elif corridor_count > 0:
        recommendations.append({
            "recommendation_type": "corridor_strategy",
            "content": f"{corridor_count} corridor(s) detecte(s). Positionnez-vous en embuscade le long du corridor principal.",
            "confidence": 70,
            "species": species,
            "source_data": {"corridor_count": corridor_count}
        })

    # Recommandation basee sur l'historique (tendance)
    if len(analyses) >= 3:
        recommendations.append({
            "recommendation_type": "history_trend",
            "content": f"{len(analyses)} analyses recentes disponibles. Comparez les zones pour identifier les patterns saisonniers.",
            "confidence": 65,
            "species": species,
            "source_data": {"analysis_count": len(analyses)}
        })

    # Recommandation validation BCE-4X
    validation = latest.get("validation", {})
    if validation.get("all_modules_executed"):
        recommendations.append({
            "recommendation_type": "validation_status",
            "content": "Pipeline SUPRA valide BCE-4X — tous les modules executes, donnees fiables.",
            "confidence": 95,
            "species": species,
            "source_data": {"validation": validation}
        })

    return recommendations


async def store_recommendation(user_id: str, recommendation: Dict) -> str:
    """
    Stocke une recommandation en MongoDB.
    """
    db = _get_db()

    doc = {
        "user_id": user_id,
        "species": recommendation.get("species", ""),
        "recommendation_type": recommendation.get("recommendation_type", ""),
        "content": recommendation.get("content", ""),
        "confidence": recommendation.get("confidence", 0),
        "source_data": recommendation.get("source_data", {}),
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = await db.ai_recommendations.insert_one(doc)
    return str(result.inserted_id)


async def get_user_recommendations(
    user_id: str,
    species: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """
    Recupere les recommandations actives pour un utilisateur.
    """
    db = _get_db()

    query = {"user_id": user_id, "status": "active"}
    if species:
        query["species"] = species

    cursor = db.ai_recommendations.find(
        query, {"_id": 0}
    ).sort("created_at", -1).limit(limit)

    results = []
    async for doc in cursor:
        results.append(doc)
    return results
