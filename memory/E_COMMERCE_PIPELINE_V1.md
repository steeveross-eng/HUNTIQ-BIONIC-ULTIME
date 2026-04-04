# E_COMMERCE_PIPELINE_V1 — SPECIFICATION PIPELINE E-COMMERCE BIONIC OS
## Directive x5310-STEEVE_MAX — Version 1.0.0
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-05 | Merge MAIN : STRICTEMENT INTERDIT
### Reference : AUBO_V2.md Section 2.2 + Domaine 1.4

---

# TABLE DES MATIERES

1. [VUE D'ENSEMBLE](#1-vue-densemble)
2. [FLUX PRINCIPAL](#2-flux-principal)
3. [MODULES — SPECIFICATION](#3-modules-specification)
4. [PIPELINE AFFILIATION](#4-pipeline-affiliation)
5. [PIPELINE ABONNEMENTS](#5-pipeline-abonnements)
6. [INTEGRATION STRIPE](#6-integration-stripe)
7. [MODELES DE DONNEES](#7-modeles-de-donnees)
8. [ENDPOINTS API COMPLETS](#8-endpoints-api-complets)
9. [ETATS ET TRANSITIONS](#9-etats-et-transitions)
10. [VALIDATION BCE-4X](#10-validation-bce-4x)

---

# 1. VUE D'ENSEMBLE

## 1.1 Objectif

Le Pipeline E-Commerce orchestre le cycle complet de monetisation de BIONIC OS :
catalogue produits, panier, checkout Stripe, commandes, gestion fournisseurs/clients,
affiliation, abonnements freemium/premium/pro, et upsell.

## 1.2 Modules impliques (10)

| # | Module | Prefix API | Endpoints | Architecture |
|---|--------|-----------|-----------|--------------|
| 1 | products_engine | /api/v1/products | 13 | v1/ (router + models + service) |
| 2 | cart_engine | /api/v1/cart | 7 | v1/ (router + models + service) |
| 3 | orders_engine | /api/v1/orders | 9 | v1/ (router + models + service) |
| 4 | payment_engine | /api/v1/payments | 6 | router.py direct |
| 5 | suppliers_engine | /api/v1/suppliers | 7 | v1/ (router + models + service) |
| 6 | customers_engine | /api/v1/customers | 7 | v1/ (router + models + service) |
| 7 | affiliate_ads_engine | /api/v1/affiliate-ads | 24 | router.py direct |
| 8 | ad_spaces_engine | /api/v1/ad-spaces | 16 | router.py direct |
| 9 | freemium_engine | /api/v1/freemium | 8 | router.py direct |
| 10 | upsell_engine | /api/v1/upsell | 6 | router.py direct |

**Facade** : ads_engine (consolidation logique pour affiliate_ads_engine + ad_spaces_engine)

## 1.3 Collections MongoDB

| Collection | Module | Documents | Champs cles |
|-----------|--------|-----------|-------------|
| products | products_engine | 5 | id, name, brand, category, price, score, image_url |
| cart | cart_engine | 7 | id, product_id, quantity, session_id |
| orders | orders_engine | 0 | (schema defini, pas de commandes reelles) |
| supplier_submissions | suppliers_engine | 4 | submission_id, status, supplier, product |
| supplier_counters | suppliers_engine | 1 | seq |

---

# 2. FLUX PRINCIPAL

## 2.1 Parcours achat standard

```
[1. CATALOGUE]                         [2. PANIER]
products_engine                        cart_engine
GET /products → liste                  POST /cart → ajout item
GET /products/:id → detail             PUT /cart/:id → modifier quantite
POST /products/search → recherche      DELETE /cart/:id → retirer item
GET /products/top → meilleures ventes  GET /cart/session/:sid → contenu panier
GET /products/filters/options          DELETE /cart/session/:sid/clear → vider
    |                                      |
    v                                      v
[3. CHECKOUT]                          [4. CONFIRMATION]
payment_engine                         orders_engine
POST /payments/checkout/session        POST /orders → creation commande
    → Stripe Checkout Session              (declenche par webhook Stripe)
    → Redirect vers Stripe                 |
    |                                      v
    v                                  [5. SUIVI]
[STRIPE HOSTED CHECKOUT]              orders_engine
    |                                  GET /orders → historique
    +--→ SUCCESS → /payment/success    GET /orders/:id → detail
    +--→ CANCEL  → /payment/cancel     PUT /orders/:id → mise a jour statut
    |                                  POST /orders/:id/cancel → annulation
    v
[WEBHOOK]
POST /payments/webhook/stripe
    → checkout.session.completed
    → _process_successful_payment()
    → Upgrade tier dans users
```

## 2.2 Diagramme sequentiel

```
Utilisateur         Frontend           Backend              Stripe
    |                  |                  |                    |
    |  Selectionne     |                  |                    |
    |  produit         |                  |                    |
    +----------------->|                  |                    |
    |                  | GET /products/:id|                    |
    |                  +----------------->|                    |
    |                  |<----- product ---|                    |
    |                  |                  |                    |
    |  Ajoute au panier|                  |                    |
    +----------------->|                  |                    |
    |                  | POST /cart       |                    |
    |                  +----------------->|                    |
    |                  |<--- cart item ---|                    |
    |                  |                  |                    |
    |  Lance checkout  |                  |                    |
    +----------------->|                  |                    |
    |                  | POST /payments/  |                    |
    |                  | checkout/session |                    |
    |                  +----------------->|                    |
    |                  |                  | stripe.checkout.   |
    |                  |                  | sessions.create()  |
    |                  |                  +------------------->|
    |                  |                  |<-- checkout_url ---|
    |                  |<-- checkout_url -|                    |
    |                  |                  |                    |
    |  REDIRECT ------>| STRIPE CHECKOUT  |                    |
    |                  |                  |                    |
    |                  |                  |  webhook POST      |
    |                  |                  |  /payments/webhook |
    |                  |                  |<---  event --------|
    |                  |                  |                    |
    |                  |                  | _process_successful|
    |                  |                  | _payment()         |
    |                  |                  |                    |
    |  /payment/success|                  |                    |
    |<----- redirect --|                  |                    |
```

---

# 3. MODULES — SPECIFICATION

## 3.1 products_engine — Catalogue

**Prefix** : /api/v1/products | **Architecture** : v1/ (router, models, service)

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | /health | Health check |
| GET | /stats | Statistiques moteur |
| GET | / | Liste produits (filtrage, pagination) |
| GET | /top | Top produits (par score) |
| GET | /filters/options | Options de filtrage disponibles |
| GET | /:product_id | Detail produit |
| POST | / | Creer produit |
| PUT | /:product_id | Modifier produit |
| DELETE | /:product_id | Supprimer produit |
| POST | /search | Recherche avancee |
| POST | /:product_id/track/analyze | Tracker analyse produit |
| POST | /:product_id/track/compare | Tracker comparaison produit |

**Modele Product** : id, name, brand, category, subcategory, price, score, rank, image_url, description, ingredients, target_species, season, in_stock

---

## 3.2 cart_engine — Panier

**Prefix** : /api/v1/cart | **Architecture** : v1/ (router, models, service)

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | /health | Health check |
| GET | /stats | Statistiques |
| GET | /session/:session_id | Contenu panier par session |
| POST | / | Ajouter au panier |
| PUT | /:item_id | Modifier quantite |
| DELETE | /:item_id | Retirer item |
| DELETE | /session/:session_id/clear | Vider panier |

**Modele CartItem** : id, product_id, quantity, session_id

---

## 3.3 orders_engine — Commandes

**Prefix** : /api/v1/orders | **Architecture** : v1/ (router, models, service)

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | /health | Health check |
| GET | /stats | Statistiques |
| GET | / | Liste commandes (filtrage user_id) |
| GET | /:order_id | Detail commande |
| POST | / | Creer commande (via webhook Stripe) |
| PUT | /:order_id | Mettre a jour statut |
| POST | /:order_id/cancel | Annuler commande |

---

## 3.4 payment_engine — Paiements Stripe

**Prefix** : /api/v1/payments | **Architecture** : router.py direct

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | / | Info moteur |
| GET | /packages | Liste des forfaits disponibles |
| POST | /checkout/session | Creer session Stripe Checkout |
| GET | /checkout/status/:session_id | Verifier statut checkout |
| POST | /webhook/stripe | Webhook Stripe (events) |
| GET | /transactions/:user_id | Historique transactions |

**Forfaits** :

| Type | Nom | Prix | Devise | Tier | Duree |
|------|-----|------|--------|------|-------|
| premium_monthly | Premium Mensuel | 9.99 | CAD | premium | 30j |
| premium_yearly | Premium Annuel | 99.99 | CAD | premium | 365j |
| pro_monthly | Pro Mensuel | 19.99 | CAD | pro | 30j |
| pro_yearly | Pro Annuel | 199.99 | CAD | pro | 365j |

---

## 3.5 suppliers_engine — Fournisseurs

**Prefix** : /api/v1/suppliers | **Architecture** : v1/ (router, models, service)

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | /health | Health check |
| GET | /stats | Statistiques |
| GET | / | Liste fournisseurs |
| GET | /:supplier_id | Detail fournisseur |
| POST | / | Creer fournisseur |
| PUT | /:supplier_id | Modifier fournisseur |
| DELETE | /:supplier_id | Supprimer fournisseur |

**Pipeline validation fournisseur** : auto_validation + human_review → 4 statuts supplier_submissions

---

## 3.6 customers_engine — Clients

**Prefix** : /api/v1/customers | **Architecture** : v1/ (router, models, service)

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | /health | Health check |
| GET | /stats | Statistiques |
| GET | / | Liste clients |
| GET | /:customer_id | Detail client |
| GET | /session/:session_id | Client par session |
| POST | / | Creer client |
| PUT | /:customer_id | Modifier client |

---

# 4. PIPELINE AFFILIATION

## 4.1 Vue d'ensemble

Systeme d'affiliation a 3 niveaux pour les annonceurs sur la plateforme BIONIC OS.

```
[ANNONCEUR]
    |
    +---> affiliate_switch_engine — Gestion affilies + validation
    |         |
    |         +---> 5 etapes validation (AUTO, REVIEW, LEGAL, COMPLIANCE, FINAL)
    |         +---> Toggle activation/desactivation
    |         +---> Accord contrat
    |
    +---> affiliate_ads_engine — Opportunites publicitaires
    |         |
    |         +---> Creer opportunite (AUTO_AD, OUTREACH, PROPOSAL)
    |         +---> Packages (basic/standard/premium/enterprise)
    |         +---> Checkout + paiement
    |         +---> Deploiement automatique → calendrier marketing
    |         +---> Email offre SEO x300
    |
    +---> ad_spaces_engine — Espaces publicitaires
              |
              +---> Catalogue 6 emplacements par page
              +---> Reservation + activation slots
              +---> Categorie (premium/standard/contextual/native/sidebar/footer)
```

## 4.2 affiliate_ads_engine — Detail

**Prefix** : /api/v1/affiliate-ads | **24 endpoints**

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | / | Info module |
| POST | /opportunities/create | Creer opportunite publicitaire |
| GET | /opportunities | Liste opportunites |
| GET | /opportunities/:id | Detail opportunite |
| GET | /checkout/:token | Page checkout |
| POST | /checkout/:token/submit | Soumettre checkout |
| POST | /pay/:id | Traiter paiement |
| POST | /opportunities/:id/resend-email | Renvoyer email offre |
| + 16 | ... | Gestion creatives, analytics, reporting |

**Statuts opportunite** : DRAFT → SENT → VIEWED → ACCEPTED → PAID → ACTIVE → COMPLETED / EXPIRED / REJECTED

**Packages** :

| Package | Prix | Duree | Impressions |
|---------|------|-------|-------------|
| basic | 99$ | 7j | 5000 |
| standard | 249$ | 14j | 15000 |
| premium | 499$ | 30j | 50000 |
| enterprise | Sur mesure | Sur mesure | Illimite |

## 4.3 ad_spaces_engine — Espaces publicitaires

**Prefix** : /api/v1/ad-spaces | **16 endpoints**

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | / | Info module |
| GET | /catalog | Catalogue espaces |
| GET | /catalog/:space_id | Detail espace |
| GET | /catalog/by-category/:category | Espaces par categorie |
| GET | /catalog/by-page/:page | Espaces par page |
| POST | /slots/reserve | Reserver slot |
| POST | /slots/:id/activate | Activer slot |
| POST | /slots/:id/deactivate | Desactiver slot |
| + 8 | ... | Analytics, gestion, reporting |

**Categories** : premium, standard, contextual, native, sidebar, footer
**Priorites** : critical, high, medium, low

## 4.4 affiliate_switch_engine — Basculement

**Prefix** : /api/v1/affiliate-switch | **15 endpoints**

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | / | Info module |
| GET | /affiliates | Liste affilies |
| GET | /affiliates/:id | Detail affilie |
| POST | /affiliates | Creer affilie (5 etapes validation) |
| POST | /affiliates/:id/toggle | Basculer activation |
| POST | /affiliates/:id/revoke | Revoquer affilie |
| POST | /affiliates/:id/validate/:step | Valider etape |
| GET | /affiliates/:id/validation-status | Statut validation |
| POST | /affiliates/:id/agreement/confirm | Confirmer accord |
| + 6 | ... | Mode hybride, analytics |

**Etapes validation** : AUTO → REVIEW → LEGAL → COMPLIANCE → FINAL

---

# 5. PIPELINE ABONNEMENTS

## 5.1 Flux abonnement

```
[UTILISATEUR FREE]
    |
    +---> /pricing (PricingPage)
    |     freemium_engine → compare_tiers()
    |
    +---> [Selection plan] → payment_engine
    |     POST /payments/checkout/session
    |         package: premium_monthly | premium_yearly | pro_monthly | pro_yearly
    |
    +---> [Stripe Checkout] → Paiement
    |
    +---> [Webhook] → _process_successful_payment()
    |         |
    |         +---> users.subscription_tier = "premium" | "pro"
    |         +---> users.subscription_expires_at = now + duration_days
    |
    +---> [Post-upgrade]
          upsell_engine → check_trigger()
              |
              +---> Campagnes upsell actives
              +---> Conversion tracking
              +---> A/B testing
```

## 5.2 freemium_engine — Plans et quotas

**Prefix** : /api/v1/freemium | **8 endpoints**

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | / | Info moteur |
| GET | /subscription/:user_id | Abonnement actif |
| POST | /subscription/upgrade | Upgrader abonnement |
| GET | /quota/:user_id/:feature | Usage quota |
| POST | /quota/:user_id/:feature/increment | Incrementer quota |
| POST | /check-access | Verifier acces feature |
| GET | /tiers/compare | Comparaison des plans |

**Plans** :

| Plan | Analyses/jour | SUPRA | Rapports | Prix |
|------|--------------|-------|----------|------|
| Free | 3 | Non | Non | 0$ |
| Premium | Illimite | Oui | Oui | 9.99$/mois |
| Pro | Illimite | Oui + priorite | Oui + export | 19.99$/mois |

**Features gatees** : analysis, supra, reports, export, compare, multi_species, ai_recommendations

## 5.3 upsell_engine — Campagnes d'upsell

**Prefix** : /api/v1/upsell | **6 endpoints**

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | / | Info moteur |
| POST | /trigger | Verifier trigger (evenement utilisateur) |
| GET | /campaigns | Liste campagnes actives |
| POST | /campaigns/dismiss | Rejeter campagne |
| POST | /campaigns/click | Enregistrer clic |
| GET | /analytics | Analytics upsell (dernier N jours) |

**Types de trigger** : quota_reached, feature_blocked, session_count, time_based
**Types d'upsell** : modal, banner, inline, notification

---

# 6. INTEGRATION STRIPE

## 6.1 Configuration

```
Variable: STRIPE_API_KEY
Valeur: sk_test_emergent (mode test)
Devise: CAD (Dollar canadien)
Mode: Checkout Sessions (hosted)
```

## 6.2 Flux Stripe

```
1. Frontend appelle POST /api/v1/payments/checkout/session
       body: { user_id, package_type, success_url, cancel_url }

2. Backend cree Stripe Checkout Session:
       stripe.checkout.sessions.create(
           payment_method_types=["card"],
           line_items=[{
               price_data: { currency, product_data, unit_amount },
               quantity: 1
           }],
           mode="payment",
           success_url=success_url,
           cancel_url=cancel_url
       )

3. Backend retourne { checkout_url, session_id, status }

4. Frontend redirige vers checkout_url (Stripe hosted)

5. Utilisateur paie sur Stripe

6. Stripe envoie webhook POST /api/v1/payments/webhook/stripe
       event: checkout.session.completed

7. Backend execute _process_successful_payment():
       - Met a jour users.subscription_tier
       - Enregistre transaction
       - Notifie l'utilisateur
```

## 6.3 Statuts paiement

| Statut | Description |
|--------|-------------|
| initiated | Session creee, attente redirect |
| pending | Utilisateur sur Stripe, en cours |
| paid | Paiement confirme (webhook recu) |
| failed | Paiement echoue |
| expired | Session expiree |
| refunded | Remboursement effectue |

## 6.4 Securite Stripe

| Mesure | Implementation |
|--------|---------------|
| Montants server-side | PACKAGES definis cote serveur uniquement |
| Webhook signature | Verification signature Stripe (production) |
| Mode test | sk_test_emergent (pas de vrai paiement) |
| Fallback demo | Mode demo si Stripe indisponible |

---

# 7. MODELES DE DONNEES

## 7.1 Product

```python
Product {
    id: str                    # Identifiant unique
    name: str                  # Nom du produit
    brand: str                 # Marque
    category: str              # Categorie principale
    subcategory: str           # Sous-categorie
    price: float               # Prix en CAD
    score: float               # Score BIONIC (0-100)
    rank: int                  # Classement
    image_url: str             # URL image
    description: str           # Description
    ingredients: List[str]     # Ingredients/composants
    target_species: List[str]  # Especes ciblees
    season: str                # Saison recommandee
    in_stock: bool             # Disponibilite
}
```

## 7.2 CartItem

```python
CartItem {
    id: str                    # Identifiant unique
    product_id: str            # Reference produit
    quantity: int              # Quantite
    session_id: str            # Session utilisateur
}
```

## 7.3 Order

```python
Order {
    order_id: str              # Identifiant commande
    user_id: str               # Utilisateur
    items: List[OrderItem]     # Items commandes
    total: float               # Total en CAD
    status: OrderStatus        # Statut commande
    payment_id: str            # Reference paiement Stripe
    created_at: datetime       # Date creation
    updated_at: datetime       # Derniere mise a jour
}
```

## 7.4 AdOpportunity

```python
AdOpportunity {
    opportunity_id: str        # Identifiant
    supplier_id: str           # Annonceur
    type: AdOpportunityStatus  # AUTO_AD | OUTREACH | PROPOSAL
    package: AdPackage         # basic | standard | premium | enterprise
    placement: AdPlacement     # Emplacement sur la page
    creative: AdCreative       # Contenu publicitaire
    budget: float              # Budget
    status: str                # DRAFT → ACTIVE → COMPLETED
    metrics: dict              # Impressions, clics, conversions
}
```

## 7.5 UserSubscription

```python
UserSubscription {
    user_id: str               # Utilisateur
    tier: SubscriptionTier     # free | premium | pro
    expires_at: datetime       # Date expiration
    features: List[str]        # Features autorisees
    quota_remaining: dict      # Quotas restants par feature
}
```

---

# 8. ENDPOINTS API COMPLETS

## 8.1 Sommaire par module

| Module | GET | POST | PUT | DELETE | Total |
|--------|-----|------|-----|--------|-------|
| products_engine | 5 | 3 | 1 | 1 | 13* |
| cart_engine | 3 | 1 | 1 | 2 | 7 |
| orders_engine | 4 | 2 | 1 | 0 | 9* |
| payment_engine | 3 | 2 | 0 | 0 | 6* |
| suppliers_engine | 4 | 1 | 1 | 1 | 7 |
| customers_engine | 4 | 1 | 1 | 0 | 7* |
| affiliate_ads_engine | 4 | 6+ | 0 | 0 | 24 |
| ad_spaces_engine | 5 | 3+ | 0 | 0 | 16 |
| affiliate_switch_engine | 3 | 5+ | 0 | 0 | 15 |
| freemium_engine | 4 | 3 | 0 | 0 | 8* |
| upsell_engine | 2 | 3 | 0 | 0 | 6* |
| **TOTAL** | | | | | **118** |

(*) Includes health + stats endpoints

## 8.2 Pages frontend associees

| Page | Route | Modules consommes |
|------|-------|-------------------|
| ShopPage | /shop | products_engine, cart_engine |
| ProductPage | /product/:id | products_engine |
| PricingPage | /pricing | freemium_engine, payment_engine |
| PaymentSuccessPage | /payment/success | payment_engine |
| PaymentCancelPage | /payment/cancel | — |
| LandsRental | /lands | lands_rental.py |
| BusinessPage | /business | analytics, marketing |
| AdminPremiumPage | /admin-premium | admin_engine (sections paiement, freemium, upsell) |
| BsaaDashboardPage | /bsaa | bsaa (campagnes ads) |

---

# 9. ETATS ET TRANSITIONS

## 9.1 Cycle de vie commande

```
INITIATED → PENDING → PAID → SHIPPED → DELIVERED
                 |              |
                 v              v
              FAILED         CANCELLED
                 |
                 v
              EXPIRED
                              PAID → REFUNDED
```

## 9.2 Cycle de vie opportunite publicitaire

```
DRAFT → SENT → VIEWED → ACCEPTED → PAID → ACTIVE → COMPLETED
          |        |         |                          |
          v        v         v                          v
       EXPIRED  EXPIRED   REJECTED                   EXPIRED
```

## 9.3 Cycle de vie affilie

```
PENDING → AUTO_VALIDATED → REVIEW → LEGAL → COMPLIANCE → FINAL → ACTIVE
                                                                     |
                                                                     v
                                                                  REVOKED
```

## 9.4 Cycle de vie abonnement

```
FREE → CHECKOUT_INITIATED → PAID → PREMIUM/PRO → (expiration) → FREE
                 |                                    |
                 v                                    v
              CANCELLED                           RENEWED
```

---

# 10. VALIDATION BCE-4X

## 10.1 Regles de securite

| Regle | Description | Module |
|-------|-------------|--------|
| Prix server-side | Montants definis exclusivement cote serveur (PACKAGES dict) | payment_engine |
| Webhook verification | Signature Stripe verifiee (production) | payment_engine |
| Quota enforcement | Verification quotas avant chaque analyse | freemium_engine |
| Role-based access | Acces conditionne par subscription tier | roles_engine |

## 10.2 Conformite BCE-4X

| Contrainte | Application |
|-----------|-------------|
| ZERO LOSS | Aucune transaction perdue — webhook Stripe + fallback |
| ZERO REGRESSION | Montants et plans immutables sans validation STEEVE-MAX |
| ZERO INTERPRETATION | Execution stricte des forfaits definis |

## 10.3 Points de surveillance

| Point | Seuil | Action |
|-------|-------|--------|
| Webhook non recu | > 5 min apres checkout | Alert admin |
| Taux echec paiement | > 10% | Alert STEEVE-MAX |
| Quota depassement | 100% utilise | Trigger upsell |
| Affilie non valide | Etape COMPLIANCE echouee | Revocation auto |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : E_COMMERCE_PIPELINE_V1 1.0.0
**Reference** : AUBO_V2.md Section 2.2 + Domaine 1.4
**Modules documentes** : 10 (+ 1 facade)
**Endpoints documentes** : 118
**Integration externe** : Stripe (mode test sk_test_emergent)
**Merge main** : STRICTEMENT INTERDIT
