# HUNTIQ V8 — PRD
## BCE-4X GOVERNANCE-Omega MASTER-SWITCH-SUPREMACY — CERTIFIE
**MAJ:** 2026-04-16 | **23/23 PASS** | **100/100** | **MASTER SWITCH SUPREME**

## Architecture V8 NATIONALE
```
TERRITOIRE-V7.2 (ScoreV8Badge PREVIEW tag)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/*)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/*)
INTELLIGENCE-V7
SUPRA-ENGINE-V7 (/api/v7/supra/*)
CANADA-V7.2 (/api/v7/canada/*)
V8-NATIONAL (/api/v8/national/* — GOVERNANCE LOCKED par defaut)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 22 criteres)
V8-P1 PIPELINES (/api/v8/p1/* — STUB mode)
V8-GOVERNANCE-SUPREMACY (/api/v8/governance/* — Master Switch)
CARTE-2027 (terrain V8 PREVIEW tag)
```

## V8-GOVERNANCE-SUPREMACY v8.2.0
- Authority: COMMANDANT_STEEVE_MAX exclusivement (admin@huntiq.com)
- POST-PREVIEW LOCKDOWN: Defaut = LOCKED (JAMAIS PREVIEW/PUBLIC au boot)
- Score V8 retourne 0 + V8-GOVERNANCE-LOCKED quand LOCKED
- Activation PREVIEW/PUBLIC = Master Switch Admin Premium seulement
- Non-auth = REFUS AUTOMATIQUE
- Audit trail MongoDB (v8_governance_audit collection)
- Transitions loggees: from_mode -> to_mode + by + at + authority
- 4 supremacy rules dans /state, 7 dans /audit
- Endpoints: /state, /activate (POST), /audit

## Endpoints V8
### V8-GOVERNANCE (3)
/state, /activate (POST admin), /audit (admin)

### V8-NATIONAL (5)
/biome-profile, /species-profile, /score (governance-gated), /referentials, /status

### EXCLUSION-ENGINE-V8 (3)
/decision (22 criteres), /referential, /status

### V8-P1 PIPELINES (3)
/lidar, /pedology, /status

## Fichiers
- /app/backend/engines/v8_national/governance.py (v8.2.0 SUPREMACY)
- /app/backend/engines/v8_national/router.py
- /app/backend/engines/v8_national/referentials.py
- /app/backend/engines/v8_national/exclusion_engine.py
- /app/backend/engines/v8_national/p1_pipelines.py
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
