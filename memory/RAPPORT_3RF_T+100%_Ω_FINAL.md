# RAPPORT_3RF_T+100%_Ω_FINAL

- **Doctrine**: P22ΩΩ_AUTOPILOT_4D_SAFE_Ω
- **Commandant**: STEEVE-MAX
- **Emitted at**: 2026-05-24T11:35:33.073921+00:00
- **Trigger**: 3RF coverage 100.11% >= 99.5%
- **Mode**: AUTO-EMIT (autopilot orchestrator)

---

```
══════════════════════════════════════════════════════════════════════════════
  RAPPORT_3RF_T+95%_Ω · P22ΩΩ_3RF_ACCELERATION_P0_Ω
  Generated : 2026-05-24T11:34:01.474780+00:00
  Mode      : FULL  (threshold=95.0%)
══════════════════════════════════════════════════════════════════════════════

§ 1 · COUVERTURE CELLULAIRE 3 RF
RF                                                 |  Cible |   Couv |      %
------------------------------------------------------------------------------
OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD                |    129 |    130 | 100.8%
MAURICIE_RF_MASTIGOUCHE_ST_MAURICE                 |    412 |    412 | 100.0%
LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN           |   1234 |   1235 | 100.1%
------------------------------------------------------------------------------
TOTAL 3 RF                                         |   1775 |   1777 | 100.11%

§ 2 · COUVERTURE TUILAIRE 3 RF · 128013 / 127800 (100.2%)
  OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD
    chevreuil         :   1597 tuiles
    coyote            :   1549 tuiles
    dindon_sauvage    :   1549 tuiles
    orignal           :   1567 tuiles
    ours_noir         :   1549 tuiles
    wapiti            :   1549 tuiles
  MAURICIE_RF_MASTIGOUCHE_ST_MAURICE
    chevreuil         :   4944 tuiles
    coyote            :   4944 tuiles
    dindon_sauvage    :   4944 tuiles
    orignal           :   4944 tuiles
    ours_noir         :   4944 tuiles
    wapiti            :   4944 tuiles
  LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN
    chevreuil         :  14839 tuiles
    coyote            :  14818 tuiles
    dindon_sauvage    :  14827 tuiles
    orignal           :  14839 tuiles
    ours_noir         :  14833 tuiles
    wapiti            :  14833 tuiles

§ 3 · MANIFEST CHECKPOINT
  doctrine          : P22ΩΩ_ZEROCOST_CANADA_H3R6_Ω
  generated_at      : 2026-05-24T11:28:46.381374+00:00
  drift_seconds     : 315.578075 (cible <900s)
  drift_ok          : True
  n_tiles_reporté   : 128475
  cells_unique      : 1818
  total_size_mb     : 2216.24
  by_species        : {'chevreuil': 1818, 'coyote': 1787, 'dindon_sauvage': 1787, 'orignal': 1795, 'ours_noir': 1787, 'wapiti': 1787}

§ 4 · AUDIT DIVERGENCE BIOLOGIQUE (échantillons R2)
  OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD
    per_species_avg_score : {'chevreuil': 62.8, 'coyote': 62.6, 'dindon_sauvage': 62.6, 'orignal': 59.5, 'ours_noir': 62.4, 'wapiti': 62.0}
    distinct_scores       : 5 (≥2 attendu)
    divergence_ok         : True
  MAURICIE_RF_MASTIGOUCHE_ST_MAURICE
    per_species_avg_score : {'chevreuil': 61.5, 'coyote': 61.0, 'dindon_sauvage': 62.3, 'orignal': 59.5, 'ours_noir': 60.9, 'wapiti': 61.5}
    distinct_scores       : 5 (≥2 attendu)
    divergence_ok         : True
  LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN
    per_species_avg_score : {'chevreuil': 60.9, 'coyote': 61.0, 'dindon_sauvage': 61.6, 'orignal': 57.9, 'ours_noir': 61.3, 'wapiti': 61.3}
    distinct_scores       : 5 (≥2 attendu)
    divergence_ok         : True

§ 5 · AUDIT HORS-3RF (BLOCK_OUTSIDE_3RF)
  tiles_hors_3rf_cumul : 462
  status               : EFFICACE
  note                 : Les 462 tuiles existantes sont des résidus pilote P1 ≥ T-3j · aucune nouvelle écriture depuis activation BLOCK_OUTSIDE_3RF=1

§ 6 · VERDICT
  status                                : T+95%_ATTEINT_VALIDÉ
  global_pct                            : 100.11
  all_rf_ge_90pct                       : True
  biological_divergence_ok              : True
  block_outside_3rf_efficace            : True
  manifest_drift_ok                     : True
  overall_pass                          : True
══════════════════════════════════════════════════════════════════════════════

```
