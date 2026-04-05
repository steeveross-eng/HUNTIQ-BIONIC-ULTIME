# BDRE — BIONIC DATA RELIABILITY ENGINE
## Specification Racine | BCE-4X GOLDEN V6+
## Composante FONDAMENTALE et NON NEGOCIABLE de BIONIC OS
## Directive STEEVE-MAX | Date: 2026-04-05

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
                  |    BDRE     |  ← RACINE TRANSVERSALE
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

### F1 — Monitoring de disponibilite/performance APIs externes
Surveille en continu la disponibilite et le temps de reponse de chaque API
externe. Maintient un registre de sante par source.

### F2 — Scoring de fiabilite des sources
Attribue un score de fiabilite (0.0 → 1.0) a chaque source de donnees
en fonction de: couverture, fraicheur, precision, completude, coherence.

### F3 — Detection automatique sources vides/incoherentes/obsoletes
Detecte et signale automatiquement les sources vides (cache AE-V6 = 0 noeuds),
incoherentes (noeuds orphelins), ou obsoletes (cache > TTL).

### F4 — Selection dynamique meilleure source selon BCE-4X
Selectionne automatiquement la meilleure source disponible pour chaque requete
en fonction du score de fiabilite et des criteres BCE-4X.

### F5 — Declenchement automatique pipeline hybride 4 niveaux
Quand la source primaire echoue ou est vide, declenche automatiquement
le niveau suivant du pipeline hybride:
  1. Waterway Routing → 2. Terrain Topology → 3. Corridor A* → 4. GPS Tracks

### F6 — Journalisation institutionnelle permanente
Enregistre chaque acces source, chaque score, chaque fallback, chaque alerte
dans un journal permanent et auditable.

### F7 — Integration dans tous les engines terrain
Chaque engine qui accede a des donnees terrain DOIT passer par le BDRE.

### F8 — Integration dans tous les trajets humains et affuts
Chaque calcul de trajet humain ou route vers affut DOIT etre valide par
le BDRE avant d'etre retourne au frontend.

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

| ID | Source | Type | Fichier | Mutable |
|---|---|---|---|---|
| INT-01 | TERRAIN_COSTS | Couts terrain animaux | corridor_10x.py:10-83 | Non |
| INT-02 | HUMAN_TRAJET_COSTS | Couts terrain humains | corridor_10x.py:499-533 | Non |
| INT-03 | LAYER_TO_TERRAIN | Mapping zone→terrain | zone_engine_core_v2.py:1007-1018 | Non |
| INT-04 | Ecological DB V8 | Base ecologique | ecological_database_v8.py | Non |
| INT-05 | Species Rules | Regles especes | knowledge/species/*.py | Non |
| INT-06 | Water Exclusion DB | Base zones eau | knowledge/terrain/water_exclusion.py | Non |
| INT-07 | OSM_HIGHWAY_TO_TERRAIN | Mapping OSM→terrain | engine_osm_lite.py:37-49 | Non |
| INT-08 | ROAD_COSTS | Couts routes trail grid | trail_cost_grid_v7.py:33-67 | Non |

---

## 5. DATACONTRACTS BDRE

| ID | Nom | Schema |
|---|---|---|
| DC-BDRE-01 | SourceHealthContract | { source_id, status, latency_ms, last_check, score } |
| DC-BDRE-02 | DataQualityContract | { source_id, coverage, freshness, precision, completeness, coherence, score } |
| DC-BDRE-03 | FallbackChainContract | { request_id, levels_tried[], selected_source, reason } |
| DC-BDRE-04 | AuditLogContract | { timestamp, engine, source_id, action, result, score, fallback } |

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

## 8. CONFORMITE BCE-4X

| Critere | Application BDRE |
|---------|---------|
| ZERO INTERPRETATION | Le BDRE score objectivement, pas subjectivement |
| ZERO DOUBLON | Le BDRE unifie les acces sources (un seul point d'entree) |
| ZERO REGRESSION | Le BDRE garantit un fallback avant tout echec silencieux |
| ZERO OBSOLESCENCE | Le BDRE detecte et signale les donnees perimees |
| ZERO LOSS | Le BDRE interdit de retourner un resultat vide sans avoir epuise toutes les sources |

---

**STATUT: SPECIFICATION RACINE COMPLETE — EN ATTENTE VALIDATION STEEVE-MAX**
