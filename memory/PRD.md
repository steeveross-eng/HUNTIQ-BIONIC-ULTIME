# HUNTIQ-V6 — PRD (Product Requirements Document)
## Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

### Projet
Reconstruction, modernisation et stabilisation de la plateforme HUNTIQ-V6.

### Stack Technique
- **Backend**: FastAPI, ThreadPoolExecutor, MongoDB
- **Frontend**: React, Zustand, React-Leaflet, Tailwind
- **Gouvernance**: BCE-4X, BCE-4X-UI (PositionLock, ZIndexGuard, RenderGuard, LayoutFreeze, OverlayCompliance)

---

## Travaux Accomplis

### Phase 1-3: Import et Archive
- Clone bionic-v3-dev depuis HUNTIQ-V5
- Inventaire certifie + ZIP archive

### Gouvernance
- GOVERNANCE.md, EMERGENT_PROTOCOL.md, SECURITY_POLICY.md
- Protocole ZERO LOSS, ZERO REGRESSION

### Audits
- Engine Audit (84+ modules confirmes)
- Coherence Audit (Phase 5B)
- Historical Audit V1-V6 (Phase 5C)

### Architecture BSAA
- Phase BSAA-0/BSAA-1: Etude + Architecture complete

### Optimisation TERRITOIRE
- Performance backend (stale-while-revalidate, ThreadPoolExecutor)
- Weather Engine v3 (nowcasting, visibilite, score meteo)
- Moteurs SUPRA avances hybrides
- Bloc Meteo Intelligent (Zustand store unifie useWeatherStore)
- Suppression watermark + BCE4X_UIShield

### P0 Score Header (26 Mars 2026)
- Score badge TOUJOURS visible, pipeline: globalScore > bionicZones > heatmapV10Data > bionicStats
- Typographie harmonisee WAYPOINT, position verrouillee

### P0 SUPRA Uniformisation (26 Mars 2026)
- Couleur unique #FF9800, SupraButton unifie, RenderGuard actif

### P0 Weather Engine v3 Unification (27 Mars 2026)
- Dashboard relie a Weather v3 via useWeatherStore (source unique)
- WeatherWidget reecrit, ancien pipeline V1 elimine du Dashboard
- CoreDashboard: huntingConditions calcule depuis v3 reel

### P0 Header Stability Rule (27 Mars 2026)
- LayoutFreeze(), CSS contain:layout style, Guards periodiques actifs

### P0 Navigation Restructuration (27 Mars 2026)
- MAP dropdown -> 2 entrees nav primaires: ANALYSE TERRITOIRE + CARTE INTERACTIVE
- TRIPS/SORTIES supprime de la navigation
- "Mon Territoire" renomme "Analyse Territoire BIONIC"
- Route /analyse-territoire ajoutee (alias -> MonTerritoireBionicPage)
- FULL_VIEWPORT_ROUTES mis a jour
- Nav mobile restructuree en miroir du desktop
- Activation gold (#F5A623) sur la page active
- BCE-4X-UI applique sur les deux entrees nav

### Migration MongoDB x7000
- Pipeline soumission fournisseur operationnel

---

## Modules Primaires

### ANALYSE TERRITOIRE (/mon-territoire-bionic)
Carte strategique: zones, corridors, hotspots, vent, meteo v3, SUPRA, trails optimises.
Position GPS usager (marker discret). Pas de GPS lourd.

### CARTE INTERACTIVE (/map)
Carte terrain GPS: navigation, GPS tracking, groupe, traces, waypoints, notes, sessions.
GPS Engine v1, Trail Engine v1, Mode GPS, Mode Groupe, Mode Traces.

---

## Taches Prochaines

### P1 - Frontend Admin x7000
### P1 - Fiche produit x6030
### P1 - Nettoyage modules V5 residuels

### P2 - BSAA-2: Implementation (GELE/BACKLOG)
### P3 - Merge Work1 vers main (INTERDIT sans validation STEEVE-MAX)

---

## Fichiers Cles
- /app/frontend/src/App.js (Navigation principale)
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx
- /app/frontend/src/pages/NutritionIntelligenceSupra.jsx
- /app/frontend/src/components/territoire/map/BCE4X_UIShield.jsx
- /app/frontend/src/stores/useBionicStore.js
- /app/frontend/src/stores/useWeatherStore.js
- /app/frontend/src/modules/dashboard/CoreDashboard.jsx
- /app/frontend/src/modules/weather/components/WeatherWidget.jsx

## API Endpoints
- /api/v3/weather/current (Weather Engine v3 — SOURCE UNIQUE)
- /api/v6/supra/advanced
- /supplier/submit, /supplier/review, /supplier/activate
