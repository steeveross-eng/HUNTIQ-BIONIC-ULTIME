"""
Gestionnaire Engine -- Router
=============================================================
Directive x7100-M4 Phase C | BCE-4X GOLDEN V6+

Source unique de verite pour :
  - Localisation LIVE (DC-12)
  - Gestion secteurs/blocs (DC-13)
  - Urgences SECOURS (DC-14)
  - Consentement GPS
  - Cloisonnement par territoire/organisation

Endpoints :
  0. GET    /health
  1. POST   /position              (reception position LIVE)
  2. GET    /positions/{territory}  (positions LIVE du territoire)
  3. GET    /sectors/{territory}    (secteurs du territoire)
  4. POST   /sectors/{sector_id}/status
  5. POST   /sectors/{sector_id}/assign
  6. POST   /sectors/{sector_id}/remove
  7. POST   /emergency             (declenchement alerte)
  8. POST   /emergency/{alert_id}/ack
  9. POST   /emergency/{alert_id}/resolve
  10. GET   /emergency/active/{territory}
  11. POST  /consent               (enregistrer consentement GPS)
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Body
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

router = APIRouter(prefix="/api/v1/gestionnaire", tags=["Gestionnaire Engine"])

VALID_COUNTRIES = {"CA", "US", "QC"}


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


@router.get("/health")
async def health():
    return {
        "status": "operational",
        "engine": "gestionnaire_engine",
        "version": "1.0.0",
        "phase": "M4-PHASE-C",
        "directive": "x7100-M4",
        "endpoints": 12,
        "services": ["PositionLive", "SectorManager", "EmergencySecours", "ConsentGPS"],
    }


# ==============================================
# POSITION LIVE (DC-12)
# ==============================================

@router.post("/position")
async def receive_position(payload: Dict[str, Any] = Body(...)):
    """Reception position LIVE chasseur. Stocke dans live_positions."""
    db = _get_db()
    user_id = payload.get("user_id", "")
    if not user_id:
        return {"success": False, "error": "MISSING_USER_ID"}

    doc = {
        "user_id": user_id,
        "lat": payload.get("lat", 0),
        "lng": payload.get("lng", 0),
        "accuracy": payload.get("accuracy", 0),
        "heading": payload.get("heading"),
        "speed": payload.get("speed", 0),
        "altitude": payload.get("altitude"),
        "timestamp": payload.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "status": payload.get("status", "active"),
        "consent": payload.get("consent", "none"),
        "territory_id": payload.get("territory_id", ""),
    }

    await db.live_positions.update_one(
        {"user_id": user_id},
        {"$set": doc},
        upsert=True
    )

    # Append to position history
    history = {**doc, "recorded_at": datetime.now(timezone.utc).isoformat()}
    await db.position_history.insert_one(history)

    return {"success": True, "position": {k: v for k, v in doc.items() if k != "_id"}}


@router.get("/positions/{territory_id}")
async def get_territory_positions(territory_id: str):
    """Positions LIVE de tous les chasseurs consentants dans un territoire."""
    db = _get_db()
    cursor = db.live_positions.find(
        {"territory_id": territory_id, "consent": {"$in": ["permanent", "emergency"]}},
        {"_id": 0}
    )
    positions = await cursor.to_list(length=200)
    return {
        "success": True,
        "territory_id": territory_id,
        "positions": positions,
        "count": len(positions),
    }


# ==============================================
# SECTEURS / BLOCS (DC-13)
# ==============================================

@router.get("/sectors/{territory_id}")
async def get_sectors(territory_id: str):
    """Secteurs/blocs d'un territoire."""
    db = _get_db()
    cursor = db.sectors.find({"territory_id": territory_id}, {"_id": 0})
    sectors = await cursor.to_list(length=100)
    return {"success": True, "territory_id": territory_id, "sectors": sectors, "count": len(sectors)}


@router.post("/sectors/{sector_id}/status")
async def update_sector_status(sector_id: str, payload: Dict[str, Any] = Body(...)):
    """Mettre a jour le statut d'un secteur (libre/occupe)."""
    db = _get_db()
    status = payload.get("status", "libre")
    now = datetime.now(timezone.utc).isoformat()

    result = await db.sectors.find_one_and_update(
        {"sector_id": sector_id},
        {"$set": {"status": status, "updated_at": now}},
        return_document=True
    )
    if result:
        result.pop("_id", None)
        return {"success": True, "sector": result}
    return {"success": False, "error": "SECTOR_NOT_FOUND"}


@router.post("/sectors/{sector_id}/assign")
async def assign_hunter(sector_id: str, payload: Dict[str, Any] = Body(...)):
    """Assigner un chasseur a un secteur."""
    db = _get_db()
    user_id = payload.get("user_id", "")
    now = datetime.now(timezone.utc).isoformat()

    result = await db.sectors.find_one_and_update(
        {"sector_id": sector_id},
        {
            "$addToSet": {"hunters": {"user_id": user_id, "name": payload.get("name", ""), "entered_at": now}},
            "$set": {"status": "occupe", "updated_at": now},
            "$inc": {"hunters_count": 1},
        },
        return_document=True
    )
    if result:
        result.pop("_id", None)
        return {"success": True, "sector": result}
    return {"success": False, "error": "SECTOR_NOT_FOUND"}


@router.post("/sectors/{sector_id}/remove")
async def remove_hunter(sector_id: str, payload: Dict[str, Any] = Body(...)):
    """Retirer un chasseur d'un secteur."""
    db = _get_db()
    user_id = payload.get("user_id", "")
    now = datetime.now(timezone.utc).isoformat()

    result = await db.sectors.find_one_and_update(
        {"sector_id": sector_id},
        {
            "$pull": {"hunters": {"user_id": user_id}},
            "$set": {"updated_at": now},
            "$inc": {"hunters_count": -1},
        },
        return_document=True
    )
    if result:
        result.pop("_id", None)
        hunters_count = len(result.get("hunters", []))
        if hunters_count == 0:
            await db.sectors.update_one({"sector_id": sector_id}, {"$set": {"status": "libre", "hunters_count": 0}})
            result["status"] = "libre"
            result["hunters_count"] = 0
        return {"success": True, "sector": result}
    return {"success": False, "error": "SECTOR_NOT_FOUND"}


# ==============================================
# URGENCES / SECOURS (DC-14)
# ==============================================

@router.post("/emergency")
async def trigger_emergency(payload: Dict[str, Any] = Body(...)):
    """Declenchement alerte SECOURS."""
    db = _get_db()
    alert_id = payload.get("alert_id", str(uuid.uuid4()))
    now = datetime.now(timezone.utc).isoformat()

    alert = {
        "alert_id": alert_id,
        "user_id": payload.get("user_id", ""),
        "user_name": payload.get("user_name", ""),
        "position": payload.get("position", {"lat": 0, "lng": 0, "accuracy": 0}),
        "timestamp": now,
        "status": "active",
        "type": payload.get("type", "secours"),
        "message": payload.get("message", "URGENCE"),
        "channel_id": payload.get("channel_id", f"emergency_{alert_id}"),
        "territory_id": payload.get("territory_id", ""),
        "responders": [],
        "created_at": now,
    }

    await db.emergency_alerts.insert_one(alert)
    alert.pop("_id", None)

    return {"success": True, "alert": alert}


@router.post("/emergency/{alert_id}/ack")
async def acknowledge_emergency(alert_id: str, payload: Dict[str, Any] = Body(...)):
    """Acquitter une alerte SECOURS."""
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    responder = {
        "user_id": payload.get("user_id", ""),
        "name": payload.get("name", ""),
        "acknowledged_at": now,
    }

    result = await db.emergency_alerts.find_one_and_update(
        {"alert_id": alert_id, "status": "active"},
        {"$addToSet": {"responders": responder}},
        return_document=True
    )
    if result:
        result.pop("_id", None)
        return {"success": True, "alert": result}
    return {"success": False, "error": "ALERT_NOT_FOUND_OR_RESOLVED"}


@router.post("/emergency/{alert_id}/resolve")
async def resolve_emergency(alert_id: str, payload: Dict[str, Any] = Body(...)):
    """Resoudre une alerte SECOURS."""
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()

    result = await db.emergency_alerts.find_one_and_update(
        {"alert_id": alert_id},
        {"$set": {"status": "resolved", "resolved_at": now}},
        return_document=True
    )
    if result:
        result.pop("_id", None)
        return {"success": True, "alert": result}
    return {"success": False, "error": "ALERT_NOT_FOUND"}


@router.get("/emergency/active/{territory_id}")
async def get_active_alerts(territory_id: str):
    """Alertes actives d'un territoire."""
    db = _get_db()
    cursor = db.emergency_alerts.find(
        {"territory_id": territory_id, "status": "active"},
        {"_id": 0}
    )
    alerts = await cursor.to_list(length=50)
    return {"success": True, "territory_id": territory_id, "alerts": alerts, "count": len(alerts)}


# ==============================================
# CONSENTEMENT GPS
# ==============================================

@router.post("/consent")
async def register_consent(payload: Dict[str, Any] = Body(...)):
    """Enregistrer consentement GPS (permanent/session/none)."""
    db = _get_db()
    user_id = payload.get("user_id", "")
    consent_type = payload.get("consent", "none")
    now = datetime.now(timezone.utc).isoformat()

    await db.gps_consents.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "consent": consent_type,
            "territory_id": payload.get("territory_id", ""),
            "granted_at": now,
            "updated_at": now,
        }},
        upsert=True
    )

    return {
        "success": True,
        "user_id": user_id,
        "consent": consent_type,
        "advantages": [
            "SECOURS instantane",
            "GUIDE PRO automatique",
            "Position LIVE sur CARTE",
            "Hotspots dynamiques",
            "Synchronisation traces/waypoints",
            "Experience terrain fluide"
        ] if consent_type == "permanent" else [],
    }
