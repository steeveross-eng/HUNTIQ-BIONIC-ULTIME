# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-14

---

## Stack technique
- Backend: FastAPI (Python) | Frontend: React + Leaflet | DB: MongoDB

---

## Ce qui a ete implemente

### CAMERA-Omega-ULTRA (2026-04-14)
- 21 marques, modeles dynamiques, type obligatoire, popup riche

### AFFUT-IA-Omega-PLUS (2026-04-14)
- Moteur IA affuts: salines 20-100m, 5 refs scientifiques, 4 especes

### SUPRA-REACT-Omega (2026-04-14)
- SUPRA v2 reconnecte: territory_bridge + 9 moteurs

### TERRITOIRE-FULL-RESTORE-Omega (2026-04-14)
- 18 couches actives, 5 especes avec salines, PROTECTED_LAYERS, PRESET

### P1-ENGINE-Omega + SYSTEM-Omega-EXPANSION-V1 (2026-04-14)
- 12 moteurs deployes sous /api/v1/p1/:
  1. OPTIMIZATION_ENGINE-Omega (score multi-couches 0-100)
  2. HEAT-UNIFY-Omega (heatmap IA unifiee)
  3. PREDICT-BEHAVIOR-Omega (prediction comportementale 5 especes)
  4. ECO-DYNAMICS-Omega (dynamique ecologique saisonniere)
  5. TERRAIN-RISK-Omega-PLUS (evaluation risques terrain)
  6. CONSISTENCY-ENGINE-Omega (verification coherence donnees)
  7. SCIENCE-CHECK-Omega (validation 7 refs scientifiques)
  8. SHIELD-Omega-PLUS (protections institutionnelles)
  9. GLOBAL-CERT-Omega (certification globale 8 modules)
  10. CMP-CERT-Omega (compatibilite 7 modules)
  11. TRACE-LOG-Omega (tracabilite + gouvernance)
  12. BRANCH-REALIGN-Omega (alignement branches systeme)
- GUIDE-PRO-Omega: deja deploye (15 endpoints /api/v1/guide-pro)

---

## Backlog

### COMPLET
- [x] Auth Migration D1-D3
- [x] Camera Engine + Brands + Popup
- [x] IA Vision + Cert (12/12)
- [x] MAP-ENGINE-UNIFY + MAP-PERF
- [x] AFFUT-IA-Omega-PLUS
- [x] SUPRA-REACT-Omega
- [x] MAP-FIX (buffer 600m, hydro, eau)
- [x] TERRITOIRE-FULL-RESTORE (18 couches, 5 especes)
- [x] P1-ENGINE-Omega (12 moteurs)
- [x] GUIDE-PRO-Omega (existant)

### P3 — A demarrer apres validation SYSTEM-Omega-EXPANSION-V1
- [ ] CAMERA-SEC-Omega
- [ ] M5 Offline Mode Ultra
- [ ] DEM LIDAR
- [ ] SIEF ecoforesterie
- [ ] MVT tiles
- [ ] LIDAR-FUSION-Omega
- [ ] SIEF-ECO-Omega

## Regles verrouillees
BFS 780m | max_salines=2 | top-N | M1-M5 | T1-T5 | Salines 20-100m

FIN DU DOCUMENT
