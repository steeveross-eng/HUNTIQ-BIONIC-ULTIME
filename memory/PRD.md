# PRD — HUNTIQ / BIONIC KNOWLEDGE ENGINE

## Protocole
BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX

## Description
Application geospatiale de chasse intelligente avec backend FastAPI et frontend React/Leaflet. Modules: SUPRA, ULTRA, FICHE, SOL, Species Engine K3, Bionic Knowledge Engine, Freemium, Saline, etc.

## Branche active
`SUPRA_RECONSTRUCTION` — NE PAS MERGER vers `main`.

## Travail accompli

### Phase R (Reconstruction SUPRA)
- R0: Branche creee, baselines verifiees (SUPRA=63, ULTRA=47.8, FICHE=71, SOL=47)
- R1: Nettoyage institutionnel (aliases, IC extrait, colonnes round-robin, session regex)
- R2: 7 duplications eliminees (5 inline + CriteriaDetailModal + GoldenComponents)
- R3: Extraction 5 onglets (AnalyseTab, FicheTab, IntelligenceTab, ComparezTab, CommandezTab) + constants.js
- R4: Corrections UX (grid-cols-4, fallback product_id)

### Phase K (Knowledge Engine)
- K1: Injection knowledge.json annotations scientifiques additives dans supra-batch
- K2: Audits JSON integrity valides
- K3 v3.0.0: Extraction 4 rapports docx scientifiques, knowledge.json genere
- K3 v3.1.0: Integration Black Bear
- K5: Overlay scientifique active progressivement dans supra-batch (5 especes)
- K6: Certification & Audits A/B/C/D — ZERO score drift

### Phase P0 (Evaluation differentielle) — Fevrier 2026
- BIONIC_DIFFERENTIAL_REPORT.md genere et commite
- Resultat: 0 REGRESSION, 40 AMELIORATIONS, 66 NEUTRE-STRUCTUREL
- 14/14 couches geospatiales intactes, MonTerritoireBionicPage.jsx inchange
- ZERO derive sur 4 baselines

### Audit Integrite Scientifique — Fevrier 2026
- AUDIT_INTEGRITE_SCIENTIFIQUE.md genere et commite
- 9 points institutionnels verifies: 7/9 CONFORME, 2/9 CONSTATATIONS
- Constatation 1 (MODEREE): knowledge.json regenere a K3 sous directive explicite (14/18 sources K0 remplacees, impact operationnel NUL)
- Constatation 2 (MINEURE): 3 types list→dict + 8 cles ajoutees (impact operationnel NUL)
- ZERO derive scores, ZERO impact moteurs, ZERO impact MON_TERRITOIRE

### Audit Multi-Especes Points Chauds & Salines — Fevrier 2026
- MULTI_SPECIES_HOTSPOTS_SALINES_AUDIT.md genere et commite
- Diagnostic: convergence inter-especes expliquee par 6 causes racines
- ~44% du score consolide (11 moteurs hash + PRESSION) = ZERO differenciation inter-especes
- Saline positionnement = 100% geophysique, aucun critere espece-specifique
- 11 couches manquantes, 8 parametres comportementaux absents, 6 logiques saline manquantes identifies
- Actions correctives proposees : P0 (ponderations dynamiques + RSF Engine) → P2 (DEM reel + hyperphagie ours)

### Plans de Restauration — Fevrier 2026
- MULTI_SPECIES_RESTORATION_PLAN.md genere et commite (6 phases MS-1→MS-6)
- CORRIDORS_ZONES_UI_RESTORATION_PLAN.md genere et commite
- Diagnostic UI/UX : infrastructure corridors + zones + toggles = OPERATIONNELLE
- Corridors V6 (683 lignes, rendering 5 niveaux, glow CRITIQUE) = OPERATIONNEL
- Zones (alimentation, repos, rut, eau) + 15+ toggles + sous-filtres = OPERATIONNELS
- Elements desactives par ORDONNANCE : AccessRouteV6, HuntingPath, HydrographyOverlay
- ZERO MODIFICATION de code executee — Plans d'action uniquement

### Execution MS-1 a MS-6 + Levee ordonnance + Reparation visibilite — Fevrier 2026
- MS-1: 5 matrices SPECIES_ENGINE_WEIGHTS (sum=1.0000 chacune) dans constants.py
- MS-2: RSF Engine cree (rsf_engine/coefficients.py + engine.py) — 13 covariables, delta 10.4pts inter-especes
- MS-3: 11 couches ecologiques integrees via covariables RSF
- MS-4: 8 parametres comportementaux (BREEDING_PERIODS, DISTURBANCE, WATER, THERMAL, CIRCADIAN)
- MS-5: 15 moteurs convertis en hybride RSF/hash (ratio 50-70% RSF)
- MS-6: Salines differentiees par espece (CERF/ORIGNAL/WAPITI profils + espacement)
- LEVEE ORDONNANCE: HydrographyOverlay, HuntingPath, AccessRouteV6 reactivees
- 3 bugs visibilite critiques corriges: multiEngines court-circuit, saisonniers court-circuit, aliasing zone/point
- CSS pulsation CRITIQUE extrait en fichier externe (anti-fantome gatekeeper)
- 5 livrables commites: MS_EXECUTION_REPORT, VISIBILITY_PIPELINE_AUDIT, VISIBILITY_PIPELINE_REPAIR_PLAN, CORRIDORS_ZONES_UI_RESTORED, validation BCE-4X

### Mise a jour regle metier Points Nutritionnels — Fevrier 2026
- DIRECTIVE COMMANDANT: Limite maximale de points nutritionnels par zone = 2 (anciennement 4)
- Relaxation progressive min_distance_m REFUSEE
- Backend: router.py, engine.py, salines.py, shadow_mode.py, salines_v4.py, schemas.py — tous mis a jour
- Frontend: MonTerritoireBionicPage.jsx (state initial=2), NutritionPointsLayer.jsx (default=2), TerritoireToolbar.jsx (selecteur [1,2])
- Validation Pydantic rejette max_salines > 2
- ZERO modification aux moteurs RSF, couches ecologiques, pipelines geospatiaux
- Livrable: NUTRITION_POINTS_POLICY_UPDATE.md
- Statut: APPLIQUE ET VERIFIE (API + UI)

## Taches en attente

### Correctif Zone Repos — Incoherence Rendu — Fevrier 2026
- BUG: Polygone repos non rendu malgre toggle actif et donnees backend valides
- CAUSE: `ringsCentroid(rawRings)` calculait le centroide geometrique des 1000+ vertices du polygone lisse
  Le centroide derivait hors du rayon d'analyse (780m), eliminant le polygone entier
- FIX: Remplacement par `props.center_lat/center_lng` (centre ecologique primaire) avec fallback ringsCentroid
- Fichier modifie: `frontend/src/components/territoire/BionicCorridorsV6Layer.jsx` (3 lignes)
- ZERO modification backend / RSF / SSF / couches ecologiques
- Livrable: REPOS_ZONE_AUDIT.md
- Statut: CORRIGE ET VERIFIE VISUELLEMENT

### P1 — Depreciation 9 endpoints AUTH-USAGER
- NON AUTORISE. En attente d'ordre explicite du Commandant.
- Reference: `/app/backend/AUTH_DEPRECATION_PLAN.md`

### P2 — M5 Offline Mode Ultra / BSAA-2
- GEL MAINTENU.

## Baselines certifiees
| Score | Valeur |
|---|---|
| SUPRA | 63 |
| ULTRA | 47.8 |
| FICHE | 71 |
| SOL | 47 |

## Credentials
- Admin Premium: `admin@huntiq.com` / `Saturn5858*`

## Integrations 3rd party
- Stripe Checkout
- OSM / Overpass APIs
