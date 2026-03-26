# HUNTIQ-V6 — PRD (Product Requirements Document)

## Probleme Original
Reconstruction, modernisation et stabilisation de la plateforme HUNTIQ-V6 sous gouvernance BCE-4X / MAX ULTRA dictee par STEEVE-MAX. Application full-stack (FastAPI/React) de chasse intelligente avec moteurs d'analyse territoriale, nutritionnelle et ecologique.

## Architecture
- **Backend**: FastAPI, 73+ modules, MongoDB, architecture pipeline (x5000-x7000)
- **Frontend**: React, TailwindCSS, React-Leaflet, Zustand stores
- **Branche active**: Work1

## Fonctionnalites Core
- Carte interactive TERRITOIRE (Leaflet, zones organiques, corridors A*)
- Panel SUPRA (nutrition intelligence, x5100-x7000)
- Moteurs d'analyse: qualite, conformite, solutions terrain, ecosysteme
- Pipeline admin x7000 (soumission fournisseur, MongoDB)
- Gouvernance BCE-4X avec audits et documentation
- Bloc meteo intelligent unifie (Open-Meteo fallback)

## Ce qui a ete implemente

### Session precedente
- Import et certification HUNTIQ-V6
- Gouvernance BCE-4X
- Architecture BSAA (BSAA-0, BSAA-1)
- Audits: moteur, coherence, historique V1-V6
- Phases 2Bbis, 3A, 3B, 3C, 3D, 3E: Moteurs x6010-x7000

### Session actuelle (2026-03-27)
- Directive 7P: Exclusions TERRITOIRE, Audit BCE-4X, Cartographie, Performance, BCE-4X-UI, MongoDB x7000
- Performance TERRITOIRE: 8.0s → 3.3s (-59%) via stale-while-revalidate
- Migration x7000 vers MongoDB (supplier_submissions)
- Suppression watermark Emergent
- Repositionnement widget VENT + Position Lock Guard
- **Bloc Meteo Intelligent** (useWeatherStore, useSharedWeather, WeatherPanel)
  - Source unique Zustand pour tous les modules
  - Backend OWM + fallback Open-Meteo
  - Synchronisation TerritoireHeader
  - Animation vent conservee

## Backlog Prioritise

### P1 (Prochaine iteration)
- Frontend admin x7000 (interface gestion soumissions fournisseurs)
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
