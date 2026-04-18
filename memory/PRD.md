# HUNTIQ V10 — PRD
## TERRAIN V10-SUPRA ACTIF — 100% REEL + IA — BIONIC OS SUPRA
**MAJ:** 2026-04-17 | **V10-SUPRA** | **FIABILITE 1.0**

## Architecture V10-SUPRA-INSTITUTIONNEL
- ENGINE V10-SUPRA TERRAIN: source absolue de verite
- 24 Engines + SUPRA-DONNEES, 4 Piliers, ESI-Omega
- Donnees: REELLES (Open-Meteo SRTM + Forecast ECCC/NOAA) + IA Vision

## ENGINE V10-SUPRA TERRAIN
### Ingestion Reelle
- MNT: SRTM 25pts grille (Open-Meteo Elevation)
- Meteo: 37 parametres (16 current + 21 hourly)
- Sol: temperature 0/6cm, moisture 0-1/1-3cm
- Radiation: direct + diffuse W/m2
- Atmosphere: pression, CAPE, visibilite

### IA Vision
- Canopy, strate, feuillus: estimes depuis donnees reelles
- Zones probables: repos, alimentation, thermique, humide

### Surfaces Derivees
- Cost surface, thermal comfort, olfactive diffusion
- Hydro index, connectivity

### Fiabilite
- 1.0 quand toutes sources actives (SRTM + meteo + IA)
- 0.65 sans elevation
- 0.45 sans meteo
- STUB: LiDAR WCS 1m, IRDA pedologie

## Endpoints
- GET /api/v8/institutional/terrain-v10 — Profil complet V10
- GET /api/v8/institutional/territoire-reel — Territoire enrichi
- GET /api/v8/institutional/territoire — Territoire classique
- GET /api/v3/weather/windgrid — Vent grille reel

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
