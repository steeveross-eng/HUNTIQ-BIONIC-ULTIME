# HUNTIQ V8 — PRD
## BCE-4X V8-PREVIEW-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **26/26 PASS** | **100/100** | **V8 PREVIEW NATIONAL ACTIF**

## Architecture V8 NATIONALE
```
TERRITOIRE-V7.2 (canvas — zones V7 + exclusions BCE-4X + ScoreV8Badge PREVIEW)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 9 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
V8-NATIONAL (/api/v8/national/* — 5 endpoints — mode PREVIEW)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 3 endpoints — 22 criteres)
V8-P1 PIPELINES (/api/v8/p1/* — 3 endpoints — STUB mode)
CARTE-2027 (terrain V8 PREVIEW)
```

## V8-NATIONAL v8.1.0-preview
- Mode: PREVIEW
- 10 composantes de score
- Habitat enrichi par P1 (LiDAR + pedologie)
- Integrations: SPATIAL-V7.2, NUTRITION-V7.2, CANADA-V7.2, ECCC, Open-Meteo, EXCLUSION-ENGINE-V8

## EXCLUSION-ENGINE-V8 v8.1.0
- 22 criteres BCE-4X
- 24 zones urbaines, 5 corridors, 10 zones legales, 4 militaires, 4 aeroports
- LEGAL_PRIVATE_RESTRICTED: exclusion UNIQUEMENT si interdiction explicite
- Terrain prive sans interdiction = INCLUS

## V8-P1 PIPELINES (STUB_ACTIVE)
- LiDAR WCS: 5 provinces configurees (QC MRNF, ON OMNR, BC GeoBC, AB Environment, NB SNB) + 8 fallback federal
- IRDA Pedologie: 9 types de sol avec attractivite faunique
- Fallbacks: Copernicus DEM 30m + SoilGrids 250m
- Activation: necessite cles d'acces gouvernemental/institutionnel

## Endpoints
### V8-NATIONAL
- /api/v8/national/biome-profile
- /api/v8/national/species-profile
- /api/v8/national/score (mode PREVIEW + p1_data)
- /api/v8/national/referentials
- /api/v8/national/status

### EXCLUSION-ENGINE-V8
- /api/v8/exclusion/decision
- /api/v8/exclusion/referential
- /api/v8/exclusion/status

### V8-P1 PIPELINES
- /api/v8/p1/lidar
- /api/v8/p1/pedology
- /api/v8/p1/status

## Fichiers
- /app/backend/engines/v8_national/router.py
- /app/backend/engines/v8_national/referentials.py
- /app/backend/engines/v8_national/exclusion_engine.py
- /app/backend/engines/v8_national/p1_pipelines.py (NOUVEAU)
- /app/backend/server.py
- /app/frontend/src/hooks/useBionicScoringV8.js
- /app/frontend/src/components/territoire/ScoreV8Badge.jsx
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx
- /app/frontend/src/pages/Carte2027Page.jsx

## Taches futures
- P1-ACTIVATION: Connexion LiDAR WCS reel (cles MRNF, OMNR, GeoBC)
- P1-ACTIVATION: Connexion IRDA API reelle (acces institutionnel)
- P2: Integration OSM reelle pour road/building density
- P2: ECCC stations meteo provinciales dediees

FIN DU DOCUMENT
