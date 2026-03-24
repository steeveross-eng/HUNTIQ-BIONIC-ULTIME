# PRD.md — HUNTIQ-V6
# GOLDEN-BCE-4X / BCE ULTRA MAX / STEEVE-MAX x100

## Probleme Original
Reconstruction HUNTIQ-V6, gouvernance BCE-4X, audits, restauration, parite totale.

## Architecture
- Backend: FastAPI (85 modules) | Frontend: React | DB: MongoDB
- Branche: Work1 | Gouvernance: GOLDEN-BCE-4X / BCE ULTRA MAX / STEEVE-MAX x100

## GOLDEN BUILDS
- GOLDEN V5.4: branche bionic-v3-dev (reference)
- GOLDEN V6.x: branche Work1 (100% parite + optimization_engine + audits)
- Validation STEEVE-MAX: OFFICIELLE

## Accompli

### Phases 1-5C — Import, Gouvernance, Audits
### Phase 5C-R — Restauration optimization_engine (VALIDE)
### Montage Preview V6
- URL: https://huntiq-restore.preview.emergentagent.com

### Corrections V6
- Weather API 2.5
- Exclusion V7 active

### GOLDEN BUILD Audit V5.4 → V6.x
- 85/85 modules (100% parite)

### Audit Total + Inspection Microscopique
- 5 rapports, 17 dimensions, 0 divergence

### FIX CRITIQUE: Hotspots V7 — Cache local (2026-03-23)
- Triple verification V7 (point V5 + cache local 41,944 polygones + Overpass fallback)
- Commit: 64bcdfac

### MIGRATION CERCLES 600m + ADMIN PREMIUM FIX (2026-03-24)
- **Directive STEEVE-MAX: Conversion carres → cercles 600m**
  - hotspot_service.py: Cercle 600m (48pts) remplace contours organiques
  - hotspot_engine.py: Cercle 600m remplace convex hull V3
  - AdminHotspots.jsx: BIONIC V3 → V6 + satellite 600m
  - BionicEngineHub.jsx: BIONIC V3 → V6
- **Correction Admin Premium hotspots sur eau**
  - 7 causes identifiees et corrigees
  - Cache eau V7: 41,944 polygones au demarrage
  - BCE-4X: PASS 1800/1800 (WATER-001, GEOM-003)
- **Resultats**
  - Admin: 300 hs, 12 regions, ZERO sur eau
  - Carte: 7 hs, 9 exclus eau, 55ms
- **Rapports**
  - audit/geometry_square_to_circle_migration.md
  - audit/zones_circulaires_600m_alignment.md
  - audit/admin_premium_hotspots_water_fix.md
- Commit: 8e99f3fe

## Moteurs Verrouilles V6.x
1. organic_zones_v7
2. corridors_v10
3. exclusion_engine_v7
4. behavior_engine
5. solunar/astro V5 restaure
6. weather_engine 2.5
7. optimization_engine
8. hotspots_engine V6/V7 (CERCLES 600m + cache local eau)
9. admin_hotspots V6 (CERCLES 600m + BCE-4X PASS)

## Preview URL
https://huntiq-restore.preview.emergentagent.com

## Backlog

### P0 — En attente
- Validation STEEVE-MAX du fix cercles 600m + Admin Premium

### P1 — A venir
- Phase BSAA-2: Implementation module BIONIC Social Ads Automation

### P2 — Futur
- Merge Work1 vers main
- Nettoyage /app/audit_historical/
