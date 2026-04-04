# BIONIC_V6_MAP_INTELLIGENCE_PLAN — PLAN D'INTELLIGENCE CARTOGRAPHIQUE
## Directive x6400-A-STEEVE_MAX — Version 1.0.0
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-04 | Merge MAIN : STRICTEMENT INTERDIT
### Aucun code modifie tant que ce plan n'est pas valide

---

# TABLE DES MATIERES

1. [SYNTHESE EXECUTIVE](#1-synthese-executive)
2. [AUDIT MODULES EXISTANTS](#2-audit-modules-existants)
3. [M1 — NATIONAL DATA HARVESTER + LEGAL BOUNDARY ENGINE](#3-m1)
4. [M2 — BIONIC POI GRAPH](#4-m2)
5. [M3 — PREDICTIVE LAYER ENGINE + TIME-SERIES ENGINE](#5-m3)
6. [M4 — ADAPTIVE USER PROFILE + NAVIGATION OUTDOOR IA](#6-m4)
7. [M5 — OFFLINE MODE ULTRA + TERRAIN & SPECIES INTELLIGENCE](#7-m5)
8. [SEQUENCE D'EXECUTION](#8-sequence-dexecution)
9. [RISQUES ET DEPENDANCES](#9-risques-et-dependances)
10. [INVENTAIRE GLOBAL](#10-inventaire-global)

---

# 1. SYNTHESE EXECUTIVE

## 1.1 Objectif

Le plan MAP INTELLIGENCE vise a transformer le systeme cartographique BIONIC d'un outil
de visualisation en une plateforme d'intelligence spatiale complete. Les 5 sous-phases
(M1-M5) couvrent l'ensemble de la chaine : de la collecte de donnees nationales brutes
jusqu'a l'intelligence terrain hors-ligne, en passant par les graphes de points d'interet,
la prediction temporelle, et la navigation IA adaptative.

## 1.2 Principes

| Principe | Application |
|----------|-------------|
| ZERO LOSS | Aucun module existant supprime ou modifie |
| ZERO REGRESSION | geo_engine, geospatial_engine, territory_engine restent inchanges |
| ZERO INTERPRETATION | Implementation stricte de ce plan |
| Modules decouples | Communication via MongoDB bridges, jamais import direct |
| SUPRA connexion | Chaque phase definit ses points d'integration avec SUPRA (P4) |
| P6 connexion | Chaque phase definit ses points d'integration avec Territoire (P6) |

## 1.3 Metriques globales

| Metrique | M1 | M2 | M3 | M4 | M5 | TOTAL |
|----------|----|----|----|----|----|----|
| Services a CREER | 4 | 3 | 4 | 4 | 4 | 19 |
| Collections MongoDB | 3 | 2 | 3 | 2 | 3 | 13 |
| Endpoints a CREER | 8 | 10 | 9 | 11 | 8 | 46 |
| Tests a CREER | 2 | 2 | 2 | 2 | 2 | 10 |
| Lignes estimees | ~600 | ~700 | ~800 | ~750 | ~650 | ~3500 |

---

# 2. AUDIT MODULES EXISTANTS

## 2.1 Modules cartographiques actifs

| Module | Version | Statut | Role |
|--------|---------|--------|------|
| geo_engine | v6 | ACTIF | Geocodage, zones, reverse-geocoding |
| geospatial_engine | v6 | ACTIF | Analyses spatiales avancees, buffers, intersections |
| territory_engine | v6 | ACTIF | Gestion de territoires, zones de chasse |
| data_layers | v6 | ACTIF | Couches de donnees (ecoforestry, behavioral, 3D, simulation) |
| waypoint_engine | v6 | ACTIF | Points de passage GPS |
| waypoint_scoring_engine | v6 | ACTIF | Scoring des waypoints |
| soil_engine | v6 | ACTIF | Analyse des sols, geologie |

## 2.2 Modules intelligence actifs (connexions SUPRA P4)

| Module | Role | Connexion MAP |
|--------|------|---------------|
| predictive_engine | Predictions comportementales | M3 (Time-Series) |
| wildlife_behavior_engine | Comportement faunique | M5 (Species Intelligence) |
| weather_fauna_simulation_engine | Simulation meteo/faune | M3 (Predictive Layer) |
| scoring_engine | Scoring global | M2 (POI scoring) |
| solunar | Calendrier solunar | M3 (Time-Series) |
| legal_time_engine | Periodes legales de chasse | M1 (Legal Boundary) |
| hunting_trip_logger | Journal de sorties | M4 (Adaptive Profile) |
| bionic_ecological_engine | Intelligence ecologique | M5 (Terrain Intelligence) |

## 2.3 Modules Territoire (connexions P6)

| Module | Role | Connexion MAP |
|--------|------|---------------|
| camera_engine | Cameras trail | M2 (POI source) |
| live_heading_engine | Direction en temps reel | M4 (Navigation IA) |
| tracking_engine | Suivi GPS | M4 (Navigation) |

## 2.4 Garantie ZERO LOSS

Les 82+ modules existants NE SONT PAS modifies. Les phases M1-M5 creent exclusivement
de NOUVEAUX modules qui communiquent avec l'existant via MongoDB bridges.

---

# 3. M1 — NATIONAL DATA HARVESTER + LEGAL BOUNDARY ENGINE

## 3.1 Objectif

Collecter, normaliser et servir les donnees publiques nationales (limites administratives,
zones de chasse reglementaires, reserves fauniques, ZEC, pourvoiries) et les contraintes
legales geospatiales (periodes, quotas, restrictions).

## 3.2 Services a CREER

### Module : `national_data_harvester/`

| # | Service | Fichier | Description |
|---|---------|---------|-------------|
| 1 | HarvestScheduler | services/harvest_scheduler.py | Planification et execution des collectes periodiques |
| 2 | DataNormalizer | services/data_normalizer.py | Normalisation des formats (GeoJSON, Shapefile, KML → format BIONIC) |
| 3 | BoundaryResolver | services/boundary_resolver.py | Resolution des limites administratives et legales |
| 4 | LegalConstraintEngine | services/legal_constraint_engine.py | Moteur de contraintes legales (periodes, quotas, zones interdites) |

### Structure

```
/app/backend/modules/national_data_harvester/
    __init__.py
    router.py
    services/
        __init__.py
        harvest_scheduler.py
        data_normalizer.py
        boundary_resolver.py
        legal_constraint_engine.py
```

## 3.3 Collections MongoDB

| # | Collection | Schema simplifie | Description |
|---|-----------|-----------------|-------------|
| 1 | national_boundaries | {boundary_id, type, name, geometry: GeoJSON, province, source, updated_at} | Limites administratives nationales |
| 2 | legal_zones | {zone_id, type: "zec|reserve|pourvoirie|public", name, geometry, regulations: [], season_dates: {}, quotas: {}} | Zones reglementaires avec contraintes |
| 3 | harvest_logs | {harvest_id, source, status, records_processed, errors, started_at, completed_at} | Journal des collectes de donnees |

### Schema detaille : national_boundaries

```json
{
  "boundary_id": "uuid-v4",
  "type": "province | region | mrc | municipalite | zone_chasse",
  "name": "string",
  "code": "string (code officiel)",
  "geometry": {
    "type": "Polygon | MultiPolygon",
    "coordinates": [[]]
  },
  "properties": {
    "province": "QC | ON | NB | ...",
    "area_km2": 0,
    "population": 0
  },
  "source": "string (URL source)",
  "source_format": "geojson | shapefile | kml",
  "updated_at": "ISO8601",
  "created_at": "ISO8601"
}
```

### Schema detaille : legal_zones

```json
{
  "zone_id": "uuid-v4",
  "type": "zec | reserve_faunique | pourvoirie | terre_publique | terre_privee",
  "name": "string",
  "code": "string",
  "geometry": {
    "type": "Polygon | MultiPolygon",
    "coordinates": [[]]
  },
  "regulations": [
    {
      "species": "orignal | chevreuil | ours_noir | ...",
      "weapon_type": "arme_feu | arc | arbalete",
      "season_start": "ISO8601",
      "season_end": "ISO8601",
      "quota": 1,
      "restrictions": ["string"]
    }
  ],
  "access": {
    "type": "libre | droit_acces | reservation | prive",
    "cost": 0,
    "contact": "string"
  },
  "updated_at": "ISO8601"
}
```

## 3.4 Endpoints

| # | Methode | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | GET | /api/v1/map-intel/boundaries | Liste des limites par type/province |
| 2 | GET | /api/v1/map-intel/boundaries/{boundary_id} | Detail d'une limite |
| 3 | GET | /api/v1/map-intel/boundaries/at/{lat}/{lng} | Limites contenant un point GPS |
| 4 | GET | /api/v1/map-intel/legal-zones | Liste des zones legales par type |
| 5 | GET | /api/v1/map-intel/legal-zones/{zone_id} | Detail d'une zone legale |
| 6 | GET | /api/v1/map-intel/legal-zones/at/{lat}/{lng} | Zones legales contenant un point |
| 7 | GET | /api/v1/map-intel/legal-check/{lat}/{lng}/{species} | Verification de legalite pour un point/espece |
| 8 | POST | /api/v1/map-intel/harvest/trigger | Admin: declencher une collecte |

## 3.5 Connexions SUPRA (P4) et Territoire (P6)

| Source | Destination | Methode | Donnee |
|--------|-------------|---------|--------|
| M1 → legal_time_engine | MongoDB bridge | legal_zones regulations → periodes actives |
| M1 → territory_engine | MongoDB bridge | national_boundaries → zones selectionnables |
| M1 → geo_engine | MongoDB bridge | boundaries geometry → geocodage inverse enrichi |
| M1 ← predictive_engine | Lecture | predictions par zone legale |

## 3.6 Tests

| # | Fichier | Couverture |
|---|---------|------------|
| T1 | test_national_data_harvester.py | Endpoints 1-6, normalisation, resolution |
| T2 | test_legal_boundary_engine.py | Endpoint 7-8, contraintes, validation legale |

## 3.7 Risques et dependances

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Donnees publiques indisponibles | MODERE | ELEVE | Cache MongoDB local, derniere version valide |
| Format de donnees non standard | MODERE | MODERE | Pipeline de normalisation flexible |
| Volume de donnees GeoJSON | FAIBLE | MODERE | Index 2dsphere MongoDB |
| Dep: legal_time_engine | AUCUNE | - | Lecture seule, zero couplage |

---

# 4. M2 — BIONIC POI GRAPH

## 4.1 Objectif

Construire un graphe de Points d'Interet (POI) interconnectes : cameras trail, observations,
stands, caches, points d'eau, ravages, corridors de deplacement, sources de nourriture.
Le graphe permet une analyse relationnelle entre POIs et genere des scores de potentiel.

## 4.2 Services a CREER

### Module : `poi_graph_engine/`

| # | Service | Fichier | Description |
|---|---------|---------|-------------|
| 1 | POIGraphBuilder | services/poi_graph_builder.py | Construction et maintenance du graphe de POIs |
| 2 | POIScorer | services/poi_scorer.py | Scoring multi-critere de chaque POI |
| 3 | POIRelationResolver | services/poi_relation_resolver.py | Calcul des relations spatiales entre POIs |

### Structure

```
/app/backend/modules/poi_graph_engine/
    __init__.py
    router.py
    services/
        __init__.py
        poi_graph_builder.py
        poi_scorer.py
        poi_relation_resolver.py
```

## 4.3 Collections MongoDB

| # | Collection | Schema simplifie | Description |
|---|-----------|-----------------|-------------|
| 1 | poi_nodes | {poi_id, type, name, location: GeoJSON Point, properties, score, connections: [], zone_id} | Noeuds du graphe |
| 2 | poi_edges | {edge_id, from_poi, to_poi, relation_type, distance_m, weight, properties} | Aretes du graphe |

### Schema detaille : poi_nodes

```json
{
  "poi_id": "uuid-v4",
  "type": "camera | observation | stand | cache | point_eau | ravage | corridor | nourriture | saline",
  "name": "string",
  "description": "string",
  "location": {
    "type": "Point",
    "coordinates": [lng, lat]
  },
  "altitude_m": 0,
  "properties": {
    "species_observed": ["orignal", "chevreuil"],
    "last_activity": "ISO8601",
    "frequency": 0,
    "confidence": 0.0
  },
  "score": {
    "global": 0,
    "accessibility": 0,
    "activity": 0,
    "strategic": 0
  },
  "connections": ["poi_id_1", "poi_id_2"],
  "zone_id": "string (ref legal_zones)",
  "user_id": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### Schema detaille : poi_edges

```json
{
  "edge_id": "uuid-v4",
  "from_poi": "poi_id",
  "to_poi": "poi_id",
  "relation_type": "proximity | corridor | line_of_sight | water_flow | trail",
  "distance_m": 0,
  "elevation_diff_m": 0,
  "weight": 0.0,
  "properties": {
    "terrain_type": "forest | field | water | rock",
    "traversability": 0.0,
    "species_usage": ["orignal"]
  },
  "created_at": "ISO8601"
}
```

## 4.4 Endpoints

| # | Methode | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | GET | /api/v1/poi-graph/nodes | Liste des POIs avec filtres (type, zone, species) |
| 2 | POST | /api/v1/poi-graph/nodes | Creer un POI |
| 3 | GET | /api/v1/poi-graph/nodes/{poi_id} | Detail d'un POI avec connexions |
| 4 | PATCH | /api/v1/poi-graph/nodes/{poi_id} | Mettre a jour un POI |
| 5 | DELETE | /api/v1/poi-graph/nodes/{poi_id} | Supprimer un POI |
| 6 | GET | /api/v1/poi-graph/near/{lat}/{lng} | POIs a proximite avec distances |
| 7 | GET | /api/v1/poi-graph/edges/{poi_id} | Aretes connectees a un POI |
| 8 | POST | /api/v1/poi-graph/edges | Creer une arete entre 2 POIs |
| 9 | GET | /api/v1/poi-graph/cluster/{lat}/{lng}/{radius_m} | Cluster de POIs dans un rayon |
| 10 | GET | /api/v1/poi-graph/score/{poi_id} | Score detaille d'un POI |

## 4.5 Connexions SUPRA (P4) et Territoire (P6)

| Source | Destination | Methode | Donnee |
|--------|-------------|---------|--------|
| M2 ← camera_engine | MongoDB bridge | cameras trail → POI nodes type "camera" |
| M2 ← waypoint_engine | MongoDB bridge | waypoints → POI nodes |
| M2 → scoring_engine | MongoDB bridge | POI scores → scoring global |
| M2 → territory_engine | MongoDB bridge | clusters POI → analyse territoire |
| M2 ← M1 | MongoDB bridge | legal_zones → enrichissement POI context |
| M2 → predictive_engine | MongoDB bridge | POI activity patterns → predictions |

## 4.6 Tests

| # | Fichier | Couverture |
|---|---------|------------|
| T3 | test_poi_graph_crud.py | Endpoints 1-5, creation, mise a jour, suppression |
| T4 | test_poi_graph_spatial.py | Endpoints 6-10, proximite, clusters, scoring |

## 4.7 Risques et dependances

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Volume de POIs eleve | MODERE | MODERE | Index 2dsphere + pagination |
| Calcul de distances couteux | FAIBLE | MODERE | Pre-calcul des aretes dans un batch |
| Graphe deconnecte | FAIBLE | FAIBLE | Algorithme de cluster auto-connect |
| Dep: camera_engine, waypoint_engine | AUCUNE | - | Lecture seule MongoDB |

---

# 5. M3 — PREDICTIVE LAYER ENGINE + TIME-SERIES ENGINE

## 5.1 Objectif

Ajouter une couche de prediction temporelle sur la carte : predictions d'activite faunique
par zone et par heure, series temporelles historiques, tendances saisonnieres, et correlations
meteo-faune.

## 5.2 Services a CREER

### Module : `predictive_layer_engine/`

| # | Service | Fichier | Description |
|---|---------|---------|-------------|
| 1 | TimeSeriesCollector | services/timeseries_collector.py | Collecte et stockage des series temporelles |
| 2 | PredictiveLayerComputer | services/predictive_layer_computer.py | Calcul des couches predictives par zone |
| 3 | SeasonalTrendAnalyzer | services/seasonal_trend_analyzer.py | Analyse des tendances saisonnieres |
| 4 | MeteoFaunaCorrelator | services/meteo_fauna_correlator.py | Correlation meteo ↔ activite faunique |

### Structure

```
/app/backend/modules/predictive_layer_engine/
    __init__.py
    router.py
    services/
        __init__.py
        timeseries_collector.py
        predictive_layer_computer.py
        seasonal_trend_analyzer.py
        meteo_fauna_correlator.py
```

## 5.3 Collections MongoDB

| # | Collection | Schema simplifie | Description |
|---|-----------|-----------------|-------------|
| 1 | timeseries_data | {ts_id, metric, zone_id, species, values: [{timestamp, value}], granularity} | Series temporelles brutes |
| 2 | predictive_layers | {layer_id, zone_id, species, predictions: [{hour, probability, confidence}], computed_at} | Couches predictives calculees |
| 3 | seasonal_trends | {trend_id, species, zone_id, year, monthly_patterns: [{month, peak_hours, activity_index}]} | Tendances saisonnieres |

### Schema detaille : predictive_layers

```json
{
  "layer_id": "uuid-v4",
  "zone_id": "string (ref legal_zones ou territory)",
  "species": "orignal | chevreuil | ours_noir | dindon_sauvage",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[]]
  },
  "predictions": [
    {
      "hour": 0,
      "probability": 0.0,
      "confidence": 0.0,
      "factors": ["meteo", "solunar", "saison"]
    }
  ],
  "aggregation": {
    "peak_probability": 0.0,
    "peak_hour": 0,
    "best_window": {"start": 0, "end": 0},
    "trend": "increasing | stable | decreasing"
  },
  "data_sources": ["timeseries", "solunar", "weather"],
  "computed_at": "ISO8601",
  "valid_until": "ISO8601"
}
```

## 5.4 Endpoints

| # | Methode | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | GET | /api/v1/predict-layer/zone/{zone_id}/species/{species} | Couche predictive pour une zone/espece |
| 2 | GET | /api/v1/predict-layer/at/{lat}/{lng}/species/{species} | Prediction au point GPS |
| 3 | GET | /api/v1/predict-layer/heatmap/{zone_id} | Heatmap de probabilite pour une zone |
| 4 | GET | /api/v1/predict-layer/best-times/{zone_id}/{species} | Meilleurs creneaux pour une zone/espece |
| 5 | GET | /api/v1/timeseries/{zone_id}/{species} | Serie temporelle brute |
| 6 | POST | /api/v1/timeseries/record | Enregistrer un point de serie |
| 7 | GET | /api/v1/timeseries/trends/{species} | Tendances saisonnieres par espece |
| 8 | GET | /api/v1/predict-layer/correlation/meteo/{zone_id} | Correlations meteo-faune |
| 9 | POST | /api/v1/predict-layer/compute/{zone_id} | Admin: forcer le recalcul d'une couche |

## 5.5 Connexions SUPRA (P4) et Territoire (P6)

| Source | Destination | Methode | Donnee |
|--------|-------------|---------|--------|
| M3 ← predictive_engine | MongoDB bridge | predictions existantes → timeseries input |
| M3 ← weather_fauna_simulation_engine | MongoDB bridge | simulations meteo → correlations |
| M3 ← solunar | MongoDB bridge | calendrier solunar → facteur prediction |
| M3 → territory_engine | MongoDB bridge | couches predictives → overlay carte |
| M3 → M2 | MongoDB bridge | predictions → enrichissement score POI |
| M3 ← hunting_trip_logger | MongoDB bridge | sorties reelles → validation predictions |

## 5.6 Tests

| # | Fichier | Couverture |
|---|---------|------------|
| T5 | test_predictive_layer.py | Endpoints 1-4, couches, heatmap, best-times |
| T6 | test_timeseries_engine.py | Endpoints 5-9, enregistrement, tendances, correlations |

## 5.7 Risques et dependances

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Donnees insuffisantes pour prediction | ELEVE | MODERE | Fallback sur moyennes saisonnieres historiques |
| Calcul heatmap couteux | MODERE | MODERE | Cache Redis ou MongoDB TTL |
| Correlation meteo imprecise | MODERE | FAIBLE | Multi-facteurs (solunar + meteo + historique) |
| Dep: predictive_engine, solunar | AUCUNE | - | Lecture seule |

---

# 6. M4 — ADAPTIVE USER PROFILE + NAVIGATION OUTDOOR IA

## 6.1 Objectif

Creer des profils utilisateur adaptatifs qui apprennent des habitudes de chasse
(especes preferees, zones frequentees, heures actives, preferences meteo), et un
systeme de navigation outdoor assiste par IA qui suggere des itineraires optimaux
vers les POIs les plus prometteurs.

## 6.2 Services a CREER

### Module : `adaptive_navigation_engine/`

| # | Service | Fichier | Description |
|---|---------|---------|-------------|
| 1 | UserProfileLearner | services/user_profile_learner.py | Apprentissage du profil chasseur |
| 2 | NavigationPlanner | services/navigation_planner.py | Planification d'itineraires intelligents |
| 3 | RouteOptimizer | services/route_optimizer.py | Optimisation multi-critere des routes |
| 4 | ContextualAdvisor | services/contextual_advisor.py | Conseils contextuels IA en temps reel |

### Structure

```
/app/backend/modules/adaptive_navigation_engine/
    __init__.py
    router.py
    services/
        __init__.py
        user_profile_learner.py
        navigation_planner.py
        route_optimizer.py
        contextual_advisor.py
```

## 6.3 Collections MongoDB

| # | Collection | Schema simplifie | Description |
|---|-----------|-----------------|-------------|
| 1 | hunter_profiles | {profile_id, user_id, species_preferences, zone_preferences, time_preferences, skill_level, history_stats} | Profils adaptatifs |
| 2 | navigation_sessions | {session_id, user_id, route, waypoints, status, started_at, metrics} | Sessions de navigation |

### Schema detaille : hunter_profiles

```json
{
  "profile_id": "uuid-v4",
  "user_id": "string",
  "species_preferences": [
    {
      "species": "orignal",
      "frequency": 0.7,
      "success_rate": 0.3,
      "preferred_weapon": "arme_feu",
      "preferred_zones": ["zone_id_1"]
    }
  ],
  "zone_preferences": [
    {
      "zone_id": "string",
      "visit_count": 10,
      "last_visit": "ISO8601",
      "satisfaction_score": 0.8
    }
  ],
  "time_preferences": {
    "preferred_hours": [5, 6, 7, 16, 17, 18],
    "preferred_days": ["samedi", "dimanche"],
    "preferred_season_weeks": [38, 39, 40, 41, 42]
  },
  "meteo_preferences": {
    "min_temp_c": -5,
    "max_temp_c": 15,
    "wind_tolerance_kmh": 20,
    "rain_tolerance": "light"
  },
  "skill_level": "debutant | intermediaire | avance | expert",
  "equipment": {
    "has_gps": true,
    "has_radio": false,
    "mobility": "a_pied | vtt | bateau"
  },
  "history_stats": {
    "total_trips": 0,
    "total_hours": 0,
    "species_harvested": {},
    "avg_distance_km": 0
  },
  "updated_at": "ISO8601"
}
```

### Schema detaille : navigation_sessions

```json
{
  "session_id": "uuid-v4",
  "user_id": "string",
  "profile_id": "string",
  "target_species": "orignal",
  "route": {
    "type": "LineString",
    "coordinates": [[lng, lat], ...]
  },
  "waypoints": [
    {
      "poi_id": "string",
      "name": "string",
      "location": {"type": "Point", "coordinates": [lng, lat]},
      "poi_score": 0,
      "eta_minutes": 0,
      "priority": "high | medium | low"
    }
  ],
  "optimization_criteria": {
    "priority": "score | distance | accessibility",
    "max_distance_km": 10,
    "max_duration_hours": 4,
    "avoid_terrain": ["water", "rock"]
  },
  "status": "planned | active | completed | abandoned",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "metrics": {
    "distance_walked_km": 0,
    "duration_hours": 0,
    "pois_visited": 0,
    "observations_made": 0
  }
}
```

## 6.4 Endpoints

| # | Methode | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | GET | /api/v1/nav-intel/profile/{user_id} | Profil adaptatif complet |
| 2 | PATCH | /api/v1/nav-intel/profile/{user_id} | Mettre a jour preferences |
| 3 | POST | /api/v1/nav-intel/profile/{user_id}/learn | Declencher apprentissage du profil |
| 4 | POST | /api/v1/nav-intel/plan-route | Planifier un itineraire optimal |
| 5 | GET | /api/v1/nav-intel/plan-route/{session_id} | Detail d'un itineraire planifie |
| 6 | POST | /api/v1/nav-intel/optimize | Optimiser un itineraire existant |
| 7 | GET | /api/v1/nav-intel/suggestions/{user_id} | Suggestions personnalisees (zones, creneaux) |
| 8 | GET | /api/v1/nav-intel/advice/{user_id}/{lat}/{lng} | Conseil contextuel a une position |
| 9 | POST | /api/v1/nav-intel/session/start | Demarrer une session de navigation |
| 10 | POST | /api/v1/nav-intel/session/{session_id}/end | Terminer une session |
| 11 | GET | /api/v1/nav-intel/session/{session_id}/status | Statut session active |

## 6.5 Connexions SUPRA (P4) et Territoire (P6)

| Source | Destination | Methode | Donnee |
|--------|-------------|---------|--------|
| M4 ← hunting_trip_logger | MongoDB bridge | sorties → apprentissage profil |
| M4 ← M2 | MongoDB bridge | POI graph → destinations itineraire |
| M4 ← M3 | MongoDB bridge | predictions → creneaux optimaux |
| M4 ← M1 | MongoDB bridge | zones legales → contraintes itineraire |
| M4 → live_heading_engine | MongoDB bridge | itineraire → cap de navigation |
| M4 → tracking_engine | MongoDB bridge | session active → tracking GPS |
| M4 ← strategy_master_engine | MongoDB bridge | strategies → enrichissement conseils |

## 6.6 Tests

| # | Fichier | Couverture |
|---|---------|------------|
| T7 | test_adaptive_profile.py | Endpoints 1-3, 7, profil adaptatif, preferences, apprentissage |
| T8 | test_navigation_planner.py | Endpoints 4-6, 8-11, planification, optimisation, sessions |

## 6.7 Risques et dependances

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Profil insuffisant (nouvel utilisateur) | ELEVE | MODERE | Profil par defaut base sur la region |
| Itineraire hors sentier dangereux | FAIBLE | ELEVE | Contraintes terrain + avertissements |
| Calcul route couteux | MODERE | MODERE | Pre-calcul des segments frequents |
| Dep: M1, M2, M3 | M1-M3 doivent etre deployes | ELEVE | Fallback sur donnees statiques |

---

# 7. M5 — OFFLINE MODE ULTRA + TERRAIN & SPECIES INTELLIGENCE

## 7.1 Objectif

Permettre l'utilisation complete de l'intelligence cartographique en mode hors-ligne
(zones sans couverture reseau), avec pre-telechargement des tuiles, POIs, predictions
et donnees terrain. En parallele, construire un moteur d'intelligence terrain (topographie,
vegetation, hydrographie) croise avec l'intelligence des especes.

## 7.2 Services a CREER

### Module : `offline_terrain_intelligence/`

| # | Service | Fichier | Description |
|---|---------|---------|-------------|
| 1 | OfflinePackager | services/offline_packager.py | Empaquetage des donnees pour usage offline |
| 2 | TerrainAnalyzer | services/terrain_analyzer.py | Analyse topographique et vegetale |
| 3 | SpeciesHabitatMapper | services/species_habitat_mapper.py | Cartographie des habitats par espece |
| 4 | SyncManager | services/sync_manager.py | Gestion de la synchronisation online ↔ offline |

### Structure

```
/app/backend/modules/offline_terrain_intelligence/
    __init__.py
    router.py
    services/
        __init__.py
        offline_packager.py
        terrain_analyzer.py
        species_habitat_mapper.py
        sync_manager.py
```

## 7.3 Collections MongoDB

| # | Collection | Schema simplifie | Description |
|---|-----------|-----------------|-------------|
| 1 | offline_packages | {package_id, user_id, zone_id, layers: [], size_mb, created_at, expires_at} | Paquets de donnees offline |
| 2 | terrain_analyses | {analysis_id, zone_id, topography, vegetation, hydrology, habitat_suitability} | Analyses terrain |
| 3 | species_habitats | {habitat_id, species, zone_id, suitability_score, geometry, factors} | Habitats cartographies par espece |

### Schema detaille : offline_packages

```json
{
  "package_id": "uuid-v4",
  "user_id": "string",
  "zone_id": "string",
  "zone_name": "string",
  "center": {"type": "Point", "coordinates": [lng, lat]},
  "radius_km": 10,
  "layers": [
    {
      "type": "tiles | pois | predictions | boundaries | terrain",
      "record_count": 0,
      "size_kb": 0,
      "version": "ISO8601"
    }
  ],
  "total_size_mb": 0,
  "status": "generating | ready | expired | error",
  "created_at": "ISO8601",
  "expires_at": "ISO8601",
  "download_url": "string"
}
```

### Schema detaille : terrain_analyses

```json
{
  "analysis_id": "uuid-v4",
  "zone_id": "string",
  "geometry": {"type": "Polygon", "coordinates": [[]]},
  "topography": {
    "min_elevation_m": 0,
    "max_elevation_m": 0,
    "avg_slope_deg": 0,
    "aspect_dominant": "north | south | east | west",
    "terrain_ruggedness": 0.0
  },
  "vegetation": {
    "dominant_type": "conifere | feuillu | mixte | coupe",
    "canopy_density": 0.0,
    "understory_density": 0.0,
    "age_class": "jeune | mature | vieux"
  },
  "hydrology": {
    "water_bodies": [{"type": "lac | riviere | ruisseau | marecage", "distance_m": 0}],
    "drainage": "bon | modere | mauvais",
    "water_proximity_score": 0.0
  },
  "habitat_suitability": {
    "orignal": 0.0,
    "chevreuil": 0.0,
    "ours_noir": 0.0,
    "dindon_sauvage": 0.0
  },
  "computed_at": "ISO8601"
}
```

### Schema detaille : species_habitats

```json
{
  "habitat_id": "uuid-v4",
  "species": "orignal | chevreuil | ours_noir | dindon_sauvage",
  "zone_id": "string",
  "suitability_score": 0.0,
  "geometry": {"type": "Polygon", "coordinates": [[]]},
  "factors": {
    "vegetation_match": 0.0,
    "water_access": 0.0,
    "elevation_match": 0.0,
    "food_availability": 0.0,
    "cover_quality": 0.0,
    "human_disturbance": 0.0
  },
  "seasonal_variation": {
    "spring": 0.0,
    "summer": 0.0,
    "fall": 0.0,
    "winter": 0.0
  },
  "data_sources": ["ecoforestry", "terrain", "observations"],
  "computed_at": "ISO8601"
}
```

## 7.4 Endpoints

| # | Methode | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | POST | /api/v1/offline/generate/{zone_id} | Generer un paquet offline pour une zone |
| 2 | GET | /api/v1/offline/packages/{user_id} | Liste des paquets offline d'un utilisateur |
| 3 | GET | /api/v1/offline/packages/{package_id}/status | Statut de generation d'un paquet |
| 4 | POST | /api/v1/offline/sync | Synchroniser les donnees offline → online |
| 5 | GET | /api/v1/terrain/{zone_id}/analysis | Analyse terrain complete d'une zone |
| 6 | GET | /api/v1/terrain/at/{lat}/{lng} | Analyse terrain a un point GPS |
| 7 | GET | /api/v1/terrain/habitat/{species}/{zone_id} | Carte d'habitat pour une espece/zone |
| 8 | GET | /api/v1/terrain/habitat/compare/{zone_id} | Comparaison habitats multi-especes |

## 7.5 Connexions SUPRA (P4) et Territoire (P6)

| Source | Destination | Methode | Donnee |
|--------|-------------|---------|--------|
| M5 ← M1 | MongoDB bridge | boundaries → inclus dans paquet offline |
| M5 ← M2 | MongoDB bridge | POI graph → inclus dans paquet offline |
| M5 ← M3 | MongoDB bridge | predictions → inclus dans paquet offline |
| M5 ← M4 | MongoDB bridge | itineraires planifies → inclus offline |
| M5 ← soil_engine | MongoDB bridge | donnees sols → facteur habitat |
| M5 ← bionic_ecological_engine | MongoDB bridge | donnees ecologiques → facteur habitat |
| M5 ← wildlife_behavior_engine | MongoDB bridge | comportements → suitability scoring |
| M5 ← ecoforestry_engine | MongoDB bridge | donnees ecoforestry → vegetation analysis |
| M5 → territory_engine | MongoDB bridge | habitats → couche carte territoire |

## 7.6 Tests

| # | Fichier | Couverture |
|---|---------|------------|
| T9 | test_offline_mode.py | Endpoints 1-4, generation, sync, download |
| T10 | test_terrain_species_intel.py | Endpoints 5-8, topographie, habitats, comparaison |

## 7.7 Risques et dependances

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Taille paquet offline trop grande | MODERE | MODERE | Compression, selection de couches, rayon limite |
| Donnees terrain insuffisantes | MODERE | MODERE | Fallback sur donnees generiques par biome |
| Sync conflit (offline edits vs online) | FAIBLE | ELEVE | Strategie last-write-wins avec historique |
| Dep: M1-M4 + soil + eco + wildlife | Toutes phases precedentes | ELEVE | Chaque couche est optionnelle dans le paquet |

---

# 8. SEQUENCE D'EXECUTION

## 8.1 Ordre strict

```
M1 — NATIONAL DATA HARVESTER + LEGAL BOUNDARY    [PRIORITE 1]
    |                                              [Base pour toutes les phases]
    +--→ harvest_scheduler.py
    +--→ data_normalizer.py
    +--→ boundary_resolver.py
    +--→ legal_constraint_engine.py
    +--→ 8 endpoints
    +--→ Tests T1, T2
    +--→ VALIDATION STEEVE-MAX
    |
M2 — BIONIC POI GRAPH                             [PRIORITE 2]
    |                                              [Dep: M1 pour zones legales]
    +--→ poi_graph_builder.py
    +--→ poi_scorer.py
    +--→ poi_relation_resolver.py
    +--→ 10 endpoints
    +--→ Tests T3, T4
    +--→ VALIDATION STEEVE-MAX
    |
M3 — PREDICTIVE LAYER + TIME-SERIES               [PRIORITE 3]
    |                                              [Dep: M1, M2 pour zones et POIs]
    +--→ timeseries_collector.py
    +--→ predictive_layer_computer.py
    +--→ seasonal_trend_analyzer.py
    +--→ meteo_fauna_correlator.py
    +--→ 9 endpoints
    +--→ Tests T5, T6
    +--→ VALIDATION STEEVE-MAX
    |
M4 — ADAPTIVE PROFILE + NAVIGATION IA             [PRIORITE 4]
    |                                              [Dep: M1, M2, M3]
    +--→ user_profile_learner.py
    +--→ navigation_planner.py
    +--→ route_optimizer.py
    +--→ contextual_advisor.py
    +--→ 11 endpoints
    +--→ Tests T7, T8
    +--→ VALIDATION STEEVE-MAX
    |
M5 — OFFLINE MODE ULTRA + TERRAIN INTELLIGENCE    [PRIORITE 5]
    |                                              [Dep: M1-M4 pour paquetage]
    +--→ offline_packager.py
    +--→ terrain_analyzer.py
    +--→ species_habitat_mapper.py
    +--→ sync_manager.py
    +--→ 8 endpoints
    +--→ Tests T9, T10
    +--→ VALIDATION STEEVE-MAX
```

## 8.2 Estimation

| Phase | Services | Collections | Endpoints | Tests | Lignes | Duree estimee |
|-------|----------|-------------|-----------|-------|--------|--------------|
| M1 | 4 | 3 | 8 | 2 | ~600 | 1 session |
| M2 | 3 | 2 | 10 | 2 | ~700 | 1 session |
| M3 | 4 | 3 | 9 | 2 | ~800 | 1-2 sessions |
| M4 | 4 | 2 | 11 | 2 | ~750 | 1-2 sessions |
| M5 | 4 | 3 | 8 | 2 | ~650 | 1 session |
| **TOTAL** | **19** | **13** | **46** | **10** | **~3500** | **5-7 sessions** |

## 8.3 Points de validation STEEVE-MAX

| Point | Phase | Delivrable | Critere |
|-------|-------|-----------|---------|
| V1 | M1 | 8 endpoints operationnels + T1/T2 pass | Donnees nationales accessibles |
| V2 | M2 | 10 endpoints + T3/T4 pass | Graphe POI fonctionnel |
| V3 | M3 | 9 endpoints + T5/T6 pass | Predictions temporelles operationnelles |
| V4 | M4 | 11 endpoints + T7/T8 pass | Navigation IA fonctionnelle |
| V5 | M5 | 8 endpoints + T9/T10 pass | Mode offline + terrain intel operationnels |

---

# 9. RISQUES ET DEPENDANCES

## 9.1 Matrice de dependances inter-phases

```
M1 ──→ M2 ──→ M3 ──→ M4 ──→ M5
 │      │      │      │      │
 │      │      │      │      └──→ soil_engine, bionic_ecological, wildlife_behavior
 │      │      │      └──────→ hunting_trip_logger, live_heading, tracking
 │      │      └──────────→ predictive_engine, solunar, weather_fauna_sim
 │      └──────────────→ camera_engine, waypoint_engine, scoring_engine
 └──────────────────→ legal_time_engine, territory_engine, geo_engine
```

## 9.2 Risques globaux

| # | Risque | Probabilite | Impact | Phase | Mitigation |
|---|--------|-------------|--------|-------|-----------|
| G1 | Performance MongoDB avec indexes GeoJSON | MODERE | ELEVE | M1-M5 | 2dsphere indexes, pagination, TTL cache |
| G2 | Volume de donnees geospatiales | MODERE | MODERE | M1, M5 | Compression, simplification geometries |
| G3 | Temps de calcul predictions | MODERE | MODERE | M3, M4 | Calculs batch, pre-calcul nocturne |
| G4 | Complexite du graphe POI | FAIBLE | MODERE | M2 | Limiter connexions par noeud |
| G5 | Taille paquets offline | MODERE | MODERE | M5 | Selection couches, compression, rayon max |

## 9.3 Dependances externes

| Dependance | Phase | Impact | Alternative |
|-----------|-------|--------|------------|
| Donnees MFFP Quebec | M1 | ELEVE | Donnees OpenStreetMap comme fallback |
| Donnees topographiques | M5 | MODERE | SRTM/ASTER open data |
| Donnees ecoforestry | M5 | MODERE | Donnees SIGEOM Quebec |

---

# 10. INVENTAIRE GLOBAL

## 10.1 Modules a CREER (4)

| # | Module | Phase | Services | Endpoints |
|---|--------|-------|----------|-----------|
| 1 | national_data_harvester | M1 | 4 | 8 |
| 2 | poi_graph_engine | M2 | 3 | 10 |
| 3 | predictive_layer_engine | M3 | 4 | 9 |
| 4 | adaptive_navigation_engine | M4 | 4 | 11 |
| 5 | offline_terrain_intelligence | M5 | 4 | 8 |

## 10.2 Collections MongoDB a CREER (13)

| # | Collection | Phase |
|---|-----------|-------|
| 1 | national_boundaries | M1 |
| 2 | legal_zones | M1 |
| 3 | harvest_logs | M1 |
| 4 | poi_nodes | M2 |
| 5 | poi_edges | M2 |
| 6 | timeseries_data | M3 |
| 7 | predictive_layers | M3 |
| 8 | seasonal_trends | M3 |
| 9 | hunter_profiles | M4 |
| 10 | navigation_sessions | M4 |
| 11 | offline_packages | M5 |
| 12 | terrain_analyses | M5 |
| 13 | species_habitats | M5 |

## 10.3 Endpoints a CREER (46)

| Phase | Endpoints |
|-------|-----------|
| M1 | 8 (boundaries, legal-zones, legal-check, harvest) |
| M2 | 10 (POI CRUD, near, edges, cluster, score) |
| M3 | 9 (predict-layer, timeseries, trends, correlation) |
| M4 | 11 (profile, plan-route, optimize, suggestions, advice, session) |
| M5 | 8 (offline generate/packages/sync, terrain analysis/habitat) |

## 10.4 Tests a CREER (10 fichiers)

| # | Fichier | Phase | Couverture |
|---|---------|-------|------------|
| T1 | test_national_data_harvester.py | M1 | Boundaries, normalisation |
| T2 | test_legal_boundary_engine.py | M1 | Legal check, contraintes |
| T3 | test_poi_graph_crud.py | M2 | POI CRUD |
| T4 | test_poi_graph_spatial.py | M2 | Proximite, clusters |
| T5 | test_predictive_layer.py | M3 | Couches, heatmap |
| T6 | test_timeseries_engine.py | M3 | Series, tendances |
| T7 | test_adaptive_profile.py | M4 | Profil, preferences |
| T8 | test_navigation_planner.py | M4 | Routes, sessions |
| T9 | test_offline_mode.py | M5 | Paquets, sync |
| T10 | test_terrain_species_intel.py | M5 | Terrain, habitats |

## 10.5 Modules existants NON MODIFIES (confirmation ZERO LOSS)

Les modules suivants ne sont PAS modifies :
- geo_engine, geospatial_engine, territory_engine, data_layers
- waypoint_engine, waypoint_scoring_engine, soil_engine
- predictive_engine, wildlife_behavior_engine, weather_fauna_simulation_engine
- scoring_engine, solunar, legal_time_engine
- hunting_trip_logger, camera_engine, live_heading_engine, tracking_engine
- bionic_ecological_engine, ecoforestry_engine
- Tous les 82+ modules existants

---

## PROCHAINES ETAPES

Ce plan requiert la **validation explicite de STEEVE-MAX** avant toute modification de code.

Apres validation, l'execution suivra la sequence definie en Section 8 :
M1 → M2 → M3 → M4 → M5

Chaque phase est independante (avec fallbacks) mais optimale en sequence.
La validation STEEVE-MAX est requise entre chaque phase.

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : BIONIC_V6_MAP_INTELLIGENCE_PLAN 1.0.0
**References** : IMPLEMENTATION_PLAN_V1, AUBO_V2, SUPRA_PIPELINE_V1
**Code modifie** : AUCUN (plan uniquement)
**Merge main** : STRICTEMENT INTERDIT
