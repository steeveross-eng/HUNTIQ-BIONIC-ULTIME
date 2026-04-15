# HUNTIQ V6 — PRD
## BCE-4X V6.2 — NUTRITION-ENGINE-V7-FINAL-INTEGRATION-Omega
**MAJ:** 2026-04-15 | **92+ MOTEURS** | **SCORE CONFORMITE: 92/100**

## Architecture V7-ULTIME (FIGEE)
```
TERRITOIRE-V7 (canvas strategique)
    ↑ donnees nutritionnelles spatiales
NUTRITION-ENGINE-V7 (moteur scientifique central)
    ↓ modeles nutritionnels
INTELLIGENCE-V7 (analyse, scoring, predictions)
    ↓ analyses + scores
BDE/SUPRA-V7 (decision, recommandations)
    ↓ actions
CARTE-2027 (terrain)
```

## NUTRITION-ENGINE-V7 — Moteur central
- Module: /app/backend/modules/nutrition_engine_v7/
- Pipeline: Sol → Nutriments → Fourrage/NDVI → Eau → Metabolisme → Temporel → Attractivite
- 7 endpoints: /api/v7/nutrition/*
- Poids: Soil(20%), Nutrients(25%), Forage(20%), Water(10%), Metabolism(15%), Temporal(10%)
- Sorties standardisees: soil_nutrients_layer, forage_quality_model, wildlife_nutrition_attractiveness
- Donnees reelles: SoilGrids ISRIC (phh2o,soc,nitrogen,clay,sand,cec), Open-Meteo ET0 proxy NDVI
- Consommateurs: INTELLIGENCE V7 Score, OPTIMIZATION ENGINE (#13 12%), SUPRA (bloc+justifications), CARTE-2027 (heatmap), SCORE CONSOLIDE (23 moteurs)

## Integrations actives
- INTELLIGENCE V7: nutrition=LIVE (53.0, plus en dur)
- OPTIMIZATION ENGINE: nutrition_v7 couche #13 (12% ponderation)
- SUPRA: bloc nutrition_v7 complet (soil_nutrients_layer, forage_quality_model, wildlife_nutrition_attractiveness, justifications)
- CARTE-2027: heatmap enrichi nutrition V7 au centre
- SCORE CONSOLIDE: 23 moteurs (22 legacy + nutrition_v7)
- SALINES: v7_temporal injecte

## Donnees reelles
- SoilGrids ISRIC: phh2o, soc, nitrogen, clay, sand, cec (API REST rest.isric.org)
- Open-Meteo: temp, vent, pression (ECCC/NOAA/GFS), ET0 evapotranspiration (NDVI proxy)

## Taches futures
- P1: V7.2 Sentinel-2 NDVI direct (API Copernicus/GEE)
- P1: M5 Offline Mode Ultra (PWA caching)
- P2: IRDA Quebec pedologie reelle
- P2: LiDAR MRNF integration (DEM, canopee, pentes)
- P3: Vision IA scoring V7, CursorBionicLayer V7

FIN DU DOCUMENT
