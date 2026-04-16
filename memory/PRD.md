# HUNTIQ V8 — PRD
## BCE-4X V8-FULL-DEPLOY-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **29/29 PASS** | **100/100** | **V8 DEPLOYE NATIONALEMENT**

## Architecture V8 NATIONALE
```
TERRITOIRE-V7.2 (canvas — zones V7 + exclusions BCE-4X)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 9 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
V8-NATIONAL (/api/v8/national/* — 5 endpoints)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 3 endpoints)
CARTE-2027 (terrain V8)
```

## EXCLUSION-ENGINE-V8 v8.1.0
- 22 criteres BCE-4X:
  1-URBAN_POLYGON, 2-URBAN_BUFFER, 3-URBAN_CORRIDOR,
  4-LEGAL_PARC_NATIONAL, 5-LEGAL_RESERVE_ECOLOGIQUE, 6-LEGAL_PRIVATE_RESTRICTED,
  7-ARCTIC_EXTREME, 8-SUBARCTIC_LIMITE, 9-ALTITUDE_EXTREME,
  10-SLOPE_EXTREME, 11-WATER_DEEP, 12-CONTAMINATION,
  13-ROAD_DENSITY, 14-BUILDING_DENSITY, 15-INDUSTRIAL_ZONE,
  16-MILITARY_ZONE, 17-AIRPORT_BUFFER, 18-RAILWAY_BUFFER,
  19-MINE_ACTIVE, 20-POWER_LINE_CORRIDOR, 21-FLOOD_ZONE, 22-SECURITY_PERIMETER
- 24 zones urbaines, 5 corridors, 10 zones legales, 4 militaires, 4 aeroports
- Severites: HARD, SOFT, NONE
- LEGAL_PRIVATE_RESTRICTED: Exclusion UNIQUEMENT si interdiction explicite
  (panneau_officiel, avis_legal, bail_exclusif, servitude_legale, reserve_privee)
- Terrain prive sans interdiction = INCLUS

## Endpoints V8
- /api/v8/national/biome-profile
- /api/v8/national/species-profile
- /api/v8/national/score
- /api/v8/national/referentials
- /api/v8/national/status
- /api/v8/exclusion/decision
- /api/v8/exclusion/referential
- /api/v8/exclusion/status

## Deploiement complet

### Phase 1 — Score V8 Frontend (2026-04-15)
- useBionicScoringV8.js, ScoreV8Badge.jsx, TerritoireHeader V8, MonTerritoireBionicPage V8

### Phase 2 — CARTE-2027 V8 (2026-04-15)
- V8IntelPanel, 10 composantes, contexte biome, compat espece-biome
- 8 especes nationales, 13 provinces/territoires

### Phase 3 — Normalisation (2026-04-15)
- 13/13 provinces actives, ecart 14.2pts

### Phase 4 — BCE-4X 22 exclusions (2026-04-16)
- /api/v8/exclusion/referential expose
- Logs BCE-4X structures (reason + severity)
- Zones militaires (CFB Gagetown, Halifax, Ottawa-Uplands, Winnipeg)
- Aeroports (YUL, YYZ, YVR, YYC)

### Phase 5 — LEGAL_PRIVATE_RESTRICTED (2026-04-16)
- Politique corrigee: exclusion seulement si interdiction explicite
- 5 champs: panneau_officiel, avis_legal, bail_exclusif, servitude_legale, reserve_privee

### Phase 6 — Validation (2026-04-16)
- 29/29 PASS, 100/100

## Fichiers
- /app/frontend/src/hooks/useBionicScoringV8.js
- /app/frontend/src/components/territoire/ScoreV8Badge.jsx
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx
- /app/frontend/src/pages/Carte2027Page.jsx
- /app/backend/engines/v8_national/exclusion_engine.py
- /app/backend/engines/v8_national/router.py
- /app/backend/engines/v8_national/referentials.py
- /app/backend/server.py

## Taches futures
- P1: LiDAR WCS real multi-provincial (acces gouvernemental)
- P1: IRDA API pedologie reelle Quebec (acces institutionnel)
- P2: OSM real data pour road/building density
- P2: ECCC stations meteo provinciales

FIN DU DOCUMENT
