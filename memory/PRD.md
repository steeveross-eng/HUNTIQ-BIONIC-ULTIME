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
| **x4520-F** | **VALIDATION_PREVIEW_FINAL** | **COMMITE** |
| **x4520-F2** | **TOTAL PURGE V10 + MIGRATION V6** | **COMMITE — EN ATTENTE VALIDATION** |
| **x4520-G** | **RESET_PLAYWRIGHT + PROOF** | **COMMITE** |

## Score: 57.6 (22 moteurs, Option C)

## Architecture V6-CORE

### Frontend
- Couche corridors: `BionicCorridorsV6Layer.jsx` (Haversine 780m + clipping circulaire)
- Panneaux: PinnablePanel V2 (AmenagementPanel, StandDetailPanel)
- API: `/api/v6/corridors/analyze-full`
- Cache: CACHE_VERSION `_v6_core`, DB_VERSION 2, SW_VERSION v7
- ZERO reference V10 active

### Backend
- Route V6: `/api/v6/corridors/*` (alias de /api/v10/ pour compatibilite)
- Salines: filtrage Haversine strict ≤ 600m
- Affuts: positionnement ecologique (corridors critiques, crosswind)

## Tests
- Salines: 4 cand, max 464m ≤ 600m — PASS
- Affuts: 5 stands, max 401m ≤ 600m — PASS
- V6 API corridors: PASS
- Frontend compile: 0 erreur
- Playwright: PASS (captures reussies)

## Prochaines etapes
- Validation STEEVE-MAX sur x4520-F+F2+G
- BSAA-2 en standby (attente directive)
