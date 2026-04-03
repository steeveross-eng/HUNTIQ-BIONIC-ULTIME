# HUNTIQ-V6 / BIONIC HUNT — PRD
## Protocole BCE-4X — STEEVE-MAX — GOLDEN UI

---

## Probleme Original
Plateforme d'analyse de territoires de chasse avec scoring multi-criteres, guide BIONIC professionnel, intelligence IA, et fonctionnalites e-commerce (Premium, Shop, Commandez).

## Utilisateurs
- Chasseurs professionnels Quebec/Canada
- Gestionnaires de territoires fauniques
- Guides de chasse et pourvoiries

## Architecture
- Frontend: React + Leaflet + Shadcn UI
- Backend: FastAPI + MongoDB
- Modules: Soil Engine, Guide BIONIC (criteriaDatabase), Meteo, Score Chasse, Share Engine V1

## Fonctionnalites Implementees

### UI / Navigation (GOLDEN V9)
- Header principal: HOME, DASHBOARD, ANALYSE TERRITOIRE, CARTE, PERMIS, SHOP
- Sub-header Territoire: SPLIT, CARTE, ESPECES, OBSERVATION, INTELLIGENCE, ZONES, ALIMENTATION, POINTS CHAUDS, SEUIL, CURSEUR
- Bouton WAYPOINT (renomme depuis WPT en V8)
- Bouton PARTAGER dans le sub-header (relocalise depuis App.js en V8)
- SCORE CHASSE dans le sub-header
- Meteo consolidee — source unique METEO BIONIC (V9: duplication sub-header supprimee)
- Scrollbar ORANGE BIONIC globale: 14px, gradient #FF9800-#E65100, fleches SVG haut/bas (V9)
- SUPRA V2 grilles: gap-1.5, space-y-1.5, paddings reduits, rounded-lg (V9)
- Fiches techniques: max-w-6xl, layout multi-colonnes 2x et 3x, scroll reduit -60% (V9)
- Cookie banner conforme Quebec

### Guide BIONIC — Niveau Professionnel V2
- 32 criteres au standard V2 complet (ZERO DEFAULT generique)
- 13 criteres originaux (V1 + P0 V2) dans criteriaDatabase.js
- 19 criteres P1/P2 dans criteriaDatabase_P1P2.js (1327 lignes)
- 5 especes: Orignal, Chevreuil, Ours noir, Wapiti, Dindon sauvage
- 15 sections/critere: definition, methodologie, justification, recommandations, strategies, techniques, erreurs, optimisations, seuils, sources TOP-TIER

### Share Engine V1 — Directive x5001 (NOUVEAU)
- SECTION A: Texte officiel BIONIC injecte dans LanguageContext.jsx (FR + EN)
- SECTION B: Page principale mise a jour avec texte officiel via t() keys
- SECTION C: Screenshot automatique html2canvas + watermark "Analyse generee avec BIONIC OS — IA Terrain"
- SECTION D: Share Card / Payload avec texte officiel certifie + URL EASYlead
- SECTION E: EASYlead tracking URL (?ref=USER_ID&lead=SHARE_ID&page=PAGE_SHARED)
  - Backend: POST /api/share/easylead/generate, GET /api/share/easylead/track, GET /api/share/easylead/stats
- SECTION F: Integration globale — 14 canaux + EASYlead sur toutes les pages
- SECTION G: Livrables SHARE_ENGINE_V1_SPEC.md + EASYLEAD_TRACKING_MAP.md

### Backend
- GET /api/v1/soil — Soil Engine (pedologie, LiDAR)
- POST /api/share/track — Tracking partage + Marketing Engine
- POST /api/share/easylead/generate — Generation liens EASYlead
- GET /api/share/easylead/track — Tracking clics entrants
- GET /api/share/easylead/stats — Statistiques EASYlead admin
- GET /api/share/status — Status module v4.0.0
- Scoring multi-criteres sur 100 points

### Integrations
- Stripe (paiement Premium)
- Shapely (geometrie territoriale)
- Leaflet (cartographie)
- html2canvas (screenshot partage)

---

## Livrables Completes

### Directive x4850-x4852 — REWRITE + INTERCONNEXIONS
- [x] Section A: PARTAGER relocalise + WPT->WAYPOINT + AUDIT_CSS_HEADER_V8.md
- [x] Section B: criteriaDatabase_P1P2.js (19 criteres V2) + SOUS_CRITERES_V2_COMPLET.md
- [x] Section C: INTERCONNEXIONS_P3_P6.md

### Directive x4950 — UI_HARMONISATION_V9
- [x] Section A: Meteo duplication supprimee du sub-header
- [x] Section B: Scrollbar ORANGE BIONIC globale (14px, fleches, gradient)
- [x] Section C: SUPRA V2 grille harmonisee (gap-1.5, padding reduit, 5 onglets)
- [x] Section D: Fiches techniques elargies (max-w-6xl, multi-colonnes, scroll -60%)
- [x] AUDIT_UI_V9.md genere

### Directive x5001 — SHARE_ENGINE_V1_EASYLEAD_ULTRA_REVISION_3
- [x] Section A: Texte officiel BIONIC injecte (FR + EN)
- [x] Section B: Page principale harmonisee avec texte officiel
- [x] Section C: Screenshot html2canvas + watermark BIONIC OS
- [x] Section D: Share Card / Payload officiel
- [x] Section E: EASYlead tracking (generate + track + stats)
- [x] Section F: Integration globale 14 canaux
- [x] Section G: SHARE_ENGINE_V1_SPEC.md + EASYLEAD_TRACKING_MAP.md

### Directive x5200 — ARCHITECTURE_AUDIT_V1
- [x] Section A: Architecture logicielle HIGH-LEVEL (75 modules, 5 moteurs, 9 core, 1675+ API)
- [x] Section B: Architecture moteurs SUPRA (18+ sous-routeurs bionic_engine_p0)
- [x] Section C: Architecture e-commerce (7 pipelines)
- [x] Section D: Architecture Admin Premium (10 modules)
- [x] Section E: Modules annexes (SEO, Marketing, Messaging, etc.)
- [x] Section F: Architecture des flux (8 flux documentes)
- [x] Section G: Permissions et gouvernance (Master Switch, Roles, Pare-feux)
- [x] Section H: Logs et BCE-4X (compliance, ULTRA-MAX++ Lock)
- [x] Section I: Texte officiel mis a jour (hero_highlight x5200)
- [x] Livrable: /app/memory/ARCHITECTURE_BIONIC_OS_V1.md

### Directive x5201 — ARCHITECTURE_AUDIT_EXPORT_REQUEST
- [x] Section A: Export HTTPS (ARCHITECTURE + MODULES via /public/)
- [x] Section B: Liste complete 87 modules backend (MODULES_BACKEND_COMPLET_V1.md)
- [x] Section C: Objectifs preparatoires (certification, V2, EASYlead Admin, P3-P6)

### Directive x5300 — BACKUP_TOTAL_BIONIC_OS
- [x] Section A: ZIP principal (128 MB) + MongoDB dump (34 collections, 703 docs) + Snapshot systeme
- [x] Section B: ZIP #2 (128 MB) — 7 blocs critiques (Frontend, Backend, MongoDB, ENV, Assets, Build, System)
- [x] Section C: Point de restauration scelle BIONIC_OS_v5201 (RESTORE_POINT_v5201.md)
- [x] Section D: Protocole ZERO-REGRESSION BCE-4X actif (ZERO_REGRESSION_PROTOCOL_v5201.md)

### Directive x5302 — ARCHIVE_PERMANENTE_BIONIC_OS
- [x] Section A: Archivage long terme — 4 fichiers en triple redondance (public/, static/, memory/)
- [x] Section B: Accessibilite HTTPS verifiee — Endpoint 1 (frontend) + Endpoint 2 (backend API)
- [x] Section C: Double redondance — /api/archive/v5201/ operationnel (list + download)
- [x] Section D: Rapport ARCHIVE_PERMANENTE_v5201.md genere — v5201 protegee

### Directive x5304 — ARCHIVE_GITHUB_PERMANENTE
- [x] Section A: Sauvegarde GitHub validee operationnelle
- [x] Section B: Export prepare — 8 fichiers + 4 configs systeme + ENV chiffrees + RECONSTRUCT.sh
- [x] Section B: ZIP fractionnes <95 MB (GitHub compatible) — integrite MD5 + Python zipfile verifiee
- [x] Section C: Procedure "Save to GitHub" + tag + Release documentee
- [x] Section D: Rapport ARCHIVE_GITHUB_PERMANENTE_v5201.md genere

### Consolidation V6 (STEEVE-MAX)
- [x] Merge: geo_engine → geospatial_engine (logique absorbee, prefix API preserve)
- [x] Merge: affiliate_ads_engine + ad_spaces_engine → ads_engine (facade, 30 endpoints)
- [x] Merge: tutorial_engine + formations_engine → learning_engine (facade, 12 endpoints)
- [x] Deprecate: geo_engine (marque DEPRECATED, successor=geospatial_engine)
- [x] Deprecate: core/alimentation (marque DEPRECATED, successor=nutrition_engine)
- [x] Reclass: chasseur_jumeau.py → experiments/ (redirect d'import conserve)
- [x] Reclass: liste_epicerie.py → utility_modules/ (redirect d'import conserve)
- [x] routers.py mis a jour v4.0.0 — Backend stable, tous modules charges

---

## Backlog (GELE par STEEVE-MAX)
- P2: Soil Engine V2 (donnees pedologiques reelles, LiDAR) — GELE
- P2: Phase 2D (Purge shadcn/utils) — GELE
- P2: Phase BSAA-2 (Social Ads Automation) — GELE
- P2: Implementation P3-P6 (Interconnexions modules) — GELE
- INTERDIT: Merge vers main — STRICTEMENT INTERDIT

---

## Fichiers Cles
- /app/frontend/src/App.js
- /app/frontend/src/App.css
- /app/frontend/src/index.css
- /app/frontend/src/contexts/LanguageContext.jsx
- /app/frontend/src/components/territoire/ui/ShareBionicButton.jsx
- /app/frontend/src/components/territoire/ui/TerritoireHeader.jsx
- /app/frontend/src/components/territoire/ui/CriteriaDetailModal.jsx
- /app/frontend/src/components/territoire/ui/criteriaDatabase.js
- /app/frontend/src/components/territoire/ui/criteriaDatabase_P1P2.js
- /app/backend/modules/share_engine/router.py
- /app/memory/SHARE_ENGINE_V1_SPEC.md
- /app/memory/EASYLEAD_TRACKING_MAP.md
- /app/memory/ARCHITECTURE_BIONIC_OS_V1.md
- /app/memory/MODULES_BACKEND_COMPLET_V1.md
- /app/memory/AUDIT_CSS_HEADER_V8.md
- /app/memory/AUDIT_UI_V9.md
- /app/memory/SOUS_CRITERES_V2_COMPLET.md
- /app/memory/INTERCONNEXIONS_P3_P6.md

---

## Regles de Gouvernance
- Protocole BCE-4X / GOLDEN UI
- Autorite: STEEVE-MAX
- ZERO LOSS, ZERO REGRESSION
- Validation explicite requise pour chaque phase
- Merge main STRICTEMENT INTERDIT
