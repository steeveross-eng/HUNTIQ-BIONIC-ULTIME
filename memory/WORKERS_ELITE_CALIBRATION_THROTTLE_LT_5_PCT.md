# WORKERS_ELITE_CALIBRATION_THROTTLE_LT_5_PCT — DEPLOY READY
## P22ΩΩ_ELITE_CALIBRATION_THROTTLE_LT_5_PCT_Ω · 2026-06-06 · COMMANDANT STEEVE-MAX
## BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

---

## 🎯 OBJECTIF
Sur le pod **Elite (4 vCPUs)**, atteindre :
- **8 workers actifs** (inferred_target_workers=8)
- **throttle_ratio_pct < 5 %**
- Maximisation du throughput R6 (≥ 3.5× preview attendu)
- Cohabitation FastAPI/MongoDB/e1_monitor stable

---

## 📊 MODÉLISATION MATHÉMATIQUE

**Données preview observées** (mesures cycles 3w sur 2 vCPUs) :
- Consommation moyenne par worker : **55-65 % d'un vCPU** (compute V20 H3/H6, CPU-bound)
- Memory : ~500 MB par worker

**Projection Elite (4 vCPUs · 8 workers SANS calibration)** :
```
8 workers × 60 % vCPU = 4.8 vCPUs cumulés théoriques
Quota disponible       = 4.0 vCPUs
Overshoot              = 20 %
Throttle attendu       = ~15-17 %  ❌ (cible <5%)
```

**Solution mathématique** :
```
Cible throttle    = <5 %
→ Consommation    ≤ 95 % du quota = 3.8 vCPUs cumulés
→ Par worker      ≤ 47.5 % d'un vCPU en moyenne
→ Réduction requise vs preview : ~21 %
```

**Mécanisme appliqué** :
- **WORKER_PACING_MS = 50** : pause asyncio 50ms après chaque R5 complète
- Compute moyen par R5 (5 species × 12 months × 24 hours = 1440 SEED + fan-out) : **~150-250 ms estimé**
- Pause 50ms → **idle ratio ~20-25 %** post-R5
- Consommation effective : **60% × (1 - 0.22) = 46.8 %** → 8 workers = 3.74 vCPUs = **93.5 % quota**
- **Throttle projeté : ~3-5 %** ✅

**Spawn stagger** : 2000ms entre workers (8w × 2s = 14s spread)
- Évite le spike de bootstrap V20 parallèle (~3-5s de pic CPU à 400 %+ qui déclenche probes liveness)
- Une fois steady-state atteint (T+20s), le pacing intra-worker régule

---

## 📦 FICHIERS MODIFIÉS (additif strict)

### 1. `/app/backend/tools/zerocost_seed_r5_supervisor_watchdog.sh`
Activation conditionnelle stagger + pacing en TIER=ELITE (preview reste à 0).

### 2. `/app/backend/tools/zerocost_seed_r5_daemon.sh`
- Lecture env `SPAWN_STAGGER_MS` (défaut 0 = preview legacy)
- Lecture env `WORKER_PACING_MS` (défaut 0 = preview legacy)
- Spawn loop : `sleep SPAWN_STAGGER_MS/1000` entre workers si activé
- Propage `WORKER_PACING_MS` aux workers via env

### 3. `/app/backend/tools/zerocost_worker_seed_r5.py`
- Lecture env `WORKER_PACING_MS` à la fin de chaque R5 complète
- Si > 0 : `await asyncio.sleep(WORKER_PACING_MS / 1000.0)` (non-bloquant)

---

## 🔧 CONFIGURATION FINALE PAR TIER

| Tier | TARGET | SPAWN_STAGGER_MS | WORKER_PACING_MS | Throttle projeté |
|---|---|---|---|---|
| **PREVIEW** (cpu.max < 400k) | 3 | **0** (legacy) | **0** (legacy) | ~92% (capacitaire 2vCPU) |
| **ELITE** (cpu.max ≥ 400k) | **8** | **2000** | **50** | **<5%** |
| **ELITE_UNLIMITED** (cpu.max = max) | 8 | 2000 | 50 | <5% |

**Overrides possibles via env** (si calibration fine post-deploy nécessaire) :
- `TARGET_WORKERS_ELITE` (défaut 8)
- `SPAWN_STAGGER_MS` (défaut 2000 en Elite, 0 en preview)
- `WORKER_PACING_MS` (défaut 50 en Elite, 0 en preview)

---

## 🚀 PROCÉDURE DE DÉPLOIEMENT

1. **Clic `Deploy`** dans l'interface Emergent
2. Attendre 10-15 min provisionnement pod Elite
3. Au boot pod Elite :
   - Watchdog lit `cpu.max ≥ 400000` → TIER=ELITE
   - TARGET=8 · SPAWN_STAGGER_MS=2000 · WORKER_PACING_MS=50
   - 8 workers spawnés avec délai 2s entre chacun (spread 14s)
   - Chaque worker fait pause 50ms après chaque R5 complète
4. **Vérification distante** (sans accès pod) :
   ```bash
   curl https://huntiq-restore.emergent.host/api/v30/runtime/tier-status | jq \
     '.tier, .workers.count, .cpu.stat.throttle_ratio_pct'
   ```
   **Attendu** :
   ```
   "ELITE"
   8
   <5.0
   ```

---

## 📈 BENCHMARKS PROJETÉS (Elite vs Preview)

| Métrique | Preview 3w | Elite 8w (sans calib) | Elite 8w (avec calib) |
|---|---|---|---|
| Workers | 3 | 8 | **8** ✅ |
| CPU quota | 2 vCPUs | 4 vCPUs | 4 vCPUs |
| Throttle ratio | 92 % | ~15-17 % | **<5 %** ✅ |
| Throughput R5/h | ~1.4 | ~2.8 (limité throttle) | **~4.6** (×3.3 preview) |
| Latency API médiane | 166ms | risque dégradation | <100ms (cible) |
| MTBF pod | ~3h | ~6h estimé | **>24h** (cible) |

---

## 🔍 CALIBRATION FINE POST-DEPLOY (si nécessaire)

Si après deploy le throttle reste > 5%, ajuster :

**Cas A — Throttle 5-10 %** : augmenter pacing
```bash
# Edit /etc/supervisor/conf.d/zerocost-seed-r5.conf :
environment=...,WORKER_PACING_MS="100"
sudo supervisorctl restart zerocost-seed-r5-watchdog
```

**Cas B — Throttle 10-20 %** : réduire workers à 7
```bash
environment=...,TARGET_WORKERS_ELITE="7"
sudo supervisorctl restart zerocost-seed-r5-watchdog
```

**Cas C — Throttle <2 % + workers idle** : réduire pacing
```bash
environment=...,WORKER_PACING_MS="20"
sudo supervisorctl restart zerocost-seed-r5-watchdog
```

Endpoint `/api/v30/runtime/tier-status` permet la mesure en temps réel.

---

## 🛡️ VERROU PHASE III
- ✅ Modifications strictement additives (env vars optionnels · défaut 0)
- ✅ Aucun engine modifié (V20/V10/V7 intacts)
- ✅ Aucun pipeline supprimé
- ✅ Preview comportement legacy 100 % préservé (workers PIDs 127-129 inchangés validé)
- ✅ Stagger et pacing désactivables instantanément via env override
- ✅ Rollback simple : `git checkout`

---

## 📌 STATUT
- ✅ Code calibré et déployé en preview (2026-06-06)
- ✅ Workers preview PIDs 127-129 inchangés · uptime 47min+ continu
- ✅ Backend FastAPI HTTP 200 · endpoint tier-status reflète config
- ⏸️ **Attente deploy Elite par Commandant** pour activation

---

**FIN CALIBRATION ELITE — DEPLOY READY**
