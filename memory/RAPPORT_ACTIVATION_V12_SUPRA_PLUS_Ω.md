# RAPPORT ACTIVATION V12-SUPRA+ · FICHE SALINE ULTIME · Ω

**Doctrine** : `P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_ACTIVATION_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟢 **V12-SUPRA+ EN PRODUCTION · TESTS 5 ESPÈCES OK**

---

## 1. DIRECTIVE COMMANDANT EXÉCUTÉE

```
ACTIVATE V12-SUPRA+ OPTION B           ✅ Wrapper additif, à la demande UI
UI 11 SECTIONS (pas de 12e)            ✅ Bundle absorbé par sections existantes
NDVI : ATTENDRE TIF (Q3-Q4)            ✅ Stub conservé
PRIORITÉS P0 D'ABORD                   ✅ NaCl + Ca:P + déficits P/Zn/Se + kg maïs/soya + m²
FICHE SALINE ULTIME PRD-READY          ✅ 10 blocs structurés produits
```

---

## 2. ARTEFACTS LIVRÉS

| Fichier | LoC | Rôle |
|---|---|---|
| `engines/v8_institutional/_v12_plus_tables.py` | 233 | Tables doctrinales (ratio Ca:P, conso kg/j, m² food plots, trace ppm, vent, corridors, plan 30j) |
| `engines/v8_institutional/engine_nutrition_v12_supra_plus.py` | 340 | Hub V12+ · `compute_fiche_saline_ultime` |
| `engines/v8_institutional/v12_plus_router.py` | 110 | Router REST autonome (bypass init.py cassé nutrition_intelligence) |
| `server.py` (+10 lignes additives) | — | Inclusion router V12+ |

**Total** : **~700 LoC strictement additifs · 0 modification engines V10/V20**.

---

## 3. ENDPOINTS REST PRODUITS

### 3.1 Health check
```bash
GET /api/v6/nutrition-intelligence/v12-plus/health
HTTP 200 · ~80ms
```
Retourne : engine, version, doctrine, phase_iii_lock, tables disponibles (6 dictionnaires
doctrinaux × 9 espèces couvertes).

### 3.2 Fiche Saline Ultime PRD-READY
```bash
POST /api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime
Content-Type: application/json
Body : {
  "lat": 45.65, "lon": -75.30,
  "species": "chevreuil|orignal|ours_noir|wapiti|dindon_sauvage|cerf|coyote",
  "month": 1-12,
  "profil": "moyenne|male_rut|femelle_gest|femelle_lact|juvenile",
  "hour": 0-23,
  "wind_deg": 0-360,
  "wind_speed": float,
  "saline_id": "TEST_001",
  "saline_score": 80,
  "saline_type": "naturelle"
}
HTTP 200 · ~40ms (mesure live)
```
Retourne : **10 blocs structurés**.

---

## 4. STRUCTURE FICHE 10 BLOCS

| # | Bloc | Champs principaux |
|---|---|---|
| 1 | `1_identite_site` | saline_id, coordonnees, altitude_m, type_saline, statut, score_global_saline, saison, mois, espece_active, profil_physio |
| 2 | `2_profil_biologique` | espece, poids_base_kg, olfaction, ouie, vue, saisonnalite_besoins |
| 3 | `3_habitat_terrain` | score_habitat, composantes, limitations, data_sources, type_terrain_optimal, vegetation_couvert |
| 4 | `4_besoins_journaliers` | proteines_g_jour, energie_kcal_jour, mineraux_mg_jour {Ca,P,Na,Mg,Zn,Se} |
| 5 | `5_deficits_pct` | Ca, P, Na, Mg, Zn, Se (en %) + `_severite_globale` (CRITIQUE/ÉLEVÉE/MODÉRÉE) |
| 6 | `6_recettes_automatiques` | `recette_saline` (produit base + ratio_cap + nacl + trace_ppm) + `recette_alimentaire` (type champ + kg maïs/soya + surface m²) |
| 7 | `7_champs_nourriciers` | top_3_cultures, saison_factor, rotation_recommandee, type_principal |
| 8 | `8_strategie_chasse` | approche_vent, distance_min/optimale, vent_critique_deg, heure_optimale, type_terrain, vegetation_couvert, vent_compatible (bool) |
| 9 | `9_plan_30_jours` | 4 phases × actions doctrinales (préparation → habituation → fenêtre tactique → jour de chasse) |
| 10 | `10_synthese_finale` | score_global_site, carence_dominante, recommandation_clef, fenetre_optimale, espece_compatibilite |

---

## 5. CALCULS V12+ ACTIVÉS (P0)

### 5.1 NaCl explicit
```
NaCl = Na × 2.54 / 1000  (formule chimique Na/NaCl ratio molaire)
Exemple : orignal Na=4500 mg/j (rut) → 11.43 g NaCl/jour
```

### 5.2 Ratio Ca:P
Tables doctrinales NRC Wildlife Nutrition par espèce :
- Orignal/Chevreuil/Cerf/Wapiti : 1.5:1 (bois + lactation)
- Ours_noir : 1.2:1 (omnivore + hibernation)
- Dindon : 2.0:1 (ponte + coquille calcique)
- Coyote : 1.2:1 (carnivore — n/a saline)

### 5.3 Déficits P / Zn / Se
- Ca/Na/Mg : depuis `compute_nutrition_v12._carences_point` (V12 hub, grille spatiale)
- P : heuristique `0.8 × deficit_Ca + 15 × (1 - sol_quality)`
- Zn : heuristique `30 + 40 × (1 - sol_quality)` (~30-70% selon terroir)
- Se : heuristique `45 + 35 × (1 - sol_quality)` (sols boréaux QC traditionnellement déficitaires)

### 5.4 kg maïs/soya par semaine
```
kg_semaine = attractivite_crop × 7 × conso_kg_ms_jour × 0.15
            (15% MS = ration complémentaire vs ration totale naturelle)
```
Exemples mesurés :
- Chevreuil maïs : 0.95 × 7 × 1.5 × 0.15 = **1.50 kg/semaine**
- Orignal maïs : 0.70 × 7 × 7.0 × 0.15 = **5.14 kg/semaine**

### 5.5 Surfaces m² champs nourriciers
Tables doctrinales par individu × culture :
| Culture | Orignal | Chevreuil | Wapiti | Ours_noir | Dindon |
|---|---|---|---|---|---|
| Trèfle | 800 | 400 | 700 | 200 | 50 |
| Luzerne | 1000 | 600 | 900 | 250 | 80 |
| Brassicas | 450 | 250 | 400 | 150 | 30 |
| Avoine | 600 | 350 | 500 | 180 | 60 |
| Maïs | 900 | 500 | 800 | 220 | 100 |

---

## 6. ESPÈCES ADAPTÉES (8 + coyote)

| Espèce | Vent critique | Distance opti | Heure opti | Format saline |
|---|---|---|---|---|
| Orignal | 45° | 30 m | Aube/crépuscule | Granules ou bloc |
| Chevreuil | 60° | 20 m | Aube/crépuscule + nuit pleine lune | Bloc |
| Cerf | 60° | 20 m | Aube/crépuscule | Bloc |
| Wapiti | 30° | 40 m | Aube/soirée fin de jour | Bloc |
| Ours_noir | 25° | 15 m | Crépuscule + tôt matin | Granules |
| Dindon_sauvage | 90° | 15 m | Aube perchage / fin de jour | Granules fin |
| Coyote | 45° | 50 m | Nuit + crépuscule + aube | n/a (carnivore) |

---

## 7. TESTS LIVE (5 ESPÈCES VALIDÉES)

| Espèce | Région test | Mois | Profil | HTTP | Latence | Blocs |
|---|---|---|---|---|---|---|
| chevreuil | Outaouais (45.65,-75.30) | 10 | moyenne | 200 | 47 ms | 10/10 |
| orignal | Mauricie (46.92,-72.10) | 10 | male_rut | 200 | 40 ms | 10/10 |
| ours_noir | Laurentides (47.50,-71.30) | 9 | moyenne | 200 | 6 ms | 10/10 |
| wapiti | Côte-Nord (51.49,-65.20) | 10 | moyenne | 200 | 45 ms | 10/10 |
| dindon_sauvage | Estrie (45.20,-73.50) | 4 | moyenne | 200 | 46 ms | 10/10 |

**Latence moyenne : 37 ms · objectif <200 ms largement atteint**.

---

## 8. EXEMPLE COMPLET (Orignal Mauricie rut octobre)

```json
{
  "1_identite_site": {
    "saline_id": "TEST_Mauricie_rut",
    "coordonnees": {"lat": 46.92, "lng": -72.10},
    "type_saline": "naturelle",
    "score_global_saline": 80,
    "saison": "automne",
    "espece_active": "orignal",
    "profil_physio": "male_rut"
  },
  "4_besoins_journaliers": {
    "proteines_g_jour": 195.0,
    "energie_kcal_jour": 10000,
    "mineraux_mg_jour": {"Ca": 22000, "P": 15000, "Na": 4500, "Mg": 3500, "Zn": 180, "Se": 1.8}
  },
  "5_deficits_pct": {
    "Ca": 0, "P": 7.5, "Na": 0, "Mg": 0, "Zn": 50.0, "Se": 62.5,
    "_severite_globale": "CRITIQUE"
  },
  "6_recettes_automatiques": {
    "recette_saline": {
      "produit_base_recommande": "SEL_MARIN_TRACE_MINERAL",
      "ratio_cap": {"actuel": "1.47:1", "cible": "1.5:1", "ecart_pct": -2.0},
      "nacl_g_jour": 11.43,
      "trace_minerale_ppm": {"Zn_ppm": 450, "Se_ppm": 22, "Cu_ppm": 15, "I_ppm": 5},
      "format_recommande": "granules", "base_carrier": "argile_bentonite"
    },
    "recette_alimentaire": {
      "type_champ_nourricier_recommande": "luzerne",
      "kg_mais_semaine": 5.14, "kg_soya_semaine": 2.94,
      "surface_m2": {"trefle": 800, "luzerne": 1000, "brassicas": 450, "avoine": 600}
    }
  },
  "8_strategie_chasse": {
    "approche_vent_recommandee": "Sous le vent strict",
    "distance_optimale_m": 30, "distance_minimale_m": 80,
    "vent_critique_deg": 45, "vent_compatible": true,
    "heure_optimale": "Aube (5h-7h) et crépuscule (18h-20h)",
    "vegetation_couvert": "Aulnaies, jeunes coupes, marécages"
  },
  "10_synthese_finale": {
    "score_global_site": 80.0,
    "carence_dominante": "Se",
    "recommandation_clef": "Saline minérale (ratio Ca:P 1.5:1) + 11 g NaCl/jour · champ luzerne 1000 m²/indiv.",
    "fenetre_optimale": "Aube (5h-7h) et crépuscule (18h-20h)"
  }
}
```

---

## 9. VERROU PHASE III · CONFORMITÉ STRICTE

| Composant | Modifié ? |
|---|---|
| `engine_nutrition_v12_supra.py` (HUB V12) | ❌ INTACT |
| Tous engines V10/V20/LiDAR/IRDA/terrain | ❌ INTACT |
| `compute_territoire_v10` chaîne β2-ΣΤ | ❌ INTACT |
| `tools/zerocost_worker_seed_r5.py` | ❌ INTACT |
| Frontend (`useZerocostBundle.js`, `lkgCacheOmega.js`, `BionicLayersV8.jsx`, `NutritionPanelOmega.jsx`) | ❌ INTACT |
| `wildlife_nutritional_engine.py` (saline NRC) | ❌ INTACT (lecture seule) |
| `engine_carence_nutritionnelle_omega.py` | ❌ INTACT (lecture seule) |
| `engine_champs_nourriciers_omega.py` | ❌ INTACT (lecture seule) |
| `tools/zerocost_seed_r5_daemon.sh` | ❌ INTACT |
| **Nouveau** `_v12_plus_tables.py` | 🆕 ADDITIF |
| **Nouveau** `engine_nutrition_v12_supra_plus.py` | 🆕 ADDITIF |
| **Nouveau** `v12_plus_router.py` | 🆕 ADDITIF |
| `server.py` (+10 lignes additives) | ✅ Ajout `app.include_router(v12_plus_router)` |

→ **Verrou Phase III strictement respecté · β2-ΣΤ poursuit en mode nominal · 0 régression**.

---

## 10. PROCHAINES ÉTAPES (sur ordre Commandant)

### 10.1 Intégration UI optionnelle
Branchement `NutritionPanelOmega.jsx` sur le nouveau endpoint :
```javascript
// Au double-clic saline, en plus du POST /supra-panel actuel :
const v12plus = await fetch(`${API_URL}/api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime`, {
  method: 'POST',
  body: JSON.stringify({ lat, lon, species, month, saline_id, saline_score, ... }),
});
// Mapper les 10 blocs dans les 11 sections existantes
```
Mapping suggéré (UI 11 sections existantes) :
- Section `besoins_journaliers` ← `4_besoins_journaliers`
- Section `carences` ← `5_deficits_pct`
- Section `mineraux` ← bloc 4 mineraux_mg_jour + bloc 6 trace_minerale_ppm
- Section `proteines` ← bloc 4 proteines_g_jour
- Section `saisonnalite` ← bloc 1 saison + bloc 2 saisonnalite_besoins
- Section `recommandations` ← bloc 6 recette_alimentaire + bloc 8 stratégie chasse
- Section `quantites` ← bloc 6 kg_mais_semaine + kg_soya_semaine + surface_m²
- Section `frequences` ← bloc 9 plan_30_jours
- Section `recettes_minerales` ← bloc 6 recette_saline
- Section `impact_biologique` ← bloc 2 profil_biologique
- Section `score_nutritionnel_institutionnel` ← bloc 10 synthese_finale

### 10.2 Priorités P1/P2 différées
| Priorité | Champ | Statut |
|---|---|---|
| P1 | Tables NRC complètes (Se mg/j vérification) | En attente confirmation |
| P1 | `score_produit` réel via `x6000_product_score` | En attente déblocage init.py nutrition_intelligence |
| P2 | NDVI integration runtime | En attente TIF Q3-Q4 |
| P2 | `ajustement_terrain` via `x6020_terrain_solutions` | En attente déblocage init.py |

### 10.3 Plan de remédiation `nutrition_intelligence/__init__.py`
Le bug `x5100_mineral_score module manquant` est **pré-existant** (pas lié à V12+).
Le router `nutrition_intelligence` n'a JAMAIS chargé (depuis fork antérieur).
→ **Plan séparé requis** sur ordre Commandant pour reconstruire `__init__.py` et débloquer
les 38 endpoints REST de `nutrition_intelligence`. Le V12+ fonctionne autonomement.

---

## 11. ÉTAT DE PRODUCTION POST-ACTIVATION

| Composant | État |
|---|---|
| Endpoint `/api/v6/nutrition-intelligence/v12-plus/health` | 🟢 OPERATIONAL · 80 ms |
| Endpoint `/api/v6/nutrition-intelligence/v12-plus/fiche-saline-ultime` | 🟢 OPERATIONAL · 37 ms moyenne |
| Daemon β2-ΣΤ 6 workers | 🟢 Inchangé, continue production |
| Watchdog supervisor | 🟢 RUNNING |
| Verrou Phase III | 🔒 STRICT |
| Schedulers T+1h/T+3h/T+6h | 🟢 Actifs |
| NEVER BLANK Ω | 🟢 GARANTI |

---

**FIN ACTIVATION V12-SUPRA+ · FICHE SALINE ULTIME PRD-READY OPÉRATIONNELLE · EN ATTENTE DIRECTIVE COMMANDANT POUR INTÉGRATION UI**
