# PRD.md — HUNTIQ-V6 / BIONIC

## Problem Statement
Reconstruction du repo HUNTIQ-V6 depuis HUNTIQ-V5 branche bionic-v3-dev, avec governance BCE-4X / STEEVE-MAX, audits, restauration de fonctionnalites perdues, et nouvelles fonctionnalites.

## What's Implemented (2026-03-24)

### SALINE INTELLIGENCE ULTRA (COMPLETE — Tests 100%)
- **Phase A**: 7 moteurs scientifiques backend (soil, nutrient deficiency, wildlife nutritional, vegetation forage, hydrology leaching, seasonal metabolism, saline recommendation)
- **Phase B**: 5 couches geospatiales (SoilGrids, HydroSHEDS, Ecoforestry, Behavioral, SRTM)
- **Phase C+D**: API endpoints + E-Commerce Stripe complet (catalogue 6 produits, panier, checkout)
- **Phase E**: Frontend immersif pleine page (4 onglets: Analyse, Recettes, Produits, Commande)
- **Phase F**: Interconnexion avec BIONIC (11 engines reutilises, navigation integree)
- **Phase G**: 5 rapports d'audit produits, commits Work1, ZIP archive

### Infrastructure precedente
- Import et certification du repo HUNTIQ-V6
- Governance BCE-4X / MAX ULTRA / STEEVE-MAX
- Branche Work1 active
- Architecture BSAA (spec complete)
- Audits: engines, coherence, historique V1-V6
- Restauration auto_optimization (optimization_engine)
- Migration geometrie: cercles 600m uniformes
- Exclusion eau V7 complete
- Fix admin premium hotspots

## Prioritized Backlog

### P0 — En attente validation STEEVE-MAX
- Validation utilisateur des phases A-G Saline Intelligence Ultra

### P1 — Prochaines taches
- BSAA-2: Implementation BIONIC Social Ads Automation
- Interconnexion Saline <-> Mon Territoire (carte)

### P2 — Futur
- Merge Work1 vers main
- Nettoyage audit_historical
- Integration API externes (SoilGrids, HydroSHEDS reelles)

## Tech Stack
- Backend: FastAPI, Python, MongoDB
- Frontend: React, Leaflet
- E-Commerce: Stripe (emergentintegrations)
- Architecture: 84+ engines modulaires
- Governance: BCE-4X / STEEVE-MAX

## Key Routes
- `/saline` — Saline Intelligence Ultra
- `/api/v1/saline/*` — 14 endpoints scientifiques
- `/api/v1/saline/shop/*` — 7 endpoints e-commerce
