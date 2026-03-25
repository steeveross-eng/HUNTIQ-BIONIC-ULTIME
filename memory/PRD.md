# PRD — HUNTIQ-V6

## Projet
Application de scoring ecologique multi-moteurs pour la faune du Quebec. Architecture FastAPI + React.

## Etat actuel
- Branche active : `STEEVE-MAX-x3200-V6-CORE`
- Phase : ×3400 COMPLETE — Interconnexion totale backend + frontend
- Pipeline CORE : backend/core/scoring_pipeline/ — 5 moteurs + common/ + score_consolide
- Frontend : Tous imports resolus, design-system complet, utils restaures

## Historique complet
- ×3050 : Audit total
- ×310-312 : Governance, freeze Work1, backup
- ×3101-3105 : PHASE 2 — Purge code mort (~32000 lignes)
- ×3200-3203 : PHASE 3 — Migration V6-CORE
- ×3204 : Cartographie fonctionnelle CORE
- ×3205 : Normalisation scientifique — module common/
- ×3300 : Normalisation V6 CORE+ — migration score_consolide, suppression proxy
- ×3400 : Interconnexion totale — 18 fichiers restaures, ZERO import casse

## Backlog (P0-P3)
- P0 : ×4000 — CORE++ (moteurs scientifiques manquants)
- P1 : Verification PREVIEW complète (carte, couches, diagnostics)
- P2 : Merge branche vers V6-CORE puis main
- P3 : MASTER_SWITCH unlock + deploiement public
- P3 : Implementation BSAA
