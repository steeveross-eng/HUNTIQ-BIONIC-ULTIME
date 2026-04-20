# HEALTH PANEL — INTÉGRATION SLA 30J (Phase XI-SUPRA-D / Annexe 2)

> **COMMANDANT :** STEEVE-MAX  
> **STATUT :** ✅ CONFORME

## Composant

`/app/frontend/src/components/territoire/InstitutionalHealthPanel.jsx`

## Endpoint consommé

```
GET /api/v20/territoire/sla-baseline-30j
```

Retourne :
```json
{
  "series": [
    { "date": "2026-03-21", "latency_cold_ms": 89, "latency_warm_ms": 32, "score_global_avg": 0.96 },
    ...30 points...
  ],
  "summary": {
    "score_global_drift": 0.012,
    "perf_warnings_count": 2
  }
}
```

## Rendu institutionnel

Trois sparklines SVG empilées dans la section `SLA 30 JOURS` du Health Panel :

| Métrique | Couleur | Unit | `data-testid` |
|----------|---------|------|---------------|
| Latence cold | `#fbbf24` (ambre) | ms | `sla-sparkline-latence-cold` |
| Latence warm | `#60a5fa` (bleu) | ms | `sla-sparkline-latence-warm` |
| Drift score | `#a78bfa` (violet) | — | `sla-sparkline-drift-score` |

Chaque sparkline affiche :
- Label + dernière valeur en haut
- Polyline SVG 260×36 px, stroke 1.4 px
- Min/max en bas

Deux métriques synthétiques suivent :
- `Drift score (30j)` : valeur de dérive cumulée
- `Alertes perf (30j)` : nombre d'alertes perf-guard sur les 30 derniers jours

## Hook React

```js
function useSlaBaseline30j(visible) {
  const [data, setData] = useState(null);
  useEffect(() => {
    if (!visible) return;
    fetch(`${API}/api/v20/territoire/sla-baseline-30j`)
      .then((r) => r.json())
      .then(setData);
  }, [visible]);
  return data;
}
```

## Tests

- Panneau rendu conditionnel (`visible`) — ne fetch pas si fermé
- `data-testid="health-panel-sla30j"` pour validation Playwright
- Fallback "n/a" si la série est vide
