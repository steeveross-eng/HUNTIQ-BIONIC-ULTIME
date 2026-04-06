# PRD — HUNTIQ BIONIC V6 | BCE-4X GOLDEN V6+

## Probleme original
Application de routage terrain pour la chasse (affuts, corridors, zones) avec pathfinding A* et integration OSM/Overpass. Gouvernance stricte BCE-4X GOLDEN V6+ sous autorite COMMANDANT STEEVE-MAX.

## Architecture
- Backend: FastAPI + A* Pathfinding + OSM/Overpass
- Frontend: React 19 + Leaflet Maps
- Modules: 84+ engines backend (BDRE, Terrain Nav, Hunt Orchestrator, Access Engine, etc.)
- Governance: BCE-4X / STEEVE-MAX / ZERO LOSS / ZERO REGRESSION

## Ce qui a ete implemente

### Session 2026-04-06
- [x] BCE-4X Territorial Exclusions (cout 1,000,000 pour eau/routes/urbain)
- [x] Terrain Graph fragment connector (composants deconnectes)
- [x] STEEVE-MAX Terrain Guidance (corridors virtuels waypoint LUC + affuts)
- [x] Preuve visuelle 100% corridor adherence (corridor_proof_luc_v2.html)
- [x] Multi-engine BDRE integration orchestrateur
- [x] P2 Gel complet — DIRECTIVE STEEVE-MAX

### Session 2026-04-07
- [x] NORME OFFICIELLE A->L — Cache Institutionnel BCE-4X
  - Module `institutional_cache.py`: cache permanent JSON
  - 6 endpoints `/api/v1/bdre/cache/*` (consultation legere < 1ms)
  - Orchestrateur cache-first: consultation cache AVANT calcul A*
  - Audit non-regression: verification 0 objets manquants
- [x] BUG FIX: Alimentation 3/4 -> 4/4 (promotion candidats)
- [x] BUG FIX: Routes V-shape -> routes directes (junction directionnelle + seuils adaptatifs)
- [x] ORDONNANCE: DESACTIVATION SECURISEE ACCES AUX AFFUTS
  - Inventaire complet: 66 fichiers, 6 geometries, 5 caches, 8 endpoints, 4 couches
  - Archive institutionnelle: `/app/LEGACY_ACCESS_AFFUTS/` (2.7 MB)
  - MODE OFF: Backend (orchestrateur + 6 endpoints) + Frontend (3 couches)
  - Validation: 8/8 tests PASS, 0 regression
  - Donnees PRESERVEES (non supprimees)
  - Reactivation documentee dans CONFIRMATION_DESACTIVATION.md

## Backlog

### P0 (Aucun — tout P0 complete)

### P1 (En attente directive STEEVE-MAX)
- Validation utilisateur de la desactivation securisee

### P2 (GELE — NE PAS TOUCHER)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (STRICTEMENT INTERDIT)
