"""
Guide Session Manager — CRUD + Lifecycle Sessions Guidees
BIONIC OS V8.5 | Phase E-1 | BCE-4X GOLDEN V6+

DataContract: DC-15 GuidedSessionContract
EventBus: EB-20 guide:session:update
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger("guide_pro.session_manager")

# =====================================================================
# IN-MEMORY STORE (sera migre vers MongoDB post-validation)
# =====================================================================
_sessions: Dict[str, Dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_guide_role(guide_id: str) -> bool:
    """Verification role GUIDE via roles_engine (Point de Fusion PF-E1)."""
    try:
        from modules.roles_engine.v1.service import get_user_role
        role = get_user_role(guide_id)
        return role and role.value in ("guide", "admin", "manager")
    except Exception:
        # Fallback: accepter tout guide_id non vide
        logger.debug(f"[GUIDE PRO] roles_engine non disponible, fallback guide_id={guide_id}")
        return bool(guide_id)


def create_session(
    guide_id: str,
    territory_id: str,
    title: str,
    species: str,
    start_date: str,
    end_date: str,
    bounds: Optional[Dict] = None,
    config: Optional[Dict] = None,
) -> Dict:
    """Creer une session de chasse guidee."""
    if not _validate_guide_role(guide_id):
        return {"success": False, "error": "INVALID_GUIDE_ROLE"}

    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "guide_id": guide_id,
        "territory_id": territory_id,
        "title": title,
        "species": species,
        "status": "planned",
        "start_date": start_date,
        "end_date": end_date,
        "actual_start": None,
        "actual_end": None,
        "clients": [],
        "bounds": bounds or {},
        "config": {
            "walking_speed_kmh": 3.5,
            "max_group_spread_m": 500.0,
            "emergency_radius_m": 200.0,
            "require_gps_consent": True,
            **(config or {}),
        },
        "routes": [],
        "predictions": {},
        "report": {"generated": False},
        "created_at": _now(),
        "updated_at": _now(),
    }

    _sessions[session_id] = session
    logger.info(f"[GUIDE PRO] Session creee: {session_id} ({title})")
    return {"success": True, "session": _sanitize(session)}


def get_session(session_id: str) -> Dict:
    """Lire une session."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    return {"success": True, "session": _sanitize(session)}


def update_session(session_id: str, updates: Dict) -> Dict:
    """Modifier une session (uniquement si planned ou paused)."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    if session["status"] not in ("planned", "paused"):
        return {"success": False, "error": "SESSION_NOT_MODIFIABLE"}

    allowed_fields = {"title", "species", "start_date", "end_date", "bounds", "config"}
    for key, value in updates.items():
        if key in allowed_fields:
            session[key] = value

    session["updated_at"] = _now()
    logger.info(f"[GUIDE PRO] Session modifiee: {session_id}")
    return {"success": True, "session": _sanitize(session)}


def delete_session(session_id: str) -> Dict:
    """Annuler une session."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}

    session["status"] = "cancelled"
    session["updated_at"] = _now()
    logger.info(f"[GUIDE PRO] Session annulee: {session_id}")
    return {"success": True, "message": "SESSION_CANCELLED"}


def list_sessions(guide_id: str) -> Dict:
    """Lister les sessions d'un guide."""
    sessions = [
        _sanitize(s) for s in _sessions.values()
        if s["guide_id"] == guide_id and s["status"] != "cancelled"
    ]
    return {"success": True, "sessions": sessions, "count": len(sessions)}


def start_session(session_id: str) -> Dict:
    """Demarrer une session de chasse."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    if session["status"] != "planned":
        return {"success": False, "error": "SESSION_NOT_STARTABLE"}
    if not session["clients"]:
        return {"success": False, "error": "NO_CLIENTS"}

    session["status"] = "active"
    session["actual_start"] = _now()
    session["updated_at"] = _now()
    logger.info(f"[GUIDE PRO] Session demarree: {session_id}")
    return {"success": True, "session": _sanitize(session)}


def end_session(session_id: str) -> Dict:
    """Terminer une session de chasse."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    if session["status"] != "active":
        return {"success": False, "error": "SESSION_NOT_ACTIVE"}

    session["status"] = "completed"
    session["actual_end"] = _now()
    session["updated_at"] = _now()
    logger.info(f"[GUIDE PRO] Session terminee: {session_id}")
    return {"success": True, "session": _sanitize(session)}


def add_client(
    session_id: str,
    user_id: str,
    name: str,
    skill_level: str = "intermediate",
    consent_gps: bool = True,
) -> Dict:
    """Ajouter un client a une session."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    if session["status"] not in ("planned",):
        return {"success": False, "error": "SESSION_NOT_MODIFIABLE"}

    # Verifier doublon
    for c in session["clients"]:
        if c["user_id"] == user_id:
            return {"success": False, "error": "CLIENT_ALREADY_EXISTS"}

    client = {
        "user_id": user_id,
        "name": name,
        "skill_level": skill_level,
        "consent_gps": consent_gps,
        "assigned_sector": None,
        "status": "confirmed",
    }
    session["clients"].append(client)
    session["updated_at"] = _now()

    # Point de Fusion PF-E5: Profil M4
    try:
        from modules.adaptive_navigation_engine.services.user_profile_learner import (
            get_or_create_profile,
        )
        get_or_create_profile(user_id)
    except Exception:
        pass

    logger.info(f"[GUIDE PRO] Client ajoute: {user_id} → session {session_id}")
    return {"success": True, "client": client}


def remove_client(session_id: str, user_id: str) -> Dict:
    """Retirer un client d'une session."""
    session = _sessions.get(session_id)
    if not session:
        return {"success": False, "error": "SESSION_NOT_FOUND"}
    if session["status"] not in ("planned",):
        return {"success": False, "error": "SESSION_NOT_MODIFIABLE"}

    original_len = len(session["clients"])
    session["clients"] = [c for c in session["clients"] if c["user_id"] != user_id]
    if len(session["clients"]) == original_len:
        return {"success": False, "error": "CLIENT_NOT_FOUND"}

    session["updated_at"] = _now()
    logger.info(f"[GUIDE PRO] Client retire: {user_id} de session {session_id}")
    return {"success": True, "message": "CLIENT_REMOVED"}


def _sanitize(session: Dict) -> Dict:
    """Copie securisee sans reference interne."""
    return {k: v for k, v in session.items()}


def get_session_internal(session_id: str) -> Optional[Dict]:
    """Acces interne pour mutation (router seulement). Retourne la reference directe."""
    return _sessions.get(session_id)
