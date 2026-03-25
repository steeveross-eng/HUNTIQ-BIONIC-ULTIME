# REPOS-V1 — Moteur des zones de repos faune

## Role
Moteur scientifique d'analyse des zones de repos pour la faune.
Evalue la qualite des zones de refuge, de thermoregulation et de
securite par espece et saison sur une grille de 10m.

## Poids dans le score consolide
**0.20** (20%)

## Points d'entree
- `engine.py` → `analyze_single_point(lat, lng, species, month)`
- `router.py` → API `/api/v1/repos` (POST /analyze, GET /zones)

## Fichiers (9 fichiers, 838 lignes)
| Fichier | Role |
|---|---|
| engine.py | Orchestrateur principal |
| router.py | Endpoints FastAPI |
| grid_generator.py | Generation grille 10m |
| layers.py | Chargement couches (reutilise alimentation_v1.layers) |
| scoring.py | Calcul score repos par cellule |
| classifier.py | Classification qualite |
| species_profiles.py | Profils repos par espece |
| documentation.py | Documentation interne |
| __init__.py | Init module |

## Dependances
- `modules.alimentation_v1.layers` → `load_layers` (dependance critique)

## Dependants
- `score_consolide.py` → `analyze_single_point` (poids 0.20)
- `corridors_v10/multi_engine.py` → poids 0.14 + attracteurs
- `engine_registry/adapters.py` → `analyze_single_point`
- `server.py` → router enregistre

## Limitations actuelles
- Dependance sur alimentation_v1 pour le chargement des couches
- Profils especes limites a 5 especes principales

## Plan de migration CORE
1. Copie identique dans core/scoring_pipeline/ (x3201) ← FAIT
2. Bascule imports vers core/ (x3202)
3. Internaliser load_layers (supprimer dependance alimentation_v1) (x3300)
