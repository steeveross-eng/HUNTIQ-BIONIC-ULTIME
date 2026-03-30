# HUNTIQ-V6 — PRD (Product Requirements Document)
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Problème Original

STEEVE-MAX dirige la reconstruction et l'évolution du projet HUNTIQ-V6, une plateforme de chasse intelligente au Québec. Le projet suit un protocole de gouvernance strict (BCE-4X, MAX ULTRA, STEEVE-MAX) avec politique ZÉRO PERTE, ZÉRO RÉGRESSION.

## 2. Architecture

- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de données:** MongoDB
- **APIs externes:** Open-Meteo (météo), Overpass API (OSM terrain/sentiers)
- **Branche active:** `STEEVE-MAX-x3200-V6-CORE` (EXCLUSIVEMENT)

## 3. Fonctionnalités Implémentées

### 3.1 Backend Modules Actifs
- `access_clarity_engine_v7` — Lissage ×1000% + TCS 6 composantes + Modèle Québec
- `share_engine` — Module PARTAGER (tracking, stats, 8 canaux sociaux)
- `access_engine_v6` — Routage terrain A*/Dijkstra
- `weather_v3` — Météo + score chasse SUPRA
- 84+ modules au total

### 3.2 Frontend V6+ GOLDEN
- `TerritoireHeader.jsx` — Header V6+ (Score + Météo + PARTAGER)
- `ShareBionicButton.jsx` — 8 canaux, 3 templates, tracking Premium
- `BionicMapSelector.jsx` — 12 fonds de carte (5 std + 7 HF)
- `PinnablePanel.jsx` — Purgé de showPrint

### 3.3 Purge V1-V5 (2026-03-30)
- PRINT: SUPPRIMÉ (4 fichiers nettoyés)
- LIVE: SUPPRIMÉ (4 fichiers nettoyés)
- Confirmation: grep ZÉRO résultat

### 3.4 Optimisation ×1000% (2026-03-30)
- +3 phases: Fragmentation + Déviation + Passe-bas
- 5 points → 43 points, angle moyen 2.9°
- Modèle Québec: 7 types terrain avec pondérations

## 4. Documents GOVERNANCE

### GOVERNANCE.md v3.0 INSTITUTIONNELLE (2026-03-30)
- Section 1: Fondations BCE-4X
- Section 2: Module PARTAGER GOLDEN Standard
- Section 3: Normes GOLDEN Header V6+
- Section 4: Pipelines Externes
- Section 5: Scoring Ambassadeur GOLDEN
- Section 6: Optimisation ×1000% Clarity V7
- Section 7: Livrables Obligatoires
- Section 8: Annexes

### Audits de Certification
| Audit | Statut |
|-------|--------|
| governance_integration_certification.md | LIVRÉ |
| ui_header_v6_certification.md | LIVRÉ |
| pipelines_externes_certification.md | LIVRÉ |
| scoring_ambassadeur_certification.md | LIVRÉ |
| access_v7_optimization_certification.md | LIVRÉ |
| ui_header_share_button_certification.md | LIVRÉ |
| admin_premium_v2_share_ecosystem_audit.md | LIVRÉ |

## 5. Backlog

### P0 — COMPLÉTÉ
- [x] Purge PRINT+LIVE, Module PARTAGER, Optimisation ×1000%
- [x] GOVERNANCE.md v3.0 institutionnelle
- [x] 7 audits de certification

### P1 — À venir
- [ ] ULTRA-MAX++ Firewall (Phase C) — Geo-fencing urbain
- [ ] Module Salines BIONIC ULTIME
- [ ] Preuves visuelles multi-scénarios (forêt dense, ouverte, hydro)

### P2 — GELÉ
- [ ] Purge frontend shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2 (Social Ads)
- [ ] Merge vers main — INTERDIT
