# RAPPORT_X200_P3B_PREDICTIVE_MULTIPOINT_Ω

**Protocole** : BCE-4X ULTIME ABSOLU — TOP-ABSOLU  
**Phase**     : X200_P3B_HUMAN_PREDICTIVE_Ω — Axe 2 : PREDICTIVE multi-points  
**Commandant**: STEEVE-MAX — Date : 2026-04-23 (UTC)  
**Waypoint**  : LAT 48.206657 / LNG -68.382422  
**V30**       : LOCKED — INTANGIBLE

## 1. Objet
Étendre l'intégration `predictive_omega` → smoother X180 en échantillonnant
**plusieurs points** le long des corridors longs (au lieu du seul point
médian de P2) et en agrégeant par moyenne pondérée déterministe.

## 2. Barème institutionnel X200-P3B

| Longueur path        | N samples | Indices fractionnaires | Poids (kernel centré)    |
|----------------------|-----------|------------------------|---------------------------|
| L < 200 m            | **1**     | [ 1/2 ]                | [1.00]                    |
| 200 m ≤ L < 400 m    | **3**     | [ 1/4, 2/4, 3/4 ]      | [0.25, 0.50, 0.25]        |
| L ≥ 400 m            | **5**     | [ 1/6, 2/6, …, 5/6 ]   | [0.10, 0.20, 0.40, 0.20, 0.10] |

Bornes dures : `MULTIPOINT_MIN_SAMPLES=1`, `MULTIPOINT_MAX_SAMPLES=5`.

## 3. Reproductibilité
- Aucune RNG utilisée.
- Indices `_sample_indices(n_path, n_samples)` → fractions rationnelles fixes.
- Poids `MULTIPOINT_WEIGHTS[n]` → constantes (somme = 1.0).
- Méthode : `aggregation_method = "weighted_mean_kernel_centered"` (traçable).

Test dédié : `test_multipoint_reproducibility` → deux appels identiques
retournent des samples identiques.

## 4. Formule Ω

```
probability_raw = Σ (P_i · w_i) / Σ w_i        ∀ i ∈ [0..n_samples-1]
corridor_probability_omega = probability_raw · hierarchical_factor
```

Où `hierarchical_factor = COMMANDANT_WEIGHT / 6` (inchangé P2, CRITIQUE=6 → FAIBLE=1).

## 5. Traçabilité des échantillons

Chaque corridor porte désormais dans
`corridor_probability_components` :
- `n_samples` : 1 / 3 / 5
- `path_length_m` : longueur géodésique cumulée du path
- `aggregation_method` : `weighted_mean_kernel_centered`
- `samples` : liste détaillée `{order, path_index, lat, lng, probability_0_1, weight}`

Cette granularité permet un audit institutionnel point-par-point.

## 6. Preuve live (waypoint officiel)

```
POST /api/v20/territoire/corridors-organic/generate (P2+P3+P3B actifs)
→ HTTP 200
   n_samples distribution = { 5: 21,  3: 1 }      ← corridors longs majoritaires
   corridor[0].path_length_m        = 732.13
   corridor[0].n_samples            = 5
   corridor[0].aggregation_method   = weighted_mean_kernel_centered
   corridor[0].corridor_probability_omega = 0.098
```

## 7. Tests manuels — 7 cas verts

- `test_sample_indices_deterministic_1_3_5` ✅ — indices vérifiés.
- `test_choose_n_samples_by_path_length` ✅ — 1/3/5 selon longueur.
- `test_multipoint_weights_sum_to_1` ✅ — poids normalisés.
- `test_short_path_uses_single_sample` ✅ — fallback 1 échantillon.
- `test_long_path_uses_five_samples` ✅ — 5 échantillons, path_length > 800 m.
- `test_multipoint_aggregation_matches_weighted_mean` ✅ — écart < 1e-3.
- `test_multipoint_reproducibility` ✅ — samples identiques à chaque appel.
- `test_p3b_does_not_import_v30` ✅ — `sys.modules` V30 inchangé.

## 8. Garde-fous Ω
- V30 intangible (preuve par sys.modules).
- Aucun rendu hors smoother.
- DIAGNOSTIC-CORRIDORS-Ω inactif.
- Zones/salines non modifiées.

## 9. Fichiers impactés
```
backend/engines/post_smoothing/predictive_integration.py    (multi-points)
backend/tests/test_x200_p3b_human_predictive.py             (AXE 2 : 8 tests)
memory/RAPPORT_X200_P3B_PREDICTIVE_MULTIPOINT_Ω.md          (présent rapport)
```

**STATUT : SCELLÉ — PREDICTIVE MULTI-POINTS OPÉRATIONNEL**
