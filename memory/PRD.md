# HUNTIQ-V6 — PRD (Product Requirements Document)
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Problème Original

STEEVE-MAX dirige la reconstruction et l'évolution du projet HUNTIQ-V6, une plateforme de chasse intelligente au Québec. Le projet suit un protocole de gouvernance strict (BCE-4X, MAX ULTRA, STEEVE-MAX) avec politique ZÉRO PERTE, ZÉRO RÉGRESSION.

## 2. Utilisateur Principal

- **STEEVE-MAX** — Autorité suprême, chasseur expert, directeur technique
- Langue: Français
- Région: Québec, Canada

## 3. Architecture

- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de données:** MongoDB
- **APIs externes:** Open-Meteo (météo), Overpass API (OSM terrain/sentiers)
- **Branche active:** `STEEVE-MAX-x3200-V6-CORE` (EXCLUSIVEMENT)

## 4. Fonctionnalités Implémentées

### 4.1 Moteurs Backend (84+ modules)
- `access_engine_v6` — Routage terrain A*/Dijkstra, sentiers réels x0.1
- `access_clarity_engine_v7` — Pipeline lissage + TCS 6 composantes
- `bionic_stand_recommendation_engine` — Recommandation affûts
- `hunt_orchestrator` — Orchestrateur chasse + clarity_v7 intégré
- `terrain_nav` — Navigation terrain graphe
- `zone_engine_core_v2` — Zones bionic 15 couches
- `weather_v3` — Météo + score chasse SUPRA

### 4.2 Frontend
- `TerritoireHeader.jsx` — Header V6+ (SCORE CHASSE synchronisé + météo source unique)
- `StandsMapLayer.jsx` — Carte affûts + légende GOLDEN v2.0 + rendu clarity v7
- `BionicMapSelector.jsx` — 12 fonds de carte (5 standard + 7 HF) dans MAP TYPE officiel
- `WeatherPanel.jsx` — METEO BIONIC (source officielle)
- Panneau "CARTES HF" autonome — **SUPPRIMÉ** (fusionné dans MAP TYPE)

### 4.3 access_clarity_engine_v7 (2026-03-29)
- `smoother.py` — Zigzag removal + Douglas-Peucker + Catmull-Rom
- `scorer.py` — TCS: Alignement 30%, Lissage 20%, Pénétrabilité 15%, Topo LIDAR 15%, Hydro 10%, Effort 10%
- `clarity_engine.py` — Pipeline complet + auto-correction + rendu bleu-clair
- `router.py` — `/api/v7/clarity/{compute|score|status}`
- Tests: **11/11 passés**

### 4.4 Harmonisation UI (2026-03-29)
- SCORE V1-V5 supprimé → SCORE CHASSE V6+ (SUPRA/V6)
- Météo header synchronisée (source unique `sharedWeather`)
- 7 cartes HF fusionnées dans MAP TYPE officiel
- Health check système certifié

## 5. Documents Produits

| Document | Type | Date |
|----------|------|------|
| `architecture/access_clarity_engine_v7_architecture.md` | Architecture | 2026-03-29 |
| `architecture/saline_module_ULTIME_architecture.md` | Architecture | 2026-03-29 |
| `architecture/carte_hf_fusion.md` | Architecture | 2026-03-29 |
| `audit/post_purge_integrity_check.md` | Audit | 2026-03-29 |
| `audit/ui_header_meteo_harmonisation.md` | Audit | 2026-03-29 |
| `audit/carte_hf_integration_certification.md` | Audit | 2026-03-29 |
| `healthcheck/system_integrity_report.md` | Health Check | 2026-03-29 |

## 6. Backlog Prioritisé

### P0 (Critique) — COMPLÉTÉ
- [x] access_clarity_engine_v7 complet
- [x] Cartes HF intégrées dans MAP TYPE officiel
- [x] Audit post-purge
- [x] Architecture Salines ULTIME
- [x] Purge V1-V5 header
- [x] Harmonisation météo source unique
- [x] Fusion cartes HF (panneau autonome supprimé)
- [x] Health check système

### P1 (Important — À venir)
- [ ] ULTRA-MAX++ Firewall (Phase C) — Geo-fencing urbain Shapely
- [ ] Preuves visuelles multi-scénarios avant/après chemins v7
- [ ] Implémentation module Salines BIONIC ULTIME

### P2 (GELÉ)
- [ ] Purge frontend `shadcn`/`utils`
- [ ] Pression historique chasse dans `choix_affuts`
- [ ] Phase BSAA-2 (Social Ads)
- [ ] Merge vers `main` — STRICTEMENT INTERDIT

## 7. Contraintes
- Légende: DOM pur (PAS L.control)
- Sentiers OSM: x0.1 trails, x3.0 hors-sentier
- ZÉRO référence V1-V5
- Branche EXCLUSIVE: `STEEVE-MAX-x3200-V6-CORE`
- UN SEUL fond de carte actif, couches SUPRA/V6 superposables
