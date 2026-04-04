# VALIDATION_INTERCONNEXION_NUTRITIONNELLE_V5_V6
## Directive x6500-B — STEEVE-MAX
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-04 | Merge MAIN : STRICTEMENT INTERDIT
### Aucun code modifie — Document d'audit et de validation uniquement

---

# TABLE DES MATIERES

1. [INVENTAIRE MOTEURS NUTRITIONNELS EXISTANTS (V5)](#1-inventaire-v5)
2. [CARTOGRAPHIE CHAINE SOL → NUTRIMENTS → FOURRAGE → GIBIER](#2-cartographie-chaine)
3. [VALIDATION INTERCONNEXION V5](#3-validation-v5)
4. [INTEGRATION NUTRITIONNELLE V6 (M1→M5)](#4-integration-v6)
5. [AUDIT ANTI-DOUBLON GLOBAL](#5-anti-doublon-global)
6. [ANTI-DOUBLON PAR SOUS-PHASE M1→M5](#6-anti-doublon-par-phase)
7. [MATRICE DE VERROUILLAGE](#7-verrouillage)

---

# 1. INVENTAIRE MOTEURS NUTRITIONNELS EXISTANTS (V5)

## 1.1 Moteurs principaux identifies

| # | Module | Fichier | Role nutritionnel | Statut |
|---|--------|---------|------------------|--------|
| N1 | saline_engine | engines/soil_composition_engine.py | Analyse pH, CEC, 10 mineraux, texture, drainage par ecozone | ACTIF |
| N2 | saline_engine | engines/nutrient_deficiency_engine.py | Couverture besoins vs sol, deficits, interactions minerales | ACTIF |
| N3 | saline_engine | engines/wildlife_nutritional_engine.py | Besoins journaliers par espece/sexe/saison (Ca, P, K, Mg, Na, etc.) | ACTIF |
| N4 | saline_engine | engines/vegetation_forage_engine.py | Qualite fourrage, phenologie, mineraux vegetaux par type | ACTIF |
| N5 | saline_engine | engines/hydrology_leaching_engine.py | Lessivage mineraux, drainage, impact hydrique sur nutriments | ACTIF |
| N6 | saline_engine | engines/seasonal_metabolism_engine.py | Etat metabolique par espece/saison (bois, gestation, rut, hiver) | ACTIF |
| N7 | saline_engine | engines/saline_recommendation_engine.py | Synthese complete : score intelligence, placement optimal | ACTIF |
| N8 | bionic_engine_p0 | engines/nutrition_engine.py | NDVI + fourrage + attractivite nutritionnelle par zone/espece | ACTIF |
| N9 | bionic_engine_p0 | engines/phenology_engine.py | Phenologie vegetale, saison de croissance | ACTIF |
| N10 | soil_engine | router.py | Classification pedologique (V1 deterministe — hash GPS) | ACTIF |
| N11 | nutrition_engine | v1/service.py | Analyse nutritionnelle produits (ingredients, macros) | ACTIF |
| N12 | bionic_ecological_engine | intelligence_core.py | Intelligence ecologique unifiee (sol, hydro, vegetation, mineraux) | ACTIF |
| N13 | bionic_ecological_engine | behavior_pipeline.py | Pipeline comportemental integrant nutrition | ACTIF |

## 1.2 Chaine nutritionnelle complete (V5)

```
SOL (N1, N10)
  ├── pH, CEC, texture, drainage, 10 mineraux
  ├── Profils par ecozone (boreal, mixedwood, atlantic, hudson, taiga)
  └── Facteurs saisonniers (lessivage printemps, concentration ete)
      │
      ▼
NUTRIMENTS (N2, N5)
  ├── Couverture besoins vs disponibilite sol
  ├── Interactions minerales (Ca↔Zn, K↔Mg, Ca:P ratio)
  ├── Biodisponibilite par mineral
  ├── Deficits critiques et alertes
  └── Impact hydrologique sur retention/lessivage
      │
      ▼
FOURRAGE (N4, N8, N9)
  ├── Qualite fourrage par type vegetation et saison
  ├── Mineraux par type vegetal (feuillus, resineux, arbustes, herbacees, aquatiques)
  ├── Phenologie : dormance → debourrement → croissance → senescence
  ├── NDVI par zone et saison
  └── Attractivite nutritionnelle par espece
      │
      ▼
GIBIER (N3, N6)
  ├── Besoins journaliers par espece (orignal, chevreuil, ours_noir, dindon)
  ├── Besoins par phase metabolique (base, bois, gestation, rut, hiver)
  ├── 10 mineraux essentiels par espece
  └── Etat metabolique saisonnier
      │
      ▼
SYNTHESE (N7, N12, N13)
  ├── Score intelligence unifie
  ├── Placement optimal (salines)
  ├── Intelligence ecologique globale
  └── Pipeline comportemental
```

---

# 2. CARTOGRAPHIE CHAINE SOL → NUTRIMENTS → FOURRAGE → GIBIER

## 2.1 Flux de donnees inter-moteurs (V5 actuel)

```
soil_composition_engine ──────────→ nutrient_deficiency_engine
        │                                     │
        │ (pH, mineraux sol)                   │ (deficits, couverture %)
        │                                     │
        ▼                                     ▼
hydrology_leaching_engine         wildlife_nutritional_engine
        │                                     │
        │ (lessivage, drainage)               │ (besoins journaliers)
        │                                     │
        └──────┐           ┌──────────────────┘
               ▼           ▼
     vegetation_forage_engine
               │
               │ (fourrage, phenologie, NDVI)
               │
               ▼
     seasonal_metabolism_engine
               │
               │ (etat metabolique)
               │
               ▼
     saline_recommendation_engine ──→ SCORE INTELLIGENCE UNIFIE
               │
               ▼
     bionic_ecological_engine (intelligence_core)
               │
               ▼
     bionic_engine_p0/nutrition_engine ──→ SCORING ZONES
```

## 2.2 Collections MongoDB associees

| Collection | Moteur source | Donnees nutritionnelles |
|-----------|--------------|------------------------|
| saline_analyses | saline_recommendation_engine | Score complet sol→gibier |
| soil_results | soil_engine | Classification pedologique |
| ecological_analyses | bionic_ecological_engine | Intelligence ecologique unifiee |
| pipeline_results | bionic_engine_p0 | Scores NDVI + nutrition par zone |

---

# 3. VALIDATION INTERCONNEXION V5

## 3.1 Points de validation

| # | Point de validation | Statut | Details |
|---|-------------------|--------|---------|
| V5-1 | Chaine Sol → Nutriments complete | VALIDE | soil_composition → nutrient_deficiency couvre 10 mineraux |
| V5-2 | Chaine Nutriments → Fourrage complete | VALIDE | deficiency → vegetation_forage integre disponibilite |
| V5-3 | Chaine Fourrage → Gibier complete | VALIDE | forage → wildlife_nutritional couvre 4 especes |
| V5-4 | Metabolisme saisonnier integre | VALIDE | seasonal_metabolism fournit phases physiologiques |
| V5-5 | Hydrologie integree | VALIDE | hydrology_leaching impacte retention mineraux |
| V5-6 | Synthese unifiee | VALIDE | saline_recommendation_engine consolide tout |
| V5-7 | Intelligence ecologique | VALIDE | bionic_ecological_engine consomme sol, hydro, vegetation |
| V5-8 | Scoring zones NDVI | VALIDE | bionic_engine_p0/nutrition_engine couvre scoring |

## 3.2 Points d'attention V5

| # | Point | Severite | Description |
|---|-------|----------|-------------|
| A1 | soil_engine V1 deterministe | MODEREE | Hash GPS, pas de donnees reelles. Plan V2 existe. |
| A2 | Deux nutrition engines | FAIBLE | nutrition_engine (produits) ≠ bionic_engine_p0/nutrition_engine (zones). Pas de doublon fonctionnel. |
| A3 | bionic_ecological_engine integre en interne | FAIBLE | Recalcule sol/hydro au lieu de consommer saline_engine. Acceptable car isolation module. |

---

# 4. INTEGRATION NUTRITIONNELLE V6 (M1→M5)

## 4.1 Principe d'integration

Les phases M1→M5 du BIONIC_V6_MAP_INTELLIGENCE_PLAN NE DUPLIQUENT PAS
les moteurs nutritionnels V5. Elles les CONSOMMENT via MongoDB bridges
(lecture seule) pour enrichir leurs propres fonctionnalites.

```
M1 ← soil_composition_engine (lecture des profils sol par ecozone)
M2 ← vegetation_forage_engine (POI nutritionnels, qualite fourrage)
M3 ← nutrient_deficiency_engine + seasonal_metabolism (facteurs predictifs)
M4 ← wildlife_nutritional_engine (ponderation profil par espece)
M5 ← saline_recommendation_engine (paquet offline complet)
```

## 4.2 Integration par sous-phase

### M1 : National Data Harvester + Legal Boundary

| Fonction nutritionnelle | Source V5 | Methode | Description |
|------------------------|-----------|---------|-------------|
| Ingestion donnees sol nationales | soil_composition_engine (N1) | MongoDB lecture | Profils sol par ecozone → enrichissement national_boundaries |
| Normalisation 0-1 SUPRA | soil_composition_engine | Transformation | Mineraux sol normalises pour scoring unifie |
| Classification nutritionnelle des zones | nutrient_deficiency_engine (N2) | MongoDB lecture | Deficits par zone legale |

**Impact sur schema national_boundaries** :
```json
{
  "...existing fields...",
  "nutrition_profile": {
    "soil_quality_index": 0.0,
    "dominant_minerals": ["Ca", "K", "Mg"],
    "deficiency_risk": "low | moderate | high",
    "ecozone": "string",
    "source": "soil_composition_engine"
  }
}
```

### M2 : BIONIC POI Graph

| Fonction nutritionnelle | Source V5 | Methode | Description |
|------------------------|-----------|---------|-------------|
| POI nutritionnels | vegetation_forage_engine (N4) | MongoDB lecture | Zones de fourrage haute qualite → POI type "nourriture" |
| Qualite vegetale par POI | vegetation_forage_engine | Calcul | Forage quality score par POI |
| Score nutritionnel POI | bionic_engine_p0/nutrition_engine (N8) | MongoDB lecture | NDVI + attractivite → enrichissement score POI |

**Impact sur schema poi_nodes** :
```json
{
  "...existing fields...",
  "nutrition": {
    "forage_quality": 0.0,
    "mineral_richness": 0.0,
    "ndvi_index": 0.0,
    "species_attractiveness": {"orignal": 0.0, "chevreuil": 0.0},
    "source": "vegetation_forage_engine + nutrition_engine_p0"
  }
}
```

### M3 : Predictive Layer Engine + Time-Series

| Fonction nutritionnelle | Source V5 | Methode | Description |
|------------------------|-----------|---------|-------------|
| Couches nutritionnelles heatmap | nutrient_deficiency_engine (N2) | MongoDB lecture | Deficits → facteur de prediction |
| Phenologie dans predictions | phenology_engine (N9) | Calcul | Phase phenologique → impact fourrage → probabilite |
| Metabolisme saisonnier | seasonal_metabolism_engine (N6) | MongoDB lecture | Besoins metaboliques → ponderation prediction |
| Correlation nutrition-presence | saline_recommendation_engine (N7) | MongoDB lecture | Score intelligence → facteur correlation |

**Impact sur schema predictive_layers** :
```json
{
  "...existing fields...",
  "predictions[].factors": ["meteo", "solunar", "saison", "nutrition"],
  "nutrition_layer": {
    "forage_availability": 0.0,
    "mineral_deficit_index": 0.0,
    "metabolic_demand": 0.0,
    "nutrition_weight_in_prediction": 0.15,
    "source": "nutrient_deficiency + seasonal_metabolism"
  }
}
```

### M4 : Adaptive User Profile + Navigation Outdoor IA

| Fonction nutritionnelle | Source V5 | Methode | Description |
|------------------------|-----------|---------|-------------|
| Ponderation espece ciblee | wildlife_nutritional_engine (N3) | MongoDB lecture | Besoins nutritifs espece → ponderation itineraire |
| Attractivite nutritionnelle route | vegetation_forage_engine (N4) | MongoDB lecture | Qualite fourrage long du trajet → scoring route |
| Conseil nutritionnel contextuel | saline_recommendation_engine (N7) | MongoDB lecture | Score intelligence zone → conseils IA |

**Impact sur schema hunter_profiles** :
```json
{
  "...existing fields...",
  "nutrition_preferences": {
    "prioritize_nutritional_hotspots": true,
    "species_nutrition_weight": 0.3,
    "source": "wildlife_nutritional_engine"
  }
}
```

**Impact sur schema navigation_sessions** :
```json
{
  "...existing fields...",
  "optimization_criteria": {
    "...existing...",
    "nutrition_weight": 0.2,
    "prefer_high_forage": true
  }
}
```

### M5 : Offline Mode Ultra + Terrain & Species Intelligence

| Fonction nutritionnelle | Source V5 | Methode | Description |
|------------------------|-----------|---------|-------------|
| Paquet offline nutritionnel | saline_recommendation_engine (N7) | MongoDB lecture | Analyses completes sol→gibier pour zone |
| Couche terrain sol | soil_composition_engine (N1) | MongoDB lecture | Profils sol dans le paquet |
| Couche terrain fourrage | vegetation_forage_engine (N4) | MongoDB lecture | Qualite fourrage dans le paquet |
| Habitat nutritionnel | wildlife_nutritional_engine (N3) | Calcul | Suitability par espece incluant nutrition |

**Impact sur schema offline_packages** :
```json
{
  "...existing fields...",
  "layers": [
    {"type": "nutrition_soil", "record_count": 0, "size_kb": 0},
    {"type": "nutrition_forage", "record_count": 0, "size_kb": 0},
    {"type": "nutrition_intelligence", "record_count": 0, "size_kb": 0}
  ]
}
```

**Impact sur schema terrain_analyses** :
```json
{
  "...existing fields...",
  "nutrition": {
    "soil_mineral_index": 0.0,
    "forage_quality_index": 0.0,
    "nutrition_deficit_zones": [],
    "source": "soil_composition + vegetation_forage + nutrient_deficiency"
  }
}
```

**Impact sur schema species_habitats** :
```json
{
  "...existing fields...",
  "factors": {
    "...existing...",
    "nutrition_match": 0.0,
    "mineral_availability": 0.0
  }
}
```

---

# 5. AUDIT ANTI-DOUBLON GLOBAL

## 5.1 Moteurs fonctionnels existants — Matrice de consommation

| Fonctionnalite | Moteur source UNIQUE | Consommateurs autorises | DUPLICATION INTERDITE |
|----------------|---------------------|------------------------|----------------------|
| Analyse sol (pH, mineraux, texture) | soil_composition_engine (N1) | M1, M5, bionic_ecological | OUI — aucun autre moteur ne recalcule le sol |
| Deficits nutritionnels | nutrient_deficiency_engine (N2) | M3, M5 | OUI — deficits calcules en un seul lieu |
| Besoins journaliers especes | wildlife_nutritional_engine (N3) | M4, M5, bionic_ecological | OUI — besoins definis en un seul lieu |
| Qualite fourrage | vegetation_forage_engine (N4) | M2, M3, M4, M5 | OUI — fourrage calcule en un seul lieu |
| Lessivage hydrologique | hydrology_leaching_engine (N5) | saline_recommendation | OUI — hydrologie en un seul lieu |
| Etat metabolique | seasonal_metabolism_engine (N6) | M3, saline_recommendation | OUI — metabolisme en un seul lieu |
| Score intelligence saline | saline_recommendation_engine (N7) | M4, M5 | OUI — synthese en un seul lieu |
| NDVI + scoring zones | nutrition_engine P0 (N8) | M2, M3 | OUI — NDVI zones en un seul lieu |
| Phenologie | phenology_engine (N9) | M3, vegetation_forage | OUI — phenologie en un seul lieu |
| Classification pedologique | soil_engine (N10) | M1, soil_composition | OUI — classification en un seul lieu |
| Intelligence ecologique | bionic_ecological_engine (N12) | M5 | OUI — synthese eco en un seul lieu |
| Scoring attractants | scoring_engine (scr) | M2 | OUI — scoring produits en un seul lieu |
| Species behavior models | wildlife_behavior_engine | M3, M5 | OUI — comportement en un seul lieu |
| Predictive attractiveness | predictive_engine | M3 | OUI — predictions en un seul lieu |
| Strategy SUPRA | strategy_master_engine | M4 | OUI — strategies en un seul lieu |
| Zone engine (territoire) | territory_engine | M1, M2, M4 | OUI — zones en un seul lieu |

## 5.2 Modules interdits de duplication dans M1→M5

| Module interdit de recalcul | Raison | Action si besoin |
|----------------------------|--------|-----------------|
| Recalcul pH / mineraux sol | soil_composition_engine existe | LIRE via MongoDB bridge |
| Recalcul besoins especes | wildlife_nutritional_engine existe | LIRE via MongoDB bridge |
| Recalcul fourrage | vegetation_forage_engine existe | LIRE via MongoDB bridge |
| Recalcul deficits | nutrient_deficiency_engine existe | LIRE via MongoDB bridge |
| Recalcul NDVI | nutrition_engine P0 existe | LIRE via MongoDB bridge |
| Recalcul metabolisme | seasonal_metabolism_engine existe | LIRE via MongoDB bridge |
| Recalcul scoring SUPRA | scoring_engine + strategy_master | LIRE via MongoDB bridge |
| Recalcul predictions | predictive_engine existe | LIRE via MongoDB bridge |
| Recalcul zones | territory_engine existe | LIRE via MongoDB bridge |
| Recalcul comportement | wildlife_behavior_engine existe | LIRE via MongoDB bridge |
| Recalcul phenologie | phenology_engine existe | LIRE via MongoDB bridge |
| Recalcul hydrologie | hydrology_leaching_engine existe | LIRE via MongoDB bridge |

---

# 6. ANTI-DOUBLON PAR SOUS-PHASE M1→M5

## 6.1 M1 — National Data Harvester

### ANTI-DOUBLON

| Sources utilisees | Modules consommes (lecture) | Modules INTERDITS de recreation |
|-------------------|---------------------------|-------------------------------|
| Donnees publiques nationales (MFFP, MRNF) | soil_composition_engine, territory_engine, geo_engine, legal_time_engine | soil_engine (classification), geospatial_engine (analyses spatiales) |

### ANTI-DOUBLON NUTRITIONNEL

| Sources nutritionnelles | Consommation | Interdiction |
|------------------------|-------------|-------------|
| soil_composition_engine | LECTURE profils ecozone → enrichissement boundaries | NE PAS recalculer pH, mineraux, texture |
| nutrient_deficiency_engine | LECTURE deficits → classification zones | NE PAS recalculer couverture besoins |

### Points de fusion

| Point de fusion | Module source | Module cible | Donnee |
|----------------|--------------|-------------|--------|
| SUPRA | strategy_master_engine | M1 (scoring zones) | Strategies par zone legale |
| Zone Engine | territory_engine | M1 (boundaries) | Zones de chasse existantes |
| P6 Territoire | territory_engine | M1 (navigation) | Zones selectionnables |
| Species Models | wildlife_behavior_engine | M1 (legal check) | Periodes par espece |
| Predictive | predictive_engine | M1 (enrichissement) | Predictions par zone |

---

## 6.2 M2 — BIONIC POI Graph

### ANTI-DOUBLON

| Sources utilisees | Modules consommes (lecture) | Modules INTERDITS de recreation |
|-------------------|---------------------------|-------------------------------|
| camera_engine, waypoint_engine, hunting_trip_logger | scoring_engine, M1 (zones) | waypoint_scoring_engine (scoring waypoints), scoring_engine (scoring attractants) |

### ANTI-DOUBLON NUTRITIONNEL

| Sources nutritionnelles | Consommation | Interdiction |
|------------------------|-------------|-------------|
| vegetation_forage_engine | LECTURE qualite fourrage → POI type "nourriture" | NE PAS recalculer phenologie, mineraux vegetaux |
| nutrition_engine P0 | LECTURE NDVI + attractivite → enrichissement score POI | NE PAS recalculer NDVI |
| saline_recommendation_engine | LECTURE scores intelligence → POI salines | NE PAS recalculer synthese saline |

### Points de fusion

| Point de fusion | Module source | Module cible | Donnee |
|----------------|--------------|-------------|--------|
| SUPRA | scoring_engine | M2 (POI score) | Criteres de scoring |
| Zone Engine | territory_engine | M2 (contexte POI) | Zones d'appartenance |
| Species Models | wildlife_behavior_engine | M2 (observations) | Patterns comportementaux |

---

## 6.3 M3 — Predictive Layer + Time-Series

### ANTI-DOUBLON

| Sources utilisees | Modules consommes (lecture) | Modules INTERDITS de recreation |
|-------------------|---------------------------|-------------------------------|
| predictive_engine, weather_fauna_simulation, solunar | M1 (zones), M2 (POIs), hunting_trip_logger | predictive_engine (predictions existantes), solunar (calendrier) |

### ANTI-DOUBLON NUTRITIONNEL

| Sources nutritionnelles | Consommation | Interdiction |
|------------------------|-------------|-------------|
| nutrient_deficiency_engine | LECTURE deficits → facteur prediction nutritionnel | NE PAS recalculer deficits |
| seasonal_metabolism_engine | LECTURE etat metabolique → ponderation saisonniere | NE PAS recalculer metabolisme |
| phenology_engine | LECTURE phase phenologique → impact fourrage temporal | NE PAS recalculer phenologie |
| vegetation_forage_engine | LECTURE qualite fourrage saisonniere → heatmap nutritionnelle | NE PAS recalculer fourrage |

### Points de fusion

| Point de fusion | Module source | Module cible | Donnee |
|----------------|--------------|-------------|--------|
| SUPRA | strategy_master_engine | M3 (strategies predictives) | Strategies par zone/espece |
| Predictive | predictive_engine | M3 (input) | Predictions existantes |
| Zone Engine | territory_engine | M3 (overlay) | Geometries zones |
| Species Models | wildlife_behavior_engine | M3 (comportement) | Patterns horaires |

---

## 6.4 M4 — Adaptive Profile + Navigation IA

### ANTI-DOUBLON

| Sources utilisees | Modules consommes (lecture) | Modules INTERDITS de recreation |
|-------------------|---------------------------|-------------------------------|
| hunting_trip_logger, M2, M3, M1 | live_heading_engine, tracking_engine, strategy_master | recommendation_engine (recommandations existantes) |

### ANTI-DOUBLON NUTRITIONNEL

| Sources nutritionnelles | Consommation | Interdiction |
|------------------------|-------------|-------------|
| wildlife_nutritional_engine | LECTURE besoins espece ciblee → ponderation itineraire | NE PAS redefinir besoins journaliers |
| vegetation_forage_engine | LECTURE qualite fourrage → scoring route | NE PAS recalculer fourrage |
| saline_recommendation_engine | LECTURE score intelligence → conseils contextuels | NE PAS recalculer synthese saline |

### Points de fusion

| Point de fusion | Module source | Module cible | Donnee |
|----------------|--------------|-------------|--------|
| SUPRA | strategy_master_engine | M4 (enrichissement conseils) | Strategies actives |
| P6 Territoire | live_heading_engine + tracking_engine | M4 (navigation) | Cap + suivi GPS |
| Zone Engine | territory_engine | M4 (contraintes itineraire) | Limites zones |
| Predictive | M3 (predictive_layer) | M4 (creneaux optimaux) | Predictions par heure |

---

## 6.5 M5 — Offline Mode Ultra + Terrain Intelligence

### ANTI-DOUBLON

| Sources utilisees | Modules consommes (lecture) | Modules INTERDITS de recreation |
|-------------------|---------------------------|-------------------------------|
| M1-M4 (toutes couches), soil_engine, ecoforestry_engine | bionic_ecological_engine, wildlife_behavior_engine | ecoforestry_engine (donnees forestieres), soil_engine (classification) |

### ANTI-DOUBLON NUTRITIONNEL

| Sources nutritionnelles | Consommation | Interdiction |
|------------------------|-------------|-------------|
| saline_recommendation_engine | LECTURE analyse complete → paquet offline | NE PAS recalculer synthese |
| soil_composition_engine | LECTURE profils sol → couche terrain | NE PAS recalculer sol |
| vegetation_forage_engine | LECTURE fourrage → couche terrain | NE PAS recalculer fourrage |
| wildlife_nutritional_engine | LECTURE besoins → suitability habitat | NE PAS redefinir besoins |
| bionic_ecological_engine | LECTURE intelligence eco → paquet offline | NE PAS recalculer intelligence |

### Points de fusion

| Point de fusion | Module source | Module cible | Donnee |
|----------------|--------------|-------------|--------|
| SUPRA | strategy_master_engine | M5 (strategies offline) | Strategies pre-calculees |
| Zone Engine | territory_engine | M5 (zones dans paquet) | Geometries |
| Species Models | wildlife_behavior_engine | M5 (comportement) | Patterns pre-charges |
| Predictive | M3 + predictive_engine | M5 (predictions offline) | Couches predictives |
| P6 Territoire | M4 (navigation) | M5 (itineraires offline) | Routes pre-planifiees |

---

# 7. MATRICE DE VERROUILLAGE

## 7.1 Conditions d'execution M1→M5

| Phase | Condition pre-execution | Verrouillage nutritionnel |
|-------|------------------------|--------------------------|
| M1 | Ce document valide par STEEVE-MAX | Sections ANTI-DOUBLON M1 validees |
| M2 | M1 complete + valide | Sections ANTI-DOUBLON M2 validees |
| M3 | M1 + M2 completes + validees | Sections ANTI-DOUBLON M3 validees |
| M4 | M1 + M2 + M3 completes + validees | Sections ANTI-DOUBLON M4 validees |
| M5 | M1 + M2 + M3 + M4 completes + validees | Sections ANTI-DOUBLON M5 validees |

## 7.2 Regles absolues

| # | Regle | Sanction |
|---|-------|---------|
| R1 | Aucun moteur nutritionnel V5 n'est duplique dans M1→M5 | Blocage execution phase |
| R2 | Toute donnee nutritionnelle est LUES via MongoDB bridge | Blocage execution phase |
| R3 | Aucun import direct entre routers M1→M5 et moteurs V5 | Blocage execution phase |
| R4 | Les schemas MongoDB M1→M5 incluent les champs nutrition documentes ici | Blocage execution phase |
| R5 | Les tests M1→M5 verifient la non-regression des endpoints V5 | Blocage execution phase |

## 7.3 Verification pre-code

Avant d'ecrire le MOINDRE code pour une phase M1→M5, verifier :

- [ ] Section ANTI-DOUBLON de la phase consultee
- [ ] Section ANTI-DOUBLON NUTRITIONNEL de la phase consultee
- [ ] Sources V5 identifiees comme LECTURE SEULE
- [ ] Aucun recalcul des fonctions listees en INTERDIT
- [ ] Points de fusion SUPRA / Zone Engine / P6 / Species / Predictive identifies
- [ ] Schemas MongoDB enrichis avec champs nutritionnels documentes

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : VALIDATION_INTERCONNEXION_NUTRITIONNELLE 1.0.0
**References** : BIONIC_V6_MAP_INTELLIGENCE_PLAN, IMPLEMENTATION_PLAN_V1
**Code modifie** : AUCUN (audit uniquement)
**Merge main** : STRICTEMENT INTERDIT
