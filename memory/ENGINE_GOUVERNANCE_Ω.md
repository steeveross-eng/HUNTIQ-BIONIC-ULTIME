# ENGINE_GOUVERNANCE_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_gouvernance_omega.py`

## Rôle
Fusion institutionnelle unifiée : **MONITORING-Ω + ALERTE-ANOMALIES-Ω + SCIENCE-Ω + AUDIT + SLA**. Point d'entrée unique pour la gouvernance opérationnelle de BIONIC OS.

## Endpoint
`GET /api/v20/territoire/gouvernance`

## Structure de réponse
```json
{
  "engine": "ENGINE-GOUVERNANCE-Ω",
  "version": "V1-SUPRA-2026-04",
  "global_status": "ok | warning | fail",
  "pillars": {
    "monitoring": { "engines_count": N, "engines_pillars": {...} },
    "alertes":    { "total": N, "by_severity": {...}, "alerts": [...] },
    "science":    { "summary": {...}, "gaps": [...], "data_sources_count": N },
    "audit":      { "last_ran_at": ..., "conforme": bool, "suites_ok": N, ... },
    "sla":        { "baseline_present": bool, "baseline_timestamp": ... }
  },
  "registry_md_path": "/app/memory/GOVERNANCE_REGISTRY.md"
}
```

## Résultat observé
```
global_status: warning  (pas d'audit récent au démarrage)
engines_pillars: GOUVERNANCE=7, BIO-SYSTEME=9, COMPORTEMENT-HUMAIN=2, SYSTEME-SENSORIEL=1, ENVIRONNEMENT=3
total_engines: 22
```

## Registry GOVERNANCE_REGISTRY.md
Documentation complète des 22 engines SUPRA-Ω, leurs versions, pillars et dépendances. Voir fichier séparé.

## Test SELF-AUDIT
`test_gouvernance.py` (25e suite)

## Panels UX disponibles
- `InstitutionalHealthPanel` (frontend, à intégrer) : brancher sur `/gouvernance` pour vue synthétique carte
- Composants : global_status badge, 4 gauges (quality/uncertainty/calibration/perf), alertes actives

## Intégration
- **Remplace** les endpoints dispersés `/monitoring`, `/alertes`, `/engines-catalog`, `/self-audit/last`
- Les endpoints dispersés restent disponibles (backward-compat)
