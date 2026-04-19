# ENGINE_PRESSION_ATMOSPHERIQUE_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_pression_atmospherique_omega.py`

## Rôle
Pression atmosphérique (hPa) + tendance 24h + impact comportemental faunique.

## Entrées
- `pressure_hpa` (Open-Meteo `pressure_msl` via meteo bundle)
- `pressure_trend_24h` (optionnel)

## Bands d'activité
| Pression (hPa) | Stability | Score base |
|---|---|---|
| 1010-1020 | STABLE | 80 |
| 1005-1010 / 1020-1025 | TRANSITION | 70 |
| <1005 | BASSE | 55 |
| >1025 | HAUTE | 65 |

## Bonus/Malus tendance
- Trend < -2 hPa/24h → PRE-FRONT : +15 pts (activité accrue avant front)
- Trend > +2 hPa/24h → POST-FRONT : -5 pts
- Sinon : STABLE

## Résultat observé QC
- pressure_hpa=1013.25 (default)
- score=80 (STABLE, activité NORMALE)

## Test SELF-AUDIT
`test_pression_atmospherique.py` (24e suite)

## Intégration
- Bundle champ `pression_atmospherique`
- Axe `pressure_score` dans SCORE-GLOBAL-REALITY (poids 4%)

## Références scientifiques
- Vercauteren et al. 2006 — deer activity & barometric pressure
- Solunar theory atmospheric fluctuations
