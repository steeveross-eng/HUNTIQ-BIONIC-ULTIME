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
| **x4520-H4** | **WIND_FLOW_CRASH_FIX** | **COMMITE — EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4520-H4 — WIND_FLOW_CRASH_FIX (25 mars 2026)
- Cause: animateParticles/drawArrowsMode → containerPointToLatLng → NaN pendant transition panneau
- Fix: Guards NaN + try/catch + bounds degenerees + stopPropagation PinnablePanel
- Playwright: 0 console errors, 0 NaN, carte stable

## Prochaines etapes
- Validation STEEVE-MAX sur x4520-H4
- Attente directive suivante
