# PRD.md — BIONIC KNOWLEDGE ENGINE / HUNTIQ
## BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX

---

## Enonce du Probleme Original

Application geospatiale de chasse intelligente (HUNTIQ) avec pipeline RSF/SSF, generation de zones/corridors/polygones, selection de salines, et UI cartographique Leaflet. Protocole BCE-4X ULTIME ABSOLU x3 avec gouvernance stricte, zero regression, zero perte.

## Architecture

- **Backend:** FastAPI (Python) — scoring_pipeline (alimentation_v2, corridors_v10, repos_v1, pression_v1)
- **Frontend:** React — Leaflet, BionicCorridorsV6Layer, TerritoireToolbar, NutritionPointsLayer
- **Base de donnees:** MongoDB
- **Branche active:** SUPRA_RECONSTRUCTION

## Ce qui a ete implemente

### Corrections Logiques (FAIT)
- [x] Nutrition Points max 2 strict (triple enforcement Pydantic + engine + salines)
- [x] Selection top-N salines sans exclusion distance (SAL-06/SAL-11 restaurees)
- [x] BFS radius aligne 780m pour couverture 100% hotspots RUT
- [x] Rendu Repos zones via centroide ecologique
- [x] Toggle Affuts connecte au bon toggle UI
- [x] Purge couches inactives (Habitat, Trajet, Multi-Engines)

### Restauration Visuelle (FAIT)
- [x] Suppression casings blancs non autorises
- [x] fillColor transparent, fillOpacity 0
- [x] Ordre de rendu: Zones > Corridors > Points
- [x] Palette normative ZONE_COLORS respectee

### Gouvernance (FAIT — 30+ documents)
- [x] 13 livrables governance generes et verifies
- [x] Suite anti-regression T1-T5 (21/21 PASSES)

### 7 Livrables de Preuve Finale — TRANSMIS INTEGRALEMENT (2026-04-09)
1. GOVERNANCE_VALIDATION_REPORT.md — 13/13 documents avec preuves grep+API par document
2. ABSOLUTE_LOCK_STATUS.md — 13 interdictions, procedure 9 etapes, sanctions
3. CONTINUOUS_MONITORING_PROTOCOL.md — Journalisation, 10 alertes, commandes reproductibles
4. ALERTS_LAST_24H.md — ZERO alerte, traces API T1 complete, traces grep T3-T5
5. MODULARITY_CERTIFICATION_REPORT.md — 5/5 modules avec code source, ponderations, API LIVE
6. BCE4X_REGRESSION_EXECUTION_PROOF.md — 21/21 tests avec commandes, reponses JSON, grep
7. SALINES_SELECTION_FINAL_VALIDATION.md — Algorithme, triple enforcement, 9 etapes E2E

## Backlog Priorise

### P0 — En attente validation Commandant
- [ ] Validation des 7 livrables par le Commandant STEEVE-MAX
- [ ] Lancement certifications K1/K2, CMP, SHIELD, GLOBAL-CERT

### P1 — Apres validation
- [ ] Phase P2: Depreciation 9 endpoints AUTH-USAGER

### P2 — Gele
- [ ] M5 Offline Mode Ultra / BSAA-2
- [ ] Integration donnees DEM LIDAR / SIEF reelles

---
**Derniere mise a jour:** 2026-04-09 13:22 UTC
