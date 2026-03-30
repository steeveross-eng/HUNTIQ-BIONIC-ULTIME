# HUNTIQ-V6 — PRD (Product Requirements Document)
## BCE-4X / STEEVE-MAX V6 — PROTOCOLE GOLDEN

---

## Probleme Original
Application HUNTIQ V6 — Plateforme avancee de chasse avec modules territoire, nutrition, scoring, IA, salines, meteo, shop, admin premium. Architecture modulaire FastAPI + React. Gouvernance stricte BCE-4X / STEEVE-MAX / GOLDEN.

## Architecture
- **Backend:** FastAPI, MongoDB, 84+ modules engines
- **Frontend:** React, Tailwind CSS, shadcn/ui, Leaflet
- **Integrations:** Stripe, Shapely, Leaflet, Open-Meteo
- **Branch:** STEEVE-MAX-x3200-V6-CORE (MERGE MAIN INTERDIT)

---

## What's Been Implemented

### Session 2 — Feb 2026 (CURRENT)

1. **SUPRA v2 — 5/5 Sous-tableaux en 3 Colonnes GOLDEN** (P0 - DONE)
   - **ANALYSE**: Col1 (Score+Gauge+Ecozone+Besoins) | Col2 (Sol+Metabolisme+Vegetation+Hydrologie) | Col3 (Mineraux+Recette+Couts) + PREMIUM collapsibles pleine largeur
   - **FICHE**: Col1 (Logistique+Gros Males) | Col2 (Strategique+Cout/ROI+TCS) | Col3 (Plan Gros Males+ROI+Sources)
   - **INTELLIGENCE**: 3 colonnes de produits avec scores, tags, CMD buttons, mini-bars
   - **COMPAREZ**: 3 colonnes cote-a-cote avec MEILLEUR CHOIX, mini-bars comparatives
   - **COMMANDEZ**: Col1 (Recette complete) | Col2 (Produits individuels) | Col3 (Panier Stripe)
   - Compact mode pour densite maximale, accent bars, icones en cercles, mini-bars 6px

2. **Marketing Engine V2 — PARTAGER** (P0 - DONE)
   - POST /api/share/track — Enrichi: auto-capture user_email + recipient_email + context
   - POST /api/share/capture-lead — Capture manuelle de leads marketing
   - GET /api/share/contacts — Liste contacts marketing (10 contacts auto-crees)
   - GET /api/share/marketing-stats — Stats enrichies (conversion, channels, sources)
   - Auto-creation contacts MongoDB (marketing_contacts + marketing_events)
   - Lead scoring, BCE-4X logs, Master Switch sync, Admin Premium integration

3. **STANDARD GOLDEN — Propagation Universelle** (P0 - DONE)
   - CSS variables Tailwind (--card: #1E293B, --border: transparent, --background: #0F172A)
   - CoreDashboard.jsx: GoldenCard, GCard, accent bars, zero bordure
   - AdminPremiumPage.jsx: Sidebar GOLDEN accent bar
   - App.css: Overrides globaux (borders, bg-slate, tabs active)
   - GoldenComponents.jsx: Composants partages universels
   - index.css: Variables CSS racine modifiees

### Session 1 — Previous
- Import/Archive V5 → V6, Governance BCE-4X, Branch Work1
- BSAA Architecture, Engine/Coherence/Historical Audits
- Removed BIONIC watermark, Fixed Map crash, Fixed Biology logic
- PARTAGER 13 canaux UI, SUPRA v2 base panel

---

## Prioritized Backlog

### P1 — Upcoming
- [ ] Verification rapport confirming GOLDEN + BCE-4X standards
- [ ] Commit all to STEEVE-MAX-x3200-V6-CORE branch

### P2 — Future / GELE
- [ ] Phase 2D: Purge frontend shadcn/utils
- [ ] Pression historique chasse → choix_affuts engine
- [ ] BSAA-2: Implementation Social Ads module
- [ ] auto_optimization.py restoration into optimization_engine
- [ ] Merge main — STRICTEMENT INTERDIT

---

## Key Endpoints (Marketing Engine V2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/share/track | Share event + auto-capture marketing |
| POST | /api/share/capture-lead | Manual lead capture |
| GET | /api/share/contacts | List marketing contacts |
| GET | /api/share/marketing-stats | Enriched marketing stats |
| GET | /api/share/stats | Share stats (Admin Premium) |
| GET | /api/share/status | Module + Master Switch + Marketing Engine status |
| GET | /api/share/master-switch | Master Switch state |
| PUT | /api/share/master-switch | Update Master Switch (STEEVE-MAX only) |

## Key DB Collections (MongoDB)
- marketing_contacts: Auto-created contacts (email, name, phone, source, score, channels, interactions)
- marketing_events: Marketing events (event_type, channel, data, timestamp, protocol)
- share_events: Share tracking events (channel, template, url, user/recipient info)

## Key Files Modified
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx — 5 tabs 3-col GOLDEN
- /app/frontend/src/components/territoire/ui/GoldenComponents.jsx — Shared GOLDEN components
- /app/frontend/src/modules/dashboard/CoreDashboard.jsx — Dashboard GOLDEN
- /app/frontend/src/pages/AdminPremiumPage.jsx — Admin sidebar GOLDEN
- /app/frontend/src/App.css — Global GOLDEN overrides
- /app/frontend/src/index.css — CSS variables GOLDEN
- /app/backend/modules/share_engine/router.py — Marketing Engine V2
