# PRD — HUNTIQ BIONIC OS
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

---

## Enonce du probleme original

Reconstruction du repository HUNTIQ-V6, implementation de l'architecture modulaire
BIONIC OS avec 82+ engines decouples, gouvernance BCE-4X stricte, et implementation
sequentielle de pipelines inter-modules incluant Cart V2 e-commerce et MAP Intelligence.

## Personas utilisateurs

- **STEEVE-MAX** : Commandant — autorite supreme
- **Utilisateurs HUNTIQ** : Chasseurs utilisant la plateforme

## Exigences fondamentales

1. ZERO LOSS, ZERO REGRESSION, ZERO INTERPRETATION
2. Merge vers `main` STRICTEMENT INTERDIT sauf bypass explicite STEEVE-MAX
3. Validation STEEVE-MAX requise entre chaque phase

---

## Ce qui a ete implemente

### Sessions precedentes
- Import/certification HUNTIQ-V6, governance BCE-4X
- BSAA architecture, audits complets
- AUBO_V2.md, Pipeline architectures, IMPLEMENTATION_PLAN_V1
- Phase I (SUPRA), Phase II (E-Commerce), Phase III (Marketing), Phase IV (Territoire)

### Session actuelle — 2026-04-04

#### Directive x5400-G (P5-D/E)
- **P5-D Frontend Cart V2** : 5 composants React crees
  - CartPanel.jsx, CartItem.jsx, CartSummary.jsx, CartBadge.jsx, PromoInput.jsx
  - CartService.js upgraded (V2 methods, V1 preserved)
  - App.js updated (CartPanel V2 replaces CartSheet)
- **P5-E Tests Finaux** : 58/58 PASSED, ZERO REGRESSION

#### Directive x6400-A (MAP Intelligence Plan)
- **BIONIC_V6_MAP_INTELLIGENCE_PLAN.md** genere
  - M1: National Data Harvester + Legal Boundary (8 endpoints, 3 collections)
  - M2: BIONIC POI Graph (10 endpoints, 2 collections)
  - M3: Predictive Layer + Time-Series (9 endpoints, 3 collections)
  - M4: Adaptive User Profile + Navigation IA (11 endpoints, 2 collections)
  - M5: Offline Mode Ultra + Terrain & Species Intel (8 endpoints, 3 collections)
  - Total: 46 endpoints, 13 collections, 19 services, 10 fichiers tests

---

## Backlog priorise

### P0 — Immediat
- [x] P5-D Frontend Cart V2 (5 composants)
- [x] P5-E Tests finaux (58/58 PASSED)
- [x] BIONIC_V6_MAP_INTELLIGENCE_PLAN.md genere
- [ ] Validation STEEVE-MAX des delivrables x5400-G + x6400-A

### P1 — Prochain (apres validation)
- [ ] M1: National Data Harvester + Legal Boundary Engine
- [ ] M2: BIONIC POI Graph

### P2 — Futur
- [ ] M3: Predictive Layer + Time-Series Engine
- [ ] M4: Adaptive User Profile + Navigation IA
- [ ] M5: Offline Mode Ultra + Terrain & Species Intelligence
- [ ] BSAA-2 Implementation
- [ ] Merge Work1 → main (INTERDIT)

---

## Stack technique

- Backend: FastAPI, 82+ modules
- Frontend: React 19
- BDD: MongoDB (Motor async)
- Paiements: Stripe
- Tests: pytest 9.0.2 + httpx 0.28.1

---

**Derniere mise a jour** : 2026-04-04
