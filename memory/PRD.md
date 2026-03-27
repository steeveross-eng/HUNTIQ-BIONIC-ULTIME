# HUNTIQ-V6 — Product Requirements Document
## BCE-4X / STEEVE-MAX V6

---

## Enonce original
Reconstruction et modernisation HUNTIQ-V6 sous gouvernance BCE-4X / MAX ULTRA / STEEVE-MAX.

## Architecture
- Backend: FastAPI, 84+ engines | Frontend: React, Zustand, Leaflet, Tailwind
- E-commerce: Stripe via emergentintegrations | Gouvernance UI: BCE4X_UIShield
- Branche: Work1

---

## Implemente

### Purge Architecturale (27 Mars 2026)
- 5 endpoints SHADOW desactives
- Meteo: source unique /api/v3/weather/*
- 15 imports fantomes supprimes

### Phase P0 — Fusion Totale (27 Mars 2026)
- SUPRA v2, MAGASIN v2, ADMIN v2, Nettoyage

### Phase 2 — Corrections Logiques (27 Mars 2026)
- AdvancedWeatherWidget: lecture EXCLUSIVE useWeatherStore
- CoreDashboard: fetchWeather supprime du dependency array

### Phase 2.5 — TERRAIN NAV ENGINE (TNE) (27 Mars 2026)
- A* terrain-weighted + Dijkstra fallback + Overpass combinee

### Phase 2.6 — Corrections TNE + Vent (27 Mars 2026)
- Snap par projection + waypoints intermediaires + cache

### Phase 2.9 — Corrections critiques (27 Mars 2026)
- SUPRA v2 SAL-10: 100vh, ZERO scroll interne
- Typographie alignee Dashboard (slate-800/700)
- Temperature: suppression fallback intelligenceWeather
- Masques exclusion urbain dans zone_engine_core_v2.py
- WindFlowLayer: animation rAF particules (v1)

### Phase 3.1 — WindFlow DOUX + Unification Temperature + Sync Waypoint (27 Mars 2026)
- WindFlow: 140 particules, opacity max 0.35, sinusoidal wavy drift
- Temperature UNIFIEE via waypoint unique (Dashboard = MonTerritoire = METEO BIONIC)
- Synchronisation waypoint: localStorage(LAST_WAYPOINT_KEY) prioritaire

### Phase 3.2-S — ÉRADICATION BUG POLLUTION CACHE URBAIN (27 Mars 2026)

**CAUSE RACINE IDENTIFIÉE:**
- `_inject_raw_osm_into_urban_cache()` ajoutait des batiments RAW OSM au cache global à CHAQUE requête
- Le cache grossissait de manière CUMULATIVE (15,736 → 33,436 → infini)
- Résultat: zones forestières légitimes faussement exclues comme "urbaines"

**CORRECTIFS APPLIQUÉS:**
1. **SUPPRESSION** de `_inject_raw_osm_into_urban_cache()` du pipeline
2. **BCE4X_URBAN_CACHE_SAFE_MODE = True** — garde-fou contre toute réinjection
3. **Cache urbain STATIQUE** (100,699 polygones OSM, chargé au boot uniquement)
4. **Seuil urbain** ajusté: 10% → 15% (réduit faux positifs en bordure)
5. **preload_urban_cache()** au démarrage serveur (comme le cache eau)
6. **Compteur audit** `_urban_cache_polygon_count` dans tous les logs et réponses API

**RÉSULTATS VÉRIFIÉS:**
- Forêt (Stoneham): 5 zones stables sur 3 requêtes ✅
- Ville (Québec centre): 0 zones ✅
- Stabilité post-mixte: cache IDENTIQUE (100,699) après requête ville ✅
- ZERO pollution cumulative ✅

**FICHIERS MODIFIÉS:**
- /app/backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py
- /app/backend/server.py

**BACKUP:** /app/backend/data/ARCHIVES_V6/backup_phase32s/

---

## En attente: Validation STEEVE-MAX Phase 3.2-S
- PREVIEWs 1-4 livrés
- Logs sécurité livrés
- Aucune donnée métier modifiée

## Backlog
- P1: Activation ULTRA-MAX++ Lock (Golden State, CSS Hash, API Lock)
- P1: Nettoyage fichiers V5, enrichissement catalogue API x6030
- P2: BSAA-2 (gele) | P3: Merge Work1 -> main

*Mis a jour le 27 Mars 2026 — Phase 3.2-S*
