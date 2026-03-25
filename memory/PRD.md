# HUNTIQ-V6 — PRD
## GOLDEN-BCE-4X / STEEVE-MAX

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200-x3205 | Migration core/ + Cartographie | COMPLETE |
| x3300-x3400 | Migration score_consolide + Interconnexion | COMPLETE |
| x4000-SUPRA | 17 moteurs squelettes | CERTIFIE |
| x4100 | Integration scientifique 22 moteurs (Option C) | CERTIFIE |
| x4500-ULTRA | Reconstruction PREVIEW + BSAA | CERTIFIE |
| x4515-FIX | PinnablePanel V2 — 8 panneaux | CERTIFIE |
| x4515-FIX-CRITICAL | Rayon 600m + AmenagementPanel | COMMITE |
| x4520 | Dashboard unifie V6-CORE | COMMITE |
| x4520-A | AUDIT_CORE_BIONIC — 10000% modulaire | COMMITE |
| x4520-B | FIX_PIPELINE_ZONES — ZERO cache legacy | COMMITE |
| x4520-B2 | REBUILD_PREVIEW_ZONES — Purge cache totale | COMMITE |
| x4520-C | ALIGNEMENT_SALINES_600M_V6 — Pipeline scientifique | COMMITE |
| x4520-E | VALIDATION_PREVIEW + BUFFER_30 + PANNEAUX_V6 | COMMITE |
| x4520-F | VALIDATION_PREVIEW_FINAL | COMMITE |
| x4520-F2 | TOTAL PURGE V10 + MIGRATION V6 | COMMITE |
| x4520-G | RESET_PLAYWRIGHT + PROOF | COMMITE |
| x4520-H | PANNEAUX_PLEINE_PAGE + WAYPOINT_DELETE_FIX | COMMITE |
| x4520-H2 | REFRESH_OR_REBUILD_PREVIEW | COMMITE |
| x4520-H4 | WIND_FLOW_CRASH_FIX | COMMITE |
| x4600-R2 | NUTRITION_RENAME — Renommage complet 100% | COMPLETE |
| **x4600-R4** | **WAYPOINT_DELETE_TOTAL_RESET** | **COMPLETE — EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4600-R4 — WAYPOINT_DELETE_TOTAL_RESET (Fevrier 2026)

### Cause racine
NutritionPointsLayer et StandsMapLayer n'appelaient pas clearLayers() au demontage.
onClearAllMapData ne resetait pas alimentationV2Data ni showNutritionPanel.

### Fix triple couche
1. Cleanup composant: clearLayers() dans useEffect return (NutritionPointsLayer + StandsMapLayer)
2. Reset etat complet: 7 variables d'etat resetees dans onClearAllMapData
3. Nettoyage nucleaire Leaflet: map.eachLayer -> removeLayer sur tous les layers non-tile

### Validation
- Compilation: ZERO erreur
- Rapport: audit/rapport_x4600-NUTRITION_RENAME-R4.md

## Prochaines etapes
- Validation STEEVE-MAX sur x4600-R4
- BSAA-2: Implementation module BIONIC Social Ads Automation (en attente directive)
- Merge Work1 vers main (strictement sous controle STEEVE-MAX)
