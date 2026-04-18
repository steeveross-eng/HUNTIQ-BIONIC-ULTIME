# HUNTIQ V11-SUPRA — PRD
## ENGINE CONTAMINATION-Omega OPTIMISE — SOURCE = AFFUTS
**MAJ:** 2026-04-17 | **CONTAMINATION-Omega** | **15 CONES** | **ZERO WAYPOINT**

## Architecture V11-SUPRA
- LiDAR 121pts + IRDA drainage + Meteo 37p + IA Vision
- CONTAMINATION-Omega: source = AFFUTS OPTIMAUX exclusivement

## ENGINE CONTAMINATION-Omega
- 5 affuts x 3 intensites = 15 cones Catmull-Rom
- FORT: #D32F2F, portee longue, opacity 0.25
- MOYEN: #FF7043, portee moyenne, opacity 0.20
- FAIBLE: #FFAB91, portee courte, opacity 0.15
- Vent reel (ECCC/NOAA), terrain-aware (canopy, rugosite, soil_moisture)
- ZERO waypoint, ZERO smoothing

## Couches V11 (7 actives)
1. Zones 5 types 29vtx | 2. Corridors 12 28pts | 3. Contamination 15 cones
4. Vent Ventusky | 5. Hotspots 10 | 6. Salines 4 | 7. Affuts 5

## Endpoints
- GET /api/v8/institutional/territoire — V11-SUPRA
- GET /api/v8/institutional/terrain-v10 — Profil V11

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
