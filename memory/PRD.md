# PRD — BIONIC OS V20-SUPRA / TERRITOIRE
## Last updated : 2026-04-22 — PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω (X180-AMENDEMENT-FINAL) CLOS

## Protocol
BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX
Language : FR. Persona : formel, martial, institutionnel.
Aucun testing subagent autorisé.
Waypoint canonique exclusif : **48.206657 / -68.382422**
Registre V30 SHA-256 verrouillé : `27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c`

## Architecture canonique
- Backend FastAPI (V30 LOCKED) + post_smoothing externe `organic_corridor_smoother.py`
- Frontend React + Leaflet (`BionicLayersV8.jsx`, `renduOmegaStore.js`)
- CI_STATUS_Ω runtime dashboard (`routes/ci_status_omega.py`, 6 suites / 65 tests sentinelles)

## Phases complétées
| Phase | Statut |
| --- | --- |
| X20 / X30 PIPELINE_AUDIT | DONE |
| X40 OPS_RESTORATION (zones 404) | DONE |
| X50 OPS_REFUS_VALIDATION (wind, nutrition, popups) | DONE |
| X70 SUPRA_VENT_VISUEL (compass + cone) | DONE |
| X80 SUPRA_VERITE_TERRAIN (waypoint officiel + probes) | DONE |
| X120 SUPRA_RENDU_TERRITOIRE (contamination #FF0000 0.18, popups) | DONE |
| X150 / X170 CORRIDORS_RENDU + REPAIR frontend | DONE |
| X180 CORRIDORS_REPAIR AMENDEMENT-FINAL | DONE (2026-04-22) |
| X195 RAPATRIEMENT_TERRITOIRE_V7_ULTIME AMENDEMENT-ABSOLU | DONE (2026-04-22) |
| X197 COMPARATIF_TERRITOIRE_Ω AMENDEMENT-ABSOLU | DONE (2026-04-22) |
| X198 ENGINES_OPTIMISATION_Ω AMENDEMENT-ABSOLU | DONE (2026-04-22) |
| X199 VALIDATION_ENGINES_Ω AMENDEMENT-ABSOLU | DONE (2026-04-22) |
| X200-P0 ACTIVATION V31_CORE_PREPARATOIRE_Ω | DONE (2026-04-22) |
| X200-P1-PREVIEW_ET_PREPARATION_Ω | DONE (2026-04-22) |
| **X200-P1-EXTERNAL-INFLOW_Ω** | **DONE (2026-04-22)** |

## X200-P1-EXTERNAL-INFLOW livrables
- **Module** : `/app/backend/engines/reseau_veineux_omega/external_inflow.py` (350+ lignes, entièrement testé)
- **12-24 ENTRY_NODES** générés sur couronne externe 700-800 m, distribution angulaire uniforme (step 360/count)
- **Pondération directionnelle** §5.2 : hydro 40% / slope 25% / forest 20% / vital_zones 15% (somme = 1.0)
- **Traçage organique** : spline Bézier cubique 28 points, courbure progressive (path > distance directe)
- **Fusion externe ↔ interne** : seuil 75 m, élargissement ×1.5 sur segments superposés
- **Hiérarchie 5 niveaux VERSION COMMANDANT §5.5** : CRITIQUE #CC0000/6m/6, MAJEUR #FF0000/4m/5, FORT #FF8C00/3m/4, MODÉRÉ #FFD700/2m/3, FAIBLE #BFBFBF/1m/2
- **Double-verrou d'autorisation** : `EXTERNAL_INFLOW_ENABLED` OFF par défaut + env `P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true` + token `STEEVE-MAX-P1-EXTERNAL-INFLOW`
- **Endpoints HTTPS** (READ_ONLY) : `GET /external-inflow/status`, `POST /external-inflow/preview`
- **Rapport** : `/app/memory/RAPPORT_X200_P1_EXTERNAL_INFLOW_Ω.md` (SHA-256 `cb06a229e4620de60c21c238e9c8f1abd453e6ca173922063273b885a562e37a`)
- **Tests** : 23/23 Pytest nouveaux → **88/88 Pytest backend** + **65/65 Jest** = **153 verts**
- **Audit CI** : overall_ok=True (V30 / flags / zero_doublon)
- **Smoother X180, V30, rendu** : **intacts**

## X200-P1 livrables
- **Endpoint preview** `/api/v7-ultime/corridor-pipeline-preview` (POST/GET status) — READ_ONLY strict (smoother/rendu/v30 non touchés)
- **5 waypoints testés** : waypoint officiel, Québec, Saguenay, Montréal, 49N70W — tous conformes
- **Preview enrichi** vérifié : bio_score 93.99, CRITIQUE (#CC0000), hydro_bonus +0.2541, terrain_boost 1.70, habitat FONCTIONNEL
- **P1 préparation brouillon** : `/app/backend/engines/post_smoothing/p1_preparation.py` (3 flags OFF + double-verrou env+token)
- **Audit continu intégré CI_STATUS_Ω** : champ `engines_audit_x199_x200` avec 3 gates (V30 / flags / zero_doublon)
- **Plan X199 étendus** : ordre d'activation recommandé (ecoforestry → advanced_geospatial → terrain_3d → legal_time → wildlife_extended → predictive) avec rôle/dépendances/risques/tests/impact
- **Rapport institutionnel** : `/app/memory/RAPPORT_X200_P1_PREVIEW_Ω.md` (SHA-256 `a83ecf22f00c0d39c854cdda12f04ef53aa67494ecfb7c0a15d3356108d2389a`)
- **Tests** : 65/65 Pytest + 65/65 Jest = 130/130 verts ; audit CI overall_ok=True

## X200-P0 livrables
- **5 engines activés** (feature flag ON) : WILDLIFE_BEHAVIOR (CERF restauré), ECO_ZONES (20 salines hiérarchisées), HYDRO_TOPO (inversion hydro corrigée) + supports RESEAU_VEINEUX (5 niveaux V7) + BIO_SCORING (8-facteurs V7)
- **5 engines étendus** restent OFF (ecoforestry, terrain_3d, legal_time, predictive, advanced_geospatial)
- **Sources V7 restaurées** : species_profiles, classifier, scoring 8-facteurs (corridors_v10) + salines_ultime_engine + nutrition_engine_v7 + terrainBoosts
- **Inversion hydro CORRIGÉE** : passage du modèle répulsif X180 au modèle attractif V7 pondéré par `affinite_hydro` par espèce (bonus < 150m)
- **Audit continu** : `/app/backend/tools/audit_engines_x199_x200.py` (3 gates : V30 integrity, feature flags, ZERO-DOUBLON-Ω) — tous verts
- **Rapport institutionnel** : `/app/memory/RAPPORT_X200_P0_ACTIVATION_Ω.md` (SHA-256 `09dee83a1cc4143c…`)
- **Endpoints publics** : `/api/v7-ultime/{wildlife-behavior,eco-zones,hydro-topo,reseau-veineux,bio-scoring}/*` (12 routes)
- **Tests** : 65/65 Pytest backend + 65/65 Jest frontend = 130/130 verts
- **V30 intact** : SHA-256 `027712696407882fb41e34b0325e1f2b8dacb9082a860146659dc7650e6c8fc3` inchangé

## X199 livrables
- **Scaffolder** : `/app/backend/tools/scaffold_engines_cibles.py` (idempotent, dry-run supporté)
- **10 engines scaffoldés** (feature flags OFF) : 4 canoniques (reseau_veineux/eco_zones/bio_scoring/hydro_topo) + 6 étendus (ecoforestry/terrain_3d/wildlife_behavior/legal_time/predictive/advanced_geospatial)
- **Façade V30 miroir** : `/app/backend/engines/bio_scoring_omega/v30_mirror_read_only.py` — SHA-256 V30 vérifié pré/post, cache TTL 60s, champs autorisés `cost_surface`/`ecl`/`canopy_density`
- **YAML enrichi** : sections `validation_x199`, `engines_canoniques_x198`, `engines_etendus_x199`, `zero_doublon_omega`, `priorisation_12_critiques_x199`, `garde_fous_x199` (nouveau SHA-256 `5f25fe4c…`)
- **Rapport validation** : `/app/memory/VALIDATION_ENGINES_X199_Ω.md` (SHA-256 `a98790d59cb749f4…`)
- **Priorisation 12 critiques** : P0 (cerf, 20 salines, inversion hydro) / P1 (scoring 8-facteurs, 5 niveaux, nutrition, réseau enforce) / P2 (cost_surface, ecl, canopy, multi-échelles, terrain-aware)
- **Tests** : Pytest **61/61 PASS** (37 X199 scaffold + 24 X180 verrou), Jest **65/65 PASS**
- **ZERO-DOUBLON-Ω** : 10 routers legacy déjà désactivés historiquement (PURGE-V6-PHASE-B / ANTI-DUPLICATION-A-Omega), règles explicites encodées dans `zero_doublon_omega.interdictions_doublons_futurs`

## Garde-fous X199 respectés
- Engine V30 intact (SHA-256 `027712696407…` mesuré/vérifié par façade)
- Feature flags OFF : tous les 10 engines inertes, endpoints `/compute` retournent HTTP 503
- Routers non inclus dans `server.py` (aucune activation involontaire)
- DIAGNOSTIC-CORRIDORS-Ω toujours non activé
- Aucun rendu visuel modifié
- X200 non lancé (validation uniquement)

## X198 livrables
- **Cartographie** : `/app/memory/ENGINES_ACTUELS_CARTOGRAPHIE_Ω.md` (SHA-256 `abfa7047fa3a60cb0a2c7dc9f28a36cb88f0b27b2edafa568aa70cb6045d4ac3`) — ~5 660 KB totaux, ~522 .py, analyse redondances (corridors×3, salines×3, nutrition×3, alimentation v1/v2/v4)
- **Plan architecture cible** : `/app/memory/ENGINES_CIBLES_PLAN_Ω.md` (SHA-256 `37754f6dcfb8d3978a61b83c3a443aa1cd2062ef2a237e99c20b98b5a78eac6d`) — 4 engines cibles : ENGINE_RÉSEAU_VEINEUX_Ω (≤40KB), ENGINE_ECO_ZONES_Ω (≤120KB), ENGINE_BIO_SCORING_Ω (≤60KB), ENGINE_HYDRO_TOPO_Ω (≤80KB)
- **YAML engines_mapping** : section ajoutée à `V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml` (nouveau SHA-256 `d11bbfb1cdb28c384f294c1391bba40e4a81176b4e92344b71e648fab2a6482d`) — 12 critiques mappées sur 4 engines avec params V7 à réinjecter + actions X200
- **Endpoint HTTPS DIFF_MATRIX** PRO/EXPERT-only : `/api/v7-vs-actuel/diff-matrix` (YAML), `.json`, `/status`. Accès sans rôle → HTTP 403
- **Recommandation V30** : Façade-miroir lecture seule `v30_mirror_read_only.py` avec vérification SHA-256 V30 invariant (décrite §7 du plan)
- **Économie visée** : ~867 KB bruts / ~567 KB net après ajout des 4 engines cibles (−10 %)
- **Non-régression** : Pytest 24/24, Jest 65/65

## X197 livrables
- Rapport : `/app/memory/TERRITOIRE_V7_vs_TERRITOIRE_ACTUEL_Ω.md` (SHA-256 `94974bc3cf505a23809206fe51aa99952f2348a97d167aafc36c94a219c68a62`)
- YAML DIFF MATRIX : `/app/memory/V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml` (SHA-256 `2325a61eeac107df3c1f66b7be0dd3fcae075313cb2c639c07b4a0ee32049d63`) — **45 divergences**, 12 catégories, triplets `clé/V7/actuel/impact` + sévérité + source + action X200 recommandée
- Impacts : 23 PERTE, 3 INVERSION, 4 SIMPLIFICATION, 2 DÉGRADATION, 2 AJOUT, 4 PARITE_PARTIELLE, 2 PARITE_FRONTEND, 1 PARITE, 2 RENOMMAGE, 2 DIVERGENCE
- Sévérités : 12 CRITIQUE, 13 MAJEURE, 8 MODEREE, 6 MINEURE
- Base du futur CONTRAT RENDUΩ-RÉSEAU VEINEUX (phase X200)

## X195 livrables
- Archive V7 ULTIME rapatriée : `/app/memory/V7_ULTIME_EXPORT/V7_ULTIME_FULL.tar.gz` (156 entrées, 2.06 MB)
- SHA-256 : `c8c2f6a3339b3fb5624d3cc640174ed6fc07e10d4c519bb9f2341a788d1dc29f`
- Endpoints HTTPS : `/api/v7-ultime-export/{status,download,manifest,list,sha256}`
- Rapport comparatif V7 vs V20-X180 : `/app/memory/V7_vs_V20_X180_COMPARATIF_Ω.md` (SHA-256 `c748513bddf5b085e7ed3df5ffac1846f24f611b9edc6c0a4ba57fa94db3b0f4`)
- Verrou Pytest smoother 9 passes : `/app/backend/tests/test_smoother_x180_verrou.py` → **24/24 PASS**
- Contenu rapatrié (aucune simplification) : spatial_engine_v7, supra_engine_v7, nutrition_engine_v7, access_clarity_engine_v7, corridors_v10, alimentation_v1/v2, repos_v1, carte2027_engine, salines_ultime_engine, canada_v72, LEGACY_ACCESS_AFFUTS, composants frontend V7

## Interdictions X195 respectées
- Engine V30 non modifié
- Panneau DIAGNOSTIC-CORRIDORS-Ω NON activé
- Données V7 ULTIME non transformées
- Aucun filtrage / simplification

## X180 livrables
- Test Jest `phase_x170_corridors_biologie.test.js` : **8/8 PASS** (triple pipeline + constantes RENDU-Ω)
- Suite sentinelle globale : **65/65 PASS**, 6 suites
- `organic_corridor_smoother.py` AMENDEMENT-FINAL :
  - 9 passes (trim / smooth / despike / eliminate_fuite / segment_max / eco_alignment / ia_attractors / re-smooth / re-densify)
  - 5 profils espèces (chevreuil/orignal/wapiti/ours/dindon) avec angle_max, segment_max, water_tolerance, slope_max, human_avoidance
  - 6 types zones vitales (salines, alimentation, repos, rut, thermique, humide)
  - Endpoint `/smoother-status` institutionnel
- Conformité mesurée waypoint officiel : angle **27.04°** / segment **8.95 m** / zéro demi-tour
- CI_STATUS_Ω mis à jour (6 suites, 65 tests)
- Rapport PEDIGREE `/app/memory/PEDIGREE_DONNEES_X180.md` (DEM LiDAR, EarthData Hydro, ForestDensity, MicroRelief, IA Vision, species_profile, cartes coût/probabilité/attractivité)

## Backlog (attente directive)
- P1 : validation utilisateur visuelle corridors avec couche CORRIDORS active à zoom ≥ 13 sur waypoint officiel
- P2 : tests Pytest backend dédiés au smoother (passes 1-8) pour verrou institutionnel

## Tests
- Jest via `craco test` : 6/6 suites, 65/65 tests verts
- Backend `curl /api/v20/territoire/corridors-organic/generate` → HTTP 200, smoother_applied OK
- `curl /api/omega/ci-status` → 6 suites détectées, sentinelles alignées

## Contrats verrouillés
- Engine V30 : aucune mutation
- Post-processeur externe : registration AVANT `engine_ia_corridors_organic_omega.router` (priorité FastAPI first-match)
- Non-régression : en l'absence de signaux terrain/IA, path inchangé hors géométrie RENDU-Ω
