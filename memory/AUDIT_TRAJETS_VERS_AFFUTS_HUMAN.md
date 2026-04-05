# AUDIT BCE-4X — TRAJETS HUMAINS VERS AFFUTS
## Rapport Complet | Directive STEEVE-MAX
## Date: 2026-04-05 | Branche: Work1

---

## 1. RESUME EXECUTIF

**HUMAN_TRAJET_COSTS est correctement applique** au pathfinder A* pour les corridors impliquant des affuts. Cependant, la grille de terrain qui alimente ce pathfinder ne contient **AUCUNE donnee de sentier reel**. Le resultat : les trajets humains sont calcules sur un terrain **uniforme** (mixed_forest partout), produisant des trajectoires quasi-rectilignes a travers la foret dense.

**Les lignes BLEUES** visibles sur la carte (capture d'ecran fournie) proviennent d'un **pipeline SEPARE** (Access Engine V6 + OSM Overpass API) qui, lui, utilise des sentiers reels.

---

## 2. SECTION A — VERSION ET PIPELINE

### 2.1 Table de couts active

| Parametre | Valeur |
|---|---|
| Table active pour trajets humains | `HUMAN_TRAJET_COSTS` (corridor_10x.py:499-533) |
| Fichier | `/app/backend/modules/bionic_engine_p0/services/corridor_10x.py` |
| Nombre de types terrain | 23 |
| Instance pathfinder | `human_trajet_pathfinder` (corridor_10x.py:757) |
| Selection pathfinder | Automatique via `is_human_trajet` (zone_engine_core_v2.py:825) |

**CONFIRME**: `HUMAN_TRAJET_COSTS` est la table de couts active pour TOUS les trajets humains vers affuts.

### 2.2 Determination trajet humain

Les paires de couches impliquant un affut sont dans `HUMAN_PAIRS` (zone_engine_core_v2.py:779-785):
```
("affuts", "habitats"), ("affuts", "rut"), ("affuts", "trajets"),
("affuts", "repos"), ("affuts", "alimentation"),
("trajets", "alimentation"), ("trajets", "rut"),
("salines", "affuts"), ("salines", "trajets"),
("habitats", "trajets")
```

**CONFIRME**: Bidirectionnel. `(from_layer, to_layer) in HUMAN_PAIRS or (to_layer, from_layer) in HUMAN_PAIRS`.

### 2.3 Post-filtre foret

| Composant | Statut |
|---|---|
| `_assess_forest_ratio` | OPERATIONNEL (zone_engine_core_v2.py:952-1001) |
| Seuil | >60% foret → `forest_heavy=True` |
| Cible | Uniquement `movement_type == "human"` |
| Position pipeline | Apres `_filter_corridors_water`, avant return |

**CONFIRME**: Le post-filtre foret est appele et fonctionne.

### 2.4 Verification aucune table legacy

| Risque | Verification | Resultat |
|---|---|---|
| Table animal utilisee pour humain | `active_pathfinder = human_trajet_pathfinder if is_human_trajet else corridor_pathfinder` | IMPOSSIBLE — selection explicite |
| Table mixte/legacy | Grep complet du codebase | AUCUNE autre table trouvee |
| Override de la table | `cost_table` fixe a l'initialisation du singleton | STABLE |

**CONFIRME**: Aucune autre table de couts n'est utilisee pour les trajets humains.

---

## 3. SECTION B — PROBLEME CRITIQUE: DONNEES TERRAIN

### 3.1 Source du terrain pour le pathfinder A*

La grille de terrain est construite par `_build_terrain_grid()` (zone_engine_core_v2.py:1004-1055):

```python
LAYER_TO_TERRAIN = {
    "habitats": "mature_forest",     # cout H=4.0
    "alimentation": "forest_edge",   # cout H=1.2
    "repos": "conifer_forest",       # cout H=4.5
    "rut": "mixed_forest",           # cout H=3.5
    "affuts": "hedgerow",            # cout H=1.0
    "trajets": "wooded_strip",       # cout H=1.0
    "salines": "riparian",           # cout H=1.2
    "corridors": "valley",           # cout H=1.0
    "peuplements": "mixed_forest",   # cout H=3.5
    "hydro": "water_body",           # cout H=999.0
}
```

**Probleme**: Cette grille mappe des ZONES COMPORTEMENTALES a des types de terrain. Elle NE contient PAS:
- Sentiers reels (path, footway, track)
- Donnees topographiques (coulee, saddle, gentle_ridge)
- Infrastructure (roads, urban)
- Vegetation reelle (clearcut, dense_thicket, deciduous_forest)

### 3.2 Types de terrain JAMAIS utilises (17/23)

| Type | Cout Humain | Jamais dans grille |
|---|---|---|
| agriculture | 1.5 | OUI |
| clearcut | 2.0 | OUI |
| cliff | 999.0 | OUI |
| coulee | 1.3 | OUI |
| deciduous_forest | 3.0 | OUI |
| dense_thicket | 6.0 | OUI |
| drainage | 2.5 | OUI |
| gentle_ridge | 1.8 | OUI |
| highway | 8.0 | OUI |
| open_field | 1.5 | OUI |
| plateau | 1.6 | OUI |
| ravine | 3.0 | OUI |
| road_crossing | 1.5 | OUI |
| saddle | 1.3 | OUI |
| steep_slope | 5.0 | OUI |
| urban | 8.0 | OUI |
| urban_edge | 6.0 | OUI |

### 3.3 Default terrain entre les zones

Quand une cellule de la grille est HORS de toute zone connue (la majorite du territoire):
```python
# corridor_10x.py:596
terrain_type = terrain_info.get("type", "mixed_forest")
```
→ **Cout humain par defaut = 3.5** (mixed_forest)

**Consequence**: Toutes les cellules entre les zones sont IDENTIQUES (cout 3.5). Le A* ne peut pas trouver de sentier car il n'en existe pas dans la grille. La trajectoire est quasi-rectiligne.

### 3.4 Resolution insuffisante

| Parametre | Valeur |
|---|---|
| Resolution grille | 0.0015° ≈ 167m |
| Max cellules | 2000 |
| Largeur sentier reel | 2-5m |
| Ratio | 167m / 3m = **55x trop grossier** |

---

## 4. SECTION B — VERIFICATION AFFICHAGE CARTE

### 4.1 Deux pipelines distincts

L'analyse de la capture d'ecran revele que les **lignes BLEUES** visibles sur la carte proviennent du **pipeline Access Engine V6**, PAS du pipeline corridor:

| Pipeline | Composant Backend | Composant Frontend | Couleur | Source terrain |
|---|---|---|---|---|
| **Corridors fauniques** | `zone_engine_core_v2.py` → `corridor_10x.py` | `BionicCorridorsV6Layer.jsx` | Orange/Rouge | `_build_terrain_grid()` — SYNTHETIQUE |
| **Routes d'acces affuts** | `bionic_stand_recommendation_engine` → `access_engine_v6` → TNE | `StandsMapLayer.jsx` | **Bleu/Cyan** | OSM Overpass API — **REEL** |

### 4.2 Etat du cache OSM

| Cache | Contenu | Sentiers | Routes |
|---|---|---|---|
| `data/osm_cache/` | 9 exclusions (eau) | ZERO | ZERO |
| `access_engine_v6/cache/` | 12282 noeuds, 14014 aretes | OUI | OUI |

**Le graphe sentiers reel existe** dans Access Engine V6 mais n'est **PAS consomme** par le pipeline corridor.

### 4.3 Pipeline existant mais deconnecte

`trail_cost_grid_v7.py` (441 lignes) dans `bionic_engine_p0/services/`:
- Rasterise les exclusions OSM en grille numpy
- Sentier/footway/path: cout 0.2-0.3 (TRES favorable)
- Eau: IMPASSABLE (999.0)
- Routes majeures: IMPASSABLE
- **Consomme par**: `corridor_v7.py` (pipeline V7 ancien)
- **PAS consomme par**: `zone_engine_core_v2.py` (pipeline V6-CORE actuel)

---

## 5. ANALYSE DES 3 CAS D'AFFUTS

### CAS 1: Affut → Habitats (trajet humain le plus frequent)

| Metrique | Valeur |
|---|---|
| Paire | (affuts, habitats) ∈ HUMAN_PAIRS |
| Terrain zone depart (affuts) | hedgerow → cout H=1.0 |
| Terrain zone arrivee (habitats) | mature_forest → cout H=4.0 |
| Terrain entre les zones | mixed_forest → cout H=3.5 |
| Sentiers reels dans la grille | ZERO |
| Trajectoire calculee | Quasi-rectiligne a travers foret |
| Trajectoire optimale | Devrait suivre sentiers et lisieres |

**Ecart**: Le A* traverse 100% de foret mixte entre affut et habitat car il n'y a pas de sentier a suivre.

### CAS 2: Salines → Affuts (chasseur revenant d'une saline)

| Metrique | Valeur |
|---|---|
| Paire | (salines, affuts) ∈ HUMAN_PAIRS |
| Terrain zone depart (salines) | riparian → cout H=1.2 |
| Terrain zone arrivee (affuts) | hedgerow → cout H=1.0 |
| Terrain entre les zones | mixed_forest → cout H=3.5 |
| Sentiers reels dans la grille | ZERO |
| Trajectoire calculee | Quasi-rectiligne a travers foret |
| Trajectoire optimale | Devrait suivre berge/ruisseau puis sentier |

**Ecart**: Le A* ne detecte pas la berge du ruisseau comme chemin naturel car le type "riparian" n'est present que dans la zone salines elle-meme.

### CAS 3: Trajets → Alimentation (chasseur se deplacant entre zones)

| Metrique | Valeur |
|---|---|
| Paire | (trajets, alimentation) ∈ HUMAN_PAIRS |
| Terrain zone depart (trajets) | wooded_strip → cout H=1.0 |
| Terrain zone arrivee (alimentation) | forest_edge → cout H=1.2 |
| Terrain entre les zones | mixed_forest → cout H=3.5 |
| Sentiers reels dans la grille | ZERO |
| Trajectoire calculee | Quasi-rectiligne a travers foret |
| Trajectoire optimale | Devrait emprunter la bande boisee existante |

**Ecart**: Ironiquement, la zone "trajets" (wooded_strip, cout 1.0) devrait representer un sentier, mais son influence ne s'etend que sur la zone elle-meme, pas sur le trajet complet.

---

## 6. RECOMMANDATIONS

### Option A — Enrichir `_build_terrain_grid()` avec donnees OSM (RECOMMANDEE)

Injecter les exclusions OSM (sentiers, routes, eau) dans la grille terrain du pathfinder corridors:

```
Source: data/osm_cache/*.json → exclusion_zones
Types a injecter:
  - roads/track → "wooded_strip" (cout H=1.0) — sentier forestier
  - roads/path → "valley" (cout H=1.0) — sentier pedestre
  - roads/footway → "hedgerow" (cout H=1.0) — sentier amenage
  - water/water → "water_body" (cout H=999.0)
  - water/stream → "riparian" (cout H=1.2)
Resolution: Garder 167m mais ajouter une bande de 2 cellules autour des sentiers
```

**Impact**: Le A* detecterait les sentiers reels et les privilegierait (cout 1.0 vs 3.5).

### Option B — Connecter Access Engine V6 au pipeline corridor

Reutiliser le graphe sentiers de Access Engine V6 (12282 noeuds) pour:
1. Extraire les segments de sentier dans la zone du territoire
2. Rasteriser ces segments dans la grille terrain du corridor
3. Le A* utiliserait automatiquement les sentiers

**Avantage**: Graphe riche (12k noeuds) deja disponible.
**Risque**: Couplage entre Access Engine et Zone Engine.

### Option C — Migrer vers trail_cost_grid_v7.py

Utiliser `trail_cost_grid_v7.py` (deja existant dans bionic_engine_p0) comme source terrain:
1. Il a DEJA la logique de rasterisation OSM
2. Il a DEJA les couts de sentier (path=0.2, track=0.3)
3. Il est DEJA dans le meme module

**Avantage**: Module existant, zero nouveau code.
**Risque**: Il utilise numpy (performance), et les couts sont differents de HUMAN_TRAJET_COSTS.

### Garanties pour chaque option

| Garantie | Comment |
|---|---|
| Trajet le moins energivore | Sentiers reels a cout minimal (1.0) vs foret (3.5-4.5) |
| Trajet le moins dangereux | Eau impassable (999.0), pentes raides penalisees (5.0) |
| Conformite BCE-4X | ZERO modification de la logique maitresse, enrichissement ADDITIONNEL uniquement |

---

## 7. CONFORMITE BCE-4X

| Critere | Statut |
|---------|--------|
| ZERO LOSS | CONFORME — Aucune fonctionnalite supprimee |
| ZERO REGRESSION | CONFORME — Pipeline corridor intact |
| ZERO INTERPRETATION | CONFORME — Diagnostic factuel, aucune modification |
| ZERO DOUBLON | CONFORME — Identification de pipeline existant deconnecte |
| ZERO OBSOLESCENCE | **NON-CONFORME** — 17 types terrain non exploites |
| Merge Work1 → main | INTERDIT — Aucun merge effectue |

---

## 8. STATUT

- **HUMAN_TRAJET_COSTS**: OPERATIONNEL mais inefficace sans donnees sentiers reelles
- **_assess_forest_ratio**: OPERATIONNEL (6/6 tests PASS)
- **Pipeline corridor**: Fonctionnel mais alimente par grille terrain synthetique
- **Pipeline access route (bleu)**: Fonctionnel avec OSM reel (systeme separe)
- **Correction necessaire**: Enrichir `_build_terrain_grid()` avec donnees OSM

**EN ATTENTE DECISION COMMANDANT STEEVE-MAX: Option A, B, ou C**

---

**FIN D'AUDIT — BCE-4X GOLDEN V6+**
