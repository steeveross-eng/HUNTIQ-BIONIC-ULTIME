# PLAN TECHNIQUE P0-X — SALINES V4 (TERRAIN-CENTRE)
## BCE-4X GOLDEN V6+ | ORDONNANCE STEEVE-MAX 2026-04-06
## BRANCHE: BIONIC_REWRITE_P0

---

## STATUT : EN ATTENTE DE VALIDATION STEEVE-MAX

---

# SOMMAIRE

1. Schema SALINES V4 (terrain-centre, sans grille 4x4)
2. Criteres proposes (eau, couvert, habitat, mineraux, saison)
3. Integration BDRE (corridors, pression, contamination)
4. Densite adaptative
5. Ponderations proposees
6. Logique de generation
7. Logique de filtrage
8. Logique de scoring
9. Echeancier dedie

---

# ═══════════════════════════════════════════════════════════
# 1. SCHEMA SALINES V4 — TERRAIN-CENTRE (SANS GRILLE 4x4)
# ═══════════════════════════════════════════════════════════

## 1.1 Probleme de la grille V3

La grille 4x4 (V2/V3) genere 16 candidats AVEUGLES au terrain:
- Les candidats tombent aleatoirement sur des zones d'eau, falaises, routes
- La diversification spatiale est ARTIFICIELLE (perturbation MD5 dans chaque cellule)
- Aucune logique de placement lie aux FEATURES terrain (rivieres, sentiers, lisières)
- Les candidats se concentrent dans un carre regulier, ignorant la topographie

## 1.2 Philosophie V4: GENERATION TERRAIN-PILOTEE

```
[Waypoint utilisateur]
        │
        ▼
[COLLECTE TERRAIN CONTEXTUELLE]
        │
        ├── (1) OSM water: localiser cours d'eau, lacs, ruisseaux
        │        → generer candidats a 30-80m de chaque source d'eau
        │
        ├── (2) OSM trails: localiser sentiers, chemins forestiers
        │        → generer candidats a < 200m des sentiers accessibles
        │
        ├── (3) BDRE corridors: identifier corridors de deplacement
        │        → generer candidats aux intersections corridor/lisiere
        │
        ├── (4) Terrain relief: identifier zones plates (pente < 10%)
        │        → exclure zones a forte pente (> 20%)
        │
        └── (5) Foret lisiere: identifier transitions foret/clairiere
                 → generer candidats en zone de transition (ecotone)
        │
        ▼
[POOL DE CANDIDATS TERRAIN-PILOTES]
        │ Variable: 8 à 30 candidats selon richesse du terrain
        │
        ▼
[FILTRAGE STRICT]
        │ Haversine <= 600m du centre
        │ Exclusion < 150m du centre
        │ Exclusion zones urbaines
        │ Exclusion zones d'eau directe
        │ Exclusion pente > 20%
        │
        ▼
[SCORING V4 (9 criteres)]
        │ Eau 20% | Couvert 15% | Habitat 10% | Mineraux 10% | Saison 10%
        │ Corridor 15% | Sentier 10% | Pente 5% | Securite 5%
        │
        ▼
[SELECTION GLOUTONNE ADAPTATIVE]
        │ max_salines = 1-4 (selon densite du pool)
        │ min_distance 300m entre selectionnees
        ▼
[RETOUR: N JAUNES + M GRIS]
```

## 1.3 Comparaison V3 vs V4

| Aspect | V3 (actuel) | V4 (propose) |
|--------|-----------|-------------|
| Generation | Grille 4x4 fixe (16 candidats) | Terrain-pilotee (8-30 candidats) |
| Sources donnees | 3/6 reels, 3/6 MD5 | 9/9 criteres terrain |
| Criteres | 6 criteres | 9 criteres |
| BDRE | Non integre | Corridor + contamination |
| Mineraux sol | Affiches mais pas dans le score | Integres dans le score (10%) |
| Saison | Type saline (sodium/calcium) | Ponderation saisonniere dynamique |
| Densite | Fixe (16 candidats) | Adaptative (8-30 selon terrain) |

---

# ═══════════════════════════════════════════════════════════
# 2. CRITERES PROPOSES — LISTE EXHAUSTIVE
# ═══════════════════════════════════════════════════════════

## 2.1 Critere 1 — PROXIMITE EAU (20%)

**Source:** OSM water cache + `_nearest_water_distance_saline()`
**Logique:** Distance reelle au point d'eau le plus proche

| Distance | Score | Justification |
|----------|-------|---------------|
| 30-80m | 100 | Zone optimale — animaux se nourrissent pres de l'eau |
| 80-150m | 75 | Zone acceptable — trajet court |
| 150-300m | 45 | Penalite moderee — animaux doivent choisir |
| < 30m | 40 | Risque terrain mou, inondation |
| > 300m | 20 | Penalite severe — saline trop eloignee |

## 2.2 Critere 2 — COUVERT FORESTIER (15%)

**Source:** `terrain.foret.couvert_pct` (analyse terrain algorithmique)
**Logique:** Zone optimale 40-80% de couvert = protection + lumiere

| Couvert | Score | Justification |
|---------|-------|---------------|
| 40-80% | 100 | Zone ideale — protection + visibilite |
| 30-40% | 75 | Acceptable — un peu expose |
| 80-90% | 70 | Dense — moins de lumiere/chaleur |
| < 30% | 40 | Trop expose — animaux mefiants |
| > 90% | 35 | Trop dense — acces difficile |

## 2.3 Critere 3 — DIVERSITE MICRO-HABITAT (10%)

**Source:** Composite terrain (couvert + eau + relief + essences)
**Logique:** Les ecotones (zones de transition) sont les plus riches

| Indicateur | Score contribution | Calcul |
|-----------|-------------------|--------|
| Couvert 40-70% (ecotone) | +30 | 1 si dans la plage, 0 sinon |
| Eau < 200m | +25 | 1 si vrai, 0 sinon |
| Pente < 15% | +20 | 1 si vrai, 0 sinon |
| N essences > 4 | +15 | 1 si vrai, 0 sinon |
| Strate arbustive > 20% | +10 | 1 si vrai, 0 sinon |
| **Total** | **100** | |

## 2.4 Critere 4 — MINERAUX DU SOL (10%) — NOUVEAU

**Source:** `terrain.nutriments_sol` (analyse terrain algorithmique)
**Logique:** Le sol pauvre en mineraux NECESSSITE plus une saline

| Indicateur | Score | Calcul |
|-----------|-------|--------|
| Se < 0.2 ppm (carence selenium) | +30 | Besoin urgent de supplementation |
| Ca < 500 ppm (carence calcium) | +25 | Besoin supplementation |
| P < 10 ppm (carence phosphore) | +20 | Besoin supplementation |
| Zn < 5 ppm (carence zinc) | +15 | Besoin supplementation |
| Cu < 3 ppm (carence cuivre) | +10 | Besoin supplementation |
| **Total** | **100** | Score = somme des carences detectees |

**Logique inversee:** Un sol TRES carencé donne un score ELEVE (= la saline est PLUS justifiee ici).

## 2.5 Critere 5 — SAISON (10%) — NOUVEAU

**Source:** Parametre `month` + espece
**Logique:** Les besoins nutritionnels varient selon la saison

| Saison | Mois | Besoin principal | Score multiplicateur |
|--------|------|-----------------|---------------------|
| Printemps (croissance bois) | 4-5 | Calcium + Phosphore | x1.2 si Ca/P carences |
| Ete (lactation) | 6-7 | Sodium + Energie | x1.3 si Na carence |
| Automne (rut/engraissement) | 8-10 | Mineraux complets | x1.0 (base) |
| Hiver (survie) | 11-3 | Energie + Sel | x0.8 (activite reduite) |

Le score saisonnier est un MULTIPLICATEUR applique au score mineral de base.

## 2.6 Critere 6 — CORRIDOR BDRE (15%) — NOUVEAU

**Source:** `engines/bdre/corridor_optimizer_v2.py`
**Logique:** Une saline PRES d'un corridor de deplacement est plus efficace

| Position | Score | Justification |
|----------|-------|---------------|
| Sur un corridor BDRE identifie | 100 | Position optimale — animaux en deplacement |
| < 200m d'un corridor | 80 | Bonne position — a proximite |
| 200-500m d'un corridor | 50 | Acceptable — pas ideal |
| > 500m ou aucun corridor | 30 | Isole — animaux doivent devier |

## 2.7 Critere 7 — ACCESSIBILITE SENTIER (10%)

**Source:** OSM terrain_nav graph + `_nearest_trail_distance_saline()`
**Logique:** Le chasseur doit pouvoir transporter les mineraux

| Distance sentier | Score |
|-----------------|-------|
| < 100m | 90 |
| 100-300m | 70 |
| 300-600m | 40 |
| > 600m | 10 |

## 2.8 Critere 8 — PENTE (5%)

**Source:** `terrain.relief.pente_moyenne_pct`
**Logique:** Zone plate = frequentation accrue

| Pente | Score |
|-------|-------|
| < 5% | 100 |
| 5-10% | 80 |
| 10-15% | 60 |
| 15-20% | 30 |
| > 20% | EXCLUSION (filtre, pas de score) |

## 2.9 Critere 9 — SECURITE / PRESSION HUMAINE (5%)

**Source:** Distance au centre du waypoint (proxy)
**Logique:** Plus on s'eloigne du centre, plus la pression humaine diminue

| Distance centre | Score |
|----------------|-------|
| > 400m | 90 |
| 300-400m | 75 |
| 200-300m | 60 |
| 150-200m | 50 |

---

# ═══════════════════════════════════════════════════════════
# 3. INTEGRATION BDRE
# ═══════════════════════════════════════════════════════════

## 3.1 Corridors

Le moteur BDRE (`corridor_optimizer_v2.py`) analyse les corridors de deplacement
a partir du graphe terrain. Les corridors representent les axes de circulation
preferentiels du gibier (ratio sentier/hors-sentier 95/5).

**Integration dans V4:**
- Charger les corridors BDRE lors de la generation des candidats
- Generer des candidats SUPPLEMENTAIRES aux intersections corridor/lisiere
- Utiliser le `bdre_corridor_score` comme critere de scoring (15%)

## 3.2 Contamination

Le moteur vent/odeur (`vent_odeurs.py`) evalue la contamination olfactive.

**Integration dans V4:**
- Lors du scoring, appeler `evaluate_blind_wind_score()` pour chaque candidat
  saline avec la direction/vitesse du vent courante
- Un site alimente contamine par le vent du chasseur recoit un MALUS
  (mais n'est pas exclu — c'est un site statique, pas un affut)

## 3.3 Pression / Anomalies

Le detecteur d'anomalies BDRE (`anomaly_detector.py`) identifie les zones
a donnees deficientes.

**Integration dans V4:**
- Si le terrain autour d'un candidat a un score BDRE DEFICIENT,
  penaliser le critere SECURITE de -20%
- Logging des anomalies dans la reponse pour tracabilite

---

# ═══════════════════════════════════════════════════════════
# 4. DENSITE ADAPTATIVE
# ═══════════════════════════════════════════════════════════

## 4.1 Principe

Au lieu de generer un nombre FIXE de candidats (16 dans V3),
V4 adapte le nombre de candidats a la RICHESSE du terrain:

| Richesse terrain | Candidats generes | Justification |
|-----------------|-------------------|---------------|
| RICHE (> 3 sources eau, > 2 sentiers, corridor) | 20-30 | Beaucoup de positions viables |
| MOYEN (1-3 sources eau, 1-2 sentiers) | 12-20 | Moderement viable |
| PAUVRE (0-1 source eau, 0-1 sentier, pas de corridor) | 8-12 | Peu d'options, fallback grille |

## 4.2 Sources de candidats

| Source | Candidats generes par source | Logique |
|--------|------------------------------|---------|
| Points d'eau OSM | 2-4 par source | Position a 30-80m du rivage |
| Noeuds sentier OSM | 1-2 par segment | Position a 100-200m du sentier |
| Intersections corridor BDRE | 1-2 par intersection | Sur le corridor |
| Lisières foret (ecotone) | 2-4 | Zones de transition |
| Fallback grille 3x3 | 9 | Si < 8 candidats terrain |

## 4.3 Fallback garanti

Si le terrain est PAUVRE (aucune source d'eau, aucun sentier, aucun corridor),
le systeme revient a une grille 3x3 perturbee (similaire a V3 mais 9 candidats au lieu de 16).
**ZERO echec de generation.**

---

# ═══════════════════════════════════════════════════════════
# 5. PONDERATIONS PROPOSEES
# ═══════════════════════════════════════════════════════════

| # | Critere | Poids V3 | Poids V4 | Justification changement |
|---|---------|----------|----------|--------------------------|
| 1 | Proximite eau | **25%** | **20%** | Redistribue vers Corridor + Mineraux |
| 2 | Couvert forestier | **20%** | **15%** | Redistribue vers Saison |
| 3 | Diversite habitat | **10%** | **10%** | INCHANGE |
| 4 | Mineraux du sol | **0%** | **10%** | NOUVEAU — justification biologique |
| 5 | Saison | **0%** | **10%** | NOUVEAU — besoins variables |
| 6 | Corridor BDRE | **0%** | **15%** | NOUVEAU — deplacement reel |
| 7 | Accessibilite sentier | **15%** | **10%** | Reduit — corridor est plus pertinent |
| 8 | Pente | **20%** | **5%** | Reduit — pente > 20% deja filtre |
| 9 | Securite | **10%** | **5%** | Reduit — proxy moins precis |
| **Total** | **100%** | **100%** | |

**Changements majeurs:**
- Eau passe de 25% a 20% (toujours dominant)
- 3 NOUVEAUX criteres (Mineraux 10%, Saison 10%, Corridor 15%)
- Pente et Securite reduits car moins fiables (proxy/algorithmique)

---

# ═══════════════════════════════════════════════════════════
# 6. LOGIQUE DE GENERATION
# ═══════════════════════════════════════════════════════════

```python
def compute_salines_v4(center_lat, center_lng, terrain, species, month,
                        trail_graph, bdre_data, wind_data,
                        max_radius_m=600, max_salines=4):
    """
    V4 Terrain-centre: genere candidats à partir des FEATURES terrain.
    """
    candidates = []

    # Phase 1: CANDIDATS EAU (2-4 par source d'eau)
    water_sources = detect_water_sources(center_lat, center_lng, max_radius_m)
    for ws in water_sources:
        for angle in [0, 90, 180, 270]:  # 4 directions autour de chaque source
            cand = offset_point(ws, distance_m=random(30, 80), angle=angle)
            if in_radius(cand, center, max_radius_m) and not on_exclusion(cand):
                candidates.append(cand)

    # Phase 2: CANDIDATS SENTIER (1-2 par segment proche)
    trail_nodes = get_nearby_trail_nodes(trail_graph, center, max_radius_m)
    for tn in trail_nodes[:6]:
        cand = offset_point(tn, distance_m=random(100, 200), angle=perpendicular)
        candidates.append(cand)

    # Phase 3: CANDIDATS CORRIDOR BDRE
    corridors = bdre_data.get("corridors", [])
    for corr in corridors:
        intersections = find_intersections(corr, trail_nodes)
        for inter in intersections[:3]:
            candidates.append(inter)

    # Phase 4: CANDIDATS LISIERE (ecotone)
    ecotones = detect_ecotones(terrain, center, max_radius_m)
    for eco in ecotones[:4]:
        candidates.append(eco)

    # Phase 5: FALLBACK si < 8 candidats
    if len(candidates) < 8:
        grid_candidates = generate_grid_3x3(center, side_m=1200)
        candidates.extend(grid_candidates)

    # Phase 6: FILTRAGE + SCORING + SELECTION
    candidates = filter_candidates(candidates, center, max_radius_m)
    candidates = score_candidates_v4(candidates, terrain, species, month,
                                      trail_graph, bdre_data, wind_data)
    return select_with_min_distance(candidates, max_salines, min_dist=300)
```

---

# ═══════════════════════════════════════════════════════════
# 7. LOGIQUE DE FILTRAGE
# ═══════════════════════════════════════════════════════════

## 7.1 Filtres d'exclusion (eliminent le candidat)

| # | Filtre | Seuil | Source |
|---|--------|-------|--------|
| F1 | Distance au centre > max_radius_m | 600m | Haversine |
| F2 | Distance au centre < 150m | 150m | Haversine |
| F3 | Sur zone urbaine | Booleen | `_circle_on_urban()` |
| F4 | Sur zone d'eau directe | Booleen | `_circle_on_water()` |
| F5 | Pente > 20% | 20% | Estimation locale |
| F6 | Distance a un autre candidat < 50m | 50m | Deduplication |

## 7.2 Filtres de penalite (reduisent le score mais ne suppriment pas)

| # | Filtre | Effet | Critere affecte |
|---|--------|-------|----------------|
| P1 | Eau < 30m | score_eau = 40/100 | Eau (20%) |
| P2 | Couvert < 30% ou > 90% | score_couvert = 35-40/100 | Couvert (15%) |
| P3 | Aucun corridor < 500m | score_corridor = 30/100 | Corridor (15%) |
| P4 | Aucun sentier < 600m | score_acces = 10/100 | Accessibilite (10%) |
| P5 | Vent defavorable | malus -15% sur score total | Securite (5%) |

---

# ═══════════════════════════════════════════════════════════
# 8. LOGIQUE DE SCORING V4
# ═══════════════════════════════════════════════════════════

```
SCORE_TOTAL = (
    score_eau × 0.20           # Distance reelle au point d'eau
  + score_couvert × 0.15       # Couvert forestier optimal 40-80%
  + score_habitat × 0.10       # Diversite ecologique composite
  + score_mineraux × 0.10      # Carences sol (inversé: + carence = + score)
  + score_saison × 0.10        # Multiplicateur saisonnier
  + score_corridor × 0.15      # Proximite corridor BDRE
  + score_sentier × 0.10       # Distance sentier OSM
  + score_pente × 0.05         # Terrain plat
  + score_securite × 0.05      # Distance centre (proxy pression)
)

# Malus optionnel vent
if wind_contamination:
    SCORE_TOTAL *= 0.85  # -15% si vent du chasseur porte vers la saline

# Borne finale
SCORE_TOTAL = max(0, min(100, SCORE_TOTAL × 100))
```

## 8.1 Tracabilite V4

Chaque candidat retournera:
```json
{
  "id": "SAL-V4-01",
  "scoring_version": "V4",
  "criteres": {
    "eau": 85, "couvert": 70, "habitat": 65, "mineraux": 80,
    "saison": 96, "corridor": 60, "sentier": 90, "pente": 100, "securite": 75
  },
  "criteres_sources": {
    "eau_distance_m": 55,
    "eau_source": "OSM_water_cache",
    "trail_distance_m": 85,
    "trail_source": "OSM_terrain_nav",
    "corridor_distance_m": 180,
    "corridor_source": "BDRE_corridor_v2",
    "habitat_source": "terrain_composite",
    "mineraux_source": "terrain_nutriments_sol",
    "season_month": 10,
    "season_multiplier": 1.0,
    "wind_contaminated": false,
    "generation_source": "water_proximity"  // ou "trail_node", "corridor_intersection", "ecotone", "fallback_grid"
  }
}
```

---

# ═══════════════════════════════════════════════════════════
# 9. ECHEANCIER DEDIE
# ═══════════════════════════════════════════════════════════

| Phase | Description | Prerequis | Duree estimee |
|-------|-------------|-----------|---------------|
| **P0-X-0** | Plan technique (CE DOCUMENT) | Aucun | **FAIT** |
| **P0-X-1** | Validation plan par STEEVE-MAX | P0-X-0 | En attente |
| **P0-X-2** | Fonctions de detection terrain (water_sources, ecotones) | P0-X-1 valide | 1 session |
| **P0-X-3** | Generateur de candidats terrain-pilotes | P0-X-2 | 1 session |
| **P0-X-4** | Scoring V4 (9 criteres) | P0-X-3 | 1 session |
| **P0-X-5** | Integration BDRE (corridor scoring) | P0-X-4 | 1 session |
| **P0-X-6** | Integration vent/contamination | P0-X-5 | 0.5 session |
| **P0-X-7** | Tests terrain (3 waypoints) | P0-X-6 | 1 session |
| **P0-X-8** | Audit regression V3→V4 | P0-X-7 | 0.5 session |
| **P0-X-9** | Shadow mode V3/V4 en parallele | P0-X-8 | 0.5 session |
| **P0-X-10** | Validation finale STEEVE-MAX | P0-X-9 | En attente |

**Duree totale estimee:** 6 sessions apres validation du plan.

---

# ═══════════════════════════════════════════════════════════
# ANNEXES
# ═══════════════════════════════════════════════════════════

## A. Fichiers a creer (BIONIC_REWRITE_P0 uniquement)

| Fichier | Contenu |
|---------|---------|
| `core/scoring_pipeline/alimentation_v4/salines_v4.py` | Nouveau moteur V4 |
| `core/scoring_pipeline/alimentation_v4/terrain_features.py` | Detection eau, ecotones, lisières |
| `core/scoring_pipeline/alimentation_v4/mineral_scorer.py` | Scoring mineraux + saisonnier |
| `core/scoring_pipeline/alimentation_v4/bdre_integration.py` | Integration corridor BDRE |

## B. Fichiers a modifier

| Fichier | Modification |
|---------|-------------|
| `core/scoring_pipeline/alimentation_v2/engine.py` | Appel V4 au lieu de V3 (switch configurable) |
| `core/scoring_pipeline/alimentation_v2/router.py` | Parametre `version=v4` optionnel |

## C. Fichiers NON modifies

| Fichier | Raison |
|---------|--------|
| `core/scoring_pipeline/alimentation_v2/salines.py` | V3 conserve pour Shadow Mode |
| `engines/nutrition_intelligence/router.py` | SUPRA INCHANGE |
| `engines/hunt_orchestrator/*` | Affuts V2 INCHANGE |
| `frontend/*` | Aucun changement frontend pour V4 |

---

## SIGNATURES

| Role | Identifiant |
|------|-------------|
| Autorite | COMMANDANT STEEVE-MAX |
| Protocole | BCE-4X GOLDEN V6+ |
| Agent executant | EMERGENT E1 |
| Date de soumission | 2026-04-06 |
| Statut | **EN ATTENTE DE VALIDATION** |
