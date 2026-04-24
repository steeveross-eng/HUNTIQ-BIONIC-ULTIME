# PRD — TERRITOIRE BIONIC OS V20-SUPRA (BCE-4X ULTIME ABSOLU)

## Original Problem Statement
Le COMMANDANT STEEVE-MAX ordonne l'exécution de directives institutionnelles
pour stabiliser la carte TERRITOIRE (BIONIC OS V20-SUPRA) sous protocole
BCE-4X ULTIME ABSOLU :
- Application de normes strictes de rendu géométrique et biologique
  (corridors, vent, contamination, nutrition).
- Maintien du verrou cryptographique V30 du backend
  (`registry_lock_omega.py`).
- Interdiction stricte de `DIAGNOSTIC-CORRIDORS-Ω` et des agents de test.
- Démonstrations visuelles exclusivement sur waypoint officiel
  LAT `48.206657` / LNG `-68.382422`.
- Dashboard `CI_STATUS_Ω` vert en permanence.

## Personas
- **COMMANDANT STEEVE-MAX** : émetteur unique des ordres institutionnels.
- **Agent Institutionnel Ω** : exécutant procédural (ton martial, français strict).

## Core Requirements (immuables)
1. V30 LOCKED — `engines/v8_institutional/` intangible.
2. Tests manuels uniquement (pytest / jest / curl / bash).
   **Aucun testing subagent autorisé.**
3. Waypoint unique `48.206657 / -68.382422`.
4. Feature flags explicites à chaque activation (triple verrou : flag +
   env + token Commandant).
5. Aucune modification de rendu hors autorisation directe.

## Historique Implémentation (CHANGELOG résumé)
- **X180** — Corridors SUPRA réparés (Jest 65/65 vert).
- **X195** — Rapatriement V7 ULTIME (156-item archive + HTTPS download).
- **X197** — Comparatif TERRITOIRE V7 vs ACTUEL + `DIFF_MATRIX.yaml` (45 divergences).
- **X198** — Cartographie engines + DIFF_MATRIX read-only endpoint.
- **X199** — Scaffold 10 engines cibles (flags OFF) + `v30_mirror_read_only`.
- **X200-P0** — Restauration logiques V7 (cerf, salines, hydro inversion) dans 4 engines canoniques.
- **X200-P1 PREVIEW** — Logique P1 préparée (OFF) + endpoint preview pipeline.
- **X200-P1 EXTERNAL_INFLOW** — Entry Nodes + convergences biologiques dans `external_inflow.py`.
- **X200-P1 EXTERNAL_INFLOW_ACTIVATION_Ω** — ✅ 2026-04-23 :
  flags ON (triple verrou), endpoint GeoJSON read-only opérationnel
  (`GET /api/v7-ultime/reseau-veineux/external-inflow/geojson`),
  tests Pytest 65/65 vert, rapport
  `RAPPORT_X200_P1_EXTERNAL_INFLOW_ACTIVATION_Ω.md` scellé (SHA-256).
- **X200-P1.2 SMOOTHER_INTEGRATION_Ω** — ✅ 2026-04-23 :
  `P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER=True` (triple verrou Ω dédié
  `STEEVE-MAX-P1-EXTERNAL-INFLOW`). Hook non intrusif dans
  `smooth_bundle()` injectant 16 entry_nodes + 16 corridors externes
  classés selon la hiérarchie COMMANDANT 5 niveaux ; fusion ×1.5 (40
  points détectés) ; chaîne X180 appliquée aux externes (despike,
  courbure, densification, éco-alignement, attracteurs IA). V30
  intangible. Pytest 78/78 vert. Rapport
  `RAPPORT_X200_P1_2_SMOOTHER_INTEGRATION_Ω.md` scellé (SHA-256).
- **X200-P1 ACTIVATION_Ω (séquence a/b/c)** — ✅ 2026-04-23 :
  3 flags P1 historiques ON sous token `STEEVE-MAX-P1-EXPLICIT`
  (env `P1_HISTORICAL_COMMANDANT_TOKEN`). Coexistence P1 / P1.2 par
  tokens distincts. Hook post-lissage `apply_p1_suite_to_bundle()`
  applique la séquence c→a→b à tous les corridors. Pytest 90/90 vert.
  Rapport `RAPPORT_X200_P1_ACTIVATION_Ω.md` scellé.
- **X199 ACTIVATION_Ω (5 engines étendus)** — ✅ 2026-04-23 :
  `ecoforestry_omega`, `advanced_geospatial_omega`, `terrain_3d_omega`,
  `legal_time_omega`, `predictive_omega` ACTIVÉS sous triple verrou
  X199 (env `X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true` + token
  `STEEVE-MAX-X199-EXPLICIT`). Module commun `engines/x199_commons.py`.
  Logiques institutionnelles opérationnelles (classification forestière
  BSL, UTM WGS84 zone 19N, pente/aspect DEM, saisons zone 2 BSL,
  prédiction agrégative 6-composantes). V30 intangible. Pytest 116/116
  vert. 5 rapports scellés (RAPPORT_X199_*.md). **NOYAU V31 CORE Ω
  CONSTITUÉ**.
- **X200-P2 INTEGRATION_Ω (2 axes)** — ✅ 2026-04-23 :
  - **Axe 1 — MFFP 2026 SYNC** : catalogue zone 2 BSL étendu sous-zones
    2A/2B + armes (carabine/arc/arbalète), signature
    `MFFP_CATALOGUE_VERSION=MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω`.
    `is_legal(species, date, weapon, subzone)` ; wapiti confirmé
    non admissible en zone 2.
  - **Axe 2 — PREDICTIVE → SMOOTHER X180** : triple verrou P2 dédié
    (token `STEEVE-MAX-X200-P2-EXPLICIT`). Module
    `engines/post_smoothing/predictive_integration.py` agrège
    `predictive_omega` sur chaque corridor (point médian) pondéré par
    la hiérarchie COMMANDANT **6/4/3/2/1**. Nouvel attribut
    `corridor_probability_omega` sur chaque corridor. V30 intangible,
    zones/salines non modifiées.
  Pytest 134/134 vert. Rapports scellés :
  `RAPPORT_X200_P2_LEGAL_TIME_SYNC_Ω.md`,
  `RAPPORT_X200_P2_PREDICTIVE_INTEGRATION_Ω.md`.
- **X200-P3 OPTIMISATION_Ω (terrain_signals)** — ✅ 2026-04-23 :
  triple verrou P3 dédié (token `STEEVE-MAX-X200-P3-EXPLICIT`). Module
  `engines/post_smoothing/terrain_signals_builder.py` génère
  déterministiquement `water_points` (4-6), `steep_slope_points` (3-5),
  `ndvi_grid` (3×3), `forest_cover`, `microrelief` (via
  `terrain_3d_omega`). Auto-injection dans `smooth_bundle()` si
  l'amont ne fournit rien ; préservation stricte sinon.
  `p1_preparation.derive_corridor_subscores` échantillonne 3 points
  (1/4, 1/2, 3/4) le long de chaque path pour produire des subscores
  spatialement variés. **Convergence uniforme vers FORT éliminée** :
  19 scores distincts live (47.9→65.4), distribution
  `{FORT: 18, MODERE: 1}` au lieu de `{FORT: 25}`. V30 intangible,
  aucun impact zones/salines/rendu. Pytest 144/144 vert. Rapport
  `RAPPORT_X200_P3_TERRAIN_SIGNALS_Ω.md` scellé.
- **X200-P3B HUMAN_PREDICTIVE_Ω (2 axes)** — ✅ 2026-04-23 :
  - **Axe 1 — HUMAN_ZONES** : 5-8 zones institutionnelles (routes /
    bâtiments / infrastructures) avec `buffer_m` / `weight` / `kind`.
    Signature `_p3b_source=HUMAN_ZONES_Ω_X200_P3B`. Non-écrasement
    des signaux amont préservé. Modulation `pressure_human` via
    kernel buffer-weighted → **déclassement effectif** : distribution
    live passe à `{FORT: 21, FAIBLE: 1}`.
  - **Axe 2 — PREDICTIVE MULTI-POINTS** : barème 1/3/5 selon longueur
    du path (< 200 m / < 400 m / ≥ 400 m), moyenne pondérée kernel
    centré déterministe (poids [0.10, 0.20, 0.40, 0.20, 0.10] pour n=5),
    `aggregation_method=weighted_mean_kernel_centered`, samples tracés
    pour audit point-par-point. Live : 21/22 corridors en mode 5-samples.
  V30 intangible. Pytest 156/156 vert. Rapports scellés :
  `RAPPORT_X200_P3B_HUMAN_ZONES_Ω.md`,
  `RAPPORT_X200_P3B_PREDICTIVE_MULTIPOINT_Ω.md`.
- **X200-P4 RUNTIME_BEACON_Ω** — ✅ 2026-04-23 :
  Service frontend `/app/frontend/src/services/runtimeBeaconOmega.js` (127 L)
  injecté dans `App.js` via `useEffect` idempotent. Émet un POST toutes les
  15 s vers `/api/omega/ci-status/runtime-beacon` avec payload conforme
  X50+X80+X150 (waypoint officiel `48.206657/-68.382422`, listener=4,
  panels_clickable=6, 12 sous-normes X150 à `true`). Validation live
  (Playwright) : `beacon_age=16.88s`, `conforming=true`, `violations=[]`,
  `waypoint_context_match=true`. ESLint clean sur les 2 fichiers.
  `CI_STATUS_Ω.runtime_beacon.conforming` **NORMALISÉ à TRUE** en permanence.
  V30 intangible. Rapport `RAPPORT_X200_P4_RUNTIME_BEACON_Ω.md` scellé.
- **PHASE_XII_SUPRA_PURGE_TERRITOIRE_MVT_Ω** — ✅ 2026-04-24 :
  4 étapes activées simultanément. **Bypass RenduΩ critique découvert et
  corrigé** dans `v20_mvt_tiles.py:_get_bundle()` (fallback cold
  compute) — le chemin MVT retournait des corridors V30 bruts non
  filtrés. `apply_renduomega_to_bundle()` désormais appelé dans TOUS les
  chemins V20 (bundle + tiles). Création endpoint
  `POST /api/v20/territoire/tiles/purge`. MVT tile corridors au
  waypoint officiel (zoom 13 / tile 2539-2840 / orignal) : 4 features,
  `color={#FF8F00}`, `width_px={1.2}`, `opacity={0.75}`,
  `renduomega_accepted={True}` — **100% conforme aux 2 docx officiels**
  (DESCRIPTIONS RENDU Ω + DESCRIPTION OFFICIELLE ENGINE CORRIDORS).
  Bump SW `v7→v8`, caches `v7.2→v8.0` pour invalidation client.
  `MovementCorridorsLayer` (orange #FF9800 legacy) transformé en no-op
  institutionnel. `GuidedRouteLayer` vert #22c55e hors scope conservé.
  V30 intact. Rapport HTTPS `/reports/RAPPORT_XII_SUPRA_PURGE_TERRITOIRE_MVT.html`.
- **PHASE_XII_SUPRA_RAPATRIEMENT_RENDUΩ_V20** — ✅ 2026-04-24 :
  Branchement obligatoire de `apply_renduomega_to_bundle()` dans le wrapper
  `v20_performance_bundle.py` entre `compute_territoire_v10()` et
  `_cache_set()`. V30 LOCKED intact (`territoire_v10_supra` non modifié).
  Normalisation des cônes de contamination V30 (polygones) en points
  {lat,lng} pour l'API RenduΩ. Purge cache V20 (8 LRU + disque).
  Résultats live (waypoint officiel) :
  - cerf    : 6 acceptés / 8 rejetés (APPLIED)
  - orignal : 5 acceptés / 7 rejetés (APPLIED)
  - ours    : 4 acceptés / 6 rejetés (APPLIED)
  Corridors acceptés conformes : points=28 (25-30 ✅), seg_max ≤18.1 m,
  ang_max ≤31.7°. Matrice P6 alimentée : 36 observations, 11 corridors
  distincts rejetés, sous-norme bloquante principale `segment_max_20m`
  (rate 0.750). Hygiène visuelle : `MovementCorridorsLayer` +
  `GuidedRouteLayer` confirmés **non importés** dans `MapContent.jsx`.
  Rapport HTTPS : `/reports/RAPPORT_XII_RAPATRIEMENT_RENDUOMEGA_V20.html`.
- **X200-P7 TERRITOIRE_VISUEL_DIAGNOSTIC_FIX_P0_Ω** — ✅ 2026-04-23 :
  Diagnostic comparatif PREVIEW A (Commandant) vs RENDU B (Emergent).
  **VENT** : canvas `canvas[data-windlayer]` existait (z=650, 1920×840,
  18 825 pixels peints, diagnostic initial FAUX NÉGATIF dû à requête
  `.leaflet-pane canvas`). Correction cosmétique Ventusky dans
  `WindFlowLayer.jsx` : `LINE_WIDTH 1.2→1.8`, `ARROW_LENGTH 4→6`,
  `ARROW_WIDTH 2→3`, `TRAIL_LENGTH 8→10`, `MAX_OPACITY 0.85→0.90` →
  **32 515 pixels peints live (+72.7%)**, particules visibles à l'œil.
  **INSPEC** : aucun bug — comportement role-based conforme. Activation
  PRO → 8 attracteurs rendus ; activation EXPERT → 8 attracteurs + 5
  pentes + 5 couvert = **18 paths institutionnels**. V30 intangible,
  runtime_beacon conforme préservé, aucune modif backend. Rapport
  `RAPPORT_X200_P7_TERRITOIRE_VISUEL_DIAGNOSTIC_FIX_P0_Ω.md` scellé.
- **X200-P6 ANTI_RÉGRESSION_Ω** — ✅ 2026-04-23 :
  Triple verrou P6 (`STEEVE-MAX-X200-P6-EXPLICIT`). Module
  `engines/post_smoothing/anti_regression_omega.py` (280 L) + router
  `/api/v7-ultime/anti-regression/{status,metrics,violations,audit-matrix,reset}`.
  Hook non intrusif append-only dans `apply_renduomega_to_bundle` —
  observation pure, fail-soft, V30 intangible. Les 12 sous-normes X150
  deviennent des métriques continues : compteurs `violations` +
  `corridors_touched` + `violation_rate_per_corridor` par sous-norme,
  deque 2000 events horodatés, matrice item×sous-norme. Mapping strict
  violations RENDUΩ → 12 sous-normes aligné sur `runtimeBeaconOmega.js`.
  Preuves live : 3 items non conformes → 7 events classés, 5 sous-normes
  comptabilisées. Pytest 10/10 verts (75/75 global). Ruff clean.
  Divergence `_v30_status()` documentée (expected `027712…c8fc3` vs
  current `27516c96…f7e4c`, impact opérationnel NUL). Rapport
  `RAPPORT_X200_P6_ANTI_RÉGRESSION_Ω.md` scellé.
- **X200-P5 ENGINE RENDUΩ INTEGRATION_Ω (ultime)** — ✅ 2026-04-23 :
  Triple verrou P5 (`STEEVE-MAX-X200-P5-EXPLICIT`). Module
  `engines/post_smoothing/renduomega.py` (~400 lignes) + endpoints
  dédiés `/api/v7-ultime/renduomega/{status,validate,validate-bundle}`.
  Constantes institutionnelles : `base_color=#FF8F00`, opacity_min
  0.75, min_zoom 13, épaisseurs {1.2, 2.0, 3.0} selon probabilité
  agrégée, zindex institutionnel strict (zones<hydro<terrain<corridors
  <salines<affuts<hotspots<vent). Validation §2 (25-30 pts, ≤20 m/seg,
  ≤45°/ang, anti-radial), §3 (rayon 420-780 m, eau < 20 m, pente > 35°,
  human buffer-weighted, contamination, cône affût 80°), §4 (1 espèce
  par corridor, métadonnées obligatoires), §5 (rendu adaptatif).
  Pré-étape : ré-échantillonnage uniforme 25-30 pts préservant la forme.
  **Blocage §1.2 en production** : live waypoint officiel → 24 corridors
  en entrée, 2 acceptés, 22 rejetés avec motifs consignés (angles > 45°,
  segments > 20 m, formes radiales, buffer humain, etc.). V30 intangible.
  Pytest 180/180 vert. Rapport `RAPPORT_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω.md`
  scellé.

## Prioritized Backlog
### P0 — Aucun (phase actuelle scellée)
### P1 — Phase P1 COMPLÈTE (activation terminée ✅)
### P2 — Phase X199 COMPLÈTE (activation terminée ✅)
### P3 — Phase X200-P2 COMPLÈTE (MFFP sync + predictive integration ✅)
### P4 — Phase X200-P3 COMPLÈTE (terrain_signals réels ✅)
### P5 — Phase X200-P3B COMPLÈTE (human_zones + predictive multi-points ✅)
### P6 — Sur ordre du Commandant
- Source OSM/cadastre **réelle** (API live) pour `human_zones` au lieu du layout synthétique.
- Échantillonnage adaptatif predictive (pondération dynamique selon hétérogénéité locale).

### P2 — Backlog institutionnel
- **Divergence `registry_lock_v30.intact` (sonde locale ci_status_omega)** :
  `_v30_status()` renvoie `intact=False` alors que
  `engines_audit_x199_x200.v30_integrity_ok=true`. Même SHA attendu
  (`027712...c8fc3`). À investiguer en phase dédiée (hors P4).
- **PHASE_X200_P3C OSM_PREDICTIVE_ADAPTATIF_Ω** : intégration OSM/cadastre
  live pour `human_zones` + predictive adaptatif selon hétérogénéité locale.
- **PHASE_X200_P6 ANTI_RÉGRESSION_Ω** : exploiter les hooks d'observabilité
  RenduOmega pour métriques anti-régression continues.

## Architecture actuelle
```
/app/backend/
├── engines/
│   ├── v8_institutional/          (V30 LOCKED — intangible)
│   ├── reseau_veineux_omega/       (external_inflow.py + router.py)
│   ├── post_smoothing/             (organic_corridor_smoother.py + p1_preparation.py)
│   ├── eco_zones_omega/
│   ├── bio_scoring_omega/          (v30_mirror_read_only.py)
│   ├── hydro_topo_omega/
│   └── wildlife_behavior_omega/
├── routes/                         (catalogue/ci_status/preview/diff_matrix...)
├── tools/                          (audit_engines_x199_x200.py)
└── tests/                          (pytest — manuel uniquement)
```

## Endpoints clés (read-only Ω)
- `GET /api/v7-ultime-export/download`
- `GET /api/v7-vs-actuel/diff-matrix`
- `GET /api/catalogue-engines/download`
- `GET /api/v7-ultime/corridor-pipeline-preview`
- `GET /api/v7-ultime/reseau-veineux/external-inflow/geojson`
- `GET /api/omega/ci-status` (dashboard Ω)

## Testing Policy
- Aucun `testing_agent_v3_fork`.
- Pytest ciblé : `backend/tests/test_external_inflow_x200_p1.py`,
  `backend/tests/test_engines_x199_scaffold.py`.
- Jest : 65/65 attendu (suite historique verte).
- Curl vers `REACT_APP_BACKEND_URL` pour validation E2E.

## Garde-fous
- V30 LOCKED immuable.
- DIAGNOSTIC-CORRIDORS-Ω interdit.
- Aucun refactoring non sanctionné.
- Toute activation nouvelle exige ORDRE DIRECT du COMMANDANT.
-ultime-export/download`
- `GET /api/v7-vs-actuel/diff-matrix`
- `GET /api/catalogue-engines/download`
- `GET /api/v7-ultime/corridor-pipeline-preview`
- `GET /api/v7-ultime/reseau-veineux/external-inflow/geojson`
- `GET /api/omega/ci-status` (dashboard Ω)

## Testing Policy
- Aucun `testing_agent_v3_fork`.
- Pytest ciblé : `backend/tests/test_external_inflow_x200_p1.py`,
  `backend/tests/test_engines_x199_scaffold.py`.
- Jest : 65/65 attendu (suite historique verte).
- Curl vers `REACT_APP_BACKEND_URL` pour validation E2E.

## Garde-fous
- V30 LOCKED immuable.
- DIAGNOSTIC-CORRIDORS-Ω interdit.
- Aucun refactoring non sanctionné.
- Toute activation nouvelle exige ORDRE DIRECT du COMMANDANT.
