# ENGINE_CLIMAT_FUTUR_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_climat_futur_omega.py`

## Rôle
Projections climatiques **CMIP6 SSP2-4.5** (scenario médian IPCC AR6) pour 2030/2040/2050.

## Données ingérées
- Anomalies T : 2030=+1.5°C, 2040=+2.2°C, 2050=+2.8°C
- Changement précipitations : 2030=+4%, 2040=+7.5%, 2050=+11%
- Réduction jours de neige : 2030=-12%, 2040=-20%, 2050=-28%

Sources : IPCC AR6 Atlas (interactive-atlas.ipcc.ch) + consortium Ouranos QC 2022.

## Formule score (0-100, 100=stable)
```
penalty = T_anomaly_2050 × 20 + snow_reduction_2050_abs × 1.0
score = max(0, 100 - penalty)
```

## Stability levels
- >70: STABLE | 50-70: MODERE | 30-50: PREOCCUPANT | <30: CRITIQUE

## Résultat observé QC
`score=16.0 — CRITIQUE` (T+2.8°C, -28% jours neige → impact massif orignal+dindon)

## Test SELF-AUDIT
`test_climat_futur.py` (22e suite)

## Intégration
- Bundle champ `climat_futur`
- Axe `climate_future_score` dans SCORE-GLOBAL-REALITY (poids 4%)

## Limites
- Scénario unique SSP2-4.5 (SSP5-8.5 en backlog)
- Grille AR6 ~100 km, pas de downscaling fin
