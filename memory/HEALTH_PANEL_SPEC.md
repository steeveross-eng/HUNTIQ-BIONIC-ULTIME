# HEALTH_PANEL_SPEC — Phase X

> **Composant :** `/app/frontend/src/components/territoire/InstitutionalHealthPanel.jsx`
> **Date :** 2026-04-19

## Rôle

Panneau de santé institutionnelle flottant (admin) affichant en temps réel :

- **GLOBAL STATUS** : conforme, suites SELF-AUDIT OK/total, PERF-GUARD
- **REGISTRY LOCK** : version, engines scellés, SHA-256 registre + Doc Maître
- **GOUVERNANCE** : engines live, sources données, date dernier audit
- **ENGINES** : liste scrollable par pilier

## Endpoints consommés (parallèle)

| Endpoint | Rôle |
|----------|------|
| `GET /api/v20/territoire/gouvernance` | Agrégé gouvernance unifié |
| `GET /api/v20/territoire/engines-catalog` | Catalog live + last_audit |
| `GET /api/v20/territoire/registry-lock` | Registre scellé + hashes |

## Props

| Prop | Type | Défaut | Rôle |
|------|------|--------|------|
| `visible` | bool | `true` | affichage conditionnel |
| `onClose` | fn | `null` | bouton fermeture |

## data-testid exposés

- `institutional-health-panel` (racine)
- `health-panel-status-dot`
- `health-panel-conforme`
- `health-panel-suites`
- `health-panel-perf`
- `health-panel-registry-version`
- `health-panel-engines-locked`
- `health-panel-doc-sha`
- `health-panel-engines-live`
- `health-panel-engines-list`
- `health-panel-close`

## Rendu visuel

- Position fixed top-right (360px), backdrop blur, glass-morphism
- Palette dark institutionnelle (`#0E1117`, `#1f2937`, `#60a5fa`)
- Dot coloré selon statut (vert/orange/rouge)

## Validation
- `test_healthpanel.py` — catalog ≥ 20 engines, sources présentes, registry OK.

## Sealed
```
SEALED  — Phase X — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
