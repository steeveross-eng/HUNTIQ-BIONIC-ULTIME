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
- Historical Audit V1-V6 (Phase 5C) -> Identification auto_optimization.py manquant

### Architecture BSAA
- Phase BSAA-0: Etude de faisabilite
- Phase BSAA-1: Architecture complete (endpoints, modeles, connecteurs)

### Optimisation TERRITOIRE
- Performance backend (stale-while-revalidate, ThreadPoolExecutor)
- Weather Engine v3 (nowcasting, visibilite, score meteo)
- Moteurs SUPRA avances hybrides (deterministes + LLM)
- Bloc Meteo Intelligent (Zustand store unifie useWeatherStore)
- Suppression watermark Emergent + BCE4X_UIShield
- Repositionnement VENT v2.0 flow

### P0 Score Header (26 Mars 2026)
- Score badge TOUJOURS visible dans le header (etat loading + valeur)
- Pipeline score: globalScore > bionicZones > heatmapV10Data > bionicStats
- Typographie harmonisee avec bouton WAYPOINT
- Position verrouillee via BCE4X_UIShield

### P0 SUPRA Uniformisation (26 Mars 2026)
- Couleur unique #FF9800 pour TOUS les boutons CMD/Commander/Commandez
- Composant SupraButton unifie (sm/md/lg, hover/pressed/disabled)
- Tableau produits modernise
- RenderGuard verifie conformite couleur

### P0 Weather Engine v3 Unification (27 Mars 2026)
- Dashboard BIONIC relie a Weather Engine v3 via useWeatherStore (source unique)
- WeatherWidget reecrit pour consommer useWeatherStore au lieu de WeatherService V1
- CoreDashboard: huntingConditions calcule depuis donnees v3 reelles
- Normalisation v3: description (weather_code), hunting_score (object->flat), visibility_km
- Ancien pipeline V1 (WeatherService.getCurrentWeather) elimine du Dashboard
- PREVIEW comparatif confirme: Dashboard et TERRITOIRE affichent les MEMES valeurs

### P0 Header Stability Rule (27 Mars 2026)
- LayoutFreeze() implemente dans BCE4X_UIShield
- CSS contain: layout style applique au header
- data-bce4x-layout-frozen="true" sur le header
- Guards periodiques: enforceOverlayCompliance + enforcePositionLock + enforceRenderGuard + enforceLayoutFreeze
- Verification automatique: presence + visibilite + position des elements header
- Elements proteges: score-badge, waypoint-btn, weather-official, live, back-btn

### Migration MongoDB x7000
- Pipeline soumission fournisseur operationnel

---

## Taches Prochaines

### P1 - Frontend Admin x7000
### P1 - Fiche produit x6030
### P1 - Nettoyage modules V5 residuels

### P2 - BSAA-2: Implementation (GELE/BACKLOG)
### P3 - Merge Work1 vers main (INTERDIT sans validation STEEVE-MAX)

---

## Fichiers Cles
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
