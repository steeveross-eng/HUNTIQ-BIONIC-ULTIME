# HUNTIQ V9 — PRD
## PHASE-4Omega TERMINEE — NORMALISATION V9 + VENT REEL VENTUSKY
**MAJ:** 2026-04-17 | **V9-INSTITUTIONNEL** | **VENTUSKY-STEEVE-MAX ACTIF**

## Architecture V9-INSTITUTIONNEL
- 24 Engines, 4 Piliers, ESI-Omega Guardian Central
- Document Maitre: V8-ENGINES-INSTITUTIONNEL-Omega-ULTIME-MAX-2026
- Upgrade V8→V9: Catmull-Rom zones + Vent reel dynamique

## Phases Completees
- PHASE-1: Verrouillage Ultime Max
- PHASE-2: Integration Territoire/Supra
- PHASE-3: Validation + Stabilisation + Score Global
- PHASE-4B: Purge legacy + source unique
- PHASE-4E: Reintroduction tous engines
- PHASE-4Omega: Normalisation visuelle V9 + Vent reel Ventusky

## PHASE-4Omega: Details
### Design System Steeve-Max
- Palette BCE-4X complete (8 couleurs institutionnelles)
- Epaisseurs/opacites standardisees
- Z-order hierarchique strict

### Engines Visuels Normalises
- Zones: Catmull-Rom 31 vertices, courbes douces
- Corridors: Bezier cubique 9pts, #FF8F00, 600m rayon
- Affuts: cercle gris + X, orientation vent
- Contamination: cone 500m #FF7043
- Pression: gradient #EF5350
- Hotspots: intensite 1-5
- Salines: #FDD835

### Vent Reel Dynamique (VENTUSKY-STEEVE-MAX)
- Source: Open-Meteo (ECCC/NOAA GFS-Global)
- Endpoint: /api/v3/weather/windgrid
- Streamlines: 2500 particules Canvas, ~60 FPS
- Interpolation bilineaire spatiale
- Physique: friction foret 55%, Venturi +25%, turbulence ±3deg

### Integration Multi-Engines
- VENT → CONTAMINATION (cone synchronise)
- VENT → AFFUTS (orientation)
- CORRIDORS → ZONES (attraction)

## Endpoints
- GET /api/v8/institutional/territoire — Source UNIQUE rendering
- GET /api/v3/weather/windgrid — Champ vent grille reel
- GET /api/v3/weather/current — Meteo temps reel
- GET /api/v8/esi/conformite/full — 8/8 CONFORME

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
