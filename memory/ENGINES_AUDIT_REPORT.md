# BIONIC — ENGINES-AUDIT-Ω-TOTAL — RAPPORT INSTITUTIONNEL
## Date: 2026-04-16 | Niveau: INSTITUTIONNEL ABSOLU | ZERO MODIFICATION

---

## SYNTHÈSE EXÉCUTIVE

**Inventaire total:** 120+ fichiers engine, 69 routers actifs, 9 purges V8
**Engines V8 (ACTIFS):** 8 engines terrain-aware (Phase A+B+C + Core)
**Engines V6 (ACTIFS):** ~40 routers héritage encore enregistrés
**Engines V6 (PURGÉS):** 6 routers désenregistrés (corridors, zones organiques, relocation, salines)
**Scoring Pipeline:** 22 engines, seulement 4 avec routers actifs (alimentation v1/v2, repos, corridors_v10-purgé)
**Données sources:** ZERO GPS/télémétrie. Procédural + OSM + heuristique.

---

## TABLEAU COMPLET DES ENGINES

### A. V8 NATIONAL (engines/v8_national/) — ACTIF

| Engine | Statut | Description | Sources | Consommateurs |
|--------|--------|-------------|---------|---------------|
| **router.py** (Score V8) | ACTIF | Score National V8, biome, habitat 13 provinces | referentials.py, Open-Meteo (cache) | ScoreV8Badge, V8IntelPanel |
| **exclusion_engine.py** | ACTIF | 22 critères BCE-4X exclusion (urbain/eau/militaire/routes) | Heuristique terrain | Bundle V8, Phase A |
| **governance.py** | ACTIF | Master Switch PREVIEW/PUBLIC, rôle admin | MongoDB (users) | Toolbar PREVIEW badge |
| **map_bundle.py** | ACTIF | Bundle consolidé zones+corridors+affuts+thermal+multi-engine | Phase B + Phase C | BionicLayersV8.jsx |
| **phase_a_engines.py** | ACTIF | Relocalisation (top-3) + Salines (placement optimal) | Terrain heuristique (_terrain_profile) | PhaseALayerV8, PhaseAPanelV8 |
| **phase_b_engines.py** | ACTIF | Zones terrain-aware (5 types) + Corridors Bézier (exclusions eau/pente) + Affûts (vent+corridors) | Terrain heuristique | map_bundle.py |
| **phase_c_engines.py** | ACTIF | Thermal (wind chill/confort) + Scenario (8 presets) + Multi-Engine Scoring | Phase A + Phase B + heuristique saisonnière | PhaseCPanelV8 |
| **p1_pipelines.py** | STUB | LiDAR MRNF + IRDA pédologie (accès institutionnel requis) | Fallback heuristique | map_bundle.py (optionnel) |
| **referentials.py** | ACTIF | Référentiels 13 provinces, biomes, espèces | Données statiques internes | router.py, scoring |

### B. ENGINES PRINCIPAUX (engines/) — ACTIFS

| Engine | Statut | Description | Prefix API |
|--------|--------|-------------|------------|
| **hunt_orchestrator** | ACTIF | Recommandation chasse complète: affûts, salines, vent, accès | /api/v1/hunt |
| **weather_v3** | ACTIF | Météo temps réel (Open-Meteo), vent, score chasse | /api/v3/weather |
| **nutrition_intelligence** | ACTIF | x5100-x7000: scoring minéral, recettes, coûts, produits, fournisseurs | /api/v1/nutrition-intel |
| **supra_advanced** | ACTIF | Pont territoire avancé, analyses SUPRA | /api/v1/supra-advanced |
| **supra_engine_v7** | ACTIF | Engine SUPRA V7, analyses spatiales | /api/v7/supra |
| **spatial_engine_v7** | ACTIF | Analyses spatiales V7, projections | /api/v7/spatial |
| **bdre** | ACTIF | Bionic Data Reliability Engine: source selection, qualité, fallback, hydrologie | /api/v1/bdre |
| **terrain_nav** | NON-ROUTÉ | Navigation terrain: coûts, graphe, routage | Pas de router actif |
| **corridor_unified** | PURGÉ | Corridors V6 unifiés — remplacé par Phase B V8 | /api/v1/corridor-unified → 404 |
| **relocation** | PURGÉ | Relocalisation V6 — remplacée par Phase A V8 | /api/v1/relocation → 404 |

### C. BIONIC ENGINE P0 (modules/bionic_engine_p0/) — PRINCIPAL V6

| Sous-engine | Statut | Description |
|-------------|--------|-------------|
| **zone_engine_core_v2.py** | ACTIF (router) | Pipeline zones organiques V6: cercles 600m, grille terrain, A* corridors, exclusions OSM |
| **corridor_10x.py** | PRÉSENT NON-ROUTÉ | A* pathfinding sur grille de terrain. Non intégré dans V8 |
| **exclusion_engine_v6.py** | PRÉSENT | Exclusions V6: OSM, urbain, eau. Remplacé par exclusion_engine V8 |
| **exclusion_engine_v7.py** | PRÉSENT | Exclusions V7. Remplacé par V8 |
| **engine_osm_lite.py** | PRÉSENT | Enrichissement terrain grille via OSM |
| **hotspot_engine.py** | ACTIF (router) | Points chauds comportementaux |
| **multifactor_scoring_engine.py** | PRÉSENT | Scoring multi-facteur V6 |
| **bmpe_engine.py** | ACTIF | Bionic Movement Pattern Engine |
| **cme_engine.py** | ACTIF | Corridor Movement Engine |
| **osg_engine.py** | ACTIF | Organic Spatial Grid engine |
| **pme_engine.py** | ACTIF | Predictive Movement Engine |
| **sse_engine.py** | ACTIF | Spatial Scoring Engine |
| **ssvl_engine.py** | ACTIF | Spatial Score Validation Layer |
| **tcve_engine.py** | ACTIF | Terrain Cost-Value Engine |
| **tfe_engine.py** | ACTIF | Terrain Feature Engine |
| **vfe_engine.py** | ACTIF | Vegetation Feature Engine |
| **wse_wiv_engine.py** | ACTIF | Weather-Species-Environment Weighted Index |

### D. SCORING PIPELINE (core/scoring_pipeline/) — 22 ENGINES

| Engine | Router | Statut | Domaine |
|--------|--------|--------|---------|
| alimentation_v1 | OUI | ACTIF | Nutrition basique |
| alimentation_v2 | OUI | ACTIF | Nutrition avancée + terrain |
| repos_v1 | OUI | ACTIF | Zones de repos |
| corridors_v10 | OUI | PURGÉ V8 | Corridors V10 — remplacé Phase B |
| attractors_v1 | NON | NON-ROUTÉ | Attracteurs (salines, nourriture) |
| behavior_v1 | NON | NON-ROUTÉ | Comportement animal |
| ecosystem_v1 | NON | NON-ROUTÉ | Écosystème global |
| habitat_v1 | NON | NON-ROUTÉ | Score habitat |
| hydro_v1 | NON | NON-ROUTÉ | Hydrologie |
| learning_v1 | NON | NON-ROUTÉ | Apprentissage adaptatif |
| multi_species_v1 | NON | NON-ROUTÉ | Multi-espèces |
| ndvi_vegetation_v1 | NON | NON-ROUTÉ | NDVI / végétation |
| opportunity_v1 | NON | NON-ROUTÉ | Score opportunité |
| pression_v1 | NON | NON-ROUTÉ | Pression humaine |
| risk_v1 | NON | NON-ROUTÉ | Risque |
| rsf_engine | NON | NON-ROUTÉ | Resource Selection Function |
| scenario_v1 | NON | NON-ROUTÉ | Scénarios V1 (remplacé Phase C) |
| simulation_v1 | NON | NON-ROUTÉ | Simulation |
| temporal_v1 | NON | NON-ROUTÉ | Temporel V1 |
| thermal_v1 | NON | NON-ROUTÉ | Thermal V1 (remplacé Phase C) |
| trajets_v1 | NON | NON-ROUTÉ | Trajets |
| visibility_v1 | NON | NON-ROUTÉ | Visibilité |

### E. MODULES FONCTIONNELS ACTIFS

| Module | Statut | Domaine |
|--------|--------|---------|
| affut_ia_engine | ACTIF | IA affûts recommandation |
| camera_engine | ACTIF | Gestion caméras trail |
| vision_engine | ACTIF | IA Vision (analyse photos) |
| guide_pro_engine | ACTIF | Guide pro recommandations |
| species_engine | ACTIF | Gestion espèces |
| soil_engine | ACTIF | Sol/pédologie |
| saline_engine | ACTIF | Moteurs salines (7 sous-engines) |
| bsaa | ACTIF | Bionic Stand Analytics Advanced |
| canada_v72 | ACTIF | Données Canada 13 provinces |
| carte2027_engine | ACTIF | Carte 2027 |
| ecoforestry_engine | ACTIF | Couches écoforestières |
| wms_engine | ACTIF | Proxy WMS (NFIS, cartes) |
| legal_time_engine | ACTIF | Heures légales chasse |
| solunar | ACTIF | Calendrier solunaire |
| auth_engine | ACTIF | Authentification |
| payment_engine | ACTIF | Paiement Stripe |
| share_engine | ACTIF | Partage |
| messaging_engine | ACTIF | Messagerie |

---

## VÉRIFICATION 18 DOMAINES

| # | Domaine | Engine V8 | Engine V6 | Statut |
|---|---------|-----------|-----------|--------|
| 1 | Score global | router.py (V8 National) | scoring_engine | V8 ACTIF |
| 2 | Thermal | phase_c_engines.py | thermal_v1 (non-routé) | V8 ACTIF |
| 3 | Hydrologie | bdre (waterway_classifier) | hydro_v1 (non-routé) | PARTIEL |
| 4 | Pentes/orientation | phase_b (_terrain_profile) | DEM/SRTM (fallback) | HEURISTIQUE |
| 5 | Structure forestière | phase_b (canopy/strate) | zone_engine_core_v2 | HEURISTIQUE |
| 6 | Canopy/LiDAR | p1_pipelines.py (STUB) | WMS NFIS-QC | STUB (accès requis) |
| 7 | NDVI/végétation | — | ndvi_vegetation_v1 (non-routé) | ABSENT V8 |
| 8 | Pression humaine | exclusion_engine (routes) | pression_v1 (non-routé) | PARTIEL |
| 9 | Corridors réels | phase_b (Bézier) | zone_engine_core_v2 (A* grille) | V8 SIMPLIFIÉ |
| 10 | Corridors IA | — | corridor_10x (A* pathfinding) | ABSENT V8 |
| 11 | Zones écologiques | phase_b (zones_ta 5 types) | zone_engine_core_v2 (cercles) | V8 ACTIF |
| 12 | Scénarios temporels | phase_c (8 presets) | scenario_v1 (non-routé) | V8 ACTIF |
| 13 | Météo temps réel | weather_v3 (Open-Meteo) | weather_engine_v3 | ACTIF |
| 14 | Exclusions | exclusion_engine V8 (22 critères) | exclusion_v6/v7 | V8 ACTIF |
| 15 | Heatmaps comportementales | hotspot_engine | — | V6 ACTIF |
| 16 | Données caméras | camera_engine | — | ACTIF |
| 17 | Données terrain (pins/traces/notes) | waypoint_engine | — | ACTIF |
| 18 | Données IA Vision | vision_engine | — | ACTIF |

---

## ANOMALIES IDENTIFIÉES

### URGENCES
1. **Corridors IA (A*)**: corridor_10x.py EXISTE mais NON INTÉGRÉ dans V8. V8 utilise Bézier simple.
2. **NDVI/Végétation**: ndvi_vegetation_v1 NON-ROUTÉ. Aucun équivalent V8.
3. **LiDAR/Canopy**: p1_pipelines.py = STUB. Nécessite accès institutionnel MRNF.

### ANOMALIES
4. **18 scoring pipeline engines** présents mais NON-ROUTÉS (behavior, ecosystem, habitat, hydro, learning, multi_species, opportunity, pression, risk, RSF, simulation, temporal, thermal_v1, trajets, visibility, attractors, ndvi, scenario_v1).
5. **terrain_nav** engine complet (coûts, graphe, routeur) mais NON-ROUTÉ dans server.py.
6. **Phase B terrain_profile** est HEURISTIQUE (sin/cos/seed) — pas de données DEM/SRTM réelles.
7. **40+ routers V6** encore actifs dans server.py (bionic_p0, hunt_orchestrator, weather_v3, etc.) — certains consommés par le frontend, d'autres potentiellement fantômes.

### ENGINES PRÉSENTS MAIS NON UTILISÉS
- corridor_10x.py (A* pathfinding)
- terrain_nav/ (graphe + coûts terrain)
- 18 scoring pipeline engines sans router
- exclusion_engine_v6.py, exclusion_engine_v7.py (remplacés par V8)

### ENGINES V6 NON RÉINTÉGRÉS DANS V8
- A* pathfinding corridors (corridor_10x.py)
- NDVI/végétation scoring
- Pression humaine complète
- Hydrologie complète
- RSF (Resource Selection Function)
- Comportement animal
- Apprentissage adaptatif

---

## DÉPENDANCES CRITIQUES

| Dépendance | Engines concernés | Risque |
|------------|-------------------|--------|
| Open-Meteo API | weather_v3, phase_c thermal | EXTERNE (si down = fallback) |
| OSM/Overpass | zone_engine_core_v2, exclusions | EXTERNE (cache local existe) |
| MongoDB | auth, waypoints, cameras, users | INTERNE CRITIQUE |
| Terrain heuristique | phase_a, phase_b, phase_c | FAUX TERRAIN (sin/cos pas DEM) |
| MRNF/IRDA | p1_pipelines (STUB) | INSTITUTIONNEL (pas d'accès) |

---

## PLAN DE CORRECTION PRIORISÉ (en attente approbation)

| Priorité | Action | Impact |
|----------|--------|--------|
| P0 | Intégrer A* pathfinding (corridor_10x.py) dans Phase B V8 | Corridors terrain-aware réels |
| P0 | Connecter terrain_nav au graphe de coûts Phase B | Routage terrain réel |
| P1 | Activer NDVI engine dans V8 | Végétation réelle |
| P1 | Connecter SRTM/DEM réel à _terrain_profile | Pente/altitude réelles |
| P1 | Activer pression_v1 dans V8 | Pression humaine complète |
| P2 | Activer hydro_v1 dans V8 | Hydrologie complète |
| P2 | Obtenir accès LiDAR MRNF | Canopy réelle |
| P3 | Évaluer les 18 scoring pipeline engines | Potentiel réintégration |

---

**AUCUNE ACTION ENTREPRISE. AUDIT SEULEMENT. ZERO RISQUE.**
**EN ATTENTE APPROBATION INSTITUTIONNELLE.**

FIN DU RAPPORT
