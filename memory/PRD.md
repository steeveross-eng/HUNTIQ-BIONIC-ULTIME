# HUNTIQ-V6/V7 — Product Requirements Document
## GOLDEN-BCE-4X | STEEVE-MAX Protocol

---

## Original Problem Statement
Reconstruction et evolution du projet HUNTIQ (V6 → V7), application modulaire full-stack
(FastAPI + React + MongoDB) dediee a la chasse intelligente. Protocole strict de gouvernance
(GOLDEN-BCE-4X / STEEVE-MAX) avec validation explicite a chaque phase.

---

## What Has Been Implemented

### Phases historiques (Complete)
- Import & Governance, Audits, SALINE INTELLIGENCE ULTRA, P0 Admin Refactor

### ECOSYSTEME UNIFIE x2000 (Complete - 2026-03-25)
- Moteur ecologique (13 sous-moteurs, 9 endpoints)
- Data Fabric (15→18 domaines, 6 endpoints)
- Pipeline comportemental (16 correlations, 4 patterns)
- UI 10 modules predictifs + 3 couches cartographiques

### INTEGRATION SYSTEMIQUE ESPECES x2250 (Complete - 2026-03-25)
- 8 especes integrees transversalement: Orignal, Cerf de Virginie, Ours noir,
  Dindon sauvage, Caribou, Wapiti, Cerf mulet, Pronghorn
- species_profiles.py: referentiel central (ecologie, alimentation, comportement,
  chasse, predictions, cartographie)
- Predictions species-aware (taux de base, plages temperature, sensibilites)
- Correlations et patterns comportementaux par espece
- 4 endpoints species API, 18 domaines Data Fabric
- Frontend 8 especes dans selecteur + cameras multi-especes
- SPECIES_MAP_CONFIG pour couches cartographiques par espece
- Rapport: audit/bionic_species_full_integration_x2250.md

### MATRICE BIOGEOGRAPHIQUE x2260-V2 (Complete - 2026-03-25)
- Matrice biogeographique JSON: distribution reelle 8 especes / 26+ juridictions (CA + US)
- Moteur filtrage biogeography.py: geocodage inverse, filtrage par juridiction (243 lignes)
- 4 nouveaux endpoints: /biogeography/jurisdiction, /filter, /species/{id}
- Integration intelligence_core.py: hotspots, corridors, predictions filtrés par especes locales
- Integration frontend: selecteur especes filtre dynamiquement selon juridiction
- Sources officielles: MFFP, MNRF, ECCC, USFWS, NatureServe, IUCN
- Rapport: audit/bionic_species_biogeography_x2260.md
- Commit: 8c20e902 sur Work1

### SYNCHRONISATION PREVIEW x2275 (Complete - 2026-03-25)
- Deploiement immediat de toutes les directives (x1900→x2260) vers PREVIEW
- Script auto-sync: scripts/sync_preview.sh
- Pipeline: chaque directive commitee = PREVIEW mis a jour automatiquement
- Rapport: audit/bionic_preview_sync_x2275.md
- Commit: 392ef93f sur Work1

### DIRECTIVE x2290-V3 (Complete - 2026-03-25)
**x2200-FINAL-V2 — Permis + Enregistrement gibier:**
- HuntingLicensePage reecrit: 2 onglets (Permis | Enregistrement)
- Selecteur pays/province, filtrage biogeographique, portails officiels

**x2280-A — Vent Renforce +15%:**
- Rose des vents SVG interactive + fleche dynamique
- Barre intensite gradient + interpretation professionnelle

**x2280-B — Moteur d'Affuts Professionnels:**
- bionic_stand_recommendation_engine (backend): 5 types, 7 facteurs scoring
- 11 sections justification par affut, chemin approche 13 points
- Endpoints: /api/v1/stand-recommendation/health + /recommend

**x2290 — Pop-up + Chemin:**
- JustificationPopup: modale pleine grandeur, 11 sections detaillees
- ApproachPathMap: trace pointe SVG, calcul anti-vent
- StandsModule: onglet Affuts Pro dans BIONIC Intelligence
- Rapport: audit/bionic_permis_wind_affuts_x2290.md
- Commit: 020226fe sur Work1

### DIRECTIVE x2300-EXEC — Architecture Hybride BIONIC (Complete - 2026-03-25)
- Architecture hybride WEB + Mobile Native definie comme standard institutionnel
- bionic_hybrid_architecture_x2300.md: WEB (analyse, planification, gouvernance) + Mobile (terrain, GPS, affuts, hors-ligne)
- bionic_api_spec_x2300.md: API unifiee 10 domaines, 46 endpoints, JWT, WebSocket, pagination
- roadmap_x2300.md: 4 phases (P0→P3), 20-28 semaines, dependances identifiees
- Mode hors-ligne specifie: MBTiles, SQLite (WatermelonDB), sync differee
- Rapport: audit/bionic_architecture_hybride_x2300.md
- Commit: 93c76f2c sur Work1

---

## Prioritized Backlog

### P0 — Attente validation x2300-EXEC
- Validation STEEVE-MAX requise pour l'architecture hybride

### P0 — Phase 1 Roadmap (attente directive x2300-P1)
- Normalisation API unifiee, endpoints observations + sync, adaptation mobile

### P1 — Phase 2 Roadmap (attente directive x2300-P2)
- Prototype app mobile (carte, GPS, zones 600m, affuts, hors-ligne minimal)

### P2 — Phase 3 Roadmap
- Observations terrain, alertes push, UX terrain

### P3 — Phase 4 Roadmap + Autres
- Durcissement, beta fermee, publication Stores
- BSAA-2: Social Ads Automation
- Merge Work1 → main

---

## Architecture
```
CORE_ROUTERS: 75 modules actifs
Master Switch: 22 switches (tous LOCKED)
Species: 8 especes integrees systemiquement
Biogeography: 8 especes / 26+ juridictions / filtrage systemique
Stand Engine: 5 types, 7 facteurs, 11 sections justification
Endpoints ecological: 16 (9 base + 4 species + 4 biogeography)
Endpoints stand-recommendation: 2 (health + recommend)
Endpoints data-fabric: 6
Hybrid Architecture: WEB (React) + Mobile Native (React Native/Expo)
API Unifiee: 10 domaines, 46 endpoints specifies
Roadmap: 4 phases, 20-28 semaines
Architecture: V7-X2300-HYBRID-BIONIC
```

**Derniere mise a jour:** 2026-03-25 — x2300-EXEC Complete
**Branche active:** Work1
**PREVIEW URL:** https://huntiq-restore.preview.emergentagent.com
