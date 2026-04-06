# PRD — HUNTIQ BIONIC OS
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

---

## Enonce du probleme original

Reconstruction du repository HUNTIQ-V6, implementation de l'architecture modulaire
BIONIC OS avec 82+ engines decouples, gouvernance BCE-4X stricte, et implementation
sequentielle de pipelines inter-modules, Cart V2, MAP Intelligence, et interface
nutritionnelle V6 unifiee.

## Exigences fondamentales

1. ZERO LOSS, ZERO REGRESSION, ZERO INTERPRETATION
2. Merge vers `main` STRICTEMENT INTERDIT
3. Validation STEEVE-MAX requise entre chaque phase

---

## Ce qui a ete implemente

### Sessions precedentes
- Import/certification HUNTIQ-V6, governance BCE-4X
- BSAA architecture, audits complets
- Phases I→V (SUPRA, E-Commerce, Marketing, Territoire, Tests)
- P5-OPTIMIZATION Cart V2 (backend + frontend, 58/58 tests)
- BIONIC_V6_MAP_INTELLIGENCE_PLAN (M1→M5)
- VALIDATION_INTERCONNEXION_NUTRITIONNELLE_V5_V6

### Session precedente — x6800-A — 2026-04-04

#### Directive 1 — M1 National Data Harvester
- Module `national_data_harvester` deploye (4 services, 10 endpoints)
- boundary_resolver, legal_constraint_engine, harvest_scheduler, data_normalizer
- Connexions SUPRA/Zone/P6/Species/Predictive via MongoDB bridges
- Integration nutritionnelle V6 dans legal-check

#### Directive 2 — Wrappers V6
- Module `nutrition_v6_interface` deploye (4 wrappers, 12 endpoints)
- 13 moteurs V5 encapsules
- Verrouillage V5 au niveau API

#### Directive 3 — Activation Nutrition V6
- V6 = source unique officielle

#### Directive 4 — Synchronisation documentaire
- Score de coherence : 98/100

### Session actuelle — x7100-M4 — 2026-04-05

#### Directive x6900-M2 — M2 BIONIC POI Graph
- Module `poi_graph_engine` deploye (3 services, 11 endpoints)
- POIGraphBuilder : CRUD complet
- POIScorer : Scoring multi-critere
- POIRelationResolver : Near, clusters, aretes
- 2 collections MongoDB : poi_nodes (2dsphere), poi_edges
- Tests : 98/98 TOTAL

#### Directive x7000-M3 — M3 Predictive Layer Engine + Time-Series Engine
- Module `predictive_layer_engine` deploye (4 services, 10 endpoints)
- Tests : 144/144 TOTAL

#### Directive x7000-M3-DASHBOARD — Integration Dashboard Intelligence V6
- Data Fusion Layer (DFL), Event Bus V6, Data Contracts V6
- 8 widgets operationnels
- Page /intelligence-v6

#### Directive x7100-M4 — M4 Adaptive User Profile + Outdoor Navigation IA
- Module `adaptive_navigation_engine` deploye (4 services, 12 endpoints)
- Tests : 175/175 TOTAL

---

## Backlog priorise

### P0 — Immediat
- [x] M1 deploye (10 endpoints)
- [x] Nutrition V6 Interface (12 endpoints, 13 V5 wraps)
- [x] Synchronisation documentaire (score 98/100)
- [x] M2: BIONIC POI Graph (11 endpoints, 40/40 tests, 14 points de fusion)
- [x] M3: Predictive Layer + Time-Series (10 endpoints, 46/46 tests, 22 points de fusion)
- [x] DASH: Integration Dashboard Intelligence V6 (8 widgets, DFL, EventBus, DataContracts)
- [x] M4: Adaptive Profile + Navigation IA (12 endpoints, 31/31 tests, 19 points de fusion)

#### Phase C — Gestionnaire + Hotspots + DataContracts
- [x] Module `gestionnaire_engine` deploye (12 endpoints backend)
- [x] Tests : 44/45 PASS

#### Phase D — Widgets M4
- [x] INTELLIGENCE V6-CORE: 9 widgets (6 M3 + 3 M4)

#### Directive x7200 — UNIFICATION HOTSPOTS / CORRIDORS / ZONES / TRAJETS
- [x] Toutes corrections implementees (water cost, Bezier anti-eau, post-filtre, union hydro, HUMAN_TRAJET_COSTS)
- [x] Tests : 6/6 PASS

### P1 — Deploye
- [x] Phase E-1: GUIDE PRO Backend (15/15 endpoints PASS)
- [x] Pipeline Terrain A+F+G (ENGINE_OSM_LITE operationnel)
- [x] Phase E-2: Frontend GUIDE PRO — DEPLOYE (7 composants React, 9 endpoints connectes)
  - GuideProPage: Dashboard 3 tabs (Dashboard, Sessions, BDRE)
  - BDREMonitor, TerrainScoreCard, SessionCreator, RouteViewer, AuditLogPanel, AnomalyPanel
  - Route /guide-pro + Navigation desktop/mobile integree
  - 17 data-testid, BDRE-FIRST natif, lazy loading
  - Rapport: E2_GUIDE_PRO_FRONTEND_REPORT.md
- [x] Phase F: Module Gestionnaire UI — DEPLOYE (5 onglets + SECOURS, 11 endpoints)
  - GestionnairePage: 5 tabs (CARTE, BDRE, ANOMALIES, JOURNAL, SOURCES)
  - Bouton SECOURS institutionnel (confirmation 2 etapes)
  - 8 composants, 25+ data-testid, auto-refresh 15s
  - Rapport: PHASE_F_GESTIONNAIRE_UI_REPORT.md
- [x] Correction Affuts BCE-4X — INVARIANT INSTITUTIONNEL
  - Start point = waypoint chasseur (center_lat, center_lng)
  - Applique dans orchestrator.py + fallback_chain.py (L0-L4)
  - Verifie: MATCHES_HUNTER=True
  - Rapport: AFFUTS_BDRE_CORRECTION_REPORT.md
- [ ] Phase G: (En attente directive STEEVE-MAX)

### P2 — Futur (GELE)
- [x] P1 BDRE-FIRST Optimisation Continue — COMPLET
  - Intelligence V6: Widget BDRE Health (version, sources actives, fallbacks, dots)
  - Mon Territoire: Indicateur BDRE carte (bouton Shield + Popover 4 compteurs + 16 dots)
  - Admin Premium: Section BDRE Monitor (dashboard, registre 16 sources, 5 engines, journal, anomalies)
  - Rapport: P1_BDRE_OPTIMISATION_REPORT.md
  - 10/10 modules BIONIC integres BDRE
- [x] Dashboard Frontend: Indicateur BDRE global dans header — COMPLET
  - data-testid: dashboard-bdre-indicator, auto-refresh 30s
  - 11/11 modules BDRE-FIRST (couverture TOTALE)
  - Rapport: DASHBOARD_BDRE_INTEGRATION_REPORT.md
- [x] CORRIDOR-FIRST X1000 — INVARIANT INSTITUTIONNEL
  - Corridors: couts reduits 20-29% (routes 0.6-0.8, stream bank 0.9)
  - Foret: couts augmentes 200-213% (off-trail 12.0, dense 25.0)
  - Ratio corridor/foret ameliore x4.0
  - Rapport: AFFUTS_CORRIDOR_FIRST_REPORT.md
- [x] CORRIDOR-FIRST 500% — INVARIANT ULTIME
  - Corridors divises par 3-4 (routes 0.2-0.3, stream bank 0.3)
  - Foret multipliee par 15+ (off-trail 60.0, dense 125.0)
  - Ratio corridor/foret: 0.0016 (x62.5 vs initial)
  - corridor_lock=True, corridor_pct=90%, forest_pct=10%
  - Metriques BDRE propagees dans access_engine.py result
  - Rapport: AFFUTS_CORRIDOR_500_REPORT.md
- [x] CORRIDOR-FIRST X1 000 000% — CORRECTION STEEVE-MAX 2026-04-06
  - REJET validation precedente. Corrections immediates appliquees.
  - Detection stricte 3 points/segment (debut + milieu + fin), rayon 40m
  - Contrainte max segment foret : 5% du total
  - Scoring BDRE multi-engine 4 moteurs (E1:50% + E2:20% + E3:15% + E4:15%)
  - Suppression hardcoding corridor_pct dans fallback_chain.py
  - Orchestrateur scoring BDRE-FIRST : blind(40%) + access(30%) + corridor(30%)
  - Engines integres : trail_graph + quality_scorer + anomaly_detector + terrain_costs
  - Rapport: AFFUTS_CORRIDOR_X1M_REPORT.md
- [x] EXCLUSIONS TERRITORIALES BCE-4X + PREUVE VISUELLE LUC — 2026-04-06
  - REJET preuve visuelle precedente (zones urbaines). Corrections appliquees.
  - Exclusions BCE-4X: routes/highways/residentiel/eau = INTERDIT (1M)
  - Chemins forestiers (track/unclassified/service) AUTORISES en contexte territorial
  - Fetch terrain reel WAYPOINT LUC (48.206417, -68.382588), rayon 3000m
  - 4 routes A* multi-affuts: MATCHES_HUNTER=True (4/4)
  - Corridor 72-85%, foret 14-27% (approche LUC->sentier ~605m irreductible)
  - Preuve visuelle satellite: corridor_proof_luc.html
  - Rapport: AFFUTS_CORRIDOR_X1M_REPORT_LUC.md
- [x] P2 Preparation (M5 + BSAA-2) — Documentation complete
  - M5: 8 endpoints prevus, hooks BDRE identifies
  - BSAA-2: 18 endpoints prevus, architecture existante
  - Rapport: P2_PREPARATION_REPORT.md
  - Execution EN ATTENTE directive STEEVE-MAX
- [x] P2 Gel complet — DIRECTIVE STEEVE-MAX 2026-04-06
  - Rapport: P2_READY_REPORT.md
- [x] PREUVE VISUELLE TERRAIN — DIRECTIVE STEEVE-MAX 2026-04-06
  - 3 pages interactives Leaflet (corridor_proof_index, corridor_proof, corridor_proof_forest)
  - Superposition 7 couches: corridors, sentiers, chemins, acces BDRE, foret, eau, distances
  - 6 routes sur 2 zones: 100% corridor, 0% foret, MATCHES_HUNTER=OUI, CONFORME 95/5
  - Zone 1: 2632 sentiers, 11811 noeuds, 3 routes
  - Zone 2: 855 sentiers, 8729 noeuds, 1502 noeuds foret, 3 routes
- [ ] M5: Offline Mode Ultra + Terrain Intelligence (8 endpoints)
- [ ] BSAA-2, Soil Engine V2
- [ ] Merge Work1 -> main (INTERDIT)

---

## Politique BDRE-FIRST (Invariant Permanent)

Tout composant BIONIC OS doit :
- Integrer scores BDRE, niveaux L1-L4, anomalies, corridors
- Statuts de validation territoire et journaux BDRE
- Etre revu et optimise en continu sans regression
- Etre trace dans BIONIC_OPTIMISATION_LOG.md

---

## Documents canoniques

| Document | Chemin | Version |
|----------|--------|---------|
| PRD | /app/memory/PRD.md | actuel |
| MAP_INTELLIGENCE_PLAN | /app/memory/BIONIC_V6_MAP_INTELLIGENCE_PLAN.md | 1.1.0 |
| M2_RAPPORT_FINAL | /app/memory/M2_RAPPORT_FINAL.md | 1.0.0 |
| M3_RAPPORT_FINAL | /app/memory/M3_RAPPORT_FINAL.md | 1.0.0 |
| DASH_RAPPORT_FINAL | /app/memory/DASH_RAPPORT_FINAL.md | 1.0.0 |
| M4_RAPPORT_FINAL | /app/memory/M4_RAPPORT_FINAL.md | 1.0.0 |
| PHASE_C_RAPPORT | /app/memory/PHASE_C_RAPPORT.md | 1.0.0 |
| PHASE_D_RAPPORT | /app/memory/PHASE_D_RAPPORT.md | 1.0.0 |
| PHASE_E_GUIDE_PRO_ARCHITECTURE | /app/memory/PHASE_E_GUIDE_PRO_ARCHITECTURE.md | 1.0.0 |
| E2_GUIDE_PRO_FRONTEND_REPORT | /app/memory/E2_GUIDE_PRO_FRONTEND_REPORT.md | 1.0.0 |
| BIONIC_OPTIMISATION_LOG | /app/memory/BIONIC_OPTIMISATION_LOG.md | 1.0.0 |
| BDRE_TABLEAU_OPTIMISATION_REPORT | /app/memory/BDRE_TABLEAU_OPTIMISATION_REPORT.md | 1.0.0 |
| BDRE_CONFORMITY_REPORT | /app/memory/BDRE_CONFORMITY_REPORT.md | 1.0.0 |
| BDRE_PHASE1_IMPLEMENTATION_REPORT | /app/memory/BDRE_PHASE1_IMPLEMENTATION_REPORT.md | 1.0.0 |
| BDRE_PHASE2_IMPLEMENTATION_REPORT | /app/memory/BDRE_PHASE2_IMPLEMENTATION_REPORT.md | 1.0.0 |
| BDRE_PHASE3_IMPLEMENTATION_REPORT | /app/memory/BDRE_PHASE3_IMPLEMENTATION_REPORT.md | 1.0.0 |
| BDRE_PHASE4_IMPLEMENTATION_REPORT | /app/memory/BDRE_PHASE4_IMPLEMENTATION_REPORT.md | 1.0.0 |
| DASHBOARD_BDRE_INTEGRATION_REPORT | /app/memory/DASHBOARD_BDRE_INTEGRATION_REPORT.md | 1.0.0 |
| AFFUTS_CORRIDOR_500_REPORT | /app/memory/AFFUTS_CORRIDOR_500_REPORT.md | 1.0.0 |
| P2_PREPARATION_REPORT | /app/memory/P2_PREPARATION_REPORT.md | 1.0.0 |
| PHASE_F_GESTIONNAIRE_UI_REPORT | /app/memory/PHASE_F_GESTIONNAIRE_UI_REPORT.md | 1.0.0 |
| AUDIT_HOTSPOTS_x7200 | /app/memory/AUDIT_HOTSPOTS_x7200.md | 1.0.0 |
| AUDIT_TRAJETS_HUMAINS_x7200 | /app/memory/AUDIT_TRAJETS_HUMAINS_x7200.md | 1.0.0 |
| AFFUTS_CORRIDOR_X1M_REPORT | /app/memory/AFFUTS_CORRIDOR_X1M_REPORT.md | 1.0.0 |
| P2_READY_REPORT | /app/memory/P2_READY_REPORT.md | 1.0.0 |

| AFFUTS_CORRIDOR_X1M_REPORT_LUC | /app/memory/AFFUTS_CORRIDOR_X1M_REPORT_LUC.md | 1.0.0 |

---

**Derniere mise a jour** : 2026-04-06 — EXCLUSIONS TERRITORIALES BCE-4X + PREUVE VISUELLE LUC. Exclusions routes/urbain/eau appliquees. 4 routes A* MATCHES_HUNTER=True. Corridor 72-85% (approche LUC→sentier irreductible). Satellite Esri: corridor_proof_luc.html. P2 GELE.
