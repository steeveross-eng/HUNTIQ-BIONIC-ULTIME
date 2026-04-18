# HUNTIQ V20 — PRD
## ENGINE-PERFORMANCE-Ω V11-SUPRA — ACTIVATION TOTALE
**MAJ:** 2026-04-18

## PRINCIPE DIRECTEUR
**PROTOCOLE BCE-4X ULTIME ABSOLU — TERRITOIRE <1s, ZERO FENETRE, ZERO TRIANGLE OPAQUE, ZERO COUCHE FANTOME, MVT SCALABLE 5000+**

## ENGINE-PERFORMANCE-Ω V11-SUPRA (2026-04-18)
### MVT Tiles — `/api/v20/territoire/tiles/{layer}/{z}/{x}/{y}.json`
- Nouveau moteur `engines/v8_institutional/v20_mvt_tiles.py`
- Couches supportées : `corridors`, `zones`, `contamination`
- Zoom : 12-16 (validation 400 hors plage)
- Format : tile-filtered GeoJSON (Leaflet.VectorGrid.slicer compatible)
  - Note architecturale : MVT PBF (mapbox-vector-tile) écarté → conflit protobuf>=6 avec google-ai-generativelanguage. GeoJSON filtré par tile offre identique scalabilité CDN + bandwidth pour notre volumetrie (<10K entités). Voir `DIAGNOSTIC_OMEGA_TRIANGLE_V11.md`.
- Cache LRU mémoire TTL 24h, max 1024 tuiles
- Headers : `Cache-Control: public, max-age=86400, immutable`, `X-Cache HIT/MISS`
- Shared bundle cache (réutilise `v20_performance_bundle._cache`)
- Mesures : MISS 700ms (bundle cached) → WARM **97ms, 2.3KB gzip** sur tile 27 corridors

### CACHE-STATE-Ω overlay (ADMIN uniquement)
- Composant `frontend/src/components/territoire/ui/CacheStateOmega.jsx`
- 60×18px+, halo vert #2E7D32 opacité 0.92, bas-droite
- Texte dynamique : `CACHE HIT XXms` / `COMPUTE XXms`
- Source : `cacheState` + `servedMs` + `computeMs` via `useMapBundleV8`
- Visible uniquement si `adminArchitecteMode === true`
- `data-testid="cache-state-omega"`

### ANTI-LEGACY-Ω — Purge triangle blanc (DIAGNOSTIC-Ω V11)
- **Forme identifiée** : tête de flèche polygone pleine de corridor NORMAL (#FFFFFF, fillOpacity 0.85, taille ~150m)
- **Verdict** : géométrie institutionnelle officielle MAL paramétrée (pas fantôme V7/V8)
- **Correctif** : polygon rempli → polyline chevron stroke-only (`fill: false`), arrowSize 0.0008 → 0.00025
- **Rapport complet** : `/app/memory/DIAGNOSTIC_OMEGA_TRIANGLE_V11.md`

## PERFORMANCE-Ω (Phase précédente)
### Backend — `/api/v20/territoire/bundle`
- Cache LRU TTL 24h (256 entrées, quantification lat/lon 3dec, wind 15°)
- Headers `Cache-Control`, `X-Cache`, `X-Compute-Ms`
- Endpoints ops `/bundle/stats` + `/bundle/purge`
- GZipMiddleware : 45.6KB → 7.9KB (ratio 5.7x)

### Frontend — `useMapBundleV8.js`
- Endpoint V20, cache 24h, LRU 64, quantification alignée backend
- Expose `cacheState`, `servedMs`, `computeMs` pour overlay

### Lazy Load Strict — `BionicLayersV8.jsx`
- Décharge immédiate si `enabled=false` ou `bundleData=null`
- Chaque sous-couche conditionnelle (zones/corridors/affuts/salines/hotspots/contam/wind)

### Mesures Bundle
- COLD MISS : 2.69s
- WARM HIT : **98-157ms** (moyenne 127ms sur 5 requêtes)
- Hit ratio : 63.64%

## FRONTEND-Omega V2 (Phase antérieure)
### Toolbar presseuse
- 13 PressButton ON/OFF, 0 Dropdown, 1 Popover (Carte only)
- INTEL = master institutionnel ON/OFF

### Purge analytique
- Supprimé : IntelligenceDashboard, PhaseA/CPanelV8, NutritionPanel, AmenagementPanel, StandDetailPanel, NutritionPointDetailPanel, BionicZoneDiagnosticPanel, DiagnosticExclusionsPanel, GroupeTab
- HEARTBEAT 5s purgé

## RENDERER V20-INSTITUTIONNEL
### Corridors — 4 niveaux stricts + chevron V11-SUPRA
- EXTREME  : #D32F2F 4.2px opacity 0.95
- INTENSE  : #FF9800 3.0px opacity 0.90
- SAISONNIER: #4CAF50 2.4px opacity 0.90
- NORMAL   : #FFFFFF 1.6px opacity 0.85
- Chevron directionnel stroke-only (arrowSize 0.00025°)
- Catmull-Rom, smoothFactor=0

### Salines / Affûts / Contamination / Hotspots
- Tooltips enrichis, cônes multi-intensité, 5 niveaux hotspots

## Architecture V20 (backend payload)
- CONTOUR 600m | ZONES 5 | CORRIDORS 27 (4 types) | CONTAMINATION 18
- AFFUTS 6 | SALINES 6 | HOTSPOTS 11
- SECURITE 5/5 | ESI 8/8

## Endpoints V20
- `GET /api/v20/territoire/bundle` — bundle complet (cache 24h)
- `GET /api/v20/territoire/bundle/stats` | `POST /bundle/purge`
- `GET /api/v20/territoire/tiles/{corridors|zones|contamination}/{z}/{x}/{y}.json` — MVT-like tile
- `GET /api/v20/territoire/tiles/stats`
- `GET /api/v8/institutional/territoire` — legacy compute direct (compat)

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Backlog
- P1: Intégration directe LiDAR WCS 1m & WMS IRDA pédologique
- P2: Migration MVT PBF natif si upgrade protobuf env possible (actuellement blocking)
- P3: Leaflet.VectorGrid.slicer frontend consommant `/tiles/{layer}/{z}/{x}/{y}.json` pour exclusion totale du JSON bundle sur layers MVT-ready
