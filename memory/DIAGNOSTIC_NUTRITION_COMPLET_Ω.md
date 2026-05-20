# DIAGNOSTIC NUTRITIONNEL COMPLET BIONIC · Ω

**Doctrine** : `P22ΩΩ_DIAGNOSTIC_NUTRITION_COMPLET_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Méthodologie** : Audit READ-ONLY exhaustif · `grep`/`find` ciblés · cartographie graphes d'appels
**Objectif Commandant** : Éviter tout doublon · préparer intégration **NUTRITION V12-SUPRA+**

---

## 1. SYNTHÈSE EXÉCUTIVE

L'écosystème nutritionnel BIONIC est **richement développé** avec **4 niveaux d'engines**
coexistant, certains délégant explicitement aux autres pour éviter la duplication :

| Niveau | Module | Rôle | Statut |
|---|---|---|---|
| Hub central | `engine_nutrition_v12_supra` | Moteur biologique central (7 outputs obligatoires) | 🔴 ACTIF · appelé par V20→V10 |
| Wrapper V8 | `engine_nutrition` | Délégateur vers nutrition_intelligence + saline_engine + alimentation | 🟡 DÉLÉGATEUR pur |
| Intelligence | `nutrition_intelligence` (x5100-x7000) | 12 sous-engines + 38 endpoints API | 🔴 ACTIF · `/api/v6/nutrition-intelligence` |
| Pipeline V7 | `nutrition_engine_v7` | Pipeline soil→nutrients→forage→metabolism→attractiveness | 🔴 ACTIF · `/api/v7/nutrition` |
| Saline-binding | `wildlife_nutritional_engine` (saline) | Besoins minéraux/jour par espèce/saison/physiologie | 🔴 ACTIF · sub-engine saline_engine |
| Sub-engines | 7 engines saline (mineral, hydrology, vegetation, etc.) | Pipeline saline nutrition | 🔴 ACTIFS |
| Ω auxiliaires | engine_carence + engine_nutritional_attractiveness | Détection carences / synthèse attractivité | 🔴 ACTIFS (E39, E47) |

→ **L'engine hub `compute_nutrition_v12` est appelé systématiquement par `compute_territoire_v10` à chaque requête V20 bundle** (chaîne β2-ΣΤ inclus).

---

## 2. ENGINES NUTRITIONNELS ACTIFS

### 2.1 `ENGINE-NUTRITION-V12-SUPRA` (hub central) 🔴

**Fichier** : `/app/backend/engines/v8_institutional/engine_nutrition_v12_supra.py` (749 LoC)
**Version** : `V12-SUPRA-2026-04`
**Pilier** : BIO-SYSTEME · Sources : `LIDAR_WCS_1M`, `IRDA_PEDOLOGIE`, `OPEN_METEO`
**Doctrine** : auto-register dans registry institutionnel via `_mark(ENGINE_NAME)`

**Fonction principale exposée** :
```python
compute_nutrition_v12(
    lat, lon, species, month, hour,
    terrain_v10, zones, corridors, affuts, hotspots, salines,
    profil="moyenne"  # moyenne|male_rut|femelle_gest|femelle_lact|juvenile
) -> dict  # 7 outputs obligatoires
```

**Modules internes** :
| Sigle | Fonction | Rôle |
|---|---|---|
| **A. SAISON** | `besoins_saison(month) -> dict` | Besoins énergie/protéines/fibres/minéraux par mois (printemps/été/automne/hiver) |
| **B. PHYSIOLOGIE** | `apply_physiologie(besoins, month, profil)` | Modulation mâle rut/bois · femelle gestation/lactation · juvénile · base |
| **C. HABITAT** | `score_habitat(terrain) -> dict` | Score habitat (0-100) depuis terrain LiDAR : densité forêt, essences, structure verticale, hydrologie, pentes |
| **D. DISPONIBILITÉ** | `disponibilite_fourrage(terrain, month)` | Pipeline `Sol → Nutriments → Fourrage → Gibier` (charge portative + indices Na/Ca/Mg) |
| **E. COMPORTEMENT** | `score_zones_alimentation` + `influence_corridors` + `influence_hotspots` | Modulation des artefacts spatiaux par nutrition |
| **F. SALINES** | `attractivite_salines(salines, besoins_eff, dispo, month)` | Multiplicateur attractivité par saline (hook vers SALINES-V11-SUPRA) |
| **G. CARTES** | `_carences_point` + `_besoins_point` + `build_grid` | Grilles spatiales 25×25 points autour du waypoint |

**Outputs obligatoires** (7) :
1. `score_nutritionnel` (0-100) — waypoint central composite habitat 35% + charge 30% + couverture 35%
2. `carte_carences` — grille points {lat, lng, severity, carence (Na/Ca/Mg)}
3. `carte_besoins` — grille points {lat, lng, besoin_dominant, intensite}
4. `zones_alimentation` — zones existantes scorées nutrition
5. `attractivite_salines` — `{saline_id: multiplier}`
6. `influence_corridors` — `[{corridor_id, boost_delta}]`
7. `influence_hotspots` — `[{hotspot_id, boost_delta}]`

**Constantes Besoins minéraux** (extrait, mois × catégorie) :
```python
# Printemps (avril-mai) : recuperation hiver, lactation debutante
energie=75, proteines=90, fibres=50, mineraux_ca=85, mineraux_na=80, mineraux_mg=60
# Été (juin-août) : pression salines maximale
energie=55, proteines=70, fibres=55, mineraux_ca=70, mineraux_na=75, mineraux_mg=55
# Automne (sept-oct) : reserves + rut males (+30% energie)
energie=95, proteines=65, fibres=70, mineraux_ca=55, mineraux_na=45, mineraux_mg=50
# Hiver (nov-mars) : thermogenese
energie=90, proteines=60, fibres=80, mineraux_ca=40, mineraux_na=30, mineraux_mg=45
```

**Indices nutritionnels calculés** depuis terrain :
- `calcium_index` = min(1, sol_quality × 0.4 + (1-|drainage-5|/5) × 0.4 + feuillus × 0.2)
- `sodium_index` = min(1, (1-moisture) × 0.3 + (drainage/7) × 0.4 + 0.3) — **Na faible en boréal**
- `magnesium_index`, `nitrogen_index`, etc. (depuis lignes 295-310)

**Déficits calculés** (par point grille) :
```python
"Na": besoins["mineraux_na"] - dispo_local["sodium_index"] × 100  # déficit %
"Ca": besoins["mineraux_ca"] - dispo_local["calcium_index"] × 100
"Mg": besoins["mineraux_mg"] - dispo_local["magnesium_index"] × 100
```

**Métadonnées sources** retournées :
```python
"data_sources": {
    "terrain": terrain.source,
    "terrain_fiabilite": 0-100,
    "lidar": "OK"|"ABSENT"|"INCONNU",
    "irda": "OK"|"ABSENT"|"INCONNU",
}
```

### 2.2 `ENGINE_NUTRITION_V12_SUPRA+` (proposé) ⏳

**Statut** : **N'EXISTE PAS ENCORE**. Cible du Commandant pour intégration future.
**Fichier cible suggéré** : `/app/backend/engines/v8_institutional/engine_nutrition_v12_supra_plus.py`
**Différence attendue avec V12** : à définir par Commandant — voir §10.

### 2.3 `ENGINE 08 — NUTRITION-MINERAUX` (V8 wrapper) 🟡

**Fichier** : `/app/backend/engines/v8_institutional/engine_nutrition.py` (39 LoC)
**Rôle** : **DÉLÉGATEUR PUR**, aucune logique métier.
**Délégué à** :
- `nutrition_intelligence/` (12 sous-engines x5100-x7000)
- `modules/saline_engine/engines/` (7 sub-engines)
- `core/scoring_pipeline/alimentation_v1/` + `alimentation_v2/`
**Status** : "ACTIF — delegation preservée"

### 2.4 `ENGINE_CARENCE_NUTRITIONNELLE_Ω` 🔴

**Fichier** : `engines/v8_institutional/engine_carence_nutritionnelle_omega.py`
**Niveau** : BIOLOGIE (E39) · Rôle SECONDAIRE · Priorité MAJEUR
**Version** : `V1-SUPRA-2026-04`
**Tables internes** : besoins minéraux relatifs par espèce (orignal/chevreuil/cerf/ours_noir/dindon/wapiti)
- Orignal : Na=1.30, Ca=1.15, P=1.05, Mg=1.00, K=1.05
- Chevreuil : Na=1.20, Ca=1.10, P=1.00, Mg=0.95, K=1.05
- Ours_noir : Na=0.90, Ca=1.20, P=1.15, Mg=0.90, K=1.00
- Dindon : Na=0.60, Ca=1.35, P=1.15, Mg=0.80, K=0.95
- Wapiti : Na=1.25, Ca=1.15, P=1.10, Mg=1.00, K=1.05

### 2.5 `ENGINE_NUTRITIONAL_ATTRACTIVENESS_Ω` 🔴

**Fichier** : `engine_nutritional_attractiveness_omega.py`
**Niveau** : FUSION/SYNTHÈSE (E47) · Rôle PRINCIPAL · Priorité CRITIQUE
**Fonction** : `compute_nutritional_attractiveness(species, forage_quality, champs_nourriciers, sol_nutriments, recettes_salines, sante_physio)` → synthèse multi-sources

### 2.6 `engine_nutritional_attractiveness_omega` (E47 fusion) 🔴

Idem ci-dessus — engine de synthèse cross-modules (forage + champs + sol + salines + santé physiologique).

---

## 3. SOUS-MODULES INTERNES ACTIFS

### 3.1 `nutrition_intelligence/` (12 sous-engines x5100-x7000) 🔴

**Path** : `/app/backend/engines/nutrition_intelligence/`
**Route FastAPI** : `/api/v6/nutrition-intelligence/*`
**Endpoints actifs** : **38 endpoints REST**

| Sub-engine | Fichier | Rôle |
|---|---|---|
| x5100 | `x5100_mineral_score` | Score minéral composite (Ca/P/Na/Mg/K) |
| x5200 | `x5200_mineral_recommendation` | Recommandations correctifs minéraux |
| x5300 | `x5300_order_engine` | Génération bon de commande minéraux |
| x5500 | `x5500_energy_protein` | Calcul énergie/protéines par physiologie |
| x5600 | `x5600_site_guide` | Guide site selon écozones |
| x5700 | `x5700_cost_engine` | Calcul coûts substrats |
| x5800 | `x5800_recipe_engine` | Génération recettes minérales |
| x5900 | `x5900_evidence_engine` | Evidence scientifique par recommandation |
| x6000 | `x6000_product_score` | Scoring produits commerciaux |
| x6010 | `x6010_product_quality_analyzer` | Analyse qualité produit |
| x6011 | `x6011_market_availability_engine` | Disponibilité marché par province |
| x6012 | `x6012_regulatory_compliance_engine` | Conformité réglementaire (MAPAQ, CFIA, OIE, etc.) |
| x6020 | `x6020_terrain_solutions` | Solutions terrain pour déficits identifiés |
| x6030 | `x6030_product_ecosystem` | Écosystème produits + traçabilité |
| x7000 | `x7000_supplier_product_engine` | Pipeline fournisseur (submit/review/activate) |

**Endpoints REST exposés** (38 total) :
- `/score`, `/recommendations`, `/order`, `/energy-protein`, `/site-guide`
- `/costs`, `/costs/compare`, `/recipe`, `/evidence`, `/full-analysis`
- `/products/score`, `/products/all`, `/products/compare`, `/products/shop`
- `/supra-panel`, `/supra-batch`, `/knowledge/{species_id}`, `/export-pdf`
- `/products/quality`, `/products/quality/all`
- `/products/availability`, `/products/availability/all`, `/products/restrictions/{province}`
- `/products/compliance`, `/products/compliance/all`, `/products/compliance/{organism}`
- `/terrain/solutions`, `/terrain/solutions/compute`
- `/products/ecosystem`, `/products/ecosystem/all`, `/products/tracability`
- `/supplier/submit`, `/supplier/review`, `/supplier/activate`
- `/supplier/submission/{id}`, `/supplier/submissions`, `/supplier/pipeline/stats`

### 3.2 `nutrition_engine_v7` (pipeline biologique) 🔴

**Path** : `/app/backend/modules/nutrition_engine_v7/`
**Route FastAPI** : `/api/v7/nutrition/*`
**Pipeline** (8 endpoints) :
- `/soil-layer` — sol pédologique
- `/nutrients` — extraction nutriments
- `/forage` — fourrage potentiel
- `/water` — accès eau
- `/metabolism` — métabolisme énergétique
- `/attractiveness` — attractivité spatiale
- `/full-pipeline` — chaîne complète
- `/status` — health check

### 3.3 `saline_engine/engines/` (7 sub-engines saline-nutrition) 🔴

**Path** : `/app/backend/modules/saline_engine/engines/`

| Sub-engine | Rôle |
|---|---|
| `wildlife_nutritional_engine.py` | Besoins minéraux/jour par espèce/sexe/âge/saison (NRC Wildlife Nutrition + Bubenik + Verme & Ullrey) |
| `soil_composition_engine.py` | Composition pédologique zone saline |
| `vegetation_forage_engine.py` | Fourrage végétation locale |
| `seasonal_metabolism_engine.py` | Métabolisme saisonnier (rut, gestation, lactation) |
| `nutrient_deficiency_engine.py` | Détection carences zone |
| `hydrology_leaching_engine.py` | Lessivage hydrologique (perte nutriments) |
| `saline_recommendation_engine.py` | Recommandation site saline |

**Tables besoins minéraux par espèce** (mg/jour, extrait orignal) :
```python
"Ca": {base=18000, antler=35000, gestation=25000, rut=22000, winter=12000}
"P":  {base=12000, antler=25000, gestation=18000, rut=15000, winter= 8000}
"Na": {base= 4000, antler= 5000, gestation= 5500, rut= 4500, winter= 3000}
"Mg": {base= 3000, antler= 5000, gestation= 4000, rut= 3500, winter= 2000}
"Zn": {base=  150, antler=  300, gestation=  200, rut=  180, winter=  100}
+ K, S, Se (présents dans table complète)
```

### 3.4 `nutrition_v6_interface/` (legacy wrapper) 🟡

**Path** : `/app/backend/modules/nutrition_v6_interface/`
**Rôle** : Wrapper interface V6 → délègue à `wildlife_nutrition_attractiveness.py`

### 3.5 `nutrition_loader_omega` (espèces) ⚠️ STUB

**Path** : `engines/v8_institutional/especes/nutrition_loader_omega.py`
**Statut** : **STUB · aucune logique métier, aucune donnée** (selon header doctrinal)
**Sources externes attendues (Q3-Q4 selon planning)** :
- `/app/backend/data/nutrition/ndvi/nasa_ndvi_2004_2024.tif`
- `/app/backend/data/nutrition/sol/soil_quality_canada.tif`
- `/app/backend/data/nutrition/mineraux/soil_minerals_quebec.tif`
- `/app/backend/data/nutrition/attractivite/mast_index_2004_2024.csv`

### 3.6 `core/scoring_pipeline/alimentation_v2/nutrition.py` 🟡

Pipeline scoring alimentation V2 (utilisé par scoring_pipeline legacy).

### 3.7 `species_engine/nutrition.py` 🟡

Module nutrition lié au species_engine. Présent, à vérifier import direct V20.

### 3.8 `bionic_engine_p0/engines/nutrition_engine.py` 🟡

Module P0 nutrition (legacy bionic engine).

---

## 4. CALCULS AUTOMATIQUES EN PLACE

### 4.1 Calculs PROTÉINES
- Besoins protéiques par mois × espèce (table `besoins_saison`) — index 0-100
- Modulation physiologie (mâle rut +20% / femelle lactation +35% / juvénile +25%)
- Sub-engine x5500 `x5500_energy_protein` — calcul énergie/protéines détaillé

### 4.2 Calculs ÉNERGIE
- Besoins énergétiques par mois (rut +30% mâles, thermogénèse hiver +90%)
- Calcul charge portative ratio (lié à `dispo["charge_portative_ratio"]`)

### 4.3 Calculs MINÉRAUX (Ca, P, Mg, Na, K, S, Zn, Se)
- **engine_carence_nutritionnelle_omega** : tables `_NEEDS` par espèce
- **wildlife_nutritional_engine (saline)** : tables mg/jour détaillées
- **engine_nutrition_v12_supra** : indices terrain (`calcium_index`, `sodium_index`, `magnesium_index`)
- Computation déficit : `besoin% - (index_local × 100) = déficit` (par point grille)

### 4.4 Ratios calculés
- **Ca:P** : computation présente dans tables NRC (besoins_minéraux), à confirmer ratio exposé
- **NaCl** : `sodium_index` calculé indépendamment, **pas de calcul NaCl explicite** dans V12-SUPRA
- **Zn, Se** : présents dans tables NRC saline mais **PAS dans V12-SUPRA core**

### 4.5 Carences (déficits)
- Calculées par point de grille `_carences_point(lat, lon, terrain, besoins, dispo)`
- 5 catégories : Na, Ca, Mg (couvertes) · P, K (partielles dans engine_carence_omega)
- Severity : pourcentage `max(0, besoin - dispo×100)`

---

## 5. CHAMPS EXPOSÉS NutritionPanelOmega (11 SECTIONS)

**Fichier** : `/app/frontend/src/components/territoire/NutritionPanelOmega.jsx` (197 LoC)
**Doctrine** : `PHASE_NUTRITION_SALINES_BINDING_Ω — INTEGRATED_WITH_FILTERING`
**Activation** : DOUBLE-CLIC sur une saline de BionicLayersV8
**Filtres pré-affichage** : EXCLUSION / HABITAT / TERRAIN / BIOLOGIE_AWARE_Ω

**Les 11 sections** (depuis `SECTION_META`) :

| # | Clé | Label affiché | Icône lucide |
|---|---|---|---|
| 1 | `besoins_journaliers` | Besoins journaliers | Wheat |
| 2 | `carences` | Carences | ShieldAlert |
| 3 | `mineraux` | Minéraux | Activity |
| 4 | `proteines` | Protéines | Droplets |
| 5 | `saisonnalite` | Saisonnalité | Calendar |
| 6 | `recommandations` | Recommandations | ClipboardList |
| 7 | `quantites` | Quantités | Package |
| 8 | `frequences` | Fréquences | Repeat |
| 9 | `recettes_minerales` | Recettes minérales | FlaskConical |
| 10 | `impact_biologique` | Impact biologique | HeartPulse |
| 11 | `score_nutritionnel_institutionnel` | Score nutritionnel Ω | Award |

**Data-testids exposés** :
- `nutrition-panel-omega` (root)
- `nutrition-panel-close-btn`
- `nutrition-panel-rejected` (si saline rejetée par filtres)
- `nutrition-section-{key}` (×11 par section)

**Champs SALINE attachés au panel** :
- `payload.saline.id`, `payload.saline.lat`, `payload.saline.lng`, `payload.saline.status`
- `payload.species`, `payload.month`

---

## 6. MODULES LIÉS AUX SALINES

### 6.1 `PHASE_NUTRITION_SALINES_BINDING_Ω` 🔴

**Fichiers de production** (5 frontend, 1 doctrine) :
- `frontend/src/components/territoire/map/MapContent.jsx`
- `frontend/src/components/territoire/NutritionPanelOmega.jsx`
- `frontend/src/components/territoire/BionicLayersV8.jsx`
- `frontend/src/pages/MonTerritoireBionicPage.jsx`
- `frontend/src/lib/renduOmegaStore.js`
- Doc : `/app/memory/PHASE_NUTRITION_SALINES_BINDING_OMEGA_REPORT.md`
- Test : `frontend/src/lib/__tests__/nutritionSalinesBinding.test.js`

**Mécanisme** :
1. Saline cliquée 2× sur la carte
2. Filtres appliqués : EXCLUSION (zone interdite) / HABITAT (saline ≠ habitat espèce) / TERRAIN (qualité sol insuffisante) / BIOLOGIE_AWARE_Ω
3. Si OK → POST `/api/v6/nutrition-intelligence/supra-panel` ou compute V12 local
4. Bundle de 11 sections retourné et affiché dans `NutritionPanelOmega`

### 6.2 Fusion `attractivite_salines` dans V12

`compute_nutrition_v12` retourne le mapping `{saline_id: multiplier}` qui est ensuite
**appliqué au bundle V20** (lignes 1293+ de `territoire_v10_supra.py`) :
```python
_smap = nutrition.get("attractivite_salines", {})
for s in salines:
    mult = _smap.get(s.get("id"))
    if mult:
        s["nutrition_multiplier"] = mult
        if isinstance(s.get("attractiveness_score"), (int, float)):
            s["attractiveness_with_nutrition"] = round(s["attractiveness_score"] * mult, 2)
```

### 6.3 `engine_salines_v11_supra` (legacy/coexistence)

**Statut audit global** : LEGACY (importé uniquement par tests/audit). Le runtime utilise
`engine_nutrition_v12_supra.attractivite_salines` + sub-engines `saline_engine`.

---

## 7. MODULES NDVI / LiDAR — STATUT ACTUEL

### 7.1 NDVI nutritionnel ⚠️ STUB UNIQUEMENT

| Référence | Statut |
|---|---|
| `engines/v8_institutional/especes/nutrition_loader_omega.py` | 🟡 **STUB** · TIF NDVI attendu en `/app/backend/data/nutrition/ndvi/nasa_ndvi_2004_2024.tif` (Q3-Q4 planning) |
| `modules/poi_graph_engine/services/poi_scorer.py` | 🟡 Référence NDVI mais pas fed nutrition |
| `data/territoire/dictionaries_proposed/nutrition_rules.json` | 🟡 Règles candidates, statut DICTIONARY_PROPOSED (non-activé) |
| `engine_nutrition_v12_supra.py` | ❌ **AUCUNE référence NDVI directe** (TODO connexion) |

→ **NDVI n'est PAS encore connecté au pipeline nutrition runtime**.

### 7.2 LiDAR nutritionnel 🔴 ACTIF (indirect)

| Référence | Statut |
|---|---|
| `engine_nutrition_v12_supra.py` ligne 47 | ✅ Déclare dépendance `LIDAR_WCS_1M` |
| `engine_nutrition_v12_supra.py` ligne 257 | ✅ Détecte `sources_actives.lidar == ABSENT` → `lidar_absent_canopy_estime` |
| `engine_nutrition_v12_supra.py` ligne 667 | ✅ Retourne `data_sources.lidar` dans output |
| Pipeline réel `lidar_irda_v11.py` → `compute_terrain_v10` → `compute_nutrition_v12` | 🔴 ACTIF chaîné |

→ **LiDAR FEED nutrition via terrain_v10** (couverture canopée, structure verticale, essences).

### 7.3 IRDA pédologie 🔴 ACTIF (indirect)

Identique LiDAR : IRDA pédologie fed via `terrain_v10` → indices sol/drainage/moisture → indices nutriments.

---

## 8. PIPELINES NUTRITIONNELS EN COURS β2-ΣΤ

### Cartographie chaîne d'appels

```
zerocost_worker_seed_r5.py (worker β2-ΣΤ)
  └── await v20_territoire_bundle(lat, lon, species, month, hour)
       └── compute_territoire_v10(...)  [territoire_v10_supra.py]
            ├── compute_terrain_v10(...)          [terrain_v10_supra.py]
            │    └── lidar_irda_v11 fetches       [LIDAR + IRDA + Meteo via WeatherCache]
            ├── compute_zones_v10(...)
            ├── compute_corridors_omega(...)
            ├── compute_affuts_omega(...)
            ├── compute_hotspots_v10(...)
            ├── compute_salines_omega(...)
            └── compute_nutrition_v12(...)         [engine_nutrition_v12_supra.py]  ◀── HUB nutrition
                 ├── besoins_saison(month)
                 ├── apply_physiologie(...)
                 ├── score_habitat(terrain)
                 ├── disponibilite_fourrage(terrain, month)
                 ├── score_zones_alimentation(zones, habitat, dispo)
                 ├── influence_corridors(corridors, zones_nutri, dispo)
                 ├── influence_hotspots(hotspots, zones_nutri, dispo)
                 ├── attractivite_salines(salines, besoins_eff, dispo, month)
                 ├── _carences_point × N_grid
                 └── _besoins_point × N_grid
```

→ **CHAQUE TUILE BUNDLE V20 produite par β2-ΣΤ inclut systématiquement les 7 outputs nutrition_v12** :
- score_nutritionnel
- carte_carences (grille spatiale)
- carte_besoins (grille spatiale)
- zones_alimentation
- attractivite_salines
- influence_corridors
- influence_hotspots

**Volume théorique pré-warmé** : 1 775 cellules R6 × 6 espèces × 4 mois × 3 heures × 1 bundle nutrition = **127 800 bundles nutritionnels** intégrés au CDN R2 in fine.

---

## 9. DOUBLONS POTENTIELS IDENTIFIÉS

| # | Module A | Module B | Risque doublon | Mitigation déjà en place |
|---|---|---|---|---|
| 1 | `engine_nutrition_v12_supra.attractivite_salines` | `wildlife_nutritional_engine.py` (saline) | 🟡 Moyen — tous deux calculent attractivité saline | V12 hook explicite vers SALINES-V11-SUPRA |
| 2 | `engine_nutrition_v12_supra.disponibilite_fourrage` | `nutrition_engine_v7.pipeline (forage)` | 🟡 Moyen | engine_nutrition.py (V8) délègue explicitement |
| 3 | `engine_carence_nutritionnelle_omega` (tables) | `wildlife_nutritional_engine` (tables) | 🟡 Moyen — deux tables besoins minéraux par espèce | V12 utilise ses propres constantes |
| 4 | `engine_nutritional_attractiveness_omega` | `attractivite_salines` (V12 interne) | 🟢 Faible — niveaux différents (E47 fusion vs hub) | E47 = synthèse multi-sources |
| 5 | `nutrition_engine_v7` (V7 pipeline) | `nutrition_intelligence` (12 sub-engines) | 🟢 Faible — V7 = pipeline biologique séquentiel · v6 = API REST hub |
| 6 | `nutrition_v6_interface` | `nutrition_intelligence` | 🟡 Moyen — wrapper legacy peut être déprécié |
| 7 | `core/alimentation_v2/nutrition.py` | `engine_nutrition_v12_supra` | 🟢 Faible — alimentation_v2 = legacy scoring_pipeline |
| 8 | `engines/v8_institutional/engine_nutrition.py` | tous les engines délégués | 🟢 Wrapper-pur (pas de calcul propre) |

### Recommandation anti-doublon pour V12-SUPRA+

Pour éviter de créer de nouveaux doublons en intégrant V12-SUPRA+, **respecter le pattern existant** :
- ✅ V12-SUPRA = HUB CENTRAL (orchestration)
- ✅ Sub-engines (nutrition_intelligence/saline_engine) = LOGIQUE MÉTIER spécialisée
- ✅ engine_nutrition.py = WRAPPER V8 délégateur
- ✅ NutritionPanelOmega = AFFICHAGE UI (11 sections normalisées)
- ✅ engine_carence + engine_attractiveness = SUB-ENGINES Ω auxiliaires

**À éviter** :
- ❌ Ré-implémenter `besoins_saison` ou `attractivite_salines` ailleurs
- ❌ Créer un nouvel endpoint REST nutrition séparé de `/api/v6/nutrition-intelligence/*` ou `/api/v7/nutrition/*`
- ❌ Bypasser `compute_nutrition_v12` dans le chaînage V20→V10

---

## 10. PRÉPARATION INTÉGRATION NUTRITION V12-SUPRA+

### 10.1 Champs / capacités candidats pour V12-SUPRA+

Si l'objectif est **étendre V12-SUPRA** sans le doubler, suggestions doctrinales :

| Extension candidate | Justification | Composant à étendre |
|---|---|---|
| **NDVI integration runtime** | Stub nutrition_loader_omega présent · TIF attendu Q3-Q4 | `engine_nutrition_v12_supra.disponibilite_fourrage` + ajout `forage_ndvi_index` |
| **Calcul ratio Ca:P** | Tables NRC contiennent les deux mais pas le ratio | Ajout `_ratio_cap_point(...)` dans grille |
| **Calcul NaCl explicite** | sodium_index présent, NaCl explicit absent | Computation `NaCl = Na × 2.54` + comparaison saline |
| **Zn / Se grille spatiale** | Tables NRC mais pas dans V12 core grille | Étendre `_carences_point` aux 5 minéraux + 2 trace |
| **MAST index (chêne/feuillus)** | TIF mast_index_2004_2024.csv attendu | Ajout `mast_index` dans `disponibilite_fourrage` |
| **Soil quality Canada raster** | TIF soil_quality_canada.tif attendu | Remplacer heuristique `sol_quality` par lecture raster |
| **Soil minerals Quebec raster** | TIF soil_minerals_quebec.tif attendu | Remplacer `calcium_index`/`sodium_index` heuristiques |
| **Profil physiologique étendu** | Actuellement 5 profils · pourrait inclure âge sub-adulte, état sanitaire | Étendre `apply_physiologie` |
| **Pression de chasse historique** | Pas dans V12 actuel | Nouveau module ou fed par chain_omega_cascade |
| **Climat futur (réchauffement)** | `compute_climat_futur` existe en V10 mais pas dans nutrition | Hook V12 → climat_futur |

### 10.2 Structures de fichiers à PRÉSERVER

```
engines/v8_institutional/engine_nutrition_v12_supra.py    ← HUB INTACT
                          ↓ (delegation par import)
engines/nutrition_intelligence/                            ← 12 sub-engines INTACTS
modules/saline_engine/engines/                              ← 7 sub-engines INTACTS
modules/nutrition_engine_v7/                                ← pipeline biologique INTACT
core/scoring_pipeline/alimentation_v2/nutrition.py          ← legacy à NE PAS toucher
frontend/src/components/territoire/NutritionPanelOmega.jsx  ← 11 sections INTACTES
```

### 10.3 Pattern d'extension doctrinal proposé

**Option A — Extension in-place V12 (recommandée)** :
```python
# engine_nutrition_v12_supra.py — ajout SUFFIXE _v2 sur fonctions étendues
def disponibilite_fourrage_v2(terrain, month, ndvi_raster=None, mast_csv=None):
    base = disponibilite_fourrage(terrain, month)
    if ndvi_raster: base["ndvi_index"] = _ndvi_lookup(...)
    if mast_csv: base["mast_index"] = _mast_lookup(...)
    return base

def compute_nutrition_v12_supra_plus(...):  # nouveau point d'entrée
    # Appelle compute_nutrition_v12 puis ajoute extensions
    base = compute_nutrition_v12(...)
    base["v12_plus"] = {
        "ratio_cap_grid": ...,
        "ndvi_grid": ...,
        "mast_index_grid": ...,
    }
    return base
```

**Option B — Nouveau fichier V12+ délégateur** :
```python
# engine_nutrition_v12_supra_plus.py — nouveau wrapper
from .engine_nutrition_v12_supra import compute_nutrition_v12, ENGINE_NAME as V12_NAME

ENGINE_NAME = "ENGINE-NUTRITION-V12-SUPRA-PLUS"
ENGINE_VERSION = "V12+-2026-XX"

def compute_nutrition_v12_plus(...):
    base = compute_nutrition_v12(...)
    base["extensions_v12_plus"] = {
        # NDVI grid
        # MAST index
        # Ratio Ca:P
        # NaCl explicit
        # Zn/Se grids
    }
    return base
```

→ Option B **moins risquée** (pas de modification du V12 actuel actif dans β2-ΣΤ) · **plus modulaire** · **réversible**.

---

## 11. VERROU PHASE III · CONFORMITÉ AUDIT

| Composant audité | Modifié durant audit ? |
|---|---|
| Tous engines V10/V20/IA/LiDAR/IRDA/nutrition | ❌ STRICTEMENT READ-ONLY |
| Frontend NutritionPanelOmega | ❌ READ-ONLY |
| Sub-engines nutrition_intelligence/saline_engine | ❌ READ-ONLY |

→ **Audit 100% READ-ONLY** · Verrou Phase III maintenu.

---

## 12. RÉSUMÉ POUR DÉCISION COMMANDANT

### État nutritionnel BIONIC à date
- ✅ **Hub central actif** : `compute_nutrition_v12` (engine_nutrition_v12_supra · 749 LoC · 7 outputs garantis)
- ✅ **38 endpoints REST** nutrition_intelligence + 8 endpoints nutrition_engine_v7
- ✅ **11 sections UI** NutritionPanelOmega exposées
- ✅ **7 sub-engines saline-nutrition** opérationnels
- ✅ **5 calculs minéraux** (Na, Ca, Mg) au runtime + tables NRC (P, K, S, Zn, Se) en réserve
- ✅ **LiDAR/IRDA fed** indirectement via terrain_v10 → compute_nutrition_v12
- ⚠️ **NDVI = STUB** (TIF attendu, pas encore activé)
- ⚠️ **Ratios Ca:P, NaCl explicit, Zn/Se grilles** = présents dans tables mais **non exposés grille spatiale V12**
- ⚠️ **MAST index** = stub uniquement

### Capacités à activer dans V12-SUPRA+ (sans doublon)
1. Connecter NDVI (nasa_ndvi raster) → `forage_ndvi_index` dans disponibilite_fourrage
2. Connecter soil_quality_canada.tif → remplacer heuristique sol_quality
3. Connecter soil_minerals_quebec.tif → enrichir calcium_index, sodium_index
4. Activer mast_index_2004_2024.csv → diversification fourrage automne
5. Ajouter grille Zn / Se / P / K / Ca:P dans `_carences_point`
6. Ajouter NaCl explicit dans output (Na × 2.54)
7. Étendre apply_physiologie (âge sub-adulte, état sanitaire)
8. Hook climat_futur dans modulation besoins long-terme

### Position d'intégration recommandée
**OPTION B doctrinale** : créer `engine_nutrition_v12_supra_plus.py` comme **wrapper additif** au-dessus de V12 actuel, exposant `compute_nutrition_v12_plus(...)` qui appelle V12 puis enrichit. **Verrou Phase III préservé** · **β2-ΣΤ continue à utiliser V12 stable** · **V12+ activable progressivement**.

---

**FIN DIAGNOSTIC · AUDIT READ-ONLY EXHAUSTIF · 0 MODIFICATION CODE · VERROU PHASE III MAINTENU**

**Prêt pour la directive Commandant d'intégration V12-SUPRA+ selon le pattern doctrinal proposé.**
