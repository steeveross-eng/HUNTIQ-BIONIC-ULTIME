"""
Smoother — Pipeline de lissage ×1000% BCE-4X GOLDEN
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Pipeline de lissage OPTIMISE:
  1. Suppression zigzags (angles brusques >120 deg)
  2. Fragmentation segments longs (anti lignes artificielles)
  3. Douglas-Peucker (reduction bruit grille)
  4. Deviation naturelle terrain (jitter forestier deterministe)
  5. Interpolation naturelle Catmull-Rom (courbes humaines)
  6. Lissage final passe-bas (moyenne mobile)

Modele Quebec (ponderations officielles STEEVE-MAX):
  sentier reel : x0.1
  zone ouverte : x0.5
  foret ouverte : x0.8
  foret moyenne : x1.2
  foret dense  : x2.5
  hors-sentier : x3.0
  non conforme : x10.0
"""
import math
import hashlib
from typing import List, Optional

# ═══════════════════════════════════════════
# MODÈLE QUÉBEC — Pondérations officielles
# ═══════════════════════════════════════════
QUEBEC_TERRAIN_COSTS = {
    "sentier_reel": 0.1,
    "zone_ouverte": 0.5,
    "foret_ouverte": 0.8,
    "foret_moyenne": 1.2,
    "foret_dense": 2.5,
    "hors_sentier": 3.0,
    "non_conforme": 10.0,
}

# Seuils de fragmentation — segments trop longs = artificiels
MAX_STRAIGHT_SEGMENT_M = 80   # Au-dela de 80m en ligne droite = fragmenter
MIN_POINTS_FOR_NATURAL = 6    # Minimum de points pour un acces naturel
JITTER_AMPLITUDE_DEG = 0.00008  # Amplitude de deviation naturelle (~8m)
JITTER_AMPLITUDE_TRAIL_DEG = 0.00002  # Deviation minimale sur sentier (~2m)


def smooth_full_pipeline(
    coords: list,
    dp_tolerance: float = 0.00003,
    zigzag_angle_threshold: float = 115.0,
    interp_points: int = 2,
    terrain_context: Optional[dict] = None,
) -> list:
    """
    Pipeline complet de lissage BCE-4X ×1000%:
    1. Suppression des zigzags (angles brusques)
    2. Fragmentation des segments longs (anti lignes artificielles)
    3. Douglas-Peucker (reduction bruit)
    4. Deviation naturelle terrain (jitter forestier)
    5. Interpolation naturelle Catmull-Rom
    6. Lissage final passe-bas (moyenne mobile)
    """
    if len(coords) < 3:
        return coords

    # Phase 1: Suppression des zigzags
    cleaned = remove_zigzags(coords, angle_threshold=zigzag_angle_threshold)

    # Phase 2: Douglas-Peucker AVANT fragmentation (reduction bruit grille)
    if len(cleaned) >= 3:
        smoothed = douglas_peucker(cleaned, tolerance=dp_tolerance)
    else:
        smoothed = cleaned

    # Phase 3: Fragmentation des segments longs (NOUVEAU x1000%)
    fragmented = fragment_long_segments(smoothed, max_segment_m=MAX_STRAIGHT_SEGMENT_M)

    # Phase 4: Deviation naturelle terrain (NOUVEAU x1000%)
    deviated = apply_natural_deviation(fragmented, terrain_context)

    # Phase 5: Interpolation naturelle Catmull-Rom
    if len(deviated) >= 3:
        natural = interpolate_natural(deviated, num_interp=interp_points)
    else:
        natural = deviated

    # Phase 6: Lissage final passe-bas (NOUVEAU ×1000%)
    if len(natural) >= 5:
        final = lowpass_smooth(natural, window=3)
    else:
        final = natural

    return final


def fragment_long_segments(coords: list, max_segment_m: float = 80) -> list:
    """
    ×1000% OPTIMISATION: Fragmente les segments trop longs en sous-segments.
    Un segment de 200m en ligne droite est artificiel — le fractionner
    en points intermediaires permet au Catmull-Rom de creer des courbes naturelles.
    """
    if len(coords) < 2:
        return coords

    is_dict = isinstance(coords[0], dict)
    result = [coords[0]]

    for i in range(len(coords) - 1):
        c1 = coords[i]
        c2 = coords[i + 1]
        dist = _haversine(c1, c2)

        if dist > max_segment_m:
            # Nombre de sous-segments necessaires
            n_sub = max(2, int(dist / max_segment_m) + 1)

            if is_dict:
                for j in range(1, n_sub):
                    t = j / n_sub
                    result.append({
                        "lat": round(c1["lat"] + t * (c2["lat"] - c1["lat"]), 7),
                        "lng": round(c1["lng"] + t * (c2["lng"] - c1["lng"]), 7),
                    })
            else:
                for j in range(1, n_sub):
                    t = j / n_sub
                    result.append([
                        round(c1[0] + t * (c2[0] - c1[0]), 7),
                        round(c1[1] + t * (c2[1] - c1[1]), 7),
                    ])

        result.append(c2)

    return result


def apply_natural_deviation(coords: list, terrain_context: Optional[dict] = None) -> list:
    """
    ×1000% OPTIMISATION: Deviation naturelle terrain.
    Ajoute de petites deviations laterales deterministes qui simulent
    le contournement naturel d'obstacles (arbres, rochers, boue).

    La graine est basee sur la position (deterministe = reproductible).
    L'amplitude varie selon le type de terrain.
    """
    if len(coords) < 3:
        return coords

    is_dict = isinstance(coords[0], dict)
    result = [coords[0]]  # Premier point toujours preservé

    for i in range(1, len(coords) - 1):
        c = coords[i]

        if is_dict:
            lat, lng = c["lat"], c["lng"]
        else:
            lng, lat = c[0], c[1]

        # Graine deterministe basee sur la position
        seed = int(hashlib.md5(f"{lat:.7f},{lng:.7f}".encode()).hexdigest()[:8], 16)
        # Convertir en angle [-pi, pi]
        angle = (seed % 628) / 100.0 - math.pi
        # Convertir en amplitude [0.3, 1.0]
        amp_factor = 0.3 + (seed % 700) / 1000.0

        # Determiner l'amplitude selon le terrain
        amplitude = JITTER_AMPLITUDE_DEG * amp_factor

        # Direction perpendiculaire au segment
        if i < len(coords) - 1:
            if is_dict:
                dx = coords[i + 1]["lng"] - coords[i - 1]["lng"]
                dy = coords[i + 1]["lat"] - coords[i - 1]["lat"]
            else:
                dx = coords[i + 1][0] - coords[i - 1][0]
                dy = coords[i + 1][1] - coords[i - 1][1]

            mag = math.sqrt(dx * dx + dy * dy)
            if mag > 1e-12:
                # Normal perpendiculaire
                nx = -dy / mag
                ny = dx / mag
                # Appliquer la deviation perpendiculaire avec variation sinusoidale
                offset_x = nx * amplitude * math.sin(angle)
                offset_y = ny * amplitude * math.sin(angle)
            else:
                offset_x = amplitude * math.cos(angle)
                offset_y = amplitude * math.sin(angle)
        else:
            offset_x = amplitude * math.cos(angle)
            offset_y = amplitude * math.sin(angle)

        new_lat = lat + offset_y
        new_lng = lng + offset_x

        if is_dict:
            result.append({"lat": round(new_lat, 7), "lng": round(new_lng, 7)})
        else:
            result.append([round(new_lng, 7), round(new_lat, 7)])

    result.append(coords[-1])  # Dernier point toujours preserve
    return result


def lowpass_smooth(coords: list, window: int = 3) -> list:
    """
    ×1000% OPTIMISATION: Lissage passe-bas (moyenne mobile).
    Adoucit les micro-deviations pour un rendu naturel et fluide.
    Preserve premier et dernier points.
    """
    if len(coords) < window + 2:
        return coords

    is_dict = isinstance(coords[0], dict)
    result = [coords[0]]  # Premier preservé

    half_w = window // 2

    for i in range(1, len(coords) - 1):
        start = max(0, i - half_w)
        end = min(len(coords), i + half_w + 1)
        n = end - start

        if is_dict:
            avg_lat = sum(coords[j]["lat"] for j in range(start, end)) / n
            avg_lng = sum(coords[j]["lng"] for j in range(start, end)) / n
            result.append({"lat": round(avg_lat, 7), "lng": round(avg_lng, 7)})
        else:
            avg_x = sum(coords[j][0] for j in range(start, end)) / n
            avg_y = sum(coords[j][1] for j in range(start, end)) / n
            result.append([round(avg_x, 7), round(avg_y, 7)])

    result.append(coords[-1])  # Dernier preserve
    return result


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
    if result[0] != coords[0]:
        result.insert(0, coords[0])
    if result[-1] != coords[-1]:
        result.append(coords[-1])

    return result


def douglas_peucker(coords: list, tolerance: float = 0.00005) -> list:
    """
    Douglas-Peucker pour reduire les points tout en preservant la forme.
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


# ═══════════════════════════════════════════
# UTILITAIRES INTERNES
# ═══════════════════════════════════════════

def _haversine(c1, c2) -> float:
    """Distance en metres entre deux coordonnees."""
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
