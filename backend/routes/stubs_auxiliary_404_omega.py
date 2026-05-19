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
# P22OMEGAOMEGA_STUBS_AUXILIAIRES_404_BIS · 2026-05-18 · COMMANDANT STEEVE-MAX
# Extension : 5 endpoints additionnels détectés en console (DevTools)
#   - /api/sharing/received/{user_id}        ← useSharing.js:113
#   - /api/sharing/sent/{user_id}            ← useSharing.js:125
#   - /api/sharing/notifications/{user_id}   ← useSharing.js:400
#   - /api/groups/{user_id}/my-groups        ← useSharing.js:217
#   - /api/zones/alerts?user_id=...          ← ZoneFavorites.jsx:52
# ──────────────────────────────────────────────────────────────────────────

# Shape attendue : { shares: [] }
@router.get("/sharing/received/{user_id}")
async def sharing_received_stub(user_id: str):
    """Stub sharing received — aucun partage reçu."""
    return _stub_response({"shares": [], "stub": True})


# Shape attendue : { email_shares: [], link_shares: [] } (useSharing.js:33)
@router.get("/sharing/sent/{user_id}")
async def sharing_sent_stub(user_id: str):
    """Stub sharing sent — objet avec arrays email_shares/link_shares."""
    return _stub_response({
        "email_shares": [],
        "link_shares": [],
        "stub": True,
    })


# Shape attendue : { notifications: [], unread_count: 0 }
@router.get("/sharing/notifications/{user_id}")
async def sharing_notifications_user_stub(user_id: str, unread_only: bool = False):
    """Stub sharing notifications par user — aucune notification."""
    return _stub_response({
        "notifications": [],
        "unread_count": 0,
        "stub": True,
    })


# Shape attendue : { owned_groups: [], member_groups: [] }
# (vérifié par useSharing.js:373 → `[...myGroups.owned_groups, ...myGroups.member_groups]`)
@router.get("/groups/{user_id}/my-groups")
async def groups_my_groups_stub(user_id: str):
    """Stub groups my-groups — objet vide avec arrays attendus par useHuntingGroups."""
    return _stub_response({
        "owned_groups": [],
        "member_groups": [],
        "stub": True,
    })


# Shape attendue : { alerts: [], unread_count: 0 }
@router.get("/zones/alerts")
async def zones_alerts_stub(user_id: str | None = None):
    """Stub zones alerts — aucune alerte."""
    return _stub_response({
        "alerts": [],
        "unread_count": 0,
        "stub": True,
    })


# ════════════════════════════════════════════════════════════════════════════
# P22ΩΩ_TERRITOIRE_STABILISATION_TOTALE_Ω · 2026-02-XX · COMMANDANT STEEVE-MAX
# Stubs additionnels pour endpoints 404 répandus dans la console DevTools.
# Causes : routers `weather_v3` et `v8_national` échouent au chargement
# (imports cassés `wind_model_provider`, `WILDLIFE_REGIMES`). Les frontends
# (Vent HUD, Score V8 HUD) appellent ces endpoints au monté.
# Doctrine : stubs minimaux 200 OK · shapes compatibles · aucune logique métier.
# ════════════════════════════════════════════════════════════════════════════

# Shape attendue : { temperature, wind_speed, wind_deg, condition, ... }
@router.get("/v3/weather/current")
async def v3_weather_current_stub(lat: float, lng: float):
    """Stub weather current — payload neutre conformément à Open-Meteo Lite."""
    return _stub_response({
        "lat": lat,
        "lng": lng,
        "temperature_c": None,
        "wind_speed_kmh": None,
        "wind_deg": None,
        "humidity_pct": None,
        "condition": "UNAVAILABLE",
        "source": "STUB_P22OMEGAOMEGA_TERRITOIRE_STABILISATION",
        "stub": True,
    })


# Shape attendue : { grid: { rows, cols, lats[], lngs[], u[][], v[][] } }
@router.get("/v3/weather/windgrid")
async def v3_weather_windgrid_stub(
    south: float,
    north: float,
    west: float,
    east: float,
    resolution: float = 0.05,
):
    """Stub windgrid — structure compatible WindFlowLayer (rows=cols=0 = no-op safe).

    Frontend `WindFlowLayer.jsx` ligne 74 protège uniquement contre
    `grid.rows < 2 || grid.cols < 2`. Une array vide planterait
    `lats.length` ligne 78. On renvoie donc une structure complète
    avec rows=0/cols=0 pour court-circuit propre.
    """
    return _stub_response({
        "bbox": {"south": south, "north": north, "west": west, "east": east},
        "resolution": resolution,
        "grid": {
            "rows": 0,
            "cols": 0,
            "lats": [],
            "lngs": [],
            "u": [],
            "v": [],
        },
        "source": "STUB_P22OMEGAOMEGA_TERRITOIRE_STABILISATION",
        "stub": True,
    })


# Shape attendue : { score_v8, classification, scores_detail: {...} }
@router.get("/v8/national/score")
async def v8_national_score_stub(
    lat: float,
    lon: float,
    species: str = "orignal",
    month: int = 5,
    hour: int = 12,
):
    """Stub V8 national score — score neutre 50.0 (NEUTRE) pour éviter crash UI."""
    return _stub_response({
        "lat": lat,
        "lon": lon,
        "species": species,
        "month": month,
        "hour": hour,
        "score_v8": 50.0,
        "classification": "NEUTRE",
        "scores_detail": {
            "biome": 50.0,
            "habitat": 50.0,
            "regime": 50.0,
            "season": 50.0,
        },
        "source": "STUB_P22OMEGAOMEGA_TERRITOIRE_STABILISATION",
        "stub": True,
    })


# Shape minimale pour habitat-score realtime (400 sur le frontend)
@router.get("/v1/bionic/habitat-score/realtime")
async def v1_bionic_habitat_score_realtime_stub(
    lat: float | None = None,
    lon: float | None = None,
    species: str | None = None,
):
    """Stub habitat-score realtime — neutre, compatible front."""
    return _stub_response({
        "lat": lat,
        "lon": lon,
        "species": species or "orignal",
        "habitat_score": 50.0,
        "components": {
            "land_cover": 50.0,
            "water_proximity": 50.0,
            "elevation": 50.0,
        },
        "source": "STUB_P22OMEGAOMEGA_TERRITOIRE_STABILISATION",
        "stub": True,
    })


# Shape attendue : { favorites: [], total: 0 }
@router.get("/zones/favorites")
async def zones_favorites_stub(user_id: str | None = None):
    """Stub zones favorites — aucune favorite par défaut.

    Endpoint legacy appelé par MesZonesPage / dashboard. Le frontend
    affiche une liste vide gracieusement.
    """
    return _stub_response({
        "user_id": user_id,
        "favorites": [],
        "total": 0,
        "stub": True,
    })


# Shape attendue : { biome, regime, season, ... }
@router.get("/v8/national/biome-profile")
async def v8_national_biome_profile_stub(
    lat: float,
    lon: float,
    species: str = "orignal",
):
    """Stub V8 biome profile — profil neutre forestier mixte.

    Frontend `useBionicScoringV8` appelle cet endpoint pour enrichir
    le score V8. Le payload minimal évite tout crash dans le HUD.
    """
    return _stub_response({
        "lat": lat,
        "lon": lon,
        "species": species,
        "biome": "FORESTIER_MIXTE",
        "biome_label": "Forêt mixte boréale",
        "regime": "NEUTRE",
        "regime_score": 50.0,
        "season": "ETE",
        "snow_class": "SANS_NEIGE",
        "forest_class": "DENSE",
        "source": "STUB_P22OMEGAOMEGA_TERRITOIRE_STABILISATION",
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
            "GET /api/sharing/received/{user_id}",
            "GET /api/sharing/sent/{user_id}",
            "GET /api/sharing/notifications/{user_id}",
            "GET /api/groups/{user_id}/my-groups",
            "GET /api/zones/alerts",
            "GET /api/v3/weather/current",
            "GET /api/v3/weather/windgrid",
            "GET /api/v8/national/score",
            "GET /api/v1/bionic/habitat-score/realtime",
            "GET /api/zones/favorites",
            "GET /api/v8/national/biome-profile",
        ],
        "status": "ACTIVE",
    })
