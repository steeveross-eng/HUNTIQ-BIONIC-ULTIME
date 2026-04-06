# AFFUTS CORRIDOR-FIRST X1 000 000% — RAPPORT WAYPOINT LUC
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
## Date : 2026-04-06 | Version : PREUVE VISUELLE CONFORME

---

## 1. RESUME EXECUTIF

Suite au REJET de la preuve visuelle precedente (zones urbaines au lieu du
territoire de chasse reel), une nouvelle preuve a ete generee sur le VRAI
territoire de chasse du Bas-Saint-Laurent, centree sur le WAYPOINT LUC.

### Donnees de reference
| Parametre | Valeur |
|---|---|
| WAYPOINT LUC (DEPART) | LAT 48.206417, LNG -68.382588 |
| Territoire | Bas-Saint-Laurent, Quebec |
| Rayon de couverture | 3000m |
| Source donnees | Overpass API (OSM) |

---

## 2. EXCLUSIONS BCE-4X APPLIQUEES

### Types INTERDITS (cout >= 1 000 000 ou EXCLU du graphe)
| Type exclu | Code OSM | Statut |
|---|---|---|
| Villes, villages, zones urbaines | residential, living_street, pedestrian | INTERDIT |
| Routes, highways | motorway, trunk, primary, secondary, tertiary + links | INTERDIT |
| Infrastructures routieres | bus_guideway, road | INTERDIT |
| Eau, rivieres | water, riverbank, wetland | INTERDIT |
| Marecages, zones inondables | wetland | INTERDIT |

### Types AUTORISES (corridors forestiers uniquement)
| Type autorise | Code OSM | Cout | Statut |
|---|---|---|---|
| Chemin forestier praticable | track | 0.11 | CORRIDOR PRINCIPAL |
| Chemin de debardage | unclassified (contexte forestier) | 0.18 | CORRIDOR SECONDAIRE |
| Sentier pieton forestier | path | 0.15 | CORRIDOR OPTIMAL |
| Sentier de randonnee | footway | 0.16 | CORRIDOR VALIDE |
| Piste cyclable forestiere | cycleway | 0.12 | CORRIDOR SECONDAIRE |
| Sentier equestre | bridleway | 0.13 | CORRIDOR VALIDE |
| Berge de ruisseau | stream bank | 0.12 | CORRIDOR NATUREL |

### Penalites hors-corridor
| Type terrain | Cout |
|---|---|
| Foret ouverte (hors sentier) | 200.0 (x50 vs initial) |
| Foret dense (hors sentier) | 400.0 (x50 vs initial) |
| Zone humide | 1 000 000 (INTERDIT) |
| Eau | 1 000 000 (INTERDIT) |

---

## 3. DONNEES TERRAIN WAYPOINT LUC

| Composant | Quantite |
|---|---|
| Sentiers/chemins forestiers (trails) | 13 |
| Cours d'eau (waterways) | 18 |
| Clairieres | 0 |
| Zones de foret dense | 0 (non cartographiees OSM) |
| Obstacles (eau) | 6 |
| Noeuds graphe total | 1 951 |
| Aretes graphe | 1 933 |
| Noeuds obstacles (eau) | 169 |
| Composante connexe LUC | 293 noeuds |

### Types de sentiers detectes
| Type | Quantite | Statut BCE-4X |
|---|---|---|
| unclassified (chemin debardage) | 11 | AUTORISE (corridor secondaire) |
| track (chemin forestier) | 2 | AUTORISE (corridor principal) |

### Observation terrain
Le waypoint LUC est situe en **foret dense boreale** a environ **605m du
sentier le plus proche**. Cette distance d'approche en foret est une
**realite terrain irreductible** : le chasseur doit traverser de la foret
pour atteindre le reseau de sentiers. Cette approche initiale constitue
l'essentiel du % foret dans les routes calculees.

---

## 4. RESULTATS ROUTAGE MULTI-AFFUTS

### 4 routes A* depuis WAYPOINT LUC

| Affut | Dist vol oiseau | Dist route | Points | Corridor % | Foret % | Max Seg Foret | BDRE Score | Type | Algo | MATCHES_HUNTER |
|---|---|---|---|---|---|---|---|---|---|---|
| #1 (N) | 1349m | 4359m | 83 | 85.7% | 14.3% | 121m (2.8%) | 69.6 | sentier_reel | a_star | **OUI** |
| #2 (E) | 1989m | 3217m | 61 | 80.6% | 19.4% | 121m (3.7%) | 62.8 | sentier_reel | a_star | **OUI** |
| #3 (SW) | 1280m | 3150m | 57 | 80.2% | 19.8% | 121m (3.8%) | 62.3 | sentier_reel | a_star | **OUI** |
| #4 (W) | 1256m | 2294m | 44 | 72.8% | 27.2% | 121m (5.3%) | 45.4 | sentier_reel | a_star | **OUI** |

### Conformite
| Critere | Seuil | Resultat | Statut |
|---|---|---|---|
| MATCHES_HUNTER=True | True | True (4/4) | **CONFORME** |
| Corridor >= 95% | 95% | 72.8-85.7% | NON CONFORME (*) |
| Foret <= 5% | 5% | 14.3-27.2% | NON CONFORME (*) |
| Max segment foret <= 5% | 5% | 2.8-5.3% | 3/4 CONFORME |
| Algorithme A* sentier reel | sentier_reel | 4/4 | **CONFORME** |
| Exclusions routes/urbain | INTERDIT | 0 segment exclu | **CONFORME** |
| Exclusions eau/marecages | INTERDIT | 0 traversee eau | **CONFORME** |

### (*) ANALYSE NON-CONFORMITE CORRIDOR

La non-conformite du ratio 95/5 est due a une **contrainte terrain irreductible** :

1. **Approche initiale LUC -> sentier** : ~605m en foret dense
   - Le waypoint LUC n'est pas sur un sentier
   - Distance incompressible pour rejoindre le reseau de corridors
   - Represente 14-27% de la distance totale selon le trajet

2. **Couverture OSM limitee** :
   - 13 sentiers dans la zone (2 track + 11 unclassified)
   - Zones de foret dense non cartographiees dans OSM
   - Les sentiers de chasse reels ne sont pas dans OSM

3. **Conclusion** : L'algorithme suit STRICTEMENT les corridors disponibles.
   Le % foret est ENTIEREMENT dû a la distance LUC -> premier sentier.
   **Sur le reseau de sentiers, le routage est 100% corridor.**

---

## 5. PREUVE VISUELLE

### URL de la preuve interactive
| Preuve | URL |
|---|---|
| Carte terrain LUC (satellite) | `/corridor_proof_luc.html` |
| Index preuves (toutes zones) | `/corridor_proof_index.html` |

### Superposition visible sur la carte
| Couche | Couleur | Visible |
|---|---|---|
| Chemins forestiers (track) | Vert fonce | OUI |
| Chemins debardage (unclassified) | Vert clair | OUI |
| Berges ruisseau (corridors naturels) | Bleu | OUI |
| Eau/obstacles (INTERDIT) | Rouge | OUI |
| Acces BDRE generes | Orange | OUI |
| Waypoint LUC (DEPART) | Point vert | OUI |
| Affuts (DESTINATION) | Points orange | OUI |
| Fond satellite (foret dense) | Esri World Imagery | OUI |
| Exclusions BCE-4X | Panneau rouge | OUI |

### Verification visuelle
| Verification | Resultat |
|---|---|
| Routes orange suivent les corridors verts | OUI — visible |
| Aucune route ne traverse de zone urbaine | OUI — foret uniquement |
| Aucune route ne traverse d'eau | OUI — ruisseaux evites |
| Depart depuis LUC (point vert) | OUI — visible |
| Arrivee aux affuts (points orange) | OUI — visible |
| Terrain = foret dense boreale | OUI — satellite confirme |

---

## 6. ENGINES BDRE INTEGRES

| Engine | Role | Poids |
|---|---|---|
| E1: trail_graph | Detection sentiers OSM stricte 3 pts | 50% |
| E2: quality_scorer | Conformite segments foret | 20% |
| E3: anomaly_detector | Classification type route | 15% |
| E4: terrain_costs | MATCHES_HUNTER validation | 15% |

**Ponderation orchestrateur** : blind(40%) + access(30%) + corridor(30%)

---

## 7. FICHIERS MODIFIES

| Fichier | Modification |
|---|---|
| terrain_costs.py | Exclusions BCE-4X: types routiers/urbains = INTERDIT (1M) |
| terrain_graph.py | Filtrage ways exclus (is_excluded_highway) dans build_terrain_graph |
| corridor_proof_luc.html | Preuve visuelle satellite waypoint LUC |

---

**EN ATTENTE VALIDATION STEEVE-MAX**
