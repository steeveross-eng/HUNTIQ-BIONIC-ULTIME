# HUNTIQ-V6 — PRD (Product Requirements Document)
## Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

### Projet
Reconstruction, modernisation et stabilisation de la plateforme HUNTIQ-V6.

### Stack Technique
- **Backend**: FastAPI, ThreadPoolExecutor, MongoDB
- **Frontend**: React, Zustand, React-Leaflet, Tailwind
- **Gouvernance**: BCE-4X, BCE-4X-UI (PositionLock, ZIndexGuard, RenderGuard, OverlayCompliance)

---

## Travaux Accomplis

### Phase 1-3: Import et Archive
- Clone `bionic-v3-dev` depuis HUNTIQ-V5
- Inventaire certifie + ZIP archive

### Gouvernance
- `GOVERNANCE.md`, `EMERGENT_PROTOCOL.md`, `SECURITY_POLICY.md`
- Protocole ZERO LOSS, ZERO REGRESSION

### Audits
- Engine Audit (84+ modules confirmes)
- Coherence Audit (Phase 5B)
- Historical Audit V1-V6 (Phase 5C) -> Identification `auto_optimization.py` manquant

### Architecture BSAA
- Phase BSAA-0: Etude de faisabilite
- Phase BSAA-1: Architecture complete (endpoints, modeles, connecteurs)

### Optimisation TERRITOIRE
- Performance backend (stale-while-revalidate, ThreadPoolExecutor)
- Weather Engine v3 (nowcasting, visibilite, score meteo)
- Moteurs SUPRA avances hybrides (deterministes + LLM)
- Bloc Meteo Intelligent (Zustand store unifie `useWeatherStore`)
- Suppression watermark Emergent + BCE4X_UIShield
- Repositionnement VENT v2.0 flow

### P0 Score Header (26 Mars 2026)
- Score badge TOUJOURS visible dans le header (etat loading + valeur)
- Pipeline score: globalScore > bionicZones > heatmapV10Data > bionicStats
- Typographie harmonisee avec bouton WAYPOINT (font-bold, uppercase, tracking-wider)
- Position verrouillee via BCE4X_UIShield (PositionLock + ZIndexGuard)
- RenderGuard + enforceOverlayCompliance() actifs periodiquement

### P0 SUPRA Uniformisation (26 Mars 2026)
- Couleur unique officielle SUPRA: #FF9800 pour TOUS les boutons de commande
- `SupraButton` composant unifie (sm/md/lg, hover/pressed/disabled)
- Tableau produits modernise (alignement scores, prix, titres)
- Tab "Commandez" unifie avec couleur SUPRA
- Boutons CMD dans NutritionIntelligenceSupra uniformises
- Protection BCE-4X-UI: RenderGuard verifie conformite couleur

### Migration MongoDB x7000
- Pipeline soumission fournisseur operationnel

---

## Taches En Cours / Prochaines

### P1 - Frontend Admin x7000
### P1 - Fiche produit x6030
### P1 - Nettoyage modules V5 residuels

### P2 - BSAA-2: Implementation (GELE/BACKLOG)
### P3 - Merge Work1 vers main (INTERDIT sans validation STEEVE-MAX)

---

## Fichiers Cles
- `/app/frontend/src/components/territoire/ui/TerritoireHeader.jsx`
- `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`
- `/app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx`
- `/app/frontend/src/pages/NutritionIntelligenceSupra.jsx`
- `/app/frontend/src/components/territoire/map/BCE4X_UIShield.jsx`
- `/app/frontend/src/stores/useBionicStore.js`
- `/app/frontend/src/stores/useWeatherStore.js`

## API Endpoints
- `/api/v3/weather/now`
- `/api/v6/supra/advanced`
- `/supplier/submit`, `/supplier/review`, `/supplier/activate`
