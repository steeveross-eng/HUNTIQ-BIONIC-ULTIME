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
**AXE 1 — Meteo: Alignement Dashboard <-> Territoire**
- AdvancedWeatherWidget.jsx reecrit: lecture EXCLUSIVE useWeatherStore
- CoreDashboard.jsx: fetchWeather supprime du dependency array
- Verification: valeurs identiques sur les deux pages

**AXE 2 — Phase 2.5: TERRAIN NAV ENGINE (TNE) (27 Mars 2026)**
Localisation: `/app/backend/engines/terrain_nav/` (protegee ULTRA-MAX++)

Structure:
- `__init__.py` — Interface publique (get_terrain_nav, navigate_terrain)
- `terrain_sources.py` — Acquisition Overpass combinee (1 seule requete), 3 miroirs, retry exponentiel
- `terrain_graph.py` — Graphe terrain avec noeuds ponderes (chemins OSM + obstacles + foret)
- `terrain_costs.py` — Modele de couts (type chemin, pente, densite, zones humides/eau)
- `terrain_router.py` — A* terrain-weighted + Dijkstra fallback

Resultats:
- Zone urbaine Quebec: 5/5 sentiers reels, 11171 noeuds, 12734 aretes, 2644 trails OSM
- Zone foret eloignee: 5/5 sentiers reels, 861 noeuds, 6 trails, 15 obstacles
- Cache: 0.024s (vs ~30s premier appel)
- Ancien trail_graph.py SUPPRIME
- Sinusoides SUPPRIMEES integralement

---

## Prochain: Verrouillage ULTRA-MAX++
- Golden State au boot (terrain_nav dans le manifeste)
- Golden CSS Hash
- SUPRA v2 Guard
- Route Guard
- API Lock
- File Integrity Lock (protection engines/terrain_nav)

## Backlog
- P1: Nettoyage fichiers V5, enrichissement catalogue API x6030
- P2: BSAA-2 (gele) | P3: Merge Work1 -> main

*Mis a jour le 27 Mars 2026 — Phase 2.5 TNE*
