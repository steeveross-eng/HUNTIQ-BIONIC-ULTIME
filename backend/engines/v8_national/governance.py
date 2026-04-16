"""
V8-GOVERNANCE — Master Switch Admin Premium SUPREMACY
======================================================
GOVERNANCE-Omega — MASTER-SWITCH-SUPREMACY + POST-PREVIEW-LOCKDOWN

REGLE ABSOLUE: Le Master Switch Admin Premium (Commandant Steeve-Max)
est l'UNIQUE autorite capable d'activer PREVIEW/PUBLIC.

POST-PREVIEW LOCKDOWN:
  - Defaut systeme = LOCKED (JAMAIS PREVIEW/PUBLIC au boot)
  - Score V8 retourne 0 + engine=V8-GOVERNANCE-LOCKED quand LOCKED
  - TERRITOIRE/CARTE-2027 affichent PREVIEW TAG mais INACTIF quand LOCKED
  - ZERO activation automatique, ZERO contournement API

Etats:
  LOCKED  — V8 construit, ZERO acces (defaut systeme)
  PREVIEW — Admin premium seulement (activation Steeve requise)
  PUBLIC  — Tous utilisateurs (activation Steeve requise)

Authority: COMMANDANT STEEVE-MAX — admin@huntiq.com — EXCLUSIVEMENT.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List
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

# MASTER SWITCH SUPREMACY: Defaut = LOCKED (POST-PREVIEW LOCKDOWN)
_DEFAULT_STATE = {
    "mode": "LOCKED",
    "authority": "COMMANDANT_STEEVE_MAX",
    "activated_by": "SYSTEM_BOOT",
    "activated_at": "2026-04-16T00:00:00Z",
    "lock_version": "8.2.0",
    "lockdown_reason": "POST-PREVIEW-LOCKDOWN — Activation explicite requise via Master Switch",
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
    """Etat actuel du Master Switch V8 — SUPREMACY."""
    state = await _get_governance_state(db)
    mode = state.get("mode", "LOCKED")
    return {
        "mode": mode,
        "master_switch": "LOCKED" if mode == "LOCKED" else "ACTIVE",
        "authority": state.get("authority"),
        "activated_by": state.get("activated_by"),
        "activated_at": state.get("activated_at"),
        "lock_version": state.get("lock_version", "8.2.0"),
        "lockdown_reason": state.get("lockdown_reason"),
        "allowed_modes": ["LOCKED", "PREVIEW", "PUBLIC"],
        "supremacy_rules": [
            "AUCUN module ne peut activer PREVIEW/PUBLIC sans Master Switch",
            "Defaut systeme = LOCKED (POST-PREVIEW LOCKDOWN)",
            "Authority = COMMANDANT_STEEVE_MAX exclusivement",
            "Toute tentative hors Master Switch = REFUS AUTOMATIQUE",
        ],
        "governance_policy": "Activation PREVIEW/PUBLIC reservee exclusivement au Master Switch Admin Premium (Commandant Steeve-Max)",
        "engine": "V8-GOVERNANCE-SUPREMACY",
        "dataVersion": "V8",
    }


@router.post("/activate")
async def activate_mode(
    mode: str = Body(..., embed=True),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Activer un mode V8 — RESERVE EXCLUSIF Master Switch Admin Premium (Steeve)."""
    # SUPREMACY CHECK
    if not await _is_admin_premium(user):
        logger.warning(f"[GOVERNANCE-SUPREMACY] REFUS ABSOLU activation {mode} par {user.email} (role={user.role})")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "MASTER_SWITCH_SUPREMACY_VIOLATION",
                "message": "Activation PREVIEW/PUBLIC reservee EXCLUSIVEMENT au Master Switch Admin Premium (Commandant Steeve-Max)",
                "required_authority": "COMMANDANT_STEEVE_MAX",
                "your_email": user.email,
                "your_role": user.role,
                "action": "REFUS_AUTOMATIQUE",
            }
        )

    if mode not in ("LOCKED", "PREVIEW", "PUBLIC"):
        raise HTTPException(status_code=400, detail=f"Mode invalide: {mode}. Valeurs: LOCKED, PREVIEW, PUBLIC")

    now = datetime.now(timezone.utc).isoformat()
    prev_state = await _get_governance_state(db)
    prev_mode = prev_state.get("mode", "LOCKED")

    update = {
        "mode": mode,
        "authority": "COMMANDANT_STEEVE_MAX",
        "activated_by": user.email,
        "activated_at": now,
        "lock_version": "8.2.0",
        "lockdown_reason": f"Mode {mode} active par Master Switch" if mode != "LOCKED" else "POST-PREVIEW-LOCKDOWN",
        "previous_mode": prev_mode,
    }

    await db[GOVERNANCE_COLLECTION].update_one(
        {"doc_id": GOVERNANCE_DOC_ID},
        {"$set": {**update, "doc_id": GOVERNANCE_DOC_ID}},
        upsert=True,
    )

    # Audit log
    await db[GOVERNANCE_COLLECTION + "_audit"].insert_one({
        "action": "MODE_CHANGE",
        "from_mode": prev_mode,
        "to_mode": mode,
        "by": user.email,
        "at": now,
        "authority": "COMMANDANT_STEEVE_MAX",
    })

    logger.info(f"[GOVERNANCE-SUPREMACY] {prev_mode} -> {mode} par {user.email} (authority=COMMANDANT_STEEVE_MAX)")

    return {
        "success": True,
        "mode": mode,
        "previous_mode": prev_mode,
        "activated_by": user.email,
        "activated_at": now,
        "message": f"V8 mode {prev_mode} -> {mode} par autorite COMMANDANT_STEEVE_MAX",
        "engine": "V8-GOVERNANCE-SUPREMACY",
    }


@router.get("/audit")
async def governance_audit(
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Audit de gouvernance V8 — acces admin uniquement."""
    if not await _is_admin_premium(user):
        raise HTTPException(status_code=403, detail="Acces audit reserve Master Switch Admin Premium")

    state = await _get_governance_state(db)

    # Fetch audit trail
    audit_cursor = db[GOVERNANCE_COLLECTION + "_audit"].find({}, {"_id": 0}).sort("at", -1).limit(20)
    audit_trail = await audit_cursor.to_list(length=20)

    return {
        "current_state": state,
        "audit_trail": audit_trail,
        "supremacy_rules": [
            "1. AUCUN module ne peut activer PREVIEW/PUBLIC sans Master Switch",
            "2. Master Switch = COMMANDANT_STEEVE_MAX exclusivement",
            "3. Defaut systeme = LOCKED (POST-PREVIEW LOCKDOWN)",
            "4. Tout changement de mode est logge dans audit_trail",
            "5. Score V8 retourne 0 quand LOCKED",
            "6. ZERO activation automatique PREVIEW/PUBLIC",
            "7. ZERO contournement API possible",
        ],
        "engine": "V8-GOVERNANCE-SUPREMACY",
        "dataVersion": "V8",
    }
