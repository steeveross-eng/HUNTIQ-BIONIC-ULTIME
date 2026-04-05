"""
BDRE — Health Monitor (F1)
BCE-4X GOLDEN V6+ | Phase 2
Monitoring periodique de la disponibilite et performance des APIs externes.
Maintient les metriques de sante dans le registre de sources.
"""
import logging
import time
from typing import Dict

logger = logging.getLogger("bionic.bdre.health_monitor")


class HealthMonitor:
    """
    Monitoring de sante des sources de donnees.
    Enregistre chaque check dans le registre via update_status.
    """

    def __init__(self, registry):
        self._registry = registry
        self._check_history: Dict[str, list] = {}

    def record_check(
        self,
        source_id: str,
        success: bool,
        latency_ms: float = 0.0,
        data_count: int = 0,
        details: str = "",
    ) -> dict:
        """
        Enregistrer un check de sante pour une source.
        Appele par les engines apres chaque acces source.

        Args:
            source_id: ID de la source
            success: True si l'acces a reussi
            latency_ms: Temps de reponse en ms
            data_count: Nombre d'elements retournes
            details: Informations supplementaires
        """
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if success and data_count > 0:
            status = "healthy"
        elif success and data_count == 0:
            status = "empty"
        else:
            status = "down"

        self._registry.update_status(source_id, status, latency_ms)

        entry = {
            "timestamp": now,
            "source_id": source_id,
            "success": success,
            "status": status,
            "latency_ms": round(latency_ms, 1),
            "data_count": data_count,
            "details": details,
        }

        if source_id not in self._check_history:
            self._check_history[source_id] = []
        self._check_history[source_id].append(entry)

        # Garder les 100 derniers checks par source
        if len(self._check_history[source_id]) > 100:
            self._check_history[source_id] = self._check_history[source_id][-100:]

        logger.info(
            f"[BDRE-HEALTH] {source_id}: {status} "
            f"latency={latency_ms:.0f}ms data_count={data_count} {details}"
        )

        return entry

    def get_source_history(self, source_id: str, limit: int = 20) -> list:
        """Obtenir l'historique des checks pour une source."""
        history = self._check_history.get(source_id, [])
        return list(reversed(history[-limit:]))

    def get_all_statuses(self) -> dict:
        """Statut de toutes les sources monitorees."""
        return {
            src_id: {
                "checks": len(history),
                "last": history[-1] if history else None,
            }
            for src_id, history in self._check_history.items()
        }
