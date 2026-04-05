"""
GUIDE PRO Engine — Router (15 endpoints)
BIONIC OS V8.5 | Phase E-1 | BCE-4X GOLDEN V6+

PREFIX: /api/v1/guide-pro

DataContracts: DC-15, DC-16, DC-17
EventBus: EB-20, EB-21, EB-22, EB-23
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from modules.guide_pro_engine.services import (
    guide_session_manager,
    group_tracker,
    guided_route_builder,
    post_hunt_reporter,
)

logger = logging.getLogger("guide_pro.router")

router = APIRouter(prefix="/api/v1/guide-pro", tags=["guide-pro"])


# =====================================================================
# REQUEST MODELS
# =====================================================================

class CreateSessionRequest(BaseModel):
    guide_id: str
    territory_id: str
    title: str
    species: str = "deer"
    start_date: str
    end_date: str
    bounds: Optional[dict] = None
    config: Optional[dict] = None


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None
    species: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bounds: Optional[dict] = None
    config: Optional[dict] = None


class AddClientRequest(BaseModel):
    user_id: str
    name: str
    skill_level: str = "intermediate"
    consent_gps: bool = True


# =====================================================================
# ENDPOINT 0: HEALTH
# =====================================================================

@router.get("/health")
async def guide_pro_health():
    """Sante du module GUIDE PRO."""
    return {
        "status": "operational",
        "module": "guide_pro_engine",
        "version": "V8.5",
        "protocol": "BCE-4X GOLDEN V6+",
        "endpoints": 15,
        "services": ["guide_session_manager", "group_tracker", "guided_route_builder", "post_hunt_reporter"],
    }


# =====================================================================
# ENDPOINTS 1-5: SESSION CRUD
# =====================================================================

@router.post("/sessions")
async def create_session(req: CreateSessionRequest):
    """Endpoint 1: Creer une session guidee."""
    result = guide_session_manager.create_session(
        guide_id=req.guide_id,
        territory_id=req.territory_id,
        title=req.title,
        species=req.species,
        start_date=req.start_date,
        end_date=req.end_date,
        bounds=req.bounds,
        config=req.config,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Endpoint 2: Lire une session."""
    result = guide_session_manager.get_session(session_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, req: UpdateSessionRequest):
    """Endpoint 3: Modifier une session."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    result = guide_session_manager.update_session(session_id, updates)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Endpoint 4: Annuler une session."""
    result = guide_session_manager.delete_session(session_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.get("/sessions/guide/{guide_id}")
async def list_sessions(guide_id: str):
    """Endpoint 5: Lister les sessions d'un guide."""
    return guide_session_manager.list_sessions(guide_id)


# =====================================================================
# ENDPOINTS 6-7: SESSION LIFECYCLE
# =====================================================================

@router.post("/sessions/{session_id}/start")
async def start_session(session_id: str):
    """Endpoint 6: Demarrer la session."""
    result = guide_session_manager.start_session(session_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str):
    """Endpoint 7: Terminer la session."""
    result = guide_session_manager.end_session(session_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# =====================================================================
# ENDPOINTS 8-9: CLIENT MANAGEMENT
# =====================================================================

@router.post("/sessions/{session_id}/clients")
async def add_client(session_id: str, req: AddClientRequest):
    """Endpoint 8: Ajouter un client a la session."""
    result = guide_session_manager.add_client(
        session_id=session_id,
        user_id=req.user_id,
        name=req.name,
        skill_level=req.skill_level,
        consent_gps=req.consent_gps,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.delete("/sessions/{session_id}/clients/{user_id}")
async def remove_client(session_id: str, user_id: str):
    """Endpoint 9: Retirer un client de la session."""
    result = guide_session_manager.remove_client(session_id, user_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


# =====================================================================
# ENDPOINT 10: GROUP TRACKING
# =====================================================================

@router.get("/sessions/{session_id}/positions")
async def get_positions(session_id: str):
    """Endpoint 10: Positions LIVE du groupe."""
    session = guide_session_manager.get_session_internal(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return group_tracker.get_group_positions(session)


# =====================================================================
# ENDPOINTS 11-12: ROUTE GENERATION
# =====================================================================

@router.post("/sessions/{session_id}/routes/generate")
async def generate_routes(session_id: str):
    """Endpoint 11: Generer les parcours optimises."""
    session = guide_session_manager.get_session_internal(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")

    result = guided_route_builder.generate_routes(session)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/sessions/{session_id}/routes")
async def get_routes(session_id: str):
    """Endpoint 12: Lire les parcours generes."""
    session = guide_session_manager.get_session_internal(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return guided_route_builder.get_routes(session)


# =====================================================================
# ENDPOINTS 13-14: REPORT
# =====================================================================

@router.post("/sessions/{session_id}/report")
async def generate_report(session_id: str):
    """Endpoint 13: Generer le rapport post-chasse."""
    session = guide_session_manager.get_session_internal(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")

    result = post_hunt_reporter.generate_report(session)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@router.get("/sessions/{session_id}/report")
async def get_report(session_id: str):
    """Endpoint 14: Lire le rapport post-chasse."""
    session = guide_session_manager.get_session_internal(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SESSION_NOT_FOUND")
    return post_hunt_reporter.get_report(session)
