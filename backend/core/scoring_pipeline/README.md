# CORE Scoring Pipeline — README
## Directive x3205 — Normalisation scientifique

### Architecture

```
core/scoring_pipeline/
├── common/                   Module partage (x3205)
│   ├── constants.py          Toutes les constantes CORE
│   ├── species.py            Registre des especes
│   ├── seasons.py            Mapping mois → saison
│   ├── classification.py     Systeme de classification unifie
│   ├── errors.py             Modele d'erreurs COREError
│   ├── schemas.py            Schemas d'entree/sortie normalises
│   ├── grid.py               Generateur de grille partage
│   └── hash.py               Documentation des variantes de hash
├── alimentation_v1/          Moteur alimentaire V1 (830 lignes)
├── alimentation_v2/          Moteur alimentaire V2 (560 lignes)
├── repos_v1/                 Moteur repos V1 (740 lignes)
├── corridors_v10/            Moteur corridors V10 (2600 lignes)
└── pression_v1/              Moteur pression V1 (85 lignes)
```

### Signatures normalisees (x3205)

Chaque moteur expose ces fonctions principales:

| Moteur | Fonction principale | Entree | Sortie |
|--------|-------------------|--------|--------|
| alimentation_v1 | `analyze_square(lat,lng,species,month,...)` | CoreAnalysisInput | {engine,score,cells,...} |
| alimentation_v1 | `analyze_single_point(lat,lng,species,month)` | lat,lng,species,month | {engine,score,...} |
| alimentation_v2 | `analyze_alimentation_v2(lat,lng,species,month,max)` | CoreAnalysisInput | {score_global,terrain,...} |
| repos_v1 | `analyze_square(lat,lng,species,month,...)` | CoreAnalysisInput | {engine,score,cells,...} |
| repos_v1 | `analyze_single_point(lat,lng,species,month)` | lat,lng,species,month | {engine,score,...} |
| corridors_v10 | `analyze_corridors(lat,lng,species,month,...)` | CorridorAnalysisInput | {engine,score,...} |
| corridors_v10 | `analyze_corridors_full(lat,lng,species,month,...)` | CorridorAnalysisInput | {engine,score,geojson,...} |
| pression_v1 | `PressionV1Engine.score_point(lat,lng,species,month)` | lat,lng,species,month | EngineScore |

### Especes supportees (5)

CERF, ORIGNAL, OURS, DINDON, WAPITI
Voir `common/species.py` pour le registre complet et le mapping frontend.

### Saisons

printemps (3-5), ete (6-8), automne (9-11), hiver (12-2)
Voir `common/seasons.py` — source unique.

### Classifications

5 systemes preserves dans `common/classification.py`:
- ALIMENTATION_V1: 4 niveaux (OPTIMALE/TRES_BONNE/UTILISABLE/FAIBLE)
- REPOS_V1: 4 niveaux (OPTIMAL/TRES_BON/UTILISABLE/FAIBLE)
- CORRIDORS_V10_NETWORK: 4 niveaux (OPTIMAL/FONCTIONNEL/DEGRADE/INUTILISABLE)
- CORRIDORS_V10_CORRIDOR: 5 niveaux normatifs (CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE)
- SCORE_CONSOLIDE: 4 niveaux (OPTIMAL/BON/MODERE/FAIBLE)

### Constantes

Toutes extraites dans `common/constants.py` avec documentation d'origine et unite.

### Erreurs

Hierarchie COREError dans `common/errors.py`:
- COREError (base)
- COREValidationError (entrees invalides)
- CORESpeciesError (espece inconnue)
- COREGridError (grille invalide)
- COREBarrierError (barriere ecologique)
- COREPathError (pathfinding echoue)
- COREClassificationError (classification inconnue)
- COREDependencyError (dependance manquante)

### Dependances inter-moteurs

| Source | Cible | Type |
|--------|-------|------|
| repos_v1 | alimentation_v1/layers.py | Import direct |
| pression_v1 | alimentation_v1/layers.py | Import direct |
| pression_v1 | modules/engine_registry/base.py | Import direct (a decoupler) |
| score_consolide | alimentation_v1/engine.py | Import direct |
| score_consolide | repos_v1/engine.py | Import direct |
| corridors_v10 | shapely | Dependance externe |
| alimentation_v1 | common/ | Constantes, saisons |
| repos_v1 | common/ | Constantes, saisons, grille |
| corridors_v10 | common/ | Constantes, saisons |
