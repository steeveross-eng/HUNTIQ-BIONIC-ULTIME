# 📋 ANALYSE_MONOLITHIQUE_SERVER · TERRITOIRE Ω
**Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE — Livrable 1/4
**Date** : 2026-05-19 · **Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX

> ⚠️ **DOCUMENT D'ANALYSE — AUCUN CODE MODIFIÉ.**

---

## 1. SYNTHÈSE EXÉCUTIVE

| Composant | Taille | Type | Responsabilités enchevêtrées | Gravité |
|---|---|---|---|---|
| **`v20_performance_bundle.py`** | **1 982 lignes** | Mégafichier orchestrateur | Cache + hardcaps + warmup + daemons + corridors V5 + endpoints HTTP + monitoring + alerting Resend + audit V5 | 🔴 CRITIQUE |
| **`territoire_v10_supra.py`** | **1 495 lignes** | Mégafichier scientifique | Terrain + zones + corridors V10 + affûts + hotspots + salines + contamination + comportement biologique + population | 🔴 CRITIQUE |
| **`server.py`** | **1 686 lignes** | Mégafichier routing | Lifespan + 142 routers + auth + payments + waypoints + groups + cache management | 🟠 ÉLEVÉE |
| **`MonTerritoireBionicPage.jsx`** | **1 907 lignes** | Mégafichier UI | Carte + HUD + panneaux + waypoints + sharing + onboarding | 🟠 ÉLEVÉE |

**Verdict** : 7 070 lignes monolithiques réparties sur 4 fichiers. Une réduction de 60% est atteignable en modularisant.

---

## 2. CARTOGRAPHIE PRÉCISE DES ZONES MONOLITHIQUES

### 2.1 `v20_performance_bundle.py` — 28 fonctions top-level mélangées

Découpage logique des responsabilités enchevêtrées :

| Zone fonctionnelle | Lignes approx. | Fonctions concernées |
|---|---|---|
| **A. Cache & TTL** (LRU + Redis + disk) | ~150 | `_cache_key`, `_cache_get`, `_cache_set`, `_cache_save_disk`, `_cache_load_disk` |
| **B. Daemons & Warmup** | ~250 | `_daemon_sleep_randomized`, `_warmup_single`, `_get_top_waypoints`, `run_prechauffage_omega`, `_prewarm_engines_omega`, `_periodic_refresh_daemon`, `_warmup_bsl_5_species_standard_contexts` |
| **C. Lazy-init & Startup** | ~120 | `_ensure_lazy_init`, `_ensure_redis_daemon_up`, `v20_startup`, `v20_shutdown` |
| **D. Hardcaps & Timeouts** | ~80 | `_effective_miss_hardcap`, `_GLOBAL_BUNDLE_DEADLINE_SEC` |
| **E. Corridors V5 mapping** | ~60 | `map_v5_corridors_to_ui` |
| **F. Bundle orchestrator** (cœur) | ~520 | `v20_territoire_bundle` (la fonction monstre 865→1383) |
| **G. Compliance monitor V5** | ~250 | `_v5_compliance_check_single`, `_v5_send_alert_resend`, `_v5_journal_append`, `_v5_compliance_monitor_daemon` |
| **H. Endpoints HTTP** | ~340 | `v20_bundle_stats`, `v20_bundle_purge`, `v20_bundle_warmup`, `v20_bundle_save_disk`, `v20_healthz_worker`, `v20_audit_v5_*` (×4) |
| **I. Helpers** | ~80 | `normalize_species`, etc. |

🔴 **Problème** : Tout est dans un seul fichier. Modification d'un sous-système risque d'impacter les autres.

### 2.2 `territoire_v10_supra.py` — Pipeline scientifique tout-en-un

```
compute_territoire_v10 (orchestrateur, ligne 1154, signature 8 paramètres)
    │
    ├─ await compute_terrain_v10           (1 seul await, le reste sync)
    ├─ compute_zones_v10                   (ligne 64, 165 lignes)
    ├─ compute_corridors_omega             (ligne 260, 129 lignes — pas la V5 native, ancienne)
    ├─ compute_contamination_omega         (ligne 521, 46 lignes)
    ├─ compute_affuts_omega                (ligne 590, 266 lignes — TROP GROSSE)
    ├─ compute_hotspots_v10                (ligne 856, 49 lignes)
    ├─ compute_salines_omega               (ligne 1026, 128 lignes)
    ├─ compute_comportement_biologique     (import dynamique ligne 1238)
    ├─ compute_population_dynamics         (import dynamique ligne 1246)
    └─ retour bundle dict
```

🔴 **Problème** : Le `compute_affuts_omega` (266 lignes) intègre visibilité + terrain_cost + acoustique. Devrait être 4 sous-pipelines.

### 2.3 Dépendances croisées identifiées

```
v20_performance_bundle.py
    ├── importe compute_territoire_v10 (territoire_v10_supra.py)
    ├── importe generate_organic_corridors (engine_ia_corridors_organic_omega.py)
    ├── importe apply_predictive_omega_v2_to_bundle (predictive_omega_v2.py)
    └── importe redis_omega (redis_omega.py)

territoire_v10_supra.py
    ├── importe terrain_v10 (terrain_v10_supra.py)
    ├── importe engine_comportement_biologique_omega (lazy)
    └── importe engine_population_dynamics_omega (lazy)

ecological_orchestrator_omega.py (orchestrateur secondaire)
    └── importe corridors_vitaux_omega, engine_connectivite_ecologique_omega
```

**Couplage fort** : V20 ne peut pas tourner sans V10 (logique). V10 ne peut PAS tourner sans terrain V10.

---

## 3. MODULES LEGACY IDENTIFIÉS (audit production)

### 3.1 Tests legacy (à archiver)

- **`/app/backend/tests/test_phase_*.py`** : **116 fichiers** de tests historiques (phases A, B, C, D, E, XI, XII, XIII, XIV, XV, XVII, XVIII, XIX)
- **`/app/backend/tests/test_render_*.py`** : **12 fichiers** de tests rendu legacy
- **`/app/backend/tests/test_phase_e_purge_legacy_omega_reinjection.py`** : référence directe aux modules legacy

🟡 **Note** : Ces tests sont **archivés** (pas exécutés en CI actuellement). Ils peuvent être déplacés vers `/app/backend/tests/archive/` sans impact.

### 3.2 Engines V4 LEGACY

| Engine | Production usage ? | Verdict |
|---|---|---|
| `engine_ia_corridors_omega.py` (V4) | ❌ 0 ref hors tests | 🟢 **SUPPRESSIBLE** (V5 organic actif) |
| `corridors_organic_v1.py` | N/A (déjà supprimé phase 1) | ✅ DÉJÀ FAIT |
| `engine_comportement.py` (legacy) | ⚠️ ref par `piliers_router`, `securite_omega_v19`, `supra_v8` | 🟠 **CONSERVER** (chaîne piliers) |
| `engine_comportement_avance.py` | ⚠️ ref par `piliers_router`, `securite_omega_v19`, `supra_v8` | 🟠 **CONSERVER** |
| `engine_psychologie.py` | ⚠️ ref par `piliers_router`, `securite_omega_v19` | 🟠 **CONSERVER** |
| `engine_comportement_biologique_omega.py` (V11) | ✅ PRIMARY in `territoire_v10_supra` ligne 1238 | ✅ ACTIF |

### 3.3 Engines rendu legacy

| Engine | Usage | Verdict |
|---|---|---|
| `engine_render_omega.py` | ✅ ref par `phase_omega_secure_lockdown` + `doctrine_v90_omega` + `server.py` | 🟢 ACTIF |
| `engine_rendu_omega.py` | Pipeline post-V5 | 🟢 ACTIF |

### 3.4 Datasets legacy

| Engine | Usage prod (hors tests) | Verdict |
|---|---|---|
| `federal_datasets_omega.py` | ❌ Aucune | 🟢 **SUPPRESSIBLE** (post-validation) |
| `science_gaps_datasets.py` | ❌ Aucune | 🟢 **SUPPRESSIBLE** (post-validation) |
| `origine_externe_filter_omega.py` | ✅ ref `v20_performance_bundle.py` | 🟢 ACTIF |
| `origine_externe_inversion_omega.py` | ⚠️ ref tests + tools uniquement | 🟡 **À ÉVALUER** |
| `lep_ingestion_omega.py` | ✅ ref `server.py` + `self_audit_omega` | 🟢 ACTIF (stub doctrinal) |

### 3.5 Sécurité legacy

| Engine | Usage | Verdict |
|---|---|---|
| `securite_omega_v19.py` | ✅ ref `piliers_router` + lockdown | 🟢 ACTIF (mais V19, à moderniser) |
| `protections_omega.py` | ✅ ref `piliers_router` + lockdown | 🟢 ACTIF |
| `phase_omega_secure_lockdown.py` | ✅ ref `fusion_territoire_omega_router` | 🟢 ACTIF |
| `registry_lock_omega.py` | ✅ Self-audit chain | 🟢 ACTIF |

### 3.6 Affûts legacy

| Engine | Usage | Verdict |
|---|---|---|
| `engine_affuts.py` (PRIMARY V11) | ✅ via `compute_affuts_omega` chain | 🟢 ACTIF |
| Aucun `engine_affuts_v1/v2/v3` trouvé | — | ✅ Déjà purgé |

---

## 4. RISQUES IDENTIFIÉS POUR LA MODULARISATION

| # | Risque | Impact | Mitigation |
|---|---|---|---|
| R1 | **`compute_territoire_v10` est un import direct** — si on le déplace, cassure des imports backend | 🔴 HIGH | Phase d'extraction avec ré-export rétrocompatible |
| R2 | **`v20_territoire_bundle` est l'unique handler de `/api/v20/territoire/bundle`** — toute scission introduit du refactor route | 🟠 MEDIUM | Garder la signature publique inchangée |
| R3 | **Headers `X-Bundle-Tier` requis pour P22ΩΩ_ESSENTIEL_1WORKER** — chaque sub-pipeline doit savoir set ses propres headers | 🟠 MEDIUM | Pattern : orchestrator inject les headers |
| R4 | **Tests legacy 116 fichiers** non maintenus — risque de tester du code mort | 🟡 LOW | Archiver vers `/tests/archive/` |
| R5 | **Daemons + Cron prewarm** dispersés entre `v20_performance_bundle.py` et `essentiel_prewarm_cron.py` | 🟡 LOW | Regrouper sous `v20_daemons_omega.py` |
| R6 | **Pipeline post-V5** (RenduΩ + veineux + predictive + 3D + MVT) mélangé avec orchestrateur | 🟠 MEDIUM | Sortir en `v20_rendu_avance.py` |
| R7 | **Compliance monitor V5 + alerting Resend** intégré au `v20_performance_bundle.py` | 🟠 MEDIUM | Sortir en `v20_compliance_omega.py` |
| R8 | **Engines V4 LEGACY `engine_ia_corridors_omega.py`** présent mais non utilisé | 🟢 LOW | Supprimer après revue finale |

---

## 5. RECOMMANDATIONS D'ARCHITECTURE CIBLE

```
/app/backend/engines/v8_institutional/
│
├── v10/                                  # Pipelines V10 (extraction scientifique pure)
│   ├── __init__.py
│   ├── terrain_pipeline.py               # ← compute_terrain_v10 (déjà séparé)
│   ├── meteo_pipeline.py                 # ← open_meteo_breaker + lidar_irda_v11
│   ├── biologie_pipeline.py              # ← zones + hotspots + salines
│   └── affuts_pipeline.py                # ← affuts + visibilite + terrain_cost + audio
│
├── v20/                                  # Pipelines V20 (composition)
│   ├── __init__.py
│   ├── territoire_logic.py               # ← orchestration V10 + V5 corridors
│   ├── rendu_avance.py                   # ← veineux + predictive + 3D + MVT
│   ├── cache_orchestrator.py             # ← LRU + Redis + disk + TTL tiers
│   ├── daemons.py                        # ← warmup + prechauffage + refresh
│   └── compliance_omega.py               # ← V5 compliance monitor + Resend alerts
│
├── v30_future/                           # Engines futurs
│   ├── territory_static_engine.py        # ← ZeroCost phase 1
│   ├── deferred_rendering_engine.py      # ← ZeroCost phase 1
│   └── zero_cost_engine.py               # ← ZeroCost phase 2 (CDN edge)
│
└── (engines scientifiques inchangés)
```

---

## 6. CONCLUSION

### Verdict global
- **Monolithe quantifié** : 7 070 lignes en 4 fichiers principaux
- **Modules legacy à supprimer** : 4 candidats (V4 corridors, federal_datasets, science_gaps, origine_externe_inversion)
- **Tests à archiver** : 116 fichiers test_phase_* + 12 test_render_*
- **Risques** : 8 identifiés, tous mitigables avec un découpage séquentiel

### Action immédiate recommandée
**Phase 0 — Pre-modularisation cleanup** :
1. Supprimer `engine_ia_corridors_omega.py` (V4 legacy)
2. Supprimer `federal_datasets_omega.py` + `science_gaps_datasets.py` (datasets non utilisés)
3. Archiver `/tests/test_phase_*.py` (116 fichiers) vers `/tests/archive/`

### Action de fond
**Phase 1 → Phase 5** : voir `Plan_de_decoupage_V10_V20.md`

---

## 📋 SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE
- **Livrable** : 1/4 — Analyse monolithique
- **Validation** : COMMANDANT STEEVE-MAX
