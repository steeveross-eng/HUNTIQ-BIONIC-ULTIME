"""
BCE-4X Phase 2.5 — TERRAIN NAV ENGINE (TNE)
=============================================
__init__.py — Interface publique du moteur de navigation terrain

API publique:
- get_terrain_nav(lat, lng) -> TerrainGraph (cache automatique)
- navigate_terrain(graph, start, end) -> route result
- get_terrain_stats(lat, lng) -> stats du graphe

STEEVE-MAX: Ce module est le SEUL point d'entree pour le routage terrain.
Localisation protegee par ULTRA-MAX++ (File Integrity Lock).

BDRE Phase 2: Hooks pre-call, post-call, scoring et anomaly detection integres.
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple

from .terrain_sources import fetch_terrain_data
from .terrain_graph import TerrainGraph, build_terrain_graph
from .terrain_router import route_terrain

logger = logging.getLogger("bionic.terrain_nav")

# Cache global: { zone_key: TerrainGraph }
_nav_cache: Dict[str, TerrainGraph] = {}
# Cache terrain_data brut pour le routage terrain-aware
_terrain_data_cache: Dict[str, Dict] = {}


def _cache_key(lat: float, lng: float) -> str:
    # BCE-4X P0 B4: Elargi de 111m (3 decimales) a 1.1km (2 decimales) — STEEVE-MAX 2026-03-28
    return f"tne:{round(lat, 2)}:{round(lng, 2)}"


def _bdre_available() -> bool:
    """Verifier si le BDRE est disponible (import paresseux)."""
    try:
        from engines.bdre import check_source
        return True
    except Exception:
        return False


def get_terrain_nav(lat: float, lng: float, radius_m: int = 2000) -> TerrainGraph:
    """
    Obtenir le graphe de navigation terrain pour une zone.
    
    BDRE Phase 2:
    1. Verifie le cache en memoire
    2. Si absent: BDRE pre-call -> fetch Overpass -> BDRE post-call/scoring
    3. Build graphe (enrichi waterways + clearings BDRE DS-8)
    4. BDRE anomaly detection sur le graphe
    5. Cache + retourne le graphe
    """
    key = _cache_key(lat, lng)
    if key in _nav_cache:
        logger.info(f"[TNE] Cache HIT: {key}")
        return _nav_cache[key]

    logger.info(f"[TNE] Building terrain graph for ({lat:.4f}, {lng:.4f}), radius={radius_m}m")
    t0 = time.time()
    territory = f"{lat:.4f},{lng:.4f}"

    # BDRE pre-call: verifier la sante de la source
    if _bdre_available():
        try:
            from engines.bdre import check_source, score_response, log_audit
            from engines.bdre import get_audit_logger
            from engines.bdre.anomaly_detector import AnomalyDetector
            from engines.bdre.health_monitor import HealthMonitor

            pre_check = check_source("SRC-01")
            logger.info(f"[TNE-BDRE] Pre-check SRC-01: status={pre_check['status']}, score={pre_check['score']}")
        except Exception as e:
            logger.warning(f"[TNE-BDRE] Pre-check failed: {e}")

    # Fetch terrain data from Overpass (UNE SEULE FOIS)
    terrain_data = fetch_terrain_data(lat, lng, radius_m)
    fetch_ms = (time.time() - t0) * 1000

    # BDRE post-call: scorer la reponse et detecter anomalies
    if _bdre_available():
        try:
            from engines.bdre import score_response, log_audit, get_registry, get_audit_logger
            from engines.bdre.anomaly_detector import AnomalyDetector
            from engines.bdre.health_monitor import HealthMonitor

            # Health monitoring
            registry = get_registry()
            monitor = HealthMonitor(registry)
            trails = terrain_data.get("trails", {})
            trail_count = len(trails.get("ways", []))
            monitor.record_check(
                "SRC-01", success=True, latency_ms=fetch_ms,
                data_count=trail_count, details=f"radius={radius_m}m"
            )

            # Scoring
            quality = score_response("SRC-01", terrain_data)
            logger.info(
                f"[TNE-BDRE] Score SRC-01: {quality['score']:.3f} "
                f"({quality['classification']}), fallback_level={quality['fallback_level']}"
            )

            # Anomaly detection
            audit = get_audit_logger()
            detector = AnomalyDetector(registry, audit)
            anomaly_result = detector.check_terrain_data("SRC-01", terrain_data, territory)
            if not anomaly_result["is_healthy"]:
                logger.warning(
                    f"[TNE-BDRE] Anomalies detectees: {anomaly_result['anomaly_count']} "
                    f"({[a['type'] for a in anomaly_result['anomalies']]})"
                )

            log_audit(
                engine="TNE", source_id="SRC-01", action="fetch_complete",
                score=quality["score"], territory=territory,
                details=f"trails={trail_count} classification={quality['classification']}"
            )
        except Exception as e:
            logger.warning(f"[TNE-BDRE] Post-call scoring failed: {e}")

    # Build graph (enrichi avec waterways + clearings grace a BDRE DS-8)
    graph = build_terrain_graph(terrain_data)

    # BDRE: verifier la sante du graphe construit
    if _bdre_available():
        try:
            from engines.bdre import log_audit, get_registry, get_audit_logger
            from engines.bdre.anomaly_detector import AnomalyDetector

            registry = get_registry()
            audit = get_audit_logger()
            detector = AnomalyDetector(registry, audit)
            graph_check = detector.check_graph("SRC-01", graph, territory)
            if not graph_check["is_healthy"]:
                log_audit(
                    engine="TNE", source_id="SRC-01", action="graph_empty",
                    score=0.0, territory=territory,
                    details="Graphe vide apres construction"
                )
        except Exception as e:
            logger.warning(f"[TNE-BDRE] Graph check failed: {e}")

    _nav_cache[key] = graph
    _terrain_data_cache[key] = terrain_data
    return graph


def get_raw_terrain_data(lat: float, lng: float) -> Optional[Dict]:
    """
    Obtenir les donnees terrain brutes (waterways, clearings, forest, obstacles).
    Utilisees par le routage terrain-aware quand pas de sentiers formels.
    """
    key = _cache_key(lat, lng)
    return _terrain_data_cache.get(key)


def navigate_terrain(
    graph: TerrainGraph,
    start_lat: float, start_lng: float,
    end_lat: float, end_lng: float,
) -> Optional[Dict]:
    """
    Router entre deux points via le graphe terrain.
    
    Retourne:
    {
        "coords": [{"lat": ..., "lng": ...}, ...],
        "distance_m": int,
        "type": "sentier_reel",
        "segments_count": int,
        "routing_algo": str,
    }
    ou None si pas de chemin.
    """
    return route_terrain(graph, start_lat, start_lng, end_lat, end_lng)


def get_terrain_stats(lat: float, lng: float) -> Dict[str, Any]:
    """Stats du graphe terrain pour une zone (debug/audit)."""
    key = _cache_key(lat, lng)
    if key in _nav_cache:
        g = _nav_cache[key]
        return {
            "cached": True,
            "empty": g.is_empty,
            **g.stats,
        }
    return {"cached": False, "empty": True}
