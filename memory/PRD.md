# HUNTIQ-V6 — PRD (Product Requirements Document)
## Protocole BCE-4X | ULTRA-MAX++ | Autorite STEEVE-MAX

---

## Enonce du Probleme Original
Reconstruction du repository HUNTIQ-V6 a partir de la branche `bionic-v3-dev` de HUNTIQ-V5, avec gouvernance stricte BCE-4X, audits multi-versions (V1-V6), implementation de nouvelles fonctionnalites (Trail-First Routing, Terrain Cache, ULTRA-MAX++ Firewall), et purge complete des pipelines V1-V5 legacy.

## Architecture
- **Backend:** FastAPI, 84+ modules moteur, Shapely (geo-fencing), A* pathfinding
- **Frontend:** React, Leaflet, modular territory analysis
- **Cache:** Fichiers `.json.gz` persistants (terrain, OSM)
- **Branche active:** `Work1` (merge `main` STRICTEMENT INTERDIT)

## Ce qui est implemente

### Purge V1-V5 (Fevrier 2026 — Phase A-D) — EN ATTENTE VALIDATION
- **Phase A:** Double-clic waypoint SUPPRIME. MapInteractionLayer purifie GPS-only (362->107 lignes). 3 sites appel mis a jour.
- **Phase B (v2):** Double halo salines ELIMINE. CAUSE RACINE: `StandsMapLayer._feeding_sites_display` (markers dores navy #1a1a2e). AUSSI: centroides alimentation BionicCorridorsV6Layer exclus (3 modes). DOM Evidence: 4 V6/SUPRA markers, 0 legacy.
- **Phase C:** Firewall corridors renforce (5 points echantillonnes: 0%, 25%, 50%, 75%, 100%)
- **Phase D:** Rapport BCE-4X v2 genere avec cause racine corrigee, commite Work1

### Fonctionnalites Anterieures
- Trail-First Routing (A* hybride sentier+terrain)
- Cache terrain persistant `.json.gz`
- Firewall ULTRA-MAX++ (`_point_intersects_anthropic`, multi-point)
- Correction geolocation waypoint
- SUPRA V2 fallback UI salines

## Backlog Priorise

### P0 (BLOQUANT — En attente validation STEEVE-MAX)
- Validation rapport BCE-4X v2 (Phases A-D)

### P0 (SUSPENDU — Conditionne a validation Phase B)
- Point 5: Acces aux affuts V6 (logique circulation + vegetation)
- Point 6: GOVERNANCE.md Section 14
- Point 7: Clause non-regression

### P1
- Restauration `auto_optimization.py` (module `optimization_engine`)

### P2 (GELE)
- Phase BSAA-2: Implementation module Social Ads
- Phase 2D: Purge shadcn/utils frontend
- Pression historique -> moteur `choix_affuts`
- Merge `Work1` -> `main` (STRICTEMENT INTERDIT)

## Fichiers Modifies (Purge V1-V5)
1. `frontend/src/modules/map_interaction/components/MapInteractionLayer.jsx` — Reecrit GPS-only
2. `frontend/src/components/territoire/map/MapContent.jsx` — Props purgees
3. `frontend/src/components/territoire/MonTerritoireBionic.jsx` — Props purgees
4. `frontend/src/modules/territory/components/WaypointMap.jsx` — Props purgees
5. `frontend/src/components/territoire/StandsMapLayer.jsx` — feeding_sites SUPPRIME
6. `frontend/src/components/territoire/BionicCorridorsV6Layer.jsx` — alimentation centroides exclus
7. `frontend/src/components/territoire/NutritionPointsLayer.jsx` — useEffect legacy remplace
8. `backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py` — Firewall multi-point
9. `backend/core/scoring_pipeline/corridors_v10/engine.py` — Firewall multi-point
