"""
Scorer — Terrain Clarity Score (TCS) 0 → 100
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Composantes TCS (STEEVE-MAX directive):
  Alignement sentiers  (30%) : % de distance sur sentier reel
  Lissage              (20%) : inverse deviation angulaire
  Penetrabilite        (15%) : densite vegetation / terrain ouvert
  Topographie LIDAR    (15%) : pente, elevation, micro-relief
  Hydrologie           (10%) : proximite eau, risque inondation
  Effort reel          (10%) : ratio distance / vol oiseau + temps

Score final: 0-100, Grades: S (95+), A (80+), B (60+), C (40+), D (20+), F (<20)
"""
import math
from typing import Dict, List, Optional


# Poids TCS GOLDEN
TCS_WEIGHTS = {
    "trail_alignment": 0.30,
    "smoothness": 0.20,
    "penetrability": 0.15,
    "topography_lidar": 0.15,
    "hydrology": 0.10,
    "real_effort": 0.10,
}


def compute_tcs(
    route_data: dict,
    terrain_context: Optional[dict] = None,
) -> dict:
    """
    Calcule le Terrain Clarity Score (TCS) complet.

    route_data: sortie de access_engine ou access_clarity_engine
    terrain_context: donnees terrain supplementaires (LIDAR, hydro, vegetation)

    Retourne:
    {
        "score": 0-100,
        "grade": "S"|"A"|"B"|"C"|"D"|"F",
        "components": {
            "trail_alignment": {"score": 0-100, "weighted": 0-30, "detail": "..."},
            "smoothness": {"score": 0-100, "weighted": 0-20, "detail": "..."},
            ...
        },
        "summary": "...",
    }
    """
    if terrain_context is None:
        terrain_context = {}

    # Extraire donnees de route
    coords = route_data.get("coords", [])
    distance_m = route_data.get("distance_m", 0)
    trail_type = route_data.get("trail_type", "")
    routing_algo = route_data.get("routing_algo", "")
    segments = route_data.get("segments", [])
    trail_pct = route_data.get("trail_percentage", 0)
    phase1_dist = route_data.get("phase1_distance_m", 0)
    phase2_dist = route_data.get("phase2_distance_m", 0)

    # Si pas de segments dans route_data, estimer trail_pct depuis trail_type
    if trail_pct == 0 and trail_type:
        if trail_type in ("sentier_reel", "trail"):
            trail_pct = 95
        elif trail_type in ("hybride_sentier_terrain", "hybride"):
            trail_pct = round(phase1_dist / max(distance_m, 1) * 100, 1) if distance_m > 0 else 50
        elif trail_type in ("terrain_aware", "terrain_naturel"):
            trail_pct = 5
        elif trail_type in ("estimation", "hors_sentier"):
            trail_pct = 0

    # 1. Alignement sentiers (0-100 -> 0-30)
    trail_raw = _compute_trail_alignment(trail_pct, routing_algo)

    # 2. Lissage (0-100 -> 0-20)
    smooth_raw = _compute_smoothness(coords)

    # 3. Penetrabilite (0-100 -> 0-15)
    penetrability_raw = _compute_penetrability(
        route_data, terrain_context.get("vegetation", {})
    )

    # 4. Topographie LIDAR (0-100 -> 0-15)
    topo_raw = _compute_topography(
        coords, terrain_context.get("lidar", {}), terrain_context.get("dem", {})
    )

    # 5. Hydrologie (0-100 -> 0-10)
    hydro_raw = _compute_hydrology(
        coords, terrain_context.get("hydrology", {})
    )

    # 6. Effort reel (0-100 -> 0-10)
    effort_raw = _compute_real_effort(coords, distance_m)

    # Assembler le score
    components = {
        "trail_alignment": {
            "score": round(trail_raw, 1),
            "weighted": round(trail_raw * TCS_WEIGHTS["trail_alignment"], 1),
            "weight_pct": 30,
            "detail": f"Sentier reel: {trail_pct}%, algo: {routing_algo}",
        },
        "smoothness": {
            "score": round(smooth_raw, 1),
            "weighted": round(smooth_raw * TCS_WEIGHTS["smoothness"], 1),
            "weight_pct": 20,
            "detail": f"Angle moyen: {_avg_angle(coords):.1f} deg",
        },
        "penetrability": {
            "score": round(penetrability_raw, 1),
            "weighted": round(penetrability_raw * TCS_WEIGHTS["penetrability"], 1),
            "weight_pct": 15,
            "detail": _penetrability_detail(route_data),
        },
        "topography_lidar": {
            "score": round(topo_raw, 1),
            "weighted": round(topo_raw * TCS_WEIGHTS["topography_lidar"], 1),
            "weight_pct": 15,
            "detail": "Pente et micro-relief",
        },
        "hydrology": {
            "score": round(hydro_raw, 1),
            "weighted": round(hydro_raw * TCS_WEIGHTS["hydrology"], 1),
            "weight_pct": 10,
            "detail": "Proximite eau et drainage",
        },
        "real_effort": {
            "score": round(effort_raw, 1),
            "weighted": round(effort_raw * TCS_WEIGHTS["real_effort"], 1),
            "weight_pct": 10,
            "detail": f"Distance: {distance_m}m, directness ratio: {_directness_ratio(coords):.2f}",
        },
    }

    total = sum(c["weighted"] for c in components.values())
    total = round(min(100, max(0, total)), 1)

    grade = _grade_from_score(total)

    summary = _generate_tcs_summary(total, grade, components, distance_m, trail_pct)

    return {
        "score": total,
        "grade": grade,
        "components": components,
        "summary": summary,
        "trail_percentage": trail_pct,
        "distance_m": distance_m,
    }


def _compute_trail_alignment(trail_pct: float, routing_algo: str) -> float:
    """Score d'alignement sentier 0-100."""
    base = min(100, trail_pct)

    # Bonus pour algos reels
    if routing_algo in ("a_star", "dijkstra", "hybrid_trail_terrain"):
        base = min(100, base + 5)
    elif routing_algo == "direct_line":
        base = max(0, base - 20)

    return base


def _compute_smoothness(coords: list) -> float:
    """Score de lissage 0-100 (inverse deviation angulaire)."""
    if len(coords) < 3:
        return 70.0

    total_angles = 0
    count = 0

    for i in range(1, len(coords) - 1):
        a = _angle_change(coords[i - 1], coords[i], coords[i + 1])
        total_angles += abs(a)
        count += 1

    if count == 0:
        return 75.0

    avg_angle = total_angles / count
    # <10 deg = tres fluide (100), >90 deg = tres brusque (0)
    return max(0, min(100, 100 * (1 - avg_angle / 90)))


def _compute_penetrability(route_data: dict, vegetation: dict) -> float:
    """Score de penetrabilite 0-100."""
    terrain_types = route_data.get("terrain_types", route_data.get("phase2_terrain_types", []))
    trail_type = route_data.get("trail_type", "")

    # Sentier reel = penetrabilite maximale
    if trail_type in ("sentier_reel", "trail"):
        return 95.0

    # Terrain types scoring
    type_scores = {
        "stream_bank": 80,
        "clearing_edge": 85,
        "clearing": 75,
        "open_forest": 55,
        "dense_forest": 25,
        "wetland": 15,
    }

    if terrain_types:
        scores = [type_scores.get(t, 50) for t in terrain_types]
        return sum(scores) / len(scores)

    # Vegetation data
    canopy = vegetation.get("canopy_avg", 0.5)
    if canopy < 0.3:
        return 80.0
    elif canopy < 0.6:
        return 60.0
    elif canopy < 0.8:
        return 40.0
    return 25.0


def _compute_topography(coords: list, lidar: dict, dem: dict) -> float:
    """Score topographique LIDAR 0-100."""
    # Si donnees LIDAR disponibles
    avg_slope = lidar.get("avg_slope_pct", dem.get("avg_slope_pct", None))
    if avg_slope is not None:
        # Pente <5% = ideal (100), >30% = impraticable (10)
        return max(10, min(100, 100 - avg_slope * 3))

    # Estimation par elevation changes dans les coords
    if len(coords) < 2:
        return 65.0

    # Sans LIDAR, estimer d'apres la geometrie du chemin
    # Un chemin lisse implique peu de variation topographique
    return 65.0


def _compute_hydrology(coords: list, hydro_data: dict) -> float:
    """Score hydrologique 0-100."""
    crossings = hydro_data.get("water_crossings", 0)
    near_water = hydro_data.get("near_water_pct", 0)

    score = 80.0
    # Penaliser les traversees d'eau
    score -= crossings * 15
    # Bonus modere pour proximite eau (bords de ruisseau = corridors naturels)
    if 0 < near_water < 30:
        score += 10

    return max(0, min(100, score))


def _compute_real_effort(coords: list, distance_m: float) -> float:
    """Score d'effort reel 0-100."""
    if distance_m <= 0 or len(coords) < 2:
        return 50.0

    # Ratio directness
    ratio = _directness_ratio(coords)

    # Distance penalty
    dist_factor = 1.0
    if distance_m > 2000:
        dist_factor = max(0.5, 1 - (distance_m - 2000) / 5000)
    elif distance_m < 100:
        dist_factor = 0.9  # Trop court = suspect

    # Directness: ratio 1.0 = parfait (100), ratio 0.3 = tres indirect (30)
    directness_score = max(0, min(100, 100 * ((ratio - 0.2) / 0.8)))

    return directness_score * dist_factor


def _directness_ratio(coords: list) -> float:
    """Ratio vol d'oiseau / distance reelle."""
    if len(coords) < 2:
        return 1.0

    first = coords[0]
    last = coords[-1]
    direct = _haversine_coord(first, last)

    total = 0
    for i in range(len(coords) - 1):
        total += _haversine_coord(coords[i], coords[i + 1])

    if total <= 0:
        return 1.0
    return min(1.0, direct / total)


def _avg_angle(coords: list) -> float:
    """Angle moyen de changement de direction."""
    if len(coords) < 3:
        return 0.0
    total = 0
    count = 0
    for i in range(1, len(coords) - 1):
        total += abs(_angle_change(coords[i - 1], coords[i], coords[i + 1]))
        count += 1
    return total / max(count, 1)


def _grade_from_score(score: float) -> str:
    if score >= 95:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    elif score >= 20:
        return "D"
    return "F"


def _generate_tcs_summary(
    total: float, grade: str, components: dict,
    distance_m: float, trail_pct: float,
) -> str:
    """Resume TCS textuel."""
    best = max(components.items(), key=lambda x: x[1]["score"])
    worst = min(components.items(), key=lambda x: x[1]["score"])

    parts = [
        f"TCS {total}/100 (Grade {grade}).",
        f"Distance: {distance_m}m, sentier: {trail_pct}%.",
        f"Point fort: {best[0]} ({best[1]['score']}/100).",
        f"Amelioration: {worst[0]} ({worst[1]['score']}/100).",
    ]
    return " ".join(parts)


def _penetrability_detail(route_data: dict) -> str:
    terrain_types = route_data.get("terrain_types", route_data.get("phase2_terrain_types", []))
    if terrain_types:
        return f"Terrain: {', '.join(terrain_types)}"
    return f"Type: {route_data.get('trail_type', 'inconnu')}"


def _angle_change(p1, p2, p3):
    """Angle de changement de direction en degres entre 3 points."""
    if isinstance(p1, dict):
        dx1, dy1 = p2["lng"] - p1["lng"], p2["lat"] - p1["lat"]
        dx2, dy2 = p3["lng"] - p2["lng"], p3["lat"] - p2["lat"]
    else:
        dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
        dx2, dy2 = p3[0] - p2[0], p3[1] - p2[1]

    dot = dx1 * dx2 + dy1 * dy2
    cross = dx1 * dy2 - dy1 * dx2
    angle = math.degrees(math.atan2(abs(cross), dot))
    return angle


def _haversine_coord(c1, c2):
    if isinstance(c1, dict):
        lat1, lng1 = c1["lat"], c1["lng"]
        lat2, lng2 = c2["lat"], c2["lng"]
    else:
        lng1, lat1 = c1[0], c1[1]
        lng2, lat2 = c2[0], c2[1]

    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
