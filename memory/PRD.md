# HUNTIQ V7.2 — PRD
## BCE-4X EXPANSION-CANADA-V7.2-Omega — CERTIFIE
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 100/100** | **NATIONAL 13 PROVINCES**

## Architecture V7.2 NATIONALE CERTIFIEE
```
TERRITOIRE-V7 (canvas strategique — 100% V7)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 8 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
CARTE-2027 (terrain)
```

## CANADA-V7.2 Module National
- 13 provinces/territoires couverts (QC, ON, BC, AB, SK, MB, NB, NS, NL, PEI, YT, NT, NU)
- 16 ecozones terrestres
- 10 ordres pedologiques CanSIS SLC v3.2
- 13 sources LiDAR provinciales
- 11 sources de donnees (Sentinel-2, SoilGrids, ECCC, Open-Meteo, CanSIS, etc.)

## Endpoints /api/v7/canada/*
- /ndvi: NDVI Sentinel-2 national (Copernicus STAC + ET0 regionalise)
- /lidar: LiDAR multi-provincial (canopy, slope)
- /soil: Pedologie CanSIS + SoilGrids ISRIC
- /profile: Profil complet (NDVI + LiDAR + Sol + Ecozone)
- /provinces: 13 provinces metadata
- /status: Statut module

## Anti-regression: 20/20 PASS | V6: 404

## Taches futures (V8)
- V8-PREPARATION: Moteurs nationaux V8
- LiDAR WCS reel (acces gouvernemental)
- IRDA API pedologie (acces institutionnel)

FIN DU DOCUMENT
