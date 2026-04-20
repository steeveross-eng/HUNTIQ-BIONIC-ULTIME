# HEALTH_PANEL_ADMIN_INTEGRATION — Phase X-C

> **Composant :** `/app/frontend/src/components/territoire/InstitutionalHealthPanel.jsx`
> **Hôte :** `/app/frontend/src/pages/AdminPremiumPage.jsx`
> **Date :** 2026-04-19

## 1. Intégration

Le composant `InstitutionalHealthPanel` est désormais monté dans
`AdminPremiumPage` avec un item de navigation dédié :

```jsx
// navItems (section highlight)
{ id: 'health-panel-v20', label: 'Health Panel V20', icon: Activity, highlight: true },

// renderContent switch
case 'health-panel-v20':
  return <InstitutionalHealthPanel visible={true} />;
```

## 2. Accès

Route : `/admin-premium` → item latéral **« Health Panel V20 »**.

## 3. Données affichées (ordre de priorité)

1. **GLOBAL STATUS** : conforme, suites OK/total, PERF-GUARD
2. **REGISTRY LOCK** : version, engines scellés, SHA-256 registre + Doc Maître
3. **GOUVERNANCE** : engines live, sources données, dernier audit
4. **ENGINES** : liste scrollable par pilier avec nom + pilier

## 4. Endpoints consommés (Promise.all)

| Endpoint | Rôle |
|----------|------|
| `GET /api/v20/territoire/gouvernance` | agrégé gouvernance unifié |
| `GET /api/v20/territoire/engines-catalog` | catalog live + last_audit |
| `GET /api/v20/territoire/registry-lock` | registre scellé + hashes |

## 5. Validation automatique

`test_healthpanel_admin.py` :

- Composant `InstitutionalHealthPanel.jsx` existant
- Markers requis présents (`institutional-health-panel`, `registry-lock`, `engines-catalog`, `gouvernance`)
- Import du composant détecté dans au moins un autre fichier (montage confirmé)

```
OK: health panel admin monté (composant + import confirmé)
```

## 6. Extension future

- Ajouter section **CONTAMINATION** affichant le malus propagé (habitat/pop/stress) par zone.
- Ajouter **ALERT TOAST** si `conforme=false`.
- Ajouter **GRAPH HISTORIQUE** sur 30 jours via `SLA-BASELINE-Ω`.

## 7. Sealed
```
SEALED  — Phase X-C — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
