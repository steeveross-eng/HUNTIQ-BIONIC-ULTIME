# P5-OPTIMIZATION — PLAN D'OPTIMISATION E-COMMERCE CART V2
## Directive x5400-E — STEEVE-MAX
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-02-07 | Merge MAIN : STRICTEMENT INTERDIT
### Aucun code modifie tant que ce plan n'est pas valide

---

# TABLE DES MATIERES

1. [SYNTHESE EXECUTIVE](#1-synthese-executive)
2. [AUDIT CART V1 — ETAT ACTUEL](#2-audit-cart-v1)
3. [ARCHITECTURE CART V2](#3-architecture-cart-v2)
4. [PHASE P5-A — PANIER BACKEND](#4-phase-p5-a-panier-backend)
5. [PHASE P5-B — OPERATIONS AVANCEES](#5-phase-p5-b-operations-avancees)
6. [PHASE P5-C — SYNCHRONISATION INTER-MODULES](#6-phase-p5-c-synchronisation-inter-modules)
7. [PHASE P5-D — UX FRONTEND](#7-phase-p5-d-ux-frontend)
8. [PHASE P5-E — TESTS D'INTEGRATION](#8-phase-p5-e-tests-dintegration)
9. [SEQUENCE D'EXECUTION](#9-sequence-dexecution)
10. [RISQUES ET MITIGATIONS](#10-risques-et-mitigations)
11. [INVENTAIRE MODIFICATIONS](#11-inventaire-modifications)

---

# 1. SYNTHESE EXECUTIVE

## 1.1 Objectif

Le plan P5-OPTIMIZATION vise a implementer un systeme de panier e-commerce complet
et performant pour la plateforme HUNTIQ. Le Cart V2 remplace la logique d'achat direct
(one-shot checkout) par un panier persistant avec operations CRUD avancees, gestion
des quantites, synchronisation avec les modules freemium/upsell, et une experience
utilisateur fluide.

## 1.2 Perimetre

| Element | Cart V1 (actuel) | Cart V2 (cible) |
|---------|-----------------|-----------------|
| Modele d'achat | Checkout direct (1 package) | Panier multi-articles |
| Persistance | Aucune (session Stripe) | MongoDB + session utilisateur |
| Operations | Achat unique | Add, Update, Remove, Clear, Merge |
| Quantites | 1 seul article | Quantites variables par article |
| Synchronisation | Aucune | Freemium, Upsell, Inventory |
| UX | Bouton "Acheter" → Stripe | Panier visuel, resume, checkout |
| Promotions | Aucune | Codes promo, remises tier, bundles |
| Validation | Aucune | Stock, eligibilite, quotas |

## 1.3 Principes

| Principe | Application |
|----------|-------------|
| ZERO LOSS | Aucun endpoint existant supprime ou modifie |
| ZERO REGRESSION | Checkout Stripe V1 reste fonctionnel |
| ZERO INTERPRETATION | Implementation stricte de ce plan |
| Isolation | Cart V2 dans un service dedie, zero import direct entre routers |
| Backward Compatible | V1 checkout coexiste avec V2 cart pendant la transition |

## 1.4 Metriques globales

| Metrique | Valeur |
|----------|--------|
| Fichiers a CREER | 8 |
| Fichiers a MODIFIER | 3 |
| Endpoints a CREER | 12 |
| Tests a CREER | 2 fichiers |
| Collections MongoDB | 2 (carts, cart_promotions) |
| Endpoints existants preserves | 1701+ (ZERO LOSS) |

---

# 2. AUDIT CART V1

## 2.1 Etat actuel du flux d'achat

### Flux V1 actuel

```
Utilisateur → Selectionne package → POST /payments/create-checkout-session
    → Stripe Session creee → Redirect Stripe
    → Webhook checkout.session.completed
    → _process_successful_payment() → Mise a jour tier utilisateur
```

### Endpoints existants (payment_engine)

| Endpoint | Methode | Fonction |
|----------|---------|----------|
| /api/v1/payments/ | GET | Info module |
| /api/v1/payments/packages | GET | Liste packages |
| /api/v1/payments/create-checkout-session | POST | Cree session Stripe |
| /api/v1/payments/webhook | POST | Traite webhooks Stripe |
| /api/v1/payments/status/{user_id} | GET | Statut paiement |

### Limitations V1

1. **Pas de panier** : achat direct d'un seul package
2. **Pas de persistance** : aucune trace cote serveur avant checkout
3. **Pas de quantites** : 1 article = 1 achat
4. **Pas de promotions** : prix fixe
5. **Pas de validation** : aucune verification d'eligibilite pre-checkout
6. **Pas de synchronisation** : upsell_notifier et freemium sont deconnectes du flux d'achat

---

# 3. ARCHITECTURE CART V2

## 3.1 Schema global

```
                        ┌─────────────────────┐
                        │   FRONTEND CART UI   │
                        │ (CartPanel.jsx)      │
                        └──────────┬──────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │  CART ENGINE (cart_engine/)   │
                    │  router.py — 12 endpoints    │
                    │  services/                   │
                    │    cart_service.py            │
                    │    cart_validator.py          │
                    │    cart_promotions.py         │
                    └──────┬───────┬───────┬───────┘
                           │       │       │
                   ┌───────┘       │       └───────┐
                   ▼               ▼               ▼
          ┌────────────┐  ┌────────────┐  ┌────────────────┐
          │  MongoDB    │  │ freemium   │  │ upsell         │
          │ carts       │  │ (quotas)   │  │ (notifications)│
          │ cart_promos  │  │ via bridge │  │ via bridge     │
          └────────────┘  └────────────┘  └────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  payment_engine  │
                        │  (Stripe V1)     │
                        │  INCHANGE        │
                        └─────────────────┘
```

## 3.2 Collection MongoDB : carts

```json
{
  "cart_id": "uuid-v4",
  "user_id": "string",
  "status": "active | merged | checked_out | abandoned",
  "items": [
    {
      "item_id": "uuid-v4",
      "product_type": "package | addon | feature",
      "product_id": "string",
      "name": "string",
      "description": "string",
      "quantity": 1,
      "unit_price": 0.00,
      "currency": "CAD",
      "metadata": {}
    }
  ],
  "promotions_applied": [
    {
      "promo_code": "string",
      "discount_type": "percentage | fixed",
      "discount_value": 0,
      "applied_to": "cart | item_id"
    }
  ],
  "subtotal": 0.00,
  "discount_total": 0.00,
  "total": 0.00,
  "currency": "CAD",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "expires_at": "ISO8601 (24h apres creation)"
}
```

## 3.3 Collection MongoDB : cart_promotions

```json
{
  "promo_code": "string (unique)",
  "discount_type": "percentage | fixed",
  "discount_value": 0,
  "applicable_products": ["product_id1", "product_id2"],
  "min_cart_total": 0.00,
  "max_uses": 0,
  "current_uses": 0,
  "valid_from": "ISO8601",
  "valid_until": "ISO8601",
  "status": "active | expired | depleted",
  "created_at": "ISO8601"
}
```

---

# 4. PHASE P5-A — PANIER BACKEND (CRUD)

## 4.1 Module a CREER : cart_engine

### Structure

```
/app/backend/modules/cart_engine/
    __init__.py
    router.py
    services/
        __init__.py
        cart_service.py
```

### 4.1.1 cart_service.py — Fonctions CRUD

| Fonction | Entree | Sortie | Description |
|----------|--------|--------|-------------|
| create_cart(user_id) | user_id | cart_id | Cree un panier vide avec expiration 24h |
| get_cart(user_id) | user_id | Cart | Recupere le panier actif (cree si absent) |
| add_item(user_id, item) | user_id, CartItem | Cart | Ajoute un article (merge si deja present) |
| update_quantity(user_id, item_id, qty) | user_id, item_id, int | Cart | Met a jour la quantite (supprime si 0) |
| remove_item(user_id, item_id) | user_id, item_id | Cart | Supprime un article |
| clear_cart(user_id) | user_id | confirmation | Vide le panier |
| get_cart_summary(user_id) | user_id | Summary | Resume avec totaux calcules |

### 4.1.2 router.py — Endpoints CRUD

| # | Methode | Endpoint | Fonction |
|---|---------|----------|----------|
| 1 | GET | /api/v1/cart/{user_id} | Recuperer le panier actif |
| 2 | POST | /api/v1/cart/{user_id}/items | Ajouter un article |
| 3 | PATCH | /api/v1/cart/{user_id}/items/{item_id} | Modifier quantite |
| 4 | DELETE | /api/v1/cart/{user_id}/items/{item_id} | Supprimer un article |
| 5 | DELETE | /api/v1/cart/{user_id}/clear | Vider le panier |
| 6 | GET | /api/v1/cart/{user_id}/summary | Resume du panier |

**Endpoints crees** : 6
**Risque** : FAIBLE (module nouveau, aucune modification d'existant)

---

# 5. PHASE P5-B — OPERATIONS AVANCEES

## 5.1 Validation pre-checkout

### Fichier a CREER : cart_engine/services/cart_validator.py

| Fonction | Description |
|----------|-------------|
| validate_cart(cart) | Verifie eligibilite, quotas, disponibilite |
| check_tier_eligibility(user_id, items) | Verifie que l'utilisateur peut acheter les items |
| check_promotion_validity(promo_code) | Verifie que la promotion est valide |
| compute_totals(cart) | Recalcule subtotal, discounts, total |

### 5.2 Promotions

### Fichier a CREER : cart_engine/services/cart_promotions.py

| Fonction | Description |
|----------|-------------|
| apply_promotion(user_id, promo_code) | Applique un code promo au panier |
| remove_promotion(user_id, promo_code) | Retire un code promo |
| validate_promo_code(code) | Verifie validite, usages restants |
| create_promotion(promo_data) | Admin: cree une promotion |

### 5.3 Endpoints supplementaires

| # | Methode | Endpoint | Phase | Fonction |
|---|---------|----------|-------|----------|
| 7 | POST | /api/v1/cart/{user_id}/validate | P5-B | Validation pre-checkout |
| 8 | POST | /api/v1/cart/{user_id}/promotions | P5-B | Appliquer promo |
| 9 | DELETE | /api/v1/cart/{user_id}/promotions/{code} | P5-B | Retirer promo |
| 10 | POST | /api/v1/cart/{user_id}/checkout | P5-B | Initier checkout Stripe |

**Endpoints crees** : 4
**Risque** : FAIBLE (le checkout V2 cree une session Stripe en interne, sans modifier le flux V1)

---

# 6. PHASE P5-C — SYNCHRONISATION INTER-MODULES

## 6.1 Bridges via MongoDB (ZERO couplage direct)

### Fichier a CREER : cart_engine/services/cart_sync_bridge.py

| Fonction | Source | Destination | Methode |
|----------|--------|-------------|---------|
| notify_cart_checkout(user_id, cart) | cart_engine | payment_engine | MongoDB: orders |
| notify_tier_upgrade(user_id, new_tier) | payment_engine | cart_engine | MongoDB: carts (recalcul) |
| sync_upsell_suggestions(user_id) | cart_engine | upsell_engine | MongoDB: upsell_events |
| sync_freemium_quotas(user_id) | cart_engine | freemium_engine | MongoDB: lecture quotas |

### 6.2 Endpoints synchronisation

| # | Methode | Endpoint | Fonction |
|---|---------|----------|----------|
| 11 | POST | /api/v1/cart/{user_id}/sync | Synchroniser panier avec quotas/tier |
| 12 | GET | /api/v1/cart/{user_id}/suggestions | Suggestions upsell basees sur le panier |

**Endpoints crees** : 2
**Risque** : FAIBLE (communication via MongoDB uniquement)

---

# 7. PHASE P5-D — UX FRONTEND

## 7.1 Composants React a CREER

| Composant | Emplacement | Fonction |
|-----------|-------------|----------|
| CartPanel.jsx | src/components/cart/ | Panel lateral avec liste articles |
| CartItem.jsx | src/components/cart/ | Ligne article avec +/- quantite |
| CartSummary.jsx | src/components/cart/ | Resume totaux, promos, checkout |
| CartBadge.jsx | src/components/cart/ | Badge compteur dans la navbar |
| PromoInput.jsx | src/components/cart/ | Champ saisie code promo |

## 7.2 Flux UX cible

```
1. Utilisateur clique "Ajouter au panier" sur un package/addon
   → POST /api/v1/cart/{user_id}/items
   → CartBadge se met a jour (compteur)

2. Utilisateur ouvre le CartPanel
   → GET /api/v1/cart/{user_id}
   → Affichage liste articles avec quantites

3. Utilisateur modifie quantites (+/-)
   → PATCH /api/v1/cart/{user_id}/items/{item_id}
   → Recalcul total en temps reel

4. Utilisateur applique code promo
   → POST /api/v1/cart/{user_id}/promotions
   → Affichage remise

5. Utilisateur clique "Passer au paiement"
   → POST /api/v1/cart/{user_id}/validate (pre-check)
   → POST /api/v1/cart/{user_id}/checkout
   → Redirect Stripe
   → Webhook → Mise a jour tier + vidage panier
```

## 7.3 Principes UX

| Principe | Implementation |
|----------|---------------|
| Feedback instantane | Chaque action met a jour le panier sans reload |
| Persistance | Panier sauvegarde en BDD, retrouve apres deconnexion |
| Accessibilite | Labels ARIA, navigation clavier |
| Responsive | Panel lateral desktop, plein ecran mobile |
| Error states | Messages d'erreur clairs pour quotas, promos invalides |

---

# 8. PHASE P5-E — TESTS D'INTEGRATION

## 8.1 Tests backend

| # | Fichier | Couverture |
|---|---------|------------|
| T5 | test_cart_crud.py | CRUD panier : create, add, update, remove, clear |
| T6 | test_cart_checkout_flow.py | Validation, promo, checkout, sync |

## 8.2 Strategie de test

| Type | Methode | Objectif |
|------|---------|----------|
| Unitaire | pytest direct | Valider chaque service individuellement |
| Integration | pytest + httpx | Flux complet add → promo → validate → checkout |
| Non-regression | Endpoints V1 | Verifier que checkout direct Stripe fonctionne encore |

---

# 9. SEQUENCE D'EXECUTION

## 9.1 Ordre strict

```
PHASE P5-A — PANIER CRUD                   [PRIORITE 1]
    |
    +--→ cart_service.py (6 fonctions CRUD)
    +--→ router.py (6 endpoints)
    +--→ Tests CRUD rapides (curl)
    +--→ VALIDATION STEEVE-MAX
    |
PHASE P5-B — OPERATIONS AVANCEES           [PRIORITE 2]
    |
    +--→ cart_validator.py (4 fonctions)
    +--→ cart_promotions.py (4 fonctions)
    +--→ router.py (+4 endpoints)
    +--→ Tests validation + promo (curl)
    +--→ VALIDATION STEEVE-MAX
    |
PHASE P5-C — SYNCHRONISATION               [PRIORITE 3]
    |
    +--→ cart_sync_bridge.py (4 fonctions)
    +--→ router.py (+2 endpoints)
    +--→ Tests sync (curl)
    +--→ VALIDATION STEEVE-MAX
    |
PHASE P5-D — UX FRONTEND                   [PRIORITE 4]
    |
    +--→ 5 composants React
    +--→ Integration visuelle
    +--→ VALIDATION STEEVE-MAX
    |
PHASE P5-E — TESTS D'INTEGRATION           [OBLIGATOIRE]
    |
    +--→ test_cart_crud.py
    +--→ test_cart_checkout_flow.py
    +--→ Non-regression V1 (endpoints existants)
    +--→ RAPPORT FINAL
```

## 9.2 Estimation

| Phase | Fichiers crees | Fichiers modifies | Endpoints | Lignes de code |
|-------|---------------|-------------------|-----------|----------------|
| P5-A | 3 | 0 | 6 | ~200 |
| P5-B | 2 | 1 (router) | 4 | ~180 |
| P5-C | 1 | 1 (router) | 2 | ~100 |
| P5-D | 5 | 2 (App.jsx, Navbar) | 0 | ~400 |
| P5-E | 2 | 0 | 0 | ~200 |
| **TOTAL** | **13** | **4** | **12** | **~1080** |

---

# 10. RISQUES ET MITIGATIONS

## 10.1 Risques identifies

| # | Risque | Probabilite | Impact | Mitigation |
|---|--------|-------------|--------|-----------|
| R1 | Regression checkout V1 | TRES FAIBLE | CRITIQUE | V1 reste inchange, V2 est un nouveau module |
| R2 | Panier expire non nettoye | FAIBLE | FAIBLE | TTL index MongoDB ou cron de nettoyage |
| R3 | Race condition sur quantites | FAIBLE | MODERE | Utiliser findOneAndUpdate atomique |
| R4 | Code promo utilise 2x | FAIBLE | MODERE | Increment atomique + validation pre-checkout |
| R5 | Desync panier/prix | MODERE | MODERE | Recalcul systematique des totaux a chaque operation |

## 10.2 Garanties architecturales

| Garantie | Mecanisme |
|----------|-----------|
| ZERO modification payment_engine | Cart V2 cree ses propres sessions Stripe |
| ZERO import direct router-to-router | Communication via MongoDB bridges |
| Backward compatible | Checkout V1 (direct) coexiste avec V2 (panier) |
| Rollback possible | Chaque phase est independante et reversible |

---

# 11. INVENTAIRE MODIFICATIONS

## 11.1 Fichiers a CREER (8 backend + 5 frontend)

| # | Fichier | Phase | Lignes |
|---|---------|-------|--------|
| 1 | modules/cart_engine/__init__.py | P5-A | ~5 |
| 2 | modules/cart_engine/router.py | P5-A/B/C | ~250 |
| 3 | modules/cart_engine/services/__init__.py | P5-A | ~5 |
| 4 | modules/cart_engine/services/cart_service.py | P5-A | ~150 |
| 5 | modules/cart_engine/services/cart_validator.py | P5-B | ~100 |
| 6 | modules/cart_engine/services/cart_promotions.py | P5-B | ~80 |
| 7 | modules/cart_engine/services/cart_sync_bridge.py | P5-C | ~100 |
| 8 | tests/integration/test_cart_crud.py | P5-E | ~100 |
| 9 | tests/integration/test_cart_checkout_flow.py | P5-E | ~100 |
| 10 | frontend/src/components/cart/CartPanel.jsx | P5-D | ~120 |
| 11 | frontend/src/components/cart/CartItem.jsx | P5-D | ~60 |
| 12 | frontend/src/components/cart/CartSummary.jsx | P5-D | ~80 |
| 13 | frontend/src/components/cart/CartBadge.jsx | P5-D | ~40 |
| 14 | frontend/src/components/cart/PromoInput.jsx | P5-D | ~60 |

## 11.2 Fichiers a MODIFIER (3)

| # | Fichier | Phase | Modification |
|---|---------|-------|-------------|
| 1 | modules/routers.py | P5-A | +include cart_engine router |
| 2 | frontend/src/App.jsx | P5-D | +import CartPanel |
| 3 | frontend/src/components/Navbar.jsx | P5-D | +CartBadge |

## 11.3 Collections MongoDB a CREER (2)

| # | Collection | Phase | Description |
|---|-----------|-------|-------------|
| 1 | carts | P5-A | Paniers utilisateurs |
| 2 | cart_promotions | P5-B | Codes promotionnels |

## 11.4 Endpoints a CREER (12)

| # | Methode | Endpoint | Phase |
|---|---------|----------|-------|
| 1 | GET | /api/v1/cart/{user_id} | P5-A |
| 2 | POST | /api/v1/cart/{user_id}/items | P5-A |
| 3 | PATCH | /api/v1/cart/{user_id}/items/{item_id} | P5-A |
| 4 | DELETE | /api/v1/cart/{user_id}/items/{item_id} | P5-A |
| 5 | DELETE | /api/v1/cart/{user_id}/clear | P5-A |
| 6 | GET | /api/v1/cart/{user_id}/summary | P5-A |
| 7 | POST | /api/v1/cart/{user_id}/validate | P5-B |
| 8 | POST | /api/v1/cart/{user_id}/promotions | P5-B |
| 9 | DELETE | /api/v1/cart/{user_id}/promotions/{code} | P5-B |
| 10 | POST | /api/v1/cart/{user_id}/checkout | P5-B |
| 11 | POST | /api/v1/cart/{user_id}/sync | P5-C |
| 12 | GET | /api/v1/cart/{user_id}/suggestions | P5-C |

## 11.5 Fichiers existants NON MODIFIES (confirmation ZERO LOSS)

Les fichiers suivants ne sont PAS modifies :
- payment_engine/router.py (V1 checkout inchange)
- freemium_engine/router.py
- upsell_engine/router.py
- Tous les 185+ fichiers de tests existants
- server.py
- Tous les services intermediaires des Phases I-IV
- core/ (aucune modification)

---

## PROCHAINES ETAPES

Ce plan requiert la **validation explicite de STEEVE-MAX** avant toute modification de code.

Apres validation, l'execution suivra la sequence definie en Section 9 :
P5-A (CRUD) → P5-B (Operations avancees) → P5-C (Sync) → P5-D (Frontend) → P5-E (Tests)

Chaque phase est independante et reversible. La validation STEEVE-MAX est requise entre chaque phase.

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : P5_OPTIMIZATION_PLAN 1.0.0
**References** : IMPLEMENTATION_PLAN_V1, E_COMMERCE_PIPELINE_V1
**Code modifie** : AUCUN (plan uniquement)
**Merge main** : STRICTEMENT INTERDIT
