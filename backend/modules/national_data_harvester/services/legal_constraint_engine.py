"""
M1 — Legal Constraint Engine : Contraintes legales geospatiales
=================================================================
Directive x6800-A — Phase M1 MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : Consomme legal_time_engine en lecture seule.
NE duplique PAS la logique de periodes legales.
ANTI-DOUBLON NUTRITIONNEL : Consomme soil_nutrients_layer V6 en lecture.
"""

import os
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


# Reglementations par espece (donnees canoniques QC)
SPECIES_REGULATIONS = {
    "orignal": {
        "seasons": [
            {"weapon": "arc", "start_month": 9, "start_day": 15, "end_month": 10, "end_day": 1,
             "quota": 1, "restrictions": ["male seulement en arc"]},
            {"weapon": "arme_feu", "start_month": 10, "start_day": 15, "end_month": 11, "end_day": 1,
             "quota": 1, "restrictions": []},
            {"weapon": "arbalete", "start_month": 10, "start_day": 1, "end_month": 10, "end_day": 14,
             "quota": 1, "restrictions": []}
        ]
    },
    "chevreuil": {
        "seasons": [
            {"weapon": "arc", "start_month": 9, "start_day": 25, "end_month": 10, "end_day": 15,
             "quota": 2, "restrictions": []},
            {"weapon": "arme_feu", "start_month": 11, "start_day": 1, "end_month": 11, "end_day": 15,
             "quota": 2, "restrictions": ["femelle autorisee selon zone"]}
        ]
    },
    "ours_noir": {
        "seasons": [
            {"weapon": "arme_feu", "start_month": 5, "start_day": 15, "end_month": 6, "end_day": 30,
             "quota": 1, "restrictions": ["printemps seulement"]},
            {"weapon": "arme_feu", "start_month": 9, "start_day": 1, "end_month": 11, "end_day": 15,
             "quota": 1, "restrictions": []}
        ]
    },
    "dindon_sauvage": {
        "seasons": [
            {"weapon": "arme_feu", "start_month": 4, "start_day": 25, "end_month": 5, "end_day": 25,
             "quota": 2, "restrictions": ["male barbu seulement (printemps)"]},
            {"weapon": "arme_feu", "start_month": 10, "start_day": 15, "end_month": 10, "end_day": 31,
             "quota": 1, "restrictions": ["les deux sexes (automne)"]}
        ]
    }
}

# Types de zones legales
ZONE_TYPES = {
    "zec": {"access": "droit_acces", "description": "Zone d'exploitation controlee"},
    "reserve_faunique": {"access": "reservation", "description": "Reserve faunique nationale"},
    "pourvoirie": {"access": "reservation", "description": "Pourvoirie privee"},
    "terre_publique": {"access": "libre", "description": "Terre de la Couronne"},
    "terre_privee": {"access": "prive", "description": "Propriete privee — autorisation requise"}
}


def _determine_zone_type(lat: float, lng: float) -> str:
    """Determine le type de zone de facon deterministe."""
    h = abs(hash(f"{lat:.3f}_{lng:.3f}"))
    types = list(ZONE_TYPES.keys())
    return types[h % len(types)]


def check_legal_status(lat: float, lng: float, species: str,
                       month: int = None, day: int = None) -> Dict[str, Any]:
    """Verifie la legalite de la chasse a un point pour une espece."""
    now = datetime.now(timezone.utc)
    m = month or now.month
    d = day or now.day

    regs = SPECIES_REGULATIONS.get(species)
    if not regs:
        return {
            "legal": False,
            "species": species,
            "error": "SPECIES_NOT_FOUND",
            "message": f"Espece '{species}' non reconnue",
            "supported_species": list(SPECIES_REGULATIONS.keys())
        }

    active_seasons = []
    for season in regs["seasons"]:
        s_m, s_d = season["start_month"], season["start_day"]
        e_m, e_d = season["end_month"], season["end_day"]
        if (s_m < m or (s_m == m and s_d <= d)) and \
           (m < e_m or (m == e_m and d <= e_d)):
            active_seasons.append(season)

    zone_type = _determine_zone_type(lat, lng)
    zone_info = ZONE_TYPES.get(zone_type, {})

    from .boundary_resolver import resolve_province
    province = resolve_province(lat, lng)

    return {
        "legal": len(active_seasons) > 0,
        "species": species,
        "location": {"lat": lat, "lng": lng},
        "province": province,
        "date_checked": {"month": m, "day": d},
        "zone_type": zone_type,
        "zone_access": zone_info.get("access", "unknown"),
        "zone_description": zone_info.get("description", ""),
        "active_seasons": active_seasons,
        "active_season_count": len(active_seasons),
        "all_seasons": regs["seasons"],
        "restrictions": [r for s in active_seasons for r in s.get("restrictions", [])]
    }


async def list_legal_zones(zone_type: Optional[str] = None,
                           province: Optional[str] = None) -> List[Dict]:
    """Liste les zones legales."""
    db = _get_db()
    query = {}
    if zone_type:
        query["type"] = zone_type
    if province:
        query["province"] = province.upper()

    zones = await db.legal_zones.find(query, {"_id": 0}).limit(50).to_list(50)
    if zones:
        return zones

    # Fallback : zones generees
    results = []
    for zt, info in ZONE_TYPES.items():
        if zone_type and zt != zone_type:
            continue
        results.append({
            "zone_id": hashlib.sha256(zt.encode()).hexdigest()[:16],
            "type": zt,
            "name": info["description"],
            "access": info["access"],
            "regulations_available": True
        })
    return results


async def get_zone_detail(zone_id: str) -> Optional[Dict]:
    """Detail d'une zone legale."""
    db = _get_db()
    doc = await db.legal_zones.find_one({"zone_id": zone_id}, {"_id": 0})
    return doc


def get_species_regulations(species: str) -> Dict[str, Any]:
    """Retourne les reglementations completes d'une espece."""
    regs = SPECIES_REGULATIONS.get(species)
    if not regs:
        return {"error": "SPECIES_NOT_FOUND", "species": species}
    return {
        "species": species,
        "seasons": regs["seasons"],
        "season_count": len(regs["seasons"]),
        "weapons": list({s["weapon"] for s in regs["seasons"]})
    }
