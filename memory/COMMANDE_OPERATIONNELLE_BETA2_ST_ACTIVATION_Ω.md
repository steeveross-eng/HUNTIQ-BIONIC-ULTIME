# COMMANDE OPÉRATIONNELLE · ACTIVATION β2-ΣΤ · Ω

**Doctrine** : `P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_ACTIVATION_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟡 **COMMANDE PRÊTE · INERTE · ATTEND VALIDATION EXPLICITE COMMANDANT**

> **Rappel doctrinal** : aucune des étapes décrites ci-dessous n'est exécutée
> tant que le COMMANDANT n'a pas émis la directive explicite d'activation.
> Tous les artefacts cités sont présents en mode INERTE.

---

## 1. RÉSUMÉ EXÉCUTIF

| Indicateur | Valeur projetée |
|---|---|
| Périmètre cible | 3 RF prioritaires (Laurentides + Mauricie + Outaouais) — 1 775 cellules R6 |
| Cellules R5 SEED à compute | **~250 cellules R5** (estimation 1/7 de 1 775) |
| Tuiles SEED compute V20 | **~18 000 tuiles** (×6 sp × ×4 mois × ×3 h) |
| Tuiles R6 fan-out zéro-cost | **127 800 tuiles R6** (×7 enfants par R5) |
| Gain compute vs direct R6 | **×7** |
| ETA 8 workers locaux nice 19 | **~1.5 jour** au lieu de ~11j |
| ETA 16 workers locaux | **~0.7 jour** |
| ETA 256 workers k8s | **~1 heure** |
| Verrou Phase III | 🔒 MAINTENU (additif strict, V10/V20 inchangés) |
| QUOTA600 OWM | 🟢 Aucun risque (<1 fetch/jour stationnaire) |

---

## 2. ARTEFACTS PRÉ-INSTALLÉS · MODE INERTE

| Fichier | Rôle | Statut |
|---|---|---|
| `/app/backend/tools/zerocost_seed_r5_grid_generator.py` | Génère grille H3 R5 + mapping enfants R6 | 🟡 PRÊT, NON-EXÉCUTÉ |
| `/app/backend/tools/bundle_adapter_r5_to_r6_omega.py` | Adaptateur fan-out R5 → 7 R6 (offset + jitter déterministe) | 🟡 PRÊT, NON-EXÉCUTÉ |
| `/app/backend/tools/zerocost_worker_seed_r5.py` | Worker SEED+FAN-OUT (compute R5 + 7 uploads R6) | 🟡 PRÊT, NON-EXÉCUTÉ |
| `/app/memory/PLAN_BUNDLE_SEED_H3R5_BETA2_ΣΤ_Ω.md` | Plan stratégique β2-ΣΤ (analyse, gains, risques) | 🟢 RÉFÉRENCE |

**Vérification au pod actuel** : aucun de ces fichiers n'est invoqué par le `server.py`,
le `useZerocostBundle.js`, ou un cron/daemon actuellement actif. Ils sont strictement inertes.

---

## 3. SÉQUENCE D'ACTIVATION OPÉRATIONNELLE (à exécuter sur ordre Commandant)

### ÉTAPE 1 — Stop du daemon 3 RF en cours (P0)

```bash
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh stop
```

**Validation attendue** :
- `Workers restants : 0`
- 0 process `zerocost_worker_precompute` dans `ps -ef`

**Justification** : libère les ressources CPU/RAM pour le worker β2-ΣΤ qui sera plus intensif
par cellule (compute V20 + 7 uploads R2 par tuile SEED).

---

### ÉTAPE 2 — Génération de la grille H3 R5 SEED (P0)

```bash
cd /app/backend && python3 tools/zerocost_seed_r5_grid_generator.py \
  --input /app/backend/cache/zerocost_v1/canada_h3_grid_r6_3rf_focused.json \
  --output /app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed.json
```

**Validation attendue** :
- Fichier `canada_h3_grid_r5_seed.json` créé (~30-50 KB)
- Ratio compression affiché ≈ ×7 (entre 6.5 et 7.0)
- Nombre R5 affiché ~250 cellules
- Nombre R6 enfants affiché = 1 775 (idempotent avec la grille 3 RF source)

**Critère de stop si échec** : si n_r5 < 200 ou ratio compression < 5, NE PAS continuer.

---

### ÉTAPE 3 — Test unitaire de l'adaptateur (P0)

```bash
cd /app/backend && python3 tools/bundle_adapter_r5_to_r6_omega.py
```

**Validation attendue** :
- Affichage de 7 enfants R6 avec coords distinctes mais cohérentes (Δlat ≤ 0.02°, Δlng ≤ 0.02°)
- `wind_deg` jittered chacun différent (±2° autour de 225°)
- `score_global` jittered (±1.5% autour de 75)
- `_fan_out_jitter` affiché entre -0.5 et 0.5

**Critère de stop si échec** : si jitter constant ou coords identiques → bug adaptateur, ne pas activer worker.

---

### ÉTAPE 4 — Smoke-test worker β2-ΣΤ (P0, MAX_R5_CELLS=2)

```bash
cd /app/backend && \
GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed.json \
WORKER_INDEX=0 WORKER_COUNT=125 MAX_R5_CELLS=2 \
timeout 1800 python3 tools/zerocost_worker_seed_r5.py 2>&1 | tee /tmp/seed_r5_smoketest.log
```

**Validation attendue** :
- 2 cellules R5 traitées
- ~144 tuiles SEED computées (2 × 6 × 4 × 3 = 144)
- ~1 008 tuiles R6 fan-out uploadées (144 × 7)
- 0 erreur HTTP 429 (WeatherCache OK)
- 0 SEED_FAIL ou FAN-OUT_FAIL > 5%
- Durée ≤ 30 min

**Critère de stop si échec** : si FAN-OUT_FAIL > 5%, investigation requise sur l'adaptateur.

---

### ÉTAPE 5 — Validation R2 des tuiles fan-out (P0)

```bash
python3 -c "
import os, boto3, json, datetime
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
s = boto3.client('s3',
    endpoint_url=os.environ['R2_S3_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
    region_name='auto')
cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=45)
recent = []
for page in s.get_paginator('list_objects_v2').paginate(Bucket=os.environ['CF_R2_BUCKET'], Prefix='v1/'):
    for o in page.get('Contents', []):
        if o['LastModified'] > cutoff:
            recent.append((o['Key'], o['Size']))
print(f'Tuiles uploadées <45min : {len(recent)}')
print('Échantillon coords :')
for k, sz in recent[:8]:
    parts = k.split('/')
    print(f'  {parts[1]:18s} {parts[2]:20s} {parts[3]}  ({sz}B)')

# Test que des coords adjacentes (R6 enfants même R5) existent
cells = sorted(set(p.split('/')[2] for p, _ in recent))
print(f'Cellules R6 distinctes : {len(cells)}')"
```

**Validation attendue** :
- ≥ 1 000 tuiles uploadées dans la dernière 45 min
- ≥ 14 cellules R6 distinctes (= 2 R5 × 7 enfants)
- Coords cohérentes géographiquement (différences typiques 0.01°-0.05°)

**Critère de stop si échec** : si <90% des uploads attendus présents → R2 backpressure ou bug.

---

### ÉTAPE 6 — Validation visuelle preview UI (P1)

```bash
# Frontend cible
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d= -f2)
# Test sur l'une des nouvelles cellules R6
# (utiliser une coord depuis l'étape 5)
curl -s -o /tmp/test_bundle.json -w "HTTP %{http_code} · %{time_total}s\n" \
  "https://cdn-zerocost.bionichunt.com/v1/chevreuil/<COORDS_DEPUIS_ETAPE_5>/m10_h14.json.gz"
gunzip -c /tmp/test_bundle.json | python3 -m json.tool | head -20
```

**Validation attendue** :
- HTTP 200 depuis le CDN Cloudflare
- Bundle décodé avec `corridors`, `zones`, `affuts`, `salines`, `hotspots` présents
- Champ `_seed_r5_parent` présent (signature β2-ΣΤ)
- Champ `_fan_out_jitter` présent (variations déterministes appliquées)

---

### ÉTAPE 7 — Cohérence inter-R6 (anti "tuile copiée-collée") (P1)

```bash
# Comparer 3 cellules R6 sœurs (même parent R5) pour vérifier les variations
for cell_coords in "<COORD_R6_1>" "<COORD_R6_2>" "<COORD_R6_3>"; do
    curl -s "https://cdn-zerocost.bionichunt.com/v1/chevreuil/${cell_coords}/m10_h14.json.gz" \
      | gunzip -c | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'cell ${cell_coords} :')
print(f'  wind_deg     : {d.get(\"wind_deg\")}')
print(f'  score_global : {d.get(\"score_global\")}')
print(f'  corridors[0] pt0 : {d.get(\"corridors\", [{}])[0].get(\"path\", [None])[0] if d.get(\"corridors\") else \"N/A\"}')
print(f'  _fan_out_jitter : {d.get(\"_fan_out_jitter\")}')
print()
"
done
```

**Validation attendue** :
- `wind_deg` différent entre les 3 sœurs (±2° doctrinal)
- `score_global` différent (±1.5% doctrinal)
- 1er point corridor[0] décalé (preuve d'offset géométrique)

---

### ÉTAPE 8 — Bascule production daemon β2-ΣΤ (P0, après validation 1-7 OK)

```bash
# Création d'un launcher dédié β2-ΣΤ (script à dériver de zerocost_prewarm_p1_daemon.sh)
# Pour démarrer 8 workers β2-ΣΤ nice -n 19 sur la grille R5 seed :

LOG_DIR=/var/log/bionic-zerocost-seed-r5
mkdir -p $LOG_DIR
rm -f $LOG_DIR/worker_*.log

for i in 0 1 2 3 4 5 6 7; do
    setsid nohup nice -n 19 env \
        GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed.json \
        WORKER_INDEX=$i WORKER_COUNT=8 MAX_R5_CELLS=0 \
        PYTHONUNBUFFERED=1 \
        python3 /app/backend/tools/zerocost_worker_seed_r5.py \
        > $LOG_DIR/worker_${i}.log 2>&1 < /dev/null &
    disown
done

echo "8 workers β2-ΣΤ lancés en daemon · nice 19 · PPID=1 attendu"
```

**Validation attendue** :
- 8 process actifs `ps -ef | grep zerocost_worker_seed_r5`
- PPID=1 sur tous (indépendants de la session shell)
- Load avg <1.5 après 5 min (nice 19 préserve la réactivité backend)
- Pas de saturation OWM/R2

**Critère de stop si échec** : si load avg > 3.0 ou backend uvicorn timeout → fallback à 4 workers.

---

### ÉTAPE 9 — Régénération manifeste R2 (à T+1h puis périodique) (P1)

```bash
cd /app/backend && python3 tools/zerocost_manifest_update.py
```

**Validation attendue** :
- HTTP 200 sur `https://cdn-zerocost.bionichunt.com/manifest.json`
- `n_tiles` ≥ valeur précédente + ~1000 par heure pendant le run

---

### ÉTAPE 10 — Rapport de complétion β2-ΣΤ (P1, après ETA terminée)

```bash
# Génération automatique du rapport final
python3 -c "
import os, boto3, json, datetime
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
# Aggregate stats from worker logs + R2 listing
# Produce /app/memory/RAPPORT_BETA2_ST_COMPLETION_Ω.md
print('Rapport β2-ΣΤ à produire post-complétion')
"
```

**Contenu attendu du rapport final** :
- Couverture effective R6 (compte tuiles uniques par RF prioritaire)
- Latence moyenne SEED + fan-out
- Volume R2 final + coût stockage
- Validation cohérence inter-R6 sur échantillon 100 cellules
- Comparatif scores macro R6 fan-out vs un compute direct R6 témoin (50 cellules)

---

## 4. POINTS DE ROLLBACK (DOCTRINE NEVER BLANK Ω)

Si une étape échoue ou produit des résultats anormaux :

```bash
# 1. Stop immédiat des workers β2-ΣΤ
ps -ef | grep zerocost_worker_seed_r5 | grep -v grep | awk '{print $2}' | xargs -r kill

# 2. (Optionnel) Purger les tuiles β2-ΣΤ uploadées par lifecycle R2
# Les tuiles fan-out portent le marqueur "_seed_r5_parent" ; on peut les identifier en R2

# 3. Reprendre le daemon 16w/8w direct R6 (mode β2-Β+β2-Ε classique)
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh start
```

Le frontend reste sur LKG IndexedDB + fallback API V20 pendant le rollback : **0 écran blanc**.

---

## 5. CRITÈRES D'AUTORISATION COMMANDANT

Avant d'activer la séquence, je requiers la confirmation explicite des points suivants :

- ☐ **Validation du plan** `PLAN_BUNDLE_SEED_H3R5_BETA2_ΣΤ_Ω.md` (déjà APPROUVÉ par directive précédente)
- ☐ **Validation de cette commande opérationnelle** dans son intégralité
- ☐ **Choix du périmètre initial** :
  - α) 3 RF prioritaires (~250 R5 / 1 775 R6) — ETA ~1.5j local 8w  ⬅ RECOMMANDÉ
  - β) P1 complet 7 077 R6 (~1 010 R5) — ETA ~6j local 8w
  - γ) Test sur 1 RF seule (Laurentides 1 234 R6 / ~176 R5) — ETA ~1j local 8w
- ☐ **Cible workers** :
  - 8 workers nice 19 local (préserve backend) ⬅ RECOMMANDÉ
  - 16 workers nice 19 local (compromis backend réactivité)
  - k8s 256w (nécessite cluster cible non-fourni à ce jour)
- ☐ **Émission de la commande d'activation** (texte libre, e.g. "ACTIVATE β2-ΣΤ option α")

---

## 6. RISQUES IDENTIFIÉS · MITIGATIONS PRÉ-DÉPLOYÉES

| Risque | Probabilité | Impact | Mitigation déjà en place |
|---|---|---|---|
| Discontinuité visuelle R6 voisines | Moyenne | Moyen | Offset géométrique + jitter ±2° wind / ±1.5% score (dans `bundle_adapter_r5_to_r6_omega.py`) |
| HALT R5 incorrect propagé R6 | Faible | Moyen | Adapter conserve `bio_presence_mask_halt` du seed (V20 logic préservée) |
| Saturation backend uvicorn pendant SEED compute | Moyenne | Élevé | nice -n 19 + max 8 workers concurrent |
| OWM 429 lors du SEED | Très Faible | Faible | `install_open_meteo_interceptor` hérité (WeatherCache H3 R3 actif) |
| Coût stockage R2 doublé (seed + R6) | Faible | Faible | Worker n'upload PAS le seed bundle, uniquement les R6 fan-out (économie ÷8) |
| Régression Verrou Phase III | Nul | Critique | Aucune modification V10/V20 — uniquement nouveaux fichiers additifs |

---

## 7. CONFORMITÉ VERROU PHASE III

| Composant | Statut |
|---|---|
| `engines/v8_institutional/v20_performance_bundle.py` | ❌ INTACT (appelé inchangé via `v20_territoire_bundle()`) |
| `engines/v8_institutional/territoire_v10_supra.py` | ❌ INTACT |
| Tous engines V10/LiDAR/IRDA/terrain_hr_omega/IA | ❌ INTACT |
| Frontend (`useZerocostBundle.js`, `lkgCacheOmega.js`, `BionicLayersV8.jsx`) | ❌ INTACT |
| `tools/zerocost_worker_precompute.py` (worker direct R6 existant) | ❌ INTACT |
| `tools/zerocost_prewarm_p1_daemon.sh` (daemon direct R6 existant) | ❌ INTACT |
| 🆕 `tools/zerocost_seed_r5_grid_generator.py` | NOUVEAU ADDITIF |
| 🆕 `tools/bundle_adapter_r5_to_r6_omega.py` | NOUVEAU ADDITIF |
| 🆕 `tools/zerocost_worker_seed_r5.py` | NOUVEAU ADDITIF |

→ **Verrou Phase III strictement respecté** · activation 100% additive · reversible par stop+lifecycle R2.

---

## 8. INERTIE GARANTIE TANT QUE NON-COMMANDÉ

À la date de ce document :
- ✅ Les 3 nouveaux fichiers sont créés mais **ne sont importés nulle part** dans `server.py`
- ✅ Aucun cron / daemon / worker actif ne les invoque
- ✅ Le daemon 8w direct R6 actuel (3 RF focalisé) continue son travail normalement
- ✅ Le middleware anti-502 / frontend / V20 / CDN restent dans leur configuration arbitrage actuel
- ✅ Aucune modification de `.env`, `package.json`, `requirements.txt`

---

## 9. DÉCISION COMMANDANT POUR ACTIVATION

Pour activer la séquence, le COMMANDANT doit émettre une directive contenant :

```
ACTIVATE β2-ΣΤ option {α|β|γ} workers {8|16|k8s256}
```

Exemples :
- `ACTIVATE β2-ΣΤ option α workers 8` → 3 RF, 8 workers nice 19, ETA ~1.5j (recommandé)
- `ACTIVATE β2-ΣΤ option γ workers 8` → Test 1 RF Laurentides, ETA ~1j (très conservateur)
- `ACTIVATE β2-ΣΤ option β workers 16` → P1 complet, ETA ~3j (agressif)

Tant que cette directive n'est pas reçue, **TOUS les artefacts ci-dessus restent INERTES**.

---

**FIN COMMANDE OPÉRATIONNELLE β2-ΣΤ · STATUT : PRÊT_NON_EXÉCUTÉ · EN ATTENTE DIRECTIVE COMMANDANT**
