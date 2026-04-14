# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-14

---

## Stack technique
- Backend: FastAPI (Python) | Frontend: React + Leaflet | DB: MongoDB

---

## Ce qui a ete implemente (sessions recentes)

### RUT-RENDER-Omega (2026-04-09)
- Polygones RUT restaures — VALIDE

### Phase D1-D3 Auth Migration (2026-04-13)
- 11 endpoints AUTH-USAGER deprecies (D1:3 + D2:2 + D3:6)

### CAMERA-Omega-ULTRA (2026-04-14)
- 21 marques officielles, modeles dynamiques, type obligatoire, ZERO texte libre
- Popup riche (infos + photos + IA Vision + actions), endpoint popup-data

### MAP-PERF-Omega (2026-04-14)
- GZip middleware, cache serveur TTL 5min, endpoint preload, cache client sessionStorage

### AFFUT-IA-Omega-PLUS (2026-04-14)
- Moteur IA affuts potentiels integrant: IA Vision + Salines 20-100m + Corridors + Vent + Science BIONIC
- 5 references scientifiques, 4 especes (orignal, cerf, ours noir, caribou), scoring multi-couches 0-100
- Justification IA + biologique + scientifique par affut
- Endpoints: generate, list, explain, references
- Regle biologique saline: <20m=0, 20-40m=max, 40-100m=decroissant, >100m=faible

### MAP-FIX-Omega-V3 (2026-04-14)
- Buffer 600m cameras SUPPRIME des cartes publiques (MON TERRITOIRE, CARTE, Analyse)
- Toggle "Eau" dans toolbar lie a HydrographyOverlayLayer (effectiveShowHydro)
- Opacite hydrographique augmentee 0.25→0.45

### IA-VISION-CERT-Omega (2026-04-14)
- 12/12 endpoints certifies, compatibilite totale avec tous les moteurs
- Rapport: /app/IA_VISION_CERT_REPORT.md

---

## Backlog priorise

### P0 — Complet
- [x] RUT-RENDER-Omega
- [x] Certifications K1/K2/CMP/SHIELD/GLOBAL-CERT
- [x] Phase D1-D3 Auth Migration

### P1 — Complet
- [x] Phase P2 Auth Depreciation (11 endpoints)

### P2 — Complet
- [x] Module Cameras (CAM-EXEC-Omega)
- [x] IA Vision Engine (VIS-A a VIS-F)
- [x] ALPHA Layer + Trajectories carte
- [x] IA Vision Phase 2 (clustering, notifications, anomalies)
- [x] Valeur commerciale ALPHA (Section H)
- [x] MAP-ENGINE-UNIFY-Omega
- [x] CAMERA-BRANDS-Omega-FINAL (21 marques)
- [x] CAMERA-POPUP-Omega (popup riche)
- [x] MAP-PERF-Omega (GZip, cache, preload)
- [x] AFFUT-IA-Omega-PLUS (moteur IA affuts)
- [x] MAP-FIX-Omega-V3 (eau, buffer 600m, hydro precision)
- [x] IA-VISION-CERT-Omega (12/12 certifie)

### P3 — En attente
- [ ] OPTIMIZATION_ENGINE-Omega (moteur centralise ponderation)
- [ ] Heatmap IA unifiee (HEAT-UNIFY)
- [ ] Securite cameras (CAMERA-SEC)
- [ ] M5 Offline Mode Ultra
- [ ] Integration DEM LIDAR et SIEF ecoforesterie
- [ ] MVT Tiles conversion

## Fichiers cles modifies (session courante)
- /app/backend/modules/affut_ia_engine/ (NEW - moteur IA affuts)
- /app/backend/modules/camera_engine/v1/brands_config.py (NEW)
- /app/backend/modules/camera_engine/v1/models.py (UPDATED - CameraType)
- /app/backend/modules/camera_engine/v1/router.py (UPDATED - brands-config, popup-data)
- /app/backend/routes/map_perf.py (NEW - preload + cache)
- /app/backend/server.py (UPDATED - GZip)
- /app/frontend/src/components/CameraModule.jsx (UPDATED)
- /app/frontend/src/components/territoire/CameraMarkersLayer.jsx (REWRITTEN)
- /app/frontend/src/components/territoire/map/MapContent.jsx (UPDATED - hydro opacity)
- /app/frontend/src/hooks/useCameraLayer.js (UPDATED - cache client)
- /app/frontend/src/utils/mapCache.js (NEW)
- /app/frontend/src/pages/MonTerritoireBionicPage.jsx (UPDATED - effectiveShowHydro)
- /app/IA_VISION_CERT_REPORT.md (NEW)

## Regles verrouillees
BFS 780m | max_salines=2 | top-N | M1-M5 | T1-T5 | Salines 20-100m

FIN DU DOCUMENT
