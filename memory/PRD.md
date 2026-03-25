# HUNTIQ-V6 — PRD
## GOLDEN-BCE-4X / STEEVE-MAX

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200-x3203 | Migration core/ et encapsulation | COMPLETE |
| x3204-x3205 | Cartographie + Normalisation scientifique | COMPLETE |
| x3300 | Migration score_consolide dans core/ | COMPLETE |
| x3400 | Interconnexion totale frontend | COMPLETE |
| x4000-SUPRA | 17 moteurs squelettes (Option A) | CERTIFIE |
| x4100 | Integration scientifique 22 moteurs (Option C) | CERTIFIE |
| x4500-ULTRA | Reconstruction PREVIEW + BSAA | CERTIFIE |
| x4515-FIX | PinnablePanel V2 — 8 panneaux conformes | CERTIFIE |
| **x4515-FIX-CRITICAL** | **Rayon 600m Haversine + AmenagementPanel** | **EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4515-FIX-CRITICAL (25 mars 2026)
Corrections appliquees:
1. **Rayon 600m circulaire strict (Haversine)** — Remplacement du bbox rectangulaire 2km x 2km
2. **Masquage total hors-rayon** — Zones hors 600m completement masquees (pas attenuees)
3. **AmenagementPanel (Salines/Affuts)** integre dans MonTerritoireBionicPage + toggle toolbar
4. **PinnablePanel V2** uniforme sur tous les panneaux (8/8)

## PinnablePanel V2 (x4515-FIX)
8 panneaux couverts:
1. TerritoryAnalysisPanel (territoire)
2. BionicZoneDiagnosticPanel (diagnostics)
3. GuidedRoutePanel (parcours guide)
4. NutritionPanel (alimentation/nutrition)
5. AmenagementPanel (salines/affuts) — Nouvellement integre dans la page
6. CorridorsEcologyPanel (corridors V10)
7. DiagnosticExclusionsPanel (exclusions spatiales)
8. ZoneInfoPanel (info zone)

## Architecture
- Branche: STEEVE-MAX-x3200-V6-CORE
- Frontend: React (Craco/Webpack)
- Backend: FastAPI
- Composant cle: PinnablePanel.jsx (321 lignes)
- Zone rendering: BionicCorridorsV10Layer.jsx (Haversine 600m)

## Prochaines etapes
- Validation STEEVE-MAX sur x4515-FIX-CRITICAL
- BSAA-2 (implementation) — apres validation
- Merge vers main — gere exclusivement par STEEVE-MAX
