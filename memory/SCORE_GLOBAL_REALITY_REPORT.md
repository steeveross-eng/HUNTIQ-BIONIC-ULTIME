# SCORE_GLOBAL_REALITY_REPORT — Phase IX

**Date:** 2026-04-19 22:20Z | **Engine:** SCORE-GLOBAL-REALITY-Ω | **Mode:** REALITE

## 1. Abandon du mode non-invasif

Avant Phase IX, `engine_score_global` utilisait uniquement `_multi_engine_score` V8 legacy + axes optionnels via paramètres nommés.

**Maintenant :** la fonction lit directement le bundle V20 complet et **recalcule** un composite 21-axes SUPRA-Ω.

La fonction `compute_score_global(..., bundle=...)` ajoute le mode REALITE tout en préservant le legacy (si `bundle=None` → legacy V8).

## 2. Pondérations calibrées (total = 100%)

| Rang | Axe SUPRA-Ω | Poids | Justification |
|---|---|---|---|
| 1 | nutrition (V12-SUPRA) | 10% | Biologie alimentaire = base survie |
| 2 | habitat-supra | 8% | Habitat = fondation écologique |
| 2 | stress_anthropique-Ω | 8% | Pression humaine = facteur majeur |
| 4 | population-dynamics-Ω | 6% | Dynamique démographique |
| 4 | hotspots | 6% | Pattern spatial validé |
| 4 | connectivite-ecologique-Ω | 6% | Corridors = viabilité long terme |
| 4 | comportement-biologique-Ω | 6% | Activité saisonnière |
| 4 | thermique-microclimat-Ω | 6% | Stress chaleur/froid |
| 9 | quality-donnees-Ω | 5% | Fiabilité système |
| 9 | calibration-Ω | 5% | Calibration modèles |
| 11 | sensoriel-vent-odeurs-Ω | 4% | Détection prédateurs |
| 11 | hydrologie-supra | 4% | Eau = limitation |
| 11 | sol-supra | 4% | Fertilité minérale |
| 11 | climat-futur-Ω | 4% | Projection 2030-2050 |
| 11 | pression-atmospherique-Ω | 4% | Activité avant fronts |
| 11 | **incertitude-Ω (inverse)** | 4% | Certitude = qualité score |
| 17 | zones | 3% | Proxy score zones moyennes |
| 18 | lunaire-Ω | 2% | Solunar (effet faible) |
| 18 | ia-vision-ecologique-Ω | 2% | Reconnaissance zones probables |
| 18 | **contamination-Ω (malus)** | 2% | Pénalité cônes contam |
| 21 | vent | 1% | Proxy richesse segments |

**Total : 100%**

## 3. Résultat observé (QC 46.8139, cerf, oct, 7h)

```
score_global: 66.71 / classification: BON
axes_count: 21
Top 5 axes:
  hotspots:        96.8
  quality:         94.5
  incertitude_inv: 88.2
  thermique:       86.5
  connectivite:    85.3
```

## 4. Validation

- **Test dédié** : `test_score_global_reality.py` (26e suite SELF-AUDIT)
- Vérifie : somme pondérations = 1.0 ±0.01, score ∈ [0,100], axes_count = 21, bundle expose `score_global_reality`
- **SELF-AUDIT complet 26/26 OK, PERF-GUARD severity_max = ok**

## 5. Intégration pipeline

- `compute_territoire_v10` calcule `score_global_reality` APRÈS tous les autres engines (lecture du bundle partiel)
- Exposé dans le bundle : `score_global_reality` (champ de haut niveau)
- Contient : `mode, score_global, classification, axes_scores (dict 21), weights, axes_count`

## 6. Comparaison avant/après

| Aspect | Avant (non-invasif) | Après (Phase IX REALITE) |
|---|---|---|
| Formule | `_multi_engine_score` V8 (3-4 composantes legacy) | Composite pondéré 21 axes SUPRA-Ω |
| Axes considérés | saline + affut + terrain (+ opt nutrition) | **21 axes SUPRA-Ω** |
| Scientificité | Heuristique V8 | Calibré SCIENCE-Ω |
| Traçabilité | Partielle | **Complète** (chaque axe exposé) |

## 7. Backlog (Phase X éventuelle)

- Calibration des pondérations par machine learning sur observations terrain (caméras Reconyx, GPS collar)
- Variante par espèce (pondérations spécifiques cerf vs orignal vs ours)
- Intégration feedback ENGINE-CALIBRATION-Ω pour ajuster pondérations dynamiquement
