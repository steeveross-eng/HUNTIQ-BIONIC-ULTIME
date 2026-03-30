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

### Completed (Session Feb 2026)

1. **SUPRA v2 — Grille 3 Colonnes** (P0 - DONE)
   - Reconstruction complete de NutritionPointDetailPanel.jsx AnalyseTab
   - Structure grid-cols-3: Col1 (Score+Gauge+Ecozone+Besoins) | Col2 (Sol+Metabolisme+Vegetation+Hydrologie) | Col3 (Mineraux+Recette+Couts)
   - Compact mode pour densification dans colonnes etroites
   - PREMIUM collapsibles pleine largeur (Physiologie, Comportement, Support, Sources)
   - Accent bars, icones en cercles, mini-bars 6px, rounded-xl

2. **Marketing Engine V2 — PARTAGER** (P0 - DONE)
   - POST /api/share/track — Enrichi: auto-capture user_email + recipient_email + page_context + species + sal_id
   - POST /api/share/capture-lead — Capture manuelle de leads marketing
   - GET /api/share/contacts — Liste contacts marketing auto-crees (MongoDB)
   - GET /api/share/marketing-stats — Stats enrichies: channels, sources, conversion rate
   - Auto-creation contacts MongoDB (collection marketing_contacts + marketing_events)
   - Lead scoring (10 points auto-captured, 5 points phone-only)
   - Integration ADMIN Premium + Master Switch synchronisation
   - BCE-4X logs complets

3. **STANDARD GOLDEN — Propagation Universelle** (P0 - DONE)
   - CSS variables Tailwind mise a jour (--card: #1E293B, --border: transparent, --background: #0F172A)
   - CoreDashboard.jsx: Card/Badge/Tabs converti en GoldenCard/GCard (zero bordure, accent bars, icones cercles)
   - AdminPremiumPage.jsx: Sidebar GOLDEN (accent bar gauche, icone en cercle)
   - App.css: Overrides globaux (borders transparent, bg-slate-800 → #1E293B, tabs active → #f5a623)
   - GoldenComponents.jsx: Composants partages (GoldenCard, GoldenCollapsible, IconCircle, GoldenMiniBar, GoldenDataRow, GoldenBadge, GoldenScoreBox)

### Completed (Previous Sessions)
- Import/Archive V5 → V6
- Governance BCE-4X / STEEVE-MAX framework
- Branch Work1 / STEEVE-MAX-x3200-V6-CORE
- BSAA Module Architecture (Feasibility + Specs)
- Engine Audit, Coherence Audit, Historical Audit
- Removed BIONIC watermark
- Fixed Map crash
- Fixed Biology logic (Orignal vs Chevreuil)
- PARTAGER 13 canaux UI
- SUPRA v2 base panel

---

## Prioritized Backlog

### P1 — Upcoming
- [ ] Final verification report confirming GOLDEN + BCE-4X standards
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
- `marketing_contacts`: Auto-created contacts (email, name, phone, source, score, channels_used, interaction_count)
- `marketing_events`: All marketing events (event_type, channel, data, timestamp, protocol)
- `share_events`: Share tracking events (channel, template, url, user/recipient info)
