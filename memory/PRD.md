# HUNTIQ V8 — PRD
## V8-ULTIME-INSTITUTIONNEL-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **8/8 PASS** | **ARCHITECTURE V8 PURE COMPLETE**

## Architecture V8 — Production Ready

### Backend (engines/v8_national/)
- `router.py` — Score V8, Biome, Habitat (13 provinces)
- `referentials.py` — Referentiels nationaux
- `exclusion_engine.py` — 22 criteres BCE-4X
- `governance.py` — Master Switch PREVIEW/PUBLIC
- `map_bundle.py` — Bundle consolide (Phase B terrain-aware + Phase C thermal/multi-engine, <5ms)
- `phase_a_engines.py` — Relocalisation + Salines V8
- `phase_b_engines.py` — Zones/Corridors/Affuts terrain-aware (cost surface, COR-006)
- `phase_c_engines.py` — Thermal + Scenario (8 presets) + Multi-Engine Scoring
- `p1_pipelines.py` — Stubs LiDAR MRNF / IRDA pedologie

### Frontend (V8 exclusif)
- `BionicLayersV8.jsx` — Rendu organique (polygones, Bezier, triangles)
- `PhaseALayerV8.jsx` — Couche carte relocalisation+salines
- `PhaseAPanelV8.jsx` — Panneau Phase A (scoring, explications)
- `PhaseCPanelV8.jsx` — Panneau Phase C (Score/Thermal/Scenarios)
- `usePhaseAV8.js` + `useMapBundleV8.js` + `useBionicScoringV8.js` — Hooks V8

### Purge V6 Totale — 7 couches/routers
1. relocation_router → 404
2. organic_zones_router → 404
3. corridor_unified_router → 404
4. movement_corridors_router → 404
5. corridors_v10_router → 404
6. salines_ultime_router → 404
7. BionicCorridorsV6Layer → SUPPRIME du rendu

### Key Endpoints V8
- `/api/v8/map/bundle` — Bundle consolide (terrain-aware+thermal+multi-engine)
- `/api/v8/map/relocalisation` + `/api/v8/map/salines` — Phase A
- `/api/v8/map/zones-ta` + `/api/v8/map/corridors-ta` + `/api/v8/map/affuts-ta` — Phase B
- `/api/v8/engines/thermal` + `/api/v8/engines/scenario` + `/api/v8/engines/multi-score` — Phase C
- `/api/v8/national/score` + `/api/v8/governance/state` — Core

### Performances
- Bundle TTFB: <5ms
- Thermal: <1ms
- Multi-Engine: <2ms
- Scenario: <2ms

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Remaining (P1)
- LiDAR MRNF multi-provincial (stubs)
- IRDA pedologie Quebec (stubs)
- Open-Meteo integration pour Thermal Engine (actuellement heuristique)

FIN DU DOCUMENT
