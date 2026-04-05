"""
BDRE — BIONIC Data Reliability Engine
BCE-4X GOLDEN V6+ | Phase 1+2 Fondations + Monitoring
Directive STEEVE-MAX | 2026-04-06

Point d'entree unique du BDRE.
Expose les fonctions publiques pour tous les engines consommateurs.
"""
import logging

from .source_registry import SourceRegistry
from .quality_scorer import QualityScorer
from .audit_logger import AuditLogger
from .waterway_classifier import WaterwayClassifier
from .health_monitor import HealthMonitor
from .anomaly_detector import AnomalyDetector
from .source_selector import SourceSelector
from .fallback_chain import FallbackChain

logger = logging.getLogger("bionic.bdre")

_registry = SourceRegistry()
_scorer = QualityScorer(_registry)
_audit = AuditLogger()
_waterway = WaterwayClassifier()
_monitor = HealthMonitor(_registry)
_anomaly = AnomalyDetector(_registry, _audit)
_selector = SourceSelector(_registry, _scorer)
_chain = FallbackChain(_registry, _scorer, _audit)


def check_source(source_id: str) -> dict:
    """F1 — Verifier la sante d'une source avant acces."""
    health = _registry.get_health(source_id)
    _audit.log(engine="BDRE", source_id=source_id, action="check_source", score=health["score"])
    return health


def score_response(source_id: str, data: dict, expected_coverage: float = 0.5) -> dict:
    """F2 — Scorer la reponse d'une source apres reception."""
    quality = _scorer.score_response(source_id, data, expected_coverage)
    _audit.log(
        engine="BDRE", source_id=source_id,
        action="score_response", score=quality["score"],
        details=f"classification={quality['classification']}"
    )
    if quality["score"] < 0.40:
        _registry.update_status(source_id, "degraded")
    return quality


def alert_empty(source_id: str, details: str = "") -> None:
    """F3 — Signaler une source vide."""
    _registry.update_status(source_id, "empty")
    _audit.log(
        engine="BDRE", source_id=source_id,
        action="alert_empty", score=0.0,
        details=details or f"Source {source_id} retourne VIDE"
    )
    logger.warning(f"[BDRE] ALERTE: Source {source_id} VIDE — {details}")


def log_audit(engine: str, source_id: str, action: str, score: float,
              fallback_level: int = 0, territory: str = "", details: str = "") -> None:
    """F6 — Journaliser un evenement."""
    _audit.log(
        engine=engine, source_id=source_id,
        action=action, score=score,
        fallback_level=fallback_level,
        territory=territory, details=details
    )


def classify_waterway(tags: dict) -> dict:
    """DS-8 — Classifier un element hydrologique."""
    return _waterway.classify(tags)


def get_registry() -> SourceRegistry:
    """Acces au registre pour le router."""
    return _registry


def get_scorer() -> QualityScorer:
    """Acces au scorer pour le router."""
    return _scorer


def get_audit_logger() -> AuditLogger:
    """Acces au journal pour le router."""
    return _audit


def get_health_monitor() -> HealthMonitor:
    """Acces au moniteur de sante pour le router."""
    return _monitor


def get_anomaly_detector() -> AnomalyDetector:
    """Acces au detecteur d'anomalies pour le router."""
    return _anomaly


def get_source_selector() -> SourceSelector:
    """Acces au selecteur de source (F4)."""
    return _selector


def get_fallback_chain() -> FallbackChain:
    """Acces au pipeline hybride 4 niveaux (F5)."""
    return _chain
