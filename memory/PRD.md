# HUNTIQ V8 — PRD
## BCE-4X V8-PREVIEW-Omega GOVERNANCE-LOCK — CERTIFIE
**MAJ:** 2026-04-16 | **25/25 PASS** | **100/100** | **GOVERNANCE LOCK ACTIF**

## Architecture V8 NATIONALE
```
TERRITOIRE-V7.2 (ScoreV8Badge PREVIEW)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/*)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/*)
INTELLIGENCE-V7
SUPRA-ENGINE-V7 (/api/v7/supra/*)
CANADA-V7.2 (/api/v7/canada/*)
V8-NATIONAL (/api/v8/national/* — mode PREVIEW — governance lock)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 22 criteres)
V8-P1 PIPELINES (/api/v8/p1/* — STUB mode)
V8-GOVERNANCE (/api/v8/governance/* — Master Switch Admin Premium)
CARTE-2027 (terrain V8 PREVIEW)
```

## V8-GOVERNANCE (Master Switch)
- Authority: COMMANDANT_STEEVE_MAX exclusivement
- Modes: LOCKED (bloque score), PREVIEW (admin premium), PUBLIC (tous)
- Activation: admin@huntiq.com uniquement
- LOCKED: Score V8 retourne 0 + engine=V8-GOVERNANCE-LOCKED
- Non-auth: REFUS automatique
- Audit trail: MongoDB v8_governance collection
- Endpoints: /state, /activate (POST), /audit

## Endpoints V8
### V8-NATIONAL (5)
/biome-profile, /species-profile, /score (PREVIEW+P1), /referentials, /status

### EXCLUSION-ENGINE-V8 (3)
/decision (22 criteres), /referential, /status

### V8-P1 PIPELINES (3)
/lidar (5 prov + fallback), /pedology (IRDA 9 sols), /status

### V8-GOVERNANCE (3)
/state, /activate (POST admin), /audit (admin)

## Fichiers
- /app/backend/engines/v8_national/router.py
- /app/backend/engines/v8_national/referentials.py
- /app/backend/engines/v8_national/exclusion_engine.py
- /app/backend/engines/v8_national/p1_pipelines.py
- /app/backend/engines/v8_national/governance.py (NOUVEAU)
- /app/backend/server.py
- /app/frontend/src/hooks/useBionicScoringV8.js
- /app/frontend/src/components/territoire/ScoreV8Badge.jsx
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx
- /app/frontend/src/pages/Carte2027Page.jsx

## Taches futures
- P1-ACTIVATION: Cles WCS (MRNF QC, OMNR ON, GeoBC, AB Env, SNB NB)
- P1-ACTIVATION: Acces IRDA API institutionnel Quebec
- P2: OSM road/building density
- P2: ECCC stations meteo provinciales

FIN DU DOCUMENT
