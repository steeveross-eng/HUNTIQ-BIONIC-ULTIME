"""
BCE-4X P0 — HUNT ORCHESTRATOR API
===================================
Endpoints FastAPI pour l'orchestration de chasse.

Endpoints:
- POST /api/v1/hunt/orchestrate  — Recommandation complete
- POST /api/v1/hunt/scent-zone   — Zone de contamination pour un point
- POST /api/v1/hunt/access-route  — Route d'acces vers un affut

STEEVE-MAX 2026-03-28 — Standard institutionnel.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.hunt_orchestrator.router")

router = APIRouter(prefix="/api/v1/hunt", tags=["Hunt Orchestrator"])


# === Modeles Pydantic ===

class FeedingSite(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None
    type: Optional[str] = "alimentation"


class FixedBlind(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = "Affut fixe"
    type_key: Optional[str] = "tree_stand"
    id: Optional[str] = None


class OrchestrationRequest(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre du territoire")
    center_lng: float = Field(..., description="Longitude du centre du territoire")
    wind_direction_deg: float = Field(..., ge=0, lt=360, description="Direction du vent (degres)")
    wind_speed_kmh: float = Field(..., ge=0, description="Vitesse du vent (km/h)")
    session: str = Field("matin", description="matin ou soir")
    species: str = Field("orignal", description="Espece ciblee")
    radius_m: int = Field(600, ge=200, le=2000, description="Rayon du territoire")
    max_blinds: int = Field(5, ge=1, le=10, description="Nombre max de recommandations")
    feeding_sites: List[FeedingSite] = Field(default_factory=list)
    fixed_blinds: List[FixedBlind] = Field(default_factory=list)


class ScentZoneRequest(BaseModel):
    lat: float
    lng: float
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wind_speed_kmh: float = Field(..., ge=0)
    session: str = Field("matin")


class AccessRouteRequest(BaseModel):
    entry_lat: float
    entry_lng: float
    blind_lat: float
    blind_lng: float
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wind_speed_kmh: float = Field(..., ge=0)
    session: str = Field("matin")
    feeding_sites: List[FeedingSite] = Field(default_factory=list)


# === Endpoints ===

@router.post("/orchestrate")
async def orchestrate_hunt(req: OrchestrationRequest):
    """
    Orchestration complete d'une session de chasse.
    Combine vent/odeurs + acces dynamique + choix d'affuts.
    """
    try:
        from engines.hunt_orchestrator.orchestrator import orchestrate_hunt_session

        # Convertir les modeles Pydantic en dicts
        feeding = [{"lat": fs.lat, "lng": fs.lng, "name": fs.name} for fs in req.feeding_sites]
        fixed = [
            {"lat": fb.lat, "lng": fb.lng, "name": fb.name,
             "type_key": fb.type_key, "id": fb.id or f"fixed-{fb.lat:.4f}"}
            for fb in req.fixed_blinds
        ]

        result = orchestrate_hunt_session(
            center_lat=req.center_lat,
            center_lng=req.center_lng,
            wind_direction_deg=req.wind_direction_deg,
            wind_speed_kmh=req.wind_speed_kmh,
            session=req.session,
            species=req.species,
            radius_m=req.radius_m,
            feeding_sites=feeding,
            fixed_blinds=fixed,
            max_blinds=req.max_blinds,
        )

        return result

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scent-zone")
async def compute_scent(req: ScentZoneRequest):
    """Calculer la zone de contamination olfactive pour un point donne."""
    try:
        from engines.hunt_orchestrator.vent_odeurs import compute_scent_zone
        return compute_scent_zone(
            req.lat, req.lng,
            req.wind_direction_deg, req.wind_speed_kmh,
            req.session,
        )
    except Exception as e:
        logger.error(f"[SCENT-ZONE] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/access-route")
async def compute_access(req: AccessRouteRequest):
    """Calculer la route d'acces optimale vers un affut."""
    try:
        from engines.terrain_nav import get_terrain_nav
        from engines.hunt_orchestrator.vent_odeurs import compute_scent_zone
        from engines.hunt_orchestrator.access_engine import compute_access_route

        # Charger le graphe terrain
        mid_lat = (req.entry_lat + req.blind_lat) / 2
        mid_lng = (req.entry_lng + req.blind_lng) / 2
        trail_graph = get_terrain_nav(mid_lat, mid_lng, radius_m=2000)

        # Zone de contamination
        scent_zone = compute_scent_zone(
            req.blind_lat, req.blind_lng,
            req.wind_direction_deg, req.wind_speed_kmh,
            req.session,
        )

        feeding = [{"lat": fs.lat, "lng": fs.lng} for fs in req.feeding_sites]

        result = compute_access_route(
            req.entry_lat, req.entry_lng,
            req.blind_lat, req.blind_lng,
            trail_graph, feeding, scent_zone,
        )

        return result

    except Exception as e:
        logger.error(f"[ACCESS-ROUTE] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def hunt_orchestrator_status():
    """Statut de l'engine d'orchestration de chasse."""
    return {
        "engine": "hunt_orchestrator",
        "version": "1.0.0",
        "status": "active",
        "modules": [
            "vent_odeurs_v1",
            "access_engine_v1",
            "choix_affuts_v1",
            "orchestrator_v1",
        ],
        "data_sources": {
            "wind": "Open-Meteo V3 (reel)",
            "trails": "OSM/Overpass (reel)",
            "water": "OSM cache (41K polygones)",
            "dominant_wind": "NW hardcode (Quebec, autorise STEEVE-MAX)",
        },
        "governance": "BCE-4X P0 — STEEVE-MAX",
    }
