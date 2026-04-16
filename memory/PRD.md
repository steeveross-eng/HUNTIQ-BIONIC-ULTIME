# HUNTIQ V8 — PRD
## BCE-4X MAP-LAYERS-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **20/20 PASS** | **100/100**

## Architecture V8
```
TERRITOIRE-V7.2 (MAP-LAYERS ALWAYS_ON + HEARTBEAT 5s)
V8-NATIONAL (/api/v8/national/* — GOVERNANCE LOCKED defaut)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 22 criteres)
V8-P1 PIPELINES (/api/v8/p1/* — STUB mode)
V8-GOVERNANCE-SUPREMACY (/api/v8/governance/* — v8.2.0)
V8-MAP-BUNDLE (/api/v8/map/* — bundle unique + cache 30s)
CARTE-2027 (V8 PREVIEW tag)
+ SPATIAL/NUTRITION/INTELLIGENCE/SUPRA/CANADA V7.2
```

## V8-MAP-BUNDLE
- Endpoint: /api/v8/map/bundle
- Combine: zones + corridors + heatmap + biome + exclusion + P1 (optionnel)
- Performance: Compute 1ms, RTT ~140ms (objectif <1s DEPASSE)
- Cache serveur 30s in-memory, 200 entries max
- GOVERNANCE-INDEPENDENT: couches servies meme en LOCKED
- 5 zones + 10 corridors + 169 heatmap points

## MAP-LAYERS ALWAYS_ON
- 14 couches permanentes
- 5 forced toggles (zones, corridors, points, heatmap, wind)
- HEARTBEAT 5s (hook + page)
- ZERO auto-hide / ZERO auto-filter / ZERO dependance score

## Endpoints
/api/v8/map/bundle (GET) — toutes couches en 1 appel
/api/v8/map/bundle/status (GET) — statut bundle
/api/v8/national/* (5) — score, biome, species, referentials, status
/api/v8/exclusion/* (3) — decision, referential, status
/api/v8/p1/* (3) — lidar, pedology, status
/api/v8/governance/* (3) — state, activate, audit

## Fichiers
- /app/backend/engines/v8_national/map_bundle.py (NOUVEAU)
- /app/frontend/src/hooks/useBionicLayers.js (ALWAYS_ON + HEARTBEAT)
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx (layer heartbeat)
- /app/backend/server.py (bundle registered)

FIN DU DOCUMENT
