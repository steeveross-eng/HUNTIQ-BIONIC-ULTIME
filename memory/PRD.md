# HUNTIQ V6 — PRD
## BCE-4X V6.2 — SYSTEM-Omega-ULTIMATE-V5.4 + CARTE-2027 + P1-V7 + NUTRITION-ENGINE-V7
**MAJ:** 2026-04-15 | **87+ MOTEURS** | **NUTRITION-ENGINE-V7 ACTIVE**

## Hierarchie cartes institutionnelle
- L1: TERRITOIRE (carte institutionnelle, 87 moteurs, source verite)
- L2: INTELLIGENCE (carte analytique, Score V7, predictions)
- L3: CARTE 2027 (carte terrain V7, Leaflet interactive)
- Regle: TERRITOIRE -> INTELLIGENCE -> CARTE (descendant)

## Pages actives
- /mon-territoire-bionic (TERRITOIRE L1)
- /intelligence-v6 (INTELLIGENCE L2)
- /carte-2027 (CARTE L3)
- /cameras, /shop

## NUTRITION-ENGINE-V7 — Deploye 2026-04-15
- Module isole: /app/backend/modules/nutrition_engine_v7/
- Pipeline: Sol -> Nutriments -> Plantes -> Fourrage -> Attractivite -> Gibier
- 7 endpoints: /api/v7/nutrition/{soil-layer,nutrients,forage,water,metabolism,attractiveness,status}
- 6 couches: Soil(20%), Nutrients(25%), Forage(20%), Water(10%), Metabolism(15%), Temporal(10%)
- 7 moteurs V5 encapsules (soil_composition, nutrient_deficiency, wildlife_nutritional, vegetation_forage, hydrology_leaching, seasonal_metabolism, saline_recommendation)
- Integrations: INTELLIGENCE V7 Score (nutrition=LIVE), SUPRA (bloc nutrition_v7), CARTE-2027 (heatmap centre)
- Score completude scientifique: 62/100
- Plan V7.1: SoilGrids reel, Sentinel-2 NDVI, IRDA Quebec, LiDAR MRNF

## Deploiements precedents
- CARTE-2027-REBUILD-Omega-FULL-DEPLOY (2026-04-15)
- V7-P1-CRITICAL-EXECUTION (meteo ECCC/NOAA, corridors V7, salines V7, affuts V7)
- V7-SUBLAYERS-TOTAL-AUDIT (62 sous-couches, 9 commandes correctives)

## Taches futures
- P2-CMD05: V7 comme couche #13 dans optimization engine
- P2-CMD06: Rebuild ConsolidatedHeatmapLayer sur V7
- P2-CMD07: Migration IntelligenceDashboard vers V7
- P3-CMD08: Vision IA scoring V7
- P3-CMD09: CursorBionicLayer migration V7
- P1: M5 Offline Mode Ultra (PWA caching)
- V7.1: SoilGrids + Sentinel-2 NDVI reels

FIN DU DOCUMENT
