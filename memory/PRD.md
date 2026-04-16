# HUNTIQ V8 — PRD
## PHASE-B-V8-SAFE-INTEGRATION-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **8/8 PASS** | **TERRAIN-AWARE COMPLET** | **6 ROUTERS V6 PURGES**

## Architecture V8 Pure — Terrain-Aware

### Backend Engines (V8 National)
- `router.py` — Score V8, Biome, Habitat
- `referentials.py` — Donnees reference 13 provinces
- `exclusion_engine.py` — 22 criteres BCE-4X
- `governance.py` — Master Switch PREVIEW/PUBLIC
- `map_bundle.py` — Bundle (delegue Phase B terrain-aware, TTFB <5ms, SANS auth)
- `phase_a_engines.py` — Relocalisation + Salines V8
- `phase_b_engines.py` — Zones/Corridors/Affuts terrain-aware V8
- `p1_pipelines.py` — Stubs LiDAR/IRDA

### Phase B — Terrain-Aware V8
- `generate_zones_ta()` — 5 types, scoring terrain (canopy/pente/eau/route/strate/feuillus)
- `generate_corridors_ta()` — 10 corridors, cost surface simplifie, continuite COR-006
- `generate_affuts_ta()` — 3 affuts, coherence zones+corridors, bonus proximite corridor
- `_cost_surface_score()` — penalite deplacement (pente/eau/route vs couvert)
- `_corridor_intensity()` — intensite temporelle + cost surface

### Purge V6 — 6 Routers Deregistres
1. relocation_router → 404
2. organic_zones_router → 404
3. corridor_unified_router → 404
4. movement_corridors_router → 404
5. corridors_v10_router → 404
6. salines_ultime_router → 404

### Frontend V8 (inchange)
- BionicLayersV8 consomme bundle V8 terrain-aware
- PhaseALayerV8 consomme Phase A
- PhaseAPanelV8 panneau lateral

## Key API Endpoints (V8 Only)
- `GET /api/v8/map/bundle` — Bundle terrain-aware (NO AUTH)
- `GET /api/v8/map/zones-ta` — Zones terrain-aware sandbox
- `GET /api/v8/map/corridors-ta` — Corridors terrain-aware sandbox
- `GET /api/v8/map/affuts-ta` — Affuts terrain-aware sandbox
- `GET /api/v8/map/relocalisation` — Relocalisation V8
- `GET /api/v8/map/salines` — Salines V8
- `GET /api/v8/national/score` — Score V8 National
- `GET /api/v8/governance/state` — Governance

## Completed Work
1-9. Phases precedentes (voir historique)
10. V8-FRONTEND-PHASE-A-Omega
11. PURGE-V6-ANTI-DUPLICATION-A-Omega
12. V8-REINTEGRATION-PHASE-B-Omega (Zones+Corridors+Affuts terrain-aware)
13. PURGE-V6-PHASE-B (6 routers V6 purges)
14. AUDIT-ANTI-DUPLICATION-B (8/8 PASS)

## Phase C — FUTUR
- Scenario Engine
- Thermal Engine
- Multi-Engine Scoring

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

FIN DU DOCUMENT
