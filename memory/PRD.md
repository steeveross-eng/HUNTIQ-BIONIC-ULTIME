# PRD.md — HUNTIQ-V6
# GOLDEN-BCE-4X / BCE ULTRA MAX / STEEVE-MAX x100

## Probleme Original
Reconstruction HUNTIQ-V6, gouvernance BCE-4X, audits, restauration, parite totale.

## Architecture
- Backend: FastAPI (85 modules) | Frontend: React | DB: MongoDB
- Branche: Work1 | Gouvernance: GOLDEN-BCE-4X / BCE ULTRA MAX / STEEVE-MAX x100

## Accompli

### Phases 1-5C — Import, Gouvernance, Audits
### Phase 5C-R — Restauration optimization_engine (VALIDE)
### Montage Preview V6 — URL: https://huntiq-restore.preview.emergentagent.com
### Corrections V6 — Weather API 2.5, Exclusion V7
### GOLDEN BUILD Audit V5.4 → V6.x — 85/85 modules (100%)
### Audit Total + Inspection Microscopique — 17 dimensions, 0 divergence

### FIX CRITIQUE: Hotspots V7 — Cache local (2026-03-23)
- Triple verification V7, 41,944 polygones eau, ZERO hotspot eau

### MIGRATION CERCLES 600m (2026-03-24)
**Phase 1 — Hotspots (commit 8e99f3fe):**
- hotspot_service.py + hotspot_engine.py: Cercle 600m
- Admin Premium fix: 7 causes corrigees, BCE-4X PASS 1800/1800

**Phase 2 — Migration TOTALE (commit d90453a9, 3508ee46):**
- zone_engine_core_v2.py: Post-traitement cercles 600m toutes features GeoJSON + eau V7
- osg_engine.py: Zones OSG converties en cercles 600m
- BionicZone600m.jsx: NOUVEAU composant L.Circle(600m) remplace L.Rectangle(2km)
- BionicZone2km.jsx: Delegue a BionicZone600m
- useSpatialClipping.js: Box 2000m → 1200m
- 13+ zones eau exclues par requete

## Moteurs Verrouilles V6.x
1-7. (precedemment valides)
8. hotspots_engine V6/V7 (CERCLES 600m + cache local eau)
9. admin_hotspots V6 (CERCLES 600m + BCE-4X PASS)
10. zone_engine_core_v2 (CERCLES 600m + eau V7)
11. osg_engine (CERCLES 600m)

## Preview URL
https://huntiq-restore.preview.emergentagent.com

## Backlog
### P0 — En attente: Validation STEEVE-MAX migration cercles 600m totale
### P1 — Phase BSAA-2: Implementation BIONIC Social Ads Automation
### P2 — Merge Work1 vers main, nettoyage audit_historical
