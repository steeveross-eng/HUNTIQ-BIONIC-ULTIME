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

## Prioritized Backlog
### P0 — Aucun (phase actuelle scellée)
### P1 — Sur ordre du Commandant
- **PHASE X200-P1 (density / vital / scoring)** : activation séquencée des
  3 flags historiques (token dédié `STEEVE-MAX-P1-EXPLICIT`).
    a) `P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER`
    b) `P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES`
    c) `P1_FLAG_POST_V30_SCORING_8_FACTORS`
- **PHASE X199-ACTIVATION** : Plan d'activation engine-par-engine des 5
  engines étendus (`ecoforestry_omega`, `terrain_3d_omega`,
  `legal_time_omega`, `predictive_omega`, `advanced_geospatial_omega`).

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
