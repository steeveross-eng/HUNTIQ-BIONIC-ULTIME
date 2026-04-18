# HUNTIQ V20 — PRD
## FRONTEND-Omega V2 + PERFORMANCE-Omega — TERRITOIRE <1s
**MAJ:** 2026-04-18

## PRINCIPE DIRECTEUR
**PROTOCOLE BCE-4X ULTIME ABSOLU — ZERO FENETRE, ZERO PANNEAU LATERAL ANALYTIQUE, ZERO REACTIVATION AUTOMATIQUE, <1s LOADING**
Tous les contrôles institutionnels = boutons presseurs ON/OFF stricts. Tout rendu backend cache-first TTL 24h.

## PERFORMANCE-Omega (2026-04-18) — TERRITOIRE <1s
### Backend — `/api/v20/territoire/bundle`
- Nouveau router `engines/v8_institutional/v20_performance_bundle.py`
- Cache in-memory LRU TTL 24h (256 entrées max)
- Quantification clef: lat/lon 3 décimales, wind_deg arrondi 15°
- Headers: `Cache-Control: public, max-age=3600, stale-while-revalidate=82800`
- Headers diagnostic: `X-Cache: HIT/MISS`, `X-Cache-Age-Sec`, `X-Compute-Ms`
- Endpoints admin: `/bundle/stats` + `/bundle/purge`
- GZipMiddleware actif (déjà présent, compression 5.7x: 45KB → 7.8KB)

### Frontend — `useMapBundleV8.js`
- Migration endpoint: `/api/v8/institutional/territoire` → `/api/v20/territoire/bundle`
- Cache client TTL: 30s → 24h (aligné avec backend)
- LRU cap: 30 → 64 entrées
- Quantification alignée backend (lat/lon 3dec, wind 15°)

### Frontend — Lazy Load Strict (`BionicLayersV8.jsx`)
- Fix: `enabled=false` décharge immédiatement tous les layers (auparavant freeze visuel)
- Chaque sous-couche (zones/corridors/affuts/salines/hotspots/contam/wind) reste conditionnelle
- `onDataLoaded` fire uniquement quand master ON

### Mesures
- COLD MISS: 2.7s (full V20-INSTITUTIONNEL compute)
- WARM HIT: **127ms moyenne** (5 fetches consécutifs 98-157ms)
- Gzip compression: 45.6KB → 7.9KB (ratio 5.7x)
- Hit ratio mesuré: 63.64% après 11 requêtes

## FRONTEND-Omega V2 (Phase précédente 2026-04-18)
### Boutons presseurs (TerritoireToolbar.jsx)
- 13 PressButton ON/OFF avec halo lumineux
- 0 DropdownMenu, 0 Switch, 1 Popover (fond de carte UNIQUEMENT)
- Ordre: SPLIT | CARTE | ESPECE | WAYPOINTS | LIEUX | **INTEL** | ZONES | CORRIDORS | AFFUTS | SALINES | HOTSPOTS | VENT | CONTAM | CURSEUR | SCORE | ADMIN
- ESPECE = bouton cyclique
- **INTEL** = master institutionnel (ON = rendu V20 complet, OFF = carte nue)

### Purge (MonTerritoireBionicPage.jsx)
- **Supprimé**: IntelligenceDashboard, PhaseAPanelV8, PhaseCPanelV8, NutritionPanel, AmenagementPanel, StandDetailPanel, NutritionPointDetailPanel, BionicZoneDiagnosticPanel, DiagnosticExclusionsPanel, GroupeTab
- **Onglets supprimés**: 'groupe', 'exclusions', 'intelligence'
- **Conservé**: WaypointUnifiedPanel + PlacesSidePanel (opérationnels CRUD)
- **Purgé**: HEARTBEAT 5s → ON/OFF strict

### Câblage (MapContent.jsx)
- BionicLayersV8 reçoit les toggles réels (showSalinesLayer/ContaminationLayer/HeatmapV10/WindFlow/IntelLayer)
- WindFlowLayer conditionné par `showWindFlow && showIntelLayer`
- `enabled={showIntelLayer}` = kill-switch master

## RENDERER V20-INSTITUTIONNEL (BionicLayersV8.jsx)
### Corridors — 4 niveaux stricts
- EXTREME  : #D32F2F 4.2px opacity 0.95
- INTENSE  : #FF9800 3.0px opacity 0.90
- SAISONNIER: #4CAF50 2.4px opacity 0.90
- NORMAL   : #FFFFFF 1.6px opacity 0.85
- Catmull-Rom, smoothFactor=0, ZERO bezier

### Salines / Affûts / Contamination / Hotspots
- Tooltips enrichis (description, corridor, orientation, distance saline)
- Contamination multi-cônes SOURCE=AFFUTS (3 intensités)

## Architecture V20 (backend payload)
- CONTOUR 600m | ZONES 5 | CORRIDORS 27 (4 types) | CONTAMINATION 18
- AFFUTS 6 | SALINES 6 | HOTSPOTS 11
- SECURITE 5/5 | ESI 8/8

## Endpoints
- **PRIMAIRE**: `GET /api/v20/territoire/bundle` (cache 24h, <1s)
- **LEGACY**: `GET /api/v8/institutional/territoire` (compute direct, maintenu pour compat)
- Ops: `GET /api/v20/territoire/bundle/stats` + `POST /api/v20/territoire/bundle/purge`

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Backlog
- P1: Intégration directe LiDAR WCS 1m & WMS IRDA pédologique
- P2 (futur): Vector Tiles MVT pour corridors/zones/contamination si volume >10K entités/tuile
