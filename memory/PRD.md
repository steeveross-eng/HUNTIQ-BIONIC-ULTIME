# HUNTIQ-V6 — PRD (Product Requirements Document)
## BCE-4X / STEEVE-MAX V6 — PROTOCOLE GOLDEN

---

## Probleme Original
Application HUNTIQ V6 — Plateforme avancee de chasse. Architecture modulaire FastAPI + React. Gouvernance stricte BCE-4X / STEEVE-MAX / GOLDEN.

## Architecture
- **Backend:** FastAPI, MongoDB, 84+ modules engines
- **Frontend:** React, Tailwind CSS, shadcn/ui, Leaflet
- **Integrations:** Stripe, Shapely, Leaflet, Open-Meteo
- **Branch:** STEEVE-MAX-x3200-V6-CORE (MERGE MAIN INTERDIT)

---

## What's Been Implemented

### Session 3 — Feb 30, 2026 (CURRENT)

1. **HYPERLIENS sous-criteres FICHE SALINE ULTIME** (P0 - DONE)
   - CriteriaDetailModal.jsx: modal fiche explicative pour 17+ sous-criteres
   - Chaque critere: titre complet (ZERO abbreviation), definition, methodologie scoring, justification score, facteurs influents, recommandations, seuils vert/jaune/rouge, sources
   - Base de donnees: accessibilite_vehicule, facilite_maintenance, proximite_infrastructure, securite_acces, frequence_visite, potentiel_trophee, corridors_deplacement, couvert_lateral, zone_transition, densite_population, position_vent, visibilite_affut, connectivite_territoire, cout_installation, cout_annuel, retour_investissement, drainage_sol, topographie_locale, clarte_terrain
   - CriteriaRow dans FicheTab: chaque sous-critere CLIQUABLE, hover underline dotted, icone Info

2. **PARTAGER — Reconstruction complete** (P0 - DONE)
   - ShareBionicButton.jsx reecrit: panneau absolute position au lieu de Popover
   - 14 canaux fonctionnels: Partage natif, Gmail, Outlook, Yahoo, Facebook, Messenger, WhatsApp, X, LinkedIn, Instagram, TikTok, SMS, Copier lien
   - 3 templates: Territoire / Premium / Viral
   - Master Switch integration + status fetch
   - Auto-capture marketing: page_context, user_email, user_id via localStorage
   - window.open pour chaque canal, navigator.share pour natif, clipboard pour copy/instagram/tiktok

### Session 2 — VALIDATED

1. **SUPRA v2 — 5/5 Sous-tableaux en 3 Colonnes GOLDEN** (VALIDATED)
2. **Marketing Engine V2 — PARTAGER Backend** (VALIDATED)
3. **STANDARD GOLDEN — Propagation Universelle** (VALIDATED)

### Session 1 — Previous
- Import/Archive V5 → V6, Governance BCE-4X, Branch Work1
- BSAA Architecture, Engine/Coherence/Historical Audits
- PARTAGER 13 canaux UI base, SUPRA v2 base panel

---

## Prioritized Backlog

### P1 — Upcoming
- [ ] Verification finale GOLDEN + BCE-4X standards
- [ ] Commit final STEEVE-MAX-x3200-V6-CORE

### P2 — Future / GELE
- [ ] Phase 2D: Purge frontend shadcn/utils
- [ ] Pression historique chasse → choix_affuts engine
- [ ] BSAA-2: Implementation Social Ads module
- [ ] auto_optimization.py restoration into optimization_engine
- [ ] Merge main — STRICTEMENT INTERDIT

---

## Key Files Modified (Session 3)
- /app/frontend/src/components/territoire/ui/CriteriaDetailModal.jsx — NEW: 17+ fiches explicatives
- /app/frontend/src/components/territoire/ui/ShareBionicButton.jsx — REWRITTEN: 14 canaux, absolute panel
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx — FicheTab CriteriaRow cliquables

## Key Endpoints (Marketing Engine V2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/share/track | Share event + auto-capture marketing |
| POST | /api/share/capture-lead | Manual lead capture |
| GET | /api/share/contacts | List marketing contacts (13 contacts) |
| GET | /api/share/marketing-stats | Stats: 12 shares, 13 events, 108% conversion |

## Key DB Collections (MongoDB)
- marketing_contacts: 13 contacts auto-crees (email, name, score, channels_used, interactions)
- marketing_events: 13 evenements (share_executed, lead_captured)
- share_events: 12 partages (gmail, facebook, whatsapp, linkedin, native)
