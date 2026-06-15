# 🛠️ PLAN_DE_DECOUPAGE_V10_V20 · TERRITOIRE Ω
**Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE — Livrable 2/4
**Date** : 2026-05-19 · **Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX

> ⚠️ **PLAN D'EXÉCUTION — Code modifié uniquement après autorisation Phase 2.**

---

## 1. PRINCIPE DIRECTEUR

> *« Diviser un monolithe sans casser la science »*

- **Aucune modification** des algorithmes scientifiques Ω.
- **Aucune modification** des signatures publiques (handler `v20_territoire_bundle`, etc.).
- **Aucune modification** de la sémantique du bundle JSON (clés, valeurs, types).
- **Seuls** l'**emplacement** des fonctions, leur **organisation**, et les **imports** changent.

---

## 2. RÈGLES DE CONFORMITÉ Ω (à valider après chaque étape)

| # | Test | Critère de succès |
|---|---|---|
| C1 | `curl /api/v20/territoire/bundle?...chevreuil` | HTTP 200 + `X-Bundle-Tier` set |
| C2 | `curl /api/health` | HTTP 200 < 1s |
| C3 | Screenshot Playwright `/territoire` | 90+ polylines · CONFORMITÉ Ω 100% |
| C4 | Bundle JSON cohérence | zones≥1 · corridors≥1 · salines≥1 · hotspots≥1 |
| C5 | Bundle 5 espèces × 2 saisons | 0 erreur · 0 régression métrique |
| C6 | Cache HIT post-restart | bundle restauré du disque OK |
| C7 | Widget Premium IntelligentPreload | rendu OK sur user admin |

---

## 3. ORDRE D'EXTRACTION SÉQUENTIEL (10 étapes)

### 🔵 ÉTAPE 1 — Création de la structure modulaire (no-op)
```
/app/backend/engines/v8_institutional/
├── v10/__init__.py        ← package
├── v20/__init__.py        ← package
└── v30_future/__init__.py ← package
```
**Risque** : 🟢 nul · **Validation** : pylint imports OK · **Rollback** : `rm -rf v10 v20 v30_future`

---

### 🔵 ÉTAPE 2 — Extraction `v20/cache_orchestrator.py`
**Sortir de** `v20_performance_bundle.py` :
- `_CACHE` / `_CACHE_TTL_OVERRIDES` / `_CACHE_TTL_SEC` / `_CACHE_ESSENTIEL_TTL_SEC` / `_CACHE_DEGRADED_TTL_SEC`
- `_cache_key()` / `_cache_get()` / `_cache_set()` / `_cache_save_disk()` / `_cache_load_disk()`
- Constants `_LAST_BG_DISK_SAVE_TS` / `_STATS`

**Dans `v20_performance_bundle.py`** ajouter :
```python
from engines.v8_institutional.v20.cache_orchestrator import (
    _CACHE, _cache_key, _cache_get, _cache_set,
    _cache_save_disk, _cache_load_disk,
    _CACHE_ESSENTIEL_TTL_SEC, _CACHE_DEGRADED_TTL_SEC,
)
```

**Dépendances critiques** :
- `redis_omega.py` (lazy import dans `_cache_set`) — inchangé
- Aucune dépendance circulaire détectée

**Test** : C1 + C6 ✅

---

### 🔵 ÉTAPE 3 — Extraction `v20/daemons.py`
**Sortir de** `v20_performance_bundle.py` :
- `_daemon_sleep_randomized()`
- `_warmup_single()` / `_get_top_waypoints()` / `run_prechauffage_omega()`
- `_prewarm_engines_omega()`
- `_warmup_bsl_5_species_standard_contexts()`
- `_periodic_refresh_daemon()`
- `_DAEMONS_STATE` / `_BSL5_WARMUP_STARTED`

**Dépendances** : `_cache_set`, `_cache_get` → import depuis `cache_orchestrator`
**Test** : C1 + C6 ✅

---

### 🔵 ÉTAPE 4 — Extraction `v20/compliance_omega.py`
**Sortir de** `v20_performance_bundle.py` :
- `_v5_compliance_check_single()`
- `_v5_send_alert_resend()`
- `_v5_journal_append()`
- `_v5_compliance_monitor_daemon()`
- 4 endpoints `v20_audit_v5_*` (compliance live, monitor stats, monitor tick, alert test, daily report)

**Dépendances** : engine_ia_corridors_organic_omega + Resend
**Test** : C1 + C2 + endpoint compliance audit retournent 200

---

### 🔵 ÉTAPE 5 — Extraction `v20/rendu_avance.py`
**Sortir du `v20_territoire_bundle()`** la sub-routine post-V5 (RenduΩ + veineux + interzone + predictive + smoothing) :
- Bloc lignes ~1180-1300 du `v20_performance_bundle.py` actuel
- Imports `apply_predictive_omega_v2_to_bundle`, `engine_rendu_omega`, etc.

**Signature** :
```python
async def apply_rendu_avance(
    bundle: dict, lat: float, lon: float, species: str,
    month: int, hour: int, deadline_remaining: float
) -> dict:
    """Pipeline post-V5 : RenduΩ + veineux + interzone + predictive + smoothing.
    Court-circuit si deadline_remaining < 2s."""
```

**Test** : C5 (bundle final identique avant/après extraction)

---

### 🔵 ÉTAPE 6 — Extraction `v10/terrain_pipeline.py`
**Sortir de** `territoire_v10_supra.py` :
- (déjà partiel — `terrain_v10_supra.py` existe)
- Re-organiser proprement : créer wrapper `terrain_pipeline.compute_terrain_block(lat, lon)` qui appelle `compute_terrain_v10`

**Contrat JSON** : voir `INTERFACES_PIPELINES_V10_V20.md`

---

### 🔵 ÉTAPE 7 — Extraction `v10/meteo_pipeline.py`
**Wrapper** autour de :
- `open_meteo_breaker.fetch_meteo()`
- `lidar_irda_v11.fetch_lidar_irda()` (fallback)

**Signature** :
```python
async def compute_meteo_block(lat: float, lon: float, hour: int) -> dict:
    """Renvoie {temp, wind_deg, wind_speed, humidity, pressure, source}.
    Fallback automatique sur LIDAR-IRDA si Open-Meteo CB OPEN."""
```

---

### 🔵 ÉTAPE 8 — Extraction `v10/biologie_pipeline.py`
**Sortir de** `territoire_v10_supra.py` :
- `compute_zones_v10()` (165 lignes)
- `compute_hotspots_v10()` (49 lignes)
- `compute_salines_omega()` (128 lignes)
- Helpers : `_classify_corridor`, `_saline_terrain_profile`, `_find_nearest_corridor_intense`, `_suggest_new_position`

**Signature unifiée** :
```python
def compute_biologie_block(
    lat: float, lon: float, species: str, month: int,
    terrain_block: dict, corridors_block: dict
) -> dict:
    """Renvoie {zones, hotspots, salines}."""
```

---

### 🔵 ÉTAPE 9 — Extraction `v10/affuts_pipeline.py`
**Sortir de** `territoire_v10_supra.py` :
- `compute_affuts_omega()` (266 lignes — la plus grosse) → décomposer en :
  - `_compute_affuts_placement` (recherche emplacements)
  - `_compute_affuts_visibility` (rayon visibilité)
  - `_compute_affuts_acoustique` (audio)
  - `_compute_affuts_terrain_cost` (coût parcours)
- `compute_contamination_omega()` (cônes vent)
- Helpers : `_generate_cone`, `_is_under_wind`, `_cone_overlap_check`

**Signature** :
```python
def compute_affuts_block(
    lat: float, lon: float, species: str,
    zones_block: dict, corridors_block: dict,
    meteo_block: dict, terrain_block: dict
) -> dict:
    """Renvoie {affuts, contamination, visibility_radii}."""
```

---

### 🔵 ÉTAPE 10 — Extraction `v20/territoire_logic.py`
**Sortir de** `v20_performance_bundle.py` la fonction maîtresse `v20_territoire_bundle` :
- Garder le handler HTTP minimal dans `server.py` (route prefix `/api/v20/territoire/bundle`)
- Le handler appelle `v20_territoire_logic.execute(...)`
- `execute()` orchestre : terrain → meteo → biologie → corridors V5 → affuts → rendu

**Test final** : C1-C7 tous validés ✅

---

## 4. PARALLÉLISATION ASYNCIO (post-extraction)

Après les 10 étapes, on peut **paralléliser** les sub-pipelines V10 :

```python
# AVANT (séquentiel ~50s cold-start)
terrain = await compute_terrain_block(lat, lon)
meteo = await compute_meteo_block(lat, lon, hour)
biologie = compute_biologie_block(...)
affuts = compute_affuts_block(...)

# APRÈS (parallèle ~15s cold-start)
terrain_task = asyncio.create_task(compute_terrain_block(lat, lon))
meteo_task = asyncio.create_task(compute_meteo_block(lat, lon, hour))
terrain, meteo = await asyncio.gather(terrain_task, meteo_task)
biologie = compute_biologie_block(terrain=terrain, ...)  # dépend de terrain
affuts = compute_affuts_block(biologie=biologie, meteo=meteo, terrain=terrain, ...)
```

**Gain estimé** : 50s → 15s sur le cold-start (multi-worker bonus indépendant).

---

## 5. PRÉREQUIS LEGACY À SUPPRIMER **AVANT** EXÉCUTION

| Fichier | Lignes | Raison |
|---|---|---|
| `engines/v8_institutional/engine_ia_corridors_omega.py` (V4) | ~400 | Remplacé par V5 organic |
| `engines/v8_institutional/federal_datasets_omega.py` | ~200 | 0 usage prod |
| `engines/v8_institutional/science_gaps_datasets.py` | ~150 | 0 usage prod |
| `/app/backend/tests/test_phase_*.py` (116 fichiers) → archivage | ~12 000 | Tests legacy non-CI |
| `/app/backend/tests/test_render_*.py` (12 fichiers) → archivage | ~1 500 | Idem |

**Total** : ~14 250 lignes à neutraliser avant extraction.

---

## 6. TESTS DE CONFORMITÉ Ω PAR ÉTAPE

```bash
# Test post-extraction (à exécuter après chaque étape 1→10)
API="https://bionic-ultime-1.preview.emergentagent.com"

# C1 — Bundle endpoint
curl -s -m 8 "$API/api/v20/territoire/bundle?lat=48.207&lon=-68.382&species=chevreuil&month=5&hour=13&wind_deg=225" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); \
    assert d.get('cache') in ['HIT','MISS'], 'cache field missing'; \
    assert d.get('bundle_tier') in ['ESSENTIEL_T0','ENRICHI_TDELTA','COMPLET_T0'], 'bundle_tier wrong'; \
    assert len(d.get('zones',[])) >= 1, 'zones empty'; \
    assert len(d.get('corridors',[])) >= 1, 'corridors empty'; \
    print('✓ C1 OK')"

# C2 — Health
curl -s -m 3 "$API/api/health" | grep -q "healthy" && echo "✓ C2 OK"

# C3 — Playwright (manuel via screenshot tool)

# C4 — Cohérence multi-espèces × multi-saisons
for sp in chevreuil orignal ours_noir coyote dindon_sauvage ; do
  for month in 5 10 ; do
    curl -s -m 8 "$API/api/v20/territoire/bundle?lat=48.207&lon=-68.382&species=$sp&month=$month&hour=13&wind_deg=225" \
      | python3 -c "import json,sys; d=json.load(sys.stdin); assert len(d.get('zones',[]))>=1; print('  ✓ $sp m=$month OK')"
  done
done

# C6 — Cache HIT post-restart
sudo supervisorctl restart backend ; sleep 10
curl -s -m 8 "$API/api/v20/territoire/bundle?lat=48.207&lon=-68.382&species=chevreuil&month=5&hour=13&wind_deg=225" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('cache')=='HIT'; print('✓ C6 OK')"
```

---

## 7. PLANNING ESTIMATIF

| Étape | Description | Effort | Validation |
|---|---|---|---|
| 0 | Cleanup legacy (P22ΩΩ_CLEANUP_LEGACY_FINAL) | 1 jour | C1-C7 |
| 1 | Création packages `v10/` `v20/` `v30_future/` | 0.5 jour | pylint imports |
| 2 | Extraction `cache_orchestrator.py` | 1 jour | C1 + C6 |
| 3 | Extraction `daemons.py` | 1 jour | C1 + smoke daemons |
| 4 | Extraction `compliance_omega.py` | 1 jour | C2 + audit endpoints |
| 5 | Extraction `rendu_avance.py` | 2 jours | C5 |
| 6 | Wrapper `terrain_pipeline.py` | 0.5 jour | C1 |
| 7 | Wrapper `meteo_pipeline.py` | 0.5 jour | C1 |
| 8 | Extraction `biologie_pipeline.py` | 2 jours | C4 + C5 |
| 9 | Extraction `affuts_pipeline.py` (le plus gros) | 3 jours | C4 + C5 |
| 10 | Extraction `territoire_logic.py` + parallélisation | 2 jours | C1-C7 + benchmark |

**Total estimé** : ~14 jours d'effort (~3 semaines avec marge sécurité).

---

## 8. RISQUES & MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Casse import circulaire | Moyenne | Élevé | Tests pytest unitaires par étape |
| Régression bio-précision | Faible | Critique | Diff bundle JSON avant/après (script auto) |
| Régression cache HIT ratio | Faible | Élevé | C6 + métrique cache_size |
| Dépendance lazy oubliée | Moyenne | Moyen | Audit imports `grep -r "import territoire_v10"` |

---

## 9. SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE
- **Livrable** : 2/4 — Plan de découpage V10/V20
- **Validation** : COMMANDANT STEEVE-MAX
