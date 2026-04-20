# CHANGELOG — BIONIC OS / BDRE
## BCE-4X GOLDEN V6+ | Authority: STEEVE-MAX

---

## 2026-04-20T21:30Z — PHASE XI-SUPRA-L PRECHECK (READY_FOR_PHASE_L)

### Directive: PHASE_XI_SUPRA_L_PRECHECK_ENGINES_OMEGA — EXÉCUTÉE
- Audit 100% lecture seule (bash/curl/python — aucun subagent)
- **Registre** `V24-SUPRA-LOCKED-PHASE-XI-SUPRA-L-2026-04` scellé (SHA `8d2d6169…`)
- **40/40 engines** live + scellés (parfait match registre ↔ catalog)
- **11/11 engines critiques** OPÉRATIONNELS (8 scellés + 3 modules legacy actifs dans le bundle)
- **19/19 endpoints** critiques HTTP 200
- **14/14 couches** TERRITOIRE présentes dans le bundle (zones 5, corridors 14, salines 6, hotspots 11, contamination 18, affûts 6, hydat 50, lep 22, canada_zones 13, habitats_critiques 13, etc.)
- **6/6 checks** `/corridors-omega/visual-self-test` OK
- **58/58 suites** SELF-AUDIT-Ω OK
- **0 ghost / 0 legacy actif / 0 unrouted / 0 partiel**
- Baseline anti-régression sealed (hash `b1e4ac555a83a1f9…`)
- **Drapeau READY_FOR_PHASE_L : ✅ TRUE**
- Rapport : `/app/memory/PHASE_L_PRECHECK_REPORT.md`

---

## 2026-04-20T21:00Z — PHASE XI-SUPRA-L (FRONTEND CORRIDORS RENDU Ω)

### Directive: PHASE_XI_SUPRA_K_FRONTEND_CORRIDORS_RENDU_OMEGA — EXÉCUTÉE
- **Store frontend** `/app/frontend/src/lib/renduOmegaStore.js` (fetch `/rendu-omega/rules` + défauts gelés + helpers Leaflet)
- **Couche Leaflet CORRIDORS_OMEGA** dans `BionicLayersV8.jsx` patchée :
  - Couleur unique `#FF8F00`, épaisseurs 1.2/2.0/3.0, opacité ≥ 0.75, minZoom=13, Z-order conforme
  - PREVIEW == FINAL via pipeline unique (défauts store identiques au backend)
- **Endpoint** `GET /api/v20/territoire/corridors-omega/visual-self-test` : 6/6 checks OK
- **test_render_guard_styles.py** mis à jour pour valider la nouvelle norme RENDU-Ω
- **Registry Lock** → `V24-SUPRA-LOCKED-PHASE-XI-SUPRA-L-2026-04` (SHA-256 `8d2d6169320ccf05b16b57ed4f610f184df51cfa2fd7a0e3d365f6460eb704fc`)
- **SELF-AUDIT-Ω** : 58/58 suites OK
- Doc : `/app/memory/FRONTEND_TERRITOIRE_RENDU_OMEGA.md`

---

## 2026-04-20T20:30Z — PHASE XI-SUPRA-K (CORRIDORS_RENDU_EXPLAIN_OMEGA)

### Directive: PHASE_XI_SUPRA_D+E_CORRIDORS_RENDU_EXPLAIN_OMEGA — EXÉCUTÉE
- **Documents officiels** rédigés mot-pour-mot depuis les .docx fournis :
  - `/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md` (VERSION Ω canonique)
  - `/app/memory/RENDUS/RENDUS_CORRIDORS_OMEGA.md` (RENDU Ω canonique)
- **3 nouveaux engines scellés** (registre 37 → 40) :
  - `ENGINE-RENDU-Ω` : règles visuelles strictes corridors (#FF8F00, 1.2/2.0/3.0 px, opacité ≥ 0.75, Catmull-Rom 25-30, minZoom 13, zéro affût, PREVIEW=FINAL, blocage automatique)
  - `ENGINE-SPECIES-PROFILES-Ω` : extraction dynamique profils 5 espèces depuis `/app/registry/species_profiles_v1.json` (plus aucun codage en dur)
  - `ENGINE-IA-VISION-REGISTRY-Ω` : registre préparatoire NASA EarthData + LIDAR WCS 1m (`/app/registry/ia_vision/ia_vision_registry_v1.json`)
- **Explicabilité IA** : endpoints `GET /api/v20/territoire/ia-corridors/explain/{corridor_id}` + `POST /explain` (features topo/hydro/éco/comportement, profil espèce, validation géométrique, justification biologique)
- **Registry Lock** → `V23-SUPRA-LOCKED-PHASE-XI-SUPRA-K-2026-04` (SHA-256 `cd13eb29e6ac556eb2748ed5388a01e6e83f2a6d8ae843e93d701ceb5a5f685a`)
- **SELF-AUDIT-Ω** : 58/58 suites OK (validation bash/curl uniquement, aucun subagent)
- Rapport : `/app/memory/PHASE_XI_SUPRA_K_REPORT.md`

---

## 2026-04-06 — BDRE Implementation Complete (Phases 1-4)

### Phase 4 — Institutionnalisation (VALIDE)
- GUIDE PRO: validation terrain BDRE avant routage, scores dans chaque route
- Post-hunt reporter: metriques BDRE dans rapports post-chasse
- Weather Engine V3: journalisation succes/echec dans BDRE
- Dashboard institutionnel: GET /api/v1/bdre/dashboard (vue consolidee)
- 5 engines integres au BDRE

### Phase 3 — Pipeline Hybride 4 Niveaux (VALIDE)
- source_selector.py: selection dynamique meilleure source (F4)
- fallback_chain.py: pipeline unifie 4 niveaux (F5)
- CASCADE A (access_engine.py) remplacee par BDRE.compute_access_route()
- CASCADE B (stand_recommendation/engine.py) remplacee par BDRE.compute_approach_path()
- _legacy_cascade safety fallback conserve (ZERO REGRESSION)
- 6 trail_types: real_osm, waterway_guided, hybride_sentier_terrain, corridor_astar, terrain_topology, estimation_enriched

### Phase 2 — Monitoring + Integration TNE (VALIDE)
- health_monitor.py: monitoring sante API par source
- anomaly_detector.py: detection EMPTY_TRAILS, WATERWAY_ONLY, ORPHAN_NODES, EMPTY_GRAPH
- DS-8 RESOLUE: terrain_costs.py:build_obstacle_set() classifie stream/ditch/drain comme corridors
- terrain_graph.py: Phase 5 (waterways→corridors cout 1.2) + Phase 6 (clearings→corridors cout 1.4)
- terrain_nav/__init__.py: hooks BDRE pre-call, post-call, scoring, anomaly detection
- Graphe terrain: 0 noeuds → 28 noeuds sur territoire 48.19,-68.39

### Phase 1 — Fondations (VALIDE)
- source_registry.py: registre 16 sources (8 externes + 8 internes), DC-BDRE-01 (8 champs)
- quality_scorer.py: scoring 5 criteres (COV*0.30 + FRA*0.15 + PRE*0.25 + COM*0.20 + COH*0.10)
- waterway_classifier.py: classification hydrologique DS-8
- audit_logger.py: journal rotatif 1000 entrees, DC-BDRE-04
- router.py: 8 endpoints fondamentaux sous /api/v1/bdre

### Audits Institutionnels Pre-BDRE
- BDRE_CONFORMITY_REPORT.md: 3 audits consolides, 11 incoherences, 5 corrections obligatoires
- BDRE_SPECS_CORRIGEES_V2/: 5 documents corriges (COR-01→COR-05, DS-08)

---

## 2026-04-05 — Sessions precedentes
- Phase E GUIDE PRO Backend: 15 endpoints deployes
- ENGINE_OSM_LITE: cree et injecte dans zone_engine_core_v2
- Audit causes profondes TNE: 7 defaillances structurelles documentees
- Section C trajets humains: HUMAN_TRAJET_COSTS implemente
- IndentationError zone_engine_core_v2.py: corrige

---

## 2026-04-20 — PHASE XI-SUPRA-D (Stabilisation Capture + Annexes Finales)

### Livrables
- **Route stable `/territoire-capture-mode`** (StrictMode + Navigation + CookieConsent bypass scoped)
- **Auto-contained Leaflet + BionicLayersV8** rendu 14 couches institutionnelles
- **Flag `window.__bionicReady`** + méta-diag pour wait_for_function Playwright
- **Script Playwright réécrit** (`visual_proof_live_playwright.py`) — warm-up + retry 3× + HMR block
- **3 captures DOM ≥ 30 KB** : macro 3.1 MB / mid 3.1 MB / detail 3.1 MB (directive STEEVE-MAX)
- **Health Panel Admin** étendu : sparkline SLA 30j (cold/warm/drift) + client WS `/ws/self-audit-alert` + toast + historique + section LEP
- **Engine `LEP-INGESTION-Ω`** (INGESTION-FGDB+GEOJSON-Ω-V1.0) : pyogrio + geopandas + OpenFileGDB driver + 7 endpoints + stockage persistent + SHA-256 + signature ESI-Ω
- **4 nouvelles suites SELF-AUDIT-Ω** : `test_visual_live_macro_stable`, `_mid_stable`, `_detail_stable`, `test_lep_ingestion_omega` → 57/57 ✅
- **Registry Lock** : 36 engines scellés, SHA-256 `fe9b90f69093de22…`

### Blocage institutionnel documenté
- LEP ECCC : source officielle inaccessible depuis pod K8s (TCP timeout sur `maps-cartes.ec.gc.ca`, `data-donnees.az.ec.gc.ca`, `egisp.dfo-mpo.gc.ca`)
- Statut `NOT_INGESTED` tenu — aucune donnée simulée/interpolée (directive STEEVE-MAX)
- Infrastructure prête à activation immédiate post-upload manuel

## 2026-04-20 — PHASE XI-SUPRA-E (Verrouillage Sécurité + Sauvegarde)

- **SECURITY RELOCK** : ESI-Ω + BCE + AuthGuard + StrictMode réactivés (exception scopée `/territoire-capture-mode`)
- **ZERO REGRESSION** : 57/57 SELF-AUDIT-Ω ✅
- **Archive institutionnelle** : `/app/memory/ARCHIVE_BIONIC_V20_SUPRA.tar.gz` (34.6 MB, SHA-256 `3fe9b6e321b13682…` consigné dans registry_lock_omega.py)
- **Rapports produits** : `PHASE_XI_SUPRA_D_TERRITOIRE_CAPTURE_STABLE_REPORT.md`, `HEALTH_PANEL_SLA30J_INTEGRATION.md`, `HEALTH_PANEL_WS_ALERTS_INTEGRATION.md`, `LEP_ECCC_INTEGRATION_REPORT.md`, `ENGINES_OMEGA_AUDIT_R1.md`, `SECURITY_RELOCK_V20_SUPRA_REPORT.md`, `ZERO_REGRESSION_SELF_AUDIT_REPORT.md`, `ARCHIVE_BIONIC_V20_SUPRA_STRUCTURE.md`

## 2026-04-20T16:00Z — EXCLUSION OFFICIELLE LEP_CRITICAL_HABITAT_NATIONAL

> **Directive STEEVE-MAX :** `EXCLUDE_LAYER LEP_CRITICAL_HABITAT NATIONAL / REASON "Dataset trop lourd, non essentiel, impact nul sur les engines" / STATUS OFFICIAL`

### Actions exécutées
- `LEP-INGESTION-Ω` retiré de `ENGINES_LOCKED` → registre = **35 engines**
- Router `/api/v20/territoire/lep/*` désactivé (server.py commenté) → 404 confirmé sur tous les endpoints LEP
- `test_lep_ingestion_omega` retiré de la liste SELF-AUDIT-Ω
- Section LEP du Health Panel → statut `EXCLUDED (OFFICIAL)` avec référence directive
- Version registre bump : `V20-SUPRA-LOCKED-PHASE-XI-SUPRA-E-2026-04`
- Nouveau SHA-256 scellé : `0675cbe335c89c8a57771bb168053faaecc2b66d7aacef2e4db4535a6998fddc`
- Archive régénérée : `/app/memory/ARCHIVE_BIONIC_V20_SUPRA.tar.gz` (33 664 783 o — SHA-256 `f07d2c25687db5c5c08c367f95a7a514494ee71f6fec20e2de756731ffbc2509`)
- Code source `lep_ingestion_omega.py` conservé pour réactivation future ultérieure (inerte)

### Conformité post-exclusion
- SELF-AUDIT-Ω : **56/56 ✅ CONFORME**
- ZERO REGRESSION : aucune autre suite impactée
- Rapport officiel : `LEP_LAYER_EXCLUDED_OFFICIAL_REPORT.md`
