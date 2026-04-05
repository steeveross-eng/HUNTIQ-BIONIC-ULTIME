"""
M4 -- ContextualAdvisor : Conseils contextuels IA + Suggestions
==================================================================
Directive x7100-M4 -- Phase M4-A/B MAP Intelligence
BCE-4X GOLDEN V6+ | ZERO LOSS, ZERO REGRESSION

ANTI-DOUBLON :
  - solunar : APPELER, NE PAS recalculer
  - recommendation_engine : LIRE, NE PAS reimplementer
  - predictive_engine : LIRE via M3, NE PAS recalculer
  - poi_scorer (M2) : LIRE, NE PAS recalculer

Points de fusion :
  PF4-LUN1 : solunar.compute_solunar()
  PF4-LUN2 : solunar.hunting_windows
  PF4-MET1 : weather_fauna_simulation.optimal_conditions
  PF4-M3a  : predictive_layers
  PF4-M3d  : best_times (API)
  PF4-M2a  : poi_nodes
  PF4-N1   : nutrition_v6_interface.forage_quality
  PF4-S1   : strategy_master_engine.pipeline_results
"""

import os
import math
import logging
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


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance Haversine en metres."""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def get_suggestions(user_id: str) -> Dict[str, Any]:
    """Suggestions personnalisees basees sur le profil adaptatif.
    Fusionne : profil AUP + M3 tendances + M2 zones favorites.
    """
    db = _get_db()

    # Lecture profil AUP
    profile = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        return {
            "user_id": user_id,
            "suggestions": [],
            "reason": "NO_PROFILE"
        }

    suggestions = []

    # Suggestion basee sur especes preferees
    species_prefs = profile.get("species_preferences", [])
    if species_prefs:
        top_sp = max(species_prefs, key=lambda x: x.get("frequency", 0))
        suggestions.append({
            "type": "species",
            "priority": "high",
            "text": f"Espece recommandee : {top_sp['species']} (frequence {top_sp['frequency']:.0%})",
            "data": {"species": top_sp["species"], "frequency": top_sp["frequency"]}
        })

    # Suggestion basee sur horaires optimaux
    time_prefs = profile.get("time_preferences", {})
    hours = time_prefs.get("preferred_hours", [])
    if hours:
        hours_str = ", ".join([f"{h}h" for h in sorted(hours)[:3]])
        suggestions.append({
            "type": "timing",
            "priority": "medium",
            "text": f"Vos creneaux les plus productifs : {hours_str}",
            "data": {"preferred_hours": hours}
        })

    # Suggestion basee sur zones favorites
    zone_prefs = profile.get("zone_preferences", [])
    if zone_prefs:
        top_zone = max(zone_prefs, key=lambda x: x.get("satisfaction_score", 0))
        suggestions.append({
            "type": "zone",
            "priority": "medium",
            "text": f"Zone favorite : {top_zone['zone_id']} (satisfaction {top_zone['satisfaction_score']:.0%})",
            "data": {"zone_id": top_zone["zone_id"], "satisfaction": top_zone["satisfaction_score"]}
        })

    # Suggestion basee sur skill level
    skill = profile.get("skill_level", "intermediaire")
    stats = profile.get("history_stats", {})
    total = stats.get("total_trips", 0)
    suggestions.append({
        "type": "progression",
        "priority": "low",
        "text": f"Niveau : {skill} ({total} sorties). Continuez pour progresser !",
        "data": {"skill_level": skill, "total_trips": total}
    })

    # Lecture M3 tendances saisonnieres (LECTURE)
    try:
        if species_prefs:
            top_species = species_prefs[0]["species"]
            trend = await db.seasonal_trends.find_one(
                {"species": top_species},
                {"_id": 0},
                sort=[("computed_at", -1)]
            )
            if trend:
                current_week = datetime.now(timezone.utc).isocalendar()[1]
                weekly = trend.get("weekly_patterns", [])
                for wp in weekly:
                    if wp.get("week") == current_week:
                        suggestions.append({
                            "type": "trend",
                            "priority": "high",
                            "text": f"Tendance {top_species} semaine {current_week} : activite {wp.get('trend', 'stable')}",
                            "data": {"species": top_species, "week": current_week, "trend": wp.get("trend")}
                        })
                        break
    except Exception as e:
        logger.warning(f"M4 suggestions: M3 trend lookup failed: {e}")

    return {
        "user_id": user_id,
        "suggestions": suggestions,
        "count": len(suggestions),
        "profile_skill": profile.get("skill_level", "intermediaire"),
        "source": "contextual_advisor"
    }


async def get_advice(user_id: str, lat: float, lng: float) -> Dict[str, Any]:
    """Conseil contextuel IA a une position GPS.
    Fusionne : profil AUP + M3 predictions + M2 POIs proches + solunaire + M1 legal.
    """
    db = _get_db()

    # Lecture profil AUP
    profile = await db.hunter_profiles.find_one({"user_id": user_id}, {"_id": 0})
    if not profile:
        profile = {"user_id": user_id, "skill_level": "intermediaire", "species_preferences": []}

    target_species = "orignal"
    if profile.get("species_preferences"):
        target_species = profile["species_preferences"][0].get("species", "orignal")

    advice_list = []

    # PF4-M3a : Predictions au point GPS (LECTURE)
    prediction_data = {"current_probability": 0.0, "peak_hour": 6, "trend": "stable"}
    try:
        layer = await db.predictive_layers.find_one(
            {"species": target_species},
            {"_id": 0},
            sort=[("computed_at", -1)]
        )
        if layer:
            current_hour = datetime.now(timezone.utc).hour
            hourly = layer.get("hourly_layers", [])
            for hl in hourly:
                if hl.get("hour") == current_hour:
                    prediction_data["current_probability"] = hl.get("probability", 0.0)
                    break
            # Peak hour
            best_p = 0
            for hl in hourly:
                if hl.get("probability", 0) > best_p:
                    best_p = hl["probability"]
                    prediction_data["peak_hour"] = hl.get("hour", 6)
            prediction_data["trend"] = layer.get("trend", "stable")

            if prediction_data["current_probability"] > 0.6:
                advice_list.append({
                    "type": "prediction",
                    "priority": "high",
                    "text": f"Activite {target_species} prevue FORTE ({prediction_data['current_probability']:.0%}) maintenant"
                })
    except Exception as e:
        logger.warning(f"M4 advice: M3 prediction lookup failed: {e}")

    # PF4-LUN1 : Solunaire (LECTURE depuis solunar via strategy ou direct)
    solunar_data = {"score": 0, "phase": "inconnue", "next_window": "N/A"}
    try:
        sol_doc = await db.solunar_data.find_one(
            {},
            {"_id": 0},
            sort=[("computed_at", -1)]
        )
        if sol_doc:
            solunar_data["score"] = sol_doc.get("score", 0)
            solunar_data["phase"] = sol_doc.get("phase", "inconnue")
            windows = sol_doc.get("hunting_windows", [])
            if windows:
                solunar_data["next_window"] = f"{windows[0].get('start', '?')}-{windows[0].get('end', '?')}"
                if solunar_data["score"] > 60:
                    advice_list.append({
                        "type": "solunar",
                        "priority": "medium",
                        "text": f"Fenetre solunaire intense {solunar_data['next_window']}"
                    })
    except Exception as e:
        logger.warning(f"M4 advice: solunar lookup failed: {e}")

    # PF4-M2a : POIs proches (LECTURE poi_nodes, 2dsphere)
    nearby_pois = []
    try:
        pois_cursor = db.poi_nodes.find(
            {
                "location": {
                    "$nearSphere": {
                        "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                        "$maxDistance": 2000
                    }
                }
            },
            {"_id": 0}
        ).limit(5)
        async for poi in pois_cursor:
            poi_lat = poi.get("lat", poi.get("location", {}).get("coordinates", [0, 0])[1])
            poi_lng = poi.get("lng", poi.get("location", {}).get("coordinates", [0, 0])[0])
            dist = _haversine(lat, lng, poi_lat, poi_lng)
            score = poi.get("score", {}).get("global", 0) if isinstance(poi.get("score"), dict) else 0
            nearby_pois.append({
                "poi_id": poi.get("poi_id", ""),
                "name": poi.get("name", ""),
                "distance_m": round(dist),
                "score": score
            })

        if nearby_pois:
            best_poi = nearby_pois[0]
            if best_poi["score"] > 0.7:
                advice_list.append({
                    "type": "zone",
                    "priority": "medium",
                    "text": f"POI {best_poi['name']} a {best_poi['distance_m']}m, score {best_poi['score']:.1f}"
                })
            advice_list.append({
                "type": "zone",
                "priority": "low",
                "text": f"{len(nearby_pois)} POIs a moins de 2km"
            })
    except Exception as e:
        logger.warning(f"M4 advice: M2 POI lookup failed: {e}")

    # PF4-M1b : Verification legale (LECTURE legal_zones)
    try:
        legal_zone = await db.legal_zones.find_one(
            {
                "geometry": {
                    "$geoIntersects": {
                        "$geometry": {"type": "Point", "coordinates": [lng, lat]}
                    }
                }
            },
            {"_id": 0}
        )
        if legal_zone:
            restrictions = legal_zone.get("restrictions", [])
            for r in restrictions:
                if r.get("status") == "closed":
                    advice_list.append({
                        "type": "legal",
                        "priority": "critical",
                        "text": f"Attention: saison fermee pour {r.get('species', 'espece inconnue')}"
                    })
    except Exception as e:
        logger.warning(f"M4 advice: M1 legal lookup failed: {e}")

    return {
        "position": {"lat": lat, "lng": lng},
        "species": target_species,
        "prediction": prediction_data,
        "solunar": solunar_data,
        "advice": advice_list,
        "nearby_pois": nearby_pois,
        "source": "contextual_advisor",
        "directive": "x7100-M4"
    }
