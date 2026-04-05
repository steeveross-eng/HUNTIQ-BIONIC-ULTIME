# PLAN D'INTEGRATION DASHBOARD — INTELLIGENCE V6-CORE
## Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+ | STEEVE-MAX
## Date : 2026-04-04 | Merge MAIN : STRICTEMENT INTERDIT
## AUCUNE MODIFICATION UI/UX SANS VALIDATION STEEVE-MAX

---

# TABLE DES MATIERES

1. [OBJECTIF ET PERIMETRE](#1-objectif-et-perimetre)
2. [DATA FUSION LAYER (DFL)](#2-data-fusion-layer)
3. [EVENT BUS V6](#3-event-bus-v6)
4. [DATA CONTRACTS V6](#4-data-contracts-v6)
5. [DASHBOARD AUTO-SYNC ENGINE](#5-dashboard-auto-sync-engine)
6. [PROPAGATION MATRIX M1→M2→M3→M4→M5](#6-propagation-matrix)
7. [REGRESSION GUARD V6](#7-regression-guard-v6)
8. [INTEGRATIONS DETAILLEES](#8-integrations-detaillees)
9. [NOUVELLES HEATMAPS](#9-nouvelles-heatmaps)
10. [ENRICHISSEMENT FICHES POI/ESPECES/ZONES](#10-enrichissement-fiches)
11. [NOUVEAUX TABLEAUX](#11-nouveaux-tableaux)
12. [MISE A JOUR SCORE CONSOLIDE](#12-score-consolide)
13. [PLAN D'IMPLEMENTATION](#13-plan-implementation)
14. [INVENTAIRE MODIFICATIONS](#14-inventaire)
15. [RISQUES BCE-4X](#15-risques)

---

# 1. OBJECTIF ET PERIMETRE

## 1.1 Objectif

Integrer les sorties des modules M1, M2, M3 dans l'interface INTELLIGENCE V6-CORE
via une couche de fusion de donnees automatique, un bus evenementiel, et des contrats
de donnees stricts. L'objectif est de rendre visible dans le Dashboard BIONIC :
- Les couches predictives M3 (P(h) horaire, heatmaps, best-times)
- Les series temporelles et tendances M3
- Les correlations meteo-faune M3
- Le graphe POI M2 enrichi par M3
- Les donnees nationales M1 dans les fiches POI/zones
- Le SCORE CONSOLIDE V6 fusionnant toutes les sources

## 1.2 Principes

| Principe | Application |
|----------|-------------|
| ZERO DOUBLON | Chaque donnee a UNE source canonique, jamais dupliquee |
| ZERO CONTRADICTION | Data Contracts V6 avec schemas TypeScript stricts |
| ZERO OBSOLESCENCE | Event Bus V6 declenche refresh automatique |
| ZERO INTERPRETATION | Chaque widget lit ses donnees via DFL, pas de logique metier dans les composants |
| ZERO LOSS | Aucun composant V5 existant supprime ou modifie |

## 1.3 Architecture existante consommee

### Backend (LECTURE SEULE sur modules existants)

| Module Backend | Endpoints | Donnees |
|---------------|-----------|---------|
| predictive_layer_engine (M3) | 10 endpoints | Couches predictives, timeseries, trends, correlations |
| poi_graph_engine (M2) | 11 endpoints | Noeuds POI, aretes, clusters, scores |
| national_data_harvester (M1) | 10 endpoints | Zones legales, provinces, contraintes |
| nutrition_v6_interface | 12 endpoints | Wrappers nutritionnels V6 |
| predictive_engine (V5) | existant | Predictions comportementales |
| solunar (V5) | existant | Calendrier solunaire |
| weather_fauna_simulation (V5) | existant | Correlations meteo |
| scoring_engine (V5) | existant | Scoring produits |

### Frontend (MODIFICATION RESTRICTIVE — wrapper pattern)

| Element Frontend | Fichier | Modification |
|-----------------|---------|-------------|
| useBionicStore | stores/useBionicStore.js | EXTENSION (ajout slices M3, ZERO modification slices existants) |
| PredictiveService | modules/predictive/PredictiveService.js | WRAPPER M3 (ajout methodes, ZERO modification existantes) |
| HeatmapLayer | components/HeatmapLayer.jsx | WRAPPER M3 (ajout layer predictif, ZERO modification layer V5) |

---

# 2. DATA FUSION LAYER (DFL)

## 2.1 Definition

Le Data Fusion Layer est un service frontend centralise qui :
1. Collecte les donnees de TOUTES les sources backend (M1, M2, M3, Nutrition V6, SUPRA, Meteo, Solunaire)
2. Normalise les schemas via Data Contracts V6
3. Calcule le SCORE CONSOLIDE V6
4. Redistribue aux widgets via l'Event Bus V6

## 2.2 Architecture

```
Backend APIs
    |
    v
DataFusionLayer (NOUVEAU : services/DataFusionLayer.js)
    |
    +--- PredictiveLayerAPI      <- M3 endpoints
    +--- POIGraphAPI             <- M2 endpoints
    +--- NationalDataAPI         <- M1 endpoints
    +--- NutritionV6API          <- Nutrition V6 wrappers
    +--- PredictiveEngineAPI     <- V5 predictive (existant, LECTURE)
    +--- SolunarAPI              <- V5 solunar (existant, LECTURE)
    +--- WeatherFaunaAPI         <- V5 meteo-faune (existant, LECTURE)
    +--- ScoringAPI              <- V5 scoring (existant, LECTURE)
    |
    v
DataContracts V6 (validation)
    |
    v
Event Bus V6 (distribution)
    |
    v
Dashboard Widgets
```

## 2.3 Fichier : services/DataFusionLayer.js

### Methodes principales

| Methode | Sources fusionnees | Output |
|---------|-------------------|--------|
| `fetchConsolidatedView(zone_id, species, date)` | M3.layer + M3.trends + M2.cluster + M1.legal + Solunar + Meteo | ConsolidatedViewContract |
| `fetchPOIEnriched(poi_id)` | M2.get_poi + M3.score + M1.legal + NutritionV6 | POIEnrichedContract |
| `fetchHeatmapData(zone_id, species)` | M3.heatmap + M2.nodes | HeatmapDataContract |
| `fetchTimeSeries(zone_id, species, metric)` | M3.timeseries | TimeSeriesContract |
| `fetchTrends(species, zone_id)` | M3.trends | TrendsContract |
| `fetchCorrelationMatrix(zone_id, species)` | M3.correlation | CorrelationContract |
| `fetchBestTimes(zone_id, species, date)` | M3.best-times + Solunar | BestTimesContract |
| `fetchScoreConsolide(zone_id, species, date)` | TOUTES sources | ScoreConsolideContract |

### Regles DFL

| Regle | Description |
|-------|-------------|
| DFL-R1 | Chaque methode retourne un objet conforme a un Data Contract V6 |
| DFL-R2 | Les appels API sont mis en cache TTL 5min (configurable) |
| DFL-R3 | Les erreurs sont encapsulees (graceful degradation), jamais propagees brutes |
| DFL-R4 | Les methodes ne contiennent AUCUNE logique metier (pas de calcul de score, pas de formule) |
| DFL-R5 | DFL est stateless : pas de store interne, tout passe par le store Zustand |

---

# 3. EVENT BUS V6

## 3.1 Definition

Le Event Bus V6 est un systeme de publication/souscription frontend qui declenche
automatiquement la mise a jour des widgets lorsque les donnees changent.

## 3.2 Architecture

### Fichier : services/EventBusV6.js

```
EventBusV6
    |
    +--- Channels (topics de publication)
    |       +--- PREDICTIVE_LAYER_UPDATED
    |       +--- POI_GRAPH_UPDATED
    |       +--- HEATMAP_UPDATED
    |       +--- TIMESERIES_UPDATED
    |       +--- TRENDS_UPDATED
    |       +--- CORRELATION_UPDATED
    |       +--- SCORE_CONSOLIDE_UPDATED
    |       +--- SOLUNAR_UPDATED
    |       +--- METEO_UPDATED
    |       +--- NUTRITION_UPDATED
    |       +--- SPECIES_CHANGED
    |       +--- ZONE_CHANGED
    |       +--- DATE_CHANGED
    |
    +--- Subscribers (widgets abonnes)
            +--- PredictiveLayerWidget → ecoute PREDICTIVE_LAYER_UPDATED
            +--- HeatmapWidget → ecoute HEATMAP_UPDATED
            +--- TrendsChart → ecoute TRENDS_UPDATED
            +--- etc.
```

## 3.3 Flux de declenchement

```
Utilisateur change espece/zone/date
    → EventBusV6.emit(SPECIES_CHANGED | ZONE_CHANGED | DATE_CHANGED)
    → DFL.fetchConsolidatedView() (automatic)
    → EventBusV6.emit(PREDICTIVE_LAYER_UPDATED)
    → EventBusV6.emit(HEATMAP_UPDATED)
    → EventBusV6.emit(SCORE_CONSOLIDE_UPDATED)
    → Widgets se mettent a jour automatiquement
```

## 3.4 Regles Event Bus

| Regle | Description |
|-------|-------------|
| EB-R1 | Les widgets NE font PAS d'appels API directs, ils ecoutent le bus |
| EB-R2 | Seul DFL a le droit d'emettre sur les channels DATA_* |
| EB-R3 | Les channels SPECIES/ZONE/DATE sont emis par le store Zustand |
| EB-R4 | Anti-debounce : max 1 emission par channel par 500ms |
| EB-R5 | Compat V5 : les composants V5 existants continuent de fonctionner sans modification |

---

# 4. DATA CONTRACTS V6

## 4.1 Definition

Les Data Contracts sont des schemas TypeScript qui garantissent la forme exacte
des donnees echangees entre DFL et widgets. ZERO INTERPRETATION possible.

## 4.2 Contrats

### ConsolidatedViewContract

```typescript
interface ConsolidatedViewContract {
  zone_id: string;
  species: string;
  target_date: string;
  score_consolide: ScoreConsolideContract;
  predictive_layer: {
    predictions: Array<{ hour: number; probability: number; confidence: number; factors: FactorsContract }>;
    aggregation: { peak_probability: number; peak_hour: number; best_window: { start: number; end: number }; trend: string };
  };
  solunar: {
    phase_name: string; illumination: number; solunar_score: number;
    hunting_windows: Array<{ start: string; end: string; intensity: string }>;
  };
  meteo: {
    activity_multiplier: number; recommendation: string; limiting_factor: string;
  };
  legal: {
    province: string; zone_chasse: string; is_season_open: boolean;
  };
  poi_count: number;
  data_freshness: string; // ISO8601
}
```

### ScoreConsolideContract

```typescript
interface ScoreConsolideContract {
  global: number;        // 0-100
  rating: string;        // "A+" | "A" | "B+" | "B" | "C" | "D"
  components: {
    predictive: number;    // 0-100, poids 0.25 — P(h) peak probability
    solunar: number;       // 0-100, poids 0.15 — solunar_score
    meteo: number;         // 0-100, poids 0.20 — activity_multiplier * 100
    nutrition: number;     // 0-100, poids 0.15 — forage_quality normalized
    territory: number;     // 0-100, poids 0.15 — poi cluster density + connectivity
    legal: number;         // 0-100, poids 0.10 — saison ouverte=100, fermee=0
  };
  weights: {
    predictive: 0.25; solunar: 0.15; meteo: 0.20;
    nutrition: 0.15; territory: 0.15; legal: 0.10;
  };
  trend: "up" | "stable" | "down";
  confidence: number;     // 0-1
  computed_at: string;     // ISO8601
}
```

### FactorsContract

```typescript
interface FactorsContract {
  base_activity: number;
  season: number;
  solunar: number;
  meteo: number;
  historical: number;
  nutrition: number;
}
```

### POIEnrichedContract

```typescript
interface POIEnrichedContract {
  poi_id: string;
  name: string;
  type: string;
  location: { lat: number; lng: number };
  score: {
    global: number; accessibility: number; activity: number; strategic: number; nutrition: number;
  };
  prediction: {
    current_probability: number;
    peak_hour: number;
    peak_probability: number;
    best_window: { start: number; end: number };
  };
  nutrition: {
    forage_quality: number; mineral_richness: number; ndvi_index: number;
    species_attractiveness: Record<string, number>;
  };
  legal: {
    province: string; zone_chasse: string; regulations: string[];
  };
  connections: number;
  edge_count: number;
}
```

### HeatmapDataContract

```typescript
interface HeatmapDataContract {
  zone_id: string;
  species: string;
  points: Array<{
    poi_id: string; name: string; type: string;
    lat: number; lng: number;
    probability: number; // 0-1, from M3 predictive heatmap
    poi_score: number;   // 0-1, from M2 POI score
    intensity: "high" | "medium" | "low";
  }>;
  total_pois: number;
  computed_at: string;
}
```

### TimeSeriesContract

```typescript
interface TimeSeriesContract {
  zone_id: string;
  species: string;
  metric: string;
  values: Array<{ timestamp: string; value: number; source: string }>;
  total_points: number;
  latest_value: number;
  granularity: "hourly" | "daily" | "weekly";
}
```

### TrendsContract

```typescript
interface TrendsContract {
  species: string;
  zone_id: string;
  year: number;
  monthly_patterns: Array<{
    month: number;
    activity_index: number;
    peak_hours: number[];
    observation_count: number;
    trend_vs_previous: "up" | "stable" | "down";
    baseline_factor: number;
  }>;
  annual_summary: {
    peak_month: number; peak_activity: number;
    low_month: number; low_activity: number;
    avg_activity: number;
  };
}
```

### CorrelationContract

```typescript
interface CorrelationContract {
  zone_id: string;
  species: string;
  correlation_matrix: Record<string, {
    correlation_strength: number;
    impact: "primary" | "secondary" | "tertiary";
    optimal_range?: { min: number; max: number };
    description: string;
  }>;
  optimal_conditions: {
    optimal_temp_min: number; optimal_temp_max: number;
    max_wind_speed: number; pressure_trend: string;
  };
  solunar_context: {
    solunar_score: number; phase_name: string; lunar_intensity: number;
  };
  confidence: number;
}
```

### BestTimesContract

```typescript
interface BestTimesContract {
  zone_id: string;
  species: string;
  target_date: string;
  best_windows: Array<{
    start_hour: number; end_hour: number;
    label: string; period: string;
    avg_probability: number; peak_probability: number;
    dominant_factor: string;
  }>;
  solunar_windows: Array<{ start: string; end: string; intensity: string }>;
  recommendation: string;
}
```

## 4.3 Regles Data Contracts

| Regle | Description |
|-------|-------------|
| DC-R1 | DFL DOIT valider la conformite de chaque reponse API avant de redistribuer |
| DC-R2 | Les champs manquants sont remplaces par des valeurs par defaut (jamais null/undefined) |
| DC-R3 | Les scores sont TOUJOURS normalises 0-100 pour le Score Consolide, 0-1 pour les facteurs |
| DC-R4 | Les dates sont TOUJOURS en ISO8601 UTC |
| DC-R5 | Les especes sont TOUJOURS en format canonique M3 (orignal, chevreuil, ours_noir, dindon_sauvage) |

---

# 5. DASHBOARD AUTO-SYNC ENGINE

## 5.1 Definition

Le Dashboard Auto-Sync Engine orchestre automatiquement la mise a jour de tous
les widgets du Dashboard lorsque l'utilisateur change d'espece, de zone ou de date.

## 5.2 Widgets alimentes

| # | Widget | Source DFL | Event Bus Channel | Composant |
|---|--------|-----------|-------------------|-----------|
| W1 | SCORE CONSOLIDE | fetchScoreConsolide() | SCORE_CONSOLIDE_UPDATED | ScoreConsolideWidget (NOUVEAU) |
| W2 | LUNA/SOLCAL | fetchConsolidatedView().solunar | SOLUNAR_UPDATED | SolunarWidget (EXTENSION) |
| W3 | FORECAST P(h) | fetchConsolidatedView().predictive_layer | PREDICTIVE_LAYER_UPDATED | PredictiveLayerWidget (NOUVEAU) |
| W4 | POI Graph Map | fetchHeatmapData() | HEATMAP_UPDATED | POIGraphMapOverlay (NOUVEAU) |
| W5 | Heatmap Predictive | fetchHeatmapData() | HEATMAP_UPDATED | PredictiveHeatmapLayer (NOUVEAU) |
| W6 | Tendances | fetchTrends() | TRENDS_UPDATED | TrendsChart (NOUVEAU) |
| W7 | Correlations | fetchCorrelationMatrix() | CORRELATION_UPDATED | CorrelationMatrixWidget (NOUVEAU) |
| W8 | Best Times | fetchBestTimes() | PREDICTIVE_LAYER_UPDATED | BestTimesWidget (NOUVEAU) |
| W9 | TimeSeries | fetchTimeSeries() | TIMESERIES_UPDATED | TimeSeriesChart (NOUVEAU) |
| W10 | Fiche POI enrichie | fetchPOIEnriched() | POI_GRAPH_UPDATED | POIDetailCard (NOUVEAU) |

## 5.3 Flux Auto-Sync

```
useBionicStore.setSpecies("orignal")
    → EventBusV6.emit(SPECIES_CHANGED, "orignal")
    → DFL.fetchConsolidatedView(zone, "orignal", date)
        → GET /api/v1/predict-layer/zone/{zone}/species/orignal
        → GET /api/v1/poi-graph/nodes?zone_id={zone}
        → GET /api/v1/predict-layer/correlation/meteo/{zone}?species=orignal
        → GET /api/v1/map-intel/legal-check/{lat}/{lng}/orignal
    → DataContracts.validate(response)
    → EventBusV6.emit(PREDICTIVE_LAYER_UPDATED, validated_data)
    → EventBusV6.emit(HEATMAP_UPDATED, heatmap_data)
    → EventBusV6.emit(SCORE_CONSOLIDE_UPDATED, score)
    → Tous les widgets W1-W10 se rafraichissent
```

## 5.4 Regles Auto-Sync

| Regle | Description |
|-------|-------------|
| AS-R1 | Le refresh est declenche UNIQUEMENT par changement d'espece/zone/date |
| AS-R2 | Les appels API sont parallelises (Promise.all) |
| AS-R3 | Cache TTL 5min pour eviter les appels redondants |
| AS-R4 | Mode degrade : si M3 est indisponible, fallback sur V5 predictive_engine |
| AS-R5 | Loading states individuels par widget (pas de loading global bloquant) |

---

# 6. PROPAGATION MATRIX M1 → M2 → M3 → M4 → M5

## 6.1 Matrice de propagation des donnees

```
SOURCE             → CONSOMMATEUR      → TYPE        → CANAL DFL            → WIDGET
-------------------------------------------------------------------------------------------
M1.legal_zones     → DFL               → SYNC        → ConsolidatedView     → W1, W10
M1.boundary        → M2.poi_create     → ENRICHMENT  → POIEnriched          → W10
M1.legal_check     → DFL               → SYNC        → ConsolidatedView     → W1
M2.poi_nodes       → M3.heatmap        → INPUT       → HeatmapData          → W4, W5
M2.poi_nodes       → DFL               → SYNC        → POIEnriched          → W10
M2.poi_score       → M3.heatmap        → INPUT       → HeatmapData          → W4, W5
M2.poi_edges       → DFL               → SYNC        → POIEnriched          → W10
M2.cluster         → DFL               → SYNC        → ScoreConsolide       → W1
M3.layer           → DFL               → PRIMARY     → ConsolidatedView     → W1, W3, W8
M3.heatmap         → DFL               → PRIMARY     → HeatmapData          → W4, W5
M3.timeseries      → DFL               → PRIMARY     → TimeSeries           → W9
M3.trends          → DFL               → PRIMARY     → Trends               → W6
M3.correlation     → DFL               → PRIMARY     → Correlation          → W7
M3.best_times      → DFL               → PRIMARY     → BestTimes            → W8
NutritionV6        → M3.compute        → INPUT       → ScoreConsolide       → W1
Solunar            → M3.compute        → INPUT       → ConsolidatedView     → W2
Solunar            → DFL               → SYNC        → SolunarWidget        → W2
Meteo              → M3.compute        → INPUT       → ConsolidatedView     → W1, W7
Scoring V5         → DFL               → LEGACY      → (non modifie)        → existant
```

## 6.2 Regles de propagation

| Regle | Description |
|-------|-------------|
| PM-R1 | Les donnees M3 sont la SOURCE PRIMAIRE pour les widgets predictifs |
| PM-R2 | Les donnees V5 (predictive_engine, solunar, scoring) restent accessibles comme LEGACY |
| PM-R3 | La propagation est UNIDIRECTIONNELLE : M1→M2→M3→Widgets |
| PM-R4 | AUCUN widget ne modifie les donnees (read-only) |
| PM-R5 | M4 consommera DFL (pas les APIs directement) quand il sera deploye |
| PM-R6 | M5 consommera les donnees via cache offline (pas DFL en temps reel) |

## 6.3 Impact M4 et M5

| Phase | Consommation | Integration |
|-------|-------------|-------------|
| M4 (Adaptive Navigation) | DFL.fetchBestTimes + DFL.fetchHeatmapData + DFL.fetchScoreConsolide | Ajout NavigationWidget (futur) |
| M5 (Offline Mode) | DFL → OfflinePackager (export JSON) | Ajout OfflineExportWidget (futur) |

---

# 7. REGRESSION GUARD V6

## 7.1 Definition

Le Regression Guard V6 garantit ZERO LOSS, ZERO REGRESSION, ZERO OBSOLESCENCE
dans l'interface Dashboard lors de l'integration des sorties M3.

## 7.2 Mecanismes

### 7.2.1 ZERO LOSS (code existant preserve)

| Composant existant | Action | Justification |
|-------------------|--------|---------------|
| PredictiveService.js | WRAPPER : ajout methodes M3, methodes V5 preservees | predictHuntingSuccess() reste intacte |
| ScoringService.js | NON MODIFIE | Scoring produits independant de M3 |
| useBionicStore.js | EXTENSION : ajout slices M3, slices existants NON modifies | fetchSummary/fetchForecast/fetchPlan/fetchSolunar intacts |
| HeatmapLayer.jsx | WRAPPER : ajout layer predictif, layer V5 preserve | Le heatmap waypoint V5 reste actif |
| SuccessForecast.jsx | NON MODIFIE | Forecast V5 reste disponible en parallele |
| useBionicScoring.js | NON MODIFIE | Scoring waypoints V5 independant |
| useBionicWeather.js | NON MODIFIE | Meteo V5 independante |

### 7.2.2 ZERO REGRESSION (tests)

| Test | Description | Cible |
|------|-------------|-------|
| RG-T1 | Widget V5 existants fonctionnent sans M3 | Fallback mode |
| RG-T2 | Changement espece/zone/date rafraichit tous les widgets | Auto-sync |
| RG-T3 | Score Consolide est coherent (0-100, rating A+→D) | Data Contract |
| RG-T4 | Heatmap predictive ne masque pas heatmap V5 | Layers coexistence |
| RG-T5 | Loading states ne bloquent pas l'interface | UX |

### 7.2.3 ZERO OBSOLESCENCE (freshness)

| Mecanisme | Description |
|-----------|-------------|
| TTL Cache | Cache DFL expire apres 5min, force refresh |
| data_freshness | Chaque ConsolidatedView contient un timestamp de fraicheur |
| valid_until | Les predictive_layers M3 ont un TTL 6h cote backend |
| Event Bus auto-refresh | Changement contexte (espece/zone/date) → refresh immediat |

---

# 8. INTEGRATIONS DETAILLEES

## 8.1 Integration solunaire avancee (PF3-LUN1/LUN2/LUN3)

| Element | Source | Integration Dashboard | Widget |
|---------|--------|----------------------|--------|
| Phase lunaire | solunar.moon.phase_name → M3.solunar_context | ConsolidatedView.solunar.phase_name | W2 SolunarWidget |
| Score solunaire | solunar.solunar_score → M3.solunar_context | ConsolidatedView.solunar.solunar_score | W2, W1 |
| Illumination | solunar.moon.illumination → M3.solunar_context | ConsolidatedView.solunar.illumination | W2 |
| Fenetres chasse | solunar.hunting_windows → M3.best_times | BestTimesContract.solunar_windows | W8 |
| Impact horaire | solunar.curve_24h → M3.P(h).solunar factor | ConsolidatedView.predictive_layer.predictions[h].factors.solunar | W3 |

**Nouveau widget W2 (SolunarWidget)** :
- Affiche phase lunaire avec icone
- Score solunaire (gauge 0-100)
- Fenetres optimales solunaires
- Croisement avec best-times M3

## 8.2 Integration meteo-faune (PF3-MET1/MET2/MET3)

| Element | Source | Integration Dashboard | Widget |
|---------|--------|----------------------|--------|
| Conditions optimales | weather_fauna.optimal_conditions → M3.correlation | CorrelationContract.optimal_conditions | W7 |
| Matrice correlation | M3.correlation.correlation_matrix | CorrelationContract.correlation_matrix | W7 |
| Facteur meteo horaire | M3.P(h).factors.meteo | ConsolidatedView.predictive_layer.predictions[h].factors.meteo | W3 |
| Recommandation | M3.layer.meteo_context.recommendation | ConsolidatedView.meteo.recommendation | W1 |
| Impact par facteur | temperature, pression, vent, precipitations, lune, humidite | CorrelationContract.correlation_matrix (6 axes) | W7 |

**Nouveau widget W7 (CorrelationMatrixWidget)** :
- Radar chart 6 axes (temperature, pression, vent, precipitations, lune, humidite)
- Codes couleur : primaire (rouge), secondaire (orange), tertiaire (jaune)
- Conditions optimales par espece

## 8.3 Integration Nutrition V6 (PF3-N1/N2/N3/N4)

| Element | Source | Integration Dashboard | Widget |
|---------|--------|----------------------|--------|
| Qualite fourrage | nutrition_v6_interface → M3.P(h).factors.nutrition | ConsolidatedView.predictive_layer.predictions[h].factors.nutrition | W3, W1 |
| Richesse minerale | nutrition_v6_interface.soil_nutrients | POIEnrichedContract.nutrition.mineral_richness | W10 |
| NDVI | nutrition_v6_interface.forage_quality | POIEnrichedContract.nutrition.ndvi_index | W10 |
| Attractivite espece | nutrition_v6_interface.wildlife_attractiveness | POIEnrichedContract.nutrition.species_attractiveness | W10 |

**Pas de nouveau widget nutritionnel** : les donnees Nutrition V6 sont injectees dans le Score Consolide (composant nutrition, poids 0.15) et dans les fiches POI enrichies.

## 8.4 Integration predictive horaire P(h) (PF3-S1/S2)

| Element | Source | Integration Dashboard | Widget |
|---------|--------|----------------------|--------|
| Courbe 24h | M3.layer.predictions (24 points) | ConsolidatedView.predictive_layer.predictions | W3 PredictiveLayerWidget |
| Peak probability | M3.layer.aggregation.peak_probability | ConsolidatedView.predictive_layer.aggregation.peak_probability | W3, W1 |
| Best window | M3.layer.aggregation.best_window | ConsolidatedView.predictive_layer.aggregation.best_window | W3, W8 |
| Trend | M3.layer.aggregation.trend | ConsolidatedView.predictive_layer.aggregation.trend | W3 |
| Decomposition 6 facteurs | predictions[h].factors | FactorsContract | W3 (tooltip detail) |

**Nouveau widget W3 (PredictiveLayerWidget)** :
- Courbe P(h) sur 24h (area chart)
- Highlight de la fenetre optimale (best_window)
- Decomposition des facteurs en tooltip
- Badge peak hour + peak probability

---

# 9. NOUVELLES HEATMAPS

## 9.1 Heatmap Predictive (W5)

| Attribut | Valeur |
|----------|--------|
| Source | M3.heatmap → DFL.fetchHeatmapData() |
| Format | Array de { lat, lng, probability, intensity } |
| Layer Leaflet | PredictiveHeatmapLayer (NOUVEAU, coexiste avec HeatmapLayer V5) |
| Gradient | bleu(0.0) → vert(0.3) → jaune(0.5) → orange(0.7) → rouge(1.0) |
| Rayon | 40px (plus large que V5 pour visibilite predictive) |
| Toggle | Bouton ON/OFF independant de la heatmap V5 |

### Specifications

```javascript
// PredictiveHeatmapLayer.jsx (NOUVEAU)
// Consomme HeatmapDataContract via DFL
// Ne modifie PAS HeatmapLayer.jsx existant
```

## 9.2 Heatmap Temporelle (variante du W5)

| Attribut | Valeur |
|----------|--------|
| Source | M3.heatmap filtre par heure du jour |
| Interaction | Slider horaire (0-23) pour voir l'evolution |
| Animation | Transition smooth entre heures (fade) |

---

# 10. ENRICHISSEMENT FICHES POI / ESPECES / ZONES

## 10.1 Fiche POI enrichie (W10)

| Section | Source | Contenu |
|---------|--------|---------|
| Identite | M2.get_poi | nom, type, coordonnees, altitude |
| Score POI | M2.get_poi.score | global, accessibilite, activite, strategique, nutrition |
| Prediction | M3.layer | probabilite actuelle, peak hour, best window |
| Nutrition | M2.get_poi.nutrition (via nutrition_v6_interface) | qualite fourrage, richesse minerale, NDVI |
| Legal | M1.legal_check | province, zone_chasse, regulations |
| Connexions | M2.get_poi.edges | aretes connectees, types de relation |
| Tendance | M3.trends (zone du POI) | trend mensuel, baseline saisonniere |

## 10.2 Fiche Espece enrichie

| Section | Source | Contenu |
|---------|--------|---------|
| Prediction | M3.layer | courbe P(h) pour l'espece |
| Best times | M3.best_times | creneaux optimaux |
| Tendances | M3.trends | patterns mensuels, peak/low mois |
| Conditions optimales | M3.correlation.optimal_conditions | temp, vent, pression ideaux |
| Score consolide | DFL.fetchScoreConsolide | score global pour l'espece dans la zone |

## 10.3 Fiche Zone enrichie

| Section | Source | Contenu |
|---------|--------|---------|
| Legal | M1.boundaries | province, regulations |
| Cluster | M2.cluster | POI count, types, densite, POIs isoles |
| Heatmap | M3.heatmap | points de probabilite, high/medium/low count |
| Tendances | M3.trends | activite mensuelle dans la zone |
| Correlations | M3.correlation | matrice meteo-faune pour la zone |

---

# 11. NOUVEAUX TABLEAUX

## 11.1 Tableau Tendances (W6 — TrendsChart)

| Colonne | Source | Format |
|---------|--------|--------|
| Mois | M3.trends.monthly_patterns[].month | Nom du mois |
| Indice activite | monthly_patterns[].activity_index | Barre proportionnelle 0-1 |
| Heures pic | monthly_patterns[].peak_hours | Badges horaires |
| Observations | monthly_patterns[].observation_count | Nombre |
| Tendance | monthly_patterns[].trend_vs_previous | Fleche (up/stable/down) |
| Baseline | monthly_patterns[].baseline_factor | Barre grise de reference |

**Visualisation** : Bar chart 12 mois + ligne de baseline (predictive_engine.SEASON_FACTORS).

## 11.2 Tableau Correlations (W7 — CorrelationMatrixWidget)

| Colonne | Source | Format |
|---------|--------|--------|
| Facteur | correlation_matrix keys | temperature, pression, vent, precipitations, lune, humidite |
| Force | correlation_matrix[].correlation_strength | Jauge -1 à +1 |
| Impact | correlation_matrix[].impact | Badge primary/secondary/tertiary |
| Range optimal | correlation_matrix[].optimal_range | min — max |
| Description | correlation_matrix[].description | Texte |

**Visualisation** : Table sortable + radar chart overlay.

## 11.3 Tableau Best Times (W8 — BestTimesWidget)

| Colonne | Source | Format |
|---------|--------|--------|
| Creneau | best_windows[].label | "05:00-07:59" |
| Periode | best_windows[].period | Badge aube/midi/crepuscule/nuit |
| Probabilite | best_windows[].avg_probability | Gauge % |
| Peak | best_windows[].peak_probability | % bold |
| Facteur dominant | best_windows[].dominant_factor | Badge colore |

## 11.4 Tableau TimeSeries (W9 — TimeSeriesChart)

| Element | Source | Format |
|---------|--------|--------|
| Graphe | timeseries.values | Line chart temporal |
| Metrique | timeseries.metric | Selecteur (activity_index, observation_count, camera_detection, poi_frequency) |
| Total points | timeseries.total_points | Badge |
| Derniere valeur | timeseries.latest_value | Highlight |

---

# 12. MISE A JOUR SCORE CONSOLIDE

## 12.1 Formule Score Consolide V6

```
SCORE_CONSOLIDE = 
    predictive * 0.25    ← M3 peak_probability * 100
  + solunar * 0.15       ← solunar.solunar_score
  + meteo * 0.20         ← M3 meteo_factor * 100
  + nutrition * 0.15     ← nutrition_v6 forage_quality_normalized * 100
  + territory * 0.15     ← M2 cluster density_score * 100
  + legal * 0.10         ← M1 saison ouverte=100, fermee=20
```

## 12.2 Grille de rating

| Score | Rating | Couleur | Description |
|-------|--------|---------|-------------|
| 90-100 | A+ | #22c55e (vert) | Conditions exceptionnelles |
| 80-89 | A | #3b82f6 (bleu) | Conditions excellentes |
| 65-79 | B+ | #f5a623 (orange) | Bonnes conditions |
| 50-64 | B | #eab308 (jaune) | Conditions moyennes |
| 35-49 | C | #f97316 (orange fonce) | Conditions limitees |
| 0-34 | D | #ef4444 (rouge) | Conditions defavorables |

## 12.3 Widget Score Consolide (W1)

- Gauge circulaire (0-100) avec animation
- Rating badge (A+ → D) avec couleur
- Decomposition 6 composants en bar chart
- Tendance (up/stable/down) avec fleche
- Tooltip detaille par composant

---

# 13. PLAN D'IMPLEMENTATION

## 13.1 Fichiers a creer (FRONTEND)

| # | Fichier | Type | Description |
|---|---------|------|-------------|
| F1 | src/services/DataFusionLayer.js | Service | DFL — Fusion, normalisation, cache |
| F2 | src/services/EventBusV6.js | Service | Event Bus publication/souscription |
| F3 | src/services/DataContractsV6.js | Validation | Validation schemas Data Contracts |
| F4 | src/modules/intelligence-v6/PredictiveLayerService.js | API Client | Client API M3 |
| F5 | src/modules/intelligence-v6/POIGraphService.js | API Client | Client API M2 |
| F6 | src/modules/intelligence-v6/components/ScoreConsolideWidget.jsx | Widget | W1 Score Consolide |
| F7 | src/modules/intelligence-v6/components/PredictiveLayerWidget.jsx | Widget | W3 Courbe P(h) 24h |
| F8 | src/modules/intelligence-v6/components/BestTimesWidget.jsx | Widget | W8 Creneaux optimaux |
| F9 | src/modules/intelligence-v6/components/TrendsChart.jsx | Widget | W6 Tendances saisonnieres |
| F10 | src/modules/intelligence-v6/components/CorrelationMatrixWidget.jsx | Widget | W7 Correlations meteo |
| F11 | src/modules/intelligence-v6/components/TimeSeriesChart.jsx | Widget | W9 Series temporelles |
| F12 | src/modules/intelligence-v6/components/POIDetailCard.jsx | Widget | W10 Fiche POI enrichie |
| F13 | src/components/map/PredictiveHeatmapLayer.jsx | Map Layer | W5 Heatmap predictive |
| F14 | src/modules/intelligence-v6/index.js | Index | Exports du module |

## 13.2 Fichiers existants modifies (EXTENSION/WRAPPER)

| # | Fichier | Modification | Impact |
|---|---------|-------------|--------|
| E1 | src/stores/useBionicStore.js | Ajout slices M3 (predictiveLayer, heatmap, trends, correlation, scoreConsolide) | EXTENSION — slices existants INTACTS |
| E2 | src/modules/predictive/PredictiveService.js | Ajout methodes M3 (getLayer, getHeatmap, getBestTimes, getTrends, getCorrelation) | WRAPPER — methodes V5 INTACTES |

## 13.3 Fichiers NON modifies

TOUS les fichiers existants non listes dans E1/E2 restent STRICTEMENT inchanges :
- ScoringService.js, useBionicScoring.js, useBionicWeather.js
- SuccessForecast.jsx, HeatmapLayer.jsx, tous les components V5
- Tous les hooks, stores, services, pages, utils existants

## 13.4 Sous-phases

```
DASH-A : Infrastructure (DFL + Event Bus + Data Contracts + API clients)
    → F1, F2, F3, F4, F5, F14
    → E1, E2

DASH-B : Widgets principaux (Score Consolide + P(h) + Best Times + Heatmap)
    → F6, F7, F8, F13

DASH-C : Tableaux et fiches (Tendances + Correlations + TimeSeries + POI Detail)
    → F9, F10, F11, F12

DASH-D : Tests (integration frontend + non-regression)
    → Tests playwright ou testing agent
```

---

# 14. INVENTAIRE MODIFICATIONS

## 14.1 ZERO modification backend

Aucune modification backend. Tous les endpoints M1, M2, M3, Nutrition V6, SUPRA, Solunar,
Meteo, Scoring restent strictement inchanges.

## 14.2 Frontend — Fichiers CREES (14)

| # | Chemin | Phase |
|---|--------|-------|
| F1 | src/services/DataFusionLayer.js | DASH-A |
| F2 | src/services/EventBusV6.js | DASH-A |
| F3 | src/services/DataContractsV6.js | DASH-A |
| F4 | src/modules/intelligence-v6/PredictiveLayerService.js | DASH-A |
| F5 | src/modules/intelligence-v6/POIGraphService.js | DASH-A |
| F6 | src/modules/intelligence-v6/components/ScoreConsolideWidget.jsx | DASH-B |
| F7 | src/modules/intelligence-v6/components/PredictiveLayerWidget.jsx | DASH-B |
| F8 | src/modules/intelligence-v6/components/BestTimesWidget.jsx | DASH-B |
| F9 | src/modules/intelligence-v6/components/TrendsChart.jsx | DASH-C |
| F10 | src/modules/intelligence-v6/components/CorrelationMatrixWidget.jsx | DASH-C |
| F11 | src/modules/intelligence-v6/components/TimeSeriesChart.jsx | DASH-C |
| F12 | src/modules/intelligence-v6/components/POIDetailCard.jsx | DASH-C |
| F13 | src/components/map/PredictiveHeatmapLayer.jsx | DASH-B |
| F14 | src/modules/intelligence-v6/index.js | DASH-A |

## 14.3 Frontend — Fichiers MODIFIES (2)

| # | Chemin | Type | Phase |
|---|--------|------|-------|
| E1 | src/stores/useBionicStore.js | EXTENSION (+50 lignes) | DASH-A |
| E2 | src/modules/predictive/PredictiveService.js | WRAPPER (+60 lignes) | DASH-A |

---

# 15. RISQUES BCE-4X

| # | Risque | Prob. | Impact | Mitigation |
|---|--------|-------|--------|-----------|
| R1 | Widgets V5 casses par integration M3 | TRES FAIBLE | CRITIQUE | Pattern EXTENSION/WRAPPER, ZERO modification V5 |
| R2 | Surcharge API (trop d'appels simultanes) | MODERE | MODERE | Cache DFL TTL 5min, Promise.all, debounce 500ms |
| R3 | Incoherence Score Consolide | FAIBLE | ELEVE | Data Contracts stricts, validation DFL |
| R4 | Heatmap predictive masque heatmap V5 | FAIBLE | MODERE | Layers independants, toggle ON/OFF |
| R5 | Latence DFL (aggregation multi-sources) | MODERE | FAIBLE | Loading states individuels, fallback V5 |

---

## PROCHAINES ETAPES

Ce plan requiert la **validation explicite de STEEVE-MAX** avant toute execution.

Apres validation, l'execution suivra la sequence :
DASH-A (Infrastructure) → DASH-B (Widgets) → DASH-C (Tableaux) → DASH-D (Tests)

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : M3_DASHBOARD_INTEGRATION_PLAN 1.0.0
**References** : M3_RAPPORT_FINAL 1.0.0, M2_RAPPORT_FINAL 1.0.0, BIONIC_V6_MAP_INTELLIGENCE_PLAN 1.1.0
**Code modifie** : AUCUN (plan uniquement)
**Backend modifie** : ZERO
**Merge main** : STRICTEMENT INTERDIT
