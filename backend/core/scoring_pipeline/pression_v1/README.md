# PRESSION-V1 — Moteur de pression humaine

## Role
Calcul de la pression humaine sur un territoire.
Evalue l'impact des routes, batiments et activites humaines
sur la qualite de l'habitat faunique. Calcul deterministe
base sur les distances aux infrastructures.

## Poids dans le score consolide
**0.20** (20%)

## Points d'entree
- `engine.py` → classe `PressionV1Engine` (conforme BionicEngine)
  - `analyze(lat, lng, species, month)` → `EngineScore`

## Fichiers (2 fichiers, 88 lignes)
| Fichier | Role |
|---|---|
| engine.py | Calcul pression (distances routes/batiments) |
| __init__.py | Init module |

## Dependances
- `modules.engine_registry.base` → `BionicEngine`, `EngineMeta`, `EngineScore`, etc.
- `modules.alimentation_v1.layers` → `load_layers` (routes, batiments)

## Dependants
- `engine_registry/registry.py` → enregistre comme "PRESSION-V1"
- `score_consolide.py` → poids 0.20

## Limitations actuelles
- Pas de router propre (pas d'API exposee directement)
- Modele simplifie (distance lineaire, pas de ponderation par type de route)
- Dependance sur engine_registry et alimentation_v1

## Plan de migration CORE
1. Copie identique dans core/scoring_pipeline/ (x3201) ← FAIT
2. Bascule imports vers core/ (x3202)
3. Ajouter router + API propre (x3300)
4. Internaliser load_layers (x3300)
