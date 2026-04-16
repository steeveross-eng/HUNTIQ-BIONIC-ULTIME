# HUNTIQ V8 — PRD
## BCE-4X UI-V8-FORCE-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **18/18 PASS** | **100/100** | **UI UNIFIEE V8**

## Architecture V8 — UI Unifiee
```
TERRITOIRE (useMapBundleV8 -> BionicLayersV8 + BionicCorridorsV6Layer complementaire)
  -> Score V8 dans header (ScoreV8Badge)
  -> Score V8 dans METEO panel (WeatherPanel.scoreV8)
  -> Zones+Corridors+Heatmap depuis bundle V8
  -> BionicCorridorsV6Layer (enrichi GeoJSON guide pro)
V8-NATIONAL (/api/v8/national/* — GOVERNANCE PREVIEW)
EXCLUSION-ENGINE-V8 (/api/v8/exclusion/* — 22 criteres)
V8-MAP-BUNDLE (/api/v8/map/bundle — source unique couches)
V8-GOVERNANCE (/api/v8/governance/* — v8.2.0)
V8-P1 PIPELINES (/api/v8/p1/* — STUB)
CARTE-2027 (V8 PREVIEW)
```

## Fichiers crees/modifies UI-V8-FORCE
- /app/frontend/src/hooks/useMapBundleV8.js (NOUVEAU — hook bundle V8)
- /app/frontend/src/components/territoire/BionicLayersV8.jsx (NOUVEAU — rendu Leaflet unifie V8)
- /app/frontend/src/components/territoire/map/MapContent.jsx (MODIFIE — BionicLayersV8 ajoute)
- /app/frontend/src/components/territoire/ui/WeatherPanel.jsx (MODIFIE — Score V8 prioritaire)
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx (MODIFIE — hooks V8 + props)

## Safety Protocol
- Score V8 prioritaire dans WeatherPanel (fallback V7 si LOCKED)
- Bundle V8 governance-independent (couches TOUJOURS servies)
- HEARTBEAT 5s maintenu (ALWAYS_ON layers)
- BionicCorridorsV6Layer conserve (rendu GeoJSON guide pro complementaire)

FIN DU DOCUMENT
