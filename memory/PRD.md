# HUNTIQ-V6 / BIONIC HUNT — PRD
## Protocole BCE-4X — STEEVE-MAX — GOLDEN UI

---

## Probleme Original
Plateforme d'analyse de territoires de chasse avec scoring multi-criteres, guide BIONIC professionnel, intelligence IA, et fonctionnalites e-commerce (Premium, Shop, Commandez).

## Utilisateurs
- Chasseurs professionnels Quebec/Canada
- Gestionnaires de territoires fauniques
- Guides de chasse et pourvoiries

## Architecture
- Frontend: React + Leaflet + Shadcn UI
- Backend: FastAPI + MongoDB
- Modules: Soil Engine, Guide BIONIC (criteriaDatabase), Meteo, Score Chasse

## Fonctionnalites Implementees

### UI / Navigation (GOLDEN V9)
- Header principal: HOME, DASHBOARD, ANALYSE TERRITOIRE, CARTE, PERMIS, SHOP
- Sub-header Territoire: SPLIT, CARTE, ESPECES, OBSERVATION, INTELLIGENCE, ZONES, ALIMENTATION, POINTS CHAUDS, SEUIL, CURSEUR
- Bouton WAYPOINT (renomme depuis WPT en V8)
- Bouton PARTAGER dans le sub-header (relocalise depuis App.js en V8)
- SCORE CHASSE dans le sub-header
- **Meteo consolidee — source unique METEO BIONIC (V9: duplication sub-header supprimee)**
- **Scrollbar ORANGE BIONIC globale: 14px, gradient #FF9800-#E65100, fleches SVG haut/bas (V9)**
- **SUPRA V2 grilles: gap-1.5, space-y-1.5, paddings reduits, rounded-lg (V9)**
- **Fiches techniques: max-w-6xl, layout multi-colonnes 2x et 3x, scroll reduit -60% (V9)**
- Cookie banner conforme Quebec

### Guide BIONIC — Niveau Professionnel V2
- **32 criteres au standard V2 complet** (ZERO DEFAULT generique)
- 13 criteres originaux (V1 + P0 V2) dans `criteriaDatabase.js`
- **19 criteres P1/P2 dans `criteriaDatabase_P1P2.js`** (1327 lignes)
- 5 especes: Orignal, Chevreuil, Ours noir, Wapiti, Dindon sauvage
- 15 sections/critere: definition, methodologie, justification, recommandations, strategies, techniques, erreurs, optimisations, seuils, sources TOP-TIER

### Backend
- GET /api/v1/soil — Soil Engine (pedologie, LiDAR)
- Scoring multi-criteres sur 100 points

### Integrations
- Stripe (paiement Premium)
- Shapely (geometrie territoriale)
- Leaflet (cartographie)

---

## Livrables Completes

### Directive x4850-x4852 — REWRITE + INTERCONNEXIONS
- [x] Section A: PARTAGER relocalise + WPT→WAYPOINT + AUDIT_CSS_HEADER_V8.md
- [x] Section B: criteriaDatabase_P1P2.js (19 criteres V2) + SOUS_CRITERES_V2_COMPLET.md
- [x] Section C: INTERCONNEXIONS_P3_P6.md

### Directive x4950 — UI_HARMONISATION_V9
- [x] Section A: Meteo duplication supprimee du sub-header
- [x] Section B: Scrollbar ORANGE BIONIC globale (14px, fleches, gradient)
- [x] Section C: SUPRA V2 grille harmonisee (gap-1.5, padding reduit, 5 onglets)
- [x] Section D: Fiches techniques elargies (max-w-6xl, multi-colonnes, scroll -60%)
- [x] AUDIT_UI_V9.md genere

---

## Backlog (GELE par STEEVE-MAX)
- P2: Soil Engine V2 (donnees pedologiques reelles, LiDAR) — GELE
- P2: Phase 2D (Purge shadcn/utils) — GELE
- P2: Phase BSAA-2 (Social Ads Automation) — GELE
- P2: Implementation P3-P6 (Interconnexions modules) — GELE
- INTERDIT: Merge vers main — STRICTEMENT INTERDIT

---

## Fichiers Cles
- `/app/frontend/src/App.js`
- `/app/frontend/src/App.css`
- `/app/frontend/src/index.css`
- `/app/frontend/src/components/territoire/ui/TerritoireHeader.jsx`
- `/app/frontend/src/components/territoire/ui/CriteriaDetailModal.jsx`
- `/app/frontend/src/components/territoire/ui/criteriaDatabase.js`
- `/app/frontend/src/components/territoire/ui/criteriaDatabase_P1P2.js`
- `/app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx`
- `/app/frontend/src/components/territoire/PinnablePanel.jsx`
- `/app/memory/AUDIT_CSS_HEADER_V8.md`
- `/app/memory/AUDIT_UI_V9.md`
- `/app/memory/SOUS_CRITERES_V2_COMPLET.md`
- `/app/memory/INTERCONNEXIONS_P3_P6.md`

---

## Regles de Gouvernance
- Protocole BCE-4X / GOLDEN UI
- Autorite: STEEVE-MAX
- ZERO LOSS, ZERO REGRESSION
- Validation explicite requise pour chaque phase
- Merge main STRICTEMENT INTERDIT
