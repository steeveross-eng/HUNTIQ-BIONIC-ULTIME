# PRD — HUNTIQ BIONIC V6 | BCE-4X GOLDEN V6+

## Probleme original
Application de routage terrain pour la chasse (affuts, corridors, zones) avec pathfinding A* et integration OSM/Overpass. Gouvernance stricte BCE-4X GOLDEN V6+ sous autorite COMMANDANT STEEVE-MAX.

## Architecture
- Backend: FastAPI + A* Pathfinding + OSM/Overpass
- Frontend: React 19 + Leaflet Maps
- Modules: 84+ engines backend (BDRE, Terrain Nav, Hunt Orchestrator, Access Engine, etc.)
- Routing: Virtual corridor injection (GUIDANCE) + BCE-4X exclusions (cout 1,000,000)
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
- [x] NORME OFFICIELLE A→L — Cache Institutionnel BCE-4X
  - Module `institutional_cache.py`: cache permanent JSON (affuts, zones, corridors, routes)
  - 6 nouveaux endpoints `/api/v1/bdre/cache/*` (consultation legere < 1ms)
  - Orchestrateur cache-first: consultation cache AVANT calcul A*
  - Certification territoire: pipeline lourd offline (graphe + GUIDANCE + BCE-4X)
  - Audit non-regression: verification 0 objets manquants
  - Tests: 10/10 pytest PASS + E2E curl PASS
  - Rapport: AFFUTS_ZONES_NON_REGRESSION_REPORT.md
- [x] BUG FIX: Alimentation 3/4 → 4/4 (promotion candidats apres exclusion BCE-4X)
  - Fichier: `alimentation_v2/engine.py` — ajout logique de promotion
- [x] BUG FIX: Routes V-shape (detour nord) → routes directes
  - Garde-fou ratio detour (MAX 2.5x) dans `terrain_router.py` et `fallback_chain.py`
  - Cascade: L0/L1/L2 rejetes si detour excessif → L3 terrain-grid-A* (route directe)
  - Ratio apres fix: 1.0x-1.1x (avant: 3.7x-7.6x)

## Endpoints cles

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/api/v1/hunt/orchestrate` | POST | Orchestration session de chasse |
| `/api/v2/alimentation/analyze` | POST | Analyse sites alimentation |
| `/api/v1/bdre/cache/objects/{t}` | GET | Consultation objets institutionnels |
| `/api/v1/bdre/cache/objects/{t}` | POST | Enregistrement objet INTOUCHABLE |
| `/api/v1/bdre/cache/routes/{t}` | GET | Consultation routes pre-certifiees |
| `/api/v1/bdre/cache/corridors/{t}` | GET | Consultation corridors virtuels |
| `/api/v1/bdre/cache/certify/{t}` | POST | Certification territoire (offline) |
| `/api/v1/bdre/cache/audit/{t}` | GET | Audit non-regression |
| `/api/v1/bdre/health` | GET | Sante BDRE (17 endpoints) |

## Backlog

### P0 (Aucun — tout P0 est complete)

### P1 (En attente directive STEEVE-MAX)
- Validation utilisateur des corrections bugs
- Validation visuelle frontend des routes directes

### P2 (GELE — NE PAS TOUCHER)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 → main (STRICTEMENT INTERDIT)
