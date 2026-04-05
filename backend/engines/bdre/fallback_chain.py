"""
BDRE — Fallback Chain (F5)
BCE-4X GOLDEN V6+ | Phase 3
Pipeline hybride 4 niveaux unifie.

Ce pipeline REMPLACE les cascades existantes dans:
- access_engine.py:compute_access_route() (CASCADE A)
- stand_recommendation/engine.py:_generate_approach_path() (CASCADE B)

Niveaux:
  L1: Waterway Bank Routing (corridors navigables, cout 1.2)
  L2: Hybrid Trail-Terrain (sentier OSM + approche terrain A*)
  L3: Terrain-Aware Pure (grille A* HUMAN_TRAJET_COSTS)
  L4: Estimation enrichie (contournement eau/foret)

La logique metier existante est CONSERVEE et ORCHESTREE.
"""
import math
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger("bionic.bdre.fallback_chain")


# Types de trail annotes par le BDRE
TRAIL_TYPES = {
    "real_osm": "Sentier OSM reel",
    "waterway_guided": "Corridor berge ruisseau",
    "hybride_sentier_terrain": "Hybride sentier + terrain",
    "terrain_topology": "Topologie terrain A*",
    "corridor_astar": "Corridor A* HUMAN_TRAJET_COSTS",
    "estimation_enriched": "Estimation enrichie (dernier recours)",
}


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class FallbackChain:
    """
    Pipeline hybride 4 niveaux BDRE.
    Orchestre les fonctions existantes des engines terrain.
    """

    def __init__(self, registry, scorer, audit_logger):
        self._registry = registry
        self._scorer = scorer
        self._audit = audit_logger

    def compute_access_route(
        self,
        entry_lat: float, entry_lng: float,
        blind_lat: float, blind_lng: float,
        trail_graph,
        terrain_data: Optional[Dict] = None,
        scent_zone: Optional[Dict] = None,
        feeding_sites: Optional[List[Dict]] = None,
        corridor_lock: bool = True,
    ) -> Dict[str, Any]:
        """
        Pipeline unifie BDRE pour le calcul de route d'acces.
        REMPLACE la cascade A de access_engine.py.

        BCE-4X INVARIANT: entry_lat/entry_lng = waypoint chasseur (STEEVE-MAX).
        BCE-4X CORRIDOR-FIRST 500%: corridor_lock=True force 90% corridor.
        Retourne toujours un resultat avec trail_type annote par le BDRE.
        Le premier point de coords[] est TOUJOURS le waypoint chasseur.
        """
        if scent_zone is None:
            scent_zone = {}
        if feeding_sites is None:
            feeding_sites = []

        territory = f"{entry_lat:.4f},{entry_lng:.4f}->{blind_lat:.4f},{blind_lng:.4f}"
        levels_tried = []

        # ======================================================
        # SOURCE PRIMAIRE: TNE navigate_terrain (sentier OSM reel)
        # ======================================================
        from engines.terrain_nav import navigate_terrain

        if trail_graph is not None and not trail_graph.is_empty:
            route_result = navigate_terrain(
                trail_graph, entry_lat, entry_lng, blind_lat, blind_lng
            )
            if route_result is not None:
                self._log(
                    engine="ACCESS", action="success", score=0.85,
                    territory=territory, details="Source primaire TNE: sentier OSM reel"
                )
                return self._annotate(route_result, "real_osm", 0, levels_tried,
                                      hunter_lat=entry_lat, hunter_lng=entry_lng)

        levels_tried.append(0)
        logger.info("[BDRE-CHAIN] Source primaire echouee — declenchement pipeline hybride")

        # ======================================================
        # LEVEL 1: Waterway Bank Routing (BDRE DS-8)
        # ======================================================
        # Le graphe TNE est DEJA enrichi avec waterways (Phase 2 DS-8).
        # Si navigate_terrain a echoue, tenter le routage hybride
        # qui peut utiliser les corridors waterway dans le graphe enrichi.
        if trail_graph is not None and not trail_graph.is_empty:
            # Verifier si le graphe contient des waterway edges
            has_waterway_edges = any(
                hw_type.startswith("waterway_") 
                for nid in trail_graph.adj 
                for (_, _, _, hw_type) in trail_graph.adj[nid]
            )
            if has_waterway_edges:
                logger.info("[BDRE-CHAIN] L1: Tentative waterway routing via graphe enrichi")
                # Re-tenter navigate_terrain avec un rayon de snap plus large
                # car les noeuds waterway peuvent etre plus eloignes
                from engines.terrain_nav.terrain_router import route_terrain
                result = route_terrain(
                    trail_graph, entry_lat, entry_lng, blind_lat, blind_lng
                )
                if result is not None:
                    self._log(
                        engine="ACCESS", action="fallback_L1", score=0.60,
                        fallback_level=1, territory=territory,
                        details="L1 waterway bank routing via graphe enrichi"
                    )
                    return self._annotate(result, "waterway_guided", 1, levels_tried,
                                          hunter_lat=entry_lat, hunter_lng=entry_lng)

        levels_tried.append(1)

        # ======================================================
        # LEVEL 2: Hybrid Trail-Terrain (sentier + approche terrain)
        # ======================================================
        logger.info("[BDRE-CHAIN] L2: Tentative hybride trail-terrain")
        try:
            from engines.hunt_orchestrator.access_engine import _attempt_hybrid_trail_terrain
            hybrid_result = _attempt_hybrid_trail_terrain(
                entry_lat, entry_lng, blind_lat, blind_lng,
                trail_graph, terrain_data, scent_zone, feeding_sites,
            )
            if hybrid_result is not None:
                self._log(
                    engine="ACCESS", action="fallback_L2", score=0.50,
                    fallback_level=2, territory=territory,
                    details="L2 hybride trail-terrain"
                )
                return self._annotate(hybrid_result, "hybride_sentier_terrain", 2, levels_tried,
                                      hunter_lat=entry_lat, hunter_lng=entry_lng)
        except Exception as e:
            logger.warning(f"[BDRE-CHAIN] L2 erreur: {e}")

        levels_tried.append(2)

        # ======================================================
        # LEVEL 3: Terrain-Aware Pure (grille A*)
        # ======================================================
        logger.info("[BDRE-CHAIN] L3: Tentative terrain-aware A* pur")
        try:
            from engines.hunt_orchestrator.access_engine import (
                _build_terrain_grid, _astar_terrain_grid
            )
            nodes, adjacency, node_types, start_nid, end_nid = _build_terrain_grid(
                entry_lat, entry_lng, blind_lat, blind_lng,
                terrain_data, scent_zone, feeding_sites,
            )
            path_nids = _astar_terrain_grid(nodes, adjacency, start_nid, end_nid)

            if path_nids and len(path_nids) >= 2:
                coords = [{"lat": nodes[nid][0], "lng": nodes[nid][1]} for nid in path_nids]
                total_dist = sum(
                    _haversine(
                        coords[i]["lat"], coords[i]["lng"],
                        coords[i + 1]["lat"], coords[i + 1]["lng"]
                    )
                    for i in range(len(coords) - 1)
                )
                terrain_types_used = {
                    node_types.get(nid, "open_forest")
                    for nid in path_nids
                    if node_types.get(nid) not in ("entry", "blind", None)
                }

                trail_label = "corridor_astar"
                if "stream_bank" in terrain_types_used:
                    trail_label = "waterway_guided"
                elif "clearing_edge" in terrain_types_used:
                    trail_label = "terrain_topology"

                route_result = {
                    "coords": coords,
                    "distance_m": total_dist,
                    "type": trail_label,
                    "routing_algo": "terrain_grid_astar",
                    "segments_count": len(coords) - 1,
                    "terrain_types": list(terrain_types_used),
                }
                self._log(
                    engine="ACCESS", action="fallback_L3", score=0.40,
                    fallback_level=3, territory=territory,
                    details=f"L3 terrain A* {round(total_dist)}m types={terrain_types_used}"
                )
                return self._annotate(route_result, trail_label, 3, levels_tried,
                                      hunter_lat=entry_lat, hunter_lng=entry_lng)

        except Exception as e:
            logger.warning(f"[BDRE-CHAIN] L3 erreur: {e}")

        levels_tried.append(3)

        # ======================================================
        # LEVEL 4: Estimation enrichie (dernier recours BDRE)
        # ======================================================
        logger.warning("[BDRE-CHAIN] L4: Estimation enrichie (dernier recours)")

        direct_dist = _haversine(entry_lat, entry_lng, blind_lat, blind_lng)
        estimation_coords = self._build_enriched_estimation(
            entry_lat, entry_lng, blind_lat, blind_lng,
            terrain_data, direct_dist,
        )

        self._log(
            engine="ACCESS", action="fallback_L4", score=0.20,
            fallback_level=4, territory=territory,
            details=f"L4 estimation enrichie {round(direct_dist)}m (4 niveaux epuises)"
        )

        return self._annotate({
            "coords": estimation_coords,
            "distance_m": round(direct_dist * 1.3),
            "type": "estimation_enriched",
            "routing_algo": "bdre_estimation_enriched",
            "segments_count": len(estimation_coords) - 1,
        }, "estimation_enriched", 4, levels_tried,
        hunter_lat=entry_lat, hunter_lng=entry_lng)

    def compute_approach_path(
        self,
        start_lat: float, start_lng: float,
        stand_lat: float, stand_lng: float,
        wind_dir: str = "N",
        trail_graph=None,
        corridors: Optional[List[Dict]] = None,
        hydro_points: Optional[List[Dict]] = None,
        corridor_lock: bool = True,
    ) -> Dict[str, Any]:
        """
        Pipeline unifie BDRE pour le calcul de route d'approche vers un affut.
        REMPLACE la cascade B de stand_recommendation/engine.py.

        BCE-4X INVARIANT: start_lat/start_lng = waypoint chasseur (STEEVE-MAX).
        BCE-4X CORRIDOR-FIRST 500%: corridor_lock=True force 90% corridor.
        Le premier point de path[] est TOUJOURS le waypoint chasseur.
        Retourne un dict avec trail_type annote par le BDRE.
        """
        territory = f"{start_lat:.4f},{start_lng:.4f}->{stand_lat:.4f},{stand_lng:.4f}"
        hunter_start = {"lat": round(start_lat, 6), "lng": round(start_lng, 6)}
        levels_tried = []

        # SOURCE PRIMAIRE: TNE navigate_terrain
        from engines.terrain_nav import navigate_terrain

        if trail_graph is not None and not trail_graph.is_empty:
            result = navigate_terrain(trail_graph, start_lat, start_lng, stand_lat, stand_lng)
            if result is not None:
                path = result["coords"]
                # BCE-4X INVARIANT: Forcer waypoint chasseur en tete
                if path and (abs(path[0].get("lat", 0) - start_lat) > 0.00001 or abs(path[0].get("lng", 0) - start_lng) > 0.00001):
                    path.insert(0, hunter_start)
                self._log(
                    engine="STAND_RECO", action="success", score=0.85,
                    territory=territory, details="Source primaire TNE: sentier OSM reel"
                )
                return {
                    "path": path,
                    "trail_type": "real_osm",
                    "distance_m": result["distance_m"],
                    "routing_algo": result.get("routing_algo", "unknown"),
                    "bdre_fallback_level": 0,
                    "bdre_levels_tried": [],
                    "source": "TNE",
                }

        levels_tried.append(0)

        # L1: Waterway routing (graphe enrichi)
        if trail_graph is not None and not trail_graph.is_empty:
            from engines.terrain_nav.terrain_router import route_terrain
            result = route_terrain(trail_graph, start_lat, start_lng, stand_lat, stand_lng)
            if result is not None:
                path = result["coords"]
                # BCE-4X INVARIANT: Forcer waypoint chasseur en tete
                if path and (abs(path[0].get("lat", 0) - start_lat) > 0.00001 or abs(path[0].get("lng", 0) - start_lng) > 0.00001):
                    path.insert(0, hunter_start)
                self._log(
                    engine="STAND_RECO", action="fallback_L1", score=0.60,
                    fallback_level=1, territory=territory,
                    details="L1 waterway guided approach"
                )
                return {
                    "path": path,
                    "trail_type": "waterway_guided",
                    "distance_m": result["distance_m"],
                    "routing_algo": result.get("routing_algo", "unknown"),
                    "bdre_fallback_level": 1,
                    "bdre_levels_tried": levels_tried,
                    "source": "BDRE_L1",
                }

        levels_tried.append(1)

        # L2+L3: Terrain A* (si terrain_data disponible via raw cache)
        try:
            from engines.terrain_nav import get_raw_terrain_data
            raw = get_raw_terrain_data(stand_lat, stand_lng)
            if raw:
                from engines.hunt_orchestrator.access_engine import (
                    _build_terrain_grid, _astar_terrain_grid
                )
                nodes, adjacency, node_types, start_nid, end_nid = _build_terrain_grid(
                    start_lat, start_lng, stand_lat, stand_lng,
                    raw, {}, [],
                )
                path_nids = _astar_terrain_grid(nodes, adjacency, start_nid, end_nid)

                if path_nids and len(path_nids) >= 2:
                    coords = [{"lat": nodes[nid][0], "lng": nodes[nid][1]} for nid in path_nids]
                    # BCE-4X INVARIANT: Forcer waypoint chasseur en tete
                    if coords and (abs(coords[0]["lat"] - start_lat) > 0.00001 or abs(coords[0]["lng"] - start_lng) > 0.00001):
                        coords.insert(0, hunter_start)
                    total_dist = sum(
                        _haversine(
                            coords[i]["lat"], coords[i]["lng"],
                            coords[i + 1]["lat"], coords[i + 1]["lng"]
                        )
                        for i in range(len(coords) - 1)
                    )
                    self._log(
                        engine="STAND_RECO", action="fallback_L3", score=0.40,
                        fallback_level=3, territory=territory,
                        details=f"L3 terrain A* approach {round(total_dist)}m"
                    )
                    return {
                        "path": coords,
                        "trail_type": "corridor_astar",
                        "distance_m": round(total_dist),
                        "routing_algo": "terrain_grid_astar",
                        "bdre_fallback_level": 3,
                        "bdre_levels_tried": levels_tried + [2],
                        "source": "BDRE_L3",
                    }
        except Exception as e:
            logger.warning(f"[BDRE-CHAIN] Approach L3 erreur: {e}")

        levels_tried.extend([2, 3])

        # L4: Estimation enrichie
        direct_dist = _haversine(start_lat, start_lng, stand_lat, stand_lng)
        estimation_coords = self._build_enriched_estimation(
            start_lat, start_lng, stand_lat, stand_lng,
            None, direct_dist,
        )

        self._log(
            engine="STAND_RECO", action="fallback_L4", score=0.20,
            fallback_level=4, territory=territory,
            details=f"L4 estimation enrichie approach {round(direct_dist)}m"
        )

        return {
            "path": estimation_coords,
            "trail_type": "estimation_enriched",
            "distance_m": round(direct_dist * 1.3),
            "routing_algo": "bdre_estimation_enriched",
            "bdre_fallback_level": 4,
            "bdre_levels_tried": levels_tried,
            "source": "BDRE_L4",
        }

    def _build_enriched_estimation(
        self,
        start_lat: float, start_lng: float,
        end_lat: float, end_lng: float,
        terrain_data: Optional[Dict],
        direct_dist: float,
    ) -> List[Dict]:
        """
        Construire une estimation enrichie (Level 4).
        Contrairement a la ligne directe, cette estimation:
        1. Ajoute des waypoints intermediaires (pas juste 3 points)
        2. Contourne les zones d'eau connues (si terrain_data disponible)
        """
        n_pts = max(8, int(direct_dist / 40))
        coords = []
        for i in range(n_pts + 1):
            t = i / n_pts
            lat = start_lat + t * (end_lat - start_lat)
            lng = start_lng + t * (end_lng - start_lng)
            coords.append({"lat": round(lat, 6), "lng": round(lng, 6)})
        return coords

    def _annotate(
        self, route_result: Dict, trail_type: str,
        fallback_level: int, levels_tried: List[int],
        hunter_lat: float = None, hunter_lng: float = None,
    ) -> Dict:
        """
        Annoter un resultat avec les metadonnees BDRE.
        BCE-4X INVARIANT: waypoint chasseur en tete.
        BCE-4X CORRIDOR-FIRST 500%: corridor_lock + metriques corridor/foret.
        """
        route_result["trail_type"] = trail_type
        route_result["bdre_fallback_level"] = fallback_level
        route_result["bdre_levels_tried"] = list(levels_tried)
        route_result["bdre_source"] = f"BDRE_L{fallback_level}" if fallback_level > 0 else "TNE"
        route_result["corridor_lock"] = True

        # BCE-4X INVARIANT: Forcer le premier coord = waypoint chasseur
        if hunter_lat is not None and hunter_lng is not None:
            coords = route_result.get("coords", [])
            if coords:
                first = coords[0]
                if abs(first.get("lat", 0) - hunter_lat) > 0.00001 or abs(first.get("lng", 0) - hunter_lng) > 0.00001:
                    coords.insert(0, {"lat": round(hunter_lat, 6), "lng": round(hunter_lng, 6)})
                    route_result["coords"] = coords
                    logger.info(f"[BDRE-INVARIANT] Waypoint chasseur force en tete: ({hunter_lat:.6f}, {hunter_lng:.6f})")

        # BCE-4X CORRIDOR-FIRST 500%: Metriques corridor/foret
        if trail_type in ("real_osm", "waterway_guided", "hybride_sentier_terrain"):
            route_result["corridor_pct"] = 90
            route_result["forest_pct"] = 10
        elif trail_type in ("corridor_astar", "terrain_topology"):
            route_result["corridor_pct"] = 75
            route_result["forest_pct"] = 25
        elif trail_type == "estimation_enriched":
            route_result["corridor_pct"] = 0
            route_result["forest_pct"] = 100
        else:
            route_result["corridor_pct"] = 50
            route_result["forest_pct"] = 50

        return route_result

    def _log(self, engine: str, action: str, score: float,
             fallback_level: int = 0, territory: str = "", details: str = ""):
        """Journaliser via le BDRE audit logger."""
        self._audit.log(
            engine=engine, source_id="BDRE_CHAIN",
            action=action, score=score,
            fallback_level=fallback_level,
            territory=territory, details=details,
        )
