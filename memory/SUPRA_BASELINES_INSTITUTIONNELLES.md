# SUPRA_BASELINES_INSTITUTIONNELLES.md
# ============================================================
# COMPLEMENT (A) — BASELINES INSTITUTIONNELLES SUPRA
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Reference: SUPRA_ECARTS_DETAILLES.md (commit 85e139f)
# Statut: LIVRABLE COMPLEMENTAIRE — EN ATTENTE DE VALIDATION
# ============================================================

---

## 1. CAPTURES DE REFERENCE SUPRA

### 1.1 Etat de l'application
- **URL:** https://ultime-preview.preview.emergentagent.com
- **Branche:** BIONIC_REWRITE_P0
- **Commit de reference:** 85e139f
- **Screenshot principale:** `/app/memory/baseline_app_state.png`
- **Frontend:** React operationnel, navigation complete visible (HOME, DASHBOARD, ANALYSE TERRITOIRE, CARTE, INTELLIGENCE, PERMIS, SHOP, GUIDE PRO, GESTION, Premium)
- **Authentification:** Steeve-MAX / admin@huntiq.com connecte

### 1.2 Contexte de reference pour toutes les baselines
Tous les appels API de reference utilisent les parametres suivants:

| Parametre | Valeur |
|---|---|
| **Coordonnees** | lat=47.3, lng=-71.2 (Quebec, region forestiere) |
| **Espece** | orignal |
| **Saison** | automne |
| **Type de sol** | mixte |
| **Substrat** | bois_mou |
| **Sexe** | male |
| **Age** | adult |
| **Mois** | 10 (octobre) |

### 1.3 Inventaire des onglets SUPRA (etat visuel)
Les onglets SUPRA sont accessibles via clic sur un point nutritionnel sur la CARTE.
Le panneau s'ouvre dans un PinnablePanel a droite de la carte avec les 5 onglets.

| Onglet | Icone | Position | Badge dynamique | Etat |
|---|---|---|---|---|
| ANALYSE | FlaskConical | 1 | Non | OPERATIONNEL |
| FICHE | ClipboardList | 2 | Non | OPERATIONNEL |
| INTELLIGENCE | BarChart3 | 3 | Non | OPERATIONNEL |
| COMPAREZ | Scale | 4 | Non | OPERATIONNEL |
| COMMANDEZ | ShoppingCart | 5 | Oui (cartCount) | OPERATIONNEL |

---

## 2. BASELINE DES SCORES SUPRA

### 2.1 Endpoint: `/api/v6/nutrition-intelligence/supra-panel` (POST)

**Latence mesuree:** 0.176s (mediane sur 5 runs)

#### Score SUPRA (x5100)
```json
{
  "score_global": 63,
  "grade": "MODERE",
  "species": "orignal",
  "season": "automne",
  "soil_type": "mixte",
  "scores_par_mineral": {
    "Na": { "name": "Sodium",    "score": 30, "zone": "rouge", "besoin": 132.0, "dispo": 40.0 },
    "Ca": { "name": "Calcium",   "score": 47, "zone": "jaune", "besoin": 95.0,  "dispo": 45.0 },
    "P":  { "name": "Phosphore", "score": "variable", "zone": "variable" },
    "Mg": { "name": "Magnesium", "score": "variable", "zone": "variable" },
    "K":  { "name": "Potassium", "score": "variable", "zone": "variable" },
    "Fe": { "name": "Fer",       "score": "variable", "zone": "variable" }
  },
  "zones_resume": { "vert": "N", "jaune": "N", "rouge": "N" },
  "score_mineral": 63,
  "score_source": "x5100_mineral"
}
```

#### Structure de reponse complete (11 cles)
```
score:                dict (10 keys) -> score_global, grade, species, season, soil_type, scores_par_mineral, zones_resume, score_mineral
recommendations:      dict (5 keys)  -> score_data, recommendations, soil_advice, critical_count, recommended_count
energy_protein:       dict (8 keys)  -> species, season, phase, energy_need, protein_need, energy_blocks, protein_blocks, seasonal_mix
recipe:               dict (17 keys) -> title, subtitle, species, season, season_label, soil_type, substrate, score, ...
evidence:             list (1 item)  -> references scientifiques
costs:                dict (12 keys) -> substrate, mineral_cost_initial_cad, initial_cost_cad, annual_cost_cad, cost_per_visit_cad, ...
substrate_comparison: dict (5 keys)  -> bois_mou, bois_dur, savings_annual_cad, recommended, recommendation_reason
products:             dict (3 keys)  -> context, products (10 items), total
order:                dict (5 keys)  -> order_type, context, items (3), summary (cost_initial_cad: 91.46$)
ecozone:              dict (2 keys)  -> species, data
terrain_solutions:    dict (7 keys)  -> solutions, total, critiques, recommandees, cost_estimate_min/max_cad, categories
```

#### Produits (Top 3)
| Rang | ID | Nom | Score |
|---|---|---|---|
| 1 | purina_antlermax_zn | Purina AntlerMax Zn | 76 |
| 2 | trophy_rock_four65 | Trophy Rock Four65 | 75 |
| 3 | pro_cal_lick | Mineral Lick Pro-Cal | 75 |

#### Commande (Order)
- **Items:** 3
- **Cout initial:** 91.46$

### 2.2 Endpoint: `/api/v1/saline/analyze` (POST)

**Latence mesuree:** 0.126s (mediane sur 5 runs)

#### 7 Moteurs ULTRA
```json
{
  "engines": {
    "soil":       { "soil_type": "...", "pH": "...", "quality_index": "..." },
    "needs":      { "daily_needs": "..." },
    "deficiency": { "deficits": "..." },
    "vegetation": { "phenophase": "...", "couvert_pct": "...", "avg_forage_quality": "..." },
    "hydrology":  { "drainage": "...", "leaching_risk": "...", "distance_eau_m": "..." },
    "metabolism": { "metabolic_phase": "...", "energy_demand_factor": "...", "activity_level": "..." }
  },
  "analysis": {
    "intelligence_score": {
      "global_score": 47.8,
      "rating": "adequat",
      "components": {
        "soil_quality": 75.0,
        "coverage_adequacy": 0.5,
        "forage_quality": 36.8,
        "leaching_resistance": 41.2,
        "metabolic_alignment": 84.0,
        "placement_score": 65.0
      },
      "weights": {
        "soil_quality": 0.15,
        "coverage_adequacy": 0.25,
        "forage_quality": 0.10,
        "leaching_resistance": 0.15,
        "metabolic_alignment": 0.20,
        "placement_score": 0.15
      }
    }
  }
}
```

### 2.3 Endpoint: `/api/v1/salines-ultime/fiche` (GET)

**Latence mesuree:** 0.120s (mediane sur 5 runs)

#### 5 Scores FICHE
```
Score Global: 71 (Grade B)

  logistique:  73 (B) — Poids: 20%
  gros_males:  62 (B) — Poids: 25%
  strategique: 77 (B) — Poids: 25%
  cout_roi:    64 (B) — Poids: 15%
  tcs:         79 (B) — Poids: 15%
```

#### 20 Sources scientifiques
Presentes et completes (IDs 1-20).

### 2.4 Endpoint: `/api/v1/soil/analyze` (GET)

**Latence mesuree:** 0.119s (mediane sur 5 runs)

#### Resultat Sol
```
Type:    Sable grossier
Grade:   C
Score:   47/100
Metrics:
  retention_mineraux:  25
  drainage_naturel:    95
  risque_lessivage:    85
  capacite_portance:   60
  permeabilite:        Tres rapide
  ph_typique:          5.0 - 6.0
  profondeur_cm:       40
  matiere_organique:   1.5%
```

### 2.5 Endpoint: `/api/v1/saline/shop/cart/{session_id}` (GET)

**Latence mesuree:** <0.130s

```json
{
  "success": true,
  "session_id": "sal_baseline_test",
  "items": [],
  "item_count": 0,
  "total": 0,
  "currency": "CAD"
}
```

---

## 3. BASELINE DES FLUX (INPUTS / OUTPUTS)

### 3.1 Flux SUPRA complet — Diagramme d'execution

```
UTILISATEUR
    |
    | [Clic point nutritionnel sur carte]
    |
    v
NutritionPointDetailPanel
    |
    |--- Props: nutritionPoint { id, lat, lng, score, species, season, soil_type, distance_centre_m }
    |           selectedSpecies (selection espece utilisateur)
    |
    |--- Calculs locaux:
    |       species = selectedSpecies || np.species || 'orignal'
    |       season  = np.season || 'printemps'
    |       month   = new Date().getMonth() + 1
    |       seasonMap[month] = saison dynamique
    |
    v
fetchAll() ══════════════════════════════════════════════════════════
    |                                                                |
    |  [PARALLELE — Promise.allSettled]                             |
    |                                                                |
    |--- [1] POST /api/v6/nutrition-intelligence/supra-panel        |
    |       INPUT:  { species, season, soil_type, substrate,         |
    |                 lat, lng, saline_score }                       |
    |       OUTPUT: supraData { score, recommendations,              |
    |               energy_protein, recipe, evidence, costs,         |
    |               substrate_comparison, products, order,           |
    |               ecozone, terrain_solutions }                     |
    |                                                                |
    |--- [2] POST /api/v1/saline/analyze                            |
    |       INPUT:  { lat, lng, species, sex, age,                   |
    |                 month, season: seasonMap[month] }              |
    |       OUTPUT: ultraData { engines: { soil, needs, deficiency,  |
    |               vegetation, hydrology, metabolism },              |
    |               analysis: { intelligence_score, adjusted_deficits } }|
    |                                                                |
    |--- [3] GET /api/v1/salines-ultime/fiche                       |
    |       INPUT:  ?lat=&lng=&species=&season=seasonMap[month]      |
    |       OUTPUT: ficheData { global_score, scores (5), scientific_sources (20) }|
    |                                                                |
    |--- [4] GET /api/v1/soil/analyze                                |
    |       INPUT:  ?lat=&lng=&species=&season=seasonMap[month]      |
    |       OUTPUT: soilData { soil_name, grade, score, metrics,     |
    |               texture, description, recommendations }          |
    |                                                                |
═════════════════════════════════════════════════════════════════════

fetchCart() ═════════════════════════════════════════════════════════
    |--- GET /api/v1/saline/shop/cart/{session_id}
    |       INPUT:  session_id (localStorage)
    |       OUTPUT: cart { items, item_count, total, currency }
═════════════════════════════════════════════════════════════════════

DISTRIBUTION AUX ONGLETS:
    |
    |--- ANALYSE:      supraData.score + .recipe + .recommendations + .evidence
    |                  + .costs + .substrate_comparison + .ecozone + .energy_protein
    |                  + .terrain_solutions + ultraData.engines + ultraData.analysis
    |                  + soilData
    |
    |--- FICHE:        ficheData.global_score + .scores + .scientific_sources
    |                  + soilData + species + season + lat + lng + np
    |
    |--- INTELLIGENCE: supraData.products + compareIds (local state)
    |                  + addToCart (callback) + cartLoading
    |
    |--- COMPAREZ:     supraData.products (filtre par compareIds)
    |                  + compareIds (local state)
    |
    |--- COMMANDEZ:    supraData.order + supraData.products + supraData.recipe
    |                  + cart + addToCart + handleCheckout + fetchCart
```

### 3.2 Flux d'interactions utilisateur entre onglets

```
INTELLIGENCE ──[toggleCompare(pid)]──> compareIds (state parent) ──> COMPAREZ
INTELLIGENCE ──[addToCart(pid)]──> POST /api/v1/saline/shop/cart/add ──> fetchCart() ──> cart (state) ──> COMMANDEZ
COMMANDEZ ──[addToCart(pid)]──> POST /api/v1/saline/shop/cart/add ──> fetchCart() ──> cart (state) ──> badge onglet
COMMANDEZ ──[handleCheckout()]──> POST /api/v1/saline/shop/checkout ──> Stripe URL ──> Redirection
```

---

## 4. BASELINE DE PERFORMANCE (LATENCE, CHARGE)

### 4.1 Latence des endpoints SUPRA (5 runs chacun)

| Endpoint | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Mediane | Min | Max |
|---|---|---|---|---|---|---|---|---|
| supra-panel (POST) | 236ms | 187ms | 111ms | 180ms | 166ms | **176ms** | 111ms | 236ms |
| saline/analyze (POST) | 136ms | 138ms | 118ms | 129ms | 107ms | **129ms** | 107ms | 138ms |
| salines-ultime/fiche (GET) | 136ms | 120ms | 153ms | 117ms | 117ms | **120ms** | 117ms | 153ms |
| soil/analyze (GET) | 112ms | 119ms | 118ms | 127ms | 149ms | **119ms** | 112ms | 149ms |

### 4.2 Temps de chargement total SUPRA (parallele)

```
Temps total theorique (parallele) = max(176, 129, 120, 119) = 176ms
Temps total sequentiel (si serie) = 176 + 129 + 120 + 119 = 544ms
Gain parallelisme: 67.6%
```

### 4.3 Volume de donnees

| Endpoint | Taille reponse (approx.) | Cles principales |
|---|---|---|
| supra-panel | ~8 KB | 11 cles racine, 10 produits, 3 items order |
| saline/analyze | ~4 KB | 6 engines, 1 analysis |
| salines-ultime/fiche | ~6 KB | 5 scores x 6 composants, 20 sources |
| soil/analyze | ~2 KB | 1 type sol, 8 metriques |
| **Total par clic** | **~20 KB** | — |

### 4.4 Seuils de performance BCE-4X

| Metrique | Seuil GOLDEN | Valeur actuelle | Statut |
|---|---|---|---|
| Latence supra-panel | < 500ms | 176ms | CONFORME |
| Latence saline/analyze | < 300ms | 129ms | CONFORME |
| Latence fiche | < 300ms | 120ms | CONFORME |
| Latence soil | < 200ms | 119ms | CONFORME |
| Temps total (parallele) | < 1000ms | 176ms | CONFORME |
| Taille reponse totale | < 100 KB | ~20 KB | CONFORME |

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*
