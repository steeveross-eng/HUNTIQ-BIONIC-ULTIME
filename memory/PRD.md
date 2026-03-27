# HUNTIQ-V6 — Product Requirements Document
## BCE-4X / STEEVE-MAX V6

---

## Enonce original
Reconstruction et modernisation HUNTIQ-V6 sous gouvernance BCE-4X / MAX ULTRA / STEEVE-MAX. Application full-stack (FastAPI + React) — chasse intelligente, analyse de territoire, nutrition animale, e-commerce salines, administration centralisee.

## Architecture
- **Backend**: FastAPI, 84+ modules "engines"
- **Frontend**: React, Zustand, React-Leaflet, Tailwind
- **E-commerce**: Stripe via emergentintegrations
- **Gouvernance UI**: BCE4X_UIShield
- **Branche**: `Work1`

---

## Implemente

### P0.5 — Corrections UX (27 Mars 2026)
- **Typographie Dashboard SUPRA**: Polices agrandies (+2px), padding augmente (+1-2), blocs harmonises, icones 18px, barres mineraux h-2, espacement sections gap-6
- **Chemins & Trails**: Approach paths courbes (sinusoidales composees, 16 points), distance reelle calculee (Haversine), trail_type=sentier_forestier, lignes continues vertes (suppression pointilles cyan)
- **Header UX**: MAGASIN blanc, PREMIUM blanc+contour orange #F5A623, CONNEXION unifie #F5A623

### Phase P0 — Fusion Totale (27 Mars 2026)
- SUPRA v2 — Moteur unifie (Gauge ULTRA + Info Cards + Narration PREMIUM + Panier Stripe)
- MAGASIN v2 — Catalogue SALINE_PRODUCTS unifie, filtres, CMD → Stripe
- ADMIN v2 — Interface unique (AdminPremiumPage absorbe AdminPage)
- Nettoyage: routes, navigation, panier unifie

### Phases precedentes
- Score Header securise + BCE4X_UIShield
- Weather Engine v3 unifie, Navigation restructuree
- Audits techniques (SUPRA, MAGASIN, ADMIN), Architecture BSAA

---

## Backlog

### P1
- Nettoyage V5: Suppression NutritionIntelligencePage.jsx, AdminPage.jsx, anciens composants ULTRA
- Enrichissement catalogue API x6030 (prix dynamiques, stock, variantes)

### P2
- BSAA-2: Social Ads Automation (GELE)

### P3
- Merge Work1 → main (INTERDIT sans validation)

---

*Mis a jour le 27 Mars 2026 — BCE-4X / STEEVE-MAX V6*
