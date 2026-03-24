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

---

## Prioritized Backlog

### P0 — En attente validation x2260-V2
- Validation STEEVE-MAX de la directive x2260-V2 requise

### P1 — En attente directive
- Module Achat de permis / Enregistrement gibier (x2200 mentionne)
- Activation publique via Master Switch (x3000)
- Connexion modules cameras + alertes temps reel
- Integration donnees terrain reelles

### P2 — Futur
- BSAA-2: Social Ads Automation
- Completion modules partiels
- Documentation modules complexes

### P3 — Long terme
- Merge Work1 → main
- Nettoyage repos historiques

---

## Architecture
```
CORE_ROUTERS: 73 modules actifs
Master Switch: 22 switches (tous LOCKED)
Species: 8 especes integrees systemiquement
Biogeography: 8 especes / 26+ juridictions / filtrage systemique
Endpoints ecological: 16 (9 base + 4 species + 4 biogeography — internes, LOCKED)
Endpoints data-fabric: 6
Architecture: V7-X2260-BIOGEOGRAPHY
```

**Derniere mise a jour:** 2026-03-25 — x2260-V2 Complete
**Branche active:** Work1
