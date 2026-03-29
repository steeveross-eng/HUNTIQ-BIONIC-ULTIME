"""
Smoother — Lissage de traces Douglas-Peucker + interpolation naturelle + suppression zigzags
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Pipeline de lissage:
  1. Suppression zigzags (angles brusques >120 deg)
  2. Douglas-Peucker (reduction bruit grille)
  3. Interpolation naturelle Catmull-Rom (courbes humaines)
"""
import math
from typing import List, Union


def smooth_full_pipeline(
    coords: list,
    dp_tolerance: float = 0.00003,
    zigzag_angle_threshold: float = 120.0,
    interp_points: int = 2,
) -> list:
    """
    Pipeline complet de lissage BCE-4X:
    1. Suppression zigzags (angles brusques)
    2. Douglas-Peucker (reduction bruit)
    3. Interpolation naturelle Catmull-Rom
    """
    if len(coords) < 3:
        return coords

    # Phase 1: Suppression des zigzags
    cleaned = remove_zigzags(coords, angle_threshold=zigzag_angle_threshold)

    # Phase 2: Douglas-Peucker
    if len(cleaned) >= 3:
        smoothed = douglas_peucker(cleaned, tolerance=dp_tolerance)
    else:
        smoothed = cleaned

    # Phase 3: Interpolation naturelle
    if len(smoothed) >= 3:
        natural = interpolate_natural(smoothed, num_interp=interp_points)
    else:
        natural = smoothed

    return natural


def remove_zigzags(coords: list, angle_threshold: float = 120.0) -> list:
    """
    Supprime les points creant des changements de direction brusques (zigzags).
    Un zigzag est un point ou l'angle de changement de direction depasse le seuil.
    Preserve toujours le premier et dernier point.
    """
    if len(coords) <= 3:
        return coords

    is_dict = isinstance(coords[0], dict)
    if is_dict:
        pts = [(c["lng"], c["lat"]) for c in coords]
    else:
        pts = [(c[0], c[1]) for c in coords]

    keep = [True] * len(pts)
    max_passes = 3

    for _ in range(max_passes):
        changed = False
        active_pts = [i for i in range(len(pts)) if keep[i]]
        if len(active_pts) <= 3:
            break

        for idx in range(1, len(active_pts) - 1):
            i_prev = active_pts[idx - 1]
            i_curr = active_pts[idx]
            i_next = active_pts[idx + 1]

            angle = _angle_change_deg(pts[i_prev], pts[i_curr], pts[i_next])
            if angle > angle_threshold:
                keep[i_curr] = False
                changed = True

        if not changed:
            break

    result = [coords[i] for i in range(len(coords)) if keep[i]]
    # Toujours garder premier et dernier
    if result[0] != coords[0]:
        result.insert(0, coords[0])
    if result[-1] != coords[-1]:
        result.append(coords[-1])

    return result


def douglas_peucker(coords: list, tolerance: float = 0.00005) -> list:
    """
    Douglas-Peucker pour reduire les points tout en preservant la forme.
    coords: liste de [lng, lat] ou {"lat": ..., "lng": ...}
    """
    if len(coords) <= 2:
        return coords

    is_dict = isinstance(coords[0], dict)
    if is_dict:
        pts = [(c["lng"], c["lat"]) for c in coords]
    else:
        pts = [(c[0], c[1]) for c in coords]

    result_indices = _dp_recursive(pts, 0, len(pts) - 1, tolerance)
    result_indices = sorted(set(result_indices))

    return [coords[i] for i in result_indices]


def _dp_recursive(pts, start, end, tolerance):
    if end - start <= 1:
        return [start, end]

    max_dist = 0
    max_idx = start

    for i in range(start + 1, end):
        d = _point_line_distance(pts[i], pts[start], pts[end])
        if d > max_dist:
            max_dist = d
            max_idx = i

    if max_dist > tolerance:
        left = _dp_recursive(pts, start, max_idx, tolerance)
        right = _dp_recursive(pts, max_idx, end, tolerance)
        return left + right[1:]
    else:
        return [start, end]


def _point_line_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == 0 and dy == 0:
        return math.sqrt((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    proj = (a[0] + t * dx, a[1] + t * dy)
    return math.sqrt((p[0] - proj[0]) ** 2 + (p[1] - proj[1]) ** 2)


def interpolate_natural(coords: list, num_interp: int = 3) -> list:
    """
    Ajoute des points intermediaires entre les segments rectilignes
    pour creer un trace plus naturel (interpolation Catmull-Rom).
    """
    if len(coords) < 3:
        return coords

    is_dict = isinstance(coords[0], dict)
    if is_dict:
        pts = [(c["lng"], c["lat"]) for c in coords]
    else:
        pts = list(coords)

    result = [pts[0]]

    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1 = pts[i]
        p2 = pts[min(len(pts) - 1, i + 1)]
        p3 = pts[min(len(pts) - 1, i + 2)]

        for j in range(1, num_interp + 1):
            t = j / (num_interp + 1)
            x = _catmull_rom(t, p0[0], p1[0], p2[0], p3[0])
            y = _catmull_rom(t, p0[1], p1[1], p2[1], p3[1])
            result.append((x, y))

        result.append(pts[i + 1])

    if is_dict:
        return [{"lng": round(p[0], 7), "lat": round(p[1], 7)} for p in result]
    else:
        return [[round(p[0], 7), round(p[1], 7)] for p in result]


def _catmull_rom(t, p0, p1, p2, p3, alpha=0.3):
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        (2 * p1) +
        (-p0 + p2) * t +
        (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
        (-p0 + 3 * p1 - 3 * p2 + p3) * t3
    )


def _angle_change_deg(p1, p2, p3):
    """Angle de changement de direction en degres entre 3 points (x, y)."""
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = p3[0] - p2[0], p3[1] - p2[1]

    mag1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
    mag2 = math.sqrt(dx2 * dx2 + dy2 * dy2)
    if mag1 < 1e-12 or mag2 < 1e-12:
        return 0.0

    dot = dx1 * dx2 + dy1 * dy2
    cross = dx1 * dy2 - dy1 * dx2
    angle = math.degrees(math.atan2(abs(cross), dot))
    return angle
