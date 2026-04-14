# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-14

---

## Stack technique
- Backend: FastAPI (Python) | Frontend: React + Leaflet | DB: MongoDB

---

## Ce qui a ete implemente (sessions recentes)

### CAMERA-Omega-ULTRA (2026-04-14)
- 21 marques officielles, modeles dynamiques, type obligatoire, ZERO texte libre
- Popup riche (infos + photos + IA Vision + actions), endpoint popup-data

### MAP-PERF-Omega (2026-04-14)
- GZip middleware, cache serveur TTL 5min, endpoint preload, cache client sessionStorage

### AFFUT-IA-Omega-PLUS (2026-04-14)
- Moteur IA affuts: IA Vision + Salines 20-100m + Corridors + Vent + Science BIONIC
- 5 references scientifiques, 4 especes, scoring multi-couches 0-100
- Endpoints: generate, list, explain, references

### MAP-FIX-Omega-V3 (2026-04-14)
- Buffer 600m cameras SUPPRIME des cartes publiques
- Toggle Eau lie a HydrographyOverlayLayer, opacite 0.45

### IA-VISION-CERT-Omega (2026-04-14)
- 12/12 endpoints certifies

### SUPRA-REACT-Omega (2026-04-14)
- SUPRA v2 reactive et reconnecte a TOUTES les sources territoriales IA
- Nouveau bloc territory_ia dans supra-batch: cameras, vision_analyses, hotspots, trajectories, affuts_ia, species_detections
- Territory bridge service: /app/backend/engines/supra_advanced/territory_bridge.py
- Frontend AnalyseTab enrichi: bloc Intelligence Territoire IA (cameras, analyses, hotspots, affuts, especes)
- 9 moteurs actifs: SUPRA + ULTRA + FICHE + SOL + TERRITORY_IA + terrain_relevance + risk_assessment + recommendations + weather_terrain_correlation
- 5/5 tests PASSES

---

## Backlog priorise

### P2 — Complet
- [x] Module Cameras (CAM-EXEC-Omega)
- [x] IA Vision Engine (VIS-A a VIS-F)
- [x] ALPHA Layer + Trajectories carte
- [x] IA Vision Phase 2 Final
- [x] Valeur commerciale ALPHA (Section H)
- [x] MAP-ENGINE-UNIFY-Omega
- [x] CAMERA-BRANDS-Omega-FINAL
- [x] CAMERA-POPUP-Omega
- [x] MAP-PERF-Omega
- [x] AFFUT-IA-Omega-PLUS
- [x] MAP-FIX-Omega-V3
- [x] IA-VISION-CERT-Omega
- [x] SUPRA-REACT-Omega (reconnexion TERRITOIRE + IA Vision + CARTE)

### P3 — En attente
- [ ] OPTIMIZATION_ENGINE-Omega (moteur centralise ponderation)
- [ ] Heatmap IA unifiee (HEAT-UNIFY)
- [ ] Securite cameras (CAMERA-SEC)
- [ ] M5 Offline Mode Ultra
- [ ] Integration DEM LIDAR et SIEF ecoforesterie
- [ ] MVT Tiles conversion

## Fichiers cles modifies (SUPRA-REACT-Omega)
- /app/backend/engines/supra_advanced/territory_bridge.py (NEW)
- /app/backend/engines/nutrition_intelligence/router.py (UPDATED - territory_ia injection)
- /app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx (UPDATED - territoryIa state)
- /app/frontend/src/components/territoire/supra/AnalyseTab.jsx (UPDATED - bloc IA Territoire)
- /app/frontend/src/components/territoire/supra/FicheTab.jsx (UPDATED - territoryIa prop)

## Regles verrouillees
BFS 780m | max_salines=2 | top-N | M1-M5 | T1-T5 | Salines 20-100m

FIN DU DOCUMENT
