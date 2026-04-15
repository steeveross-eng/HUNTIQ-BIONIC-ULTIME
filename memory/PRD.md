# HUNTIQ V8 — PRD
## BCE-4X V8-INTEGRATION-Omega — PHASES 1→5 CERTIFIEES
**MAJ:** 2026-04-15 | **25/25 PASS** | **100/100** | **V8 COMPLET**

## Architecture V8 NATIONALE
```
TERRITOIRE-V7.2 (canvas — zones V7 + exclusions BCE-4X)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 9 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
V8-NATIONAL (/api/v8/national/* — 5 endpoints)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 2 endpoints)
CARTE-2027 (terrain V8)
```

## V8-NATIONAL Module
- 9 biomes canadiens
- 6 regimes fauniques
- 4 regimes de neige
- 5 regimes forestiers
- 8 especes cataloguees
- Score V8 national: 10 composantes
- Meteo temps reel ECCC integree
- Exclusions BCE-4X actives via EXCLUSION-ENGINE-V8

## EXCLUSION-ENGINE-V8
- 11 criteres d'exclusion (urban, buffer, corridor, legal, arctic, altitude, slope, water, contamination, road_density, building_density)
- 24 zones urbaines majeures
- 5 corridors urbains denses
- 7 zones legales interdites (Forillon, Grands-Jardins, Mont-Tremblant, Kouchibouguac, Jasper, Banff, Pacific Rim)
- Severites: HARD, SOFT, NONE
- Referentiel UNIQUE centralise

## Endpoints V8
- /api/v8/national/biome-profile
- /api/v8/national/species-profile
- /api/v8/national/score
- /api/v8/national/referentials
- /api/v8/national/status
- /api/v8/exclusion/decision
- /api/v8/exclusion/status

## Phases completees

### Phase 1 — Score V8 Frontend (2026-04-15)
- useBionicScoringV8.js, ScoreV8Badge.jsx, TerritoireHeader V8, MonTerritoireBionicPage V8

### Phase 2 — CARTE-2027 V8 (2026-04-15)
- V8IntelPanel remplace IntelPanel V7
- 10 composantes + contexte biome + compat espece-biome
- 8 especes nationales dans catalogue (caribou, cerf_mulet, boeuf_musque ajoutes)
- 13 provinces/territoires (NL, NU ajoutes)
- Label CARTE TERRAIN V8

### Phase 3 — Normalisation inter-provinciale (2026-04-15)
- 13/13 provinces actives, ecart 14.2 points (Min 56.8 AB, Max 71.0 BC)
- Biomes corrects: boreal_mixed, boreal_coniferous, atlantic_maritime, pacific_rainforest, taiga_subarctic, prairie_grassland, arctic_tundra

### Phase 5 — EXCLUSION-ENGINE-V8 (2026-04-15)
- exclusion_engine.py cree
- 20/20 villes exclues, 5/6 forets incluses (1 dans Banff = exclu legal CORRECT)
- 3/3 arctique exclu, 3/3 zones legales exclues
- Integre dans Score V8 (router.py)
- Enregistre dans server.py

## Fichiers crees/modifies
- /app/frontend/src/hooks/useBionicScoringV8.js (CREE)
- /app/frontend/src/components/territoire/ScoreV8Badge.jsx (CREE)
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx (MODIFIE)
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx (MODIFIE)
- /app/frontend/src/pages/Carte2027Page.jsx (MODIFIE)
- /app/backend/engines/v8_national/exclusion_engine.py (CREE)
- /app/backend/engines/v8_national/router.py (MODIFIE)
- /app/backend/server.py (MODIFIE)

## Taches futures
- P1: LiDAR WCS real multi-provincial (acces gouvernemental requis)
- P1: IRDA API pedologie reelle Quebec (acces institutionnel requis)

## Mocked/Fallback
- LiDAR MRNF: fallback Copernicus/Open-Meteo
- IRDA pedologie: fallback SoilGrids

FIN DU DOCUMENT
