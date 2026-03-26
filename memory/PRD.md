# HUNTIQ-V6 — PRD
## GOLDEN-BCE-4X / STEEVE-MAX

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200-x3205 | Migration core/ + Cartographie | COMPLETE |
| x3300-x3400 | Migration score_consolide + Interconnexion | COMPLETE |
| x4000-SUPRA | 17 moteurs squelettes | CERTIFIE |
| x4100 | Integration scientifique 22 moteurs (Option C) | CERTIFIE |
| x4500-ULTRA | Reconstruction PREVIEW + BSAA | CERTIFIE |
| x4515-FIX | PinnablePanel V2 — 8 panneaux | CERTIFIE |
| x4520-A thru H4 | Purge V10, panneaux, crash fix | COMMITE |
| x4600-R2 | NUTRITION_RENAME — Renommage 100% | CERTIFIE |
| x4600-R4 | WAYPOINT_DELETE_TOTAL_RESET | CERTIFIE |
| x4700-FREEZE-PREP | GEL v4600-STABLE | CERTIFIE |
| x4700-R2 | VISUAL_REDESIGN DASHBOARD_STYLE + Correctif UX fullHeight | COMPLETE |
| **x4700-CORRECTIF** | **Portal React fullHeight + Boutons X/Imprimer fixes z-9999** | **COMPLETE — EN ATTENTE VALIDATION** |
| **x5000** | **NUTRITION INTELLIGENCE SUPRA — 9 moteurs** | **COMPLETE — EN ATTENTE VALIDATION** |

## x4700-CORRECTIF — Detail technique

Correctif applique a `PinnablePanel.jsx`:
- `ReactDOM.createPortal()` en mode fullHeight pour echapper au stacking context
- Bouton Fermer (X): position absolute, top:16px, right:16px, z-index:10, rouge #dc2626
- Bouton Imprimer: position absolute, top:16px, right:68px, z-index:10, vert #1b5e20
- Header autonome #0d0d1a, bordure accent
- Fond opaque #0a0a0f couvrant la navbar

## x5000 — 9 moteurs implementes

| Moteur | Endpoint | Statut |
|--------|----------|--------|
| x5100 MINERAL_SCORE | POST /api/v6/nutrition-intelligence/score | OK |
| x5200 RECOMMENDATION | POST /api/v6/nutrition-intelligence/recommendations | OK |
| x5300 ORDER | POST /api/v6/nutrition-intelligence/order | OK |
| x5400 UI | Route /nutrition-supra | OK |
| x5500 ENERGY_PROTEIN | POST /api/v6/nutrition-intelligence/energy-protein | OK |
| x5600 SITE_GUIDE | POST /api/v6/nutrition-intelligence/site-guide | OK |
| x5700 COST | POST /api/v6/nutrition-intelligence/costs + /costs/compare | OK |
| x5800 RECIPE | POST /api/v6/nutrition-intelligence/recipe | OK |
| x5900 EVIDENCE | GET /api/v6/nutrition-intelligence/evidence | OK |
| FULL | POST /api/v6/nutrition-intelligence/full-analysis | OK |

## Prochaines etapes
- Validation STEEVE-MAX x4700-CORRECTIF en PREVIEW
- Validation STEEVE-MAX x5000 en PREVIEW
- Attente prochaine directive

## Backlog
- BSAA-2 (P1 — FORMELLEMENT en backlog, aucune action sans directive)
- Merge Work1 vers main (P2 — strictement STEEVE-MAX)
