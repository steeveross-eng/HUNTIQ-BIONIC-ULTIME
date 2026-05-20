# SPÉCIFICATION RECETTES AUTOMATIQUES PAR ESPÈCE · V12-SUPRA+ · Ω

**Doctrine** : `P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_RECETTES_AUTOMATIQUES_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟡 **SPÉCIFICATION DOCTRINALE · PLAN_SEULEMENT** — validation explicite Commandant requise avant implémentation
**Contexte** : Suite directive Commandant définissant la sortie attendue de V12-SUPRA+ pour
les **recettes automatiques par espèce** (4 blocs : besoins · déficits · recette saline · recette alimentaire)

---

## 1. ANALYSE DE COUVERTURE — CARTOGRAPHIE CHAMP → MOTEUR SOURCE

### 1.1 BLOC 1 — Synthèse des besoins (`{species}`, `{month}`, `{profil_physio}`)

| Champ demandé | Source actuelle | Disponibilité | Détails |
|---|---|---|---|
| `proteines_g_jour` | `x5500_energy_protein.compute_energy_protein(species, season)` | 🟢 **EXISTE** | Endpoint `/api/v6/nutrition-intelligence/energy-protein` |
| `energie_kcal_jour` | idem `x5500_energy_protein` | 🟢 **EXISTE** | idem |
| `ca_mg_jour` | `wildlife_nutritional_engine.SPECIES_NEEDS[species]["minerals"]["Ca"]` | 🟢 **EXISTE** | Tables NRC : `{base, antler, gestation, rut, winter}` |
| `p_mg_jour` | idem `SPECIES_NEEDS["P"]` | 🟢 **EXISTE** | idem |
| `na_mg_jour` | idem `SPECIES_NEEDS["Na"]` | 🟢 **EXISTE** | idem |
| `mg_mg_jour` | idem `SPECIES_NEEDS["Mg"]` | 🟢 **EXISTE** | idem |
| `zn_mg_jour` | idem `SPECIES_NEEDS["Zn"]` | 🟢 **EXISTE** | idem |
| `se_mg_jour` | idem `SPECIES_NEEDS["Se"]` (à vérifier présence ligne) | 🟡 **PROBABLE** | Tables NRC contiennent Se selon header doctrinal |

→ **Couverture BLOC 1 : 100 %** · aucun nouveau calcul nécessaire.

### 1.2 BLOC 2 — Déficits (par minéral, %)

| Champ demandé | Source actuelle | Disponibilité | Détails |
|---|---|---|---|
| `deficit_ca_pct` | `compute_nutrition_v12._carences_point["Ca"]` | 🟢 **EXISTE (grille)** | Calculé par point grille 25×25 |
| `deficit_p_pct` | ❌ **MANQUANT en grille V12** | 🔴 **À AJOUTER** | Tables NRC ont `P` mais pas dans `_carences_point` |
| `deficit_na_pct` | `compute_nutrition_v12._carences_point["Na"]` | 🟢 **EXISTE (grille)** | idem |
| `deficit_mg_pct` | `compute_nutrition_v12._carences_point["Mg"]` | 🟢 **EXISTE (grille)** | idem |
| `deficit_zn_pct` | ❌ **MANQUANT en grille V12** | 🔴 **À AJOUTER** | Tables NRC ont `Zn` mais pas dans grille |
| `deficit_se_pct` | ❌ **MANQUANT en grille V12** | 🔴 **À AJOUTER** | idem |

**Source complémentaire existante** : `engine_carence_nutritionnelle_omega` (E39) gère **tous les 5 minéraux**
(Na, Ca, P, Mg, K) avec besoins relatifs par espèce — **mais pas Zn/Se**.

→ **Couverture BLOC 2 : 50 %** · 3 minéraux manquants en grille spatiale (P, Zn, Se).

### 1.3 BLOC 3 — Recette saline recommandée

| Champ demandé | Source actuelle | Disponibilité | Détails |
|---|---|---|---|
| `produit_base` + `score_produit/100` | `x5800_recipe_engine.generate_recipe(species, season, soil_type, substrate, site_minerals)` + `x6000_product_score` | 🟢 **EXISTE** | Endpoint `/api/v6/nutrition-intelligence/recipe` |
| `ratio_cap_cible` | ❌ **MANQUANT** | 🔴 **À AJOUTER** | Tables NRC ont Ca + P mais aucune cible Ca:P explicite |
| `nacl_g_jour` | ❌ **MANQUANT (NaCl explicit)** | 🔴 **À AJOUTER** | sodium_index présent · NaCl = Na × 2.54 à calculer |
| `zn_ppm_cible` | `saline_recommendation_engine._generate_custom_recipe` (par mineral) | 🟢 **EXISTE PARTIEL** | Recipe components incluent supplément_mg_per_kg · conversion ppm requise |
| `se_ppm_cible` | idem | 🟢 **EXISTE PARTIEL** | idem |

**Source `saline_recommendation_engine._generate_custom_recipe`** retourne déjà :
- `recipe_components` : liste `{mineral, supplement_mg_per_kg}`
- `base_carrier` : `sel_marin` ou `argile_bentonite`
- `format_recommande` : `granules` ou `bloc`

→ **Couverture BLOC 3 : 60 %** · ratio Ca:P explicit + NaCl g/jour absents · `ppm_cible` dérivables de `supplement_mg_per_kg`.

### 1.4 BLOC 4 — Recette alimentaire complémentaire

| Champ demandé | Source actuelle | Disponibilité | Détails |
|---|---|---|---|
| `kg_mais_semaine` | `engine_champs_nourriciers_omega._CROP_ATTRACT["mais"][species]` (table attractivité 0-1) | 🟡 **PARTIEL** | Score 0-1 par espèce, **PAS de conversion en kg/semaine** |
| `kg_soya_semaine` | idem soya | 🟡 **PARTIEL** | idem |
| `surface_m2` (trèfle/luzerne/brassicas) | idem luzerne (pomme/avoine présents) | 🟡 **PARTIEL** | Pas de calcul m² doctrinal |
| `type_champ_nourricier_recommande` | `engine_champs_nourriciers_omega.compute_champs_nourriciers` retourne `top_crop` par espèce | 🟢 **EXISTE** | Sélection meilleure culture pondérée saison |

**Tables existantes `_CROP_ATTRACT`** (engine_champs_nourriciers_omega.py) :
```python
mais     : orignal 0.70, chevreuil 0.95, ours 0.85, dindon 1.00, wapiti 0.85
soya     : orignal 0.40, chevreuil 0.80, ours 0.55, dindon 0.70, wapiti 0.55
luzerne  : orignal 0.85, chevreuil 0.90, ours 0.30, dindon 0.35, wapiti 0.90
avoine   : orignal 0.70, chevreuil 0.75, ours 0.40, dindon 0.85, wapiti 0.75
pomme    : orignal 0.75, chevreuil 0.80, ours 0.95, dindon 0.50, wapiti 0.70
```

**Saisonnalité** : `season_factor = 1.2 si mois ∈ [8,9,10] · 0.9 si [6,7] · 0.5 sinon`

→ **Couverture BLOC 4 : 50 %** · attractivités + types présents · **conversions kg/semaine et m² non doctrinées**.

### 1.5 Synthèse couverture globale

| Bloc | Champs demandés | Disponibles | Manquants | Couverture |
|---|---|---|---|---|
| 1. Besoins | 8 | 8 | 0 | **100%** |
| 2. Déficits | 6 | 3 | 3 (P, Zn, Se en grille) | **50%** |
| 3. Recette saline | 5 | 3 partiels | 2 (Ca:P, NaCl) | **60%** |
| 4. Recette alimentaire | 4 | 1 + 3 partiels | conversions kg/m² | **50%** |
| **GLOBAL** | **23** | **15** (4 complets · 11 partiels) | **8 manquants stricts** | **~65 %** |

---

## 2. SPÉCIFICATION DOCTRINALE V12-SUPRA+ RECETTES

### 2.1 Position d'intégration (RECOMMANDATION OPTION B)

```
engine_nutrition_v12_supra_plus.py (NOUVEAU · additif)
  ├── compute_nutrition_v12_plus(species, month, profil, lat, lon, ...)
  │   │
  │   ├── 1. Appelle compute_nutrition_v12() (HUB INTACT)
  │   ├── 2. Appelle x5500_energy_protein (besoins protéines/énergie)
  │   ├── 3. Appelle wildlife_nutritional_engine.SPECIES_NEEDS (minéraux mg/jour)
  │   ├── 4. Calcule déficits étendus (5 minéraux + trace Zn/Se)
  │   ├── 5. Appelle saline_recommendation_engine.generate_full_analysis
  │   ├── 6. Appelle x5800_recipe_engine.generate_recipe (produit base)
  │   ├── 7. Appelle x6000_product_score (score produit)
  │   ├── 8. Appelle engine_champs_nourriciers_omega (champs nourriciers)
  │   ├── 9. Calcule conversions kg/semaine et m² (doctrine V12+)
  │   └── 10. Assemble bloc "recette_automatique"
  │
  └── Retourne bundle V12 enrichi avec section "recette_automatique" {1, 2, 3, 4}
```

### 2.2 Schéma de sortie "recette_automatique" — STRUCTURE DOCTRINALE

```json
{
  "engine": "ENGINE-NUTRITION-V12-SUPRA-PLUS",
  "version": "V12+-2026-04",
  "waypoint": {"species": "chevreuil", "month": 10, "profil": "mâle_rut"},

  "1_besoins_journaliers": {
    "proteines_g_jour": 280,
    "energie_kcal_jour": 8500,
    "mineraux_mg_jour": {
      "Ca": 18000,
      "P":  12000,
      "Na":  4000,
      "Mg":  3000,
      "Zn":   150,
      "Se":     5
    },
    "sources": {
      "proteines_energie": "x5500_energy_protein",
      "mineraux": "wildlife_nutritional_engine.SPECIES_NEEDS"
    }
  },

  "2_deficits_pct": {
    "Ca": 12.5,
    "P":  18.3,
    "Na": 65.0,
    "Mg":  8.2,
    "Zn": 22.1,
    "Se": 45.6,
    "sources": {
      "Ca_Na_Mg": "compute_nutrition_v12._carences_point",
      "P_Zn_Se":  "engine_nutrition_v12_supra_plus._carences_etendus (NOUVEAU)"
    }
  },

  "3_recette_saline": {
    "produit_base": "REDMOND_NATURAL_TRACE_MINERAL_SALT",
    "score_produit": 87,
    "ratio_cap_cible": "1.5:1",
    "ratio_cap_actuel": "1.2:1",
    "nacl_g_jour": 10.16,
    "trace_minerale": {
      "Zn_ppm_cible": 420,
      "Se_ppm_cible":  18
    },
    "base_carrier": "sel_marin",
    "format_recommande": "bloc",
    "sources": {
      "produit_base":   "x5800_recipe_engine + x6000_product_score",
      "ratio_cap":      "v12_supra_plus._compute_ratio_cap (NOUVEAU)",
      "nacl":           "v12_supra_plus._compute_nacl_g_jour (NOUVEAU = Na × 2.54)",
      "trace_minerale": "saline_recommendation_engine._generate_custom_recipe"
    }
  },

  "4_recette_alimentaire": {
    "type_champ_nourricier_recommande": "luzerne",
    "attractivite_score": 0.90,
    "saison_factor": 1.2,
    "kg_mais_semaine": 1.0,
    "kg_soya_semaine": 0.4,
    "surface_m2": {
      "trefle":    400,
      "luzerne":   600,
      "brassicas": 250
    },
    "ajustement_terrain": "Sol acide pH 5.8 — privilégier brassicas tolérantes",
    "sources": {
      "type_champ":  "engine_champs_nourriciers_omega.compute_champs_nourriciers",
      "kg_semaine":  "v12_supra_plus._convert_attract_to_kg_semaine (NOUVEAU)",
      "surface_m2":  "v12_supra_plus._compute_surface_m2_par_individu (NOUVEAU)",
      "ajustement":  "x6020_terrain_solutions.get_solutions_for_deficits"
    }
  },

  "_doctrine": "P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_RECETTES_AUTOMATIQUES_Ω",
  "_phase_iii_lock": "MAINTENU",
  "_data_sources_aggregated": {
    "lidar":  "OK|ABSENT",
    "irda":   "OK|ABSENT",
    "ndvi":   "STUB",
    "open_meteo": "CACHED (WeatherCacheRegional_Ω)"
  }
}
```

---

## 3. MODULES NOUVEAUX À CRÉER (V12-SUPRA+ STRICTEMENT ADDITIF)

| Module / Fonction | Rôle | LoC approx |
|---|---|---|
| `engine_nutrition_v12_supra_plus.py` | Wrapper additif hub | ~250 |
| `_carences_etendus(point, terrain, besoins_full)` | Grille spatiale 5 minéraux + Zn + Se | ~80 |
| `_compute_ratio_cap(deficits, besoins)` | Calcul ratio Ca:P cible vs actuel | ~30 |
| `_compute_nacl_g_jour(na_mg_jour)` | NaCl = Na × 2.54 (PM Na=23, NaCl=58.44) | ~10 |
| `_convert_attract_to_kg_semaine(crop, species, attractivite)` | Conversion 0-1 → kg pour 1 individu/semaine | ~50 |
| `_compute_surface_m2_par_individu(crop, species, n_individus_estimes)` | Conversion attractivité → m² doctrinaux | ~50 |
| `_aggregate_v12_plus(...)` | Assemblage final 4 blocs | ~80 |

**Total volume code estimé** : ~550 LoC (vs V12 actuel 749 LoC — **wrapper ≈ 70% taille hub**).

---

## 4. PARAMÈTRES DOCTRINAUX À VALIDER PAR COMMANDANT

### 4.1 Conversions kg/semaine
**Proposition** :
```python
kg_mais_semaine = (
    attractivite_crop × 7 × consommation_journalière_kg(species)
)
# Consommation journalière (kg matière sèche)
consommation = {
    "orignal":    7.0,  # ~7 kg MS/jour
    "chevreuil":  1.5,
    "wapiti":     6.0,
    "ours_noir":  4.0,
    "dindon":     0.15,
    "coyote":     0.5,  # carnivore (n/a pour culture)
}
```
→ Exemple chevreuil maïs : `0.95 × 7 × 1.5 = 9.97 kg/semaine` (≈ 1 poche 10 kg → cohérent avec "1 poche / individu / semaine").

### 4.2 Surface m² par individu
**Proposition** :
```python
# Surface optimale par individu cible (50 % de la conso journalière en plante locale)
surface_m2 = {
    "trefle":    {"chevreuil": 400, "orignal": 800, "wapiti": 700, "ours": 200, "dindon": 50},
    "luzerne":   {"chevreuil": 600, "orignal": 1000, "wapiti": 900, "ours": 250, "dindon": 80},
    "brassicas": {"chevreuil": 250, "orignal": 450, "wapiti": 400, "ours": 150, "dindon": 30},
}
# Ajustés par n_individus_estimes (depuis chain_omega_cascade pression chasse)
```

### 4.3 Ratio Ca:P cible par espèce
**Proposition** (NRC literature) :
```python
ratio_cap_cible = {
    "orignal":   "1.5:1",   # bois en croissance
    "chevreuil": "1.5:1",
    "wapiti":    "1.5:1",
    "ours_noir": "1.2:1",   # carnivore-omnivore
    "dindon":    "2.0:1",   # ponte
    "coyote":    "1.2:1",
}
```

### 4.4 NaCl conversion
**Standard chimique** :
- NaCl = Na × (58.44 / 23.0) = Na × 2.54
- Pour `na_mg_jour = 4000 mg` → `nacl_g_jour = 4 × 2.54 = 10.16 g`

---

## 5. ENDPOINTS V12+ PROPOSÉS

### 5.1 Nouveau endpoint REST
```
POST /api/v6/nutrition-intelligence/v12-plus/recette-automatique
Body : { species, month, profil, lat?, lon? }
Response : bundle V12+ complet (cf. §2.2)
```

### 5.2 Intégration NutritionPanelOmega
**Aucune modification UI** — les 11 sections existantes peuvent absorber le bundle V12+ :
- `besoins_journaliers` ← bloc 1
- `carences` ← bloc 2
- `recettes_minerales` ← bloc 3
- `recommandations` ← bloc 4

→ Section UI **`recettes_automatiques`** pourrait être ajoutée comme 12e section, optionnel.

---

## 6. INTÉGRATION DANS β2-ΣΤ (CHAÎNE V20→V10→NUTRITION)

### 6.1 Option A — Calculée à chaque tuile (impact compute)
Modifier `territoire_v10_supra.py` ligne 1273 :
```python
from engines.v8_institutional.engine_nutrition_v12_supra_plus import compute_nutrition_v12_plus
nutrition = compute_nutrition_v12_plus(...)  # remplace v12
```
**Risque** : ~50-100 ms par tuile additionnels → **EXCLU** car V20 déjà à 213s/tuile.

### 6.2 Option B (RECOMMANDÉE) — Calculée à la demande (UI)
**Aucune modification de la chaîne V20/β2-ΣΤ**. V12+ devient endpoint à la demande :
- Frontend POST `/api/v6/nutrition-intelligence/v12-plus/recette-automatique` lors double-clic saline
- Backend appelle V12+ qui lit le bundle V12 déjà en cache R2 et l'enrichit avec recettes
- Latence cible **< 200 ms** (lookup cache + computations légères + tables)

→ **β2-ΣΤ continue inchangé** · pas d'impact sur ETA 3 RF.

---

## 7. VERROU PHASE III · CONFORMITÉ V12-SUPRA+

| Composant | Statut planifié V12+ |
|---|---|
| `engine_nutrition_v12_supra.py` | ❌ INTACT (delegation depuis V12+) |
| `wildlife_nutritional_engine.py` (saline) | ❌ INTACT (lecture tables NRC) |
| `engine_carence_nutritionnelle_omega.py` | ❌ INTACT (lecture tables besoins) |
| `engine_champs_nourriciers_omega.py` | ❌ INTACT (lecture tables crops) |
| `x5500_energy_protein`, `x5800_recipe_engine`, etc. | ❌ INTACTS (lecture fonctions) |
| `NutritionPanelOmega.jsx` | ❌ INTACT (consomme bundle élargi) |
| `compute_territoire_v10` (chaîne V20) | ❌ INTACT (Option B) |
| `tools/zerocost_worker_seed_r5.py` | ❌ INTACT |
| **Nouveau** `engine_nutrition_v12_supra_plus.py` | 🆕 ADDITIF strict |
| **Nouveau** endpoint `/api/v6/.../v12-plus/recette-automatique` | 🆕 ADDITIF strict |

→ **Verrou Phase III strictement respecté**.

---

## 8. DÉCISIONS COMMANDANT REQUISES

Avant implémentation, je requiers la confirmation explicite des points suivants :

| # | Point doctrinal | Validation Commandant |
|---|---|---|
| 1 | Approbation du **schéma JSON** §2.2 (4 blocs structurés) | ☐ APPROUVE / ☐ MODIFIE |
| 2 | Validation des **conversions kg/semaine** §4.1 (orignal 7 kg/j · chevreuil 1.5 kg/j · etc.) | ☐ APPROUVE / ☐ MODIFIE |
| 3 | Validation des **surfaces m²** §4.2 (trèfle 400 / luzerne 600 / brassicas 250 par chevreuil) | ☐ APPROUVE / ☐ MODIFIE |
| 4 | Validation des **ratios Ca:P cibles** §4.3 (1.5:1 cervidés · 1.2:1 ours · 2.0:1 dindon) | ☐ APPROUVE / ☐ MODIFIE |
| 5 | Option d'intégration : ☐ A (in-chain) / ☐ **B (à la demande, recommandée)** | ☐ A / ☐ B |
| 6 | Position UI : ☐ absorber dans 11 sections existantes / ☐ ajouter 12ᵉ section "recettes_automatiques" | ☐ 11 / ☐ 12 |
| 7 | Inclusion **NDVI** : ☐ Attendre TIF raster Q3-Q4 / ☐ V12+ sans NDVI (stub) | ☐ ATTENDRE / ☐ STUB |

---

## 9. PRIORISATION DES MANQUES (8 champs)

| Priorité | Champ manquant | Effort | Impact UX |
|---|---|---|---|
| **P0** | `nacl_g_jour` (formule simple Na × 2.54) | 10 min | Saline binding immédiat |
| **P0** | `ratio_cap_cible` (table espèce) | 30 min | Recette saline crédible |
| **P0** | `deficit_p_pct` en grille | 1h (étend `_carences_point`) | Grille complète 4 minéraux |
| **P1** | `deficit_zn_pct`, `deficit_se_pct` en grille | 2h (étend + tables Zn/Se grille) | Recette trace minérale |
| **P1** | `kg_mais_semaine`, `kg_soya_semaine` (tables conversion) | 1h | Recommandations utilisables terrain |
| **P2** | `surface_m2` brassicas/trèfle/luzerne (table) | 1h | Recommandations parcelles food plots |
| **P2** | `type_champ_nourricier_recommande` ajustement terrain | 1h (via x6020_terrain_solutions) | Crédibilité régionale |

**Effort total estimé** : ~6-7 heures de développement Python · pas de migration BDD · pas d'impact CDN R2.

---

## 10. ARTEFACTS À CRÉER (SUR ORDRE COMMANDANT)

| Fichier | Statut | Description |
|---|---|---|
| `engines/v8_institutional/engine_nutrition_v12_supra_plus.py` | 🟡 PRÊT À CRÉER | Wrapper additif (~550 LoC) |
| `engines/v8_institutional/_v12_plus_tables.py` | 🟡 PRÊT À CRÉER | Tables conversions kg/semaine + m² + ratios Ca:P |
| `engines/nutrition_intelligence/router.py` (additif) | 🟡 ADDITIF | +1 endpoint `/v12-plus/recette-automatique` |
| `tests/test_engine_nutrition_v12_supra_plus.py` | 🟡 PRÊT À CRÉER | Tests unitaires 4 blocs |
| `frontend/.../NutritionPanelOmega.jsx` (optionnel +12ᵉ section) | 🟡 ADDITIF | Section `recettes_automatiques` |

**Tous artefacts en mode INERTE tant que la directive Commandant d'activation n'est pas reçue.**

---

## 11. COMMANDE D'ACTIVATION TYPE

Format attendu si validation :
```
ACTIVATE V12-SUPRA+
- approve schéma §2.2
- conversions §4.1 §4.2 §4.3
- option B (à la demande)
- UI : 11 sections existantes (pas de 12ᵉ)
- NDVI : attendre TIF
- priorités P0 d'abord (nacl + ratio_cap + deficit_p)
```

---

**FIN SPÉCIFICATION V12-SUPRA+ RECETTES AUTOMATIQUES · STATUT : PLAN_SEULEMENT · ATTENTE DIRECTIVE COMMANDANT**

**Verrou Phase III maintenu · β2-ΣΤ continue en mode nominal · aucune modification code engagée.**
