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

## Prioritized Backlog
### P0 — Aucun (phase actuelle scellée)
### P1 — Phase P1 COMPLÈTE (activation terminée ✅)
### P2 — Phase X199 COMPLÈTE (activation terminée ✅)
### P3 — Phase X200-P2 COMPLÈTE (MFFP sync + predictive integration ✅)
### P4 — Sur ordre du Commandant
- Enrichissement des bundles avec `terrain_signals` réels (water/slope/NDVI)
  pour étaler distribution hiérarchique des corridors externes sur 5 niveaux.

### P2 — Backlog institutionnel
- Extension `runtime_beacon.conforming` live frontend (nécessite directive
  dédiée autorisant émission beacon).
- Instrumentation CI `ci_status_omega` → cible `overall_status: OK`
  (actuellement `ATTENTION` en raison du beacon runtime hors-périmètre).

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
