"""
BCE-4X P0 — ORCHESTRATEUR DE CHASSE v1
========================================
Orchestrateur global qui combine:
- Engine Vent & Odeurs
- Engine Acces Dynamique
- Engine Choix des Affuts

Produit une recommandation complete et justifiee pour une session de chasse.

STEEVE-MAX 2026-03-28 — Standard institutionnel.
"""

import logging
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from engines.hunt_orchestrator.vent_odeurs import (
    compute_scent_zone, wind_deg_from_cardinal, DOMINANT_WIND_DEG,
)
from engines.hunt_orchestrator.choix_affuts import recommend_blinds
from engines.hunt_orchestrator.access_engine import (
    compute_access_route, find_best_entry_point,
)

logger = logging.getLogger("bionic.hunt_orchestrator")


def _haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def orchestrate_hunt_session(
    center_lat: float,
    center_lng: float,
    wind_direction_deg: float,
    wind_speed_kmh: float,
    session: str = "matin",
    species: str = "orignal",
    radius_m: int = 600,
    feeding_sites: List[Dict] = None,
    fixed_blinds: List[Dict] = None,
    trail_graph=None,
    water_check_fn=None,
    max_blinds: int = 5,
) -> Dict[str, Any]:
    """
    Orchestration complete d'une session de chasse.

    Etapes:
    1. Charger/recevoir le graphe de sentiers (terrain_nav)
    2. Recommander les affuts (choix_affuts)
    3. Pour chaque affut recommande, calculer l'acces optimal (access_engine)
    4. Valider la non-contamination de chaque acces
    5. Produire la recommandation finale
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    if feeding_sites is None:
        feeding_sites = []
    if fixed_blinds is None:
        fixed_blinds = []

    # Charger le graphe terrain si pas fourni
    if trail_graph is None:
        from engines.terrain_nav import get_terrain_nav
        trail_graph = get_terrain_nav(center_lat, center_lng, radius_m=max(radius_m * 2, 2000))

    # Charger les donnees terrain brutes pour le routage terrain-aware
    from engines.terrain_nav import get_raw_terrain_data
    raw_terrain_data = get_raw_terrain_data(center_lat, center_lng)

    # Phase 1: Recommander les affuts
    blinds = recommend_blinds(
        center_lat, center_lng,
        wind_direction_deg, wind_speed_kmh, session,
        feeding_sites, trail_graph,
        fixed_blinds=fixed_blinds,
        water_check_fn=water_check_fn,
        radius_m=radius_m,
        species=species,
        max_blinds=max_blinds,
    )

    # Phase 2: Pour chaque affut, trouver le meilleur point d'entree et calculer l'acces
    recommendations = []
    for blind in blinds:
        # Trouver les meilleurs points d'entree
        entry_points = find_best_entry_point(
            blind["lat"], blind["lng"],
            trail_graph, wind_direction_deg,
            max_entries=2,
        )

        # Calculer le cone de contamination pour cet affut
        scent_zone = compute_scent_zone(
            blind["lat"], blind["lng"],
            wind_direction_deg, wind_speed_kmh, session,
        )

        best_access = None
        access_alternatives = []

        # Essayer chaque point d'entree
        for ep in entry_points:
            access = compute_access_route(
                ep["lat"], ep["lng"],
                blind["lat"], blind["lng"],
                trail_graph, feeding_sites, scent_zone,
                water_check_fn=water_check_fn,
                terrain_data=raw_terrain_data,
            )
            access["entry_point"] = {
                "lat": ep["lat"],
                "lng": ep["lng"],
                "wind_alignment_score": ep["wind_alignment_score"],
            }

            if access["feasible"] and (best_access is None or access["quality_score"] > best_access["quality_score"]):
                if best_access:
                    access_alternatives.append(best_access)
                best_access = access
            else:
                access_alternatives.append(access)

        # Si aucun acces n'est faisable, essayer depuis le centre
        if best_access is None:
            center_access = compute_access_route(
                center_lat, center_lng,
                blind["lat"], blind["lng"],
                trail_graph, feeding_sites, scent_zone,
                water_check_fn=water_check_fn,
                terrain_data=raw_terrain_data,
            )
            center_access["entry_point"] = {
                "lat": center_lat,
                "lng": center_lng,
                "wind_alignment_score": 0,
            }
            if center_access["feasible"]:
                best_access = center_access
            else:
                # Garder le meilleur meme non conforme
                all_attempts = access_alternatives + ([center_access] if center_access["coords"] else [])
                if all_attempts:
                    best_access = max(all_attempts, key=lambda a: a.get("quality_score", 0))

        # Generer la justification textuelle
        justification = _generate_justification(
            blind, best_access, scent_zone, session,
            wind_direction_deg, wind_speed_kmh, feeding_sites,
        )

        recommendations.append({
            "blind": {
                "id": blind.get("id", "unknown"),
                "name": blind.get("name", "Affut"),
                "lat": blind["lat"],
                "lng": blind["lng"],
                "type_key": blind["type_key"],
                "type_name": blind["type_name"],
                "is_fixed": blind.get("is_fixed", False),
                "score": blind["score"],
                "factors": blind["factors"],
            },
            "access": best_access,
            "access_alternatives": access_alternatives[:1],
            "scent_zone": {
                "polygon": scent_zone["polygon"],
                "bearing_deg": scent_zone["scent"]["bearing_deg"],
                "range_m": scent_zone["scent"]["range_m"],
                "session": session,
            },
            "justification": justification,
            "rank": 0,  # Sera mis a jour apres tri
        })

    # Trier par score global (blind score + access quality)
    for rec in recommendations:
        blind_score = rec["blind"]["score"]
        access_score = rec["access"]["quality_score"] if rec["access"] else 0
        rec["composite_score"] = round(blind_score * 0.6 + access_score * 0.4, 1)

    recommendations.sort(key=lambda r: r["composite_score"], reverse=True)
    for i, rec in enumerate(recommendations):
        rec["rank"] = i + 1

    # Recommandation principale
    primary = recommendations[0] if recommendations else None

    return {
        "status": "success",
        "timestamp": timestamp,
        "session": session,
        "species": species,
        "center": {"lat": center_lat, "lng": center_lng},
        "radius_m": radius_m,
        "wind": {
            "direction_deg": wind_direction_deg,
            "speed_kmh": wind_speed_kmh,
            "dominant_deg": DOMINANT_WIND_DEG,
            "source": "real_open_meteo_v3",
        },
        "terrain": {
            "trails_available": not trail_graph.is_empty if trail_graph else False,
            "graph_stats": trail_graph.stats if trail_graph and hasattr(trail_graph, "stats") else {},
        },
        "feeding_sites_count": len(feeding_sites),
        "fixed_blinds_count": len(fixed_blinds),
        "primary_recommendation": {
            "blind_name": primary["blind"]["name"] if primary else "Aucun",
            "blind_type": primary["blind"]["type_name"] if primary else "N/A",
            "score": primary["composite_score"] if primary else 0,
            "access_distance_m": primary["access"]["distance_m"] if primary and primary["access"] else 0,
            "access_feasible": primary["access"]["feasible"] if primary and primary["access"] else False,
            "justification": primary["justification"] if primary else "Aucun affut recommandable.",
        } if primary else None,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "data_sources": {
            "wind": "Open-Meteo V3 (reel)",
            "trails": "OSM/Overpass (reel)",
            "water": "OSM cache (41K polygones)",
            "feeding": "Organic zones algorithm",
            "blinds_fixed": "Waypoints utilisateur" if fixed_blinds else "Aucun",
        },
        "governance": "BCE-4X P0 — ZERO donnee artificielle",
    }


def _generate_justification(
    blind: Dict,
    access: Optional[Dict],
    scent_zone: Dict,
    session: str,
    wind_deg: float,
    wind_kmh: float,
    feeding_sites: List[Dict],
) -> str:
    """Generer une justification textuelle claire et professionnelle."""
    parts = []

    # Type d'affut
    is_fixed = blind.get("is_fixed", False)
    parts.append(
        f"{'Affut fixe' if is_fixed else 'Position mobile'}: {blind['type_name']}."
    )

    # Vent et odeurs
    wind_cardinal = _deg_to_cardinal(wind_deg)
    scent_bearing = _deg_to_cardinal(scent_zone["scent"]["bearing_deg"])
    parts.append(
        f"Vent {wind_cardinal} {wind_kmh:.0f} km/h — odeur portee vers {scent_bearing}."
    )

    # Session
    if session == "matin":
        parts.append("Matin: convection ascendante, odeurs dispersees vers le haut.")
    else:
        parts.append("Soir: inversion thermique, odeurs restent au sol — vigilance accrue.")

    # Contamination
    wind_factor = blind.get("factors", {}).get("wind_scent", {})
    contam_count = wind_factor.get("contaminated_sites", 0)
    if contam_count == 0:
        parts.append("ZERO site d'alimentation contamine.")
    else:
        parts.append(f"ATTENTION: {contam_count} site(s) d'alimentation dans le cone de contamination.")

    # Acces
    if access and access.get("feasible"):
        parts.append(
            f"Acces: {access['distance_m']}m via sentier reel OSM ({access['routing_algo']})."
        )
    elif access and access.get("coords"):
        parts.append(
            f"Acces: {access['distance_m']}m — ATTENTION: {access['contamination_check']['violations_count']} violation(s)."
        )
    else:
        parts.append("Acces: AUCUN sentier reel disponible.")

    # Score
    parts.append(f"Score global: {blind['score']:.0f}/100.")

    return " ".join(parts)


def _deg_to_cardinal(deg: float) -> str:
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO']
    return directions[round(deg / 22.5) % 16]
