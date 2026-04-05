# AUDIT ×7200 — ARBORESCENCE ZONES ET ORIGINE ZONES D'EAU
## Directive: AUDIT_COMPLET_ARBORESCENCE_ZONES_ET_ORIGINE_DES_ZONES_D_EAU
## Autorite: COMMANDANT STEEVE-MAX | Protocole: BCE-4X GOLDEN V6+

---

## POINT 1 — DIAGNOSTIC PRECIS DES 2 ZONES D'EAU

### Fichier source exact
**`behavioral_rasterizer.py`** — lignes 267-271

Les zones hydro sont generees par **bruit Simplex procedurale**, PAS par des donnees hydro reelles.

```python
# behavioral_rasterizer.py — hydro layer generation
elif layer_id == "hydro":
    v1 = _simplex2d(x_m * 0.0008, y_m * 0.0012, perm)
    v2 = _simplex2d(x_m * 0.0015 + 100, y_m * 0.0005 + 100, perm)
    drainage = abs(v1 * v2)
    return 0.8 if drainage < 0.15 else 0.2
```

### Moteur generateur
**M1 — Pipeline de base** : `behavioral_rasterizer.py` → `zone_engine_core_v2.py` → `pipeline_v7.py`

### Etape de pipeline
```
1. generate_layer_raster()  → grille 2D de valeurs de bruit Simplex
2. generate_organic_zones() → extraction de contours (marching squares) → polygones GeoJSON
3. _convert_features_to_circles() → conversion en cercles 600m
4. process_zones_v7()       → exclusions + merge + enrichissement V7
5. _merge_nearby_same_type_zones() → fusion si centroides < 200m
```

### Type interne
- `layer_id = "hydro"`
- `terrain_type = "water_body"` (dans LAYER_TO_TERRAIN du corridor A*)
- Classification: STRUCTURAL_LAYER (non fonctionnelle — utilisee pour terrain, pas pour corridors)

### Source des donnees
| Composant | Source | Donnees reelles? |
|-----------|--------|:----------------:|
| Zones hydro (polygones) | Bruit Simplex procedurale | **NON** |
| HydrographyOverlayLayer (WMS) | NFIS-QC.hydro (ca.nfis.org) | **OUI** |
| water_bodies_qc.py (embedded) | Coordonnees manuelles lac/riviere | **OUI** |
| Cache OSM | data/osm_cache/*.json | PARTIEL (9 micro-polygones) |

**CONSTAT CRITIQUE** : Les zones hydro procedurales NE correspondent PAS aux lacs/rivières reels.
Elles sont generees par bruit mathematique et peuvent apparaitre n'importe ou,
independamment de la realite du terrain.

---

## POINT 2 — POURQUOI CES 2 ZONES NE SONT PAS UNIFIEES

### Logique actuelle de fusion
**`pipeline_v7.py`** — `_merge_nearby_same_type_zones()`

```
Algorithme:
1. Grouper les zones par layer_id
2. Pour chaque paire dans un groupe:
   - Calculer distance Haversine entre centroides
   - Si distance < 200m → unifier (Union-Find)
3. Pour chaque cluster unifie:
   - Shapely unary_union des polygones
   - Prendre le meilleur score comme base
   - Extraire la plus grande composante si MultiPolygon
```

### Cause precise de la non-fusion
| Cause | Detail |
|-------|--------|
| **Seuil de distance trop restrictif** | 200m entre centroides. Deux zones hydro proches visuellement mais dont les centroides sont a 250m+ ne fusionnent PAS |
| **Bruit Simplex multi-pics** | Le bruit genere naturellement des pics isoles. Chaque pic produit un polygone distinct |
| **Conversion en cercles 600m** | Apres conversion, deux cercles 600m dont les centres sont a 300m se chevauchent visuellement mais restent geometriquement distincts |
| **MultiPolygon → plus grand seul** | Si unary_union produit un MultiPolygon, seule la plus grande composante est gardee. Les petites sont PERDUES |

### Cas ou la fusion est volontairement evitee
- Zones de types differents (alimentation ≠ repos) → jamais fusionnees
- Meme type mais centroides > 200m → pas fusionnees (par design, pour eviter de creer des mega-zones non ecologiques)

### Limitations connues
| Limitation | Impact |
|------------|--------|
| Bruit Simplex ≠ donnees reelles | Zones hydro procedurales ne correspondent pas aux lacs reels |
| Seuil 200m fixe | Inadequat pour plans d'eau > 400m de diametre |
| Pas de fusion post-circle | Deux cercles 600m chevauchants restent deux entites distinctes |
| max_cells=2000 dans terrain_grid | Grille A* tronquee si trop de zones |

---

## POINT 3 — ARBORESCENCE COMPLETE DES ZONES

### Schema detaille du pipeline

```
                    DONNEES SOURCES
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
  behavioral_        srtm_          cache OSM
  rasterizer.py    provider_v7.py  (osm_cache/)
  (Simplex noise)  (DEM real data) (9 polygones)
          │              │              │
          ▼              │              │
  generate_layer_        │              │
  raster()               │              │
  - 15 couches           │              │
  - grille 2D            │              │
          │              │              │
          ▼              ▼              ▼
  zone_engine_core_v2.py ─── MOTEUR CENTRAL ───
  generate_organic_zones()
          │
          ├── _process_single_layer() × 15 couches
          │     ├── generate_layer_raster() → grille 2D
          │     ├── Contour extraction (marching squares)
          │     ├── Polygon simplification (Chaikin)
          │     └── _convert_features_to_circles() → cercles 600m
          │
          ├── process_zones_v7() (pipeline_v7.py)
          │     ├── Exclusion Shapely (urbain, anthropique)
          │     ├── _merge_nearby_same_type_zones() (seuil 200m)
          │     ├── Enrichissement V7 (score, season, metadata)
          │     └── Classification ZONE_TYPE_MAP
          │
          ├── _generate_corridors_10x() (corridor_10x.py)
          │     ├── _build_terrain_grid() → grille A*
          │     ├── CorridorPathfinder.find_corridor_path() → A*
          │     ├── Fallback Bezier (V7.2: deflection anti-eau)
          │     └── _filter_corridors_water() (V7.2: post-filtre)
          │
          └── Assemblage final → GeoJSON response
```

### Sources par type de zone

| Type zone | Moteur | Fichier generateur | Bruit/reel | Params Simplex |
|-----------|--------|-------------------|:---------:|----------------|
| **hydro** | M1 | behavioral_rasterizer.py:267 | BRUIT | freq=0.0008/0.0015, drainage<0.15 |
| alimentation | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=5, freq=0.0015, thresh=0.48 |
| repos | M1 | behavioral_rasterizer.py:273 | BRUIT | foret>0.5 → 0.7+0.3*foret |
| rut | M1 | behavioral_rasterizer.py:281 | BRUIT | edge>0.4 → 0.5+0.5*edge |
| habitat | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=4, freq=0.0010, thresh=0.50 |
| corridors | M1 | behavioral_rasterizer.py:260 | BRUIT | elongation + angle fractal |
| affuts | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=5, freq=0.0016, thresh=0.55 |
| trajets | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=5, freq=0.0018, thresh=0.45 |
| salines | M1 | behavioral_rasterizer.py:277 | BRUIT | v>0.82 → 1.0, sinon 0.1 (rare) |
| pentes | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=4, freq=0.0012, thresh=0.50 |
| ndvi | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=5, freq=0.0010, thresh=0.45 |
| peuplements | M1 | behavioral_rasterizer.py (default) | BRUIT | octaves=3, freq=0.0007, thresh=0.52 |

### Fichiers cles
| Fichier | Role | Lignes cles |
|---------|------|-------------|
| `behavioral_rasterizer.py` | Generation Simplex par couche | L25-41 (LAYER_PARAMS), L260-285 (logique par layer) |
| `zone_engine_core_v2.py` | Moteur central (contour, cercle, corridor, terrain) | L645 (_convert_features), L720 (_generate_corridors_10x), L927 (_build_terrain_grid), L1727 (generate_organic_zones) |
| `pipeline_v7.py` | Pipeline post-traitement (merge, enrichissement) | L44 (_merge_nearby), L156 (process_zones_v7) |
| `corridor_10x.py` | A* pathfinding + terrain costs | L457 (TERRAIN_COSTS), L515 (CorridorPathfinder) |
| `srtm_provider_v7.py` | Donnees terrain reelles (DEM) | SRTM cache, altitude, pente |
| `water_bodies_qc.py` | Base eau embarquee V7.2 (54 lacs) | Hotspots seulement |

---

## POINT 4 — LOGIQUE INTERNE — EXCLUSIONS ET PRIORITES

### Exclusions eau vs corridors
| Regle | Implementation | Fichier |
|-------|---------------|---------|
| Corridors evitent eau | `water_body cost = 999.0` (A*) | corridor_10x.py:488 |
| Post-filtre eau | `_filter_corridors_water()` (Shapely intersection) | zone_engine_core_v2.py |
| Bezier anti-eau | Deflection 2.5x si obstacle centre | zone_engine_core_v2.py |
| Affuts/salines exclues si hydro | Ray-casting BCE-4X (frontend) | MonTerritoireBionicPage.jsx:907-944 |

### Exclusions eau vs habitat
| Regle | Implementation | Fichier |
|-------|---------------|---------|
| Cercles 600m exclus si sur eau | `_circle_on_water()` | zone_engine_core_v2.py |
| Cercles 600m exclus si urbain | `_circle_on_urban()` | zone_engine_core_v2.py |
| Meta-exclusion urbaine 2km | `center_in_urban_meta_zone()` | zone_engine_core_v2.py |

### Priorites entre types de zones
```
Priorite de rendu (frontend):
1. Corridors (au-dessus de tout)
2. Affuts/Salines (interactifs)
3. Zones fonctionnelles (alimentation, repos, rut, habitat)
4. Zones structurelles (hydro, pentes, altitude, ndvi)
5. Overlays (hydrographie WMS, contours)
```

### Regles de franchissabilite (corridor A*)
| Terrain | Cost | Franchissable? |
|---------|:----:|:--------------:|
| valley, coulee, wooded_strip, riparian | 1.0-1.2 | IDEAL |
| mixed_forest, mature_forest | 1.4-1.6 | BON |
| open_field, agriculture | 2.5-3.0 | ACCEPTABLE |
| urban_edge, road_crossing | 4.5-5.0 | DIFFICILE |
| urban, highway | 10-12 | TRES DIFFICILE |
| cliff | 15 | QUASI-IMPOSSIBLE |
| **water_body** | **999.0** | **IMPASSABLE** (V7.2) |

---

## POINT 5 — VALIDATION INSTITUTIONNELLE

### Conformite norme maitresse "Mon Territoire"
| Composant | Statut |
|-----------|:------:|
| behavioral_rasterizer.py | **INTOUCHE** |
| zone_engine_core_v2.py (generate_organic_zones) | **INTOUCHE** |
| pipeline_v7.py (process_zones_v7) | **INTOUCHE** |
| srtm_provider_v7.py | **INTOUCHE** |
| zone_penalty_engine.py | **INTOUCHE** |

### Ecarts identifies
| Ecart | Gravite | Detail |
|-------|:-------:|--------|
| Hydro = bruit Simplex ≠ donnees reelles | **MAJEUR** | Zones hydro procedurales ne correspondent pas aux lacs reels du Quebec |
| Seuil fusion 200m insuffisant pour hydro | MODERE | Plans d'eau > 400m de diametre ne sont pas unifies |
| max_cells=2000 dans terrain_grid | MINEUR | Grille A* potentiellement tronquee |

### Conformite BCE-4X
| Regle | Statut |
|-------|:------:|
| ZERO LOSS | CONFORME |
| ZERO REGRESSION | CONFORME |
| ZERO INTERPRETATION | CONFORME |
| ZERO DOUBLON | ECART — 2 zones hydro non unifiees |
| ZERO OBSOLESCENCE | CONFORME (post-filtre V7.2 actif) |

---

## POINT 6 — PROPOSITIONS DE SOLUTIONS

### Option A — Augmenter le seuil de fusion hydro
```
Modification: _merge_nearby_same_type_zones()
→ Seuil hydro = 600m (au lieu de 200m universel)
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | Faible (1 parametre) |
| Impact terrain | Plans d'eau > 400m unifies |
| Impact performance | Negligeable |
| Compatibilite Mon Territoire | HAUTE (changement de parametre seulement) |
| Risque | Pourrait fusionner des zones hydro distinctes (ruisseau vs lac voisin) |

### Option B — Union geometrique post-merge pour hydro
```
Modification: Ajouter une etape apres _merge_nearby_same_type_zones()
→ Shapely unary_union de TOUTES les zones hydro
→ Decomposer en composantes connexes distinctes
→ Chaque composante = une zone hydro unifiee
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | Modere (1 fonction supplementaire) |
| Impact terrain | Toutes les zones hydro chevauchantes unifiees |
| Impact performance | Faible (Shapely operation locale) |
| Compatibilite Mon Territoire | HAUTE (post-traitement non-destructif) |
| Risque | Faible (operee APRES la generation, pas pendant) |

### Option C — Remplacer bruit Simplex hydro par donnees reelles
```
Modification: behavioral_rasterizer.py (hydro layer)
→ Utiliser MAJOR_WATER_BODIES_QC comme source de verite
→ Rasteriser les cercles eau dans la grille hydro
→ Eliminer le bruit Simplex pour la couche hydro
```
| Critere | Evaluation |
|---------|-----------|
| Impact technique | ELEVE (refonte couche hydro) |
| Impact terrain | PARFAIT (correspondance 1:1 avec lacs reels) |
| Impact performance | Amelioration (moins de calculs) |
| Compatibilite Mon Territoire | **FAIBLE** (modification de la logique maitresse) |
| Risque | Modification structurelle du rasterizer |

### RECOMMANDATION EMERGENT
**Option B** est recommandee :
- Post-traitement non-destructif (execute APRES la generation)
- Unification geometrique parfaite (Shapely unary_union)
- Aucune modification de la logique maitresse
- Risque minimal, resultat maximal
- Compatible BCE-4X ZERO REGRESSION

---

## POINT 7 — RESUME ET VALIDATION

### Cause racine
Les zones hydro sont generees par **bruit Simplex procedurale** (et non par donnees hydro reelles).
Deux pics de bruit proches generent deux polygones distincts qui ne sont pas unifies
car le seuil de fusion (200m entre centroides) est trop restrictif pour les plans d'eau.

### Corrections deja appliquees (directives precedentes)
| Correction | Statut |
|-----------|:------:|
| water_body cost = 999.0 (IMPASSABLE) | FAIT |
| Bezier anti-eau (deflection) | FAIT |
| Post-filtre _filter_corridors_water() | FAIT |
| Toggle "Eau" dans panneau de controle | FAIT |
| Base eau embarquee V7.2 (54 lacs) | FAIT (hotspots seulement) |

### Correction proposee (en attente validation STEEVE-MAX)
| Option | Description | Recommandee? |
|--------|-------------|:------------:|
| A | Seuil fusion hydro 200m → 600m | Non (risque de sur-fusion) |
| **B** | **Union geometrique post-merge hydro (Shapely)** | **OUI** |
| C | Remplacer bruit par donnees reelles | Non (modifie norme maitresse) |

---

**Rapport genere** : 2026-04-05
**Autorite** : STEEVE-MAX
**Protocole** : BCE-4X GOLDEN V6+
