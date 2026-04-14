# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-14

---

## Stack technique
- Backend: FastAPI (Python) | Frontend: React + Leaflet | DB: MongoDB

---

## Ce qui a ete implemente (sessions recentes)

### RUT-RENDER-Omega (2026-04-09)
- Polygones RUT restaures — VALIDE PAR COMMANDANT

### Certifications (2026-04-10)
- K1/K2/CMP/SHIELD/GLOBAL-CERT: 33/33 — 100%

### Phase D1 (2026-04-13)
- 3 endpoints user_engine deprecies + fallback dual-hash pbkdf2->bcrypt
- UserService.js migre vers /api/auth/* — D1_EXEC_REPORT.md

### Phase D2 (2026-04-13)
- 2 endpoints territory cameras deprecies + reference PromptManager.jsx nettoyee
- D2_EXEC_REPORT.md — ZERO regression T1-T5

### Phase D3 (2026-04-13)
- 6 endpoints marketplace+lands deprecies (auth/register, auth/login, owners/login, owners/register, renters/login, renters/register)
- Fallback SHA256->bcrypt dans auth_engine + re-hash automatique
- Frontend HuntMarketplace.jsx et LandsRental.jsx migres vers JWT auth_engine
- Script migration donnees /app/backend/scripts/migrate_d3_users.py
- Routers marketplace + lands enregistres dans server_orchestrator
- D3_EXEC_REPORT.md — 25 tests anti-regression, ZERO regression

### Cloture Phase P2 + Reset Auth (2026-04-14)
- Phase P2 officiellement close: 11 endpoints AUTH-USAGER deprecies
- Reset mot de passe admin@huntiq.com: bcrypt re-hash + 485 sessions invalidees

### CAMERA-Omega-ULTRA (2026-04-14)
#### Section 1 — CAMERA-BRANDS-Omega-FINAL
- 21 marques officielles Canada/USA (Spypoint, Browning, Bushnell, Moultrie, Tactacam Reveal, Stealth Cam, Wildgame Innovations, Cuddeback/CuddeLink, Covert, Reconyx, Exodus, Spartan, Primos, GardePro, Campark, Meidase, CreativeXP, Wosports, GSM Outdoors, Boly/BolyGuard, Autres)
- Modeles par marque (Boly BG310-M..BG960-K30 LTE inclus) + "Autres modeles" — ZERO texte libre
- Type de camera obligatoire: Cellulaire (LTE) / Reguliere
- Backend: CameraManufacturer 21 enum, CameraType enum, brands_config.py, endpoint /api/v1/camera/brands-config
- Frontend: CameraModule.jsx formulaire avec Select dynamique marque->modeles
- Validation: T1-T4 PASS (curl/bash)

#### Section 2 — CAMERA-POPUP-Omega
- CameraMarkersLayer.jsx reecrit: popup riche avec infos camera, GPS copiable, thumbnails photos, filtre espece, historique IA Vision, actions rapides
- Endpoint /api/v1/camera/cameras/{id}/popup-data bundlant camera+events+analyses+species_summary
- Validation: T5-T6 PASS (curl/bash)

#### Section 3 — MAP-PERF-Omega
- GZip middleware ajoute (GZipMiddleware min 500 bytes)
- Cache serveur in-memory avec TTL 5 min
- Endpoint /api/map/preload bundlant cameras+hotspots+trajectories+species
- Cache client sessionStorage (useCameraLayer, mapCache.js)
- Validation: T7 (115ms < 900ms), T8 (117ms cached), T9 (ZERO OSM hardcode dans carte principale), T10 (ZERO regression localisation)

## Backlog priorise
- ZERO perte de donnees

---

### P0 — Complet
- [x] RUT-RENDER-Omega
- [x] Certifications
- [x] Phase D1 (3 endpoints user_engine)
- [x] Phase D2 (2 endpoints territory cameras)

### P1 — Complet
- [x] Phase D3: marketplace+lands (6 endpoints auth deprecated + frontend migre)
- [x] Phase P2 terminee: 11 endpoints AUTH-USAGER deprecies (D1:3 + D2:2 + D3:6)

### P2 — Complet
- [x] Module Cameras (CAM-EXEC-Omega: 6 phases executees 2026-04-14, 12 endpoints, frontend /cameras)
- [x] IA Vision Engine (VIS-A a VIS-F: backend + API + frontend, GPT-4o via Emergent Key, 2026-04-14)
- [x] ALPHA Layer carte (AlphaHotspotsLayer + useAlphaLayer IA, TrajectoriesLayer, integre cartes)
- [x] IA Vision Phase 2 Final (VIS-B clustering, VIS-E notifications 7 types, anomalies avancees, 15 endpoints, 2026-04-14)
- [x] Valeur commerciale ALPHA (H1-H6: scores territoires, indices, anomalies, rapports, AdminTerritoryValue)
- [x] MAP-ENGINE-UNIFY-Omega (unification sources tuiles cartes via localStorage bionic_map_preferences)
- [x] CAMERA-BRANDS-Omega-FINAL (21 marques, modeles par marque, type obligatoire, ZERO texte libre)
- [x] CAMERA-POPUP-Omega (popup riche: infos+photos+IA Vision+actions rapides)
- [x] MAP-PERF-Omega (GZip, cache serveur, preload, cache client)

### P3 — Gele
- [ ] Heatmap IA unifiee (HEAT-UNIFY: fusion zones chaudes + heat IA, modes temporels)
- [ ] Securite cameras (CAMERA-SEC: halo couverture, detection vol/obstruction)
- [ ] M5 Offline Mode Ultra / BSAA-2
- [ ] Integration DEM LIDAR et SIEF ecoforesterie
- [ ] Module optimization_engine (Work1)

## Regles verrouillees
BFS 780m | max_salines=2 | top-N | M1-M5 | T1-T5

## Fichiers cles modifies (CAMERA-Omega-ULTRA)
- /app/backend/modules/camera_engine/v1/brands_config.py (NEW)
- /app/backend/modules/camera_engine/v1/models.py (UPDATED)
- /app/backend/modules/camera_engine/v1/router.py (UPDATED)
- /app/backend/modules/camera_engine/v1/services.py (UPDATED)
- /app/backend/routes/map_perf.py (NEW)
- /app/backend/server_orchestrator.py (UPDATED)
- /app/backend/server.py (UPDATED)
- /app/frontend/src/components/CameraModule.jsx (UPDATED)
- /app/frontend/src/components/territoire/CameraMarkersLayer.jsx (REWRITTEN)
- /app/frontend/src/hooks/useCameraLayer.js (UPDATED)
- /app/frontend/src/utils/mapCache.js (NEW)

FIN DU DOCUMENT
