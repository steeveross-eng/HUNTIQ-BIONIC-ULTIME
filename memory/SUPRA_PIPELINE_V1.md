# SUPRA_PIPELINE_V1 — SPECIFICATION PIPELINE SCORING BIONIC OS
## Directive x5310-STEEVE_MAX — Version 1.0.0
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-05 | Merge MAIN : STRICTEMENT INTERDIT
### Reference : AUBO_V2.md Section 2.1 + Section 5

---

# TABLE DES MATIERES

1. [VUE D'ENSEMBLE](#1-vue-densemble)
2. [ARCHITECTURE PIPELINE](#2-architecture-pipeline)
3. [MODULES — SPECIFICATION DETAILLEE](#3-modules-specification-detaillee)
4. [SERVICES DE SCORING (9 SCORES)](#4-services-de-scoring)
5. [CORE/SCORING_PIPELINE (20 SOUS-MOTEURS)](#5-corscoring_pipeline)
6. [PIPELINE V7 (EVOLUTION)](#6-pipeline-v7)
7. [ESPECES SUPPORTEES](#7-especes-supportees)
8. [ENDPOINTS API](#8-endpoints-api)
9. [VALIDATION BCE-4X](#9-validation-bce-4x)
10. [FLUX DE DONNEES COMPLET](#10-flux-de-donnees-complet)

---

# 1. VUE D'ENSEMBLE

## 1.1 Objectif

Le Pipeline SUPRA est le coeur fonctionnel de BIONIC OS. Il orchestre l'analyse multi-criteres
d'un territoire de chasse pour produire un **Score /100** decompose en **32 criteres detailles**,
des **zones ecologiques**, des **corridors de deplacement** et des **hotspots**.

## 1.2 Principes immuables

| Principe | Description |
|----------|-------------|
| **ZERO TRANSVERSALITE** | Aucun module n'appelle directement un autre module |
| **ZERO DUPLICATION** | Chaque calcul est execute une seule fois |
| **ORDRE SEQUENTIEL STRICT** | SSE→OSG→CME→WSE→VFE→SSVL→TCVE→PME→BMPE→TFE |
| **ISOLATION COMPLETE** | Chaque module communique uniquement via ses entrees/sorties |
| **BACKEND TRUTH** | Le backend est la seule source de verite pour les scores |

## 1.3 Entree / Sortie globale

**Entree** :
```
{
  bounds: { north: float, south: float, east: float, west: float },
  species: string (moose | deer | bear | wild_turkey | elk),
  resolution: int (20-120, defaut 60),
  layers: string[] (defaut ["habitats", "alimentation"]),
  max_zones_per_layer: int (1-20, defaut 4),
  max_corridors: int (1-20, defaut 6),
  base_wind_kmh: float (0-120, defaut 15.0),
  base_direction_deg: float (0-360, defaut 270.0)
}
```

**Sortie** :
```
{
  pipeline: "BIONIC_V5_ULTIME_300",
  species: string,
  bounds: object,
  resolution: int,
  pipeline_source_ids: { sse, osg, cme, wse, vfe, ssvl, tcve, pme, bmpe, tfe },
  module_count: 10,
  module_stats: { SSE: {}, OSG: {}, ... TFE: {} },
  module_timings_ms: { SSE: float, OSG: float, ... TFE: float },
  total_computation_time_ms: float,
  corridor_analyses: {
    pme_pressure: [...],
    bmpe_micro_patterns: [...],
    tfe_thermal: [...]
  },
  corridor_count: int,
  validation: {
    all_modules_executed: bool,
    pipeline_order: string,
    zero_transversality: bool,
    zero_duplication: bool,
    source_ids_dynamic: bool,
    all_fields_normalized: bool,
    species_profile_applied: bool
  }
}
```

---

# 2. ARCHITECTURE PIPELINE

## 2.1 Diagramme d'execution

```
ENTREE: bounds + species + resolution
    |
    v
[MODULE 1: SSE] ─── Satellite-to-Semantic Engine
    |  Sorties: forest_density, clearing_map, edge_transitions,
    |           microrelief, elevation, water_mask, landcover
    v
[MODULE 2: OSG] ─── Organic Shape Generator
    |  Entrees: SSE
    |  Sorties: zones organiques (par layer), zone_count, contours
    v
[MODULE 3: CME] ─── Corridor Morphology Engine
    |  Entrees: SSE + OSG
    |  Sorties: corridors[], corridor_types, movement paths
    v
[MODULE 4: WSE/WIV] ─── Wind/Weather Scoring + Wind Impact Vector
    |  Entrees: SSE
    |  Sorties: wind_speed, wind_direction, gust_field, wind_impact
    v
[MODULE 5: VFE] ─── Visual Fusion Engine
    |  Entrees: SSE + WSE
    |  Sorties: visibility_field, cover_opacity, fog_occlusion, visual_composite
    v
[MODULE 6: SSVL] ─── Species-Specific Visual Logic
    |  Entrees: VFE + SSE + WSE
    |  Sorties: prudence_field, vigilance, flight_response, motion_sensitivity
    v
[MODULE 7: TCVE] ─── Terrain Calibration Visual Engine
    |  Entrees: SSE + WSE + SSVL + VFE
    |  Sorties: slope_visibility_calibration, terrain_roughness, terrain_cover_index
    v
[MODULE 8: PME] ─── Pressure Memory Engine
    |  Entrees: SSE + WSE + SSVL + TCVE + bounds
    |  Sorties: pressure_memory, pressure_intensity, pressure_recency, pressure_remanence
    |  + Analyse corridors (pme_pressure)
    v
[MODULE 9: BMPE] ─── Behavioral Micro-Patterns Engine
    |  Entrees: SSE + WSE + SSVL + TCVE + PME + bounds
    |  Sorties: micro_retreat, micro_exploration, hesitation, fine_movement, composite
    |  + Analyse corridors (bmpe_micro_patterns)
    v
[MODULE 10: TFE] ─── Thermal Flow Engine
    |  Entrees: SSE + WSE + SSVL + TCVE + PME + BMPE + bounds
    |  Sorties: thermal_gradient, thermal_inertia, hot_pocket, cold_pocket, flow_composite
    |  + Analyse corridors (tfe_thermal)
    v
SORTIE: Score /100 + 32 criteres + zones + corridors + hotspots
```

## 2.2 Matrice des dependances

| Module | Depend de | Fournit a |
|--------|-----------|-----------|
| SSE (1) | bounds, species, resolution | OSG, CME, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE |
| OSG (2) | SSE | CME |
| CME (3) | SSE, OSG | PME, BMPE, TFE (analyse corridors) |
| WSE (4) | SSE | VFE, SSVL, TCVE, PME, BMPE, TFE |
| VFE (5) | SSE, WSE | SSVL, TCVE |
| SSVL (6) | VFE, SSE, WSE | TCVE, PME, BMPE, TFE |
| TCVE (7) | SSE, WSE, SSVL, VFE | PME, BMPE, TFE |
| PME (8) | SSE, WSE, SSVL, TCVE, bounds | BMPE, TFE |
| BMPE (9) | SSE, WSE, SSVL, TCVE, PME, bounds | TFE |
| TFE (10) | SSE, WSE, SSVL, TCVE, PME, BMPE, bounds | — (terminal) |

**Observation** : SSE est le module fondateur — toute la chaine en depend.
Les modules 6-10 accumulent les dependances progressivement (pattern accumulateur).

## 2.3 Versions du pipeline

| Version | Fichier | Statut | Role |
|---------|---------|--------|------|
| Pipeline Legacy | pipeline_service.py | GELE (2026-03-10) | 10 modules sequentiels purs |
| Pipeline V7 | pipeline_v7.py | ACTIF | Integre exclusion V6/V7, zone typology, terrain signals, corridors V7, zone shape V7, species behavior V7 |

Le Pipeline V7 remplace `_process_single_layer()` quand `EXCLUSION_ENGINE_VERSION=v7`.
Le Pipeline Legacy reste la reference pour l'ordre d'execution des 10 modules.

---

# 3. MODULES — SPECIFICATION DETAILLEE

## 3.1 MODULE 1 : SSE — Satellite-to-Semantic Engine

**Phase** : Optimisation #1
**Fichier** : `services/sse_engine.py`
**Fonction** : `generate_landcover_raster(bounds, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| bounds | Dict[north,south,east,west] | Coordonnees de la zone |
| species | str | Espece cible |
| resolution | int | Resolution de la grille |
| **Sorties** | | |
| forest_density | ndarray [0,1] | Densite du couvert forestier |
| clearing_map | ndarray [0,1] | Probabilite de clairiere |
| edge_transitions | ndarray [0,1] | Transitions lisiere foret/clairiere |
| microrelief | ndarray | Micro-relief du terrain |
| elevation | ndarray | Elevation en metres |
| water_mask | ndarray [0,1] | Masque des zones d'eau |
| source_id | str | Identifiant unique du calcul |
| stats | dict | Statistiques (mean, range) |

**Role** : Extraction semantique du terrain a partir des donnees satellite et topographiques.
Produit les rasters fondamentaux utilises par tous les modules suivants.

---

## 3.2 MODULE 2 : OSG — Organic Shape Generator

**Phase** : Optimisation #2
**Fichier** : `services/osg_engine.py`
**Fonction** : `generate_osg_multi_layer(bounds, species, layers, sse, resolution, max_zones)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| bounds | Dict | Coordonnees |
| species | str | Espece |
| layers | List[str] | Couches a generer (habitats, alimentation, etc.) |
| sse | Dict | Resultats SSE |
| resolution | int | Resolution |
| max_zones | int | Max zones par couche |
| **Sorties** | | |
| layers | List[Dict] | Zones organiques par couche |
| zone_count | int | Nombre total de zones |
| source_id | str | Identifiant unique |

**Role** : Generation de formes organiques enrichies par le SSE. Module la grille de base
avec le composite SSE pour amplifier les zones a haute valeur semantique.

---

## 3.3 MODULE 3 : CME — Corridor Morphology Engine

**Phase** : Optimisation #3
**Fichier** : `services/cme_engine.py`
**Fonction** : `generate_cme_corridors(bounds, species, sse, osg, resolution, types, max_corridors)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| bounds | Dict | Coordonnees |
| species | str | Espece |
| sse | Dict | Resultats SSE (microrelief, forest_density) |
| osg | Dict | Resultats OSG (zones organiques) |
| resolution | int | Resolution |
| types | List[str] | Types de corridors (movement, feeding_transit) |
| max_corridors | int | Max corridors |
| **Sorties** | | |
| corridors | List[Dict] | Corridors avec geometrie et metadata |
| source_id | str | Identifiant unique |

**Role** : Generation de corridors morphologiquement realistes. Routage par vallees et
micro-relief (SSE.microrelief), surface de cout de mouvement, lissage Chaikin, micro-perturbation.

---

## 3.4 MODULE 4 : WSE/WIV — Wind/Weather Scoring Engine + Wind Impact Vector

**Phase** : Optimisation #4
**Fichier** : `services/wse_wiv_engine.py`
**Fonction** : `generate_wind_field(bounds, species, sse, resolution, base_wind_kmh, base_direction_deg)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| bounds | Dict | Coordonnees |
| species | str | Espece |
| sse | Dict | Resultats SSE (forest_density, elevation) |
| base_wind_kmh | float | Vitesse du vent de base |
| base_direction_deg | float | Direction du vent de base |
| **Sorties** | | |
| wind_speed | ndarray | Champ de vent au sol (km/h) |
| wind_direction | ndarray | Direction du vent |
| gust_field | ndarray | Champ de rafales |
| source_id | str | Identifiant unique |

**Role** : Modulation du vent par le terrain. La densite forestiere reduit la vitesse du vent (abri),
les cretes accelerent le vent (exposition). Profils specifiques par espece.

---

## 3.5 MODULE 5 : VFE — Visual Fusion Engine

**Phase** : Optimisation #5
**Fichier** : `services/vfe_engine.py`
**Fonction** : `generate_visibility_field(sse, wse, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| sse | Dict | Resultats SSE (landcover, microrelief) |
| wse | Dict | Resultats WSE (wind_speed) |
| species | str | Espece |
| **Sorties** | | |
| visibility_field | ndarray [0,1] | Qualite de visibilite globale |
| cover_opacity | ndarray [0,1] | Qualite du couvert visuel (haut = cache) |
| fog_occlusion_field | ndarray [0,1] | Occlusion par le brouillard |
| visual_composite_field | ndarray [0,1] | Composite visuel final |

**Role** : Fusion des couches certifiees SSE + WSE pour produire le champ de visibilite.
Profils de visibilite specifiques par espece (VFE_VISIBILITY_PROFILES).

---

## 3.6 MODULE 6 : SSVL — Species-Specific Visual Logic

**Phase** : Optimisation #6
**Fichier** : `services/ssvl_engine.py`
**Fonction** : `generate_ssvl_fields(vfe, sse, wse, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| vfe | Dict | Resultats VFE (visibility, cover) |
| sse | Dict | Resultats SSE (terrain) |
| wse | Dict | Resultats WSE (vent) |
| species | str | Espece |
| **Sorties** | | |
| prudence_field | ndarray [0,1] | Niveau de prudence spatiale |
| vigilance | ndarray [0,1] | Vigilance comportementale |
| flight_response | ndarray [0,1] | Reponse de fuite |
| motion_sensitivity | ndarray [0,1] | Sensibilite au mouvement |
| composite | ndarray [0,1] | Composite comportemental |

**Role** : Preferences visuelles comportementales par espece. Utilise les profils SSVL_PROFILES
pour moduler la prudence, vigilance, et sensibilite au mouvement.

---

## 3.7 MODULE 7 : TCVE — Terrain Calibration Visual Engine

**Phase** : Optimisation #7
**Fichier** : `services/tcve_engine.py`
**Fonction** : `generate_tcve_fields(sse, wse, ssvl, vfe, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| sse | Dict | Resultats SSE (elevation, microrelief) |
| wse | Dict | Resultats WSE (vent) |
| ssvl | Dict | Resultats SSVL (comportement) |
| vfe | Dict | Resultats VFE (visibilite) |
| species | str | Espece |
| **Sorties** | | |
| terrain_visibility_calibration_field | ndarray [0,1] | Impact pente sur visibilite |
| terrain_roughness_field | ndarray [0,1] | Rugosite du terrain |
| terrain_cover_index_field | ndarray [0,1] | Index de couvert terrain |

**Role** : Calibration de la visibilite par les caracteristiques du terrain.
Integre l'interaction terrain-vent et la calibration comportementale par espece (TCVE_PROFILES).

---

## 3.8 MODULE 8 : PME — Pressure Memory Engine

**Phase** : Optimisation #8
**Fichier** : `services/pme_engine.py`
**Fonction** : `generate_pme_fields(sse, wse, ssvl, tcve, bounds, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| sse, wse, ssvl, tcve | Dict | Resultats modules precedents |
| bounds | Dict | Coordonnees (pour calculs GPS) |
| species | str | Espece |
| **Sorties** | | |
| pressure_memory_field | ndarray [0,1] | Historique de pression spatiale |
| pressure_intensity_field | ndarray [0,1] | Intensite de la pression |
| pressure_recency_field | ndarray [0,1] | Recence de la pression |
| pressure_remanence_field | ndarray [0,1] | Remanence residuelle |

**Analyse corridors** : `analyze_corridor_pressure(corridors, pme, bounds, resolution, species)`
Evalue la pression le long de chaque corridor genere par CME.

**Role** : Memoire spatiale de la pression de chasse. Modelise l'impact cumule de la presence
humaine sur le comportement animal (PME_PROFILES par espece).

---

## 3.9 MODULE 9 : BMPE — Behavioral Micro-Patterns Engine

**Phase** : Optimisation #9
**Fichier** : `services/bmpe_engine.py`
**Fonction** : `generate_bmpe_fields(sse, wse, ssvl, tcve, pme, bounds, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| sse, wse, ssvl, tcve, pme | Dict | Resultats modules precedents |
| bounds | Dict | Coordonnees |
| species | str | Espece |
| **Sorties** | | |
| micro_retreat_field | ndarray [0,1] | Probabilite de micro-recul |
| micro_exploration_field | ndarray [0,1] | Probabilite de micro-exploration |
| hesitation_field | ndarray [0,1] | Zones d'hesitation |
| fine_movement_field | ndarray [0,1] | Mouvements fins |
| composite_micro_pattern | ndarray [0,1] | Composite micro-patterns |

**Analyse corridors** : `analyze_corridor_micro_patterns(corridors, bmpe, bounds, resolution)`
Identifie les micro-patterns comportementaux le long des corridors.

**Role** : Modelisation des micro-patterns comportementaux — reaction fine de l'animal
aux conditions locales (pression, exposition, abri).

---

## 3.10 MODULE 10 : TFE — Thermal Flow Engine

**Phase** : Optimisation #10 (terminal)
**Fichier** : `services/tfe_engine.py`
**Fonction** : `generate_tfe_fields(sse, wse, ssvl, tcve, pme, bmpe, bounds, species, resolution)`

| Champ | Type | Description |
|-------|------|-------------|
| **Entrees** | | |
| sse, wse, ssvl, tcve, pme, bmpe | Dict | Resultats de TOUS les modules precedents |
| bounds | Dict | Coordonnees |
| species | str | Espece |
| **Sorties** | | |
| thermal_gradient_field | ndarray [0,1] | Gradient thermique spatial |
| thermal_inertia_field | ndarray [0,1] | Inertie thermique du terrain |
| hot_pocket_field | ndarray [0,1] | Poches de chaleur |
| cold_pocket_field | ndarray [0,1] | Poches de froid |
| thermal_flow_composite | ndarray [0,1] | Composite flux thermique |

**Analyse corridors** : `analyze_corridor_thermal(corridors, tfe, bounds, resolution)`
Evalue les gradients thermiques le long des corridors.

**Role** : Module terminal. Integre tous les resultats precedents pour modeliser les flux
thermiques et leur impact sur le positionnement de la faune (exposition, couvert, elevation).

---

# 4. SERVICES DE SCORING

## 4.1 Architecture

9 services de scoring isoles, orchestres par `unified_scoring_service.py`.
Interface commune via `BaseScoreService`.

```
unified_scoring_service.py (Orchestrateur)
    |
    +---> ScoreProbabilityService  (1) — Probabilite de succes
    +---> ScoreHabitatService      (2) — Qualite habitat
    +---> ScorePressureService     (3) — Pression chasse/humaine
    +---> ScoreWeatherService      (4) — Conditions meteo
    +---> ScoreBehaviorService     (5) — Comportement animal
    +---> ScoreMultiFactorService  (6) — Facteurs multiples
    +---> ScoreDensityService      (7) — Densite population
    +---> ScoreRiskService         (8) — Risques et dangers
    +---> ScoreMobilityService     (9) — Mobilite et mouvements
    |
    +---> LegalHoursService (temporal_factor)
    +---> AdvancedFactorsRegistry (facteurs avances Phase B)
    |
    v
    UnifiedScoreResult (score final /100 + detail par service)
```

## 4.2 Detail des 9 services

| # | Service | Fichier | Criteres evalues |
|---|---------|---------|-----------------|
| S1 | ScoreProbabilityService | score_probability_service.py | Probabilite de succes basee sur historique, saison, meteo |
| S2 | ScoreHabitatService | score_habitat_service.py | Qualite habitat (foret, eau, nourriture, abri) |
| S3 | ScorePressureService | score_pressure_service.py | Pression de chasse (PME), densite chasseurs, routes |
| S4 | ScoreWeatherService | score_weather_service.py | Conditions meteo (vent, temperature, precipitations) |
| S5 | ScoreBehaviorService | score_behavior_service.py | Patterns comportementaux (rut, alimentation, repos) |
| S6 | ScoreMultiFactorService | score_multifactor_service.py | Combinaison multi-criteres ponderee |
| S7 | ScoreDensityService | score_density_service.py | Densite de population animale estimee |
| S8 | ScoreRiskService | score_risk_service.py | Facteurs de risque (securite, acces, terrain) |
| S9 | ScoreMobilityService | score_mobility_service.py | Mobilite animale (corridors, deplacement, patterns) |

## 4.3 Modes d'analyse

| Mode | Description | Impact sur scoring |
|------|-------------|-------------------|
| live | Temps reel — conditions actuelles | temporal_factor actif, meteo temps reel |
| pre_rut | Pre-rut — preparation accouplement | Modificateurs pre_rut par espece |
| rut | Rut — periode d'accouplement | Modificateurs rut (comportement change) |
| post_rut | Post-rut — apres accouplement | Modificateurs post_rut |

## 4.4 Sortie unifiee

```
UnifiedScoreResult {
  score_final: float (0-100),
  grade: string (S/A/B/C/D/F),
  scores_by_service: {
    probability: { score, level, components[] },
    habitat: { score, level, components[] },
    pressure: { score, level, components[] },
    weather: { score, level, components[] },
    behavior: { score, level, components[] },
    multifactor: { score, level, components[] },
    density: { score, level, components[] },
    risk: { score, level, components[] },
    mobility: { score, level, components[] }
  },
  temporal_factor: float,
  analysis_mode: string,
  species: string,
  timestamp: datetime
}
```

---

# 5. CORE/SCORING_PIPELINE

## 5.1 Structure

20 sous-moteurs dans `/core/scoring_pipeline/` — moteurs de scoring specialises.

| # | Sous-moteur | Version | Role |
|---|-------------|---------|------|
| SP1 | alimentation_v1 | v1 | Alimentation et nutrition (classifier, scoring, layers) |
| SP2 | alimentation_v2 | v2 | Alimentation avancee (nutrition, salines, terrain) |
| SP3 | attractors_v1 | v1 | Attracteurs naturels et artificiels |
| SP4 | behavior_v1 | v1 | Comportement animal basique |
| SP5 | corridors_v10 | v10 | Corridors avances (cost surface, pathfinder, network builder, scoring) |
| SP6 | ecosystem_v1 | v1 | Ecosysteme global |
| SP7 | habitat_v1 | v1 | Qualite de l'habitat |
| SP8 | hydro_v1 | v1 | Hydrographie et plans d'eau |
| SP9 | learning_v1 | v1 | Apprentissage et adaptation |
| SP10 | multi_species_v1 | v1 | Multi-especes comparatif |
| SP11 | ndvi_vegetation_v1 | v1 | Vegetation NDVI satellite |
| SP12 | opportunity_v1 | v1 | Fenetre d'opportunite |
| SP13 | pression_v1 | v1 | Pression de chasse |
| SP14 | repos_v1 | v1 | Zones de repos (classifier, scoring, layers) |
| SP15 | risk_v1 | v1 | Evaluation des risques |
| SP16 | scenario_v1 | v1 | Scenarios de chasse |
| SP17 | simulation_v1 | v1 | Simulation meteo-faune |
| SP18 | temporal_v1 | v1 | Facteurs temporels |
| SP19 | thermal_v1 | v1 | Facteurs thermiques |
| SP20 | trajets_v1 | v1 | Calcul de trajets |
| SP21 | visibility_v1 | v1 | Visibilite terrain |
| — | score_consolide.py | — | Consolidation finale des scores |
| — | common/ | — | Utilitaires partages (classification, constants, grid, schemas, seasons, species) |

## 5.2 Sous-moteur avance : corridors_v10

Le sous-moteur le plus complexe du scoring_pipeline.

```
corridors_v10/
    +-- engine.py           — Moteur principal
    +-- multi_engine.py     — Moteur multi-corridors
    +-- cost_surface.py     — Surface de cout de deplacement
    +-- pathfinder.py       — Algorithme de recherche de chemin
    +-- network_builder.py  — Construction reseau corridors
    +-- classifier.py       — Classification des corridors
    +-- scoring.py          — Scoring des corridors
    +-- validator.py        — Validation conformite
    +-- species_profiles.py — Profils par espece
    +-- router.py           — Endpoints API
    +-- documentation.py    — Documentation auto-generee
```

---

# 6. PIPELINE V7

## 6.1 Architecture V7

Le Pipeline V7 est l'evolution active du pipeline. Il integre des couches additionnelles
de traitement entre la generation de zones (OSG) et l'assemblage final.

```
V7 Pipeline:
    bounds + species + resolution
        |
        v
    [Exclusion Engine V6/V7] — Exclusion geometrique (Shapely)
        |
        v
    [Zone Typology V7] — Classification + scoring multi-criteres
        |
        v
    [Terrain Signals V7] — Signaux terrain depuis OSM/DEM/meteo
        |
        v
    [Species Behavior V7] — Matrices comportementales par espece
        |
        v
    [Zone Shape V7] — Morphologie terrain-aware (smooth, snap, validate)
        |
        v
    [Corridor V7] — Corridors male/femelle, reel/IA
        |
        v
    Assemblage final → Score + zones + corridors
```

## 6.2 Composants V7

| Composant | Fichier | Role |
|-----------|---------|------|
| Exclusion V7 | exclusion_engine_v7.py | Exclusion geometrique des zones non-chassables |
| Zone Typology | zone_typology_v7.py | Classification + scoring + hotspot detection + global score |
| Terrain Signals | terrain_signals_v7.py | Extraction signaux terrain depuis donnees OSM/DEM/meteo |
| Species Behavior | species_behavior_v7.py | Besoins par espece + modificateurs saisonniers |
| Zone Shape | zone_shape_v7.py | Lissage adaptatif, snap shorelines, validation topologie |
| Corridor V7 | corridor_v7.py | Corridors avances avec styles (CORRIDOR_STYLES) |

## 6.3 Fusion zones V7

```python
# Fonctions cles de pipeline_v7.py
process_zones_v7()          — Traitement complet des zones avec exclusion + typology
generate_all_corridors_v7() — Generation de tous les corridors V7
build_v7_response_metadata()— Construction metadata de reponse V7
_merge_nearby_same_type_zones() — Fusion zones proches du meme type (<200m)
```

---

# 7. ESPECES SUPPORTEES

## 7.1 Liste des especes

| Code | Nom FR | Nom EN | Profils |
|------|--------|--------|---------|
| moose | Orignal | Moose | SSE, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE + knowledge/species/moose_rules |
| deer | Chevreuil | White-tailed Deer | SSE, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE + knowledge/species/deer_rules |
| bear | Ours noir | Black Bear | SSE, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE + knowledge/species/bear_rules |
| wild_turkey | Dindon sauvage | Wild Turkey | SSE, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE |
| elk | Wapiti | Elk | SSE, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE + knowledge/species/elk_rules |

## 7.2 Regles par espece (knowledge/species/)

| Fichier | Contenu |
|---------|---------|
| moose_rules.py | Comportement orignal — habitat, alimentation, rut, deplacement |
| deer_rules.py | Comportement chevreuil — lisiere, prudence, migration |
| bear_rules.py | Comportement ours — denning, hyperphagie, zones d'alimentation |
| elk_rules.py | Comportement wapiti — troupeau, paturage, migration |
| mule_deer_rules.py | Comportement cerf mulet — montagne, migration verticale |
| advanced_factors.py | Facteurs avances — registre Phase B |
| base.py | Classe de base commune |

---

# 8. ENDPOINTS API

## 8.1 Pipeline

| Methode | Endpoint | Role | Entree | Sortie |
|---------|----------|------|--------|--------|
| POST | /api/v1/bionic/pipeline/full-analysis | Analyse complete 10 modules | FullAnalysisRequest | PipelineResult |
| POST | /api/v1/bionic/pipeline/metrics | Metriques multi-especes | MetricsRequest | MetricsResult |
| POST | /api/v1/bionic/pipeline/comparison | Comparaison 2 territoires | ComparisonRequest | ComparisonResult |
| GET | /api/v1/bionic/pipeline/status | Statut du pipeline | — | StatusResponse |

## 8.2 Sous-routeurs associes

| Sous-routeur | Prefix | Endpoints | Role |
|-------------|--------|-----------|------|
| sse_router | /api/v1/bionic/sse | 2 | Calcul SSE direct |
| osg_router | /api/v1/bionic/osg | 2 | Generation zones OSG |
| cme_router | /api/v1/bionic/cme | 2 | Generation corridors CME |
| wse_wiv_router | /api/v1/bionic/wse | 2 | Champ de vent WSE |
| vfe_router | /api/v1/bionic/vfe | 2 | Visibilite VFE |
| ssvl_router | /api/v1/bionic/ssvl | 2 | Comportement visuel SSVL |
| tcve_router | /api/v1/bionic/tcve | 2 | Calibration terrain TCVE |
| pme_router | /api/v1/bionic/pme | 2 | Pression memoire PME |
| bmpe_router | /api/v1/bionic/bmpe | 2 | Micro-patterns BMPE |
| tfe_router | /api/v1/bionic/tfe | 2 | Flux thermiques TFE |
| habitat_score_router | /api/v1/bionic/habitat-score | 2 | Score habitat |
| dynamic_scores_router | /api/v1/bionic/dynamic-scores | 1 | Scores dynamiques |
| movement_corridors_router | /api/v1/bionic/corridors | 2 | Corridors mouvement |
| organic_zones_router | /api/v1/bionic/organic-zones | 3 | Zones organiques |
| spatial_clipping_router | /api/v1/bionic/spatial-clipping | 2 | Decoupage spatial |
| hunting_path_router | /api/v1/bionic/hunting-path | 2 | Sentiers de chasse |

---

# 9. VALIDATION BCE-4X

## 9.1 Validateurs pipeline

| Validateur | Fichier BCE | Regle |
|-----------|-------------|-------|
| pipeline_order | validators/pipeline_order.py | Ordre d'execution SSE→...→TFE strict |
| scoring_determinism | validators/scoring_determinism.py | Determinisme des scores (memes entrees = memes sorties) |
| engine_isolation | validators/engine_isolation.py | Isolation des moteurs (aucun import transversal) |
| species_coherence | validators/species_coherence.py | Coherence espece dans tout le pipeline |

## 9.2 Validation embarquee

Chaque execution du pipeline retourne un bloc `validation` :

```json
{
  "all_modules_executed": true,
  "pipeline_order": "SSE->OSG->CME->WSE->VFE->SSVL->TCVE->PME->BMPE->TFE",
  "zero_transversality": true,
  "zero_duplication": true,
  "source_ids_dynamic": true,
  "all_fields_normalized": true,
  "species_profile_applied": true
}
```

## 9.3 Contraintes BCE-4X

| Contrainte | Verification |
|-----------|-------------|
| ZERO LOSS | Tous les 10 modules doivent s'executer (all_modules_executed) |
| ZERO REGRESSION | Source IDs dynamiques verifient la regeneration complete |
| ZERO INTERPRETATION | Profils par espece appliques strictement (species_profile_applied) |

---

# 10. FLUX DE DONNEES COMPLET

## 10.1 Diagramme de flux end-to-end

```
[FRONTEND]                                    [BACKEND]
MonTerritoireBionicPage                       bionic_engine_p0
    |                                              |
    +---> useBionicStore (Zustand)                 |
    |     { gibier, selectedZone }                 |
    |                                              |
    +---> POST /api/v1/bionic/pipeline/full-analysis
    |                                              |
    |                                    [PIPELINE SERVICE]
    |                                    execute_full_pipeline()
    |                                         |
    |                                    SSE → OSG → CME → WSE
    |                                         |
    |                                    VFE → SSVL → TCVE → PME
    |                                         |
    |                                    BMPE → TFE
    |                                         |
    |                                    [UNIFIED SCORING]
    |                                    9 services de scoring
    |                                         |
    |                                    [CORE/SCORING_PIPELINE]
    |                                    20+ sous-moteurs
    |                                         |
    |                                    Score /100 + 32 criteres
    |                                         |
    +<--- Response JSON                       |
    |                                              |
    +---> ScoreRadarPanel (radar chart)            |
    +---> ScoreDistributionPanel (distribution)    |
    +---> OptimalWindowsTimeline (timeline)        |
    +---> BionicLegend (legende carte)             |
    +---> Couches carte (zones, corridors, heatmaps)
```

## 10.2 Integration avec les modules exterieurs

```
Pipeline SUPRA
    |
    +---> weather_v3 (/api/v3/weather)
    |     Fournit: conditions meteo temps reel
    |     Impact: WSE, ScoreWeatherService
    |
    +---> soil_engine (/api/v1/soil)
    |     Fournit: type_sol, drainage, fertilite
    |     Impact: SSE (semantique terrain), ScoreHabitatService
    |
    +---> wildlife_behavior_engine (/api/v1/wildlife)
    |     Fournit: patterns comportementaux
    |     Impact: SSVL, BMPE, ScoreBehaviorService
    |
    +---> supra_advanced (/api/v6/supra/advanced)
    |     Fournit: analyse SUPRA multi-criteres
    |     Impact: Score final consolide
    |
    +---> nutrition_intelligence (/api/v6/nutrition-intelligence)
    |     Fournit: intelligence nutritionnelle
    |     Impact: OSG (couches alimentation), ScoreHabitatService
    |
    +---> core/ecology
    |     Fournit: donnees ecologiques habitat
    |
    +---> core/corridors
    |     Fournit: calcul corridors fundateurs
    |
    +---> core/ndvi
    |     Fournit: indices vegetation satellite
    |
    +---> core/weather
    |     Fournit: donnees meteo
    |
    +---> core/pressure
          Fournit: pression anthropique
```

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : SUPRA_PIPELINE_V1 1.0.0
**Reference** : AUBO_V2.md Sections 2.1, 5, Annexe A
**Modules documentes** : 10 sous-moteurs + 9 services scoring + 20 sous-moteurs core
**Endpoints documentes** : 4 pipeline + 32 sous-routeurs
**Especes supportees** : 5 (moose, deer, bear, wild_turkey, elk)
**Merge main** : STRICTEMENT INTERDIT
