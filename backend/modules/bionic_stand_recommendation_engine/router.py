"""
BIONIC Stand Recommendation Engine — API Router
STEEVE-MAX x2280

Endpoints /api/v1/stand-recommendation/*
"""
import logging
from fastapi import APIRouter, Query
from typing import Optional

from .engine import recommend_stands

logger = logging.getLogger("bionic.stand_recommendation.router")

router = APIRouter(
    prefix="/api/v1/stand-recommendation",
    tags=["BIONIC STAND RECOMMENDATION"],
)


@router.get("/health")
async def health():
    return {
        "status": "operational",
        "engine": "bionic_stand_recommendation_engine",
        "version": "1.0.0",
        "directive": "STEEVE-MAX x2280",
        "master_switch": "LOCKED",
    }


@router.get("/recommend")
async def get_recommendations(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    wind_direction: str = Query("NE"),
    wind_speed_kmh: float = Query(12.0, ge=0, le=200),
    radius_m: int = Query(600, ge=100, le=5000),
    species: str = Query("orignal"),
):
    """
    Genere 3-5 affuts professionnels recommandes.
    Inclut orientation, score, justification complete et chemin d'approche.
    """
    result = recommend_stands(
        lat=lat, lng=lng,
        wind_direction=wind_direction,
        wind_speed_kmh=wind_speed_kmh,
        radius_m=radius_m,
        species=species,
    )
    return result


logger.info("BIONIC Stand Recommendation Engine loaded")
