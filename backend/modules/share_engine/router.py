"""
SHARE ENGINE — BCE-4X GOLDEN V6+ Module PARTAGER + MASTER SWITCH
=================================================================
Master Switch Premium: point de contrôle UNIQUE de tout partage externe.
Tracking Premium: clics, partages, conversions, engagement, scoring.
Intégration ADMIN PREMIUM: attribution, campagnes, optimisation.

Endpoints:
  POST /api/share/track          — Enregistre un événement de partage (via Master Switch)
  GET  /api/share/stats          — Statistiques de partage (Admin Premium)
  GET  /api/share/status         — Status du module + Master Switch
  GET  /api/share/master-switch  — État du Master Switch
  PUT  /api/share/master-switch  — Modifier l'état du Master Switch (STEEVE-MAX only)
"""
import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("share_engine")
router = APIRouter(prefix="/api/share", tags=["SHARE-BIONIC"])

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "huntiq_v6")

# ═══════════════════════════════════════════
# MASTER SWITCH PREMIUM — État global
# Mode ON permanent jusqu'à désactivation manuelle par STEEVE-MAX
# ═══════════════════════════════════════════
MASTER_SWITCH_STATE = {
    "global_enabled": False,        # OFF par défaut — activation manuelle STEEVE-MAX uniquement
    "override_mode": False,         # Pas d'override — contrôle manuel total
    "authority": "STEEVE-MAX",      # Seul STEEVE-MAX peut activer
    "channels": {
        "native":    {"enabled": False, "label": "Partage OS",  "priority": 1},
        "facebook":  {"enabled": False, "label": "Facebook",    "priority": 2},
        "messenger": {"enabled": False, "label": "Messenger",   "priority": 3},
        "whatsapp":  {"enabled": False, "label": "WhatsApp",    "priority": 4},
        "instagram": {"enabled": False, "label": "Instagram",   "priority": 5},
        "tiktok":    {"enabled": False, "label": "TikTok",      "priority": 6},
        "sms":       {"enabled": False, "label": "SMS",         "priority": 7},
        "copy":      {"enabled": False, "label": "Copier lien", "priority": 8},
    },
    "admin_sync": {
        "messaging_engine": True,
        "x300_strategy": True,
        "seo_engine": True,
        "affiliate_ads": True,
        "reseautage": True,
        "email_marketing": True,
        "analytics_engine": True,
        "partnership_engine": True,
        "freemium_upsell": True,
    },
    "activated_at": datetime.now(timezone.utc).isoformat(),
    "last_modified_by": "STEEVE-MAX",
    "protocol": "BCE-4X GOLDEN V6+",
}


def get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DB_NAME]


class ShareTrackEvent(BaseModel):
    channel: str
    template: str
    url: Optional[str] = None
    timestamp: Optional[str] = None
    hasWeather: Optional[bool] = False


class MasterSwitchUpdate(BaseModel):
    global_enabled: Optional[bool] = None
    channel_updates: Optional[Dict[str, bool]] = None
    authority_key: str = ""


@router.post("/track")
async def track_share(event: ShareTrackEvent):
    """Enregistre un événement de partage via le Master Switch Pipeline."""
    # Master Switch gate — vérifie que le canal est activé
    if not MASTER_SWITCH_STATE["global_enabled"]:
        return {"status": "blocked", "reason": "master_switch_off"}

    channel_config = MASTER_SWITCH_STATE["channels"].get(event.channel)
    if not channel_config or not channel_config["enabled"]:
        return {"status": "blocked", "reason": f"channel_{event.channel}_disabled"}

    db = get_db()
    doc = {
        "channel": event.channel,
        "template": event.template,
        "url": event.url,
        "has_weather": event.hasWeather,
        "master_switch": "ON",
        "channel_priority": channel_config["priority"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "client_timestamp": event.timestamp,
    }
    await db.share_events.insert_one(doc)

    logger.info(
        f"[MASTER-SWITCH] Share tracked: channel={event.channel}, "
        f"template={event.template}, priority={channel_config['priority']}"
    )

    return {
        "status": "tracked",
        "channel": event.channel,
        "master_switch": "ON",
        "priority": channel_config["priority"],
    }


@router.get("/stats")
async def share_stats():
    """Statistiques de partage — Admin Premium via Master Switch."""
    db = get_db()
    total = await db.share_events.count_documents({})

    pipeline_channel = [
        {"$group": {"_id": "$channel", "count": {"$sum": 1}}}
    ]
    by_channel = {}
    async for doc in db.share_events.aggregate(pipeline_channel):
        by_channel[doc["_id"]] = doc["count"]

    pipeline_template = [
        {"$group": {"_id": "$template", "count": {"$sum": 1}}}
    ]
    by_template = {}
    async for doc in db.share_events.aggregate(pipeline_template):
        by_template[doc["_id"]] = doc["count"]

    cutoff = datetime.now(timezone.utc).isoformat()
    last_24h = await db.share_events.count_documents({
        "created_at": {"$gte": cutoff[:10]}
    })

    return {
        "total_shares": total,
        "by_channel": by_channel,
        "by_template": by_template,
        "last_24h": last_24h,
        "master_switch": "ON" if MASTER_SWITCH_STATE["global_enabled"] else "OFF",
    }


@router.get("/master-switch")
async def get_master_switch():
    """Retourne l'état complet du Master Switch Premium."""
    channels_status = {}
    for ch_id, ch_config in MASTER_SWITCH_STATE["channels"].items():
        channels_status[ch_id] = {
            "enabled": ch_config["enabled"],
            "label": ch_config["label"],
            "priority": ch_config["priority"],
        }

    return {
        "global_enabled": MASTER_SWITCH_STATE["global_enabled"],
        "override_mode": MASTER_SWITCH_STATE["override_mode"],
        "authority": MASTER_SWITCH_STATE["authority"],
        "channels": channels_status,
        "admin_sync": MASTER_SWITCH_STATE["admin_sync"],
        "activated_at": MASTER_SWITCH_STATE["activated_at"],
        "last_modified_by": MASTER_SWITCH_STATE["last_modified_by"],
        "protocol": MASTER_SWITCH_STATE["protocol"],
        "total_channels_active": sum(
            1 for c in MASTER_SWITCH_STATE["channels"].values() if c["enabled"]
        ),
    }


@router.put("/master-switch")
async def update_master_switch(update: MasterSwitchUpdate):
    """Modifier l'état du Master Switch — STEEVE-MAX ONLY."""
    if update.authority_key != "STEEVE-MAX":
        raise HTTPException(
            status_code=403,
            detail="ACCÈS REFUSÉ — Seul STEEVE-MAX peut modifier le Master Switch"
        )

    if update.global_enabled is not None:
        MASTER_SWITCH_STATE["global_enabled"] = update.global_enabled
        # Si activation globale, activer tous les canaux
        if update.global_enabled:
            for ch_id in MASTER_SWITCH_STATE["channels"]:
                MASTER_SWITCH_STATE["channels"][ch_id]["enabled"] = True
        logger.info(f"[MASTER-SWITCH] Global: {'ON' if update.global_enabled else 'OFF'} — par STEEVE-MAX")

    if update.channel_updates:
        for ch_id, enabled in update.channel_updates.items():
            if ch_id in MASTER_SWITCH_STATE["channels"]:
                MASTER_SWITCH_STATE["channels"][ch_id]["enabled"] = enabled
                logger.info(f"[MASTER-SWITCH] Channel {ch_id}: {'ON' if enabled else 'OFF'}")

    MASTER_SWITCH_STATE["last_modified_by"] = "STEEVE-MAX"

    return {
        "status": "updated",
        "master_switch": MASTER_SWITCH_STATE["global_enabled"],
        "channels_active": sum(
            1 for c in MASTER_SWITCH_STATE["channels"].values() if c["enabled"]
        ),
    }


@router.get("/status")
async def share_status():
    """Status du module SHARE BIONIC + Master Switch."""
    return {
        "module": "share_engine",
        "version": "2.0.0",
        "protocol": "BCE-4X GOLDEN V6+",
        "status": "OPERATIONAL",
        "master_switch": {
            "global": "ON" if MASTER_SWITCH_STATE["global_enabled"] else "OFF",
            "override": MASTER_SWITCH_STATE["override_mode"],
            "authority": MASTER_SWITCH_STATE["authority"],
            "channels_active": sum(
                1 for c in MASTER_SWITCH_STATE["channels"].values() if c["enabled"]
            ),
        },
        "channels": list(MASTER_SWITCH_STATE["channels"].keys()),
        "templates": ["territoire", "premium", "viral"],
        "tracking": "ACTIVE",
        "admin_premium_ready": True,
        "admin_sync_modules": list(MASTER_SWITCH_STATE["admin_sync"].keys()),
    }
