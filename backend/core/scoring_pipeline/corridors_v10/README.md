# CORRIDORS-V10 — Moteur de corridors fauniques

## Role
Orchestrateur principal des corridors de deplacement de la faune.
Pipeline complet: profil espece → grille de couts → reseau de corridors
→ scoring → classification normative → validation BCE-4X.
Le moteur le plus complexe du scoring pipeline.

## Poids dans le score consolide
**0.25** (25%) — Le plus eleve avec alimentation_v1

## Points d'entree
- `engine.py` → `analyze_full(lat, lng, species, month, radius)`
- `router.py` → API `/api/v10/corridors` (POST /analyze, POST /analyze-full, GET /corridors, GET /barriers)

## Fichiers (12 fichiers, 2882 lignes)
| Fichier | Role |
|---|---|
| engine.py | Orchestrateur pipeline complet |
| router.py | Endpoints FastAPI |
| cost_surface.py | Generation grille de couts enrichie |
| network_builder.py | Construction reseau de corridors (A*) |
| pathfinder.py | Algorithme de recherche de chemin |
| scoring.py | Scoring corridors + classification normative |
| classifier.py | Niveaux de classification (CORRIDOR_LEVELS) |
| validator.py | Validation BCE-4X + Steeve-MAX |
| multi_engine.py | Score multi-moteur (integre alim, repos, pression) |
| species_profiles.py | 12 parametres par espece + modifiers saisonniers |
| documentation.py | Documentation interne |
| __init__.py | Init module |

## Dependances
- `alimentation_v1` → references poids dans multi_engine (0.18)
- `repos_v1` → references poids dans multi_engine (0.14)
- `shapely` → geometries concave_hull
- `math` → calculs trigonometriques

## Dependants
- `score_consolide.py` → poids 0.25 (le plus eleve)
- `bionic_ecological_engine` → integration corridors species-aware
- `bionic_data_fabric` → mapping DataDomain.CORRIDORS
- `saline_engine` → references directes
- `server.py` → router enregistre
- **Frontend**: `BionicCorridorsV10Layer.jsx` (composant dedie complet)

## Formule multi-engine (multi_engine.py)
```python
ENGINE_WEIGHTS = {
    "alimentation_v1": 0.18,
    "repos_v1":        0.14,
    "alimentation_v2": 0.08,
    "pression_v1":     0.10,
    "corridors_base":  0.50,
}
```

## Limitations actuelles
- Algorithme A* sans optimisation GPU
- Rayon max ~5km pour performance
- Validation BCE-4X simplifiee (regles statiques)

## Plan de migration CORE
1. Copie identique dans core/scoring_pipeline/ (x3201) ← FAIT
2. Bascule imports vers core/ (x3202)
3. Normalisation API + optimisation A* (x3300)
