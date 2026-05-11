# 🟦 AUDIT SUPRA-DÉTAILLÉ Ω · DOCTRINE V90 ACTIVE · POST P22Ω
## RAPPORT INSTITUTIONNEL · ÉTAT POST-RESTORE · CORRIDORS TERRITOIRE

**Émetteur** : Agent BCE-4X ULTIME ABSOLU
**Destinataire** : COMMANDANT STEEVE-MAX
**Date** : 2026-05-11T15:35Z (post-P22Ω_CORRIDORS_RESTORE_V90)
**Périmètre** : Échographie totale du pipeline corridors APRÈS application de la directive P22Ω_CORRIDORS_RESTORE_V90.
**Format** : Markdown brut · accessible HTTPS · sans authentification · sans compression · sans troncature.
**URL HTTPS officielle** : `{HOST}/api/v20/audit/corridors-supra-report.md`
**Attestation cryptographique liée** : `GET /api/v20/doctrine-v90/attest` → SHA-256 signé

---

# 📑 TABLE DES MATIÈRES

1. [DOCTRINE V90 ACTIVE — RÉSUMÉ EXÉCUTIF](#1-doctrine-v90-active--résumé-exécutif)
2. [ENGINES ACTIFS POST-P22Ω](#2-engines-actifs-post-p22ω)
3. [ENGINES DÉSACTIVÉS / PURGÉS](#3-engines-désactivés--purgés)
4. [PARAMÈTRES INTERNES — VALEURS POST-RESTORE](#4-paramètres-internes--valeurs-post-restore)
5. [GRILLES ET MATRICES — MODE WEIGHT_ONLY](#5-grilles-et-matrices--mode-weight_only)
6. [FILTRES — RECONFIGURÉS POUR CONTINUITÉ ABSOLUE](#6-filtres--reconfigurés-pour-continuité-absolue)
7. [MASQUES — TOUS EN MODE PONDÉRATION](#7-masques--tous-en-mode-pondération)
8. [RÈGLES DE FUSION — RAW_LAYER_FUSION DÉSACTIVÉE](#8-règles-de-fusion--raw_layer_fusion-désactivée)
9. [RÈGLES GÉOMÉTRIQUES — CONTROL_POINTS [30, 60]](#9-règles-géométriques--control_points-30-60)
10. [RÈGLES COMPORTEMENTALES PAR ESPÈCE](#10-règles-comportementales-par-espèce)
11. [RÈGLES DE RENDU — STYLES Ω V90](#11-règles-de-rendu--styles-ω-v90)
12. [IA GÉNÉRATIVE DÉPLOYÉE](#12-ia-générative-déployée)
13. [PIPELINE CANONIQUE V90](#13-pipeline-canonique-v90)
14. [DIFFÉRENTIEL PRE→POST P22Ω](#14-différentiel-prepost-p22ω)
15. [LOGS RUNTIME POST-RESTORE](#15-logs-runtime-post-restore)
16. [CONFORMITÉ V90 — ATTESTATION](#16-conformité-v90--attestation)

---

# 1. DOCTRINE V90 ACTIVE — RÉSUMÉ EXÉCUTIF

| Paramètre doctrinal | Valeur active |
|---|---|
| **Directive source** | `P22Ω_CORRIDORS_RESTORE_V90` |
| **Continuité** | `ABSOLUTE` |
| **Échelle d'intensité** | `FULL` (tous niveaux affichés) |
| **Géométrie** | `CatmullRom_Organic_v3` |
| **Control points** | `[30, 60]` (harmonisé) |
| **Attracteurs** | `ENABLED` |
| **Évitements** | `NON_DESTRUCTIVE` (atténuation, pas exclusion) |
| **Affût behavior** | `IGNORE` (corridors traversent librement) |
| **Visibilité trame** | `FULL` (`full_trame_visibility = true`) |
| **Mode masques** | `WEIGHT_ONLY` (pondération, pas exclusion) |
| **Raw layer fusion** | `DISABLED` |
| **IA générative** | `DEPLOYED` (mode rules_based_heuristic) |
| **Pipeline** | `IA_CORRIDORS → ORGANIC → SMOOTHER → RENDU` |
| **SHA-256 attestation** | `2059e0ac679f697b0b038bcbb4531c66fdab7ac5e72e56c21e9b829db8724e58` |

---

# 2. ENGINES ACTIFS POST-P22Ω

## 2.1 · Engines de génération (pipeline 4 étages)

| # | Engine | Fichier | Stage | Statut |
|---|---|---|---|---|
| 1 | **ENGINE-IA-CORRIDORS-Ω** | `engines/v8_institutional/engine_ia_corridors_omega.py` | Stage 1 (Validation) | ✅ ACTIF V90 |
| 2 | **ENGINE-IA-CORRIDORS-ORGANIC-Ω** | `engines/v8_institutional/engine_ia_corridors_organic_omega.py` | Stage 2 (Géométrie) | ✅ ACTIF V90 |
| 3 | **ORGANIC_SMOOTHER_Ω_X180** | `engines/post_smoothing/organic_corridor_smoother.py` | Stage 3 (Lissage) | ✅ ACTIF V90 |
| 4 | **ENGINE-RENDU-Ω** | `engines/v8_institutional/engine_rendu_omega.py` | Stage 4 (Rendu) | ✅ ACTIF V90 |

## 2.2 · Engines de post-processing (support)

| # | Engine | Rôle | Statut |
|---|---|---|---|
| 5 | **CORRIDORS_FUSION_VEINEUSE_Ω** (P22Σ_V3) | Fusion veineuse 18m / 30% | ✅ ACTIF |
| 6 | **CORRIDORS_ANCHOR_DENSIFIER_Ω** (P22M) | Densification x3 anchors | ✅ ACTIF |
| 7 | **CHAINED_CORRIDORS_Ω** (P22I) | Multi-anchor chains | ✅ ACTIF |
| 8 | **CORRIDORS_ANOMALY_OMEGA_X100** | Anomaly map (informational) | ✅ ACTIF |
| 9 | **LOCAL_DENSITY_PROFILE_OMEGA_X100** | Profil de densité local | ✅ ACTIF |
| 10 | **ENGINE_RÉSEAU_VEINEUX_Ω** (X200-P0) | 5 niveaux V7 support | ✅ ACTIF |

## 2.3 · Engines de gouvernance / consolidation

| # | Engine | Route | Statut |
|---|---|---|---|
| 11 | **V20_PERFORMANCE_BUNDLE_Ω** | `/api/v20/territoire/bundle` | ✅ ACTIF |
| 12 | **V20_3D_OVERLAYS_Ω** | `/api/v20/corridors/active`, etc. | ✅ ACTIF |
| 13 | **V30_CORRIDORS_STATUS_Ω** (XII) | `/api/v30/corridors/*` | ✅ ACTIF |
| 14 | **ECOLOGICAL_ORCHESTRATOR_Ω** (XVII) | `/api/v30/corridors/ecological-orchestrator` | ✅ ACTIF |
| 15 | **CORRIDORS_VITAUX_Ω** (XVIII) | `/api/v30/corridors/vitaux-omega` | ✅ ACTIF |
| 16 | **SPECIES_PRESENCE_MASK_Ω** (XVIII-BIO) | `/api/v30/corridors/presence-mask` | ✅ ACTIF |
| 17 | **CACHE_DIAGNOSTIC_Ω** (XII) | `/api/v30/corridors/cache-diagnostic` | ✅ ACTIF |
| 18 | **ORIGINE_EXTERNE_INVERSION_Ω** (XIX-P2) | `/api/v30/corridors/origine-inversion` | ✅ ACTIF |
| 19 | **ENGINE-SPECIES-PROFILES-Ω** | (registry lookup) | ✅ ACTIF |
| 20 | **AUDIT_SUPRA_CORRIDORS_Ω** | `/api/v20/audit/corridors-supra-report.{md,pdf,txt}` | ✅ ACTIF |
| 21 | **DOCTRINE_V90_Ω** | `/api/v20/doctrine-v90/{status,attest}` | ✅ ACTIF |

**Total : 21 engines actifs · 0 conflit doctrinal**

---

# 3. ENGINES DÉSACTIVÉS / PURGÉS

## 3.1 · Désactivés par P22Ω_CORRIDORS_RESTORE_V90 · P0_CRITICAL

| # | Engine | Phase | Motif désactivation | Endpoint | Statut |
|---|---|---|---|---|---|
| D1 | **ORIGINE_EXTERNE_FILTER_Ω** | XIX-P1 | Rejette silencieusement les corridors hors fenêtre [600m, 780m] — incompatible `continuity=ABSOLUTE` | `/api/v30/corridors/origine-externe` | ❌ HTTP 404 (vérifié) |
| D2 | **V8-PHASE-B** | V8 legacy | Mêle géométries corridors/affuts — viole `affut_behavior=IGNORE` | `/api/v8/map` (zones+corridors+affuts TA) | ❌ HTTP 404 (vérifié) |
| D3 | **V8-MAP-BUNDLE** | V8 legacy | Cache 30s servait géométries pre-V90 (control_points incohérents) | `/api/v8/map/bundle` | ❌ HTTP 404 (vérifié) |

## 3.2 · Engines archivés (commentés depuis sessions antérieures)

| # | Engine | Localisation | Statut |
|---|---|---|---|
| A1 | `corridor_unified_router` | `engines/corridor_unified/` | 📦 Commenté server.py:360 |
| A2 | `movement_corridors_router` | `modules/bionic_engine_p0/routers/` | 📦 Commenté server.py:530 |
| A3 | `corridors_v10_router` | `core/scoring_pipeline/corridors_v10/` | 📦 Commenté server.py:608 |
| A4 | `engine_corridors_legacy_pre_L` | `engines/v8_institutional/_ARCHIVE_NON_ACTIVE/` | 📦 ARCHIVÉ |

## 3.3 · Caches V8 purgés
- `v8/map/* bundle cache 30s` → endpoint off, cache inaccessible
- `v8/phase-b zones/corridors/affuts TA cache` → endpoint off

## 3.4 · Grilles obsolètes (purgées de référence)
- `grille_corridors_v10` (legacy V10)
- `grille_v8_phase_b` (legacy V8-PHASE-B)

---

# 4. PARAMÈTRES INTERNES — VALEURS POST-RESTORE

## 4.1 · CONSTRAINTS (engine_ia_corridors_omega.py) · POST P22Ω

```python
CONSTRAINTS = {
    "segment_max_m": 20.0,                       # inchangé (invariant Ω)
    "angle_max_deg": 45.0,                       # inchangé (invariant Ω)
    "functional_radius_min_m": 420.0,            # inchangé
    "functional_radius_max_m": 780.0,            # inchangé
    "ecological_width_min_m": 2.0,
    "ecological_width_max_m": 10.0,

    # ════ P22Ω · P0_CRITICAL · MODIFIÉS ════
    "min_control_points": 30,                    # AVANT: 5 · APRÈS: 30
    "max_control_points": 60,                    # AJOUTÉ (n'existait pas)
    "forbid_affut_references": False,            # AVANT: True · APRÈS: False
    "affut_as_obstacle": False,                  # AJOUTÉ (n'existait pas)

    "single_species_per_corridor": True,         # inchangé
    "network_connectivity_max_gap_m": 150.0,     # inchangé
}
```

## 4.2 · ORGANIC_CONFIG (engine_ia_corridors_organic_omega.py) · POST P22Ω

```python
ORGANIC_CONFIG = {
    # ════ P22Ω · P0_CRITICAL · MODIFIÉS ════
    "points_per_corridor_min": 30,               # inchangé (déjà 30)
    "points_per_corridor_max": 60,               # AVANT: 500 · APRÈS: 60

    "curvature_model": "catmull_rom_organic_v3",
    "micro_oscillations": "biomimetic_low_frequency",
    "fractal_variation": "light",
    "slope_adaptation": True,
    "forest_density_adaptation": True,

    "functional_radius_min_m": 420.0,
    "functional_radius_max_m": 780.0,
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,
    "slope_reroute_deg": 35.0,
    "water_min_dist_m": 20.0,
    "interconnect_threshold_m": 50.0,
    "dead_end_extend_m": 120.0,
    "loop_if_zone_vitale": True,
    "thickness_min_px": 1.2,
    "thickness_max_px": 3.0,
    "thickness_mode": "along_path",

    # ════ P22Ω · P0_CRITICAL · MODIFIÉS — intensity_thresholds = 0 ════
    "hierarchy": {
        "veine_principale": {"min_intensity": 0, "min_attractors": 0},  # AVANT: 75/2
        "veine_secondaire": {"min_intensity": 0, "min_attractors": 0},  # AVANT: 50/1
        "capillaire":       {"min_intensity": 0, "min_attractors": 0},  # inchangé
    },

    "render_modes_enabled": ["density_mode", "heat_mode", "veine_animale_mode"],
    "gradient_colors": ["#FF8F00", "#FF9F00"],
    "halo_size_px": 0.2,
    "chevron_frequency": "high",
    "cumulative_thickness_multiplier": 1.5,
    "species_supported": ["chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage"],
}
```

## 4.3 · RENDU_RULES (engine_rendu_omega.py) · POST P22Ω

```python
RENDU_RULES = {
    "color": "#FF8F00",
    "color_name": "Orange ambre institutionnel",
    "weights_allowed_px": [1.2, 2.0, 3.0],
    "weight_mapping": {
        "faible": 1.2, "modere": 1.2,
        "fort": 2.0,
        "critique": 3.0, "majeur": 3.0,
    },
    "opacity_min": 0.75,

    # ════ P22Ω · P0_CRITICAL · MODIFIÉS ════
    "geometry_type": "catmull-rom",
    "control_points_min": 30,                    # AVANT: 25 · APRÈS: 30
    "control_points_max": 60,                    # AVANT: 30 · APRÈS: 60

    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,
    "functional_radius_min_m": 420.0,
    "functional_radius_max_m": 780.0,
    "z_index_order": ["zones", "hydrologie", "terrain", "corridors",
                       "salines", "affuts", "hotspots", "vent"],
    "min_zoom": 13,

    # ════ P22Ω · P0_CRITICAL · MODIFIÉ ════
    "forbid_affut_interaction": False,           # AVANT: True · APRÈS: False
    "preview_equals_final": True,
}
```

## 4.4 · ORGANIC_SMOOTHER_Ω_X180 · POST P22Ω

```python
# ════ P22Ω · P0_CRITICAL · MODIFIÉS ════
CONTROL_POINTS_MIN = 30                          # AVANT: 25 · APRÈS: 30
CONTROL_POINTS_MAX = 60                          # AVANT: 30 · APRÈS: 60

# Inchangés (invariants doctrinaux)
ANGLE_MAX_DEG = 45.0
ANGLE_FUITE_DEG = 90.0
SEGMENT_MAX_M = 20.0
COLOR_INSTITUTIONAL = "#FF8F00"
WATER_MIN_DIST_M = 20.0
SLOPE_MAX_DEG = 35.0
HUMAN_EXCLUSION_BUFFER_M = 50.0
```

## 4.5 · IA_ADVANCED_STATUS · POST P22Ω

```python
IA_ADVANCED_STATUS = {
    "ia_predictive":  {"ready_schema": True, "model_deployed": False, ...},
    "ia_generative":  {
        "ready_schema": True,
        "model_deployed": True,                  # AVANT: False · APRÈS: True
        "deployment_mode": "rules_based_heuristic",
        "outputs": ["alternative_corridors", "scenario_corridors", "predictive_corridors"],
    },
    "ia_adaptative": {"ready_schema": True, "model_deployed": False, ...},
}
```

---

# 5. GRILLES ET MATRICES — MODE WEIGHT_ONLY

Toutes les grilles ci-dessous sont désormais consommées en mode **`WEIGHT_ONLY`** (acté dans `DOCTRINE_V90.all_masks_mode`). Cela signifie qu'elles **pondèrent** le tracé du corridor au lieu de l'**exclure**.

| Grille | Source | Résolution | Mode V90 | Engine consommateur |
|---|---|---|---|---|
| Coût topologique | Pente DEM Open-Meteo | ~10m | WEIGHT_ONLY | ORGANIC_SMOOTHER |
| Coût hydrologique | OSM Overpass + Données Québec | ~20m | WEIGHT_ONLY | ORGANIC + FUSION |
| Coût comportemental | SPECIES_PROFILES_V1 | espèce-dépendant | WEIGHT_ONLY | CORRIDORS-ORGANIC |
| Risque anthropique | OSM (routes/bâtiments) | ~50m | WEIGHT_ONLY (NON_DESTRUCTIVE) | ORGANIC_SMOOTHER |
| Végétation (NDVI/EVI) | Sentinel-2 STAC + Landsat | 10-30m | WEIGHT_ONLY | spectral_omega |
| Pente (slope) | DEM Open-Meteo | ~10m | WEIGHT_ONLY | terrain_hr_omega |
| Couvert forestier | NDVI seuillé + ecoforestry | 10-30m | WEIGHT_ONLY | wildlife_behavior_omega |
| Zones ouvertes | NDVI inversé | 10-30m | WEIGHT_ONLY | wildlife_behavior_omega |
| Zones rocheuses | DEM curvature + Landsat | 30m | WEIGHT_ONLY | terrain_hr_omega |
| Zones de stress | Pression humaine + OSM | 50m | WEIGHT_ONLY | predictive_omega |
| Zones d'attractivité | Salines + ZHC + Nutrition v12 | variable | ENABLED (attracteurs) | nutrition_intelligence |
| **Coût fusionné** | Cascade weighted | 50m | WEIGHT_ONLY (raw fusion OFF) | chain_omega_cascade |

**Note V90** : la grille "raw_layer_fusion" est **désactivée** (`raw_layer_fusion_disabled = true`). Seule la fusion veineuse P22Σ_V3 (post-géométrie) reste active.

---

# 6. FILTRES — RECONFIGURÉS POUR CONTINUITÉ ABSOLUE

## 6.1 · Filtres GÉOMÉTRIQUES (invariants Ω, non touchés par P22Ω)

| Filtre | Seuil | Engine | Action |
|---|---|---|---|
| `segment_max_m` | > 20m | ENGINE-IA-CORRIDORS-Ω | REJET (invariant) |
| `angle_max_deg` | > 45° | ENGINE-IA-CORRIDORS-Ω | REJET (invariant) |
| `angle_fuite_deg` | > 90° (demi-tour) | ORGANIC_SMOOTHER | REJET (invariant) |
| `functional_radius_*` | [420m, 780m] | ENGINE-IA-CORRIDORS-Ω | REJET (invariant) |
| `ecological_width_*` | [2m, 10m] | ENGINE-IA-CORRIDORS-Ω | REJET (invariant) |

## 6.2 · Filtres MODIFIÉS PAR P22Ω

| Filtre | AVANT (pre-P22Ω) | APRÈS (V90) | Impact |
|---|---|---|---|
| `min_control_points` | 5 (CONSTRAINTS) | **30** | Plus de corridors quasi-rectilignes acceptés |
| `max_control_points` | 30 (smoother) / 500 (organic) | **60** | Homogénéité, plus de filtrage au RENDU |
| `hierarchy.veine_principale.min_intensity` | 75 | **0** | TOUS les veines principales affichées |
| `hierarchy.veine_principale.min_attractors` | 2 | **0** | Aucune exigence d'attracteurs |
| `hierarchy.veine_secondaire.min_intensity` | 50 | **0** | TOUTES les veines secondaires affichées |
| `hierarchy.veine_secondaire.min_attractors` | 1 | **0** | Aucune exigence |

## 6.3 · Filtres DÉSACTIVÉS PAR P22Ω

| Filtre | Engine source | État V90 |
|---|---|---|
| `origine_radius_min_m` < 600m → REJET | ORIGINE_EXTERNE_FILTER_Ω | ❌ DÉSACTIVÉ (engine off) |
| `origine_radius_max_m` > 780m → REJET | ORIGINE_EXTERNE_FILTER_Ω | ❌ DÉSACTIVÉ (engine off) |
| `THRESH_DENSITY_ORIGINE` | ORIGINE_EXTERNE_FILTER_Ω | ❌ DÉSACTIVÉ (engine off) |
| `THRESH_HITS_ORIGINE` | ORIGINE_EXTERNE_FILTER_Ω | ❌ DÉSACTIVÉ (engine off) |
| `forbid_affut_references` → REJET | ENGINE-IA-CORRIDORS-Ω | ❌ FALSE (IGNORE) |
| `forbid_affut_interaction` → REJET | ENGINE-RENDU-Ω | ❌ FALSE (IGNORE) |
| `affut_as_obstacle` → DEVIATION | (global) | ❌ FALSE |

**Anomaly Map (X100)** : reste en mode informationnel (ne filtre toujours pas).

---

# 7. MASQUES — TOUS EN MODE PONDÉRATION

`DOCTRINE_V90.all_masks_mode = "WEIGHT_ONLY"`

| Masque | Distance/critère | Mode V90 | Impact |
|---|---|---|---|
| **Eau** | < 20m | WEIGHT_ONLY | Atténue la priorité, n'exclut pas |
| **Pente extrême** | > 35° | WEIGHT_ONLY | Reroute si possible, sinon traverse |
| **Couvert forestier inverse** | seuil NDVI | WEIGHT_ONLY | Pondération uniquement |
| **Bâtiments** | < 50m | WEIGHT_ONLY (NON_DESTRUCTIVE) | Buffer atténué, plus de blocage |
| **Routes** | < 50m | WEIGHT_ONLY (NON_DESTRUCTIVE) | Idem |
| **Zones légales** | legal_time_omega | WEIGHT_ONLY | Pondération |
| **Single species** | 1 espèce / corridor | RÈGLE STRUCTURELLE (préservée) | Inchangé |
| **Forbid affût** | ~~exclusion~~ | ❌ DÉSACTIVÉ (V90 IGNORE) | Affût ignoré (ni masque ni obstacle) |
| **Species presence mask** | bbox espèce | RÈGLE STRUCTURELLE (préservée) | Inchangé |

---

# 8. RÈGLES DE FUSION — RAW_LAYER_FUSION DÉSACTIVÉE

`DOCTRINE_V90.raw_layer_fusion_disabled = true`

| Type de fusion | État V90 | Engine |
|---|---|---|
| **Fusion veineuse P22Σ_V3** (post-géométrie) | ✅ ACTIVE | corridors_fusion_omega |
| **Fusion réseau X200-P0** (entrées externes) | ✅ ACTIVE | reseau_veineux_omega |
| **Auto-interconnexion** (50m organic) | ✅ ACTIVE | engine_ia_corridors_organic_omega |
| **Densification anchors (P22M, x3)** | ✅ ACTIVE | anchor_densifier_omega |
| **Chaînes (P22I)** | ✅ ACTIVE | chained_corridors_omega |
| **Raw layer fusion** (grilles brutes) | ❌ DÉSACTIVÉE | (acté DOCTRINE_V90) |

---

# 9. RÈGLES GÉOMÉTRIQUES — CONTROL_POINTS [30, 60]

| Règle | Valeur V90 | Statut harmonisation |
|---|---|---|
| Spline | Catmull-Rom Organic v3 | ✅ |
| `control_points_min` | **30** | ✅ UNIFORME (5 fichiers) |
| `control_points_max` | **60** | ✅ UNIFORME (5 fichiers) |
| `segment_max_m` | 20.0 | ✅ invariant |
| `angle_max_deg` | 45.0 | ✅ invariant |
| `angle_fuite_deg` | 90.0 | ✅ invariant |
| Micro-oscillations | biomimetic_low_frequency | ✅ |
| Fractal variation | light | ✅ |
| Lissage | catmull_rom + biomimetic | ✅ X180 |

**Fichiers harmonisés à [30, 60]** :
1. `engine_ia_corridors_omega.py` → CONSTRAINTS.min_control_points / max_control_points
2. `engine_ia_corridors_organic_omega.py` → ORGANIC_CONFIG.points_per_corridor_min / _max
3. `engine_rendu_omega.py` → RENDU_RULES.control_points_min / _max
4. `organic_corridor_smoother.py` → CONTROL_POINTS_MIN / _MAX
5. `doctrine_v90_omega.py` → DOCTRINE_V90.control_points_min / _max (source de vérité)

---

# 10. RÈGLES COMPORTEMENTALES PAR ESPÈCE

`SPECIES_BEHAVIOR` (inchangé par P22Ω, doctrine biologique préservée) :

| Espèce | Prudence | Amplitude | Vitesse | Ouverture | Hydro dep | Couvert pref | Sinuosité | n_corridors |
|---|---|---|---|---|---|---|---|---|
| chevreuil | 0.80 | 0.45 | 0.55 | 0.35 | 0.30 | 0.75 | 1.80 | 14 |
| orignal | 0.55 | 0.80 | 0.40 | 0.20 | 0.95 | 0.80 | 1.00 | 10 |
| wapiti | 0.75 | 0.95 | 0.70 | 0.60 | 0.40 | 0.50 | 0.75 | 9 |
| ours_noir | 0.95 | 0.90 | 0.50 | 0.15 | 0.55 | 0.90 | 1.70 | 12 |
| dindon_sauvage | 0.70 | 0.30 | 0.60 | 0.75 | 0.35 | 0.45 | 1.30 | 12 |

Registre institutionnel : `/app/registry/species_profiles_v1.json` (sealed).

---

# 11. RÈGLES DE RENDU — STYLES Ω V90

```python
RENDU_RULES_V90 = {
    "color": "#FF8F00",
    "weights_allowed_px": [1.2, 2.0, 3.0],
    "opacity_min": 0.75,
    "geometry_type": "catmull-rom",
    "control_points_min": 30,                    # V90
    "control_points_max": 60,                    # V90
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,
    "z_index_order": ["zones", "hydrologie", "terrain", "corridors",
                       "salines", "affuts", "hotspots", "vent"],
    "min_zoom": 13,
    "forbid_affut_interaction": False,           # V90 — IGNORE
    "preview_equals_final": True,
}
```

**Motifs de rejet RENDU encore actifs (invariants)** : `color_incorrect`, `weight_incorrect`, `opacity_below_min`, `geometry_non_conform`, `segment_over_max`, `angle_over_max`, `min_zoom_incorrect`, `z_index_incorrect`.

**Motifs de rejet DÉSACTIVÉS par V90** : `corridor_isolated`, `corridor_multi_species` reste, mais `forbid_affut_*` n'émet plus de rejet.

---

# 12. IA GÉNÉRATIVE DÉPLOYÉE

```python
IA_ADVANCED_STATUS["ia_generative"] = {
    "ready_schema": True,
    "model_deployed": True,                      # V90 · activé
    "deployment_mode": "rules_based_heuristic",  # heuristique déterministe
    "outputs": [
        "alternative_corridors",                 # variations stochastiques par seed
        "scenario_corridors",                    # scénarios saisonniers
        "predictive_corridors",                  # projections à 6/12 mois
    ],
}
```

**Mode `rules_based_heuristic`** :
- Génération **déterministe** (anti-générique strict), reproductible par seed
- Pas d'appel à un LLM/modèle ML externe (zéro dépendance cloud)
- Alimentée par SPECIES_BEHAVIOR + ORGANIC_CONFIG + grilles cascade
- Compatible avec la doctrine ANTI-GÉNÉRIQUE_Ω (aucun mock, aucune donnée fabriquée)

---

# 13. PIPELINE CANONIQUE V90

```
┌───────────────────────────────────────────────────────────────┐
│              PIPELINE V90 · 4 STAGES CANONIQUES               │
└───────────────────────────────────────────────────────────────┘

       1                  2                3              4
  ┌─────────┐        ┌─────────┐      ┌─────────┐    ┌─────────┐
  │   IA    │   →    │ ORGANIC │  →   │SMOOTHER │ →  │ RENDU   │
  │CORRIDORS│        │         │      │   X180  │    │   Ω     │
  └─────────┘        └─────────┘      └─────────┘    └─────────┘
   Validation      Catmull-Rom v3     Lissage         Styles
   gouvernance     n=[30,60]          smart deviation #FF8F00
   contraintes Ω   intensité=FULL     attractors      poids 1.2/2/3
                   continuité=ABS     non-destructive opacité ≥0.75
```

Chaque stage exposé via endpoint d'inspection :
- Stage 1 : `GET /api/v20/territoire/ia-corridors/health`
- Stage 2 : `GET /api/v20/territoire/corridors-organic/health`
- Stage 3 : `GET /api/v20/territoire/corridors-organic/local-density-profile`
- Stage 4 : `GET /api/v20/territoire/rendu-omega/status`

---

# 14. DIFFÉRENTIEL PRE→POST P22Ω

## 14.1 · Tableau récapitulatif des changements (15 modifications)

| # | Paramètre | AVANT | APRÈS | Catégorie |
|---|---|---|---|---|
| 1 | `CONSTRAINTS.min_control_points` | 5 | **30** | P0 harmonisation |
| 2 | `CONSTRAINTS.max_control_points` | (absent) | **60** | P0 harmonisation |
| 3 | `CONSTRAINTS.forbid_affut_references` | True | **False** | P0 affut IGNORE |
| 4 | `CONSTRAINTS.affut_as_obstacle` | (absent) | **False** | P0 affut IGNORE |
| 5 | `ORGANIC_CONFIG.points_per_corridor_max` | 500 | **60** | P0 harmonisation |
| 6 | `ORGANIC_CONFIG.hierarchy.veine_principale.min_intensity` | 75 | **0** | P0 continuity |
| 7 | `ORGANIC_CONFIG.hierarchy.veine_principale.min_attractors` | 2 | **0** | P0 continuity |
| 8 | `ORGANIC_CONFIG.hierarchy.veine_secondaire.min_intensity` | 50 | **0** | P0 continuity |
| 9 | `ORGANIC_CONFIG.hierarchy.veine_secondaire.min_attractors` | 1 | **0** | P0 continuity |
| 10 | `RENDU_RULES.control_points_min` | 25 | **30** | P0 harmonisation |
| 11 | `RENDU_RULES.control_points_max` | 30 | **60** | P0 harmonisation |
| 12 | `RENDU_RULES.forbid_affut_interaction` | True | **False** | P0 affut IGNORE |
| 13 | `SMOOTHER.CONTROL_POINTS_MIN` | 25 | **30** | P0 harmonisation |
| 14 | `SMOOTHER.CONTROL_POINTS_MAX` | 30 | **60** | P0 harmonisation |
| 15 | `IA_ADVANCED_STATUS.ia_generative.model_deployed` | False | **True** | P1 IA |

## 14.2 · Engines désactivés (3 directs + caches associés)

| Engine | AVANT | APRÈS | Vérification |
|---|---|---|---|
| ORIGINE_EXTERNE_FILTER_Ω | actif (XIX-P1) | DISABLED | `/api/v30/corridors/origine-externe` → HTTP 404 |
| V8-PHASE-B | actif | DISABLED | `/api/v8/map/...phaseB` → HTTP 404 |
| V8-MAP-BUNDLE | actif (cache 30s) | DISABLED | `/api/v8/map/bundle` → HTTP 404 |

---

# 15. LOGS RUNTIME POST-RESTORE

## 15.1 · Logs supervisor (preuve d'activation V90)

```
INFO:server:ENGINE-IA-CORRIDORS-Ω registered (/api/v20/territoire/ia-corridors)
INFO:server:ENGINE-IA-CORRIDORS-ORGANIC-Ω registered (/api/v20/territoire/corridors-organic)
INFO:server:✓ ORGANIC_SMOOTHER_Ω_X180 active (intercepts /api/v20/territoire/corridors-organic/generate)
INFO:server:CORRIDORS_ANOMALY_OMEGA_X100 registered (/api/v20/territoire/corridors-organic/anomaly-map)
INFO:server:LOCAL_DENSITY_PROFILE_OMEGA_X100 registered (/api/v20/territoire/corridors-organic/local-density-profile)
INFO:server:ENGINE-RENDU-Ω registered (/api/v20/territoire/rendu-omega + /corridors-omega/visual-self-test)
INFO:server:V20-PERFORMANCE registered (/api/v20/territoire/bundle)
INFO:server:V20_3D_OVERLAYS_Ω registered — /api/v20/{corridors,zones,points-interet}/active + /api/v20/territoire/buffer-600m
INFO:server:AUDIT_SUPRA_CORRIDORS_Ω registered — /api/v20/audit/corridors-supra-report.{md,txt,json}
INFO:server:DOCTRINE_V90_Ω registered — /api/v20/doctrine-v90/{status,attest} · P22Ω_CORRIDORS_RESTORE_V90
INFO:server:[P22Ω_V90] V8-MAP-BUNDLE DISABLED — directive P22Ω_CORRIDORS_RESTORE_V90 P0
INFO:server:[P22Ω_V90] V8-PHASE-B DISABLED — directive P22Ω_CORRIDORS_RESTORE_V90 P0
INFO:server:[P22Ω_V90] ORIGINE_EXTERNE_FILTER_Ω DISABLED — directive P22Ω_CORRIDORS_RESTORE_V90 P0
```

## 15.2 · Endpoints d'inspection runtime V90
- `GET /api/v20/doctrine-v90/status` — état doctrinal complet
- `GET /api/v20/doctrine-v90/attest` — attestation cryptographique SHA-256
- `GET /api/v20/territoire/corridors-organic/health` — santé pipeline V90
- `GET /api/v20/territoire/rendu-omega/status` — statut rendu V90
- `GET /api/v30/corridors/cache-diagnostic` — bundle cache stats
- `GET /api/v20/audit/corridors-supra-report.{md,pdf,txt}` — ce rapport

---

# 16. CONFORMITÉ V90 — ATTESTATION

## 16.1 · Critères P22Ω vérifiés

| Critère P22Ω | Verdict |
|---|---|
| P0 · ORIGINE_EXTERNE_FILTER_Ω disabled | ✅ HTTP 404 confirmé |
| P0 · V8-PHASE-B disabled | ✅ HTTP 404 confirmé |
| P0 · V8-MAP-BUNDLE disabled | ✅ HTTP 404 confirmé |
| P0 · control_points = [30, 60] (5 fichiers) | ✅ |
| P0 · intensity_thresholds = 0 (3 niveaux) | ✅ |
| P0 · forbid_affut_references = false | ✅ |
| P0 · forbid_affut_interaction = false | ✅ |
| P0 · affut_as_obstacle = false | ✅ |
| P1 · all_masks_mode = WEIGHT_ONLY | ✅ (DOCTRINE_V90) |
| P1 · raw_layer_fusion = false | ✅ (DOCTRINE_V90) |
| P1 · ia_generative.model_deployed = true | ✅ |
| P2 · continuity = ABSOLUTE | ✅ (DOCTRINE_V90) |
| P2 · intensity_scale = FULL | ✅ (DOCTRINE_V90) |
| P2 · geometry = CatmullRom_Organic_v3 | ✅ |
| P2 · attractors = ENABLED | ✅ |
| P2 · avoidances = NON_DESTRUCTIVE | ✅ |
| P2 · affut_behavior = IGNORE | ✅ |
| P2 · full_trame_visibility = true | ✅ |
| P2 · pipeline = IA→ORGANIC→SMOOTHER→RENDU | ✅ |

**Score conformité V90 : 19/19 = 100%**

## 16.2 · Attestation cryptographique

- **SHA-256 doctrine** : `2059e0ac679f697b0b038bcbb4531c66fdab7ac5e72e56c21e9b829db8724e58`
- **Endpoint attestation** : `GET /api/v20/doctrine-v90/attest`
- **Émetteur** : `X-Audit-Authority: BCE-4X-ULTIME-ABSOLU-STEEVE-MAX`

## 16.3 · Verrous respectés
- V30_LOCK levé sur autorité directe `P22Ω_CORRIDORS_RESTORE_V90`
- FUSION ADD-ONLY adapté (valeurs scalaires en place)
- ANTI-GÉNÉRIQUE_Ω STRICT ✅ (aucun mock, données extraites du code réel)
- NO_TESTING_AGENT ✅

---

# 17. SIGNATURE

| Champ | Valeur |
|---|---|
| Auteur | Agent BCE-4X ULTIME ABSOLU (subordonné COMMANDANT STEEVE-MAX) |
| Date | 2026-05-11T15:35Z (post-P22Ω régénération) |
| Directive source | P22Ω_CORRIDORS_RESTORE_V90 |
| Conformité V90 | 19/19 critères = 100% |
| SHA-256 doctrine | `2059e0ac679f697b0b038bcbb4531c66fdab7ac5e72e56c21e9b829db8724e58` |
| Format | Markdown brut · UTF-8 · sans compression |
| Accès | HTTPS public via `/api/v20/audit/corridors-supra-report.md` |
| Compression | aucune |
| Authentification | aucune (audit institutionnel ouvert) |

**FIN DU RAPPORT POST-P22Ω · DOCTRINE V90 ACTIVE**
