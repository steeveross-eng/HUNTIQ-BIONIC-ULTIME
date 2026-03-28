# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 71 modules + Hunt Orchestrator Engine (A*, Overpass, Open-Meteo)
- **Frontend:** React + Zustand + Leaflet, StandsMapLayer connecte a l'Orchestrateur
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS) — source unique
- **Terrain:** Overpass API (OSM) + ThreadPoolExecutor parallele (3 miroirs) + Cache memoire 2 niveaux
- **Securite:** 7 verrous ULTRA-MAX++ v3.0

## Implemente et Valide

### Correctifs P1 Performance + UX (2026-03-28)
- B2: Requetes Overpass PARALLELES (ThreadPoolExecutor, premier gagne) — cold cache -21% a -71%
- B5: Indicateur "Analyse terrain..." (Leaflet Control, spinner dore, transitoire)

### Correctifs P0 Orchestrateur (2026-03-28)
- A1: feedingSites connecte (alimentationV2Data -> StandsMapLayer)
- A2: fixedBlinds connecte (savedPlaces type affut -> StandsMapLayer)
- B1: Timeout Overpass reduit (20s -> 8s), cold cache -76%
- B4: Cache key elargie (111m -> 1.1km), navigation sans re-fetch
- Cache key StandsMapLayer corrigee (inclut feedingSites + fixedBlinds)

### Hunt Orchestrator Engine P0 (2026-03-28)
- Backend: orchestrator.py, vent_odeurs.py, choix_affuts.py, access_engine.py
- Frontend: StandsMapLayer.jsx integre dans MapContent.jsx
- 4 facteurs reels: vent/odeur (40%), sentier OSM (25%), alimentation (20%), eau (15%)
- Routage A* sur graphe OSM reel avec fallback Dijkstra
- ZERO donnee artificielle, ZERO Math.random

### Audit Post-Purge, Purge Legacy, WindFlowLayer v5.1 LOCK
- Audit: 5 refs corrigees, WeatherEngineV3, ZERO ref fantome
- Purge: 280+ fichiers, ~247K lignes
- WindFlowLayer v5.1: Standard Institutionnel

## Backlog
- P2: Cache persistant terrain (fichier/MongoDB, elimine cold cache)
- P2: Session dynamique (matin/soir automatique)
- P2: Pression de chasse historique dans choix_affuts
- P2: Phase 2D shadcn + utils (EN ATTENTE validation)
- P2: BSAA-2 Implementation (GELE)
- P2: Merge Work1 -> main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- WindFlowLayer v5.1: LOCK DEFINITIF
- MERGE Work1 -> main: STRICTEMENT INTERDIT
