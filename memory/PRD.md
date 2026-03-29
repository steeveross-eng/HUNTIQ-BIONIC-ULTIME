# HUNTIQ-V6 — PRD (Product Requirements Document)
## Protocole BCE-4X | ULTRA-MAX++ | Autorite STEEVE-MAX

---

## Enonce du Probleme Original
Reconstruction du repository HUNTIQ-V6 a partir de la branche `bionic-v3-dev` de HUNTIQ-V5, avec gouvernance stricte BCE-4X, audits multi-versions (V1-V6), et implementation de nouvelles fonctionnalites (Trail-First Routing, Terrain Cache, ULTRA-MAX++ Firewall, module BSAA).

## Architecture
- **Backend:** FastAPI, 84+ modules moteur, Shapely (geo-fencing), A* pathfinding
- **Frontend:** React, Leaflet, modular territory analysis
- **Cache:** Fichiers `.json.gz` persistants (terrain, OSM)
- **Branche active:** `Work1` (merge `main` STRICTEMENT INTERDIT)

## Ce qui est implemente

### Infrastructure & Gouvernance
- Import et certification du repository HUNTIQ-V6
- Framework de gouvernance BCE-4X / ULTRA-MAX++ / STEEVE-MAX
- Branche `Work1` operationnelle avec historique complet
- Documents: GOVERNANCE.md, SECURITY_POLICY.md, EMERGENT_PROTOCOL.md

### Audits Completes
- Audit moteur (84+ engines valides)
- Audit coherence inter-modules (Phase 5B)
- Audit historique V1-V6 (Phase 5C) — identification `auto_optimization.py` manquant
- Architecture BSAA (Phase BSAA-0, BSAA-1)

### Fonctionnalites Techniques
- Trail-First Routing (A* hybride sentier+terrain)
- Cache terrain persistant `.json.gz`
- Firewall ULTRA-MAX++ (`_point_intersects_anthropic`, multi-point 5 echantillons)
- Correction geolocation waypoint (priorite `selectedWaypointForZones`)
- SUPRA V2 fallback UI salines

### Purge V1-V5 (Fevrier 2026 — Phase A-D)
- **Phase A:** Double-clic waypoint SUPPRIME (MapInteractionLayer purifie GPS-only)
- **Phase B:** Double halo salines ELIMINE (exclusion centroides alimentation de BionicCorridorsV6Layer)
- **Phase C:** Firewall corridors renforce (5 points echantillonnes au lieu de 1)
- **Phase D:** Rapport BCE-4X genere et commite

## Backlog Priorise

### P0 (Bloquant)
- [COMPLETE] Purge V1-V5 frontend (Phases A-D)
- [EN ATTENTE VALIDATION] Validation STEEVE-MAX du rapport BCE-4X

### P1 (Important)
- Restauration `auto_optimization.py` → module `optimization_engine`
- Rapport integration: `architecture/auto_optimization_integration.md`
- Validation et commit restauration

### P2 (Futur — GELE)
- Phase BSAA-2: Implementation module Social Ads
- Phase 2D: Purge shadcn/utils frontend
- Pression historique → moteur `choix_affuts`
- Merge `Work1` → `main` (STRICTEMENT INTERDIT)

## Fichiers Cles
- `/app/frontend/src/modules/map_interaction/components/MapInteractionLayer.jsx`
- `/app/frontend/src/components/territoire/NutritionPointsLayer.jsx`
- `/app/frontend/src/components/territoire/BionicCorridorsV6Layer.jsx`
- `/app/backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py`
- `/app/backend/core/scoring_pipeline/corridors_v10/engine.py`
- `/app/HUNTIQ-V6-import/audit/purge_v1v5_bce4x_validation.md`
