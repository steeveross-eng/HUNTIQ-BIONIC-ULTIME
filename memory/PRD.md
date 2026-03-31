# HUNTIQ-V6 / BIONIC HUNT — PRD (Product Requirements Document)
## BCE-4X GOLDEN / STEEVE-MAX
## Derniere mise a jour: 2026-03-30

---

### Probleme original
Application de chasse BIONIC HUNT. Reconstruction SUPRA v2 (3 colonnes), Standard GOLDEN, Marketing Engine, Soil Engine, fiches GUIDE BIONIC NIVEAU PROFESSIONNEL.

### Architecture
- **Backend**: FastAPI (port 8001) | **Frontend**: React (port 3000) | **Database**: MongoDB
- **Modules backend**: 72+ modules + soil_engine + share_engine
- **UI**: STANDARD GOLDEN (#1E293B, no borders, grid-cols-3)

---

## STATUT: V1 INTERNE — NON CERTIFIEE

---

## IMPLEMENTE

### SUPRA v2 — 3 colonnes (TERMINE)
- 5 onglets: Analyse, Fiche, Intelligence, Comparez, Commandez
- Standard GOLDEN global

### PARTAGER — Marketing Engine (TERMINE)
- 14 canaux de partage | Backend: log events, create contacts

### GUIDE BIONIC — NIVEAU PROFESSIONNEL™ (V2 EN COURS)

#### 13 criteres ENTIEREMENT DETAILLES (P0 termines):
1. position_vs_affuts — 15 recos/espece, 17 sources
2. accessibilite_vehicule — 10-12 recos/espece, 8 sources
3. couverture_vent — 10 recos/espece, 10 sources
4. corridors_deplacement — 11 recos/espece, 10 sources
5. couvert_forestier — 8 recos/espece, 10 sources
6. source_eau — 10 recos/espece, 10 sources (P0 V2)
7. pression_chasse — 10 recos/espece, 10 sources (P0 V2)
8. tranquillite_zone — 8 recos/espece, 9 sources (P0 V2)
9. potentiel_trophee — 8 recos/espece, 10 sources (P0 V2)
10. visibilite_affuts — 9 recos/espece, 8 sources (P0 V2)
11. topographie_lidar — 8 recos/espece, 8 sources (P0 V2)
12. hydrologie — 8 recos/espece, 8 sources (P0 V2)
13. drainage_sol — 7 recos/espece, 6 sources (P0 V2)

#### 17 criteres en DEFAULT professionnel (P1/P2 a reecrire):
- accessibilite_pieton, facilite_maintenance, proximite_infrastructure
- securite_acces, frequence_visite, historique_observations
- complementarite_reseau, adaptabilite_saisonniere, potentiel_expansion
- cout_mineraux_annuel, cout_transport, cout_temps
- retour_observation, retour_recolte, durabilite
- alignement_sentiers, lissage, penetrabilite, effort_reel

#### Especes supportees: Orignal, Chevreuil, Ours noir, Wapiti, Dindon sauvage

### SOIL ENGINE V1 (TERMINE — DETERMINISTE)
- Endpoint: GET /api/v1/soil/analyze
- 7 types de sol, score 0-100, grade S/A/B/C/D/F
- **LIMITATION V1**: GPS hash deterministe, PAS de donnees reelles
- Integration: SUPRA ANALYSE + FICHE (cartes Sol avec recommandations)
- Marqueurs V1 dans API + code + documentation

---

## DOCUMENTATION LIVREE
- /app/memory/ARCHITECTURE_INTERCONNEXION.md — Schema des flux, dependances, validations, rollback, phasage P1-P6
- /app/memory/PLAN_V2_SOUS_CRITERES.md — Liste des 25 sous-criteres, priorites, echeancier

---

## BACKLOG V2

### P1 — Reecriture sous-criteres (17 restants)
- Voir PLAN_V2_SOUS_CRITERES.md

### P2 — Soil Engine V2
- Cartographie IRDA, LiDAR MRNF, hydrologie, score reel
- Voir ARCHITECTURE_INTERCONNEXION.md section 7

### P2 — Interconnexions P3-P6
- SUPRA <-> Strategie du Jour, Intelligence IA, Admin Premium, BCE-4X

### GELE
- Phase 2D: Purge frontend shadcn/utils
- Pression historique → choix_affuts engine
- BSAA-2: Social Ads module
- Merge main — STRICTEMENT INTERDIT

---

## FICHIERS CLES
- /app/frontend/src/components/territoire/ui/criteriaDatabase.js
- /app/frontend/src/components/territoire/ui/CriteriaDetailModal.jsx
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx
- /app/backend/modules/soil_engine/router.py
- /app/backend/server.py

## API ENDPOINTS
- GET /api/v1/soil/analyze — Analyse pedologique GPS (V1 deterministe)
- GET /api/v1/soil/status — Status Soil Engine
- POST /api/share/log-event — Log partage
- POST /api/share/master-switch — Switch marketing
