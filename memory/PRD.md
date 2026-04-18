# HUNTIQ V10-SUPRA — PRD
## TERRITOIRE V10-SUPRA — FUSION TOTALE REEL + IA
**MAJ:** 2026-04-17 | **V10-SUPRA** | **FIABILITE 1.0** | **ZERO SIMULE**

## Architecture V10-SUPRA
- /territoire consomme V10-SUPRA exclusivement
- TOUTES couches recalculees depuis donnees REELLES + IA
- ENGINE TERRAIN V10-SUPRA: source absolue de verite

## Couches V10-SUPRA (7 actives)
1. Zones — 5 types (rut/alim/repos/eau/thermique), Catmull-Rom 35vtx
2. Corridors — 12/espece, Catmull-Rom 31pts, 6 profils especes, 5 niveaux
3. Contamination — Cone Catmull-Rom 18pts, terrain-aware (canopy/rugosite)
4. Vent — WindFlowLayer Ventusky (ECCC/NOAA reel)
5. Hotspots — Fusion multi-engines 1-5
6. Salines — Soil moisture reel
7. Affuts — Terrain reel + vent reel

## Donnees Reelles
- MNT: SRTM 25pts grille (Open-Meteo Elevation)
- Meteo: 37 params (ECCC/NOAA GFS)
- Sol: temperature + moisture reels
- Fiabilite: 1.0

## Endpoints
- GET /api/v8/institutional/territoire — V10-SUPRA (source unique)
- GET /api/v8/institutional/terrain-v10 — Profil terrain complet
- GET /api/v3/weather/windgrid — Vent grille reel

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
