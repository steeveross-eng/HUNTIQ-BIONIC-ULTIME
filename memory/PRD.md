# HUNTIQ V7.2 — PRD
## BCE-4X RESTORE-ZONES-Omega + EXPANSION-CANADA-V7.2
**MAJ:** 2026-04-15 | **ZONES RESTAUREES 5/5** | **13 PROVINCES**

## Architecture V7.2 NATIONALE
```
TERRITOIRE-V7 (canvas — zones V7 restaurees)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 8 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
CARTE-2027 (terrain)
```

## RESTORE-ZONES fix
- Cause: zones generees hors rayon 780m (838-880m) par SPATIAL-ENGINE-V7
- Fix: rayon zones reduit a 270-507m (multiplicateurs 0.8-1.2)
- Fix: ZONE_COLORS ajoute salines+affuts
- Fix: LEVEL_ZINDEX ajoute MOYEN
- Fix: isZoneTypeVisible ajoute salines mapping
- Fix: DataCloneError retry sans signal (preview environment)
- Resultat: 5/5 zones visibles (alimentation, repos, rut, eau, salines)

## Anti-regression: 15/15 PASS

FIN DU DOCUMENT
