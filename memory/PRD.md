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
- 5 endpoints SHADOW desactives (weather-shadow, dem-shadow, ndvi-shadow, shadow-compare, weather-v82)
- Meteo: source unique /api/v3/weather/* (Open-Meteo). Fallbacks v1 + Open-Meteo direct SUPPRIMES
- WindFlowLayer migre de weather-shadow vers v3
- 15 imports fantomes supprimes (AnalyzerModule, TerritoryMap, HuntMarketplace, etc.)
- Route /territoire → redirect /mon-territoire-bionic
- Route /marketplace → redirect /shop
- Route /supra/:id CREEE (panneau SUPRA v2 standalone)

### P0.5 — Corrections UX (27 Mars 2026)
- Typographie Dashboard SUPRA, Chemins & Trails, Header UX

### Phase P0 — Fusion Totale (27 Mars 2026)
- SUPRA v2, MAGASIN v2, ADMIN v2, Nettoyage

### Phase 2 — Corrections Logiques (27 Mars 2026)
**AXE 1 — Meteo: Alignement Dashboard <-> Territoire**
- AdvancedWeatherWidget.jsx reecrit: lecture EXCLUSIVE useWeatherStore, ZERO auto-refresh, ZERO fallback, ZERO smoothing
- CoreDashboard.jsx: fetchWeather supprime du dependency array
- Verification: Dashboard et Territoire affichent EXACTEMENT les memes valeurs (-7.9C, 19.7 km/h, 56%, 1015.4 hPa)
- WeatherWidget.jsx deja aligne sur useWeatherStore

**AXE 2 — Sentiers: Routage REEL via Graphe OSM**
- Nouveau module: trail_graph.py (Overpass API + graphe A* local)
- _generate_approach_path() reecrit: interroge Overpass UNE SEULE FOIS, construit graphe, route via A*
- Cache en memoire par zone (evite re-fetches)
- Fallback estimation annote si aucun chemin OSM (log WARNING)
- Sinusoides et waypoints artificiels SUPPRIMES integralement
- StandsMapLayer.jsx mis a jour: vert continu = sentier reel, orange pointille = estimation
- Tests: 5/5 sentiers reels (zone urbaine Quebec), 5/5 estimation correcte (zone foret eloignee)

---

## Prochain: Verrouillage ULTRA-MAX++
- Golden State au boot
- Golden CSS Hash
- SUPRA v2 Guard
- Route Guard
- API Lock
- File Integrity Lock

## Backlog
- P1: Nettoyage fichiers V5 (WeatherService.js, bionicWeatherEngine.js, MeteoDashboard.jsx), enrichissement catalogue API x6030
- P2: BSAA-2 (gele) | P3: Merge Work1 → main

*Mis a jour le 27 Mars 2026*
