"""
BSAA — BIONIC Social Ads Automation
=============================================
x4500-ULTRA: Implementation du module BSAA.
Campagnes publicitaires multi-plateformes, generation de contenus,
templates, analytics, et planification.

Endpoints:
  POST   /api/bsaa/campaigns         — Creer une campagne
  GET    /api/bsaa/campaigns         — Lister les campagnes
  GET    /api/bsaa/campaigns/{id}    — Detail d'une campagne
  PUT    /api/bsaa/campaigns/{id}    — Mettre a jour une campagne
  DELETE /api/bsaa/campaigns/{id}    — Supprimer une campagne
  POST   /api/bsaa/content/generate  — Generer du contenu publicitaire
  GET    /api/bsaa/templates         — Lister les templates disponibles
  GET    /api/bsaa/analytics/summary — Resume analytique global
  GET    /api/bsaa/platforms         — Plateformes disponibles

BCE-4X / STEEVE-MAX / x4500-ULTRA
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import os
import uuid

router = APIRouter(prefix="/api/bsaa", tags=["BSAA"])

# --- MongoDB ---
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "huntiq_v6")
_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# --- Pydantic Models ---
class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    type: str = Field(default="awareness", pattern="^(awareness|traffic|conversion|engagement)$")
    platforms: list = Field(default=["facebook"])
    budget_total: float = 0
    budget_daily: float = 0
    currency: str = "CAD"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    languages: list = Field(default=["fr"])
    targeting: dict = Field(default_factory=dict)
    content_type: str = "auto"
    template_id: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    platforms: Optional[list] = None
    budget_total: Optional[float] = None
    budget_daily: Optional[float] = None
    targeting: Optional[dict] = None


class ContentGenerateRequest(BaseModel):
    campaign_id: Optional[str] = None
    platform: str = "facebook"
    language: str = "fr"
    type: str = "awareness"
    species: str = "CERF"
    region: str = "Quebec"
    tone: str = "professional"


# --- Templates de contenu ---
CONTENT_TEMPLATES = {
    "awareness": {
        "fr": {
            "titles": [
                "Decouvrez la chasse intelligente avec BIONIC",
                "Votre territoire, analyse par la science",
                "BIONIC Hunt — La precision au service de la chasse",
                "22 moteurs scientifiques pour votre prochaine sortie",
            ],
            "bodies": [
                "BIONIC Hunt combine {engine_count} moteurs d'analyse pour identifier les meilleurs hotspots de {species} dans votre region. Score consolide, hydrographie, NDVI, comportement animal — tout est calcule pour maximiser vos chances.",
                "Fini les sorties a l'aveugle. BIONIC analyse votre territoire avec {engine_count} couches de donnees scientifiques et vous guide vers les zones les plus productives pour le {species}.",
                "L'intelligence artificielle rencontre l'expertise terrain. BIONIC evalue chaque hectare de votre territoire selon {engine_count} criteres — alimentation, repos, corridors, pression de chasse et bien plus.",
            ],
            "cta": [
                "Analyser mon territoire",
                "Essayer BIONIC gratuitement",
                "Voir la demo",
                "Commencer maintenant",
            ],
        },
        "en": {
            "titles": [
                "Discover smart hunting with BIONIC",
                "Your territory, analyzed by science",
                "BIONIC Hunt — Precision-driven hunting",
                "22 scientific engines for your next outing",
            ],
            "bodies": [
                "BIONIC Hunt combines {engine_count} analysis engines to identify the best {species} hotspots in your area. Consolidated score, hydrography, NDVI, animal behavior — everything calculated to maximize your success.",
                "No more blind outings. BIONIC analyzes your territory with {engine_count} layers of scientific data and guides you to the most productive zones for {species}.",
                "Artificial intelligence meets field expertise. BIONIC evaluates every hectare of your territory across {engine_count} criteria — feeding, resting, corridors, hunting pressure and more.",
            ],
            "cta": [
                "Analyze my territory",
                "Try BIONIC for free",
                "See the demo",
                "Get started now",
            ],
        },
    },
    "traffic": {
        "fr": {
            "titles": [
                "Carte interactive — Explorez votre zone de chasse",
                "Score consolide en temps reel pour votre territoire",
                "Planifiez votre sortie avec BIONIC Maps",
            ],
            "bodies": [
                "Accedez a la carte interactive BIONIC et visualisez en temps reel les zones optimales pour le {species}. Heatmaps, corridors fauniques, et analyses multi-moteurs — tout sur une seule carte.",
                "BIONIC Maps integre {engine_count} couches d'analyse sur une carte interactive. Identifiez les affuts, salines et corridors de deplacement en quelques clics.",
            ],
            "cta": ["Ouvrir la carte", "Explorer mon territoire", "Voir les hotspots"],
        },
        "en": {
            "titles": [
                "Interactive map — Explore your hunting zone",
                "Real-time consolidated score for your territory",
                "Plan your outing with BIONIC Maps",
            ],
            "bodies": [
                "Access the BIONIC interactive map and visualize in real-time the optimal zones for {species}. Heatmaps, wildlife corridors, and multi-engine analysis — all on one map.",
                "BIONIC Maps integrates {engine_count} analysis layers on an interactive map. Identify blinds, salt licks and movement corridors in a few clicks.",
            ],
            "cta": ["Open the map", "Explore my territory", "See hotspots"],
        },
    },
    "conversion": {
        "fr": {
            "titles": [
                "BIONIC Premium — L'avantage scientifique",
                "Passez a BIONIC Premium et chassez mieux",
                "Score consolide x4100 — Precision ultime",
            ],
            "bodies": [
                "Avec BIONIC Premium, accedez a {engine_count} moteurs d'analyse, des previsions meteo integrees, et un score consolide calibre scientifiquement. Votre prochain trophee commence ici.",
                "Les chasseurs BIONIC Premium identifient 3x plus de hotspots productifs. {engine_count} moteurs, previsions sur 7 jours, alertes personnalisees — tout inclus.",
            ],
            "cta": ["Devenir Premium", "Commencer l'essai gratuit", "Voir les plans"],
        },
        "en": {
            "titles": [
                "BIONIC Premium — The scientific advantage",
                "Upgrade to BIONIC Premium and hunt better",
                "Consolidated score x4100 — Ultimate precision",
            ],
            "bodies": [
                "With BIONIC Premium, access {engine_count} analysis engines, integrated weather forecasts, and a scientifically calibrated consolidated score. Your next trophy starts here.",
                "BIONIC Premium hunters identify 3x more productive hotspots. {engine_count} engines, 7-day forecasts, personalized alerts — all included.",
            ],
            "cta": ["Go Premium", "Start free trial", "See plans"],
        },
    },
    "engagement": {
        "fr": {
            "titles": [
                "Partagez vos scores BIONIC avec la communaute",
                "Defi BIONIC — Qui a le meilleur territoire ?",
                "Rejoignez 10 000+ chasseurs intelligents",
            ],
            "bodies": [
                "Comparez votre territoire avec d'autres chasseurs BIONIC. Partagez vos scores, decouvrez les meilleures zones et echangez des strategies basees sur la science.",
                "La communaute BIONIC analyse collectivement des milliers de territoires avec {engine_count} moteurs scientifiques. Rejoignez le mouvement.",
            ],
            "cta": ["Rejoindre la communaute", "Partager mon score", "Voir le classement"],
        },
        "en": {
            "titles": [
                "Share your BIONIC scores with the community",
                "BIONIC Challenge — Who has the best territory?",
                "Join 10,000+ smart hunters",
            ],
            "bodies": [
                "Compare your territory with other BIONIC hunters. Share scores, discover top zones and exchange science-based strategies.",
                "The BIONIC community collectively analyzes thousands of territories with {engine_count} scientific engines. Join the movement.",
            ],
            "cta": ["Join the community", "Share my score", "See rankings"],
        },
    },
}

PLATFORMS_CONFIG = {
    "facebook": {
        "name": "Facebook",
        "icon": "facebook",
        "formats": ["image", "carousel", "video"],
        "max_title_length": 40,
        "max_body_length": 125,
        "image_sizes": ["1200x628", "1080x1080"],
        "status": "available",
    },
    "instagram": {
        "name": "Instagram",
        "icon": "instagram",
        "formats": ["image", "carousel", "reels", "story"],
        "max_title_length": 0,
        "max_body_length": 2200,
        "image_sizes": ["1080x1080", "1080x1350", "1080x1920"],
        "status": "available",
    },
    "tiktok": {
        "name": "TikTok",
        "icon": "tiktok",
        "formats": ["video", "spark_ads"],
        "max_title_length": 100,
        "max_body_length": 100,
        "image_sizes": ["1080x1920"],
        "status": "coming_soon",
    },
    "youtube": {
        "name": "YouTube",
        "icon": "youtube",
        "formats": ["video", "shorts", "display"],
        "max_title_length": 100,
        "max_body_length": 5000,
        "image_sizes": ["1280x720"],
        "status": "coming_soon",
    },
    "reddit": {
        "name": "Reddit",
        "icon": "message-circle",
        "formats": ["text", "image", "video"],
        "max_title_length": 300,
        "max_body_length": 40000,
        "image_sizes": ["1200x628"],
        "status": "coming_soon",
    },
}

SPECIES_MAP = {
    "CERF": {"fr": "cerf de Virginie", "en": "whitetail deer"},
    "ORIGNAL": {"fr": "orignal", "en": "moose"},
    "OURS": {"fr": "ours noir", "en": "black bear"},
    "DINDON": {"fr": "dindon sauvage", "en": "wild turkey"},
    "WAPITI": {"fr": "wapiti", "en": "elk"},
}


# --- Helper ---
def _gen_id():
    return str(uuid.uuid4())[:12]


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _generate_content(req: ContentGenerateRequest):
    """Genere du contenu publicitaire a partir des templates."""
    import random

    campaign_type = req.type if req.type in CONTENT_TEMPLATES else "awareness"
    lang = req.language if req.language in ("fr", "en") else "fr"
    templates = CONTENT_TEMPLATES[campaign_type][lang]

    species_name = SPECIES_MAP.get(req.species.upper(), {}).get(lang, req.species)

    title = random.choice(templates["titles"])
    body = random.choice(templates["bodies"]).format(
        engine_count=22, species=species_name
    )
    cta = random.choice(templates["cta"])

    platform_cfg = PLATFORMS_CONFIG.get(req.platform, PLATFORMS_CONFIG["facebook"])

    if platform_cfg["max_title_length"] > 0:
        title = title[: platform_cfg["max_title_length"]]
    if platform_cfg["max_body_length"] > 0:
        body = body[: platform_cfg["max_body_length"]]

    return {
        "content_id": _gen_id(),
        "platform": req.platform,
        "language": lang,
        "type": campaign_type,
        "species": req.species.upper(),
        "region": req.region,
        "title": title,
        "body": body,
        "cta": cta,
        "hashtags": _generate_hashtags(campaign_type, lang, req.species),
        "recommended_format": platform_cfg["formats"][0],
        "image_size": platform_cfg["image_sizes"][0],
        "generated_at": _now_iso(),
    }


def _generate_hashtags(campaign_type, lang, species):
    base_tags = ["#BIONICHunt", "#ChasseFuturiste", "#ScoreConsolide"]
    species_tags = {
        "CERF": ["#ChasseCerf", "#WhitetailHunting"],
        "ORIGNAL": ["#ChasseOrignal", "#MooseHunting"],
        "OURS": ["#ChasseOurs", "#BearHunting"],
        "DINDON": ["#ChasseDindon", "#TurkeyHunting"],
    }
    type_tags = {
        "awareness": ["#DecouvrirBIONIC", "#ChasseTech"],
        "traffic": ["#CarteBIONIC", "#HotspotChasse"],
        "conversion": ["#BIONICPremium", "#ChasseScientifique"],
        "engagement": ["#CommunauteBIONIC", "#ChasseursIntelligents"],
    }
    return base_tags + species_tags.get(species.upper(), []) + type_tags.get(campaign_type, [])


# --- Routes ---
@router.post("/campaigns")
async def create_campaign(data: CampaignCreate):
    db = _get_db()
    campaign = {
        "campaign_id": _gen_id(),
        "name": data.name,
        "description": data.description,
        "type": data.type,
        "platforms": data.platforms,
        "status": "draft",
        "budget": {"total": data.budget_total, "daily": data.budget_daily, "currency": data.currency},
        "schedule": {"start_date": data.start_date, "end_date": data.end_date},
        "languages": data.languages,
        "targeting": data.targeting,
        "content_type": data.content_type,
        "template_id": data.template_id,
        "analytics": {"impressions": 0, "clicks": 0, "conversions": 0, "ctr": 0.0, "spend": 0.0},
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    db.bsaa_campaigns.insert_one(campaign)
    campaign.pop("_id", None)
    return {"status": "created", "campaign": campaign}


@router.get("/campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    db = _get_db()
    query = {}
    if status:
        query["status"] = status
    if platform:
        query["platforms"] = platform

    total = db.bsaa_campaigns.count_documents(query)
    campaigns = list(
        db.bsaa_campaigns.find(query, {"_id": 0})
        .sort("created_at", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    return {"campaigns": campaigns, "total": total, "page": page, "limit": limit}


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    db = _get_db()
    campaign = db.bsaa_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campagne non trouvee")
    return campaign


@router.put("/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, data: CampaignUpdate):
    db = _get_db()
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Aucune modification fournie")
    updates["updated_at"] = _now_iso()
    result = db.bsaa_campaigns.update_one({"campaign_id": campaign_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Campagne non trouvee")
    campaign = db.bsaa_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    return {"status": "updated", "campaign": campaign}


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str):
    db = _get_db()
    result = db.bsaa_campaigns.delete_one({"campaign_id": campaign_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Campagne non trouvee")
    return {"status": "deleted", "campaign_id": campaign_id}


@router.post("/content/generate")
async def generate_content(req: ContentGenerateRequest):
    content = _generate_content(req)
    return {"status": "generated", "content": content}


@router.get("/templates")
async def list_templates():
    templates = []
    for campaign_type, langs in CONTENT_TEMPLATES.items():
        for lang, data in langs.items():
            templates.append({
                "type": campaign_type,
                "language": lang,
                "title_count": len(data["titles"]),
                "body_count": len(data["bodies"]),
                "cta_count": len(data["cta"]),
                "sample_title": data["titles"][0],
            })
    return {"templates": templates, "total": len(templates)}


@router.get("/analytics/summary")
async def analytics_summary():
    db = _get_db()
    pipeline = [
        {"$group": {
            "_id": None,
            "total_campaigns": {"$sum": 1},
            "total_impressions": {"$sum": "$analytics.impressions"},
            "total_clicks": {"$sum": "$analytics.clicks"},
            "total_conversions": {"$sum": "$analytics.conversions"},
            "total_spend": {"$sum": "$analytics.spend"},
        }}
    ]
    result = list(db.bsaa_campaigns.aggregate(pipeline))
    if result:
        summary = result[0]
        summary.pop("_id", None)
        if summary["total_impressions"] > 0:
            summary["avg_ctr"] = round(summary["total_clicks"] / summary["total_impressions"] * 100, 2)
        else:
            summary["avg_ctr"] = 0
    else:
        summary = {
            "total_campaigns": 0,
            "total_impressions": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "total_spend": 0,
            "avg_ctr": 0,
        }

    by_status = list(db.bsaa_campaigns.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    summary["by_status"] = {s["_id"]: s["count"] for s in by_status}

    by_platform = list(db.bsaa_campaigns.aggregate([
        {"$unwind": "$platforms"},
        {"$group": {"_id": "$platforms", "count": {"$sum": 1}}}
    ]))
    summary["by_platform"] = {p["_id"]: p["count"] for p in by_platform}

    return summary


@router.get("/platforms")
async def list_platforms():
    return {"platforms": PLATFORMS_CONFIG}
