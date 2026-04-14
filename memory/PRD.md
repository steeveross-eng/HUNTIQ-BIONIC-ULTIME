# HUNTIQ V6 — PRD
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX
**MAJ:** 2026-04-14

## Stack: FastAPI + React + Leaflet + MongoDB

## Deploiements session courante

### CAMERA-Omega-ULTRA — 21 marques, popup riche, ZERO texte libre
### AFFUT-IA-Omega-PLUS — Moteur IA affuts, salines 20-100m, 5 refs scientifiques
### SUPRA-REACT-Omega — SUPRA v2 reconnecte, territory_bridge, 9 moteurs
### TERRITOIRE-FULL-RESTORE — 18 couches, 5 especes, PROTECTED_LAYERS, PRESET
### P1-ENGINE-Omega (12 moteurs): OPTIMIZATION, HEAT-UNIFY, PREDICT-BEHAVIOR, ECO-DYNAMICS, TERRAIN-RISK-PLUS, CONSISTENCY, SCIENCE-CHECK, SHIELD-PLUS, GLOBAL-CERT, CMP-CERT, TRACE-LOG, BRANCH-REALIGN
### CRITICAL-MODULES-Omega (7 modules): CAMERA-SEC, M5-OFFLINE-ULTRA, DEM-LIDAR, SIEF-ECOFORESTERIE, LIDAR-FUSION, SIEF-ECO, MVT-TILES
### GUIDE-PRO-Omega — UI panel integre dans CARTE avec 4 modes (LIVE, POINT, ZONE, ESPECE)

## Architecture endpoints
- /api/v1/camera/* (camera engine, brands, popup-data)
- /api/v1/affuts-ia/* (generate, list, explain, references)
- /api/v1/vision/* (analyses, trajectories, hotspots, stats, individuals, notifications, anomalies, territories)
- /api/v1/p1/* (12 moteurs, 14 endpoints)
- /api/v1/critical/* (7 modules, 9 endpoints)
- /api/v1/guide-pro/* (15 endpoints)
- /api/map/preload (cache + GZip)
- /api/v6/nutrition-intelligence/* (SUPRA + territory_ia)
- /api/v6/supra/advanced/* (terrain, risk, recommendations, correlation)

## Backlog COMPLET
- [x] P1-ENGINE-Omega (12 moteurs)
- [x] Critical Modules (7 modules)
- [x] GUIDE-PRO-Omega UI
- [x] Cercle 600m SUPPRIME
- [x] 5/5 especes avec salines

## Performance
- Map preload: 150ms (< 1s)
- GZip: actif (500+ bytes)
- Cache serveur: TTL 5min
- Cache client: sessionStorage

FIN DU DOCUMENT
