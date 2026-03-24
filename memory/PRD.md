# PRD.md — HUNTIQ-V6 / BIONIC

## Problem Statement
Reconstruction du repo HUNTIQ-V6 depuis HUNTIQ-V5 branche bionic-v3-dev, avec governance BCE-4X / STEEVE-MAX, audits, restauration de fonctionnalites perdues, et nouvelles fonctionnalites.

## What's Implemented (2026-03-24)

### SALINE INTELLIGENCE ULTRA (COMPLETE — Tests 100%)
- 7 moteurs scientifiques backend
- 5 couches geospatiales
- E-Commerce Stripe complet (6 produits, panier, checkout CAD)
- Frontend immersif /saline (4 onglets)
- 11 engines BIONIC reutilises, 5 rapports audit

### AUDIT V5 → V6/V7 (COMPLETE)
- 10 modules V5 audites: 3 complets/actifs, 7 existants mais non enregistres
- Master Switch analyse: existe mais non enregistre, 12 switches manquants identifies
- Risques duplication/conflit documentes

### MODES D'EMPLOI (COMPLETE — STEEVE-MAX x1700)
- 10 modes d'emploi complets (description, APIs, inputs, outputs, limites, exemples)
- 7 plans UI detailles pour modules necessitant interface
- Tutoriel cameras Vision Faune (5 etapes)
- 8 endpoints cameras confirmes
- 10 switches Master Switch mappes

### Infrastructure precedente
- Governance BCE-4X / MAX ULTRA / STEEVE-MAX
- Branche Work1 active, ZIP archive a jour
- Architecture BSAA (spec complete)
- Audits: engines, coherence, historique V1-V6
- Migration geometrie cercles 600m, exclusion eau V7

## Prioritized Backlog

### P0 — En attente validation STEEVE-MAX
- Validation utilisateur des modes d'emploi et plans UI
- Validation avant integration UI frontend des 7 modules
- Validation avant enregistrement Master Switch + 7 modules dans server.py

### P1 — Actions identifiees
- Enregistrer Master Switch dans server.py + 12 switches supplementaires
- Enregistrer 7 modules V5 dans server.py (predictive, weather, camera, trip, tracking, alerts, scoring)
- Creer territory_engine router
- Creer page UI Vision Faune (cameras)

### P2 — Futur
- BSAA-2 implementation
- Merge Work1 vers main
- Fusion weather + weather_shadow
- Fusion alerts + notification
- Upload direct photos (cameras — actuellement email seulement)

## Key Documents
- `/audit/audit_v5_v6_v7_modules_predictifs.md` — Audit 10 modules
- `/audit/bionic_modules_modes_emploi.md` — Modes d'emploi + Plans UI
- `/audit/saline_validation_global.md` — Validation Saline Intelligence
- `/architecture/saline_intelligence_ultra_architecture.md` — Architecture Saline
