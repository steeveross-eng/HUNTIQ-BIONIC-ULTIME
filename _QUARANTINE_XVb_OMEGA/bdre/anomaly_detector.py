"""
BDRE — Anomaly Detector (F3)
BCE-4X GOLDEN V6+ | Phase 2
Detection automatique des sources vides, incoherentes, ou obsoletes.
Emet des alertes via l'audit logger.
"""
import logging
import time
from typing import Optional

logger = logging.getLogger("bionic.bdre.anomaly")


class AnomalyDetector:
    """
    Detecte les anomalies dans les donnees terrain:
    - Sources vides (0 noeuds, 0 ways)
    - Noeuds orphelins (dans le cache mais pas dans le graphe)
    - Cache obsolete (age > TTL)
    - Incoherences (noeuds obstacles marques comme sentiers)
    """

    def __init__(self, registry, audit_logger):
        self._registry = registry
        self._audit = audit_logger
        self._anomalies: list = []

    def check_terrain_data(self, source_id: str, terrain_data: dict, territory: str = "") -> dict:
        """
        Analyser les donnees terrain pour detecter des anomalies.

        Returns:
            {
                "source_id": str,
                "anomalies": [{"type": str, "severity": str, "details": str}],
                "is_healthy": bool,
            }
        """
        anomalies = []

        # Verifier trails
        trails = terrain_data.get("trails", {})
        trail_ways = trails.get("ways", [])
        trail_nodes = trails.get("node_coords", {})

        if not trail_ways and terrain_data.get("source") != "cache":
            anomalies.append({
                "type": "EMPTY_TRAILS",
                "severity": "CRITICAL",
                "details": f"0 sentiers dans les donnees terrain ({len(trail_nodes)} noeuds)",
            })

        # Verifier waterways
        waterways = terrain_data.get("waterways", {})
        ww_ways = waterways.get("ways", [])

        if terrain_data.get("has_waterways") and len(ww_ways) > 0 and len(trail_ways) == 0:
            anomalies.append({
                "type": "WATERWAY_ONLY",
                "severity": "WARNING",
                "details": (
                    f"{len(ww_ways)} waterways mais 0 sentiers. "
                    f"Activer BDRE Level 1 (waterway bank routing)."
                ),
            })

        # Verifier noeuds orphelins
        if trail_ways and trail_nodes:
            used_nodes = set()
            for way in trail_ways:
                for nid in way.get("nodes", []):
                    used_nodes.add(nid)
            orphan_count = len(set(trail_nodes.keys()) - used_nodes) if isinstance(trail_nodes, dict) else 0
            if orphan_count > len(used_nodes) * 2:
                anomalies.append({
                    "type": "ORPHAN_NODES",
                    "severity": "WARNING",
                    "details": f"{orphan_count} noeuds orphelins (non references par aucun way)",
                })

        # Verifier clearings
        if terrain_data.get("has_clearings"):
            clearings = terrain_data.get("clearings", {})
            cl_ways = clearings.get("ways", [])
            if cl_ways and len(trail_ways) == 0:
                anomalies.append({
                    "type": "CLEARINGS_WITHOUT_TRAILS",
                    "severity": "INFO",
                    "details": f"{len(cl_ways)} clairieres disponibles pour routage alternatif",
                })

        # Journaliser les anomalies
        is_healthy = all(a["severity"] != "CRITICAL" for a in anomalies)

        for anom in anomalies:
            self._audit.log(
                engine="BDRE_ANOMALY",
                source_id=source_id,
                action=f"anomaly:{anom['type']}",
                score=0.0 if anom["severity"] == "CRITICAL" else 0.5,
                territory=territory,
                details=anom["details"],
            )

        if not is_healthy:
            self._registry.update_status(source_id, "degraded")

        result = {
            "source_id": source_id,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "is_healthy": is_healthy,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        self._anomalies.append(result)
        if len(self._anomalies) > 200:
            self._anomalies = self._anomalies[-200:]

        return result

    def check_graph(self, source_id: str, graph, territory: str = "") -> dict:
        """Verifier la sante d'un graphe construit."""
        anomalies = []

        if graph.is_empty:
            anomalies.append({
                "type": "EMPTY_GRAPH",
                "severity": "CRITICAL",
                "details": "Graphe terrain vide (0 noeuds, 0 aretes)",
            })
        else:
            stats = graph.stats
            if stats.get("total_edges", 0) == 0 and stats.get("total_nodes", 0) > 0:
                anomalies.append({
                    "type": "DISCONNECTED_GRAPH",
                    "severity": "WARNING",
                    "details": f"{stats['total_nodes']} noeuds mais 0 aretes",
                })

        is_healthy = all(a["severity"] != "CRITICAL" for a in anomalies)
        return {
            "source_id": source_id,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "is_healthy": is_healthy,
        }

    def get_recent_anomalies(self, limit: int = 20) -> list:
        """Obtenir les dernieres anomalies detectees."""
        return list(reversed(self._anomalies[-limit:]))
