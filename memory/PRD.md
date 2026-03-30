# HUNTIQ-V6 — PRD (Product Requirements Document)
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Architecture
- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de données:** MongoDB
- **Branche active:** `STEEVE-MAX-x3200-V6-CORE` (EXCLUSIVEMENT)

## 2. Fonctionnalités Implémentées

### Share Engine v2.0 + Master Switch Premium (2026-03-30)
- 8 canaux: Native OS, Facebook, Messenger, WhatsApp, Instagram, TikTok, SMS, Copier
- Master Switch: ON permanent, override, authority STEEVE-MAX, 8/8 canaux
- Pipeline: ShareBionicButton → Master Switch gate → MongoDB share_events
- Admin sync: 9 modules ADMIN Premium connectés
- API: `/api/share/{track|stats|status|master-switch}`

### Clarity Engine v7 ×1000% (2026-03-30)
- +3 phases: fragmentation (80m), déviation naturelle, passe-bas
- Modèle Québec: 7 types terrain (sentier ×0.1 → non conforme ×10.0)
- TCS: 6 composantes, grades S→F

### Purge V1-V5 TOTALE (2026-03-30)
- PRINT bouton: SUPPRIMÉ (TerritoireHeader, PinnablePanel)
- LIVE bouton: SUPPRIMÉ (TerritoireHeader, MonTerritoireBionicPage)
- "Print." shortLabel: CORRIGÉ → "Printemps" (biologicalSeasons.js)
- Confirmation: grep ZÉRO résultat sur tout le codebase

### GOVERNANCE.md v3.0 INSTITUTIONNELLE (2026-03-30)
- 8 sections: BCE-4X, PARTAGER, Header V6+, Pipelines, Scoring, ×1000%, Livrables, Annexes

## 3. Documents Produits
| Document | Type |
|----------|------|
| GOVERNANCE.md v3.0 | Gouvernance institutionnelle |
| governance_integration_certification.md | Audit |
| ui_header_v6_certification.md | Audit |
| ui_header_share_button_certification.md | Audit |
| pipelines_externes_certification.md | Audit |
| scoring_ambassadeur_certification.md | Audit |
| access_v7_optimization_certification.md | Audit |
| admin_premium_v2_share_ecosystem_audit.md | Audit |
| print_residual_root_cause_analysis.md | RCA |
| master_switch_share_integration_certification.md | Certification |
| share_module_architecture.md | Architecture |
| admin_premium_v2_share_integration_plan.md | Architecture |
| ultra_max_pp_firewall_phaseC_preparation.md | Architecture P1 |
| saline_module_ULTIME_implementation_plan.md | Architecture P1 |

## 4. Backlog
### P0 — COMPLÉTÉ
- [x] Purge PRINT+LIVE + RCA "Print."
- [x] Module PARTAGER + Master Switch 8/8
- [x] GOVERNANCE.md v3.0 institutionnelle
- [x] Optimisation ×1000% smoother
- [x] 10+ audits/certifications

### P1 — À venir
- [ ] ULTRA-MAX++ Firewall (Phase C) — Geo-fencing urbain
- [ ] Module Salines BIONIC ULTIME

### P2 — GELÉ
- [ ] Purge frontend shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2 (Social Ads)
- [ ] Merge vers main — INTERDIT
