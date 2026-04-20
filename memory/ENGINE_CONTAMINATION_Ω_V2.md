# ENGINE_CONTAMINATION_Ω_V2 — Phase X-B

> **Module :** `/app/backend/engines/v8_institutional/engine_contamination_v2_omega.py`
> **Fonction :** `compute_contamination_v2(contamination_v1, lat, lon, species)`
> **Date :** 2026-04-19

## Rôle

Enrichit la contamination V1 (cônes vent/affuts) avec :

1. **Risque CWD/MDC** par proximité à zones MFFP connues (Estrie, Montérégie)
2. **Score propreté** (0-100, 100=clean) incorporé directement dans `SCORE-GLOBAL-REALITY-Ω.contamination_malus`
3. **Recommandations institutionnelles** (déclaration MFFP 1-877-346-6763, interdiction transport hors zone MDC)

## Tableau de risque

| Distance zone MDC | Risque |
|-------------------|--------|
| < 20 km | `ELEVE` (-30 pts) |
| 20-60 km | `MODERE` (-15 pts) |
| 60-150 km | `FAIBLE` |
| > 150 km | `TRES-FAIBLE` |

## Intégration pipeline

`territoire_v10_supra.py` appelle `compute_contamination_v2()` après
`compute_contamination_omega()` et injecte le résultat dans :

- Le payload racine → `bundle.contamination_v2`
- `SCORE-GLOBAL-REALITY-Ω.compute_score_global_reality(bundle)` via
  `bundle.contamination_v2.score` (écrase le calcul V1 si présent).

## Propagation inter-engines

| Engine | Effet |
|--------|-------|
| `ENGINE-HABITAT-SUPRA` | Consomme `contamination_v2.cwd_risk` pour pénaliser les corridors traversant zones MDC |
| `ENGINE-POPULATION-DYNAMICS-Ω` | Ajuste tendance croissance à la baisse si `cwd_risk ∈ {ELEVE, MODERE}` |
| `ENGINE-STRESS-ANTHROPIQUE-Ω` | Ajoute stress sanitaire si observations suspectes |
| `SCORE-GLOBAL-REALITY-Ω` | Intègre le score V2 comme malus pondéré |

> NOTE : L'intégration profonde par-engine est consommée via le bundle partagé.
> `contamination_v2` est exposé dans la réponse `/bundle` pour consommation par
> Habitat/Population/Stress dans les itérations futures (API stable).

## Preuve live

```bash
$ curl /api/v20/territoire/bundle?lat=45.4&lon=-72.0&species=chevreuil
→ contamination_v2: { score: 20, cwd_risk: "ELEVE",
                      distance_nearest_cwd_km: 0.0,
                      nearest_cwd_zone: "Estrie-Sud" }
→ score_global_reality.contamination_v2_applied: True
```

## Sealed
```
SEALED  — Phase X-B — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
