"""
ENGINES-CATALOG-Ω — Endpoint gouvernance
==========================================
GET /api/v20/territoire/engines-catalog
Retourne: versions, dernière exécution, nombre d'appels, statut conformité.
"""
from fastapi import APIRouter
from engines.v8_institutional.engine_science_omega import get_catalog, get_data_sources

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Engines Catalog"])


@router.get("/engines-catalog")
async def engines_catalog():
    """Registry institutionnel live des engines actifs."""
    engines = get_catalog()
    # Enrichissement avec statut conformite (via SELF-AUDIT last)
    try:
        from engines.v8_institutional.self_audit_omega import _LAST_AUDIT
        last = _LAST_AUDIT
    except Exception:
        last = None

    return {
        "total_engines": len(engines),
        "engines": engines,
        "data_sources": get_data_sources(),
        "last_audit": {
            "ran_at": last.get("ran_at") if last else None,
            "conforme": last.get("conforme") if last else None,
            "suites_total": len(last.get("suites", [])) if last else 0,
            "suites_ok": sum(1 for s in (last.get("suites") or []) if s.get("statut") == "OK") if last else 0,
            "perf_guard_severity": (last.get("perf_guard") or {}).get("severity_max") if last else None,
        },
    }
