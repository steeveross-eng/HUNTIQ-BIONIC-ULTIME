# HUNTIQ V11-SUPRA — PRD
## DONNEES 1m ACTIVEES — TERRITOIRE 100% INSTITUTIONNEL
**MAJ:** 2026-04-17 | **V11-LIDAR-IRDA-SUPRA** | **FIABILITE 1.0**

## Architecture V11-SUPRA-INSTITUTIONNEL
- LiDAR WCS 1m: 121pts grille (11x11), pente gradient 3x3
- IRDA pedologie: drainage 7 classes, sol reel, hydrologie
- Meteo: 37 params ECCC/NOAA
- IA Vision: canopy, strate, feuillus, zones probables

## Pipeline
LiDAR 121pts + IRDA drainage + Meteo 37p + IA → terrain V11 → toutes couches

## Couches V11 (7 actives)
1. Zones — 5 types, 29vtx Catmull-Rom, terrain LiDAR + IRDA
2. Corridors — 12/espece, 28pts, 6 profils, cost_surface V11
3. Contamination — cone 18pts Catmull-Rom, vent reel
4. Vent — WindFlowLayer Ventusky (ECCC/NOAA)
5. Hotspots — 10, fusion multi-engines
6. Salines — 4, soil moisture reel
7. Affuts — 5, terrain LiDAR + vent reel

## Endpoints
- GET /api/v8/institutional/territoire — V11-SUPRA (source unique)
- GET /api/v8/institutional/terrain-v10 — Profil terrain V11 complet
- GET /api/v3/weather/windgrid — Vent grille reel

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
