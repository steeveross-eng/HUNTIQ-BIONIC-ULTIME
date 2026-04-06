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
- [x] NORME OFFICIELLE A->L — Cache Institutionnel BCE-4X
  - Module `institutional_cache.py`: cache permanent JSON
  - 6 endpoints `/api/v1/bdre/cache/*` (consultation legere < 1ms)
  - Orchestrateur cache-first: consultation cache AVANT calcul A*
  - Certification territoire: pipeline lourd offline
  - Audit non-regression: verification 0 objets manquants
  - Tests: 10/10 pytest PASS + E2E curl PASS
- [x] BUG FIX: Alimentation 3/4 -> 4/4
  - Promotion candidats apres exclusion BCE-4X dans engine.py
- [x] BUG FIX: Routes V-shape (detour nord) -> routes directes
  - Junction directionnelle (Dijkstra, minimise trail+penetration)
  - Seuils adaptatifs (L0/L1: 3.5x, L2: 5.0x)
  - Rejet L2 si penetration > distance directe
  - Terrain-aware corridor detection pour zones sans OSM
  - Ratio final: 1.0-1.1x, VA_AU_NORD=NON, Corridor 100%, BDRE 86.5

## Endpoints cles

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/api/v1/hunt/orchestrate` | POST | Orchestration session chasse |
| `/api/v2/alimentation/analyze` | POST | Analyse sites alimentation |
| `/api/v1/bdre/cache/objects/{t}` | GET/POST | Objets institutionnels |
| `/api/v1/bdre/cache/routes/{t}` | GET | Routes pre-certifiees |
| `/api/v1/bdre/cache/corridors/{t}` | GET | Corridors virtuels |
| `/api/v1/bdre/cache/certify/{t}` | POST | Certification offline |
| `/api/v1/bdre/cache/audit/{t}` | GET | Audit non-regression |

## Backlog

### P0 (Aucun — tout P0 complete)

### P1 (En attente directive STEEVE-MAX)
- Validation utilisateur des corrections bugs
- Validation visuelle frontend routes directes + 4/4 alimentation

### P2 (GELE — NE PAS TOUCHER)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (STRICTEMENT INTERDIT)
