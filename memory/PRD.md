# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 71 modules + Hunt Orchestrator Engine
- **Frontend:** React + Zustand + Leaflet, StandsMapLayer connecte a l'Orchestrateur
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS) — source unique, DYNAMIQUE
- **Terrain:** Overpass API enrichi + Cache persistant 3 niveaux (memoire + fichier gzip + Overpass)
- **Securite:** 7 verrous ULTRA-MAX++ v3.0 + Firewall geometrique anthropique

## Implemente et Valide

### ORDRE 1: Firewall ULTRA-MAX++ permanent (2026-03-29)
- Fonction canonique: `_point_intersects_anthropic(lat, lng)` — Shapely point-in-polygon
- Injecte dans TOUS les pipelines: corridors, zones, choix_affuts, access_engine
- Couverture: 101K polygones (urbain 47K + routes 70K + infra 47K)
- GOVERNANCE.md Section 9: regle permanente documentee

### ORDRE 2: Cache terrain persistant (2026-03-29)
- 3 niveaux: memoire (<1ms) > fichier gzip (~250ms) > Overpass (5-8s)
- ZERO appel Overpass apres 1ere visite
- SHA256 + TTL 30j + invalidation API
- Meteo/vent/scoring DYNAMIQUES (jamais caches)
- Benchmarks: cold 7531ms → persistent 532ms (14x) → memoire 260ms

### CORRECTIF: Regression zones — META-EXCLUSION (2026-03-29)
- Remplacement META-EXCLUSION totale par filtrage point-in-core-urban
- 22/191 corridors + 1/16 zones preserves en zone forestiere

### Trail-First Routing — Hybride 2 Phases (2026-03-29)
- BFS composantes connexes + A* sentier + A* grille terrain 25m
- Cascade: sentier (80) > hybride (75) > terrain (65) > direct (20)
- Frontend: 2 segments visuels + marqueur jonction

### Correctifs anterieurs (2026-03-28)
- Vent/odeurs: placement DOWNWIND corrige
- feedingSites/fixedBlinds connectes
- Overpass parallele (ThreadPoolExecutor)
- Indicateur chargement Leaflet

## Backlog
- P0: Attente validation STEEVE-MAX sur Firewall + Cache persistant
- P2: Phase 2D shadcn + utils (GELE)
- P2: Pression de chasse historique
- P2: BSAA-2 (GELE)
- P2: Merge Work1 → main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- Firewall ULTRA-MAX++: Section 9 GOVERNANCE.md — PERMANENT
- WindFlowLayer v5.1: LOCK DEFINITIF
- MERGE Work1 → main: STRICTEMENT INTERDIT
