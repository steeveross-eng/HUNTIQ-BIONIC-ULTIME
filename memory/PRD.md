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
| **x4520-E** | **VALIDATION_PREVIEW + BUFFER_30 + PANNEAUX_V6** | **COMMITE — EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4520-E VALIDATION_PREVIEW_REBUILD + BUFFER_30 + PANNEAUX_V6 (25 mars 2026)

### Diagnostic (3 captures analysees)
1. Polygones: centroide-only check rendait polygones hors 600m
2. Corridors CRITIQUE: bypass illimite ignorait le rayon
3. Affuts: popup Leaflet natif, pas PinnablePanel V2
4. Zone de rut: absence SQ vs presence Chalet

### Correctifs
- Buffer 30%: ZONE_RADIUS_M 600→780 (rendu uniquement)
- clipRingsToCircle(): projection sommets polygon > 780m sur bord cercle
- clipCoordsToCircle(): filtrage points corridor > 780m
- ZERO bypass isExtreme pour corridors CRITIQUE
- StandDetailPanel.jsx: PinnablePanel V2 complet
- StandsMapLayer: callback onStandClick remplace L.popup
- AmenagementPanel: waypointCenter + double verif Haversine

### Tests
- Salines: 4 cand, max 464m (≤600m) — PASS
- Affuts: 5 stands, max 401m (≤600m) — PASS
- Frontend: compile 0 erreur — PASS
- HTTP 200 PREVIEW — PASS

## Prochaines etapes
- Validation visuelle STEEVE-MAX sur x4520-E (captures Chalet vs SQ)
- Attente directive suivante
- BSAA-2 en standby
