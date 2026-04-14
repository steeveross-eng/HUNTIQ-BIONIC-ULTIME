"""
AFFUT-IA-Omega-PLUS — API Router
Endpoints pour generation et consultation des affuts IA.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...camera_engine.dependencies import get_camera_db
from ...roles_engine.v1.dependencies import get_current_user_with_role
from ...roles_engine.v1.models import UserWithRole
from .engine import AffutIAEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/affuts-ia", tags=["Affuts IA Engine"])


@router.post("/generate")
async def generate_affuts(
    lat: float = Query(..., ge=-90, le=90, description="Latitude centre"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude centre"),
    species: str = Query("cerf", description="Espece cible"),
    radius_m: float = Query(2000, ge=100, le=10000, description="Rayon en metres"),
    wind_deg: Optional[float] = Query(None, ge=0, le=360, description="Direction vent en degres"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """
    AFFUT-IA-Omega-PLUS: Genere des affuts IA potentiels.
    Integre: IA Vision + Salines 20-100m + Corridors + Vent + Science BIONIC.
    """
    engine = AffutIAEngine(db)
    affuts = await engine.generate_affuts(
        user_id=user.user_id,
        center_lat=lat,
        center_lon=lon,
        species=species,
        radius_m=radius_m,
        wind_deg=wind_deg,
        month=month
    )
    return {
        "success": True,
        "affuts": affuts,
        "total": len(affuts),
        "species": species,
        "source": "AFFUT-IA-Omega-PLUS"
    }


@router.get("/list")
async def list_affuts(
    species: Optional[str] = Query(None),
    min_score: float = Query(0, ge=0, le=100),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Recupere les affuts IA generes pour l'utilisateur."""
    engine = AffutIAEngine(db)
    affuts = await engine.get_affuts(user.user_id, species, min_score)
    return {"affuts": affuts, "total": len(affuts)}


@router.get("/explain/{affut_id}")
async def explain_affut(
    affut_id: str,
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Retourne la justification detaillee IA + biologique + scientifique d'un affut."""
    engine = AffutIAEngine(db)
    result = await engine.explain_affut(user.user_id, affut_id)
    if not result:
        raise HTTPException(status_code=404, detail="Affut non trouve")
    return result


@router.get("/references")
async def get_scientific_references(
    db: AsyncIOMotorDatabase = Depends(get_camera_db)
):
    """Retourne les references scientifiques BIONIC utilisees par le moteur."""
    engine = AffutIAEngine(db)
    refs = await engine.get_scientific_references()
    return {"references": refs, "total": len(refs)}
