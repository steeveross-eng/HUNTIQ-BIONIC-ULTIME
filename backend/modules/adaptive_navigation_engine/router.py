"""
Adaptive Navigation Engine -- Router M4
=============================================================
Directive x7100-M4 -- Phase M4 MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : recommendation_engine, predictive_engine, solunar,
               scoring_engine, poi_scorer consommes en LECTURE.
ANTI-DOUBLON NUTRITIONNEL : enrichissement via nutrition_v6_interface (LECTURE).
Points de fusion : 19 (PF4-S1/S2, PF4-LUN1/LUN2, PF4-MET1, PF4-M1a/b,
    PF4-M2a/b/c/d, PF4-M3a/b/c/d/e, PF4-TRIP1, PF4-N1/N2)

12 Endpoints (1 health + 11 fonctionnels) :
  0. GET   /health
  1. GET   /profile/{user_id}
  2. PATCH /profile/{user_id}
  3. POST  /profile/{user_id}/learn
  4. POST  /plan-route
  5. GET   /plan-route/{session_id}
  6. POST  /optimize
  7. GET   /suggestions/{user_id}
  8. GET   /advice/{user_id}/{lat}/{lng}
  9. POST  /session/start
  10. POST /session/{session_id}/end
  11. GET  /session/{session_id}/status
"""

from fastapi import APIRouter, Body
from typing import Dict, Any

from .services.user_profile_learner import (
    get_or_create_profile,
    update_preferences,
    learn_from_history,
    get_species_affinity,
    ensure_indexes as ensure_profile_indexes
)
from .services.navigation_planner import (
    plan_route,
    get_session,
    start_session,
    end_session,
    get_session_status,
    ensure_indexes as ensure_session_indexes
)
from .services.route_optimizer import optimize_route
from .services.contextual_advisor import get_suggestions, get_advice

router = APIRouter(prefix="/api/v1/nav-intel", tags=["M4 Adaptive Navigation Engine"])

_indexes_created = False


async def _ensure_indexes_once():
    global _indexes_created
    if not _indexes_created:
        try:
            await ensure_profile_indexes()
            await ensure_session_indexes()
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
        "engine": "adaptive_navigation_engine",
        "version": "1.0.0",
        "phase": "M4-MAP-INTELLIGENCE",
        "directive": "x7100-M4",
        "endpoints": 12,
        "fusion_points": 19,
        "services": [
            "UserProfileLearner",
            "NavigationPlanner",
            "RouteOptimizer",
            "ContextualAdvisor"
        ],
        "anti_doublon": [
            "recommendation_engine", "predictive_engine",
            "solunar", "scoring_engine", "poi_scorer"
        ]
    }


# ==============================================
# ADAPTIVE USER PROFILE -- M4-A (1-3)
# ==============================================

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """M4-1: Profil adaptatif complet (get or create)."""
    await _ensure_indexes_once()
    profile = await get_or_create_profile(user_id)
    affinity = await get_species_affinity(user_id)
    return {
        "success": True,
        "profile": profile,
        "species_affinity": affinity.get("affinities", []),
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


@router.patch("/profile/{user_id}")
async def patch_profile(user_id: str, payload: Dict[str, Any] = Body(...)):
    """M4-2: Mettre a jour preferences explicites."""
    await _ensure_indexes_once()
    result = await update_preferences(user_id, payload)
    if result is None:
        # Profile doesn't exist yet, create it first
        await get_or_create_profile(user_id)
        result = await update_preferences(user_id, payload)

    return {
        "success": True,
        "profile": result,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


@router.post("/profile/{user_id}/learn")
async def trigger_learning(user_id: str):
    """M4-3: Declencher apprentissage depuis hunting_trips."""
    await _ensure_indexes_once()
    result = await learn_from_history(user_id)
    return {
        "success": True,
        **result,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


# ==============================================
# SUGGESTIONS -- M4-A (7)
# ==============================================

@router.get("/suggestions/{user_id}")
async def get_user_suggestions(user_id: str):
    """M4-7: Suggestions personnalisees basees sur le profil."""
    await _ensure_indexes_once()
    result = await get_suggestions(user_id)
    return {
        "success": True,
        **result,
        "directive": "x7100-M4"
    }


# ==============================================
# NAVIGATION -- M4-B (4-6)
# ==============================================

@router.post("/plan-route")
async def create_plan(payload: Dict[str, Any] = Body(...)):
    """M4-4: Planifier itineraire optimal."""
    await _ensure_indexes_once()

    required = ["user_id", "target_species", "zone_id"]
    missing = [f for f in required if f not in payload]
    if missing:
        return {"success": False, "error": "MISSING_FIELDS", "fields": missing}

    session = await plan_route(
        user_id=payload["user_id"],
        target_species=payload["target_species"],
        zone_id=payload["zone_id"],
        start_lat=payload.get("start_lat", 0),
        start_lng=payload.get("start_lng", 0),
        criteria=payload.get("criteria")
    )

    return {
        "success": True,
        "session": session,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


@router.get("/plan-route/{session_id}")
async def get_plan(session_id: str):
    """M4-5: Detail itineraire planifie."""
    session = await get_session(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    return {
        "success": True,
        "session": session,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


@router.post("/optimize")
async def optimize(payload: Dict[str, Any] = Body(...)):
    """M4-6: Optimiser itineraire existant."""
    await _ensure_indexes_once()

    session_id = payload.get("session_id")
    if not session_id:
        return {"success": False, "error": "MISSING_FIELDS", "fields": ["session_id"]}

    result = await optimize_route(session_id, payload.get("criteria"))
    if result is None:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    if "error" in result:
        return {"success": False, **result}

    return {
        "success": True,
        "session": result,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


# ==============================================
# ADVICE -- M4-B (8)
# ==============================================

@router.get("/advice/{user_id}/{lat}/{lng}")
async def get_contextual_advice(user_id: str, lat: float, lng: float):
    """M4-8: Conseil contextuel GPS."""
    await _ensure_indexes_once()
    result = await get_advice(user_id, lat, lng)
    return {
        "success": True,
        **result
    }


# ==============================================
# SESSIONS -- M4-B (9-11)
# ==============================================

@router.post("/session/start")
async def session_start(payload: Dict[str, Any] = Body(...)):
    """M4-9: Demarrer session navigation."""
    session_id = payload.get("session_id")
    if not session_id:
        return {"success": False, "error": "MISSING_FIELDS", "fields": ["session_id"]}

    result = await start_session(session_id)
    if not result:
        return {"success": False, "error": "SESSION_NOT_FOUND_OR_NOT_PLANNED"}

    return {
        "success": True,
        "session": result,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


@router.post("/session/{session_id}/end")
async def session_end(session_id: str, payload: Dict[str, Any] = Body({})):
    """M4-10: Terminer session avec metriques."""
    result = await end_session(session_id, payload.get("metrics"))
    if not result:
        return {"success": False, "error": "SESSION_NOT_FOUND_OR_NOT_ACTIVE"}

    return {
        "success": True,
        "session": result,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }


@router.get("/session/{session_id}/status")
async def session_status(session_id: str):
    """M4-11: Statut session active."""
    result = await get_session_status(session_id)
    if not result:
        return {"success": False, "error": "SESSION_NOT_FOUND"}

    return {
        "success": True,
        **result,
        "source": "adaptive_navigation_engine",
        "directive": "x7100-M4"
    }
