"""
SHARE ENGINE — BCE-4X GOLDEN V6+ Module PARTAGER + MARKETING ENGINE
====================================================================
Master Switch Premium: point de contrôle UNIQUE de tout partage externe.
Marketing Engine: capture automatique leads, création contacts, événements marketing.
Tracking Premium: clics, partages, conversions, engagement, scoring.
Intégration ADMIN PREMIUM: attribution, campagnes, optimisation.

Endpoints:
  POST /api/share/track            — Enregistre un événement de partage + auto-capture lead
  POST /api/share/capture-lead     — Capture manuelle d'un lead marketing
  GET  /api/share/contacts         — Liste tous les contacts marketing créés
  GET  /api/share/marketing-stats  — Statistiques marketing enrichies
  GET  /api/share/stats            — Statistiques de partage (Admin Premium)
  GET  /api/share/status           — Status du module + Master Switch + Marketing Engine
  GET  /api/share/master-switch    — État du Master Switch
  PUT  /api/share/master-switch    — Modifier l'état du Master Switch (STEEVE-MAX only)
"""
import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
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
    "global_enabled": True,         # ON par defaut — STANDARD GOLDEN
    "override_mode": False,
    "authority": "STEEVE-MAX",
    "channels": {
        "native":    {"enabled": True, "label": "Partage OS",  "priority": 1},
        "gmail":     {"enabled": True, "label": "Gmail",       "priority": 2},
        "outlook":   {"enabled": True, "label": "Outlook",     "priority": 3},
        "yahoo":     {"enabled": True, "label": "Yahoo Mail",  "priority": 4},
        "facebook":  {"enabled": True, "label": "Facebook",    "priority": 5},
        "messenger": {"enabled": True, "label": "Messenger",   "priority": 6},
        "whatsapp":  {"enabled": True, "label": "WhatsApp",    "priority": 7},
        "x":         {"enabled": True, "label": "X (Twitter)", "priority": 8},
        "linkedin":  {"enabled": True, "label": "LinkedIn",    "priority": 9},
        "instagram": {"enabled": True, "label": "Instagram",   "priority": 10},
        "tiktok":    {"enabled": True, "label": "TikTok",      "priority": 11},
        "sms":       {"enabled": True, "label": "SMS",         "priority": 12},
        "copy":      {"enabled": True, "label": "Copier lien", "priority": 13},
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
    user_email: Optional[str] = None
    user_id: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    page_context: Optional[str] = None
    species: Optional[str] = None
    sal_id: Optional[str] = None


class MarketingLeadCapture(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    source_channel: str
    source_page: Optional[str] = None
    species: Optional[str] = None
    sal_id: Optional[str] = None
    campaign: Optional[str] = "organic"
    metadata: Optional[Dict] = None


class MasterSwitchUpdate(BaseModel):
    global_enabled: Optional[bool] = None
    channel_updates: Optional[Dict[str, bool]] = None
    authority_key: str = ""


async def _auto_create_contact(db, email: str, name: str = None, source: str = "share", channel: str = None, metadata: dict = None):
    """Auto-création d'un contact marketing — BCE-4X Marketing Engine."""
    if not email:
        return None
    existing = await db.marketing_contacts.find_one({"email": email}, {"_id": 0})
    now = datetime.now(timezone.utc).isoformat()
    if existing:
        update_data = {
            "$inc": {"interaction_count": 1},
            "$set": {"last_interaction": now, "last_channel": channel or source},
            "$addToSet": {"channels_used": channel} if channel else {},
        }
        await db.marketing_contacts.update_one({"email": email}, update_data)
        logger.info(f"[MARKETING-ENGINE] Contact updated: {email}, interactions+1")
        return "updated"
    else:
        contact = {
            "email": email,
            "name": name or email.split("@")[0],
            "phone": None,
            "source": source,
            "first_channel": channel,
            "channels_used": [channel] if channel else [],
            "interaction_count": 1,
            "status": "lead",
            "score": 10,
            "created_at": now,
            "last_interaction": now,
            "last_channel": channel or source,
            "tags": ["auto-captured", f"via-{source}"],
            "metadata": metadata or {},
            "admin_synced": False,
            "protocol": "BCE-4X GOLDEN V6+",
        }
        await db.marketing_contacts.insert_one(contact)
        logger.info(f"[MARKETING-ENGINE] Contact CREATED: {email}, source={source}, channel={channel}")
        return "created"


async def _log_marketing_event(db, event_type: str, channel: str, data: dict):
    """Log événement marketing enrichi — BCE-4X Marketing Engine."""
    event = {
        "event_type": event_type,
        "channel": channel,
        "data": data,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "BCE-4X",
        "engine": "marketing_engine_v2",
    }
    await db.marketing_events.insert_one(event)
    logger.info(f"[MARKETING-ENGINE] Event logged: type={event_type}, channel={channel}")


@router.post("/track")
async def track_share(event: ShareTrackEvent):
    """Enregistre un événement de partage via le Master Switch Pipeline + Marketing Engine."""
    if not MASTER_SWITCH_STATE["global_enabled"]:
        return {"status": "blocked", "reason": "master_switch_off"}

    channel_config = MASTER_SWITCH_STATE["channels"].get(event.channel)
    if not channel_config or not channel_config["enabled"]:
        return {"status": "blocked", "reason": f"channel_{event.channel}_disabled"}

    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "channel": event.channel,
        "template": event.template,
        "url": event.url,
        "has_weather": event.hasWeather,
        "master_switch": "ON",
        "channel_priority": channel_config["priority"],
        "created_at": now,
        "client_timestamp": event.timestamp,
        "user_email": event.user_email,
        "user_id": event.user_id,
        "recipient_email": event.recipient_email,
        "recipient_name": event.recipient_name,
        "page_context": event.page_context,
        "species": event.species,
        "sal_id": event.sal_id,
    }
    await db.share_events.insert_one(doc)

    contact_status = None
    if event.user_email:
        contact_status = await _auto_create_contact(
            db, event.user_email, source="share_track", channel=event.channel,
            metadata={"template": event.template, "page": event.page_context, "species": event.species}
        )
    if event.recipient_email:
        await _auto_create_contact(
            db, event.recipient_email, name=event.recipient_name,
            source="share_recipient", channel=event.channel,
            metadata={"shared_by": event.user_email, "template": event.template}
        )

    await _log_marketing_event(db, "share_executed", event.channel, {
        "template": event.template, "url": event.url,
        "user_email": event.user_email, "recipient": event.recipient_email,
        "species": event.species, "sal_id": event.sal_id,
        "page": event.page_context,
    })

    logger.info(
        f"[MASTER-SWITCH] Share tracked: channel={event.channel}, "
        f"template={event.template}, priority={channel_config['priority']}, "
        f"contact={contact_status}"
    )

    return {
        "status": "tracked",
        "channel": event.channel,
        "master_switch": "ON",
        "priority": channel_config["priority"],
        "contact_status": contact_status,
    }


@router.post("/capture-lead")
async def capture_lead(lead: MarketingLeadCapture):
    """Capture manuelle d'un lead marketing — BCE-4X Marketing Engine."""
    db = get_db()

    contact_status = None
    if lead.email:
        contact_status = await _auto_create_contact(
            db, lead.email, name=lead.name, source=f"lead_{lead.campaign}",
            channel=lead.source_channel,
            metadata={
                "phone": lead.phone, "species": lead.species,
                "sal_id": lead.sal_id, "page": lead.source_page,
                **(lead.metadata or {}),
            }
        )

    if lead.phone and not lead.email:
        contact = {
            "email": None,
            "phone": lead.phone,
            "name": lead.name or "Inconnu",
            "source": f"lead_{lead.campaign}",
            "first_channel": lead.source_channel,
            "channels_used": [lead.source_channel],
            "interaction_count": 1,
            "status": "lead",
            "score": 5,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_interaction": datetime.now(timezone.utc).isoformat(),
            "last_channel": lead.source_channel,
            "tags": ["phone-only", f"campaign-{lead.campaign}"],
            "metadata": lead.metadata or {},
            "admin_synced": False,
            "protocol": "BCE-4X GOLDEN V6+",
        }
        await db.marketing_contacts.insert_one(contact)
        contact_status = "created"

    await _log_marketing_event(db, "lead_captured", lead.source_channel, {
        "email": lead.email, "name": lead.name, "phone": lead.phone,
        "campaign": lead.campaign, "species": lead.species, "sal_id": lead.sal_id,
    })

    logger.info(f"[MARKETING-ENGINE] Lead captured: email={lead.email}, phone={lead.phone}, campaign={lead.campaign}")

    return {
        "status": "captured",
        "contact_status": contact_status,
        "campaign": lead.campaign,
        "protocol": "BCE-4X",
    }


@router.get("/contacts")
async def list_contacts(limit: int = 50, skip: int = 0, status: Optional[str] = None):
    """Liste tous les contacts marketing — Admin Premium."""
    db = get_db()
    query = {}
    if status:
        query["status"] = status

    contacts = []
    cursor = db.marketing_contacts.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    async for doc in cursor:
        contacts.append(doc)

    total = await db.marketing_contacts.count_documents(query)

    return {
        "contacts": contacts,
        "total": total,
        "limit": limit,
        "skip": skip,
        "protocol": "BCE-4X",
    }


@router.get("/marketing-stats")
async def marketing_stats():
    """Statistiques marketing enrichies — BCE-4X Marketing Engine."""
    db = get_db()

    total_contacts = await db.marketing_contacts.count_documents({})
    total_leads = await db.marketing_contacts.count_documents({"status": "lead"})
    total_events = await db.marketing_events.count_documents({})
    total_shares = await db.share_events.count_documents({})

    pipeline_channels = [{"$group": {"_id": "$channel", "count": {"$sum": 1}}}]
    shares_by_channel = {}
    async for doc in db.share_events.aggregate(pipeline_channels):
        shares_by_channel[doc["_id"]] = doc["count"]

    pipeline_sources = [{"$group": {"_id": "$source", "count": {"$sum": 1}}}]
    contacts_by_source = {}
    async for doc in db.marketing_contacts.aggregate(pipeline_sources):
        contacts_by_source[doc["_id"]] = doc["count"]

    pipeline_events = [{"$group": {"_id": "$event_type", "count": {"$sum": 1}}}]
    events_by_type = {}
    async for doc in db.marketing_events.aggregate(pipeline_events):
        events_by_type[doc["_id"]] = doc["count"]

    recent_contacts = []
    cursor = db.marketing_contacts.find({}, {"_id": 0}).sort("created_at", -1).limit(5)
    async for doc in cursor:
        recent_contacts.append({"email": doc.get("email"), "name": doc.get("name"), "source": doc.get("source"), "created_at": doc.get("created_at")})

    return {
        "total_contacts": total_contacts,
        "total_leads": total_leads,
        "total_events": total_events,
        "total_shares": total_shares,
        "shares_by_channel": shares_by_channel,
        "contacts_by_source": contacts_by_source,
        "events_by_type": events_by_type,
        "recent_contacts": recent_contacts,
        "conversion_rate": round((total_contacts / max(total_shares, 1)) * 100, 1),
        "master_switch": "ON" if MASTER_SWITCH_STATE["global_enabled"] else "OFF",
        "protocol": "BCE-4X GOLDEN V6+",
    }


@router.get("/stats")
async def share_stats():
    """Statistiques de partage — Admin Premium via Master Switch + Marketing Engine."""
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

    total_contacts = await db.marketing_contacts.count_documents({})
    total_marketing_events = await db.marketing_events.count_documents({})

    return {
        "total_shares": total,
        "by_channel": by_channel,
        "by_template": by_template,
        "last_24h": last_24h,
        "master_switch": "ON" if MASTER_SWITCH_STATE["global_enabled"] else "OFF",
        "marketing_engine": {
            "total_contacts": total_contacts,
            "total_events": total_marketing_events,
            "auto_capture": True,
        },
        "protocol": "BCE-4X GOLDEN V6+",
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
    """Status du module SHARE BIONIC + Master Switch + Marketing Engine."""
    return {
        "module": "share_engine",
        "version": "3.0.0",
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
        "marketing_engine": {
            "status": "OPERATIONAL",
            "version": "2.0.0",
            "auto_capture": True,
            "auto_contact_creation": True,
            "lead_scoring": True,
            "admin_sync": True,
        },
        "channels": list(MASTER_SWITCH_STATE["channels"].keys()),
        "templates": ["territoire", "premium", "viral"],
        "tracking": "ACTIVE",
        "admin_premium_ready": True,
        "admin_sync_modules": list(MASTER_SWITCH_STATE["admin_sync"].keys()),
    }
