# HUNTIQ-V6 — PRD
## Protocole BCE-4X | BIONIC GOLDEN | STEEVE-MAX

## Branche souveraine: STEEVE-MAX-x3200-V6-CORE
## Work1: GELEE

## Etat courant

### EXECUTE ET COMMITE (branche souveraine)
- Phase A: MapInteractionLayer GPS-only
- Phase B: BionicCorridorsV6Layer alimentation centroids exclus + AlimentationV2Layer useEffect
- GOVERNANCE.md: PROTOCOLE BIONIC GOLDEN (11 sections)
- Architecture access_engine_v6: document complet valide par STEEVE-MAX
- Draft Section 14 GOVERNANCE: soumis a validation
- Draft clause non-regression: soumis a validation
- STANDARD GOLDEN Legende: repositionnee en topleft (StandsMapLayer.jsx)
- **access_engine_v6**: Implementation complete backend + frontend + tests (43/43 PASSES)
  - engine.py: Orchestrateur Trail-First Dijkstra + Terrain Grid A*
  - router.py: POST /api/v6/access/compute + /compute-batch + /health
  - osm_trails.py: Graphe sentiers OSM via Overpass API + cache .json.gz
  - access_cost_grid.py: Grille de couts (BASE * PENTE * VEG * OBSTACLE)
  - vegetation_analyzer.py: Analyse vegetation corridors hors-sentier
  - pathfinder_v6.py: A* grille + Dijkstra graphe sentiers
  - segment_classifier.py: Classification 4 couleurs
  - AccessRouteV6Layer.jsx: Layer unique 4 couleurs (vert/bleu/or/rouge)
  - useAccessRoute.js: Hook unique
  - MapContent.jsx: Integration Layer
  - routers.py: Enregistrement routeur
  - Tests: 20 structurels + 10 GOLDEN + 13 API = 43 total

### EN ATTENTE VALIDATION STEEVE-MAX
- Point 6: Section 14 GOVERNANCE.md (draft pret)
- Point 7: Clause non-regression (draft pret)
- **access_engine_v6**: Rapport d'execution livré — en attente validation

### DETTE TECHNIQUE STRUCTURELLE
- Firewall ULTRA-MAX++ (Shapely geo-fencing) a reimplementer sous GOLDEN
- Cache terrain persistant .json.gz (Redis recommande pour production)
- Donnees terrain reelles (DEM, canopy) — actuellement simulees par hash

### GELE
- BSAA-2, Phase 2D, pression historique
- Merge main: STRICTEMENT INTERDIT
