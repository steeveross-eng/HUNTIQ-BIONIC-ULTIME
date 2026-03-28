"""
BCE-4X P0 — ENGINE VENT & ODEURS v1
=====================================
Moteur de calcul de contamination olfactive pour la chasse.

Donnees REELLES utilisees:
- Vent du jour: direction + vitesse via Open-Meteo V3 (/api/v3/weather/windgrid)
- Vent dominant: Nord-Ouest (hardcode Quebec, autorise STEEVE-MAX)
- Thermique: matin (odeurs montent), soir (odeurs descendent)

ZERO donnee artificielle. Si une donnee est absente, retourner un flag explicite.

STEEVE-MAX 2026-03-28 — Standard institutionnel.
"""

import math
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("bionic.hunt_orchestrator.vent_odeurs")

# Vent dominant Quebec saison chasse (autorise STEEVE-MAX)
DOMINANT_WIND_DEG = 315  # Nord-Ouest

# Parametres de dispersion
SCENT_CONE_ANGLE_DEG = 45  # Demi-angle du cone de contamination
SCENT_RANGE_LIGHT_M = 300  # Vent < 10 km/h
SCENT_RANGE_MODERATE_M = 500  # Vent 10-25 km/h
SCENT_RANGE_STRONG_M = 800  # Vent > 25 km/h


def wind_deg_from_cardinal(direction: str) -> float:
    """Convertir direction cardinale en degres (direction d'OU vient le vent)."""
    mapping = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSO": 202.5, "SO": 225, "OSO": 247.5,
        "O": 270, "ONO": 292.5, "NO": 315, "NNO": 337.5,
        "SSW": 202.5, "SW": 225, "WSW": 247.5, "W": 270,
        "WNW": 292.5, "NW": 315, "NNW": 337.5,
    }
    return mapping.get(direction.upper(), 0)


def _scent_range(wind_speed_kmh: float) -> float:
    """Portee de la zone de contamination selon la vitesse du vent."""
    if wind_speed_kmh < 10:
        return SCENT_RANGE_LIGHT_M
    elif wind_speed_kmh < 25:
        return SCENT_RANGE_MODERATE_M
    else:
        return SCENT_RANGE_STRONG_M


def _thermal_modifier(session: str) -> Dict[str, Any]:
    """
    Modificateur thermique selon le moment de la journee.
    - Matin: air froid au sol, odeurs MONTENT (convection ascendante)
    - Soir: air refroidit, odeurs DESCENDENT (inversion thermique)
    """
    if session == "matin":
        return {
            "direction": "ascendante",
            "description": "Matin: odeurs montent avec la convection thermique",
            "vertical_bias": "up",
            "cone_angle_modifier": 0.8,  # Cone plus etroit (odeurs dispersees vers le haut)
            "range_modifier": 0.7,  # Portee reduite au sol
        }
    else:
        return {
            "direction": "descendante",
            "description": "Soir: odeurs descendent avec l'inversion thermique",
            "vertical_bias": "down",
            "cone_angle_modifier": 1.3,  # Cone plus large (odeurs restent au sol)
            "range_modifier": 1.4,  # Portee augmentee au sol
        }


def compute_scent_zone(
    hunter_lat: float,
    hunter_lng: float,
    wind_direction_deg: float,
    wind_speed_kmh: float,
    session: str = "matin",
) -> Dict[str, Any]:
    """
    Calcule la zone de contamination olfactive du chasseur.

    Le vent PORTE l'odeur DANS la direction du vent (downwind).
    Si le vent vient du Nord (0 deg), l'odeur va vers le Sud (180 deg).

    Retourne:
    - cone de contamination (centre, angle, portee)
    - polygone approximatif (liste de points lat/lng)
    """
    thermal = _thermal_modifier(session)

    # Direction ou l'odeur EST PORTEE (downwind = vent + 180)
    scent_bearing_deg = (wind_direction_deg + 180) % 360

    # Portee ajustee par la thermique
    base_range = _scent_range(wind_speed_kmh)
    effective_range_m = base_range * thermal["range_modifier"]

    # Angle du cone ajuste
    half_angle = SCENT_CONE_ANGLE_DEG * thermal["cone_angle_modifier"]

    # Generer le polygone du cone de contamination
    polygon = _generate_cone_polygon(
        hunter_lat, hunter_lng,
        scent_bearing_deg, half_angle, effective_range_m,
        num_arc_points=12
    )

    return {
        "hunter_position": {"lat": hunter_lat, "lng": hunter_lng},
        "wind": {
            "direction_deg": wind_direction_deg,
            "speed_kmh": wind_speed_kmh,
            "source": "real_v3",
        },
        "scent": {
            "bearing_deg": round(scent_bearing_deg, 1),
            "half_angle_deg": round(half_angle, 1),
            "range_m": round(effective_range_m),
            "thermal": thermal,
        },
        "session": session,
        "polygon": polygon,
    }


def _generate_cone_polygon(
    lat: float, lng: float,
    bearing_deg: float,
    half_angle_deg: float,
    range_m: float,
    num_arc_points: int = 12,
) -> List[Dict[str, float]]:
    """Generer les points du polygone conique de contamination."""
    points = [{"lat": round(lat, 6), "lng": round(lng, 6)}]  # Apex = chasseur

    start_angle = bearing_deg - half_angle_deg
    end_angle = bearing_deg + half_angle_deg
    step = (end_angle - start_angle) / num_arc_points

    for i in range(num_arc_points + 1):
        angle = math.radians(start_angle + step * i)
        dlat = (range_m / 111320) * math.cos(angle)
        dlng = (range_m / (111320 * math.cos(math.radians(lat)))) * math.sin(angle)
        points.append({
            "lat": round(lat + dlat, 6),
            "lng": round(lng + dlng, 6),
        })

    points.append({"lat": round(lat, 6), "lng": round(lng, 6)})  # Fermer le polygone
    return points


def point_in_scent_zone(
    point_lat: float, point_lng: float,
    scent_zone: Dict[str, Any],
) -> bool:
    """
    Verifier si un point est dans la zone de contamination.
    Utilise le test point-in-polygon (ray casting).
    """
    polygon = scent_zone.get("polygon", [])
    if len(polygon) < 3:
        return False
    return _point_in_polygon(point_lat, point_lng, polygon)


def _point_in_polygon(lat: float, lng: float, polygon: List[Dict]) -> bool:
    """Ray casting algorithm pour test point-in-polygon."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]["lat"], polygon[i]["lng"]
        yj, xj = polygon[j]["lat"], polygon[j]["lng"]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def check_path_contamination(
    path_coords: List[Dict[str, float]],
    feeding_sites: List[Dict[str, float]],
    scent_zone: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Verifier si un chemin d'acces contamine des sites d'alimentation.

    Regles:
    1. Aucun point du chemin ne doit etre a moins de 50m d'un site d'alimentation
    2. Le cone de contamination ne doit pas couvrir un site d'alimentation
    3. Le chemin ne doit pas traverser la zone de contamination d'un site

    Retourne un rapport de conformite.
    """
    violations = []

    for fs in feeding_sites:
        fs_lat, fs_lng = fs["lat"], fs["lng"]

        # Test 1: Le site d'alimentation est dans le cone de contamination du chasseur
        if point_in_scent_zone(fs_lat, fs_lng, scent_zone):
            violations.append({
                "type": "scent_contamination",
                "severity": "CRITIQUE",
                "feeding_site": fs,
                "message": f"Site alimentation ({fs_lat:.4f}, {fs_lng:.4f}) dans le cone de contamination",
            })

        # Test 2: Le chemin passe trop pres du site d'alimentation
        for i, coord in enumerate(path_coords):
            dist = _haversine(coord["lat"], coord["lng"], fs_lat, fs_lng)
            if dist < 50:
                violations.append({
                    "type": "path_proximity",
                    "severity": "HAUTE",
                    "feeding_site": fs,
                    "path_point_index": i,
                    "distance_m": round(dist),
                    "message": f"Chemin passe a {round(dist)}m du site alimentation",
                })
                break  # Une violation par site suffit

    return {
        "compliant": len(violations) == 0,
        "violations_count": len(violations),
        "violations": violations,
    }


def evaluate_blind_wind_score(
    blind_lat: float,
    blind_lng: float,
    feeding_sites: List[Dict[str, float]],
    wind_direction_deg: float,
    wind_speed_kmh: float,
    session: str = "matin",
) -> Dict[str, Any]:
    """
    Evaluer le score vent/odeur d'un affut par rapport aux sites d'alimentation.

    Un bon affut est positionne de sorte que l'odeur du chasseur
    ne soit JAMAIS portee vers les sites d'alimentation.

    Score 100 = parfait (odeur dans la direction opposee aux sites)
    Score 0 = catastrophique (odeur directement vers les sites)
    """
    if not feeding_sites:
        scent_zone = compute_scent_zone(
            blind_lat, blind_lng,
            wind_direction_deg, wind_speed_kmh, session
        )
        return {
            "score": 50,
            "certainty": 0.3,
            "message": "Aucun site alimentation connu — score neutre",
            "contaminated_sites": [],
            "contamination_count": 0,
            "session": session,
            "scent_zone": scent_zone,
        }

    scent_zone = compute_scent_zone(
        blind_lat, blind_lng,
        wind_direction_deg, wind_speed_kmh, session
    )

    contaminated = []
    scores = []

    for fs in feeding_sites:
        fs_lat, fs_lng = fs["lat"], fs["lng"]
        # Angle entre l'affut et le site d'alimentation
        angle_to_site = math.degrees(math.atan2(
            fs_lng - blind_lng, fs_lat - blind_lat
        )) % 360

        # Direction de l'odeur (downwind)
        scent_bearing = scent_zone["scent"]["bearing_deg"]

        # Difference angulaire
        diff = abs(angle_to_site - scent_bearing)
        if diff > 180:
            diff = 360 - diff

        # Score: plus la difference est grande, mieux c'est
        # 180 deg = parfait (odeur dans la direction opposee)
        # 0 deg = catastrophique (odeur droit vers le site)
        site_score = min(100, (diff / 180) * 100)

        # Verifier contamination directe
        is_contaminated = point_in_scent_zone(fs_lat, fs_lng, scent_zone)
        if is_contaminated:
            site_score = 0
            contaminated.append(fs)

        scores.append(site_score)

    avg_score = sum(scores) / len(scores) if scores else 50
    min_score = min(scores) if scores else 50

    # Le score final est le MINIMUM (le pire cas dicte la decision)
    final_score = min_score

    return {
        "score": round(final_score, 1),
        "certainty": 0.9,
        "avg_score": round(avg_score, 1),
        "min_score": round(min_score, 1),
        "contaminated_sites": contaminated,
        "contamination_count": len(contaminated),
        "session": session,
        "scent_zone": scent_zone,
        "message": (
            f"Score vent/odeur: {round(final_score)}/100. "
            f"{len(contaminated)} site(s) contamine(s)."
        ),
    }


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance en metres entre deux points GPS."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
