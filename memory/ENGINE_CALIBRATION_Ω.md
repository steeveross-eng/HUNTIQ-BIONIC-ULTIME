# ENGINE_CALIBRATION_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_calibration_omega.py`

## Rôle
Calibration **non-invasive** des modèles via observations terrain (caméras, GPS, MVT). MVP expose la couverture de sources active et recommande les ajustements.

## Formule MVP
```
source_score = sources_actives / total_sources × 100
score = source_score × 0.5 + terrain_fiabilite × 0.5
```

## Sorties
| Champ | Type | Description |
|---|---|---|
| `score` | 0-100 | Calibration globale |
| `source_coverage` | % | % sources actives |
| `terrain_fiabilite_pct` | % | Fiabilité terrain |
| `active_sources` | list | Sources actives (lidar, irda, meteo, forest) |
| `absent_sources` | list | Sources manquantes |
| `adjustments_recommended` | list | [{layer, param, suggestion}] |
| `calibration_method` | str | "MVP — source coverage + fiabilite" |

## Résultat observé (QC 46.8139)
```
score: 75.0
source_coverage: 75.0  (3/4 sources actives)
terrain_fiabilite_pct: 100.0
active_sources: [lidar, irda, meteo]
absent_sources: [forest]
adjustments_recommended: []
```

## Logs
Chaque appel produit une entrée dans l'engines catalog (`mark_call`). Les ajustements ne sont **jamais appliqués automatiquement** — ils sont signalés pour audit humain.

## Gaps (CALIBRATION_GAPS.md)
- Pas de feedback loop sur camera observations (caméras Reconyx → GPS collar)
- Pas de comparaison prédiction vs observation (backlog : Kalman filter per engine)
- Pas de calibration Bayésienne (backlog : priors MFFP)
- Pas de feedback chasse (harvest reports MFFP non croisés)

## Test SELF-AUDIT
`/app/backend/tests/test_calibration.py` (20e suite)

## Intégration
- Bundle champ `calibration`
- Pas d'axe INTELLIGENCE (MVP, backlog)
