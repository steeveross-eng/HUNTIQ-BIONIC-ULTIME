# P2 · WORKER PARTIAL RECOVERY · REDEPLOY READY

**Doctrine** : `P22ΩΩ_P2_WORKER_PARTIAL_RECOVERY_Ω` · COMMANDANT STEEVE-MAX · 2026-06-08
**Protocole** : BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF
**Statut** : ✅ PRÊT POUR REDEPLOY ELITE (lint + 7/7 tests Pytest + régression E2E Preview validés)

---

## 1. FICHIERS MODIFIÉS (2 fichiers · additif strict)

| Fichier | Type | Diff résumé |
|---|---|---|
| `backend/zerocost_workers_runtime.py` | Mutation interne (+108 / -32 lignes) | R3 partial respawn + refactor `_pids: list[int] → dict[int, int]` (worker_index→PID) · API publique inchangée |
| `backend/tests/test_worker_partial_recovery.py` | Nouveau fichier (+196 lignes) | 7 tests Pytest unitaires (mock-based · 0 subprocess réel) |

**Légende des changements** :
- API publique (`start_zerocost_workers_inprocess`, `stop_zerocost_workers_inprocess`) inchangée
- Bash watchdog `tools/zerocost_seed_r5_supervisor_watchdog.sh` → **intouché** ✅
- Worker script `tools/zerocost_worker_seed_r5.py` → **intouché** ✅
- Doctrine Verrou Phase III maintenue

---

## 2. DIAGNOSTIC FORENSIQUE (cause racine 5/8 chronique)

**Avant le fix** (lignes 363-368 originales) :
```python
# Partial recovery : si n_alive entre min et target, respawn manquants
if n_alive < worker_count:
    pass  # ← BUG : aucune action, le commentaire est un TODO non implémenté
```

→ Si 3 workers crashent au boot (idx 3,4,5 par ex.), il reste 5 alive ≥ min=3 → **le watchdog ne fait jamais rien**. État chronique 5/8 figé.

**Après le fix** :
1. **R3.a** · Refactor `_pids: list[int] → dict[int, int]` (worker_index → PID) pour tracking précis par index
2. **R3.b** · Watchdog détecte `missing_indices = set(range(worker_count)) - alive.keys()` sous 60s (1 cycle)
3. **R3.c** · Partial respawn ciblé sur les seuls indices manquants (PAS de full kill+respawn)
4. **R3.d** · Cooldown anti-thrash 5min (configurable via `WORKER_PARTIAL_RESPAWN_COOLDOWN_S`)
5. **R3.e** · Comportement legacy `n_alive < min_workers → full respawn` **préservé inchangé** ✅

---

## 3. R1 · SPAWN_STAGGER_MS=5000 (env var · gestion COMMANDANT)

**État code** : Lecture env var déjà implémentée (P22ΩΩ_SPAWN_STAGGER_INPROCESS_Ω précédent).
**Action requise** : `COMMANDANT` met à jour Secret Manager Elite : `SPAWN_STAGGER_MS=2000` → `5000`.

**Bénéfice attendu** :
- Boot 8 workers (stagger 5s) : 35s total · pic CPU ≤200% lissé (vs 14s · pic 400% actuel)
- Mitigation des liveness probe failures sur bootstrap V20 parallèle

Le code R3 fonctionne correctement avec `SPAWN_STAGGER_MS=2000` ou `5000` (paramétrique).

---

## 4. TESTS PYTEST · 7/7 RÉUSSIS

```
tests/test_worker_partial_recovery.py
  ✅ test_spawn_all_workers_returns_dict_indexed       (R3.a refactor list→dict)
  ✅ test_terminate_workers_accepts_dict_and_list      (compat legacy list)
  ✅ test_partial_respawn_detects_missing_indices      (R3 core fix · idx 3,4,5 → 8/8)
  ✅ test_partial_respawn_respects_cooldown            (anti-thrash 5min)
  ✅ test_legacy_full_respawn_below_min                (legacy preserved · Verrou III)
  ✅ test_stable_state_no_action                       (idempotence si 8/8 OK)
  ✅ test_cooldown_env_var_parsing                     (env var configuration)

Total: 7 passed in 0.84s
```

**Couverture** :
- Mocking complet `_is_pid_alive`, `_spawn_worker`, `_terminate_workers`, `_resolve_grid_file`, `_WORKER_SCRIPT`
- ZÉRO subprocess réel exécuté (tests rapides + reproductibles)

---

## 5. SCÉNARIOS D'ACTIVATION POST-DEPLOY

### Scénario 1 · Boot Elite normal (8 workers OK)
- `SPAWN_STAGGER_MS=5000` → spread bootstrap 35s
- Watchdog heartbeat toutes les 5min : `workers=8/8 OK`
- Aucune action partial respawn nécessaire

### Scénario 2 · Boot partiel (idx 3,4,5 crash au démarrage = état chronique actuel)
- Au 1er cycle watchdog (T+60s) :
  ```
  [WATCHDOG-PARTIAL] détection idx manquants : [3, 4, 5] (n_alive=5 >= min=3) · RESPAWN CIBLÉ
  [WATCHDOG-PARTIAL] respawn idx=3 PID=...
  [WATCHDOG-PARTIAL] respawn idx=4 PID=...
  [WATCHDOG-PARTIAL] respawn idx=5 PID=...
  [WATCHDOG-PARTIAL] cycle complete · respawned=3/3 · now 8/8 actifs
  ```
- État stable 8/8 atteint **sous 90s** après reboot Elite

### Scénario 3 · Worker crash en runtime
- 1 worker meurt à T+10min · n_alive=7 ≥ min=3
- Watchdog T+11min : partial respawn cooldown OK (>5min depuis dernier respawn)
- Idx manquant respawné · retour à 8/8

### Scénario 4 · Crash cascade (n_alive < min)
- Si 6 workers meurent simultanément (rare · OOMkill cluster) :
- Comportement legacy : full respawn (`_terminate_workers + _spawn_all_workers`)
- Comportement inchangé · Verrou Phase III

---

## 6. PLAN DE VÉRIFICATION POST-DEPLOY ELITE

**Phase 1 · Smoke check (T+2min après reboot)** :
```bash
curl /api/v30/runtime/tier-status
# Attendu : workers count=8/8 sous 2 cycles watchdog
```

**Phase 2 · Logs watchdog (T+5min)** :
```bash
# Sur Elite (via tier-status detail ou supervisor logs)
# Chercher : [WATCHDOG-PARTIAL] ou [β2-ΣΤ-INPROCESS-WATCHDOG] workers=8/8 OK
```

**Phase 3 · Régression Phase A + B** :
- NASA dry_run : 2-3 granules
- ESA dry_run : 3 produits L2A
- NRCan dry_run : 22 tuiles
- MFFP dry_run : 50 feuillets
- cdse-auth-probe : 401_invalid_grant (état attendu)

**Phase 4 · Test stress (optionnel · sur ordre)** :
- Real ingestion NASA HLS (1 granule · 47 MB) · vérifier que les 8 workers absorbent sans throttle

---

## 7. RISQUES & ROLLBACK

| Risque | Probabilité | Mitigation |
|---|---|---|
| Boucle de respawn infini | TRÈS FAIBLE | Cooldown 5min anti-thrash (par défaut) |
| Memory leak du worker tracking dict | NULLE | dict[int,int] · 8 entrées max, GC-friendly |
| Régression du chemin full respawn (n<min) | NULLE | Preserved inchangé · Test unitaire dédié |
| Incompatibilité API (`_pids`) avec autres modules | NULLE | Variable interne au module · grep confirmé 0 import externe |

**Rollback** : Simple `git revert` du commit (≤2 fichiers). Service backend redémarre proprement avec ancien code.

---

## 8. SÉQUENCE REDEPLOY ELITE

1. **COMMANDANT** :
   - (a) Mettre à jour Secret Manager Elite : `SPAWN_STAGGER_MS=5000` (recommandé)
   - (b) Clic "Deploy" UI Emergent
2. **AGENT** (post-deploy) :
   - Watchdog reboot Elite (uptime court)
   - `curl /api/v30/runtime/tier-status` → vérifier `workers count=8/8`
   - Régression Phase A + B (5 dry_run)
   - Si workers=8/8 confirmé : passer à directive (d) déblocage CDSE ou (f) Phase B real ingestion

---

**Préparé par** : Agent BCE-4X · Verrou Phase III maintenu · Aucune dépendance ajoutée · Aucun engine touché.
**Lint** : ✅ Python ruff/pyflakes clean
**Tests** : ✅ 7/7 pytest passed (0.84s · 0 subprocess réel)
**Régression Preview** : ✅ NASA + ESA + NRCan + MFFP + cdse-auth-probe OK
