# BDRE — INTEGRATION ENGINES V2
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-06
## Corrections appliquees: COR-05

---

## HISTORIQUE DES CORRECTIONS

| Correction | Description | Statut |
|------------|-------------|--------|
| COR-05 | Section "REMPLACEMENT cascades existantes" ajoutee | APPLIQUEE |
| DS-08 | Classification hydrologique alignee avec ROOT_SPEC V2 | APPLIQUEE |

---

## 1. PRINCIPE D'INTEGRATION

Chaque engine qui accede a des donnees terrain DOIT implementer le pattern
BDRE suivant:

```python
# Pattern BDRE standard
from engines.bdre import check_source, score_response, trigger_fallback, log_audit

# 1. PRE-CALL: Verifier la source
source_health = check_source("SRC-01")
if source_health.score < 0.20:
    # Source inutilisable -- fallback direct
    result = trigger_fallback(territory_id, level=3)
    log_audit("ENGINE_X", "SRC-01", "fallback_direct", source_health.score)
    return result

# 2. CALL: Executer la requete
data = fetch_from_source("SRC-01", params)

# 3. POST-CALL: Scorer la reponse
quality = score_response("SRC-01", data, expected_coverage)
if quality.score < 0.40:
    # Enrichir avec fallback
    enriched = trigger_fallback(territory_id, level=2, base_data=data)
    log_audit("ENGINE_X", "SRC-01", "fallback_enriched", quality.score)
    return enriched

# 4. LOG: Journaliser
log_audit("ENGINE_X", "SRC-01", "success", quality.score)
return data
```

---

## 2. INTEGRATION PAR ENGINE

### 2.1 TNE (Terrain Nav Engine) -- PRIORITE CRITIQUE

**Etat actuel**: Le TNE accede directement a Overpass sans verification BDRE.
Quand les donnees sont vides, il retourne un graphe vide sans alerte.

**Integration BDRE**:

```
engines/terrain_nav/__init__.py:
  get_terrain_nav(lat, lng, radius_m)
    +-- BDRE.check_source("SRC-01")       [NOUVEAU]
    +-- fetch_terrain_data(lat, lng)       [EXISTANT]
    +-- BDRE.score_response(data)          [NOUVEAU]
    +-- build_terrain_graph(data)          [EXISTANT — MODIFIE DS-8]
    +-- Si graphe.is_empty:
    |   +-- BDRE.trigger_fallback(lat,lng) [NOUVEAU]
    +-- BDRE.log_audit(result)             [NOUVEAU]
```

**Points de controle BDRE dans le TNE**:

| Point | Fichier | Fonction/Constante | Action BDRE |
|---|---|---|---|
| PC-1 | __init__.py | get_terrain_nav() debut | check_source("SRC-01") |
| PC-2 | terrain_sources.py | fetch_terrain_data() retour | score_response(data) |
| PC-3 | terrain_graph.py | build_terrain_graph() | Si vide -> alert_empty("SRC-01") |
| PC-4 | terrain_graph.py | build_terrain_graph() | Integrer waterway corridors (DS-8) |
| PC-5 | terrain_router.py | route_terrain() echec | trigger_fallback() |
| PC-6 | terrain_router.py | route_terrain() fin | log_audit() |

### 2.2 ENGINE_OSM_LITE -- PRIORITE HAUTE

**Etat actuel**: Consomme le cache AE-V6 (vide) et OSM (eau seulement).
Ne signale pas que l'enrichissement est inefficace.

| Point | Fonction | Action BDRE |
|---|---|---|
| PC-1 | load_trail_segments_from_access_cache() | check_source("SRC-03") |
| PC-2 | load_trail_segments_from_access_cache() | Si 0 segments -> alert_empty("SRC-03") |
| PC-3 | load_exclusions_from_osm_cache() | score_response(exclusions) |
| PC-4 | enrich_terrain_grid() | Si 0 enrichissement -> trigger_fallback() |
| PC-5 | enrich_terrain_grid() | log_audit("enrichment_result") |

### 2.3 Stand Recommendation Engine -- PRIORITE CRITIQUE (COR-05 REMPLACEMENT)

**Etat actuel**: Quand TNE echoue -> fallback 3-point lineaire sans alerte.

**AVANT (cascade B actuelle)**:
```python
# engine.py:_generate_approach_path() lignes 162-204
if trail_graph and not trail_graph.is_empty:
    result = navigate_terrain(...)
    if result: return result          # Niveau 1: TNE
# FALLBACK: 3 points en ligne droite
path = [start, entry_vent, stand]     # Niveau 2: estimation
path[0]["trail_type"] = "estimation"
```

**APRES (delegation au BDRE)**:
```python
# engine.py:_generate_approach_path() — REMPLACE par BDRE
from engines.bdre import compute_approach_path, log_audit

bdre_result = compute_approach_path(
    start_lat, start_lng, stand_lat, stand_lng,
    trail_graph=trail_graph, wind_dir=wind_dir,
    corridors=corridors, hydro_points=hydro_points
)
# bdre_result.trail_type est TOUJOURS annote:
#   "real_osm" | "waterway_guided" | "terrain_topology" |
#   "corridor_astar" | "gps_track" | "estimation_enriched"
log_audit("STAND_RECO", bdre_result.source_id, bdre_result.action, bdre_result.score)
return bdre_result.path
```

### 2.4 Access Engine V6 -- PRIORITE CRITIQUE (COR-05 REMPLACEMENT)

**Etat actuel**: Cascade A (4 niveaux) dans compute_access_route().

**AVANT (cascade A actuelle)**:
```
compute_access_route():
  1. navigate_terrain() -> sentier OSM complet
  2. _attempt_hybrid_trail_terrain() -> hybride
  3. _build_terrain_grid() + _astar_terrain_grid() -> terrain-aware
  4. Ligne directe (quality_score=20)
```

**APRES (delegation au BDRE)**:
```
compute_access_route():
  bdre_result = BDRE.compute_access_route(
      entry_lat, entry_lng, blind_lat, blind_lng,
      trail_graph, terrain_data, scent_zone, feeding_sites
  )
  # Le BDRE execute sa propre cascade:
  #   1. TNE navigate_terrain + waterway corridors (enrichi)
  #   2. Hybrid trail-terrain (conserve la logique existante)
  #   3. Corridor A* HUMAN_TRAJET_COSTS
  #   4. GPS tracks / estimation enrichie
  # Chaque niveau est journalise
```

**IMPORTANT**: La logique metier de `_attempt_hybrid_trail_terrain()`,
`_build_terrain_grid()`, et `_astar_terrain_grid()` est CONSERVEE.
Le BDRE les ORCHESTRE, il ne les REMPLACE PAS.

### 2.5 Corridor Engine (zone_engine_core_v2) -- PRIORITE MOYENNE

**Etat actuel**: Construit grille terrain depuis zones comportementales.
ENGINE_OSM_LITE enrichit mais avec des donnees vides.

| Point | Fonction cible | Action BDRE |
|---|---|---|
| PC-1 | zone_engine_core_v2.py:_build_terrain_grid() | Apres construction -> BDRE.score_grid(terrain_data) |
| PC-2 | Enrichissement ENGINE_OSM_LITE | Si 0 -> BDRE.alert_insufficient_terrain() |
| PC-3 | corridor_10x.py:find_path() (A*) | Si echec -> log_audit("astar_failure") |
| PC-4 | Pipeline corridor complet | Fin -> log_audit("corridor_generation") |

### 2.6 Access Engine V6 grille (COR-04)

| Point | Fonction cible | Action BDRE |
|---|---|---|
| PC-1 | access_engine.py:_build_terrain_grid() | Apres construction -> BDRE.score_grid(terrain_data) |
| PC-2 | access_engine.py:_astar_terrain_grid() | Si echec -> log_audit("access_astar_failure") |

### 2.7 GUIDE PRO -- PRIORITE MOYENNE

**Etat actuel**: Consomme les engines sans verifier la fiabilite.

| Point | Fonction | Action BDRE |
|---|---|---|
| PC-1 | generate_routes() | BDRE.validate_territory(territory_id) |
| PC-2 | generate_routes() | Si score < 0.40 -> warning au guide |
| PC-3 | generate_routes() | Ajouter score BDRE aux routes |
| PC-4 | generate_report() | Inclure metriques BDRE dans rapport |

### 2.8 Weather Engine -- PRIORITE BASSE

**Etat actuel**: Fallback interne deja present.

| Point | Fonction | Action BDRE |
|---|---|---|
| PC-1 | get_weather() | check_source("SRC-07") |
| PC-2 | get_weather() | log_audit("weather") |

---

## 3. PIPELINE HYBRIDE 4 NIVEAUX (F5)

### Declenchement

```
Score BDRE source primaire
    |
    +-- > 0.60 -> Utiliser source primaire
    |
    +-- 0.40-0.59 -> NIVEAU 1: Waterway Bank Routing
    |   +-- Integrer les 7 cours d'eau (357 noeuds) comme CORRIDORS
    |       Couts: berge=1.2 (stream_bank), eau=999.0 (water_body)
    |       Classification: DS-8 (stream/ditch/drain = corridor, water/wetland = obstacle)
    |
    +-- 0.20-0.39 -> NIVEAU 2: Terrain Topology
    |   +-- Utiliser pente, altitude, densite pour sentiers synthetiques
    |       Preference: vallees, coulees, lisieres, cretes basses
    |       Source: get_raw_terrain_data() clearings + waterways
    |
    +-- 0.01-0.19 -> NIVEAU 3: Corridor A* HUMAN_TRAJET_COSTS
    |   +-- Pathfinder A* avec grille terrain enrichie
    |       Couts: foret=3.5-4.5, sentier=1.0, eau=999.0
    |
    +-- 0.00 -> NIVEAU 4: GPS Tracks + Estimation enrichie
        +-- Si GPS tracks dispo -> suivre trace exacte
            Sinon -> estimation avec contournement eau/foret
```

### Resultat par niveau

| Niveau | trail_type | Fiabilite | Contournement obstacles |
|--------|-----------|-----------|------------------------|
| Source primaire | "real_osm" | 0.80+ | OUI (sentiers reels) |
| Niveau 1 | "waterway_guided" | 0.60 | Partiel (berges) |
| Niveau 2 | "terrain_topology" | 0.50 | OUI (pente/altitude) |
| Niveau 3 | "corridor_astar" | 0.40 | OUI (couts terrain) |
| Niveau 4 | "gps_track" ou "estimation_enriched" | 0.30 | Basique |

---

## 4. SCHEMA DE DONNEES BDRE

### 4.1 SourceHealth (en memoire) — Aligne DC-BDRE-01

```python
SourceHealth = {
    "source_id": str,           # "SRC-01"
    "status": str,              # "healthy" | "degraded" | "down" | "empty"
    "latency_ms": float,        # Derniere latence
    "last_check": str,          # ISO timestamp
    "score": float,             # 0.0 -> 1.0
    "checks_24h": int,          # Nombre de checks en 24h
    "failures_24h": int,        # Nombre d'echecs en 24h
    "availability_pct": float,  # % disponibilite
}
```

### 4.2 AuditLog (en memoire, rotatif 1000 entrees)

```python
AuditLog = {
    "timestamp": str,           # ISO
    "engine": str,              # "TNE" | "OSM_LITE" | "CORRIDOR" | "ACCESS" | "STAND_RECO" | "GUIDE_PRO"
    "source_id": str,           # "SRC-01"
    "action": str,              # "success" | "fallback" | "alert" | "empty"
    "score": float,             # Score BDRE au moment de l'action
    "fallback_level": int,      # 0 (pas de fallback) | 1-4
    "territory": str,           # ID ou coords territoire
    "details": str,             # Message libre
}
```

---

## 5. CONFORMITE BCE-4X

| Critere | Implementation BDRE |
|---------|---------|
| ZERO INTERPRETATION | Scoring numerique objectif, seuils fixes |
| ZERO DOUBLON | Point d'acces unique par source. Cascades existantes REMPLACEES (pas dupliquees) |
| ZERO REGRESSION | Fallback garanti avant retour vide. Logique metier existante CONSERVEE |
| ZERO OBSOLESCENCE | TTL par source, detection peremption |
| ZERO LOSS | Epuisement 4 niveaux avant retour estimation |

---

**STATUT: SPECIFICATION INTEGRATION ENGINES V2 COMPLETE — CORRECTIONS COR-05, DS-08 APPLIQUEES**
**EN ATTENTE VALIDATION STEEVE-MAX**
