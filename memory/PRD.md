# HUNTIQ-V6 — Product Requirements Document
## BCE-4X / STEEVE-MAX V6 / GOLDEN BCE

---

## Enonce original
Reconstruction et modernisation HUNTIQ-V6 sous gouvernance BCE-4X / MAX ULTRA / STEEVE-MAX.

## Architecture
- Backend: FastAPI, 84+ engines, Shapely (exclusions spatiales) | Frontend: React, Zustand, Leaflet, Tailwind
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

### Phase 3.1 — WindFlow DOUX + Unification Temperature (27 Mars 2026)
- WindFlow: 140 particules, opacity max 0.35, sinusoidal wavy drift
- Temperature UNIFIEE via waypoint unique

### Phase 3.2-S — Suppression pollution cumulative cache urbain (27 Mars 2026)
- _inject_raw_osm_into_urban_cache() DESACTIVEE du pipeline
- BCE4X_URBAN_CACHE_SAFE_MODE = True

### Phase 3.2-V + 3.3-U-PRIME — VALIDATION VISUELLE + EXCLUSIONS ULTIMES (27 Mars 2026)

**PROBLEME IDENTIFIE:**
Deux causes racines distinctes:
1. **Pollution cumulative du cache urbain** (Phase 3.2-S) — CORRIGEE
2. **SECOND PIPELINE sans exclusions** — `/api/v6/corridors/analyze-full` (engine.py) generait des zones SANS aucun filtre urbain/eau. C'est CE pipeline qui alimentait le rendu visuel via `BionicCorridorsV6Layer`.
3. **Cache IndexedDB frontend** — Les anciennes zones etaient persistees dans le navigateur de l'utilisateur (DB_VERSION=2, CACHE_VERSION=_v6_core)

**CORRECTIFS:**
1. Exclusion ULTIME dans `zone_engine_core_v2.py`:
   - Buffer 55m (0.0005deg) sur le cache urbain au chargement
   - Check CENTRE (point-in-polygon rapide) + overlap 3%
   - Check centre eau + overlap 25%
   - 101,182 polygones urbains statiques

2. Exclusion ULTIME dans `corridors_v10/engine.py`:
   - Filtre post-generation utilisant _circle_on_urban() et _circle_on_water()
   - Applique aux zone_polygons AVANT ajout au GeoJSON

3. Invalidation cache frontend:
   - IndexedDB DB_VERSION: 2 → 3 (purge totale)
   - CACHE_VERSION: _v6_core → _v6_phase32s

**RESULTATS VERIFIES:**
| Zone | Pipeline | Input | Urban | Water | Kept |
|------|----------|-------|-------|-------|------|
| Ville (waypoint user) | organic-zones | 17 | 17 | 0 | **0** |
| Ville (waypoint user) | analyze-full | 16 | **16** | 0 | **0** |
| Foret profonde | analyze-full | 16 | 0 | 0 | **16** |
| Stabilite 3x ville | analyze-full | 16 | 16 | 0 | 0 (stable) |
| Post-ville foret | analyze-full | 16 | 0 | 0 | 16 (zero pollution) |

**FICHIERS MODIFIES:**
- /app/backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py
- /app/backend/core/scoring_pipeline/corridors_v10/engine.py
- /app/backend/server.py
- /app/frontend/src/hooks/useZoneOrchestrator.js
- /app/frontend/src/hooks/useZoneCache.js

**BACKUP:** /app/backend/data/ARCHIVES_V6/backup_phase32s/

---

## Charte 3.3-U-PRIME — ACTIVE
- BCE-4X (non-regression): ACTIVE
- STEEVE-MAX (gouvernance): ACTIVE
- GOLDEN BCE (structure): ACTIVE
- SAFE MODE permanent: ACTIVE
- Exclusions ULTIMES (2 pipelines): ACTIVE
- Purge V1-V5 cache dynamique: COMPLETE

## En attente: Validation STEEVE-MAX Phase 3.2-V + 3.3-U-PRIME

## Backlog
- P1: Activation ULTRA-MAX++ Lock (Golden State, CSS Hash, API Lock)
- P1: Nettoyage fichiers V5, enrichissement catalogue API x6030
- P2: BSAA-2 (gele) | P3: Merge Work1 -> main

*Mis a jour le 27 Mars 2026 — Phase 3.2-V + 3.3-U-PRIME*
