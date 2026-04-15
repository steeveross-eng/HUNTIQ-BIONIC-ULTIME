# HUNTIQ V7 — PRD
## BCE-4X V7-ULTIME-Omega — SYSTEM-Omega-TOTAL-V4 CERTIFIE
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 100/100** | **V6 SUPPRIME DEFINITIVEMENT**

## Architecture V7-ULTIME CERTIFIEE
```
TERRITOIRE-V7 (canvas strategique — 100% V7)
    ↑ SPATIAL-ENGINE-V7 /analyze-full (GeoJSON natif)
    ↑ SPATIAL-ENGINE-V7 /heatmap
    ↑ SPATIAL-ENGINE-V7 /scoring
SPATIAL-ENGINE-V7 (/api/v7/spatial/* — 7 endpoints)
NUTRITION-ENGINE-V7 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CARTE-2027 (terrain)
```

## V6 SUPPRIME DEFINITIVEMENT
- /api/v1/score-consolide/*: 404
- /api/v6/corridors/analyze-full: 404
- AccessRouteV6Layer: supprime
- router_v6 corridors: supprime server.py
- Score Chasse V6+: recable V7

## V7 Engines (27 endpoints)
- SPATIAL: corridors, zones, heatmap, scoring, amenagement, analyze-full, status
- NUTRITION: soil-layer, nutrients, forage, water, metabolism, attractiveness, status
- SUPRA: analyse, fiche, compare, recommande, commande, status
- INTELLIGENCE: score, score-chasse, hourly-forecast

## Donnees reelles integrees
- SoilGrids ISRIC, Open-Meteo ECCC/NOAA/GFS, ET0 NDVI proxy

## Taches futures
- V7.2: Sentinel-2 NDVI direct (Copernicus/GEE)
- PWA M5 Offline Mode Ultra
- IRDA Quebec pedologie, LiDAR MRNF

FIN DU DOCUMENT
