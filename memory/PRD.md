# HUNTIQ V8 — PRD
## V8-ULTIME-INSTITUTIONNEL-Omega — CERTIFIE FINAL
**MAJ:** 2026-04-16 | **7/7 PASS** | **CORRECTIONS FINALES COMPLETES** | **ARCHITECTURE V8 PURE**

## Architecture V8 — Production Ready

### Backend (engines/v8_national/)
- `router.py` — Score V8, Biome, Habitat (13 provinces)
- `referentials.py` — Referentiels nationaux
- `exclusion_engine.py` — 22 criteres BCE-4X
- `governance.py` — Master Switch PREVIEW/PUBLIC
- `map_bundle.py` — Bundle consolide (Phase B+C, exclusions terrain, <5ms)
- `phase_a_engines.py` — Relocalisation + Salines V8
- `phase_b_engines.py` — Zones/Corridors/Affuts terrain-aware + exclusions (eau<20m, pente>35deg)
- `phase_c_engines.py` — Thermal + Scenario (8 presets) + Multi-Engine Scoring
- `p1_pipelines.py` — Stubs LiDAR MRNF / IRDA pedologie

### Frontend (V8 exclusif)
- `BionicLayersV8.jsx` — Rendu organique + tooltips enrichis (terrain data + exclusions)
- `PhaseALayerV8.jsx` + `PhaseAPanelV8.jsx` — Phase A UI
- `PhaseCPanelV8.jsx` — Phase C UI (Score/Thermal/Scenarios)
- Hooks: `usePhaseAV8.js`, `useMapBundleV8.js`, `useBionicScoringV8.js`

### Corrections Finales
- Exclusions terrain: corridors eau<20m + pente>35deg filtres backend
- Zones: flag excluded + exclusion_reason
- Tooltips: canopy/pente/eau/route/strate/feuillus + cost surface + corridor bonus
- Cartes: 11→9 types (ORTHOPHOTO fusionne SATELLITE, CANOPY fusionne LIDAR)
- V6 BionicCorridorsV6Layer: PURGE definitive du rendu

### Cartes V8 Consolidees (9 types)
1. Ecoforestry | 2. Satellite | 3. IQHO | 4. Forest Roads
5. LIDAR+Canopee | 6. Hydrologie | 7. Chemins | 8. Neige | 9. Pente

### Key Endpoints V8
- `/api/v8/map/bundle` — Bundle consolide
- `/api/v8/map/relocalisation` + `/api/v8/map/salines` — Phase A
- `/api/v8/map/zones-ta` + `/api/v8/map/corridors-ta` + `/api/v8/map/affuts-ta` — Phase B
- `/api/v8/engines/thermal` + `/api/v8/engines/scenario` + `/api/v8/engines/multi-score` — Phase C
- `/api/v8/national/score` + `/api/v8/governance/state` — Core

### Purge V6 Totale — 7 routers + 1 layer
relocation, organic_zones, corridor_unified, movement_corridors, corridors_v10, salines_ultime, BionicCorridorsV6Layer

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Remaining (P1)
- LiDAR MRNF multi-provincial (stubs)
- IRDA pedologie Quebec (stubs)
- Open-Meteo temps reel pour Thermal Engine

FIN DU DOCUMENT
