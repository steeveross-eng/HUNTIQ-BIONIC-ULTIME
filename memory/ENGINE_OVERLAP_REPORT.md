# ENGINE_OVERLAP_REPORT — Inventaire anti-duplication

**Date:** 2026-04-19
**Directive:** COMMANDE Phase II — Inventaire officiel des engines
**Scope audit:** `/app/backend/engines/v8_institutional/` + `/app/backend/modules/` + `/app/backend/core/scoring_pipeline/`

---

## 1. Engines CONFIRMÉS dans la pipeline V20 (source de vérité)

Un seul moteur par responsabilité est appelé dans `compute_territoire_v10()` :

| # | Moteur | Fichier | Version | Portée pipeline V20 | Dépendances |
|---|---|---|---|---|---|
| 1 | TERRAIN | `terrain_v10_supra.py` → `lidar_irda_v11.py` | V11-LIDAR-IRDA-SUPRA | `compute_terrain_v10()` | LiDAR WCS 1m, IRDA pédologie, Open-Meteo |
| 2 | ZONES | `engine_zones.py` (stub 10L) + `territoire_v10_supra.compute_zones_v10` | V10-TA | `compute_zones_v10()` | terrain_v10, phase_b_engines |
| 3 | COMPORTEMENT | `engine_comportement.py` + `engine_comportement_avance.py` | V8 stubs | **NON appelé** V20 directement | phase_c (legacy) |
| 4 | CORRIDORS | `territoire_v10_supra.compute_corridors_omega` | Ω V12 | `compute_corridors_omega()` | terrain_v10, zones |
| 5 | AFFÛTS | `territoire_v10_supra.compute_affuts_omega` | Ω V12 | `compute_affuts_omega()` | zones, corridors, terrain |
| 6 | CONTAMINATION | `territoire_v10_supra.compute_contamination_omega` | Ω | `compute_contamination_omega()` | affuts, vent |
| 7 | SALINES | `territoire_v10_supra.compute_salines_omega` + `engine_salines_v11_supra.py` | V11-SUPRA | `compute_salines_omega()` + `enrich_salines_v11_supra()` | terrain, corridors, affuts, contamination, nutrition (indirect) |
| 8 | HOTSPOTS | `engine_hotspots.py` (stub) + `territoire_v10_supra.compute_hotspots_v10` | V10 | `compute_hotspots_v10()` | zones, corridors, affuts |
| 9 | VENT | `engine_vent.py` | V8-V3 | `compute_wind_vectors()` | Open-Meteo |
| 10 | NUTRITION | `engine_nutrition_v12_supra.py` | **V12-SUPRA-2026-04** | `compute_nutrition_v12()` | terrain, zones, corridors, affuts, hotspots, salines |
| 11 | INTELLIGENCE | `engine_intelligence.py` | V8+axe nutrition | appelé via `/api/*` pas V20 bundle | phase_a_engines |
| 12 | SCORE GLOBAL | `engine_score_global.py` | V8+axe nutrition | appelé via `/api/*` pas V20 bundle | phase_c_engines |
| 13 | ESI-Ω | `esi_omega.py` | Ω | validate_bundle | — |
| 14 | SELF-AUDIT-Ω | `self_audit_omega.py` | Ω (11 suites) | hook startup + `/self-audit` | — |
| 15 | SLA-BASELINE-Ω | `sla_baseline_omega.py` | Ω hybride | `/sla-baseline/*` | PERF-GUARD |
| 16 | MVT-TILES | `v20_mvt_tiles.py` | V20 (8 layers) | `/tiles/{layer}/{z}/{x}/{y}.json` | bundle cache |
| 17 | PERFORMANCE-BUNDLE | `v20_performance_bundle.py` | V11-SUPRA | `/bundle` cache LRU 10K + disk | territoire_v10 |

---

## 2. Engines stubs v8_institutional NON intégrés V20 (legacy, 13 fichiers)

Ces moteurs existent comme fichiers courts (8-100 lignes) mais **ne sont pas appelés par `compute_territoire_v10`** :

| Fichier | Lignes | Rôle documenté | Statut V20 |
|---|---|---|---|
| `engine_nutrition.py` | 24 | Stub délégation (V8-NUTRITION-MINERAUX) | **REMPLACÉ par V12-SUPRA** — à supprimer backlog |
| `engine_salines.py` | — | Stub V8 | REMPLACÉ par V11-SUPRA |
| `engine_comportement.py` | 20 | Stub V8 | Non intégré V20 |
| `engine_comportement_avance.py` | 12 | Stub V8 | Non intégré V20 |
| `engine_connectivite.py` | 13 | Stub V8 | Non intégré V20 |
| `engine_saisonnalite.py` | 16 | Stub V8 | Non intégré V20 |
| `engine_pression.py` | 14 | Stub V8 | Non intégré V20 |
| `engine_risque.py` | 15 | Stub V8 | Non intégré V20 |
| `engine_visibilite.py` | 16 | Stub V8 | Non intégré V20 |
| `engine_frequentation.py` | 19 | Stub V8 | Non intégré V20 |
| `engine_heatmap.py` | 22 | Stub V8 | Non intégré V20 |
| `engine_cameras.py` | 8 | Stub V8 | Non intégré V20 |
| `engine_terrain_cost.py` | 12 | Stub V8 | Non intégré V20 |
| `engine_prediction.py` | 88 | Engine partiel | Non intégré V20 |
| `engine_psychologie.py` | 87 | Engine partiel | Non intégré V20 |
| `engine_bio_signes.py` | 94 | Engine partiel | Non intégré V20 |
| `engine_audio_acoustique.py` | 90 | Engine partiel | Non intégré V20 |
| `engine_corridors.py` | — | Stub V8 | REMPLACÉ par `compute_corridors_omega` |
| `engine_affuts.py` | — | Stub V8 | REMPLACÉ par `compute_affuts_omega` |

**Impact V20 : AUCUN** — ces moteurs ne sont pas référencés par la pipeline. Ils constituent du code mort/historique à nettoyer (backlog).

---

## 3. Chevauchements identifiés (hors pipeline V20)

### 3.1 Chevauchement NUTRITION (7 fichiers)

| Fichier | Nature | Risque pipeline V20 |
|---|---|---|
| `engine_nutrition_v12_supra.py` | **Moteur officiel V12-SUPRA** | Aucun (source de vérité) |
| `engine_nutrition.py` (v8_institutional) | Stub 24L non appelé | Aucun — à purger backlog |
| `modules/bionic_engine_p0/engines/nutrition_engine.py` | Module legacy P0 | Non appelé V20 |
| `modules/saline_engine/engines/wildlife_nutritional_engine.py` | Legacy saline-nutrition | Non appelé V20 |
| `modules/nutrition_v6_interface/wrappers/wildlife_nutrition_attractiveness.py` | API V6 wrapper | API distincte `/api/v6` |
| `modules/species_engine/nutrition.py` | Données par espèce | Legacy — à consolider |
| `core/scoring_pipeline/alimentation_v2/nutrition.py` | Legacy scoring v2 | Non appelé V20 |

**Verdict :** Chevauchement existe mais **confiné hors pipeline V20**. Un seul moteur (`engine_nutrition_v12_supra.py`) est effectivement appelé. Nettoyage = **backlog purge** (P2), pas bloquant.

### 3.2 Chevauchement SALINES (5 fichiers)

| Fichier | Nature | Risque V20 |
|---|---|---|
| `engine_salines_v11_supra.py` | **Moteur officiel V11-SUPRA** | Aucun (source de vérité) |
| `engine_salines.py` (v8_institutional) | Stub V8 | Non appelé V20 |
| `modules/saline_engine/engines/saline_recommendation_engine.py` | API recommandation | API distincte |
| `core/scoring_pipeline/alimentation_v2/salines.py` | Legacy | Non appelé V20 |
| `core/scoring_pipeline/alimentation_v4/salines_v4.py` | Legacy v4 | Non appelé V20 |

**Verdict :** idem, chevauchement hors V20. Backlog P2.

### 3.3 Chevauchement CONNECTIVITÉ / HABITAT / SENSORIEL

- `engine_connectivite.py` (v8_institutional stub 13L) = ne fait que déléguer à `ecosystem_v1, bdre`
- Aucun moteur SUPRA institutionnel connectivité écologique dédié
- Aucun moteur HABITAT autonome (fonction `score_habitat` intégrée **dans V12-SUPRA NUTRITION**)
- Sensoriel : `engine_visibilite`, `engine_audio_acoustique`, `engine_bio_signes` partiels

**Verdict :** pas de duplication bloquante. Les fonctions habitat/connectivité/sensoriel sont soit absentes, soit partielles, soit déjà encapsulées dans V12-SUPRA.

---

## 4. Absence vérifiée des engines SUPRA-Ω demandés

| Engine SUPRA-Ω | Existe ? | Note |
|---|---|---|
| ENGINE-HABITAT-SUPRA | ❌ absent | **Fonction `score_habitat` déjà dans V12-SUPRA** — futur engine externe possible |
| ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω | ❌ absent | — |
| ENGINE-CONNECTIVITÉ-ÉCOLOGIQUE-Ω | ❌ absent (stub 13L seulement) | — |
| ENGINE-SENSORIEL-VENT-ODEURS-Ω | ❌ absent | `engine_vent` + `olfactive_diffusion` (terrain) partiel |
| ENGINE-STRESS-ANTHROPIQUE-Ω | ❌ absent | `engine_pression` stub 14L |
| ENGINE-THERMIQUE-MICROCLIMAT-Ω | ❌ absent | `thermal_comfort` (terrain) partiel |
| ENGINE-IA-VISION-ÉCOLOGIQUE-Ω | ⚠️ partiel | `_ia_vision_forest` dans terrain_v10 |
| ENGINE-POPULATION-DYNAMICS-Ω | ❌ absent | — |
| ENGINE-SCIENCE-Ω | ❌ absent | — |
| ENGINE-QUALITÉ-DONNÉES-Ω | ❌ absent | `data_fiabilite` champ partiel |
| ENGINE-INCERTITUDE-Ω | ❌ absent | — |
| ENGINE-CALIBRATION-Ω | ❌ absent | — |
| ENGINE-CLIMAT-FUTUR-Ω | ❌ absent | — |
| ENGINE-HYDROLOGIE-SUPRA | ❌ absent | `hydro_index` terrain partiel, IRDA |
| ENGINE-SOL-SUPRA | ❌ absent | IRDA `drainage_class` + `soil_moisture` partiel |
| ENGINE-MONITORING-Ω | ❌ absent | SELF-AUDIT-Ω + SLA-BASELINE-Ω **proches** |
| ENGINE-ALERTE-ANOMALIES-Ω | ❌ absent | PERF-GUARD-Ω **proche** |
| ENGINE-GOUVERNANCE-Ω | ❌ absent | `governance` legacy référencé |
| ENGINE-INFLUENCE-LUNAIRE-Ω | ❌ absent | — |
| ENGINE-PRESSION-ATMOSPHÉRIQUE-Ω | ❌ absent | Open-Meteo `pressure_hpa` disponible mais non utilisé |
| ENGINE-ESPÈCE-Ω | ❌ absent | `modules/species_engine` legacy |

---

## 5. Verdict institutionnel

> **AUCUN CHEVAUCHEMENT BLOQUANT dans la pipeline V20.**
> **AUTORISATION DE PROCÉDER à la Phase SUPRA accordée.**

- Les 21 engines SUPRA-Ω demandés sont tous absents (ou à l'état de stubs/partiels).
- Les chevauchements NUTRITION/SALINES existent uniquement dans du code legacy **hors pipeline V20** (API V6, scoring legacy v2/v4, modules P0). Un seul moteur par responsabilité est effectivement exécuté par `compute_territoire_v10`.
- Backlog P2 recommandé : purger les stubs `engine_nutrition.py`, `engine_salines.py`, `engine_corridors.py`, `engine_affuts.py` de `v8_institutional/` pour éliminer toute ambiguïté.

## 6. Recommandations ordre d'activation SUPRA-Ω (P0→P2)

**P0 (directement utiles V20 actuel) :**
1. ENGINE-HABITAT-SUPRA (extraire + enrichir `score_habitat` de V12-SUPRA)
2. ENGINE-HYDROLOGIE-SUPRA (étendre IRDA + nappe + hydro_index)
3. ENGINE-SOL-SUPRA (pédologie Ca/Na/K/Mg échangeables — comblerait la limitation V12-SUPRA)
4. ENGINE-STRESS-ANTHROPIQUE-Ω (pression humaine = axe majeur manquant)
5. ENGINE-MONITORING-Ω + ENGINE-ALERTE-ANOMALIES-Ω (fusion avec SELF-AUDIT/PERF-GUARD existants)

**P1 :**
6. ENGINE-SENSORIEL-VENT-ODEURS-Ω (fusion vent + olfactive_diffusion)
7. ENGINE-THERMIQUE-MICROCLIMAT-Ω (fusion thermal_comfort + Open-Meteo)
8. ENGINE-CONNECTIVITÉ-ÉCOLOGIQUE-Ω
9. ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω
10. ENGINE-ESPÈCE-Ω
11. ENGINE-IA-VISION-ÉCOLOGIQUE-Ω (upgrade IA vision existante)

**P2 (scientifique avancé) :**
12. ENGINE-POPULATION-DYNAMICS-Ω
13. ENGINE-INCERTITUDE-Ω + ENGINE-CALIBRATION-Ω + ENGINE-QUALITÉ-DONNÉES-Ω
14. ENGINE-SCIENCE-Ω
15. ENGINE-GOUVERNANCE-Ω

**P3 (exotique/recherche) :**
16. ENGINE-CLIMAT-FUTUR-Ω
17. ENGINE-INFLUENCE-LUNAIRE-Ω
18. ENGINE-PRESSION-ATMOSPHÉRIQUE-Ω

Fin du rapport.
