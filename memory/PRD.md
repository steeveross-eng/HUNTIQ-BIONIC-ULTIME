# HUNTIQ-V6 — PRD (Product Requirements Document)

## Probleme Original
Reconstruction, modernisation et stabilisation de la plateforme HUNTIQ-V6 sous gouvernance BCE-4X / MAX ULTRA dictee par STEEVE-MAX. Application full-stack (FastAPI/React) de chasse intelligente avec moteurs d'analyse territoriale, nutritionnelle et ecologique.

## Architecture
- **Backend**: FastAPI, 73+ modules, MongoDB, architecture pipeline (x5000-x7000)
- **Frontend**: React, TailwindCSS, React-Leaflet, Zustand-like hooks
- **Branche active**: Work1

## Fonctionnalites Core
- Carte interactive TERRITOIRE (Leaflet, zones organiques, corridors A*)
- Panel SUPRA (nutrition intelligence, x5100-x7000)
- Moteurs d'analyse: qualite, conformite, solutions terrain, ecosysteme
- Pipeline admin x7000 (soumission fournisseur → validation → activation)
- Gouvernance BCE-4X avec audits et documentation

## Ce qui a ete implemente

### Session precedente
- Import et certification HUNTIQ-V6
- Gouvernance BCE-4X (GOVERNANCE.md, EMERGENT_PROTOCOL.md, SECURITY_POLICY.md)
- Branche Work1
- Architecture BSAA (BSAA-0, BSAA-1)
- Audits: moteur, coherence, historique V1-V6
- Phase 3D: Typographie SUPRA (WCAG AA)
- Phases 2Bbis, 3A, 3B, 3C, 3E: Moteurs x6010-x7000

### Session actuelle (2026-03-27)
- **Partie 1**: Exclusions TERRITOIRE dans tests (conftest.py, pyproject.toml)
- **Partie 2**: Audit BCE-4X — cause racine regression Leaflet
- **Partie 3**: Cartographie architecture frontend (55 composants, 14 hooks)
- **Partie 4**: Diagnostic performance TERRITOIRE (8.0s → 3.3s)
- **Partie 5**: Optimisation performance:
  - Stale-while-revalidate pour Overpass
  - Parallelisation DEM + Overpass (asyncio.create_task)
  - Timeout Overpass reduit 12s → 5s
  - Cache TTL augmente 15min → 30min
  - Pre-chargement water cache au demarrage
- **Partie 6**: Boucliers BCE-4X-UI (LeafletShield HOC, z-index guard, render guard)
- **Partie 7**: Migration x7000 vers MongoDB (supplier_submissions collection)

## Backlog Prioritise

### P0 (Immediat)
- [DONE] Directive BCE-4X en 7 parties

### P1 (Prochaine iteration)
- Frontend admin x7000 (interface de gestion des soumissions)
- Frontend x6030 fiche produit ecosysteme
- Nettoyage modules V5 residuels

### P2 (Futur)
- Phase BSAA-2: Implementation module Social Ads Automation
- Frontend complet pour tous les moteurs x6010-x7000

### P3 (Bloque)
- Merge Work1 → main (INTERDIT sans validation STEEVE-MAX)

## Contraintes Techniques
- Test automatise INTERDIT sur module TERRITOIRE (Leaflet fragile)
- Tous les changements doivent etre sur branche Work1
- Validation STEEVE-MAX obligatoire avant merge
- BCE-4X: Zero Loss, Zero Regression
