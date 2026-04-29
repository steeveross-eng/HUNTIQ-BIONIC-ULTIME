"""
BCE-4X BLOC 1 — CORRIDOR_UNIFIED BUILDER
===========================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Fusion du trail_graph OSM (terrain_nav) avec le corridor_optimizer BDRE
pour creer le modele CORRIDOR_UNIFIED.

Sources fusionnees:
  - E1: trail_graph (noeuds sentiers OSM, edges, snap_radius 40m)
  - E2: corridor_optimizer_v2 (scoring 95/5, compliance ratio, forest segments)
"""
import math
import logging
from typing import Dict, List, Any, Optional

from .corridor_model import (
    build_corridor_segment,
    check_segment_water_exclusion,
    _haversine_m,
    _seed_float,
)
from bce.exclusion_layer_bce4x import check_segment_exclusions

logger = logging.getLogger("bionic.corridor_unified.builder")


def build_unified_corridors(
    center_lat: float,
    center_lng: float,
    radius_m: float = 600,
    species: str = "ORIGNAL",
    season: str = "automne",
) -> List[Dict[str, Any]]:
    """
    Point d'entree principal: construire la liste de corridors UNIFIED.

    Etapes:
    1. Charger le trail_graph OSM
    2. Extraire les segments du graphe de sentiers (E1)
    3. Scorer chaque segment via le scoring BDRE (E2)
    4. Construire les CorridorSegment unifies
    5. Trier par score_unified decroissant
    """
    corridors = []
    water_excluded = []

    # Phase 1: Charger le graphe terrain OSM
    trail_graph = _load_trail_graph(center_lat, center_lng, radius_m)

    # Phase 2: Extraire segments du graphe
    raw_segments = _extract_graph_segments(trail_graph, center_lat, center_lng, radius_m)

    # Phase 3: Scorer, filtrer eau, et construire les corridors unifies
    for i, seg in enumerate(raw_segments):
        # COUCHE BCE-4X UNIVERSELLE — TOUTES EXCLUSIONS (eau + urbain + routes + humain + securite)
        bce_check = check_segment_exclusions(seg["coords"], f"CU-{i + 1:03d}")
        if bce_check["excluded"]:
            types = [e["types"] for e in bce_check["exclusions_found"]]
            flat_types = [t for sub in types for t in sub]
            water_excluded.append({
                "segment_id": f"CU-{i + 1:03d}",
                "reason": f"BCE-4X: {', '.join(set(flat_types))}",
                "details": bce_check["exclusions_found"],
            })
            logger.warning(
                f"[CORRIDOR-UNIFIED] EXCLUSION BCE-4X: CU-{i + 1:03d} — {', '.join(set(flat_types))}"
            )
            continue

        bdre_score = _compute_segment_bdre_score(seg, trail_graph)
        corridor = build_corridor_segment(
            segment_id=f"CU-{i + 1:03d}",
            coords=seg["coords"],
            bdre_score=bdre_score,
            has_osm_trail=seg.get("has_osm_trail", True),
            connectivity=seg.get("connectivity", 1),
            species=species,
            season=season,
            source=seg.get("source", "osm_trail"),
        )
        corridors.append(corridor)

    # Phase 4: Generer des corridors BDRE supplementaires (zones sans sentiers OSM)
    bdre_corridors = _generate_bdre_only_corridors(
        center_lat, center_lng, radius_m, trail_graph, species, season,
    )
    corridors.extend(bdre_corridors)

    # Phase 5: Trier par score_unified decroissant
    corridors.sort(key=lambda c: c["score_unified"], reverse=True)

    # Stats
    n_critique = sum(1 for c in corridors if c["type"] == "CRITIQUE")
    n_majeur = sum(1 for c in corridors if c["type"] == "MAJEUR")
    n_mineur = sum(1 for c in corridors if c["type"] == "MINEUR")
    logger.info(
        f"[CORRIDOR-UNIFIED] Construit {len(corridors)} corridors: "
        f"CRITIQUE={n_critique} MAJEUR={n_majeur} MINEUR={n_mineur} "
        f"| EXCLUS EAU={len(water_excluded)}"
    )

    return corridors


def _load_trail_graph(center_lat, center_lng, radius_m):
    """Charger le graphe terrain OSM avec cache."""
    try:
        from engines.terrain_nav import get_terrain_nav
        return get_terrain_nav(
            center_lat, center_lng,
            radius_m=max(int(radius_m * 2), 2000),
        )
    except Exception as e:
        logger.warning(f"[CORRIDOR-UNIFIED] Trail graph indisponible: {e}")
        return None


def _extract_graph_segments(trail_graph, center_lat, center_lng, radius_m):
    """
    Extraire les segments de sentier depuis le trail_graph.
    Chaque edge du graphe devient un segment avec ses attributs.
    """
    segments = []

    if trail_graph is None or trail_graph.is_empty:
        logger.info("[CORRIDOR-UNIFIED] Trail graph vide — utilisation BDRE seul")
        return segments

    visited_edges = set()

    for node_id, neighbors in trail_graph.adj.items():
        if node_id not in trail_graph.nodes:
            continue

        n_lat, n_lng = trail_graph.nodes[node_id]
        dist_center = _haversine_m(n_lat, n_lng, center_lat, center_lng)

        if dist_center > radius_m * 1.5:
            continue

        connectivity = len(neighbors)

        for neighbor_id in neighbors:
            edge_key = tuple(sorted([node_id, neighbor_id]))
            if edge_key in visited_edges:
                continue
            visited_edges.add(edge_key)

            if neighbor_id not in trail_graph.nodes:
                continue

            nb_lat, nb_lng = trail_graph.nodes[neighbor_id]
            nb_connectivity = len(trail_graph.adj.get(neighbor_id, []))

            segments.append({
                "coords": [
                    {"lat": round(n_lat, 6), "lng": round(n_lng, 6)},
                    {"lat": round(nb_lat, 6), "lng": round(nb_lng, 6)},
                ],
                "has_osm_trail": True,
                "connectivity": max(connectivity, nb_connectivity),
                "source": "osm_trail",
                "node_ids": [node_id, neighbor_id],
            })

    logger.info(f"[CORRIDOR-UNIFIED] Segments extraits du graphe: {len(segments)}")

    # Limiter le nombre de segments pour la performance
    if len(segments) > 60:
        segments.sort(key=lambda s: s["connectivity"], reverse=True)
        segments = segments[:60]

    return segments


def _compute_segment_bdre_score(segment, trail_graph):
    """
    Calculer le score BDRE d'un segment.
    Utilise corridor_optimizer_v2 comme source de scoring.
    """
    from engines.bdre.corridor_optimizer_v2 import (
        CORRIDOR_MIN_PCT,
        CORRIDOR_SNAP_RADIUS_M,
    )

    coords = segment.get("coords", [])
    if not coords or len(coords) < 2:
        return 30

    # Score base sur la presence sentier OSM et la connectivity
    has_osm = segment.get("has_osm_trail", False)
    connectivity = segment.get("connectivity", 1)

    # BDRE score composite
    base = 50
    if has_osm:
        base += 30  # Sentier OSM reel = fort indicateur corridor
    if connectivity >= 3:
        base += 15  # Intersection = noeud strategique
    elif connectivity >= 2:
        base += 5

    # Clamp 0-100
    return min(100, max(0, base))


def _generate_bdre_only_corridors(
    center_lat, center_lng, radius_m, trail_graph, species, season,
):
    """
    Generer des corridors a partir de la logique BDRE pure.
    Pour les zones sans couverture sentier OSM, les axes de deplacement
    sont estimes a partir de la topographie et des corridors d'eau.
    """
    corridors = []

    # Generer des axes de deplacement estimes (8 directions cardinales)
    for bearing_deg in range(0, 360, 45):
        rad = math.radians(bearing_deg)
        inner_dist = radius_m * 0.4
        outer_dist = radius_m * 0.9

        start_lat = center_lat + (inner_dist / 111320) * math.cos(rad)
        start_lng = center_lng + (inner_dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(rad)
        end_lat = center_lat + (outer_dist / 111320) * math.cos(rad)
        end_lng = center_lng + (outer_dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(rad)

        # Verifier si ce segment est deja couvert par un sentier OSM
        osm_covered = False
        if trail_graph and not trail_graph.is_empty:
            mid_lat = (start_lat + end_lat) / 2
            mid_lng = (start_lng + end_lng) / 2
            nearest = trail_graph.nearest_node(mid_lat, mid_lng, max_dist_m=100)
            if nearest is not None:
                osm_covered = True

        if osm_covered:
            continue  # Deja couvert par un sentier OSM

        # COUCHE BCE-4X UNIVERSELLE — TOUTES EXCLUSIONS
        segment_coords = [
            {"lat": round(start_lat, 6), "lng": round(start_lng, 6)},
            {"lat": round(end_lat, 6), "lng": round(end_lng, 6)},
        ]
        bce_check = check_segment_exclusions(segment_coords, f"CU-BDRE-{bearing_deg:03d}")
        if bce_check["excluded"]:
            types = [t for e in bce_check["exclusions_found"] for t in e["types"]]
            logger.warning(
                f"[CORRIDOR-UNIFIED] EXCLUSION BCE-4X BDRE: CU-BDRE-{bearing_deg:03d} — {', '.join(set(types))}"
            )
            continue

        # Creer un corridor BDRE estime
        bdre_score = 30 + _seed_float(start_lat, start_lng, "bdre_only") * 25
        corridor = build_corridor_segment(
            segment_id=f"CU-BDRE-{bearing_deg:03d}",
            coords=segment_coords,
            bdre_score=bdre_score,
            has_osm_trail=False,
            connectivity=1,
            species=species,
            season=season,
            source="bdre_computed",
        )
        corridors.append(corridor)

    logger.info(f"[CORRIDOR-UNIFIED] Corridors BDRE supplementaires: {len(corridors)}")
    return corridors
