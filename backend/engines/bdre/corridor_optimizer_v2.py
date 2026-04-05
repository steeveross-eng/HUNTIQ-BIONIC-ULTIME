"""
corridor_optimizer_v2.py — CORRIDOR-FIRST X1 000 000%
BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

Module d'optimisation post-route qui verifie et corrige la conformite
CORRIDOR-FIRST: 95% corridor / 5% foret max.

Fonctions:
- analyze_corridor_ratio: Calcule le % corridor vs foret d'un trajet
- enforce_corridor_lock: Verifie la contrainte 95/5 et annote
- select_shortest_corridor: Selectionne le corridor le plus court parmi alternatives
"""

import logging
import math
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance haversine en metres."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def analyze_corridor_ratio(coords: List[Dict], trail_graph=None) -> Dict[str, Any]:
    """
    Analyser le ratio corridor/foret d'un trajet.

    Retourne:
    - total_distance_m: distance totale
    - corridor_distance_m: distance sur corridor
    - forest_distance_m: distance en foret
    - corridor_pct: % corridor
    - forest_pct: % foret
    - max_forest_segment_m: plus long segment en foret
    - compliant: True si corridor_pct >= 95 et forest_pct <= 5
    """
    if not coords or len(coords) < 2:
        return {
            "total_distance_m": 0,
            "corridor_distance_m": 0,
            "forest_distance_m": 0,
            "corridor_pct": 0,
            "forest_pct": 100,
            "max_forest_segment_m": 0,
            "compliant": False,
        }

    total_dist = 0.0
    corridor_dist = 0.0
    forest_dist = 0.0
    max_forest_seg = 0.0

    for i in range(len(coords) - 1):
        seg_dist = _haversine(
            coords[i]["lat"], coords[i]["lng"],
            coords[i + 1]["lat"], coords[i + 1]["lng"],
        )
        total_dist += seg_dist

        # Determiner si ce segment est sur un corridor
        is_corridor = False
        if trail_graph is not None and hasattr(trail_graph, "nearest_node"):
            mid_lat = (coords[i]["lat"] + coords[i + 1]["lat"]) / 2
            mid_lng = (coords[i]["lng"] + coords[i + 1]["lng"]) / 2
            nearest = trail_graph.nearest_node(mid_lat, mid_lng, max_dist_m=50)
            if nearest is not None:
                is_corridor = True
        else:
            # Heuristique: segments courts (<80m) entre points annotes
            # sont probablement sur corridor
            if seg_dist < 80:
                is_corridor = True

        if is_corridor:
            corridor_dist += seg_dist
        else:
            forest_dist += seg_dist
            max_forest_seg = max(max_forest_seg, seg_dist)

    corridor_pct = (corridor_dist / total_dist * 100) if total_dist > 0 else 0
    forest_pct = (forest_dist / total_dist * 100) if total_dist > 0 else 0

    return {
        "total_distance_m": round(total_dist),
        "corridor_distance_m": round(corridor_dist),
        "forest_distance_m": round(forest_dist),
        "corridor_pct": round(corridor_pct, 1),
        "forest_pct": round(forest_pct, 1),
        "max_forest_segment_m": round(max_forest_seg),
        "compliant": corridor_pct >= 95 and forest_pct <= 5,
    }


def enforce_corridor_lock(
    route_result: Dict,
    trail_graph=None,
    threshold_corridor_pct: float = 95.0,
    threshold_forest_pct: float = 5.0,
) -> Dict:
    """
    Verifier et annoter la conformite CORRIDOR-FIRST X1 000 000%.

    BCE-4X: Si le trajet ne respecte pas 95/5, log un avertissement
    mais retourne quand meme le trajet (le pathfinder doit faire mieux,
    pas le post-processeur).
    """
    coords = route_result.get("coords", route_result.get("path", []))
    analysis = analyze_corridor_ratio(coords, trail_graph)

    route_result["corridor_analysis"] = analysis
    route_result["corridor_pct"] = analysis["corridor_pct"]
    route_result["forest_pct"] = analysis["forest_pct"]
    route_result["corridor_compliant"] = analysis["compliant"]
    route_result["corridor_lock"] = True

    if not analysis["compliant"]:
        logger.warning(
            f"[CORRIDOR-FIRST] NON CONFORME: "
            f"corridor={analysis['corridor_pct']:.1f}% "
            f"(requis>={threshold_corridor_pct}%), "
            f"foret={analysis['forest_pct']:.1f}% "
            f"(max={threshold_forest_pct}%), "
            f"max_seg_foret={analysis['max_forest_segment_m']}m"
        )
    else:
        logger.info(
            f"[CORRIDOR-FIRST] CONFORME: "
            f"corridor={analysis['corridor_pct']:.1f}%, "
            f"foret={analysis['forest_pct']:.1f}%"
        )

    return route_result


def select_shortest_corridor(
    alternatives: List[Dict],
    trail_graph=None,
) -> Optional[Dict]:
    """
    Parmi une liste de routes alternatives, selectionner celle qui:
    1. Respecte CORRIDOR-FIRST (95/5) ET est la plus courte
    2. Si aucune n'est conforme, prendre la plus courte quand meme

    BCE-4X: Selection automatique du corridor le plus court.
    """
    if not alternatives:
        return None

    # Annoter toutes les alternatives
    for alt in alternatives:
        enforce_corridor_lock(alt, trail_graph)

    # Trier: conformes d'abord, puis par distance
    conformes = [a for a in alternatives if a.get("corridor_compliant")]
    if conformes:
        return min(conformes, key=lambda a: a.get("distance_m", float("inf")))

    # Aucune conforme: prendre la plus courte
    return min(alternatives, key=lambda a: a.get("distance_m", float("inf")))
