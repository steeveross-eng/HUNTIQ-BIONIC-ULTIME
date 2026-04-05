# BDRE — PLAN D'INTEGRATION
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-05

---

## 1. ARCHITECTURE MODULE

```
backend/engines/bdre/
├── __init__.py                    (Point d'entree BDRE)
├── source_registry.py             (Registre des sources F1/F2)
├── health_monitor.py              (Monitoring API F1)
├── quality_scorer.py              (Scoring fiabilite F2)
├── anomaly_detector.py            (Detection vide/incoherent F3)
├── source_selector.py             (Selection dynamique F4)
├── fallback_chain.py              (Pipeline hybride 4 niveaux F5)
├── audit_logger.py                (Journalisation F6)
└── router.py                      (Endpoints API BDRE)
```

---

## 2. PLAN D'INTEGRATION PAR ENGINE

### 2.1 TNE (Terrain Nav Engine)
| Fichier | Integration | Type |
|---|---|---|
| terrain_sources.py:_fetch_overpass() | Avant appel → BDRE.check_source("SRC-01") | Pre-call |
| terrain_sources.py:_fetch_overpass() | Apres reponse → BDRE.score_response() | Post-call |
| terrain_graph.py:build_terrain_graph() | Si graphe vide → BDRE.trigger_fallback() | Fallback |
| terrain_router.py:route_terrain() | Si echec → BDRE.log_fallback() | Audit |

### 2.2 ENGINE_OSM_LITE
| Fichier | Integration | Type |
|---|---|---|
| engine_osm_lite.py:load_trail_segments() | Avant chargement → BDRE.check_source("SRC-03") | Pre-call |
| engine_osm_lite.py:load_exclusions() | Score reponse → BDRE.score_response() | Post-call |
| engine_osm_lite.py:enrich_terrain_grid() | Si 0 enrichissement → BDRE.alert_empty() | Detection |

### 2.3 Access Engine V6
| Fichier | Integration | Type |
|---|---|---|
| osm_trails.py:build_trail_graph() | Avant appel → BDRE.check_source("SRC-03") | Pre-call |
| osm_trails.py:build_trail_graph() | Si cache vide → BDRE.alert_empty("SRC-03") | Detection |

### 2.4 Corridor Engine
| Fichier | Integration | Type |
|---|---|---|
| zone_engine_core_v2.py:_build_terrain_grid() | Apres construction → BDRE.score_grid() | Post-call |
| corridor_10x.py:find_path() | Si echec → BDRE.log_fallback("corridors") | Audit |

### 2.5 Stand Recommendation Engine
| Fichier | Integration | Type |
|---|---|---|
| engine.py:recommend_stands() | Avant TNE → BDRE.check_source("SRC-01") | Pre-call |
| engine.py:_generate_approach_path() | Si fallback → BDRE.trigger_hybrid_fallback() | Fallback |

### 2.6 GUIDE PRO
| Fichier | Integration | Type |
|---|---|---|
| guided_route_builder.py:generate_routes() | Avant calcul → BDRE.validate_sources() | Pre-call |
| guided_route_builder.py:generate_routes() | Score routes → BDRE.score_route_quality() | Post-call |

### 2.7 Weather Engine
| Fichier | Integration | Type |
|---|---|---|
| weather_v3/router.py | Avant appel → BDRE.check_source("SRC-07") | Pre-call |
| weather_v3/router.py | Si fallback → BDRE.log_fallback("meteo") | Audit |

---

## 3. ENDPOINTS API BDRE (8)

```
PREFIX: /api/v1/bdre
```

| # | Route | Method | Description |
|---|-------|--------|-------------|
| 0 | /health | GET | Sante du BDRE |
| 1 | /sources | GET | Registre complet des sources |
| 2 | /sources/{id}/health | GET | Sante d'une source specifique |
| 3 | /sources/{id}/score | GET | Score de fiabilite |
| 4 | /quality/report | GET | Rapport qualite global |
| 5 | /fallbacks/recent | GET | Derniers fallbacks declenches |
| 6 | /audit/log | GET | Journal d'audit (pagine) |
| 7 | /validate/{territory_id} | POST | Validation BDRE d'un territoire |

---

## 4. PHASES D'IMPLEMENTATION

### Phase BDRE-1: Fondations (P0)
1. source_registry.py — Registre des 8 sources externes + 8 internes
2. quality_scorer.py — Scoring basique (couverture, fraicheur)
3. audit_logger.py — Journal en memoire
4. router.py — 8 endpoints

### Phase BDRE-2: Monitoring (P1)
1. health_monitor.py — Ping periodique des APIs
2. anomaly_detector.py — Detection sources vides
3. Integration TNE + ENGINE_OSM_LITE

### Phase BDRE-3: Intelligence (P2)
1. source_selector.py — Selection dynamique
2. fallback_chain.py — Pipeline hybride 4 niveaux
3. Integration tous engines

### Phase BDRE-4: Institutionnalisation (P3)
1. Hooks dans tous les engines
2. Dashboard monitoring frontend
3. Alertes BCE-4X automatiques

---

## 5. DEPENDANCES

| Phase | Depend de | Bloquant pour |
|---|---|---|
| BDRE-1 | Aucune | BDRE-2 |
| BDRE-2 | BDRE-1 | BDRE-3 |
| BDRE-3 | BDRE-2 | BDRE-4, corrections A→F sentiers |
| BDRE-4 | BDRE-3 | Validation BIONIC OS V8.6 |

---

**STATUT: PLAN D'INTEGRATION COMPLETE — EN ATTENTE VALIDATION STEEVE-MAX**
