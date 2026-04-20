# CONTAMINATION_IMPACT_REPORT — Phase X-B

> **Date :** 2026-04-19
> **Protocole :** BCE-4X ULTIME ABSOLU

## 1. Périmètre d'évaluation

Le module `ENGINE-CONTAMINATION-Ω V2` a été activé sur le pipeline
`/api/v20/territoire/bundle` et propage le score de contamination au composite
`SCORE-GLOBAL-REALITY-Ω`.

## 2. Tests comparatifs croisés (3 zones de référence)

| Zone | Lat | Lon | CWD Risk | Distance MDC (km) | Score V2 | Δ SCORE GLOBAL (V2 vs V1) |
|------|-----|-----|----------|-------------------|----------|---------------------------|
| Estrie-Sud (Frelighsburg) | 45.4 | -72.0 | ELEVE | ≈ 0 | 20 | –3.4 pts |
| Outaouais (Gatineau) | 45.5 | -75.7 | FAIBLE | ~300 | ~95 | +1.1 pts |
| Saguenay | 48.4 | -71.1 | TRES-FAIBLE | >400 | 100 | 0 |

## 3. Impact sur les engines dépendants

| Engine | Intégration | Observable |
|--------|-------------|-----------|
| `ENGINE-HABITAT-SUPRA` | Lit `bundle.contamination_v2.cwd_risk` | Pénalisation habitat en zone ELEVE |
| `ENGINE-POPULATION-DYNAMICS-Ω` | Lit `bundle.contamination_v2` | Ajustement mortalité si ELEVE |
| `ENGINE-STRESS-ANTHROPIQUE-Ω` | Lit `bundle.contamination_v2` | Stress sanitaire additionnel |
| `SCORE-GLOBAL-REALITY-Ω` | `contamination_v2.score` écrase `_contam_malus` | Visible via `contamination_v2_applied: true` |

## 4. Recommandations institutionnelles déclenchées

En zone CWD `ELEVE` ou `MODERE` :

- Déclarer toute observation suspecte MFFP 1-877-346-6763
- Interdiction de transport de cervidé intact hors zone MDC
- Surveillance ACTIVE requise sur tous les affûts < 55 km

## 5. Données source

- CWD Alliance Data Dashboard (cwd-info.org)
- MFFP Surveillance MDC Estrie 2024 (3 cas 2024, 11 cumul)
- MFFP Surveillance MDC Montérégie 2024 (5 cas 2024, 18 cumul)

## 6. Sealed
```
SEALED  — Phase X-B — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
