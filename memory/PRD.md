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
- POIGraphBuilder : CRUD complet (create, get, update, delete, list, filters)
- POIScorer : Scoring multi-critere (accessibilite, activite, strategique, nutrition)
- POIRelationResolver : Near, clusters, aretes, distances Haversine
- 2 collections MongoDB : poi_nodes (2dsphere), poi_edges
- 14 points de fusion documentes (PF-M1 et PF-N2 actifs)
- ANTI-DOUBLON strict : 5 modules interdits de recreation
- Tests : 40/40 PASS + 58/58 non-regression = 98/98 TOTAL
- Rapport final : /app/memory/M2_RAPPORT_FINAL.md

#### Directive x7000-M3 — M3 Predictive Layer Engine + Time-Series Engine
- Module `predictive_layer_engine` deploye (4 services, 10 endpoints)
- PredictiveLayerComputer : Couches predictives 24h, heatmaps, best-times, prediction GPS
- TimeSeriesCollector : Collecte et stockage series temporelles (4 metriques)
- SeasonalTrendAnalyzer : Tendances saisonnieres multi-annuelles
- MeteoFaunaCorrelator : Matrice de correlation meteo-faune (6 facteurs)
- 3 collections MongoDB : timeseries_data, predictive_layers, seasonal_trends
- 22 points de fusion documentes (14 actifs, 8 prets)
- Formule : P(h) = base(0.25) + season(0.15) + solunar(0.15) + meteo(0.20) + historical(0.15) + nutrition(0.10)
- ANTI-DOUBLON strict : 6 modules interdits de recreation
- Tests : 46/46 PASS + 98/98 non-regression = 144/144 TOTAL
#### Directive x7000-M3-DASHBOARD — Integration Dashboard Intelligence V6
- Data Fusion Layer (DFL) deploye : 8 methodes de fusion, cache TTL 5min
- Event Bus V6 deploye : 13 channels, anti-debounce 500ms
- Data Contracts V6 deployes : 8 contrats stricts
- 8 widgets operationnels : ScoreConsolide, PredictiveLayer, BestTimes, Heatmap, Trends, Correlation, TimeSeries, POIDetail
- Page /intelligence-v6 avec auto-sync (espece/zone/date → refresh tous widgets)
- ZERO modification backend, ZERO modification modules V5
- Rapport final : /app/memory/DASH_RAPPORT_FINAL.md

#### Directive x7100-M4 — M4 Adaptive User Profile + Outdoor Navigation IA
- Module `adaptive_navigation_engine` deploye (4 services, 12 endpoints)
- UserProfileLearner : Profil adaptatif chasseur, apprentissage auto, skill_level, affinites
- NavigationPlanner : Planification itineraires, sessions lifecycle (plan → start → end)
- RouteOptimizer : Re-optimisation multi-critere dynamique (5 facteurs ponderes)
- ContextualAdvisor : Conseils contextuels GPS, suggestions personnalisees
- 2 collections MongoDB : hunter_profiles, navigation_sessions
- 19 points de fusion documentes (SUPRA, Solunaire, Meteo, M1, M2, M3, Chasse, Nutrition)
- Score combine : prediction(0.30) + poi(0.25) + affinity(0.20) + distance(0.15) + legal(0.10)
- ANTI-DOUBLON strict : 5 modules interdits de recreation
- Tests : 31/31 PASS + 144/144 non-regression = 175/175 TOTAL
- Rapport final : /app/memory/M4_RAPPORT_FINAL.md

---

## Backlog priorise

### P0 — Immediat
- [x] M1 deploye (10 endpoints)
- [x] Nutrition V6 Interface (12 endpoints, 13 V5 wraps)
- [x] Synchronisation documentaire (score 98/100)
- [x] Validation STEEVE-MAX x6800-A
- [x] M2: BIONIC POI Graph (11 endpoints, 40/40 tests, 14 points de fusion)
- [x] M3: Predictive Layer + Time-Series (10 endpoints, 46/46 tests, 22 points de fusion)
- [x] DASH: Integration Dashboard Intelligence V6 (8 widgets, DFL, EventBus, DataContracts)
- [x] M4: Adaptive Profile + Navigation IA (12 endpoints, 31/31 tests, 19 points de fusion)

#### Directive x7100-M4 Phase C — Gestionnaire + Hotspots + DataContracts
- Module `gestionnaire_engine` deploye (12 endpoints backend)
- 6 nouveaux DataContracts (DC-09 HunterProfile, DC-10 NavigationSession, DC-11 ContextualAdvice, DC-12 LivePosition, DC-13 SectorStatus, DC-14 EmergencyAlert)
- 6 nouveaux channels EventBus (EB-14→EB-19)
- 7 nouvelles methodes DFL (fetchHunterProfile, fetchNavigationSession, fetchContextualAdvice, fetchSuggestions, emitLivePosition, emitSectorUpdate, emitEmergencyAlert)
- Module Gestionnaire frontend (GestionnairePositionService, GestionnaireSectorService, GestionnairePermissionService, SecoursService)
- Validation geographique hotspots (QC/CA/USA seulement)
- Architecture consentement GPS documentee
- Harmonisation CARTE ↔ MON TERRITOIRE documentee
- Tests : 44/45 PASS + 0 FAIL
- Rapport final : /app/memory/PHASE_C_RAPPORT.md

- [x] Phase D: Widgets M4 (HunterProfileWidget W10, NavigationWidget W11, AdviceWidget W12)
- [x] INTELLIGENCE V6-CORE: 9 widgets (6 M3 + 3 M4), badge M1+M2+M3+M4 FUSION

#### Directive x7200 — UNIFICATION HOTSPOTS ADMIN PREMIUM ET LOGIQUE BIONIC
- [x] Moteur Hotspot V7.2 deploye : scoring terrain-aware, ecologie latitude/habitat, eau embarquee
- [x] Base de donnees eau embarquee : 54 lacs/rivieres QC + 11 zones urbaines
- [x] Contraintes ecologiques : dindon ≤46.8°N, orignal boreal, ours large, chevreuil sud
- [x] Dispersion minimale 1.5km inter-hotspots (0 violations)
- [x] Exclusion eau : 1183 cellules exclues (vs 0 avant)
- [x] Admin Premium = SOURCE DE VERITE avec gradient BIONIC (vert/jaune/orange/rouge)
- [x] Route /admin/hotspots standalone SUPPRIMEE (redirect → /admin-premium)
- [x] Tableau enrichi : ID, Region, Ville, Score, Gradient, Espece, Habitat, Territoire, Acces, Alt, Intensite, GPS
- [x] Metadonnees V7.2 : habitat_type, water_proximity, ecological_coherence, intensity, density_factor, terrain_factors
- [x] BCE-4X PASS : 2100/2100
- [x] Rapport audit : /app/memory/AUDIT_HOTSPOTS_x7200.md
- Fichiers modifies : hotspot_engine.py, water_bodies_qc.py (nouveau), AdminHotspots.jsx, App.js

### P1 — Prochain
- [ ] Phase E: GUIDE PRO (chasse guidee 100%) — DEBLOQUEE par validation x7200
- [ ] Phase F: Module Gestionnaire UI (CARTE tabs + SECOURS button)

### P2 — Futur
- [ ] M5: Offline Mode Ultra + Terrain Intelligence (8 endpoints)
- [ ] BSAA-2, Soil Engine V2
- [ ] Merge Work1 → main (INTERDIT)

---

## Documents canoniques

| Document | Chemin | Version |
|----------|--------|---------|
| PRD | /app/memory/PRD.md | actuel |
| MAP_INTELLIGENCE_PLAN | /app/memory/BIONIC_V6_MAP_INTELLIGENCE_PLAN.md | 1.1.0 |
| M2_POI_GRAPH_PLAN | /app/memory/M2_POI_GRAPH_PLAN.md | 1.0.0 |
| M2_RAPPORT_FINAL | /app/memory/M2_RAPPORT_FINAL.md | 1.0.0 |
| M3_PREDICTIVE_LAYER_PLAN | /app/memory/M3_PREDICTIVE_LAYER_PLAN.md | 1.0.0 |
| M3_RAPPORT_FINAL | /app/memory/M3_RAPPORT_FINAL.md | 1.0.0 |
| M3_DASHBOARD_INTEGRATION_PLAN | /app/memory/M3_DASHBOARD_INTEGRATION_PLAN.md | 1.0.0 |
| DASH_RAPPORT_FINAL | /app/memory/DASH_RAPPORT_FINAL.md | 1.0.0 |
| PHASE_D_RAPPORT | /app/memory/PHASE_D_RAPPORT.md | 1.0.0 |
| PHASE_C_RAPPORT | /app/memory/PHASE_C_RAPPORT.md | 1.0.0 |
| AUDIT_BIONIC_OS_DEDUP | /app/memory/AUDIT_BIONIC_OS_DEDUP.md | 1.0.0 |
| PHASE_A_RAPPORT | /app/memory/PHASE_A_RAPPORT.md | 1.0.0 |
| M4_ADAPTIVE_NAVIGATION_PLAN | /app/memory/M4_ADAPTIVE_NAVIGATION_PLAN.md | 1.0.0 |
| M4_RAPPORT_FINAL | /app/memory/M4_RAPPORT_FINAL.md | 1.0.0 |
| INTERCONNEXION_NUTRITIONNELLE | /app/memory/VALIDATION_INTERCONNEXION_NUTRITIONNELLE_V5_V6.md | 1.0.0 |
| RAPPORT_SYNC_DOC | /app/memory/RAPPORT_SYNCHRONISATION_DOCUMENTAIRE_V6.md | 1.0.0 |
| IMPLEMENTATION_PLAN_V1 | /app/memory/IMPLEMENTATION_PLAN_V1.md | 1.0.0 |
| P5_OPTIMIZATION_PLAN | /app/memory/P5_OPTIMIZATION_PLAN.md | 1.0.0 |
| AUBO_V2 | /app/memory/AUBO_V2.md | 2.0.0 |
| AUDIT_HOTSPOTS_x7200 | /app/memory/AUDIT_HOTSPOTS_x7200.md | 1.0.0 |

---

**Derniere mise a jour** : 2026-04-05 — Directive x7200 COMPLETE (Hotspots V7.2 terrain-aware, Admin Premium SOURCE DE VERITE, gradient BIONIC, ecologie, eau embarquee, dispersion 1.5km)
