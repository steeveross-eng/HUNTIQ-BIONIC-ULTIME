"""
M2 — POI Graph Builder : CRUD POI nodes + edges
====================================================
Directive x6900-M2 — Phase M2 MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : camera_engine, waypoint_engine, scoring_engine consommes en LECTURE.
NE recree PAS waypoint_scoring_engine, scoring_engine, geo_engine, geospatial_engine, territory_engine.
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

VALID_POI_TYPES = [
    "camera", "observation", "stand", "cache",
    "point_eau", "ravage", "corridor", "nourriture", "saline"
]


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


async def ensure_indexes():
    """Cree les index MongoDB pour poi_nodes et poi_edges."""
    db = _get_db()
    await db.poi_nodes.create_index([("location", "2dsphere")])
    await db.poi_nodes.create_index("user_id")
    await db.poi_nodes.create_index("type")
    await db.poi_nodes.create_index("zone_id")
    await db.poi_nodes.create_index("poi_id", unique=True)
    await db.poi_edges.create_index("from_poi")
    await db.poi_edges.create_index("to_poi")
    await db.poi_edges.create_index("relation_type")
    await db.poi_edges.create_index("edge_id", unique=True)
    logger.info("M2 POI Graph indexes created")


async def create_poi(user_id: str, poi_type: str, name: str,
                     lat: float, lng: float,
                     description: str = "",
                     altitude_m: float = 0,
                     properties: Optional[Dict] = None,
                     zone_id: str = "") -> Dict[str, Any]:
    """Cree un noeud POI dans le graphe."""
    if poi_type not in VALID_POI_TYPES:
        return {"error": "INVALID_POI_TYPE", "valid_types": VALID_POI_TYPES}

    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    poi_id = str(uuid.uuid4())

    poi_node = {
        "poi_id": poi_id,
        "type": poi_type,
        "name": name,
        "description": description,
        "location": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "altitude_m": altitude_m,
        "properties": properties or {
            "species_observed": [],
            "last_activity": None,
            "frequency": 0,
            "confidence": 0.0
        },
        "score": {
            "global": 0.0,
            "accessibility": 0.0,
            "activity": 0.0,
            "strategic": 0.0,
            "nutrition": 0.0
        },
        "nutrition": {
            "forage_quality": 0.0,
            "mineral_richness": 0.0,
            "ndvi_index": 0.0,
            "species_attractiveness": {},
            "source": "nutrition_v6_interface"
        },
        "connections": [],
        "zone_id": zone_id,
        "province": "",
        "user_id": user_id,
        "created_at": now,
        "updated_at": now
    }

    # POINT DE FUSION PF-M1 : enrichissement province via M1
    try:
        from modules.national_data_harvester.services.boundary_resolver import resolve_province
        province = resolve_province(lat, lng)
        if province:
            poi_node["province"] = province
    except Exception:
        pass

    await db.poi_nodes.insert_one(poi_node)

    # Retourne sans _id MongoDB
    poi_node.pop("_id", None)
    return poi_node


async def get_poi(poi_id: str) -> Optional[Dict[str, Any]]:
    """Recupere un POI avec ses connexions."""
    db = _get_db()
    poi = await db.poi_nodes.find_one({"poi_id": poi_id}, {"_id": 0})
    if not poi:
        return None

    # Ajouter les edges connectes
    edges_cursor = db.poi_edges.find(
        {"$or": [{"from_poi": poi_id}, {"to_poi": poi_id}]},
        {"_id": 0}
    )
    edges = await edges_cursor.to_list(100)
    poi["edges"] = edges
    poi["edge_count"] = len(edges)
    return poi


async def update_poi(poi_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Met a jour un POI."""
    db = _get_db()

    # Champs interdits de modification directe
    forbidden = {"poi_id", "created_at", "location"}
    clean_updates = {k: v for k, v in updates.items() if k not in forbidden}
    clean_updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.poi_nodes.find_one_and_update(
        {"poi_id": poi_id},
        {"$set": clean_updates},
        return_document=True
    )
    if result:
        result.pop("_id", None)
    return result


async def delete_poi(poi_id: str) -> Dict[str, Any]:
    """Supprime un POI et toutes ses aretes."""
    db = _get_db()

    # Supprimer les aretes liees
    edge_result = await db.poi_edges.delete_many(
        {"$or": [{"from_poi": poi_id}, {"to_poi": poi_id}]}
    )

    # Retirer de la liste connections des POIs connectes
    await db.poi_nodes.update_many(
        {"connections": poi_id},
        {"$pull": {"connections": poi_id}}
    )

    # Supprimer le noeud
    node_result = await db.poi_nodes.delete_one({"poi_id": poi_id})

    return {
        "deleted": node_result.deleted_count > 0,
        "poi_id": poi_id,
        "edges_removed": edge_result.deleted_count
    }


async def list_pois(user_id: Optional[str] = None,
                    poi_type: Optional[str] = None,
                    zone_id: Optional[str] = None,
                    species: Optional[str] = None,
                    skip: int = 0,
                    limit: int = 50) -> List[Dict[str, Any]]:
    """Liste les POIs avec filtres."""
    db = _get_db()
    query = {}

    if user_id:
        query["user_id"] = user_id
    if poi_type:
        query["type"] = poi_type
    if zone_id:
        query["zone_id"] = zone_id
    if species:
        query["properties.species_observed"] = species

    cursor = db.poi_nodes.find(query, {"_id": 0}).skip(skip).limit(limit)
    return await cursor.to_list(limit)


async def create_edge(from_poi: str, to_poi: str, relation_type: str,
                      distance_m: float = 0.0,
                      elevation_diff_m: float = 0.0,
                      properties: Optional[Dict] = None) -> Dict[str, Any]:
    """Cree une arete entre deux POIs."""
    valid_relations = ["proximity", "corridor", "line_of_sight", "water_flow", "trail"]
    if relation_type not in valid_relations:
        return {"error": "INVALID_RELATION_TYPE", "valid_types": valid_relations}

    db = _get_db()

    # Verifier que les deux POIs existent
    from_exists = await db.poi_nodes.find_one({"poi_id": from_poi})
    to_exists = await db.poi_nodes.find_one({"poi_id": to_poi})
    if not from_exists or not to_exists:
        return {"error": "POI_NOT_FOUND", "from_exists": bool(from_exists), "to_exists": bool(to_exists)}

    edge_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    edge = {
        "edge_id": edge_id,
        "from_poi": from_poi,
        "to_poi": to_poi,
        "relation_type": relation_type,
        "distance_m": distance_m,
        "elevation_diff_m": elevation_diff_m,
        "weight": 1.0 / (1.0 + distance_m / 1000.0),
        "properties": properties or {
            "terrain_type": "forest",
            "traversability": 0.5,
            "species_usage": []
        },
        "created_at": now
    }

    await db.poi_edges.insert_one(edge)

    # Mettre a jour les connexions bidirectionnelles
    await db.poi_nodes.update_one(
        {"poi_id": from_poi},
        {"$addToSet": {"connections": to_poi}}
    )
    await db.poi_nodes.update_one(
        {"poi_id": to_poi},
        {"$addToSet": {"connections": from_poi}}
    )

    edge.pop("_id", None)
    return edge


async def get_edges(poi_id: str) -> List[Dict[str, Any]]:
    """Retourne les aretes connectees a un POI."""
    db = _get_db()
    cursor = db.poi_edges.find(
        {"$or": [{"from_poi": poi_id}, {"to_poi": poi_id}]},
        {"_id": 0}
    )
    return await cursor.to_list(100)
