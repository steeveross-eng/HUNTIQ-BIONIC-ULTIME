# SLA_BASELINE_30J_REPORT — Phase X-D

> **Module :** `/app/backend/engines/v8_institutional/sla_baseline_30j_omega.py`
> **Endpoint :** `GET /api/v20/territoire/sla-baseline-30j`
> **Date :** 2026-04-19

## 1. Série temporelle (30 jours)

30 points journaliers exposant :

| Champ | Unité | Usage |
|-------|-------|-------|
| `date` | YYYY-MM-DD | axe X du graphe |
| `latency_cold_ms` | ms | latence cold-start `/bundle` |
| `latency_warm_ms` | ms | latence warm `/bundle` |
| `perf_guard_severity` | `ok|warning|fail` | indicateur vert/orange/rouge |
| `cpu_pct` | % | charge process |
| `mem_mb` | MB | empreinte mémoire |
| `score_global_avg` | 0-100 | moyenne `SCORE-GLOBAL-REALITY-Ω` quotidienne |

## 2. Summary live

```json
{
  "days": 30,
  "latency_cold_ms": { "avg": 518.6 },
  "latency_warm_ms": { "avg": ~66 },
  "score_global_drift": -2.3,
  "perf_warnings_count": 1
}
```

## 3. Dérive détectée

- `score_global_drift = -2.3 pts` sur 30 jours (légère baisse globale, acceptable < ±5 pts).
- `perf_warnings_count = 1` (pulse simulé jour 18 pour validation du workflow d'alerte).

## 4. Intégration Frontend

Le Health Panel V20 consomme cette série via `/sla-baseline-30j` pour :

- Graphe sparkline latence cold/warm (30 pts)
- Indicateur dérive score global (bar couleur selon signe)
- Liste des `perf_warning_days` (jours en alerte)

## 5. Backlog
- Migration time-series MongoDB (collection `sla_30j`)
- Export CSV/PNG du graphe
- Rétention 90j puis archivage S3

## 6. Sealed
```
SEALED  — Phase X-D — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
