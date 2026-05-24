# AUDIT_DIVERGENCE_BIO_Ω

- **Doctrine**: P22ΩΩ_AUTOPILOT_4D_SAFE_Ω · audit divergence biologique
- **Emitted at**: 2026-05-24T11:35:33.074809+00:00
- **Méthode**: échantillonnage stratifié 1-3 tuiles par (RF × espèce) depuis R2, parsing bundle.score_local, agrégation moyenne par espèce.
- **Critère doctrinal**: distinct ≥ max(2, N_species-1)

## Résultats par RF

| RF | per_species_avg_score | distinct | divergence_ok |
|---|---|---:|---:|
| OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD | `{'chevreuil': 62.8, 'coyote': 62.6, 'dindon_sauvage': 62.6, 'orignal': 59.5, 'ours_noir': 62.4, 'wapiti': 62.0}` | 5 | True |
| MAURICIE_RF_MASTIGOUCHE_ST_MAURICE | `{'chevreuil': 61.5, 'coyote': 61.0, 'dindon_sauvage': 62.3, 'orignal': 59.5, 'ours_noir': 60.9, 'wapiti': 61.5}` | 5 | True |
| LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN | `{'chevreuil': 60.9, 'coyote': 61.0, 'dindon_sauvage': 61.6, 'orignal': 57.9, 'ours_noir': 61.3, 'wapiti': 61.3}` | 5 | True |

## Verdict global

- **Divergence stricte respectée** : True
- **Tous les axes biologiques opérationnels** : ✅
- **Anti-générique strict** : ✅ orignal systématiquement plus bas (cohérent doctrine)
