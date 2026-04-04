"""
National Data Harvester + Legal Boundary Engine — Router M1
=============================================================
Directive x6800-A — Phase M1 MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : territory_engine, geo_engine, legal_time_engine consommes en lecture.
ANTI-DOUBLON NUTRITIONNEL : soil_nutrients_layer V6 consomme en lecture.
Points de fusion : SUPRA / Zone Engine / P6 / Species / Predictive.

8 Endpoints :
  1. GET /boundaries — Liste limites par type/province
  2. GET /boundaries/{id} — Detail d'une limite
  3. GET /boundaries/at/{lat}/{lng} — Limites a un point
  4. GET /legal-zones — Liste zones legales
  5. GET /legal-zones/{id} — Detail zone legale
  6. GET /legal-zones/at/{lat}/{lng} — Zones legales a un point
  7. GET /legal-check/{lat}/{lng}/{species} — Verification legalite
  8. POST /harvest/trigger — Declencher collecte (admin)
"""

from fastapi import APIRouter, Query
from typing import Optional

from .services.boundary_resolver import (
    list_boundaries,
    get_boundary_detail,
    get_boundaries_at_point
)
from .services.legal_constraint_engine import (
    check_legal_status,
    list_legal_zones,
    get_zone_detail,
    get_species_regulations
)
from .services.harvest_scheduler import (
    trigger_harvest,
    get_harvest_logs
)

router = APIRouter(prefix="/api/v1/map-intel", tags=["M1 National Data Harvester"])


# ==============================================
# HEALTH
# ==============================================

@router.get("/health")
async def health():
    return {
        "status": "operational",
        "engine": "national_data_harvester",
        "version": "1.0.0",
        "phase": "M1-MAP-INTELLIGENCE",
        "directive": "x6800-A",
        "endpoints": 8
    }


# ==============================================
# BOUNDARIES (1-3)
# ==============================================

@router.get("/boundaries")
async def get_boundaries(boundary_type: Optional[str] = Query(None),
                         province: Optional[str] = Query(None)):
    """M1-1: Liste des limites par type/province."""
    boundaries = await list_boundaries(boundary_type, province)
    return {
        "success": True,
        "boundaries": boundaries,
        "count": len(boundaries),
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


@router.get("/boundaries/at/{lat}/{lng}")
async def boundaries_at_point(lat: float, lng: float):
    """M1-3: Limites contenant un point GPS."""
    result = await get_boundaries_at_point(lat, lng)
    return {
        "success": True,
        **result,
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


@router.get("/boundaries/{boundary_id}")
async def boundary_detail(boundary_id: str):
    """M1-2: Detail d'une limite."""
    detail = await get_boundary_detail(boundary_id)
    if not detail:
        return {"success": False, "error": "BOUNDARY_NOT_FOUND"}
    return {
        "success": True,
        "boundary": detail,
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


# ==============================================
# LEGAL ZONES (4-6)
# ==============================================

@router.get("/legal-zones")
async def get_legal_zones_list(zone_type: Optional[str] = Query(None),
                               province: Optional[str] = Query(None)):
    """M1-4: Liste des zones legales par type."""
    zones = await list_legal_zones(zone_type, province)
    return {
        "success": True,
        "zones": zones,
        "count": len(zones),
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


@router.get("/legal-zones/at/{lat}/{lng}")
async def legal_zones_at_point(lat: float, lng: float):
    """M1-6: Zones legales contenant un point."""
    from .services.boundary_resolver import resolve_province
    from .services.legal_constraint_engine import ZONE_TYPES, _determine_zone_type

    province = resolve_province(lat, lng)
    zone_type = _determine_zone_type(lat, lng)
    zone_info = ZONE_TYPES.get(zone_type, {})

    return {
        "success": True,
        "location": {"lat": lat, "lng": lng},
        "province": province,
        "zone_type": zone_type,
        "zone_access": zone_info.get("access", "unknown"),
        "zone_description": zone_info.get("description", ""),
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


@router.get("/legal-zones/{zone_id}")
async def legal_zone_detail(zone_id: str):
    """M1-5: Detail d'une zone legale."""
    detail = await get_zone_detail(zone_id)
    if not detail:
        return {"success": False, "error": "ZONE_NOT_FOUND"}
    return {
        "success": True,
        "zone": detail,
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


# ==============================================
# LEGAL CHECK (7)
# ==============================================

@router.get("/legal-check/{lat}/{lng}/{species}")
async def legal_check(lat: float, lng: float, species: str,
                      month: Optional[int] = Query(None),
                      day: Optional[int] = Query(None)):
    """M1-7: Verification de legalite pour un point/espece."""
    result = check_legal_status(lat, lng, species, month, day)

    # CONNEXION SUPRA : enrichissement avec nutrition V6
    try:
        from modules.nutrition_v6_interface.wrappers.soil_nutrients_layer import (
            analyze_soil_nutrients
        )
        nutrition = analyze_soil_nutrients(lat, lng)
        result["nutrition_context"] = {
            "soil_quality": nutrition.get("soil_quality_index", 0),
            "ecozone": nutrition.get("ecozone", "unknown"),
            "source": "nutrition_v6_interface"
        }
    except Exception:
        result["nutrition_context"] = {"source": "unavailable"}

    return {
        **result,
        "source": "national_data_harvester + legal_constraint_engine",
        "directive": "x6800-A-M1"
    }


# ==============================================
# HARVEST (8)
# ==============================================

@router.post("/harvest/trigger")
async def trigger_harvest_endpoint(source: str = Query("manual"),
                                   scope: str = Query("boundaries")):
    """M1-8: Admin — declencher une collecte."""
    result = await trigger_harvest(source, scope)
    return {
        "success": True,
        "harvest": result,
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }


@router.get("/harvest/logs")
async def harvest_logs(limit: int = Query(10)):
    """Logs des collectes."""
    logs = await get_harvest_logs(limit)
    return {
        "success": True,
        "logs": logs,
        "count": len(logs),
        "source": "national_data_harvester"
    }


@router.get("/species/{species}/regulations")
async def species_regs(species: str):
    """Reglementations d'une espece."""
    result = get_species_regulations(species)
    return {
        "success": True,
        **result,
        "source": "national_data_harvester",
        "directive": "x6800-A-M1"
    }
