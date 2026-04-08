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
### R3: Découpage monolithe (5 onglets + stabilisation) ✅ COMPLET
- R3.1: constants.js (165 lignes) ✅
- R3.2: AnalyseTab.jsx (331 lignes) ✅
- R3.4: FicheTab.jsx (260 lignes) ✅
- R3.6: IntelligenceTab.jsx (88 lignes) ✅
- R3.7: ComparezTab.jsx (117 lignes) ✅
- R3.8: CommandezTab.jsx (139 lignes) ✅
- R3.10: Stabilisation finale (271 lignes shell pur) ✅
- R3.11-R3.13: Certification (72/72 tests, triple baseline) ✅
- **Résultat**: 1235 → 271 lignes (-78.1%), ZERO régression

### R4: Corrections UX ⏳ EN ATTENTE AUTORISATION
- COMPAREZ grid-cols-4
- Round-robin INTELLIGENCE amélioration

### R5: Cohérence données ⏳
### R6: Optimisation backend ⏳
### R7: Externalisation PREMIUM ⏳

## Tâches gelées
- P1: Harmonisation x1000% + Test export PDF
- P2: Déprécation 9 endpoints AUTH-USAGER
- P2: M5 Offline Mode Ultra
- P2: BSAA-2 Social Ads Automation
- ⛔ Merge SUPRA_RECONSTRUCTION → main: STRICTEMENT INTERDIT

## Scores de référence (session courante)
SUPRA=52 | ULTRA=39.3 | FICHE=68 | SOL=47

## Credentials
Admin Premium: admin@huntiq.com / Saturn5858*
