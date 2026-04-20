# SELF_AUDIT_ALERT_SPEC — Phase X-D

> **Module :** `/app/backend/engines/v8_institutional/self_audit_alerts_omega.py`
> **Date :** 2026-04-19

## 1. Canal WebSocket institutionnel

**Endpoint :** `WS /ws/self-audit-alert`

À la connexion, le serveur envoie un message `hello` incluant les 5 dernières
alertes historiques. Les clients sont inscrits dans le pool `_CLIENTS` (liste
protégée par `asyncio.Lock`).

## 2. Endpoints REST complémentaires

| Verb | Endpoint | Rôle |
|------|----------|------|
| POST | `/api/v20/territoire/self-audit-alert/trigger` | Déclenchement manuel admin |
| GET | `/api/v20/territoire/self-audit-alert/last?limit=N` | Historique N dernières alertes |

## 3. Triggers automatiques

`self_audit_omega.run_self_audit()` appelle désormais
`check_and_emit_from_audit(result)` après chaque audit complet.

| Condition | Kind | Severity |
|-----------|------|----------|
| `conforme == False` | `self-audit` | `critical` |
| `perf_guard.severity_max == "warning"` | `perf-guard` | `warning` |
| `perf_guard.severity_max == "fail"` | `perf-guard` | `critical` |
| Registry hash modifié (previous ≠ current) | `registry-lock` | `critical` |

## 4. Payload d'alerte

```json
{
  "kind": "self-audit|perf-guard|registry-lock",
  "severity": "info|warning|critical",
  "message": "texte lisible",
  "details": {...},
  "emitted_at": "2026-04-19T00:00:00.000Z"
}
```

## 5. Fiabilité

- Diffusion **best-effort** : les clients déconnectés sont purgés du pool.
- **Buffer historique** : `deque(maxlen=50)` permet aux clients entrants de
  récupérer les dernières alertes via le `hello`.
- **Fallback** : si la boucle asyncio n'est pas disponible, l'alerte est
  quand même ajoutée à l'historique (persistance RAM).

## 6. Validation

`test_selfaudit_alerts.py` vérifie :

- Audit CONFORME → 0 alerte
- Audit NON-CONFORME → alerte `self-audit`
- `perf_guard=warning` → alerte `perf-guard`
- Hash registry changé → alerte `registry-lock`

```
OK: 3 types d'alertes émis correctement (self-audit/perf-guard/registry-lock)
```

## 7. Sealed
```
SEALED  — Phase X-D — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
