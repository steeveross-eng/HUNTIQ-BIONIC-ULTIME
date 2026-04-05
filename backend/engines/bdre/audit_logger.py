"""
BDRE — Audit Logger (F6)
BCE-4X GOLDEN V6+ | Phase 1
Journalisation institutionnelle permanente.
Journal rotatif en memoire (1000 entrees max).
Conforme au DC-BDRE-04 AuditLogContract.
"""
import logging
import time
from collections import deque
from typing import List, Optional

logger = logging.getLogger("bionic.bdre.audit")

MAX_LOG_ENTRIES = 1000
MAX_FALLBACK_ENTRIES = 100


class AuditLogger:
    """
    Journal d'audit BDRE conforme DC-BDRE-04.
    Stockage en memoire avec rotation automatique.
    """

    def __init__(self):
        self._logs: deque = deque(maxlen=MAX_LOG_ENTRIES)
        self._fallbacks: deque = deque(maxlen=MAX_FALLBACK_ENTRIES)
        self._stats = {
            "total_entries": 0,
            "total_fallbacks": 0,
            "total_alerts": 0,
            "total_empty": 0,
        }
        logger.info("[BDRE-AUDIT] Journal initialise (rotatif 1000 entrees)")

    def log(
        self,
        engine: str,
        source_id: str,
        action: str,
        score: float,
        fallback_level: int = 0,
        territory: str = "",
        details: str = "",
    ) -> None:
        """
        Enregistrer un evenement dans le journal d'audit.
        Conforme DC-BDRE-04 AuditLogContract.
        """
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "engine": engine,
            "source_id": source_id,
            "action": action,
            "score": round(score, 4),
            "fallback_level": fallback_level,
            "territory": territory,
            "details": details,
        }
        self._logs.append(entry)
        self._stats["total_entries"] += 1

        if action == "alert_empty" or action == "empty":
            self._stats["total_empty"] += 1
        if fallback_level > 0:
            self._fallbacks.append(entry)
            self._stats["total_fallbacks"] += 1
        if "alert" in action.lower():
            self._stats["total_alerts"] += 1

        log_level = logging.WARNING if fallback_level > 0 or "alert" in action else logging.INFO
        logger.log(
            log_level,
            f"[BDRE-AUDIT] {engine}/{source_id}: {action} "
            f"score={score:.3f} fallback={fallback_level} {details}"
        )

    def get_logs(self, limit: int = 50, offset: int = 0, engine: Optional[str] = None) -> dict:
        """Obtenir les entrees du journal (pagine)."""
        all_logs = list(self._logs)
        all_logs.reverse()

        if engine:
            all_logs = [e for e in all_logs if e["engine"] == engine]

        total = len(all_logs)
        page = all_logs[offset:offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "entries": page,
        }

    def get_recent_fallbacks(self, limit: int = 20) -> list:
        """Obtenir les derniers fallbacks declenches."""
        fallbacks = list(self._fallbacks)
        fallbacks.reverse()
        return fallbacks[:limit]

    def get_stats(self) -> dict:
        """Statistiques du journal."""
        return {
            **self._stats,
            "buffer_size": len(self._logs),
            "buffer_max": MAX_LOG_ENTRIES,
            "fallback_buffer_size": len(self._fallbacks),
        }
