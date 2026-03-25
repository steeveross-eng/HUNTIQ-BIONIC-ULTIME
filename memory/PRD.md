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
| **x4520-H** | **PANNEAUX_PLEINE_PAGE + WAYPOINT_DELETE_FIX** | **COMMITE — EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## Architecture V6-CORE

### Panneaux PinnablePanel V2 (9/9)
| Panneau | Composant | Statut |
|---------|-----------|--------|
| Salines | SalineDetailPanel.jsx | V2 (x4520-H) |
| Affuts | StandDetailPanel.jsx | V2 (x4520-E) |
| Amenagement | AmenagementPanel.jsx | V2 (x4520-C) |
| Intelligence | IntelligenceDashboard.jsx | V2 (x4515) |
| Diagnostics | DiagnosticsPanel.jsx | V2 (x4515) |
| Corridors | CorridorsEcologyPanel.jsx | V2 (x4515) |
| Guide Pro | GuideProPanel.jsx | V2 (x4515) |
| Terrain | TerrainPanel.jsx | V2 (x4515) |
| Scientifique | ScientifiquePanel.jsx | V2 (x4515) |

### Waypoint Delete
- onClearAllMapData: ferme panneaux + vide donnees
- ZERO residu apres suppression

## Tests
- Salines: max 464m ≤ 600m — PASS
- Affuts: max 401m ≤ 600m — PASS
- V6 API corridors: PASS
- Frontend compile: 0 erreur
- Playwright: PASS

## Prochaines etapes
- Validation STEEVE-MAX sur x4520-H
- BSAA-2 en standby
