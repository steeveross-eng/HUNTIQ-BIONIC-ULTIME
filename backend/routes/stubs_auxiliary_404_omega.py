"""
╔══════════════════════════════════════════════════════════════════════════╗
║  stubs_auxiliary_404_omega.py — PHASE 2 STABILISATION TERRITOIRE Ω        ║
║  Commandant : STEEVE-MAX                                                  ║
║  Protocole  : BCE-4X ULTIME ABSOLU — TOP-ABSOLU                           ║
║  Directive  : P22ΩΩ_STUBS_AUXILIAIRES_404 · 2026-05-18                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  OBJET                                                                    ║
║  ─────                                                                    ║
║  Stubs minimaux 200 OK pour les endpoints AUXILIAIRES historiquement      ║
║  appelés par le frontend mais JAMAIS implémentés côté backend.            ║
║                                                                           ║
║  Ces endpoints étaient documentés comme « non-bloquants » par l'audit     ║
║  Phase-A (cf. backend/tools/audit_phase_a_generate_synthese.py:151) mais  ║
║  polluaient la console DevTools du COMMANDANT avec des 404 répétés,       ║
║  créant la perception d'un système instable.                              ║
║                                                                           ║
║  ENDPOINTS COUVERTS (tous montés sous prefix /api dans server.py)         ║
║  ───────────────────────────────────────────────────────────              ║
║  GET  /api/seo/meta/{path:path}                  ← SEOHead.jsx           ║
║  GET  /api/v1/bdre/dashboard                     ← DashboardPage, etc.   ║
║  GET  /api/v1/bdre/sources                       ← DashboardPage, etc.   ║
║  GET  /api/v1/notification/legal-time/status     ← NotificationService   ║
║  GET  /api/v1/notification/legal-time/upcoming   ← NotificationService   ║
║  GET  /api/sharing/notifications/anonymous       ← legacy frontend       ║
║                                                                           ║
║  Les shapes retournées respectent EXACTEMENT ce que le frontend attend    ║
║  (vérifié par inspection statique : DashboardPage.jsx ligne 44-52,        ║
║  NotificationService.js ligne 16-19, etc.). Tous les payloads sont        ║
║  délibérément vides (no-op) — aucune logique métier reproduite.           ║
║                                                                           ║
║  CACHE-CONTROL : 5 minutes (stable, économise la bande passante).         ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

router = APIRouter(tags=["stubs-auxiliary-404-omega"])

_STUB_HEADERS = {
    "Cache-Control": "public, max-age=300, stale-while-revalidate=900",
    "X-Stub-Auxiliary-Omega": "P22OMEGAOMEGA_STUBS_AUXILIAIRES_404",
}


def _stub_response(payload: dict | list | None) -> JSONResponse:
    """Helper : 200 OK + headers stub + cache-control."""
    return JSONResponse(content=payload, status_code=200, headers=_STUB_HEADERS)


# ──────────────────────────────────────────────────────────────────────────
# SEO META — appelé par SEOHead.jsx au mount de chaque page
# Shape attendue : objet meta (title/description/og_image) OU null
# ──────────────────────────────────────────────────────────────────────────
@router.get("/seo/meta/{path:path}")
async def seo_meta_stub(path: str = ""):
    """Stub SEO meta — retourne null (frontend fallback sur PAGE_META_CONFIG client)."""
    return _stub_response(None)


# ──────────────────────────────────────────────────────────────────────────
# BDRE DASHBOARD — appelé par DashboardPage / IntelligenceV6 / GuidePro / etc.
# Shape attendue : { bdre_version, audit_stats:{total_fallbacks,total_alerts} }
# ──────────────────────────────────────────────────────────────────────────
@router.get("/v1/bdre/dashboard")
async def bdre_dashboard_stub():
    """Stub BDRE dashboard — version sentinel + stats nulles."""
    return _stub_response({
        "bdre_version": "stub-omega-1.0",
        "audit_stats": {
            "total_fallbacks": 0,
            "total_alerts": 0,
            "total_queries": 0,
        },
        "stub": True,
        "note": "P22ΩΩ_STUBS_AUXILIAIRES_404 — endpoint BDRE non implémenté, "
                "stub non-bloquant pour éliminer les 404 console.",
    })


# ──────────────────────────────────────────────────────────────────────────
# BDRE SOURCES — frontend itère sur sources[] et filtre par .status === 'healthy'
# ──────────────────────────────────────────────────────────────────────────
@router.get("/v1/bdre/sources")
async def bdre_sources_stub():
    """Stub BDRE sources — liste vide."""
    return _stub_response({
        "sources": [],
        "stub": True,
    })


# ──────────────────────────────────────────────────────────────────────────
# LEGAL-TIME STATUS — NotificationService.getLegalTimeStatus()
# Shape attendue : { success: bool, warning_active: bool, ... }
# ──────────────────────────────────────────────────────────────────────────
@router.get("/v1/notification/legal-time/status")
async def legal_time_status_stub(lat: float | None = None, lng: float | None = None):
    """Stub legal-time status — pas d'alerte active."""
    return _stub_response({
        "success": False,
        "warning_active": False,
        "stub": True,
        "note": "P22ΩΩ_STUBS_AUXILIAIRES_404 — engine legal-time non câblé HTTP, "
                "stub neutre. Voir routes/legal_time_router pour activation future.",
    })


# ──────────────────────────────────────────────────────────────────────────
# LEGAL-TIME UPCOMING — NotificationService.getUpcomingAlerts()
# Shape attendue : { success: bool, notifications: [] }
# ──────────────────────────────────────────────────────────────────────────
@router.get("/v1/notification/legal-time/upcoming")
async def legal_time_upcoming_stub(
    lat: float | None = None,
    lng: float | None = None,
    hours: int = 24,
):
    """Stub legal-time upcoming — aucune notification programmée."""
    return _stub_response({
        "success": False,
        "notifications": [],
        "stub": True,
    })


# ──────────────────────────────────────────────────────────────────────────
# SHARING NOTIFICATIONS ANONYMOUS — legacy frontend
# Shape attendue : { success: bool, notifications: [] }
# ──────────────────────────────────────────────────────────────────────────
@router.get("/sharing/notifications/anonymous")
async def sharing_notifications_anonymous_stub():
    """Stub sharing notifications anonymous — aucune notification."""
    return _stub_response({
        "success": False,
        "notifications": [],
        "stub": True,
    })


# ──────────────────────────────────────────────────────────────────────────
# HEALTHCHECK STUB — pour validation d'intégration
# ──────────────────────────────────────────────────────────────────────────
@router.get("/stubs-auxiliary/healthz")
async def stubs_auxiliary_healthz():
    """Healthcheck du router stubs auxiliaires."""
    return _stub_response({
        "router": "stubs_auxiliary_404_omega",
        "directive": "P22ΩΩ_STUBS_AUXILIAIRES_404",
        "commandant": "STEEVE-MAX",
        "protocole": "BCE-4X ULTIME ABSOLU — TOP-ABSOLU",
        "endpoints": [
            "GET /api/seo/meta/{path}",
            "GET /api/v1/bdre/dashboard",
            "GET /api/v1/bdre/sources",
            "GET /api/v1/notification/legal-time/status",
            "GET /api/v1/notification/legal-time/upcoming",
            "GET /api/sharing/notifications/anonymous",
        ],
        "status": "ACTIVE",
    })
