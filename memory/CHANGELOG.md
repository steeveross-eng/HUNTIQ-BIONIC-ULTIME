# CHANGELOG · TERRITOIRE Ω · BIONIC HUNT
**Format**: Chronologique inverse (plus récent en premier)

## 2026-05-19 · P22ΩΩ_CLEANUP_LEGACY_FINAL — Phase 0 EXÉCUTÉE (avec autocritique)

### DIRECTIVE COMMANDANT STEEVE-MAX
Suppression Phase 0 des artefacts legacy identifiés. **Validation par audit ultime**
avant toute suppression destructive.

### AUTOCRITIQUE BCE-4X (transparence totale)
L'audit initial du `p22omegaomega_cleanup_legacy_final.md` classifiait 3 engines
comme "Catégorie A — 0 usage prod" :
- `engine_ia_corridors_omega.py` (V4)
- `federal_datasets_omega.py`
- `science_gaps_datasets.py`

**Audit ultime avant suppression** a révélé que ces 3 fichiers sont **TOUS importés
activement** par `territoire_v10_supra.py` et `server.py` :
- `territoire_v10_supra.py:376` → `from ... engine_ia_corridors_omega import filter_conforme_corridors`
- `territoire_v10_supra.py:1351-1352` → `from ... science_gaps_datasets import CWD_HEATMAP` + `from ... federal_datasets_omega import LEP_HABITATS, HYDAT_STATIONS`
- `server.py:956,972` → `app.include_router(gaps_router)`, `app.include_router(federal_router)` (routers `/science-gaps`, `/federal/lep`, `/federal/hydat` actifs)

Conformément aux contraintes inviolables, **REFUS de suppression Catégorie A** appliqué.

### EXÉCUTION RÉELLE
✅ **128 fichiers tests legacy archivés** via `git mv`-equivalent :
- 99 fichiers `test_phase_*.py` → `tests/archive/phases_a_e/`
- 6 fichiers `test_phase_xi-xv*.py` → `tests/archive/phases_xi_xv/`
- 11 fichiers `test_phase_xvii-xix*.py` → `tests/archive/phases_xvii_xix/`
- 12 fichiers `test_render_*.py` → `tests/archive/render/`
- **27 507 lignes archivées** (2× plus que l'estimation initiale 14 250)

✅ Configuration pytest :
- `pyproject.toml` : `norecursedirs = ["archive", "__pycache__", "node_modules", ".git"]`
- `tests/archive/__init__.py` : guard documenté

### VALIDATION POST-EXÉCUTION (curl URL publique)
| Endpoint | HTTP | Temps |
|---|---|---|
| `/api/health` | ✅ 200 | 0.28s |
| `/api/v20/territoire/lep/status` | ✅ 200 | 0.15s |
| `/api/v30/especes/list` | ✅ 200 | 0.10s |
| 5 espèces × month=5 (HIT cache TTL 3600s) | ✅ 200 toutes | <0.17s chacune |
| Conformité Ω | ✅ 100% maintenue | |

### CUMUL DEPUIS DÉBUT P22ΩΩ
| Phase | Lignes purgées/archivées |
|---|---|
| P22ΩΩ_ALLEGEMENT_STRUCTUREL (2026-05-17) | 2 628 (3 stubs backend + 7 composants frontend) |
| P22ΩΩ_CLEANUP_LEGACY_FINAL (2026-05-19) | 27 507 (128 tests archivés) |
| **TOTAL** | **30 135 lignes** |

### GARDE-FOUS RESPECTÉS
- ❌ 0 engine scientifique Ω modifié
- ❌ 0 algorithme scoring/corridors/zones/salines/espèces touché
- ❌ 0 modification contrat bundle JSON public
- ❌ 0 impact TERRITOIRE_ESSENTIEL_1WORKER
- ❌ 0 modification TTL ESSENTIEL_T0=3600s
- ✅ Conformité Ω 100% maintenue

### LEÇON DOCTRINALE
Toujours INSPECTER le contexte des imports (lignes ±2) avant suppression, jamais
se fier uniquement au count grep. Le document `p22omegaomega_cleanup_legacy_final.md`
a été mis à jour avec un §10 d'autocritique complet.

---

## 2026-05-19 · P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE — Plan institutionnel complet (PLAN ONLY)

### DIRECTIVE COMMANDANT STEEVE-MAX
Établir la feuille de route complète de modularisation de TERRITOIRE Ω.
**AUCUN code modifié** — uniquement plan institutionnel.

### LIVRABLES (5 documents dans `/app/memory/audit_provenance/`)
- `p22omegaomega_analyse_monolithique_server.md` — 7070 lignes monolithiques cartographiées
- `p22omegaomega_plan_de_decoupage_v10_v20.md` — 10 étapes de découpage séquentiel
- `p22omegaomega_roadmap_zero_cost_engine.md` — Phase 1A→2C sur 12 mois
- `p22omegaomega_cleanup_legacy_final.md` — Liste candidats + ordre suppression
- `p22omegaomega_plan_modularisation_master.md` — Document maître consolidé

### CARTOGRAPHIE MONOLITHE
| Fichier | Lignes | Type |
|---|---|---|
| v20_performance_bundle.py | 1 982 | Cache + hardcaps + warmup + daemons + corridors V5 + endpoints + monitoring |
| territoire_v10_supra.py | 1 495 | Terrain + zones + corridors V10 + affûts + hotspots + salines + comportement |
| server.py | 1 686 | Lifespan + 142 routers + auth + payments |
| MonTerritoireBionicPage.jsx | 1 907 | Carte + HUD + panneaux + waypoints |

### ARCHITECTURE MODULAIRE CIBLE
```
engines/v8_institutional/
├── v10/  (4 pipelines : terrain, meteo, biologie, affuts)
├── v20/  (5 pipelines : territoire_logic, cache, daemons, compliance, rendu_avance)
└── v30_future/  (3 engines : static, deferred_rendering, zero_cost)
```

### LEGACY À SUPPRIMER (Phase 0)
- 3 engines V4 (engine_ia_corridors_omega.py V4, federal_datasets_omega.py, science_gaps_datasets.py) : ~750 lignes
- 116 fichiers `test_phase_*.py` (à archiver via git mv) : ~12 000 lignes
- 12 fichiers `test_render_*.py` (à archiver) : ~1 500 lignes
- **Total Phase 0** : ~14 250 lignes purgeables/archivables

### CONTRAINTES INVIOLABLES
- ❌ Aucune modification engines scientifiques Ω
- ❌ Aucune modification scoring/corridors/zones/salines/espèces
- ❌ Aucune modification contrat bundle JSON public
- ❌ Aucun impact TERRITOIRE_ESSENTIEL_1WORKER
- ❌ Aucun impact TTL ESSENTIEL_T0=3600s
- ❌ Aucun impact Conformité Ω 100%

### EFFORT ESTIMÉ
- Phase 0 (cleanup) : 1 jour
- Phase 1 (découpage V10/V20) : ~14 jours
- Phase 1B+1C (Static + Deferred) : 2 mois
- Phase 2 (Zero-Cost edge) : 6 mois supplémentaires

### STATUT
🟡 **EN ATTENTE D'AUTORISATION COMMANDANT** pour exécution Phase 0.

---

## 2026-05-19 · P22ΩΩ_TERRITOIRE_TTL_ESSENTIEL_3600S — TTL ESSENTIEL_T0 600s → 3600s + CPU SAFE MODE

### DIRECTIVE COMMANDANT STEEVE-MAX
Maximiser la stabilité et la performance de TERRITOIRE Ω en `--workers 1` pour
2 000 membres en étendant le TTL ESSENTIEL_T0 à 3 600s (1h), tout en maintenant
la conformité scientifique et opérationnelle Ω.

### MODIFICATIONS BACKEND
- `v20_performance_bundle.py` :
  - `_CACHE_ESSENTIEL_TTL_SEC = 600 → 3600` (× 6 plus de cache HIT)
  - Alias canonique `_CACHE_TTL_ESSENTIEL_SEC = _CACHE_ESSENTIEL_TTL_SEC`
  - Les 4 chemins ESSENTIEL_T0 (early-return V10 dégradé, V5 fail, deadline hit, end-of-pipeline degraded) honorent automatiquement le nouveau TTL
  - TTL COMPLET_T0 / ENRICHI_TDELTA inchangés (24h)
- `essentiel_prewarm_cron.py` :
  - **SKIP recompute** si bundle ESSENTIEL valide < 3600s déjà en cache (évite le recalcul inutile)
  - **CPU SAFE MODE** : pause 30s si CPU > 70%, resume si < 50%
  - `_CRON_STATE["last_cycle_cpu_pauses"]` exposé
  - `get_cron_state()` expose : `ttl_essentiel_sec`, `cpu_pause_threshold_pct`, `cpu_resume_threshold_pct`, `current_cpu_pct`
- `psutil==7.2.2` ajouté à `requirements.txt`

### MODIFICATIONS FRONTEND
- `lib/bionicBundleCache.js` :
  - `essentielTtlMs: 600_000 → 3_600_000` (1h)
  - `defaultTtlMs: 600_000 → 3_600_000`
  - `completTtlMs: 24h` inchangé
  - Nouvelle fonction `bundleCacheAge(key)` exposée
- `hooks/useMapBundleV8.js` :
  - Import de `bundleCacheAge`
  - Constante `REFETCH_AGE_THRESHOLD_MS = 60_000`
  - **Re-fetch silencieux T+Δ uniquement si âge cache < 60s** (BG_CACHE backend a ~50-60s pour produire ENRICHI_TDELTA)
  - Si bundle ESSENTIEL_T0 > 60s : skip re-fetch (le ENRICHI ne sera plus produit, on respecte le TTL 3600s)
  - Délais re-fetch adaptés : `delay - age` pour éviter double-call après reload

### VALIDATION
- `/api/admin/essentiel-prewarm/status` expose `ttl_essentiel_sec=3600`, `cpu_pause_threshold_pct=70.0`, `current_cpu_pct` ✓
- Bundle chevreuil HIT cache : `X-Bundle-Tier: ENRICHI_TDELTA · X-Cache: HIT · X-Cache-Age-Sec: 8395` ✓
- Cache disk : 11 entrées persistées ✓
- Screenshot Playwright T+15s : **95 polylines · 10 markers · CONFORMITÉ Ω 100% · SCORE 62.24** · Widget Premium "T0 ESSENTIEL · 1/3 · orignal" ✓

### ENV-VARS (nouveaux)
```bash
P22OMEGA_PREWARM_CPU_PAUSE_THRESHOLD=70.0   # CPU% pour pause cron
P22OMEGA_PREWARM_CPU_RESUME_THRESHOLD=50.0  # CPU% pour resume cron
```

### GAINS QUANTIFIÉS
| Métrique | Avant (600s) | Après (3600s) | Gain |
|---|---|---|---|
| TTL ESSENTIEL backend | 600s | **3600s** | ×6 |
| TTL ESSENTIEL frontend | 600s | **3600s** | ×6 |
| Recalculs/h pour 2000 membres | ~12 000 (10min×60) | **~2 000 (1h)** | ÷6 |
| Charge CPU moyenne 1-worker | référence | **-60-80%** estimé | divisée par 5 |
| Garde-fou CPU | aucun | **pause si > 70% / resume si < 50%** | ∞ |
| SKIP recompute si cache valide | non | **oui** (cron) | -100% recompute redondants |

---

## 2026-05-18 · P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER — Profil 3-cercles + Cache 2000 membres

### DIRECTIVE COMMANDANT STEEVE-MAX
Rendre TERRITOIRE Ω pleinement exploitable en `--workers 1` pour 2 000 membres,
affichage perçu <1s grâce au squelette instantané + préchargement intelligent +
cache multi-niveaux optimisé.

### ARCHITECTURE 3-CERCLES TEMPORELS
- **Cercle T0 (~6s)** : terrain + meteo + zones + hotspots + salines + species + V5 corridors essentiels
- **Cercle T+Δ (BG_CACHE)** : corridors_vitaux + connectivité + affuts détaillés + comportement
- **Cercle AVANCÉ** : predictive IA + 3D overlays + MVT tiles (opt-in)

### MODIFICATIONS BACKEND
- `v20_performance_bundle.py` : constantes ESSENTIEL (TTL 600s, max 5000 entries),
  tag `bundle_tier` partout (ESSENTIEL_T0 / ENRICHI_TDELTA / COMPLET_T0),
  header `X-Bundle-Tier` sur toutes les réponses
- **NOUVEAU** `engines/v8_institutional/essentiel_prewarm_cron.py` :
  daemon cron pré-calcul 2000 membres (env-gated)
- **NOUVEAU** `routes/essentiel_prewarm_router.py` : endpoints `/api/admin/essentiel-prewarm/{status,trigger}`
- `server.py` : router + daemon enregistrés dans lifespan

### MODIFICATIONS FRONTEND
- `lib/bionicBundleCache.js` : maxEntries 128→5000, TTL ESSENTIEL 90s→600s,
  TTL COMPLET 24h, `bundleCacheTier()` exposé
- `hooks/useMapBundleV8.js` réécrit : état `bundleTier`, re-fetch silencieux T+12s/T+25s
- `IntelligentPreloadWidget.jsx` : préchargement ouvert à **tous les membres authentifiés**
  (pas seulement Premium), label dynamique selon tier user
- `TerritoireWarmupSplash.jsx` : durée 3-5s → 0.5-2s (squelette instantané)

### VALIDATION
- Bundle waypoint neuf : **2.84s · COMPLET_T0** (HTTP 200)
- Bundle HIT cache : **0.18s** (`X-Bundle-Tier: COMPLET_T0`)
- 2 espèces parallèles : 0.76s simultanées
- Screenshot Playwright : 94 polylines · CONFORMITÉ Ω 100% · SCORE 65.22

### ENV-VARS
- `P22OMEGA_ESSENTIEL_1WORKER=1` (ON par défaut)
- `P22OMEGA_PREWARM_MEMBERS_CRON=1` (OFF par défaut — activer post multi-worker)
- `P22OMEGA_PREWARM_MAX_MEMBERS=2000`
- `P22OMEGA_PREWARM_THROTTLE_SEC=3.0`
- `P22OMEGA_PREWARM_INTERVAL_SEC=14400`

---

## 2026-05-17 · P22ΩΩ_ALLEGEMENT_STRUCTUREL_OMEGA — Suppression 2628 lignes + Export JSON

### DIRECTIVE COMMANDANT STEEVE-MAX (Phase 2 autorisée explicitement)

### PHASE 1 — VALIDATION (sans effet)
- 10 modules `*_v1.py` listés : **7 N'EXISTAIENT PAS** déjà · 3 stubs trouvés (zones/hotspots/salines `_organic_v1.py`)
- Corridors V1-V4 : **0 existants**
- Scoring V1-V6 : **0 existants**
- Météo legacy : **0 existants**
- 7 composants frontend confirmés **0 imports** : Amenagement/BionicZoneDiagnostic/DiagnosticExclusions/MonTerritoireBionic/PhaseAPanelV8/PhaseCPanelV8/StandDetailPanel
- Routes "orphelines" `bionic_engine_router` + `map_perf` → en réalité **ACTIVES** via `modules/routers.py` et `server_orchestrator.py` (conservées)

### PHASE 2 — SUPPRESSION (autorisée)
- **3 stubs backend** : `zones_organic_v1.py` (55l) · `hotspots_organic_v1.py` (57l) · `salines_organic_v1.py` (55l)
- **7 composants frontend** : 2 461 lignes au total
- **Total purgé** : **2 628 lignes**
- 3 audit-tools nettoyés : `phase_omega_secure_lockdown.py` · `tools/audit_phase_engine_canonique.py` · `tools/audit_engines_x199_x200.py`

### VALIDATION POST-SUPPRESSION
- Screenshot Playwright `/territoire` : **94 polylines · 10 markers · HUD complet · CONFORMITÉ Ω 100% · SCORE 65.22**
- Bundle chevreuil : 5 zones · 13 corridors · 4 salines · 5 hotspots · HIT cache · NON dégradé
- Widget Premium fonctionnel : "1/3 · orignal"
- **0 régression**

### P22ΩΩ_TERRITOIRE_STRUCTURE_EXPORT
- JSON maître `/app/memory/TERRITOIRE_STRUCTURE_OMEGA.json` (20.17 KB · UTF-8)
- Endpoint téléchargeable `GET /api/export/territoire-structure?download=true`
- Endpoint metadata `GET /api/export/territoire-structure/meta`
- Copie miroir `/app/memory/audit_provenance/TERRITOIRE_STRUCTURE_OMEGA.json`
- Routeur : `routes/territoire_structure_export_router.py`

### PLAN_OPTIMISATION_TERRITOIRE_OMEGA
- 6 axes × 29 actions × roadmap P0→P5 (12 mois)
- Document : `/app/memory/PLAN_OPTIMISATION_TERRITOIRE_OMEGA.md`

---

## 2026-05-14 · P22ΩΩ_PRECHARGEMENT_INTELLIGENT_GEOLOCALISATION — Widget Premium

### DIRECTIVE COMMANDANT STEEVE-MAX
Implémenter un widget frontend "Préchargement intelligent par géolocalisation"
pour offrir une expérience 0-cold-start aux utilisateurs Premium en pré-chargeant
les 3 espèces préférées au waypoint favori.

### IMPLÉMENTATION
- **NOUVEAU** : `/app/frontend/src/lib/bionicBundleCache.js` — Cache LRU global
  window-level (90s TTL, 128 entrées) partagé entre `useMapBundleV8` et le widget.
- **NOUVEAU** : `/app/frontend/src/components/territoire/IntelligentPreloadWidget.jsx`
  — Widget Premium auto-déclenché. Préchargement séquentiel 3 espèces (1.5s
  inter-espèces, soft timeout 12s, retry 1× sur 502/503/504). États idle /
  running (cyan + spinner) / done (emerald + checkmark) / skipped. Position
  fixed bottom-4 right-4, pointer-events-none, non-bloquant.
- **MODIFIÉ** : `/app/frontend/src/hooks/useMapBundleV8.js` — Utilise le cache
  global window (les bundles préchargés sont consommés instantanément).
- **MODIFIÉ** : `/app/frontend/src/pages/MonTerritoireBionicPage.jsx` — Insertion
  du widget après `<TerritoireHeader/>`. Passage de favLat/favLon depuis
  `selectedWaypointForZones || activeWaypoints[0]`.

### VALIDATION VISUELLE (Playwright sur URL publique)
- T+8s : Widget visible "⚡ PRÉCHARGEMENT INTELLIGENT · Actif… 1/3 · chevreuil"
- T+18s : Widget terminé "⚡ PRÉCHARGEMENT INTELLIGENT · 0-cold-start prêt · 3/3 espèces"
- Couches rendues : corridors multi-espèces colorés, zones, affûts, hotspots, salines.
- HUD : CONFORMITÉ Ω 100% · CORRIDORS Ω 13 · ZONES Ω 5 · AFFÛTS Ω 8 · SALINES Ω 4 · HOTSPOTS Ω 4.

### BÉNÉFICES
- 0 cold-start visible pour Premium.
- Différenciation Premium / Free → argument de conversion.
- Aucun overhead Free (widget ne se rend pas).
- Compatible single-worker (séquentiel + pauses inter-espèces).

---

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
