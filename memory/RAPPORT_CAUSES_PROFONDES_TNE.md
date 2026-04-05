# RAPPORT CAUSES PROFONDES TNE
## Audit Institutionnel Approfondi | BCE-4X GOLDEN V6+
## Directive STEEVE-MAX | Date: 2026-04-05

---

## 1. RESUME EXECUTIF

Les sentiers vers affuts sont des FALLBACKS en ligne droite (3 points)
car il n'existe AUCUNE donnee de sentier OSM a moins de 1000m des affuts.
Ce n'est PAS un defaut de code ou de parametrage — c'est un probleme
fondamental de DONNEES TERRAIN ABSENTES.

---

## 2. DEFAILLANCES STRUCTURELLES (7)

### DS-1: ABSENCE TOTALE DE SENTIERS OSM DANS LA ZONE DES AFFUTS

| Metrique | Valeur |
|---|---|
| Nombre de ways trail (highway=*) dans le cache TNE | 5 |
| Types de ways | TOUTES unclassified (routes non classees) |
| Noeud trail le + proche de MOBILE 38.9 | **1887m** |
| Noeud trail le + proche de MOBILE 29.8 | **1407m** |
| Noeud trail le + proche de MOBILE 12a | **1016m** |
| Noeud trail le + proche de MOBILE 12b | **1171m** |
| Ways de type path/footway/track/bridleway | **ZERO** |
| Sentiers forestiers dans OSM | **ZERO** |

**Preuve**: Les sentiers de chasse visibles sur l'imagerie satellite ne sont
PAS cartographies dans OpenStreetMap. Ce territoire est en zone forestiere
eloignee (Bas-Saint-Laurent / Rimouski) avec une couverture OSM MINIMALE.

### DS-2: CACHE ACCESS ENGINE V6 VIDE POUR CETTE ZONE

| Parametre | Valeur |
|---|---|
| Fichier cache | f2f2e17eb19571c58fd86968fedec7c3.json.gz |
| Taille | 159 bytes (fichier quasi-vide) |
| Centre | lat=48.20615, lng=-68.37985 |
| Rayon | 3000m |
| Nodes | **0** |
| Edges | **0** |
| Requete Overpass | Executee le 2026-04-05 — resultat: VIDE |

**Preuve**: L'Access Engine V6 a lance une requete Overpass pour cette zone
et a recu ZERO resultat. Le cache de 159 bytes est la preuve que le serveur
Overpass n'a retourne aucune donnee de sentier.

### DS-3: ENGINE_OSM_LITE STRUCTURELLEMENT INOPERANT

| Composant | Etat |
|---|---|
| load_trail_segments_from_access_cache() | 0 segments (cache AE vide) |
| load_exclusions_from_osm_cache() | 9 exclusions (eau seulement) |
| enrich_terrain_grid() | Enrichit UNIQUEMENT les corridors (zone_engine_core_v2) |
| Connexion au TNE | **AUCUNE** |
| Connexion aux routes d'acces affuts | **AUCUNE** |

**Cause**: ENGINE_OSM_LITE consomme le cache Access Engine V6 qui est VIDE
pour cette zone. Meme s'il etait connecte au TNE, il n'aurait rien a injecter.

### DS-4: SEUIL SNAP TROP RESTRICTIF (secondaire)

| Parametre | Valeur | Impact |
|---|---|---|
| route_terrain max_snap_dist_m | 1200m | 2/4 affuts inatteignables |
| nearest_node max_dist_m | 1200m | Meme effet |
| _snap_to_segment max_dist_m | 1200m | Meme effet |
| Noeud le + proche de MOBILE 38.9 | 1887m | > 1200m → rejet |
| Noeud le + proche de MOBILE 29.8 | 1407m | > 1200m → rejet |

**Note**: Cette defaillance est SECONDAIRE. Meme si le seuil etait augmente
a 2000m, les routes passeraient par les 5 routes non classees a l'EST du
territoire — NE suivraient toujours PAS les sentiers reels.

### DS-5: GRAPHE TNE DECONNECTE

| Metrique | Valeur |
|---|---|
| Composantes connexes | 2 |
| CC-0 | 105 noeuds, lat=[48.176,48.183] lng=[-68.376,-68.356] |
| CC-1 | 81 noeuds, lat=[48.187,48.204] lng=[-68.364,-68.347] |

**Impact**: Si le point de depart est dans CC-0 et l'affut est le + proche
de CC-1, le routeur A*/Dijkstra ne trouvera AUCUN chemin entre les deux
composantes deconnectees.

### DS-6: FALLBACK = ESTIMATION LINEAIRE (3 POINTS)

| Parametre | Valeur |
|---|---|
| Fichier | bionic_stand_recommendation_engine/engine.py:175-204 |
| Comportement | Quand TNE echoue → 3 points (start, entry_vent, stand) |
| Points generes | start(GPS) → entry(vent) → stand → 3 points en ligne |
| trail_type retourne | "estimation" |
| Contournement eau | NON |
| Contournement foret | NON |
| Utilisation terrain | NON |

### DS-7: POOL node_coords PARTAGE — FAUX POSITIF

Les 575 node_coords dans le cache terrain sont un POOL PARTAGE entre
toutes les categories (trails, obstacles, waterways, forest, clearings).
Les 389 "orphelins" dans la categorie trails sont en realite des noeuds
de COURS D'EAU, pas des sentiers perdus.

| Noeud proche affut | Distance | Categorie reelle |
|---|---|---|
| 1294852543 (→ MOBILE 38.9) | 315m | **Waterway** (pas trail) |
| 1294919682 (→ MOBILE 29.8) | 357m | **Waterway** (pas trail) |
| 1294913101 (→ MOBILE 12a) | 72m | **Waterway** (pas trail) |
| 1294875487 (→ MOBILE 12b) | 20m | **Waterway** (pas trail) |

---

## 3. INCOHERENCES TERRAIN vs PIPELINE

### 3.1 Ce qui est visible sur satellite vs ce qui est dans les donnees

| Element visible | Dans OSM | Dans TNE | Dans Access Engine | Dans ENGINE_OSM_LITE |
|---|---|---|---|---|
| Chemin forestier principal (E-O) | NON | NON | NON | NON |
| Piste ATV nord (N-S) | NON | NON | NON | NON |
| Sentier lac (sinueux) | NON | NON | NON | NON |
| Chemin du mont Longue-Vue | OUI | OUI (81 noeuds) | NON | NON |
| 4 routes non classees | OUI | OUI (105 noeuds) | NON | NON |
| Lac Laurent | OUI | OUI (obstacle) | NON | OUI (eau) |
| 7 cours d'eau | OUI | OUI (exclu) | NON | OUI (eau) |

### 3.2 Coherence inter-modules

| Flux | Etat | Detail |
|---|---|---|
| TNE → StandsMapLayer | DEFAILLANT | Fallback 3-point, pas de sentier reel |
| ENGINE_OSM_LITE → corridor pipeline | OPERATIONNEL | Enrichit avec eau (seules donnees dispo) |
| ENGINE_OSM_LITE → TNE | **NON CONNECTE** | Aucun flux de donnees |
| ENGINE_OSM_LITE → Access Engine | **NON CONNECTE** | Aucun flux de donnees |
| Access Engine → TNE | **NON CONNECTE** | Cache vide de toute facon |
| HUMAN_TRAJET_COSTS → corridors | OPERATIONNEL | Mais grille sans sentiers reels |
| HUMAN_TRAJET_COSTS → routes affuts | **NON UTILISE** | Routes affuts utilisent TNE, pas A* |

---

## 4. PLAN DE CORRECTION INSTITUTIONNEL

Les corrections A→F precedemment proposees sont des PATCHES PARAMETRIQUES.
Elles ne resolvent pas le probleme fondamental: **ABSENCE DE DONNEES TERRAIN**.

### Solution institutionnelle: PIPELINE HYBRIDE MULTI-SOURCE

#### Niveau 1 — WATERWAY ROUTING (donnees EXISTANTES)
Les cours d'eau (7 waterways, 357 noeuds) sont les SEULS elements terrain
proches des affuts. Dans la realite, les chasseurs suivent souvent les berges
de ruisseaux pour naviguer en foret. Integrer les waterways comme sentiers
a faible cout dans le graphe TNE.

#### Niveau 2 — TERRAIN TOPOLOGY PATHFINDING (donnees DERIVEES)
Utiliser les donnees topographiques disponibles (pente, altitude, densite
forestiere) pour generer des SENTIERS SYNTHETIQUES qui suivent les chemins
naturels (vallees, coulees, lisieres, cretes). Ces sentiers n'existent
pas dans OSM mais correspondent a la realite du terrain.

#### Niveau 3 — CORRIDOR A* FALLBACK (composant EXISTANT)
Quand le TNE echoue (pas de sentier OSM), utiliser le pathfinder A* de
corridor_10x avec HUMAN_TRAJET_COSTS au lieu du fallback 3-point lineaire.
Ce pathfinder evite au moins la foret dense et l'eau.

#### Niveau 4 — GPS TRACK IMPORT (donnees FUTURES)
Permettre aux guides de telecharger leurs traces GPS reelles (GPX).
Ces traces deviennent les donnees de reference pour les sentiers vers affuts
de chaque territoire. Priorite ultime: les donnees REELLES du terrain.

---

## 5. CRITERES DE VALIDATION STEEVE-MAX

Pour que BIONIC OS V8.5 (ou V8.6) soit valide, les conditions suivantes
doivent etre remplies:

1. **ZERO route d'estimation lineaire** quand des elements terrain (waterways,
   topographie, zones) existent dans la zone
2. **Les routes suivent les cours d'eau** quand ils sont le seul element
   navigable disponible
3. **Les routes contournent l'eau et la foret dense** via A* terrain
4. **trail_type != "estimation"** pour au moins 3/4 des affuts
5. **Validation visuelle**: les routes bleues doivent etre coherentes avec
   la topographie visible sur satellite
6. **Conformite BCE-4X**: ZERO doublon, ZERO regression, ZERO loss

---

## 6. CONFORMITE BCE-4X

| Critere | Statut de l'audit |
|---------|----------|
| ZERO INTERPRETATION | CONFORME — Chaque defaillance demontree avec preuve numerique |
| ZERO DOUBLON | INFRACTION IDENTIFIEE — 3 pipelines paralleles non connectes (TNE, ENGINE_OSM_LITE, corridors) |
| ZERO REGRESSION | CONFORME — Aucune modification effectuee |
| ZERO OBSOLESCENCE | INFRACTION IDENTIFIEE — Cache vide non invalide, donnees absentes non signalees |
| ZERO LOSS | INFRACTION IDENTIFIEE — 5 ways OSM existantes mais inutilisees (hors portee snap) |

---

**STATUT: AUDIT CAUSES PROFONDES COMPLÉTÉ**
**AUCUNE CORRECTION APPLIQUÉE — EN ATTENTE VALIDATION STEEVE-MAX**
**BIONIC OS V8.5: NON VALIDÉ**
