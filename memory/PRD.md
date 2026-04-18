# HUNTIQ V9 — PRD
## ENGINE SUPRA-DONNEES ACTIVE — BIONIC 100% OPTIMISE
**MAJ:** 2026-04-17 | **DONNEES REELLES** | **SUPRA-DONNEES-Omega**

## Architecture V9-INSTITUTIONNEL
- 24 Engines + SUPRA-DONNEES central
- 4 Piliers, ESI-Omega Guardian
- Donnees REELLES: Open-Meteo Elevation (SRTM) + Forecast (ECCC/NOAA)

## ENGINE SUPRA-DONNEES-Omega
- MNT: Open-Meteo Elevation API (SRTM ~90m, 9 pts grille)
- Meteo: Open-Meteo Forecast (vent, temp, sol, precipitation)
- Sol: soil_temperature + soil_moisture reels
- Fiabilite: 0.85 (REEL) vs 0.30 (ESTIME fallback)
- Validation: outliers, coherence, bornes
- Distribution: terrain enrichi pour tous engines

## Endpoints
- GET /api/v8/institutional/supra-donnees — Terrain enrichi reel
- GET /api/v8/institutional/territoire-reel — Territoire + donnees reelles
- GET /api/v8/institutional/territoire — Territoire classique
- GET /api/v3/weather/windgrid — Vent grille reel

## Couches Actives (7)
corridors, zones, vent, contamination, hotspots, salines, affuts

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
