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

### Phase 2.9 — Corrections critiques (27 Mars 2026)
**FIX 1 — SUPRA v2 SAL-10: Suppression scroll interne**
- SupraPage.jsx: Wrapper `max-w-3xl` retire, 100vh/100vw plein ecran
- NutritionPointDetailPanel.jsx: `overflow-y-auto` + `maxHeight` supprimes du contenu
- PinnablePanel.jsx: `overflowY: 'hidden'` remplace par `overflowY: 'auto'` en mode fullHeight

**FIX 2 — SUPRA v2: Alignement typographie/layout avec Dashboard BIONIC**
- Cards: fond `rgb(30 41 59)` (slate-800), bordure `rgb(51 65 85)` (slate-700)
- CollapsibleSection: icones 4w/4h, texte `text-sm font-semibold`, badges arrondis
- InfoCard: labels `text-slate-400`, valeurs `text-slate-200`
- Mineraux: barres avec `zoneColor()`, labels `text-slate-300`, scores tabular-nums
- Physiologie & Comportement: `text-sm text-slate-300 leading-relaxed`

**FIX 3 — Temperature Mismatch: Dashboard = Mon Territoire**
- TerritoireHeader.jsx: Suppression fallback `intelligenceWeather` (useBionicStore)
- Source UNIQUE: `useWeatherStore(s => s.current).temperature_c`
- Resultat: -6.4C identique Dashboard <-> Mon Territoire

**FIX 4 — Zones & Corridors: Masques d'exclusion urbain**
- zone_engine_core_v2.py: Cache urbain (`_load_urban_cache_zones`) charge depuis OSM cache
- Types exclus: urban, roads (motorway, trunk, primary)
- Buffer routes majeures: 0.001-0.0012 deg (~111-133m)
- `_circle_on_urban()`: seuil 10% overlap → exclusion
- Corridors: midpoint check dans urban_cache → exclusion
- Metadata V6.x enrichi: `urban_exclusion_engine: Phase2.9-local-cache`

**FIX 5 — WindFlowLayer: Animation DYNAMIQUE**
- Systeme particules: 300 particules avec trainee
- `requestAnimationFrame` loop continu
- Fade progressif (globalCompositeOperation destination-in)
- Recyclage particules aux bords (direction upwind)
- Variation naturelle par particule (sin wave)
- Reset automatique sur moveend/zoomend
- Canvas z-index 400, pointer-events none

**PREVIEWS valides Phase 2.9:**
- PREVIEW 1: SUPRA v2 1920x1080 fullscreen, ZERO scroll
- PREVIEW 2: Cards SUPRA alignees Dashboard (slate-800/700)
- PREVIEW 3: -6.4C Dashboard = -6.4C Mon Territoire
- PREVIEW 4: Zones en foret uniquement, ZERO zone urbaine
- PREVIEW 5: WindFlow 40/100 pixels actifs, rAF animation continue

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

*Mis a jour le 27 Mars 2026 — Phase 2.9*
