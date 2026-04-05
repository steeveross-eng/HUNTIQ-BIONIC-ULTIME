# BDRE — PLAN D'INTEGRATION V2
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-06
## Corrections appliquees: COR-04, COR-05

---

## HISTORIQUE DES CORRECTIONS

| Correction | Description | Statut |
|------------|-------------|--------|
| COR-04 | Precision des 2 fonctions _build_terrain_grid (zone + access) | APPLIQUEE |
| COR-05 | Section REMPLACEMENT cascades existantes ajoutee | APPLIQUEE |

---

## 1. ARCHITECTURE MODULE

```
backend/engines/bdre/
    __init__.py                    (Point d'entree BDRE)
    source_registry.py             (Registre des sources F1/F2)
    health_monitor.py              (Monitoring API F1)
    quality_scorer.py              (Scoring fiabilite F2)
    anomaly_detector.py            (Detection vide/incoherent F3)
    source_selector.py             (Selection dynamique F4 — HOOK INTERNE)
    fallback_chain.py              (Pipeline hybride 4 niveaux F5 — HOOK INTERNE)
    waterway_classifier.py         (Classification hydrologique DS-8)
    audit_logger.py                (Journalisation F6)
    router.py                      (Endpoints API BDRE)
```

---

## 2. PLAN D'INTEGRATION PAR ENGINE

### 2.1 TNE (Terrain Nav Engine)
| Fichier | Integration | Type |
|---|---|---|
| terrain_sources.py:_fetch_overpass() | Avant appel -> BDRE.check_source("SRC-01") | Pre-call |
| terrain_sources.py:_fetch_overpass() | Apres reponse -> BDRE.score_response() | Post-call |
| terrain_graph.py:build_terrain_graph() | Si graphe vide -> BDRE.trigger_fallback() | Fallback |
| terrain_graph.py:build_terrain_graph() | Integrer waterway corridors (DS-8) | Construction |
| terrain_router.py:route_terrain() | Si echec -> BDRE.log_fallback() | Audit |

### 2.2 ENGINE_OSM_LITE
| Fichier | Integration | Type |
|---|---|---|
| engine_osm_lite.py:load_trail_segments_from_access_cache() | Avant chargement -> BDRE.check_source("SRC-03") | Pre-call |
| engine_osm_lite.py:load_exclusions_from_osm_cache() | Score reponse -> BDRE.score_response() | Post-call |
| engine_osm_lite.py:enrich_terrain_grid() | Si 0 enrichissement -> BDRE.alert_empty() | Detection |

### 2.3 Access Engine V6
| Fichier | Integration | Type |
|---|---|---|
| access_engine.py:compute_access_route() | Cascade existante REMPLACEE par BDRE F5 | Remplacement |
| osm_trails.py:build_trail_graph() | Avant appel -> BDRE.check_source("SRC-03") | Pre-call |
| osm_trails.py:build_trail_graph() | Si cache vide -> BDRE.alert_empty("SRC-03") | Detection |

### 2.4 Corridor Engine (COR-04 APPLIQUEE: 2 fonctions distinctes)

#### 2.4a — zone_engine_core_v2.py:_build_terrain_grid()
Fonction de construction de grille pour les CORRIDORS ANIMAUX.

| Fichier | Integration | Type |
|---|---|---|
| zone_engine_core_v2.py:_build_terrain_grid() | Apres construction -> BDRE.score_grid() | Post-call |
| zone_engine_core_v2.py (appel ENGINE_OSM_LITE) | Si 0 enrichissement -> BDRE.alert_insufficient_terrain() | Detection |
| corridor_10x.py:find_path() | Si echec -> BDRE.log_fallback("corridors_animaux") | Audit |

#### 2.4b — access_engine.py:_build_terrain_grid()
Fonction de construction de grille pour les ROUTES D'ACCES HUMAINES.

| Fichier | Integration | Type |
|---|---|---|
| access_engine.py:_build_terrain_grid() | Apres construction -> BDRE.score_grid() | Post-call |
| access_engine.py:_astar_terrain_grid() | Si echec -> BDRE.log_fallback("acces_humain") | Audit |

### 2.5 Stand Recommendation Engine
| Fichier | Integration | Type |
|---|---|---|
| engine.py:recommend_stands() | Avant TNE -> BDRE.validate_sources(territory) | Pre-call |
| engine.py:_generate_approach_path() | FALLBACK 3-POINT REMPLACE par BDRE F5 | Remplacement |
| engine.py:_generate_approach_path() | Si fallback -> BDRE.trigger_hybrid_fallback() | Fallback |
| engine.py:_generate_approach_path() | Marquer trail_type avec source BDRE | Tagging |

### 2.6 GUIDE PRO
| Fichier | Integration | Type |
|---|---|---|
| guided_route_builder.py:generate_routes() | Avant calcul -> BDRE.validate_sources() | Pre-call |
| guided_route_builder.py:generate_routes() | Score routes -> BDRE.score_route_quality() | Post-call |
| post_hunt_reporter.py:generate_report() | Inclure metriques BDRE dans rapport | Enrichissement |

### 2.7 Weather Engine
| Fichier | Integration | Type |
|---|---|---|
| weather_v3/router.py | Avant appel -> BDRE.check_source("SRC-07") | Pre-call |
| weather_v3/router.py | Si fallback -> BDRE.log_fallback("meteo") | Audit |

---

## 3. ENDPOINTS API BDRE (8)

```
PREFIX: /api/v1/bdre
```

| # | Route | Method | Description | Fonction |
|---|-------|--------|-------------|----------|
| 0 | /health | GET | Sante du BDRE | F1 |
| 1 | /sources | GET | Registre complet des sources | F1/F2 |
| 2 | /sources/{id}/health | GET | Sante d'une source specifique | F1 |
| 3 | /sources/{id}/score | GET | Score de fiabilite | F2 |
| 4 | /quality/report | GET | Rapport qualite global | F2/F3 |
| 5 | /fallbacks/recent | GET | Derniers fallbacks declenches | F5/F6 |
| 6 | /audit/log | GET | Journal d'audit (pagine) | F6 |
| 7 | /validate/{territory_id} | POST | Validation BDRE d'un territoire | F4/F5 |

**Note COR-02**: Les fonctions F4 (selection dynamique), F5 (pipeline hybride),
F7 (integration engines), et F8 (integration trajets) sont des HOOKS INTERNES.
Elles n'ont pas d'endpoints API propres mais sont accessibles indirectement
via /validate/{territory_id} qui declenche F4+F5 et via /audit/log qui
expose les resultats de F7+F8.

---

## 4. STRATEGIE DE REMPLACEMENT DES CASCADES EXISTANTES (COR-05)

### 4.1 Etat Actuel — 3 Cascades Independantes

```
CASCADE A — access_engine.py:compute_access_route() (lignes 570-663)
  Niveau 1: Route sentier OSM complete (navigate_terrain)
  Niveau 2: Route HYBRIDE trail-first (hybrid_trail_terrain)
  Niveau 3: Route terrain-aware pure (grille A*)
  Niveau 4: Ligne directe (quality_score=20)

CASCADE B — engine.py:_generate_approach_path() (lignes 162-204)
  Niveau 1: TNE navigate_terrain()
  Niveau 2: Estimation 3 points (trail_type="estimation")

CASCADE C — BDRE Pipeline Hybride (propose)
  Niveau 1: Waterway Bank Routing
  Niveau 2: Terrain Topology
  Niveau 3: Corridor A* HUMAN_TRAJET_COSTS
  Niveau 4: GPS Tracks / Estimation enrichie
```

### 4.2 Strategie de Remplacement

La CASCADE C (BDRE) REMPLACE les cascades A et B.
Les cascades A et B ne sont PAS supprimees — elles sont ENVELOPPEES par le BDRE.

```
AVANT (3 cascades independantes):
  access_engine → cascade A (4 niveaux)
  stand_reco    → cascade B (2 niveaux)

APRES (1 cascade BDRE unifiee):
  access_engine → BDRE.compute_access_route()
                    → F4 (selection source)
                    → Source primaire (TNE navigate_terrain)
                    → Si echec: F5 (pipeline hybride)
                      → Level 1: Waterway corridors (BDRE enrichit le graphe TNE)
                      → Level 2: Terrain topology (clairieres + pentes)
                      → Level 3: Corridor A* (HUMAN_TRAJET_COSTS)
                      → Level 4: GPS tracks ou estimation enrichie
                    → F6 (journalisation de chaque etape)

  stand_reco    → BDRE.generate_approach_path()
                    → Meme pipeline F4→F5→F6
                    → trail_type TOUJOURS annote avec source BDRE
```

### 4.3 Regles de Remplacement

| Regle | Detail |
|-------|--------|
| R1 | access_engine.py:compute_access_route() delegue au BDRE au lieu d'implementer sa propre cascade |
| R2 | engine.py:_generate_approach_path() delegue au BDRE au lieu de retourner un 3-point |
| R3 | trail_type est TOUJOURS annote par le BDRE: "real_osm", "waterway_guided", "terrain_topology", "corridor_astar", "gps_track", "estimation_enriched" |
| R4 | Le fallback "estimation" (3 points ligne droite) est le DERNIER RECOURS, pas le 2e |
| R5 | Chaque niveau de fallback est journalise via F6 (audit_logger) |

---

## 5. PHASES D'IMPLEMENTATION

### Phase BDRE-1: Fondations (P0)
1. source_registry.py — Registre des 8 sources externes + 8 internes
2. quality_scorer.py — Scoring basique (couverture, fraicheur)
3. waterway_classifier.py — Classification hydrologique DS-8
4. audit_logger.py — Journal en memoire
5. router.py — 8 endpoints

### Phase BDRE-2: Monitoring + Integration TNE (P1)
1. health_monitor.py — Ping periodique des APIs
2. anomaly_detector.py — Detection sources vides
3. Integration TNE: modifier build_obstacle_set + build_terrain_graph
4. Integration ENGINE_OSM_LITE: hooks pre/post-call

### Phase BDRE-3: Intelligence + Remplacement Cascades (P2)
1. source_selector.py — Selection dynamique F4
2. fallback_chain.py — Pipeline hybride 4 niveaux F5
3. Remplacement CASCADE A (access_engine.py)
4. Remplacement CASCADE B (stand_recommendation/engine.py)

### Phase BDRE-4: Institutionnalisation (P3)
1. Hooks dans tous les engines restants (GUIDE PRO, Weather, etc.)
2. Dashboard monitoring frontend
3. Alertes BCE-4X automatiques
4. Integration GUIDE PRO terrain validation

---

## 6. DEPENDANCES

| Phase | Depend de | Bloquant pour |
|---|---|---|
| BDRE-1 | Aucune | BDRE-2 |
| BDRE-2 | BDRE-1 | BDRE-3 |
| BDRE-3 | BDRE-2 | BDRE-4, corrections sentiers vers affuts |
| BDRE-4 | BDRE-3 | Validation BIONIC OS V8.6 |

---

**STATUT: PLAN D'INTEGRATION V2 COMPLETE — CORRECTIONS COR-04, COR-05 APPLIQUEES**
**EN ATTENTE VALIDATION STEEVE-MAX**
