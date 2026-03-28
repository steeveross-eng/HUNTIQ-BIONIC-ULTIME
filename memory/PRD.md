# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026 — Phase 3.2-CV v2 CERTIFICATION

---

## Phase 3.2-CV v2 — Contre-Validation CERTIFICATION (COMPLETE — EN ATTENTE VALIDATION)

### Probleme resolu
Zones et corridors dans patches forestieres entre batiments zone portuaire Quebec/Beauport.

### Solution: META-EXCLUSION
- Cercle 2km, seuil 8% overlap urbain -> rejet TOTAL tous pipelines
- Tests unitaires: 12/12 PASSED
- Pipeline V5 NEUTRALISE (3 vecteurs frontend)
- Exclusions ULTIMES: V6, V2, Alimentation, Stands

### Livrables fournis
1. Snippet implementation + function center_in_urban_meta_zone()
2. Tests unitaires: /app/backend/tests/test_meta_exclusion_bce4x.py (12/12)
3. PREVIEW A (MonTerritoire): ZERO element BIONIC
4. PREVIEW B (/map): BIONIC V5: 0
5. PREVIEW C (Backend): Urbain=0, Foret=16/189/4/5
6. Logs backend Beauport: overlap 49% -> ALL rejected
7. Rapport: /audit/bce4x_max_certification_phase32cv.md
8. SAFE MODE permanent confirme
9. Alignement structurel confirme

### Pipelines Autorises
1. /api/v1/bionic/organic-zones (V2) — meta + individuel
2. /api/v6/corridors/analyze-full (V6) — meta + individuel
3. /api/v2/alimentation/analyze — meta + individuel
4. /api/v1/stand-recommendation/recommend — meta + individuel

### Pipelines Neutralises
1. generateBionicZonesV5 — DESACTIVE (3 vecteurs)
2. BionicMapOverlay -> BionicMicroZones — return null

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
- Phase 3.2-CV v2: META-EXCLUSION + CERTIFICATION (PRESENT)

## Phases a venir (BLOQUEES par validation)
- Phase 3.3-U-PRIME: Nettoyage code legacy V1-V5
- ULTRA-MAX++ Lock
- Phase BSAA-2: Implementation (GELE)
- Merge Work1 -> main (INTERDIT)
