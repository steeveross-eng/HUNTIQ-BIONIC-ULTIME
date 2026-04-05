# RAPPORT AUDIT CIBLÉ — SENTIERS VERS AFFÛTS
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-05 | Branche: Work1

---

## 1. RÉSUMÉ EXÉCUTIF

Les routes d'accès aux affûts (lignes BLEUES sur la carte) sont des
**estimations en ligne droite (3 points)**, PAS des routes réelles
suivant les sentiers. La chaîne de défaillance est complète et
documentée ci-dessous.

---

## 2. CHAÎNE DE DÉFAILLANCE

```
1. recommend_stands(48.19, -68.39) → ligne 223
2. get_terrain_nav(48.19, -68.39, radius_m=2000) → TNE init
3. Overpass API → 186 noeuds, 5 ways (toutes "unclassified")
4. nearest_node(start, max_dist=1200m) → None
   *** Noeud le + proche = 1269m > seuil 1200m ***
5. navigate_terrain(graph, start, stand) → None
6. _generate_approach_path() → FALLBACK 3-point line
7. Rendu frontend: ligne bleue en pointillé (estimation)
```

---

## 3. CAUSES RACINES (5)

### CAUSE A — Seuil nearest_node trop restrictif
- **Fichier**: engines/terrain_nav/terrain_graph.py:104
- **Valeur actuelle**: max_dist_m = 1200.0
- **Impact**: Le noeud le plus proche du centre est à 1269m → exclus
- **Conséquence**: Le routeur TNE ne peut pas trouver de point de départ
- **Correction**: Augmenter à 2500m pour zones rurales

### CAUSE B — Rayon de recherche TNE insuffisant
- **Fichier**: modules/bionic_stand_recommendation_engine/engine.py:223
- **Valeur actuelle**: get_terrain_nav(lat, lng) → default radius_m=2000
- **Impact**: Les sentiers sont entre 1269m et 3567m du centre
- **Conséquence**: Couverture partielle, noeuds lointains non utilisables
- **Correction**: Augmenter à 3000m

### CAUSE C — OSM très creux pour zone forestière
- **Fichier**: data/terrain_cache/48.19_-68.39_2000_v1.json.gz
- **Données disponibles**:
  - 5 trail ways (toutes "unclassified")
  - "Chemin du mont Longue-Vue" (81 noeuds, unpaved)
  - ZERO path, footway, track, bridleway
  - 2 obstacles (dont Lac Laurent)
  - 7 waterways
  - 0 zones forêt, 0 clairières
- **Impact**: Les sentiers de chasse réels (visibles sur satellite) ne sont PAS dans OSM
- **Conséquence**: Même avec un graphe non-vide, les chemins forestiers sont absents

### CAUSE D — Fallback = ligne droite
- **Fichier**: modules/bionic_stand_recommendation_engine/engine.py:175-204
- **Comportement**: Quand TNE échoue → 3 points (start, entry_vent, stand)
- **Impact**: Aucun contournement de forêt, eau, obstacles
- **Conséquence**: Les lignes bleues coupent à travers la forêt dense

### CAUSE E — ENGINE_OSM_LITE déconnecté du TNE
- **Fichier**: modules/bionic_engine_p0/services/engine_osm_lite.py
- **Comportement**: Enrichit la grille terrain des CORRIDORS (zone_engine_core_v2)
- **Impact**: N'enrichit PAS le graphe TNE utilisé par les routes d'accès affûts
- **Conséquence**: Deux systèmes parallèles non synchronisés

---

## 4. DONNÉES TERRAIN PAR AFFÛT

### Affût 1 (MOBILE 38.9)
- Position: ≈(48.196, -68.393) (score le plus élevé)
- Noeud trail le plus proche: Node 1106979739 (48.183, -68.376) → 1620m
- nearest_node(affût): None (> 1200m)
- Route calculée: ESTIMATION 3 points (ligne droite)
- Sentiers réels visibles: Chemin forestier E-O à ~200m au nord (NON dans OSM)
- Écart: Route coupe 100% forêt dense au lieu de suivre le chemin visible

### Affût 2 (MOBILE 29.8)
- Position: ≈(48.185, -68.395)
- Noeud trail le plus proche: Node 1106979725 (48.183, -68.376) → 1650m
- nearest_node(affût): None
- Route calculée: ESTIMATION 3 points
- Sentiers réels: Piste ATV N-S à ~300m à l'est (NON dans OSM)
- Écart: Route traverse un lac et une zone humide

### Affût 3 (MOBILE 12)
- Position: ≈(48.178, -68.388)
- nearest_node(affût): None
- Route calculée: ESTIMATION 3 points
- Sentiers réels: Chemin du mont Longue-Vue passe à ~400m (DANS OSM)
- Écart: Route ignore le chemin existant car le noeud est hors portée

---

## 5. INCOHÉRENCES PAR CATÉGORIE

### 5.1 Sentiers mal utilisés
| Sentier | Statut OSM | Utilisé par TNE | Raison |
|---------|-----------|----------------|--------|
| Chemin du mont Longue-Vue | OUI (81 noeuds) | NON | Hors portée nearest_node |
| Chemin forestier N (visible satellite) | NON | NON | Pas dans OSM |
| Piste ATV E (visible satellite) | NON | NON | Pas dans OSM |
| Sentier lac (visible satellite) | NON | NON | Pas dans OSM |

### 5.2 Erreurs de grille terrain
| Erreur | Impact |
|--------|--------|
| Grille comportementale sans sentiers | A* corridor ne suit pas de sentier réel |
| ENGINE_OSM_LITE enrichit corridors, PAS affûts | Routes affûts ignorent les données OSM |
| Resolution 167m (grille) vs 2-5m (sentier réel) | Sentiers invisibles dans la grille |

### 5.3 Erreurs de logique
| Erreur | Fichier | Ligne |
|--------|---------|-------|
| max_dist_m=1200 trop restrictif | terrain_graph.py | 104 |
| radius_m=2000 trop petit | engine.py | 223 |
| Fallback = 3 points (pas de contournement) | engine.py | 188-193 |
| Pas de connecteur virtuel stand→trail | Absent | - |

---

## 6. PROPOSITION DE CORRECTION

### Correction A — nearest_node max_dist
```
terrain_graph.py:104
max_dist_m: 1200.0 → 2500.0
```
Impact: Le noeud à 1269m devient atteignable. +8 noeuds reachables.

### Correction B — TNE search radius
```
bionic_stand_recommendation_engine/engine.py:223
get_terrain_nav(lat, lng) → get_terrain_nav(lat, lng, radius_m=3000)
```
Impact: Plus de sentiers captés dans la zone de recherche.

### Correction C — Connecteurs virtuels stand→trail
Quand nearest_node du stand est loin mais un trail existe dans le graphe:
1. Trouver le noeud trail le plus proche du stand (sans limite)
2. Créer une arête virtuelle (stand→trail) avec coût off-trail élevé
3. Le routeur peut alors: stand → off-trail → trail → suivre sentier

### Correction D — Fallback intelligent
Remplacer le FALLBACK 3-point par:
1. Utiliser le pathfinder A* de corridor_10x avec HUMAN_TRAJET_COSTS
2. Enrichi par ENGINE_OSM_LITE
3. Contourne forêt dense et eau

### Correction E — Connecter ENGINE_OSM_LITE au TNE
Injecter les données Access Engine V6 dans le graphe TNE:
1. Charger les segments sentiers du cache Access Engine
2. Les ajouter comme ways supplémentaires au TerrainGraph
3. Le routeur A* les utilise automatiquement

### Correction F — Cache invalidation
Invalider le cache terrain 48.19_-68.39 après correction du rayon
pour forcer un rechargement avec les nouvelles données.

---

## 7. RECOMMANDATION ULTIME

### Pipeline "Sentiers vers affûts" conforme STEEVE-MAX + BCE-4X:

```
1. recommend_stands(lat, lng)
2. get_terrain_nav(lat, lng, radius_m=3000)  [B]
3. Injecter donnees ENGINE_OSM_LITE dans le graphe  [E]
4. Pour chaque affut:
   a. nearest_node(affut, max_dist=2500m)  [A]
   b. Si None: creer connecteur virtuel  [C]
   c. navigate_terrain(graph, start, stand)
   d. Si echec: fallback A* corridor HUMAN_TRAJET_COSTS  [D]
   e. trail_type = "real" ou "hybrid" ou "estimation_enriched"
5. Cache mise a jour  [F]
```

### Critères de validation ULTIME:
1. Aucune route trail_type="estimation" quand des sentiers OSM existent dans 3km
2. Les routes suivent les sentiers OSM quand ils existent
3. Les routes contournent les zones d'eau et de forêt dense
4. Les routes utilisent HUMAN_TRAJET_COSTS pour les segments off-trail
5. Cohérence visuelle: route bleue alignée avec sentiers satellite

### Conditions pour valider BIONIC OS V8.5 (ou V8.6):
- Toutes les corrections A→F implémentées
- Tests E2E sur le territoire 48.19/-68.39
- nearest_node retourne un noeud pour au moins 3/4 des affûts
- trail_type != "estimation" pour au moins 3/4 des affûts
- Validation visuelle STEEVE-MAX sur carte

---

## 8. CONFORMITÉ BCE-4X

| Critère | Statut | Détail |
|---------|--------|--------|
| ZERO INTERPRÉTATION | CONFORME | Chaque écart démontré avec preuve |
| ZERO DOUBLON | INFRACTION | 2 pipelines terrain parallèles non synchronisés |
| ZERO REGRESSION | CONFORME | Aucune dégradation des trajets existants |
| ZERO OBSOLESCENCE | INFRACTION | Cache terrain avec données incomplètes |
| ZERO LOSS | INFRACTION | Chemin du mont Longue-Vue ignoré malgré données OSM |

---

**STATUT: AUDIT COMPLÉTÉ — EN ATTENTE VALIDATION ET AUTORISATION CORRECTIONS**
**BIONIC OS V8.5: NON VALIDÉ TANT QUE CORRECTIONS A→F NON DÉPLOYÉES**
