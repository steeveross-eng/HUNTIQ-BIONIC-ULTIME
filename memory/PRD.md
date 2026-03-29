# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 71 modules + Hunt Orchestrator Engine
- **Frontend:** React + Zustand + Leaflet, StandsMapLayer connecte a l'Orchestrateur
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS) — source unique
- **Terrain:** Overpass API enrichi (sentiers + waterways + clearings + forest) + Grille terrain A* + Cache 2 niveaux
- **Securite:** 7 verrous ULTRA-MAX++ v3.0

## Implemente et Valide

### Moteur Acces Terrain-Aware v2 (2026-03-29)
- Grille navigation terrain avec A* pondéré (35m resolution)
- Priorisation: sentiers OSM > bords ruisseau (1.2x) > clairières (1.4x) > forêt ouverte (4x)
- Evitement: forêt dense (8x), marécages (50x), eau (999x), contamination olfactive (15x)
- Requête Overpass enrichie: waterways + clearings + grassland/scrub/heath
- Frontend: styles distincts par type corridor (cyan ruisseau, vert clairière, teal terrain)

### Correctif Placement Vent/Odeurs (2026-03-29)
- Fix: affûts placés DOWNWIND (aval vent) au lieu d'UPWIND
- downwind_rad = radians((wind_direction_deg + 180) % 360)
- Scores: 12 → 17-38 (amélioration nette)

### Correctifs P1 (2026-03-28)
- B2: Overpass parallèle (ThreadPoolExecutor) — cold cache -21% a -71%
- B5: Indicateur "Analyse terrain..." (Leaflet Control)

### Correctifs P0 (2026-03-28)
- A1/A2: feedingSites + fixedBlinds connectés
- B1: Timeout Overpass réduit (8s)
- B4: Cache key élargie (1.1km)

## Backlog
- P2: Cache persistant terrain (elimine cold cache)
- P2: Session dynamique (matin/soir)
- P2: Pression de chasse historique
- P2: Phase 2D shadcn + utils (GELÉ)
- P2: BSAA-2 (GELÉ)
- P2: Merge Work1 → main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- WindFlowLayer v5.1: LOCK DEFINITIF
- MERGE Work1 → main: STRICTEMENT INTERDIT
