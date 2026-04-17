# HUNTIQ V9 — PRD
## RENDERER V9-PURE VERROUILLE
**MAJ:** 2026-04-17 | **RENDERER V9-PURE** | **ZERO SMOOTHING** | **ZERO BEZIER**

## Architecture V9-INSTITUTIONNEL
- 24 Engines, 4 Piliers, ESI-Omega Guardian
- ENGINE CORRIDORS V9-x20: Catmull-Rom multi-especes
- RENDERER: V9-PURE verrouille

## Phases Completees
- PHASE-1 a PHASE-4Omega: toutes terminees
- ENGINE CORRIDORS V9-x20: SURCLASSE (6 especes, 20 dimensions)
- RENDERER V9-PURE: VERROUILLE

## RENDERER V9-PURE
- smoothFactor: 0 (zones + corridors + contamination)
- ZERO Bezier, ZERO interpolation Leaflet, ZERO fallback
- Corridors: 5 niveaux (Critique #FF0000 → Faible #FFFFFF)
- Fleches directionnelles sur chaque corridor
- Tooltip enrichi: type, intensite, cost, profil espece, connexions zones
- Zones: Catmull-Rom 31 vertices, smoothFactor=0
- Synchronise: VENT, CONTAMINATION, PRESSION, HOTSPOTS, AFFUTS

## Endpoints
- GET /api/v8/institutional/territoire — Source UNIQUE rendering
- GET /api/v3/weather/windgrid — Vent reel
- GET /api/v8/esi/conformite/full — 8/8 CONFORME

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
