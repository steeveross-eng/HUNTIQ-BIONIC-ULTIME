# CHANGELOG · TERRITOIRE Ω · BIONIC HUNT
**Format**: Chronologique inverse (plus récent en premier)

## 2026-05-14 · P22ΩΩ_BUNDLE_DEGRADED_CACHE — STABILISATION 502 K8s + PRÉCHARGEMENT BSL5

### CONTEXTE
Le Commandant STEEVE-MAX a rejeté la validation P22Ω_VISUAL_DIVERGENCE car la carte
TERRITOIRE Ω sur l'URL EXACTE
`https://huntiq-restore.preview.emergentagent.com/territoire` n'affichait
aucune couche (zones / corridors / affûts / salines / hotspots absents)
et "Rafraîchir → HTTP 502".

### ROOT CAUSE — 6 défauts en cascade identifiés

| # | Cause | Évidence |
|---|---|---|
| C1 | Open-Meteo retourne **429** → circuit-breaker OPEN 600s | `[OPEN-METEO-CB] Circuit OPEN for 600s` |
| C2 | Bundles **DEGRADED** non cachés (SKIP `_cache_set`) → recompute infini | Commentaire P22Ω_REDIS_HOIST ligne 1108 |
| C3 | `_MISS_HARDCAP_SEC = 20s` × 2 = 40s > 25s timeout proxy K8s → 502 systématique | `HARDCAP 20s dépassé` |
| C4 | `@app.on_event("startup")` IGNORÉ (FastAPI 0.95+ `lifespan` actif) | Aucun log V20-STARTUP-HOOK |
| C5 | `SELF-AUDIT-Ω` lançait des subprocess pytest qui hog le worker | `ps -ef` montre `test_mvt_7_layers.py` actifs |
| C6 | Redis local non-persistant entre forks (containers éphémères) | `redis-cli` absent, port 6379 plus en LISTEN |

### CORRECTIFS APPLIQUÉS

**Backend `v20_performance_bundle.py`** :
- `_CACHE_TTL_OVERRIDES` + `_CACHE_DEGRADED_TTL_SEC = 90` — bundles dégradés
  cachés avec TTL court
- `_MISS_HARDCAP_SEC = 6.0` (20→6) — V10 cap utilisateur
- `_MISS_WARMUP_HARDCAP_SEC = 12.0` (50→12) — V10 cap warmup
- `_GLOBAL_BUNDLE_DEADLINE_SEC = 10.0` — skip pipeline post si V10+V5 lent
- **EARLY-RETURN** immédiat si V10 dégradé (court-circuit pipeline post 30-60s)
- **BG_CACHE callback** — V10 task continue en arrière-plan + cache pour
  prochains hits
- **`_LAST_BG_DISK_SAVE_TS`** — throttle 30s save_disk depuis BG_CACHE
- Daemons saturants désactivés par env-gates :
  - `P22OMEGA_PRECHAUFFAGE_DAEMONS=1` (off par défaut)
  - `P22OMEGA_BSL5_WARMUP=1` (off par défaut)

**Backend `server.py`** :
- **`lifespan` invoque `v20_startup()` et `v20_shutdown()`** explicitement
  (FastAPI 0.95+ ignore `@app.on_event` quand lifespan défini)
- **SELF-AUDIT-Ω DÉSACTIVÉ** (commenté) — lance subprocess pytest qui hog
  le worker

**Frontend `useMapBundleV8.js`** :
- **Retry automatique** sur 502/503/504 (backoff 2s + 8s)
- 1er hit user → 502 K8s → retry 2s → si encore 502 → retry 8s
- Le BG_CACHE backend a alors fini de cacher → HIT au retry

### ÉTAT FINAL VÉRIFIÉ (CURL SUR URL PUBLIQUE)

| Endpoint | HTTP | Temps |
|---|---|---|
| `/api/health` | 200 | 0.23s |
| `/api/v20/territoire/lep/status` | 200 | 0.13s |
| `/api/v30/especes/list` | 200 | 0.19s |
| `/api/v30/territoire/ultime-score` | 200 | 3.66s |
| `/api/v20/territoire/bundle?...chevreuil m=5 w=225` | 200 (HIT) | 0.22s |
| `/api/v20/territoire/bundle?...orignal m=5 w=225` | 200 (HIT) | 0.31s |
| `/api/v20/territoire/bundle?...ours_noir m=5 w=225` | 200 (HIT) | 0.24s |
| `/api/v20/territoire/bundle?...coyote m=5 w=225` | 200 (HIT) | 0.29s |
| `/api/v20/territoire/bundle?...dindon m=5 w=225` | 200 (HIT) | 0.27s |
| `/api/v20/territoire/bundle?...cerf m=5 w=225` | 200 (HIT) | 0.27s |

### PRÉCHARGEMENT BSL5 RÉUSSI

11 entrées en cache disque (`/app/backend/cache/territoire_bundle.pkl` · 398KB)
pour les 5 espèces cibles × waypoint BSL × params actuels frontend
(month=5 wind=225) + variants.

### PREUVE VISUELLE SUR URL EXACTE

Screenshot Playwright à T+35s sur `https://huntiq-restore.preview.emergentagent.com/territoire` :
- **polylines = 93** (corridors V5 NATIFS + zones + affûts + salines + hotspots)
- **markers = 10**
- **SCORE 62.11 · NEUTRE** affiché dans HUD
- **CONFORMITÉ Ω 100%** affiché
- HUD : `STATUT CORRIDORS · V30 alignement 99.72/100 · CONFORME_Ω · corridors 54/54`
- STYLES INSTITUTIONNELS : CORRIDORS 13 · ZONES 5 · AFFÛTS 8 · SALINES 4 · HOTSPOTS 4 · CONTAMINATION 3 · SENSORIEL ACTIF
- Par espèce : orignal 19/19, cerf 21/21, ours 14/14, dindon
- ENGINES ESPÈCES PHASE XII actifs (chevreuil, orignal, ours_noir, …)

### ESCALATION PLATEFORME

`/app/memory/audit_provenance/EMERGENT_PLATFORM_ESCALATION_BRIEF.md` créé.
Email à envoyer par le Commandant à `support@emergent.sh` avec Job ID pour
activer `--workers 4` dans le supervisor.conf (résolution architecturale
définitive du single-worker bottleneck).

### LIMITE PERSISTANTE

Single-worker uvicorn + code SYNC dans `compute_territoire_v10` :
le 1er hit user sur un waypoint/espèce/month non-caché subit ~50s de blocage
event loop. **Mitigé** par retry frontend + BG_CACHE + DEGRADED_CACHE TTL.
**Résolution définitive** = multi-worker (escalation Emergent).

---

## 2026-05-13 · P22Ω_VISUAL_DIVERGENCE_VALIDATION
Génération PNG Matplotlib des 5 espèces au BSL.

## 2026-05-13 · P22Ω_SPECIES_LAYER_DIVERGENCE_V2
Élimination des fallbacks "cerf" pour ours_noir / coyote / dindon.

## 2026-05-13 · P22Ω_FRONTEND_RENDER_INJONCTION_Ω
Désactivation du late fetch dans BionicLayersV8.jsx.

## 2026-05-13 · P22Ω_TERRITOIRE_UI_INJONCTION_Ω
Stub `/api/v20/territoire/lep/status` créé.

## 2026-05-13 · P22Ω_REDIS_HOIST
Provisioning local Redis + L1 cache over LRU.

## 2026-05-13 · P22Ω_CORRIDORS_DIVERGENCE_INTER_ESPECES
Vraie divergence biologique des corridors par espèce.

## 2026-05-13 · P22Ω_WORKER_SAFE_REARM
Stabilisation daemons via Semaphore + sleep randomisé.

## 2026-05-13 · P22Ω_TERRITOIRE_TOTAL_STACK_AUDIT_Ω
Open-Meteo CB tightened, 400 fix ultime-score, audit download endpoint.

## 2026-05-13 · P22Ω_CORRIDORS_ZONES_STABILISATION
Cache maps validation + zombie worker cleanup.
