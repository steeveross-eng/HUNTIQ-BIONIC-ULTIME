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

**FIX 1 — WindFlow DOUX / WAVY / SMOOTH**
- 140 particules (reduit de 300)
- Max opacity 0.35 (mesure: 0.318)
- Taille 1.2px (reduit de 3px)
- Vitesse = wind_speed * 0.25
- Interpolation sinusoidale (wavy drift, amplitude 0.6, frequence 0.015)
- Smoothing directionnel lerp (factor 0.08)
- Fade-in/fade-out envelope (sin lifecycle)
- FADE_RATE 0.93 pour trails courts
- Verdict: SUBTIL — ZERO saturation, ZERO dominance

**FIX 2 — Temperature UNIFIEE**
- CAUSE RACINE IDENTIFIEE: 3 sources de divergence
  1. DashboardPage hardcodait {46.8139, -71.2082} (Quebec centre)
  2. MonTerritoire utilisait mapCenter (position carte) au lieu du waypoint
  3. TerritoireHeader avait fallback intelligenceWeather (stale data)
- CORRECTION:
  - DashboardPage: lit waypoint via useUserData + localStorage(LAST_WAYPOINT_KEY)
  - MonTerritoire: weatherCoords derive de selectedWaypointForZones
  - TerritoireHeader: ZERO fallback (Phase 2.9)
- RESULTAT: Dashboard = MonTerritoire = METEO BIONIC = -6.5C / 1014.5 hPa / 18.4 km/h

**FIX 3 — Synchronisation Waypoint**
- DashboardPage: useAuth + useUserData pour lire le meme waypoint
- Priorite: localStorage(LAST_WAYPOINT_KEY) > premier waypoint actif > waypoints[0] > default
- MonTerritoire: weatherCoords = selectedWaypointForZones > activeWaypoints[0] > mapCenter
- ZERO fallback GPS navigateur, ZERO fallback region administrative
- Coordonnee UNIQUE pour les deux modules

**PREVIEWS valides Phase 3.1:**
- WindFlow DOUX: maxOpacity 0.318, verdict SUBTIL
- Temperature Dashboard = -6.5C = METEO BIONIC = -6.5C = Header = -6.5C
- Coordonnee unique: useWeatherStore.lastFetchCoords synchronise

---

## Prochain: Validation STEEVE-MAX Phase 3.1
- Aucune activation ULTRA-MAX++ tant que Phase 3.1 non validee

## Backlog
- P1: Activation ULTRA-MAX++ Lock (Golden State, CSS Hash, API Lock)
- P1: Nettoyage fichiers V5, enrichissement catalogue API x6030
- P2: BSAA-2 (gele) | P3: Merge Work1 -> main

*Mis a jour le 27 Mars 2026 — Phase 3.1*
