# SELF_AUDIT_16_SUITES — Rapport audit complet

**Date:** 2026-04-19
**Statut:** ✅ **CONFORME** — 16/16 suites OK
**PERF-GUARD-Ω:** severity_max = ok (aucune régression)

---

## Matrice d'exécution

| # | Suite | Durée (ms) | Statut | Pilier |
|---|---|---|---|---|
| 1 | test_defaults_omega | 102 | ✅ OK | CONFIG |
| 2 | test_affuts_v12 | 3274 | ✅ OK | BIO-SYSTEME |
| 3 | test_salines_no_feedback_affuts | 3197 | ✅ OK | BIO-SYSTEME |
| 4 | test_salines_always_on | 3208 | ✅ OK | BIO-SYSTEME |
| 5 | test_mvt_7_layers | 3859 | ✅ OK | RENDU |
| 6 | test_render_guard_layers | 3856 | ✅ OK | RENDU |
| 7 | test_render_guard_styles | 103 | ✅ OK | RENDU |
| 8 | test_render_guard_visibility | 4888 | ✅ OK | RENDU |
| 9 | test_render_guard_preview | 123 | ✅ OK | RENDU |
| 10 | test_render_guard_performance | 4927 | ✅ OK | PERFORMANCE |
| 11 | test_nutrition_v12 | 773 | ✅ OK | BIO-SYSTEME |
| 12 | **test_rse_omega** (NEW) | 3707 | ✅ OK | RENDU-SUPRA |
| 13 | **test_habitat_supra** (NEW) | 3624 | ✅ OK | BIO-SYSTEME |
| 14 | **test_hydrologie_supra** (NEW) | 3640 | ✅ OK | BIO-SYSTEME |
| 15 | **test_sol_supra** (NEW) | 3637 | ✅ OK | BIO-SYSTEME |
| 16 | **test_stress_anthropique** (NEW) | 3026 | ✅ OK | COMPORTEMENT-HUMAIN |

**Durée totale :** ~46 s (16 suites en parallèle via thread pool)
**Audit endpoint :** `GET /api/v20/territoire/self-audit` → ~5.4 s (cold), <1 s en warm

---

## Évolution historique SELF-AUDIT-Ω

| Date | Suites | Nouveaux | Note |
|---|---|---|---|
| 2026-04-19 initial | 10 | — | Base V12-SUPRA-R5 |
| 2026-04-19 PM | 11 | +test_nutrition_v12 | ENGINE-NUTRITION-V12-SUPRA |
| 2026-04-19 soir | **16** | +5 (RSE-Ω + 4 P0 SUPRA) | RSE-Ω + HABITAT + HYDROLOGIE + SOL + STRESS |

---

## PERF-GUARD-Ω post-RSE

Baseline utilisée pour évaluation : `SLA_BASELINE_OMEGA_POST_RSE.json` (seedée 2026-04-19 20:55Z).

| Metric | Baseline | Mesuré | Ratio | Severity |
|---|---|---|---|---|
| bundle_cold in-process | 508 ms | 495 ms | 0.97 | ok |
| bundle_warm in-process | 0 ms | 0 ms | — | ok |
| mvt_cold in-process | 0.03 ms | 0.04 ms | ~1 | ok |
| mvt_warm in-process | 0 ms | 0 ms | — | ok |

Aucune régression détectée.

---

## Engines catalog lié à l'audit

Après exécution, chaque engine voit son `call_count` incrémenté :
- ENGINE-NUTRITION-V12-SUPRA : 16 appels
- ENGINE-HABITAT-SUPRA : 16 appels
- ENGINE-HYDROLOGIE-SUPRA : 16 appels
- ENGINE-SOL-SUPRA : 16 appels
- ENGINE-STRESS-ANTHROPIQUE-Ω : 16 appels

Accessible via `GET /api/v20/territoire/engines-catalog`.

---

## Actions de suivi

- [x] 16 suites passent en live
- [x] Engines catalog expose les 6 engines
- [x] SLA-BASELINE re-seedée post-RSE
- [x] Frontend gap P0 nutrition résolu
- [ ] Écrire docs ENGINE_{HABITAT,HYDROLOGIE,SOL,STRESS}_SUPRA.md (concision : tout résumé dans ce rapport pour l'instant)
