# ENGINE_QUALITY_DATA_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_qualite_donnees_omega.py`

## Rôle
Audit institutionnel de la **qualité des données** utilisées par tous les engines : complétude, cohérence, fraicheur.

## Formule (score 0-100)
```
score = completeness × 0.40 + coherence × 0.30 + freshness × 0.30
```

### Sous-scores
| Sous-score | Définition | Source |
|---|---|---|
| **completeness** | % critères catalog remplis (≥5 species, ≥3 studies, ≥5 datasets, ≥5 engine_links) | SCIENCE-Ω |
| **coherence** | % datasets avec URL (proxy traçabilité) | SCIENCE-Ω |
| **freshness** | % engines appelés < 1h | Registry live |

### Statut dérivé
- > 80 : **EXCELLENT**
- 60-80 : BON
- 40-60 : MODÉRÉ
- < 40 : FAIBLE

## Résultat observé (2026-04-19)
```
score: 89.4 — status: EXCELLENT
completeness: 100%  (5 species, 5 studies, 9 datasets, 11 links)
coherence: 78%      (7/9 datasets avec URL)
freshness: 93%      (13/14 engines actifs)
```

## Intégration
- Appelé dans `compute_territoire_v10` → bundle champ `quality_data`
- Axe `quality_score` injecté dans `engine_intelligence.compute_intelligence(..., quality_score=...)`
- Aucune modification SCORE GLOBAL pondéré (non-invasif)

## Test SELF-AUDIT
`/app/backend/tests/test_quality_data.py` (18e suite)

## Limites documentées
- Fraîcheur basée sur `last_called_at` (périme au redémarrage pod)
- Cohérence = proxy URL présence (pas de deep-check liens morts)

## Rapport DATA_QUALITY_REPORT.md
Voir `/app/memory/SUPRA_P2_VALIDATION_REPORT.md` qui consolide les 4 engines P2.
