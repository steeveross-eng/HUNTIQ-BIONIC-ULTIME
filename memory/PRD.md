# HUNTIQ-V6 — PRD (Product Requirements Document)
## Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

### Projet
Reconstruction, modernisation et stabilisation de la plateforme HUNTIQ-V6.

### Stack Technique
- **Backend**: FastAPI, ThreadPoolExecutor, MongoDB
- **Frontend**: React, Zustand, React-Leaflet, Tailwind
- **Gouvernance**: BCE-4X, BCE-4X-UI (PositionLock, ZIndexGuard, RenderGuard, LayoutFreeze)

---

## Travaux Accomplis

### Phase 1-3: Import, Archive, Gouvernance, Audits, BSAA
- Clone, inventaire, ZIP, GOVERNANCE.md, Engine/Coherence/Historical audits, BSAA-0/1

### Optimisation TERRITOIRE
- Performance backend, Weather Engine v3, Moteurs SUPRA hybrides
- Bloc Meteo Intelligent, BCE4X_UIShield, Suppression watermark

### P0 Score Header (26 Mars) — DONE
### P0 SUPRA Uniformisation (26 Mars) — DONE
### P0 Weather Engine v3 Unification (27 Mars) — DONE
### P0 Header Stability Rule (27 Mars) — DONE
### P0 Navigation Restructuration (27 Mars) — DONE
### P0 Refonte SUPRA PREMIUM (27 Mars) — DONE
### P1 Fiches Produits (27 Mars) — DONE

### P0 Unification SUPRA LOCAL (27 Mars)
- Onglet SUPRA supprime de la navigation (desktop + mobile)
- Lazy import NutritionIntelligenceSupra supprime
- Route /nutrition-supra redirige vers /mon-territoire-bionic (ANALYSE TERRITOIRE)
- SUPRA LOCAL (SAL-XX via NutritionPointDetailPanel) = moteur unique officiel
- Interaction carte: clic point jaune -> SUPRA SAL-XX (panel contextuel)
- Tooltip: "VOIR LES BESOINS DE TON SITE" sur survol point jaune
- Navigation finale: HOME | DASHBOARD | ANALYSE TERRITOIRE | CARTE INTERACTIVE | PERMIS | SHOP | NUTRITION

---

## Navigation Officielle (27 Mars 2026)
1. HOME
2. DASHBOARD
3. ANALYSE TERRITOIRE (/mon-territoire-bionic) — Carte strategique
4. CARTE INTERACTIVE (/map) — Carte terrain GPS
5. PERMIS & ENREGISTREMENT
6. SHOP
7. NUTRITION
- ~~SUPRA~~ (SUPPRIME — unifie dans SUPRA LOCAL)
- ~~TRIPS~~ (SUPPRIME)

---

## Modules Primaires

### ANALYSE TERRITOIRE (/mon-territoire-bionic)
Carte strategique + SUPRA LOCAL (SAL-XX) via points jaunes.

### CARTE INTERACTIVE (/map)
Carte terrain GPS: navigation, tracking, groupe, traces, waypoints.

### SUPRA LOCAL (NutritionPointDetailPanel)
Moteur unique SUPRA. Ouvert via clic sur point jaune dans ANALYSE TERRITOIRE.
Score mineral, recettes, physiologie, comportement, couts.

### Fiches Produits (/product/:id)
Detail produit mineral: role, dosage, prix, disponibilite.

---

## Taches Prochaines
### P1 - Frontend Admin x7000
### P1 - Fiche produit x6030 (enrichissement)
### P1 - Nettoyage modules V5 residuels

## Backlog
### P2 - BSAA-2: Implementation (GELE)
### P3 - Merge Work1 vers main (INTERDIT sans validation STEEVE-MAX)

---

## Fichiers Cles
- /app/frontend/src/App.js
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx
- /app/frontend/src/pages/ProductPage.jsx
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx (SUPRA LOCAL)
- /app/frontend/src/components/territoire/NutritionPointsLayer.jsx
- /app/frontend/src/components/territoire/map/BCE4X_UIShield.jsx
- /app/frontend/src/stores/useBionicStore.js
- /app/frontend/src/stores/useWeatherStore.js
- /app/frontend/src/modules/dashboard/CoreDashboard.jsx
- /app/frontend/src/modules/weather/components/WeatherWidget.jsx

## API Endpoints
- /api/v3/weather/current (Weather Engine v3)
- /api/v6/nutrition-intelligence/full-analysis (SUPRA)
- /api/v6/supra/advanced
- /supplier/submit, /supplier/review, /supplier/activate

## Fichiers Obsoletes (non supprimes, desactives)
- /app/frontend/src/pages/NutritionIntelligenceSupra.jsx (ancien SUPRA global, plus charge)
