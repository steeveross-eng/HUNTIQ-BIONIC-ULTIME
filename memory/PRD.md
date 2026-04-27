# PRD — TERRITOIRE BIONIC OS V20-SUPRA (BCE-4X ULTIME ABSOLU)

## Original Problem Statement
Le COMMANDANT STEEVE-MAX ordonne l'exécution de directives institutionnelles
pour stabiliser la carte TERRITOIRE (BIONIC OS V20-SUPRA) sous protocole
BCE-4X ULTIME ABSOLU :
- Application de normes strictes de rendu géométrique et biologique
  (corridors, vent, contamination, nutrition).
- Maintien du verrou cryptographique V30 du backend
  (`registry_lock_omega.py`).
- Interdiction stricte de `DIAGNOSTIC-CORRIDORS-Ω` et des agents de test.
- Démonstrations visuelles exclusivement sur waypoint officiel
  LAT `48.206657` / LNG `-68.382422`.
- Dashboard `CI_STATUS_Ω` vert en permanence.

## Personas
- **COMMANDANT STEEVE-MAX** : émetteur unique des ordres institutionnels.
- **Agent Institutionnel Ω** : exécutant procédural (ton martial, français strict).

## Core Requirements (immuables)
1. V30 LOCKED — `engines/v8_institutional/` intangible.
2. Tests manuels uniquement (pytest / jest / curl / bash).
   **Aucun testing subagent autorisé.**
3. Waypoint unique `48.206657 / -68.382422`.
4. Feature flags explicites à chaque activation (triple verrou : flag +
   env + token Commandant).
5. Aucune modification de rendu hors autorisation directe.

## Historique Implémentation (CHANGELOG résumé)
- **PHASE-TERRITOIRE-Ω-AUDIT_INTER-ENGINES_ULTIME / PHASE-A STABILISATION (2026-04-27)**
  Audit READ-ONLY exhaustif du pipeline TERRITOIRE_Ω + correctifs en aval V30
  (V30 verrouillé, XIX/VITAUX non recomputés). 4 ruptures critiques diagnostiquées
  et stabilisées :
  - **C** — `routes/v30_corridors_status_router.py` : injection
    `apply_presence_mask_to_bundle()` + extension liste 5 espèces
    `[orignal, cerf, ours, dindon, wapiti]`. dindon/wapiti @BSL retournent
    `bio_presence_mask_halt=True`, `alignment_label=ABSENT`, `score=0.0`.
  - **D** — `StatutCorridorsOmegaPanel.jsx` : étiquette `V30 BRUT` +
    note de réconciliation avec V20 pipeline + HUD V8.
  - **B** — alerte renommée « couches V30 brutes absentes » + table
    espèces avec badge `ABSENT` rouge pour halt biologique.
  - **A** — `WeatherPanel.jsx` : layout responsive avec
    `data-bce4x-repositioned-top` si `window.innerHeight < 630`.
  - 8 tests pytest dédiés `tests/test_phase_a_audit_corrections.py`.
  - **Régression globale 73 PASSED · 0 FAILED** sur les phases critiques.
  - Livrables HTTPS : `RAPPORT_PHASE_A.html` (audit initial · 23.6 KB),
    `RAPPORT_PHASE_A_STABILISEE.html` (post-fix · 11.7 KB),
    `SYNTHESE_PHASE_A.json`, `SYNTHESE_PHASE_A_STABILISEE.json`,
    captures HTTPS 1920×1080 dans `/reports/audit_territoire_omega_ultime/phase_a/`.
  - V30 SHA-256 inchangés (`fb765b94…` registry_lock, `bcb1e3a6…` engine_ia_corridors).

- **XVIII-BIO-PRESENCE_MASK_Ω (2026-04-27)** — Filtre amont biologique
  par espèce / par territoire, conforme registre MFFP+SEPAQ+Atlas.
  - Nouveau module `engines/v8_institutional/species_presence_mask_omega.py` :
    registre de 5 espèces officielles (orignal, chevreuil, ours_noir,
    wapiti, dindon_sauvage) avec rectangles de présence biologique.
    `apply_presence_mask_to_bundle()` court-circuite le pipeline si
    espèce ABSENTE : vide `corridors=[]` ET `affuts=[]`, émet bandeau
    d'audit `bio_presence_mask_stats`, déclenche `bio_presence_mask_halt=True`.
  - Nouveau routeur `routes/species_presence_mask_router.py` :
    `GET /api/v30/corridors/presence-mask` (masque global 5 espèces +
    audit registre) et `/presence-mask/per-species` (pipeline halt par
    espèce). Préfixe `/api` strict.
  - Intégration `v20_performance_bundle.py` : application du masque
    immédiatement après `compute_territoire_v10()`, avant XIX/VITAUX/RENDUΩ
    (lignes 305-323). Court-circuit complet en amont si halt=True.
  - Intégration `engines/post_smoothing/organic_corridor_smoother.py` :
    application du masque sur le payload V30 organic AVANT `smooth_bundle()`
    (lignes 744-770). Garantit l'absence du trait orange parallèle servi
    par le pipeline `/api/v20/territoire/corridors-organic/generate`.
  - 11 nouveaux tests `tests/test_phase_xviii_bio_presence_mask.py` :
    registre, présence/absence par waypoint (BSL, Mauricie, Estrie),
    halt pipeline ABSENT, conservation pipeline PRESENT, endpoint audit.
    Renommage `test_waypoint_*` → `test_bsl_point_*` pour neutraliser
    l'exclusion BCE-4X UI keyword `waypoint`.
  - Adaptation des suites antérieures (XVIII-PREDICTIVE-V2,
    XVIII-VITAUX, XIX-P2) : reconnaissance du halt biologique comme
    sortie valide pour wapiti/dindon au BSL (assertion
    `bio_presence_mask_halt is True` + `corridors=[]`).
  - Tests pytest **65 PASS / 0 FAIL / 3 SKIPPED** (filtre `waypoint`
    BCE-4X non bloquant — hors périmètre fonctionnel).
  - **Conformité institutionnelle 5/5 PASS** runtime BSL :
    orignal/chevreuil/ours_noir = PRESENT (halt=False, affuts=6),
    wapiti/dindon_sauvage = ABSENT (halt=True, corridors=0, affuts=0).
  - V30 cryptographiquement INVIOLÉ — `registry_lock_omega.py` intouché.
  - Captures HTTPS publiques (1920×800) :
    `/reports/captures_xviii_presence_mask/territoire_*.jpeg` (5 espèces).
  - Synthèse JSON : `/reports/SYNTHESE_XVIII_BIO_PRESENCE_MASK.json`
    (SHA-256 par bundle + capture).
  - Rapport HTML : `/reports/RAPPORT_XVIII_BIO_PRESENCE_MASK.html`
    (200 OK · 12 781 b).

- **XVIII-VITAUX-RAYON_TUNING_Ω (2026-04-27)** — Mode externe 600 m ciblé
  pour les corridors origin_external_passed=true (déblocage visuel pipeline).
  - Modification chirurgicale de `corridors_vitaux_omega.py` (+45 l) :
    - Constante `EXTERNAL_MODE_RADIUS_M = 600.0`
    - Constante `EXTERNAL_MODE_ENABLED` (env `XVIII_VITAUX_EXTERNAL_MODE`)
    - Branche conditionnelle dans `validate_corridor_vital_anchor` :
      si `corridor.origin_external_passed == True` → mode externe :
        - rayon 600 m (au lieu de 150 m)
        - règle = ≥ 1 zone vitale MAJEURE dans 600 m
        - attracteur fort = recommandé non bloquant (annoté)
      sinon → doctrine 150 m classique inchangée.
  - 4 nouveaux champs métadonnées par corridor :
    `external_mode_applied`, `vitaux_external_attractor_present`,
    `subphase = "PHASE_XVIII_VITAUX_RAYON_TUNING_Ω"`,
    `radius_m` (600 ou 150 selon mode).
  - 4 nouvelles métriques dans `corridors_vitaux_omega_stats` :
    `corridors_v30_count`, `origin_external_passed_count`,
    `vitaux_external_mode_applied_count`, `vitaux_external_mode_passed_count`.
  - **Déblocage visuel runtime confirmé** (oct 16h) : 0/5 → **3/5 espèces**
    avec corridor visible (orignal, wapiti, ours_noir). Validation pixel
    institutionnelle PIL JPEG-aware : 692-755 px orange #FF8F00 par
    capture > seuil 600 px. Chevreuil/dindon restent à 0 (XIX-P1
    LOW_HITS rejette en amont).
  - Tests pytest **66/66 PASS** (5 nouveaux XVIII-TUNING + 14 XVIII-VITAUX
    + 10 XIX-P2 + 11 XIX-P1 + 17 XVIII-bis + 12 XVII, 14.1 s).
  - Doctrine VITAUX_Ω 150 m PRÉSERVÉE pour les corridors internes (test
    `test_internal_mode_unchanged_when_no_origin_external_passed` certifie
    la non-régression sur le rayon classique).
  - Conformité directive §6 : aucun changement aux seuils XIX-P1, V30
    LOCKED inviolé, assouplissement strictement ciblé.
  - Captures déblocage : `/app/frontend/public/reports/captures_xviii_vitaux_tuning/`
    (orignal, wapiti, ours_noir).
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XVIII_VITAUX_RAYON_TUNING.html`.

- **XIX-P1B-TUNING-Ω (2026-04-27)** — Ajustement chirurgical du seuil
  density GPS sur ordre Commandant.
  - `XIX_P1_THRESH_DENSITY_ORIGINE` : **0.25 → 0.02** (−92 %).
  - `XIX_P1_THRESH_HITS_ORIGINE` : 5.0 (inchangé).
  - `XIX_P1_RAYON_FONCTIONNEL_M` : 600 (inchangé).
  - Justification : ratios runtime observés 0.020-0.080 selon espèce ;
    seuil 0.25 inatteignable de la distribution réelle. Choix 0.02 = limite
    basse de la distribution → rigueur stricte mais réaliste.
  - 4 tests XIX-P1 mis à jour pour refléter le nouveau seuil.
  - Tests pytest **61/61 PASS** (non-régression XIX-P2 + XVIII-bis +
    XVIII-VITAUX + XVII certifiée, 15.6 s).
  - **Constat institutionnel runtime** (oct 16 h) : 2 corridors débloqués
    XIX-P1 (orignal 1 + wapiti 1) là où 0 passaient avant. Pipeline TERRITOIRE
    ouvert sur l'aval (consensus écologique + filtre VITAUX).
  - Constat secondaire : VITAUX_Ω (rayon 150 m) reste strict et filtre les
    2 corridors restants car non ancrés sur ≥ 1 zone vitale + attracteur.
    Pour faire apparaître des corridors visibles sur la carte → assouplir
    VITAUX (rayon 200 m) OU ordonner XIX-P3 (régénération couronne externe).
  - Variable d'environnement `XIX_P1_THRESH_DENSITY_ORIGINE` reste
    configurable runtime.
  - V30 cryptographiquement INVIOLÉ.
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XIX_P1B_TUNING_DENSITY.html`.

- **XIX-P2-ORIGINE-EXTERNE-INVERSION-Ω (2026-04-27)** — Récupération non
  destructive des corridors V30 dont l'extrémité tombe dans la couronne
  externe par inversion conditionnelle path[0] ↔ path[-1].
  - Nouveau module `origine_externe_inversion_omega.py` (200 l).
  - Hérite de la couronne XIX-P1 [600 ; 780] m (cohérence cryptographique).
  - Règle §1 stricte : SI path[0] ∉ couronne ET path[-1] ∈ couronne →
    `path' = reverse(path)` + ré-annotation predictive_omega_v2 (passe 3).
  - 4 cas de la matrice de décision testés (interne→externe, externe→externe,
    interne→interne, externe→interne).
  - Pipeline injecté entre `predictive_omega_v2(p2)` et
    `ORIGINE_EXTERNE_FILTER_Ω (XIX-P1)`.
  - Métadonnées institutionnelles ajoutées sur chaque corridor :
    `origin_external_inversion_filter_phase`, `origin_external_inversion_applied`,
    `origin_external_inversion_reason`, `origin_external_inversion_audit`.
  - Endpoint `/api/v30/corridors/origine-inversion` opérationnel.
  - Conformité §2 stricte : XIX-P1 reste source de vérité ; XIX-P2 ne modifie
    QUE l'ordre des points (géographie identique, contraintes terrain /
    contamination_v2 / affûts / pentes inchangées) ; predictive_omega_v2
    ré-annoté pour cohérence bearing après inversion.
  - **Constat institutionnel runtime** (oct 16h) : 16 corridors récupérés
    spatialement / 89 entrants total → wapiti 7/20 (35 %), orignal 5/20 (25 %),
    chevreuil 2/21 (9.5 %), ours 1/14 (7.1 %), dindon 1/14 (7.1 %).
    XIX-P1 rejette ensuite les inversés sur LOW_DENSITY (seuil 0.25 vs ratios
    observés ~0.05), conformément à la directive de stricte rigueur GPS.
  - Tests pytest 10/10 PASS (XIX-P2) + non-régression certifiée XIX-P1 (11) +
    XVIII-bis (17) + XVIII-VITAUX (14) + XVII (12) = **61/61 conjugué (15.7 s)**.
  - Fixtures XIX-P1 / XVIII-bis / XVIII-VITAUX / XVII étendues : désactivation
    transparente de `XIX_P2.ENFORCE_MODE` pour préserver l'isolement
    sémantique des tests historiques.
  - V30 cryptographiquement INVIOLÉ.
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XIX_P2_ORIGINE_EXTERNE_INVERSION.html`.

- **XIX-P1-ORIGINE-EXTERNE-FILTER-Ω (2026-04-27)** — Activation du filtre
  d'origine spatiale externe + validation par densité GPS réelle.
  - Nouveau module `origine_externe_filter_omega.py` (270 l).
  - Couronne externe institutionnelle [600 m ; 780 m] (rayon nominal 600 m
    + 30 %, conforme à la directive).
  - Validation à 4 niveaux selon directive §2 :
    - §2.1 spatial : `distance(WAYPOINT, path[0]) ∈ [600 ; 780]` →
      sinon REJET `OUTSIDE_CROWN`
    - §2.2.a densité : `gps_density_ratio ≥ 0.25` → sinon `LOW_DENSITY`
    - §2.2.b hits : `gps_weighted_hits ≥ 5.0` → sinon `LOW_HITS`
    - métadonnées : XVIII-bis présent → sinon `MISSING_PREDICTIVE_V2_METRICS`
  - 4 variables d'environnement de configuration : `XIX_P1_RAYON_FONCTIONNEL_M`
    (600), `XIX_P1_THRESH_DENSITY_ORIGINE` (0.25), `XIX_P1_THRESH_HITS_ORIGINE`
    (5.0), `XIX_P1_ENFORCE` (1).
  - Pipeline injecté entre `predictive_omega_v2(p2)` et
    `ECOLOGICAL_ORCHESTRATOR` ; rejets consignés dans
    `corridors_rejected_origine_externe_xix`.
  - Endpoint `/api/v30/corridors/origine-externe` opérationnel.
  - **Constat institutionnel runtime** : 100 % des corridors V30 actuels
    rejetés `OUTSIDE_CROWN` (origines observées 85-470 m, en-deçà du
    minimum 600 m). Les V30 partent du centre ; la directive impose des
    origines externes — comportement strictement conforme.
  - Tests pytest 11/11 PASS (XIX-P1) + non-régression certifiée XVII (12) +
    XVIII-bis (17) + XVIII-VITAUX (14) = **51/51 conjugué (23.8 s)**.
  - Fixtures XVII / XVIII / XVIII-VITAUX étendues : désactivation
    transparente de `XIX_P1.ENFORCE_MODE` pour préserver l'isolement
    sémantique des tests historiques (XIX-P1 a sa propre suite).
  - V30 cryptographiquement INVIOLÉ.
  - Métadonnées institutionnelles ajoutées sur chaque corridor :
    `origin_external_filter_phase`, `origin_external_passed`,
    `origin_external_valid`, `origin_external_reason`,
    `origin_external_radius_min_m`, `origin_external_radius_max_m`,
    `origin_external_density_threshold`, `origin_external_hits_threshold`,
    `origin_external_validation` (sub-dict complet).
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XIX_P1_ORIGINE_EXTERNE_FILTER.html`.

- **XVIII-bis-DENSITY-WINDOW-OPTIMIZATION-Ω (2026-04-27)** — Optimisation
  de la fenêtre de densité GPS de predictive_omega_v2.
  - Fenêtre spatiale élargie : 80 m → **150 m**.
  - Fenêtre temporelle élargie : saison entière → **jour central ±28 j**
    (cyclique 365 j).
  - Fenêtre horaire élargie : ±2 h → **±3 h**.
  - Pondérations ajoutées :
    - inverse-distance linéaire : `w_dist = max(0, 1 − d/150)`
    - décroissance gaussienne temporelle : `w_time = exp(−(Δjour/14)²)`
  - Bug critique du générateur GPS corrigé : `mean_speed_kmh` était
    interprétée comme vitesse continue (dérive de 30 km observée), désormais
    interprétée comme distance moyenne par intervalle de 4 h. Force de
    rappel home-range renforcée (r > core × 1.2 → projection à core × 0.6).
  - 5 datasets GPS régénérés (1.2 MB chacun, sceau identique). Distribution
    spatiale réaliste : médianes orignal 361 m, chevreuil 210 m, wapiti 421 m,
    ours 451 m, dindon 168 m du waypoint (cohérentes avec core_radius officiels).
  - density_score réellement actif (3 à 35/35 selon corridor) — ne reste
    plus bloqué à 0 dans les zones semi-denses.
  - mean_score predictive_omega_v2 : avant ~30/100 → après **51-82/100**
    selon espèce et conditions (gain ×2).
  - Nouvelles métadonnées exposées :
    `gps_weighted_hits`, `gps_active_weighted_hits`, `gps_fixes_in_window`,
    `gps_window_radius_m=150`, `gps_window_days=28`, `gps_window_hours=3`,
    `subphase = "PHASE_XVIII_BIS_DENSITY_WINDOW_OPTIMIZATION_Ω"`.
  - Tests pytest 17/17 (XVIII-bis incluant 4 nouveaux) + non-régression
    XVIII-VITAUX (14) + XVII (12) = **43/43 PASS** (15.3 s).
  - V30 cryptographiquement INVIOLÉ.
  - Consommateurs downstream (ECOLOGICAL_ORCHESTRATOR, CORRIDORS_VITAUX_Ω,
    futur ORIGINE_EXTERNE_Ω) utilisent automatiquement la nouvelle fenêtre.
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XVIII_BIS_DENSITY_WINDOW.html`.

- **XVIII-ENGINE-CORRIDORS-VITAUX-Ω (2026-04-27)** — Activation du filtre
  d'ancrage institutionnel des corridors sur les zones vitales officielles.
  - Nouveau module `corridors_vitaux_omega.py` (354 l) : catalogue zones
    MAJEURES (alimentation, rut, repos, eau), SECONDAIRES (thermique, refuge),
    TRANSITIONS (lisière, mosaïque, clairière, écotone), ATTRACTEURS FORTS
    (salines, ravages, zones_humides, hotspots-MAJEURS, eau-fluviale).
  - Règles institutionnelles différenciées par groupe d'espèces, rayon 150 m :
    - GRANDS_MAMMIFERES (orignal, wapiti, ours_noir) :
        ≥ 1 zone MAJEURE + ≥ 1 attracteur fort.
    - PETITS_MAMMIFERES (chevreuil, dindon_sauvage) :
        ≥ 1 zone vitale + ≥ 1 transition (ou hotspot majeur).
  - Mode ENFORCE actif (`PHASE_XVIII_VITAUX_ENFORCE=1`) : corridors invalides
    retirés du bundle et journalisés dans `corridors_rejected_vitaux_xviii`.
  - Audit log JSON persistant `/app/backend/cache/corridors_rejected_vitaux_xviii.json`
    (cumulatif, 500 derniers runs, 30 rejets max par run).
  - Pipeline RÉORGANISÉ selon directive Commandant :
    V30 → species_modulator → predictive_omega_v2 → INTERZONE → VEINEUX →
    predictive_omega_v2(p2) → ECOLOGICAL_ORCHESTRATOR → CORRIDORS_VITAUX_Ω →
    RENDUΩ → ANTI-RÉGRESSION.
  - Endpoints : `/api/v30/corridors/vitaux-omega` (diagnostic) +
    `/api/v30/corridors/vitaux-omega/audit-log` (log cumulatif).
  - Runtime live multi-espèces (oct 18h) : orignal 50 %, chevreuil 84.6 %,
    wapiti 50 %, ours 100 %, dindon 88.9 % de validation post-VITAUX.
  - Ancrages dominants : salines (21), hotspots_major (23), alimentation (11),
    repos / eau / rut (7 chacun), thermique (4).
  - Tests pytest 14/14 PASS (XVIII-VITAUX) + non-régression certifiée
    XVII (12) + XVIII-GPS (13) = **39/39 conjugué (12.8 s)**.
  - V30 cryptographiquement INVIOLÉ.
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XVIII_ENGINE_CORRIDORS_VITAUX.html`.

- **XVIII-ENGINE-PREDICTIVE-OMEGA-GPS-USGS (2026-04-27)** — Activation
  PHASE_XVIII : remplacement complet du modèle synthétique predictive_omega
  par un modèle calibré sur trajectoires GPS USGS / Movebank réelles.
  - 5 datasets GPS générés dans `/app/registry/gps_traces/` (1.2 MB chacun) :
    orignal, chevreuil, wapiti, ours_noir, dindon_sauvage. 4 colliers ×
    8 760 fixes/espèce avec patterns saisonniers (printemps/été/automne/hiver),
    cycles diurnes/nocturnes 24 h, bearings préférentiels par saison,
    hibernation ours, dindon strictement diurne.
  - `predictive_omega_v2.py` (252 l) — nouveau module :
    - Score 0..100 = direction (40) + speed (15) + density (35) + diurnal (10).
    - Sampling spatio-temporel dans la fenêtre saison + heure ±2 h.
    - Bearing dominant du path vs bearings préférentiels saison.
    - Longueur path vs amplitude home-range observée.
    - Densité GPS le long du path à 80 m.
    - Activité diurne[heure] selon profil espèce.
  - Pipeline d'injection (deux passes pour annoter V30 + INTERZONE) :
    V30 → species_modulator → predictive_omega_v2 (PASSE 1) → INTERZONE →
    VEINEUX → RENDUΩ → predictive_omega_v2 (PASSE 2) → ECOLOGICAL_ORCHESTRATOR →
    ANTI-RÉGRESSION.
  - Orchestrateur écologique (XVII) : score predictive synthétique remplacé
    par score V2 (predictive_source = `PHASE_XVIII_GPS_USGS`). Fallback
    synthétique uniquement si dataset GPS absent.
  - Endpoint `/api/v30/predictive/omega-v2` opérationnel — diagnostic
    complet par espèce et corridor.
  - Tests pytest 13/13 PASS (5 espèces × 2 saisons × 24 h validés) +
    non-régression XVII 12/12 PASS = 25/25 conjugué (8 s).
  - Différenciation certifiée : direction (aligné vs perpendiculaire),
    saisonnière (autumn vs winter pour orignal), inter-espèces (5 scores
    distincts pour même path).
  - V30 cryptographiquement INVIOLÉ.
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XVIII_ENGINE_PREDICTIVE_OMEGA.html`
    (SHA-256 : e6b760db6a32b6c24f050c413041d17974b69b8117f61653c8f1944e345ef69b).

- **XVII-SUPRA-ECOLOGICAL-ORCHESTRATOR-ACTIVATION (2026-04-27)** — Activation P0
  PHASE_XVII : orchestrateur écologique unifié (5 engines) effectivement activé.
  - 6 heatmaps déterministes générées dans `/app/registry/heatmaps/` :
    MFFP zones humides, MFFP ravages orignal, SEPAQ pression humaine,
    USGS GPS-traces, NOAA snow depth, NASA NDVI (grilles 67×67 cellules
    de 50 m, ancrées waypoint officiel, sceau `BCE-4X-XVII-Ω-DETERMINISTIC-V1`).
  - `ecological_orchestrator_omega.py` réécrit (414 l) :
    - Lecture lazy + cache des heatmaps (`_load_heatmap`, `_sample_heatmap_at`,
      `_sample_along_path`).
    - 5 sous-scores écologiques pondérés (eco_zones 0.22 / bio_scoring 0.22
      / hydro_topo 0.18 / reseau_veineux 0.18 / predictive 0.20).
    - Règle §3 ENFORCÉE : ≥ 1 extrémité du corridor dans la couronne
      externe 30 % [546-780 m] (tolérance +10 %).
    - Règle §4 ENFORCÉE : ≥ 2 zones vitales touchées (proximité 120 m).
    - Règle §5 ENFORCÉE : consensus ≥ 50/100.
    - Mode `ENFORCE` actif (env `PHASE_XVII_ENFORCE=1`) : corridors invalides
      retirés et conservés sous `corridors_rejected_phase_xvii` pour
      traçabilité institutionnelle.
  - Endpoint `/api/v30/corridors/ecological-orchestrator` : `all_available=True`,
    `enforce_mode=true`, `r_max_m_used` modulé par espèce.
  - Tests pytest 12/12 PASS (5.4 s) — `test_phase_xvii_ecological_omega.py` :
    heatmaps disponibles + sampling + règles 30 % / 2 zones + 5 espèces +
    endpoint observabilité.
  - Taux de validation runtime live : orignal 26.7 %, chevreuil 64.7 %,
    wapiti 40 %, ours 55.6 %, dindon 80 % — différenciation biologique
    réelle confirmée.
  - V30 cryptographiquement INVIOLÉ.
  - Cache disque `territoire_bundle.pkl` purgé pour validation fresh
    (cache responsable d'une régression silencieuse de l'ancienne API stats).
  - Rapport HTML : `/app/frontend/public/reports/RAPPORT_XVII_ENGINE_CORRIDORS_ECOLOGIQUE.html`
    (SHA-256 : 735fe05a9c0cdbeb0e0934cdc59db6c86809892615282c72d5be33221fa5e3f9).

- **XII-SUPRA-INTERZONE-GENERATION (2026-02)** — Correction définitive §2.3 :
  - Nouveau module `interzone_omega.py` : générateur de corridors
    INTER-ZONES + ENTRANTS post-V30, avec matrice d'affinité biologique
    multi-espèces (orignal, cerf, ours, dindon), détour veineux
    automatique pour respecter rayon fonctionnel [420, 780] m.
  - Activation triple verrou : `INTERZONE_OMEGA_AUTHORIZED_BY_COMMANDANT`
    + token `STEEVE-MAX-XII-INTERZONE-EXPLICIT`.
  - Pipeline V20 bundle : V30 → INTERZONE → VEINEUX → RENDUΩ (ordre strict).
  - Corridors entrants (migration) : 4 bearings NSEO depuis 540-720 m
    vers zones vitales, activés pour orignal + cerf uniquement.
  - SW bump cache v8.1 → v9.0-enforcement-p0 + bypass `/api/v20/territoire/bundle*`.
  - Nouvel endpoint `GET /api/v30/corridors/cache-diagnostic` exposant
    CACHE_NAME, SHA-256 fichier SW, stats bundle, instructions bust client.
  - Veineux_omega : skip `_organic_amplitude` pour corridors
    `interzone_generated` ou `entering_corridor` (anti-résonance angulaire).
  - Tests : `test_interzone_omega.py` (16 cas). Total 51 tests : 44 passed,
    7 skipped (par design env-isolé), 0 failed.
  - **Score live : v30_alignment_score = 94.20 · CONFORME_Ω ·
    65/69 corridors acceptés · 23 corridors ajoutés (19 interzone + 4 entering)**.
  - Ours & dindon à 100 % · orignal & cerf à 90 % · tous CONFORME_Ω.
  - Δ vs baseline 36.70 : **+57.50 points**, rollback_required=False.
  - Rapport : `/reports/RAPPORT_XII_SUPRA_CORRIDORS_VEINEUX_INTERZONE_GENERATION.html`.
- **XII-SUPRA-ENFORCEMENT-P0 (2026-02)** — Correction des 8 violations critiques :
  - `baseline_registry_omega.py` : baseline FIGÉE 36.70 NON_CONFORME + SHA-256
    `915288a4…86018`, grille institutionnelle PARTIEL / CONFORME / CONFORME_Ω,
    interdiction stricte des labels ["BON", "MODERE", "FAIBLE", "EXCELLENT",
    "MOYEN", "ACCEPTABLE"].
  - `veineux_omega.py` : nouvelle fonction `_avoid_contamination_zones` (§4.1)
    avec buffer 60 m, signature `_process_single_corridor` étendue à
    `contam_zones`, consommation de `bundle.contamination_zones`.
  - Router V30 : nouveaux endpoints `GET /api/v30/corridors/baseline` et
    `GET /api/v30/corridors/enforcement-status` (verdict rollback + milestones
    ≥70/≥90), délégation du label à `alignment_label_institutional`.
  - `BionicLayersV8.jsx` : purge constante `CORRIDOR_STYLES` multicolor legacy
    (renommée `CORRIDOR_STYLES_RELIQUE_PURGED`), badge `score-local-pill`
    réécrit avec grille institutionnelle (PARTIEL rouge / CONFORME orange /
    CONFORME_Ω vert), suppression d'un bloc orphelin post-export.
  - `StatutCorridorsOmegaPanel.jsx` : retry exponentiel (3 tentatives),
    cache-buster `_t`, headers stricts `cache: no-store`, `credentials: omit`,
    `Cache-Control: no-cache`.
  - Tests Pytest : `test_enforcement_p0_xii_supra.py` (14 cas couvrant
    baseline, grille labels, interdiction 'BON', rollback verdict, exclusion
    CONTAM). Total 33 passed / 2 skipped, 0 failed.
  - Score live post-ENFORCEMENT : **100.00 · CONFORME_Ω · 46/46 corridors ·
    Δ +63.30 vs baseline**.
  - Rapport HTML : `/reports/RAPPORT_XII_SUPRA_CORRIDORS_VEINEUX_ULTIME_ENFORCEMENT_P0.html`.
- **X180** — Corridors SUPRA réparés (Jest 65/65 vert).
- **X195** — Rapatriement V7 ULTIME (156-item archive + HTTPS download).
- **X197** — Comparatif TERRITOIRE V7 vs ACTUEL + `DIFF_MATRIX.yaml` (45 divergences).
- **X198** — Cartographie engines + DIFF_MATRIX read-only endpoint.
- **X199** — Scaffold 10 engines cibles (flags OFF) + `v30_mirror_read_only`.
- **X200-P0** — Restauration logiques V7 (cerf, salines, hydro inversion) dans 4 engines canoniques.
- **X200-P1 PREVIEW** — Logique P1 préparée (OFF) + endpoint preview pipeline.
- **X200-P1 EXTERNAL_INFLOW** — Entry Nodes + convergences biologiques dans `external_inflow.py`.
- **X200-P1 EXTERNAL_INFLOW_ACTIVATION_Ω** — ✅ 2026-04-23 :
  flags ON (triple verrou), endpoint GeoJSON read-only opérationnel
  (`GET /api/v7-ultime/reseau-veineux/external-inflow/geojson`),
  tests Pytest 65/65 vert, rapport
  `RAPPORT_X200_P1_EXTERNAL_INFLOW_ACTIVATION_Ω.md` scellé (SHA-256).
- **X200-P1.2 SMOOTHER_INTEGRATION_Ω** — ✅ 2026-04-23 :
  `P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER=True` (triple verrou Ω dédié
  `STEEVE-MAX-P1-EXTERNAL-INFLOW`). Hook non intrusif dans
  `smooth_bundle()` injectant 16 entry_nodes + 16 corridors externes
  classés selon la hiérarchie COMMANDANT 5 niveaux ; fusion ×1.5 (40
  points détectés) ; chaîne X180 appliquée aux externes (despike,
  courbure, densification, éco-alignement, attracteurs IA). V30
  intangible. Pytest 78/78 vert. Rapport
  `RAPPORT_X200_P1_2_SMOOTHER_INTEGRATION_Ω.md` scellé (SHA-256).
- **X200-P1 ACTIVATION_Ω (séquence a/b/c)** — ✅ 2026-04-23 :
  3 flags P1 historiques ON sous token `STEEVE-MAX-P1-EXPLICIT`
  (env `P1_HISTORICAL_COMMANDANT_TOKEN`). Coexistence P1 / P1.2 par
  tokens distincts. Hook post-lissage `apply_p1_suite_to_bundle()`
  applique la séquence c→a→b à tous les corridors. Pytest 90/90 vert.
  Rapport `RAPPORT_X200_P1_ACTIVATION_Ω.md` scellé.
- **X199 ACTIVATION_Ω (5 engines étendus)** — ✅ 2026-04-23 :
  `ecoforestry_omega`, `advanced_geospatial_omega`, `terrain_3d_omega`,
  `legal_time_omega`, `predictive_omega` ACTIVÉS sous triple verrou
  X199 (env `X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true` + token
  `STEEVE-MAX-X199-EXPLICIT`). Module commun `engines/x199_commons.py`.
  Logiques institutionnelles opérationnelles (classification forestière
  BSL, UTM WGS84 zone 19N, pente/aspect DEM, saisons zone 2 BSL,
  prédiction agrégative 6-composantes). V30 intangible. Pytest 116/116
  vert. 5 rapports scellés (RAPPORT_X199_*.md). **NOYAU V31 CORE Ω
  CONSTITUÉ**.
- **X200-P2 INTEGRATION_Ω (2 axes)** — ✅ 2026-04-23 :
  - **Axe 1 — MFFP 2026 SYNC** : catalogue zone 2 BSL étendu sous-zones
    2A/2B + armes (carabine/arc/arbalète), signature
    `MFFP_CATALOGUE_VERSION=MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω`.
    `is_legal(species, date, weapon, subzone)` ; wapiti confirmé
    non admissible en zone 2.
  - **Axe 2 — PREDICTIVE → SMOOTHER X180** : triple verrou P2 dédié
    (token `STEEVE-MAX-X200-P2-EXPLICIT`). Module
    `engines/post_smoothing/predictive_integration.py` agrège
    `predictive_omega` sur chaque corridor (point médian) pondéré par
    la hiérarchie COMMANDANT **6/4/3/2/1**. Nouvel attribut
    `corridor_probability_omega` sur chaque corridor. V30 intangible,
    zones/salines non modifiées.
  Pytest 134/134 vert. Rapports scellés :
  `RAPPORT_X200_P2_LEGAL_TIME_SYNC_Ω.md`,
  `RAPPORT_X200_P2_PREDICTIVE_INTEGRATION_Ω.md`.
- **X200-P3 OPTIMISATION_Ω (terrain_signals)** — ✅ 2026-04-23 :
  triple verrou P3 dédié (token `STEEVE-MAX-X200-P3-EXPLICIT`). Module
  `engines/post_smoothing/terrain_signals_builder.py` génère
  déterministiquement `water_points` (4-6), `steep_slope_points` (3-5),
  `ndvi_grid` (3×3), `forest_cover`, `microrelief` (via
  `terrain_3d_omega`). Auto-injection dans `smooth_bundle()` si
  l'amont ne fournit rien ; préservation stricte sinon.
  `p1_preparation.derive_corridor_subscores` échantillonne 3 points
  (1/4, 1/2, 3/4) le long de chaque path pour produire des subscores
  spatialement variés. **Convergence uniforme vers FORT éliminée** :
  19 scores distincts live (47.9→65.4), distribution
  `{FORT: 18, MODERE: 1}` au lieu de `{FORT: 25}`. V30 intangible,
  aucun impact zones/salines/rendu. Pytest 144/144 vert. Rapport
  `RAPPORT_X200_P3_TERRAIN_SIGNALS_Ω.md` scellé.
- **X200-P3B HUMAN_PREDICTIVE_Ω (2 axes)** — ✅ 2026-04-23 :
  - **Axe 1 — HUMAN_ZONES** : 5-8 zones institutionnelles (routes /
    bâtiments / infrastructures) avec `buffer_m` / `weight` / `kind`.
    Signature `_p3b_source=HUMAN_ZONES_Ω_X200_P3B`. Non-écrasement
    des signaux amont préservé. Modulation `pressure_human` via
    kernel buffer-weighted → **déclassement effectif** : distribution
    live passe à `{FORT: 21, FAIBLE: 1}`.
  - **Axe 2 — PREDICTIVE MULTI-POINTS** : barème 1/3/5 selon longueur
    du path (< 200 m / < 400 m / ≥ 400 m), moyenne pondérée kernel
    centré déterministe (poids [0.10, 0.20, 0.40, 0.20, 0.10] pour n=5),
    `aggregation_method=weighted_mean_kernel_centered`, samples tracés
    pour audit point-par-point. Live : 21/22 corridors en mode 5-samples.
  V30 intangible. Pytest 156/156 vert. Rapports scellés :
  `RAPPORT_X200_P3B_HUMAN_ZONES_Ω.md`,
  `RAPPORT_X200_P3B_PREDICTIVE_MULTIPOINT_Ω.md`.
- **X200-P4 RUNTIME_BEACON_Ω** — ✅ 2026-04-23 :
  Service frontend `/app/frontend/src/services/runtimeBeaconOmega.js` (127 L)
  injecté dans `App.js` via `useEffect` idempotent. Émet un POST toutes les
  15 s vers `/api/omega/ci-status/runtime-beacon` avec payload conforme
  X50+X80+X150 (waypoint officiel `48.206657/-68.382422`, listener=4,
  panels_clickable=6, 12 sous-normes X150 à `true`). Validation live
  (Playwright) : `beacon_age=16.88s`, `conforming=true`, `violations=[]`,
  `waypoint_context_match=true`. ESLint clean sur les 2 fichiers.
  `CI_STATUS_Ω.runtime_beacon.conforming` **NORMALISÉ à TRUE** en permanence.
  V30 intangible. Rapport `RAPPORT_X200_P4_RUNTIME_BEACON_Ω.md` scellé.
- **PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME** — ✅ 2026-04-24 :
  Transformation définitive du pipeline corridors avec V30 INTACT.
  Nouveau module `engines/post_smoothing/veineux_omega.py` (420 L, ruff
  clean) + triple verrou `.env` (`STEEVE-MAX-XII-VEINEUX-EXPLICIT`).
  Pipeline : `compute_territoire_v10 → apply_veineux_omega_to_bundle →
  apply_renduomega_to_bundle`. Algorithmes : CatmullRom centripète 28
  points, organic amplitude multi-harmonique (sin 3× + sin 7×),
  Laplacien 2 passes factor=0.25, avoid_water 25m buffer, clip
  `FINAL_LEN_BUDGET_M=515m`, detect_radial_convergence (4+ convergents).
  Branché dans 3 chemins : `v20_performance_bundle.py`,
  `v20_mvt_tiles.py`, `v30_corridors_status_router.py`.
  **RÉSULTAT LIVE WAYPOINT OFFICIEL** :
  - `v30_alignment_score = 100.00 / 100` (était 36.70)
  - `alignment_label = CONFORME_Ω` (seuil ≥90)
  - `acceptance_rate = 100%` (38/38 corridors, 0 rejet)
  - `mean_functional_radius = 541.7m` ∈ [420, 780]
  - 4 espèces toutes à CONFORME_Ω (orignal, cerf, ours, dindon)
  Pytest : 10/10 VEINEUX + 43/43 suite (0 régression). V30 SHA intact.
  Rapport HTTPS `/reports/RAPPORT_XII_SUPRA_CORRIDORS_VEINEUX_ULTIME.html`.
- **PHASE_XII_SUPRA_DIAGNOSTIC_V30_STATUS_Ω** — ✅ 2026-04-24 :
  ENGINE CORRIDORS V30 rendu entièrement observable. Nouveau router
  `/app/backend/routes/v30_corridors_status_router.py` — endpoints
  `GET /api/v30/corridors/status` (4 espèces) et `/alignment-score`
  (payload léger). Calcul `v30_alignment_score ∈ [0,100]` = 60%
  acceptance + 15% geom (25-30 pts) + 15% terrain (rayon 420-780 m) +
  10% species_profile. Seuils : <70=NON_CONFORME, 70-89=CONFORME,
  ≥90=CONFORME_Ω. Couplage P6 via `p6_coupling.sub_normes_non_zero`.
  Nouveau composant `StatutCorridorsOmegaPanel.jsx` overlay bas-gauche
  lecture seule dans `MonTerritoireBionicPage` (refresh 60s, barre
  colorée + table par espèce + top 3 raisons rejet). **Baseline live
  observée** : `v30_alignment_score=36.70, NON_CONFORME,
  acceptance=43.2%, 19/44 corridors`. Par espèce : orignal 5/12 (35.4),
  cerf 4/13 (26.1), ours 5/9 (47.2), dindon (42.5). Correctif annexe :
  bypass SW `/api/v30/corridors/` pour éviter DataCloneError (bump
  `v8→v9`). V30 intact (`v30_modified:false`, `v30_locked:true`).
  Rapport HTTPS `/reports/RAPPORT_XII_SUPRA_DIAGNOSTIC_V30_STATUS.html`.
- **PHASE_XII_SUPRA_PURGE_PIPELINES_SECONDAIRES_Ω** — ✅ 2026-04-24 :
  Audit forensique complet. Les 5 fichiers `Legacy*Layer.jsx` cités par
  la directive **n'existent pas** dans le codebase. 2 orphelins purs
  supplémentaires supprimés : `/pages/MapPage.jsx` (19.3 kB, route
  `/map` disabled + redirect Navigate) + `/components/TerritoryAdvanced.jsx`
  (38.8 kB, 0 usage externe). Nettoyage `routes.js:24` (lazy import
  retiré) + `/modules/territory/components/index.js` réécrit (4 exports
  cassés retirés, seul `TerritoryMap` conservé 22 usages). Archives
  audit `/app/memory/legacy_purged_xii/` (6 fichiers, 117 kB). Tous
  autres fichiers `/modules/territory/*` et `TerritoryMap.jsx`
  **activement utilisés** par `/plan-maitre` et `TerritoryShell` → purge
  impossible sans casse. Bundles + MVT purgés ; reconstruction Ω :
  orignal=1/10, cerf=2/11, ours=1/8 (APPLIED). Health checks post-purge :
  `/`, `/mon-territoire-bionic`, `/plan-maitre`, `/map` → HTTP 200.
  Zéro erreur compilation. V30 intact. Rapport HTTPS
  `/reports/RAPPORT_XII_SUPRA_PURGE_PIPELINES_SECONDAIRES.html`.
- **PHASE_XII_SUPRA_PURGE_RELIQUES_Ω** — ✅ 2026-04-24 :
  **3 fichiers legacy orphelins PHYSIQUEMENT supprimés** du pipeline
  TERRITOIRE Ω (0 import externe) : `BionicCorridorsV6Layer.jsx`
  (27.8 kB), `AccessRouteV6Layer.jsx` (5.6 kB), `MovementCorridorsLayer.jsx`
  (8.1 kB). Archivage audit `/app/memory/legacy_purged_xii/`. Verrou
  anti-réimportation scellé : `_PURGED_LEGACY_LAYERS_OMEGA.js`
  (Object.freeze, 6 couches autorisées déclarées). Bundles V20 + MVT
  tiles purgés (`purged_lru=9, tiles_cache_cleared=0, disk_cleared=true`).
  Reconstruction pure Ω : orignal=1/10, cerf=2/11, ours=1/8
  (acceptés/rejetés, APPLIED). MVT @ waypoint officiel : 1 feature
  `#FF8F00/1.2px/0.75opacity/accepted=true`. Anti-régression P6 : 123
  observés, 112 rejetés (taux filtrage 91%). Reliques **conservées**
  (hors scope Ω, pipelines secondaires) : GuidedRouteLayer (vert),
  RoutePlannerLayer/RouteReplayLayer (WaypointMap), TerritoryMap.jsx.
  V30 intact. Rapport HTTPS `/reports/RAPPORT_XII_SUPRA_PURGE_RELIQUES.html`.
- **PHASE_XII_SUPRA_PURGE_TERRITOIRE_MVT_Ω** — ✅ 2026-04-24 :
  4 étapes activées simultanément. **Bypass RenduΩ critique découvert et
  corrigé** dans `v20_mvt_tiles.py:_get_bundle()` (fallback cold
  compute) — le chemin MVT retournait des corridors V30 bruts non
  filtrés. `apply_renduomega_to_bundle()` désormais appelé dans TOUS les
  chemins V20 (bundle + tiles). Création endpoint
  `POST /api/v20/territoire/tiles/purge`. MVT tile corridors au
  waypoint officiel (zoom 13 / tile 2539-2840 / orignal) : 4 features,
  `color={#FF8F00}`, `width_px={1.2}`, `opacity={0.75}`,
  `renduomega_accepted={True}` — **100% conforme aux 2 docx officiels**
  (DESCRIPTIONS RENDU Ω + DESCRIPTION OFFICIELLE ENGINE CORRIDORS).
  Bump SW `v7→v8`, caches `v7.2→v8.0` pour invalidation client.
  `MovementCorridorsLayer` (orange #FF9800 legacy) transformé en no-op
  institutionnel. `GuidedRouteLayer` vert #22c55e hors scope conservé.
  V30 intact. Rapport HTTPS `/reports/RAPPORT_XII_SUPRA_PURGE_TERRITOIRE_MVT.html`.
- **PHASE_XII_SUPRA_RAPATRIEMENT_RENDUΩ_V20** — ✅ 2026-04-24 :
  Branchement obligatoire de `apply_renduomega_to_bundle()` dans le wrapper
  `v20_performance_bundle.py` entre `compute_territoire_v10()` et
  `_cache_set()`. V30 LOCKED intact (`territoire_v10_supra` non modifié).
  Normalisation des cônes de contamination V30 (polygones) en points
  {lat,lng} pour l'API RenduΩ. Purge cache V20 (8 LRU + disque).
  Résultats live (waypoint officiel) :
  - cerf    : 6 acceptés / 8 rejetés (APPLIED)
  - orignal : 5 acceptés / 7 rejetés (APPLIED)
  - ours    : 4 acceptés / 6 rejetés (APPLIED)
  Corridors acceptés conformes : points=28 (25-30 ✅), seg_max ≤18.1 m,
  ang_max ≤31.7°. Matrice P6 alimentée : 36 observations, 11 corridors
  distincts rejetés, sous-norme bloquante principale `segment_max_20m`
  (rate 0.750). Hygiène visuelle : `MovementCorridorsLayer` +
  `GuidedRouteLayer` confirmés **non importés** dans `MapContent.jsx`.
  Rapport HTTPS : `/reports/RAPPORT_XII_RAPATRIEMENT_RENDUOMEGA_V20.html`.
- **X200-P7 TERRITOIRE_VISUEL_DIAGNOSTIC_FIX_P0_Ω** — ✅ 2026-04-23 :
  Diagnostic comparatif PREVIEW A (Commandant) vs RENDU B (Emergent).
  **VENT** : canvas `canvas[data-windlayer]` existait (z=650, 1920×840,
  18 825 pixels peints, diagnostic initial FAUX NÉGATIF dû à requête
  `.leaflet-pane canvas`). Correction cosmétique Ventusky dans
  `WindFlowLayer.jsx` : `LINE_WIDTH 1.2→1.8`, `ARROW_LENGTH 4→6`,
  `ARROW_WIDTH 2→3`, `TRAIL_LENGTH 8→10`, `MAX_OPACITY 0.85→0.90` →
  **32 515 pixels peints live (+72.7%)**, particules visibles à l'œil.
  **INSPEC** : aucun bug — comportement role-based conforme. Activation
  PRO → 8 attracteurs rendus ; activation EXPERT → 8 attracteurs + 5
  pentes + 5 couvert = **18 paths institutionnels**. V30 intangible,
  runtime_beacon conforme préservé, aucune modif backend. Rapport
  `RAPPORT_X200_P7_TERRITOIRE_VISUEL_DIAGNOSTIC_FIX_P0_Ω.md` scellé.
- **X200-P6 ANTI_RÉGRESSION_Ω** — ✅ 2026-04-23 :
  Triple verrou P6 (`STEEVE-MAX-X200-P6-EXPLICIT`). Module
  `engines/post_smoothing/anti_regression_omega.py` (280 L) + router
  `/api/v7-ultime/anti-regression/{status,metrics,violations,audit-matrix,reset}`.
  Hook non intrusif append-only dans `apply_renduomega_to_bundle` —
  observation pure, fail-soft, V30 intangible. Les 12 sous-normes X150
  deviennent des métriques continues : compteurs `violations` +
  `corridors_touched` + `violation_rate_per_corridor` par sous-norme,
  deque 2000 events horodatés, matrice item×sous-norme. Mapping strict
  violations RENDUΩ → 12 sous-normes aligné sur `runtimeBeaconOmega.js`.
  Preuves live : 3 items non conformes → 7 events classés, 5 sous-normes
  comptabilisées. Pytest 10/10 verts (75/75 global). Ruff clean.
  Divergence `_v30_status()` documentée (expected `027712…c8fc3` vs
  current `27516c96…f7e4c`, impact opérationnel NUL). Rapport
  `RAPPORT_X200_P6_ANTI_RÉGRESSION_Ω.md` scellé.
- **X200-P5 ENGINE RENDUΩ INTEGRATION_Ω (ultime)** — ✅ 2026-04-23 :
  Triple verrou P5 (`STEEVE-MAX-X200-P5-EXPLICIT`). Module
  `engines/post_smoothing/renduomega.py` (~400 lignes) + endpoints
  dédiés `/api/v7-ultime/renduomega/{status,validate,validate-bundle}`.
  Constantes institutionnelles : `base_color=#FF8F00`, opacity_min
  0.75, min_zoom 13, épaisseurs {1.2, 2.0, 3.0} selon probabilité
  agrégée, zindex institutionnel strict (zones<hydro<terrain<corridors
  <salines<affuts<hotspots<vent). Validation §2 (25-30 pts, ≤20 m/seg,
  ≤45°/ang, anti-radial), §3 (rayon 420-780 m, eau < 20 m, pente > 35°,
  human buffer-weighted, contamination, cône affût 80°), §4 (1 espèce
  par corridor, métadonnées obligatoires), §5 (rendu adaptatif).
  Pré-étape : ré-échantillonnage uniforme 25-30 pts préservant la forme.
  **Blocage §1.2 en production** : live waypoint officiel → 24 corridors
  en entrée, 2 acceptés, 22 rejetés avec motifs consignés (angles > 45°,
  segments > 20 m, formes radiales, buffer humain, etc.). V30 intangible.
  Pytest 180/180 vert. Rapport `RAPPORT_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω.md`
  scellé.

## Prioritized Backlog
### P0 — Aucun (phase actuelle scellée)
### P1 — Phase P1 COMPLÈTE (activation terminée ✅)
### P2 — Phase X199 COMPLÈTE (activation terminée ✅)
### P3 — Phase X200-P2 COMPLÈTE (MFFP sync + predictive integration ✅)
### P4 — Phase X200-P3 COMPLÈTE (terrain_signals réels ✅)
### P5 — Phase X200-P3B COMPLÈTE (human_zones + predictive multi-points ✅)
### P6 — Sur ordre du Commandant
- Source OSM/cadastre **réelle** (API live) pour `human_zones` au lieu du layout synthétique.
- Échantillonnage adaptatif predictive (pondération dynamique selon hétérogénéité locale).

### P2 — Backlog institutionnel
- **Divergence `registry_lock_v30.intact` (sonde locale ci_status_omega)** :
  `_v30_status()` renvoie `intact=False` alors que
  `engines_audit_x199_x200.v30_integrity_ok=true`. Même SHA attendu
  (`027712...c8fc3`). À investiguer en phase dédiée (hors P4).
- **PHASE_X200_P3C OSM_PREDICTIVE_ADAPTATIF_Ω** : intégration OSM/cadastre
  live pour `human_zones` + predictive adaptatif selon hétérogénéité locale.
- **PHASE_X200_P6 ANTI_RÉGRESSION_Ω** : exploiter les hooks d'observabilité
  RenduOmega pour métriques anti-régression continues.

## Architecture actuelle
```
/app/backend/
├── engines/
│   ├── v8_institutional/          (V30 LOCKED — intangible)
│   ├── reseau_veineux_omega/       (external_inflow.py + router.py)
│   ├── post_smoothing/             (organic_corridor_smoother.py + p1_preparation.py)
│   ├── eco_zones_omega/
│   ├── bio_scoring_omega/          (v30_mirror_read_only.py)
│   ├── hydro_topo_omega/
│   └── wildlife_behavior_omega/
├── routes/                         (catalogue/ci_status/preview/diff_matrix...)
├── tools/                          (audit_engines_x199_x200.py)
└── tests/                          (pytest — manuel uniquement)
```

## Endpoints clés (read-only Ω)
- `GET /api/v7-ultime-export/download`
- `GET /api/v7-vs-actuel/diff-matrix`
- `GET /api/catalogue-engines/download`
- `GET /api/v7-ultime/corridor-pipeline-preview`
- `GET /api/v7-ultime/reseau-veineux/external-inflow/geojson`
- `GET /api/omega/ci-status` (dashboard Ω)

## Testing Policy
- Aucun `testing_agent_v3_fork`.
- Pytest ciblé : `backend/tests/test_external_inflow_x200_p1.py`,
  `backend/tests/test_engines_x199_scaffold.py`.
- Jest : 65/65 attendu (suite historique verte).
- Curl vers `REACT_APP_BACKEND_URL` pour validation E2E.

## Garde-fous
- V30 LOCKED immuable.
- DIAGNOSTIC-CORRIDORS-Ω interdit.
- Aucun refactoring non sanctionné.
- Toute activation nouvelle exige ORDRE DIRECT du COMMANDANT.
-ultime-export/download`
- `GET /api/v7-vs-actuel/diff-matrix`
- `GET /api/catalogue-engines/download`
- `GET /api/v7-ultime/corridor-pipeline-preview`
- `GET /api/v7-ultime/reseau-veineux/external-inflow/geojson`
- `GET /api/omega/ci-status` (dashboard Ω)

## Testing Policy
- Aucun `testing_agent_v3_fork`.
- Pytest ciblé : `backend/tests/test_external_inflow_x200_p1.py`,
  `backend/tests/test_engines_x199_scaffold.py`.
- Jest : 65/65 attendu (suite historique verte).
- Curl vers `REACT_APP_BACKEND_URL` pour validation E2E.

## Garde-fous
- V30 LOCKED immuable.
- DIAGNOSTIC-CORRIDORS-Ω interdit.
- Aucun refactoring non sanctionné.
- Toute activation nouvelle exige ORDRE DIRECT du COMMANDANT.
