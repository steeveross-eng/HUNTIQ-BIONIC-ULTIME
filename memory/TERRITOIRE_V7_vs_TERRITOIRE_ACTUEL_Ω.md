# RAPPORT COMPARATIF — TERRITOIRE V7 ULTIME vs TERRITOIRE ACTUEL (V20-X180)
## PHASE_XI_SUPRA_COMPARATIF_TERRITOIRE_Ω
## VERSION_X197-SUPRA-V7_vs_TERRITOIRE_ACTUEL-Ω — AMENDEMENT-ABSOLU

**Commandant** : STEEVE-MAX  
**Date** : 2026-04-22  
**Waypoint canonique** : 48.206657 / -68.382422  
**Archive V7 ULTIME de référence** : SHA-256 `c8c2f6a3339b3fb5624d3cc640174ed6fc07e10d4c519bb9f2341a788d1dc29f`  
**Engine V30 TERRITOIRE ACTUEL** : SHA-256 `27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c` (scellé)

---

## 1. PORTÉE DU COMPARATIF

Ce rapport étend le rapport X195 (centré corridors/moteurs) à **l'ENSEMBLE du TERRITOIRE** :
zones écologiques, attracteurs, réseau veineux, pondérations, IA Vision, multi-échelles,
locomotion, densité, fusion, continuité, hiérarchie d'intensités, terrain-aware.

Les valeurs V7 ULTIME sont extraites verbatim des sources archivées :
- `backend/core/scoring_pipeline/corridors_v10/scoring.py` (8 facteurs)
- `backend/core/scoring_pipeline/corridors_v10/classifier.py` (5 niveaux CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE)
- `backend/core/scoring_pipeline/corridors_v10/species_profiles.py` (profils CERF/ORIGNAL/...)
- `backend/engines/spatial_engine_v7/router.py` (heatmap, vision-scoring)
- `backend/modules/nutrition_engine_v7/pipeline.py` (Sol → Nutriments → Fourrage → Gibier)
- `backend/modules/salines_ultime_engine/` (5 scores × 20 sources)
- `backend/modules/access_clarity_engine_v7/` (pondérations accès)

Les valeurs TERRITOIRE ACTUEL sont extraites verbatim des sources en production :
- `frontend/src/lib/renduOmegaStore.js` (RENDU_OMEGA, 3 épaisseurs, 600 m ± 30 %)
- `backend/engines/post_smoothing/organic_corridor_smoother.py` (X180-AMENDEMENT-FINAL)
- `backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py` (V30 LOCKED)

---

## 2. ZONES ÉCOLOGIQUES

| Zone | V7 ULTIME | TERRITOIRE ACTUEL (V20-X180) | Impact |
| --- | --- | --- | --- |
| Habitat optimal | Classification 4 niveaux `CLASSIFICATION_THRESHOLDS` (OPTIMAL ≥75, FONCTIONNEL ≥50, DEGRADE ≥25, INUTILISABLE) | Inspection-bio filters (HABITAT_AWARE_Ω, min 1 zone vitale non-excluded) | **PERTE** : pas de gradient OPTIMAL/FONCTIONNEL/DEGRADE — binaire habitat/non-habitat |
| Zones repos (`repos_v1`) | Moteur dédié `/api/v1/repos` par espèce | Type `repos` dans `VITAL_ZONE_TYPES` smoother (liste plate) | **SIMPLIFICATION** : scoring repos V7 non reconduit post-smoother |
| Zones alimentation (`alimentation_v1/v2`) | 2 moteurs `/api/v{1,2}/alimentation` multi-espèces | Type `alimentation` dans `VITAL_ZONE_TYPES` | **PERTE** : pipeline nutritionnel détaillé (Sol→Nutriments→Fourrage→Gibier) non exposé au smoother |
| Zones rut | Pondération saisonnière par espèce (`saisonnalite`) | Type `rut` dans `VITAL_ZONE_TYPES` | **PARITÉ type**, perte saisonnalité |
| Zones humides | `wet` + `affinite_hydro` (profils espèces) | `humide` dans `VITAL_ZONE_TYPES` + `water_tolerance_m` | **DIVERGENCE** : V7 attirait, V20 ne distingue que tolérance |
| Forêts matures | `preference_forestiere` ∈ [0,1] + `canopy_density` scoring | Non exposé post-smoother | **PERTE CRITIQUE** : 2e facteur de scoring V7 (0-20 pts) inexistant |
| Zones thermiques | `thermique` | `thermique` dans `VITAL_ZONE_TYPES` | PARITÉ type |

---

## 3. ATTRACTEURS (20 SOURCES SALINES V7)

| Attracteur | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| Salines | `salines_ultime_engine` : **5 scores × 20 sources** | Bundle V30 → `salines[]` plat, injection auto smoother | **PERTE** : 20 sources non hiérarchisées |
| Eau | `affinite_hydro` par espèce (0-1) | `water_tolerance_m` par espèce (m absolu) | **INVERSION SÉMANTIQUE** : attraction → repoussement |
| Alimentation | `compute_nutrient_layer + compute_forage_layer` (pipeline V7 Sol→Gibier) | Type `alimentation` dans `VITAL_ZONE_TYPES` | **PERTE** : scoring alimentation détaillé non branché |
| Repos | `repos_v1.compute_rest_score` par espèce | Type `repos` dans `VITAL_ZONE_TYPES` | **PERTE** : scoring repos V7 non reconduit |
| Rut | Saisonnalité (`automne.mobilite 0.95` pour cerf) | Type `rut` dans `VITAL_ZONE_TYPES` | **PERTE** : modulation saisonnière |
| Thermiques | Bonus thermal V7 (heatmap) | Type `thermique` dans `VITAL_ZONE_TYPES` | **PARITÉ type** |

---

## 4. CORRIDORS (toutes espèces)

| Aspect | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| Moteur principal | `corridors_v10` + `spatial_engine_v7` (éditables) | `engine_ia_corridors_organic_omega` (V30 LOCKED) + smoother externe | Source scellée |
| Scoring | 8 facteurs explicites (voir §6) | Non exposé post-smoother | **PERTE CRITIQUE** |
| Classification | 5 niveaux (CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE) | 3 épaisseurs (1.2 / 2.0 / 3.0 px) | **DÉGRADATION** : résolution divisée par 5/3 |
| Couleur par niveau | CRITIQUE `#CC0000`, MAJEUR `#FF0000`, FORT `#FF8C00`, MODERE `#FFD700`, FAIBLE `#BFBFBF` | Uniforme `#FF8F00` | **PERTE** : hiérarchie couleur perdue |
| Largeur | 4m / 6m / 11m / 17m / 26m selon niveau | N/A (épaisseur pixel uniquement) | **PERTE** : notion largeur_m |
| Pattern | CRITIQUE `striped` (dash `10,4`) | Aucun pattern | **PERTE** |

---

## 5. RÉSEAU VEINEUX COMPLET

| Règle | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| Rayon fonctionnel nominal | 600 m | `RENDU_OMEGA.functionalRadiusNominalM = 600` | PARITÉ frontend |
| Tolérance ±30 % | 420 m – 780 m | `functionalRadiusMinM = 420`, `functionalRadiusMaxM = 780` | **PARITÉ frontend**, **absent backend** |
| Convergence veine principale | < 15 m (fusion en veine principale) | `mainVeinConvergenceRadiusM = 15` + `detectConvergenceMainVein` | PARITÉ frontend |
| Multiplicateur halo veine | ×1.5 | `mainVeinHaloMultiplier = 1.5` | PARITÉ frontend |
| Multiplicateur luminosité | ×1.6 | `mainVeinLumMultiplier = 1.6` | PARITÉ frontend |
| Réseau continu | Règle V7 : corridor ≥ 2 zones vitales | `detect_vital_zone_connections` smoother (détecte mais ne force pas ≥ 2) | **SIMPLIFICATION** : contrainte observée mais non imposée |
| Hiérarchie sociale | `influence_dominants` (0-1) par espèce | N/A | **PERTE** : dominance non reconduite |

---

## 6. PONDÉRATIONS BIOLOGIQUES (scoring 8 facteurs V7)

Extrait verbatim `scoring.py` (0-100 points) :

| # | Facteur V7 | Poids V7 | Seuils | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- | --- | --- |
| 1 | ECL (espace classe) | **0-25 pts** | ≥0.7 → 25, ≥0.5 → 15+(x-0.5)*50, ≥0.3 → 5+(x-0.3)*50 | Non exposé | **PERTE** facteur dominant |
| 2 | Canopy density | **0-20 pts** | ≥0.7 → 20, ≥0.4 → 8+(x-0.4)*40 | Non exposé | **PERTE** |
| 3 | Distance route (pression humaine) | **0-15 pts** | ≥400m → 15, ≥200m → 8+... | `human_avoidance_m` (ours 120m) | **SIMPLIFICATION** : V7 scorait gradient, V20 seuil unique |
| 4 | Nourriture + Refuge | **0-15 pts** | `min(15, (nourriture+refuge)*10)` | Non exposé | **PERTE** |
| 5 | Micro-topo + Hydro | **0-10 pts** | `vallon*0.5 + hydro*0.3 + tampon*0.2` | `valley/wet/transition` boosts frontend | **PARITÉ partielle frontend** |
| 6 | Régénération | **0-5 pts** | `min(5, regen*7)` | Non exposé | **PERTE** |
| 7 | Coût de traversée | **0-10 pts** | `cost_per_cell` seuils 0.3/0.8/1.5 | Non exposé (IA cost surface scellée V30) | **PERTE directe** |
| 8 | Bonus diversité types zones | **×1.05** si `from_type ≠ to_type` | Non exposé | **PERTE** |
| Modif | Corridor court `<8` cellules | **×1.10** (goulot critique) | Non exposé | **PERTE** |
| Modif | Corridor long `>40` cellules | **×0.85** | Non exposé | **PERTE** |

---

## 7. PONDÉRATIONS TOPOLOGIQUES

| Signal | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| `micro_topo_vallon` | Bonus 0.5 × pct_vallon | `valley` boost 0.30 (frontend), non smoother | **PERTE backend** |
| `zone_tampon` | Bonus 0.2 si présent | Non reconduit | **PERTE** |
| `regeneration` | `min(5, regen*7)` | Non reconduit | **PERTE** |
| `distance_route_m` | Scoring gradient 0-15 pts | `human_avoidance_m` seuil unique | **SIMPLIFICATION** |
| Pente optimale par espèce | CERF 5°, ORIGNAL 8°, pentes_max par espèce | `slope_max_deg` par espèce (25/30/20/45/20) | **PARITÉ max**, **perte optimale** |
| `pente_max_deg` | CERF 15°, ORIGNAL 25° | 25° / 30° | **PARITÉ X180** |

---

## 8. PONDÉRATIONS HYDROLOGIQUES

| Signal | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| Proximité eau | **BONIFICATION** si < 150 m (`hydro_near`) | **REPOUSSEMENT** si < water_tolerance (sauf orignal) | **INVERSION SÉMANTIQUE** critique |
| `affinite_hydro` par espèce | CERF 0.60, ORIGNAL 0.85, WAPITI — | N/A — remplacé par `water_tolerance_m` | **PERTE** : échelle 0-1 attractive → mètres répulsifs |
| Traversée ruisseau | Autorisée en parallèle | Règle non implémentée dans smoother | **PERTE** règle parallèle |
| Contour lac | Longe sans toucher | Règle non implémentée | **PERTE** |
| Profondeur | V7 non distinguée | V20 non distinguée | PARITÉ |

---

## 9. PARAMÈTRES IA VISION

| Paramètre | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| Endpoint dédié | `/spatial/vision-scoring` | `engine_ia_vision_registry_omega` (registre) | Endpoint conservé |
| Pondération pins utilisateur | Explicite, pondérée par rôle | Reçue via `vision_behavioral_map` mais non re-scorée smoother | **PERTE** : pins PRO/EXPERT ne boostent plus post-smoother |
| Patterns (traces, grattage, frottoir) | 3 classes + bonus saison | Préservé via bundle V30 | **PARITÉ brute**, **perte re-scoring** |
| IA pattern matching | Algorithme V7 spatial_engine_v7 | Non exposé post-smoother | **PERTE** |

---

## 10. PARAMÈTRES MULTI-ÉCHELLES

| Paramètre | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| `terrain_multiscale` | Pipeline DEM 1m / 5m / 10m agrégé | Bundle V30 préserve `terrain_multiscale` | **PARITÉ (transparence)** |
| Résolution corridor | Grille cellulaire `row, col` | Points latlng continus | **CHANGEMENT DE REPRÉSENTATION** non destructif |
| Fusion cross-scale | V7 fusion explicit | Non gérée post-smoother | **PERTE** |

---

## 11. RÈGLES DE DENSITÉ / FUSION / CONTINUITÉ

| Règle | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| Densité (5 niveaux) | CRITIQUE / MAJEUR / FORT / MODERE / FAIBLE (weights 6/5/4/3/2) | 3 épaisseurs (1.2 / 2.0 / 3.0 px) | **DÉGRADATION 5→3** |
| Fusion veine | < 15 m endpoints proches | `detectConvergenceMainVein` frontend | PARITÉ frontend |
| Continuité | Grille continue garantie | `enforce_segment_max` subdivision linéaire | **PARITÉ** |
| Subdivision max | 26 m (FAIBLE largeur) | 20 m (`SEGMENT_MAX_M`) | **DIVERGENCE** |
| Angle max | Non scoré directement V7 | 45° universel + par espèce | **AJOUT X180** |

---

## 12. LOCOMOTION PAR ESPÈCE

| Paramètre | V7 CERF | V7 ORIGNAL | X180 CERF | X180 ORIGNAL | Impact |
| --- | --- | --- | --- | --- | --- |
| Pente optimale | 5° | 8° | N/A | N/A | **PERTE** concept optimal |
| Pente max | 15° | 25° | N/A (cerf absent) | 30° | **DIVERGENCE** orignal 25→30 |
| Sensibilité pression | 0.75 | 0.80 | N/A | N/A | **PERTE** |
| Style déplacement | sinueux | linéaire | N/A | large_stable | **RENOMMAGE** |
| Distance route évitement | 150 m | 300 m | N/A | 50 m défaut | **DIVERGENCE** 150→50 |
| Largeur corridor | 100 m | 150 m | N/A | N/A | **PERTE** |
| Préférence forestière | 0.85 | 0.75 | N/A | N/A | **PERTE** |
| Affinité hydro | 0.60 | 0.85 | N/A | `water_tolerance_m` 30 | **INVERSION** |
| Vitesse | modéré | modéré | N/A | N/A | **PERTE** |
| Saisonnalité automne mobilité | 0.95 | 0.95 | N/A | N/A | **PERTE** |

**PROFIL CERF** : **ABSENT** de `SPECIES_LOCOMOTION` X180 — chevreuil ≠ cerf (Odocoileus virginianus). **RÉGRESSION CRITIQUE**.

---

## 13. SCORING BIOLOGIQUE 8-FACTEURS

Synthèse totale des 8 facteurs V7 (max 100 pts) :

```
Score V7 = f1(ECL, 25) + f2(canopy, 20) + f3(dist_route, 15)
         + f4(nourriture+refuge, 15) + f5(topo+hydro, 10)
         + f6(regen, 5) + f7(cost, 10)
         + bonus(from≠to, +5%) * bonus(n<8, +10%) * pénalité(n>40, -15%)
```

**TERRITOIRE ACTUEL** : aucun scoring biologique n'est ré-appliqué après le V30 scellé ; le smoother ne produit que conformité géométrique.

**IMPACT** : PERTE TOTALE de la traçabilité biologique 0-100 côté post-V30.

---

## 14. TERRAIN-AWARE

| Facteur | V7 ULTIME | TERRITOIRE ACTUEL | Impact |
| --- | --- | --- | --- |
| slope_high | Bonus scoring | Frontend `terrainBoosts.slope_high = 0.20` | **PARITÉ frontend** |
| valley | `micro_topo_vallon` bonus | `terrainBoosts.valley = 0.30` | **PARITÉ frontend**, **perte backend** |
| wet | `hydro_near` bonus | `terrainBoosts.wet = 0.25` | **PARITÉ frontend** |
| transition | `zone_tampon` lisières | `terrainBoosts.transition = 0.15` | **PARITÉ frontend** |
| Cap multiplicateur | Non borné V7 | ×1.95 X180 | **CAP AJOUTÉ** (protecteur) |
| Floor | Non borné V7 | ×1.0 X180 (jamais atténuation) | **FLOOR AJOUTÉ** (protecteur) |

---

## 15. INTENSITÉS (Critique / Majeur / Fort / Modéré / Faible)

| Intensité | V7 score | V7 color | V7 weight | V7 largeur_m | V7 pattern | TERRITOIRE ACTUEL équivalent | Impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CRITIQUE | 85-100 | #CC0000 | 6 | 4 m | striped 10,4 | 3.0 px (aucune couleur dédiée) | **PERTE** dash + couleur + largeur |
| MAJEUR | 70-84 | #FF0000 | 5 | 6 m | — | 3.0 px | **PERTE** couleur + largeur |
| FORT | 50-69 | #FF8C00 | 4 | 11 m | — | 2.0 px | **DIVERGENCE** couleur (#FF8C00 → #FF8F00) |
| MODERE | 30-49 | #FFD700 | 3 | 17 m | — | 1.2 px | **PERTE** couleur |
| FAIBLE | 0-29 | #BFBFBF | 2 | 26 m | — | 1.2 px | **PERTE** couleur + distinction |

---

## 16. SIGNATURE INSTITUTIONNELLE

```
Phase         : PHASE_XI_SUPRA_COMPARATIF_TERRITOIRE_Ω
Version       : X197-SUPRA-V7_vs_TERRITOIRE_ACTUEL-Ω-AMENDEMENT-ABSOLU
Commandant    : STEEVE-MAX
Archive V7    : SHA-256 c8c2f6a3339b3fb5624d3cc640174ed6fc07e10d4c519bb9f2341a788d1dc29f
Engine V30    : SHA-256 27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c
Document companion : V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml (base CONTRAT RENDUΩ-RÉSEAU VEINEUX)
```

---

## 17. GARDE-FOUS X197 RESPECTÉS

- ✅ Panneau DIAGNOSTIC-CORRIDORS-Ω **NON ACTIVÉ**
- ✅ Aucune validation des corridors actuels
- ✅ Aucune publication hors PRO/EXPERT
- ✅ Aucun rendu expérimental (X200 non initiée)
- ✅ Engine V30 **non modifié**
- ✅ Données V7 ULTIME **non transformées, non filtrées, non simplifiées**

---

## FIN DE RAPPORT — NON VALIDATION DES CORRIDORS COURANTS

Ce rapport ne constitue PAS une approbation des corridors V20-X180 ; il documente objectivement
les divergences afin de préparer la phase X200 de reconstruction contrôlée.
