# EXTERNALISATION_STATE_FILES_ATLAS_R2 — PATCH READY
## P22ΩΩ_EXTERNALISATION_STATE_FILES_R2_Ω · 2026-06-06 · COMMANDANT STEEVE-MAX
## BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF · DUAL-WRITE

---

## 🎯 OBJECTIF DOCTRINAL
Externaliser les state files `state_worker_*.json` vers Cloudflare R2 sous le préfixe
`state/` pour permettre :
1. Persistance à travers pod restart (déjà OK via filesystem, R2 = redondance)
2. **Cold-start safe** depuis pod production neuf (filesystem éphémère possible)
3. Audit centralisé multi-pod (preview ↔ production)

**Doctrine** : STRICT ADDITIF · dual-write R2 + filesystem maintenu · zéro mutation
des pipelines legacy · Verrou Phase III intact.

---

## 📦 ARTEFACTS STAGÉS (non-runtime · création seule)
- `/app/backend/integrations/r2_state_persistence_omega.py` (nouveau module helper)
- `/app/memory/EXTERNALISATION_R2_STATE_PATCH_READY.md` (ce document)

---

## ✅ PRÉ-REQUIS DE BASCULE (à VALIDER AVANT exécution)
1. ✅ R2 credentials présents dans `/app/backend/.env` :
   `CF_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `CF_R2_BUCKET`
2. ⚠️ **Workers 3 actifs · ATTENDRE complétion R5 #0 sur tous** (directive Commandant).
   Condition : `state_worker_{0,1,2}.json` ont tous `r5_idx_done >= 1`.
3. 🟡 Test connectivité R2 standalone (1× avant bascule) :
   ```bash
   python3 /app/backend/integrations/r2_state_persistence_omega.py --check
   python3 /app/backend/integrations/r2_state_persistence_omega.py --write-test
   ```
   Doit afficher : `✅ R2 dual-write OPÉRATIONNEL · prêt pour bascule à froid`

---

## 🔧 PATCH À APPLIQUER À FROID (workers stoppés)

### Cible : `/app/backend/tools/zerocost_worker_seed_r5.py`

#### Patch 1 — Import du module R2 (ligne ~30, après les autres imports)
```python
# P22ΩΩ_EXTERNALISATION_STATE_FILES_R2_Ω · dual-write best-effort additif
try:
    from backend.integrations.r2_state_persistence_omega import (
        save_state_to_r2 as _r2_save_state,
        load_state_from_r2 as _r2_load_state,
    )
    _R2_DUAL_WRITE_ENABLED = True
except Exception as _e_r2:
    _r2_save_state = lambda *a, **k: False  # noqa: E731
    _r2_load_state = lambda *a, **k: None  # noqa: E731
    _R2_DUAL_WRITE_ENABLED = False
```

#### Patch 2 — `_load_worker_state()` : fallback R2 si filesystem vide
```python
def _load_worker_state():
    """Retourne (r5_idx_done, species_done_in_current).
    OMEGA-X ∑ · tuple (int, list[str]) granularité species.
    P22ΩΩ_R2_DUAL_READ_Ω · fallback R2 si filesystem absent (cold-start)."""
    # 1. Source primaire : filesystem (rapide, source de vérité runtime)
    try:
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text())
            if data.get("grid_file") != str(GRID_FILE):
                logger.info("[STATE_FILE_Ω] grid changed · reset r5_idx_done=0")
                return 0, []
            return int(data.get("r5_idx_done", 0)), list(data.get("species_done", []))
    except Exception as e:
        logger.warning(f"[STATE_FILE_Ω] read fail: {e} · tentative R2 cold-start")

    # 2. Cold-start : fallback R2 si filesystem absent ou corrompu
    if _R2_DUAL_WRITE_ENABLED:
        r2_data = _r2_load_state(WORKER_INDEX)
        if r2_data is not None:
            if r2_data.get("grid_file") != str(GRID_FILE):
                logger.info("[STATE_FILE_Ω] R2 grid mismatch · reset r5_idx_done=0")
                return 0, []
            logger.info(
                f"[STATE_FILE_Ω] COLD-START RESUME depuis R2 · "
                f"r5_idx_done={r2_data.get('r5_idx_done')} · "
                f"species_done={r2_data.get('species_done')}"
            )
            return int(r2_data.get("r5_idx_done", 0)), list(r2_data.get("species_done", []))

    return 0, []
```

#### Patch 3 — `_save_worker_state()` : dual-write R2 best-effort
```python
def _save_worker_state(r5_idx_done: int, species_done=None) -> None:
    """Sauve r5_idx_done + species_done atomiquement.
    OMEGA-X ∑ · granularité species.
    P22ΩΩ_R2_DUAL_WRITE_Ω · best-effort R2 après commit filesystem."""
    state_dict = {
        "worker_index": WORKER_INDEX,
        "worker_count": WORKER_COUNT,
        "grid_file": str(GRID_FILE),
        "r5_idx_done": r5_idx_done,
        "species_done": list(species_done) if species_done else [],
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # 1. Write filesystem (atomic, source de vérité runtime)
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = STATE_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state_dict))
        tmp.replace(STATE_FILE)
    except Exception as e:
        logger.warning(f"[STATE_FILE_Ω] save fail at idx={r5_idx_done}: {e}")

    # 2. Dual-write R2 best-effort (ne bloque jamais le worker)
    if _R2_DUAL_WRITE_ENABLED:
        try:
            _r2_save_state(WORKER_INDEX, state_dict)
        except Exception as e:
            logger.warning(f"[R2_STATE] dual-write fail at idx={r5_idx_done}: {e}")
```

---

## 🚦 PROCÉDURE DE BASCULE À FROID

```bash
# 0. Pré-check (à exécuter quand workers atteignent r5_idx_done >= 1)
for f in /var/log/bionic-zerocost-seed-r5/state_worker_*.json; do
  cat "$f" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['worker_index'],d['r5_idx_done'])"
done
# DOIT afficher : 0 N · 1 M · 2 P  où N,M,P >= 1

# 1. Test R2 connectivité (zéro impact runtime)
python3 /app/backend/integrations/r2_state_persistence_omega.py --check
python3 /app/backend/integrations/r2_state_persistence_omega.py --write-test
# DOIT afficher : ✅ R2 dual-write OPÉRATIONNEL

# 2. Stop daemon propre (SIGTERM preserve last state JSON)
bash /app/backend/tools/zerocost_seed_r5_daemon.sh stop

# 3. Backup défensif state files actuels
cp -a /var/log/bionic-zerocost-seed-r5 /var/log/bionic-zerocost-seed-r5.pre-r2-backup-$(date +%s)

# 4. Apply patch (manuel · 3 blocs ci-dessus dans zerocost_worker_seed_r5.py)
#    OU script auto à venir : tools/apply_externalisation_r2_state_patch.py

# 5. Push initial filesystem → R2 (sync one-shot)
python3 -c "
import json, sys, glob
sys.path.insert(0, '/app/backend')
from integrations.r2_state_persistence_omega import save_state_to_r2
for f in glob.glob('/var/log/bionic-zerocost-seed-r5/state_worker_*.json'):
    d = json.load(open(f))
    ok = save_state_to_r2(d['worker_index'], d)
    print(f'  push {f} → R2: {\"OK\" if ok else \"FAIL\"}')
"

# 6. Restart watchdog (relancera les workers avec le nouveau code)
sudo supervisorctl restart zerocost-seed-r5-watchdog

# 7. Vérif post-restart (workers reprennent depuis filesystem · R2 dual-write démarre)
sleep 60
ps -ef | grep zerocost_worker_seed_r5 | grep -v grep
tail -30 /var/log/bionic-zerocost-seed-r5/worker_0.log | grep -E "R2_STATE|STATE_FILE_Ω|RESUME"

# 8. Vérif R2 contient bien les states après ~1 min
python3 /app/backend/integrations/r2_state_persistence_omega.py --list
# DOIT afficher : state/state_worker_0.json · state/state_worker_1.json · state/state_worker_2.json

# 9. Test cold-start scenario (READ-ONLY, simulation prod migration)
python3 /app/backend/integrations/r2_state_persistence_omega.py --load 0
# DOIT afficher state JSON du worker 0 chargé depuis R2
```

---

## 🧪 SCÉNARIO COLD-START (validation production-ready)
```bash
# SIMULATION pod production neuf · filesystem vide
# (à exécuter EN STOP COMPLET workers · purge state files local · vérifier que
#  workers reprennent depuis R2)

bash /app/backend/tools/zerocost_seed_r5_daemon.sh stop
rm -rf /var/log/bionic-zerocost-seed-r5/state_worker_*.json
sudo supervisorctl restart zerocost-seed-r5-watchdog
sleep 60

# Workers logs DOIVENT contenir :
#   [STATE_FILE_Ω] COLD-START RESUME depuis R2 · r5_idx_done=X · species_done=[...]
grep "COLD-START RESUME" /var/log/bionic-zerocost-seed-r5/worker_*.log
```

---

## 📈 IMPACT CPU / RÉSEAU ATTENDU
- **Save state** : ajout HTTP PUT R2 (~50-300ms) toutes les ~5-15 min par worker
- **CPU additionnel** : <1% (sérialisation JSON déjà faite, upload async non-bloquant best-effort)
- **R2 writes** : ~3 workers × ~10 saves/h × 24h = ~720 writes/jour = ~$0.0026/jour ($0.08/mois)
- **R2 storage** : 3 fichiers × <1KB = <3KB total = négligeable
- **Pas d'aggravation throttling** (volume négligeable vs base load workers)

---

## 🛡️ ROLLBACK PROCEDURE (en cas de problème post-bascule)
```bash
# 1. Stop daemon
bash /app/backend/tools/zerocost_seed_r5_daemon.sh stop

# 2. Restore worker file pre-patch (git)
cd /app && git checkout backend/tools/zerocost_worker_seed_r5.py

# 3. Restore state filesystem
rm -rf /var/log/bionic-zerocost-seed-r5/state_worker_*.json
cp -a /var/log/bionic-zerocost-seed-r5.pre-r2-backup-*/state_worker_*.json /var/log/bionic-zerocost-seed-r5/

# 4. Restart watchdog
sudo supervisorctl restart zerocost-seed-r5-watchdog
```

---

## 🔒 VERROU PHASE III
- ✅ Aucun engine modifié
- ✅ Aucun pipeline supprimé/refactoré
- ✅ Le filesystem reste source de vérité runtime (R2 = redondance + cold-start)
- ✅ Le module R2 est isolé dans `/app/backend/integrations/` (additif)
- ✅ Le patch worker est `try/except` gracieux → si R2 down, comportement legacy intact
- ✅ Compatible Phase 2 limitrophes + Phase 3 future sans modification

---

## 📌 STATUS
- **Stagé** : ✅ 2026-06-06 (modules créés, non importés par runtime actif)
- **Pré-bascule check** : ⏸️ EN ATTENTE complétion R5 #0 sur 3 workers (MODE SILENCE)
- **Test R2 connectivité** : ⏸️ À déclencher manuellement avant bascule
- **Apply patch** : ⏸️ EN ATTENTE ordre Commandant `EXTERNALISATION_GO_LIVE`
- **Validation cold-start** : ⏸️ Post-bascule

---

**FIN PATCH READY — VERROU PHASE III INTACT**
