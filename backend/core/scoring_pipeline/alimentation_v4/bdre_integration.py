"""
BCE-4X P0-X-5 — INTEGRATION BDRE POUR SALINES V4
===================================================
ORDONNANCE STEEVE-MAX 2026-04-06 | SUPRA VALIDE
Branche: BIONIC_REWRITE_P0

Integration des corridors BDRE dans le scoring des salines.
Source scientifique: Marchinton & Hirth 1984, Courtois et al. 2002, Beier & Noss 1998.

Le corridor BDRE est un axe de deplacement preferentiel du gibier.
Une saline pres d'un corridor sera decouverte et frequentee plus vite.
"""
import logging
import math

logger = logging.getLogger("bionic.salines_v4.bdre_integration")


def _haversine_m(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = (
        math.sin((lat2 - lat1) * p / 2) ** 2
        + math.cos(lat1 * p) * math.cos(lat2 * p)
        * math.sin((lng2 - lng1) * p / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def get_corridor_score(lat, lng, center_lat, center_lng, trail_graph):
    """
    Calcule le score corridor BDRE pour un candidat saline.

    Logique SUPRA validee:
    - Sur un corridor (noeud sentier < 50m): 100
    - < 200m d'un corridor: 80
    - 200-500m: 50
    - > 500m ou aucun corridor: 30

    Le graphe terrain_nav est utilise comme proxy des corridors BDRE.
    Les noeuds du graphe representent les points de passage sur les sentiers OSM.
    """
    if trail_graph is None or trail_graph.is_empty:
        # Fallback: estimer la distance corridor a partir de la position relative
        # Les corridors BDRE longent typiquement les cours d'eau et les vallees
        # En l'absence de donnees, score neutre
        return 50, 0, "corridor_fallback"

    # Trouver le noeud sentier le plus proche
    nearest = trail_graph.nearest_node(lat, lng, max_dist_m=1000)
    if nearest is None:
        return 30, 999, "corridor_no_data"

    n_lat, n_lng = trail_graph.nodes[nearest]
    dist = _haversine_m(lat, lng, n_lat, n_lng)

    if dist < 50:
        return 100, round(dist), "corridor_on"
    elif dist < 200:
        return 80, round(dist), "corridor_near"
    elif dist < 500:
        return 50, round(dist), "corridor_moderate"
    else:
        return 30, round(dist), "corridor_far"


def generate_corridor_candidates(center_lat, center_lng, trail_graph, max_radius_m=600):
    """
    Genere des candidats aux positions strategiques des corridors BDRE.
    Intersection corridor/lisiere = position optimale pour une saline.
    """
    candidates = []

    if trail_graph is None or trail_graph.is_empty:
        logger.info("[BDRE-V4] Trail graph vide, pas de candidats corridor")
        return candidates

    import hashlib

    for node_id, (n_lat, n_lng) in list(trail_graph.nodes.items())[:15]:
        dist_center = _haversine_m(center_lat, center_lng, n_lat, n_lng)
        if dist_center > max_radius_m or dist_center < 150:
            continue

        # Generer un candidat decale du corridor (pas directement dessus)
        h = hashlib.md5(f"{n_lat:.6f}:{n_lng:.6f}:bdre".encode()).hexdigest()
        offset_angle = (int(h[:4], 16) / 0xFFFF) * 360
        offset_dist = 50 + (int(h[4:8], 16) / 0xFFFF) * 100  # 50-150m du corridor
        rad = math.radians(offset_angle)
        c_lat = n_lat + (offset_dist / 111320) * math.cos(rad)
        c_lng = n_lng + (offset_dist / (111320 * math.cos(math.radians(n_lat)))) * math.sin(rad)

        if _haversine_m(center_lat, center_lng, c_lat, c_lng) <= max_radius_m:
            candidates.append({
                "lat": round(c_lat, 6),
                "lng": round(c_lng, 6),
                "source": "corridor_bdre",
                "corridor_distance_m": round(offset_dist),
            })

        if len(candidates) >= 4:
            break

    logger.info(f"[BDRE-V4] Corridor candidats: {len(candidates)}")
    return candidates
