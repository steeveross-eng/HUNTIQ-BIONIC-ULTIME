"""
ROUTER · TERRITOIRE-Ω · SPATIAL (Heatmap + Score + Status)
===========================================================

╔═══════════════════════════════════════════════════════════════════════════╗
║  P22ΩΩ_PALIER_3_MIGRATION_V7_SPATIAL_Ω · 2026-05-18                      ║
║  Commandant : STEEVE-MAX                                                  ║
║  Protocole : BCE-4X ULTIME ABSOLU                                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  OBJET                                                                    ║
║  ─────                                                                    ║
║  Endpoints Ω institutionnels qui DÉLÈGUENT à la logique métier V7         ║
║  existante. Aucune modification du scoring (V30_LOCK respecté).           ║
║                                                                           ║
║  ENDPOINTS Ω                                                              ║
║    GET /api/v20/territoire/spatial/heatmap                                ║
║    GET /api/v20/territoire/spatial/score                                  ║
║    GET /api/v20/territoire/spatial/status                                 ║
║                                                                           ║
║  REMPLACE                                                                 ║
║    GET /api/v7/spatial/heatmap   (legacy SPATIAL-ENGINE-V7)               ║
║    GET /api/v7/spatial/scoring   (legacy SPATIAL-ENGINE-V7)               ║
║    GET /api/v7/spatial/status                                             ║
║                                                                           ║
║  DOCTRINE INSTITUTIONNELLE                                                ║
║  ─────────────────────────                                                ║
║  - Délégation pure aux fonctions V7 existantes via import direct          ║
║  - Aucune duplication de la logique métier                                ║
║  - Shape de retour identique (compat frontend immédiate)                  ║
║  - Adaptation marginale du `dataVersion` et `engine` pour traçabilité Ω   ║
║  - Auth identique (get_current_user_with_role + get_camera_db)            ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from modules.camera_engine.dependencies import get_camera_db
from modules.roles_engine.v1.dependencies import get_current_user_with_role
from modules.roles_engine.v1.models import UserWithRole

# Délégation directe aux fonctions V7 (V30_LOCK : aucune modification métier).
from engines.spatial_engine_v7.router import (
    spatial_heatmap as _v7_spatial_heatmap,
    spatial_scoring as _v7_spatial_scoring,
    spatial_status as _v7_spatial_status,
)

router = APIRouter(
    prefix="/api/v20/territoire/spatial",
    tags=["TERRITOIRE-Ω · Spatial"],
)


def _omega_tag(payload: dict) -> dict:
    """Marque la traçabilité Ω sans casser le shape V7."""
    if isinstance(payload, dict):
        payload["served_by"] = "TERRITOIRE-Ω-SPATIAL-ROUTER"
        payload["upstream_engine"] = payload.get("engine", "SPATIAL-ENGINE-V7")
        # Préservation stricte du shape : `dataVersion` original conservé pour
        # garantir compatibilité descendante des composants frontend.
    return payload


@router.get("/heatmap")
async def spatial_heatmap_omega(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int | None = Query(None),
    day: int | None = Query(None),
    hour: int | None = Query(None),
    grid_size: int = Query(12, ge=5, le=25),
    radius_km: float = Query(1.5),
    user: UserWithRole = Depends(get_current_user_with_role),
):
    """Heatmap spatiale Ω — délégation V7 (23 moteurs consolidés + nutrition + temporal).

    Migration directe depuis `/api/v7/spatial/heatmap`. Aucune modification
    fonctionnelle — la logique métier reste dans `spatial_engine_v7/router.py`.
    """
    payload = await _v7_spatial_heatmap(
        lat=lat, lon=lon, species=species,
        month=month, day=day, hour=hour,
        grid_size=grid_size, radius_km=radius_km,
        user=user,
    )
    return _omega_tag(payload)


@router.get("/score")
async def spatial_score_omega(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int | None = Query(None),
    hour: int | None = Query(None),
    user: UserWithRole = Depends(get_current_user_with_role),
    db: AsyncIOMotorDatabase = Depends(get_camera_db),
):
    """Score spatial Ω — délégation V7 (habitat, pression, relief, hydro, nutrition, temporal).

    Migration directe depuis `/api/v7/spatial/scoring`. Aucune modification
    fonctionnelle.
    """
    payload = await _v7_spatial_scoring(
        lat=lat, lon=lon, species=species,
        month=month, hour=hour,
        user=user, db=db,
    )
    return _omega_tag(payload)


@router.get("/status")
async def spatial_status_omega():
    """Status TERRITOIRE-Ω Spatial — info upstream + endpoints Ω."""
    upstream = await _v7_spatial_status()
    return {
        "engine": "TERRITOIRE-Ω-SPATIAL",
        "version": "Ω.1.0",
        "status": "OPERATIONNEL",
        "doctrine": "P22ΩΩ_PALIER_3_MIGRATION_V7_SPATIAL_Ω",
        "upstream_engine": upstream.get("engine"),
        "upstream_version": upstream.get("version"),
        "endpoints_omega": [
            "/api/v20/territoire/spatial/heatmap",
            "/api/v20/territoire/spatial/score",
            "/api/v20/territoire/spatial/status",
        ],
        "delegation_mode": "PROXY_PURE — logique métier V7 préservée (V30_LOCK)",
        "exclusions_bce4x": upstream.get("exclusions_bce4x"),
        "integrations": upstream.get("integrations"),
        "dataVersion": "Ω",
        "migrated_from": "SPATIAL-ENGINE-V7 (/api/v7/spatial/{heatmap,scoring,status})",
    }
