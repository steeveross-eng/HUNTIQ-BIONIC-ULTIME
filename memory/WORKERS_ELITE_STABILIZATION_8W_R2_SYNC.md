# WORKERS_ELITE_STABILIZATION_8W_R2_SYNC — DEPLOY READY
## P22ΩΩ_ELITE_STABILIZATION_8W_R2_SYNC_Ω · 2026-06-07 · COMMANDANT STEEVE-MAX
## BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

---

## 🎯 OBJECTIF DOCTRINAL
1. **Stabiliser la configuration workers Elite** : confirmer 8 workers (vs 6w défensif) selon calibration mathématique <5% throttle
2. **Corriger STALE_R2** : harmoniser sync FS↔R2 pour `lag_max_s < 60s` et `sync_status = OK/MATCH` sur tous les workers actifs

---

## ✅ DÉCISION CONFIG WORKERS : 8 WORKERS ELITE CONFIRMÉ

**Modélisation mathématique** (référence `WORKERS_ELITE_CALIBRATION_THROTTLE_LT_5_PCT.md`) :

| Config | Quota cumul | Avec pacing | Throttle | Throughput |
|--------|-------------|-------------|----------|------------|
| 6w sans pacing | 3.6 vCPUs (90%) | — | 5-8 % | 100 % |
| 6w + pacing 30ms | 3.13 vCPUs (78%) | idle 13% | <2 % | 87 % |
| 7w + pacing 40ms | 3.49 vCPUs (87%) | idle 17% | 3-5 % | 102 % |
| **8w + pacing 50ms** ✅ | **3.74 vCPUs (94%)** | **idle 20%** | **3-5 %** | **117 %** |

**Verdict** : 8 workers + pacing 50ms = meilleur compromis throughput/throttle. Config déjà déployée dans `TARGET_WORKERS_ELITE=8` + `WORKER_PACING_MS=50`.

---

## 🔧 PATCHES STALE_R2 (ADDITIFS · Verrou Phase III intact)

### 1. `r2_state_persistence_omega.py` — `prune_orphan_state_keys()`
- Nouvelle fonction de purge cross-pod-safe
- Filtre par `grid_file` matching → préserve cohabitation autres pipelines (ex Phase 1 résiduelle)
- Option `dry_run` pour audit sans suppression
- Retour structuré : `{checked, purged, kept_active, kept_other_pod, errors, dry_run}`

### 2. `zerocost_worker_seed_r5.py` — `BOOT UNIFIED-SYNC FS+R2`
- Au démarrage du worker, post `_load_worker_state()`, appel `_save_worker_state(r5_idx_done, species_done_current)`
- Garantit FS et R2 avec **timestamp unifié** dès le boot
- Élimine le lag artificiel (FS conserve ancien ts + R2 reçoit fresh ts → divergence)
- Log : `[STATE_FILE_Ω] BOOT UNIFIED-SYNC FS+R2 OK · worker_idx=N · r5=M · species=K`

### 3. `zerocost_seed_r5_supervisor_watchdog.sh` — Auto-purge cross-pod-safe
- Appel automatique `prune_orphan_state_keys(active_worker_count=$TARGET_WORKERS, expected_grid_file=$LOCAL_GRID)` après chaque respawn workers
- Préserve les clés cross-pod (Phase 1 ou autres pipelines partageant le bucket R2)
- Idempotent · best-effort · log structuré dans `/var/log/supervisor/zerocost-seed-r5-watchdog.out.log`

---

## 📊 VALIDATION PREVIEW POST-CORRECTIFS

**Tier-status `/api/v30/runtime/tier-status` avant correctifs** :
- `lag_max_s = 446s` ❌
- `sync_status = STALE_R2` sur 2/3 workers ❌
- R2 inventory contenant 6 keys (3 actives + 3 vestiges) ❌

**Tier-status `/api/v30/runtime/tier-status` après correctifs** :
- `lag_max_s = 12s` ✅ (<60s)
- `sync_status = MATCH/OK` sur **3/3 workers actifs** ✅
- `lag_avg_s = 4s · lag_min_s = 0s` ✅
- Cross-pod keys (Phase 1) préservées intactes 🔵

**Logs workers (preuve BOOT UNIFIED-SYNC)** :
```
worker_0.log : BOOT UNIFIED-SYNC FS+R2 OK · worker_idx=0 · r5=13 · species=3
worker_1.log : BOOT UNIFIED-SYNC FS+R2 OK · worker_idx=1 · r5=15 · species=0
worker_2.log : BOOT UNIFIED-SYNC FS+R2 OK · worker_idx=2 · r5=14 · species=1
```

---

## 🚀 COMPORTEMENT POD ELITE POST-DEPLOY

Au boot du pod Elite (cpu.max ≥ 400000) :
1. Watchdog détecte `TIER=ELITE · TARGET=8 · stagger=2000ms · pacing=50ms`
2. Daemon spawn 8 workers avec délai 2s entre chacun (spread 14s)
3. **Chaque worker fait BOOT UNIFIED-SYNC FS+R2** dès `_load_worker_state()` → lag=0s immédiat
4. **Purge cross-pod-safe** des clés R2 orphelines (worker_index ≥ 8) matchant la grille active
5. Cross-pod keys (autres pipelines, Phase 1) **préservées intactes**

**Vérification distante** :
```bash
curl https://huntiq-restore.emergent.host/api/v30/runtime/tier-status | jq \
  '.tier, .workers.count, .cpu.stat.throttle_ratio_pct, .r2_state_lag.summary'
```

**Attendu** :
```json
"ELITE"
8
< 5.0
{"workers_with_both_fs_r2": 8, "lag_min_s": 0, "lag_max_s": <60, "lag_avg_s": <30}
```

---

## 🛡️ VERROU PHASE III · CONFORMITÉ TOTALE
- ✅ Aucun engine touché
- ✅ Aucun pipeline supprimé
- ✅ Strict additif : 3 fonctions/blocs ajoutés, comportement legacy préservé si env unset
- ✅ Cross-pod safety : ne casse JAMAIS les pipelines cohabitants
- ✅ Boot UNIFIED-SYNC est `try/except` gracieux
- ✅ Rollback simple via `git checkout`

---

## 📌 STATUT
- ✅ Code calibré + STALE_R2 corrigé en preview (2026-06-07)
- ✅ Workers preview 3w · lag_max=12s · sync 3/3 OK/MATCH
- ✅ Cross-pod cohabitation testée (Phase 1 keys préservées)
- ⏸️ **Attente Deploy par Commandant** pour activation Elite 8w

---

**FIN ELITE STABILIZATION 8W + R2 SYNC — DEPLOY READY**
