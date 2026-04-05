"""
Post-Hunt Reporter — Rapports post-chasse
BIONIC OS V8.5 | Phase E-1 | BCE-4X GOLDEN V6+

DataContract: DC-17 PostHuntReportContract
EventBus: EB-23 guide:report:ready

Points de Fusion:
  PF-E7: adaptive_navigation_engine → learn_from_history
"""

import logging
from datetime import datetime, timezone
from typing import Dict

logger = logging.getLogger("guide_pro.post_hunt_reporter")


def generate_report(session: Dict) -> Dict:
    """
    Generer un rapport post-chasse complet.
    Ne fonctionne que pour les sessions 'completed'.
    """
    if session.get("status") != "completed":
        return {"success": False, "error": "SESSION_NOT_COMPLETED"}

    routes = session.get("routes", [])
    clients = session.get("clients", [])

    # Calculer les metriques aggregees
    total_distance = sum(r.get("total_distance_km", 0) for r in routes)
    total_time = sum(r.get("estimated_time_hours", 0) for r in routes)
    avg_forest_ratio = (
        sum(r.get("forest_ratio", 0) for r in routes) / len(routes)
        if routes else 0
    )

    # Duree reelle de la session
    actual_start = session.get("actual_start", "")
    actual_end = session.get("actual_end", "")
    real_duration_hours = 0.0
    if actual_start and actual_end:
        try:
            t1 = datetime.fromisoformat(actual_start)
            t2 = datetime.fromisoformat(actual_end)
            real_duration_hours = (t2 - t1).total_seconds() / 3600
        except Exception:
            pass

    # Client summaries
    client_summaries = []
    for client in clients:
        client_route = next(
            (r for r in routes if r.get("client_id") == client.get("user_id")),
            None,
        )
        client_summaries.append({
            "user_id": client.get("user_id"),
            "name": client.get("name"),
            "skill_level": client.get("skill_level"),
            "distance_km": client_route.get("total_distance_km", 0) if client_route else 0,
            "hotspots_visited": client_route.get("hotspots_assigned", 0) if client_route else 0,
        })

    report = {
        "generated": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_distance_km": round(total_distance, 2),
        "total_time_hours": round(total_time, 2),
        "real_duration_hours": round(real_duration_hours, 2),
        "avg_forest_ratio": round(avg_forest_ratio, 2),
        "routes_count": len(routes),
        "clients_count": len(clients),
        "sightings": 0,
        "harvests": 0,
        "safety_incidents": 0,
        "client_summaries": client_summaries,
        "session_title": session.get("title", ""),
        "species": session.get("species", ""),
        "territory_id": session.get("territory_id", ""),
        "bdre_metrics": _get_bdre_metrics(session),
    }

    # Stocker le rapport dans la session
    session["report"] = report

    # PF-E7: Apprentissage M4 (si disponible)
    try:
        from modules.adaptive_navigation_engine.services.user_profile_learner import (
            learn_from_session,
        )
        for client in clients:
            learn_from_session(client.get("user_id"), session)
    except Exception:
        pass

    logger.info(
        f"[GUIDE PRO] Rapport genere: session {session.get('session_id', '?')}, "
        f"{total_distance:.1f}km, {len(clients)} clients"
    )

    return {"success": True, "report": report}


def get_report(session: Dict) -> Dict:
    """Lire le rapport post-chasse."""
    report = session.get("report", {})
    if not report.get("generated"):
        return {"success": False, "error": "REPORT_NOT_GENERATED"}
    return {"success": True, "report": report}


def _get_bdre_metrics(session: Dict) -> Dict:
    """
    BDRE Phase 4: Inclure les metriques BDRE dans le rapport post-chasse.
    """
    # Metriques de la validation terrain effectuee lors de la generation des routes
    bdre_validation = session.get("bdre_validation", {})

    # Metriques du journal BDRE pour cette session
    try:
        from engines.bdre import get_audit_logger
        audit = get_audit_logger()
        recent = audit.get_recent_fallbacks(limit=10)
        fallback_count = len(recent)
    except Exception:
        fallback_count = 0

    return {
        "terrain_score": bdre_validation.get("min_score", 0.0),
        "terrain_status": bdre_validation.get("recommendation", "UNKNOWN"),
        "terrain_warning": bdre_validation.get("warning"),
        "fallbacks_during_session": fallback_count,
        "data_reliability": "BDRE Phase 4 active",
    }
