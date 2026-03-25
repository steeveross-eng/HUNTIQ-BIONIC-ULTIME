# PRD — HUNTIQ-V6

## Projet
Application de scoring ecologique multi-moteurs pour la faune du Quebec (cerf, orignal, ours, dindon, wapiti). Architecture FastAPI + React.

## Etat actuel
- Branche active : `STEEVE-MAX-x3200-V6-CORE`
- Phase : PHASE 3 — Migration V6-CORE (×3200-×3204)
- Pipeline CORE : `backend/core/scoring_pipeline/` — 5 moteurs, 37 fichiers

## Historique des phases
- ×3050 : Audit total
- ×310-312 : Governance, freeze Work1, backup
- ×3101-3105 : PHASE 2 — Purge code mort (~32000 lignes)
- ×3200 : Creation branche V6-CORE
- ×3201 : Encapsulation 5 moteurs dans core/
- ×3202 : Bascule 17 imports vers core/
- ×3203 : Retrait anciens moteurs modules/
- ×3204 : Cartographie fonctionnelle CORE (COMPLETE)

## Backlog (P0-P3)
- P0 : ×3205 — Normalisation scientifique pipeline CORE
- P1 : ×3300 — Normalisation V6
- P1 : ×3400 — Interconnexion totale
- P2 : Merge STEEVE-MAX-x3200-V6-CORE vers V6-CORE
- P3 : Merge vers main + MASTER_SWITCH unlock
- P3 : Implementation BSAA (Social Ads Automation)

## Points critiques identifies (×3204)
1. 3 moteurs sur 5 utilisent des PROXY dans score_consolide (divergence potentielle)
2. score_consolide.py non migre dans core/
3. 5+ duplications de code (hash, grille, constantes)
4. Classifications incoherentes entre moteurs
5. pression_v1 couple a modules/engine_registry
