"""
BDRE — Router (8 endpoints)
BCE-4X GOLDEN V6+ | Phase 1
PREFIX: /api/v1/bdre

Endpoints:
  0. /health           GET   Sante du BDRE
  1. /sources          GET   Registre complet des sources
  2. /sources/{id}/health  GET   Sante d'une source specifique
  3. /sources/{id}/score   GET   Score de fiabilite
  4. /quality/report   GET   Rapport qualite global
  5. /fallbacks/recent GET   Derniers fallbacks declenches
  6. /audit/log        GET   Journal d'audit (pagine)
  7. /validate/{territory_id}  POST  Validation BDRE d'un territoire
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger("bionic.bdre.router")

router = APIRouter(prefix="/api/v1/bdre", tags=["bdre"])


def _get_bdre():
    """Import paresseux pour eviter les imports circulaires."""
    from engines.bdre import get_registry, get_scorer, get_audit_logger
    return get_registry(), get_scorer(), get_audit_logger()


# =====================================================================
# ENDPOINT 0: HEALTH
# =====================================================================

@router.get("/health", tags=["bdre"])
async def bdre_health():
    """Sante du BDRE."""
    registry, scorer, audit = _get_bdre()
    stats = audit.get_stats()
    return {
        "status": "operational",
        "module": "bdre",
        "version": "V2",
        "protocol": "BCE-4X GOLDEN V6+",
        "phase": "Phase 4 — Institutionnalisation BDRE",
        "endpoints": 11,
        "components": [
            "source_registry",
            "quality_scorer",
            "waterway_classifier",
            "audit_logger",
            "health_monitor",
            "anomaly_detector",
            "source_selector",
            "fallback_chain",
        ],
        "sources_registered": len(registry.get_all_sources()),
        "audit_stats": stats,
    }


# =====================================================================
# ENDPOINT 1: SOURCES (registre complet)
# =====================================================================

@router.get("/sources", tags=["bdre"])
async def get_sources(
    category: Optional[str] = Query(None, description="Filtrer par type: external, internal"),
):
    """Registre complet des sources."""
    registry, _, _ = _get_bdre()

    if category == "external":
        sources = registry.get_external_sources()
    elif category == "internal":
        sources = registry.get_internal_sources()
    else:
        sources = registry.get_all_sources()

    return {
        "total": len(sources),
        "category": category or "all",
        "sources": sources,
    }


# =====================================================================
# ENDPOINT 2: SOURCE HEALTH
# =====================================================================

@router.get("/sources/{source_id}/health", tags=["bdre"])
async def get_source_health(source_id: str):
    """Sante d'une source specifique (DC-BDRE-01)."""
    registry, _, _ = _get_bdre()
    health = registry.get_health(source_id)
    if health["status"] == "unknown":
        raise HTTPException(status_code=404, detail=f"Source {source_id} inconnue")
    return health


# =====================================================================
# ENDPOINT 3: SOURCE SCORE
# =====================================================================

@router.get("/sources/{source_id}/score", tags=["bdre"])
async def get_source_score(source_id: str):
    """Score de fiabilite d'une source (DC-BDRE-02)."""
    _, scorer, _ = _get_bdre()
    last = scorer.get_last_score(source_id)
    if last is None:
        registry, _, _ = _get_bdre()
        health = registry.get_health(source_id)
        if health["status"] == "unknown":
            raise HTTPException(status_code=404, detail=f"Source {source_id} inconnue")
        return {
            "source_id": source_id,
            "score": health["score"],
            "classification": "NON EVALUE",
            "message": "Aucun scoring effectue. Le score sera calcule lors du prochain acces a la source.",
        }
    return last


# =====================================================================
# ENDPOINT 4: QUALITY REPORT
# =====================================================================

@router.get("/quality/report", tags=["bdre"])
async def get_quality_report():
    """Rapport qualite global de toutes les sources scorees."""
    _, scorer, _ = _get_bdre()
    return scorer.get_quality_report()


# =====================================================================
# ENDPOINT 5: RECENT FALLBACKS
# =====================================================================

@router.get("/fallbacks/recent", tags=["bdre"])
async def get_recent_fallbacks(
    limit: int = Query(20, ge=1, le=100),
):
    """Derniers fallbacks declenches (DC-BDRE-03)."""
    _, _, audit = _get_bdre()
    fallbacks = audit.get_recent_fallbacks(limit=limit)
    return {
        "total": len(fallbacks),
        "limit": limit,
        "fallbacks": fallbacks,
    }


# =====================================================================
# ENDPOINT 6: AUDIT LOG
# =====================================================================

@router.get("/audit/log", tags=["bdre"])
async def get_audit_log(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    engine: Optional[str] = Query(None, description="Filtrer par engine"),
):
    """Journal d'audit BDRE (pagine, DC-BDRE-04)."""
    _, _, audit = _get_bdre()
    return audit.get_logs(limit=limit, offset=offset, engine=engine)


# =====================================================================
# ENDPOINT 7: VALIDATE TERRITORY
# =====================================================================

@router.post("/validate/{territory_id}", tags=["bdre"])
async def validate_territory(territory_id: str):
    """
    Validation BDRE d'un territoire.
    Verifie la fiabilite de toutes les sources pour un territoire donne.
    Retourne le score global et les recommandations.
    """
    registry, scorer, audit = _get_bdre()
    from engines.bdre import log_audit

    terrain_sources = ["SRC-01", "SRC-02", "SRC-03"]
    results = []
    min_score = 1.0

    for src_id in terrain_sources:
        health = registry.get_health(src_id)
        results.append({
            "source_id": src_id,
            "name": health.get("name", src_id),
            "status": health["status"],
            "score": health["score"],
        })
        if health["score"] < min_score:
            min_score = health["score"]

    # Determiner le niveau de fallback requis
    if min_score >= 0.60:
        recommendation = "SOURCE_PRIMAIRE"
        fallback = 0
    elif min_score >= 0.40:
        recommendation = "FALLBACK_LEVEL_1_WATERWAY"
        fallback = 1
    elif min_score >= 0.20:
        recommendation = "FALLBACK_LEVEL_2_TERRAIN"
        fallback = 2
    elif min_score > 0.0:
        recommendation = "FALLBACK_LEVEL_3_CORRIDOR_ASTAR"
        fallback = 3
    else:
        recommendation = "FALLBACK_LEVEL_4_GPS_ESTIMATION"
        fallback = 4

    log_audit(
        engine="BDRE", source_id="TERRITORY",
        action="validate_territory", score=min_score,
        fallback_level=fallback, territory=territory_id,
        details=f"recommendation={recommendation}"
    )

    return {
        "territory_id": territory_id,
        "sources_checked": results,
        "min_score": round(min_score, 4),
        "recommendation": recommendation,
        "fallback_level": fallback,
        "message": (
            f"Territoire {territory_id}: score minimal {min_score:.3f}. "
            f"Recommendation: {recommendation}."
        ),
    }


# =====================================================================
# ENDPOINT 8: HEALTH MONITOR STATUS (Phase 2)
# =====================================================================

@router.get("/monitor/status", tags=["bdre"])
async def get_monitor_status():
    """Statut du monitoring de sante de toutes les sources."""
    from engines.bdre import get_health_monitor
    monitor = get_health_monitor()
    return {
        "monitor": "active",
        "sources": monitor.get_all_statuses(),
    }


# =====================================================================
# ENDPOINT 9: ANOMALIES (Phase 2)
# =====================================================================

@router.get("/anomalies/recent", tags=["bdre"])
async def get_recent_anomalies(
    limit: int = Query(20, ge=1, le=100),
):
    """Dernieres anomalies detectees par le BDRE."""
    from engines.bdre import get_anomaly_detector
    detector = get_anomaly_detector()
    anomalies = detector.get_recent_anomalies(limit=limit)
    return {
        "total": len(anomalies),
        "limit": limit,
        "anomalies": anomalies,
    }


# =====================================================================
# ENDPOINT 10: DASHBOARD INSTITUTIONNEL (Phase 4)
# =====================================================================

@router.get("/dashboard", tags=["bdre"])
async def get_dashboard():
    """
    Dashboard institutionnel BDRE.
    Vue consolidee de toutes les metriques pour monitoring STEEVE-MAX.
    """
    from engines.bdre import (
        get_registry, get_scorer, get_audit_logger,
        get_health_monitor, get_anomaly_detector,
    )

    registry = get_registry()
    scorer = get_scorer()
    audit = get_audit_logger()
    monitor = get_health_monitor()
    detector = get_anomaly_detector()

    # Sources externes avec statut
    external = registry.get_external_sources()
    internal = registry.get_internal_sources()

    # Compter par statut
    status_counts = {}
    for src in external + internal:
        st = src.get("status", "unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    # Dernier score par source
    source_scores = []
    for src in external:
        last = scorer.get_last_score(src["source_id"])
        source_scores.append({
            "source_id": src["source_id"],
            "name": src.get("name", ""),
            "status": src["status"],
            "score": last["score"] if last else src.get("score", 0.0),
            "classification": last["classification"] if last else "NON EVALUE",
        })

    # Stats audit
    audit_stats = audit.get_stats()
    recent_fallbacks = audit.get_recent_fallbacks(limit=5)

    # Anomalies
    anomalies = detector.get_recent_anomalies(limit=5)

    # Monitoring
    monitor_status = monitor.get_all_statuses()

    return {
        "protocol": "BCE-4X GOLDEN V6+",
        "bdre_version": "Phase 4",
        "status": "OPERATIONAL",
        "sources": {
            "total": len(external) + len(internal),
            "external": len(external),
            "internal": len(internal),
            "by_status": status_counts,
        },
        "source_scores": source_scores,
        "audit": {
            "total_entries": audit_stats["total_entries"],
            "total_fallbacks": audit_stats["total_fallbacks"],
            "total_alerts": audit_stats["total_alerts"],
            "total_empty": audit_stats["total_empty"],
        },
        "recent_fallbacks": recent_fallbacks,
        "recent_anomalies": anomalies,
        "monitor": monitor_status,
        "engines_integrated": [
            "TNE (Terrain Nav Engine)",
            "Access Engine V6",
            "Stand Recommendation Engine",
            "GUIDE PRO Engine",
            "Weather Engine V3",
        ],
    }
