# HUNTIQ V8 — PRD
## PHASE-4B TERMINEE — RENDERING V8-INSTITUTIONNEL EXCLUSIF
**MAJ:** 2026-04-17 | **RENDERING CORRIGE** | **FORMES CONFORMES**

## Architecture V8-PURE
- 24 Engines Institutionnels sous /app/backend/engines/v8_institutional/
- 4 Piliers: BIO-SYSTEME, COMPORTEMENT-HUMAIN, SYSTEME-SENSORIEL, PREDICTION-INTELLIGENCE
- ESI-Omega: Guardian Central, 13 lois BCE-4X
- SUPRA V8: 6 modules

## PHASE-1: VERROUILLAGE ULTIME MAX (FAIT)
## PHASE-2: INTEGRATION TERRITOIRE / SUPRA (FAIT)
## PHASE-3: VALIDATION + STABILISATION + SCORE GLOBAL (FAIT)

## PHASE-4B: RENDERING TERRITOIRE V8 (FAIT)
### 1. Purge Immediate
- 100% couches legacy V6/V7 desactivees dans MapContent.jsx
- 100% couches debug desactivees
- 0 fallback, 0 substitution

### 2. Source Unique
- useMapBundleV8 → /api/v8/institutional/territoire (EXCLUSIF)
- ESI-Omega validation sur chaque render
- Zones, Corridors, Affuts, Hotspots, Salines, Vent — tous V8

### 3. Formes Institutionnelles
- Zones: polygones organiques terrain-aware (14-20 vertices, smoothFactor=0)
- Corridors: veines animales angulaires (3-5 segments, ZERO Bezier)
- Affuts: cercle gris #9E9E9E + X central #424242
- Salines: cercle organique #FDD835
- Hotspots: marqueur rouge #E53935

### 4. Corrections Techniques
- Corridors: lineCap butt, lineJoin miter (etait round/round)
- Backend: _bezier_curve remplacee par segments angulaires
- Nouveau endpoint: /api/v8/institutional/territoire
- Fallback Master Switch corrige: LOCKED (etait PREVIEW)

## Endpoints Cles
- GET /api/v8/institutional/full — 24 engines consolidation
- GET /api/v8/institutional/territoire — Source UNIQUE rendering
- GET /api/v8/institutional/pilier/{nom} — Pilier individuel
- GET /api/v8/supra/score-global-interne — 6 composantes mode interne
- GET /api/v8/esi/conformite/full — Validation ESI-Omega
- GET /api/v8/esi/verify-master-switch — Verification Master Switch
- GET /api/v8/governance/state — Etat Master Switch

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
