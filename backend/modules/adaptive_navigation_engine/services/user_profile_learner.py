"""
M4 -- UserProfileLearner : Profil adaptatif chasseur
========================================================
Directive x7100-M4 -- Phase M4-A MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON : recommendation_engine, scoring_engine consommes en LECTURE.
NE recree PAS la logique de recommandation ni de scoring produit.
Apprentissage depuis hunting_trip_logger (LECTURE), navigation_sessions (M4 interne).
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
_client = None
_db = None

SKILL_LEVELS = ["debutant", "intermediaire", "avance", "expert"]

DEFAULT_PROFILE_TEMPLATE = {
    "species_preferences": [],
    "zone_preferences": [],
    "time_preferences": {
        "preferred_hours": [5, 6, 7, 16, 17, 18],
        "preferred_days": ["samedi", "dimanche"],
        "preferred_season_weeks": [38, 39, 40, 41, 42]
    },
    "meteo_preferences": {
        "min_temp_c": -5,
        "max_temp_c": 15,
        "wind_tolerance_kmh": 20,
        "rain_tolerance": "light"
    },
    "skill_level": "intermediaire",
    "equipment": {
        "has_gps": True,
        "has_radio": False,
        "mobility": "a_pied"
    },
    "history_stats": {
        "total_trips": 0,
        "total_hours": 0,
        "species_harvested": {},
        "avg_distance_km": 0
    }
}


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


async def ensure_indexes():
    """Cree les index MongoDB pour hunter_profiles."""
    db = _get_db()
    await db.hunter_profiles.create_index("user_id", unique=True)
    await db.hunter_profiles.create_index("profile_id", unique=True)
    await db.hunter_profiles.create_index("skill_level")
    logger.info("M4 hunter_profiles indexes created")


async def get_or_create_profile(user_id: str) -> Dict[str, Any]:
    """Recupere ou cree le profil adaptatif avec valeurs par defaut regionales (QC)."""
    db = _get_db()
    doc = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if doc:
        return doc

    now = datetime.now(timezone.utc).isoformat()
    profile = {
        "profile_id": str(uuid.uuid4()),
        "user_id": user_id,
        **{k: (v.copy() if isinstance(v, (dict, list)) else v)
           for k, v in DEFAULT_PROFILE_TEMPLATE.items()},
        "created_at": now,
        "updated_at": now
    }
    # Deep copy nested structures
    profile["species_preferences"] = []
    profile["zone_preferences"] = []
    profile["time_preferences"] = dict(DEFAULT_PROFILE_TEMPLATE["time_preferences"])
    profile["time_preferences"]["preferred_hours"] = list(DEFAULT_PROFILE_TEMPLATE["time_preferences"]["preferred_hours"])
    profile["time_preferences"]["preferred_days"] = list(DEFAULT_PROFILE_TEMPLATE["time_preferences"]["preferred_days"])
    profile["time_preferences"]["preferred_season_weeks"] = list(DEFAULT_PROFILE_TEMPLATE["time_preferences"]["preferred_season_weeks"])
    profile["meteo_preferences"] = dict(DEFAULT_PROFILE_TEMPLATE["meteo_preferences"])
    profile["equipment"] = dict(DEFAULT_PROFILE_TEMPLATE["equipment"])
    profile["history_stats"] = dict(DEFAULT_PROFILE_TEMPLATE["history_stats"])
    profile["history_stats"]["species_harvested"] = {}

    await db.hunter_profiles.insert_one(profile)
    # Remove _id from returned profile
    profile.pop("_id", None)
    return profile


async def update_preferences(user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Met a jour les preferences explicites du profil."""
    db = _get_db()
    existing = await db.hunter_profiles.find_one({"user_id": user_id})
    if not existing:
        return None

    allowed_fields = [
        "species_preferences", "zone_preferences", "time_preferences",
        "meteo_preferences", "equipment"
    ]
    set_fields = {}
    for key, value in updates.items():
        if key in allowed_fields:
            set_fields[key] = value

    if not set_fields:
        existing.pop("_id", None)
        return existing

    set_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.hunter_profiles.update_one(
        {"user_id": user_id},
        {"$set": set_fields}
    )

    doc = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})
    return doc


def _compute_skill(stats: Dict[str, Any]) -> str:
    """Calcul du skill_level selon les regles AUP-L6."""
    total_trips = stats.get("total_trips", 0)
    total_harvested = sum(stats.get("species_harvested", {}).values())
    success_rate = total_harvested / total_trips if total_trips > 0 else 0
    avg_distance = stats.get("avg_distance_km", 0)

    score = 0
    # trips
    if total_trips >= 50:
        score += 3
    elif total_trips >= 20:
        score += 2
    elif total_trips >= 5:
        score += 1

    # success_rate
    if success_rate > 0.4:
        score += 3
    elif success_rate > 0.25:
        score += 2
    elif success_rate > 0.1:
        score += 1

    # distance
    if avg_distance > 10:
        score += 3
    elif avg_distance > 5:
        score += 2
    elif avg_distance > 2:
        score += 1

    if score >= 7:
        return "expert"
    elif score >= 4:
        return "avance"
    elif score >= 2:
        return "intermediaire"
    return "debutant"


async def learn_from_history(user_id: str) -> Dict[str, Any]:
    """Apprentissage automatique depuis hunting_trips (LECTURE)."""
    db = _get_db()

    # Ensure profile exists
    profile = await get_or_create_profile(user_id)

    # Read from hunting_trips (hunting_trip_logger, LECTURE SEULE)
    trips_cursor = db.hunting_trips.find({"user_id": user_id}, {"_id": 0})
    trips = await trips_cursor.to_list(length=500)

    if not trips:
        return {
            "user_id": user_id,
            "trips_analyzed": 0,
            "learning_applied": False,
            "reason": "NO_TRIPS_FOUND",
            "profile": profile
        }

    # AUP-L1: Frequence espece
    species_count = {}
    species_success = {}
    total_trips = len(trips)
    total_hours = 0
    distances = []
    start_hours = []
    zone_visits = {}

    for trip in trips:
        species = trip.get("species") or trip.get("target_species", "unknown")
        species_count[species] = species_count.get(species, 0) + 1

        if trip.get("success") or trip.get("harvest"):
            species_success[species] = species_success.get(species, 0) + 1

        total_hours += trip.get("duration_hours", 0)
        if trip.get("distance_km"):
            distances.append(trip["distance_km"])

        start_h = trip.get("start_hour")
        if start_h is not None:
            start_hours.append(start_h)

        zone = trip.get("zone_id", "")
        if zone:
            zone_visits[zone] = zone_visits.get(zone, 0) + 1

    # Build species_preferences (AUP-L1, AUP-L2)
    species_preferences = []
    for sp, count in species_count.items():
        freq = count / total_trips
        success = species_success.get(sp, 0)
        sr = success / count if count > 0 else 0
        species_preferences.append({
            "species": sp,
            "frequency": round(freq, 3),
            "success_rate": round(sr, 3),
            "preferred_weapon": "arme_feu",
            "preferred_zones": []
        })

    # AUP-L3: Heures preferees (mode sur les 20 dernieres sorties)
    recent_hours = start_hours[-20:] if start_hours else [5, 6, 7, 16, 17, 18]
    hour_count = {}
    for h in recent_hours:
        hour_count[h] = hour_count.get(h, 0) + 1
    preferred_hours = sorted(hour_count, key=hour_count.get, reverse=True)[:6]

    # AUP-L4: Zones preferees
    zone_preferences = []
    for zid, vcount in sorted(zone_visits.items(), key=lambda x: x[1], reverse=True)[:10]:
        zone_preferences.append({
            "zone_id": zid,
            "visit_count": vcount,
            "last_visit": datetime.now(timezone.utc).isoformat(),
            "satisfaction_score": min(1.0, vcount / max(total_trips, 1))
        })

    # AUP-L7: Distance moyenne
    avg_distance = sum(distances) / len(distances) if distances else 0

    # History stats
    history_stats = {
        "total_trips": total_trips,
        "total_hours": round(total_hours, 1),
        "species_harvested": species_success,
        "avg_distance_km": round(avg_distance, 2)
    }

    # AUP-L6: Compute skill
    skill_level = _compute_skill(history_stats)

    now = datetime.now(timezone.utc).isoformat()
    update_data = {
        "species_preferences": species_preferences,
        "zone_preferences": zone_preferences,
        "time_preferences": {
            **profile.get("time_preferences", {}),
            "preferred_hours": preferred_hours
        },
        "history_stats": history_stats,
        "skill_level": skill_level,
        "updated_at": now
    }

    await db.hunter_profiles.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )

    updated = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})

    return {
        "user_id": user_id,
        "trips_analyzed": total_trips,
        "learning_applied": True,
        "species_learned": len(species_preferences),
        "zones_learned": len(zone_preferences),
        "skill_level": skill_level,
        "profile": updated
    }


async def get_species_affinity(user_id: str) -> Dict[str, Any]:
    """Affinites espece calculees depuis le profil."""
    profile = await get_or_create_profile(user_id)
    prefs = profile.get("species_preferences", [])
    affinities = []
    for sp in prefs:
        affinity = round(sp.get("frequency", 0) * 0.5 + sp.get("success_rate", 0) * 0.5, 3)
        affinities.append({
            "species": sp["species"],
            "affinity": affinity,
            "frequency": sp.get("frequency", 0),
            "success_rate": sp.get("success_rate", 0)
        })
    affinities.sort(key=lambda x: x["affinity"], reverse=True)
    return {
        "user_id": user_id,
        "affinities": affinities,
        "top_species": affinities[0]["species"] if affinities else None
    }
