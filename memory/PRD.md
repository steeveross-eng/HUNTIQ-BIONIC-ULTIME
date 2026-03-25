# PRD — HUNTIQ-V6

## Projet
Application de scoring ecologique multi-moteurs pour la faune du Quebec (cerf, orignal, ours, dindon, wapiti). Architecture FastAPI + React.

## Etat actuel
- Branche active : `STEEVE-MAX-x3200-V6-CORE`
- Phase : CORE+ complete (×3300)
- Pipeline CORE : `backend/core/scoring_pipeline/` — 5 moteurs + common/ + score_consolide

## Historique des phases
- ×3050 : Audit total
- ×310-312 : Governance, freeze Work1, backup
- ×3101-3105 : PHASE 2 — Purge code mort (~32000 lignes)
- ×3200-3203 : PHASE 3 — Migration V6-CORE (encapsulation, bascule imports, retrait anciens)
- ×3204 : Cartographie fonctionnelle CORE (COMPLETE)
- ×3205 : Normalisation scientifique — module common/ (COMPLETE)
- ×3300 : Normalisation V6 CORE+ — migration score_consolide, suppression proxy (COMPLETE)

## Ce qui a ete fait dans ×3300
- score_consolide.py migre de modules/ vers core/scoring_pipeline/
- 3 PROXY supprimes: corridors, alimentation_v2, pression → appels directs moteurs CORE
- Hash variante C centralisee dans common/hash.py
- Classification via common/classification.py
- Redirect retrocompatible dans modules/score_consolide.py
- Score 56.2 — ZERO divergence confirmee

## Backlog (P0-P3)
- P0 : ×3400 — Interconnexion totale (backend + frontend)
- P1 : ×4000 — CORE++ (moteurs scientifiques: Hydro, Thermal, Visibility, NDVI, Habitat, Trajets, Attracteurs)
- P2 : Merge STEEVE-MAX-x3200-V6-CORE vers V6-CORE
- P3 : Merge vers main + MASTER_SWITCH unlock
- P3 : Implementation BSAA (Social Ads Automation)
