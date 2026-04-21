# PLAN_PREVENTION_REGRESSION_Ω — TERRITOIRE
> **Ordre :** `PHASE_ZERO_PLUS_CONSOLIDATION_GOUVERNANCE_Ω` — X30
> **Principe :** ZERO-REGRESSION DOUBLÉ

## Objectif
Empêcher toute régression fonctionnelle dans TERRITOIRE par défense en profondeur :
détection, blocage, rollback automatique.

## Couches de protection (5 niveaux)

### Niveau 1 — Hook `pre-commit` Jest
- **Fichier** : `.git/hooks/pre-commit`
- **Règle** : Tout commit touchant `frontend/src/components/territoire/`, `frontend/src/lib/renduOmegaStore.js`, `frontend/src/lib/__tests__/` DOIT passer `yarn test`
- **Effet en cas d'échec** : commit REFUSÉ

### Niveau 2 — Sentinelles Jest (57 tests)
- **Emplacement** : `/app/frontend/src/lib/__tests__/*.test.js`
- **Rôle** : Contrôle parité fonctionnelle + pipeline unique + absence rendu anthropique
- **Suites** :
  - `inspectionBioFiltering.test.js`
  - `nutritionSalinesBinding.test.js`
  - `phase_xiv_functional_parity.test.js`
  - `phase_xv_contamination_parity.test.js`
  - `phase_xvi_enforce_single_pipeline.test.js`

### Niveau 3 — Enforcement runtime
- `enforceInstitutionalPipeline(caller, context)` bloque `bypassOmega` et `filtered=false`
- `assertNoAnthropicRender(feature, caller)` lève une erreur si feature urbaine
- Compteurs globaux : `window.__RAW_RENDER_ATTEMPTS__`, `window.__ANTHROPIC_RENDER_FAILURES__`

### Niveau 4 — Registre V30 SHA-256
- `registry_lock_omega.py` calcule/valide le hash des 41 engines
- Toute dérive → audit écarte le build

### Niveau 5 — Rollback automatique
- Détection régression → script `scripts/rollback_to_v30.sh` (à usage manuel signé)
- Procédure : `git log --oneline` → identifier dernier commit V30 + Jest 57/57 PASS → `git revert` ou cherry-pick rollback

## Détection régression (triggers)
| Trigger | Niveau | Action |
|---|---|---|
| `yarn test` < 57 PASS | 2 | Bloque hook, refuse commit |
| `window.__RAW_RENDER_ATTEMPTS__.count > 0` | 3 | Log console + dashboard alerte |
| `window.__ANTHROPIC_RENDER_FAILURES__.length > 0` | 3 | Log console + throw Error |
| SHA-256 V30 modifié | 4 | Build audit FAIL |
| Supervisor service DOWN | 1 (infra) | Notification Commandant |

## Rapport obligatoire en cas de régression
Fichier : `/app/memory/INCIDENTS_Ω.md` (ajouté en mode append)
Contenu obligatoire :
- Timestamp ISO
- Trigger déclenché
- Commit auteur/hash
- Impact (nombre de tests en échec, composants touchés)
- Décision (rollback / correction / escalade)
- Signature

## Interdictions strictes
- ❌ Désactiver hook `pre-commit`
- ❌ Commit avec `--no-verify` sur TERRITOIRE
- ❌ Modifier un test Jest sentinelle sans ordre signé
- ❌ Tolérer un seul `RAW_RENDER_ATTEMPT`

## Signature
Agent Emergent — sous autorité COMMANDANT STEEVE-MAX
