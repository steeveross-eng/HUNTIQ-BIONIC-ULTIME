# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026 — Phase 3.3-U-PRIME COMPLETE

---

## Phase 3.2-CV v2 — CERTIFIE PAR STEEVE-MAX
- Meta-exclusion: center_in_urban_meta_zone() — 2km / 8%
- Tests: 12/12 PASSED
- PREVIEWS A/B/C valides

## Phase 3.3-U-PRIME — COMPLETE
- 608 lignes code mort V5 supprimees
- 3 composants neutralises (BionicMicroZones, TerritoryShell, BionicMapOverlay)
- 1 fonction V5 desactivee (generateBionicZonesV5 = stub vide)
- ZERO residu V5 dans le codebase
- Frontend compile sans erreur
- Rapport: /audit/phase_33_uprime_report.md

### Architecture V6 finale
- Pipelines autorises: V2 organic-zones, V6 corridors, V2 alimentation, V1 stands
- Pipeline V5 bounds: DEFINITIVEMENT DESACTIVE
- Meta-exclusion: 2km rayon, 8% seuil, tous pipelines
- SAFE MODE: TRUE, 101K polygones, 222m buffer, 1% seuil

---

## Phases completees
- Phase 1-3: Import, Archive, Gouvernance
- Phase 4: Audit moteurs
- Phase 5B: Audit coherence
- Phase 5C: Audit historique
- Phase BSAA-0/1: Faisabilite + Architecture
- Phase 2.5-3.1: TNE, Stands, Weather, WindFlow
- Phase 3.2-S: Safe Mode, Cache purge
- Phase 3.2-V: Validation visuelle
- Phase 3.2-CV v2: META-EXCLUSION (CERTIFIE)
- Phase 3.3-U-PRIME: Nettoyage V1-V5 (COMPLETE)

## Phases a venir
- ULTRA-MAX++ Lock (CONDITIONNE a validation 3.3-U-PRIME)
- Phase BSAA-2: Implementation (GELE)
- Merge Work1 -> main (INTERDIT sans validation complete)
