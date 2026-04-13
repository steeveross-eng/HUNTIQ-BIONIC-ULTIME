# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-13

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

---

## Backlog priorise

### P0 — Complet
- [x] RUT-RENDER-Omega
- [x] Certifications
- [x] Phase D1 (3 endpoints user_engine)
- [x] Phase D2 (2 endpoints territory cameras)

### P1 — En attente
- [ ] Phase D3: marketplace+lands (4+2 endpoints auth, RISQUE ELEVE, migration frontend obligatoire)
  - D3_PREP_REPORT.md livre 2026-04-13 — En attente validation Commandant pour EXEC-D3

### P2 — Gele
- [ ] M5 Offline Mode Ultra / BSAA-2
- [ ] Integration DEM LIDAR et SIEF ecoforesterie
- [ ] Module optimization_engine (Work1)

## Regles verrouillees
BFS 780m | max_salines=2 | top-N | M1-M5 | T1-T5

FIN DU DOCUMENT
