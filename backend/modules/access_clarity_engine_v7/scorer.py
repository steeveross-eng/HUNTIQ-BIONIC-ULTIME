"""
Scorer — Score de clarte des acces (0→100)
PROTOCOLE BIONIC GOLDEN | BCE-4X

Composantes:
  trail_ratio (0-40):  % de distance sur sentier reel
  smoothness  (0-20):  inverse deviation angulaire
  directness  (0-20):  ratio distance_reelle / vol_oiseau
  safety      (0-20):  absence de segments non conformes
"""
import math


def compute_clarity_score(route_data: dict) -> dict:
    """
    Calcule le score de clarte d'un itineraire.
    route_data: sortie de access_engine_v6.compute_access_route
    """
    if not route_data or route_data.get("status") != "ok":
        return {"score": 0, "components": {}, "grade": "F"}

    route = route_data.get("route", {})
    segments = route.get("segments", [])

    if not segments:
        return {"score": 0, "components": {}, "grade": "F"}

    total_dist = route.get("total_distance_m", 0)
    trail_pct = route.get("trail_percentage", 0)

    # 1. Trail ratio (0-40 points)
    trail_score = min(40, trail_pct * 0.4)

    # 2. Smoothness (0-20 points)
    smoothness_score = _compute_smoothness(segments)

    # 3. Directness (0-20 points)
    directness_score = _compute_directness(segments, total_dist)

    # 4. Safety (0-20 points)
    safety_score = _compute_safety(segments)

    total = round(trail_score + smoothness_score + directness_score + safety_score, 1)

    grade = "A" if total >= 80 else "B" if total >= 60 else "C" if total >= 40 else "D" if total >= 20 else "F"

    return {
        "score": total,
        "grade": grade,
        "components": {
            "trail_ratio": round(trail_score, 1),
            "smoothness": round(smoothness_score, 1),
            "directness": round(directness_score, 1),
            "safety": round(safety_score, 1),
        },
    }


def _compute_smoothness(segments) -> float:
    """Mesure l'absence de changements de direction brusques."""
    total_angles = 0
    count = 0

    for seg in segments:
        coords = seg.get("coordinates", [])
        if len(coords) < 3:
            continue
        for i in range(1, len(coords) - 1):
            a = _angle_change(coords[i - 1], coords[i], coords[i + 1])
            total_angles += abs(a)
            count += 1

    if count == 0:
        return 15.0

    avg_angle = total_angles / count
    # Angle moyen < 10 deg = tres fluide (20 pts)
    # Angle moyen > 60 deg = tres brusque (0 pts)
    return max(0, min(20, 20 * (1 - avg_angle / 60)))


def _compute_directness(segments, total_dist) -> float:
    """Ratio distance reelle / vol d'oiseau."""
    if not segments or total_dist <= 0:
        return 10.0

    all_coords = []
    for seg in segments:
        all_coords.extend(seg.get("coordinates", []))

    if len(all_coords) < 2:
        return 10.0

    first = all_coords[0]
    last = all_coords[-1]
    direct_dist = _haversine_coord(first, last)

    if direct_dist <= 0:
        return 10.0

    ratio = direct_dist / total_dist
    # ratio 1.0 = parfaitement direct (20 pts)
    # ratio 0.3 = tres indirect (0 pts)
    return max(0, min(20, 20 * ((ratio - 0.3) / 0.7)))


def _compute_safety(segments) -> float:
    """Penalise les segments non conformes."""
    total = 0
    non_conf = 0
    for seg in segments:
        d = seg.get("distance_m", 0)
        total += d
        if seg.get("type") == "non_conformant":
            non_conf += d

    if total <= 0:
        return 15.0

    safe_ratio = 1 - (non_conf / total)
    return round(20 * safe_ratio, 1)


def _angle_change(p1, p2, p3):
    """Angle de changement de direction en degres entre 3 points [lng, lat]."""
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
