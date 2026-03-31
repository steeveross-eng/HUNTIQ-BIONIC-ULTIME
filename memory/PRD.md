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

### UI / Navigation
- Header principal: HOME, DASHBOARD, ANALYSE TERRITOIRE, CARTE, PERMIS, SHOP
- Sub-header Territoire: SPLIT, CARTE, ESPECES, OBSERVATION, INTELLIGENCE, ZONES, ALIMENTATION, POINTS CHAUDS, SEUIL, CURSEUR
- Bouton WAYPOINT (anciennement WPT) dans le sub-header
- Bouton PARTAGER relocalise dans le sub-header (V8)
- SCORE CHASSE dans le sub-header
- METEO BIONIC compact
- Cookie banner conforme Quebec

### Guide BIONIC — Niveau Professionnel V2
- **32 criteres au standard V2 complet** (ZERO DEFAULT generique)
- 13 criteres originaux (V1 + P0 V2) dans `criteriaDatabase.js`
- **19 criteres P1/P2 dans `criteriaDatabase_P1P2.js`** (1327 lignes, 197 KB)
- 5 especes par critere: Orignal, Chevreuil, Ours noir, Wapiti, Dindon sauvage
- 15 sections par critere: definition, methodologie, justification, recommandations, strategies, techniques, erreurs, optimisations (4 saisons + meteo + support + pression), seuils, sources TOP-TIER
- Sources: MFFP, UQAR, ULaval, NDA, RMEF, NWTF, MSU Deer Lab, UGA Deer Lab

### Backend
- GET /api/v1/soil — Soil Engine (pedologie, LiDAR)
- Scoring multi-criteres sur 100 points par critere

### Integrations
- Stripe (paiement Premium)
- Shapely (geometrie territoriale)
- Leaflet (cartographie)

---

## Livrables Completes (Directive x4850-x4852)

### Section A — UI_HEADER_ALIGNMENT_V8
- [x] PARTAGER relocalise App.js → TerritoireHeader.jsx
- [x] WPT renomme en WAYPOINT
- [x] AUDIT_CSS_HEADER_V8.md genere

### Section B — REWRITE_19_SUBCRITERIA_P1_P2
- [x] criteriaDatabase_P1P2.js cree (19 criteres, 1327 lignes)
- [x] Import dans criteriaDatabase.js (ES module)
- [x] 19 entrees DEFAULT remplacees par les imports reels
- [x] SOUS_CRITERES_V2_COMPLET.md genere
- [x] Frontend compile et fonctionne

### Section C — INTERCONNEXIONS_P3_P6
- [x] INTERCONNEXIONS_P3_P6.md genere
- [x] Cartographie: SUPRA ↔ Strategie du Jour ↔ Intelligence IA ↔ Admin Premium ↔ BCE-4X
- [x] Matrice des flux de donnees
- [x] Regles d'interconnexion et de validation
- [x] Phases d'implementation P3-P6 definies

---

## Backlog (GELE par STEEVE-MAX)

- P2: Soil Engine V2 (donnees pedologiques reelles, LiDAR) — GELE
- P2: Phase 2D (Purge shadcn/utils) — GELE
- P2: Phase BSAA-2 (Social Ads Automation) — GELE
- P2: Implementation P3-P6 (Interconnexions) — GELE
- INTERDIT: Merge vers main — STRICTEMENT INTERDIT

---

## Fichiers Cles
- `/app/frontend/src/App.js`
- `/app/frontend/src/components/territoire/ui/TerritoireHeader.jsx`
- `/app/frontend/src/components/territoire/ui/criteriaDatabase.js`
- `/app/frontend/src/components/territoire/ui/criteriaDatabase_P1P2.js`
- `/app/memory/AUDIT_CSS_HEADER_V8.md`
- `/app/memory/SOUS_CRITERES_V2_COMPLET.md`
- `/app/memory/INTERCONNEXIONS_P3_P6.md`
- `/app/memory/PLAN_V2_SOUS_CRITERES.md`

---

## Regles de Gouvernance
- Protocole BCE-4X / GOLDEN UI
- Autorite: STEEVE-MAX
- ZERO LOSS, ZERO REGRESSION
- Validation explicite requise pour chaque phase
- Merge main STRICTEMENT INTERDIT
