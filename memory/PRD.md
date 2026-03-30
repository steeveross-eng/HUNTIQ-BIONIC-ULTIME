# HUNTIQ-V6 / BIONIC HUNT — PRD (Product Requirements Document)
## BCE-4X GOLDEN / STEEVE-MAX

### Probleme original
Application de chasse BIONIC HUNT — plateforme d'analyse de territoire, intelligence nutritionnelle, gestion de salines, et recommandations scientifiques. Reconstruction du module SUPRA v2 avec grilles 3 colonnes, Standard GOLDEN, Marketing Engine (PARTAGER), Soil Engine, et fiches explicatives GUIDE BIONIC — NIVEAU PROFESSIONNEL.

### Architecture
- **Backend**: FastAPI (port 8001)
- **Frontend**: React (port 3000)
- **Database**: MongoDB
- **Modules backend**: 72+ modules (moteurs), dont share_engine, salines_ultime_engine, soil_engine
- **UI**: STANDARD GOLDEN (#1E293B, no borders, grid-cols-3)

---

## IMPLEMENTE

### Phase 1: SUPRA v2 — Grilles 3 colonnes (TERMINE)
- 5 onglets (Analyse, Fiche, Intelligence, Comparez, Commandez) en grid-cols-3
- Standard GOLDEN global (CSS vars, no borders, contrast-only separation)

### Phase 2: PARTAGER — Marketing Engine (TERMINE)
- 14 canaux de partage (gmail, facebook, whatsapp, linkedin, etc.)
- Backend share_engine: log events, create contacts, master-switch

### Phase 3: Fiches GUIDE BIONIC — NIVEAU PROFESSIONNEL™ (TERMINE — 2026-03-30)
- Tous les sous-criteres dans l'onglet FICHE sont cliquables (30 sous-criteres)
- Ouverture de modales avec 15 sections obligatoires
- Separation stricte par espece: Orignal, Chevreuil, Ours, Wapiti, Dindon
- 10-20 recommandations terrain concretes par espece (distances, angles, hauteurs)
- Sources TOP-TIER: 5-17 references par fiche
  - Niveau 1: MFFP, UQAR, ULaval, UQAC, Parcs Canada, USGS, USDA
  - Niveau 2: J. Wildlife Mgmt, Can. J. Zoology, Wildlife Soc. Bulletin
  - Niveau 3: NDA, RMEF, NWTF, Bear Trust, QDMA
  - Niveau 4: MSU Deer Lab, UGA Deer Lab, Alberta Fish & Wildlife
- Fichier de donnees: criteriaDatabase.js (5 criteres detailles + DEFAULT professionnel)
- Criteres entierement detailles: position_vs_affuts, accessibilite_vehicule, couverture_vent, corridors_deplacement, couvert_forestier
- Criteres avec DEFAULT professionnel espece-specifique: 25 autres sous-criteres

### Phase 4: SOIL ENGINE — Classification pedologique (TERMINE — 2026-03-30)
- Backend module: /app/backend/modules/soil_engine/router.py
- Endpoint: GET /api/v1/soil/analyze?lat=X&lng=Y&species=X&season=X
- 7 types de sol: loam_sableux, argile_limoneuse, sable_grossier, organique_tourbeux, roc_affleurant, loam_argileux, glaciaire_morainique
- Score pedologique (0-100) avec grade (S/A/B/C/D/F)
- Metriques: retention_mineraux, drainage_naturel, risque_lessivage, capacite_portance, permeabilite, pH, profondeur, matiere_organique, texture
- Recommandations espece-specifiques (orignal, chevreuil, ours, wapiti, dindon)
- Notes saisonnieres
- Sources: IRDA Quebec, MRNF, CGQ, MFFP, SLC, USDA
- Integration SUPRA v2: affiche dans onglet ANALYSE (carte Sol complete) et onglet FICHE (panneau Sol — Type detecte avec recommandations)

---

## BACKLOG / GELE

- P2: Phase 2D — Purge frontend shadcn/utils (GELE)
- P2: Pression historique chasse → choix_affuts engine (GELE)
- P2: Phase BSAA-2 — Implementation Social Ads module (GELE)
- P2: Merge vers main — STRICTEMENT INTERDIT

---

## FICHIERS CLES
- /app/frontend/src/components/territoire/ui/CriteriaDetailModal.jsx
- /app/frontend/src/components/territoire/ui/criteriaDatabase.js
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx
- /app/backend/modules/soil_engine/router.py
- /app/backend/modules/share_engine/router.py
- /app/backend/server.py

## API ENDPOINTS
- GET /api/v1/soil/analyze — Analyse pedologique GPS
- GET /api/v1/soil/status — Status du module
- POST /api/share/log-event — Log partage
- POST /api/share/master-switch — Switch marketing
