# HUNTIQ V9 — PRD
## VERITE TOTALE CARTOGRAPHIEE — TERRITOIRE 10000% VERITE
**MAJ:** 2026-04-17 | **V9-PURE** | **RAPPORT VERITE COMPLET**

## Architecture V9-INSTITUTIONNEL
- 7 couches actives, 2 inactives (heatmap, wind_vectors statiques)
- 0 couche legacy/debug/fallback
- ESI-Omega: 8/8 CONFORME

## Couches Actives
1. corridors — L.polyline Catmull-Rom 22pts, ENGINE 02
2. zones — L.polygon Catmull-Rom 31vtx, ENGINE 01
3. vent — Canvas 2500 particules, WindFlowLayer (Open-Meteo REEL)
4. contamination — L.polygon cone 4pts, ENGINE 05
5. hotspots — L.circleMarker 5 niveaux, ENGINE 04
6. salines — L.circleMarker, ENGINE 07
7. affuts — L.circleMarker+divIcon, ENGINE 03

## Donnees
- SIMULEES: terrain (seed deterministe) → zones, corridors, affuts, salines, hotspots
- REELLES: Open-Meteo/ECCC/NOAA → vent, meteo
- P1 STUB: LiDAR WCS, IRDA pedologie (acces requis)

## Rapport complet: /app/memory/RAPPORT_VERITE_TERRITOIRE_V9.md

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
