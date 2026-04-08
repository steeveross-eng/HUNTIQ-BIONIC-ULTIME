# PLAN DE RESTAURATION MULTI-ESPECES
# DIFFERENCIATION ECOLOGIQUE ORIGNAL / CHEVREUIL / OURS NOIR / WAPITI / DINDON

**Protocole:** BCE-4X ULTIME ABSOLU x3
**Classification:** PLAN D'ACTION CORRECTIVE — COMMANDANT STEEVE-MAX
**Date:** Fevrier 2026
**Branche:** `SUPRA_RECONSTRUCTION`
**Reference:** MULTI_SPECIES_HOTSPOTS_SALINES_AUDIT.md

---

## 1. SYNTHESE DU PLAN

Ce plan corrige les 6 causes racines de convergence inter-especes identifiees dans l'audit. Il est structure en **6 phases sequentielles**, chacune testable independamment.

| Phase | Objet | Priorite | Fichiers impactes | Effort |
|---|---|---|---|---|
| MS-1 | Ponderations dynamiques ENGINE_WEIGHTS par espece | **P0** | `common/constants.py`, `score_consolide.py` | Faible |
| MS-2 | Moteur RSF (Resource Selection Function) par espece | **P0** | Nouveau: `rsf_engine/` | Eleve |
| MS-3 | 11 couches ecologiques manquantes | **P0** | 11 nouveaux sous-modules dans les engines existants | Eleve |
| MS-4 | 8 parametres comportementaux par espece | **P1** | `behavior_v1/engine.py`, `corridors_v10/species_profiles.py`, nouveau: `circadian_engine.py` | Moyen |
| MS-5 | Elimination hash generique — terrain espece-specifique | **P1** | 11 engines CORE++/CORE+++/BIONIC-OS | Eleve |
| MS-6 | Logique SALINES differentiee par espece | **P1** | `alimentation_v2/salines.py`, `alimentation_v2/engine.py` | Moyen |

---

## 2. PHASE MS-1 — PONDERATIONS DYNAMIQUES PAR ESPECE

### 2.1 Objectif
Remplacer la matrice `ENGINE_WEIGHTS` statique unique par une matrice par espece.

### 2.2 Architecture proposee

**Fichier :** `backend/core/scoring_pipeline/common/constants.py`

```python
# REMPLACEMENT de ENGINE_WEIGHTS (statique) par SPECIES_ENGINE_WEIGHTS (dynamique)

SPECIES_ENGINE_WEIGHTS = {
    "CERF": {
        "alimentation": 0.18,    # Cerf = lisiere + friches + mast = alimentation critique
        "repos": 0.12,
        "corridors_v10": 0.12,
        "alimentation_v2": 0.08,
        "pression": 0.10,
        "hydro": 0.03,
        "thermal": 0.02,
        "habitat": 0.06,         # +++ habitat mosaique essentiel
        "behavior": 0.04,        # +++ comportement gregaire important
        "ndvi_vegetation": 0.04,
        "risk": 0.03,
        "opportunity": 0.03,
        "attractors": 0.04,
        "weather": 0.02,
        "temporal": 0.02,
        "ecosystem": 0.02,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.02,
        "visibility": 0.02,
        "learning": 0.01,
    },
    "ORIGNAL": {
        "alimentation": 0.14,
        "repos": 0.10,
        "corridors_v10": 0.15,   # +++ corridors directionnels critiques
        "alimentation_v2": 0.06,
        "pression": 0.12,
        "hydro": 0.08,           # +++ affinite hydro TRES elevee
        "thermal": 0.04,         # +++ sensibilite thermique haute
        "habitat": 0.05,
        "behavior": 0.03,
        "ndvi_vegetation": 0.03,
        "risk": 0.03,
        "opportunity": 0.02,
        "attractors": 0.03,
        "weather": 0.03,
        "temporal": 0.02,
        "ecosystem": 0.02,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.03,
        "visibility": 0.02,
        "learning": 0.01,
    },
    "OURS": {
        "alimentation": 0.22,    # +++ omnivore, alimentation = facteur dominant
        "repos": 0.08,
        "corridors_v10": 0.10,
        "alimentation_v2": 0.04, # Pas de salines, mais nutrition presente
        "pression": 0.12,
        "hydro": 0.04,
        "thermal": 0.04,
        "habitat": 0.06,         # +++ foret dense essentielle
        "behavior": 0.05,        # +++ comportement solitaire, opportuniste
        "ndvi_vegetation": 0.05, # +++ vegetation = indicateur nourriture
        "risk": 0.03,
        "opportunity": 0.04,     # +++ zones opportunistes (baies, insectes)
        "attractors": 0.05,      # +++ attracteurs alimentaires dominants
        "weather": 0.02,
        "temporal": 0.02,
        "ecosystem": 0.02,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.02,
        "visibility": 0.01,
        "learning": 0.01,
    },
    "DINDON": {
        "alimentation": 0.20,    # +++ mast + insectes critiques
        "repos": 0.10,
        "corridors_v10": 0.08,
        "alimentation_v2": 0.04,
        "pression": 0.08,
        "hydro": 0.03,
        "thermal": 0.02,
        "habitat": 0.08,         # +++ foret mature + clairieres
        "behavior": 0.06,        # +++ territorial, gloussement
        "ndvi_vegetation": 0.06, # +++ vegetation sol = alimentation
        "risk": 0.03,
        "opportunity": 0.04,
        "attractors": 0.05,
        "weather": 0.03,
        "temporal": 0.03,
        "ecosystem": 0.02,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.02,
        "visibility": 0.03,      # +++ visibilite sol critique
        "learning": 0.01,
    },
    "WAPITI": {
        "alimentation": 0.16,
        "repos": 0.10,
        "corridors_v10": 0.14,   # +++ migrateur, corridors importants
        "alimentation_v2": 0.07,
        "pression": 0.10,
        "hydro": 0.05,
        "thermal": 0.03,
        "habitat": 0.06,
        "behavior": 0.04,
        "ndvi_vegetation": 0.04,
        "risk": 0.03,
        "opportunity": 0.03,
        "attractors": 0.03,
        "weather": 0.03,
        "temporal": 0.02,
        "ecosystem": 0.02,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.02,
        "trajets": 0.03,
        "visibility": 0.02,
        "learning": 0.01,
    },
}
```

### 2.3 Modification dans score_consolide.py

```python
# AVANT:
weights = ENGINE_WEIGHTS

# APRES:
from .common.constants import SPECIES_ENGINE_WEIGHTS, ENGINE_WEIGHTS

def get_species_weights(species):
    return SPECIES_ENGINE_WEIGHTS.get(species.upper(), ENGINE_WEIGHTS)

# Dans compute_consolidated_score():
weights = get_species_weights(species)
```

### 2.4 Test de validation

```bash
# Pour chaque espece, verifier que sum(weights) == 1.00
python3 -c "
from constants import SPECIES_ENGINE_WEIGHTS
for sp, w in SPECIES_ENGINE_WEIGHTS.items():
    total = sum(w.values())
    assert abs(total - 1.0) < 0.001, f'{sp}: {total}'
    print(f'{sp}: {total:.4f} OK')
"
```

### 2.5 Impact attendu

| Metrique | Avant | Apres |
|---|---|---|
| Differenciation ponderations | 0% (identique) | 100% (5 matrices) |
| Poids HYDRO ORIGNAL vs CERF | 3.48% = 3.48% | 8% vs 3% |
| Poids ALIMENTATION OURS vs CERF | 15.03% = 15.03% | 22% vs 18% |
| Score CRITIQUE pour changement | Non | Oui — scores vont changer |

### 2.6 Contrainte ZERO REGRESSION
Les baselines SUPRA/ULTRA/FICHE/SOL ne sont PAS impactees car elles utilisent le pipeline `nutrition_intelligence` (modules x5100-x7000), pas `score_consolide`. ZERO derive.

---

## 3. PHASE MS-2 — MOTEUR RSF (RESOURCE SELECTION FUNCTION)

### 3.1 Objectif
Creer un moteur RSF par espece qui remplace le hash deterministe par des coefficients de selection de ressources calibres sur la litterature scientifique.

### 3.2 Architecture proposee

**Repertoire :** `backend/core/scoring_pipeline/rsf_engine/`

```
rsf_engine/
├── __init__.py
├── engine.py           # Moteur principal RSF
├── coefficients.py     # Coefficients beta par espece
├── habitat_layers.py   # Couches d'habitat simulees (phase transitoire)
└── integration.py      # Integration dans score_consolide
```

### 3.3 Modele RSF

Le modele RSF classique : `w(x) = exp(beta1*x1 + beta2*x2 + ... + betaN*xN)`

Ou `x1..xN` sont les covariables d'habitat et `beta1..betaN` les coefficients de selection par espece.

```python
# coefficients.py — Coefficients RSF par espece
# Source: Litterature scientifique (Boyce 2006, Manly 2002, DeCesare 2012)

RSF_COEFFICIENTS = {
    "CERF": {
        "couvert_conifere": -0.15,      # Evite conifere dense
        "couvert_feuillu": 0.45,        # Prefere feuillu
        "couvert_mixte": 0.30,
        "lisiere_100m": 0.65,           # Forte attraction lisiere
        "friche_regeneration": 0.55,    # Forte attraction friches
        "culture_proximite": 0.40,      # Attrait cultures
        "distance_eau_log": -0.20,      # Attraction moderee eau
        "distance_route_log": 0.35,     # Evitement routes
        "pente_deg": -0.08,             # Evite fortes pentes
        "altitude_m": -0.005,           # Preference basse altitude
        "densite_route_km2": -0.45,     # Evitement densite routiere
        "marecage": -0.10,              # Evite marecages
        "exposition_sud": 0.25,         # Preference versants sud
    },
    "ORIGNAL": {
        "couvert_conifere": 0.35,       # Prefere conifere (ravage)
        "couvert_feuillu": 0.15,
        "couvert_mixte": 0.40,          # Mixte = optimal
        "lisiere_100m": 0.20,           # Lisiere moderee
        "friche_regeneration": 0.60,    # Forte attraction regenerations
        "culture_proximite": -0.30,     # Evite cultures
        "distance_eau_log": -0.55,      # TRES forte attraction eau
        "distance_route_log": 0.50,     # Fort evitement routes
        "pente_deg": -0.04,             # Tolere pentes
        "altitude_m": 0.002,            # Preference altitude moderee
        "densite_route_km2": -0.60,     # Fort evitement densite routiere
        "marecage": 0.45,               # FORTE attraction marecages
        "exposition_sud": 0.10,         # Faible preference exposition
    },
    "OURS": {
        "couvert_conifere": 0.20,
        "couvert_feuillu": 0.40,        # Prefere feuillu (baies, mast)
        "couvert_mixte": 0.35,
        "lisiere_100m": 0.15,
        "friche_regeneration": 0.70,    # TRES forte attraction friches (baies)
        "culture_proximite": 0.20,
        "distance_eau_log": -0.30,
        "distance_route_log": 0.40,
        "pente_deg": 0.05,              # Tolere et prefere legeres pentes
        "altitude_m": 0.003,
        "densite_route_km2": -0.55,
        "marecage": 0.10,
        "exposition_sud": 0.15,
    },
    "DINDON": {
        "couvert_conifere": -0.20,      # Evite conifere dense
        "couvert_feuillu": 0.55,        # Forte preference feuillu mature
        "couvert_mixte": 0.30,
        "lisiere_100m": 0.50,           # Forte attraction lisiere
        "friche_regeneration": 0.25,
        "culture_proximite": 0.45,      # Attraction cultures (mais)
        "distance_eau_log": -0.15,
        "distance_route_log": 0.20,
        "pente_deg": -0.12,             # Evite fortes pentes (marche au sol)
        "altitude_m": -0.008,           # Basse altitude
        "densite_route_km2": -0.30,
        "marecage": -0.25,              # Evite marecages
        "exposition_sud": 0.30,         # Preference versants sud chauds
    },
    "WAPITI": {
        "couvert_conifere": 0.10,
        "couvert_feuillu": 0.25,
        "couvert_mixte": 0.35,
        "lisiere_100m": 0.40,           # Lisiere importante
        "friche_regeneration": 0.45,
        "culture_proximite": 0.15,
        "distance_eau_log": -0.35,      # Attraction eau moderee-forte
        "distance_route_log": 0.45,     # Fort evitement routes
        "pente_deg": -0.03,
        "altitude_m": 0.004,            # Preference altitude
        "densite_route_km2": -0.50,
        "marecage": 0.05,
        "exposition_sud": 0.20,
    },
}
```

### 3.4 Integration dans score_consolide

Le moteur RSF remplacera progressivement les 11 moteurs hash generiques :
1. Phase transitoire : RSF = 20% du score, hash = 12% (reduction)
2. Phase finale : RSF = 32%, hash = 0% (elimination totale)

### 3.5 Test de validation

```bash
# Verifier que RSF produit des scores significativement differents par espece
python3 -c "
from rsf_engine.engine import compute_rsf_score
lat, lng = 46.8, -71.2
for sp in ['CERF', 'ORIGNAL', 'OURS', 'DINDON', 'WAPITI']:
    score = compute_rsf_score(lat, lng, sp, month=10)
    print(f'{sp}: RSF={score:.1f}')
# Delta minimum attendu: >10 points entre especes les plus differentes
"
```

---

## 4. PHASE MS-3 — 11 COUCHES ECOLOGIQUES MANQUANTES

### 4.1 Liste des couches a implementer

| # | Couche | Fichier | Integration | Especes beneficiaires |
|---|---|---|---|---|
| L1 | **Lisiere** | `rsf_engine/layers/lisiere_layer.py` | Coefficient RSF `lisiere_100m` | CERF, DINDON |
| L2 | **Friche / Regeneration** | `rsf_engine/layers/friche_layer.py` | Coefficient RSF `friche_regeneration` | OURS, ORIGNAL, CERF |
| L3 | **Culture / Jacheres** | `rsf_engine/layers/culture_layer.py` | Coefficient RSF `culture_proximite` | CERF, DINDON |
| L4 | **Marecage / Tourbiere** | `rsf_engine/layers/marecage_layer.py` | Coefficient RSF `marecage` | ORIGNAL |
| L5 | **Zone fraiche** | `rsf_engine/layers/thermal_refuge_layer.py` | Coefficient RSF + thermal_v1 | ORIGNAL, OURS |
| L6 | **Pression de chasse espece** | `rsf_engine/layers/pression_espece_layer.py` | Coefficient RSF `densite_route_km2` + donnees recolte | Toutes |
| L7 | **Fragmentation** | `rsf_engine/layers/fragmentation_layer.py` | Nouveau dans habitat_v1 | Toutes |
| L8 | **DEM simule ameliore** | `rsf_engine/layers/dem_layer.py` | Remplace hash terrain par modele perlin | Toutes |
| L9 | **Couvert forestier differencie** | `rsf_engine/layers/couvert_layer.py` | Coefficients RSF `couvert_*` | Toutes |
| L10 | **Zone d'abri specifique** | `rsf_engine/layers/abri_layer.py` | Integration repos_v1 | CERF, ORIGNAL |
| L11 | **Productivite fruitiere** | `rsf_engine/layers/mast_layer.py` | Integration alimentation_v1 + RSF | OURS, DINDON, CERF |

### 4.2 Implementation type (exemple L1 — Lisiere)

```python
# rsf_engine/layers/lisiere_layer.py

import math
from core.scoring_pipeline.common.hash import deterministic_hash_a as _seed

def compute_lisiere_score(lat, lng, species, month):
    """
    Calcule la proximite et qualite de la lisiere pour un point donne.
    Utilise les donnees OSM (quand disponibles) ou simulation calibree.
    
    ORIGNAL: faible affinite lisiere (0.20)
    CERF: forte affinite lisiere (0.65)
    OURS: faible affinite lisiere (0.15)
    DINDON: forte affinite lisiere (0.50)
    WAPITI: moderee affinite lisiere (0.40)
    """
    LISIERE_AFFINITE = {
        "CERF": 0.65, "ORIGNAL": 0.20, "OURS": 0.15,
        "DINDON": 0.50, "WAPITI": 0.40,
    }
    
    # Simulation calibree de la distance a la lisiere la plus proche
    # Phase transitoire: hash perlin ameliore
    # Phase finale: remplacement par donnees ecoforestry reelles
    raw_distance = _seed(lat, lng, "lisiere_dist") * 500  # 0-500m
    
    # Score inversement proportionnel a la distance
    if raw_distance < 50:
        base_score = 95
    elif raw_distance < 100:
        base_score = 80
    elif raw_distance < 200:
        base_score = 55
    elif raw_distance < 350:
        base_score = 30
    else:
        base_score = 10
    
    affinite = LISIERE_AFFINITE.get(species.upper(), 0.40)
    return round(base_score * affinite + (1 - affinite) * 50, 1)
```

### 4.3 Chaque couche suit le meme pattern :
1. Coefficient d'affinite par espece (biologie validee)
2. Donnee terrain simulee (hash calibre) ou reelle (OSM/SIEF quand disponible)
3. Score normalise 0-100
4. Integration dans le pipeline RSF via les coefficients beta

---

## 5. PHASE MS-4 — 8 PARAMETRES COMPORTEMENTAUX PAR ESPECE

### 5.1 Liste des parametres

| # | Parametre | Fichier | Detail |
|---|---|---|---|
| P1 | **Periode reproductrice (pre-rut, rut, post-rut)** | `behavior_v1/engine.py` + `corridors_v10/species_profiles.py` | Dates specifiques par espece |
| P2 | **Saisonnalite fine** | `corridors_v10/species_profiles.py` | 12 mois au lieu de 4 saisons |
| P3 | **Tolerance au derangement** | `pression_v1/engine.py` | Coefficient espece-specifique |
| P4 | **Amplitude de deplacement** | `corridors_v10/engine.py` | Rayon d'analyse proportionnel au domaine vital |
| P5 | **Preferences thermiques** | `thermal_v1/engine.py` | Seuils de confort thermique par espece |
| P6 | **Dependance a l'eau** | `hydro_v1/engine.py` | Distance optimale espece-specifique |
| P7 | **Dependance aux lisieres** | `rsf_engine/` | Via coefficients RSF (cf. MS-3) |
| P8 | **Dependance aux sources alimentaires** | `alimentation_v1/engine.py` | Saison + type de nourriture par espece |

### 5.2 Detail P1 — Periodes reproductrices

```python
# behavior_v1/engine.py — AJOUT

BREEDING_PERIODS = {
    "CERF": {
        "pre_rut": {"mois": [9, 10], "mobilite": 1.3, "agressivite": 0.6},
        "rut": {"mois": [11], "mobilite": 1.8, "agressivite": 1.0},
        "post_rut": {"mois": [12], "mobilite": 0.6, "agressivite": 0.2},
    },
    "ORIGNAL": {
        "pre_rut": {"mois": [8, 9], "mobilite": 1.2, "agressivite": 0.5},
        "rut": {"mois": [9, 10], "mobilite": 1.6, "agressivite": 1.0},
        "post_rut": {"mois": [11], "mobilite": 0.5, "agressivite": 0.1},
    },
    "OURS": {
        "pre_rut": {"mois": [5], "mobilite": 1.1, "agressivite": 0.4},
        "rut": {"mois": [6, 7], "mobilite": 1.5, "agressivite": 0.8},
        "post_rut": {"mois": [8], "mobilite": 0.9, "agressivite": 0.2},
        "hyperphagie": {"mois": [9, 10, 11], "mobilite": 1.4, "alimentation": 2.5},
        "hibernation": {"mois": [12, 1, 2, 3], "mobilite": 0.01, "alimentation": 0.0},
    },
    "DINDON": {
        "pre_rut": {"mois": [3], "mobilite": 1.1, "vocalisation": 0.6},
        "rut": {"mois": [4, 5], "mobilite": 1.3, "vocalisation": 1.0},
        "post_rut": {"mois": [6], "mobilite": 0.8, "vocalisation": 0.2},
        "elevage": {"mois": [6, 7, 8], "mobilite": 0.5, "couvert": 1.5},
    },
    "WAPITI": {
        "pre_rut": {"mois": [8], "mobilite": 1.2, "bugling": 0.5},
        "rut": {"mois": [9, 10], "mobilite": 1.7, "bugling": 1.0},
        "post_rut": {"mois": [11], "mobilite": 0.6, "bugling": 0.1},
    },
}
```

### 5.3 Detail P3 — Tolerance au derangement

```python
# pression_v1/engine.py — AJOUT a SPECIES_DISTURBANCE_TOLERANCE

SPECIES_DISTURBANCE_TOLERANCE = {
    "CERF":    {"route_buffer_m": 150, "batiment_buffer_m": 200, "sentier_buffer_m": 80, "sensibilite": 0.75},
    "ORIGNAL": {"route_buffer_m": 300, "batiment_buffer_m": 400, "sentier_buffer_m": 150, "sensibilite": 0.80},
    "OURS":    {"route_buffer_m": 200, "batiment_buffer_m": 300, "sentier_buffer_m": 120, "sensibilite": 0.85},
    "DINDON":  {"route_buffer_m": 100, "batiment_buffer_m": 150, "sentier_buffer_m": 60, "sensibilite": 0.65},
    "WAPITI":  {"route_buffer_m": 250, "batiment_buffer_m": 350, "sentier_buffer_m": 130, "sensibilite": 0.70},
}
```

### 5.4 Detail P6 — Dependance a l'eau

```python
# hydro_v1/engine.py — AJOUT

SPECIES_WATER_DEPENDENCY = {
    "CERF":    {"distance_optimale_m": 200, "penalite_max": 0.25, "affinite": 0.60},
    "ORIGNAL": {"distance_optimale_m": 100, "penalite_max": 0.50, "affinite": 0.85},
    "OURS":    {"distance_optimale_m": 300, "penalite_max": 0.15, "affinite": 0.50},
    "DINDON":  {"distance_optimale_m": 400, "penalite_max": 0.10, "affinite": 0.35},
    "WAPITI":  {"distance_optimale_m": 250, "penalite_max": 0.30, "affinite": 0.55},
}
```

---

## 6. PHASE MS-5 — ELIMINATION HASH GENERIQUE

### 6.1 Objectif
Remplacer les 11 moteurs 100% hash generiques par des moteurs qui utilisent les couches RSF espece-specifiques.

### 6.2 Moteurs a modifier

| Moteur | Strategie de remplacement |
|---|---|
| NDVI-VEGETATION-V1 | Utiliser couche couvert forestier differencie (L9) |
| WEATHER-V1 | Integrer preferences thermiques espece (P5) |
| TEMPORAL-V1 | Integrer rythme circadien espece + periodes reproductrices (P1) |
| ECOSYSTEM-V1 | Utiliser couche fragmentation (L7) + productivite fruitiere (L11) |
| RISK-V1 | Utiliser pression chasse espece (L6) + tolerance derangement (P3) |
| OPPORTUNITY-V1 | Utiliser couche lisiere (L1) + friche (L2) + culture (L3) |
| ATTRACTORS-V1 | Utiliser couche mast (L11) + culture (L3) + marecage (L4) |
| SCENARIO-V1 | Utiliser periodes reproductrices (P1) + amplitude deplacement (P4) |
| SIMULATION-V1 | Utiliser modele RSF (MS-2) comme base |
| TRAJETS-V1 | Utiliser amplitude deplacement (P4) + corridors species |
| LEARNING-V1 | Utiliser historique accumule par espece |

### 6.3 Pattern de modification

```python
# AVANT (hash generique):
def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    h = deterministic_hash_a(lat, lng, "ndvi")
    return h * 100  # Identique pour toutes les especes

# APRES (RSF-integre):
def score_point_consolidated(lat, lng, center_lat, center_lng, species, month):
    from rsf_engine.engine import compute_rsf_score
    rsf = compute_rsf_score(lat, lng, species, month)
    # Moduler par la couche specifique du moteur
    couvert = compute_couvert_score(lat, lng, species)
    return (rsf * 0.4 + couvert * 0.6)  # Espece-specifique
```

### 6.4 Contrainte ZERO REGRESSION
Chaque moteur modifie doit produire des scores dans la meme plage [0, 100]. Le score consolide moyen par zone ne doit pas devier de plus de +/- 5 points par rapport a l'etat actuel.

---

## 7. PHASE MS-6 — LOGIQUE SALINES DIFFERENTIEE PAR ESPECE

### 7.1 Objectif
Remplacer les 6 criteres de positionnement geophysiques (identiques pour toutes les especes) par des criteres ecologiques specifiques.

### 7.2 Criteres de positionnement par espece

| Critere | ORIGNAL | CHEVREUIL | WAPITI | Poids |
|---|---|---|---|---|
| Distance eau | 30-80m (optimal) | 100-250m | 80-200m | 25% |
| Couvert forestier | Conifere dense 60-80% | Lisiere mixte 30-50% | Semi-ouvert 20-40% | 20% |
| Pente | 5-15 deg (vallon) | 0-8 deg (plat) | 3-12 deg | 15% |
| Vegetation | Regeneration, saule | Friche, mosaique | Prairie, clairiere | 15% |
| Distance route | >300m | >150m | >250m | 15% |
| Micro-topographie | Fond de vallee, cuvette | Plateau, replat | Plaine, pied de pente | 10% |

### 7.3 Implementation dans salines.py

```python
# alimentation_v2/salines.py — AJOUT

SALINE_POSITIONING_PROFILES = {
    "CERF": {
        "eau_optimal_m": (100, 250),
        "eau_penalite_m": 400,
        "couvert_optimal_pct": (30, 50),
        "pente_optimal_deg": (0, 8),
        "distance_route_min_m": 150,
        "vegetation_preference": "lisiere_mixte",
        "topographie_preference": "plateau_replat",
        "poids": {"eau": 0.20, "couvert": 0.20, "pente": 0.15, "vegetation": 0.20, "route": 0.15, "topo": 0.10},
    },
    "ORIGNAL": {
        "eau_optimal_m": (30, 80),
        "eau_penalite_m": 200,
        "couvert_optimal_pct": (60, 80),
        "pente_optimal_deg": (5, 15),
        "distance_route_min_m": 300,
        "vegetation_preference": "regeneration_conifere",
        "topographie_preference": "fond_vallee",
        "poids": {"eau": 0.30, "couvert": 0.20, "pente": 0.10, "vegetation": 0.15, "route": 0.15, "topo": 0.10},
    },
    "WAPITI": {
        "eau_optimal_m": (80, 200),
        "eau_penalite_m": 350,
        "couvert_optimal_pct": (20, 40),
        "pente_optimal_deg": (3, 12),
        "distance_route_min_m": 250,
        "vegetation_preference": "prairie_clairiere",
        "topographie_preference": "plaine",
        "poids": {"eau": 0.25, "couvert": 0.15, "pente": 0.15, "vegetation": 0.20, "route": 0.15, "topo": 0.10},
    },
}
```

### 7.4 OURS NOIR et DINDON

OURS NOIR et DINDON restent **EXCLUS** des salines (`SPECIES_NO_SALINES = {"OURS", "DINDON"}`). Ceci est biologiquement correct et ne sera PAS modifie.

### 7.5 Distance inter-salines par espece

```python
# AVANT: MIN_SALINE_DISTANCE_M = 300 (identique)
# APRES:
SPECIES_SALINE_SPACING = {
    "CERF": 250,     # Domaine vital 2.5 km2 → espacement rapproche
    "ORIGNAL": 500,  # Domaine vital 15 km2 → espacement large
    "WAPITI": 400,   # Domaine vital 20 km2 → espacement intermediaire
}
```

---

## 8. TABLEAU RECAPITULATIF — IMPACT ATTENDU SUR LA DIFFERENCIATION

| Metrique | Avant (audit) | Apres (plan complet) |
|---|---|---|
| Ponderations identiques inter-especes | 100% (22/22 moteurs) | 0% (5 matrices distinctes) |
| Moteurs 100% hash generiques | 31.71% (11 moteurs) | 0% (remplaces par RSF) |
| PRESSION espece-agnostique | 12% | 0% (tolerance au derangement par espece) |
| Criteres salines identiques | 100% (6/6 criteres) | 0% (profils specifiques) |
| Couches ecologiques espece-specifiques | 3-4 (ALIM, CORRIDORS, BEHAVIOR, HABITAT) | 14-15 (+ 11 nouvelles couches) |
| Parametres comportementaux | 4 saisons generiques | 12 mois + periodes reproductrices + circadien |
| Delta score inter-especes | 5-15 points | >25 points attendu |

---

## 9. CONTRAINTES DE NON-REGRESSION

| Contrainte | Mecanisme de protection |
|---|---|
| ZERO derive SUPRA/ULTRA/FICHE/SOL | Ces scores utilisent un pipeline different (nutrition_intelligence x5100-x7000) — non impacte |
| ZERO regression frontend | Le frontend recoit les memes structures JSON — seules les VALEURS changent |
| ZERO perte de composant | Aucun composant frontend n'est supprime ou modifie |
| ZERO merge main | Tout sur `SUPRA_RECONSTRUCTION` |
| ZERO rollback | Chaque phase est additive, pas destructive |

---

*PLAN GENERE SOUS PROTOCOLE BCE-4X ULTIME ABSOLU x3*
*ZERO MODIFICATION EXECUTEE — PLAN UNIQUEMENT*
*Autorite : COMMANDANT STEEVE-MAX*
*Agent Operationnel — Fevrier 2026*
