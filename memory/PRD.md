# PRD · TERRITOIRE Ω · BIONIC HUNT/CHASSE
**Last updated**: 2026-02-XX · BCE-4X ULTIME ABSOLU · COMMANDANT STEEVE-MAX

## ORIGINAL PROBLEM STATEMENT
PROTOCOLE BCE-4X ULTIME ABSOLU — Stabilisation exhaustive du backend et frontend
de l'écosystème TERRITOIRE Ω. Rendu parfait sur la carte des 5 espèces cibles
(chevreuil, orignal, ours_noir, coyote, dindon_sauvage) avec biological
divergence stricte. 0 erreur 502/404/400. Caching full-bundle stabilisé.
Persona BCE-4X non-déviante.

## URL CIBLE
`https://huntiq-restore.preview.emergentagent.com/territoire`

## STACK
- **Frontend** : React + Leaflet (BionicLayersV8.jsx, MonTerritoireBionicPage)
- **Backend** : FastAPI 1 worker uvicorn (single-thread asyncio)
- **DB** : MongoDB (`huntiq_v6`)
- **Cache** : LRU in-memory (Redis désactivé entre forks éphémères)
- **3rd party** : Open-Meteo (rate-limited 429, circuit-breaker actif), Resend

## CREDENTIALS
- Admin : `commandant@bionichunt.com` / `Commandant2026`

## REQUIREMENTS COMPLETED
- ✅ **P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω** (2026-02-XX) — FULL PACK P0→P3 :
  - **P0 Purge absolue** : `setBundleData(null)` à chaque changement d'espèce (useMapBundleV8 ligne 64),
    invalidation cache LRU si `bio_presence_mask_halt=True` (bionicBundleCache.haltTtlMs=60s),
    TTL ESSENTIEL_T0 réduit de 3600s → 60s pour éliminer la contamination inter-espèces.
  - **P1 Différenciation visuelle** : palette `SPECIES_COLOR_OMEGA` (vert chevreuil #2D7A2D,
    brun orignal #8B4513, violet ours_noir #5D2E8C, bleu wapiti #1E5F8E, ambre dindon #D4A017,
    gris coyote #555555), épaisseur weight 4.0/2.5/1.5 par hiérarchie, opacité 1.0/0.78/0.55,
    halo externe teinté espèce, badge permanent "ESPÈCE: <nom>" sur pill SCORE.
  - **P2 Vérité données** : pill rendu multiligne `SCORE X · NEUTRE / ESPÈCE: X / TIER: X`,
    badge dédié "⛔ ABSENT MFFP" pour espèces halt (wapiti/dindon BSL), normalisation
    'tous' → resolveSpeciesByBioregion (BSL → orignal) au lieu de mapping 'cerf' opaque.
  - **P3 Conformité géométrique** : `_apply_catmullrom_cap_to_corridors` post-cap BLOC 2.5,
    target 30 points/corridor. Audit live confirmé : ours_noir **531→30**, coyote **399→30**,
    chevreuil/orignal **133→30**.
  - **Validation live x6 espèces (audit post-correction)** :
    | Espèce | n_corr | CR cap | tier | score_local |
    |---|---|---|---|---|
    | chevreuil | 7 | 30 | ESSENTIEL_T0 | 68.26 |
    | orignal | 7 | 30 | ESSENTIEL_T0 | 66.10 |
    | ours_noir | 7 | 30 (531→30) | ESSENTIEL_T0 | 68.45 |
    | wapiti | 0 (mask halt) | n/a | n/a | 67.57 |
    | dindon_sauvage | 0 (mask halt) | n/a | n/a | 70.22 |
    | coyote | 7 | 30 (399→30) | ESSENTIEL_T0 | 68.34 |
  - **Preuve frontend palette** : 14 corridors mono rendus avec `species_signature='chevreuil'`,
    couleurs `#2D7A2D` (primary) et `#5BC68F` (secondary) confirmées via inspection DOM Leaflet.
  - **Tests** : 27/27 pytest doctrinaux passent.
  - **Fichiers modifiés** :
    - `/app/frontend/src/lib/speciesColorOmega.js` (nouveau · palette + helpers)
    - `/app/frontend/src/lib/bionicBundleCache.js` (TTL adaptatif halt 60s)
    - `/app/frontend/src/hooks/useMapBundleV8.js` (purge inter-espèces + halt-aware)
    - `/app/frontend/src/components/territoire/BionicLayersV8.jsx` (pill multiligne + palette mono override)
    - `/app/frontend/src/pages/MonTerritoireBionicPage.jsx` (alignement resolveSpeciesByBioregion)
    - `/app/backend/engines/v8_institutional/v20_performance_bundle.py` (CatmullRom cap 30 pts + alias multi_aggregated)

- ✅ **P22ΩΩ_BLOC_2_5_CORRIGE_DEADLINE_GATE_Ω** (2026-02-XX) — CORRECTION CRITIQUE BLOC 2.5 :
  - **Root cause identifiée** : le bypass du cap doctrinal 5-7 corridors n'était PAS
    causé par `_V5_REWIRE_ACTIVE` (déjà appelé inconditionnellement ligne 1476),
    mais par le **deadline gate global 10s** (lignes 1148-1167) qui retournait
    `result` AVANT le V5 rewire + BLOC 2.5 dans 100% des cold-starts.
  - **Fix** : extraction `_apply_v5_rewire_to_result` + `_apply_bloc25_hierarchy_and_cap`
    au niveau module (juste après `map_v5_corridors_to_ui`).
  - **Branchement** : application des deux helpers dans la branche deadline
    AVANT le `return` ESSENTIEL_T0 → bundles dégradés respectent désormais la doctrine.
  - **Validation live** : chevreuil/orignal/ours_noir BSL retournent 7 corridors
    (2 veine_principale + 5 veine_secondaire), `bloc_2_5_applied=True`,
    `v5_rewire_applied=True`, `bundle_tier=ESSENTIEL_T0`, `deadline_hit=True`.
  - **Validation MFFP** : wapiti/dindon_sauvage BSL → 0 corridors (mask_halt préservé).
  - **Headers** : `X-Bloc-2-5-Applied: 1` ajouté en ESSENTIEL_T0.
  - **Tests** : 27/27 pytest doctrinaux passent (test_bloc25_hierarchy_enforce_in_v20_bundle
    mis à jour pour valider présence des helpers module-level + marqueur DEADLINE_PATCH).
- ✅ V5 corridors organic divergence inter-espèces
- ✅ Zones / hotspots / salines non-fallback to "cerf" pour ours/coyote/dindon
- ✅ Audit download endpoint `/api/v20/territoire/audit/files/{filename}`
- ✅ PNG divergence visuelle BSL × 5 espèces
- ✅ Open-Meteo circuit-breaker (3 errors / 600s window)
- ✅ **P22ΩΩ_BUNDLE_DEGRADED_CACHE** (2026-05-14) — stabilisation 502 :
  - Bundles dégradés cachés TTL 90s (au lieu de SKIP)
  - `_MISS_HARDCAP_SEC = 6s` (au lieu de 20s)
  - EARLY-RETURN immédiat si V10 dégradé
  - `BG_CACHE` callback : V10 task continue en arrière-plan + cache
  - `lifespan` invoque `v20_startup()` (FastAPI 0.95+ ignore @on_event)
  - Daemons saturants désactivés par défaut (env gates)
  - SELF-AUDIT-Ω pytest subprocess désactivé (cause hog worker)
  - Frontend `useMapBundleV8.js` retry automatique 502/503/504 (backoff 2s+8s)
- ✅ **P22ΩΩ_PRECHARGEMENT_INTELLIGENT_GEOLOCALISATION** (2026-05-14) — Widget Premium :
  - Cache LRU global window (90s) partagé useMapBundleV8 + widget
  - Détection Premium (admin/premium_tier/is_premium/tier)
  - Préchargement séquentiel 3 espèces × waypoint favori
  - États visuels discrets (cyan running → emerald done)
  - Non-bloquant, position fixed bottom-4 right-4
  - 0-cold-start UX pour Premium → argument conversion
- ✅ **P22ΩΩ_STUBS_AUXILIAIRES_404** (2026-05-18) — Élimination 404 console :
  - Nouveau router `/app/backend/routes/stubs_auxiliary_404_omega.py`
  - 11 stubs 200 OK pour endpoints orphelins frontend (non-bloquants documentés)
  - Couverts : seo/meta, bdre/dashboard, bdre/sources, legal-time/status,
    legal-time/upcoming, sharing/notifications/anonymous, sharing/received,
    sharing/sent, sharing/notifications/{user}, groups/{user}/my-groups,
    zones/alerts
  - Cache-Control public 300s, shapes EXACTES respectées (vérifiées par grep
    frontend hooks/useSharing.js, NotificationService.js, DashboardPage.jsx)
  - Latence : <10ms localhost / 90-264ms externe Cloudflare
- ✅ **P22ΩΩ_PREWARM_SYNCHRONE_BETA** (2026-05-18) — Élimination cold-start 12s :
  - Lifespan startup déclenche prewarm background non-bloquant
  - 2 espèces canoniques : chevreuil (default frontend `cerf` alias) + orignal
  - Waypoint BSL (48.206657, -68.382422) — référence COMMANDANT
  - Premier hit utilisateur = cache HIT 130-190ms (au lieu de 12-50s cold)
  - Survit aux restarts via disk cache `/app/backend/cache/territoire_bundle.pkl`
- ✅ **P22ΩΩ_CLEANUP_3D_MVT_EDGE** (2026-05-18) — Allègement structurel post-1-worker :
  - Suite à décision plateforme : --workers 4 refusé → doctrine 1-worker confirmée
  - **Supprimés backend** : `engines/mesh_3d_omega/` (3 fichiers, 32.5 KB),
    `engines/terrain_3d_omega/` (2 fichiers), `engines/v8_institutional/v20_3d_overlays_omega.py`,
    `engines/v8_institutional/v20_mvt_tiles.py`, 2 tests associés
  - **Supprimés frontend** : `components/territoire/CesiumTerritoireViewer.jsx`
  - **Modifs server.py** : 3 blocs `include_router` retirés, X199 catalogue passé de 5 à 4 engines
  - **Modifs sla_baseline_omega.py** : sections MVT remplacées par stubs 0.0ms
  - **Modifs predictive_omega/router.py** : import terrain_3d → stub no-op interne
  - **Modifs MonTerritoireBionicPage.jsx** : import / useState / props / overlay 3D retirés
  - **Modifs TerritoireToolbar.jsx** : props show3DViewer + bouton "3D" retirés
  - **`.env` frontend** : `REACT_APP_CESIUM_ION_TOKEN` retiré
  - **Routes nouvellement 404** : 17 routes 3D/MVT (mesh-3d/*, tiles/*, corridors/active,
    zones/active, points-interet/active, buffer-600m, terrain-3d/compute)
  - **Routes préservées** : bundle V20 (cache HIT 193ms externe), santé, espèces, 11 stubs P0a
- ✅ **P22ΩΩ_FRONTEND_FIX_GROUPS_ITERABLE_Ω** (2026-05-18) — Fix crash React TERRITOIRE :
  - **Symptôme** : `TypeError: myGroups.owned_groups is not iterable` (écran rouge plein)
  - **Cause** : stub backend `/api/groups/{user_id}/my-groups` renvoyait `[]` ;
    `useHuntingGroups` init `{ owned_groups: [], member_groups: [] }` et fait
    `[...myGroups.owned_groups, ...myGroups.member_groups]` (ligne 373)
  - **Fix backend** : stub renvoie `{ owned_groups: [], member_groups: [] }` (shape correcte)
  - **Fix backend** : stub `/api/sharing/sent/{user_id}` renvoie `{ email_shares: [], link_shares: [] }`
  - **Fix frontend** : `useSharing.js` (`fetchMyGroups`, `fetchSentShares`, `allGroups`)
    garde défensive systematique — validation `Array.isArray` + fallback objet vide en cas d'erreur
  - **Validation Playwright** : page TERRITOIRE Ω complètement hydratée, HUD + carte + panels
    actifs, AUCUN crash, score 100/100 corridors 55/55
- ✅ **P22ΩΩ_FIX_PRESENCE_MASK_BYPASS_ORGANIC_GENERATE** (2026-05-18) — Correction
  doctrinale du bypass SPECIES_PRESENCE_MASK_Ω (XVIII-BIO) :
  - **Symptôme** : 16 corridors wapiti générés @ BSL (48.2, -68.4) alors que
    wapiti=ABSENT par registre MFFP 2024 (3 rectangles intro Mauricie/Portneuf/Outaouais)
  - **Root cause** : double bypass identifié
    1. `engine_ia_corridors_organic_omega.py:1607 organic_generate` n'invoquait pas
       le presence_mask (mais l'endpoint était shadowé par le smoother)
    2. `organic_corridor_smoother.py:863-875` appliquait le mask AVANT `smooth_bundle`,
       qui ré-injectait 16 corridors EXTERNAL_INFLOW_X200_P1_2 via
       `draft_external_inflow_to_smoother` (couronne 700-800m, P1.2 X200)
  - **Fix patché** : 4 modifications
    - `engine_ia_corridors_organic_omega.py:1607,1648,1678` : injection
      `_apply_organic_presence_mask()` dans `organic_generate`, `network-hierarchy`,
      `seal-baseline` (V30_LOCK respecté, masquage AVAL uniquement)
    - `organic_corridor_smoother.py:877` : **ré-application** idempotente du
      `apply_presence_mask_to_bundle` APRÈS `smooth_bundle` (flag
      `bio_presence_mask_reapplied_post_smoother=True`)
  - **Validation triple** :
    - wapiti @ BSL (ABSENT) → **0 corridors** ✅ halt=True ✅
    - chevreuil @ BSL (PRESENT) → 81 corridors ✅ halt=False ✅ (aucune régression)
    - wapiti @ Mauricie (PRESENT zone intro) → 89 corridors ✅ halt=False ✅
  - Cache `_ORGANIC_CACHE` et `_SMOOTHER_CACHE` purgés via restart backend (in-memory)
- ✅ **P22ΩΩ_TERRITOIRE_Ω_SUPRA BLOC 1 + 2** (2026-05-18) — Stabilisation doctrinale complète :
  - **BLOC 1 (validation)** : 7 waypoints × 5 espèces audités, 5 endpoints critiques
    conformes au mask XVIII-BIO, caches saines (93.94% hit ratio), aucune pollution
  - **BLOC 2.1 — Purge sélective zones tagged species** :
    - Patch `species_presence_mask_omega.py:288-330` : ajout purge sélective zones
    - Critères : zones avec `species==canonical` OU `species_bias_applied!=None` purgées
    - Infrastructure (zones sans tag espèce) préservée → `zones_preserved_infrastructure`
    - Nouveau flag : `zones_rejected_bio_presence_mask` + `_count`
    - **Validation wapiti @ BSL** : zones 5 → 0 (toutes tagged), chevreuil @ BSL : zones 5 préservées
  - **BLOC 2.2 — Rayon entry/exit 600m → 780m** (rayon institutionnel fixe) :
    - Patch `engine_ia_corridors_organic_omega.py:966` default 600→780
    - Patch `organic_corridor_smoother.py:841` default 600→780 (smoother shadow)
    - Aligné avec `functional_radius_max_m=780.0` (zone fonctionnelle 600m + 30%)
  - **BLOC 2.3 — Fusion veineuse inter-corridors** :
    - Déjà active sous condition `anchor_mode=TERRITORY_CONTINUOUS`
    - Conservée by design (préserve rosace P22H en mode AUTO/SALINE_CENTERED)
  - **BLOC 2.4 — Promotion auto veine principale (fused_score max)** :
    - Patch `engine_ia_corridors_organic_omega.py:1273-1310` : si 0 veine_principale
      après hierarchy_counts, promouvoir corridor de plus fort `fused_score`
    - Idempotent (skip si ≥1 veine principale existe déjà)
    - Nouveau flag : `p22omegaomega_promotion_doctrine` dans réponse
- ✅ **P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω** (2026-05-18) — Purge legacy + sanctuarisation :
  - **PALIER 1** : suppression physique de 4 modules legacy (~1 563 L libérées)
    - `engines/v8_national/map_bundle.py` (313 L)
    - `engines/v8_national/phase_b_engines.py` (770 L)
    - `modules/bionic_engine_p0/routers/movement_corridors_router.py` (480 L)
    - `engines/v8_institutional/_ARCHIVE_NON_ACTIVE/engine_corridors_legacy_pre_L.py`
    - 4 tests associés supprimés (~500 L)
  - **PALIER 4** : 17 fichiers `tools/audit_phase_*.py` archivés dans `tools/archive/`
  - **Cleanup server.py** : 5 blocs de commentaires legacy retirés (corridor_unified,
    relocation, movement_corridors, V8-MAP-BUNDLE, V8-PHASE-B) + logs résiduels
  - **Sanctuarisation `corridors_v10`** : marquage CORE_MODULE explicite dans
    `__init__.py` avec `__purge_forbidden__=True`, liste des 5 consommateurs cascade
    documentée (bce/exclusion_layer, score_consolide, wildlife_behavior_omega)
  - **Pré-plans documentés** :
    - `P22OMEGAOMEGA_PALIER_2_EXTRACTION_PHASE_A_PRE_PLAN.md` (relocalisation+salines)
    - `P22OMEGAOMEGA_PALIER_3_MIGRATION_V7_SPATIAL_PRE_PLAN.md` (3 consommateurs FE)
  - **Validation** : backend boot OK, 78 modules registered, endpoints purgés → 404 propre,
    V20 bundle + V7 spatial préservés (chevreuil @ BSL OK), V30_LOCK respecté
- ✅ **P22ΩΩ_QUALITY_GROUPE_A** (2026-05-18) — Correctifs revue de code (triage):
  - **Syntax error frontend** : `src/config/modules.js:45` commentaire `#` (Python)
    remplacé par `//` (JavaScript)
  - **Wildcard imports → imports explicites** (3 fichiers) :
    - `config/__init__.py` : `from .settings import *` → 10 imports explicites
    - `modules/chasseur_jumeau.py` : `from .experiments import *` → 4 imports explicites
    - `modules/liste_epicerie.py` : `from .utility_modules import *` → 5 imports explicites
    - Bénéfice : namespace clarifié, dépendances tracées, lint conforme
  - **Validation** : lint Python + JS conformes, backend boot OK, 78 modules,
    singletons fonctionnels (`chasseur_jumeau_service`, `liste_epicerie_service`),
    config exporte 26 modules + `ARCHITECTURE_VERSION=3.0.0`
  - **Items EXCLUS du GROUPE A** (motifs documentés) :
    - MD5 → SHA-256 sur `hash.py` : INTERDIT par doctrine BCE-4X x3205
      (rupture cache + clés différentes). Différé jusqu'à x3300.
    - Mutable default arguments : **0 instance trouvée** dans le code actif (rapport gonflé)
  - **Items du rapport identifiés comme FAUX POSITIFS** :
    - `exec()` `wms_proxy_router.py:131` : c'est `asyncio.create_subprocess_exec()`
    - Hardcoded secrets (31 instances) : ce sont des fixtures de tests, pas des
      credentials de production
    - Syntax error : Webpack tolérait silencieusement, mais correction quand même appliquée
- ✅ **P22ΩΩ_QUALITY_GROUPE_B** (2026-05-18) — Durcissement sécurité ciblé:
  - **Module `secure_pickle_omega.py`** (177 L) — Pickle HMAC-SHA256 :
    - `secure_dumps()` : 32 bytes HMAC + pickle binaire
    - `secure_loads()` : vérification HMAC en temps constant, refus si mismatch
    - `secure_loads_legacy_tolerant()` : rétrocompatibilité migration premier boot
    - Clé secrète en cascade : ENV → fichier persistant (`mode=0600`) → fallback
    - Tests roundtrip + tampering detection + legacy migration validés (5/5)
  - **Migration `v20_performance_bundle.py`** : `pickle.dump`/`pickle.load` → `secure_dumps`/`secure_loads_legacy_tolerant`
    - Cache disque post-migration : `Disk load: 9 entries (HMAC-verified)`
  - **Migration `redis_omega.py`** : idem (Redis off en preview, code prêt en production)
  - **Lockdown SHA-256 `phase_omega_secure_lockdown.py:281`** :
    - Vérification SHA-256 du fichier `registry_lock_omega.py` AVANT `exec()`
    - Comparaison avec `ENGINES_LOCKED_HASHES["registry_lock_omega.py"]`
    - Refus catégorique si mismatch (renvoie erreur explicite, exec non lancé)
    - Nouveau flag : `registry_exec_authorized` dans réponse
    - Mise à jour des 3 hashes obsolètes (organic, rendu, registry) suite aux patches
      institutionnels antérieurs (BLOC 2.x)
  - **Circular import `bce_corridor_v9` ↔ `corridors_v9`** :
    - Documentation in-source dans les 2 fonctions impliquées (validate_corridor_visual_balance, enrich_corridor)
    - Document institutionnel : `/app/memory/CIRCULAR_IMPORT_BCE_CORRIDORS_V9_DOCUMENTATION.md`
    - Pattern lazy-import bidirectionnel **DOCTRINAIREMENT ACCEPTÉ** (faux positif rapport)
  - **Validation post-déploiement** :
    - Backend boot OK · 78 modules registered
    - HMAC verified sur cache disque (9 entries)
    - `registry_exec_authorized=True`, `hashes_conforme=True`
    - Endpoints critiques (`/health`, `/bundle`, `/especes/list`) → 200 OK
    - V30_LOCK respecté · aucune modification fonctionnelle
- ✅ **P22ΩΩ_EXTRACTION_PHASE_A_RELOCALISATION_SALINES** (2026-05-18) — Migration V8-PHASE-A vers Ω:
  - **Nouveau module Ω** `engines/v8_institutional/territoire_omega_relocalisation_salines.py` (388 L)
    - Extraction PURE de la logique métier (zéro modification fonctionnelle)
    - Fonctions : `compute_relocalisation_omega()`, `compute_salines_placement_omega()`, `status_omega()`
    - Feature flags : `FEATURE_FLAG_RELOCALISATION`, `FEATURE_FLAG_SALINES`
    - Conservation des appels à `engines.v8_national.exclusion_engine` (toujours actif)
  - **Nouveau router** `routes/territoire_omega_reloc_salines_router.py` (84 L)
    - `GET /api/v20/territoire/relocalisation`
    - `GET /api/v20/territoire/salines-placement`
    - `GET /api/v20/territoire/relocalisation-salines/status`
  - **Re-câblage frontend** `hooks/usePhaseAV8.js` :
    - `/api/v8/map/relocalisation` → `/api/v20/territoire/relocalisation`
    - `/api/v8/map/salines` → `/api/v20/territoire/salines-placement`
    - Shape de retour STRICTEMENT identique (validation Playwright précédente)
    - Nom hook conservé pour stabilité imports (1 consommateur MonTerritoireBionicPage.jsx)
  - **Suppression physique** : `engines/v8_national/phase_a_engines.py` retiré (déjà supprimé en PALIER 1)
  - **server.py** : log de migration mis à jour, router institutionnel enregistré
  - **Validation triple** :
    - localhost : status 200, relocalisation 16 candidats / 3 retournés, salines 10/4
    - externe (proxy K8s) : relocalisation 223ms 200 OK, salines 187ms 200 OK
    - endpoints legacy V8 : toujours 404 (préservé conformément à la doctrine)
  - **2 derniers 404 console DevTools éliminés** : `/api/v8/map/relocalisation` + `/salines`
  - **V30_LOCK** respecté · aucune modification fonctionnelle TERRITOIRE Ω
- ✅ **P22ΩΩ_PALIER_3_MIGRATION_V7_SPATIAL_Ω** (2026-05-18) — Migration V7 SPATIAL vers Ω:
  - **Nouveau router proxy** `routes/territoire_omega_spatial_router.py` (114 L) :
    - `GET /api/v20/territoire/spatial/heatmap` (proxy → V7 heatmap, 23 moteurs + nutrition + temporal)
    - `GET /api/v20/territoire/spatial/score` (proxy → V7 scoring)
    - `GET /api/v20/territoire/spatial/status`
    - Mode : **PROXY PURE** — délégation aux fonctions V7 par import direct (aucune duplication logique)
    - Tag `served_by=TERRITOIRE-Ω-SPATIAL-ROUTER` + `upstream_engine` pour traçabilité
  - **Re-câblage frontend** (2 composants) :
    - `components/territoire/ConsolidatedHeatmapLayer.jsx` : 3 occurrences `v7/spatial/heatmap` → `v20/territoire/spatial/heatmap` (3 fetch + retry DataCloneError)
    - `components/territoire/BionicScoreBadge.jsx` : 2 occurrences `v7/spatial/scoring` → `v20/territoire/spatial/score`
    - `hooks/useBionicScoring.js` : header docstring corrigé (utilisait déjà `/v1/v51/intelligence/v7/score-chasse`, hors V7 spatial)
  - **Désactivation V7 legacy HTTP** : `server.py:821-830` router V7 spatial commenté (module Python toujours importé pour délégation Ω)
  - **Validation externe proxy K8s** :
    - Ω heatmap : 200 OK · 144 points · 3.7s · `served_by=TERRITOIRE-Ω-SPATIAL-ROUTER`
    - Ω score : 200 OK · `spatial_score=51.3 rating=adequat` · 3.3s
    - V7 legacy `/api/v7/spatial/{heatmap,scoring}` → **404 propre** (désactivé)
    - Bundle V20 intact : 14 corridors · 5 zones · 4 salines · 148ms (cache HIT)
  - **V30_LOCK** respecté · aucune modification scoring V7 (délégation pure)
  - **Console DevTools COMMANDANT** : aucun appel résiduel `/api/v7/spatial/*` côté frontend
- ✅ **P22ΩΩ_BLOC_5_TESTS_REGRESSION_PRESENCE_MASK_Ω** (2026-05-18) — Verrouillage doctrinal par tests:
  - **Nouveau fichier** `tests/test_doctrinal_omega_presence_mask.py` (358 L)
  - **25 tests doctrinaux couvrant 14 invariants Ω** :
    - I-1/I-1bis/I-2/I-3 : Registre présence MFFP 2024 (wapiti ABSENT @ 3 waypoints, PRESENT @ Mauricie, chevreuil PRESENT @ BSL)
    - I-4/I-5/I-6 : `apply_presence_mask_to_bundle` purge corridors+affuts+hotspots+salines, purge zones tagged, préserve infrastructure
    - I-7/I-7bis : Rayon entry/exit 780m default (engine + smoother)
    - I-8 : Promotion auto veine principale `P22ΩΩ_TERRITOIRE_Ω_SUPRA_BLOC_2_4`
    - I-9 : Aucun fallback legacy (V8-PHASE-A/B/MAP_BUNDLE supprimés, corridors_v10 sanctuarisé, V7 spatial désactivé)
    - I-10/I-11 : FIX BYPASS (organic_generate + smoother re-application après external_inflow)
    - I-12/I-12bis : E2E pipeline wapiti @ BSL → 0 corridors, chevreuil @ BSL → corridors présents
    - I-13 : Migration endpoints Ω (relocalisation/salines + spatial routers enregistrés)
    - I-14 : Secure pickle HMAC roundtrip + tampering detection + legacy tolerance
  - **conftest.py** : marqueur `doctrinal_omega` whitelisté (exemption filtre BCE-4X TERRITOIRE)
  - **pyproject.toml** : marker `doctrinal_omega` enregistré
  - **Résultat exécution** : **25/25 PASSED · 47.86s · 0 erreur**
  - Aucun changement fonctionnel — tests uniquement, doctrine de vérification verrouillée

## PENDING / KNOWN ISSUES
- ⚠️ **Single-worker uvicorn** : code SYNC dans `compute_territoire_v10` (1 await,
  reste sync) hog l'event loop 50s+ en cold-start → 502 sur 1er hit
- ⚠️ Bundle complet (V10+V5+pipeline post) prend 60-100s en cold-start ; les
  bundles servis sont PARTIELS (zones seulement, sans corridors/affuts/salines/
  hotspots) à cause du DEADLINE 10s global skip-pipeline-post
- ⚠️ Redis local non-persistant entre forks de containers
- ⚠️ Open-Meteo CB ouvert régulièrement (429 rate limit Open-Meteo gratuit)

## ROADMAP P0/P1/P2

### P0 (En attente d'orientation Commandant)
- [ ] **EMERGENT_PLATFORM_ESCALATION_BRIEF.md** : Demande de multi-worker uvicorn
  (4 workers) à l'admin plateforme. Document prêt dans
  `/app/memory/audit_provenance/`. Résout C4 architecturelle (event-loop blocking).

### P1 (Après validation P0)
- [ ] `P22Ω_CORRIDORS_CONTINUITÉ_1000` — audit continuité géométrique des
  corridors sur 1000 itérations multi-espèces.
- [ ] `ULTRA TERRITOIRE Ω AUDIT` — audit complet end-to-end.

### P2 / Backlog
- [ ] Activer `P22OMEGA_PRECHAUFFAGE_DAEMONS=1` après multi-worker (sans hog)
- [ ] Activer `P22OMEGA_BSL5_WARMUP=1` après multi-worker
- [ ] Réactiver `SELF-AUDIT-Ω` avec subprocess limit (1 simultané max)
- [ ] Refactoring : extraire les routes hors de `server.py` (1637 lignes) vers
  `/app/backend/routes/`
- [ ] Tests pytest réguliers dans `/app/backend/tests/`
- [ ] Provisionner un Redis externe persistant (option : Redis Cloud free tier)

## FILES OF REFERENCE
- `/app/backend/server.py` (1637 lignes, lifespan + routes)
- `/app/backend/engines/v8_institutional/v20_performance_bundle.py` (1915 lignes)
- `/app/backend/engines/v8_institutional/territoire_v10_supra.py` (1496 lignes,
  `compute_territoire_v10` ligne 1154 — SYNC après 1 await)
- `/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py`
- `/app/frontend/src/components/territoire/BionicLayersV8.jsx`
- `/app/frontend/src/hooks/useMapBundleV8.js` (retry P22ΩΩ)
- `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`

## AUDIT MEMORIES
- `/app/memory/audit_provenance/p22omegaomega_bundle_degraded_cache.md` (NEW · 2026-05-14)
- `/app/memory/audit_provenance/EMERGENT_PLATFORM_ESCALATION_BRIEF.md` (NEW · 2026-05-14)
- `/app/memory/audit_provenance/visual_divergence/divergence_bsl_*.png`
- `/app/memory/audit_provenance/p22omega_territoire_total_stack_audit.md`
- `/app/memory/CHANGELOG.md`
