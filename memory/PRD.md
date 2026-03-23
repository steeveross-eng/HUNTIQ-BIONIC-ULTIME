# PRD.md — HUNTIQ-V6
# BCE-4X / BCE ULTRA MAX / STEEVE-MAX

## Probleme Original
Reconstruction du depot HUNTIQ-V6 depuis HUNTIQ-V5 (branche bionic-v3-dev), mise en place d'un cadre de gouvernance strict (BCE-4X, MAX ULTRA, STEEVE-MAX), audits complets, et restauration de fonctionnalites perdues.

## Architecture
- Backend: FastAPI (85 modules dans /backend/modules/)
- Frontend: React (Craco, TailwindCSS)
- Base de donnees: MongoDB
- Branche de travail: Work1
- Gouvernance: BCE-4X / BCE ULTRA MAX / STEEVE-MAX

## Ce qui a ete accompli

### Phase 1-3 — Import et Certification (2026-03-22)
- Clone de bionic-v3-dev depuis HUNTIQ-V5
- Inventaire certifie (2426 fichiers, 469 dossiers)
- Archive ZIP certifiee

### Gouvernance (2026-03-22)
- README.md, GOVERNANCE.md, EMERGENT_PROTOCOL.md, SECURITY_POLICY.md

### Phase 4 — Audit Engines (2026-03-22)
- 84 modules verifies complets

### Phase 5B — Audit Coherence (2026-03-22)
- Matrice de coherence inter-modules, rapport de duplication

### Phase BSAA-0 & BSAA-1 (2026-03-22)
- Etude de faisabilite + architecture complete BIONIC Social Ads Automation

### Phase 5C — Audit Historique (2026-03-23)
- Clone et analyse V1-V4, identification du module manquant auto_optimization.py

### Phase 5C-R — Restauration optimization_engine (2026-03-23)
- Module optimization_engine cree (730 lignes, 13 endpoints)
- Enregistre dans CORE_ROUTERS (85 modules total)
- 3 livrables produits, commit Work1: 8b0cbfc1
- VALIDE PAR STEEVE

### Montage Preview V6 (2026-03-23)
- Backend/frontend V6 montes dans l'environnement de preview
- URL: https://huntiq-restore.preview.emergentagent.com
- Pages validees: Home, Dashboard, Shop, API Docs
- Guide d'execution locale: documentation/run_local_guide.md
- Commit Work1: 81f27162

## Preview URL
https://huntiq-restore.preview.emergentagent.com

## Backlog Priorise

### P0 — En attente
- Validation visuelle Steeve du preview V6

### P1 — A venir
- Phase BSAA-2: Implementation du module BIONIC Social Ads Automation

### P2 — Futur
- Merge Work1 vers main (apres validation complete)
- Nettoyage /app/audit_historical/
