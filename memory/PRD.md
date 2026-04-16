# HUNTIQ V8 — PRD
## V8-FRONTEND-PHASE-A-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **7/7 PASS** | **FRONTEND+BACKEND INTEGRE**

## Architecture V8 Complete

### Backend Engines (V8 National)
- `router.py` — Score V8, Biome, Habitat
- `referentials.py` — Donnees de reference 13 provinces
- `exclusion_engine.py` — 22 criteres BCE-4X
- `governance.py` — Master Switch PREVIEW/PUBLIC
- `map_bundle.py` — Zones organiques, corridors Bezier, affuts (TTFB <150ms, SANS auth)
- `p1_pipelines.py` — Stubs LiDAR/IRDA (acces institutionnel requis)
- `phase_a_engines.py` — Relocalisation + Salines V8 (SANDBOX)

### Frontend V8
- `useMapBundleV8.js` — Hook bundle V8 unique (zones+corridors+affuts)
- `useBionicScoringV8.js` — Hook Score V8 National
- `usePhaseAV8.js` — Hook Phase A (Relocalisation + Salines)
- `BionicLayersV8.jsx` — Rendu organique Leaflet (polygones, courbes Bezier, triangles)
- `PhaseALayerV8.jsx` — Couche carte Phase A (marqueurs relocalisation + salines)
- `PhaseAPanelV8.jsx` — Panneau lateral Phase A (top-3, scores, explications)
- `MonTerritoireBionicPage.jsx` — Page principale TERRITOIRE
- `MapContent.jsx` — Contenu carte Leaflet (toutes couches)
- `TerritoireToolbar.jsx` — Barre outils avec bouton Phase A

### Rendu V8 conforme STEEVE-MAX
- Zones: polygones organiques 12+ vertices, contours opaques 2.5px, interieur TRANSPARENT
- Corridors: courbes Bezier 9 points, 5 niveaux intensite, opacite 0.85
- Affuts: triangles orientes (direction vent), halo discret, 3 qualites
- Phase A Relocalisation: cercles organiques + halo + rang numerote + lignes connexion
- Phase A Salines: losanges organiques + halo
- ZERO micro-points, ZERO rectangles, ZERO artefacts

## Completed Work
1. V8-INTEGRATION-Omega Phases 1-5 (Score V8 React, V8IntelPanel, 13 provinces)
2. EXCLUSION-ENGINE-V8 (22 criteres BCE-4X)
3. V8-PREVIEW-Omega + GOVERNANCE-Omega (Master Switch, PREVIEW tag, role-based)
4. MAP-LAYERS-Omega (Bundle /api/v8/map/bundle, TTFB <150ms, sans auth)
5. UI-V8-FORCE-Omega (BionicLayersV8 exclusif, V7 purge)
6. SCORE-V8-PERF-Omega (Cache Open-Meteo, ~500ms)
7. TERRITOIRE-V8-FIX-Omega (Couches carte stables)
8. V8-VISUAL-STEVE-MAX-Omega (Zones organiques, corridors Bezier)
9. V8-REINTEGRATION-PHASE-A-Omega Backend (Relocalisation + Salines V8)
10. V8-FRONTEND-PHASE-A-Omega (Integration UI complete)

## Key API Endpoints
- `GET /api/v8/map/bundle` — Bundle carte (NO AUTH, cached)
- `GET /api/v8/national/score` — Score V8 National
- `GET /api/v8/governance/state` — Etat governance
- `GET /api/v8/map/relocalisation` — Relocalisation V8 (Phase A)
- `GET /api/v8/map/salines` — Salines V8 (Phase A)
- `GET /api/v8/map/phase-a/status` — Status Phase A

## Upcoming Tasks
- P0: V8-REINTEGRATION-PHASE-B (Scenario Engine, Cost Surface, Temporal V1)
- P1: LiDAR MRNF multi-provincial (stubs actuels)
- P1: IRDA pedologie Quebec (stubs actuels)

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

FIN DU DOCUMENT
