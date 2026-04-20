# HEALTH PANEL — INTÉGRATION WS ALERTS (Phase XI-SUPRA-D / Annexe 3)

> **COMMANDANT :** STEEVE-MAX  
> **STATUT :** ✅ CONFORME

## Composant

`/app/frontend/src/components/territoire/InstitutionalHealthPanel.jsx`

## Canal WebSocket

```
ws(s)://{REACT_APP_BACKEND_URL}/ws/self-audit-alert
```

L'URL est construite dynamiquement depuis `REACT_APP_BACKEND_URL` :
- `https:` → `wss:`
- `http:` → `ws:`

## Hook React `useSelfAuditAlertWS`

État interne :
- `alerts` : liste des 50 dernières alertes (FIFO)
- `toast` : alerte courante affichée en bannière (clear après 8 s)
- `wsStatus` : `connecting | open | closed | error`
- `audioRef` : référence audio beacon WAV (data-URI)

Connexion résiliente :
- Sur `onclose` → `setTimeout(connect, 5000)` → reconnexion auto toutes les 5 s
- Sur message `hello` avec `last_alerts[]` → hydrate l'historique

## Format messages WS attendus

```json
{
  "kind": "PERF-GUARD-Ω" | "ESI-Ω" | "SELF-AUDIT-Ω" | ...,
  "severity": "info" | "warning" | "critical",
  "message": "Latency warm p95 > threshold",
  "timestamp": "2026-04-20T15:32:11Z"
}
```

## Rendu

### Toast critique (plein-écran, top-center)

- `data-testid="health-panel-alert-toast"`
- Couleur fond : `#7f1d1d` (critical) / `#78350f` (warning)
- Audio beacon joué automatiquement (`audioRef.current.play()`)
- Affichage 8 s puis disparition auto

### Historique (140px scrollable)

- `data-testid="health-panel-alert-history"`
- Couleurs :
  - `critical` → `#fca5a5`
  - `warning` → `#fcd34d`
  - `info` → `#9ca3af`
- Affiche `[severity] kind: message`

### Statut canal

- `data-testid="health-panel-ws-status"` dans section `GLOBAL STATUS`
- `<StatusDot ok={wsStatus === 'open'} />` + libellé

## Audio beacon

Mini WAV synthétique embarqué en data-URI (250 ms, 440 Hz) pour déclenchement immédiat sans HTTP round-trip.
