# BIONIC — ENGINES-AUDIT-DESCRIPTIONS-Ω-FINAL
# RAPPORT COMPLET DESCRIPTIF — FORMAT INSTITUTIONNEL
## Date: 2026-04-16 | Émetteur: EMERGENT | Destinataire: Direction Nationale
## AUCUNE MODIFICATION — AUDIT ET DESCRIPTION UNIQUEMENT

---

# SECTION A — ENGINES V8 NATIONAL (8 engines actifs)

---

## A1. SCORE V8 NATIONAL
- **Fichier:** engines/v8_national/router.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/national
- **Domaine:** Score global national, profil biome, profil espèce
- **Description:** Calcule le score V8 national en combinant météo temps réel (Open-Meteo), profil biome provincial, habitat espèce, et exclusions BCE-4X. Score 0-100 avec prédiction (excellent/bon/modéré/faible/exclu).
- **Entrées:** lat, lon, species, month, hour
- **Sorties:** score_v8, prediction, biome, habitat_data, meteo, exclusion_status
- **Sources:** Open-Meteo API (cache 1.5s), referentials.py (statique), exclusion_engine.py
- **Dépendances:** referentials.py, exclusion_engine.py, Open-Meteo
- **Consommateurs:** ScoreV8Badge.jsx, V8IntelPanel, Multi-Engine Phase C
- **Limitations:** Météo en cache (pas streaming temps réel)
- **Conformité:** CONFORME V8
- **Migration:** Natif V8 (pas de V6 équivalent direct)

---

## A2. EXCLUSION ENGINE V8
- **Fichier:** engines/v8_national/exclusion_engine.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/exclusions
- **Domaine:** Exclusions terrain BCE-4X (22 critères)
- **Description:** Évalue 22 critères d'exclusion: zones urbaines, militaires, parcs nationaux, routes majeures, plans d'eau, pentes extrêmes, zones protégées, aéroports, voies ferrées, lignes HT, etc. Retourne INCLUDED/EXCLUDED avec liste des critères déclenchés.
- **Entrées:** lat, lon, species
- **Sorties:** status (INCLUDED/EXCLUDED), triggered_criteria[], total_criteria
- **Sources:** Heuristique géospatiale (distances estimées)
- **Dépendances:** Aucune externe
- **Consommateurs:** map_bundle.py, Score V8, Phase A
- **Limitations:** Heuristique, pas de données cadastrales réelles
- **Conformité:** CONFORME V8
- **Migration:** Remplace exclusion_engine_v6.py et exclusion_engine_v7.py

---

## A3. GOVERNANCE ENGINE
- **Fichier:** engines/v8_national/governance.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/governance
- **Domaine:** Master Switch PREVIEW/PUBLIC
- **Description:** Contrôle l'état de publication du système V8. Modes: LOCKED (défaut) → PREVIEW (admin uniquement) → PUBLIC. Seul admin@huntiq.com peut activer.
- **Entrées:** action (activate/deactivate), credentials admin
- **Sorties:** mode (LOCKED/PREVIEW/PUBLIC), activated_by, timestamp
- **Sources:** MongoDB (users)
- **Dépendances:** auth_engine
- **Consommateurs:** Toolbar PREVIEW badge
- **Limitations:** Un seul admin autorisé
- **Conformité:** CONFORME V8

---

## A4. MAP BUNDLE ENGINE
- **Fichier:** engines/v8_national/map_bundle.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/map/bundle (NO AUTH)
- **Domaine:** Bundle consolidé toutes couches TERRITOIRE
- **Description:** Endpoint unique servant zones terrain-aware (5 types), corridors Bézier (exclusions eau/pente), affûts (vent + corridor bonus), thermal, multi-engine score. Cache 30s. TTFB <5ms.
- **Entrées:** lat, lon, species, month, hour, wind_deg
- **Sorties:** zones[], corridors[], affuts[], thermal{}, multi_engine{}, biome{}, exclusion{}, compute_ms
- **Sources:** Phase B generators, Phase C thermal/multi-engine
- **Dépendances:** phase_b_engines.py, phase_c_engines.py, exclusion_engine.py, referentials.py
- **Consommateurs:** useMapBundleV8.js → BionicLayersV8.jsx
- **Limitations:** Terrain heuristique (sin/cos), pas de DEM réel
- **Conformité:** CONFORME V8

---

## A5. PHASE A ENGINES (Relocalisation + Salines)
- **Fichier:** engines/v8_national/phase_a_engines.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/map/relocalisation, /api/v8/map/salines
- **Domaine:** Intelligence décisionnelle: relocalisation optimale + placement salines
- **Description:** Relocalisation: génère N candidats autour du site, score composite (saline 40% + affût 35% + couvert 15% + bonus), retourne top-3 avec explications 6-12 lignes. Salines: évalue positions optimales (eau 25%, couvert 20%, pente 20%, accessibilité 15%, sécurité 10%, diversité 10%).
- **Entrées:** lat, lon, species, month, wind_deg, radius_m, n_candidates
- **Sorties:** relocalisations[] (top-3, scores, terrain, explications), site_actuel{}, salines[] (scores, detail, terrain, explications)
- **Sources:** _terrain_profile (heuristique), exclusion_engine V8
- **Dépendances:** exclusion_engine.py
- **Consommateurs:** usePhaseAV8.js → PhaseALayerV8.jsx + PhaseAPanelV8.jsx
- **Limitations:** Terrain heuristique
- **Conformité:** CONFORME V8

---

## A6. PHASE B ENGINES (Zones + Corridors + Affûts terrain-aware)
- **Fichier:** engines/v8_national/phase_b_engines.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/map/zones-ta, corridors-ta, affuts-ta
- **Domaine:** Couches géospatiales terrain-aware
- **Description:** Zones: 5 types (alimentation, repos, rut, affûts, eau), 14-20 vertices organiques, scoring terrain par type, exclusion eau/pente. Corridors: Bézier 9 points entre positions procédurales (0.2-1.8km), cost surface simplifié, exclusion eau<20m et pente>35°, intensité variable (5 niveaux). Affûts: positionnés opposé au vent, score terrain + bonus proximité corridor.
- **Entrées:** lat, lon, species, month, hour, wind_deg
- **Sorties:** zones[] (polygon, score, terrain, excluded), corridors[] (path, intensity, type, cost_surface, terrain), affuts[] (lat, lng, quality, score, orientation, terrain)
- **Sources:** _terrain_profile (heuristique), _cost_surface_score, _corridor_intensity
- **Logique interne:** Zones placement par angle 72° autour du waypoint, polygones _organic_polygon (jitter sinusoïdal). Corridors entre paires de points aléatoires, filtrage exclusion, classification par intensité. Affûts à l'intersection zones alimentation/rut/repos et direction vent inversée.
- **Dépendances:** Aucune externe
- **Consommateurs:** map_bundle.py → BionicLayersV8.jsx
- **Limitations:** Terrain heuristique (sin/cos seed), pas de A* pathfinding, pas de DEM réel
- **Conformité:** PARTIELLE — écart A* vs Bézier par rapport à V6
- **Plan migration:** Intégrer corridor_10x.py (A*) si approuvé

---

## A7. PHASE C ENGINES (Thermal + Scenario + Multi-Engine)
- **Fichier:** engines/v8_national/phase_c_engines.py
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/engines/thermal, scenario, multi-score
- **Domaine:** Moteurs avancés (analyse thermique, scénarios what-if, scoring composite)
- **Description:** Thermal: wind chill (formule Env. Canada), confort animal 0-100, shelter canopy, 5 zones thermiques. Scenario: 8 presets (chasse_matin, chasse_soir, rut_peak, canicule, tempête, vent_fort, post_hiver, nuit), compare baseline vs conditions modifiées, verdict FAVORABLE/NEUTRE/DEFAVORABLE. Multi-Engine: composite pondéré terrain 40% + thermal 15% + temporal 10% + saline 15% + affût 10% + zones 10%.
- **Entrées:** lat, lon, species, month, hour, wind_speed, temp_c, scenario_id
- **Sorties:** Thermal: temp, wind_chill, confort, zone_thermique. Scenario: baseline vs scenario, deltas, impact_global, verdict. Multi: composite_score, classification, breakdown.
- **Sources:** Phase A + Phase B engines, heuristique saisonnière (pas Open-Meteo)
- **Dépendances:** phase_a_engines.py, phase_b_engines.py
- **Consommateurs:** PhaseCPanelV8.jsx, map_bundle.py
- **Limitations:** Température heuristique saisonnière (pas Open-Meteo temps réel)
- **Conformité:** CONFORME V8

---

## A8. P1 PIPELINES (LiDAR + IRDA)
- **Fichier:** engines/v8_national/p1_pipelines.py
- **Version:** V8 | **Statut:** STUB | **Router:** /api/v8/p1
- **Domaine:** Données institutionnelles (LiDAR MRNF, pédologie IRDA)
- **Description:** Stubs retournant des données fallback heuristiques en attendant l'accès aux API institutionnelles MRNF (LiDAR hauteur canopée) et IRDA (pédologie Québec).
- **Entrées:** lat, lon, province
- **Sorties:** lidar_data (fallback), pedology_data (fallback)
- **Sources:** FALLBACK heuristique uniquement
- **Consommateurs:** map_bundle.py (optionnel, include_p1=true)
- **Limitations:** AUCUNE DONNÉE RÉELLE — accès gouvernemental requis
- **Conformité:** STUB

---

# SECTION B — ENGINES PRINCIPAUX V6/V7 (actifs)

---

## B1. HUNT ORCHESTRATOR
- **Fichier:** engines/hunt_orchestrator/ (router.py, orchestrator.py, choix_affuts.py, vent_odeurs.py, access_engine.py)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/hunt
- **Domaine:** Recommandation chasse complète (affûts, salines, vent, contamination, accès)
- **Description:** Orchestrateur principal: POST /hunt/orchestrate reçoit position, vent, espèce, saisons et retourne recommandations d'affûts classifiés (optimal/bon/acceptable/a_eviter), zones de contamination olfactive, routes d'accès. Sous-engines: vent_odeurs (modèle dispersion), choix_affuts (sélection multi-critères), access_engine (itinéraires).
- **Entrées:** center_lat/lng, wind_direction/speed, species, feeding_sites[], fixed_blinds[], session
- **Sorties:** recommendations[] (blind classification, score, factors), contamination_zones, access_routes
- **Sources:** Données statiques espèces, heuristique vent
- **Dépendances:** Aucune externe
- **Consommateurs:** StandsMapLayer.jsx (TERRITOIRE)
- **Limitations:** Pas de DEM, pas de données GPS réelles
- **Conformité:** V6 LEGACY — non migré V8
- **Plan migration:** Fonctionnalité partiellement couverte par Phase A (relocalisation)

---

## B2. WEATHER V3
- **Fichier:** engines/weather_v3/ (router.py, wind_model_provider.py)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v3/weather
- **Domaine:** Météo temps réel + score chasse
- **Description:** Fetch Open-Meteo API: température, vent (direction, vitesse, rafales), humidité, pression, UV, visibilité, point de rosée. Calcule score_chasse 0-100 basé sur vent, pression, température. Cache 1.5s.
- **Entrées:** lat, lng
- **Sorties:** temperature, wind (direction, speed, gusts), humidity, pressure, visibility, uv, dew_point, score_chasse, conditions_text
- **Sources:** Open-Meteo API (externe)
- **Dépendances:** Open-Meteo API
- **Consommateurs:** METEO BIONIC panel (TERRITOIRE), Score V8 (via import)
- **Limitations:** Dépendance externe Open-Meteo
- **Conformité:** ACTIF et fonctionnel

---

## B3. NUTRITION INTELLIGENCE
- **Fichier:** engines/nutrition_intelligence/ (x5100-x7000)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/nutrition-intel
- **Domaine:** Scoring minéral, recettes, coûts, produits, fournisseurs
- **Description:** Suite de 12 sous-engines: x5100 (mineral score), x5200 (mineral recommendation), x5300 (order engine), x5500 (energy/protein), x5600 (site guide), x5700 (cost engine), x5800 (recipe engine), x5900 (evidence engine), x6000 (product score), x6010 (product quality), x6011 (market availability), x6012 (regulatory compliance), x6020 (terrain solutions), x6030 (product ecosystem), x7000 (supplier/product engine).
- **Consommateurs:** Shop, Panier, Recommandations produits
- **Conformité:** ACTIF — indépendant de V8 (commerce)

---

## B4. CAMERA ENGINE
- **Fichier:** modules/camera_engine/v1/router.py
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/cameras
- **Domaine:** Gestion caméras de trail
- **Description:** CRUD caméras: création, listing, recherche proximité, mise à jour, suppression, localisation. Gestion marques (brands_config).
- **Entrées:** camera data (brand, model, lat, lng, status), user_id
- **Sorties:** Camera objects (id, brand, location, status, photos)
- **Sources:** MongoDB (cameras collection)
- **Consommateurs:** Page Caméras frontend
- **Conformité:** ACTIF

---

## B5. VISION ENGINE (IA)
- **Fichier:** modules/vision_engine/v1/router.py
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/vision
- **Domaine:** IA Vision — analyse photos caméras trail
- **Description:** Analyse IA de photos: détection espèces, classification, comptage, hotspots IA, trajectoires estimées, statistiques. Endpoints: analyze (single), batch-analyze, hotspots/generate, trajectories/generate.
- **Entrées:** Photo (base64/URL), camera_id, user_id
- **Sorties:** Analyses (species, confidence, count), hotspots[], trajectories[]
- **Sources:** LLM Emergent (GPT Vision)
- **Dépendances:** Emergent LLM Key
- **Consommateurs:** Page Caméras, Intelligence TERRITOIRE
- **Conformité:** ACTIF

---

## B6. BDRE (Bionic Data Reliability Engine)
- **Fichier:** engines/bdre/ (router.py, source_selector.py, quality_scorer.py, etc.)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/bdre
- **Domaine:** Fiabilité données, sélection sources, fallback, qualité, audit
- **Description:** Moteur de fiabilité: sélectionne la meilleure source de données disponible, évalue la qualité, gère les fallbacks, détecte les anomalies, cache les routes institutionnelles, classifie les cours d'eau.
- **Consommateurs:** Pipelines internes
- **Conformité:** ACTIF

---

## B7. AFFUT IA ENGINE
- **Fichier:** modules/affut_ia_engine/v1/ (engine.py, router.py)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/affut-ia
- **Domaine:** Recommandation IA affûts multi-critères
- **Description:** Génère candidats affûts autour du centre, score multi-facteurs (saline_distance, wind_contamination, corridor_proximity, terrain, temporal V7), classification et justification.
- **Entrées:** center_lat/lng, feeding_sites, hotspots, trajectories, wind, species, month
- **Sorties:** affuts[] (lat, lng, score, classification, justification, stand_type)
- **Consommateurs:** StandsMapLayer.jsx
- **Conformité:** V6 LEGACY

---

## B8. SALINE ENGINE (7 sous-engines)
- **Fichier:** modules/saline_engine/engines/
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/saline
- **Domaine:** Analyse complète salines (sol, hydrologie, végétation, nutrition, métabolisme, recommandations)
- **Sous-engines:**
  - soil_composition_engine: Analyse sol par écozone
  - hydrology_leaching_engine: Lessivage minéraux par drainage/pente
  - vegetation_forage_engine: Analyse végétation et fourrage
  - wildlife_nutritional_engine: Besoins nutritionnels par espèce/saison/sexe/âge
  - nutrient_deficiency_engine: Analyse carences et interactions minérales
  - seasonal_metabolism_engine: État métabolique par saison
  - saline_recommendation_engine: Recommandations produits ajustées
- **Consommateurs:** Shop, Fiche saline, Recommandations

---

# SECTION C — BIONIC ENGINE P0 SUB-ENGINES (V6 GOLDEN)

| # | Engine | Description | Statut |
|---|--------|-------------|--------|
| C1 | **SSE** (Satellite-to-Semantic) | Extraction sémantique du terrain: classifie le type de terrain à partir de coordonnées | ACTIF (router) |
| C2 | **OSG** (Organic Shape Generator) | Génération de formes organiques enrichies par SSE | ACTIF (router) |
| C3 | **CME** (Corridor Morphology Engine) | Corridors organiques morphologiquement réalistes | ACTIF (router) |
| C4 | **WSE/WIV** (Wind Scoring + Wind Impact Vector) | Scoring vent + vecteur d'impact pour dispersion olfactive | ACTIF (router) |
| C5 | **VFE** (Visual Fusion Engine) | Fusion couches certifiées SSE+OSG+CME+WSE/WIV | ACTIF (router) |
| C6 | **SSVL** (Species-Specific Visual Logic) | Préférences visuelles comportementales par espèce | ACTIF (router) |
| C7 | **TCVE** (Terrain Calibration Visual Engine) | Calibration terrain + visibilité par espèce | ACTIF (router) |
| C8 | **PME** (Pressure Memory Engine) | Mémoire de pression de chasse par espèce | ACTIF (router) |
| C9 | **BMPE** (Behavioral Micro-Patterns Engine) | Micro-patterns comportementaux par espèce | ACTIF (router) |
| C10 | **TFE** (Thermal Flow Engine) | Gradients thermiques et flux de chaleur par espèce | ACTIF (router) |
| C11 | **zone_engine_core_v2** | Pipeline zones V6: cercles 600m, grille terrain, A* corridors, exclusions OSM | ACTIF (router bionic_p0) |
| C12 | **corridor_10x** | A* pathfinding sur grille de terrain — NON ROUTÉ dans V8 | PRÉSENT NON-ROUTÉ |
| C13 | **hotspot_engine** | Points chauds comportementaux | ACTIF (router) |
| C14 | **exclusion_engine_v6/v7** | Exclusions legacy — remplacées par V8 | PRÉSENT, REMPLACÉ |

---

# SECTION D — SCORING PIPELINE (22 engines)

| # | Engine | Domaine | Statut | Routé |
|---|--------|---------|--------|-------|
| D1 | **alimentation_v1** | Nutrition basique | ACTIF | OUI |
| D2 | **alimentation_v2** | Nutrition avancée + terrain scoring | ACTIF | OUI |
| D3 | **repos_v1** | Zones de repos: grille, multi-espèces | ACTIF | OUI |
| D4 | **corridors_v10** | Corridors V10 + multi-engine | PURGÉ V8 | NON |
| D5 | **attractors_v1** | Points d'attraction écologiques (nourriture, eau, minéraux, reproduction) | NON-ROUTÉ | NON |
| D6 | **behavior_v1** | Comportement animal (fuite, dynamique groupe, territorialité) | NON-ROUTÉ | NON |
| D7 | **ecosystem_v1** | Santé écosystémique (biodiversité, connectivité, intégrité) | NON-ROUTÉ | NON |
| D8 | **habitat_v1** | Qualité habitat (structure, diversité, bordure, connectivité) | NON-ROUTÉ | NON |
| D9 | **hydro_v1** | Hydrographie (proximité, qualité, diversité, saisonnalité eau) | NON-ROUTÉ | NON |
| D10 | **learning_v1** | Apprentissage adaptatif (tendances, fréquentation historique) | NON-ROUTÉ | NON |
| D11 | **multi_species_v1** | Interactions multi-espèces (compétition, cohabitation, prédation) | NON-ROUTÉ | NON |
| D12 | **ndvi_vegetation_v1** | NDVI saisonnier, diversité essences, structure verticale | NON-ROUTÉ | NON |
| D13 | **opportunity_v1** | Opportunités observation (fenêtres optimales, approche, lignes fuite) | NON-ROUTÉ | NON |
| D14 | **pression_v1** | Pression humaine (distance routes/bâtiments, déterministe) | NON-ROUTÉ | NON |
| D15 | **risk_v1** | Risque écologique (prédation, perturbation, mortalité routière) | NON-ROUTÉ | NON |
| D16 | **rsf_engine** | Resource Selection Function: 13 covariables, 11 couches écologiques | NON-ROUTÉ | NON |
| D17 | **scenario_v1** | Scénarios what-if (impact modifications hypothétiques) | NON-ROUTÉ | NON |
| D18 | **simulation_v1** | Simulation Monte Carlo (N itérations déterministes) | NON-ROUTÉ | NON |
| D19 | **temporal_v1** | Patrons temporels (cycles circadiens, migration, reproduction) | NON-ROUTÉ | NON |
| D20 | **thermal_v1** | Confort thermique (ombrage, exposition, élévation, couverture) | NON-ROUTÉ | NON |
| D21 | **trajets_v1** | Trajectoires déplacement (coût, perméabilité, barrières, drainage) | NON-ROUTÉ | NON |
| D22 | **visibility_v1** | Visibilité / bassin visuel (observation, détection, champ vision) | NON-ROUTÉ | NON |

---

# SECTION E — VÉRIFICATION 18 DOMAINES

| # | Domaine | Engine existant | Statut V8 | Données réelles | Écart |
|---|---------|----------------|-----------|-----------------|-------|
| 1 | Score global | V8 router.py | ACTIF | Open-Meteo + heuristique | Fonctionnel |
| 2 | Thermal | Phase C + thermal_v1 | V8 ACTIF (V1 non-routé) | Heuristique saisonnière | Pas Open-Meteo direct |
| 3 | Hydrologie | hydro_v1 + BDRE waterway | NON-ROUTÉ | Heuristique | ABSENT V8 |
| 4 | Pentes/orientation | Phase B _terrain_profile | HEURISTIQUE | sin/cos seed | Pas DEM réel |
| 5 | Structure forestière | Phase B canopy/strate | HEURISTIQUE | sin/cos seed | Pas données réelles |
| 6 | Canopy/LiDAR | p1_pipelines STUB | STUB | AUCUNE | Accès MRNF requis |
| 7 | NDVI/végétation | ndvi_vegetation_v1 | NON-ROUTÉ | AUCUNE en V8 | ABSENT V8 |
| 8 | Pression humaine | pression_v1 + exclusion V8 | PARTIEL | Heuristique distance | V1 non-routé |
| 9 | Corridors réels | Phase B Bézier | SIMPLIFIÉ | Procédural | Pas A* pathfinding |
| 10 | Corridors IA | corridor_10x A* | NON-ROUTÉ | Grille terrain | Pas intégré V8 |
| 11 | Zones écologiques | Phase B zones_ta | ACTIF | Heuristique | Fonctionnel |
| 12 | Scénarios temporels | Phase C scenario | ACTIF | 8 presets | Fonctionnel |
| 13 | Météo temps réel | weather_v3 | ACTIF | Open-Meteo API | Fonctionnel |
| 14 | Exclusions | exclusion_engine V8 | ACTIF | Heuristique 22 critères | Fonctionnel |
| 15 | Heatmaps comportementales | hotspot_engine | V6 ACTIF | Heuristique | Non-migré V8 |
| 16 | Données caméras | camera_engine | V6 ACTIF | MongoDB | Non-migré V8 |
| 17 | Données terrain (pins/traces) | waypoint_engine | V6 ACTIF | MongoDB | Non-migré V8 |
| 18 | Données IA Vision | vision_engine | V6 ACTIF | LLM Emergent | Non-migré V8 |

---

# SECTION F — ANOMALIES ET URGENCES

## Urgences (P0)
1. **corridor_10x.py (A* pathfinding)** — EXISTE dans le code, NON intégré dans V8. Seul écart majeur V6→V8 pour les corridors.
2. **Terrain heuristique** — Phase A/B/C utilisent _terrain_profile basé sur sin/cos/seed. Pas de DEM/SRTM/LiDAR réel.

## Anomalies (P1)
3. **18 scoring pipeline engines NON-ROUTÉS** — Code complet présent mais aucun router actif. Potentiel inexploité.
4. **NDVI engine** — Code présent, non-routé, aucun équivalent V8.
5. **p1_pipelines** — STUB complet, nécessite accès institutionnel MRNF/IRDA.

## Observations (P2)
6. **10 sub-engines Bionic P0 (SSE→TFE)** — Actifs avec routers V6, non intégrés dans pipeline V8.
7. **hunt_orchestrator** — V6 actif, partiellement couvert par Phase A V8.
8. **Phase C Thermal** — Utilise heuristique saisonnière au lieu de weather_v3 (Open-Meteo).

---

# SECTION G — DÉPENDANCES CRITIQUES

| Dépendance | Engines | Type | Risque |
|------------|---------|------|--------|
| Open-Meteo API | weather_v3, Score V8 | EXTERNE | Si down: fallback cache |
| MongoDB | cameras, auth, waypoints, users | INTERNE | CRITIQUE |
| Emergent LLM Key | vision_engine | EXTERNE | Si budget épuisé: blocage IA |
| Terrain heuristique (sin/cos) | Phase A/B/C, map_bundle | INTERNE | FAUX TERRAIN |
| OSM/Overpass | zone_engine_core_v2 | EXTERNE | Cache local existe |
| MRNF/IRDA | p1_pipelines | INSTITUTIONNEL | Accès non obtenu |

---

# SECTION H — PLAN DE CORRECTION PRIORISÉ

| Priorité | Action | Engine concerné | Impact |
|----------|--------|-----------------|--------|
| P0 | Intégrer A* (corridor_10x.py) dans Phase B | phase_b_engines.py | Corridors terrain-aware réels |
| P0 | Connecter weather_v3 (Open-Meteo) à Phase C Thermal | phase_c_engines.py | Température réelle |
| P1 | Router et activer ndvi_vegetation_v1 | scoring_pipeline | Végétation réelle |
| P1 | Router pression_v1 | scoring_pipeline | Pression humaine |
| P1 | Router hydro_v1 | scoring_pipeline | Hydrologie |
| P1 | Obtenir accès LiDAR MRNF | p1_pipelines | Canopy réelle |
| P2 | Évaluer intégration 10 sub-engines P0 dans V8 | SSE→TFE | Pipeline enrichi |
| P2 | Évaluer intégration RSF engine dans V8 | rsf_engine | Resource Selection Function |
| P3 | Router les 12 engines scoring restants | scoring_pipeline | Couverture complète |

---

**AUCUNE ACTION ENTREPRISE. AUDIT ET DESCRIPTION UNIQUEMENT.**
**EN ATTENTE VALIDATION DIRECTION NATIONALE.**

FIN DU RAPPORT — EMERGENT — 2026-04-16
