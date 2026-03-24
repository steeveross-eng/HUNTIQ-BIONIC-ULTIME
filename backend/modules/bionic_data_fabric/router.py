"""
BIONIC Data Fabric — API Router
STEEVE-MAX x2000 / Phase B

Endpoints /api/v1/data-fabric/*

Couche de normalisation et d'interconnexion:
- Schema unifie
- API interne multi-domaine
- Historisation des requetes
- Coherence multi-modules
- Acces centralise pour INTELLIGENCE / ANALYSE / MON TERRITOIRE
"""
import logging
from fastapi import APIRouter, Query
from typing import Optional, List

from .schemas import DataDomain, DataQuality, DataFabricQuery
from .fabric import query_fabric, get_fabric_health, get_history

logger = logging.getLogger("bionic.data_fabric.router")

router = APIRouter(
    prefix="/api/v1/data-fabric",
    tags=["BIONIC DATA FABRIC"],
)


@router.get("/health")
async def health():
    """Health check + module connection status"""
    h = get_fabric_health()
    return h.dict()


@router.get("/query")
async def fabric_query(
    domains: Optional[str] = Query(None, description="Domaines (comma-separated): territory,wildlife,weather,predictions,hotspots,etc."),
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
    radius_m: int = Query(1000, ge=100, le=50000),
    time_range_hours: int = Query(168, ge=1, le=8760),
    limit: int = Query(100, ge=1, le=1000),
    include_history: bool = Query(False),
):
    """
    Requete multi-domaine sur la Data Fabric.
    Retourne des donnees normalisees depuis tous les domaines demandes.
    """
    domain_list = []
    if domains:
        for d in domains.split(","):
            d = d.strip()
            try:
                domain_list.append(DataDomain(d))
            except ValueError:
                pass

    q = DataFabricQuery(
        domains=domain_list,
        lat=lat, lng=lng,
        radius_m=radius_m,
        time_range_hours=time_range_hours,
        limit=limit,
        include_history=include_history,
    )

    result = query_fabric(q)
    return {
        "status": result.status,
        "query_id": result.query_id,
        "total_records": result.total_records,
        "domains_queried": result.domains_queried,
        "data_points": [dp.dict() for dp in result.data_points],
        "coherence_score": result.coherence_score,
        "freshness": result.freshness,
    }


@router.get("/domains")
async def list_domains():
    """Liste tous les domaines de donnees disponibles"""
    return {
        "domains": [
            {
                "id": d.value,
                "name": d.value.replace("_", " ").title(),
                "description": f"Donnees du domaine {d.value}",
            }
            for d in DataDomain
        ],
        "total": len(DataDomain),
    }


@router.get("/modules")
async def list_connected_modules():
    """Liste les modules connectes a la Data Fabric"""
    h = get_fabric_health()
    return {
        "total_connected": h.total_modules_connected,
        "modules": [m.dict() for m in h.module_connections],
    }


@router.get("/history")
async def fabric_history(
    limit: int = Query(50, ge=1, le=500),
):
    """Historique des requetes Data Fabric"""
    entries = get_history(limit)
    return {
        "total": len(entries),
        "history": [e.dict() for e in entries],
    }


@router.get("/coherence")
async def coherence_check(
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lng: Optional[float] = Query(None, ge=-180, le=180),
):
    """Verification de coherence multi-modules pour un point donne"""
    q = DataFabricQuery(
        domains=list(DataDomain),
        lat=lat, lng=lng,
        limit=50,
    )
    result = query_fabric(q)
    return {
        "coherence_score": result.coherence_score,
        "domains_with_data": result.domains_queried,
        "total_data_points": result.total_records,
        "freshness": result.freshness,
    }


logger.info("BIONIC Data Fabric Router loaded — 6 endpoints")
