"""
ROUTER · TERRITOIRE-Ω · RELOCALISATION + SALINES
=================================================

╔═══════════════════════════════════════════════════════════════════════════╗
║  P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES · 2026-05-18            ║
║  Commandant : STEEVE-MAX                                                  ║
║  Protocole : BCE-4X ULTIME ABSOLU                                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ENDPOINTS Ω                                                              ║
║    GET /api/v20/territoire/relocalisation                                 ║
║    GET /api/v20/territoire/salines-placement                              ║
║    GET /api/v20/territoire/relocalisation-salines/status                  ║
║                                                                           ║
║  Remplace les anciens endpoints V8-PHASE-A désactivés :                   ║
║    GET /api/v8/map/relocalisation  (404 depuis 2026-05-12)                ║
║    GET /api/v8/map/salines         (404 depuis 2026-05-12)                ║
║                                                                           ║
║  Doctrine : aucun changement fonctionnel — logique identique au           ║
║  pipeline V8-PHASE-A original (extraction pure).                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from fastapi import APIRouter, Query

from engines.v8_institutional.territoire_omega_relocalisation_salines import (
    compute_relocalisation_omega,
    compute_salines_placement_omega,
    status_omega,
)

router = APIRouter(
    prefix="/api/v20/territoire",
    tags=["TERRITOIRE-Ω · Relocalisation + Salines"],
)


@router.get("/relocalisation")
async def relocalisation_omega_endpoint(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int | None = Query(None),
    wind_deg: float = Query(180),
    radius_m: int = Query(500),
    n_candidates: int = Query(12),
):
    """Relocalisation Ω — top-3 sites optimaux + explications détaillées.

    Migration directe depuis /api/v8/map/relocalisation (logique identique).
    """
    return await compute_relocalisation_omega(
        lat=lat, lon=lon, species=species, month=month,
        wind_deg=wind_deg, radius_m=radius_m, n_candidates=n_candidates,
    )


@router.get("/salines-placement")
async def salines_placement_omega_endpoint(
    lat: float = Query(...), lon: float = Query(...),
    species: str = Query("cerf"),
    month: int | None = Query(None),
    n_salines: int = Query(3),
    min_distance_m: int = Query(300),
):
    """Salines Ω — placement optimal 1-4 salines, 6 critères terrain.

    Migration directe depuis /api/v8/map/salines (logique identique).
    """
    return await compute_salines_placement_omega(
        lat=lat, lon=lon, species=species, month=month,
        n_salines=n_salines, min_distance_m=min_distance_m,
    )


@router.get("/relocalisation-salines/status")
async def relocalisation_salines_status():
    """Statut TERRITOIRE-Ω Relocalisation + Salines."""
    return status_omega()
