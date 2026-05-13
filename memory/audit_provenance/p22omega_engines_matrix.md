# P22Ω_ENGINES_MATRIX — VISIBILITÉ TOTALE ENGINES × DATASETS × COUCHES

**Date UTC** : 2026-05-13
**Commandant** : STEEVE-MAX
**Scope** : Inventaire exhaustif engines actifs + matrice 3D engines/datasets/couches

---

## 1 · INVENTAIRE EXHAUSTIF DES ENGINES ACTIFS

### 1.1 · ENGINE V5 ORGANIC (CORRIDORS NATIFS · ACTIF · PRIMARY)
- **Fichier** : `/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py` (82.6 KB, 1739 lignes)
- **Rôle** : Génération native des corridors biologiques par espèce (V5 ENGINE)
- **Inputs** :
  - bundle pré-calculé compute_territoire_v10 (zones, hotspots, salines)
  - SPECIES_BEHAVIOR (8 params: sinuosity, amplitude, vitesse, prudence, ouverture_preferee, hydro_dep, couvert_pref, n_corridors)
  - BIOLOGICAL_PAIR_COMPATIBILITY (paires vitales par espèce)
  - Paramètres : lat, lon, species, month, hour, wind_deg, wind_speed
- **Outputs** :
  - `corridors[]` : 5-7 LineStrings (Catmull-Rom 120 pts, segment ≤ 20m)
  - `hierarchy_counts` : {veine_principale, veine_secondaire, capillaire, connector}
  - `p22sigma_v5_cap_global_doctrine` : metadata cap doctrinal
  - `engine` : "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
- **Dépendances** :
  - `territoire_v10_supra.compute_territoire_v10` (pour bundle pré-calculé)
  - `engine_ia_corridors_omega.py` (legacy V8) → **NON utilisé directement**, juste référencé pour V30 SHA lock
- **Datasets consommés** : zones vitales du bundle, terrain_ms (drainage_density, forest_cover, open_areas, micro_coulees)
- **Couches influencées** : `corridors`, `hierarchy_counts` (UI métadata)
- **Redondances** : aucune
- **Lignes critiques** : L156 (SPECIES_BEHAVIOR), L590 (BIOLOGICAL_PAIR_COMPATIBILITY), L774-870 (_generate_corridor_between post-P22Ω_DIVERGENCE), L941 (SPECIES_BEHAVIOR.get fallback)

### 1.2 · ENGINE V8 LEGACY CORRIDORS (DEPRECATED · NON-UTILISÉ BUNDLE)
- **Fichier** : `/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py` (17.8 KB)
- **Rôle** : Ancien moteur V8 corridors (pre-V5)
- **Statut** : **NON IMPORTÉ par bundle V20**, gardé pour audit V30 SHA lock
- **Décommission** : C2 (J+30 stabilité V5)

### 1.3 · ENGINE V10 SUPRA (TERRITOIRE COMPUTE · ACTIF · PRIMARY)
- **Fichier** : `/app/backend/engines/v8_institutional/territoire_v10_supra.py`
- **Rôle** : Compute brut du territoire (zones, hotspots, salines, contamination, terrain_ms)
- **Inputs** : lat, lon, species, month, hour, wind_deg, wind_speed
- **Outputs** : bundle dict avec `zones`, `corridors` (V30 brut pré-V5), `hotspots`, `salines`, `affuts`, `contamination`, `terrain_ms`, `microclimat`, `social`, `sante`
- **Dépendances** : `lidar_irda_v11.py`, GIS engines, masks
- **Datasets consommés** : Lidar IRDA (NASA), Open-Meteo, Overpass OSM, WMS MFFP, terrain DEM
- **Couches influencées** : `zones`, `hotspots`, `salines`, `affuts`, `contamination`, `terrain_ms`, `microclimat`

### 1.4 · LIDAR IRDA V11 (EXTERNAL APIS · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/lidar_irda_v11.py`
- **Rôle** : Bridge Lidar IRDA + Open-Meteo + DEM
- **Inputs** : lat, lon, month
- **Outputs** : terrain features, météo, canopée
- **Dépendances** : `open_meteo_breaker.py` (circuit breaker)
- **Datasets externes** : NASA EarthData (Lidar), Open-Meteo API (météo), DEM Canada

### 1.5 · SMOOTHER ORGANIC (POST-PROCESSOR · ACTIF · ROUTE-LEVEL)
- **Fichier** : `/app/backend/engines/post_smoothing/organic_corridor_smoother.py`
- **Rôle** : Post-processing des corridors V5 (lissage, normalisation, RenduΩ inline)
- **Inputs** : body (lat, lon, species, anchor_mode), V5 engine output
- **Outputs** : corridors lissés + metadata RenduΩ
- **Dépendances** : V5 organic engine, V20 normalize_species
- **SPECIES_LOCOMOTION** : 7 espèces (chevreuil/orignal/ours/ours_noir/dindon/dindon_sauvage/coyote)
- **Endpoints exposés** : `POST /generate`, `GET /smoother-status`, `POST /purge` (P22Ω_CORRIDORS_ZONES_STABILISATION), `GET /cache-stats`
- **Couches influencées** : `corridors` (post-processing)

### 1.6 · RENDUΩ (POST-PROCESSOR · ACTIF)
- **Fichier** : `/app/backend/engines/post_smoothing/renduomega.py`
- **Rôle** : Application style RENDUΩ + couleurs doctrine + métadonnées finales
- **Inputs** : bundle complet (avant style)
- **Outputs** : bundle avec styles + flags `rendu_omega_applied`
- **Appelé 2× dans le pipeline** : ligne 1007 et 1078 de v20_performance_bundle.py (⚠ redondance P2)

### 1.7 · VEINEUX Ω (POST-PROCESSOR · ACTIF)
- **Fichier** : `/app/backend/engines/post_smoothing/veineux_omega.py`
- **Rôle** : Génération sub-network capillaire sur corridors V5
- **Inputs** : bundle avec corridors V5
- **Outputs** : bundle + sub-paths capillaires
- **Couches influencées** : `corridors` (sub-network)

### 1.8 · INTERZONE Ω (POST-PROCESSOR · ACTIF)
- **Fichier** : `/app/backend/engines/post_smoothing/interzone_omega.py`
- **Rôle** : Détection zones d'interaction inter-vitales
- **Couches influencées** : metadata zones

### 1.9 · PREDICTIVE Ω V2 (POST-PROCESSOR · ACTIF · 2× INVOCATIONS)
- **Fichier** : `/app/backend/engines/predictive_omega/predictive_omega_v2.py` (estimé)
- **Rôle** : Renforcement prédictif sur zones + contamination + hotspots
- **Couches influencées** : `contamination_v2`, `contamination_v2_heatmap`, prediction hotspots

### 1.10 · PRESENCE MASK MFFP (FILTER · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/species_presence_mask_omega.py`
- **Rôle** : Filtrage des espèces selon rectangles MFFP (présence officielle)
- **Inputs** : lat, lng, species
- **Outputs** : `bio_presence_mask_halt`, `bio_presence_mask_applied`, registry status
- **6 espèces** : chevreuil, orignal, wapiti, ours_noir, dindon_sauvage, coyote
- **Couches influencées** : tout le bundle (halt = corridors=[], hotspots=[], salines=[], zones préservées audit)

### 1.11 · ORIGINE EXTERNE FILTER Ω (DEPRECATED · DÉSACTIVÉ)
- **Fichier** : `/app/backend/engines/v8_institutional/origine_externe_filter_omega.py`
- **Statut** : ⚠ **COMMENTÉ dans server.py** (décommission J+30)
- **Rôle ancien** : Filtrage origine externe (avant V5 doctrine)
- **Décommission** : C4

### 1.12 · ESI Ω VALIDATOR (VALIDATOR · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/esi_omega.py`
- **Rôle** : Validation finale bundle (ESI Ω → CONFORME / WARN / FAIL)
- **Outputs** : `esi_omega` flag dans bundle

### 1.13 · REDIS Ω (CACHE · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/redis_omega.py`
- **Rôle** : Cache L1 Redis cross-pod
- **Endpoints** : `redis_get`, `redis_set`, `redis_purge`, `redis_stats`, `is_redis_enabled`

### 1.14 · OPEN-METEO CB (CIRCUIT BREAKER · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/open_meteo_breaker.py`
- **Rôle** : Circuit breaker pour Open-Meteo API (3 errors/90s → OPEN 600s — POST-E2)
- **Stats** : `total_blocked`, `total_errors_recorded`, `open_until`

### 1.15 · FUSION TERRITOIRE Ω (VALIDATOR PHASE-E · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/fusion_territoire_omega.py`
- **Endpoint** : `GET /api/v30/territoire/ultime-score`
- **Rôle** : Calcule ultime_score 0-1 via 6 chaînes institutionnelles
- **Lock V30** : SHA-256 des fichiers registry + V8 legacy (POST-E3 SHA réceptionné)

### 1.16 · CORRIDORS VITAUX Ω (PHASE XVIII · ACTIF)
- **Fichier** : `/app/backend/engines/v8_institutional/corridors_vitaux_omega.py`
- **Endpoint** : `GET /api/v30/corridors/vitaux-omega`
- **Rôle** : Endpoint de diagnostic des vitaux (lecture seule)

---

## 2 · MATRICE ENGINE × DATASET × COUCHE

| Engine | Datasets consommés | Couches influencées | Position pipeline |
|---|---|---|---|
| **territoire_v10_supra** | Lidar IRDA, Open-Meteo, Overpass OSM, WMS MFFP, DEM | zones, hotspots, salines, affuts, contamination, terrain_ms, microclimat | 1 |
| **engine_ia_corridors_organic_omega (V5)** | bundle compute_v10 (zones), SPECIES_BEHAVIOR, BIOLOGICAL_PAIR_COMPATIBILITY | corridors (LineStrings Catmull-Rom), hierarchy_counts | 2 |
| **map_v5_corridors_to_ui** (lambda) | V5 raw output | corridors (UI structure : id, hierarchy, color, subnet_role) | 3 |
| **species_presence_mask_omega** | SPECIES_PRESENCE_REGISTRY (MFFP rectangles), lat/lng/species | tout le bundle (halt potentiel) | 4 |
| **interzone_omega** | bundle.zones | metadata zones (interactions) | 5 |
| **veineux_omega** | bundle.corridors V5 | corridors (sub-network capillaire) | 6 |
| **predictive_omega_v2** | bundle.zones + bundle.contamination | contamination_v2, contamination_v2_heatmap, prediction hotspots | 7-7bis (2×) |
| **renduomega** (×2) | bundle complet | styles couleurs + métadonnées rendu | 8a + 8b (redondance P2) |
| **esi_omega** | bundle final | esi_omega flag | 9 |
| **organic_corridor_smoother** (route /generate) | V5 engine output | corridors lissés (post-process) | hors-bundle |
| **open_meteo_breaker** | Open-Meteo API state | bloque requêtes Open-Meteo si CB OPEN | global |
| **redis_omega** | bundle final (sérialisé) | cache L1 cross-pod | 10 |
| **fusion_territoire_omega** | bundle V30 status + microclimat + habitat | ultime_score (0-1), band, v30_invariance | endpoint séparé |
| **corridors_vitaux_omega** | bundle compute_v10 | layer-diagnostic (lecture seule) | endpoint séparé |

---

## 3 · MATRICE INVERSE : COUCHE → ENGINES PRODUCTEURS

| Couche UI | Engine principal | Post-processors |
|---|---|---|
| `corridors` | V5 organic | smoother, veineux, renduomega |
| `zones` | territoire_v10 | interzone, renduomega |
| `hotspots` | territoire_v10 | predictive_omega_v2, renduomega |
| `salines` | territoire_v10 (OSM) | renduomega |
| `affuts` | territoire_v10 (+ user DB) | renduomega |
| `contamination` | territoire_v10 (CWD DB) | renduomega |
| `contamination_v2` | predictive_omega_v2 | renduomega |
| `contamination_v2_heatmap` | predictive_omega_v2 | renduomega |
| `terrain_ms` | territoire_v10 (Lidar/DEM) | — |
| `presence_mask_halt` | species_presence_mask_omega | — (effet global) |
| `esi_omega` | esi_omega validator | — |
| `ultime_score` | fusion_territoire_omega (Phase-E) | — |

---

## 4 · REDONDANCES IDENTIFIÉES

| ID | Redondance | Sévérité | Statut |
|---|---|---|---|
| R1 | `apply_renduomega_to_bundle` appelé 2× (ligne 1007 + 1078) | 🟢 P2 | Idempotent — refactor optionnel |
| R2 | V8 legacy `engine_ia_corridors_omega.py` chargé mais non utilisé | 🟢 P2 | Décommission C2 |
| R3 | `origine_externe_filter_omega.py` désactivé mais fichier présent | 🟢 P2 | Décommission C4 |
| R4 | `engine_render_omega.py` + `engine_rendu_omega.py` (anciens) vs `renduomega.py` (actuel) | 🟢 P2 | Décommission C3 |
| R5 | `phase_a_engines.py` commenté mais présent | 🟢 P2 | Décommission C1 |
| R6 | `predictive_omega_v2` appelé 2× (orchestré inter-couches) | 🟢 OK | Doctrinalement voulu |
| R7 | Smoother peut appeler `compute_v10` indirectement via V5 (double cache) | 🟡 P2 | Cache L1/L2 mitige |
| R8 | Le bundle endpoint et le smoother endpoint produisent tous deux des corridors | 🟢 OK | Smoother = post-process indépendant, alimente UI bonus |

## 5 · DUPLICATIONS DE DONNÉES

| ID | Duplication | Sévérité | Mitigation |
|---|---|---|---|
| D1 | `corridors` dans bundle + corridors dans smoother output | 🟢 OK | Routes distinctes |
| D2 | `terrain_ms` dans bundle + features dans corridors | 🟢 OK | Référencement |
| D3 | Hotspots + contamination_v2 hotspots | 🟡 P2 | À fusionner UI side |
| D4 | Salines centroïdes + zones type=saline | 🟢 OK | Représentations différentes |

## 6 · CONFLITS POTENTIELS ENTRE COUCHES

| ID | Conflit | Sévérité | Mitigation actuelle |
|---|---|---|---|
| CF1 | Hotspots VS corridors visuels sur même pixel | 🟢 OK | Z-order doctrinal (hotspots > corridors) |
| CF2 | Vent z=605 masque affuts z=590 | 🟡 P2 | UI toggle layer (optionnel) |
| CF3 | Zones z=500 sous hydrologie z=515 | 🟢 OK | Opacité zones 0.3 |
| CF4 | Contamination overlay sans z-index doctrinal | 🟡 P2 | À ajouter à RENDU_OMEGA.zIndexOrder |
| CF5 | Cesium 3D + Leaflet 2D simultanés | 🟢 OK | Modes exclusifs (toggle UI) |
| CF6 | V30 corridors vs V5 corridors (si remap actif) | 🟢 OK | V30 remap inactif sur 5 espèces (post-fixes) |

## 7 · INCOHÉRENCES POSSIBLES DANS LE PIPELINE

| ID | Incohérence | Sévérité | Détection actuelle |
|---|---|---|---|
| I1 | Bundle dégradé (DEGRADED_MISS_ABSORPTION) caché en Redis | 🔴 Bloquant | ✓ Patché — skip cache si `p22omega_miss_absorbed=True` |
| I2 | Cache poisoning chevreuil-only par warmup compute_v10 partiel | 🔴 Bloquant | ✓ Patché — warmup invoke pipeline complet |
| I3 | Smoother direct (POST /generate) bypass normalisation species | 🟡 P1 | ✓ Patché P22Ω_MULTI_FIX_A3 (normalize_species dans cache_key + gen_func) |
| I4 | V30 invariance mismatch SHA legacy | 🔴 Bloquant | ✓ Patché P22Ω_PHASE1_P1_FIXES (E3 réceptionnement baseline) |
| I5 | Open-Meteo rate limit non géré | 🔴 Bloquant | ✓ Patché P22Σ_OPEN_METEO_CB_Ω (CB threshold 3 / cooldown 600s) |
| I6 | Daemon warmup loop synchrone bloque worker | 🔴 Bloquant | ✓ Patché P22Ω_WORKER_SAFE_REARM (sem=2, sleep randomized, limit=5) |
| I7 | asyncio.wait_for non-coopératif sur sync CPU | 🟡 P1 | ✓ Renforcé P22Ω_PHASE1_P1_FIXES (E1 Task + cancel + shield + grace) |
| I8 | Cesium 3D données stale si Leaflet rafraîchit | 🟢 P2 | Toggle UI exclusif |

---

## 8 · TABLEAU TRAÇABILITÉ ENGINES × FIXES P22Ω APPLIQUÉS

| Engine | Fix appliqué dans cette session | Date |
|---|---|---|
| `v20_performance_bundle.py` | P22Ω_BACKEND_RESTORE_ULTIME + P22Ω_CORRIDORS_ZONES_STABILISATION + P22Ω_MULTI_FIX_A1/A4 + P22Ω_WORKER_SAFE_REARM + P22Ω_REDIS_HOIST + P22Ω_PHASE1_P1_FIXES (E1) | 2026-05-13 |
| `engine_ia_corridors_organic_omega.py` | P22Ω_MULTI_FIX_A1 + P22Ω_COYOTE_REGISTRY_DECISION + P22Ω_CORRIDORS_DIVERGENCE_INTER_ESPECES | 2026-05-13 |
| `species_presence_mask_omega.py` | P22Ω_COYOTE_REGISTRY_DECISION | 2026-05-13 |
| `organic_corridor_smoother.py` | P22Ω_MULTI_FIX_A3 + P22Ω_COYOTE_REGISTRY_DECISION + P22Ω_CORRIDORS_ZONES_STABILISATION | 2026-05-13 |
| `open_meteo_breaker.py` | P22Ω_PHASE1_P1_FIXES (E2) | 2026-05-13 |
| `fusion_territoire_omega.py` | P22Ω_PHASE1_P1_FIXES (E3) — V30 baseline | 2026-05-13 |
| `fusion_territoire_omega_router.py` | P22Ω_PHASE1_P1_FIXES (E3) — allowed_species + normalize | 2026-05-13 |
| `audit_download_router.py` | P22Ω_INJONCTION_DOCTRINAL_DOWNLOAD (nouveau fichier) | 2026-05-13 |
| `speciesConfig.js` (frontend) | P22Ω_COYOTE_REGISTRY_DECISION | 2026-05-13 |
| `FusionDebugPanel.jsx` (frontend) | P22Ω_COYOTE_REGISTRY_DECISION | 2026-05-13 |
| `LocalCorridorLensPanel.jsx` (frontend) | P22Ω_COYOTE_REGISTRY_DECISION | 2026-05-13 |

---

**FIN ENGINES MATRIX** — PROTOCOLE BCE-4X ULTIME ABSOLU
