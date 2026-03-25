# PRD — HUNTIQ-V6

## Projet
Application de scoring ecologique multi-moteurs pour la faune du Quebec (cerf, orignal, ours, dindon, wapiti). Architecture FastAPI + React.

## Etat actuel
- Branche active : `STEEVE-MAX-x3200-V6-CORE`
- Phase : PHASE 4 — Normalisation scientifique (×3205 COMPLETE)
- Pipeline CORE : `backend/core/scoring_pipeline/` — 5 moteurs + module `common/`

## Historique des phases
- ×3050 : Audit total
- ×310-312 : Governance, freeze Work1, backup
- ×3101-3105 : PHASE 2 — Purge code mort (~32000 lignes)
- ×3200 : Creation branche V6-CORE
- ×3201 : Encapsulation 5 moteurs dans core/
- ×3202 : Bascule 17 imports vers core/
- ×3203 : Retrait anciens moteurs modules/
- ×3204 : Cartographie fonctionnelle CORE (COMPLETE)
- ×3205 : Normalisation scientifique — module common/ cree (COMPLETE)

## Ce qui a ete fait dans ×3205
- Module `common/` cree (9 fichiers, 828 lignes): constants, species, seasons, classification, errors, schemas, grid, hash
- 8 fichiers moteurs normalises (imports depuis common/)
- 8 duplications de code eliminees
- 5 systemes de classification unifies dans un framework parametrable
- Modele d'erreurs COREError defini (8 types)
- Schemas d'entree/sortie normalises (10 dataclasses)
- 3 variantes de hash documentees (divergence confirmee)
- ZERO changement fonctionnel — Score consolide verifie: 56.2

## Backlog (P0-P3)
- P0 : ×3300 — Normalisation V6 (migration score_consolide, remplacement proxy, integration COREError)
- P1 : ×3400 — Interconnexion totale
- P2 : Merge STEEVE-MAX-x3200-V6-CORE vers V6-CORE
- P3 : Merge vers main + MASTER_SWITCH unlock
- P3 : Implementation BSAA (Social Ads Automation)

## Points critiques identifies (×3204/×3205)
1. 3 moteurs sur 5 utilisent des PROXY dans score_consolide (divergence ~30-35%)
2. score_consolide.py non migre dans core/ (reste dans modules/)
3. pression_v1 couple a modules/engine_registry (a decoupler ×3300)
4. Variantes de hash A/B/C a unifier (×3300)
