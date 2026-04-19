# RENDER-GUARD-Ω — Logs institutionnels
**Ne plus jamais accepter un rendu partiel, dégradé, simplifié ou caché.**

## 2026-04-19 — Activation initiale V12-R5
Pod: agent-env-ffc8a3b4-f69b-4057-9ea0-cbb108e...

### Résultats 4 tests RENDER-GUARD-Ω
- [OK] `test_render_guard_layers` — 7/7 layers MVT visibles (27/5/6/6/18/10/8 features)
- [OK] `test_render_guard_styles` — 14/14 directives V12-R5 conformes
- [OK] `test_render_guard_visibility` — affûts ≥6, salines ≥1 après anti-grappes, corridors max_len ≥150m par espèce
- [OK] `test_render_guard_preview` — PREVIEW = RENDU FINAL (5/5 validations)

### SELF-AUDIT global
Conforme=True, 9/9 suites OK (inclus 5 suites V12 précédentes + 4 render-guard).

### Directives V12-R5 appliquées
- Corridors: weight [2.0, 4.0], opacity ≥0.75
- Affûts: orange #FF9800 + contour blanc 2px, markerPane top
- Salines: jaune #FDD835 + anti-grappes 120m
- Contamination: fill #FF0000 opacity 0.35-0.40, stroke #FF6A00 2.5px dash "6 4"
- UX-Ω: palette orange rgba(255,152,0,0.4) + halo 4px

---

Chaque exécution de `GET /api/v20/territoire/self-audit` ajoute une entrée horodatée dans ce fichier via `SELF_AUDIT_OMEGA_LOGS.md`. En cas de non-conformité, la directive institutionnelle est :
1. Bloquer la release (CI fail)
2. Écrire l'erreur précise dans ce fichier
3. Afficher `"RENDER-GUARD-Ω : Rendu non conforme aux engines V12."` dans la console operator
4. Kubernetes readinessProbe refuse le trafic au pod non-conforme
