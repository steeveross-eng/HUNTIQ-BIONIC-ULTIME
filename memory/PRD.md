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

### Phase 1-3: Import et Archive
- Clone bionic-v3-dev, inventaire certifie, ZIP archive

### Gouvernance
- GOVERNANCE.md, EMERGENT_PROTOCOL.md, SECURITY_POLICY.md

### Audits
- Engine, Coherence, Historical V1-V6

### Architecture BSAA
- Phase BSAA-0/BSAA-1 complete

### Optimisation TERRITOIRE
- Performance backend, Weather Engine v3, Moteurs SUPRA hybrides
- Bloc Meteo Intelligent, BCE4X_UIShield, Suppression watermark

### P0 Score Header (26 Mars)
- Score badge TOUJOURS visible, pipeline multi-source, typo WAYPOINT

### P0 SUPRA Uniformisation (26 Mars)
- Couleur unique #FF9800, SupraButton unifie, RenderGuard

### P0 Weather Engine v3 Unification (27 Mars)
- Dashboard relie a Weather v3, ancien pipeline V1 elimine

### P0 Header Stability Rule (27 Mars)
- LayoutFreeze, CSS contain:layout style, Guards periodiques

### P0 Navigation Restructuration (27 Mars)
- ANALYSE TERRITOIRE + CARTE INTERACTIVE: nav primaires directes
- TRIPS/SORTIES supprime, renommage Analyse Territoire BIONIC

### P0 Refonte SUPRA PREMIUM (27 Mars)
- 9 sections: Score, Phase physio, Physiologie minerale, Influence support, Recette optimale, Score mineral, Comportement males, Guide implantation, Preuves scientifiques
- Couts deplaces tout en bas (collapsible, ferme par defaut)
- Recettes intelligentes avec priorites (CRITIQUE/RECOMMANDE)
- Boutons "VOIR LE PRODUIT" -> lien vers fiche produit
- Tooltip carte ameliore: "VOIR LES BESOINS DE TON SITE"
- Donnees narratives: physiologie par espece/saison, comportement males
- Hierarchie substrats avec scores (bois mou 95, bois dur 70, sol nu 45, bloc 60)

### P1 Fiches Produits (27 Mars)
- Route /product/:productId
- 5 mineraux documentes: Sodium, Calcium, Phosphore, Magnesium, Potassium
- Chaque fiche: Role physiologique, Support optimal, Dosage, Prix, Disponibilite locale
- Badge SUPRA CERTIFIE + bouton Commander

### Migration MongoDB x7000
- Pipeline soumission fournisseur operationnel

---

## Modules Primaires

### ANALYSE TERRITOIRE (/mon-territoire-bionic)
Carte strategique: zones, corridors, hotspots, vent, meteo v3, SUPRA, trails.

### CARTE INTERACTIVE (/map)
Carte terrain GPS: navigation, tracking, groupe, traces, waypoints.

### SUPRA (/nutrition-supra)
Intelligence terrain: score mineral, recettes, physiologie, comportement, couts.

### Fiches Produits (/product/:id)
Detail produit mineral: role, dosage, prix, disponibilite.

---

## Taches Prochaines

### P1 - Frontend Admin x7000
### P1 - Fiche produit x6030 (enrichissement)
### P1 - Nettoyage modules V5 residuels

### P2 - BSAA-2: Implementation (GELE/BACKLOG)
### P3 - Merge Work1 vers main (INTERDIT sans validation STEEVE-MAX)

---

## Fichiers Cles
- /app/frontend/src/App.js
- /app/frontend/src/pages/NutritionIntelligenceSupra.jsx (SUPRA PREMIUM)
- /app/frontend/src/pages/ProductPage.jsx (Fiches produits)
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/components/territoire/NutritionPointsLayer.jsx (Tooltip)
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx
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
