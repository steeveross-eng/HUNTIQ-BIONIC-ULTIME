# INVENTAIRE COMPLET — ACCÈS AUX AFFÛTS
## ORDONNANCE STEEVE-MAX | Désactivation Sécurisée
## Date : 2026-04-07 | Archive : /app/LEGACY_ACCESS_AFFUTS/

---

## 1. GÉOMÉTRIES

| Composante | Fichier | Description |
|------------|---------|-------------|
| Lignes d'accès (A*) | `access_engine.py` | Routes terrain-grid A* |
| Segments corridor | `corridor_optimizer_v2.py` | Analyse corridor/forêt par segment |
| Pénétration 90° | `access_engine.py:_attempt_hybrid_trail_terrain()` | Phase 2 terrain |
| Corridors virtuels | `terrain_graph.py` | Injection guidance start/end |
| Points intermédiaires | `terrain_router.py:route_terrain()` | Coords A* sur graphe |
| Junction hybride | `fallback_chain.py` | Nœud embranchement trail→terrain |

## 2. TABLES / CACHES BACKEND

| Table/Cache | Fichier | Description |
|-------------|---------|-------------|
| `institutional_objects.json` | `institutional_cache.py` | Objets institutionnels (affûts, zones) |
| `certified_routes.json` | `institutional_cache.py` | Routes pré-certifiées |
| `virtual_corridors.json` | `institutional_cache.py` | Corridors virtuels permanents |
| `terrain_cache/` | `terrain_nav/__init__.py` | Cache graphe terrain OSM |
| `access_engine_v6/cache/` | `access_engine_v6/` | Cache accès V6 |

## 3. ENDPOINTS API

| Endpoint | Méthode | Fichier | Fonction |
|----------|---------|---------|----------|
| `/api/v1/hunt/orchestrate` | POST | `orchestrator/router.py` | Orchestration complète + accès |
| `/api/v1/hunt/access-route` | POST | `orchestrator/router.py` | Calcul accès unique |
| `/api/v6/access/compute` | POST | `access_engine_v6/router.py` | Accès V6 |
| `/api/v6/access/compute-batch` | POST | `access_engine_v6/router.py` | Accès V6 batch |
| `/api/v7/clarity/compute` | POST | `access_clarity_v7/router.py` | Clarté V7 |
| `/api/v7/clarity/score` | POST | `access_clarity_v7/router.py` | Score TCS |
| `/api/v1/bdre/cache/routes/{t}` | GET | `bdre/router.py` | Routes certifiées |
| `/api/v1/bdre/cache/certify/{t}` | POST | `bdre/router.py` | Certification territoire |

## 4. COUCHES FRONTEND

| Couche | Fichier | Description |
|--------|---------|-------------|
| AccessRouteV6Layer | `AccessRouteV6Layer.jsx` | Rendu polyline accès V6 |
| StandsMapLayer (lignes 154-330) | `StandsMapLayer.jsx` | Rendu accès intégré aux affûts |
| HuntingPathLayer | `HuntingPathLayer.jsx` | Couche chemin de chasse |
| useAccessRoute | `useAccessRoute.js` | Hook fetch API accès |

## 5. TRIGGERS AUTOMATIQUES

| Trigger | Emplacement | Description |
|---------|-------------|-------------|
| Orchestration auto | `orchestrator.py:orchestrate_hunt_session()` | Calcul accès dans boucle recommandations |
| Cache-first check | `orchestrator.py:_check_institutional_cache()` | Consultation cache avant A* |
| BDRE cascade | `fallback_chain.py:compute_access_route()` | L0→L1→L2→L3→L4 |

## 6. RÈGLES BCE-4X APPLIQUÉES AUX ACCÈS

| Règle | Fichier | Description |
|-------|---------|-------------|
| Ratio détour 3.5x (L0/L1) | `fallback_chain.py:_annotate()` | Rejet détours excessifs |
| Ratio détour 5.0x (L2) | `fallback_chain.py:_annotate()` | Seuil adaptatif hybride |
| 95/5 corridor/forêt | `corridor_optimizer_v2.py` | Objectif 95% corridor |
| Pénétration < direct | `access_engine.py` | Rejet si pénétration > distance directe |
| Coût 1,000,000 (eau/route/urbain) | `terrain_costs.py` | Exclusions BCE-4X |
| Virtual corridors GUIDANCE | `terrain_graph.py` | Injection start/end graphe |
| Terrain-aware corridor detection | `corridor_optimizer_v2.py` | Zone sans OSM |

## 7. FICHIERS ARCHIVÉS (66 fichiers, 2.7 MB)

```
/app/LEGACY_ACCESS_AFFUTS/
├── backend/
│   ├── engines/
│   │   ├── hunt_orchestrator/
│   │   │   ├── access_engine.py
│   │   │   ├── orchestrator.py
│   │   │   ├── router.py
│   │   │   ├── choix_affuts.py
│   │   │   └── vent_odeurs.py
│   │   ├── bdre/
│   │   │   ├── fallback_chain.py
│   │   │   ├── corridor_optimizer_v2.py
│   │   │   ├── institutional_cache.py
│   │   │   └── router.py
│   │   └── terrain_nav/
│   │       ├── terrain_router.py
│   │       ├── terrain_graph.py
│   │       ├── terrain_costs.py
│   │       └── __init__.py
│   ├── modules/
│   │   ├── access_engine_v6/ (complet)
│   │   └── access_clarity_engine_v7/ (complet)
│   └── data/
│       ├── institutional_cache/ (JSON)
│       └── terrain_cache/ (cache OSM)
├── frontend/
│   ├── components/territoire/
│   │   ├── AccessRouteV6Layer.jsx
│   │   ├── StandsMapLayer.jsx
│   │   └── HuntingPathLayer.jsx
│   └── hooks/
│       └── useAccessRoute.js
├── BCE4X_NORME_ACCES_AFFUTS.md
├── AFFUTS_ZONES_NON_REGRESSION_REPORT.md
└── generate_visual_proof.py
```

---

**INVENTAIRE COMPLET — 66 fichiers, 6 géométries, 5 caches, 8 endpoints, 4 couches frontend, 3 triggers, 7 règles BCE-4X.**
