"""
Smoother — Lissage de traces Douglas-Peucker + interpolation naturelle
PROTOCOLE BIONIC GOLDEN | BCE-4X
"""
import math


def douglas_peucker(coords, tolerance=0.00005):
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


def interpolate_natural(coords, num_interp=3):
    """
    Ajoute des points intermediaires entre les segments rectilignes
    pour creer un trace plus naturel (interpolation Catmull-Rom simplifiee).
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
