"""
SUPRA Bridge Service — Interconnexion Pipeline SUPRA → Strategy Master
======================================================================

Service intermediaire BCE-4X. Stocke les resultats du pipeline SUPRA
en MongoDB pour consommation par strategy_master_engine.

ZERO couplage direct : aucun import de bionic_engine_p0.
Communication exclusivement via MongoDB (collection: pipeline_results).

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


async def store_pipeline_result(
    user_id: str,
    bounds: Dict,
    species: str,
    pipeline_result: Dict
) -> str:
    """
    Stocke un resultat de pipeline SUPRA en MongoDB.
    Appele par pipeline_router apres execution reussie.
    Retourne l'ID du document cree.
    """
    db = _get_db()

    doc = {
        "user_id": user_id,
        "species": species,
        "bounds": bounds,
        "score_global": pipeline_result.get("module_stats", {}).get("TFE", {}).get("thermal_flow_composite", {}).get("mean", 0),
        "module_count": pipeline_result.get("module_count", 10),
        "module_timings_ms": pipeline_result.get("module_timings_ms", {}),
        "total_computation_time_ms": pipeline_result.get("total_computation_time_ms", 0),
        "corridor_count": pipeline_result.get("corridor_count", 0),
        "pipeline_version": pipeline_result.get("pipeline", "BIONIC_V5_ULTIME_300"),
        "resolution": pipeline_result.get("resolution", 60),
        "validation": pipeline_result.get("validation", {}),
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    result = await db.pipeline_results.insert_one(doc)
    result_id = str(result.inserted_id)
    logger.info(f"Pipeline result stored: user={user_id}, species={species}, id={result_id}")
    return result_id


async def get_latest_analysis(user_id: str, species: str) -> Optional[Dict]:
    """
    Recupere la derniere analyse SUPRA pour un utilisateur et une espece.
    """
    db = _get_db()
    doc = await db.pipeline_results.find_one(
        {"user_id": user_id, "species": species},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
    return doc


async def get_analysis_history(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Recupere l'historique des analyses SUPRA pour un utilisateur.
    """
    db = _get_db()
    cursor = db.pipeline_results.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)

    results = []
    async for doc in cursor:
        results.append(doc)
    return results
