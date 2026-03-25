# ALIMENTATION-V2 — Analyse territoriale, salines et nutrition

## Role
Moteur d'analyse territoriale avancee avec recommandations nutritionnelles
et gestion des salines. Extension du V1 avec focus sur le terrain, les
minerals et les attractifs naturels.

## Poids dans le score consolide
**0.10** (10%)

## Points d'entree
- `engine.py` → `analyze_alimentation_v2(lat, lng, species, month)`
- `router.py` → API `/api/v2/alimentation` (POST /analyze, GET /species)

## Fichiers (6 fichiers, 700 lignes)
| Fichier | Role |
|---|---|
| engine.py | Orchestrateur analyse V2 |
| router.py | Endpoints FastAPI |
| terrain.py | Analyse terrain (topographie, couvert, hydrographie) |
| salines.py | Calcul salines (mineraux, attractifs) |
| nutrition.py | Base de donnees nutritionnelle (NUTRITION_DB) |
| __init__.py | Init module |

## Dependances
- Aucune dependance externe (100% algorithmique interne)

## Dependants
- `score_consolide.py` → poids 0.10
- `saline_engine/router.py` → `analyze_terrain`
- `engine_registry/adapters.py` → `analyze_alimentation_v2`
- `server.py` → router enregistre
- **Frontend**: `AlimentationV2Layer.jsx`

## Limitations actuelles
- Modele de terrain simplifie (pas de DEM reel)
- Base nutritionnelle statique

## Plan de migration CORE
1. Copie identique dans core/scoring_pipeline/ (x3201) ← FAIT
2. Bascule imports vers core/ (x3202)
3. Normalisation API (x3300)
