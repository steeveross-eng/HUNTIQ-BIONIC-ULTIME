# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026 — INVARIANT SCORE=0ELEMENT + Doc finale

---

## CERTIFICATION COMPLETE — EN ATTENTE ULTRA-MAX++

### Phase 3.2-CV v2: CERTIFIE
- Meta-exclusion 2km/8% sur TOUS pipelines
- 15/15 tests PASSED

### Phase 3.3-U-PRIME: COMPLETE
- 608 lignes V5 supprimees
- 3 composants neutralises
- ZERO residu V5

### INVARIANT SCORE=0ELEMENT: IMPLEMENTE
- BionicScoreBadge: masque si score=0 ou meta_excluded
- ModeGuidePro: "Zone urbaine" si meta_excluded
- displayScore: null si 0 zones + 0 corridors + heatmap exclu
- score-consolide: 0.0/EXCLU si meta-exclu
- heatmap: score_avg=0, points=[] si meta-exclu
- guide-pro: score=0, label=exclu si meta-exclu

### Documentation: LIVREE
- /audit/bce4x_max_certification_phase32cv.md
- /audit/phase_33_uprime_report.md
- /audit/documentation_finale_bce4x_max.md

### Tests: 15/15
- /backend/tests/test_meta_exclusion_bce4x.py (12)
- /backend/tests/test_score_invariant_bce4x.py (3)

---

## Phases a venir
- ULTRA-MAX++ Lock (conditionne a validation)
- Phase BSAA-2 Implementation (GELE)
- Merge Work1 -> main (INTERDIT)
