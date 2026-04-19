# ENGINE_POPULATION_DYNAMICS_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_population_dynamics_omega.py`

## Rôle
Modélisation démographique multi-espèces (5 espèces BCE-4X) : croissance, mortalité, tendances 5/10/20 ans.

## Paramètres (ordre de grandeur littérature)
| Espèce | Natalité | Mortalité | Capacité km² | Tendance 10a | Sensible climat |
|---|---|---|---|---|---|
| Orignal | 0.35 | 0.18 | 0.4 | **-15%** | **oui** |
| Chevreuil | 0.75 | 0.25 | 8.0 | +20% | non |
| Wapiti | 0.50 | 0.20 | 1.5 | +10% | non |
| Ours noir | 0.30 | 0.12 | 0.1 | +5% | non |
| Dindon sauvage | 3.50 | 0.60 | 5.0 | +30% | **oui** |

## Formule score (0-100)
```
r = natalite - mortalite    # taux croissance
growth_score = (r + 0.5) × 100            # r=-0.5→0, 0→50, +0.5→100
trend_score = (tendance_10ans + 0.3) × 166  # -0.3→0, 0→50, +0.3→100
score = growth_score × 0.5 + trend_score × 0.3 + capacite_bonus × 0.2
```

## Projections
Modèle exponentiel simple `N(t) = N0 × (1+r)^t` + variante calibrée sur tendance observée.

## Résultat observé (cerf)
```
score: 84.9
r: 0.50
projections_theoriques (r=0.5):   5ans=7.6×, 10ans=57.7×, 20ans=3325×  (non réaliste sans capacité portante)
projections_observees (tendance): 5ans=1.10×, 10ans=1.22×, 20ans=1.49×  (réaliste MFFP)
```

## Intégration
- Bundle champ `population_dynamics`
- Axe `population_score` injecté dans INTELLIGENCE
- Pas de changement SCORE GLOBAL

## Test SELF-AUDIT
`/app/backend/tests/test_population_dynamics.py` (21e suite)

## Limites documentées
- Paramètres = **ordres de grandeur littérature** (pas de calibration terrain)
- Modèle exponentiel **sans capacité portante dynamique** (logistique = backlog)
- **Prédation + stochasticité** non modélisées
- Les projections théoriques divergent (croissance non bornée) — utiliser les `_observed` pour décision
