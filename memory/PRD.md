# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 71 modules + Hunt Orchestrator Engine
- **Frontend:** React + Zustand + Leaflet, StandsMapLayer connecte a l'Orchestrateur
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS) — source unique, DYNAMIQUE
- **Terrain:** Overpass API enrichi + Cache persistant 3 niveaux (memoire + fichier gzip + Overpass)
- **Securite:** 7 verrous ULTRA-MAX++ v3.0 + Firewall geometrique anthropique

## Implemente et Valide

### CORRECTIF: 4 Regressions critiques (2026-03-29)
- R1: Firewall ULTRA-MAX++ restaure — META-EXCLUSION totale quand centre urbain
  - Quebec City: 0 features | Rimouski: 209 features (16 zones + 193 corridors)
- R2: Cache terrain purge — reconstruction propre uniquement apres firewall actif
- R3: Saline descriptions — fallback + bouton retry dans NutritionPointDetailPanel
- R4: Centrage map — waypoint selectionne > savedPosition (priorite corrigee)

### Firewall ULTRA-MAX++ permanent (2026-03-29)
- `_point_intersects_anthropic(lat, lng)` — Shapely point-in-polygon
- Injecte dans TOUS les pipelines: corridors, zones, choix_affuts, access_engine
- META-EXCLUSION totale si centre d'analyse en zone urbaine

### Cache terrain persistant (2026-03-29)
- 3 niveaux: memoire (<1ms) > fichier gzip (~250ms) > Overpass (5-8s)
- SHA256 + TTL 30j + invalidation API
- Meteo/vent/scoring DYNAMIQUES (jamais caches)

### Trail-First Routing — Hybride 2 Phases (2026-03-29)
- BFS composantes connexes + A* sentier + A* grille terrain 25m

### Correctifs anterieurs (2026-03-28)
- Vent/odeurs: placement DOWNWIND corrige
- Overpass parallele (ThreadPoolExecutor)

## Backlog
- P0: Attente validation STEEVE-MAX sur correctifs 4 regressions
- P2: Phase 2D shadcn + utils (GELE)
- P2: Pression de chasse historique
- P2: BSAA-2 (GELE)
- P2: Merge Work1 → main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- Firewall ULTRA-MAX++: Section 9 GOVERNANCE.md — PERMANENT
- WindFlowLayer v5.1: LOCK DEFINITIF
- MERGE Work1 → main: STRICTEMENT INTERDIT
