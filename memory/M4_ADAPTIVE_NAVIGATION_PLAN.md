# M4 — ADAPTIVE USER PROFILE + OUTDOOR NAVIGATION IA — PLAN D'EXECUTION DETAILLE
## Directive x7100-PREP-M4 — Preparation M4
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-05 | Merge MAIN : STRICTEMENT INTERDIT
### AUCUN CODE MODIFIE tant que ce plan n'est pas valide par STEEVE-MAX

---

# TABLE DES MATIERES

1. [OBJECTIF ET PERIMETRE](#1-objectif-et-perimetre)
2. [ARCHITECTURE ADAPTIVE USER PROFILE (AUP)](#2-aup)
3. [ARCHITECTURE OUTDOOR NAVIGATION IA](#3-navigation)
4. [DEPENDANCES M1→M2→M3→M4](#4-dependances)
5. [POINTS DE FUSION](#5-points-de-fusion)
6. [REGLES D'APPRENTISSAGE ADAPTATIF](#6-regles-apprentissage)
7. [REGLES DE NAVIGATION CONTEXTUELLE](#7-regles-navigation)
8. [COLLECTIONS MONGODB](#8-collections)
9. [ENDPOINTS (11 + 1 health)](#9-endpoints)
10. [IMPACTS DFL / EVENTBUS / DATACONTRACTS](#10-impacts-dashboard)
11. [ANTI-DOUBLON](#11-anti-doublon)
12. [PLAN D'IMPLEMENTATION](#12-plan-implementation)
13. [RISQUES BCE-4X](#13-risques)
14. [PROTOCOLES DE ROLLBACK](#14-rollback)
15. [IMPACTS PREVUS SUR M5](#15-impacts-m5)
16. [TESTS](#16-tests)
17. [INVENTAIRE MODIFICATIONS](#17-inventaire)

---

# 1. OBJECTIF ET PERIMETRE

## 1.1 Objectif

Construire un moteur d'intelligence adaptative qui :
1. **Apprend** les habitudes et preferences du chasseur (especes, zones, horaires, meteo, equipement)
2. **Planifie** des itineraires optimaux vers les POIs les plus prometteurs
3. **Optimise** les routes selon multi-criteres (score, distance, accessibilite, predictions M3)
4. **Conseille** en temps reel selon la position GPS, les conditions et le profil

## 1.2 Perimetre

| Element | Valeur |
|---------|--------|
| Module | `adaptive_navigation_engine/` (NOUVEAU) |
| Services | 4 (UserProfileLearner, NavigationPlanner, RouteOptimizer, ContextualAdvisor) |
| Collections MongoDB | 2 (hunter_profiles, navigation_sessions) |
| Endpoints | 11 + 1 health = 12 |
| Tests | 2 fichiers (T7, T8) |
| Code V5 modifie | ZERO |
| Modules existants modifies | ZERO |
| Backend M1/M2/M3 modifies | ZERO |

## 1.3 Principes

| Principe | Application |
|----------|-------------|
| ZERO LOSS | Module NOUVEAU, aucune modification d'existant |
| ZERO REGRESSION | Non-regression sur 144 tests existants |
| ZERO DOUBLON | recommendation_engine consomme en LECTURE, jamais recree |
| ZERO INTERPRETATION | Ce plan est la seule specification |
| ZERO CONTRADICTION | Profil adaptatif coherent avec M3 predictions |
| ZERO OBSOLESCENCE | Profil mis a jour automatiquement apres chaque session |

---

# 2. ARCHITECTURE ADAPTIVE USER PROFILE (AUP)

## 2.1 Service : UserProfileLearner

### Responsabilites
- Creer et maintenir le profil adaptatif du chasseur
- Apprendre des sorties passees (hunting_trip_logger) en LECTURE
- Mettre a jour les preferences d'espece, zone, horaire, meteo
- Calculer le skill_level et les statistiques historiques

### Fonctions

| Fonction | Signature | Description |
|----------|-----------|-------------|
| get_or_create_profile | (user_id) → profile | Recupere ou cree le profil avec valeurs par defaut |
| update_preferences | (user_id, updates) → profile | Met a jour les preferences explicites |
| learn_from_history | (user_id) → learning_result | Apprentissage automatique depuis sorties |
| compute_skill_level | (profile) → skill_level | Calcul du niveau base sur l'historique |
| get_species_affinity | (user_id) → affinities | Affinites espece calculees |

### Schema du profil adaptatif

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
    "mobility": "a_pied"
  },
  "history_stats": {
    "total_trips": 0,
    "total_hours": 0,
    "species_harvested": {},
    "avg_distance_km": 0
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

# 3. ARCHITECTURE OUTDOOR NAVIGATION IA

## 3.1 Service : NavigationPlanner

### Responsabilites
- Planifier des itineraires en integrant POIs M2, predictions M3, contraintes M1
- Generer des waypoints ordonnes par score/proximite
- Estimer temps de parcours et ETA par waypoint

### Fonctions

| Fonction | Signature | Description |
|----------|-----------|-------------|
| plan_route | (user_id, target_species, zone_id, criteria) → session | Planification itineraire intelligent |
| get_session | (session_id) → session | Detail d'une session planifiee |
| start_session | (session_id) → session | Demarrer une session active |
| end_session | (session_id, metrics) → session | Terminer une session avec metriques |
| get_session_status | (session_id) → status | Statut session active |

### Logique de planification

```
plan_route(user_id, species, zone_id):
  1. Recuperer profil adaptatif (AUP)
  2. Recuperer POIs de la zone (M2 poi_nodes, LECTURE)
  3. Scorer les POIs avec predictions M3 (M3 layer, LECTURE)
  4. Filtrer par contraintes legales (M1 legal_check, LECTURE)
  5. Appliquer preferences profil (heures, meteo, equipement)
  6. Ordonner les waypoints par score_combine
  7. Calculer la route et les ETA
  8. Persister la session
```

## 3.2 Service : RouteOptimizer

### Responsabilites
- Optimiser un itineraire existant selon criteres dynamiques
- Re-scorer les waypoints en temps reel (conditions changeantes)
- Adapter la route en fonction de la position courante

### Fonctions

| Fonction | Signature | Description |
|----------|-----------|-------------|
| optimize_route | (session_id, criteria) → optimized_session | Re-optimisation multi-critere |
| score_waypoint | (poi_data, profile, prediction) → score | Score combine waypoint |

### Criteres d'optimisation

| Critere | Poids defaut | Source |
|---------|-------------|--------|
| prediction_score | 0.30 | M3 P(h) probability |
| poi_score | 0.25 | M2 poi_scorer |
| profile_affinity | 0.20 | AUP species_preferences |
| distance | 0.15 | Haversine (M2 relation_resolver) |
| legal_compliance | 0.10 | M1 legal_check |

## 3.3 Service : ContextualAdvisor

### Responsabilites
- Generer des conseils contextuels IA bases sur la position GPS
- Fusionner predictions M3, conditions solunaires, meteo, profil
- Suggestions personnalisees (zones, creneaux, especes)

### Fonctions

| Fonction | Signature | Description |
|----------|-----------|-------------|
| get_advice | (user_id, lat, lng) → advice | Conseil contextuel a une position |
| get_suggestions | (user_id) → suggestions | Suggestions personnalisees |

### Structure du conseil

```json
{
  "position": {"lat": 0, "lng": 0},
  "species": "orignal",
  "prediction": {
    "current_probability": 0.65,
    "peak_hour": 6,
    "trend": "increasing"
  },
  "solunar": {
    "score": 72,
    "phase": "Gibbeuse croissante",
    "next_window": "06:30-08:30"
  },
  "advice": [
    {"type": "prediction", "priority": "high", "text": "Activite orignal prevue FORTE a 06:30"},
    {"type": "solunar", "priority": "medium", "text": "Fenetre solunaire intense 06:30-08:30"},
    {"type": "zone", "priority": "low", "text": "3 POIs a moins de 500m"}
  ],
  "nearby_pois": [
    {"poi_id": "...", "name": "...", "distance_m": 250, "score": 0.8}
  ]
}
```

---

# 4. DEPENDANCES M1 → M2 → M3 → M4

## 4.1 Dependance directe M1

| Composant M1 | Usage dans M4 | Type |
|-------------|--------------|------|
| boundary_resolver | Province → contexte regional profil | LECTURE |
| legal_constraint_engine | Periodes legales → filtrage itineraire | LECTURE |
| legal_zones (collection) | Geometries zones → contraintes route | LECTURE |

## 4.2 Dependance directe M2

| Composant M2 | Usage dans M4 | Type |
|-------------|--------------|------|
| poi_nodes (collection) | POIs → destinations itineraire | LECTURE |
| poi_edges (collection) | Connexions → chemins entre POIs | LECTURE |
| poi_scorer | Score POI → scoring waypoints | LECTURE |
| cluster (API) | Densite POIs → qualite zone | LECTURE |

## 4.3 Dependance directe M3

| Composant M3 | Usage dans M4 | Type |
|-------------|--------------|------|
| predictive_layers (collection) | P(h) → creneaux optimaux itineraire | LECTURE |
| timeseries_data (collection) | Historique → validation profil adaptatif | LECTURE |
| seasonal_trends (collection) | Tendances → suggestions saisonnieres | LECTURE |
| best_times (API) | Meilleurs creneaux → enrichissement conseils | LECTURE |
| heatmap (API) | Probabilites → ponderation waypoints | LECTURE |

## 4.4 Dependances modules existants V5/V6

| Module | Collection / API | Donnee consommee | Type |
|--------|-----------------|-----------------|------|
| hunting_trip_logger | hunting_trips | Sorties passees → apprentissage profil | LECTURE |
| live_heading_engine | (interne) | Cap navigation → session active | LECTURE (futur) |
| tracking_engine | (interne) | Tracking GPS → metriques session | LECTURE (futur) |
| strategy_master_engine | pipeline_results | Strategies → enrichissement conseils | LECTURE |
| recommendation_engine | (interne) | Recommandations existantes | LECTURE |
| solunar | (interne) | Score solunaire → conseils contextuels | LECTURE |
| weather_fauna_simulation | (interne) | Conditions meteo → conseils | LECTURE |
| nutrition_v6_interface | (API) | Qualite fourrage → ponderation itineraire nutritionnel | LECTURE |

---

# 5. POINTS DE FUSION

## 5.1 Fusion SUPRA (P4)

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-S1 | strategy_master_engine | Strategies actives → enrichissement conseils | MongoDB LECTURE |
| PF4-S2 | recommendation_engine | Recommandations existantes → verification non-doublon | LECTURE |

## 5.2 Fusion Solunaire

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-LUN1 | solunar.compute_solunar() | Score solunaire → conseil contextuel | Appel direct |
| PF4-LUN2 | solunar.hunting_windows | Fenetres optimales → enrichissement planning | Appel direct |

## 5.3 Fusion Meteo

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-MET1 | weather_fauna_simulation.optimal_conditions | Conditions optimales → filtrage meteo profil | LECTURE |

## 5.4 Fusion M1

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-M1a | boundary_resolver | Province → contexte profil | Appel direct |
| PF4-M1b | legal_constraint_engine | Contraintes legales → filtrage route | Appel direct |

## 5.5 Fusion M2

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-M2a | poi_nodes | POIs zone → waypoints itineraire | MongoDB LECTURE |
| PF4-M2b | poi_scorer | Score POI → scoring waypoints | MongoDB LECTURE |
| PF4-M2c | poi_edges | Connexions → chemins entre POIs | MongoDB LECTURE |
| PF4-M2d | cluster | Densite POIs → qualite zone | API LECTURE |

## 5.6 Fusion M3

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-M3a | predictive_layers | P(h) → creneaux optimaux | MongoDB LECTURE |
| PF4-M3b | timeseries_data | Historique → validation profil | MongoDB LECTURE |
| PF4-M3c | seasonal_trends | Tendances → suggestions saison | MongoDB LECTURE |
| PF4-M3d | best_times (API) | Creneaux combines → enrichissement planning | API LECTURE |
| PF4-M3e | heatmap (API) | Probabilites → ponderation waypoints | API LECTURE |

## 5.7 Fusion Chasse

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-TRIP1 | hunting_trip_logger.hunting_trips | Sorties → apprentissage profil | MongoDB LECTURE |

## 5.8 Fusion Nutritionnelle V6

| Point | Source | Usage M4 | Methode |
|-------|--------|----------|---------|
| PF4-N1 | nutrition_v6_interface.forage_quality | Fourrage → ponderation route nutritionnelle | API LECTURE |
| PF4-N2 | nutrition_v6_interface.wildlife_attractiveness | Attractivite espece → scoring waypoints | API LECTURE |

**TOTAL POINTS DE FUSION : 19**

---

# 6. REGLES D'APPRENTISSAGE ADAPTATIF

## 6.1 Sources d'apprentissage

| Source | Donnees extraites | Impact sur profil |
|--------|------------------|-------------------|
| hunting_trips | especes ciblees, zones visitees, heures, duree, succes | species_preferences, zone_preferences, time_preferences |
| navigation_sessions (M4) | waypoints visites, metriques, satisfaction | zone_preferences.satisfaction_score |
| M3 timeseries_data | patterns d'activite | validation preferences horaires |

## 6.2 Regles d'apprentissage

| # | Regle | Formule |
|---|-------|---------|
| AUP-L1 | Frequence espece | freq(species) = trips_targeting(species) / total_trips |
| AUP-L2 | Taux de succes | success_rate(species) = harvests(species) / trips_targeting(species) |
| AUP-L3 | Heures preferees | preferred_hours = mode(start_hour) sur les 20 dernieres sorties |
| AUP-L4 | Zones preferees | zone_pref = top_N zones par visit_count, ponderes par satisfaction |
| AUP-L5 | Tolerance meteo | meteo_pref = percentile 80 des conditions des sorties passees |
| AUP-L6 | Niveau skill | skill = f(total_trips, success_rate_global, avg_distance_km) |
| AUP-L7 | Distance moyenne | avg_distance = mean(distance_walked_km) sur toutes les sorties |

## 6.3 Calcul du skill_level

| Critere | Debutant | Intermediaire | Avance | Expert |
|---------|----------|---------------|--------|--------|
| total_trips | < 5 | 5-20 | 20-50 | > 50 |
| success_rate | < 0.1 | 0.1-0.25 | 0.25-0.4 | > 0.4 |
| avg_distance_km | < 2 | 2-5 | 5-10 | > 10 |

## 6.4 Frequence d'apprentissage

| Declencheur | Action |
|------------|--------|
| Fin de session M4 | Mise a jour automatique du profil |
| Appel POST /learn | Apprentissage complet depuis hunting_trips |
| Premier acces | Creation profil avec valeurs par defaut regionales |

---

# 7. REGLES DE NAVIGATION CONTEXTUELLE

## 7.1 Planification d'itineraire

| Etape | Action | Source |
|-------|--------|--------|
| 1 | Recuperer profil AUP | hunter_profiles |
| 2 | Lister POIs de la zone | M2 poi_nodes (LECTURE) |
| 3 | Enrichir POIs avec predictions M3 | M3 predictive_layers (LECTURE) |
| 4 | Filtrer par contraintes legales | M1 legal_constraint (LECTURE) |
| 5 | Appliquer preferences profil | AUP time/meteo/species |
| 6 | Scorer chaque waypoint | score_combine (Section 3.2) |
| 7 | Trier et limiter les waypoints | Top N par score_combine |
| 8 | Calculer distances et ETA | Haversine (M2 relation_resolver) |
| 9 | Persister la session | navigation_sessions |

## 7.2 Score combine waypoint

```
score_combine(poi, profile, prediction) =
    prediction_score * 0.30    ← M3 P(h) au poi.location
  + poi_score * 0.25           ← M2 poi.score.global
  + profile_affinity * 0.20   ← AUP preference match
  + distance_score * 0.15     ← 1 / (1 + distance_km)
  + legal_score * 0.10        ← M1 saison ouverte=1, fermee=0
```

## 7.3 Conseil contextuel

| Condition | Conseil genere | Priorite |
|-----------|---------------|----------|
| M3 P(h) > 0.6 pour espece ciblee | "Activite {species} prevue FORTE a {hour}h" | HIGH |
| Solunar hunting_window active | "Fenetre solunaire intense {start}-{end}" | MEDIUM |
| POI a < 500m avec score > 0.7 | "POI {name} a {distance}m, score {score}" | MEDIUM |
| M3 trend = "increasing" | "Tendance en hausse pour {species}" | LOW |
| M1 saison fermee | "Attention: saison fermee pour {species}" | CRITICAL |

---

# 8. COLLECTIONS MONGODB

## 8.1 Collection : hunter_profiles

Voir schema Section 2.1.

**Index** : `user_id` (unique), `profile_id` (unique), `skill_level`

## 8.2 Collection : navigation_sessions

Voir schema canonique Section 3 du BIONIC_V6_MAP_INTELLIGENCE_PLAN.

**Index** : `session_id` (unique), `user_id`, `status`, compound `{user_id, status}`

---

# 9. ENDPOINTS (11 + 1 health)

| # | Methode | Endpoint | Description | Phase |
|---|---------|----------|-------------|-------|
| 0 | GET | /api/v1/nav-intel/health | Sante du module | - |
| 1 | GET | /api/v1/nav-intel/profile/{user_id} | Profil adaptatif complet | M4-A |
| 2 | PATCH | /api/v1/nav-intel/profile/{user_id} | Mettre a jour preferences | M4-A |
| 3 | POST | /api/v1/nav-intel/profile/{user_id}/learn | Declencher apprentissage | M4-A |
| 4 | POST | /api/v1/nav-intel/plan-route | Planifier itineraire optimal | M4-B |
| 5 | GET | /api/v1/nav-intel/plan-route/{session_id} | Detail itineraire planifie | M4-B |
| 6 | POST | /api/v1/nav-intel/optimize | Optimiser itineraire existant | M4-B |
| 7 | GET | /api/v1/nav-intel/suggestions/{user_id} | Suggestions personnalisees | M4-A |
| 8 | GET | /api/v1/nav-intel/advice/{user_id}/{lat}/{lng} | Conseil contextuel GPS | M4-B |
| 9 | POST | /api/v1/nav-intel/session/start | Demarrer session navigation | M4-B |
| 10 | POST | /api/v1/nav-intel/session/{session_id}/end | Terminer session | M4-B |
| 11 | GET | /api/v1/nav-intel/session/{session_id}/status | Statut session active | M4-B |

---

# 10. IMPACTS DFL / EVENTBUS / DATACONTRACTS

## 10.1 Nouveaux Data Contracts (Frontend)

### HunterProfileContract

```typescript
interface HunterProfileContract {
  profile_id: string;
  user_id: string;
  skill_level: "debutant" | "intermediaire" | "avance" | "expert";
  species_preferences: Array<{species: string; frequency: number; success_rate: number}>;
  zone_preferences: Array<{zone_id: string; visit_count: number; satisfaction_score: number}>;
  time_preferences: {preferred_hours: number[]; preferred_days: string[]};
  history_stats: {total_trips: number; total_hours: number; avg_distance_km: number};
}
```

### NavigationSessionContract

```typescript
interface NavigationSessionContract {
  session_id: string;
  status: "planned" | "active" | "completed" | "abandoned";
  target_species: string;
  waypoints: Array<{poi_id: string; name: string; distance_m: number; score: number; eta_minutes: number}>;
  metrics: {distance_walked_km: number; duration_hours: number; pois_visited: number};
}
```

### ContextualAdviceContract

```typescript
interface ContextualAdviceContract {
  position: {lat: number; lng: number};
  species: string;
  prediction: {current_probability: number; peak_hour: number; trend: string};
  solunar: {score: number; phase: string; next_window: string};
  advice: Array<{type: string; priority: "critical" | "high" | "medium" | "low"; text: string}>;
  nearby_pois: Array<{poi_id: string; name: string; distance_m: number; score: number}>;
}
```

## 10.2 Nouveaux channels EventBus V6

| Channel | Declencheur | Widgets concernes |
|---------|------------|-------------------|
| PROFILE_UPDATED | PATCH profil, POST learn | Profil widget, Suggestions |
| NAVIGATION_SESSION_UPDATED | POST plan-route, POST start/end | Navigation widget |
| ADVICE_UPDATED | GET advice | Conseil contextuel widget |

## 10.3 Extensions DFL

| Methode DFL | Sources fusionnees | Output |
|-------------|-------------------|--------|
| fetchHunterProfile(userId) | M4 profile | HunterProfileContract |
| fetchAdvice(userId, lat, lng) | M4 advice | ContextualAdviceContract |
| fetchActiveSession(userId) | M4 session/status | NavigationSessionContract |

## 10.4 Nouveaux Widgets (FUTUR DASH-M4)

| Widget | Description | Phase |
|--------|-------------|-------|
| HunterProfileWidget | Profil adaptatif avec radar chart | DASH-M4 (futur) |
| NavigationWidget | Itineraire sur carte avec waypoints | DASH-M4 (futur) |
| AdviceWidget | Conseils contextuels temps reel | DASH-M4 (futur) |

**Note** : Les widgets DASH-M4 seront implementes dans une directive separee apres validation M4 backend.

---

# 11. ANTI-DOUBLON

## 11.1 Modules consommes en LECTURE SEULE

| Module | Donnee | Type |
|--------|--------|------|
| hunting_trip_logger | hunting_trips | MongoDB LECTURE |
| M1 national_data_harvester | legal_zones, boundary_resolver | API/MongoDB LECTURE |
| M2 poi_graph_engine | poi_nodes, poi_edges, poi_scorer | MongoDB/API LECTURE |
| M3 predictive_layer_engine | predictive_layers, timeseries_data, seasonal_trends | MongoDB/API LECTURE |
| solunar | compute_solunar() | LECTURE |
| weather_fauna_simulation | optimal_conditions | LECTURE |
| strategy_master_engine | pipeline_results | MongoDB LECTURE |
| recommendation_engine | (interne) | LECTURE |
| nutrition_v6_interface | forage_quality, wildlife_attractiveness | API LECTURE |

## 11.2 Modules INTERDITS de recreation

| Module | Raison |
|--------|--------|
| recommendation_engine | Recommandations existantes — NE PAS reimplementer |
| predictive_engine | Predictions comportementales — LIRE via M3 |
| solunar | Calendrier solunaire — APPELER, NE PAS recalculer |
| scoring_engine | Scoring produits — NE PAS reimplementer |
| poi_scorer (M2) | Scoring POI — LIRE, NE PAS recalculer |

## 11.3 ANTI-DOUBLON NUTRITIONNEL M4

| Source V6 | Consommation | Interdiction |
|-----------|-------------|-------------|
| forage_quality_model | LECTURE qualite fourrage → ponderation route | NE PAS recalculer fourrage |
| wildlife_attractiveness | LECTURE attractivite → scoring waypoints | NE PAS recalculer attractivite |

---

# 12. PLAN D'IMPLEMENTATION

## 12.1 Sequence

```
M4-A : Adaptive User Profile + Suggestions     [PRIORITE 1]
    +--→ user_profile_learner.py
    +--→ contextual_advisor.py (suggestions uniquement)
    +--→ router.py (endpoints 0-3, 7)
    +--→ Tests rapides

M4-B : Navigation IA + Sessions + Conseils     [PRIORITE 2]
    +--→ navigation_planner.py
    +--→ route_optimizer.py
    +--→ contextual_advisor.py (advice)
    +--→ router.py (endpoints 4-6, 8-11)
    +--→ Tests rapides

M4-C : Integration Tests                       [OBLIGATOIRE]
    +--→ test_adaptive_profile.py (T7)
    +--→ test_navigation_planner.py (T8)
    +--→ Non-regression (M1, M2, M3, DASH, Nutrition V6, Cart V2, Phases I-V)
    +--→ RAPPORT FINAL → VALIDATION STEEVE-MAX
```

## 12.2 Estimation

| Phase | Fichiers crees | Endpoints | Lignes |
|-------|---------------|-----------|--------|
| M4-A | 4 (init, learner, advisor, router) | 5 | ~350 |
| M4-B | 3 (planner, optimizer, router update) | 7 | ~400 |
| M4-C | 2 (tests) | 0 | ~300 |
| **TOTAL** | **9** | **12** | **~1050** |

---

# 13. RISQUES BCE-4X

| # | Risque | Prob. | Impact | Mitigation |
|---|--------|-------|--------|-----------|
| R1 | Profil insuffisant (nouvel utilisateur) | ELEVE | MODERE | Profil par defaut regional (QC, intermediaire) |
| R2 | Itineraire hors sentier dangereux | FAIBLE | ELEVE | Contraintes terrain + avertissements |
| R3 | Calcul route couteux (>50 POIs) | MODERE | MODERE | Limite 20 waypoints par session |
| R4 | Latence conseils contextuels | MODERE | FAIBLE | Cache M3 predictions, reponse < 500ms |
| R5 | Dep: M1, M2, M3 non deployes | TRES FAIBLE | ELEVE | Tous deployes et testes (144/144 PASS) |
| R6 | Regression modules V5 | TRES FAIBLE | CRITIQUE | ZERO modification V5, lecture seule |
| R7 | Incoherence profil/predictions | FAIBLE | MODERE | Apprentissage pondere, fallback defaults |

---

# 14. PROTOCOLES DE ROLLBACK

## 14.1 Rollback M4-A

| Etape | Action | Verification |
|-------|--------|-------------|
| 1 | Retirer import adaptive_navigation_engine de routers.py | Import supprime |
| 2 | Retirer entry CORE_ROUTERS | Entry supprimee |
| 3 | Supprimer dossier modules/adaptive_navigation_engine/ | ls confirme |
| 4 | Verifier backend demarre | curl /health → 200 |
| 5 | Tests 144/144 | pytest → 144 PASS |

## 14.2 Rollback Total M4

| Etape | Action | Verification |
|-------|--------|-------------|
| 1 | Rollback M4-A | Backend clean |
| 2 | Drop collections | db.hunter_profiles.drop(), db.navigation_sessions.drop() |
| 3 | Supprimer tests M4 | T7 + T8 |
| 4 | Relancer suite complete | 144 PASS (retour etat DASH) |

---

# 15. IMPACTS PREVUS SUR M5

| Composant M5 | Consommation M4 | Description |
|-------------|-----------------|-------------|
| OfflinePackager | hunter_profiles → inclus dans paquet offline | Profil adaptatif disponible hors-ligne |
| OfflinePackager | navigation_sessions (planifiees) → routes pre-calculees | Itineraires pre-calcules hors-ligne |
| SyncManager | navigation_sessions → sync au retour online | Metriques de session synchronisees |
| TerrainAnalyzer | Aucune dep directe | Indirecte via M2 POIs |

**M5 fonctionne en mode degrade sans M4** : le paquet offline n'inclut pas le profil adaptatif ni les routes pre-calculees, mais les POIs, predictions et terrain restent disponibles.

---

# 16. TESTS

## 16.1 Tests d'integration M4

| # | Fichier | Couverture |
|---|---------|------------|
| T7 | test_adaptive_profile.py | Health, create/get/update profil, apprentissage, suggestions |
| T8 | test_navigation_planner.py | Plan route, get session, optimize, advice, start/end session, non-regression M1/M2/M3 |

## 16.2 Non-regression

| Suite | Tests | Statut attendu |
|-------|-------|---------------|
| Existants | 144/144 | PASS |
| M4 T7+T8 | ~35 | PASS |
| **Total** | **~179** | **ZERO FAIL** |

---

# 17. INVENTAIRE MODIFICATIONS

## 17.1 Fichiers a CREER (9)

| # | Fichier | Phase |
|---|---------|-------|
| 1 | modules/adaptive_navigation_engine/__init__.py | M4-A |
| 2 | modules/adaptive_navigation_engine/router.py | M4-A/B |
| 3 | modules/adaptive_navigation_engine/services/__init__.py | M4-A |
| 4 | modules/adaptive_navigation_engine/services/user_profile_learner.py | M4-A |
| 5 | modules/adaptive_navigation_engine/services/navigation_planner.py | M4-B |
| 6 | modules/adaptive_navigation_engine/services/route_optimizer.py | M4-B |
| 7 | modules/adaptive_navigation_engine/services/contextual_advisor.py | M4-A/B |
| 8 | modules/routers.py (MODIFICATION : +import +registration) | M4-A |
| 9 | Tests T7+T8 | M4-C |

## 17.2 Fichiers existants NON MODIFIES

Tous les 85+ modules V5/V6 existants, M1, M2, M3, DASH, Nutrition V6, Cart V2, Phases I-V.

---

## PROCHAINES ETAPES

Ce plan requiert la **validation explicite de STEEVE-MAX** avant toute execution.

Apres validation, l'execution suivra la sequence :
M4-A (Profil Adaptatif) → M4-B (Navigation IA) → M4-C (Tests)

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : M4_ADAPTIVE_NAVIGATION_PLAN 1.0.0
**References** : BIONIC_V6_MAP_INTELLIGENCE_PLAN v1.1.0, M3_RAPPORT_FINAL 1.0.0, DASH_RAPPORT_FINAL 1.0.0
**Code modifie** : AUCUN (plan uniquement)
**Merge main** : STRICTEMENT INTERDIT
**Points de fusion** : 19
**Modules existants modifies** : ZERO
