# ENGINE_NUTRITION_STATUS — Rapport diagnostic Phase II

**Date:** 2026-04-19
**Auditeur:** BIONIC OS V20-SUPRA (BCE-4X ULTIME ABSOLU)
**Directive:** COMMANDE — ENGINE-NUTRITION-V12-SUPRA — VALIDATION + INTÉGRATION

---

## 1. Scan moteurs actuels (`/app/backend/engines/v8_institutional/`)

| # | Moteur | Fichier | État | Notes |
|---|---|---|---|---|
| 1 | NUTRITION | `engine_nutrition.py` | ⚠️ **STUB** | 24 lignes, aucune logique, délégation non-fonctionnelle |
| 2 | MINÉRAUX | — | ❌ **ABSENT** | Logique partielle dans `_analyze_nutrition_600m` (SALINES-V11) |
| 3 | COMPORTEMENT | `engine_comportement.py` + `engine_comportement_avance.py` | ✅ OK | Opérationnel |
| 4 | ZONES | `engine_zones.py` + `compute_zones_v10` | ✅ OK | Polygones organiques, score terrain-aware |
| 5 | SALINES | `engine_salines_v11_supra.py` | ✅ OK | Multi-axe bio/terrain/nutrition/réseau (consomme stub nutrition actuel) |
| 6 | HOTSPOTS | `engine_hotspots.py` + `compute_hotspots_v10` | ✅ OK | Opérationnel |
| 7 | TERRAIN | `terrain_v10_supra.py` + `lidar_irda_v11.py` | ✅ OK | LiDAR 1m + IRDA + Open-Meteo |
| 8 | VENT | `engine_vent.py` | ✅ OK | Vecteurs vent réels |
| 9 | CONTAMINATION | `compute_contamination_omega` | ✅ OK | Source = affûts |
| 10 | INTELLIGENCE | `engine_intelligence.py` | ✅ OK | Composite saline+affût+terrain (**sans axe nutrition**) |
| 11 | SCORE GLOBAL | `engine_score_global.py` | ✅ OK | Multi-engine composite (**sans axe nutrition**) |

## 2. Analyse détaillée `engine_nutrition.py` actuel

```python
# Ce engine delegue aux engines existants preserves:
# - engines/nutrition_intelligence/ (12 sous-engines x5100-x7000)  [INEXISTANTS]
# - modules/saline_engine/engines/ (7 sous-engines)                 [INEXISTANTS]
# - core/scoring_pipeline/alimentation_v1/ + alimentation_v2/       [INEXISTANTS]

def get_nutrition_status():
    return {"engine": "V8-NUTRITION-MINERAUX", "status": "ACTIF — delegation preservee"}
```

- **Nom:** V8-NUTRITION-MINERAUX
- **Version:** stub v8 (jamais migré)
- **Portée:** nulle (aucune fonction exécutable hors statut)
- **Inputs:** aucun
- **Outputs:** un dict de statut static
- **Dépendances:** 3 chemins référencés mais **inexistants** dans le filesystem courant
- **Niveau de précision:** 0 (aucun calcul)
- **Intégration `compute_territoire_v10`:** ❌ AUCUNE

## 3. Verdict institutionnel

> **INSUFFISANT — migration V12-SUPRA requise et validée par le Commandant.**

Raisons :
1. Aucune logique nutritionnelle réelle
2. Dépendances délégation **cassées** (chemins inexistants)
3. Aucun output obligatoire produit (0/7)
4. Aucune intégration pipeline
5. Aucune influence sur corridors / hotspots / salines / intelligence / score global

## 4. Arbitrages Commandant (Phase II → Phase III)

| Choix | Décision |
|---|---|
| Exposition | **c) Hybride** — layer MVT `nutrition` + injection partout |
| Intégration INTEL/SCORE | **a) Axe `nutrition_score` non invasif** |
| Profondeur | **a) MVP V12-SUPRA sans mock** (données réelles uniquement) |
| Reseed SLA | **b) Manuel** sur ordre Commandant |

## 5. Données réelles disponibles pour V12-SUPRA (pas de mock)

Provenance `terrain_v10_supra` / `lidar_irda_v11` :
- Topographie LiDAR 1m : `elevation_m`, `pente_deg`, `pente_max_deg`, `exposition_deg`, `rugosite`, `micro_relief_m`
- Forêt IA-Vision : `canopy`, `strate_1_3m`, `feuillus_ratio`, `couvert_pct`
- Hydrologie IRDA : `distance_eau_m`, `drainage_class`, `zone_humide`, `soil_moisture`, `nappe_profondeur_m`, `hydro_index`
- Surfaces dérivées : `cost_surface`, `thermal_comfort`, `olfactive_diffusion`, `connectivity`
- Flags bio : `zone_repos_probable`, `zone_alimentation_probable`, `zone_thermique_probable`, `zone_humide_probable`
- Météo Open-Meteo : `temperature_c`, `humidity_pct`, `snow_depth_m`, `radiation`, `wind`

## 6. Limitations connues (non-mock, à documenter Phase V)

- Absence d'inventaire forestier détaillé par essence (épinette/sapin/bouleau/érable) → `feuillus_ratio` seul en proxy
- Absence de carte pédologique nationale (Ca/Na/K/Mg) → `drainage_class` + `canopy` en proxy minéraux
- Pas de données de broutage historiques (pression ongulés) → fallback modèle saisonnier

## 7. Décision Phase III

✅ **EXÉCUTER** création `engine_nutrition_v12_supra.py` + livrables associés.
