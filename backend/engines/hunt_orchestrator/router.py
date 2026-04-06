"""
BCE-4X P0 — HUNT ORCHESTRATOR API
===================================
Endpoints FastAPI pour l'orchestration de chasse.

Endpoints:
- POST /api/v1/hunt/orchestrate  — Recommandation complete
- POST /api/v1/hunt/scent-zone   — Zone de contamination pour un point
- POST /api/v1/hunt/access-route  — Route d'acces vers un affut

STEEVE-MAX 2026-03-28 — Standard institutionnel.
"""

import logging
import time
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.hunt_orchestrator.router")

router = APIRouter(prefix="/api/v1/hunt", tags=["Hunt Orchestrator"])


# === Modeles Pydantic ===

class FeedingSite(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None
    type: Optional[str] = "alimentation"


class FixedBlind(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = "Affut fixe"
    type_key: Optional[str] = "tree_stand"
    id: Optional[str] = None


class OrchestrationRequest(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre du territoire")
    center_lng: float = Field(..., description="Longitude du centre du territoire")
    wind_direction_deg: float = Field(..., ge=0, lt=360, description="Direction du vent (degres)")
    wind_speed_kmh: float = Field(..., ge=0, description="Vitesse du vent (km/h)")
    session: str = Field("matin", description="matin ou soir")
    species: str = Field("orignal", description="Espece ciblee")
    radius_m: int = Field(600, ge=200, le=2000, description="Rayon du territoire")
    max_blinds: int = Field(5, ge=1, le=10, description="Nombre max de recommandations")
    feeding_sites: List[FeedingSite] = Field(default_factory=list)
    fixed_blinds: List[FixedBlind] = Field(default_factory=list)


class ScentZoneRequest(BaseModel):
    lat: float
    lng: float
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wind_speed_kmh: float = Field(..., ge=0)
    session: str = Field("matin")


class AccessRouteRequest(BaseModel):
    entry_lat: float
    entry_lng: float
    blind_lat: float
    blind_lng: float
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wind_speed_kmh: float = Field(..., ge=0)
    session: str = Field("matin")
    feeding_sites: List[FeedingSite] = Field(default_factory=list)


class ContaminationZoneRequest(BaseModel):
    """BCE-4X BLOC 2 — BDRE PEDAGOGIQUE: Contamination permanente."""
    center_lat: float
    center_lng: float
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wind_speed_kmh: float = Field(..., ge=0)
    session: str = Field("matin")
    feeding_sites: List[FeedingSite] = Field(default_factory=list)



# === Endpoints ===

@router.post("/orchestrate")
async def orchestrate_hunt(req: OrchestrationRequest):
    """
    Orchestration complete d'une session de chasse.
    Combine vent/odeurs + acces dynamique + choix d'affuts.
    """
    try:
        from engines.hunt_orchestrator.orchestrator import orchestrate_hunt_session

        # Convertir les modeles Pydantic en dicts
        feeding = [{"lat": fs.lat, "lng": fs.lng, "name": fs.name} for fs in req.feeding_sites]
        fixed = [
            {"lat": fb.lat, "lng": fb.lng, "name": fb.name,
             "type_key": fb.type_key, "id": fb.id or f"fixed-{fb.lat:.4f}"}
            for fb in req.fixed_blinds
        ]

        result = orchestrate_hunt_session(
            center_lat=req.center_lat,
            center_lng=req.center_lng,
            wind_direction_deg=req.wind_direction_deg,
            wind_speed_kmh=req.wind_speed_kmh,
            session=req.session,
            species=req.species,
            radius_m=req.radius_m,
            feeding_sites=feeding,
            fixed_blinds=fixed,
            max_blinds=req.max_blinds,
        )

        return result

    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scent-zone")
async def compute_scent(req: ScentZoneRequest):
    """Calculer la zone de contamination olfactive pour un point donne."""
    try:
        from engines.hunt_orchestrator.vent_odeurs import compute_scent_zone
        return compute_scent_zone(
            req.lat, req.lng,
            req.wind_direction_deg, req.wind_speed_kmh,
            req.session,
        )
    except Exception as e:
        logger.error(f"[SCENT-ZONE] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contamination-zones")
async def compute_contamination_zones(req: ContaminationZoneRequest):
    """
    BCE-4X BLOC 2 — BDRE PEDAGOGIQUE.

    Calcule les zones de contamination olfactive PERMANENTES pour:
    - Le chasseur (position centre)
    - Chaque site d'alimentation

    Objectif pedagogique: comprendre les risques AVANT de placer un affut.
    Independant de la presence d'un affut.
    """
    try:
        from engines.hunt_orchestrator.vent_odeurs import compute_scent_zone

        zones = []

        # Zone de contamination du chasseur (position centre)
        hunter_zone = compute_scent_zone(
            req.center_lat, req.center_lng,
            req.wind_direction_deg, req.wind_speed_kmh,
            req.session,
        )
        zones.append({
            "source": "hunter_center",
            "label": "Chasseur (centre)",
            "polygon": hunter_zone["polygon"],
            "bearing_deg": hunter_zone["scent"]["bearing_deg"],
            "range_m": hunter_zone["scent"]["range_m"],
            "risk_level": _classify_risk(hunter_zone["scent"]["range_m"]),
            "style": {"color": "red", "opacity": 0.15},
        })

        # Zones de contamination pour chaque site d'alimentation
        for i, fs in enumerate(req.feeding_sites):
            fs_zone = compute_scent_zone(
                fs.lat, fs.lng,
                req.wind_direction_deg, req.wind_speed_kmh,
                req.session,
            )
            zones.append({
                "source": f"feeding_site_{i + 1}",
                "label": fs.name or f"Saline {i + 1}",
                "polygon": fs_zone["polygon"],
                "bearing_deg": fs_zone["scent"]["bearing_deg"],
                "range_m": fs_zone["scent"]["range_m"],
                "risk_level": _classify_risk(fs_zone["scent"]["range_m"]),
                "style": {"color": "orange", "opacity": 0.10},
            })

        # Message pedagogique
        scent_bearing = hunter_zone["scent"]["bearing_deg"]
        approach_deg = (scent_bearing + 180) % 360
        cardinal = _deg_to_cardinal(approach_deg)

        pedagogy = {
            "message_fr": (
                f"Zone rouge: votre odeur est portee vers {_deg_to_cardinal(scent_bearing)} "
                f"sur {hunter_zone['scent']['range_m']}m. "
                f"Session {req.session}: {hunter_zone['scent']['thermal']['description']}."
            ),
            "conseil": (
                f"Approchez par le {cardinal} pour eviter la contamination. "
                f"Placez votre affut HORS des zones colorees."
            ),
            "risque_global": "HIGH" if len(req.feeding_sites) > 0 and hunter_zone["scent"]["range_m"] > 400 else "MODERATE",
        }

        return {
            "zones": zones,
            "wind": {
                "direction_deg": req.wind_direction_deg,
                "speed_kmh": req.wind_speed_kmh,
            },
            "session": req.session,
            "pedagogy": pedagogy,
            "total_zones": len(zones),
            "version": "BDRE_PEDAGOGIQUE_V1",
            "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX",
        }

    except Exception as e:
        logger.error(f"[CONTAMINATION-ZONES] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _classify_risk(range_m: float) -> str:
    """Classifier le niveau de risque."""
    if range_m >= 500:
        return "HIGH"
    elif range_m >= 300:
        return "MODERATE"
    else:
        return "LOW"


def _deg_to_cardinal(deg: float) -> str:
    """Convertir des degres en direction cardinale."""
    directions = [
        "Nord", "Nord-Nord-Est", "Nord-Est", "Est-Nord-Est",
        "Est", "Est-Sud-Est", "Sud-Est", "Sud-Sud-Est",
        "Sud", "Sud-Sud-Ouest", "Sud-Ouest", "Ouest-Sud-Ouest",
        "Ouest", "Ouest-Nord-Ouest", "Nord-Ouest", "Nord-Nord-Ouest",
    ]
    idx = round(deg / 22.5) % 16
    return directions[idx]



@router.post("/access-route")
async def compute_access(req: AccessRouteRequest):
    """
    Calculer la route d'acces optimale vers un affut.
    
    ORDONNANCE STEEVE-MAX 2026-04-07: MODE OFF — DESACTIVE.
    Archive: /app/LEGACY_ACCESS_AFFUTS/
    """
    return {
        "status": "disabled",
        "mode": "OFF",
        "ordonnance": "STEEVE-MAX 2026-04-07 — DESACTIVATION SECURISEE",
        "message": "Calcul d'acces desactive par ordonnance. Archive disponible dans /LEGACY_ACCESS_AFFUTS/.",
        "distance_m": 0,
        "coords": [],
        "routing_algo": "disabled",
        "trail_type": "disabled",
        "feasible": False,
    }


@router.get("/status")
async def hunt_orchestrator_status():
    """Statut de l'engine d'orchestration de chasse."""
    return {
        "engine": "hunt_orchestrator",
        "version": "1.1.0",
        "status": "active",
        "modules": [
            "vent_odeurs_v1",
            "access_engine_v1",
            "choix_affuts_v1",
            "orchestrator_v1",
            "terrain_cache_persistent_v1",
        ],
        "data_sources": {
            "wind": "Open-Meteo V3 (reel, dynamique)",
            "trails": "OSM/Overpass (reel, cache persistant)",
            "water": "OSM cache (41K polygones)",
            "dominant_wind": "NW hardcode (Quebec, autorise STEEVE-MAX)",
        },
        "governance": "BCE-4X ULTRA-MAX++ — STEEVE-MAX",
    }


@router.get("/terrain-cache/stats")
async def terrain_cache_stats():
    """Statistiques du cache terrain persistant."""
    from engines.terrain_nav.terrain_sources import (
        PERSISTENT_CACHE_DIR, _source_cache, CACHE_VERSION, CACHE_TTL_SECONDS,
    )
    import os

    # Stats cache memoire
    memory_keys = list(_source_cache.keys())

    # Stats cache persistant
    persistent_files = []
    total_size_kb = 0
    if PERSISTENT_CACHE_DIR.exists():
        for f in PERSISTENT_CACHE_DIR.glob("*.json.gz"):
            stat = f.stat()
            age_days = (time.time() - stat.st_mtime) / 86400
            persistent_files.append({
                "filename": f.name,
                "size_kb": round(stat.st_size / 1024, 1),
                "age_days": round(age_days, 1),
            })
            total_size_kb += stat.st_size / 1024

    return {
        "cache_version": CACHE_VERSION,
        "ttl_days": CACHE_TTL_SECONDS / 86400,
        "memory_cache": {
            "entries": len(memory_keys),
            "keys": memory_keys[:10],
        },
        "persistent_cache": {
            "directory": str(PERSISTENT_CACHE_DIR),
            "files_count": len(persistent_files),
            "total_size_kb": round(total_size_kb, 1),
            "files": persistent_files,
        },
    }


class CacheInvalidateRequest(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    invalidate_all: bool = False


@router.post("/terrain-cache/invalidate")
async def terrain_cache_invalidate(req: CacheInvalidateRequest):
    """
    Invalider le cache terrain (memoire + persistant).
    - invalidate_all=true: purge complete
    - lat+lng: invalider une zone specifique
    """
    from engines.terrain_nav.terrain_sources import (
        PERSISTENT_CACHE_DIR, _source_cache, _zone_key, _persistent_cache_path,
    )

    purged_memory = 0
    purged_files = 0

    if req.invalidate_all:
        purged_memory = len(_source_cache)
        _source_cache.clear()
        if PERSISTENT_CACHE_DIR.exists():
            for f in PERSISTENT_CACHE_DIR.glob("*.json.gz"):
                f.unlink(missing_ok=True)
                purged_files += 1
        logger.info(f"[CACHE-INVALIDATE] ALL purged: {purged_memory} memory, {purged_files} files")
    elif req.lat is not None and req.lng is not None:
        key = _zone_key(req.lat, req.lng, 2000)
        if key in _source_cache:
            del _source_cache[key]
            purged_memory = 1
        filepath = _persistent_cache_path(req.lat, req.lng, 2000)
        if filepath.exists():
            filepath.unlink()
            purged_files = 1
        logger.info(f"[CACHE-INVALIDATE] Zone ({req.lat},{req.lng}) purged: {purged_memory}+{purged_files}")
    else:
        return {"status": "error", "message": "Fournir lat+lng ou invalidate_all=true"}

    return {
        "status": "ok",
        "purged_memory": purged_memory,
        "purged_files": purged_files,
        "governance": "BCE-4X ULTRA-MAX++ — Cache terrain persistant",
    }
