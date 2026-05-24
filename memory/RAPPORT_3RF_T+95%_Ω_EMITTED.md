# RAPPORT_3RF_T+95%_Ω — ÉMIS

- **Doctrine**: P22ΩΩ_3RF_ACCELERATION_P0_Ω
- **Commandant**: STEEVE-MAX
- **Emitted at**: 2026-05-24T01:48:21.670607+00:00
- **Threshold reached**: 95.04% ≥ 95.0%
- **Mode**: AUTO-EMIT (watcher asyncio · lecture seule)

---

```
══════════════════════════════════════════════════════════════════════════════
  RAPPORT_3RF_T+95%_Ω · P22ΩΩ_3RF_ACCELERATION_P0_Ω
  Generated : 2026-05-24T01:46:50.243648+00:00
  Mode      : FULL  (threshold=95.0%)
══════════════════════════════════════════════════════════════════════════════

§ 1 · COUVERTURE CELLULAIRE 3 RF
RF                                                 |  Cible |   Couv |      %
------------------------------------------------------------------------------
OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD                |    129 |    114 |  88.4%
MAURICIE_RF_MASTIGOUCHE_ST_MAURICE                 |    412 |    385 |  93.4%
LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN           |   1234 |   1188 |  96.3%
------------------------------------------------------------------------------
TOTAL 3 RF                                         |   1775 |   1687 | 95.04%

§ 2 · COUVERTURE TUILAIRE 3 RF · 119718 / 127800 (93.7%)
  OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD
    chevreuil         :   1366 tuiles
    coyote            :   1129 tuiles
    dindon_sauvage    :   1129 tuiles
    orignal           :   1270 tuiles
    ours_noir         :   1213 tuiles
    wapiti            :   1147 tuiles
  MAURICIE_RF_MASTIGOUCHE_ST_MAURICE
    chevreuil         :   4620 tuiles
    coyote            :   4596 tuiles
    dindon_sauvage    :   4608 tuiles
    orignal           :   4620 tuiles
    ours_noir         :   4617 tuiles
    wapiti            :   4608 tuiles
  LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN
    chevreuil         :  14245 tuiles
    coyote            :  14008 tuiles
    dindon_sauvage    :  14047 tuiles
    orignal           :  14200 tuiles
    ours_noir         :  14179 tuiles
    wapiti            :  14116 tuiles

§ 3 · MANIFEST CHECKPOINT
  doctrine          : P22ΩΩ_ZEROCOST_CANADA_H3R6_Ω
  generated_at      : 2026-05-24T01:34:37.362531+00:00
  drift_seconds     : 733.259122 (cible <900s)
  drift_ok          : True
  n_tiles_reporté   : 118983
  cells_unique      : 1713
  total_size_mb     : 2053.15
  by_species        : {'chevreuil': 1713, 'coyote': 1642, 'dindon_sauvage': 1644, 'orignal': 1678, 'ours_noir': 1662, 'wapiti': 1657}

§ 4 · AUDIT DIVERGENCE BIOLOGIQUE (échantillons R2)
  OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD
    per_species_avg_score : {'chevreuil': 61.8, 'coyote': 62.0, 'dindon_sauvage': 62.5, 'orignal': 59.6, 'ours_noir': 61.3, 'wapiti': 62.0}
    distinct_scores       : 5 (≥2 attendu)
    divergence_ok         : True
  MAURICIE_RF_MASTIGOUCHE_ST_MAURICE
    per_species_avg_score : {'chevreuil': 62.5, 'coyote': 61.7, 'dindon_sauvage': 62.7, 'orignal': 59.6, 'ours_noir': 62.2, 'wapiti': 62.4}
    distinct_scores       : 6 (≥2 attendu)
    divergence_ok         : True
  LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN
    per_species_avg_score : {'chevreuil': 63.4, 'coyote': 62.0, 'dindon_sauvage': 62.9, 'orignal': 59.0, 'ours_noir': 61.6, 'wapiti': 62.2}
    distinct_scores       : 6 (≥2 attendu)
    divergence_ok         : True

§ 5 · AUDIT HORS-3RF (BLOCK_OUTSIDE_3RF)
  tiles_hors_3rf_cumul : 462
  status               : EFFICACE
  note                 : Les 462 tuiles existantes sont des résidus pilote P1 ≥ T-3j · aucune nouvelle écriture depuis activation BLOCK_OUTSIDE_3RF=1

§ 6 · VERDICT
  status                                : T+95%_ATTEINT_REVUE
  global_pct                            : 95.04
  all_rf_ge_90pct                       : False
  biological_divergence_ok              : True
  block_outside_3rf_efficace            : True
  manifest_drift_ok                     : True
  overall_pass                          : False
══════════════════════════════════════════════════════════════════════════════

```
