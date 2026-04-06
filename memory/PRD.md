# PRD — HUNTIQ BIONIC V6 | BCE-4X GOLDEN V6+

## Probleme original
Application de routage terrain pour la chasse avec pathfinding A* et integration OSM/Overpass. Gouvernance stricte BCE-4X GOLDEN V6+.

## Architecture
- Backend: FastAPI + A* Pathfinding + OSM/Overpass
- Frontend: React 19 + Leaflet Maps
- Modules: 84+ engines backend
- Governance: BCE-4X / STEEVE-MAX / ZERO LOSS / ZERO REGRESSION

## Ce qui a ete implemente

### Sessions precedentes
- [x] BCE-4X Territorial Exclusions + Terrain Graph + STEEVE-MAX Guidance
- [x] Multi-engine BDRE integration
- [x] NORME OFFICIELLE A->L Cache Institutionnel
- [x] BUG FIX: Alimentation 3/4 -> 4/4 + Routes V-shape
- [x] DESACTIVATION SECURISEE ACCES AUX AFFUTS
- [x] VALIDATION AUTONOMIE TOTALE (7/7 tests PASS)

### Session 2026-04-06 (fork actuel)

#### P0 — UNIFICATION DES SCORES (SUPRA_SCORE UNIFIE)
- [x] Backend: RecipeRequest accepte lat, lng, saline_score
- [x] Endpoint /supra-panel utilise saline_score comme score_global principal
- [x] Score mineral x5100 conserve comme score_mineral (complementaire)
- [x] score_source: "SUPRA_UNIFIED" confirme le moteur unifie
- [x] Frontend: NutritionPointDetailPanel passe np.score + lat + lng au SUPRA panel
- [x] RESULTAT: Score carte = Score SUPRA = IDENTIQUE (teste: 71=71)

#### P0 — UNIFICATION ERGONOMIQUE (Grille 3 colonnes)
- [x] AnalyseTab restructure en 3 niveaux
- [x] Collapsibles historiques transformes en cards 3 colonnes
- [x] Sources scientifiques en card compacte

#### P0 — MODULE PEDAGOGIQUE
- [x] PedagogieModule.jsx en grille 3 colonnes STANDARD GOLDEN

#### P0 — AUDIT QUALITE
- [x] 10/10 points audites

#### P0 — HARMONISATION DES ONGLETS
- [x] Les 5 onglets utilisent des grilles 3 colonnes

### Session 2026-04-06 (fork 3 — BIONIC_REWRITE_P0)

#### P0 — SECURISATION TOTALE PRE-REFONTE
- [x] Branche BIONIC_STABLE_V6_LOCK + BIONIC_REWRITE_P0
- [x] Manifeste sanctuarisation + Gel operations + Plan technique P0

#### P0-C — IMPLEMENTATION MOTEURS V3/V2
- [x] Moteur SALINES V3 + AFFUTS V2 (seuils institutionnels)

#### P0-I — SHADOW MODE
- [x] shadow_mode.py: V2 sanctuarise en parallele de V3

#### P0-X — SALINES V4 (TERRAIN-CENTRE)
- [x] 9 criteres SUPRA valides scientifiquement (22 sources)
- [x] Triple Shadow V2/V3/V4

#### SUPRA — VALIDATION SCIENTIFIQUE V4
- [x] 8/9 criteres PLEINEMENT VALIDES

### Session 2026-04-06 (fork courant — BLOCS 1/2/3/4)

#### BLOC 1 — CORRIDOR_UNIFIED (VALIDE STEEVE-MAX, IMPLEMENTE, PATCH HYDRO V1.1)
- [x] corridor_model.py: Modele CorridorSegment + classification CRITIQUE/MAJEUR/MINEUR
- [x] corridor_builder.py: Fusion trail_graph OSM + BDRE interne
- [x] router.py: POST /api/v1/corridor-unified/build + GET /status
- [x] 7 attributs: intensite, direction, saisonnalite, espece, largeur, zone_tampon, risque
- [x] PATCH HYDRO V1.1: Masque eau obligatoire (_is_water_at, _distance_eau_at, check_segment_water_exclusion)
- [x] 5 points de controle par segment (0%, 25%, 50%, 75%, 100%)
- [x] Buffer minimum 30m, 3 corridors exclus (sur eau), ZERO regression
- [x] PIPELINE REALIGNE: corridors_v10/engine.py + fallback cost_surface.is_water
- [x] 193 corridors → 103 exclus eau → 90 valides (GeoJSON)
- [x] Teste API: 102 features (90 corridors + 12 zones)

#### BLOC 2 — BDRE PEDAGOGIQUE (INTEGRATION FRONTEND COMPLETE)
- [x] POST /api/v1/hunt/contamination-zones — Backend operationnel
- [x] ContaminationOverlayLayer.jsx CREE — Zones rouges/orange permanentes
- [x] Integre dans MapContent.jsx apres StandsMapLayer
- [x] Couverture 100%: 7/7 zones (1 chasseur + 6 salines)
- [x] Message pedagogique FR avec conseil approche

#### BLOC 3 — RELOCALISATION AUTOMATIQUE (INTEGRATION FRONTEND COMPLETE)
- [x] candidate_generator.py + relocation_engine.py + router.py — Backend operationnel
- [x] StandsMapLayer.jsx ENRICHI — Detection auto affuts a_eviter/rejected
- [x] Marqueur vert pulsant ALT + ligne pointillee + popup justification
- [x] Cas complet: triggered=true, winner composite=52.9, corridor MAJEUR, 240m

#### BLOC 4 — AUDIT COMPLET (LIVRE)
- [x] 4 fiches modules (INTELLIGENCE, TABLEAU DE BORD, SUPRA ANALYSE, SUPRA FICHE)
- [x] 8 doublons identifies (D1-D8): 2 CRITIQUES, 3 HAUTS, 3 FAIBLES
- [x] Schema flux complet + Tableau comparatif
- [x] Matrice RACI + Plan fusion systemique 4 phases (F1→F4)
- [x] Recommandations institutionnelles
- [x] Document: /app/memory/AUDIT_BLOC4_INTELLIGENCE_SUPRA.md

## Backlog

### P0 (En attente validation STEEVE-MAX)
- P0-J: Monitoring shadow V2/V3/V4
- P0-K: Validation finale STEEVE-MAX
- Tests regression V3 -> V4 complets
- Integration frontend BLOC 2 (ContaminationLayer.jsx)
- Integration frontend BLOC 3 (RelocationPanel.jsx)
- Execution plan fusion BLOC 4 (F1→F4)

### P1 (En attente directive STEEVE-MAX)
- Harmonisation x1000%
- Test export PDF

### P2 (GELE)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (INTERDIT)
