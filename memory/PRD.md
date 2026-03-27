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

### Phase 2.5 — TERRAIN NAV ENGINE (TNE) (27 Mars 2026)
Localisation: `/app/backend/engines/terrain_nav/`
- `__init__.py`, `terrain_sources.py`, `terrain_graph.py`, `terrain_costs.py`, `terrain_router.py`
- Overpass combinee (1 requete), 3 miroirs, retry exponentiel
- A* terrain-weighted + Dijkstra fallback
- Modele couts: type chemin, pente, foret, zones humides/eau

### Phase 2.6 — Corrections d'integration TNE + Vent (27 Mars 2026)
**TNE Ameliorations:**
- Snap par projection sur segment (pas seulement noeud le plus proche)
- Waypoints intermediaires dans les snap gaps (approche naturelle)
- Zone urbaine: 37-66 points/trajet | Zone foret: 15-19 points/trajet
- Cache: 0.024s (vs ~30s premier appel)

**WindFlowLayer retabli:**
- Reecrit completement: lecture DIRECTE useWeatherStore (ZERO fetch HTTP separe)
- Grille 25x25 fleches directionnelles
- Redraw automatique sur moveend/zoomend/resize + mise a jour du store
- Opacite augmentee (0.4-0.75) pour visibilite sur fond satellite
- showWindFlow force a `true` (contourne la session persiste a `false`)

**PREVIEWS valides:**
- Vent: fleches cyan 281 ONO visibles
- Sentiers: 5/5 sentier_reel (zone urbaine), fallback estimation annote (zone foret eloignee)
- Meteo: -6.6C alignee Dashboard/Territoire

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

*Mis a jour le 27 Mars 2026 — Phase 2.6*
