# ALIMENTATION-V1 — Moteur alimentaire scientifique multi-especes

## Role
Moteur principal d'analyse des sources alimentaires pour la faune.
Evalue la qualite nutritionnelle d'un territoire par espece et saison
sur une grille de 10m de resolution dans un carre de 2km2.

## Poids dans le score consolide
**0.25** (25%) — Le plus eleve avec corridors_v10

## Points d'entree
- `engine.py` → `analyze_single_point(lat, lng, species, month)`
- `router.py` → API `/api/v1/alimentation` (POST /analyze, GET /species, GET /ingredients)

## Fichiers (9 fichiers, 1080 lignes)
| Fichier | Role |
|---|---|
| engine.py | Orchestrateur principal |
| router.py | Endpoints FastAPI |
| grid_generator.py | Generation grille 10m dans carre 2km2 |
| layers.py | Chargement couches OSM (forets, eau, routes, batiments) |
| scoring.py | Calcul score alimentaire par cellule |
| classifier.py | Classification qualite (EXCELLENT, BON, MOYEN, etc.) |
| species_profiles.py | Profils par espece (orignal, cerf, ours, wapiti, mulet) |
| documentation.py | Documentation interne moteur |
| __init__.py | Init module |

## Dependances
- Aucune dependance externe (100% algorithmique interne)
- Utilise OSM via `layers.py` (cache local)

## Dependants (qui importe ce moteur)
- `score_consolide.py` → `analyze_single_point`
- `repos_v1/engine.py` → `load_layers`
- `repos_v1/layers.py` → `load_layers`
- `pression_v1/engine.py` → `load_layers`
- `corridors_v10/multi_engine.py` → references poids
- `engine_registry/adapters.py` → `analyze_single_point`
- `server.py` → router enregistre

## Limitations actuelles
- Grille fixe 2km2 (non configurable)
- Donnees OSM locales (pas de mise a jour temps reel)
- Profils especes limites a 5 especes principales

## Plan de migration CORE
1. Copie identique dans core/scoring_pipeline/ (x3201) ← FAIT
2. Bascule imports vers core/ (x3202)
3. Normalisation API (x3300)
