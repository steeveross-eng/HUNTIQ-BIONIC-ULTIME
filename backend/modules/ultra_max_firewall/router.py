"""
ULTRA-MAX++ FIREWALL — BCE-4X Phase C | Geo-fencing Urbain
============================================================
Pare-feu geographique empechant l'utilisation des fonctionnalites
BIONIC dans les zones urbaines non conformes.

Endpoints:
  POST /api/firewall/check       — Verifie si coordonnees sont en zone autorisee
  GET  /api/firewall/zones       — Liste des zones configurees
  POST /api/firewall/zones       — Ajoute une zone (Admin STEEVE-MAX)
  GET  /api/firewall/status      — Statut du module
  GET  /api/firewall/logs        — Journal des verifications

Technologie: Shapely (point-dans-polygone)
Conformite: GOLDEN + BCE-4X | STEEVE-MAX
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from shapely.geometry import Point, Polygon, shape
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("ultra_max_firewall")
router = APIRouter(prefix="/api/firewall", tags=["ULTRA-MAX++ FIREWALL"])

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "huntiq_v6")


# ══════════════════════════════════════
# MODELS
# ══════════════════════════════════════

class FirewallCheckRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class ZoneCreateRequest(BaseModel):
    name: str
    zone_type: str = "urban"
    coordinates: list  # [[lng, lat], ...]
    authority_key: str = ""

class FirewallCheckResponse(BaseModel):
    allowed: bool
    zone_name: Optional[str] = None
    zone_type: Optional[str] = None
    distance_to_boundary_m: Optional[float] = None
    message: str


# ══════════════════════════════════════
# ZONES URBAINES QUEBEC (BUILT-IN)
# ══════════════════════════════════════

BUILTIN_URBAN_ZONES = [
    {
        "name": "Montreal-Metro",
        "zone_type": "urban",
        "polygon": Polygon([
            (-73.98, 45.40), (-73.48, 45.40), (-73.48, 45.62),
            (-73.98, 45.62), (-73.98, 45.40)
        ])
    },
    {
        "name": "Quebec-Ville",
        "zone_type": "urban",
        "polygon": Polygon([
            (-71.40, 46.75), (-71.15, 46.75), (-71.15, 46.90),
            (-71.40, 46.90), (-71.40, 46.75)
        ])
    },
    {
        "name": "Laval",
        "zone_type": "urban",
        "polygon": Polygon([
            (-73.90, 45.52), (-73.60, 45.52), (-73.60, 45.65),
            (-73.90, 45.65), (-73.90, 45.52)
        ])
    },
    {
        "name": "Gatineau",
        "zone_type": "urban",
        "polygon": Polygon([
            (-75.85, 45.40), (-75.60, 45.40), (-75.60, 45.52),
            (-75.85, 45.52), (-75.85, 45.40)
        ])
    },
    {
        "name": "Sherbrooke",
        "zone_type": "urban",
        "polygon": Polygon([
            (-71.98, 45.35), (-71.82, 45.35), (-71.82, 45.45),
            (-71.98, 45.45), (-71.98, 45.35)
        ])
    },
    {
        "name": "Trois-Rivieres",
        "zone_type": "urban",
        "polygon": Polygon([
            (-72.62, 46.32), (-72.48, 46.32), (-72.48, 46.40),
            (-72.62, 46.40), (-72.62, 46.32)
        ])
    },
    {
        "name": "Saguenay",
        "zone_type": "urban",
        "polygon": Polygon([
            (-71.15, 48.38), (-70.95, 48.38), (-70.95, 48.48),
            (-71.15, 48.48), (-71.15, 48.38)
        ])
    },
]


def _get_db():
    client = AsyncIOMotorClient(MONGO_URL)
    return client[DB_NAME]


def _check_builtin_zones(lat: float, lng: float):
    """Verifie si le point est dans une zone urbaine integree."""
    point = Point(lng, lat)
    for zone in BUILTIN_URBAN_ZONES:
        poly = zone["polygon"]
        if poly.contains(point):
            dist = poly.exterior.distance(point) * 111_000
            return {
                "in_zone": True,
                "name": zone["name"],
                "zone_type": zone["zone_type"],
                "distance_m": round(dist, 1),
            }
    nearest_dist = min(
        zone["polygon"].exterior.distance(Point(lng, lat)) * 111_000
        for zone in BUILTIN_URBAN_ZONES
    )
    return {"in_zone": False, "distance_m": round(nearest_dist, 1)}


# ══════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════

@router.get("/status")
async def firewall_status():
    return {
        "status": "operational",
        "engine": "ULTRA-MAX++ Firewall",
        "version": "1.0.0",
        "builtin_zones": len(BUILTIN_URBAN_ZONES),
        "technology": "Shapely (point-in-polygon)",
        "protocol": "BCE-4X GOLDEN V6+",
        "authority": "STEEVE-MAX",
    }


@router.post("/check", response_model=FirewallCheckResponse)
async def check_coordinates(request: FirewallCheckRequest):
    """Verifie si les coordonnees sont en zone autorisee."""
    result = _check_builtin_zones(request.lat, request.lng)

    # Check custom zones from DB
    try:
        db = _get_db()
        custom_zones = await db.firewall_zones.find().to_list(100)
        point = Point(request.lng, request.lat)
        for zone_doc in custom_zones:
            coords = zone_doc.get("coordinates", [])
            if len(coords) >= 3:
                poly = Polygon(coords)
                if poly.contains(point):
                    result = {
                        "in_zone": True,
                        "name": zone_doc.get("name", "Custom Zone"),
                        "zone_type": zone_doc.get("zone_type", "custom"),
                        "distance_m": 0,
                    }
                    break
    except Exception as e:
        logger.warning(f"Custom zones check failed: {e}")

    # Log the check
    try:
        db = _get_db()
        await db.firewall_logs.insert_one({
            "lat": request.lat,
            "lng": request.lng,
            "allowed": not result["in_zone"],
            "zone_name": result.get("name"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        logger.warning(f"Firewall log failed: {e}")

    if result["in_zone"]:
        return FirewallCheckResponse(
            allowed=False,
            zone_name=result["name"],
            zone_type=result.get("zone_type", "urban"),
            distance_to_boundary_m=result["distance_m"],
            message=f"Zone urbaine detectee: {result['name']}. Fonctions BIONIC limitees.",
        )

    return FirewallCheckResponse(
        allowed=True,
        distance_to_boundary_m=result["distance_m"],
        message="Zone autorisee. Fonctions BIONIC completes.",
    )


@router.get("/zones")
async def list_zones():
    """Liste toutes les zones configurees (built-in + custom)."""
    builtin = [
        {"name": z["name"], "zone_type": z["zone_type"], "source": "builtin"}
        for z in BUILTIN_URBAN_ZONES
    ]
    custom = []
    try:
        db = _get_db()
        docs = await db.firewall_zones.find({}, {"_id": 0}).to_list(100)
        custom = [{"source": "custom", **d} for d in docs]
    except Exception:
        pass
    return {"zones": builtin + custom, "total": len(builtin) + len(custom)}


@router.post("/zones")
async def add_zone(request: ZoneCreateRequest):
    """Ajoute une zone personnalisee (STEEVE-MAX uniquement)."""
    if request.authority_key != "STEEVE-MAX":
        raise HTTPException(status_code=403, detail="Autorite STEEVE-MAX requise.")
    if len(request.coordinates) < 3:
        raise HTTPException(status_code=400, detail="Minimum 3 coordonnees pour un polygone.")

    try:
        db = _get_db()
        doc = {
            "name": request.name,
            "zone_type": request.zone_type,
            "coordinates": request.coordinates,
            "created_by": "STEEVE-MAX",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.firewall_zones.insert_one(doc)
        return {"status": "created", "zone_name": request.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_logs(limit: int = 50):
    """Journal des verifications du firewall."""
    try:
        db = _get_db()
        logs = await db.firewall_logs.find(
            {}, {"_id": 0}
        ).sort("timestamp", -1).limit(limit).to_list(limit)
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        return {"logs": [], "count": 0, "error": str(e)}
