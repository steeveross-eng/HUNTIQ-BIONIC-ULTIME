# M3 — PREDICTIVE LAYER ENGINE + TIME-SERIES ENGINE — PLAN D'EXECUTION DETAILLE
## Directive x7000-PREP-M3 — Preparation M3
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-04 | Merge MAIN : STRICTEMENT INTERDIT
### AUCUN CODE MODIFIE tant que ce plan n'est pas valide par STEEVE-MAX

---

# TABLE DES MATIERES

1. [OBJECTIF ET PERIMETRE](#1-objectif-et-perimetre)
2. [DEPENDANCES M1 → M2 → M3](#2-dependances)
3. [ANALYSE DES MODULES SOURCES (LECTURE SEULE)](#3-modules-sources)
4. [SERVICES A CREER](#4-services)
5. [COLLECTIONS MONGODB](#5-collections)
6. [ENDPOINTS (9 + 1 health)](#6-endpoints)
7. [POINTS DE FUSION](#7-points-de-fusion)
8. [CHAINE M1 → M2 → M3 (Flux de donnees)](#8-chaine-m1-m2-m3)
9. [ANTI-DOUBLON](#9-anti-doublon)
10. [ANTI-DOUBLON NUTRITIONNEL](#10-anti-doublon-nutritionnel)
11. [PLAN D'IMPLEMENTATION](#11-plan-implementation)
12. [RISQUES BCE-4X](#12-risques)
13. [PROTOCOLES DE ROLLBACK](#13-rollback)
14. [IMPACTS PREVUS SUR M4 ET M5](#14-impacts-m4-m5)
15. [TESTS](#15-tests)
16. [INVENTAIRE MODIFICATIONS](#16-inventaire)

---

# 1. OBJECTIF ET PERIMETRE

## 1.1 Objectif

Ajouter une couche d'intelligence predictive temporelle sur la carte BIONIC :
- **Predictions d'activite faunique** par zone, espece et heure
- **Series temporelles historiques** avec collecte et stockage
- **Tendances saisonnieres** multi-annuelles
- **Correlations meteo-faune** exploitant les simulations existantes
- **Heatmaps de probabilite** et **meilleurs creneaux de chasse**

Le module NE remplace PAS `predictive_engine` (qui reste la source de predictions comportementales) ni `solunar` (calendrier solunaire). M3 AGREGE ces sources avec les donnees de terrain M1/M2 pour produire des couches predictives geospatiales inedites.

## 1.2 Perimetre

| Element | Description |
|---------|-------------|
| Module | `predictive_layer_engine/` (NOUVEAU) |
| Services | 4 (TimeSeriesCollector, PredictiveLayerComputer, SeasonalTrendAnalyzer, MeteoFaunaCorrelator) |
| Collections | 3 (timeseries_data, predictive_layers, seasonal_trends) |
| Endpoints | 9 + 1 health |
| Tests | 2 fichiers |
| Code V5 modifie | ZERO |
| Modules existants modifies | ZERO |

## 1.3 Principes

| Principe | Application |
|----------|-------------|
| ZERO LOSS | Aucun endpoint de predictive_engine, solunar, weather_fauna_simulation modifie |
| ZERO REGRESSION | Aucune collection existante alteree |
| ZERO INTERPRETATION | Implementation stricte de ce plan |
| ZERO DOUBLON | M3 NE recree PAS les predictions de predictive_engine ni le calendrier solunar |
| MongoDB bridges | Communication avec modules existants via lecture seule MongoDB |
| Aggregation | M3 AGREGE les sources existantes en couches predictives spatiales NOUVELLES |

---

# 2. DEPENDANCES M1 → M2 → M3

## 2.1 Dependance directe M1

| Composant M1 | Usage dans M3 | Type |
|-------------|--------------|------|
| boundary_resolver | Province + zone_chasse → contexte geographique prediction | LECTURE |
| legal_constraint_engine | Periodes legales → filtrage predictions hors-saison | LECTURE |
| legal_zones (collection) | Geometries zones → perimetre spatial couches predictives | LECTURE |

## 2.2 Dependance directe M2

| Composant M2 | Usage dans M3 | Type |
|-------------|--------------|------|
| poi_nodes (collection) | Activite POIs → series temporelles (frequence, observations) | LECTURE |
| poi_edges (collection) | Connexions → propagation predictions entre POIs | LECTURE |
| poi_scorer | Score POI → ponderation predictions | LECTURE |

## 2.3 Dependances modules existants V5/V6

| Module | Collection / API | Donnee consommee | Type |
|--------|-----------------|-----------------|------|
| predictive_engine | (service interne) | SPECIES_PATTERNS, SEASON_FACTORS, predictions comportementales | LECTURE |
| solunar | (service interne) | compute_solunar() → phases lunaires, hunting_windows, solunar_score | LECTURE |
| weather_fauna_simulation_engine | simulation_alerts | Correlations meteo-faune, optimal_conditions, forecasts | LECTURE |
| hunting_trip_logger | hunting_trips | Sorties reelles → validation predictions, donnees historiques | LECTURE |
| wildlife_behavior_engine | (interne) | Patterns comportementaux → facteur prediction | LECTURE |
| nutrition_v6_interface | (API) | Qualite fourrage saisonniere → facteur prediction nutritionnel | LECTURE |

## 2.4 Dependances ZERO

| Module | Raison |
|--------|--------|
| waypoint_scoring_engine | Scoring waypoints independant |
| cart_engine | Aucun lien |
| payment_engine | Aucun lien |
| camera_engine | Consomme indirectement via M2 (POI type camera) |
| geo_engine | Aucun usage direct |
| geospatial_engine | Aucun usage direct |

---

# 3. ANALYSE DES MODULES SOURCES (LECTURE SEULE)

## 3.1 predictive_engine (V5)

**Fichier** : `modules/predictive_engine/v1/service.py`
**Classe** : `PredictiveService`

| Donnee exploitable | Format | Usage M3 |
|-------------------|--------|----------|
| SPECIES_PATTERNS | Dict (deer, moose, bear, wild_turkey) | dawn_activity, midday_activity, dusk_activity, night_activity → base des courbes 24h |
| SEASON_FACTORS | Dict (mois → multiplicateur 0.5-0.95) | Ponderation saisonniere des predictions |
| predict_hunting_success() | HuntingPrediction (probability, confidence, factors) | Enrichissement couches predictives |
| get_activity_timeline() | List[ActivityTimeline] (hour, score, is_legal) | Timeline 24h → input series temporelles |
| Mapping especes | deer=chevreuil, moose=orignal, bear=ours_noir, wild_turkey=dindon_sauvage | Normalisation noms especes |

**Methode d'integration** : Import direct du service (meme backend), LECTURE SEULE.

## 3.2 solunar (V5)

**Fichier** : `modules/solunar/engine.py`
**Fonction** : `compute_solunar(lat, lng, date_str)`

| Donnee exploitable | Format | Usage M3 |
|-------------------|--------|----------|
| solunar_score | float 0-100 | Facteur prediction (poids solunar) |
| lunar_intensity | float 0-1 | Ponderation intensite lunaire |
| hunting_windows | List (start, end, intensity, color) | Creneaux optimaux lunaires → enrichissement best-times |
| moon.phase_name | str | Contexte prediction (nouvelle lune vs pleine lune) |
| moon.illumination | float % | Facteur activite nocturne vs diurne |
| curve_24h | List 96 pts (moon_altitude, sun_altitude) | Courbe reference solunaire |

**Methode d'integration** : Appel direct `compute_solunar()`, LECTURE SEULE.

## 3.3 weather_fauna_simulation_engine (V5)

**Fichier** : `modules/weather_fauna_simulation_engine/v1/service.py`
**Classe** : `WeatherFaunaSimulationService`

| Donnee exploitable | Format | Usage M3 |
|-------------------|--------|----------|
| optimal_conditions | Dict par espece (temp_min/max, wind_max, pressure_trend) | Conditions optimales → facteur meteo |
| simulate_weather_impact() | WeatherImpactResult (score, multiplier, factors) | Impact meteo → ponderation prediction |
| generate_activity_forecast() | ActivityForecast (daily, best_dates, confidence) | Forecast multi-jours → enrichissement predictions |
| correlation_factors | List (temperature, wind, pressure, precipitation, humidity, moon) | Facteurs de correlation → meteo_fauna_correlator |

**Methode d'integration** : Instanciation du service, appels async, LECTURE SEULE.

---

# 4. SERVICES A CREER

## 4.1 Structure

```
/app/backend/modules/predictive_layer_engine/
    __init__.py
    router.py
    services/
        __init__.py
        timeseries_collector.py         <- Collecte/stockage series temporelles
        predictive_layer_computer.py    <- Calcul couches predictives par zone
        seasonal_trend_analyzer.py      <- Analyse tendances saisonnieres
        meteo_fauna_correlator.py       <- Correlation meteo <-> activite faunique
```

## 4.2 timeseries_collector.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| record_datapoint | (zone_id, species, metric, value, timestamp) → ts_entry | Enregistre un point de donnee |
| get_timeseries | (zone_id, species, metric, start, end) → [values] | Recupere une serie temporelle |
| get_latest | (zone_id, species, metric, limit) → [values] | Derniers N points |
| aggregate_hourly | (zone_id, species, date) → hourly_stats | Moyennes horaires d'une journee |
| ingest_from_poi | (poi_id) → count | Ingestion automatique depuis activite POI M2 |
| ingest_from_trips | (zone_id) → count | Ingestion depuis hunting_trip_logger |

**Metriques collectees** :
- `observation_count` : nombre d'observations fauniques
- `camera_detection` : detections cameras trail
- `activity_index` : indice d'activite composite
- `poi_frequency` : frequence de visite POI

## 4.3 predictive_layer_computer.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| compute_layer | (zone_id, species, target_date) → predictive_layer | Calcule une couche predictive 24h |
| compute_at_point | (lat, lng, species, target_date) → point_prediction | Prediction a un point GPS |
| get_heatmap | (zone_id, species) → heatmap_data | Heatmap de probabilite multi-POI |
| get_best_times | (zone_id, species) → best_times | Meilleurs creneaux horaires |
| _aggregate_sources | (zone_id, species, date) → aggregated | Agregation multi-sources interne |

**Sources agregees par `_aggregate_sources`** :
1. `predictive_engine.SPECIES_PATTERNS` → patterns d'activite de base (LECTURE)
2. `predictive_engine.SEASON_FACTORS` → ponderation saisonniere (LECTURE)
3. `solunar.compute_solunar()` → score/phases lunaires (LECTURE)
4. `weather_fauna_simulation.optimal_conditions` → facteur meteo (LECTURE)
5. `timeseries_data` (M3 interne) → historique observations
6. `poi_nodes` (M2) → activite POIs dans la zone (LECTURE)
7. `nutrition_v6_interface` → qualite fourrage saisonniere (LECTURE via wrapper)

**Formule de prediction horaire** :
```
P(h) = base_activity(h, species)
     * season_factor(month)
     * solunar_factor(h, solunar_data)
     * meteo_factor(conditions, species)
     * historical_factor(h, timeseries)
     * nutrition_factor(zone, season)
```

**Poids des facteurs** :
| Facteur | Poids | Source |
|---------|-------|--------|
| Base activity pattern | 0.25 | predictive_engine.SPECIES_PATTERNS |
| Saison | 0.15 | predictive_engine.SEASON_FACTORS |
| Solunaire | 0.15 | solunar.compute_solunar() |
| Meteo | 0.20 | weather_fauna_simulation.optimal_conditions |
| Historique (timeseries) | 0.15 | M3 timeseries_data |
| Nutritionnel | 0.10 | nutrition_v6_interface (via wrappers) |

## 4.4 seasonal_trend_analyzer.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| analyze_trends | (species, zone_id, years) → trend_data | Analyse tendances sur N annees |
| get_monthly_patterns | (species, zone_id) → [monthly] | Patterns mensuels d'activite |
| get_peak_periods | (species) → [periods] | Periodes de pointe par espece |
| compare_seasons | (species, zone_id, year1, year2) → comparison | Comparaison inter-annuelle |
| detect_anomalies | (species, zone_id) → [anomalies] | Detection d'anomalies d'activite |

**Source de tendances** :
- `timeseries_data` (M3 interne) → historique collecte
- `predictive_engine.SEASON_FACTORS` → baseline saisonniere (LECTURE)
- `hunting_trip_logger.hunting_trips` → sorties reelles (LECTURE)

## 4.5 meteo_fauna_correlator.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| correlate_zone | (zone_id, species) → correlation_matrix | Matrice de correlation meteo-faune |
| get_optimal_conditions | (species) → optimal | Conditions meteo optimales |
| compute_meteo_factor | (conditions, species) → factor | Facteur meteo pour prediction |
| analyze_pressure_impact | (zone_id, species) → impact | Impact pression barometrique |
| forecast_activity_window | (zone_id, species, days) → windows | Fenetres d'activite prevues |

**Consommation** :
- `weather_fauna_simulation_engine.optimal_conditions` → conditions ideales par espece (LECTURE)
- `weather_fauna_simulation_engine.simulate_weather_impact()` → scoring meteo (LECTURE)
- `solunar.compute_solunar()` → facteur lunaire croise avec meteo (LECTURE)

---

# 5. COLLECTIONS MONGODB

## 5.1 Collection : timeseries_data

```json
{
  "ts_id": "uuid-v4",
  "zone_id": "string (ref legal_zones ou territory)",
  "species": "orignal | chevreuil | ours_noir | dindon_sauvage",
  "metric": "observation_count | camera_detection | activity_index | poi_frequency",
  "values": [
    {
      "timestamp": "ISO8601",
      "value": 0.0,
      "source": "poi_graph | hunting_trip | manual",
      "poi_id": "string (optional)"
    }
  ],
  "granularity": "hourly | daily | weekly",
  "latest_value": 0.0,
  "latest_timestamp": "ISO8601",
  "total_points": 0,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Index** : `zone_id` (1), `species` (1), `metric` (1), compound `{zone_id, species, metric}` (unique)

## 5.2 Collection : predictive_layers

```json
{
  "layer_id": "uuid-v4",
  "zone_id": "string (ref legal_zones ou territory)",
  "species": "orignal | chevreuil | ours_noir | dindon_sauvage",
  "target_date": "ISO8601",
  "predictions": [
    {
      "hour": 0,
      "probability": 0.0,
      "confidence": 0.0,
      "factors": {
        "base_activity": 0.0,
        "season": 0.0,
        "solunar": 0.0,
        "meteo": 0.0,
        "historical": 0.0,
        "nutrition": 0.0
      }
    }
  ],
  "aggregation": {
    "peak_probability": 0.0,
    "peak_hour": 0,
    "best_window": {"start": 0, "end": 0},
    "trend": "increasing | stable | decreasing",
    "avg_confidence": 0.0
  },
  "solunar_context": {
    "phase_name": "string",
    "illumination": 0.0,
    "solunar_score": 0.0,
    "hunting_windows": []
  },
  "meteo_context": {
    "activity_multiplier": 0.0,
    "recommendation": "string",
    "limiting_factor": "string"
  },
  "data_sources": ["predictive_engine", "solunar", "weather_simulation", "timeseries", "poi_graph", "nutrition_v6"],
  "poi_count_in_zone": 0,
  "computed_at": "ISO8601",
  "valid_until": "ISO8601"
}
```

**Index** : `zone_id` (1), `species` (1), `target_date` (1), compound `{zone_id, species, target_date}` (unique), `valid_until` (1, TTL)

## 5.3 Collection : seasonal_trends

```json
{
  "trend_id": "uuid-v4",
  "species": "orignal | chevreuil | ours_noir | dindon_sauvage",
  "zone_id": "string",
  "year": 2026,
  "monthly_patterns": [
    {
      "month": 1,
      "activity_index": 0.0,
      "peak_hours": [6, 7, 17, 18],
      "observation_count": 0,
      "trend_vs_previous": "up | stable | down",
      "confidence": 0.0
    }
  ],
  "annual_summary": {
    "peak_month": 10,
    "peak_activity": 0.95,
    "low_month": 7,
    "low_activity": 0.5,
    "total_observations": 0,
    "avg_activity": 0.0
  },
  "computed_at": "ISO8601"
}
```

**Index** : `species` (1), `zone_id` (1), `year` (1), compound `{species, zone_id, year}` (unique)

---

# 6. ENDPOINTS (9 + 1 health)

| # | Methode | Endpoint | Description | Phase |
|---|---------|----------|-------------|-------|
| 0 | GET | /api/v1/predict-layer/health | Sante du module | - |
| 1 | GET | /api/v1/predict-layer/zone/{zone_id}/species/{species} | Couche predictive pour une zone/espece | M3-A |
| 2 | GET | /api/v1/predict-layer/at/{lat}/{lng}/species/{species} | Prediction au point GPS | M3-A |
| 3 | GET | /api/v1/predict-layer/heatmap/{zone_id} | Heatmap de probabilite pour une zone | M3-A |
| 4 | GET | /api/v1/predict-layer/best-times/{zone_id}/{species} | Meilleurs creneaux pour une zone/espece | M3-A |
| 5 | GET | /api/v1/predict-layer/timeseries/{zone_id}/{species} | Serie temporelle brute | M3-B |
| 6 | POST | /api/v1/predict-layer/timeseries/record | Enregistrer un point de serie | M3-B |
| 7 | GET | /api/v1/predict-layer/trends/{species} | Tendances saisonnieres par espece | M3-B |
| 8 | GET | /api/v1/predict-layer/correlation/meteo/{zone_id} | Correlations meteo-faune | M3-B |
| 9 | POST | /api/v1/predict-layer/compute/{zone_id} | Admin: forcer le recalcul d'une couche | M3-B |

**Note** : Le prefixe `/api/v1/predict-layer` est utilise pour les couches predictives ET les series temporelles, conformement a la specification canonique. Les timeseries sont accessible via sous-chemin `/timeseries/`.

## 6.1 Sous-phases d'implementation

| Sous-phase | Endpoints | Fichiers | Contenu |
|-----------|-----------|----------|---------|
| M3-A (Predictive) | 0-4 | predictive_layer_computer.py, router.py | Couches predictives, heatmaps, best-times |
| M3-B (TimeSeries + Correlation) | 5-9 | timeseries_collector.py, seasonal_trend_analyzer.py, meteo_fauna_correlator.py, router.py | Series temporelles, tendances, correlations, compute admin |

---

# 7. POINTS DE FUSION

## 7.1 Fusion SUPRA (P4)

| Point | Source SUPRA | Usage M3 | Methode |
|-------|-------------|----------|---------|
| PF3-S1 | predictive_engine.SPECIES_PATTERNS | Patterns d'activite de base (dawn, midday, dusk, night) → courbe 24h | Import service direct (LECTURE) |
| PF3-S2 | predictive_engine.SEASON_FACTORS | Multiplicateur saisonnier par mois → ponderation | Import service direct (LECTURE) |
| PF3-S3 | strategy_master_engine | Strategies actives → contexte enrichissement | MongoDB lecture pipeline_results |
| PF3-S4 | scoring_engine | Criteres de scoring → ponderation predictions | MongoDB lecture scoring_results |

## 7.2 Fusion Solunaire

| Point | Source | Usage M3 | Methode |
|-------|--------|----------|---------|
| PF3-LUN1 | solunar.compute_solunar() | solunar_score → facteur prediction (poids 0.15) | Appel fonction direct (LECTURE) |
| PF3-LUN2 | solunar.hunting_windows | Fenetres solunaires → enrichissement best-times | Appel fonction direct (LECTURE) |
| PF3-LUN3 | solunar.moon.phase_name | Phase lunaire → contexte prediction | Appel fonction direct (LECTURE) |

## 7.3 Fusion Meteo-Faune

| Point | Source | Usage M3 | Methode |
|-------|--------|----------|---------|
| PF3-MET1 | weather_fauna_simulation.optimal_conditions | Conditions optimales par espece → facteur meteo | Instanciation service (LECTURE) |
| PF3-MET2 | weather_fauna_simulation.simulate_weather_impact() | Impact score → multiplier predictions | Instanciation service (LECTURE) |
| PF3-MET3 | weather_fauna_simulation.correlation_factors | Facteurs de correlation → matrice correlation | Instanciation service (LECTURE) |

## 7.4 Fusion M1 (MAP Intelligence)

| Point | Source M1 | Usage M3 | Methode |
|-------|----------|----------|---------|
| PF3-M1a | boundary_resolver | Province → contexte prediction regional | Appel service direct |
| PF3-M1b | legal_constraint_engine | Periodes legales → filtrage predictions hors-saison | Appel service direct |
| PF3-M1c | legal_zones (collection) | Zones → perimetre spatial couches predictives | MongoDB lecture |

## 7.5 Fusion M2 (POI Graph)

| Point | Source M2 | Usage M3 | Methode |
|-------|----------|----------|---------|
| PF3-M2a | poi_nodes (collection) | Activite POIs → series temporelles (frequence, observations) | MongoDB lecture |
| PF3-M2b | poi_nodes.score | Score POI → ponderation predictions par localisation | MongoDB lecture |
| PF3-M2c | poi_edges (collection) | Connexions → propagation predictions entre POIs connectes | MongoDB lecture |

## 7.6 Fusion Chasse Reelle

| Point | Source | Usage M3 | Methode |
|-------|--------|----------|---------|
| PF3-TRIP1 | hunting_trip_logger.hunting_trips | Sorties reelles → validation predictions, donnees historiques | MongoDB lecture |
| PF3-TRIP2 | hunting_trip_logger.observations | Observations terrain → input series temporelles | MongoDB lecture |

## 7.7 Fusion Nutritionnelle V6

| Point | Source V6 | Usage M3 | Methode |
|-------|----------|----------|---------|
| PF3-N1 | forage_quality_model (wrapper) | Qualite fourrage saisonniere → facteur prediction nutritionnel | Appel wrapper V6 |
| PF3-N2 | phenology_engine (wrapper) | Phase phenologique → impact fourrage temporal | Appel wrapper V6 |
| PF3-N3 | seasonal_metabolism_engine (wrapper) | Etat metabolique → ponderation saisonniere activite | Appel wrapper V6 |
| PF3-N4 | nutrient_deficiency_engine (wrapper) | Deficits nutritionnels → facteur deplacement faune | Appel wrapper V6 |

## 7.8 Fusion M3 → M2 (retour)

| Point | Source M3 | Usage dans M2 | Methode |
|-------|----------|--------------|---------|
| PF3-RET1 | predictive_layers | Predictions → enrichissement futur score POI | MongoDB lecture par M2 (autonome) |

**Note** : PF3-RET1 est un point de fusion passif. M3 ecrit dans `predictive_layers`, M2 peut le consommer de facon autonome. AUCUNE modification de M2 n'est requise dans M3.

**TOTAL POINTS DE FUSION : 22**

---

# 8. CHAINE M1 → M2 → M3 (Flux de donnees)

```
M1 (National Data Harvester)
    |
    |--- legal_zones.regulations ────────────────────────> M3: filtrage periodes legales
    |--- legal_zones.geometry ───────────────────────────> M3: perimetre spatial couches
    |--- boundary_resolver.province ─────────────────────> M3: contexte regional
    |
    v
M2 (POI Graph Engine)
    |
    |--- poi_nodes.properties.frequency ─────────────────> M3: input timeseries
    |--- poi_nodes.properties.species_observed ──────────> M3: especes par zone
    |--- poi_nodes.score.global ─────────────────────────> M3: ponderation predictions
    |--- poi_edges.connections ──────────────────────────> M3: propagation predictions
    |
    v
M3 (Predictive Layer Engine)
    |
    |--- predictive_layers (output) ─────────────────────> M4: creneaux optimaux itineraire
    |--- timeseries_data (output) ───────────────────────> M4: profil historique utilisateur
    |--- seasonal_trends (output) ───────────────────────> M5: tendances dans paquet offline
    |--- heatmap (API output) ──────────────────────────> M4: overlay carte navigation
    |
    v
M4 (Adaptive Navigation) / M5 (Offline Terrain Intelligence)
```

---

# 9. ANTI-DOUBLON

## 9.1 Modules consommes en LECTURE SEULE

| Module | Collection / API | Donnee |
|--------|-----------------|--------|
| predictive_engine | Service PredictiveService | SPECIES_PATTERNS, SEASON_FACTORS, predictions |
| solunar | Fonction compute_solunar() | Scores, phases, fenetres solunaires |
| weather_fauna_simulation_engine | Service WeatherFaunaSimulationService | optimal_conditions, correlations, forecasts |
| hunting_trip_logger | hunting_trips (collection) | Sorties, observations, durees |
| M1 national_data_harvester | legal_zones, boundary_resolver | Zones, provinces, contraintes legales |
| M2 poi_graph_engine | poi_nodes, poi_edges | Activite POIs, connexions |
| wildlife_behavior_engine | (interne) | Patterns comportementaux |

## 9.2 Modules INTERDITS de recreation dans M3

| Module | Raison | Action si besoin |
|--------|--------|-----------------|
| predictive_engine | Predictions comportementales existent deja | LIRE patterns, NE PAS reimplementer la logique de prediction |
| solunar | Calendrier solunaire existe | APPELER compute_solunar(), NE PAS recalculer positions lunaires |
| weather_fauna_simulation_engine | Correlations meteo-faune existent | LIRE optimal_conditions, NE PAS refaire les simulations |
| scoring_engine | Scoring global existe | LIRE criteres, NE PAS recalculer |
| territory_engine | Gestion zones existe | NE PAS reimplementer gestion de zones |
| M2 poi_scorer | Scoring POI existe | LIRE scores, NE PAS recalculer |

## 9.3 Ce que M3 apporte de NOUVEAU (non-doublon)

| Fonctionnalite | Justification |
|----------------|---------------|
| Couches predictives geospatiales par zone | N'existe pas — predictive_engine fait des predictions ponctuelles, pas geospatiales |
| Series temporelles historiques structurees | N'existe pas — aucune collection timeseries dans le codebase |
| Heatmaps de probabilite multi-POI | N'existe pas — weather_fauna fait des forecasts ponctuels, pas des heatmaps |
| Agregation multi-sources (6 facteurs ponderes) | N'existe pas — chaque module fait sa prediction isolement |
| Tendances saisonnieres multi-annuelles | N'existe pas — predictive_engine a des SEASON_FACTORS statiques |
| Meilleurs creneaux combines (solunar + meteo + historique) | N'existe pas — solunar et weather sont separes |

---

# 10. ANTI-DOUBLON NUTRITIONNEL

## 10.1 Sources nutritionnelles

| Source V6 | Consommation dans M3 | Interdiction |
|-----------|---------------------|-------------|
| forage_quality_model (wrapper V5 → vegetation_forage_engine) | LECTURE qualite fourrage saisonniere → facteur prediction nutritionnel | NE PAS recalculer phenologie, mineraux vegetaux |
| phenology_engine (wrapper V5) | LECTURE phase phenologique → impact temporal fourrage | NE PAS recalculer stades vegetatifs |
| seasonal_metabolism_engine (wrapper V5) | LECTURE etat metabolique espece → ponderation saisonniere | NE PAS recalculer besoins energetiques |
| nutrient_deficiency_engine (wrapper V5) | LECTURE deficits nutritionnels → facteur deplacement faune | NE PAS recalculer couverture besoins |
| vegetation_forage_engine (wrapper V5) | LECTURE qualite fourrage → heatmap nutritionnelle | NE PAS recalculer analyse vegetale |
| nutrition_engine P0 (NDVI) | LECTURE indirecte via forage_quality | NE PAS recalculer NDVI |

## 10.2 Regle stricte

**Tout enrichissement nutritionnel d'une prediction DOIT passer par `nutrition_v6_interface`.**
Aucun import direct des moteurs V5 dans `predictive_layer_engine`.

---

# 11. PLAN D'IMPLEMENTATION

## 11.1 Sequence

```
M3-A : Couches Predictives                    [PRIORITE 1]
    +--→ predictive_layer_computer.py
    +--→ router.py (endpoints 0-4)
    +--→ Tests rapides (curl)
    +--→ Rapport intermediaire

M3-B : Series Temporelles + Correlations     [PRIORITE 2]
    +--→ timeseries_collector.py
    +--→ seasonal_trend_analyzer.py
    +--→ meteo_fauna_correlator.py
    +--→ router.py (endpoints 5-9)
    +--→ Tests rapides (curl)
    +--→ Rapport intermediaire

M3-C : Integration Tests                     [OBLIGATOIRE]
    +--→ test_predictive_layer.py
    +--→ test_timeseries_engine.py
    +--→ Non-regression (M1, M2, Nutrition V6, Cart V2, Phases I-V)
    +--→ RAPPORT FINAL → VALIDATION STEEVE-MAX
```

## 11.2 Estimation

| Phase | Fichiers crees | Endpoints | Lignes | Duree |
|-------|---------------|-----------|--------|-------|
| M3-A | 3 (init, computer, router) | 5 | ~350 | Phase 1 |
| M3-B | 3 (collector, trend, correlator) | 5 | ~400 | Phase 2 |
| M3-C | 2 (tests) | 0 | ~250 | Phase 3 |
| **TOTAL** | **8** | **10** | **~1000** | **1 session** |

---

# 12. RISQUES BCE-4X

## 12.1 Risques identifies

| # | Risque | Probabilite | Impact | Mitigation |
|---|--------|-------------|--------|-----------|
| R1 | Donnees insuffisantes pour prediction (zones vierges) | ELEVE | MODERE | Fallback sur SEASON_FACTORS de predictive_engine (baseline statique) |
| R2 | Calcul heatmap couteux (>100 POIs par zone) | MODERE | MODERE | Limite 100 POIs par heatmap, cache MongoDB TTL 1h |
| R3 | Correlation meteo imprecise (pas de donnees meteo temps reel) | MODERE | FAIBLE | Multi-facteurs (solunar + meteo simulee + historique) |
| R4 | Latence compute_solunar() | FAIBLE | FAIBLE | Calcul une fois par requete, cache resultat |
| R5 | Volume timeseries_data croissant | MODERE | MODERE | Granularite max daily, purge auto > 2 ans |
| R6 | Regression modules V5 (predictive_engine, solunar) | TRES FAIBLE | CRITIQUE | ZERO modification V5, lecture seule |
| R7 | Incoherence noms especes (deer vs chevreuil) | FAIBLE | MODERE | Mapping normalise dans M3 |

## 12.2 Garanties BCE-4X

| Garantie | Mecanisme |
|----------|-----------|
| ZERO LOSS | Module NOUVEAU, aucune modification d'existant |
| ZERO REGRESSION | Tests non-regression sur 98 tests existants |
| ZERO DOUBLON | Section 9 documente les interdictions |
| ZERO INTERPRETATION | Ce plan est la seule specification d'implementation |

---

# 13. PROTOCOLES DE ROLLBACK

## 13.1 Rollback M3-A

| Etape | Action | Verification |
|-------|--------|-------------|
| 1 | Retirer import `poi_graph_engine_router` de routers.py (NON — c'est M2, pas M3) | - |
| 1 | Retirer import `predictive_layer_engine_router` de routers.py | Ligne d'import supprimee |
| 2 | Retirer entry CORE_ROUTERS correspondante | Entry supprimee |
| 3 | Supprimer dossier `/app/backend/modules/predictive_layer_engine/` | `ls` confirme suppression |
| 4 | Verifier que backend demarre sans erreur | `curl /health` → 200 |
| 5 | Relancer suite de tests 98/98 | pytest → 98 PASS |

## 13.2 Rollback M3-B

| Etape | Action | Verification |
|-------|--------|-------------|
| 1 | Reverter router.py aux endpoints M3-A uniquement | Endpoints 5-9 retires |
| 2 | Supprimer fichiers M3-B (collector, trend, correlator) | Services retires |
| 3 | Verifier endpoints M3-A toujours fonctionnels | `curl /api/v1/predict-layer/health` → 200 |

## 13.3 Rollback Total M3

| Etape | Action | Verification |
|-------|--------|-------------|
| 1 | Rollback M3-A (ci-dessus) | Backend clean |
| 2 | Drop collections MongoDB | `db.timeseries_data.drop()`, `db.predictive_layers.drop()`, `db.seasonal_trends.drop()` |
| 3 | Supprimer tests M3 | `test_predictive_layer.py`, `test_timeseries_engine.py` |
| 4 | Relancer suite complete | pytest → 98 PASS (retour etat M2) |

## 13.4 Principe de rollback

**AUCUNE donnee existante n'est affectee.** Le rollback M3 consiste uniquement a :
- Supprimer les NOUVEAUX fichiers
- Retirer les NOUVELLES lignes de routers.py
- Drop les NOUVELLES collections MongoDB
- L'etat du systeme revient exactement a l'etat post-M2

---

# 14. IMPACTS PREVUS SUR M4 ET M5

## 14.1 Impact sur M4 (Adaptive User Profile + Navigation IA)

| Composant M4 | Consommation M3 | Description |
|-------------|-----------------|-------------|
| NavigationPlanner | predictive_layers → creneaux optimaux | L'itineraire utilise les best-times M3 pour planifier les heures d'arrivee aux POIs |
| RouteOptimizer | heatmap → ponderation routes | Les routes sont optimisees vers les zones a forte probabilite d'activite |
| ContextualAdvisor | predictions horaires → conseils en temps reel | "Activite orignal prevue FORTE a 06:30 dans votre secteur" |
| UserProfileLearner | timeseries_data → historique d'activite | L'apprentissage du profil utilise les series temporelles de M3 |

**Dependance M4 → M3** : LECTURE SEULE via MongoDB et API. M4 fonctionne en mode degrade si M3 n'est pas deploye (fallback predictions ponctuelles de predictive_engine).

## 14.2 Impact sur M5 (Offline Mode Ultra + Terrain Intelligence)

| Composant M5 | Consommation M3 | Description |
|-------------|-----------------|-------------|
| OfflinePackager | predictive_layers → inclus dans paquet | Les couches predictives sont empaquetees pour usage offline |
| OfflinePackager | seasonal_trends → inclus dans paquet | Les tendances saisonnieres sont incluses offline |
| TerrainAnalyzer | heatmap → overlay activite faunique | La heatmap enrichit l'analyse terrain |
| SpeciesHabitatMapper | seasonal_trends → suitability saisonniere | Les tendances alimentent le score d'habitat |

**Dependance M5 → M3** : LECTURE SEULE via MongoDB. M5 inclut les donnees M3 dans les paquets offline si disponibles, sinon le paquet est genere sans couche predictive.

## 14.3 Schema de dependance M3 → M4/M5

```
M3 (Predictive Layer Engine)
    |
    |--- predictive_layers ──────> M4.NavigationPlanner (creneaux)
    |                         └──> M4.RouteOptimizer (heatmap)
    |                         └──> M5.OfflinePackager (inclusion)
    |
    |--- timeseries_data ────────> M4.UserProfileLearner (historique)
    |
    |--- seasonal_trends ────────> M4.ContextualAdvisor (contexte)
    |                         └──> M5.SpeciesHabitatMapper (suitability)
    |
    |--- heatmap (API) ──────────> M4.ContextualAdvisor (conseils)
    |                         └──> M5.TerrainAnalyzer (overlay)
```

## 14.4 Fallback M4/M5 sans M3

| Module | Comportement sans M3 | Impact |
|--------|---------------------|--------|
| M4 | Utilise predictive_engine directement (predictions ponctuelles, pas geospatiales) | MODERE — perte creneaux combines et heatmaps |
| M5 | Paquet offline sans couche predictive | FAIBLE — reste fonctionnel avec terrain + POIs |

---

# 15. TESTS

## 15.1 Tests d'integration M3

| # | Fichier | Couverture |
|---|---------|------------|
| T5 | test_predictive_layer.py | Health, couche zone/espece, prediction GPS, heatmap, best-times, compute admin |
| T6 | test_timeseries_engine.py | Enregistrement point, serie temporelle, tendances, correlations meteo, non-regression M1/M2 |

## 15.2 Tests de non-regression

| Suite | Tests | Statut attendu |
|-------|-------|---------------|
| Phases I-V | 33/33 | PASS |
| Cart V2 | 25/25 | PASS |
| M2 POI Graph | 40/40 | PASS |
| M1 | curl endpoints | 200 OK |
| Nutrition V6 | curl endpoints | 200 OK |
| **Total** | **98+** | **ZERO FAIL** |

---

# 16. INVENTAIRE MODIFICATIONS

## 16.1 Fichiers a CREER (8)

| # | Fichier | Phase |
|---|---------|-------|
| 1 | modules/predictive_layer_engine/__init__.py | M3-A |
| 2 | modules/predictive_layer_engine/router.py | M3-A/B |
| 3 | modules/predictive_layer_engine/services/__init__.py | M3-A |
| 4 | modules/predictive_layer_engine/services/predictive_layer_computer.py | M3-A |
| 5 | modules/predictive_layer_engine/services/timeseries_collector.py | M3-B |
| 6 | modules/predictive_layer_engine/services/seasonal_trend_analyzer.py | M3-B |
| 7 | modules/predictive_layer_engine/services/meteo_fauna_correlator.py | M3-B |
| 8 | modules/routers.py (MODIFICATION : +import +registration) | M3-A |

## 16.2 Fichiers existants NON MODIFIES

- predictive_engine/* (ZERO modification)
- solunar/* (ZERO modification)
- weather_fauna_simulation_engine/* (ZERO modification)
- hunting_trip_logger/* (ZERO modification)
- wildlife_behavior_engine/* (ZERO modification)
- national_data_harvester/* (ZERO modification, M1)
- poi_graph_engine/* (ZERO modification, M2)
- nutrition_v6_interface/* (ZERO modification)
- scoring_engine/* (ZERO modification)
- territory_engine/* (ZERO modification)
- Tous les 85+ modules existants

## 16.3 Collections MongoDB

| # | Collection | Action | Index |
|---|-----------|--------|-------|
| 1 | timeseries_data | CREER | zone_id, species, metric, compound unique |
| 2 | predictive_layers | CREER | zone_id, species, target_date, compound unique, valid_until TTL |
| 3 | seasonal_trends | CREER | species, zone_id, year, compound unique |

---

## PROCHAINES ETAPES

Ce plan requiert la **validation explicite de STEEVE-MAX** avant toute execution.

Apres validation, l'execution suivra la sequence :
M3-A (Predictive) → M3-B (TimeSeries + Correlation) → M3-C (Tests)

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : M3_PREDICTIVE_LAYER_PLAN 1.0.0
**References** : BIONIC_V6_MAP_INTELLIGENCE_PLAN v1.1.0, M2_POI_GRAPH_PLAN v1.0.0, M2_RAPPORT_FINAL v1.0.0
**Code modifie** : AUCUN (plan uniquement)
**Merge main** : STRICTEMENT INTERDIT
**Points de fusion documentes** : 22
**Modules existants modifies** : ZERO
