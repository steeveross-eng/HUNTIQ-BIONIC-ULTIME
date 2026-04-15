# HUNTIQ V6 — PRD
## BCE-4X V7-ULTIME-Omega — SECURE-MIGRATION-BCE-4X
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 98/100** | **3 ENGINES V7 ACTIFS**

## Architecture V7-ULTIME (FIGEE)
```
TERRITOIRE-V7 (canvas strategique)
    ↑ donnees spatiales + nutritionnelles
SPATIAL-ENGINE-V7 (moteur geospatial) [6 endpoints]
    | corridors + zones + heatmap + scoring + amenagement
NUTRITION-ENGINE-V7 (moteur scientifique) [7 endpoints]
    | soil + forage + attractivite
    ↓
INTELLIGENCE-V7 (analyse, scoring, predictions)
    | Score V7 + Score Chasse V7 + modeles
    ↓
SUPRA-ENGINE-V7 (decision, recommandations) [6 endpoints]
    | analyse + fiche + compare + recommande + commande
    ↓
CARTE-2027 (terrain)
```

## Engines V7 actifs
- SPATIAL-ENGINE-V7: /api/v7/spatial/* (corridors, zones, heatmap, scoring, amenagement, status)
- NUTRITION-ENGINE-V7: /api/v7/nutrition/* (soil-layer, nutrients, forage, water, metabolism, attractiveness, status)
- SUPRA-ENGINE-V7: /api/v7/supra/* (analyse, fiche, compare, recommande, commande, status)
- INTELLIGENCE-V7: Score V7 + Score Chasse V7 (/api/v1/v51/intelligence/v7/score-chasse)

## Score Chasse V7
- Remplace Score Chasse V6+
- 8 composants: meteo(18%), solunar(10%), temporal(15%), rut(15%), pression(10%), nutrition_v7(15%), vision_ia(10%), spatial(7%)
- Meteo temps reel ECCC/NOAA via Open-Meteo
- Score pilote Mauricie: 62.8/100 "bon"

## Protections BCE-4X
- SHIELD-Omega-MAX, TRACE-LOG-Omega, BCE4X-LOCK, ANTI-LEGACY-Omega
- CMP-CERT: 29/29 endpoints, GLOBAL-CERT: ZERO regression
- V6 composants preserves en mode SHADOW

## V6 en attente suppression (validation Commandant)
- BionicCorridorsV6Layer, ConsolidatedHeatmapLayer, AccessRouteV6Layer, Score Chasse V6+

## Taches futures
- Recablage frontend TERRITOIRE vers V7 endpoints
- Suppression V6 apres validation SHADOW
- V7.2: Sentinel-2 NDVI direct, IRDA Quebec
- PWA M5 Offline Mode

FIN DU DOCUMENT
