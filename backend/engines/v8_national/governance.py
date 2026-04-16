"""
V8-GOVERNANCE — Master Switch Admin Premium
=============================================
V8-PREVIEW-Omega — GOVERNANCE-LOCK

Seul le Master Switch Admin Premium (Steeve) peut activer PREVIEW/PUBLIC.
Aucun module, moteur, pipeline ou commande ne peut modifier le mode
sans autorisation explicite via ce module.

Etats possibles:
  LOCKED    — V8 construit, non accessible utilisateurs (defaut)
  PREVIEW   — V8 accessible en mode preview (admin premium seulement)
  PUBLIC    — V8 accessible a tous les utilisateurs

Authority: COMMANDANT STEEVE-MAX exclusivement.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

logger = logging.getLogger("bionic.v8_governance")
router = APIRouter(prefix="/api/v8/governance", tags=["V8 Governance"])

# Collection MongoDB pour persister l'etat
GOVERNANCE_COLLECTION = "v8_governance"
GOVERNANCE_DOC_ID = "master_switch"

# Etat par defaut en memoire (fallback si MongoDB indisponible)
_DEFAULT_STATE = {
    "mode": "PREVIEW",
    "authority": "COMMANDANT_STEEVE_MAX",
    "activated_by": "admin@huntiq.com",
    "activated_at": "2026-04-16T00:00:00Z",
    "lock_version": "8.1.0",
}


async def _get_governance_state(db: AsyncIOMotorDatabase) -> dict:
    """Recupere l'etat de gouvernance depuis MongoDB."""
    doc = await db[GOVERNANCE_COLLECTION].find_one(
        {"doc_id": GOVERNANCE_DOC_ID}, {"_id": 0}
    )
    if not doc:
        # Initialiser avec l'etat par defaut
        state = {**_DEFAULT_STATE, "doc_id": GOVERNANCE_DOC_ID}
        await db[GOVERNANCE_COLLECTION].insert_one(state)
        return _DEFAULT_STATE
    return {k: v for k, v in doc.items() if k != "doc_id"}


async def _is_admin_premium(user: UserWithRole) -> bool:
    """Verifie si l'utilisateur est admin premium (authority suffisante).
    Authority: admin@huntiq.com (Commandant Steeve-Max) ou role admin/superadmin.
    """
    if user.email == "admin@huntiq.com":
        return True
    return user.role in ("admin", "premium_admin", "superadmin")


@router.get("/state")
async def governance_state(
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Etat actuel du Master Switch V8."""
    state = await _get_governance_state(db)
    return {
        "mode": state.get("mode", "LOCKED"),
        "authority": state.get("authority"),
        "activated_by": state.get("activated_by"),
        "activated_at": state.get("activated_at"),
        "lock_version": state.get("lock_version"),
        "allowed_modes": ["LOCKED", "PREVIEW", "PUBLIC"],
        "governance_policy": "Activation PREVIEW/PUBLIC reservee exclusivement au Master Switch Admin Premium (Commandant Steeve-Max)",
        "engine": "V8-GOVERNANCE",
        "dataVersion": "V8",
    }


@router.post("/activate")
async def activate_mode(
    mode: str = Body(..., embed=True),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Activer un mode V8 — RESERVE Admin Premium (Steeve)."""
    # Verification autorite
    if not await _is_admin_premium(user):
        logger.warning(f"[GOVERNANCE] REFUS activation {mode} par {user.email} (role={user.role})")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "GOVERNANCE_LOCK_VIOLATION",
                "message": "Activation PREVIEW/PUBLIC reservee exclusivement au Master Switch Admin Premium",
                "required_role": "admin",
                "your_role": user.role,
                "authority": "COMMANDANT_STEEVE_MAX",
            }
        )

    if mode not in ("LOCKED", "PREVIEW", "PUBLIC"):
        raise HTTPException(status_code=400, detail=f"Mode invalide: {mode}. Valeurs: LOCKED, PREVIEW, PUBLIC")

    now = datetime.now(timezone.utc).isoformat()
    update = {
        "mode": mode,
        "authority": "COMMANDANT_STEEVE_MAX",
        "activated_by": user.email,
        "activated_at": now,
        "lock_version": "8.1.0",
    }

    await db[GOVERNANCE_COLLECTION].update_one(
        {"doc_id": GOVERNANCE_DOC_ID},
        {"$set": {**update, "doc_id": GOVERNANCE_DOC_ID}},
        upsert=True,
    )

    logger.info(f"[GOVERNANCE] Mode {mode} ACTIVE par {user.email} (authority=COMMANDANT_STEEVE_MAX)")

    return {
        "success": True,
        "mode": mode,
        "activated_by": user.email,
        "activated_at": now,
        "message": f"V8 mode {mode} active par autorite COMMANDANT_STEEVE_MAX",
        "engine": "V8-GOVERNANCE",
    }


@router.get("/audit")
async def governance_audit(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Audit de gouvernance V8 — acces admin uniquement."""
    if not await _is_admin_premium(user):
        raise HTTPException(status_code=403, detail="Acces audit reserve admin premium")

    state = await _get_governance_state(db)
    return {
        "current_state": state,
        "governance_rules": [
            "1. Aucun module ne peut activer PREVIEW/PUBLIC sans Master Switch",
            "2. Master Switch = Admin Premium exclusivement",
            "3. Authority = COMMANDANT_STEEVE_MAX",
            "4. Tout changement de mode est logge et auditable",
            "5. Mode LOCKED = V8 construit mais non accessible",
            "6. Mode PREVIEW = accessible admin premium seulement",
            "7. Mode PUBLIC = accessible tous utilisateurs",
        ],
        "engine": "V8-GOVERNANCE",
        "dataVersion": "V8",
    }
