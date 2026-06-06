# WORKERS_SCALE_ELITE_PLUS — DEPLOY READY
## P22ΩΩ_WORKERS_SCALE_ELITE_PLUS_Ω_AUTODETECT · 2026-06-06 · COMMANDANT STEEVE-MAX
## BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

---

## 🎯 OBJECTIF
Permettre au même watchdog de tourner à **TARGET=3 workers** sur le pod preview
(2 vCPUs) et **TARGET=8 workers** sur le pod Elite (4 vCPUs) **sans manipulation
manuelle**. Auto-détection via `cgroup cpu.max`.

---

## 📦 FICHIER MODIFIÉ (additif strict)
- `/app/backend/tools/zerocost_seed_r5_supervisor_watchdog.sh`

**Diff conceptuel** :
- ❌ AVANT : `TARGET_WORKERS=3` (hardcodé)
- ✅ APRÈS : `TARGET_WORKERS` = résolu dynamiquement via `cpu.max` lecture

L'ancienne ligne hardcodée est **préservée en commentaire doctrinal** (Verrou Phase III) :
```bash
# ─── ANCIEN ASSIGN (préservé doctrinalement) : TARGET_WORKERS=3 ───
```

---

## 🔧 LOGIQUE D'AUTO-DÉTECTION

```bash
TARGET_WORKERS_PREVIEW="${TARGET_WORKERS_PREVIEW:-3}"
TARGET_WORKERS_ELITE="${TARGET_WORKERS_ELITE:-8}"
_CPU_QUOTA_RAW=$(awk '{print $1}' /sys/fs/cgroup/cpu.max)

if [[ "$_CPU_QUOTA_RAW" == "max" ]]; then
    TARGET_WORKERS=$TARGET_WORKERS_ELITE   # quota illimité (hyperscale)
elif [[ "$_CPU_QUOTA_RAW" =~ ^[0-9]+$ ]] && (( _CPU_QUOTA_RAW >= 400000 )); then
    TARGET_WORKERS=$TARGET_WORKERS_ELITE   # ≥ 4 vCPUs
else
    TARGET_WORKERS=$TARGET_WORKERS_PREVIEW # défensif (preview ou inconnu)
fi
```

### Matrice de détection validée

| `cpu.max` | Tier | TARGET |
|---|---|---|
| `200000 100000` (2 vCPUs · preview) | PREVIEW | **3** |
| `300000 100000` (3 vCPUs hypothèse) | PREVIEW | **3** |
| `400000 100000` (4 vCPUs · **Elite**) | **ELITE** | **8** |
| `800000 100000` (8 vCPUs hyperscale) | ELITE | 8 |
| `max <PERIOD>` (illimité) | ELITE_UNLIMITED | 8 |
| vide / non-lisible | PREVIEW (défensif) | 3 |

### Overrides via env (optionnels, jamais requis)
- `TARGET_WORKERS_PREVIEW` — défaut 3
- `TARGET_WORKERS_ELITE` — défaut 8

---

## 📋 STATUT POST-PATCH (preview courant)

✅ Watchdog redémarré · pickup nouveau code
✅ Log démarrage : `MIN_WORKERS=3 · TARGET=3 · TIER=PREVIEW (cpu.max=200000µs · <400000 ou non-lisible)`
✅ Workers PIDs préservés (1176-1178 · uptime 59min+) — aucun respawn parasite
✅ RELANCE count stable (zéro boucle infinie)
✅ R2 dual-write toujours actif (state files synchronisés)
✅ Verrou Phase III intact (additif uniquement · ancien `TARGET_WORKERS=3` préservé en commentaire)

---

## 🚀 PROCÉDURE DE DÉPLOIEMENT POD ELITE

1. **Cliquer le bouton `Deploy`** dans l'interface chat Emergent
2. **Confirmer `Deploy Now`**
3. **Attendre 10-15 min** le provisionnement
4. **Sur le pod Elite** :
   - Le watchdog au démarrage lira `cpu.max` = `400000 100000` (ou supérieur)
   - Détection automatique → `TIER=ELITE · TARGET=8`
   - Spawn de 8 workers (vs 3 sur preview)
   - 8 partitions modulo 8 sur la grille `qc_limitrophes` (~42 R5/worker)
   - State files seed depuis R2 (cold-start automatique)

---

## 🔍 VÉRIFICATION POST-DEPLOY ELITE

À exécuter sur le pod Elite après deploy :

```bash
# 1. Vérif TIER détecté
sudo supervisorctl tail zerocost-seed-r5-watchdog stdout | head -3
# DOIT contenir : TIER=ELITE (cpu.max=400000µs ≥ 400000) · TARGET=8

# 2. Vérif 8 workers actifs
ps -ef | grep zerocost_worker_seed_r5 | grep -v grep | wc -l
# DOIT : 8

# 3. Vérif cold-start R2 OK
grep "COLD-START RESUME depuis R2" /var/log/bionic-zerocost-seed-r5/worker_*.log
# DOIT contenir 8 occurrences (une par worker)

# 4. Vérif throttling acceptable (Elite quota 4 vCPUs)
cat /sys/fs/cgroup/cpu.stat | grep -E "nr_periods|nr_throttled"
# Throttling attendu : <30% (vs 90% sur preview 2 vCPUs)

# 5. Vérif R2 dual-write actif
ls -la /var/log/bionic-zerocost-seed-r5/state_worker_*.json
# DOIT : 8 fichiers state_worker_{0..7}.json fraîchement écrits
```

---

## 🛡️ ROLLBACK PROCEDURE
Si problème post-deploy Elite :

```bash
# Forcer le tier preview même sur Elite (downscale d'urgence)
sudo systemctl --no-pager status zerocost-seed-r5-watchdog
# Édit /etc/supervisor/conf.d/zerocost-seed-r5.conf :
#   environment=...,TARGET_WORKERS_ELITE="3"
sudo supervisorctl restart zerocost-seed-r5-watchdog
```

Ou rollback complet :
```bash
cd /app && git checkout backend/tools/zerocost_seed_r5_supervisor_watchdog.sh
sudo supervisorctl restart zerocost-seed-r5-watchdog
```

---

## 🛡️ VERROU PHASE III
- ✅ Modification strictement additive (ancien `TARGET_WORKERS=3` préservé en commentaire)
- ✅ Aucun engine modifié
- ✅ Aucun pipeline supprimé
- ✅ Fallback défensif : si lecture `cpu.max` échoue, retombe sur preview TARGET=3
- ✅ Compatible R2 dual-write (architecture cold-start safe)

---

**FIN PATCH ELITE_PLUS — PRÊT POUR DEPLOY**
