# HUNTIQ-V6 — Product Requirements Document
## BCE-4X / STEEVE-MAX V6

---

## Enonce original
Reconstruction et modernisation de la plateforme HUNTIQ-V6 sous gouvernance stricte BCE-4X / MAX ULTRA / STEEVE-MAX. Application full-stack (FastAPI + React) pour la chasse intelligente avec analyse de territoire, nutrition animale, e-commerce de produits salines, et administration centralisee.

## Architecture
- **Backend**: FastAPI, 84+ modules "engines"
- **Frontend**: React, Zustand, React-Leaflet, Tailwind
- **E-commerce**: Stripe via emergentintegrations
- **Gouvernance UI**: BCE4X_UIShield (PositionLock, RenderGuard, ZIndexGuard, LayoutFreeze)
- **Branche de travail**: `Work1`

---

## Ce qui a ete implemente

### Phase P0 — Fusion Totale (27 Mars 2026)

#### SUPRA v2 — Moteur Unifie
- Fusion SUPRA LOCAL + NUTRITION INTELLIGENCE ULTRA + SUPRA PREMIUM
- Gauge SVG animee (7 moteurs ULTRA)
- 4 Info Cards (Sol, Metabolisme, Vegetation, Hydrologie)
- Narration SUPRA PREMIUM (Physiologie, Support, Comportement)
- Panier Stripe reel dans onglet COMMANDEZ
- Session unifiee `saline_session_id`
- Checkout Stripe reel
- Routes /saline, /saline-intelligence, /nutrition-intelligence → Redirect

#### MAGASIN v2 — E-commerce Unifie
- ShopPage reecrit — Catalogue SALINE_PRODUCTS via API
- ProductPage reecrit — Fiche produit SALINE via API
- Filtres par format, espece, recherche textuelle
- Boutons CMD connectes au panier saline Stripe
- CartSheet unifie dans App.js

#### ADMIN v2 — Gouvernance Centrale
- AdminPremiumPage absorbe AdminPage
- Nouvelles sections: Moteurs SUPRA + Catalogue Produits
- Route /admin → Redirect vers /admin-premium
- Navigation simplifie: lien unique ADMIN v2

#### Nettoyage Technique
- Suppression import Trash2 inutilise
- Suppression liens navigation "Nutrition"
- Unification liens admin (un seul lien)
- Panier generique → Panier saline unifie
- Fetch produits unifie sur API saline

### Phases precedentes (deja completees)
- Score Header securise + BCE4X_UIShield
- Weather Engine v3 unifie
- Navigation restructuree (ANALYSE TERRITOIRE, CARTE INTERACTIVE)
- Audits SUPRA vs ULTRA, MAGASIN, ADMIN
- Architecture BSAA
- Import V5 → V6, gouvernance, branch Work1

---

## Backlog

### P0 (Validation STEEVE-MAX requise)
- Validation visuelle de SUPRA v2 sur la carte (clic point → panneau)

### P1
- Nettoyage V5: Suppression fichiers obsoletes (NutritionIntelligencePage.jsx, AdminPage.jsx, etc.)
- Enrichissement catalogue via API x6030 (prix dynamiques, stock, variantes)

### P2
- BSAA-2: Implementation module BIONIC Social Ads Automation (GELE)

### P3
- Merge Work1 → main (INTERDIT sans validation STEEVE-MAX)

---

*Document mis a jour le 27 Mars 2026 — BCE-4X / STEEVE-MAX V6*
