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

### Correction Header UX (27 Mars 2026)
- MAGASIN: texte blanc (#FFFFFF), espacement droit (mr-3)
- PREMIUM: texte blanc, contour orange #F5A623 (2px), fond transparent
- CONNEXION: orange unifie #F5A623
- Gradient Premium supprime, couleur harmonisee

### Phase P0 — Fusion Totale (27 Mars 2026)
- SUPRA v2 — Moteur unifie (Gauge ULTRA + Info Cards + Narration PREMIUM + Panier Stripe)
- MAGASIN v2 — Catalogue SALINE_PRODUCTS unifie, filtres, CMD → Stripe
- ADMIN v2 — Interface unique (AdminPremiumPage absorbe AdminPage)
- Nettoyage: routes, navigation, panier unifie

### Phases precedentes
- Score Header securise + BCE4X_UIShield
- Weather Engine v3 unifie
- Navigation restructuree
- Audits techniques (SUPRA, MAGASIN, ADMIN)
- Architecture BSAA
- Import V5 → V6, gouvernance, branch Work1

---

## Backlog

### P0 (Validation STEEVE-MAX requise)
- Validation visuelle SUPRA v2 sur la carte (clic point → panneau)

### P1
- Nettoyage V5: Suppression fichiers obsoletes
- Enrichissement catalogue API x6030 (prix dynamiques, stock, variantes)

### P2
- BSAA-2: Social Ads Automation (GELE)

### P3
- Merge Work1 → main (INTERDIT sans validation)

---

*Document mis a jour le 27 Mars 2026 — BCE-4X / STEEVE-MAX V6*
