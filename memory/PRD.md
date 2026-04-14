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

### Phase D3 (2026-04-13)
- 6 endpoints marketplace+lands deprecies (auth/register, auth/login, owners/login, owners/register, renters/login, renters/register)
- Fallback SHA256→bcrypt dans auth_engine + re-hash automatique
- Frontend HuntMarketplace.jsx et LandsRental.jsx migres vers JWT auth_engine
- Script migration donnees /app/backend/scripts/migrate_d3_users.py
- Routers marketplace + lands enregistres dans server_orchestrator
- D3_EXEC_REPORT.md — 25 tests anti-regression, ZERO regression

### Cloture Phase P2 + Reset Auth (2026-04-14)
- Phase P2 officiellement close: 11 endpoints AUTH-USAGER deprecies
- Reset mot de passe admin@huntiq.com: bcrypt re-hash + 485 sessions invalidees

## Backlog priorise
- ZERO perte de donnees

---

### P0 — Complet
- [x] RUT-RENDER-Omega
- [x] Certifications
- [x] Phase D1 (3 endpoints user_engine)
- [x] Phase D2 (2 endpoints territory cameras)

### P1 — En attente
- [x] Phase D3: marketplace+lands (6 endpoints auth deprecated + frontend migre)
  - D3_EXEC_REPORT.md livre 2026-04-13 — CERTIFIE 15/15

### P1 — Complet (Phase P2 Auth Depreciation)
- [x] Phase P2 terminee: 11 endpoints AUTH-USAGER deprecies (D1:3 + D2:2 + D3:6)

### P2 — Gele
- [ ] M5 Offline Mode Ultra / BSAA-2
- [ ] Integration DEM LIDAR et SIEF ecoforesterie
- [ ] Module optimization_engine (Work1)

## Regles verrouillees
BFS 780m | max_salines=2 | top-N | M1-M5 | T1-T5

FIN DU DOCUMENT
