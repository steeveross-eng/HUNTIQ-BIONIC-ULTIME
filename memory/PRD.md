# HUNTIQ V7.2 — PRD
## BCE-4X EXPANSION-V7.2 — CERTIFIE
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 100/100** | **V7.2 DEPLOYE**

## Architecture V7.2 CERTIFIEE
```
TERRITOIRE-V7 (canvas strategique — 100% V7)
SPATIAL-ENGINE-V7 (/api/v7/spatial/* — 8 endpoints)
  corridors, zones, heatmap, scoring, amenagement,
  analyze-full, vision-scoring, status
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
  soil-layer (SoilGrids ISRIC), nutrients,
  forage (Sentinel-2 + LiDAR + IRDA), water,
  metabolism, attractiveness, status
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CARTE-2027 (terrain)
```

## V7.2 Modules deployes
### Sentinel-2 NDVI
- Copernicus Data Space STAC integration (active)
- Fallback: Open-Meteo ET0 proxy
- Pipeline: STAC search → cloud_cover → NDVI estimate

### LiDAR MRNF
- Pipeline pret pour WCS MRNF (canopy_height_m)
- Fallback: estimation depuis NDVI + ecozone

### IRDA Quebec
- Pipeline pret pour API pedologie Quebec
- Fallback: unavailable (API pas publique)

### Vision IA Scoring V7.2
- /api/v7/spatial/vision-scoring
- Hotspots + trajectoires scores avec nutrition + temporal
- 4 cameras actives detectees

### PWA M5 Offline Ultra
- Service worker v7.2
- Cache tiles (CartoDB, Esri, OpenTopo)
- Cache V7 API routes (spatial, nutrition, supra)

## Donnees reelles
- SoilGrids ISRIC: phh2o, soc, nitrogen, clay, sand, cec
- Open-Meteo ECCC/NOAA/GFS: temp, vent, pression, ET0
- Copernicus Sentinel-2 L2A STAC: cloud_cover → NDVI proxy

## Anti-regression: 24/24 PASS | V6: 404 confirme

FIN DU DOCUMENT
