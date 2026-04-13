# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-13

---

## Stack technique
- Backend: FastAPI (Python) | Frontend: React + Leaflet | DB: MongoDB
- Architecture: 88 modules metier + 25 core + 16 validateurs BCE

---

## Ce qui a ete implemente (sessions recentes)

### RUT-RENDER-Omega (2026-04-09)
- Polygones RUT restaures (centroide geometrique reel)
- BionicCorridorsV6Layer.jsx (6 lignes) — VALIDE PAR COMMANDANT

### Certifications (2026-04-10)
- BRANCH-REALIGN / VALIDATE / K1/K2/CMP/SHIELD/GLOBAL-CERT: 33/33 — 100%

### Phase P2 Preparation (2026-04-10)
- P2_PREP_REPORT.md genere (9 endpoints, 3 phases, 5 risques)

### Phase D1 Execution (2026-04-13)
- 3 endpoints user_engine deprecies (headers X-Deprecated)
- Fallback dual-hash pbkdf2->bcrypt dans auth_engine
- Frontend UserService.js migre vers /api/auth/*
- ZERO regression (T1-T5 + auth PASS)
- Rapport: D1_EXEC_REPORT.md

---

## Backlog priorise

### P0 — Complet
- [x] RUT-RENDER-Omega
- [x] Certifications K1/K2/CMP/SHIELD/GLOBAL-CERT
- [x] P2 Preparation (rapport)
- [x] Phase D1 (user_engine — 3 endpoints deprecies)

### P1 — En attente validation Commandant
- [ ] Phase D2: Depreciation territory cameras (2 endpoints) — 1 session
- [ ] Phase D3: Depreciation marketplace+lands (4 endpoints) — 2 sessions

### P2 — Gele
- [ ] M5 Offline Mode Ultra / BSAA-2
- [ ] Integration DEM LIDAR et SIEF ecoforesterie reelles
- [ ] Completion module optimization_engine (Work1)

---

## Regles metier verrouillees (IMMUTABLES)
BFS 780m | max_salines=2 | top-N | M1-M5 | ABSOLUTE_LOCK | T1-T5

FIN DU DOCUMENT
