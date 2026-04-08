# PRD — HUNTIQ BIONIC V6+ / BCE-4X GOLDEN

## Objectif
Application de chasse et gestion de territoire avec analyse nutritionnelle, scoring SUPRA/ULTRA/FICHE, moteurs d'intelligence géospatiale et e-commerce (Stripe).

## Architecture
- **Backend**: FastAPI (Python) — moteurs nutritionnels, scoring, Stripe checkout
- **Frontend**: React + Leaflet — carte interactive, panneau SUPRA, dashboard
- **Branche active**: `SUPRA_RECONSTRUCTION` (merge → main INTERDIT)

## Phases SUPRA x1000% — ÉTAT

### R0: Préparation ✅
### R1: Nettoyage (dead code, E09 round-robin, E03 session) ✅
### R2: Zéro duplication (CriteriaDetailModal, GoldenComponents) ✅
### R3: Découpage monolithe (5 onglets + stabilisation) ✅ CERTIFIÉ
- 1235 → 271 lignes (-78.1%), 6 modules autonomes, 72/72 tests
### R4: Corrections UX ✅ COMPLET
- R4.1: COMPAREZ grid-cols-3 → grid-cols-4 (support 4 produits)
- R4.2: Round-robin INTELLIGENCE confirmé conforme
- R4.3: Fallback product_id supprimé, avertissement si ID manquant

### R5: Cohérence données ✅ COMPLET
- R5.1 (E06): Source SOL unifiée → soilData (soil_engine) EXCLUSIF, fallback engines.soil supprimé
- R5.2 (E07): resolvedSeason propagé aux 4 appels API + 2 onglets (AnalyseTab, FicheTab) + sous-titre panneau
- R5.3 (E11): Badge DETERMINISTE ajouté dans FicheTab (teal #009688)
- 3 fichiers, +19/-30 lignes | Baselines B+C = SUPRA=52|ULTRA=39.3|FICHE=68|SOL=47
### R6: Optimisation backend ✅ COMPLET
- R6.1: Elimination N+1 dans supra-panel (3*N → 3 appels batch + lookup O(1))
- R6.2: Endpoint batch /supra-batch (4 requetes HTTP → 1 seule, -82% latence)
- R6.2b: Frontend adapte pour utiliser le batch endpoint
- R6.3: Audit latence — tous endpoints < 220ms, batch = 118ms
- Baselines B+C = SUPRA=52|ULTRA=39.3|FICHE=68|SOL=47
### R7: Externalisation PREMIUM ✅ COMPLET
- R7.1: Cree premium_guard.py — 3 guards FastAPI Depends() (require_premium, require_pro, require_feature)
- R7.2: Separation freemium_engine (486→337 lignes, -149). Source unique TIER_LIMITS dans premium_guard.py
- R7.3: Audit securite — tous endpoints freemium fonctionnels, guard disponible pour tout endpoint
- Architecture: auth_helpers.py (JWT) | premium_guard.py (tier gating) | freemium_engine (CRUD sub)
- Baselines B+C = SUPRA=52|ULTRA=39.3|FICHE=68|SOL=47
### R8: Harmonisation x1000% + Export PDF ✅ COMPLET
- R8.1: Harmonisation _meta ajoutee au batch endpoint (4 blocs _meta + 1 global _harmonized)
- R8.2: Export PDF endpoint /export-pdf operationnel (fpdf2, 3KB) + bouton frontend
- R8.3: Document DECOUPAGE_PLAN.md cree (preparation, aucune execution)
- Baselines B+C = SUPRA=52|ULTRA=39.3|FICHE=68|SOL=47

### R9: Finalisation SUPRA Reconstruction ✅ COMPLET
- R9.1: Audit final frontend — 0 unused imports critiques, 0 TODO/FIXME, console.error catch-only
- R9.2: Cross-validation inter-moteurs 100% — species/season/coordinates 4/4 CONFORME
- R9.3: AUTH_DEPRECATION_PLAN.md cree — 9 endpoints, 3 phases D1/D2/D3 (preparation uniquement)
- Baselines B+C = SUPRA=52|ULTRA=39.3|FICHE=68|SOL=47

## SUPRA RECONSTRUCTION — CERTIFIEE R3→R9 ✅ CLOTUREE
**Date de cloture: 2026-04-08**
**Autorite: COMMANDANT STEEVE-MAX**
**Statut: VERROUILLEE — Aucune modification avant P2 (AUTH) et K0 (Knowledge Engine)**

Bilan:
- Monolithe 1235→293 lignes (-76%) + 5 onglets autonomes (930L)
- Batch endpoint /supra-batch (4→1 appel HTTP, -82% latence)
- N+1 elimine (3*N→3 appels batch)
- Export PDF /export-pdf (fpdf2)
- premium_guard.py (separation AUTH/PREMIUM, 3 guards Depends())
- Harmonisation _meta + cross-validation inter-moteurs 100%
- Baselines A/B/C identiques sur toutes les phases: SUPRA=52|ULTRA=39.3|FICHE=68|SOL=47


## Tâches gelées
- P2: Déprécation 9 endpoints AUTH-USAGER
- P2: M5 Offline Mode Ultra
- P2: BSAA-2 Social Ads Automation
- INTERDIT: Merge SUPRA_RECONSTRUCTION → main

## Scores de référence (session courante)
SUPRA=52 | ULTRA=39.3 | FICHE=68 | SOL=47

## Credentials
Admin Premium: admin@huntiq.com / Saturn5858*
