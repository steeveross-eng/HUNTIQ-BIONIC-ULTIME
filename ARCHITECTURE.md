# HUNTIQ-BIONIC-ULTIME — Architecture V10

> Version canonique V10 — Architecture modulaire + Corridors Omega + Écoforesterie + BIONIC Core
> Dernière mise à jour : 31 août 2026

---

## Vue d'ensemble

HUNTIQ-BIONIC-ULTIME est une application de chasse intelligente utilisant des grilles hexagonales H3,
des données écoforestières gouvernementales et des moteurs scientifiques pour modéliser les territoires
et corridors fauniques au Québec/Canada.

**Stack technique :**
- Frontend : React (TypeScript)
- Backend : FastAPI (Python)
- Base de données : MongoDB
- Stockage : Cloudflare R2
- Sources géospatiales : MERN/MFFP (Québec), NRCan (Canada), ESA Sentinel, NASA HLS

---

## Structure du repo

HUNTIQ-BIONIC-ULTIME/ ├── .emergent/ # Configuration Emergent (sandbox) ├── .github/workflows/ # CI/CD (deploy-backend.yml, v30_lock_check.yml) ├── backend/ │ ├── engines/ # Moteurs scientifiques Omega V10 (25 moteurs) │ ├── modules/ # Fonctionnalités applicatives (~90 modules) │ ├── routes/ # Endpoints HTTP additionnels │ ├── services/ # Logique métier partagée │ ├── middleware/ # Middleware FastAPI (auth, CORS, rate-limit) │ ├── models/ # Modèles MongoDB │ ├── schemas/mongodb/ # Schémas de validation │ ├── validators/ # Validateurs de données │ ├── core/ # Configuration et constantes │ ├── config/ # Fichiers de configuration │ ├── scripts/ # Scripts utilitaires │ ├── tools/ # Workers H3, analyseurs │ ├── tests/ # Tests de régression │ ├── integrations/ # Intégrations externes │ ├── cache/ # Système de cache │ ├── monitoring/ # Monitoring et métriques │ ├── websocket/ # Connexions temps réel │ ├── docs/ # Documentation BCE-4X │ ├── data/ # Données statiques │ ├── state/ # Gestion d'état │ ├── static/ # Fichiers statiques (archive_v5201) │ ├── server.py # Point d'entrée FastAPI (2 234 lignes) │ ├── server_orchestrator.py # Orchestrateur de modules │ ├── database.py # Connexion MongoDB │ ├── bionic_engine.py # Core engine loader │ ├── wms_proxy_router.py # Proxy WMS (SSRF patché Phase 5) │ └── zerocost_workers_runtime.py # Runtime workers H3 ├── frontend/ # Application React │ ├── src/ │ ├── public/ │ └── package.json └── ARCHITECTURE.md # Ce fichier


---

## backend/engines/ — Moteurs scientifiques Omega

Les moteurs Omega sont le coeur scientifique de BIONIC V10. Ils servent les endpoints `/api/v20/*`.

| Moteur | Rôle |
|---|---|
| `ecoforestry_omega/` | Analyse écoforestière (peuplements, coupes, habitats) |
| `wildlife_behavior_omega/` | Comportement faunique (mouvement, activité, présence) |
| `predictive_omega/` | Modèles prédictifs (succès de chasse, conditions optimales) |
| `bio_scoring_omega/` | Scoring scientifique 8 facteurs V7 |
| `nutrition_intelligence/` | Intelligence nutritionnelle (salines, minéraux) |
| `spectral_omega/` | Analyse spectrale (NDVI, indices végétation) |
| `gis_omega/` | GIS avancé (H3, corridors, zones) |
| `terrain_hr_omega/` | Terrain haute résolution (DEM, pente, exposition) |
| `hydro_topo_omega/` | Hydrologie et topographie |
| `eco_zones_omega/` | Zones écologiques et biomes |
| `weather_v3/` | Météo et impact faunique (source unique BCE-4X) |
| `corridor_omega/` | Corridors de déplacement faunique |
| `v8_institutional/` | Modules institutionnels territoriaux (~30 sous-modules) |
| + 12 autres moteurs | Voir `backend/engines/` |

---

## backend/modules/ — Fonctionnalités applicatives

Les modules applicatifs servent les endpoints `/api/v1/*` (API legacy, utilisée par le frontend actuel).

**Catégories :**
- **Auth & Users** : auth_engine, user_engine, roles_engine
- **Commerce** : cart_engine, orders_engine, payment_engine, products_engine, saline_engine
- **Territoire** : territory_engine, waypoint_engine, tracking_engine
- **Social** : networking_engine, referral_engine, partner_engine
- **Contenu** : notification_unified_engine, seo_engine, marketing_engine
- **Science** : scoring_engine⚠️, nutrition_engine⚠️, wildlife_behavior_engine⚠️, ecoforestry_engine⚠️
- **Spécialisés** : camera_engine, vision_engine, guide_pro_engine, live_heading_engine
- **Admin** : master_switch, freemium_engine, admin_backup_engine

⚠️ = Module déprécié avec DEPRECATED.md — remplacé par un moteur Omega dans `engines/`

---

## Couches API

| Préfixe | Source | Statut |
|---|---|---|
| `/api/v1/*` | `modules/routers.py` → CORE_ROUTERS | LEGACY — actif pour le frontend |
| `/api/v20/*` | `server.py` → engines Omega | V10 — institutionnel |
| `/api/v30/*` | `server.py` → admin premium GIS | V10 — admin |
| `/api/v51/*` | `modules/v51_engines/` | ACTIF — 22 moteurs temporels/solunaires |
| `/api/p1/*` | `modules/p1_engines/` | ACTIF — 12 moteurs, 14 endpoints |
| `/api/schema/*` | `server.py` → BIO_PROFILE_OMEGA_135 | V10 — schéma institutionnel |

### Plan de migration
Les endpoints `/api/v1/*` seront progressivement migrés vers `/api/v20/*` (voir les `DEPRECATED.md` dans les modules concernés).

---

## Sécurité

- **WMS Proxy** : whitelist stricte urlparse (Phase 5, SSRF patché)
- **Auth** : JWT via GitHub Secrets
- **Repo** : PRIVÉ
- **Déploiement** : GitHub Actions avec secrets chiffrés

---

## Historique

| Version | Date | Notes |
|---|---|---|
| V5-ULTIME-FUSION | ~mars 2026 | Fusion V2+V3+V4+BASE, 78 modules |
| V7 (BIONIC_ULTIME_V7) | juin 2026 | Patch R4 Sentinel |
| **V10 (main)** | **août 2026** | **25 moteurs Omega, ~90 modules, refactoring complet** |
