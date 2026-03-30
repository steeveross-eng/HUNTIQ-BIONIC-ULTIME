# HUNTIQ-V6 — PRD
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Architecture
- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de donnees:** MongoDB
- **Branche:** `STEEVE-MAX-x3200-V6-CORE`

## 2. Implemente (Session actuelle)
- Runtime Error (EcoforestryLayers.jsx BASE_MAPS fallback) — CORRIGE
- Bathymetrie + reference purge (EcoforestryLayers, mapSources, MonTerritoire) — FAIT
- LIDAR fallback satellite securise — CORRIGE
- Share Engine v2.0 + Master Switch OFF par defaut
- PARTAGER global (header App.js + panel SUPRA v2) sur 6/6 pages
- Logo BIONIC Premium v3 (140px accueil, 64px secondaires, ZERO hover/animation)
- ULTRA-MAX++ Firewall Shapely (7 zones Quebec, 5 endpoints, logs MongoDB)
- SALINES ULTIME backend (5 scores, 20 sources, FICHE)
- SALINES ULTIME Dashboard (onglet + compact overview, format vertical GOLDEN)
- FICHE SALINE integree dans panel SUPRA v2 (5eme onglet FICHE)
- Scroll GOLDEN sur TOUTES les pages (ZERO exclusions)
- GOVERNANCE.md v4.4.0

## 3. Modules Backend
- `ultra_max_firewall/` — POST /api/firewall/check, GET /zones, POST /zones, GET /status, GET /logs
- `salines_ultime_engine/` — POST|GET /api/v1/salines-ultime/fiche, GET /status

## 4. Audits Livres
- audit/non_conformite_v2_corrections.md (9 correctifs)
- audit/logo_bionic_golden_certification.md
- audit/ultra_max_pp_firewall_phaseC_execution.md
- audit/salines_ultime_execution.md
- audit/salines_ultime_dashboard_visual_certification.md
- audit/ui_header_global_share_button_certification.md

## 5. Backlog
### P2 — GELE
- [ ] Purge shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2
- [ ] Merge main — INTERDIT
