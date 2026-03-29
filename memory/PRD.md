# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 71 modules + Hunt Orchestrator Engine
- **Frontend:** React + Zustand + Leaflet, StandsMapLayer connecte a l'Orchestrateur
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS) — source unique
- **Terrain:** Overpass API enrichi (sentiers + waterways + clearings + forest) + Grille terrain A* + Cache 2 niveaux
- **Securite:** 7 verrous ULTRA-MAX++ v3.0

## Implemente et Valide

### Trail-First Routing — Hybride 2 Phases (2026-03-29)
- Algorithme BFS pour detection composantes connexes du graphe sentiers
- Phase 1 (SENTIER): Entree → noeud sentier accessible le plus proche de l'affut (A* graphe OSM)
- Phase 2 (TERRAIN): Noeud sentier → affut (A* grille terrain, resolution 25m)
- Cascade 4 strategies: sentier complet (80) > hybride (75) > terrain pur (65) > direct (20)
- Frontend: rendu visuel 2 segments (vert continu + teal tirete) + marqueur jonction
- Metadonnees: trail_segment_end_idx, phase1/phase2 distances, junction coords

### Moteur Acces Terrain-Aware v2 (2026-03-29)
- Grille navigation terrain avec A* pondere (35m resolution)
- Priorisation: sentiers OSM > bords ruisseau (1.2x) > clairieres (1.4x) > foret ouverte (4x)
- Evitement: foret dense (8x), marecages (50x), eau (999x), contamination olfactive (15x)
- Requete Overpass enrichie: waterways + clearings + grassland/scrub/heath
- Frontend: styles distincts par type corridor (cyan ruisseau, vert clairiere, teal terrain)

### Correctif Placement Vent/Odeurs (2026-03-29)
- Fix: affuts places DOWNWIND (aval vent) au lieu d'UPWIND
- downwind_rad = radians((wind_direction_deg + 180) % 360)
- Scores: 12 → 17-38 (amelioration nette)

### Correctifs P1 (2026-03-28)
- B2: Overpass parallele (ThreadPoolExecutor) — cold cache -21% a -71%
- B5: Indicateur "Analyse terrain..." (Leaflet Control)

### Correctifs P0 (2026-03-28)
- A1/A2: feedingSites + fixedBlinds connectes
- B1: Timeout Overpass reduit (8s)
- B4: Cache key elargie (1.1km)

## Backlog
- P0: Attente validation STEEVE-MAX sur Trail-First Routing
- P2: Cache persistant terrain (elimine cold cache)
- P2: Session dynamique (matin/soir)
- P2: Pression de chasse historique
- P2: Phase 2D shadcn + utils (GELE)
- P2: BSAA-2 (GELE)
- P2: Merge Work1 → main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- WindFlowLayer v5.1: LOCK DEFINITIF
- MERGE Work1 → main: STRICTEMENT INTERDIT
