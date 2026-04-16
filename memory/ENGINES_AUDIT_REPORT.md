# BIONIC — ENGINES-AUDIT-Ω-ULTIME-MILITARY-COMMAND-V12
# RAPPORT COMPLET DESCRIPTIF — FORMAT INSTITUTIONNEL
## Date: 2026-04-16 | Niveau: MILITAIRE ABSOLU | ZERO MODIFICATION
## Émetteur: EMERGENT | Destinataire: Direction Nationale

---

# MÉTADONNÉES DU SCAN

| Métrique | Valeur |
|----------|--------|
| Fichiers engine scannés | 138 |
| Fichiers router scannés | 114 |
| Routers actifs (server.py) | 60 |
| Routers purgés/commentés | 9 |
| Scoring Pipeline engines | 22 (4 routés, 18 non-routés) |
| Bionic P0 sub-engines | 14 |
| Saline sub-engines | 7 |
| Nutrition Intelligence sub-engines | 12 |
| Lignes de code total engines | ~45,000 |

---

# SECTION A — V8 NATIONAL (8 engines)

## A1. SCORE V8 NATIONAL
- **Fichier:** engines/v8_national/router.py (305 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/national/score, /biome-profile, /species-profile
- **Domaine:** Score global national 0-100
- **Description:** Calcule score V8 combinant: météo Open-Meteo (température, vent, pression, UV), profil biome provincial (13 provinces), données habitat espèce, exclusions BCE-4X. Prédiction: excellent/bon/modéré/faible/exclu.
- **Entrées:** lat:float, lon:float, species:str, month:int, hour:int
- **Sorties:** {score_v8:int, prediction:str, biome:{code,name}, habitat_data:{}, meteo:{temp,wind,pressure}, exclusion:{status,criteria[]}, compute_ms:int}
- **Sources données:** Open-Meteo API (cache _weather_cache 1.5s), referentials.py (biomes statiques 13 provinces), exclusion_engine.py
- **Logique interne:** (1) Détecte province → biome. (2) Fetch météo parallèle. (3) Évalue exclusion. (4) Score composite: habitat 35% + météo 25% + saisonnier 20% + biome 20%. Cache résultat 30s.
- **Dépendances:** referentials.py, exclusion_engine.py, Open-Meteo API
- **Consommateurs:** ScoreV8Badge.jsx, V8IntelPanel.jsx, Phase C Multi-Engine
- **Limitations:** Météo cache (pas streaming). Score composite heuristique.
- **Conformité:** CONFORME V8
- **Risque régression:** Faible (endpoint stable)

## A2. EXCLUSION ENGINE V8
- **Fichier:** engines/v8_national/exclusion_engine.py (489 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/exclusions/evaluate
- **Domaine:** Exclusions terrain BCE-4X — 22 critères
- **Description:** Évalue 22 critères d'exclusion géospatiale: zones urbaines (>50k hab), militaires, parcs nationaux, réserves fauniques, routes majeures (<100m), autoroutes (<200m), plans d'eau (<50m), pentes extrêmes (>45°), zones protégées, aéroports (<5km), voies ferrées (<100m), lignes HT (<200m), zones industrielles, cimetières, terrains de golf, stations de ski, zones portuaires, mines actives, dépotoirs, centrales électriques, barrages (<500m), zones inondables.
- **Entrées:** lat:float, lon:float, species:str
- **Sorties:** {status:"INCLUDED"|"EXCLUDED", triggered_criteria:[], total_criteria:22, details:{}}
- **Sources données:** Heuristique géospatiale (distance estimée par seed terrain)
- **Logique interne:** Pour chaque critère, calcule une probabilité d'exclusion basée sur position + seed déterministe. Si >=1 critère déclenché → EXCLUDED.
- **Dépendances:** Aucune externe
- **Consommateurs:** map_bundle.py, Score V8, Phase A engines
- **Limitations:** HEURISTIQUE — pas de données cadastrales/OSM réelles pour chaque critère
- **Conformité:** CONFORME V8 (architecture). NON-CONFORME données (heuristique vs réel)
- **Risque régression:** Moyen (faux positifs/négatifs possibles)

## A3. GOVERNANCE ENGINE
- **Fichier:** engines/v8_national/governance.py (197 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/governance/state, /activate, /deactivate
- **Domaine:** Master Switch PREVIEW/PUBLIC
- **Description:** Contrôle publication V8. LOCKED (défaut) → PREVIEW (admin) → PUBLIC. Seul admin@huntiq.com autorisé. Vérifie credentials + rôle admin dans MongoDB.
- **Entrées:** action, email, password (pour activate/deactivate)
- **Sorties:** {mode:"LOCKED"|"PREVIEW"|"PUBLIC", activated_by:str, timestamp:str}
- **Sources données:** MongoDB (users collection)
- **Dépendances:** auth_engine (bcrypt verification)
- **Consommateurs:** Toolbar PREVIEW badge
- **Limitations:** Single admin hardcodé
- **Conformité:** CONFORME V8

## A4. MAP BUNDLE ENGINE
- **Fichier:** engines/v8_national/map_bundle.py (288 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/map/bundle (NO AUTH)
- **Domaine:** Bundle consolidé TERRITOIRE — toutes couches géospatiales
- **Description:** Endpoint unique PUBLIC servant: 5 zones terrain-aware (polygones organiques 14-20 vertices), ~10 corridors Bézier (0.2-1.8km, exclusions eau/pente), 3 affûts (orientés vent), données thermal, score multi-engine. Cache 30s par position+espèce+vent.
- **Entrées:** lat:float, lon:float, species:str, month:int, hour:int, wind_deg:float, include_p1:bool
- **Sorties:** {zones:[], corridors:[], affuts:[], thermal:{}, multi_engine:{composite_score,classification,breakdown}, biome:{}, exclusion:{}, compute_ms:int, from_cache:bool}
- **Sources données:** Phase B generators, Phase C thermal/multi-engine, exclusion_engine, referentials
- **Logique interne:** (1) Check cache 30s. (2) Détecte province/biome. (3) Évalue exclusion. (4) Appelle Phase B: generate_zones_ta + generate_corridors_ta + generate_affuts_ta. (5) Appelle Phase C: _thermal_model + _multi_engine_score. (6) Cache résultat.
- **Dépendances:** phase_b_engines.py, phase_c_engines.py, exclusion_engine.py, referentials.py
- **Consommateurs:** useMapBundleV8.js → BionicLayersV8.jsx (SEUL renderer TERRITOIRE)
- **Limitations:** Terrain heuristique. Pas de A* pathfinding. TTFB <5ms.
- **Conformité:** CONFORME V8 architecture. PARTIEL géométrie (Bézier vs A*)

## A5. PHASE A ENGINES
- **Fichier:** engines/v8_national/phase_a_engines.py (360 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/map/relocalisation, /salines, /phase-a/status
- **Domaine:** Relocalisation optimale + Placement salines
- **Description:** Relocalisation: génère N candidats (default 16) dans rayon R, score composite (saline×0.40 + affût×0.35 + couvert×0.15 + bonus saisonnier/diversité), exclusion BCE-4X chaque candidat, retourne top-3 triés avec explications 6-12 lignes terrain. Salines: génère candidats, score multi-critères (eau 25%, couvert 20%, pente 20%, accessibilité 15%, sécurité 10%, diversité 10%), min_distance entre salines.
- **Entrées:** lat, lon, species, month, wind_deg, radius_m, n_candidates, n_salines, min_distance_m
- **Sorties:** Relocalisation: {relocalisations:[{lat,lon,composite_score,saline_score,affut_score,terrain{},explanation[],distance_m}], site_actuel:{}, total_candidates, compute_ms}. Salines: {salines:[{lat,lon,score,detail{eau,couvert,pente,accessibilite,securite,diversite},terrain{},explanation[]}], count, compute_ms}
- **Sources données:** _terrain_profile (heuristique seed), exclusion_engine V8
- **Logique interne:** _seed() déterministe → _terrain_profile() → _score_saline()/_score_affut() → _score_composite() → tri + filtre exclusion → explications NL
- **Dépendances:** exclusion_engine.py
- **Consommateurs:** usePhaseAV8.js → PhaseALayerV8.jsx + PhaseAPanelV8.jsx
- **Limitations:** Terrain heuristique (sin/cos seed, pas DEM)
- **Conformité:** CONFORME V8

## A6. PHASE B ENGINES
- **Fichier:** engines/v8_national/phase_b_engines.py (417 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/map/zones-ta, /corridors-ta, /affuts-ta, /phase-b/status
- **Domaine:** Zones + Corridors + Affûts terrain-aware
- **Description:** generate_zones_ta: 5 types (alimentation/repos/rut/affûts/eau), placement radial 72°, polygones _organic_polygon (14-20 vertices, jitter sin/cos), score _score_zone_terrain par type (canopy/pente/eau/route/strate/feuillus), exclusion flag (eau<15m, pente>40°). generate_corridors_ta: 10 corridors, positions procédurales (0.2-1.8km), courbes Bézier 9 points, filtrage exclusion (eau<20m, pente>35°), intensité _corridor_intensity (cost surface + COR-006 transition + pénalité pente), 5 types (critique/majeur/fort/modéré/faible). generate_affuts_ta: dérivés des zones (alimentation/rut/repos), opposé vent (wind_deg+180), score (couvert 30% + vent 25% + transition 20% + corridor_proximity_bonus 25%).
- **Entrées:** lat, lon, species, month, hour, wind_deg
- **Sorties:** zones:[{id,type,center,polygon,score,terrain{7 champs},excluded,exclusion_reason}], corridors:[{id,type,path,start,end,intensity,cost_surface,terrain_start,terrain_end}], affuts:[{id,lat,lng,orientation_deg,zone_type,quality,score,terrain{},corridor_proximity_bonus}]
- **Sources données:** _terrain_profile heuristique (seed déterministe), _cost_surface_score, _corridor_intensity
- **Logique interne:** _seed(lat,lon,salt) → valeur pseudo-aléatoire déterministe. _terrain_profile: canopy/pente/strate/feuillus/eau/route par sin/cos. _organic_polygon: n vertices + jitter radial. _bezier_curve: quadratique 2 points contrôle.
- **Dépendances:** Aucune externe
- **Consommateurs:** map_bundle.py (principal), endpoints sandbox directs
- **Limitations:** TERRAIN HEURISTIQUE (sin/cos, pas DEM/LiDAR/NDVI). Corridors Bézier simples (pas A* pathfinding V6). Placement zones radial (pas basé sur données terrain réelles).
- **Conformité:** PARTIELLE — écart A* vs Bézier, terrain heuristique vs réel
- **Risque régression:** Faible (sandbox isolé)

## A7. PHASE C ENGINES
- **Fichier:** engines/v8_national/phase_c_engines.py (364 lignes)
- **Version:** V8 | **Statut:** ACTIF | **Router:** /api/v8/engines/thermal, /scenario, /scenario/presets, /multi-score, /phase-c/status
- **Domaine:** Thermal + Scenario + Multi-Engine Scoring
- **Description:** _thermal_model: température estimée saisonnière, wind chill (formule Environnement Canada), canopy shelter, confort animal 0-100, 5 zones thermiques (extreme_froid/froid/optimal/chaud/extreme_chaud). _run_scenario: 8 presets what-if (chasse_matin, chasse_soir, rut_peak, post_hiver, canicule, tempete_neige, vent_fort, nuit), compare baseline vs conditions modifiées, deltas par composante, impact global pondéré (zones 35% + affûts 30% + thermal 30% + corridors 5%), verdict FAVORABLE/NEUTRE/DEFAVORABLE. _multi_engine_score: composite terrain 30% + zones 20% + affûts 20% + saline 15% + thermal 15%, classification 5 niveaux (EXCEPTIONNEL/EXCELLENT/BON/MODERE/FAIBLE).
- **Entrées:** lat, lon, species, month, hour, wind_speed, temp_c, scenario_id
- **Sorties:** Thermal: {temp_air_c, wind_chill_c, effective_wind_kmh, canopy_shelter_pct, confort_animal, zone_thermique, terrain{}}. Scenario: {scenario_id, description, conditions{}, baseline{}, scenario{}, deltas{}, impact_global, verdict, available_scenarios[]}. Multi: {composite_score, classification, breakdown{terrain,thermal,temporal}, components{zones_avg,corridors_avg,affuts_avg,saline_score,confort_animal}, thermal{}, terrain{}}
- **Sources données:** Phase A engines (_score_saline, _score_affut), Phase B generators, heuristique saisonnière température
- **Logique interne:** Thermal: base saisonnière + diurnal sin + seed, wind chill si T<10°C et V>4.8km/h, confort optimal 0-15°C. Scenario: appelle Phase B generators 2x (baseline + scenario), compare. Multi: agrège tous scores Phase A+B+Thermal.
- **Dépendances:** phase_a_engines.py, phase_b_engines.py
- **Consommateurs:** PhaseCPanelV8.jsx, map_bundle.py
- **Limitations:** Température heuristique saisonnière (PAS Open-Meteo temps réel pour Phase C)
- **Conformité:** CONFORME V8 architecture. PARTIEL données (heuristique T°)

## A8. P1 PIPELINES
- **Fichier:** engines/v8_national/p1_pipelines.py (261 lignes)
- **Version:** V8 | **Statut:** STUB | **Router:** /api/v8/p1/lidar, /pedology, /status
- **Domaine:** Données institutionnelles LiDAR MRNF + pédologie IRDA
- **Description:** Stubs complets retournant fallback heuristique. LiDAR: hauteur canopée estimée. IRDA: composition sol estimée par écozone.
- **Entrées:** lat, lon, province
- **Sorties:** lidar:{canopy_height_m, source:"FALLBACK"}, pedology:{soil_type, ph, drainage, source:"FALLBACK"}
- **Sources données:** AUCUNE RÉELLE — fallback sin/cos
- **Dépendances:** Accès API MRNF (non obtenu), Accès API IRDA (non obtenu)
- **Consommateurs:** map_bundle.py (optionnel include_p1=true)
- **Limitations:** 100% STUB — aucune donnée réelle
- **Conformité:** STUB

---

# SECTION B — ENGINES PRINCIPAUX V6/V7 (8 systèmes actifs)

## B1. HUNT ORCHESTRATOR
- **Fichier:** engines/hunt_orchestrator/ (router.py 454L, orchestrator.py 454L, choix_affuts.py 420L, vent_odeurs.py 337L, access_engine.py 932L)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/hunt/orchestrate, /scent-zone, /contamination-zones, /access-route
- **Domaine:** Recommandation chasse complète
- **Description:** POST /orchestrate: reçoit position centre, vent (direction/vitesse), feeding_sites, fixed_blinds, espèce, session. Retourne recommandations d'affûts classifiés (optimal/bon/acceptable/a_eviter) avec scores multi-facteurs, zones contamination olfactive (cône de dispersion vent), routes d'accès optimales.
- **Sous-engines:** orchestrator.py (logique principale, cache institutionnel), choix_affuts.py (sélection multi-critères: distance saline, vent, corridor, terrain), vent_odeurs.py (modèle dispersion olfactive gaussien), access_engine.py (routes accès, dénivelé, obstacles, coûts terrain).
- **Entrées:** {center_lat, center_lng, wind_direction_deg, wind_speed_kmh, species, feeding_sites[], fixed_blinds[], session}
- **Sorties:** {recommendations:[{blind:{lat,lng,score,classification,factors{}}, contamination_zone[]}], access_routes:[]}
- **Sources données:** Heuristique espèce, données statiques vent
- **Dépendances:** Aucune externe
- **Consommateurs:** StandsMapLayer.jsx (TERRITOIRE — appel POST /api/v1/hunt/orchestrate)
- **Limitations:** Pas de DEM, pas GPS
- **Conformité:** V6 LEGACY — non migré V8. Partiellement couvert par Phase A (relocalisation).

## B2. WEATHER V3
- **Fichier:** engines/weather_v3/ (router.py 398L, wind_model_provider.py 210L)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v3/weather/current, /wind-analysis, /score
- **Domaine:** Météo temps réel + Score chasse
- **Description:** Fetch Open-Meteo: température, vent (direction degré + cardinal, vitesse km/h, rafales), humidité %, pression hPa, UV index, visibilité km, point de rosée, couverture nuageuse. Score chasse 0-100: _score_wind (optimal 8-18km/h), _score_pressure (haute=bon), _score_temperature (saisonnier).
- **Entrées:** lat, lng
- **Sorties:** {temperature, feels_like, wind:{direction_deg, cardinal, speed_kmh, gusts_kmh}, humidity, pressure_hpa, uv_index, visibility_km, dew_point, cloud_cover, score_chasse, conditions_text}
- **Sources données:** Open-Meteo API (https://api.open-meteo.com/v1/forecast)
- **Dépendances:** Open-Meteo API (externe, gratuit, rate limit)
- **Consommateurs:** METEO BIONIC panel (TERRITOIRE droite), Score V8 (import interne)
- **Limitations:** Dépendance externe. Cache 1.5s.
- **Conformité:** ACTIF et fonctionnel

## B3. NUTRITION INTELLIGENCE (12 sous-engines)
- **Fichier:** engines/nutrition_intelligence/ (router.py 910L + 12 fichiers x5100-x7000)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/nutrition-intel/*
- **Domaine:** Intelligence nutritionnelle complète (scoring minéral, recettes, coûts, produits, fournisseurs)
- **Sous-engines:** x5100 (mineral score), x5200 (mineral recommendation), x5300 (order engine), x5500 (energy/protein analysis), x5600 (site guide), x5700 (cost engine), x5800 (recipe engine), x5900 (evidence engine), x6000 (product score), x6010 (product quality analyzer), x6011 (market availability), x6012 (regulatory compliance), x6020 (terrain solutions), x6030 (product ecosystem), x7000 (supplier/product engine)
- **Consommateurs:** Shop, Panier, Recommandations produits
- **Conformité:** ACTIF — domaine commercial indépendant de V8

## B4. CAMERA ENGINE
- **Fichier:** modules/camera_engine/v1/router.py (644L)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/cameras/*
- **Domaine:** CRUD caméras trail
- **Description:** Création/lecture/update/delete caméras. Recherche proximité géo. Gestion brands. Upload photos. Localisation GPS.
- **Entrées:** Camera CRUD data (brand, model, lat, lng, status, user_id)
- **Sorties:** Camera objects (id, brand, location, photos[], status)
- **Sources données:** MongoDB (cameras collection)
- **Consommateurs:** Page Caméras frontend
- **Conformité:** ACTIF

## B5. VISION ENGINE (IA)
- **Fichier:** modules/vision_engine/v1/router.py (322L)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/vision/*
- **Domaine:** IA Vision — analyse photos caméras trail
- **Description:** Analyse IA photos: détection espèces (species, confidence %), comptage, classification. Génération hotspots IA (patterns comportementaux). Trajectoires estimées. Batch analysis.
- **Entrées:** Photo (base64 ou URL), camera_id, user_id
- **Sorties:** {species_detected[], confidence, count, behavior, hotspots[], trajectories[]}
- **Sources données:** Emergent LLM Key (GPT Vision)
- **Dépendances:** Emergent LLM Key (CRITIQUE — budget limité)
- **Consommateurs:** Page Caméras, Intelligence panel
- **Conformité:** ACTIF

## B6. BDRE (Bionic Data Reliability Engine)
- **Fichier:** engines/bdre/ (router.py 571L + 8 modules, total ~2800L)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/bdre/*
- **Domaine:** Fiabilité données, qualité, sources, fallback, audit
- **Sous-modules:** source_selector.py (sélection meilleure source), quality_scorer.py (évaluation qualité données), fallback_chain.py (chaîne de fallback), anomaly_detector.py (détection anomalies), institutional_cache.py (cache routes/corridors certifiés), source_registry.py (registre sources), waterway_classifier.py (classification cours d'eau), health_monitor.py (monitoring santé), audit_logger.py (journalisation audit)
- **Consommateurs:** Pipelines internes
- **Conformité:** ACTIF

## B7. AFFUT IA ENGINE
- **Fichier:** modules/affut_ia_engine/v1/ (engine.py 640L, router.py 88L)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/affut-ia/generate
- **Domaine:** Recommandation IA affûts multi-critères
- **Description:** Classe AffutIAEngine: (1) Génère candidats points dans rayon. (2) Score chaque candidat: saline_distance, wind_contamination, corridor_proximity, temporal_v7, terrain. (3) Classification (optimal/bon/acceptable/a_eviter). (4) Justification NL par espèce/saison.
- **Entrées:** center_lat/lng, radius_m, feeding_sites, hotspots, trajectories, wind_deg/speed, species, month
- **Sorties:** affuts:[{lat, lng, score, classification, justification, stand_type, factors{}}]
- **Sources données:** MongoDB (hotspots), heuristique terrain
- **Dépendances:** MongoDB
- **Consommateurs:** StandsMapLayer.jsx
- **Conformité:** V6 LEGACY

## B8. SALINE ENGINE (7 sous-engines)
- **Fichier:** modules/saline_engine/ (router.py 344L + engines/ 7 fichiers)
- **Version:** V6 | **Statut:** ACTIF | **Router:** /api/v1/saline/*
- **Sous-engines:**
  1. **soil_composition_engine** (90L): Analyse sol par écozone (pH, drainage, matière organique, minéraux)
  2. **hydrology_leaching_engine** (171L): Lessivage minéraux par drainage/pente/précipitations
  3. **vegetation_forage_engine** (132L): Analyse végétation et fourrage disponible
  4. **wildlife_nutritional_engine** (117L): Besoins nutritionnels par espèce/saison/sexe/âge
  5. **nutrient_deficiency_engine** (139L): Analyse carences et interactions minérales
  6. **seasonal_metabolism_engine** (213L): État métabolique par saison, probabilité visite
  7. **saline_recommendation_engine** (411L): Recommandations produits ajustées (déficits + hydro + végétation)
- **Consommateurs:** Shop, Fiche saline, Recommandations
- **Conformité:** ACTIF

---

# SECTION C — BIONIC ENGINE P0 (V6 GOLDEN — 14 sub-engines)

| # | Engine | Fichier | Lignes | Description | Statut |
|---|--------|---------|--------|-------------|--------|
| C1 | **SSE** | sse_engine.py | 544 | Satellite-to-Semantic: extraction sémantique terrain (type habitat, couvert, pente, hydro) | ACTIF (router) |
| C2 | **OSG** | osg_engine.py | 550 | Organic Shape Generator: formes organiques enrichies SSE | ACTIF (router) |
| C3 | **CME** | cme_engine.py | 560 | Corridor Morphology Engine: corridors organiques morphologiques | ACTIF (router) |
| C4 | **WSE/WIV** | wse_wiv_engine.py | 539 | Wind Scoring + Wind Impact Vector: dispersion olfactive | ACTIF (router) |
| C5 | **VFE** | vfe_engine.py | 399 | Visual Fusion Engine: fusion SSE+OSG+CME+WSE | ACTIF (router) |
| C6 | **SSVL** | ssvl_engine.py | 416 | Species-Specific Visual Logic: préférences visuelles par espèce | ACTIF (router) |
| C7 | **TCVE** | tcve_engine.py | 331 | Terrain Calibration Visual Engine: calibration terrain+visibilité | ACTIF (router) |
| C8 | **PME** | pme_engine.py | 355 | Pressure Memory Engine: mémoire pression chasse | ACTIF (router) |
| C9 | **BMPE** | bmpe_engine.py | 343 | Behavioral Micro-Patterns Engine: micro-patterns comportementaux | ACTIF (router) |
| C10 | **TFE** | tfe_engine.py | 349 | Thermal Flow Engine: gradients thermiques et flux chaleur | ACTIF (router) |
| C11 | **zone_engine_core_v2** | zone_engine_core_v2.py | 2276 | Pipeline zones V6 complet: cercles 600m, grille terrain, A* corridors, exclusions OSM, DEM | ACTIF (via bionic_p0_router) |
| C12 | **corridor_10x** | corridor_10x.py | ~600 | A* pathfinding sur grille terrain dérivée zones. COÛTS: terrain, pente, drainage, barrières | PRÉSENT — **NON-ROUTÉ V8** |
| C13 | **hotspot_engine** | hotspot_engine.py | 805 | Points chauds comportementaux: validation coords, habitat, eau, urbain | ACTIF (router) |
| C14 | **exclusion_v6/v7** | exclusion_engine_v6.py (367L), exclusion_engine_v7.py (378L) | 745 | Exclusions legacy OSM/urbain/eau | PRÉSENT — REMPLACÉ par V8 |

---

# SECTION D — SCORING PIPELINE (22 engines)

| # | Engine | Lignes | Fonctions | Domaine | Phase SUPRA | Router | Actif server.py |
|---|--------|--------|-----------|---------|-------------|--------|-----------------|
| D1 | alimentation_v1 | 188 | 4 | Nutrition basique multi-espèces | CORE | OUI | OUI |
| D2 | alimentation_v2 | 276 | 2 | Nutrition avancée + terrain + salines | CORE | OUI | OUI |
| D3 | repos_v1 | 154 | 4 | Zones repos: grille, multi-espèces | CORE | OUI | OUI |
| D4 | corridors_v10 | 942 | 12 | Corridors V10 orchestrateur + multi-engine | CORE | OUI | **PURGÉ V8** |
| D5 | attractors_v1 | 97 | 3 | Attracteurs écologiques (nourriture, eau, minéraux, reproduction) | CORE++ | NON | NON |
| D6 | behavior_v1 | 102 | 3 | Comportement animal (fuite, groupe, territorialité, adaptation) | CORE+++ | NON | NON |
| D7 | ecosystem_v1 | 52 | 3 | Santé écosystémique (biodiversité, connectivité, intégrité) | BIONIC OS | NON | NON |
| D8 | habitat_v1 | 84 | 3 | Qualité habitat (structure, diversité, bordure, connectivité) | CORE++ | NON | NON |
| D9 | hydro_v1 | 121 | 3 | Hydrographie (proximité, qualité, diversité, saisonnalité eau) | CORE++ | NON | NON |
| D10 | learning_v1 | 52 | 3 | Apprentissage adaptatif (tendances, fréquentation historique) | BIONIC OS | NON | NON |
| D11 | multi_species_v1 | 130 | 6 | Interactions multi-espèces (compétition, cohabitation, prédation) | BIONIC OS | NON | NON |
| D12 | ndvi_vegetation_v1 | 88 | 3 | NDVI saisonnier, diversité essences, structure verticale | CORE++ | NON | NON |
| D13 | opportunity_v1 | 95 | 3 | Opportunités observation (fenêtres optimales, approche, lignes fuite) | CORE+++ | NON | NON |
| D14 | pression_v1 | 102 | 2 | Pression humaine (distance routes/bâtiments, déterministe) | CORE++ | NON | NON |
| D15 | risk_v1 | 102 | 3 | Risque écologique (prédation, perturbation, mortalité routière) | CORE+++ | NON | NON |
| D16 | rsf_engine | 153 | 7 | Resource Selection Function: 13 covariables, 11 couches écologiques | BCE-4X | NON | NON |
| D17 | scenario_v1 | 104 | 4 | Scénarios what-if (impact modifications hypothétiques) | BIONIC OS | NON | NON |
| D18 | simulation_v1 | 66 | 4 | Simulation Monte Carlo (N itérations déterministes) | BIONIC OS | NON | NON |
| D19 | temporal_v1 | 101 | 3 | Patrons temporels (cycles circadiens, migration, reproduction) | CORE+++ | NON | NON |
| D20 | thermal_v1 | 104 | 3 | Confort thermique (ombrage, exposition, élévation, couverture) | CORE++ | NON | NON |
| D21 | trajets_v1 | 101 | 3 | Trajectoires déplacement (coût, perméabilité, barrières, drainage) | CORE++ | NON | NON |
| D22 | visibility_v1 | 91 | 3 | Visibilité / bassin visuel (observation, détection, champ vision) | CORE++ | NON | NON |

---

# SECTION E — COUVERTURE PAR DOMAINE (18 domaines)

| # | Domaine | Engine V8 | Engine V6 | Données réelles | Statut |
|---|---------|-----------|-----------|-----------------|--------|
| 1 | **Score global** | router.py (V8 National) | scoring_engine | Open-Meteo + heuristique | **COUVERT** |
| 2 | **Thermal** | phase_c (thermal) | thermal_v1 (non-routé), TFE | Heuristique saisonnière | **COUVERT** (heuristique) |
| 3 | **Hydrologie** | — | hydro_v1 (non-routé), BDRE waterway | Heuristique | **ABSENT V8** |
| 4 | **Pentes/orientation** | phase_b (_terrain_profile) | DEM (fallback SRTM) | sin/cos seed | **PARTIEL** (heuristique) |
| 5 | **Structure forestière** | phase_b (canopy/strate) | SSE, zone_engine | sin/cos seed | **PARTIEL** (heuristique) |
| 6 | **Canopy/LiDAR** | p1_pipelines (STUB) | WMS NFIS-QC | AUCUNE | **STUB** |
| 7 | **NDVI/végétation** | — | ndvi_vegetation_v1 (non-routé) | AUCUNE en V8 | **ABSENT V8** |
| 8 | **Pression humaine** | exclusion_engine (22 critères) | pression_v1 (non-routé), PME | Heuristique distance | **PARTIEL** |
| 9 | **Corridors réels** | phase_b (Bézier) | corridor_10x (A*), CME | Procédural | **COUVERT** (simplifié) |
| 10 | **Corridors IA** | — | corridor_10x (A*) | Grille terrain | **ABSENT V8** |
| 11 | **Zones écologiques** | phase_b (zones_ta 5 types) | zone_engine_core_v2 | Heuristique | **COUVERT** |
| 12 | **Scénarios temporels** | phase_c (8 presets) | scenario_v1 (non-routé) | Heuristique | **COUVERT** |
| 13 | **Météo temps réel** | weather_v3 (V6 actif) | weather_v3 | Open-Meteo API | **COUVERT** |
| 14 | **Exclusions** | exclusion_engine V8 (22 critères) | exclusion_v6/v7 | Heuristique | **COUVERT** |
| 15 | **Heatmaps comportementales** | — | hotspot_engine | Heuristique | **V6 ACTIF, ABSENT V8** |
| 16 | **Données caméras** | — | camera_engine | MongoDB | **V6 ACTIF** |
| 17 | **Données terrain (pins/traces)** | — | waypoint_engine | MongoDB | **V6 ACTIF** |
| 18 | **Données IA Vision** | — | vision_engine | LLM Emergent | **V6 ACTIF** |

**Résumé:** 10 COUVERTS (dont 3 heuristiques), 3 PARTIELS, 3 ABSENTS V8, 2 STUBS

---

# SECTION F — URGENCES ET ANOMALIES

## P0 — URGENCES CRITIQUES
1. **corridor_10x.py (A* pathfinding)** — Code complet A* présent (~600L), NON intégré dans V8 Phase B. Corridors V8 utilisent Bézier simple. Écart V6→V8 majeur.
2. **Terrain heuristique** — Phase A/B/C _terrain_profile basé sur sin/cos/seed déterministe. PAS de DEM réel (SRTM/Copernicus), PAS de LiDAR, PAS de NDVI. Toutes les données terrain sont SYNTHÉTIQUES.

## P1 — ANOMALIES CRITIQUES
3. **18 scoring pipeline engines NON-ROUTÉS** — Code complet (2300+ lignes total), docstrings détaillés, logique fonctionnelle. Potentiel massif inexploité.
4. **NDVI engine** — ndvi_vegetation_v1 (88L) présent avec scoring complet, NON routé, AUCUN équivalent V8.
5. **Phase C Thermal disconnecté de weather_v3** — Phase C utilise heuristique saisonnière au lieu de consommer weather_v3 (Open-Meteo temps réel).

## P2 — OBSERVATIONS
6. **10 sub-engines Bionic P0 (SSE→TFE)** — Actifs avec routers V6, pipeline complet, NON intégrés dans V8. Total ~4300 lignes de logique spécialisée.
7. **hunt_orchestrator** — V6 actif, consommé par StandsMapLayer.jsx. Fonctionnalité partiellement couverte par Phase A V8 mais PAS équivalent (orchestrator fait contamination + accès + multi-affûts).
8. **RSF engine** — Resource Selection Function avec 13 covariables. Code complet (153L). NON routé. Potentiellement le plus scientifique de tous les engines.

---

# SECTION G — DÉPENDANCES CRITIQUES

| Dépendance | Engines | Type | Impact si indisponible |
|------------|---------|------|------------------------|
| **Open-Meteo API** | weather_v3, Score V8 | EXTERNE gratuit | Fallback cache 1.5s. Score dégradé. |
| **MongoDB** | cameras, auth, waypoints, users, governance | INTERNE | APP INUTILISABLE |
| **Emergent LLM Key** | vision_engine | EXTERNE payant | IA Vision bloquée |
| **Terrain heuristique (sin/cos)** | Phase A/B/C, map_bundle, exclusion | INTERNE | FAUX TERRAIN partout |
| **OSM/Overpass** | zone_engine_core_v2, engine_osm_lite | EXTERNE | Cache local (/app/backend/data/osm_cache/) |
| **MRNF/IRDA** | p1_pipelines | INSTITUTIONNEL | Stubs permanents |

---

# SECTION H — PLAN DE CORRECTION PRIORISÉ

| Priorité | # | Action | Engine | Impact estimé |
|----------|---|--------|--------|---------------|
| **P0** | 1 | Intégrer A* pathfinding (corridor_10x.py) dans Phase B V8 | phase_b_engines.py | Corridors terrain-aware réels |
| **P0** | 2 | Connecter Phase C Thermal à weather_v3 (Open-Meteo réel) | phase_c_engines.py | Température réelle au lieu d'heuristique |
| **P1** | 3 | Router ndvi_vegetation_v1 dans V8 | scoring_pipeline | Végétation réelle |
| **P1** | 4 | Router pression_v1 dans V8 | scoring_pipeline | Pression humaine complète |
| **P1** | 5 | Router hydro_v1 dans V8 | scoring_pipeline | Hydrologie réelle |
| **P1** | 6 | Obtenir accès LiDAR MRNF | p1_pipelines | Canopy réelle |
| **P1** | 7 | Connecter DEM réel (Copernicus/SRTM) à _terrain_profile | Phase A/B | Pente/altitude réelles |
| **P2** | 8 | Évaluer intégration 10 sub-engines P0 (SSE→TFE) | Bionic P0 | Pipeline enrichi |
| **P2** | 9 | Évaluer intégration RSF engine | scoring_pipeline | Modèle scientifique RSF |
| **P2** | 10 | Migrer hotspot_engine vers V8 | Bionic P0 | Heatmaps V8 |
| **P3** | 11 | Router les 13 engines scoring restants | scoring_pipeline | Couverture 22/22 |
| **P3** | 12 | Migrer hunt_orchestrator vers V8 | hunt_orchestrator | Recommandation chasse V8 |

---

**CONFIRMATIONS EMERGENT:**
- Audit lancé: OUI
- Extraction complète: OUI (138 engines, 114 routers, ~45,000 lignes)
- Rapport généré: OUI (/app/memory/ENGINES_AUDIT_REPORT.md)
- Actions correctives entreprises: AUCUNE
- Statut: EN ATTENTE VALIDATION INSTITUTIONNELLE

**AUCUNE MODIFICATION. AUCUN DÉPLOIEMENT. AUCUNE SUPPRESSION. AUDIT SEULEMENT.**

FIN DU RAPPORT — EMERGENT — 2026-04-16
