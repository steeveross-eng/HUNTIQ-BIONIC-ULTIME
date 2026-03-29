"""
Segment Classifier — Classification couleur des segments de chemin
PROTOCOLE BIONIC GOLDEN — Pipeline unique acces aux affuts V6
"""
import logging

logger = logging.getLogger("access_engine_v6.classifier")

SEGMENT_TYPES = {
    "trail": {"color": "#2ECC71", "label": "Sentier reel OSM", "style": "solid"},
    "hybrid": {"color": "#3498DB", "label": "Hybride sentier+terrain", "style": "solid"},
    "off_trail_optimized": {"color": "#F1C40F", "label": "Hors-sentier optimise", "style": "dashed"},
    "non_conformant": {"color": "#E74C3C", "label": "Non conforme", "style": "dotted"},
}


def classify_path_segments(
    grid_path: list,
    grid: dict,
    grid_meta: dict,
    trail_path_ids: list,
    trail_nodes: dict,
) -> list:
    """
    Classifie chaque segment du chemin par type (sentier, hybride, hors-sentier, non conforme).
    Retourne une liste de segments avec type, couleur et coordonnees.
    """
    if not grid_path:
        return []

    resolution_m = grid_meta["resolution_m"]
    center_lat = grid_meta["center_lat"]
    center_lng = grid_meta["center_lng"]
    grid_size = grid_meta["grid_size"]
    half = grid_size // 2

    import math

    # Determiner si le chemin a utilise des sentiers (Phase 1)
    has_trail_phase = len(trail_path_ids) > 1

    segments = []
    current_type = None
    current_coords = []

    for gx, gy in grid_path:
        cell = grid.get((gx, gy), {})
        is_trail = cell.get("is_trail", False)
        cost = cell.get("cost", 5.0)
        canopy = cell.get("canopy", 0.5)
        slope = cell.get("slope_deg", 0)

        # Classification de la cellule
        if is_trail:
            cell_type = "trail"
        elif cost < 3.0 and canopy < 0.6:
            cell_type = "hybrid" if has_trail_phase else "off_trail_optimized"
        elif canopy > 0.8 or slope > 20:
            cell_type = "non_conformant"
        else:
            cell_type = "off_trail_optimized"

        # Convertir coordonnees grille → geo
        lat = center_lat + (gy - half) * resolution_m / 111320
        lng = center_lng + (gx - half) * resolution_m / (111320 * math.cos(math.radians(center_lat)))

        if cell_type != current_type:
            if current_coords and current_type:
                seg_info = SEGMENT_TYPES.get(current_type, SEGMENT_TYPES["non_conformant"])
                segments.append({
                    "type": current_type,
                    "color": seg_info["color"],
                    "label": seg_info["label"],
                    "style": seg_info["style"],
                    "coordinates": current_coords.copy(),
                    "distance_m": _compute_segment_distance(current_coords),
                })
            current_type = cell_type
            # Overlap avec le dernier point du segment precedent
            if current_coords:
                current_coords = [current_coords[-1], [lng, lat]]
            else:
                current_coords = [[lng, lat]]
        else:
            current_coords.append([lng, lat])

    # Dernier segment
    if current_coords and current_type:
        seg_info = SEGMENT_TYPES.get(current_type, SEGMENT_TYPES["non_conformant"])
        segments.append({
            "type": current_type,
            "color": seg_info["color"],
            "label": seg_info["label"],
            "style": seg_info["style"],
            "coordinates": current_coords,
            "distance_m": _compute_segment_distance(current_coords),
        })

    return segments


def _compute_segment_distance(coords: list) -> float:
    import math
    total = 0
    for i in range(len(coords) - 1):
        lng1, lat1 = coords[i]
        lng2, lat2 = coords[i + 1]
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
        total += 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(total, 1)
