# M2 — BIONIC POI GRAPH — PLAN D'EXECUTION DETAILLE
## Directive x6800-A suite — Preparation M2
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-04 | Merge MAIN : STRICTEMENT INTERDIT
### AUCUN CODE MODIFIE tant que ce plan n'est pas valide par STEEVE-MAX

---

# TABLE DES MATIERES

1. [OBJECTIF ET PERIMETRE](#1-objectif)
2. [DEPENDANCES M1 → M2](#2-dependances)
3. [SERVICES A CREER](#3-services)
4. [COLLECTIONS MONGODB](#4-collections)
5. [ENDPOINTS (10)](#5-endpoints)
6. [POINTS DE FUSION](#6-points-de-fusion)
7. [ANTI-DOUBLON](#7-anti-doublon)
8. [ANTI-DOUBLON NUTRITIONNEL](#8-anti-doublon-nutritionnel)
9. [PLAN D'IMPLEMENTATION](#9-plan-implementation)
10. [RISQUES BCE-4X](#10-risques)
11. [TESTS](#11-tests)
12. [INVENTAIRE MODIFICATIONS](#12-inventaire)

---

# 1. OBJECTIF ET PERIMETRE

## 1.1 Objectif

Construire un graphe de Points d'Interet (POI) interconnectes permettant une analyse
relationnelle spatiale entre : cameras trail, observations fauniques, stands de chasse,
caches, points d'eau, ravages, corridors de deplacement, et sources de nourriture.

Le graphe genere des scores de potentiel multi-critere pour chaque POI et identifie
les clusters strategiques pour le chasseur.

## 1.2 Perimetre

| Element | Description |
|---------|-------------|
| Module | `poi_graph_engine/` (NOUVEAU) |
| Services | 3 (POIGraphBuilder, POIScorer, POIRelationResolver) |
| Collections | 2 (poi_nodes, poi_edges) |
| Endpoints | 10 + 1 health |
| Tests | 2 fichiers |
| Code V5 modifie | ZERO |
| Modules existants modifies | ZERO |

## 1.3 Principes

| Principe | Application |
|----------|-------------|
| ZERO LOSS | Aucun endpoint de camera_engine, waypoint_engine, scoring_engine modifie |
| ZERO REGRESSION | Aucune collection existante alteree |
| ZERO INTERPRETATION | Implementation stricte de ce plan |
| ZERO DOUBLON | Scoring POI NE recree PAS waypoint_scoring_engine |
| MongoDB bridges | Communication avec modules existants via lecture seule MongoDB |

---

# 2. DEPENDANCES M1 → M2

## 2.1 Dependance directe M1

| Composant M1 | Usage dans M2 | Type |
|-------------|--------------|------|
| boundary_resolver | Province + zone_chasse pour enrichissement POI | LECTURE |
| legal_constraint_engine | Reglementations par zone → contexte legal POI | LECTURE |
| harvest_logs | Non utilise | - |

## 2.2 Dependances modules existants V5/V6

| Module | Collection MongoDB | Donnee consommee | Type |
|--------|-------------------|-----------------|------|
| camera_engine | cameras | Cameras trail → POI type "camera" | LECTURE |
| waypoint_engine | waypoints | Waypoints → POI enrichissement | LECTURE |
| scoring_engine | scoring_results | Criteres de scoring → enrichissement POI score | LECTURE |
| territory_engine | territories | Zones → contexte territorial POI | LECTURE |
| wildlife_behavior_engine | (interne) | Patterns comportementaux → proprietes POI | LECTURE |
| nutrition_v6_interface | (API) | Qualite fourrage + attractivite → POI nutritionnels | LECTURE |

## 2.3 Dependances ZERO

| Module | Raison |
|--------|--------|
| waypoint_scoring_engine | INTERDIT — scoring POI est independant, NE duplique PAS WQS |
| predictive_engine | M2 ALIMENTE predictive_engine, ne le consomme pas |
| payment_engine | Aucun lien |
| cart_engine | Aucun lien |

---

# 3. SERVICES A CREER

## 3.1 Structure

```
/app/backend/modules/poi_graph_engine/
    __init__.py
    router.py
    services/
        __init__.py
        poi_graph_builder.py     ← CRUD POI nodes + edges
        poi_scorer.py            ← Scoring multi-critere
        poi_relation_resolver.py ← Relations spatiales, clusters, proximite
```

## 3.2 poi_graph_builder.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| create_poi | (user_id, type, name, lat, lng, properties) → poi_node | Cree un noeud POI |
| get_poi | (poi_id) → poi_node | Recupere un POI avec connexions |
| update_poi | (poi_id, updates) → poi_node | Met a jour un POI |
| delete_poi | (poi_id) → bool | Supprime un POI et ses aretes |
| list_pois | (filters) → [poi_node] | Liste POIs avec filtres |
| create_edge | (from_poi, to_poi, relation_type, properties) → edge | Cree une arete |
| get_edges | (poi_id) → [edge] | Aretes connectees a un POI |

## 3.3 poi_scorer.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| compute_poi_score | (poi_node) → score_dict | Calcul multi-critere (accessibility, activity, strategic, nutrition) |
| compute_batch_scores | (poi_ids) → [score_dict] | Scoring par lot |
| get_detailed_score | (poi_id) → detailed_score | Score detaille avec decomposition |

**Criteres de scoring** :
- Accessibilite (distance route, terrain) — poids 0.20
- Activite (frequence observations, cameras) — poids 0.30
- Strategique (position, visibilite, couverture) — poids 0.25
- Nutritionnel (fourrage, sol, attractivite) — poids 0.25 ← VIA nutrition_v6_interface

## 3.4 poi_relation_resolver.py

| Fonction | Signature | Description |
|----------|-----------|-------------|
| find_near | (lat, lng, radius_m, type_filter) → [poi_with_dist] | POIs a proximite |
| compute_cluster | (lat, lng, radius_m) → cluster_result | Cluster dans un rayon |
| resolve_relations | (poi_id) → [relation] | Relations spatiales d'un POI |
| compute_distance | (poi_a, poi_b) → float | Distance Haversine entre 2 POIs |

---

# 4. COLLECTIONS MONGODB

## 4.1 Collection : poi_nodes

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
    "global": 0.0,
    "accessibility": 0.0,
    "activity": 0.0,
    "strategic": 0.0,
    "nutrition": 0.0
  },
  "nutrition": {
    "forage_quality": 0.0,
    "mineral_richness": 0.0,
    "ndvi_index": 0.0,
    "species_attractiveness": {"orignal": 0.0, "chevreuil": 0.0},
    "source": "nutrition_v6_interface"
  },
  "connections": ["poi_id_1", "poi_id_2"],
  "zone_id": "string",
  "zone_type": "string",
  "province": "string",
  "user_id": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Index** : `location` (2dsphere), `user_id` (1), `type` (1), `zone_id` (1)

## 4.2 Collection : poi_edges

```json
{
  "edge_id": "uuid-v4",
  "from_poi": "poi_id",
  "to_poi": "poi_id",
  "relation_type": "proximity | corridor | line_of_sight | water_flow | trail",
  "distance_m": 0.0,
  "elevation_diff_m": 0.0,
  "weight": 0.0,
  "properties": {
    "terrain_type": "forest | field | water | rock",
    "traversability": 0.0,
    "species_usage": ["orignal"]
  },
  "created_at": "ISO8601"
}
```

**Index** : `from_poi` (1), `to_poi` (1), `relation_type` (1)

---

# 5. ENDPOINTS (10 + 1 health)

| # | Methode | Endpoint | Description | Phase |
|---|---------|----------|-------------|-------|
| 0 | GET | /api/v1/poi-graph/health | Sante du module | - |
| 1 | GET | /api/v1/poi-graph/nodes | Liste POIs (filtres: type, zone, species, user) | M2-A |
| 2 | POST | /api/v1/poi-graph/nodes | Creer un POI | M2-A |
| 3 | GET | /api/v1/poi-graph/nodes/{poi_id} | Detail POI avec connexions | M2-A |
| 4 | PATCH | /api/v1/poi-graph/nodes/{poi_id} | Mettre a jour un POI | M2-A |
| 5 | DELETE | /api/v1/poi-graph/nodes/{poi_id} | Supprimer un POI | M2-A |
| 6 | GET | /api/v1/poi-graph/near/{lat}/{lng} | POIs a proximite | M2-B |
| 7 | GET | /api/v1/poi-graph/edges/{poi_id} | Aretes d'un POI | M2-B |
| 8 | POST | /api/v1/poi-graph/edges | Creer une arete | M2-B |
| 9 | GET | /api/v1/poi-graph/cluster/{lat}/{lng}/{radius_m} | Cluster de POIs | M2-B |
| 10 | GET | /api/v1/poi-graph/score/{poi_id} | Score detaille | M2-B |

## 5.1 Sous-phases d'implementation

| Sous-phase | Endpoints | Fichiers | Contenu |
|-----------|-----------|----------|---------|
| M2-A (CRUD) | 0-5 | poi_graph_builder.py, router.py | CRUD nodes |
| M2-B (Spatial) | 6-10 | poi_relation_resolver.py, poi_scorer.py, router.py | Proximite, clusters, scoring, edges |

---

# 6. POINTS DE FUSION

## 6.1 Fusion SUPRA (P4)

| Point | Source SUPRA | Usage M2 | Methode |
|-------|-------------|----------|---------|
| PF-S1 | scoring_engine | Criteres de scoring → enrichissement score POI | MongoDB lecture scoring_results |
| PF-S2 | strategy_master_engine | Strategies actives → contexte POI | MongoDB lecture pipeline_results |

## 6.2 Fusion Zone Engine (P6 Territoire)

| Point | Source Zone | Usage M2 | Methode |
|-------|-----------|----------|---------|
| PF-Z1 | territory_engine | Zones de chasse → zone_id du POI | MongoDB lecture territories |
| PF-Z2 | hunting_trip_logger | Historique sorties → enrichissement frequence POI | MongoDB lecture hunting_trips |

## 6.3 Fusion Species Models

| Point | Source | Usage M2 | Methode |
|-------|--------|----------|---------|
| PF-SP1 | wildlife_behavior_engine | Patterns comportementaux → properties.species_observed | MongoDB lecture |
| PF-SP2 | camera_engine | Detections cameras → POI nodes type "camera" auto-generes | MongoDB lecture cameras |

## 6.4 Fusion M1 (MAP Intelligence)

| Point | Source M1 | Usage M2 | Methode |
|-------|----------|----------|---------|
| PF-M1 | boundary_resolver | Province + zone_chasse → enrichissement POI | Appel service direct (meme backend) |
| PF-M2 | legal_constraint_engine | Reglementations → contexte legal POI | Appel service direct |

## 6.5 Fusion Nutritionnelle V6

| Point | Source V6 | Usage M2 | Methode |
|-------|----------|----------|---------|
| PF-N1 | forage_quality_model | Qualite fourrage → POI.nutrition.forage_quality | Appel wrapper V6 |
| PF-N2 | soil_nutrients_layer | Mineraux sol → POI.nutrition.mineral_richness | Appel wrapper V6 |
| PF-N3 | wildlife_nutrition_attractiveness | Attractivite par espece → POI.nutrition.species_attractiveness | Appel wrapper V6 |
| PF-N4 | cross_layer_integration | Score nutritionnel global → POI.score.nutrition | Appel wrapper V6 |

---

# 7. ANTI-DOUBLON

## 7.1 Modules consommes en LECTURE SEULE

| Module | Collection / API | Donnee |
|--------|-----------------|--------|
| camera_engine | cameras | id, location, events → POI generation |
| waypoint_engine | waypoints | id, coordinates, type → POI enrichissement |
| scoring_engine | scoring_results | criteres → enrichissement score (SANS recalcul) |
| territory_engine | territories | zones → contexte geographique |
| M1 boundary_resolver | (service) | province, zone_chasse |
| M1 legal_constraint_engine | (service) | reglementations |

## 7.2 Modules INTERDITS de recreation dans M2

| Module | Raison | Action si besoin |
|--------|--------|-----------------|
| waypoint_scoring_engine | WQS existe deja pour waypoints | LIRE scores existants, NE PAS recalculer |
| scoring_engine | Scoring produits existe | LIRE criteres, NE PAS refaire le scoring |
| geo_engine | Geocodage existe | NE PAS reimplementer geocodage |
| geospatial_engine | Analyses spatiales existent | Utiliser uniquement Haversine basique dans M2 |
| territory_engine | Gestion zones existe | NE PAS recreer gestion de zones |

## 7.3 Ce que M2 apporte de NOUVEAU (non-doublon)

| Fonctionnalite | Justification |
|----------------|---------------|
| Graphe POI (noeuds + aretes) | N'existe pas dans le codebase |
| Relations spatiales entre POIs | waypoint_engine n'a pas de relations inter-waypoints |
| Clusters de POIs | N'existe pas |
| Scoring multi-critere POI avec nutrition | waypoint_scoring_engine ne fait pas de scoring nutritionnel |
| Types POI etendus (ravage, corridor, nourriture) | waypoint_engine limite a des types basiques |

---

# 8. ANTI-DOUBLON NUTRITIONNEL

## 8.1 Sources nutritionnelles

| Source V6 | Consommation dans M2 | Interdiction |
|-----------|---------------------|-------------|
| forage_quality_model (wrapper V5 → vegetation_forage_engine) | LECTURE qualite fourrage → POI type "nourriture" score | NE PAS recalculer phenologie, mineraux vegetaux |
| soil_nutrients_layer (wrapper V5 → soil_composition_engine) | LECTURE mineraux sol → POI.nutrition.mineral_richness | NE PAS recalculer pH, texture, drainage |
| wildlife_nutrition_attractiveness (wrapper V5 → wildlife_nutritional + metabolism) | LECTURE attractivite par espece → POI.nutrition.species_attractiveness | NE PAS redefinir besoins journaliers |
| cross_layer_integration (wrapper V5 → saline_recommendation) | LECTURE score nutrition global → POI.score.nutrition | NE PAS recalculer synthese Sol→Gibier |
| nutrition_engine P0 (NDVI) | LECTURE indirecte via cross_layer | NE PAS recalculer NDVI |

## 8.2 Regle stricte

**Tout enrichissement nutritionnel d'un POI DOIT passer par `nutrition_v6_interface`.**
Aucun import direct des moteurs V5 dans `poi_graph_engine`.

---

# 9. PLAN D'IMPLEMENTATION

## 9.1 Sequence

```
M2-A : CRUD POI Nodes                     [PRIORITE 1]
    +--→ poi_graph_builder.py
    +--→ router.py (endpoints 0-5)
    +--→ Tests CRUD rapides (curl)
    +--→ Rapport intermediaire

M2-B : Relations spatiales + Scoring      [PRIORITE 2]
    +--→ poi_relation_resolver.py
    +--→ poi_scorer.py
    +--→ router.py (endpoints 6-10)
    +--→ Tests spatiaux (curl)
    +--→ Rapport intermediaire

M2-C : Integration Tests                  [OBLIGATOIRE]
    +--→ test_poi_graph_crud.py
    +--→ test_poi_graph_spatial.py
    +--→ Non-regression (M1, Nutrition V6, Cart V2, Phases I-V)
    +--→ RAPPORT FINAL → VALIDATION STEEVE-MAX
```

## 9.2 Estimation

| Phase | Fichiers crees | Endpoints | Lignes | Duree |
|-------|---------------|-----------|--------|-------|
| M2-A | 3 (init, builder, router) | 6 | ~300 | Phase 1 |
| M2-B | 2 (resolver, scorer) | 5 | ~300 | Phase 2 |
| M2-C | 2 (tests) | 0 | ~200 | Phase 3 |
| **TOTAL** | **7** | **11** | **~800** | **1 session** |

---

# 10. RISQUES BCE-4X

## 10.1 Risques identifies

| # | Risque | Probabilite | Impact | Mitigation |
|---|--------|-------------|--------|-----------|
| R1 | Volume POIs eleve (>10k) | MODERE | MODERE | Index 2dsphere MongoDB + pagination 50/page |
| R2 | Calcul distances couteux | FAIBLE | MODERE | Haversine O(1) par paire, batch limit 100 |
| R3 | Graphe deconnecte (POIs isoles) | FAIBLE | FAIBLE | Flag "isolated" sur POIs sans connexions |
| R4 | Collision POI/Waypoint | FAIBLE | FAIBLE | Collections separees, pas de conflit |
| R5 | Scoring nutritionnel lent | FAIBLE | MODERE | Cache score 1h TTL, calcul async |
| R6 | Regression modules V5 | TRES FAIBLE | CRITIQUE | ZERO modification V5, lecture seule MongoDB |

## 10.2 Garanties BCE-4X

| Garantie | Mecanisme |
|----------|-----------|
| ZERO LOSS | Module NOUVEAU, aucune modification d'existant |
| ZERO REGRESSION | Tests non-regression sur 58 tests existants |
| ZERO DOUBLON | Sections 7 et 8 documentent les interdictions |
| ZERO INTERPRETATION | Ce plan est la seule specification d'implementation |

---

# 11. TESTS

## 11.1 Tests d'integration M2

| # | Fichier | Couverture |
|---|---------|------------|
| T3 | test_poi_graph_crud.py | CRUD: create, get, update, delete, list, filters |
| T4 | test_poi_graph_spatial.py | Near, cluster, edges, scoring, non-regression M1 |

## 11.2 Tests de non-regression

| Suite | Tests | Statut attendu |
|-------|-------|---------------|
| Phases I-V | 33/33 | PASS |
| Cart V2 | 25/25 | PASS |
| M1 | curl endpoints | 200 OK |
| Nutrition V6 | curl endpoints | 200 OK |
| **Total** | **58+** | **ZERO FAIL** |

---

# 12. INVENTAIRE MODIFICATIONS

## 12.1 Fichiers a CREER (7)

| # | Fichier | Phase |
|---|---------|-------|
| 1 | modules/poi_graph_engine/__init__.py | M2-A |
| 2 | modules/poi_graph_engine/router.py | M2-A/B |
| 3 | modules/poi_graph_engine/services/__init__.py | M2-A |
| 4 | modules/poi_graph_engine/services/poi_graph_builder.py | M2-A |
| 5 | modules/poi_graph_engine/services/poi_scorer.py | M2-B |
| 6 | modules/poi_graph_engine/services/poi_relation_resolver.py | M2-B |
| 7 | modules/routers.py (MODIFICATION : +import +registration) | M2-A |

## 12.2 Fichiers existants NON MODIFIES

- camera_engine/* (ZERO modification)
- waypoint_engine/* (ZERO modification)
- waypoint_scoring_engine/* (ZERO modification)
- scoring_engine/* (ZERO modification)
- territory_engine/* (ZERO modification)
- national_data_harvester/* (ZERO modification)
- nutrition_v6_interface/* (ZERO modification)
- Tous les 82+ modules existants

## 12.3 Collections MongoDB

| # | Collection | Action | Index |
|---|-----------|--------|-------|
| 1 | poi_nodes | CREER | location (2dsphere), user_id, type, zone_id |
| 2 | poi_edges | CREER | from_poi, to_poi, relation_type |

---

## PROCHAINES ETAPES

Ce plan requiert la **validation explicite de STEEVE-MAX** avant toute execution.

Apres validation, l'execution suivra la sequence :
M2-A (CRUD) → M2-B (Spatial) → M2-C (Tests)

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : M2_POI_GRAPH_PLAN 1.0.0
**References** : BIONIC_V6_MAP_INTELLIGENCE_PLAN v1.1.0, VALIDATION_INTERCONNEXION_NUTRITIONNELLE
**Code modifie** : AUCUN (plan uniquement)
**Merge main** : STRICTEMENT INTERDIT
