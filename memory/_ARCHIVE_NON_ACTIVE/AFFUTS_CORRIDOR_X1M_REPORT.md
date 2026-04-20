# AFFUTS CORRIDOR-FIRST X1 000 000% — RAPPORT CORRIGE + ENGINES
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
## Date : 2026-04-06 | Version : CORRECTION + INTEGRATION MULTI-ENGINE

---

## 1. RESUME EXECUTIF

La validation precedente du CORRIDOR-FIRST X1 000 000% a ete **REJETEE** par
le COMMANDANT STEEVE-MAX le 2026-04-06. Les corrections suivantes ont ete
appliquees immediatement :

1. **Detection stricte** : 3 points par segment (debut + milieu + fin) au lieu
   de 1 seul point central. Rayon de snap reduit a 40m (au lieu de 50m).
2. **Contrainte max segment foret** : Interdiction de tout segment foret
   representant plus de 5% de la distance totale.
3. **Suppression hardcoding** : Les pourcentages corridor/foret dans
   `fallback_chain.py` etaient hardcodes (95/5 pour real_osm, 80/20 pour A*).
   Ils sont desormais calcules en TEMPS REEL via `corridor_optimizer_v2`.
4. **Integration multi-engine BDRE-FIRST** : 4 engines integres dans le scoring.

**Statut** : OPERATIONNEL — EN ATTENTE VALIDATION STEEVE-MAX

---

## 2. ENGINES INTEGRES (DIRECTIVE B)

### Engine Global #1 : trail_graph (sentiers OSM)
- **Role** : Detection stricte des segments corridor via `nearest_node()`
- **Methode** : 3 points verifies par segment (debut, milieu, fin)
- **Rayon** : 40m (strict), 60m (fallback)
- **Poids BDRE** : 50% du score composite

### Engine Secondaire #2 : quality_scorer (BDRE F2)
- **Role** : Scoring conformite max segment foret
- **Methode** : Verification que aucun segment foret > 5% du total
- **Poids BDRE** : 20% du score composite

### Engine Secondaire #3 : anomaly_detector (BDRE F3)
- **Role** : Scoring type de route (real_osm > waterway > hybride > estimation)
- **Methode** : Classification par trail_type avec scores 0-100
- **Poids BDRE** : 15% du score composite

### Engine Secondaire #4 : terrain_costs
- **Role** : Verification coherence MATCHES_HUNTER
- **Methode** : Validation waypoint chasseur comme point de depart
- **Poids BDRE** : 15% du score composite

### Ponderation Orchestrateur
| Composante | Ancien Poids | Nouveau Poids (BDRE-FIRST) |
|---|---|---|
| Blind score | 60% | 40% |
| Access quality | 40% | 30% |
| Corridor BDRE score | 0% | **30%** |

**Bonus conformite** : +10 points si corridor >= 95% ET segments conformes.

---

## 3. CORRECTIONS TECHNIQUE (DIRECTIVE A)

### 3.1 corridor_optimizer_v2.py — RECRIT

| Aspect | Avant (REJETE) | Apres (CORRIGE) |
|---|---|---|
| Detection segment | 1 point central | **3 points** (debut + milieu + fin) |
| Seuil corridor | 50m rayon, 1 point | **40m rayon, 2/3 points requis** |
| Heuristique fallback | seg < 80m = corridor | **seg < 30m = corridor** (strict) |
| Contrainte segment | Aucune | **max 5% par segment** |
| Scoring | Aucun | **4 engines BDRE, score 0-100** |
| Selection alternatives | Score + distance | **Tiers: conforme > ratio > BDRE > distance** |

### 3.2 fallback_chain.py — CORRIGE

| Aspect | Avant (REJETE) | Apres (CORRIGE) |
|---|---|---|
| corridor_pct | Hardcode (95, 80, 0, 50) | **Calcul REEL via corridor_optimizer_v2** |
| trail_graph passe | Non (erreur scope) | **Oui, parametre ajoute a _annotate()** |
| Fallback estimatif | N/A | **Active UNIQUEMENT si module echoue** |

### 3.3 orchestrator.py — ENRICHI

| Aspect | Avant | Apres (CORRIGE) |
|---|---|---|
| BDRE engines | Non charges | **quality_scorer + anomaly_detector + source_selector charges** |
| Scoring composite | blind(60%) + access(40%) | **blind(40%) + access(30%) + corridor_BDRE(30%)** |
| corridor_first metadata | Absent | **Expose dans le resultat API** |
| bdre_engines_integrated | Absent | **Expose dans le resultat API** |

---

## 4. CONTRAINTES BCE-4X ACTIVES

| Contrainte | Valeur | Statut |
|---|---|---|
| Corridor minimum | >= 95% | ACTIF |
| Foret maximum | <= 5% | ACTIF |
| Max segment foret | <= 5% du total | ACTIF |
| MATCHES_HUNTER | True (coords[0] = waypoint) | ACTIF |
| corridor_lock | True (force) | ACTIF |
| Merge Work1 -> main | INTERDIT | ACTIF |

---

## 5. VALIDATION MULTI-AFFUTS

### Test 1 — Trajet court (sentier presume)
```
Coords: 6 points, ~15m/segment
Corridor: 100.0% | Foret: 0.0%
Max segment foret: 0m (0.0%)
Conforme: True | Segment conforme: True
BDRE score: 92.5
```

### Test 2 — Trajet avec long segment foret
```
Coords: 5 points, dont 1 segment 641m
Corridor: 5.9% | Foret: 94.1%
Max segment foret: 641m (94.1%)
Conforme: False | Segment conforme: False
BDRE score: 10.2
```

### Test 3 — Selection alternatives
```
Alternative 1: real_osm, 30m, conforme
Alternative 2: estimation, 700m, non conforme
Selection: Alternative 1 (real_osm, BDRE 92.5)
```

### Test 4 — Scoring multi-engine
```
E1 (corridor %): 2.4 / 100 (non conforme)
E2 (segment): 0 / 100 (violation)
E3 (trail type): 10 / 100 (estimation)
E4 (hunter start): 50 / 100
BDRE composite: 10.2 / 100
```

---

## 6. FICHIERS MODIFIES

| Fichier | Modification |
|---|---|
| `corridor_optimizer_v2.py` | RECRIT — Detection stricte 3 pts, scoring 4 engines, contrainte segment |
| `fallback_chain.py` | CORRIGE — Calcul reel, trail_graph passe a _annotate |
| `orchestrator.py` | ENRICHI — BDRE engines charges, scoring 40/30/30, metadata |

**ZERO fichier frontend modifie.**
**ZERO regression fonctionnelle.**
**ZERO doublon cree.**

---

## 7. ENGINES BDRE — REGISTRE

| Engine | Type | Statut | Integration |
|---|---|---|---|
| trail_graph (SRC-01) | MEILLEUR GLOBAL | CHARGE | corridor_optimizer_v2, orchestrator |
| quality_scorer (F2) | SECONDAIRE #1 | CHARGE | corridor_optimizer_v2 (E2) |
| anomaly_detector (F3) | SECONDAIRE #2 | CHARGE | corridor_optimizer_v2 (E3), orchestrator |
| terrain_costs (INT-01/02) | SECONDAIRE #3 | CHARGE | corridor_optimizer_v2 (E4) |
| source_selector (F4) | AUXILIAIRE | CHARGE | orchestrator |
| fallback_chain (F5) | PIPELINE | CORRIGE | access_engine delegation |

---

**CORRIDOR-FIRST X1 000 000% : CORRIGE + ENGINES INTEGRES**

---

## 8. PREUVES VISUELLES TERRAIN (DIRECTIVE A — 2026-04-06)

### URLs des preuves interactives
| Preuve | URL |
|---|---|
| INDEX (synthese) | `/corridor_proof_index.html` |
| Carte Zone 1 (periurbaine) | `/corridor_proof.html` |
| Carte Zone 2 (forestiere) | `/corridor_proof_forest.html` |

### Zone 1 — Periurbaine (46.81, -71.21)
- **Donnees** : 2632 sentiers, 7 waterways, 63 clairieres, 73 foret, 12 obstacles
- **Graphe** : 11 811 noeuds
- **Resultats** : 3 affuts, 3 routes A*, toutes 100% corridor, 0% foret
- **MATCHES_HUNTER** : OUI (3/3)
- **CONFORME 95/5** : OUI (3/3)

### Zone 2 — Forestiere (46.85, -71.42)
- **Donnees** : 855 sentiers, 15 waterways, 27 clairieres, 61 foret, 1502 noeuds foret
- **Graphe** : 8 729 noeuds (dont 1502 en zone foret)
- **Resultats** : 3 affuts, 3 routes A*, toutes 100% corridor, 0% foret
- **MATCHES_HUNTER** : OUI (3/3)
- **CONFORME 95/5** : OUI (3/3)

### Superposition visuelle confirme
| Element | Visible sur carte | Couleur |
|---|---|---|
| Corridors forestiers (sentiers OSM) | OUI | Vert |
| Sentiers reels | OUI | Vert (variantes par type) |
| Chemins forestiers existants | OUI | Vert |
| Acces genere par BDRE | OUI | Orange (route superposee) |
| Zones de foret dense | OUI | Vert fonce (polygones) |
| Berges ruisseau (corridors naturels) | OUI | Bleu |
| Clairieres/prairies | OUI | Jaune |
| Eau/obstacles (interdit) | OUI | Rouge |
| Waypoint chasseur (DEPART) | OUI | Point rouge |
| Affuts (DESTINATION) | OUI | Points bleus |
| Distances comparees | OUI | Tableau sous carte |

### Criteres de conformite visuelle — BILAN
| Critere | Seuil | Resultat (6 routes) | Statut |
|---|---|---|---|
| 95% trajet sur corridors reels | >= 95% | 100% (6/6) | CONFORME |
| <= 5% en foret dense | <= 5% | 0% (6/6) | CONFORME |
| MATCHES_HUNTER=True | True | True (6/6) | CONFORME |
| Distance minimale corridor → affut | - | Sentier reel A* (6/6) | CONFORME |
| Absence segments hors-sentier non justifies | 0 | 0 (6/6) | CONFORME |

---

**EN ATTENTE VALIDATION STEEVE-MAX**
