# HUNTIQ V7.2 — PRD
## BCE-4X ZONES+EXCLUSIONS-STABILIZE-Omega — CERTIFIE
**MAJ:** 2026-04-15 | **22/22 PASS** | **EXCLUSIONS BCE-4X ACTIVES**

## Architecture V7.2 STABILISEE
```
TERRITOIRE-V7.2 (canvas — zones V7 + exclusions BCE-4X)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 9 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
CARTE-2027 (terrain)
```

## Exclusions BCE-4X (PHASE 2)
- 20 zones urbaines majeures (Montreal, Quebec, Ottawa, Toronto, Vancouver, etc.)
- Buffer 2km autour centres urbains
- 3 corridors urbains (QC-MTL, GTA, Metro Vancouver)
- Exclusion Arctique (lat>72)
- Exclusion Toundra (lat>62, lng>-100)
- Seuil habitat minimum: 15/100
- Endpoint diagnostic: /api/v7/spatial/exclusion-check
- Validation: Quebec City=EXCLUS(0), Montreal=EXCLUS(0), Nunavut=EXCLUS(0), Mauricie=VALIDE(100), Algonquin=VALIDE(100)

## Zones restaurees (PHASE 1)
- 5/5 zones dans rayon 780m (270-507m)
- ZONE_COLORS: alimentation, repos, rut, eau, salines, affuts
- DataCloneError retry actif (preview environment)

## Taches V8
- V8-PREPARATION-Omega: moteurs nationaux V8
- Normalisation inter-provinciale

FIN DU DOCUMENT
