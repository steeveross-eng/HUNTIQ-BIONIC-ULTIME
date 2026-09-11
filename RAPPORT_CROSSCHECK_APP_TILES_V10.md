# HUNTIQ-BIONIC-ULTIME
## Rapport de cross-check `/app/` et `/tiles/`

**Version de référence demandée :** V10 — Architecture modulaire + Corridors Omega + Écoforesterie + BIONIC Core  
**Date du cross-check :** 2026-09-11  
**Workspace inspecté :** `/workspaces/HUNTIQ-BIONIC-ULTIME`

---

## 1. Conclusion exécutive

Le workspace courant correspond au contenu historique désigné par `/app/` dans les rapports précédents :

```text
/app/  ->  /workspaces/HUNTIQ-BIONIC-ULTIME/
```

Il n’existe pas de répertoire physique nommé `/app/` à l’intérieur du workspace, ni de répertoire physique `/tiles/`.

Le terme `/tiles/` désigne une ancienne surface API de tuiles territoriales, historiquement appelée sous la forme :

```text
/api/v20/territoire/tiles/{layer}/{z}/{x}/{y}.json
```

Dans l’état inspecté, cette surface n’est pas représentée par un dossier autonome `tiles/`. Les références restantes sont principalement historiques, documentaires ou liées à des tests archivés. Le code serveur contient aussi un statut résiduel MVT, mais pas une implémentation complète active équivalente à un dossier `/tiles/`.

---

## 2. Arborescence canonique `/app/`

```text
/app/
├── backend/
│   ├── bce/
│   ├── cache/
│   ├── config/
│   ├── core/
│   │   ├── alimentation/
│   │   ├── corridors/
│   │   ├── ecology/
│   │   ├── geo/
│   │   ├── ndvi/
│   │   ├── pressure/
│   │   ├── rest/
│   │   ├── scoring_pipeline/
│   │   └── weather/
│   ├── data/
│   ├── docs/
│   ├── engines/
│   │   ├── advanced_geospatial_omega/
│   │   ├── bio_scoring_omega/
│   │   ├── eco_zones_omega/
│   │   ├── ecoforestry_omega/
│   │   ├── gis_omega/
│   │   ├── hydro_topo_omega/
│   │   ├── nutrition_intelligence/
│   │   ├── post_smoothing/
│   │   ├── predictive_omega/
│   │   ├── spectral_omega/
│   │   ├── terrain_hr_omega/
│   │   ├── terrain_nav/
│   │   ├── v8_institutional/
│   │   ├── v8_national/
│   │   ├── weather_v3/
│   │   └── wildlife_behavior_omega/
│   ├── integrations/
│   ├── middleware/
│   ├── models/
│   ├── modules/
│   │   ├── bionic_data_fabric/
│   │   ├── bionic_ecological_engine/
│   │   ├── bionic_engine_p0/
│   │   ├── ecoforestry_engine/
│   │   ├── geospatial_engine/
│   │   ├── nutrition_engine/
│   │   ├── territory_engine/
│   │   ├── wildlife_behavior_engine/
│   │   └── ...
│   ├── monitoring/
│   ├── routes/
│   │   └── territory/
│   ├── schemas/
│   ├── scripts/
│   ├── services/
│   ├── state/
│   ├── static/
│   ├── tests/
│   ├── tools/
│   ├── validators/
│   ├── websocket/
│   ├── bionic_engine.py
│   ├── database.py
│   └── server.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── bionic/
│   │   │   ├── map/
│   │   │   ├── maps/
│   │   │   └── territoire/
│   │   ├── config/
│   │   ├── contexts/
│   │   ├── core/
│   │   │   └── bionic/
│   │   ├── data_layers/
│   │   │   ├── advanced_geospatial/
│   │   │   ├── behavioral/
│   │   │   ├── ecoforestry/
│   │   │   ├── layers_3d/
│   │   │   └── simulation/
│   │   ├── design-system/
│   │   ├── hooks/
│   │   ├── i18n/
│   │   ├── lib/
│   │   ├── modules/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── theme/
│   │   └── ui/
│   └── package.json
├── data/
├── institutional/
├── legacy/
├── memory/
├── registry/
├── scripts/
├── test_reports/
├── tests/
├── ARCHITECTURE.md
├── README.md
└── rapports et audits Markdown
```

---

## 3. Fichiers clés BIONIC Core

### Frontend

```text
frontend/src/core/bionic/
├── index.js
├── bionicColorsConfig.js
├── bionicConfig.js
├── bionicDataAdapter.js
├── bionicHybridModel.js
├── bionicModules.js
├── bionicScoring.js
├── bionicStrategyEngine.js
├── bionicWeatherEngine.js
└── speciesConfig.js
```

Fichiers d’intégration principaux :

```text
frontend/src/hooks/useBionicLayers.js
frontend/src/hooks/useBionicScoring.js
frontend/src/hooks/useBionicScoringV8.js
frontend/src/hooks/useBionicSession.js
frontend/src/hooks/useBionicWeather.js
frontend/src/hooks/useMapBundleV8.js
frontend/src/lib/bionicBundleCache.js
frontend/src/stores/useBionicStore.js
```

### Backend

```text
backend/bionic_engine.py
backend/core/scoring_pipeline/
backend/engines/bio_scoring_omega/
backend/modules/bionic_data_fabric/
backend/modules/bionic_ecological_engine/
backend/modules/bionic_engine_p0/
backend/modules/bionic_knowledge_engine/
```

---

## 4. Fichiers clés Corridors Omega

```text
backend/core/corridors/
backend/engines/gis_omega/
backend/engines/predictive_omega/
backend/engines/v8_institutional/
backend/modules/bionic_engine_p0/
frontend/src/components/territoire/BionicLayersV8.jsx
frontend/src/components/territoire/CorridorsDebugOverlay.jsx
frontend/src/components/territoire/LocalCorridorLensPanel.jsx
frontend/src/components/territoire/StatutCorridorsOmegaPanel.jsx
frontend/src/components/territoire/corridors-critique.css
frontend/src/lib/__tests__/phase_x170_corridors_biologie.test.js
```

Composants territoriaux associés :

```text
frontend/src/components/territoire/map/MapContent.jsx
frontend/src/components/territoire/map/SplitViewContainer.jsx
frontend/src/components/territoire/BionicMicroZones.jsx
frontend/src/components/territoire/BionicPrecisionZonesLayer.jsx
frontend/src/components/territoire/BionicZone2km.jsx
frontend/src/components/territoire/BionicZone600m.jsx
frontend/src/components/territoire/ConsolidatedHeatmapLayer.jsx
```

---

## 5. Fichiers clés Écoforesterie

### Backend

```text
backend/engines/ecoforestry_omega/
backend/modules/ecoforestry_engine/
backend/core/ecology/
backend/data/gis_archive/
backend/data/gis_operational/
```

### Frontend

```text
frontend/src/data_layers/ecoforestry/index.js
frontend/src/modules/ecoforestry/index.js
frontend/src/modules/ecoforestry/EcoforestryService.js
frontend/src/modules/ecoforestry/components/HabitatAnalysis.jsx
frontend/src/components/territoire/EcoforestryLayers.jsx
```

---

## 6. Statut exact de `/tiles/`

### Chemins API historiquement utilisés

```text
/api/v20/territoire/tiles/nutrition/14/4951/5775.json
/api/v20/territoire/tiles/corridors/14/4951/5776.json
/api/v20/territoire/tiles/{layer}/{z}/{x}/{y}.json
```

### Références restantes dans le checkout

```text
backend/tests/archive/render/test_render_guard_layers.py
backend/tests/archive/render/test_render_guard_performance.py
backend/tests/test_nutrition_v12.py
backend/tests/test_rse_omega.py
backend/engines/v8_institutional/redis_omega.py
backend/tools/zerocost_upload_r2_native.py
```

### Statut serveur

Le serveur contient encore des marqueurs de nettoyage MVT dans `backend/server.py`, notamment la suppression documentée de l’ancien module `v20_mvt_tiles.py`.

Le module `backend/modules/critical_modules/router.py` expose un statut MVT résiduel :

```text
/mvt/status
```

Ce statut indique notamment :

```json
{
  "engine": "MVT-TILES-Omega",
  "zones_ecologiques": "geojson_via_api (MVT conversion pending)",
  "corridors": "geojson_via_api (MVT conversion pending)"
}
```

### Conclusion `/tiles/`

```text
/tiles/                         ABSENT comme dossier physique
/api/v20/territoire/tiles/...   Surface historique/documentée
MVT-TILES-Omega                 Statut résiduel exposé
Implémentation MVT complète     NON CONFIRMÉE dans ce checkout
```

---

## 7. Sources documentaires canoniques

```text
README.md
ARCHITECTURE.md
memory/ARCHITECTURE_BIONIC_SNAPSHOT.md
memory/RSE_OMEGA_IMPLEMENTATION_REPORT.md
memory/ENGINES_ACTUELS_CARTOGRAPHIE_Ω.md
```

Le fichier [ARCHITECTURE.md](ARCHITECTURE.md) décrit l’organisation V10, les moteurs Omega et les couches API. Le fichier `memory/ARCHITECTURE_BIONIC_SNAPSHOT.md` conserve une arborescence historique plus large, correspondant à un snapshot antérieur et non nécessairement à tous les fichiers présents dans le checkout actuel.

---

## 8. Commandes de vérification

Depuis la racine du workspace :

```bash
find . -type d \( -name app -o -name tiles \) -print
find backend frontend -type f | grep -Ei 'tile|corridor|ecoforest|bionic|territoire'
grep -RInE 'territoire.*tiles|tiles.*territoire|MVT|mvt' backend
```

Résultat attendu du premier contrôle : aucune ligne pour un dossier physique `app` ou `tiles`.

---

## 9. Verdict de conformité pour cross-check

| Élément | Résultat |
|---|---|
| Architecture modulaire backend/frontend | Présente |
| BIONIC Core frontend | Présent |
| Moteurs Omega backend | Présents |
| Corridors Omega | Présence des composants et moteurs associés |
| Écoforesterie | Présence backend + frontend |
| Dossier physique `/app/` | Absent, car le workspace est déjà son équivalent |
| Dossier physique `/tiles/` | Absent |
| Endpoint historique `/api/v20/territoire/tiles/...` | Référencé par anciens tests/documentation |
| Pipeline MVT actif complet | Non confirmé dans l’état courant |

**Verdict final :** l’architecture V10 est représentée dans le workspace, mais la formulation `/tiles/` doit être comprise comme une ancienne surface API territoriale et non comme un répertoire actuellement livrable.