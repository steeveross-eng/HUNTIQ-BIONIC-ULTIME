"""ENGINE-GOUVERNANCE-Ω — Fusion MONITORING + ALERTE + SCIENCE + REGISTRY."""
from fastapi import APIRouter
from engines.v8_institutional.engine_science_omega import (
    register_engine, mark_call, get_catalog, get_catalog_summary, get_data_sources,
    get_studies, get_datasets, get_engine_links, get_science_gaps,
)

ENGINE_NAME = "ENGINE-GOUVERNANCE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Gouvernance institutionnelle unifiee (fusion MONITORING + ALERTE + SCIENCE + REGISTRY)", "GOUVERNANCE", [])

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Gouvernance"])


@router.get("/gouvernance")
async def gouvernance_unified():
    """ENGINE-GOUVERNANCE-Ω: vue consolidee complete du systeme."""
    mark_call(ENGINE_NAME)
    try:
        from engines.v8_institutional.monitoring_alerte_omega import _collect_alerts
        alerts = _collect_alerts()
    except Exception:
        alerts = []
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

    has_fail = any(a.get("severity") == "fail" for a in alerts)
    has_warning = any(a.get("severity") == "warning" for a in alerts)
    global_status = "fail" if has_fail else ("warning" if has_warning else "ok")

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "global_status": global_status,
        "pillars": {
            "monitoring": {
                "engines_count": len(get_catalog()),
                "engines_pillars": _count_by_pillar(),
            },
            "alertes": {
                "total": len(alerts),
                "by_severity": {
                    "fail": sum(1 for a in alerts if a.get("severity") == "fail"),
                    "warning": sum(1 for a in alerts if a.get("severity") == "warning"),
                },
                "alerts": alerts[:10],  # top 10
            },
            "science": {
                "summary": get_catalog_summary(),
                "gaps": get_science_gaps(),
                "data_sources_count": len(get_data_sources()),
            },
            "audit": {
                "last_ran_at": (audit or {}).get("ran_at"),
                "conforme": (audit or {}).get("conforme"),
                "suites_ok": sum(1 for s in (audit or {}).get("suites", []) if s.get("statut") == "OK"),
                "suites_total": len((audit or {}).get("suites", [])),
                "perf_guard_severity": ((audit or {}).get("perf_guard") or {}).get("severity_max"),
            },
            "sla": {
                "baseline_present": baseline is not None,
                "baseline_timestamp": (baseline or {}).get("timestamp"),
            },
        },
        "registry_md_path": "/app/memory/GOVERNANCE_REGISTRY.md",
    }


def _count_by_pillar() -> dict:
    counts = {}
    for e in get_catalog():
        p = e.get("pillar", "UNKNOWN")
        counts[p] = counts.get(p, 0) + 1
    return counts
