# HUNTIQ V8 — PRD
## BCE-4X GOVERNANCE+MAP-LAYERS-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **23/23 PASS** | **100/100**

## Architecture V8
```
TERRITOIRE-V7.2 (MAP-LAYERS ALWAYS_ON + ScoreV8Badge + HEARTBEAT 5s)
V8-NATIONAL (/api/v8/national/* — GOVERNANCE LOCKED defaut)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 22 criteres)
V8-P1 PIPELINES (/api/v8/p1/* — STUB mode)
V8-GOVERNANCE-SUPREMACY (/api/v8/governance/* — Master Switch v8.2.0)
CARTE-2027 (V8 PREVIEW tag)
+ SPATIAL/NUTRITION/INTELLIGENCE/SUPRA/CANADA V7.2
```

## MAP-LAYERS-Omega
- TERRITOIRE_PRESET = ALWAYS_ON
- 14 couches permanentes: habitats, repos, rut, trajets, corridors, ensoleillement, peuplements, affuts, pentes, orientation, altitude, eau, hydro, ndvi
- 5 forced toggles: zones, corridors, points, heatmap, wind
- MAP-LAYER-PERSISTENCE = TRUE
- MAP-LAYER-HEARTBEAT = 5000ms (re-force toutes les 5s)
- ZERO auto-hide, ZERO auto-filter, ZERO dependance score
- Survit: reload, changement espece/province/preset/moteur/governance

## V8-GOVERNANCE-SUPREMACY v8.2.0
- Defaut = LOCKED (POST-PREVIEW LOCKDOWN)
- Authority COMMANDANT_STEEVE_MAX exclusive
- Score V8 = 0 + V8-GOVERNANCE-LOCKED quand LOCKED
- Audit trail MongoDB
- Non-auth = REFUS AUTOMATIQUE

## Fichiers
- /app/frontend/src/hooks/useBionicLayers.js (ALWAYS_ON + HEARTBEAT)
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx (layer heartbeat)
- /app/backend/engines/v8_national/router.py (map_layers status)
- /app/backend/engines/v8_national/governance.py (SUPREMACY v8.2.0)
- /app/backend/engines/v8_national/exclusion_engine.py
- /app/backend/engines/v8_national/p1_pipelines.py
- /app/backend/engines/v8_national/referentials.py

## Taches futures
- P1: Cles WCS + IRDA API reelles
- P2: OSM + ECCC
FIN DU DOCUMENT
