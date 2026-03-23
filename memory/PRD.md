# PRD.md — HUNTIQ-V6
# BCE-4X / BCE ULTRA MAX / STEEVE-MAX

## Probleme Original
Reconstruction du depot HUNTIQ-V6 depuis HUNTIQ-V5, gouvernance stricte BCE-4X, audits complets, restauration de fonctionnalites perdues.

## Architecture
- Backend: FastAPI (85 modules) | Frontend: React | DB: MongoDB
- Branche: Work1 | Gouvernance: BCE-4X / BCE ULTRA MAX / STEEVE-MAX

## Ce qui a ete accompli

### Phase 1-3 — Import/Certification (2026-03-22)
### Gouvernance (2026-03-22)
### Phase 4 — Audit Engines: 84 modules verifies
### Phase 5B — Audit Coherence inter-modules
### Phase BSAA-0/1 — Architecture BIONIC Social Ads Automation
### Phase 5C — Audit Historique: identification auto_optimization.py manquant
### Phase 5C-R — Restauration optimization_engine (VALIDE PAR STEEVE)

### Montage Preview V6 (2026-03-23)
- URL: https://huntiq-restore.preview.emergentagent.com

### Fix Service Meteo (2026-03-23)
- API 2.5 au lieu de OneCall 3.0, Commit: 60e5f624

### Fix Moteur Geospatial V7 (2026-03-23)
- EXCLUSION_ENGINE_VERSION=v7 active dans .env
- Verification: 0 hotspot sur eau, 0 corridor traversant lac
- Pipeline V7: exclusion Shapely, water union, cost grid, trail gen
- Zone urbaine: 7/7 rejetees | Zone forestiere: 17 valides, 24 rejetees
- Intelligence 5 moteurs actifs, score 53.9/100
- Rapport: audit/geospatial_engine_validation.md
- Commit: c20d9a7d

## Preview URL
https://huntiq-restore.preview.emergentagent.com

## Backlog Priorise

### P0 — En attente
- Validation visuelle Steeve du moteur geospatial V7

### P1 — A venir
- Phase BSAA-2: Implementation module BIONIC Social Ads Automation

### P2 — Futur
- Merge Work1 vers main
- Nettoyage /app/audit_historical/
