"""
POI Graph Engine — Router M2
=============================================================
Directive x6900-M2 — Phase M2 MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : waypoint_scoring_engine, scoring_engine, geo_engine,
               geospatial_engine, territory_engine consommes en LECTURE.
ANTI-DOUBLON NUTRITIONNEL : Tout enrichissement nutritionnel via nutrition_v6_interface.
Points de fusion : SUPRA (PF-S1/S2) / Zone Engine (PF-Z1/Z2) / Species (PF-SP1/SP2) /
                   M1 (PF-M1/M2) / Nutrition V6 (PF-N1/N2/N3/N4)

11 Endpoints (0 health + 10 fonctionnels) :
  0. GET  /health — Sante du module
  1. GET  /nodes — Liste POIs (filtres: type, zone, species, user)
  2. POST /nodes — Creer un POI
  3. GET  /nodes/{poi_id} — Detail POI avec connexions
  4. PATCH /nodes/{poi_id} — Mettre a jour un POI
  5. DELETE /nodes/{poi_id} — Supprimer un POI
  6. GET  /near/{lat}/{lng} — POIs a proximite
  7. GET  /edges/{poi_id} — Aretes d'un POI
  8. POST /edges — Creer une arete
  9. GET  /cluster/{lat}/{lng}/{radius_m} — Cluster de POIs
  10. GET /score/{poi_id} — Score detaille
"""

from fastapi import APIRouter, Query, Body
from typing import Optional, Dict, Any

from .services.poi_graph_builder import (
    create_poi,
    get_poi,
    update_poi,
    delete_poi,
    list_pois,
    create_edge,
    get_edges,
    ensure_indexes
)
from .services.poi_scorer import (
    get_detailed_score,
    compute_batch_scores
)
from .services.poi_relation_resolver import (
    find_near,
    compute_cluster
)

router = APIRouter(prefix="/api/v1/poi-graph", tags=["M2 POI Graph Engine"])

_indexes_created = False


async def _ensure_indexes_once():
    global _indexes_created
    if not _indexes_created:
        try:
            await ensure_indexes()
            _indexes_created = True
        except Exception:
            pass


# ==============================================
# HEALTH (0)
# ==============================================

@router.get("/health")
async def health():
    await _ensure_indexes_once()
    return {
        "status": "operational",
        "engine": "poi_graph_engine",
        "version": "1.0.0",
        "phase": "M2-MAP-INTELLIGENCE",
        "directive": "x6900-M2",
        "endpoints": 11,
        "fusion_points": 14,
        "anti_doublon": [
            "waypoint_scoring_engine", "scoring_engine",
            "geo_engine", "geospatial_engine", "territory_engine"
        ]
    }


# ==============================================
# CRUD NODES — M2-A (1-5)
# ==============================================

@router.get("/nodes")
async def get_nodes(user_id: Optional[str] = Query(None),
                    poi_type: Optional[str] = Query(None, alias="type"),
                    zone_id: Optional[str] = Query(None),
                    species: Optional[str] = Query(None),
                    skip: int = Query(0, ge=0),
                    limit: int = Query(50, ge=1, le=200)):
    """M2-1: Liste des POIs avec filtres."""
    await _ensure_indexes_once()
    pois = await list_pois(user_id, poi_type, zone_id, species, skip, limit)
    return {
        "success": True,
        "nodes": pois,
        "count": len(pois),
        "skip": skip,
        "limit": limit,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.post("/nodes")
async def create_node(payload: Dict[str, Any] = Body(...)):
    """M2-2: Creer un POI."""
    await _ensure_indexes_once()

    required = ["user_id", "type", "name", "lat", "lng"]
    missing = [f for f in required if f not in payload]
    if missing:
        return {"success": False, "error": "MISSING_FIELDS", "fields": missing}

    result = await create_poi(
        user_id=payload["user_id"],
        poi_type=payload["type"],
        name=payload["name"],
        lat=payload["lat"],
        lng=payload["lng"],
        description=payload.get("description", ""),
        altitude_m=payload.get("altitude_m", 0),
        properties=payload.get("properties"),
        zone_id=payload.get("zone_id", "")
    )

    if "error" in result:
        return {"success": False, **result}

    return {
        "success": True,
        "node": result,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.get("/nodes/{poi_id}")
async def get_node(poi_id: str):
    """M2-3: Detail d'un POI avec connexions."""
    poi = await get_poi(poi_id)
    if not poi:
        return {"success": False, "error": "POI_NOT_FOUND"}
    return {
        "success": True,
        "node": poi,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.patch("/nodes/{poi_id}")
async def patch_node(poi_id: str, payload: Dict[str, Any] = Body(...)):
    """M2-4: Mettre a jour un POI."""
    result = await update_poi(poi_id, payload)
    if not result:
        return {"success": False, "error": "POI_NOT_FOUND"}
    return {
        "success": True,
        "node": result,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.delete("/nodes/{poi_id}")
async def delete_node(poi_id: str):
    """M2-5: Supprimer un POI et ses aretes."""
    result = await delete_poi(poi_id)
    return {
        "success": result["deleted"],
        **result,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


# ==============================================
# SPATIAL — M2-B (6-10)
# ==============================================

@router.get("/near/{lat}/{lng}")
async def near_pois(lat: float, lng: float,
                    radius_m: float = Query(5000, ge=100, le=50000),
                    type_filter: Optional[str] = Query(None, alias="type"),
                    limit: int = Query(50, ge=1, le=200)):
    """M2-6: POIs a proximite avec distances."""
    await _ensure_indexes_once()
    pois = await find_near(lat, lng, radius_m, type_filter, limit)
    return {
        "success": True,
        "center": {"lat": lat, "lng": lng},
        "radius_m": radius_m,
        "nodes": pois,
        "count": len(pois),
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.get("/edges/{poi_id}")
async def get_poi_edges(poi_id: str):
    """M2-7: Aretes connectees a un POI."""
    edges = await get_edges(poi_id)
    return {
        "success": True,
        "poi_id": poi_id,
        "edges": edges,
        "count": len(edges),
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.post("/edges")
async def create_poi_edge(payload: Dict[str, Any] = Body(...)):
    """M2-8: Creer une arete entre 2 POIs."""
    required = ["from_poi", "to_poi", "relation_type"]
    missing = [f for f in required if f not in payload]
    if missing:
        return {"success": False, "error": "MISSING_FIELDS", "fields": missing}

    result = await create_edge(
        from_poi=payload["from_poi"],
        to_poi=payload["to_poi"],
        relation_type=payload["relation_type"],
        distance_m=payload.get("distance_m", 0.0),
        elevation_diff_m=payload.get("elevation_diff_m", 0.0),
        properties=payload.get("properties")
    )

    if "error" in result:
        return {"success": False, **result}

    return {
        "success": True,
        "edge": result,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.get("/cluster/{lat}/{lng}/{radius_m}")
async def cluster_pois(lat: float, lng: float, radius_m: float):
    """M2-9: Cluster de POIs dans un rayon."""
    await _ensure_indexes_once()
    radius_m = max(100, min(50000, radius_m))
    cluster = await compute_cluster(lat, lng, radius_m)
    return {
        "success": True,
        **cluster,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }


@router.get("/score/{poi_id}")
async def score_poi(poi_id: str):
    """M2-10: Score detaille d'un POI."""
    result = await get_detailed_score(poi_id)
    if not result:
        return {"success": False, "error": "POI_NOT_FOUND"}
    return {
        "success": True,
        **result,
        "source": "poi_graph_engine",
        "directive": "x6900-M2"
    }
