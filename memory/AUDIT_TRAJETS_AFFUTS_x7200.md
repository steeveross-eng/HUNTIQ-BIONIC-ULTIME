# AUDIT ×7200 — TRAJETS VERS AFFUTS — ANALYSE ET PROPOSITIONS
## Directive: AUDIT_TRAJETS_VERS_AFFUTS
## Autorite: COMMANDANT STEEVE-MAX | Protocole: BCE-4X GOLDEN V6+

---

## 1. ARCHITECTURE DU MOTEUR DE ROUTAGE TRAJETS

### Pipeline actuel
```
Paires de zones (ligne 771-775 zone_engine_core_v2.py)
  → _build_terrain_grid() → grille A* (167m resolution)
  → CorridorPathfinder.find_corridor_path() → A* pathfinding
  → smooth_path() → lissage Chaikin
  → Fallback Bezier si A* echoue
  → _filter_corridors_water() → post-filtre eau V7.2
```

### Constat critique
**Le MEME moteur A* est utilise pour les corridors animaux ET les trajets humains vers les affuts.**
Il n'y a AUCUNE distinction entre le routage animalier et le routage humain.

### Paires trajet/affut generees (ligne 771-775)
```python
("affuts", "habitats"), ("trajets", "alimentation"),
("affuts", "rut"), ("affuts", "trajets"), ("trajets", "rut"),
("salines", "rut"), ("salines", "affuts"), ("habitats", "rut"),
("habitats", "trajets"), ("salines", "trajets"),
("affuts", "repos"), ("affuts", "alimentation"),
```

---

## 2. CAUSE RACINE — POURQUOI LES TRAJETS TRAVERSENT LA FORET

### TERRAIN_COSTS (corridor_10x.py:457-491)
| Terrain | Cout | Categorie |
|---------|:----:|-----------|
| valley, coulee, wooded_strip | 1.0 | IDEAL pour l'animal |
| riparian, forest_edge | 1.0-1.2 | IDEAL pour l'animal |
| saddle | 1.3 | BON pour l'animal |
| **mature_forest** | **1.4** | **BON pour l'animal** |
| **mixed_forest** | **1.5** | **BON pour l'animal** |
| **conifer_forest** | **1.6** | **BON pour l'animal** |
| gentle_ridge | 1.7 | ACCEPTABLE |
| open_field | 3.0 | A EVITER (pour l'animal) |
| road_crossing | 4.5 | A EVITER |
| water_body | 999.0 | IMPASSABLE |

### Le probleme
**La foret est traitee comme terrain PREFERE (cout 1.4-1.6)** — c'est correct pour
les **deplacements animaux** (orignal, chevreuil cherchent le couvert forestier), mais 
INCORRECT pour les **trajets humains** (un chasseur prefere les sentiers, chemins, routes).

### LAYER_TO_TERRAIN mapping (zone_engine_core_v2.py:935-941)
```python
LAYER_TO_TERRAIN = {
    "habitats": "mature_forest",      # cout 1.4
    "alimentation": "forest_edge",    # cout 1.2
    "repos": "conifer_forest",        # cout 1.6
    "rut": "mixed_forest",            # cout 1.5
    "affuts": "hedgerow",             # cout 1.1
    "trajets": "wooded_strip",        # cout 1.0
    "salines": "riparian",            # cout 1.0
    "corridors": "valley",            # cout 1.0
    "hydro": "water_body",            # cout 999.0 (V7.2)
}
```

### Consequences
1. L'A* genere des trajets a travers la foret dense (cout 1.4-1.6)
   parce que c'est MOINS COUTEUX que de faire un detour par un champ ouvert (cout 3.0)
2. Les sentiers/chemins forestiers existants ne sont PAS integres comme couche de donnees
3. Le Bezier fallback trace une courbe directe sans considerer le terrain
4. Aucun mecanisme ne distingue "deplacement humain" de "deplacement animal"

---

## 3. ANALYSE DES PONDERATIONS

### Table actuelle — Perspective animale
```
animal_preference:
  foret_mature      = TRES_PREFERE (1.4)
  lisiere           = IDEAL (1.2)
  champ_ouvert      = EVITE (3.0)
  route             = EVITE (4.5)
  zone_urbaine      = INTERDIT (10.0)
```

### Table ideale — Perspective humaine (trajets)
```
human_preference:
  sentier_boise     = IDEAL (1.0)
  route_forestiere  = PREFERE (1.2)
  champ_ouvert      = ACCEPTABLE (1.5)
  foret_mature      = DIFFICILE (3.5)
  foret_dense       = TRES_DIFFICILE (5.0)
  zone_urbaine      = FACILE (1.3)
  riviere           = IMPASSABLE (999.0)
```

---

## 4. ANALYSE RASTER & DONNEES SENTIERS

### Donnees actuellement disponibles
| Source | Integree? | Detail |
|--------|:---------:|--------|
| Bruit Simplex (M1) | OUI | Genere toutes les zones |
| SRTM DEM (altitude) | OUI | Pentes, orientation |
| Cache OSM | PARTIEL | 9 micro-polygones eau |
| NFIS-QC WMS (hydro) | OUI | Overlay visuel seulement |
| **Sentiers OSM** | **NON** | Pas de couche trails |
| **Routes forestieres** | **NON** | Pas de couche roads |
| **Sentiers de chasse** | **NON** | Pas de couche user trails |

### Constat
**Aucune donnee de sentier n'est integree dans le raster.**
Le moteur A* n'a aucune information sur les chemins existants.
Il ne peut pas "preferer" un sentier parce qu'il ne sait pas qu'il existe.

---

## 5. PROPOSITIONS DE SOLUTIONS

### Solution 1 — Table de couts dediee "Human Trajets"
```python
HUMAN_TRAJET_COSTS = {
    "valley": 1.0, "wooded_strip": 1.0,    # Sentiers naturels
    "forest_edge": 1.2, "hedgerow": 1.1,    # Lisieres accessibles
    "open_field": 1.5, "agriculture": 1.5,  # Champs (faciles pour humains)
    "mixed_forest": 3.5,                     # Foret mixte (difficile)
    "mature_forest": 4.0,                    # Foret mature (tres difficile)
    "conifer_forest": 4.5,                   # Coniferes (tres dense)
    "dense_thicket": 6.0,                    # Fourre (quasi-impenetrable)
    "water_body": 999.0,                     # Eau (impassable)
    "cliff": 999.0,                          # Falaise (impassable)
}
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | Faible (1 table + condition dans le pathfinder) |
| Impact terrain | Trajets humains evitent la foret dense |
| Impact performance | Negligeable |
| Compatibilite Mon Territoire | HAUTE (nouvelle table, pas de modification de l'existante) |

### Solution 2 — Corridors naturels comme preference
```
Si un corridor existant relie waypoint → affut:
  → utiliser le corridor comme base du trajet
  → cout corridor = 0.5 (tres prefere)
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | Modere (pre-calcul corridors → grille trajet) |
| Impact terrain | Trajets suivent les corridors ecologiques |
| Compatibilite Mon Territoire | HAUTE |

### Solution 3 — Integration sentiers OSM
```
Telecharger la couche "highway" OSM pour la zone du waypoint
  → filtrer trails, tracks, paths, forestry roads
  → rasteriser dans la grille A* comme terrain "trail" (cout 0.8)
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | ELEVE (integration API OSM, cache, rasterisation) |
| Impact terrain | PARFAIT (trajets sur vrais sentiers) |
| Compatibilite Mon Territoire | Modere (ajout d'une couche de donnees) |

### Solution 4 — Post-filtre "minimiser foret"
```
Apres generation du trajet A*:
  → calculer le % de segments en foret dense
  → si > 60% → rejeter et regenerer avec couts foret x2
  → repeter jusqu'a < 40% foret ou max 3 iterations
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | Faible (post-traitement simple) |
| Impact terrain | Amelioration progressive |
| Compatibilite Mon Territoire | HAUTE |

### Solution 5 — Multi-layer routing
```
Phase 1: Generer le trajet "humain" (waypoint → affut) avec HUMAN_TRAJET_COSTS
Phase 2: Generer le corridor "animal" (affut → zone fonctionnelle) avec TERRAIN_COSTS
Phase 3: Point de jonction = affut
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | Modere (2 passes A*) |
| Impact terrain | IDEAL (separation humain/animal) |
| Compatibilite Mon Territoire | HAUTE |

### RECOMMANDATION EMERGENT
**Solution 1 + Solution 4** en priorite :
1. Table de couts dediee `HUMAN_TRAJET_COSTS` — simple, efficace, non-destructif
2. Post-filtre "minimiser foret" — garde-fou contre les trajets absurdes
3. **Solution 3 (sentiers OSM)** — a implementer dans une phase future (M5 ou M6)

---

## 6. CONFORMITE BCE-4X

| Contrainte | Statut |
|-----------|:------:|
| ZERO LOSS | CONFORME (audit seulement, pas de modification) |
| ZERO REGRESSION | CONFORME |
| ZERO INTERPRETATION | CONFORME (analyse factuelle du code) |
| ZERO DOUBLON | CONFORME |
| ZERO OBSOLESCENCE | ECART POTENTIEL (absence de sentiers OSM) |

---

## 7. RESUME

### Cause racine
Le moteur A* utilise une **table de couts unique** concue pour les **deplacements animaux** 
(foret = terrain prefere). Les trajets humains vers les affuts sont generes avec 
les memes couts, resultant en des parcours a travers la foret dense.

### Correction recommandee
1. **IMMEDIAT** : Table `HUMAN_TRAJET_COSTS` (foret dense = cout 4.0+)
2. **IMMEDIAT** : Post-filtre "minimiser foret" (max 40% segments forestiers)
3. **FUTUR** : Integration sentiers OSM comme couche de donnees (M5/M6)

### En attente
Validation STEEVE-MAX pour implementer Solution 1 + Solution 4.

---

**Rapport genere** : 2026-04-05
**Autorite** : STEEVE-MAX
**Protocole** : BCE-4X GOLDEN V6+
