# PRD — HUNTIQ BIONIC OS
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

---

## Enonce du probleme original

Reconstruction du repository HUNTIQ-V6, implementation de l'architecture modulaire
BIONIC OS avec 82+ engines decouples, gouvernance BCE-4X stricte, et implementation
sequentielle de pipelines inter-modules incluant Cart V2 e-commerce.

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
- Phase I (SUPRA): supra_bridge.py, strategy_recommender.py
- Phase II (E-Commerce): upsell_notifier.py
- Phase III (Marketing): tracking_bridge.py, analytics_feed.py
- Phase IV (Territoire): Fix hunting_trip_logger

### Session actuelle — 2026-02-07
- **Phase V (Tests Integration)** : 33/33 PASSED
- **P5-OPTIMIZATION Cart V2 — Phases A/B/C** : 12 nouveaux endpoints, 58/58 tests PASSED
  - P5-A: CRUD panier (get, add, update, remove, clear, summary)
  - P5-B: Validation, promotions, checkout
  - P5-C: Sync freemium, suggestions upsell
  - 5 fichiers services crees, 2 fichiers tests crees
  - 2 collections MongoDB (carts, cart_promotions)
  - V1 non-regression confirmee

---

## Backlog priorise

### P0 — Immediat
- [x] Phase V — Tests integration (33/33)
- [x] P5-OPTIMIZATION Plan genere
- [x] P5-A/B/C Backend implemente (58/58 tests)
- [ ] P5-D Frontend (5 composants React) — EN ATTENTE validation STEEVE-MAX
- [ ] Validation STEEVE-MAX

### P1 — Prochain
- [ ] P5-D: Frontend Cart UI (CartPanel, CartItem, CartSummary, CartBadge, PromoInput)
- [ ] P5-E: Tests integration finaux

### P2 — Futur
- [ ] BSAA-2 Implementation
- [ ] Soil Engine V2
- [ ] EASYlead Analytics (x5100)
- [ ] Merge Work1 → main (INTERDIT)

---

## Stack technique

- Backend: FastAPI, 82+ modules
- Frontend: React 19
- BDD: MongoDB (Motor async)
- Paiements: Stripe
- Tests: pytest 9.0.2 + httpx 0.28.1

---

**Derniere mise a jour** : 2026-02-07
