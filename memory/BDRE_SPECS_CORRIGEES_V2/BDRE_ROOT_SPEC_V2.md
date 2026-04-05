# BDRE — BIONIC DATA RELIABILITY ENGINE
## Specification Racine V2 | BCE-4X GOLDEN V6+
## Composante FONDAMENTALE et NON NEGOCIABLE de BIONIC OS
## Directive STEEVE-MAX | Date: 2026-04-06
## Corrections appliquees: COR-01, COR-02, COR-03

---

## HISTORIQUE DES CORRECTIONS

| Correction | Description | Statut |
|------------|-------------|--------|
| COR-01 | Alignement DC-BDRE-01 avec schema SourceHealth (5→8 champs) | APPLIQUEE |
| COR-02 | Documentation F4/F5/F7/F8 comme hooks internes (pas endpoints) | APPLIQUEE |
| COR-03 | Remplacement references par numeros de ligne par noms de constantes | APPLIQUEE |
| DS-08 | Resolution contradiction waterway obstacle vs corridor | APPLIQUEE |

---

## 1. DECLARATION INSTITUTIONNELLE

Le BIONIC Data Reliability Engine (BDRE) est declare composante FONDAMENTALE
et NON NEGOCIABLE de BIONIC OS (toutes versions), d'EMERGENT (toutes analyses),
et de tous les projets, pipelines, modules, branches et architectures futures.

Aucun pipeline terrain, aucun trajet vers affut, aucune version BIONIC OS
ne peut etre valide sans validation explicite du BDRE par STEEVE-MAX.

---

## 2. POSITIONNEMENT ARCHITECTURAL

```
                      STEEVE-MAX
                         |
                    BCE-4X GOLDEN V6+
                         |
                  ┌──────┴──────┐
                  |    BDRE     |  <- RACINE TRANSVERSALE
                  └──────┬──────┘
         ┌───────┬───────┼───────┬───────┐
         |       |       |       |       |
    MON TERR.  CARTE  GUIDE PRO  M1-M5  BSAA
         |       |       |       |       |
    ┌────┴────┐  |   ┌───┴───┐   |       |
    Zones  Hotsp.|  Sessions Routes    ...
    Corrid. Trail|  Tracker Report
         |       |       |
    ┌────┴───────┴───────┴────┐
    |     SOURCES DE DONNEES   |
    | OSM  AE-V6  TNE  ForetOuv|
    | VGO  GPS   Meteo  DEM    |
    └──────────────────────────┘
```

Le BDRE se positionne ENTRE les engines/pipelines et les sources de donnees.
Chaque acces a une source DOIT transiter par le BDRE.

---

## 3. FONCTIONS OBLIGATOIRES (8)

### FONCTIONS EXPOSEES VIA API (3)

### F1 — Monitoring de disponibilite/performance APIs externes
Surveille en continu la disponibilite et le temps de reponse de chaque API
externe. Maintient un registre de sante par source.
**Endpoints**: `/sources/{id}/health`, `/health`

### F2 — Scoring de fiabilite des sources
Attribue un score de fiabilite (0.0 -> 1.0) a chaque source de donnees
en fonction de: couverture, fraicheur, precision, completude, coherence.
**Endpoints**: `/sources/{id}/score`, `/quality/report`

### F6 — Journalisation institutionnelle permanente
Enregistre chaque acces source, chaque score, chaque fallback, chaque alerte
dans un journal permanent et auditable.
**Endpoints**: `/audit/log`, `/fallbacks/recent`

### FONCTIONS INTERNES (HOOKS, PAS D'ENDPOINTS) (5)

### F3 — Detection automatique sources vides/incoherentes/obsoletes
Detecte et signale automatiquement les sources vides (cache AE-V6 = 0 noeuds),
incoherentes (noeuds orphelins), ou obsoletes (cache > TTL).
**Type**: Hook interne declenche automatiquement par F1 et F2.
**Emission**: EventBus EB-BDRE-03 (bdre:source:empty)

### F4 — Selection dynamique meilleure source selon BCE-4X
Selectionne automatiquement la meilleure source disponible pour chaque requete
en fonction du score de fiabilite et des criteres BCE-4X.
**Type**: Hook interne appele par chaque engine avant acces source.
**Pas d'endpoint API**: Logique interne au BDRE, invisible depuis l'exterieur.

### F5 — Declenchement automatique pipeline hybride 4 niveaux
Quand la source primaire echoue ou est vide, declenche automatiquement
le niveau suivant du pipeline hybride:
  1. Waterway Bank Routing -> 2. Terrain Topology -> 3. Corridor A* -> 4. GPS Tracks
**Type**: Hook interne declenche par F4 quand le score < seuil.
**Pas d'endpoint API**: Orchestration interne transparente pour les engines.
**IMPORTANT**: Ce pipeline REMPLACE les cascades de fallback existantes dans
`access_engine.py` et `stand_recommendation/engine.py`. Il ne se superpose PAS.

### F7 — Integration dans tous les engines terrain
Chaque engine qui accede a des donnees terrain DOIT passer par le BDRE.
**Type**: Pattern d'injection de hooks (pre-call, post-call, fallback).
**Pas d'endpoint API**: Integration au niveau du code source des engines.

### F8 — Integration dans tous les trajets humains et affuts
Chaque calcul de trajet humain ou route vers affut DOIT etre valide par
le BDRE avant d'etre retourne au frontend.
**Type**: Validation post-calcul systematique.
**Pas d'endpoint API**: Appel interne BDRE.validate_route().

---

## 4. REGISTRE DES SOURCES

### 4.1 Sources externes (APIs)

| ID | Source | Type | Endpoint | Cache | TTL |
|---|---|---|---|---|---|
| SRC-01 | OpenStreetMap (Overpass) | Sentiers/Routes | 4 miroirs | data/terrain_cache/ | 7 jours |
| SRC-02 | OpenStreetMap (Overpass) | Eau/Obstacles | Via TNE | data/terrain_cache/ | 7 jours |
| SRC-03 | Access Engine V6 OSM | Trail graph | Via osm_trails.py | modules/access_engine_v6/cache/ | 7 jours |
| SRC-04 | Foret Ouverte (MFFP) | Peuplements forestiers | WMS/WFS Quebec | Non cache | N/A |
| SRC-05 | VGO (Vegetal) | Couvert vegetal | API MFFP | Non cache | N/A |
| SRC-06 | DEM/SRTM | Elevation | Via dem_router | data/elevation_cache/ | 30 jours |
| SRC-07 | Meteo | Previsions | weatherapi.com | RAM | 1 heure |
| SRC-08 | GPS Tracks | Traces reelles | Import utilisateur | MongoDB | Permanent |

### 4.2 Sources internes (hardcoded)

| ID | Source | Type | Reference | Mutable |
|---|---|---|---|---|
| INT-01 | TERRAIN_COSTS | Couts terrain animaux | corridor_10x.py:TERRAIN_COSTS | Non |
| INT-02 | HUMAN_TRAJET_COSTS | Couts terrain humains | corridor_10x.py:HUMAN_TRAJET_COSTS | Non |
| INT-03 | LAYER_TO_TERRAIN | Mapping zone->terrain | zone_engine_core_v2.py:LAYER_TO_TERRAIN | Non |
| INT-04 | Ecological DB V8 | Base ecologique | ecological_database_v8.py:EcologicalDB | Non |
| INT-05 | Species Rules | Regles especes | knowledge/species/*.py | Non |
| INT-06 | Water Exclusion DB | Base zones eau | knowledge/terrain/water_exclusion.py | Non |
| INT-07 | OSM_HIGHWAY_TO_TERRAIN | Mapping OSM->terrain | engine_osm_lite.py:OSM_HIGHWAY_TO_TERRAIN | Non |
| INT-08 | ROAD_COSTS | Couts routes trail grid | trail_cost_grid_v7.py:ROAD_COSTS | Non |

**COR-03 APPLIQUEE**: Toutes les references pointent vers des noms de
constantes/classes, pas des numeros de ligne. Les numeros de ligne sont volatils.

---

## 5. DATACONTRACTS BDRE

### DC-BDRE-01 — SourceHealthContract (COR-01 APPLIQUEE: 8 champs)

```
{
    "source_id": str,           // "SRC-01"
    "status": str,              // "healthy" | "degraded" | "down" | "empty"
    "latency_ms": float,        // Derniere latence
    "last_check": str,          // ISO timestamp
    "score": float,             // 0.0 -> 1.0
    "checks_24h": int,          // Nombre de checks en 24h
    "failures_24h": int,        // Nombre d'echecs en 24h
    "availability_pct": float   // % disponibilite sur 24h
}
```

### DC-BDRE-02 — DataQualityContract

```
{
    "source_id": str,
    "coverage": float,          // 0.0 -> 1.0
    "freshness": float,         // 0.0 -> 1.0
    "precision": float,         // 0.0 -> 1.0
    "completeness": float,      // 0.0 -> 1.0
    "coherence": float,         // 0.0 -> 1.0
    "score": float              // Moyenne ponderee BCE-4X
}
```

### DC-BDRE-03 — FallbackChainContract

```
{
    "request_id": str,
    "levels_tried": [int],      // [1, 2, 3] = 3 niveaux tentes
    "selected_source": str,     // "SRC-01" ou "LEVEL-3-CORRIDOR-ASTAR"
    "reason": str               // "primary_deficient_score_0.31"
}
```

### DC-BDRE-04 — AuditLogContract

```
{
    "timestamp": str,           // ISO
    "engine": str,              // "TNE" | "ACCESS" | "STAND_RECO" | ...
    "source_id": str,           // "SRC-01"
    "action": str,              // "success" | "fallback" | "alert" | "empty"
    "result": str,              // Description
    "score": float,             // Score BDRE au moment de l'action
    "fallback_level": int       // 0 (pas de fallback) | 1-4
}
```

---

## 6. EVENTBUS BDRE

| ID | Channel | Emetteur | Abonnes |
|---|---|---|---|
| EB-BDRE-01 | bdre:source:down | Monitoring F1 | Tous engines |
| EB-BDRE-02 | bdre:source:degraded | Scoring F2 | Tous engines |
| EB-BDRE-03 | bdre:source:empty | Detection F3 | Audit, Logs |
| EB-BDRE-04 | bdre:fallback:triggered | Pipeline F5 | Audit, Dashboard |
| EB-BDRE-05 | bdre:quality:alert | Scoring F2 | STEEVE-MAX alert |

---

## 7. INTEGRATION RACINES

### 7.1 Racine BIONIC OS
Tous les engines BIONIC OS DOIVENT:
1. Interroger le BDRE avant d'acceder a une source externe
2. Recevoir le score de fiabilite de la source
3. Utiliser la source selectionnee par le BDRE (pas de choix arbitraire)
4. Signaler tout fallback au BDRE pour journalisation

### 7.2 Racine EMERGENT
Toutes les analyses et audits EMERGENT DOIVENT:
1. Consulter le registre BDRE pour evaluer la fiabilite des donnees analysees
2. Inclure le score BDRE dans les rapports BCE-4X
3. Signaler les infractions de fiabilite (source vide, obsolete, incoherente)

### 7.3 Racine projets futurs
Tous les projets futurs (Phase F, M5, BIONIC OS V9+) DOIVENT:
1. Declarer leurs sources de donnees dans le registre BDRE
2. Implementer les hooks BDRE dans leur pipeline
3. Respecter la chaine de fallback 4 niveaux

---

## 8. RESOLUTION DS-8 — CLASSIFICATION HYDROLOGIQUE

### 8.1 Probleme (DS-8)

`terrain_costs.py:build_obstacle_set()` marque TOUS les waterways comme
obstacles infranchissables. Cela empeche le BDRE Level 1 (Waterway Bank
Routing) d'utiliser les berges de ruisseaux comme corridors navigables.

### 8.2 Classification Hydrologique BDRE

Le BDRE impose la classification suivante:

| Element OSM | Tag OSM | Classification BDRE | Cout | Navigable ? |
|-------------|---------|---------------------|------|-------------|
| Lac, etang | natural=water | OBSTACLE | 999.0 | NON |
| Marecage, marais | natural=wetland | OBSTACLE | 50.0 | NON |
| Riviere large (>10m) | waterway=river | OBSTACLE (centre) + CORRIDOR (berges) | 999.0 / 1.2 | BERGES OUI |
| Ruisseau | waterway=stream | CORRIDOR navigable (berges) | 1.2 | OUI |
| Fosse | waterway=ditch | CORRIDOR navigable | 1.0 | OUI |
| Drain | waterway=drain | CORRIDOR navigable | 1.0 | OUI |
| Canal | waterway=canal | OBSTACLE (eau) + CORRIDOR (berges) | 999.0 / 1.2 | BERGES OUI |

### 8.3 Modification Requise (build_obstacle_set)

```python
# AVANT (code actuel — DS-8 VIOLATION):
if natural in ("water", "wetland") or waterway:
    obstacle_nodes.add(nid)

# APRES (classification hydrologique BDRE):
if natural in ("water", "wetland"):
    obstacle_nodes.add(nid)
elif waterway in ("river", "canal"):
    # Riviere/canal: noeuds centraux = obstacles, berges = corridors
    # Les berges seront ajoutees comme corridors par build_waterway_corridor_set()
    obstacle_nodes.add(nid)
elif waterway in ("stream", "ditch", "drain"):
    # Ruisseaux/fosses: corridors navigables, PAS obstacles
    # NE PAS ajouter dans obstacle_nodes
    pass
```

### 8.4 Nouvelle Fonction Requise (build_waterway_corridor_set)

Le constructeur de graphe (`terrain_graph.py:build_terrain_graph`) DOIT
integrer une nouvelle etape pour ajouter les waterways navigables:

```
build_terrain_graph(terrain_data):
    1. build_obstacle_set(obstacles)           [EXISTANT — modifie DS-8]
    2. build_forest_set(forest)                [EXISTANT — inchange]
    3. build_waterway_corridor_set(waterways)  [NOUVEAU — BDRE Level 1]
    4. add_trail_ways(trails)                  [EXISTANT — inchange]
    5. add_waterway_corridor_ways(waterways)   [NOUVEAU — BDRE Level 1]
    6. add_clearing_edge_ways(clearings)       [NOUVEAU — BDRE Level 2]
    7. finalize_stats()                        [EXISTANT — inchange]
```

---

## 9. CONFORMITE BCE-4X

| Critere | Application BDRE |
|---------|---------|
| ZERO INTERPRETATION | Le BDRE score objectivement, pas subjectivement |
| ZERO DOUBLON | Le BDRE unifie les acces sources (un seul point d'entree). Les cascades existantes sont REMPLACEES, pas dupliquees |
| ZERO REGRESSION | Le BDRE garantit un fallback avant tout echec silencieux |
| ZERO OBSOLESCENCE | Le BDRE detecte et signale les donnees perimees |
| ZERO LOSS | Le BDRE interdit de retourner un resultat vide sans avoir epuise toutes les sources |

---

**STATUT: SPECIFICATION RACINE V2 COMPLETE — CORRECTIONS COR-01, COR-02, COR-03, DS-08 APPLIQUEES**
**EN ATTENTE VALIDATION STEEVE-MAX**
