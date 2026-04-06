"""
ACCESS ENGINE V6 — Router API unique
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Endpoints:
  POST /api/v6/access/compute       — Calcul chemin unique
  POST /api/v6/access/compute-batch  — Calcul batch pour plusieurs affuts
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .engine import compute_access_route

logger = logging.getLogger("access_engine_v6.router")

router = APIRouter(prefix="/api/v6/access", tags=["access_engine_v6"])


# ═══════════════════════════════════════════
# MODELES DE DONNEES
# ═══════════════════════════════════════════

class LatLng(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class AccessOptions(BaseModel):
    max_off_trail_km: float = Field(default=2.0, ge=0.1, le=10.0)
    prefer_trails: bool = True
    analysis_radius_m: int = Field(default=3000, ge=500, le=10000)


class ComputeAccessRequest(BaseModel):
    origin: LatLng
    destination: LatLng
    month: int = Field(default=10, ge=1, le=12)
    species: str = "orignal"
    options: Optional[AccessOptions] = None


class BatchDestination(BaseModel):
    id: str
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class ComputeBatchRequest(BaseModel):
    origin: LatLng
    destinations: list[BatchDestination] = Field(..., min_length=1, max_length=20)
    month: int = Field(default=10, ge=1, le=12)
    species: str = "orignal"
    options: Optional[AccessOptions] = None


# ═══════════════════════════════════════════
# ENDPOINTS — Pipeline unique GOLDEN
# ═══════════════════════════════════════════

@router.post("/compute")
async def compute_access(req: ComputeAccessRequest):
    """
    Calcul du chemin d'acces optimal entre un point d'entree et un affut.
    Pipeline GOLDEN: Trail-First Dijkstra + Terrain Grid A*.
    """
    opts = req.options or AccessOptions()

    try:
        result = await compute_access_route(
            origin={"lat": req.origin.lat, "lng": req.origin.lng},
            destination={"lat": req.destination.lat, "lng": req.destination.lng},
            month=req.month,
            species=req.species,
            max_off_trail_km=opts.max_off_trail_km,
            prefer_trails=opts.prefer_trails,
            analysis_radius_m=opts.analysis_radius_m,
        )
        return result
    except Exception as e:
        logger.error(f"Access compute error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur calcul acces: {str(e)}")


@router.post("/compute-batch")
async def compute_access_batch(req: ComputeBatchRequest):
    """
    Calcul batch des chemins d'acces pour plusieurs affuts.
    Pipeline GOLDEN: Meme pipeline applique a chaque destination.
    """
    opts = req.options or AccessOptions()
    routes = []

    for dest in req.destinations:
        try:
            result = await compute_access_route(
                origin={"lat": req.origin.lat, "lng": req.origin.lng},
                destination={"lat": dest.lat, "lng": dest.lng},
                month=req.month,
                species=req.species,
                max_off_trail_km=opts.max_off_trail_km,
                prefer_trails=opts.prefer_trails,
                analysis_radius_m=opts.analysis_radius_m,
            )
            routes.append({"stand_id": dest.id, "route": result.get("route")})
        except Exception as e:
            logger.error(f"Batch error for {dest.id}: {e}")
            routes.append({
                "stand_id": dest.id,
                "route": None,
                "error": str(e),
            })

    return {"routes": routes}


@router.get("/health")
async def access_health():
    """Healthcheck du module access_engine_v6."""
    return {
        "module": "access_engine_v6",
        "status": "operational",
        "protocol": "BIONIC GOLDEN",
        "pipeline": "Trail-First Dijkstra + Terrain Grid A*",
    }
