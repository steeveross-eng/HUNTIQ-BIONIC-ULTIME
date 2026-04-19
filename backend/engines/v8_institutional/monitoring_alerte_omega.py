"""
ENGINE-MONITORING-Ω + ENGINE-ALERTE-ANOMALIES-Ω
================================================
Fusion gouvernance: SELF-AUDIT-Ω + PERF-GUARD-Ω sous meta-engine unique.
- MONITORING-Ω: etat live de tout le systeme (engines + tests + perf + catalog)
- ALERTE-ANOMALIES-Ω: detecte les anomalies (suite FAIL, PERF fail, engine silencieux)
"""
from fastapi import APIRouter
from engines.v8_institutional.engine_science_omega import register_engine, mark_call, get_catalog, get_catalog_summary

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Monitoring + Alerte"])

register_engine("ENGINE-MONITORING-Ω", "V1-SUPRA-2026-04", "Monitoring unifie (engines + audit + perf)", "GOUVERNANCE", [])
register_engine("ENGINE-ALERTE-ANOMALIES-Ω", "V1-SUPRA-2026-04", "Detection anomalies systeme", "GOUVERNANCE", [])


def _collect_alerts() -> list:
    """Detecte anomalies actuelles depuis l'audit."""
    alerts = []
    try:
        from engines.v8_institutional.self_audit_omega import _LAST_AUDIT
        audit = _LAST_AUDIT
    except Exception:
        audit = None

    if not audit or audit.get("ran_at") is None:
        alerts.append({"severity": "warning", "code": "NO_AUDIT", "message": "Aucun audit execute depuis startup"})
        return alerts

    # Suite failures
    for s in audit.get("suites", []):
        if s.get("statut") != "OK":
            alerts.append({
                "severity": "fail", "code": "SUITE_FAIL",
                "suite": s.get("nom"), "message": f"Suite {s.get('nom')} en echec",
            })

    # Perf-guard issues
    pg = audit.get("perf_guard") or {}
    for issue in pg.get("issues", []):
        alerts.append({
            "severity": issue.get("severity"), "code": "PERF_REGRESSION",
            "metric": issue.get("metric"), "channel": issue.get("channel"),
            "ratio": issue.get("ratio"), "baseline_ms": issue.get("baseline_ms"),
            "current_ms": issue.get("current_ms"),
            "message": f"Regression {issue.get('metric')} ({issue.get('severity')}) ratio {issue.get('ratio')}",
        })

    # Engines silencieux (enregistres mais jamais appeles)
    for eng in get_catalog():
        if eng.get("call_count", 0) == 0 and eng.get("pillar") not in ("GOUVERNANCE",):
            alerts.append({
                "severity": "warning", "code": "ENGINE_SILENT",
                "engine": eng.get("name"),
                "message": f"Engine {eng.get('name')} jamais appele",
            })

    return alerts


@router.get("/monitoring")
async def monitoring_status():
    """MONITORING-Ω: etat unifie du systeme."""
    mark_call("ENGINE-MONITORING-Ω")
    try:
        from engines.v8_institutional.self_audit_omega import _LAST_AUDIT
        audit = _LAST_AUDIT
    except Exception:
        audit = None
    try:
        from engines.v8_institutional.sla_baseline_omega import load_baseline
        baseline = load_baseline()
    except Exception:
        baseline = None

    alerts = _collect_alerts()
    has_fail = any(a.get("severity") == "fail" for a in alerts)
    has_warning = any(a.get("severity") == "warning" for a in alerts)
    global_status = "fail" if has_fail else ("warning" if has_warning else "ok")

    return {
        "engine": "ENGINE-MONITORING-Ω",
        "global_status": global_status,
        "engines": get_catalog(),
        "catalog_summary": get_catalog_summary(),
        "last_audit": {
            "ran_at": (audit or {}).get("ran_at"),
            "conforme": (audit or {}).get("conforme"),
            "suites_total": len((audit or {}).get("suites", [])),
            "suites_ok": sum(1 for s in (audit or {}).get("suites", []) if s.get("statut") == "OK"),
            "perf_guard_severity": ((audit or {}).get("perf_guard") or {}).get("severity_max"),
        },
        "sla_baseline_present": baseline is not None,
        "alerts": alerts,
        "alert_count": len(alerts),
    }


@router.get("/alertes")
async def alertes():
    """ALERTE-ANOMALIES-Ω: liste des anomalies detectees."""
    mark_call("ENGINE-ALERTE-ANOMALIES-Ω")
    alerts = _collect_alerts()
    return {
        "engine": "ENGINE-ALERTE-ANOMALIES-Ω",
        "total": len(alerts),
        "by_severity": {
            "fail": sum(1 for a in alerts if a.get("severity") == "fail"),
            "warning": sum(1 for a in alerts if a.get("severity") == "warning"),
        },
        "alerts": alerts,
    }
