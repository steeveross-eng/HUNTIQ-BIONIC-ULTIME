# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026 — Phase 3.2-CV v2 (META-EXCLUSION)

---

## Phase 3.2-CV v2 — Contre-Validation avec META-EXCLUSION (COMPLETE)

### Probleme resolu
Zones et corridors apparaissaient dans les patches forestieres entre les batiments de la zone portuaire/Beauport. L'exclusion individuelle (600m) ne couvrait pas ces micro-forets en milieu urbain.

### Solution deployee: META-EXCLUSION
- Cercle de 2km autour du waypoint centre
- Si overlap urbain > 8%, ZERO zone/corridor/saline/affut autorise
- Pipeline V5 NEUTRALISE (3 vecteurs frontend)
- Exclusions ULTIMES etendues a TOUS les pipelines: V6, V2, Alimentation, Stands

### Pipelines Autorises (exclusions actives)
1. `/api/v1/bionic/organic-zones` (V2) — meta + individuel
2. `/api/v6/corridors/analyze-full` (V6) — meta + individuel
3. `/api/v2/alimentation/analyze` — meta + individuel
4. `/api/v1/stand-recommendation/recommend` — meta + individuel

### Pipelines Neutralises
1. `generateBionicZonesV5` — DESACTIVE (3 vecteurs)
2. `BionicMapOverlay` → `BionicMicroZones` — return null

### SAFE MODE
- BCE4X_URBAN_CACHE_SAFE_MODE = True
- Cache statique: 101,391 polygones
- IndexedDB v3, module cache cleared au mount
- ZERO injection dynamique OSM

### Rapport: `/audit/bce4x_max_certification_phase32cv.md`

---

## Statut: EN ATTENTE DE VALIDATION STEEVE-MAX

### Phases completees:
- Phase 1-3: Import, Archive, Gouvernance
- Phase 4: Audit moteurs
- Phase 5B: Audit coherence
- Phase 5C: Audit historique
- Phase BSAA-0/1: Faisabilite + Architecture
- Phase 2.5-3.1: TNE, Stands, Weather, WindFlow
- Phase 3.2-S: Safe Mode, Cache purge
- Phase 3.2-V: Validation visuelle
- Phase 3.2-CV v2: META-EXCLUSION (PRESENT)

### Phases a venir (BLOQUEES):
- Phase 3.3-U-PRIME: Nettoyage code legacy V1-V5
- ULTRA-MAX++ Lock
- Phase BSAA-2: Implementation (GELE)
- Merge Work1 → main (INTERDIT)
