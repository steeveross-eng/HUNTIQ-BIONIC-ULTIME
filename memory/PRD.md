# HUNTIQ V6 — PRD (Product Requirements Document)
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Derniere mise a jour:** 2026-04-09

---

## Enonce du probleme original
Reconstruction du repository HUNTIQ-V6 a partir de la branche bionic-v3-dev de HUNTIQ-V5, avec mise en place du protocole de gouvernance BCE-4X ULTIME ABSOLU et implementation progressive de nouvelles fonctionnalites sous controle strict.

## Personas utilisateurs
- **COMMANDANT STEEVE-MAX** — Autorite supreme, validation de tous les changements
- **Agent BCE-4X** — Executant, soumis au protocole ULTIME ABSOLU

## Stack technique
- Backend: FastAPI (Python)
- Frontend: React + Leaflet
- Base de donnees: MongoDB
- Architecture: 84+ modules moteur modulaires

---

## Ce qui a ete implemente

### Session precedente
- Import et certification du projet (ZIP archive)
- Framework de gouvernance (BCE-4X, GOVERNANCE.md, SECURITY_POLICY.md, EMERGENT_PROTOCOL.md)
- Branche Work1 et audits (moteurs, coherence, historique V1-V6)
- Architecture BSAA (Phase BSAA-0 et BSAA-1)
- Restauration auto_optimization.py (en cours)

### Session actuelle (2026-04-09)
- 7 rapports de gouvernance generes et valides avec preuves T1-T5
- BCE4X_RESPONSE_STANDARD.md etabli
- **RUT-RENDER-Omega CORRIGE** — Polygones RUT restaures dans le frontend
  - Cause racine: isInAnalysisRadius utilisait props.center_lat au lieu du centroide geometrique
  - Fix: ringsCentroid(rawRings) + fillOpacity 0.08
  - Fichier: BionicCorridorsV6Layer.jsx (2 blocs, 6 lignes)

---

## Backlog priorise

### P0 — Bloquant
- [x] RUT-RENDER-Omega (COMPLETE 2026-04-09)
- [ ] Validation par COMMANDANT STEEVE-MAX

### P0 — A venir (apres validation RUT)
- [ ] Certifications K1/K2, CMP, SHIELD, GLOBAL-CERT

### P1
- [ ] Phase P2 — Depreciation de 9 endpoints AUTH-USAGER (EN ATTENTE D'ORDRES)

### P2
- [ ] M5 Offline Mode Ultra / BSAA-2 (STRICTEMENT GELE)
- [ ] Integration DEM LIDAR et SIEF ecoforesterie reelles
- [ ] Completion du module optimization_engine (Work1 branch)

---

## Fichiers de reference critiques
- `/app/frontend/src/components/territoire/BionicCorridorsV6Layer.jsx` — Rendu des zones et corridors
- `/app/backend/core/scoring_pipeline/corridors_v10/engine.py` — Moteur de generation BFS
- `/app/BCE4X_RESPONSE_STANDARD.md` — Format de reponse obligatoire
- `/app/RUT_RENDER_OMEGA_VALIDATION_REPORT.md` — Rapport de validation RUT-RENDER-Omega

---

## Regles metier verrouillees (IMMUTABLES)
- BFS rayon: 780m
- max_salines: 2
- Logique top-N
- Architecture modulaire M1-M5

FIN DU DOCUMENT
