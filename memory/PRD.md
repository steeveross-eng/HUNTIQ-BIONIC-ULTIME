# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026 — ULTRA-MAX++ v3.0 APPLIQUE

---

## ULTRA-MAX++ v3.0: APPLIQUE — EN ATTENTE VALIDATION STEEVE-MAX

### Verrous Runtime Injectes (7/7 ACTIFS)
- V1: Parametres de cache IMMUTABLES (SAFE_MODE, BUFFER_DEG)
- V2: Pipelines d'exclusion IMMUTABLES (URBAN 1%, WATER 25%)
- V3: Pipeline legacy V5 NEUTRALISE definitivement
- V4: Meta-exclusion 2km/8% INCONTOURNABLE
- V5: SAFE MODE permanent SCELLE
- V6: Modules V1-V5 bloques (CIRCLE_RADIUS=600)
- V7: Invariant SCORE=0ELEMENT verrouille

### Registre Immutable
- 12 constantes scellees dans `_UltraMaxLockedRegistry`
- Boot guard + Runtime guard a chaque appel pipeline
- Journal des violations accessible

### Tests: 43/43 PASS
- /backend/tests/test_meta_exclusion_bce4x.py (12 tests)
- /backend/tests/test_score_invariant_bce4x.py (3 tests)
- /backend/tests/test_ultra_max_runtime_lock.py (28 tests)

### Rapport
- /app/HUNTIQ-V6-import/audit/ultra_max_lock_report.md

---

## PHASES ANTERIEURES COMPLETEES

### Phase 3.2-CV v2: CERTIFIE
- Meta-exclusion 2km/8% sur TOUS pipelines

### Phase 3.3-U-PRIME: COMPLETE
- 608 lignes V5 supprimees, 3 composants neutralises

### INVARIANT SCORE=0ELEMENT: IMPLEMENTE
- Score=0, classe=EXCLU en zone urbaine meta-exclue

### Documentation: LIVREE
- /audit/bce4x_max_certification_phase32cv.md
- /audit/phase_33_uprime_report.md
- /audit/documentation_finale_bce4x_max.md

---

## Phases a venir
- **Validation ULTRA-MAX++** par STEEVE-MAX (BLOQUANT)
- Merge Work1 -> main (**INTERDIT** sans autorisation explicite)
- Restauration auto_optimization.py -> optimization_engine (P2, GELE)
- Phase BSAA-2 Implementation (P2, GELE)
