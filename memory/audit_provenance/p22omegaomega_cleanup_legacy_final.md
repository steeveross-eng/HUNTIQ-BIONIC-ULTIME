# 🧹 P22ΩΩ_CLEANUP_LEGACY_FINAL · TERRITOIRE Ω
**Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE — Livrable 4/4
**Date** : 2026-05-19 · **Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX

> ⚠️ **PLAN DE NETTOYAGE — Aucune suppression sans autorisation explicite Phase 2.**

---

## 1. PRINCIPE DE NETTOYAGE

> *« Avant de moduler, on supprime ce qui ne sert plus. »*

Chaque candidat à la suppression a été audité avec :
- Recherche `grep -rln` pour usage réel dans le code de production.
- Exclusion des refs dans `__pycache__`, `archives/`, `legacy/`, `HUNTIQ-V6-import/`.
- Distinction usage **PROD** vs usage **TESTS** vs usage **TOOLS**.
- Vérification que la suppression n'impacte pas `TERRITOIRE_ESSENTIEL_1WORKER`.

---

## 2. CANDIDATS BACKEND À SUPPRIMER (catégorisés)

### 🟢 CATÉGORIE A — Suppression sans risque (0 ref prod)

| # | Fichier | Lignes | Justification |
|---|---|---|---|
| A1 | `engines/v8_institutional/engine_ia_corridors_omega.py` | ~400 | V4 LEGACY remplacé par V5 organic. 0 ref prod, refs uniquement dans tests legacy. |
| A2 | `engines/v8_institutional/federal_datasets_omega.py` | ~200 | 0 ref prod. Référencé uniquement dans 5 tests legacy. |
| A3 | `engines/v8_institutional/science_gaps_datasets.py` | ~150 | Idem. 0 ref prod. |

**Total catégorie A** : **~750 lignes** de code prod purgeables.

### 🟡 CATÉGORIE B — Suppression conditionnelle (refs dans tests legacy)

| # | Fichier | Refs prod | Decision |
|---|---|---|---|
| B1 | `engines/v8_institutional/origine_externe_inversion_omega.py` | ❌ refs tools + tests | 🟠 À évaluer (tools maintenance) |
| B2 | `engines/v8_institutional/doctrine_v90_omega.py` | ⚠️ ref `server.py` | 🔴 NE PAS SUPPRIMER |

### 🔴 CATÉGORIE C — Engines à CONSERVER (chaîne piliers / sécurité)

| # | Fichier | Pourquoi conserver |
|---|---|---|
| C1 | `engine_comportement.py` | Ref par `piliers_router`, `securite_omega_v19`, `supra_v8` |
| C2 | `engine_comportement_avance.py` | Idem |
| C3 | `engine_psychologie.py` | Ref par `piliers_router`, `securite_omega_v19` |
| C4 | `securite_omega_v19.py` | Chaîne sécurité doctrinale active |
| C5 | `protections_omega.py` | Idem |
| C6 | `phase_omega_secure_lockdown.py` | Ref par `fusion_territoire_omega_router` |
| C7 | `engine_render_omega.py` | Ref par lockdown + doctrine_v90 + server |
| C8 | `engine_rendu_omega.py` | Pipeline post-V5 actif |
| C9 | `engine_ia_corridors_organic_omega.py` | **V5 PRIMARY** — Cœur des corridors |
| C10 | `lep_ingestion_omega.py` | Ref par `server.py` + self_audit_omega |
| C11 | `origine_externe_filter_omega.py` | Ref par `v20_performance_bundle.py` |

---

## 3. TESTS LEGACY À ARCHIVER (déplacement, pas suppression)

### 3.1 Tests phases historiques (116 fichiers)

```
/app/backend/tests/test_phase_a_*.py        → /app/backend/tests/archive/phases_a_e/
/app/backend/tests/test_phase_b_*.py        → idem
/app/backend/tests/test_phase_c_*.py        → idem
/app/backend/tests/test_phase_d_*.py        → idem
/app/backend/tests/test_phase_e_*.py        → idem
/app/backend/tests/test_phase_xi_*.py       → /app/backend/tests/archive/phases_xi_xv/
/app/backend/tests/test_phase_xii_*.py      → idem
/app/backend/tests/test_phase_xiii_*.py     → idem
/app/backend/tests/test_phase_xiv_*.py      → idem
/app/backend/tests/test_phase_xv_*.py       → idem
/app/backend/tests/test_phase_xvii_*.py     → /app/backend/tests/archive/phases_xvii_xix/
/app/backend/tests/test_phase_xviii_*.py    → idem
/app/backend/tests/test_phase_xix_*.py      → idem
```

**Volume** : 116 fichiers × ~100 lignes = **~12 000 lignes archivées**.

### 3.2 Tests rendu legacy (12 fichiers)
```
/app/backend/tests/test_render_*.py         → /app/backend/tests/archive/render/
```
**Volume** : 12 fichiers × ~125 lignes = **~1 500 lignes archivées**.

### 3.3 Méthode d'archivage (non destructive)
```bash
mkdir -p /app/backend/tests/archive/{phases_a_e,phases_xi_xv,phases_xvii_xix,render}
git mv /app/backend/tests/test_phase_a_*.py /app/backend/tests/archive/phases_a_e/
# ... (idem autres patterns)
```

L'usage de `git mv` préserve l'historique git. Les tests restent **consultables** mais ne sont **plus chargés automatiquement** par pytest (s'ils sont hors du `testpaths` configuré).

---

## 4. FRONTEND — composants déjà purgés (rappel Phase 1)

Pour mémoire, déjà supprimés par `P22ΩΩ_ALLEGEMENT_STRUCTUREL` (2026-05-17) :

```
✅ AmenagementPanel.jsx            (253 lignes)
✅ BionicZoneDiagnosticPanel.jsx   (449 lignes)
✅ DiagnosticExclusionsPanel.jsx   (367 lignes)
✅ MonTerritoireBionic.jsx         (594 lignes)
✅ PhaseAPanelV8.jsx               (357 lignes)
✅ PhaseCPanelV8.jsx               (237 lignes)
✅ StandDetailPanel.jsx            (204 lignes)
```
**Total déjà purgé** : 2 461 lignes frontend.

---

## 5. ORDRE D'EXÉCUTION (séquentiel, validation par étape)

### Étape 1 — Tests legacy archivés
```bash
mkdir -p /app/backend/tests/archive/{phases_a_e,phases_xi_xv,phases_xvii_xix,render}
git mv ...
```
**Validation** : pytest exécution actuelle inchangée (les tests legacy ne sont pas dans le run principal).

### Étape 2 — Suppression catégorie A (3 fichiers)
```bash
rm /app/backend/engines/v8_institutional/engine_ia_corridors_omega.py
rm /app/backend/engines/v8_institutional/federal_datasets_omega.py
rm /app/backend/engines/v8_institutional/science_gaps_datasets.py
```
**Validation** : 
- `curl /api/v20/territoire/bundle?...chevreuil` → 200 OK
- `curl /api/health` → 200 OK
- Screenshot Playwright TERRITOIRE Ω → CONFORMITÉ Ω 100% maintenue

### Étape 3 — Évaluation catégorie B
- B1 (`origine_externe_inversion_omega.py`) : 
  - Si tools de maintenance encore nécessaires → conserver
  - Sinon → supprimer + archiver tools associés
- B2 (`doctrine_v90_omega.py`) : **CONSERVER** (utilisé en prod)

### Étape 4 — Documentation finale
- Mise à jour `PRD.md`
- Mise à jour `CHANGELOG.md`
- Mise à jour `ARCHITECTURE_BIONIC_SNAPSHOT.md`
- Mise à jour `TERRITOIRE_STRUCTURE_OMEGA.json`

---

## 6. SYNTHÈSE — IMPACT QUANTIFIÉ

| Action | Lignes purgées/archivées | Type |
|---|---|---|
| Phase précédente (5/17) | 2 628 | DÉJÀ DONE |
| Cat. A backend (V4 + datasets) | ~750 | À supprimer |
| Tests phases archivés | ~12 000 | À archiver (git mv) |
| Tests rendu archivés | ~1 500 | À archiver (git mv) |
| **Total Phase 0 cleanup** | **~14 250 lignes** | (+2 628 déjà = 16 878 cumul) |

---

## 7. RISQUES & MITIGATIONS

| Risque | Probabilité | Mitigation |
|---|---|---|
| `engine_ia_corridors_omega.py` (V4) référencé en lazy import quelque part | Faible | grep -rln avant suppression |
| Tests legacy archivés réactivés involontairement | Très faible | `pytest --ignore=archive` |
| Suppression dataset cassant un endpoint admin | Faible | Curl test sur 142 endpoints avant/après |
| Tools maintenance dépendants de `origine_externe_inversion` | Moyenne | Conserver Cat. B1 par défaut |

---

## 8. CONDITIONS D'AUTORISATION PHASE 2

Avant d'exécuter quoi que ce soit, le Commandant doit :
1. ✅ Valider l'analyse monolithique (`p22omegaomega_analyse_monolithique_server.md`)
2. ✅ Valider le plan de découpage (`p22omegaomega_plan_de_decoupage_v10_v20.md`)
3. ✅ Valider la roadmap ZeroCost (`p22omegaomega_roadmap_zero_cost_engine.md`)
4. ✅ Valider ce plan cleanup
5. ✅ Donner l'autorisation explicite d'exécution

**Sans ces 5 validations, aucun fichier n'est touché.**

---

## 9. SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE
- **Livrable** : 4/4 — Cleanup legacy final
- **Validation** : COMMANDANT STEEVE-MAX
