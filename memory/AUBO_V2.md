# AUBO V2 — ARCHITECTURE UNIFIEE BIONIC OS
## Directive x5302-STEEVE_MAX — Version 2.0.0
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-05 | Merge MAIN : STRICTEMENT INTERDIT
### Base : AUBO_V1 1.0.0 (673 lignes) + 6 ajouts + 2 corrections + 4 sections manquantes

---

# TABLE DES MATIERES

**PARTIE I — ARCHITECTURE BACKEND**
1. [DOMAINES](#1-domaines)
2. [PIPELINES](#2-pipelines)
3. [MOTEURS SPECIALISES](#3-moteurs-specialises)
4. [CORE SYSTEMS](#4-core-systems)
5. [SOUS-ROUTEURS BIONIC_ENGINE_P0](#5-sous-routeurs-bionic_engine_p0)

**PARTIE II — FRONTEND**
6. [CARTOGRAPHIE FRONTEND](#6-cartographie-frontend)

**PARTIE III — DONNEES**
7. [BASE DE DONNEES MONGODB](#7-base-de-donnees-mongodb)

**PARTIE IV — INFRASTRUCTURE**
8. [ROUTES BACKEND /routes/](#8-routes-backend-routes)
9. [BCE ENGINE — DETAIL](#9-bce-engine-detail)
10. [INTEGRATIONS EXTERNES](#10-integrations-externes)
11. [DEPLOIEMENT & INFRASTRUCTURE](#11-deploiement-et-infrastructure)

**PARTIE V — GOUVERNANCE & SECURITE**
12. [INTERCONNEXIONS P3-P6](#12-interconnexions-p3-p6)
13. [GOUVERNANCE](#13-gouvernance)
14. [SECURITE ET PERMISSIONS](#14-securite-et-permissions)

**PARTIE VI — QUALITE & HISTORIQUE**
15. [MONITORING & OBSERVABILITE](#15-monitoring-et-observabilite)
16. [TESTS & QUALITE](#16-tests-et-qualite)
17. [CHANGELOG CONSOLIDATION V6](#17-changelog-consolidation-v6)

**ANNEXES**
A. [CARTOGRAPHIE COMPLETE (V2)](#annexe-a-cartographie-complete-v2)
B. [DELTA V1 → V2](#annexe-b-delta-v1-v2)

---

# PARTIE I — ARCHITECTURE BACKEND

---

# 1. DOMAINES

## Classification des modules (Correction V2 — §2.2)

AUBO_V2 clarifie la distinction entre 4 categories de modules :

| Categorie | Definition | Exemple | Comptage |
|-----------|------------|---------|----------|
| **ACTIF** | Module avec endpoints propres, charge par routers.py | admin_engine, scoring_engine | 70+ |
| **FACADE** | Module de consolidation logique, redirige vers sous-modules | ads_engine, learning_engine | 2 |
| **DEPRECATED** | Code present mais inactif, successeur designe | geo_engine, core/alimentation | 2 |
| **STANDALONE** | Fichier .py unique sans directory propre | score_consolide.py, docs.py | 12 |

---

## 1.1 Domaine ANALYSE & SCORING

Moteur principal d'analyse de territoires de chasse. Coeur fonctionnel de BIONIC OS.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| bionic_engine_p0 | /v1/bionic | 154 | Moteur d'analyse principal — 36 sous-routeurs (SSE, OSG, CME, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE, pipeline, hotspots, organic zones, spatial clipping, seasonal conditions, hunting path, calibration, dem, ndvi shadow, ML, etc.) | ACTIF |
| scoring_engine | /api/v1/scoring | 6 | Scoring multi-criteres sur 100 points | ACTIF |
| waypoint_scoring_engine | /api/v1/waypoint-scoring | 11 | Scoring des waypoints — evaluation qualite des points GPS | ACTIF |
| score_consolide (standalone) | interne | — | Score consolide x4100 — fusion 22 moteurs (Option C) | STANDALONE |
| score_preparation (standalone) | interne | — | Pre-traitement et normalisation des scores | STANDALONE |
| bionic_data_fabric | /api/v1/data-fabric | 6 | Fabric de donnees unifie — agregation multi-source | ACTIF |
| nutrition_engine | /api/v1/nutrition | 8 | Moteur nutritionnel V1 — attractants, mineraux, proteines | ACTIF |
| saline_engine | /api/v1/saline | 26 | Moteur saline — analyse salines, scoring | ACTIF |
| salines_ultime_engine | /api/v1/salines-ultime | 3 | Scores salines ultime — 5 scores + 20 sources scientifiques | ACTIF |
| bionic_stand_recommendation_engine | /api/v1/stand-recommendation | 2 | Recommandation de postes d'affut — positionnement optimal | ACTIF |
| predictive_engine | /api/v1/predictive | 7 | Previsions predictives — probabilites de succes, timing | ACTIF |
| solunar (standalone) | interne | — | Calculs solunaires — phases lunaires, periodes d'activite | STANDALONE |
| legal_time_engine | /api/v1/legal-time | 7 | Heures legales de chasse — lever/coucher soleil, periodes | ACTIF |

**Dependances critiques** : core/scoring_pipeline, core/weather, core/pressure, core/ecology
**Modules critiques** : bionic_engine_p0 (154 endpoints — hub central d'analyse)
**Endpoints domaine** : 230

---

## 1.2 Domaine SUPRA

Intelligence avancee multi-criteres. Couche superieure de l'analyse.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| supra_advanced (engine) | /api/v6/supra/advanced | 4 | Analyse SUPRA avancee multi-criteres | ACTIF |
| nutrition_intelligence (engine) | /api/v6/nutrition-intelligence | 35 | Intelligence nutritionnelle SUPRA | ACTIF |
| bionic_knowledge_engine | /api/v1/bionic/knowledge | 35 | Base de connaissances BIONIC — donnees scientifiques | ACTIF |
| ai_engine | /api/v1/ai | 15 | Moteur IA principal — recommandations, analyse intelligente | ACTIF |
| recommendation_engine | /api/v1/recommendation | 11 | Recommandations personnalisees — produits, zones, strategies | ACTIF |
| strategy_master_engine | /api/v1/strategy-master | 12 | Strategies de chasse globales — plans, optimisation | ACTIF |

**Dependances critiques** : bionic_engine_p0, scoring_engine, nutrition_engine
**Modules critiques** : nutrition_intelligence (35 endpoints — hub nutritionnel SUPRA)
**Endpoints domaine** : 112

---

## 1.3 Domaine GEOSPATIAL

Donnees geographiques, ecologiques, et environnementales.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| geospatial_engine | /api/v1/geospatial | 33 | Analyse geospatiale + logique Geo Engine absorbee (Consolidation V6) | ACTIF |
| geo_engine | /api/admin/geo | 26 | Fusionne dans geospatial_engine | DEPRECATED |
| ecoforestry_engine | /api/v1/ecoforestry | 7 | Donnees ecoforestieres — peuplements, drainage, depots | ACTIF |
| bionic_ecological_engine | /api/v1/ecological-intelligence | 16 | Intelligence ecologique — habitat, biodiversite | ACTIF |
| soil_engine | /api/v1/soil | 2 | Donnees pedologiques — types de sol, drainage, fertilite | ACTIF |
| wms_engine | /api/v1/wms | 9 | Proxy WMS Quebec (MRNF) — cartes ecoforestieres | ACTIF |
| data_layers | /api/v1/data/* | 59 | 5 couches de donnees (ecoforestry, behavioral, simulation, 3d, geospatial-advanced) | ACTIF |
| wildlife_behavior_engine | /api/v1/wildlife | 8 | Comportement animal — patterns, mouvements, habitat | ACTIF |
| weather_fauna_simulation_engine | /api/v1/simulation | 8 | Simulation meteo-faune — impact conditions sur comportement | ACTIF |
| weather_v3 (engine) | /api/v3/weather | 4 | Meteo BIONIC V3 temps reel | ACTIF |
| territory_engine | interne | 6 | Gestion des territoires — CRUD, polygones, metadata | ACTIF |
| engine_3d | /api/v1/3d | 7 | Visualisation 3D du terrain — elevation, relief | ACTIF |

**Dependances critiques** : core/geo, core/ndvi, core/ecology, core/corridors
**Modules critiques** : geospatial_engine (33 endpoints — hub geospatial post-consolidation)
**Endpoints domaine** : 185

---

## 1.4 Domaine E-COMMERCE

Catalogue produits, commandes, paiements, fournisseurs, affiliation.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| products_engine | /api/v1/products | 13 | CRUD produits — catalogue, scoring, import CSV/Excel | ACTIF |
| cart_engine | /api/v1/cart | 7 | Gestion du panier — session saline, ajout/suppression, totaux | ACTIF |
| orders_engine | /api/v1/orders | 9 | Gestion des commandes — creation, statut, historique | ACTIF |
| payment_engine | /api/v1/payments | 6 | Integration Stripe — checkout, webhooks, remboursements | ACTIF |
| suppliers_engine | /api/v1/suppliers | 7 | Gestion des fournisseurs/marchands — catalogue, commissions | ACTIF |
| customers_engine | /api/v1/customers | 7 | Gestion des clients — profils, historique, segmentation | ACTIF |
| ads_engine | — | — | Consolidation logique pour affiliate_ads_engine + ad_spaces_engine | FACADE |
| affiliate_ads_engine | /api/v1/affiliate-ads | 24 | Annonces affiliees, creatives, tracking conversions | ACTIF |
| ad_spaces_engine | /api/v1/ad-spaces | 16 | Espaces publicitaires sur la plateforme | ACTIF |
| affiliate_switch_engine | /api/v1/affiliate-switch | 15 | Basculement dropshipping/affiliation, mode hybride | ACTIF |
| marketplace_engine | /api/v1/marketplace | 9 | Place de marche — listing produits tiers | ACTIF |
| freemium_engine | /api/v1/freemium | 8 | Plans Free/Premium/Pro — quotas, feature flags | ACTIF |
| upsell_engine | /api/v1/upsell | 6 | Campagnes d'upsell — triggers, conversion, A/B testing | ACTIF |
| liste_epicerie (utility_modules) | interne | — | Liste de courses du chasseur — equipement, provisions | STANDALONE |

**Dependances critiques** : Stripe (paiements), roles_engine (permissions)
**Modules critiques** : payment_engine (integration Stripe), products_engine (catalogue central)
**Endpoints domaine** : 127

---

## 1.5 Domaine MARKETING

Partage, SEO, tracking, campagnes, calendrier.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| share_engine | /api/share | 11 | Share Engine V1 — 14 canaux, EASYlead tracking, screenshot + watermark | ACTIF |
| marketing_engine | /api/v1/marketing | 22 | Automation marketing — segmentation, campagnes, tracking | ACTIF |
| marketing_calendar_engine | /api/v1/marketing-calendar | 13 | Calendrier marketing V2 — evenements, rappels, campagnes | ACTIF |
| seo_engine | /api/v1/bionic/seo | 59 | SEO — meta tags, sitemap, SEO fournisseurs x300 | ACTIF |
| tracking_engine | /api/v1/tracking-engine | 22 | Tracking comportemental — sessions, evenements, heatmaps | ACTIF |
| analytics_engine | /api/v1/analytics | 11 | Tracking requetes API, temps de reponse, volume | ACTIF |
| bsaa | /api/bsaa | 9 | BIONIC Social Ads Automation (architecture definie, implementation GELEE) | ACTIF |
| referral_engine | /api/v1/referral | 15 | Programme de parrainage — codes, tracking, recompenses | ACTIF |
| contact_engine | /api/v1/contact-engine | 7 | Gestion des contacts et CRM interne | ACTIF |

**Dependances critiques** : html2canvas (screenshot), MongoDB (tracking)
**Modules critiques** : seo_engine (59 endpoints), marketing_engine (22 endpoints)
**Endpoints domaine** : 169

---

## 1.6 Domaine SOCIAL & RESEAUTAGE

Communication, messagerie, reseau de chasseurs.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| networking_engine | /api/v1/network | 19 | Reseau social de chasseurs — publications, feed, groupes | ACTIF |
| messaging_engine | /api/v1/messaging | 16 | Messagerie interne — notifications push, templates, file | ACTIF |
| notification_unified_engine | /api/v1/notifications | 17 | Notifications unifiees — push, email, in-app | ACTIF |
| partner_engine | /api/partners | 7 | Programme partenaires — inscription, dashboard, offres | ACTIF |
| camera_engine | /api/v1/camera | 9 | Cameras de trail — photos, detection, analyse | ACTIF |
| hunting_trip_logger | /api/v1/trips | 14 | Journal des sorties de chasse — logs, photos, resultats | ACTIF |
| live_heading_engine | /api/v1/live-heading | 14 | Cap de navigation en temps reel — boussole, direction | ACTIF |
| waypoint_engine | /api/v1/waypoints | 8 | Gestion des waypoints — CRUD, partage, scoring | ACTIF |
| chasseur_jumeau (experiments) | interne | — | Chasseur Jumeau — profil similaire, matching | STANDALONE |

**Modules critiques** : networking_engine (19 endpoints — hub social)
**Endpoints domaine** : 104

---

## 1.7 Domaine ADMIN & CONFIGURATION

Gouvernance, configuration, gestion utilisateurs, backups.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| admin_engine | /api/v1/admin | 210 | Centre de gouvernance Admin Premium — configuration globale | ACTIF |
| user_engine | /api/v1/user | 17 | Gestion des utilisateurs — profils, preferences, historique | ACTIF |
| roles_engine | /api/v1/roles | 14 | Gestion des roles et permissions | ACTIF |
| auth_engine | /api/auth | 12 | Authentification — JWT, login, register, reset password, Google OAuth | ACTIF |
| onboarding_engine | /api/v1/onboarding | 6 | Flux d'accueil nouveaux utilisateurs | ACTIF |
| learning_engine | — | — | Consolidation logique pour tutorial_engine + formations_engine | FACADE |
| tutorial_engine | /api/v1/tutorials | 8 | Contenus pedagogiques — tutoriels, progression | ACTIF |
| formations_engine | /api/formations | 4 | Formations FedeCF et BIONIC Academy | ACTIF |
| progression_engine | /api/v1/progression | 13 | Progression utilisateur — niveaux, badges | ACTIF |
| rules_engine | /api/v1/rules | 8 | Regles metier configurables — conditions, actions | ACTIF |
| trigger_engine | /api/v1/trigger-engine | 8 | Declencheurs d'evenements — conditions, actions | ACTIF |
| alerts_engine | /api/v1/alerts | 10 | Systeme d'alertes configurable | ACTIF |
| backup_cloud_engine | /api/backup-cloud | 11 | Backup cloud automatise, restauration | ACTIF |
| optimization_engine | /api/admin/optimization | 13 | Propositions d'optimisation systeme, gestion versions | ACTIF |
| engine_registry | interne | — | Registre central de tous les moteurs | STANDALONE |
| api_gateway | /api/v3 | 12 | Passerelle API V3 — routage intelligent | ACTIF |
| plugins_engine | /api/v1/plugins | 8 | Systeme de plugins extensible | ACTIF |

**Modules critiques** : admin_engine (210 endpoints — hub d'administration central)
**Endpoints domaine** : 354

---

## 1.8 Domaine SECURITE & ACCES

Firewall, controle d'acces, verification.

| Module | Prefix API | Endpoints | Role | Categorie |
|--------|-----------|-----------|------|-----------|
| ultra_max_firewall | /api/firewall | 5 | Pare-feu ULTRA-MAX++ — geo-fencing urbain, 7 verrous runtime | ACTIF |
| master_switch | /api/v1/master-switch | 19 | Controle global ON/OFF — autorite STEEVE-MAX, sync 9 modules | ACTIF |
| access_engine_v6 | /api/v6/access | 3 | Controle d'acces par zone geographique | ACTIF |
| access_clarity_engine_v7 | /api/v7/clarity | 3 | Clarification des niveaux d'acces, reporting conflits | ACTIF |

**Modules critiques** : ultra_max_firewall (verrous runtime), master_switch (controle global)
**Endpoints domaine** : 30

---

## MODULES STANDALONE (12)

| Module | Emplacement | Role | Reclassification V6 | Categorie |
|--------|------------|------|---------------------|-----------|
| chasseur_jumeau.py | experiments/ | Chasseur Jumeau — profil similaire | RECLASSE | STANDALONE |
| liste_epicerie.py | utility_modules/ | Liste de courses du chasseur | RECLASSE | STANDALONE |
| docs.py | modules/ | Documentation API generee | — | STANDALONE |
| hunter_score.py | modules/ | Score chasseur individuel | — | STANDALONE |
| next_step_engine.py | modules/ | Recommandation de prochaine etape | — | STANDALONE |
| permis_checklist.py | modules/ | Checklist permis de chasse | — | STANDALONE |
| plan_saison.py | modules/ | Planification saison de chasse | — | STANDALONE |
| pourvoirie_finder.py | modules/ | Recherche de pourvoiries | — | STANDALONE |
| score_consolide.py | modules/ | Score consolide x4100 | — | STANDALONE |
| score_preparation.py | modules/ | Preparation des scores | — | STANDALONE |
| setup_builder.py | modules/ | Constructeur de configuration | — | STANDALONE |
| user_context.py | modules/ | Contexte utilisateur — session | — | STANDALONE |

---

## FICHIERS BACKEND RACINE (10)

Fichiers Python a la racine de /backend/ herites du monolithe, charges directement par server.py.

| Fichier | Endpoints | Role |
|---------|-----------|------|
| networking.py | 33 | Reseau chasseurs (heritage monolithe) |
| partnership.py | 29 | Programme partenaires (heritage monolithe) |
| lands_rental.py | 20 | Location de terres de chasse |
| bionic_engine.py | 18 | Moteur bionic legacy (routes monolithe) |
| seo_analytics.py | 17 | SEO analytics legacy |
| marketplace.py | 15 | Place de marche legacy |
| hunting_groups.py | 12 | Groupes de chasse |
| notifications.py | 10 | Notifications legacy |
| feature_controls.py | 9 | Controle des fonctionnalites |
| zone_favorites.py | 9 | Zones favorites |
| live_tracking.py | 8 | Tracking temps reel |
| site_access.py | 7 | Controle d'acces site |
| email_notifications.py | 6 | Notifications email |
| payments.py | 5 | Paiements legacy |
| wms_proxy_router.py | 3 | Proxy WMS legacy |
| auth_helpers.py | 2 | Helpers authentification |

**Total endpoints fichiers racine** : 203

---

# 2. PIPELINES

## 2.1 Pipeline SUPRA

```
[Utilisateur] --> [Selection zone sur carte]
       |
       +---> bionic_engine_p0 (/v1/bionic)
       |       |
       |       +---> SSE (Species Scoring Engine)
       |       +---> OSG (Organic Scoring Grid)
       |       +---> CME (Corridor Movement Engine)
       |       +---> WSE (Weather Scoring Engine)
       |       +---> VFE (Vegetation Factor Engine)
       |       +---> SSVL (Species-Specific Vegetation Layer)
       |       +---> TCVE (Terrain Characteristic Value Engine)
       |       +---> PME (Pressure Measurement Engine)
       |       +---> BMPE (BIONIC Multi-Parameter Engine)
       |       +---> TFE (Terrain Feature Engine)
       |
       +---> supra_advanced (/api/v6/supra/advanced)
       +---> nutrition_intelligence (/api/v6/nutrition-intelligence)
       +---> soil_engine (/api/v1/soil)
       +---> weather_v3 (/api/v3/weather)
       +---> wildlife_behavior_engine (/api/v1/wildlife)
       |
       +---> [Score CHASSE /100 + 32 criteres + zones ecologiques]
               |
               +---> core/scoring_pipeline (normalisation)
               +---> core/corridors (deplacement)
               +---> core/ecology (habitat)
               +---> core/pressure (pression anthropique)
               +---> core/ndvi (vegetation satellite)
               +---> core/weather (conditions meteo)
```

**Entree** : Coordonnees GPS ou polygone territoire
**Sortie** : Score /100, 32 criteres detailles, zones ecologiques, corridors, hotspots, salines
**Sous-moteurs** : 10 (SSE, OSG, CME, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE)
**Core impliques** : 6/9

---

## 2.2 Pipeline E-Commerce

```
[Visiteur] --> [ShopPage]
       |
       +---> products_engine (/api/v1/products)
       |       +---> Catalogue + filtrage + scoring BIONIC
       |       +---> Synchronisation suppliers_engine
       |
       +---> [Ajout panier] --> cart_engine (/api/v1/cart)
       |
       +---> [Checkout] --> payment_engine (/api/v1/payments)
       |       +---> Stripe Checkout Session
       |       +---> Webhooks Stripe (confirmation)
       |       +---> orders_engine (creation commande)
       |
       +---> [Affiliation] --> ads_engine (FACADE consolidated)
       |       +---> affiliate_ads_engine (/api/v1/affiliate-ads)
       |       +---> ad_spaces_engine (/api/v1/ad-spaces)
       |       +---> affiliate_switch_engine (/api/v1/affiliate-switch)
       |
       +---> [Fournisseurs] --> suppliers_engine (/api/v1/suppliers)
               +---> customers_engine (/api/v1/customers)
```

**Integration externe** : Stripe (paiements)
**Modules impliques** : 10

---

## 2.3 Pipeline Territoire

```
[Utilisateur] --> [MonTerritoireBionicPage]
       |
       +---> geospatial_engine (/api/v1/geospatial) — hub geospatial
       +---> ecoforestry_engine (/api/v1/ecoforestry) — peuplements
       +---> soil_engine (/api/v1/soil) — pedologie
       +---> data_layers (/api/v1/data/*) — 5 couches
       +---> wms_engine (/api/v1/wms) — cartes MRNF
       |
       +---> [Navigation] --> terrain_nav (engine)
       |       +---> waypoint_engine (/api/v1/waypoints)
       |       +---> live_heading_engine (/api/v1/live-heading)
       |
       +---> [Observation] --> hunting_trip_logger (/api/v1/trips)
       |       +---> camera_engine (/api/v1/camera)
       |
       +---> [Partage] --> share_engine (/api/share)
               +---> EASYlead tracking (generate + track + stats)
```

**Core impliques** : core/geo, core/ndvi, core/ecology

---

## 2.4 Pipeline Marketing

```
[Partage] --> share_engine (/api/share)
       |
       +---> EASYlead V1 (generate, track, stats)
       +---> Marketing Engine (auto-capture, lead scoring)
       +---> Screenshot + watermark BIONIC OS
       |
       +---> [Tracking] --> tracking_engine (/api/v1/tracking-engine)
       |       +---> analytics_engine (/api/v1/analytics)
       |
       +---> [SEO] --> seo_engine (/api/v1/bionic/seo)
       |       +---> 59 endpoints, SEO fournisseurs x300
       |
       +---> [Campagnes] --> marketing_engine (/api/v1/marketing)
       |       +---> marketing_calendar_engine (/api/v1/marketing-calendar)
       |
       +---> [Contacts] --> contact_engine (/api/v1/contact-engine)
       |
       +---> [Referral] --> referral_engine (/api/v1/referral)
```

---

## 2.5 Pipeline Abonnements

```
[Utilisateur Free] --> [PricingPage]
       |
       +---> freemium_engine (/api/v1/freemium)
       |       +---> Plans : Free / Premium / Pro
       |       +---> Quotas d'utilisation
       |       +---> Feature gating
       |
       +---> [Upgrade] --> payment_engine (/api/v1/payments)
       |       +---> Stripe Checkout
       |
       +---> [Post-upgrade] --> upsell_engine (/api/v1/upsell)
       |       +---> Campagnes d'upsell
       |       +---> A/B testing
       |
       +---> [Onboarding] --> onboarding_engine (/api/v1/onboarding)
               +---> learning_engine (FACADE consolidated)
                       +---> tutorial_engine (/api/v1/tutorials)
                       +---> formations_engine (/api/formations)
```

---

# 3. MOTEURS SPECIALISES

5 engines dans /engines/ — services a haute specialisation.

| # | Moteur | Prefix API | Endpoints | Role | Dependances |
|---|--------|-----------|-----------|------|-------------|
| E1 | hunt_orchestrator | /api/v1/hunt | 6 | Orchestration complete de la session de chasse | bionic_engine_p0, weather_v3, strategy_master |
| E2 | nutrition_intelligence | /api/v6/nutrition-intelligence | 35 | Intelligence nutritionnelle SUPRA | nutrition_engine, salines_ultime |
| E3 | supra_advanced | /api/v6/supra/advanced | 4 | Analyse SUPRA avancee multi-criteres | bionic_engine_p0, scoring_engine |
| E4 | terrain_nav | interne | 0 | Navigation terrain et routage (service interne) | geo(spatial), waypoint_engine |
| E5 | weather_v3 | /api/v3/weather | 4 | Meteo BIONIC V3 temps reel | core/weather, predictive_engine |

**Total endpoints engines** : 49

---

# 4. CORE SYSTEMS

9 sous-systemes dans /core/ — fondations partagees.

| # | Core | Endpoints | Role | Modules dependants | Statut |
|---|------|-----------|------|--------------------|--------|
| C1 | alimentation | 0 | Alimentation et nutrition animale | nutrition_engine, bionic_engine_p0 | DEPRECATED |
| C2 | corridors | 0 | Calcul des corridors de deplacement | bionic_engine_p0, wildlife_behavior | ACTIF |
| C3 | ecology | 0 | Moteur ecologique et habitat | bionic_ecological_engine, bionic_engine_p0 | ACTIF |
| C4 | geo | 0 | Geolocalisation et GIS utilitaires | geospatial_engine, territory_engine | ACTIF |
| C5 | ndvi | 0 | Indice de vegetation satellite | bionic_engine_p0, ecoforestry_engine | ACTIF |
| C6 | pressure | 0 | Pression de chasse et anthropique | bionic_engine_p0, scoring_engine | ACTIF |
| C7 | rest | 0 | Zones de repos et refuges | bionic_engine_p0, wildlife_behavior | ACTIF |
| C8 | scoring_pipeline | 20 | Pipeline de scoring unifie | score_consolide, saline_engine, api_gateway | ACTIF |
| C9 | weather | 0 | Donnees meteorologiques | weather_v3, predictive_engine | ACTIF |

**Core actifs** : 8/9 (1 deprecie)
**Endpoints core** : 20

---

# 5. SOUS-ROUTEURS BIONIC_ENGINE_P0

**(Section AUBO_V2 — Ajout §1.5)**

Le module bionic_engine_p0 est le hub central d'analyse avec 154 endpoints repartis sur 36 sous-routeurs.

## 5.1 Architecture interne

```
bionic_engine_p0/
    +-- router.py                  (19 endpoints directs)
    +-- scoring_router.py          (6 endpoints scoring)
    +-- hotspots/hotspot_router.py (12 endpoints hotspots)
    +-- routers/                   (33 sous-routeurs specialises)
    +-- engines/                   (13 moteurs de calcul)
    +-- services/                  (60+ services metier)
    +-- knowledge/                 (base de connaissances)
    +-- contracts/                 (contrats de donnees)
    +-- schemas/                   (schemas Pydantic)
    +-- modules/                   (modules comportementaux)
    +-- tests/                     (10 fichiers de tests)
```

## 5.2 Sous-routeurs — Inventaire complet

| # | Sous-routeur | Endpoints | Role |
|---|-------------|-----------|------|
| SR1 | calibration_router | 19 | Calibration des modeles predictifs |
| SR2 | hotspot_router | 12 | Administration hotspots BIONIC |
| SR3 | notifications_router | 9 | Notifications temps reel |
| SR4 | gps_ultimate_router | 7 | GPS Ultimate — cartographie auto |
| SR5 | observations_router | 6 | Observations terrain |
| SR6 | scoring_router | 6 | Scoring BIONIC |
| SR7 | ml_router | 5 | Machine Learning — modeles predictifs |
| SR8 | dem_shadow_router | 5 | Ombres DEM (Digital Elevation Model) |
| SR9 | waypoint_analysis_router | 4 | Analyse qualite des waypoints |
| SR10 | pipeline_router | 4 | Pipeline d'analyse complet |
| SR11 | ndvi_shadow_router | 4 | Ombres NDVI satellite |
| SR12 | engines_v3_router | 4 | Moteurs V3 (phenologie, typologie, perturbation) |
| SR13 | organic_zones_router | 3 | Zones organiques naturelles |
| SR14 | dem_router | 3 | Donnees elevation terrain |
| SR15 | wse_wiv_router | 2 | Weather Scoring Engine + Wind Impact |
| SR16 | vfe_router | 2 | Vegetation Factor Engine |
| SR17 | tfe_router | 2 | Terrain Feature Engine |
| SR18 | terrain_data_router | 2 | Donnees terrain brutes |
| SR19 | tcve_router | 2 | Terrain Characteristic Value Engine |
| SR20 | ssvl_router | 2 | Species-Specific Vegetation Layer |
| SR21 | sse_router | 2 | Species Scoring Engine |
| SR22 | spatial_clipping_router | 2 | Decoupage spatial |
| SR23 | shadow_router | 2 | Calculs ombres terrain |
| SR24 | route_planner_router | 2 | Planification d'itineraires |
| SR25 | pme_router | 2 | Pressure Measurement Engine |
| SR26 | osg_router | 2 | Organic Scoring Grid |
| SR27 | movement_corridors_router | 2 | Corridors de mouvement |
| SR28 | hunting_path_router | 2 | Sentiers de chasse optimaux |
| SR29 | hunt_plan_router | 2 | Plan de chasse |
| SR30 | habitat_score_router | 2 | Score d'habitat |
| SR31 | full_comparison_router | 2 | Comparaison complete de zones |
| SR32 | engines_v2_router | 2 | Moteurs V2 legacy |
| SR33 | cme_router | 2 | Corridor Movement Engine |
| SR34 | bmpe_router | 2 | BIONIC Multi-Parameter Engine |
| SR35 | seasonal_conditions_router | 1 | Conditions saisonnieres |
| SR36 | dynamic_scores_router | 1 | Scores dynamiques temps reel |
| SR37 | compare_router | 1 | Comparaison rapide |
| SR38 | api_keys_router | 1 | Gestion cles API |

**Total sous-routeurs** : 38 (33 dans /routers/ + scoring_router + hotspot_router + 3 internes)
**Total endpoints bionic_engine_p0** : 154

## 5.3 Moteurs de calcul internes (/engines/)

| # | Moteur | Fichier | Role |
|---|--------|---------|------|
| ME1 | SSE | sse_engine.py (via services/) | Species Scoring — evaluation par espece |
| ME2 | OSG | osg_engine.py | Organic Scoring Grid — grille naturelle |
| ME3 | CME | cme_engine.py | Corridor Movement — deplacement faune |
| ME4 | WSE/WIV | wse_wiv_engine.py | Weather Scoring + Wind Impact Vector |
| ME5 | VFE | vfe_engine.py | Vegetation Factor — couvert vegetal |
| ME6 | SSVL | ssvl_engine.py | Species-Specific Vegetation Layer |
| ME7 | TCVE | tcve_engine.py | Terrain Characteristic Value |
| ME8 | PME | pme_engine.py | Pressure Measurement — pression humaine |
| ME9 | BMPE | bmpe_engine.py | BIONIC Multi-Parameter Engine |
| ME10 | TFE | tfe_engine.py | Terrain Feature — relief, pentes |
| ME11 | Daily Routine | daily_routine_engine.py | Routines quotidiennes animales |
| ME12 | Disturbance | disturbance_engine.py | Perturbations environnementales |
| ME13 | Habitat Enhancement | habitat_enhancement_engine.py | Amenagement d'habitat |
| ME14 | Phenology | phenology_engine.py | Phenomenes saisonniers vegetaux |
| ME15 | Typology | typology_engine.py | Typologie des zones |
| ME16 | Movement V9 | movement_engine_v9.py | Mouvement faune V9 |
| ME17 | Corridors V9 | corridors_v9.py | Corridors deplacement V9 |
| ME18 | Weather V3 | weather_engine_v3.py | Bridge meteo V3 |
| ME19 | Learning | learning_engine.py | Apprentissage comportemental |
| ME20 | Nutrition | nutrition_engine.py | Analyse nutritionnelle interne |
| ME21 | Hunting Path | hunting_path.py | Calcul sentiers optimaux |

## 5.4 Base de connaissances (/knowledge/)

| Sous-module | Fichiers | Role |
|-------------|---------|------|
| species/ | 6 fichiers (moose, deer, bear, elk, mule_deer, advanced_factors) | Regles comportementales par espece |
| calibration/ | 3 fichiers | Optimisation et prediction mobilite |
| corridors/ | 1 fichier | Modeles corridors |
| seasonal/ | 4 fichiers (calving, juvenile, seasonal, thermal) | Facteurs saisonniers |
| gps_ultimate/ | 5 fichiers | Cartographie auto, observations, securite |
| human_pressure/ | 1 fichier | Modele pression humaine |
| mobility/ | 1 fichier | Modeles mobilite |
| notifications/ | 2 fichiers | Registre et webpush |
| sources/ | 1 fichier | Schema sources scientifiques |
| validation/ | 3 fichiers | Pipeline validation Phase G |
| weights/ | 1 fichier | Poids habitat par espece |
| terrain/ | 1 fichier | Exclusion zones eau |
| ecological_database_v8.py | 1 fichier | Base ecologique V8 |

---

# PARTIE II — FRONTEND

---

# 6. CARTOGRAPHIE FRONTEND

**(Section AUBO_V2 — Ajout §1.1)**

## 6.1 Metriques globales

| Metrique | Valeur |
|----------|--------|
| Pages uniques | 38 |
| Routes (avec redirections) | 50 |
| Composants metier (hors UI) | 143 |
| Composants territoire | 65 |
| Composants UI (Shadcn) | 47 |
| Modules frontend | 30 sous-modules, 139 fichiers |
| Hooks personnalises | 18 |
| Stores Zustand | 2 |
| Contexts React | 1 |

## 6.2 Pages — Cartographie complete

| # | Route | Composant | Domaine | Backend consomme |
|---|-------|-----------|---------|------------------|
| P1 | / | HomePage | Accueil | — |
| P2 | /onboarding | OnboardingPage | Admin | onboarding_engine |
| P3 | /compare | ComparePage | Analyse | bionic_engine_p0 |
| P4 | /shop | ShopPage | E-Commerce | products_engine, cart_engine |
| P5 | /mon-territoire-bionic | MonTerritoireBionicPage | Geospatial | bionic_engine_p0, geospatial, soil, weather, data_layers, wms, share |
| P6 | /formations | FormationsPage | Admin | formations_engine |
| P7 | /permis-chasse | HuntingLicensePage | Admin | bionic_engine_router |
| P8 | /dashboard | DashboardPage | Analytics | analytics_engine, user_engine |
| P9 | /business | BusinessPage | E-Commerce | analytics, marketing |
| P10 | /plan-maitre | PlanMaitrePage | SUPRA | strategy_master_engine, bionic_engine_p0 |
| P11 | /analytics | AnalyticsPage | Analytics | analytics_engine, tracking |
| P12 | /map | MapPage | Geospatial | geospatial_engine, bionic_engine_p0 |
| P13 | /forecast | ForecastPage | Analyse | predictive_engine, weather_v3 |
| P14 | /trips | TripsPage | Social | hunting_trip_logger |
| P15 | /referral | ReferralModule | Marketing | referral_engine |
| P16 | /admin/geo | AdminGeoPage | Admin | geo_engine (deprecated), geospatial |
| P17 | /admin/hotspots | AdminHotspotsPage | Admin | hotspot_router |
| P18 | /networking | NetworkingHub | Social | networking_engine |
| P19 | /lands | LandsRental | E-Commerce | lands_rental |
| P20 | /reset-password | ResetPasswordPage | Auth | auth_engine |
| P21 | /become-partner | BecomePartner | Social | partner_engine |
| P22 | /partner/dashboard | PartnerDashboard | Social | partner_engine |
| P23 | /auth/google/callback | GoogleOAuthCallback | Auth | auth_engine |
| P24 | /pricing | PricingPage | E-Commerce | freemium_engine, payment_engine |
| P25 | /payment/success | PaymentSuccessPage | E-Commerce | payment_engine |
| P26 | /payment/cancel | PaymentCancelPage | E-Commerce | — |
| P27 | /admin-premium | AdminPremiumPage | Admin | admin_engine (210 endpoints) |
| P28 | /marketing-calendar | MarketingCalendarPage | Marketing | marketing_calendar_engine |
| P29 | /bionic-demo | BionicAnalysisDemoPage | Analyse | bionic_engine_p0 |
| P30 | /observations | FieldObservationForm | Social | observations_router |
| P31 | /calibration | CalibrationDashboard | Analyse | calibration_router |
| P32 | /reports | ReportsPage | Admin | reports router |
| P33 | /comparaison-especes | SpeciesComparisonPage | Analyse | bionic_engine_p0 |
| P34 | /product/:productId | ProductPage | E-Commerce | products_engine |
| P35 | /supra/:id | SupraPage | SUPRA | supra_advanced, nutrition_intelligence |
| P36 | /bionic-modules | BionicModulesPage | Admin | engine_registry |
| P37 | /bsaa | BsaaDashboardPage | Marketing | bsaa |
| P38 | (fallback) | MaintenancePage | Systeme | site_config |

**Routes de redirection** : /analyze→/analytics, /territoire→/mon-territoire-bionic, /marketplace→/shop, /admin→/admin-premium, /saline→/mon-territoire-bionic, /nutrition-intelligence→/mon-territoire-bionic, /intelligence→/bionic-modules, /ads→/bsaa

## 6.3 Stores Zustand

| Store | Fichier | Role | Champs principaux |
|-------|---------|------|-------------------|
| useBionicStore | stores/useBionicStore.js | Etat global BIONIC — gibier selectionne, zone, scores, especes, mode split | gibier, selectedZone, scores, selectedSpecies, splitMode |
| useWeatherStore | stores/useWeatherStore.js | Meteo centralisee BCE-4X — source unique METEO BIONIC | weatherData, loading, fetchWeather, lastUpdate |

## 6.4 Hooks personnalises

| # | Hook | Fichier | Role | Module backend associe |
|---|------|---------|------|-----------------------|
| H1 | useAccessRoute | hooks/useAccessRoute.js | Routes d'acces terrain | access_engine_v6 |
| H2 | useBionicLayers | hooks/useBionicLayers.js | Couches carte BIONIC | bionic_engine_p0 |
| H3 | useBionicScoring | hooks/useBionicScoring.js | Scoring multi-criteres | scoring_engine |
| H4 | useBionicSession | hooks/useBionicSession.js | Session utilisateur BIONIC | auth_engine, user_engine |
| H5 | useBionicWeather | hooks/useBionicWeather.js | Meteo BIONIC (bridge store) | weather_v3 |
| H6 | useGeolocation | hooks/useGeolocation.js | Geolocalisation navigateur | — (API Web) |
| H7 | useLiveTracking | hooks/useLiveTracking.js | Tracking temps reel | live_heading_engine |
| H8 | useMapType | hooks/useMapType.js | Type de carte (satellite, topo, etc.) | — |
| H9 | useSharedWeather | hooks/useSharedWeather.js | Meteo partagee entre composants | useWeatherStore |
| H10 | useSharing | hooks/useSharing.js | Partage EASYlead | share_engine |
| H11 | useSpatialClipping | hooks/useSpatialClipping.js | Decoupage spatial zones | bionic_engine_p0 |
| H12 | useSplitViewZones | hooks/useSplitViewZones.js | Mode split-view carte | bionic_engine_p0 |
| H13 | useTerritoireEffects | hooks/useTerritoireEffects.js | Effets visuels territoire | — |
| H14 | useUserData | hooks/useUserData.js | Donnees utilisateur | user_data routes |
| H15 | useWaypointActions | hooks/useWaypointActions.js | Actions waypoints (CRUD) | waypoint_engine |
| H16 | useZoneCache | hooks/useZoneCache.js | Cache zones analysees | — (local) |
| H17 | useZoneOrchestrator | hooks/useZoneOrchestrator.js | Orchestration zones | bionic_engine_p0 |
| H18 | use-toast | hooks/use-toast.js | Notifications toast UI | — |

**Hooks modules** : useGroupeAlerts, useGroupeChat, useGroupeSafety, useGroupeTracking, useOnboarding, useUserProfile, useTutorial, useTutorialProgress (8 hooks supplementaires dans /modules/)

## 6.5 Modules frontend (/modules/)

| # | Module | Composants | Role |
|---|--------|-----------|------|
| M1 | admin | composants admin | Administration plateforme |
| M2 | affiliate | composants affiliation | Gestion affilies |
| M3 | ai | composants IA | Interface IA |
| M4 | analytics | composants analytiques | Tableaux de bord |
| M5 | behavioral | composants comportementaux | Analyse comportement |
| M6 | business | composants business | Dashboard business |
| M7 | cart | composants panier | Panier d'achat |
| M8 | collaborative | composants collaboratifs | Fonctions collaboratives |
| M9 | customers | composants clients | Gestion clients |
| M10 | dashboard | composants dashboard | Tableau de bord principal |
| M11 | ecoforestry | composants ecoforestiers | Couches ecoforestieres |
| M12 | groupe | composants + hooks (4) | Groupes de chasseurs |
| M13 | legaltime | composants temps legal | Heures legales chasse |
| M14 | live_heading_view | composants cap | Navigation boussole |
| M15 | map_hotspots | composants hotspots | Hotspots carte |
| M16 | map_interaction | composants + hooks + services | Interactions carte |
| M17 | notifications | composants notifications | Centre de notifications |
| M18 | nutrition | composants nutrition | Analyse nutritionnelle |
| M19 | onboarding | composants + hooks (2) | Flux d'accueil |
| M20 | orders | composants commandes | Gestion commandes |
| M21 | planmaitre | composants plan maitre | Planification strategique |
| M22 | predictive | composants predictifs | Previsions |
| M23 | products | composants produits | Catalogue produits |
| M24 | recommendation | composants recommandations | Recommandations IA |
| M25 | scoring | composants scoring | Affichage scores |
| M26 | strategy | composants strategie | Strategies de chasse |
| M27 | suppliers | composants fournisseurs | Gestion fournisseurs |
| M28 | territory | composants territoire | Territoire legacy |
| M29 | tutorial | composants + hooks (2) + data | Tutoriels |
| M30 | user | composants utilisateur | Profil utilisateur |
| M31 | wildlife | composants faune | Comportement animal |

## 6.6 Composants territoire principaux

| Categorie | Composants cles |
|-----------|----------------|
| Carte | MonTerritoireBionic, TerritoryShell, MapContent, SplitViewContainer, MapHelpers |
| Couches | EcoforestryLayers, NdviOverlayLayer, HydrographyOverlayLayer, WindFlowLayer, ConsolidatedHeatmapLayer, BionicCorridorsV6Layer, NutritionPointsLayer, HighFidelityMapLayers, HuntingPathLayer, StandsMapLayer, StructureContrastLayer, CursorBionicLayer, ExclusionOverlayLayer, AccessRouteV6Layer, RouteReplayLayer |
| Zones | BionicZone600m, BionicZone2km, BionicPrecisionZonesLayer, BionicMicroZones, BionicMapOverlay |
| Panneaux | IntelligenceDashboard, TerritoryAnalysisPanel, BionicZoneDiagnosticPanel, AmenagementPanel, WaypointUnifiedPanel, StandDetailPanel, NutritionPointDetailPanel, ZoneInfoPanel, PlacesSidePanel, DiagnosticExclusionsPanel, GuidedRoutePanel, GroupDashboard, CompareWidget, SeasonalConditionsWidget |
| UI | TerritoireHeader, TerritoireToolbar, TerritoireDialogs, ShareBionicButton, CriteriaDetailModal, NutritionPanel, WeatherPanel, BiologicalSeasonSelector, GoldenComponents, NutritionAnalysisModal |
| BIONIC | CarteBionic, LayerControlPanel, HotspotListPanel, EnrichedHotspotPopup, SeasonalFactorsPanel, HuntPlanAnalysisPanel, WaypointSelector, SpeciesIcon, MapLegend, ScoreRadarPanel, ScoreDistributionPanel, OptimalWindowsTimeline |
| Securite | BCE4X_UIShield (protection UI BCE-4X) |

---

# PARTIE III — DONNEES

---

# 7. BASE DE DONNEES MONGODB

**(Section AUBO_V2 — Ajout §1.2)**

## 7.1 Inventaire des collections

**Base** : huntiq_v6 | **Collections** : 34 | **Documents totaux** : ~703

| # | Collection | Documents | Champs principaux | Module proprietaire |
|---|-----------|-----------|-------------------|---------------------|
| 1 | users | 1 | user_id, name, email, phone, picture, auth_provider, role, is_active, password_hash, created_at, updated_at | auth_engine, user_engine |
| 2 | user_sessions | 266 | user_id, token, expires_at, created_at | auth_engine |
| 3 | admin_hotspots | 300 | id, region_id, region_name, center, polygon, radius_m, geometry_type, score, classification, category, dominant_species, engines, justification, cell_count, accessibility, corridor_nearby, ville, code_postal, altitude_m, territory_type, gps | hotspot_router |
| 4 | hunting_trips | 50 | user_id, date, species, location_lat, location_lng, duration_hours, weather_conditions, temperature, wind_speed, moon_phase, success, observations, notes | hunting_trip_logger |
| 5 | marketing_events | 16 | event_type, channel, data, created_at, protocol, engine | marketing_engine |
| 6 | marketing_contacts | 13 | email, name, phone, source, first_channel, channels_used, interaction_count, status, score, tags, metadata | contact_engine |
| 7 | share_events | 13 | channel, template, url, has_weather, created_at, client_timestamp | share_engine |
| 8 | cart | 7 | id, product_id, quantity, session_id | cart_engine |
| 9 | marketing_triggers | 7 | id, name, name_fr, trigger_type, condition, action, action_config, delay_minutes, is_active, priority | trigger_engine |
| 10 | products | 5 | id, name, brand, category, subcategory, price, score, rank, image_url, description, ingredients, target_species, season, in_stock | products_engine |
| 11 | supplier_submissions | 4 | submission_id, status, supplier, product, auto_validation, human_review, pipeline_history | suppliers_engine |
| 12 | optimization_proposals | 4 | title, description, type, impact, affected_modules, benefits, risks, requires_restart, estimated_time, status | optimization_engine |
| 13 | firewall_logs | 4 | lat, lng, allowed, zone_name, timestamp | ultra_max_firewall |
| 14 | user_waypoints | 2 | user_id, name, lat, lng, type, active, notes, created_at, updated_at | waypoint_engine |
| 15 | optimization_versions | 2 | version_id, description, created_at, modules, module_snapshots, source | optimization_engine |
| 16 | bsaa_campaigns | 1 | campaign_id, name, description, type, platforms, status, budget, schedule, languages, targeting, content_type, analytics | bsaa |
| 17 | easylead_links | 1 | share_id, user_id, channel, page_shared, easylead_url, has_screenshot, clicks, conversions, status | share_engine |
| 18 | easylead_clicks | 1 | ref_user_id, share_id, page, clicked_at, protocol, engine | share_engine |
| 19 | master_switches | 1 | _type, switches, last_updated, updated_by | master_switch |
| 20 | optimization_config | 1 | type, enabled, updated_at | optimization_engine |
| 21 | site_config | 1 | type, enabled, message, estimated_end, allowed_ips, allowed_roles | site_access |
| 22 | supplier_counters | 1 | seq | suppliers_engine |
| 23 | territory_waypoints | 1 | user_id, latitude, longitude, name, description, waypoint_type, icon, active, color, notes | territory routes |
| 24 | trusted_devices | 1 | device_id, created_at, ip_address, last_used, user_agent, user_id | auth_engine |
| 25 | analytics | 0 | — | analytics_engine |
| 26 | geo_entities | 0 | — | geospatial_engine |
| 27 | hunting_groups | 0 | — | hunting_groups |
| 28 | orders | 0 | — | orders_engine |
| 29 | overpass_cache_r5 | 0 | — | bionic_engine_p0 (OSM) |
| 30 | sightings | 0 | — | observations_router |
| 31 | territory_cameras | 0 | — | camera_engine |
| 32 | territory_events | 0 | — | territory routes |
| 33 | territory_photos | 0 | — | territory routes |
| 34 | territory_users | 0 | — | territory routes |

## 7.2 Collections critiques

| Collection | Volume | Criticite | Index recommandes |
|-----------|--------|-----------|-------------------|
| admin_hotspots | 300 | HAUTE | region_id, score, classification |
| user_sessions | 266 | HAUTE | user_id, token, expires_at |
| hunting_trips | 50 | MOYENNE | user_id, date, species |
| marketing_contacts | 13 | MOYENNE | email, status, score |
| products | 5 | HAUTE | id, category, in_stock |
| users | 1 | CRITIQUE | user_id, email |

## 7.3 Relations inter-collections

```
users (user_id)
    +---> user_sessions (user_id) — 1:N
    +---> hunting_trips (user_id) — 1:N
    +---> user_waypoints (user_id) — 1:N
    +---> territory_waypoints (user_id) — 1:N
    +---> trusted_devices (user_id) — 1:N
    +---> easylead_links (user_id) — 1:N
    +---> cart (session_id) — 1:N

products (id)
    +---> cart (product_id) — 1:N
    +---> orders (product references) — 1:N
    +---> supplier_submissions (product) — 1:N
```

---

# PARTIE IV — INFRASTRUCTURE

---

# 8. ROUTES BACKEND /routes/

**(Section AUBO_V2 — Ajout §1.3)**

6 fichiers de routes + sous-module territory avec 7 fichiers.

## 8.1 Routes principales

| # | Fichier | Prefix API | Endpoints | Methodes |
|---|---------|-----------|-----------|----------|
| R1 | bionic_engine_router.py | /bionic | 29 | GET(24), POST(5) |
| R2 | user_data.py | /user-data | 9 | GET(2), POST(3), PUT(2), DELETE(2) |
| R3 | bathymetry.py | /api/v1/bathymetry | 7 | GET(4), POST(2), DELETE(1) |
| R4 | advanced_zones.py | /api/v1/advanced-zones | 7 | GET(3), POST(1), PUT(1), DELETE(1), GET-stats(1) |
| R5 | ecological_router_v8.py | /api/v8/ecological | 5 | GET(4), POST(1) |
| R6 | reports.py | /reports | 4 | GET(2), POST(1), GET-download(1) |

**Total routes principales** : 61

## 8.2 Routes territoire (/routes/territory/)

| # | Fichier | Role | Fonctions |
|---|---------|------|-----------|
| T1 | inventory.py | Inventaire territorial | CRUD complet, importation, filtrage |
| T2 | commerce.py | Commerce territorial | Transactions, ventes, encheres |
| T3 | events_photos.py | Evenements et photos | Upload, galerie, evenements |
| T4 | gps_routes.py | Routes GPS | Traces, export GPX, navigation |
| T5 | quebec_hunting.py | Chasse Quebec | Reglements, zones, periodes |
| T6 | users_cameras.py | Cameras utilisateurs | Installation, detection, alertes |
| T7 | analysis_layers.py | Couches d'analyse | Couches personnalisees |

**Total routes territoire** : 74 endpoints

---

# 9. BCE ENGINE — DETAIL

**(Section AUBO_V2 — Ajout §1.4)**

## 9.1 Structure BCE

```
bce/
    +-- __init__.py          (BCE v8.0.0)
    +-- engine.py            (Orchestrateur principal BCE)
    +-- router.py            (17 endpoints API)
    +-- bce_ruleset_v8.py    (Regles de validation V8 completes)
    +-- bce_corridor_v9.py   (Validation corridors V9)
    +-- bce_max_4_1.py       (Certification MAX 4.1 — anti-regression MILITARY-GRADE)
    +-- golden/
    |   +-- golden_state.json (Standards GOLDEN UI — registre scelle)
    +-- validators/          (15 validateurs specialises)
```

## 9.2 Validateurs BCE (/validators/)

| # | Validateur | Fichier | Regle |
|---|-----------|---------|-------|
| V1 | bionic_engine_framework | bionic_engine_framework.py | Conformite framework moteur BIONIC |
| V2 | color_contract | color_contract.py | Contrat de couleurs UI BIONIC |
| V3 | corridor_v9 | corridor_v9.py | Validation corridors V9 |
| V4 | debug_layer_guard | debug_layer_guard.py | Protection couches debug (anti-fuite) |
| V5 | ecological_validators_v8 | ecological_validators_v8.py | Validations ecologiques V8 |
| V6 | engine_isolation | engine_isolation.py | Isolation des moteurs (anti-couplage) |
| V7 | geometry_compliance | geometry_compliance.py | Conformite geometrique |
| V8 | golden_state | golden_state.py | Validation etat GOLDEN UI |
| V9 | pipeline_order | pipeline_order.py | Ordre d'execution pipeline |
| V10 | scoring_determinism | scoring_determinism.py | Determinisme du scoring |
| V11 | season_coherence | season_coherence.py | Coherence saisonniere |
| V12 | spatial_integrity | spatial_integrity.py | Integrite spatiale |
| V13 | species_coherence | species_coherence.py | Coherence entre especes |
| V14 | ui_coherence | ui_coherence.py | Coherence interface utilisateur |
| V15 | water_exclusion | water_exclusion.py | Exclusion zones d'eau |

## 9.3 Regles critiques

| Composant | Role |
|-----------|------|
| bce_ruleset_v8.py | Ensemble complet des regles BCE pour validation ecologique — auto-run a chaque pipeline |
| bce_corridor_v9.py | Regle BCE-4X-GEOM-001 : CorridorShapeViolation — interdit polygones massifs/circulaires |
| bce_max_4_1.py | Systeme MILITARY-GRADE anti-regression — protection absolue contre toute deviation |
| golden_state.json | Registre scelle des standards GOLDEN UI — constantes verrouillees |

## 9.4 Endpoints BCE

| Methode | Endpoint | Role |
|---------|----------|------|
| GET | /api/bce/status | Statut global BCE |
| POST | /api/bce/validate | Validation manuelle |
| GET | /api/bce/rules | Liste des regles actives |
| GET | /api/bce/validators | Liste des validateurs |
| POST | /api/bce/run | Execution pipeline BCE |
| + 12 autres | ... | Audit, historique, configuration |

**Total endpoints BCE** : 17

---

# 10. INTEGRATIONS EXTERNES

**(Section AUBO_V2 — Ajout §1.6)**

## 10.1 Integrations actives

| # | Service | Type | Module consommateur | Configuration |
|---|---------|------|---------------------|---------------|
| I1 | **Stripe** | Paiement | payment_engine | STRIPE_API_KEY (sk_test_*), webhooks checkout.session.completed |
| I2 | **OpenStreetMap / Overpass** | Geodonnees | bionic_engine_p0 (osm_extractor, osm_cache) | API publique, cache MongoDB (overpass_cache_r5) |
| I3 | **Open-Meteo** | Meteo | weather_v3 (open_meteo_service) | API publique, sans cle, rate limit souple |
| I4 | **Copernicus Sentinel Hub** | Satellite (NDVI) | bionic_engine_p0 (sentinel_oauth, sentinel_stac) | OAuth2, STAC API, imagerie satellite |
| I5 | **WMS MRNF Quebec** | Cartes ecoforestieres | wms_engine | Proxy WMS, cartes foret/peuplements du MRNF |
| I6 | **html2canvas** | Screenshot | ShareBionicButton.jsx (frontend) | Librairie JS, capture DOM, watermark BIONIC OS |
| I7 | **Google OAuth** | Authentification | auth_engine | OAuth2 callback /auth/google/callback |

## 10.2 Detail integration Stripe

```
Configuration:
    - Cle API: STRIPE_API_KEY (backend/.env)
    - Mode: test (sk_test_emergent)
    - Endpoints:
        POST /api/v1/payments/create-checkout → Stripe Checkout Session
        POST /api/v1/payments/webhook → Stripe Webhooks
    - Evenements ecoutes:
        checkout.session.completed → creation commande
        payment_intent.succeeded → confirmation paiement
    - Fallback: mode demo si Stripe indisponible
```

## 10.3 Detail integration OSM/Overpass

```
Services:
    - osm_extractor.py → Extraction elements OSM (routes, batiments, eau)
    - osm_extractor_v2.py → Version optimisee avec batch
    - osm_batch_extractor.py → Extraction par lots pour zones larges
    - osm_cache_service.py → Cache MongoDB (overpass_cache_r5)
Endpoints Overpass:
    - https://overpass-api.de/api/interpreter
Rate limit: auto-throttle integre
Cache: MongoDB collection overpass_cache_r5 (TTL configurable)
```

## 10.4 Detail integration Sentinel/NDVI

```
Services:
    - sentinel_oauth_service.py → Authentification OAuth2 Copernicus
    - sentinel_stac_service.py → Recherche imagerie satellite STAC
    - ndvi_service.py → Calcul indices vegetation
    - ndvi_cache_service.py → Cache NDVI local
Donnees: Sentinel-2 L2A, bandes B04 (red) + B08 (NIR)
Calcul: NDVI = (NIR - RED) / (NIR + RED)
```

---

# 11. DEPLOIEMENT & INFRASTRUCTURE

**(Section AUBO_V2 — Ajout §3.2)**

## 11.1 Configuration Supervisor

| Service | Commande | Port | Options |
|---------|----------|------|---------|
| backend | uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --reload | 8001 | Auto-restart, hot reload |
| frontend | yarn start | 3000 | Auto-restart, HOST=0.0.0.0 |
| mongodb | mongod --bind_ip_all | 27017 | Auto-restart |

## 11.2 Variables d'environnement

**Backend (/app/backend/.env)** :

| Variable | Valeur type | Usage |
|----------|-------------|-------|
| MONGO_URL | mongodb://localhost:27017 | Connexion MongoDB |
| DB_NAME | huntiq_v6 | Base de donnees |
| JWT_SECRET_KEY | huntiq_v6_bce4x_steeve_max_secret_2026 | Signature tokens JWT |
| CORS_ORIGINS | * | Origines CORS autorisees |
| STRIPE_API_KEY | sk_test_emergent | Cle Stripe test |

**Frontend (/app/frontend/.env)** :

| Variable | Usage |
|----------|-------|
| REACT_APP_BACKEND_URL | URL backend (Kubernetes ingress) |
| WDS_SOCKET_PORT | Port WebSocket dev server (443) |
| ENABLE_HEALTH_CHECK | Health check frontend (false) |

## 11.3 Architecture reseau

```
[Internet] --> [Kubernetes Ingress]
                    |
                    +---> /api/* → Backend (port 8001)
                    +---> /* → Frontend (port 3000)
                    |
                    [Backend] --> [MongoDB (port 27017)]
```

## 11.4 Processus de deploiement

```
1. Code modifie dans /app/
2. Hot reload detecte le changement (uvicorn --reload / react-scripts)
3. Service redemarrage automatique via Supervisor
4. Test via REACT_APP_BACKEND_URL
5. Validation par STEEVE-MAX
6. Commit sur branche Work1 (merge main STRICTEMENT INTERDIT)
```

---

# PARTIE V — GOUVERNANCE & SECURITE

---

# 12. INTERCONNEXIONS P3-P6

Planification des interconnexions inter-modules (documentees dans INTERCONNEXIONS_P3_P6.md).

## 12.1 P3 — Marketing x Partage x Analytics

```
share_engine <---> marketing_engine <---> analytics_engine
     |                  |                     |
     +---> EASYlead     +---> Campagnes       +---> Tracking API
     +---> Screenshot   +---> Segmentation    +---> Heatmaps
     +---> 14 canaux    +---> Lead scoring    +---> Volume/endpoint
```

**Statut** : PARTIELLEMENT IMPLEMENTE (share_engine + EASYlead actifs)

## 12.2 P4 — Intelligence x Strategie x IA

```
bionic_engine_p0 <---> strategy_master_engine <---> ai_engine
      |                      |                        |
      +---> 10 sous-moteurs  +---> Plans globaux      +---> Recommandations
      +---> Score /100       +---> Optimisation        +---> Analyse intelligente
      +---> 32 criteres     +---> Multi-especes       +---> Knowledge base
```

**Statut** : ARCHITECTURE DEFINIE, implementation a venir

## 12.3 P5 — Monetisation x Paiement x Upsell

```
payment_engine <---> freemium_engine <---> upsell_engine
      |                    |                    |
      +---> Stripe         +---> Plans          +---> Triggers
      +---> Webhooks       +---> Quotas         +---> Conversion
      +---> Remboursements +---> Feature flags  +---> A/B testing
```

**Statut** : FONCTIONNEL (Stripe integre, plans actifs)

## 12.4 P6 — Territoire x Navigation x Camera

```
territory_engine <---> waypoint_engine <---> camera_engine
      |                     |                    |
      +---> Polygones       +---> Points GPS     +---> Trail cameras
      +---> Metadata        +---> Partage        +---> Detection
      +---> CRUD            +---> Scoring        +---> Analyse photo
                                   |
                              hunting_trip_logger
                                   |
                              live_heading_engine
```

**Statut** : FONCTIONNEL (waypoints + trips actifs)

---

# 13. GOUVERNANCE

## 13.1 Admin Premium

Centre de gouvernance centralise : `AdminPremiumPage.jsx` / `admin_engine`.
**210 endpoints** — le plus grand module de BIONIC OS.

| Sous-module | Fonction |
|-------------|----------|
| Paiements | Suivi transactions Stripe, webhooks, remboursements |
| Freemium | Gestion plans, quotas, feature flags |
| Upsell | Campagnes, triggers, conversion |
| Onboarding | Flux d'integration, progression |
| Tutoriels | Contenus pedagogiques, certificats |
| Regles | Regles metier configurables |
| Strategies | Strategies de chasse globales |
| Utilisateurs | Gestion utilisateurs, roles, permissions |
| Logs | Journaux systeme, audit trail |
| Parametres | Configuration globale plateforme |

## 13.2 Master Switch

```
master_switch (/api/v1/master-switch, /api/v1/global-switch)
    +-- Global ON/OFF — Autorite STEEVE-MAX uniquement
    +-- Controle par canal (14 canaux partage)
    +-- Admin sync : 9 modules
    |     messaging_engine, x300_strategy, seo_engine,
    |     affiliate_ads, reseautage, email_marketing,
    |     analytics_engine, partnership_engine, freemium_upsell
    +-- Override mode pour maintenance
```

## 13.3 ULTRA-MAX++

```
ultra_max_firewall (/api/firewall)
    +-- Registre SCELLE — 12 constantes verrouillees
    +-- Authority : STEEVE-MAX
    +-- 7 verrous runtime actifs
    +-- Boot guard OK
    +-- Geo-fencing urbain (Shapely)
    +-- Aucune modification sans cle d'autorite
```

## 13.4 BCE-4X

```
bce/ (BIONIC Compliance Engine)
    +-- engine.py — Moteur principal BCE
    +-- bce_ruleset_v8.py — Regles de validation V8
    +-- bce_corridor_v9.py — Validation corridors V9
    +-- bce_max_4_1.py — Certification MAX 4.1
    +-- golden/ — Standards GOLDEN UI
    +-- validators/ — 15 validateurs specialises
```

**Principes** :
- ZERO LOSS — Aucune fonctionnalite supprimee sans validation STEEVE-MAX
- ZERO REGRESSION — Chaque modification testee et validee
- ZERO INTERPRETATION — Execution stricte des directives

---

# 14. SECURITE ET PERMISSIONS

## 14.1 Roles

| Role | Niveau | Acces |
|------|--------|-------|
| anonymous | 0 | Pages publiques (accueil, shop) |
| user | 1 | Analyse territoire (quotas Free), dashboard, waypoints |
| premium | 2 | Analyse illimitee, SUPRA, intelligence, rapports |
| business | 3 | Dashboard business, partenaires, analytics avances |
| admin | 4 | Admin Premium complet, Master Switch, BCE-4X |
| STEEVE-MAX | 5 | Autorite supreme — toutes operations + gouvernance |

## 14.2 Controle d'acces

| Module | Prefix | Fonction |
|--------|--------|----------|
| roles_engine | /api/v1/roles | Verification roles et permissions |
| access_engine_v6 | /api/v6/access | Controle d'acces par zone geographique |
| access_clarity_engine_v7 | /api/v7/clarity | Clarification niveaux d'acces |
| auth_engine | /api/auth | JWT, login, register, reset, Google OAuth |

## 14.3 Chaine de commandement

```
STEEVE-MAX (Autorite supreme, niveau 5)
    +-- BCE-4X (Protocole de gouvernance)
         +-- GOLDEN UI (Standards visuels)
         +-- ULTRA-MAX++ (Firewall + verrous + registre scelle)
         +-- Master Switch (Controle global ON/OFF)
         +-- Admin Premium (Gouvernance operationnelle, 210 endpoints)
```

---

# PARTIE VI — QUALITE & HISTORIQUE

---

# 15. MONITORING & OBSERVABILITE

**(Section AUBO_V2 — Ajout §3.1)**

## 15.1 Health checks

| Service | Endpoint | Methode |
|---------|----------|---------|
| Backend | /api/health | GET — statut serveur |
| Frontend | / | GET — page chargee |
| MongoDB | Connexion directe | pymongo ping |

## 15.2 Logs systeme

| Service | Fichier log | Contenu |
|---------|------------|---------|
| Backend stdout | /var/log/supervisor/backend.out.log | Requetes API, reponses |
| Backend stderr | /var/log/supervisor/backend.err.log | Erreurs, exceptions |
| Frontend stdout | /var/log/supervisor/frontend.out.log | Compilation, webpack |
| Frontend stderr | /var/log/supervisor/frontend.err.log | Erreurs build |
| MongoDB | /var/log/mongodb.err.log | Operations DB |

## 15.3 Metriques systeme

| Metrique | Source | Seuil critique |
|----------|--------|----------------|
| CPU | Supervisor | > 90% continu |
| RAM | Supervisor | > 85% |
| Disque | df -h | > 90% utilise |
| Connexions DB | MongoDB | > 100 simultanees |
| Temps reponse API | analytics_engine | > 5000ms (P95) |

## 15.4 Alerting

| Module | Type d'alerte | Destination |
|--------|--------------|-------------|
| alerts_engine | Alertes configurables | In-app, push |
| notification_unified_engine | Notifications systeme | Push, email, in-app |
| ultra_max_firewall | Violations securite | Logs + admin |

---

# 16. TESTS & QUALITE

**(Section AUBO_V2 — Ajout §3.3)**

## 16.1 Tests existants

| Emplacement | Fichiers | Couverture |
|-------------|---------|------------|
| modules/bionic_engine_p0/tests/ | 10 fichiers | BMPE, comparison, heatmap, legal hours, P0 modules, pipeline, scoring, TFE, unified scoring, waypoint analysis |
| /app/tests/ | __init__.py | Structure de tests globale (vide) |
| /app/backend/tests/ | Structure | Tests backend (a peupler) |

## 16.2 Tests bionic_engine_p0

| # | Fichier | Module teste |
|---|---------|-------------|
| T1 | test_bmpe.py | BIONIC Multi-Parameter Engine |
| T2 | test_comparison.py | Comparaison de zones |
| T3 | test_heatmap_fusion_service.py | Fusion heatmaps |
| T4 | test_legal_hours_service.py | Heures legales |
| T5 | test_p0_modules.py | Modules P0 globaux |
| T6 | test_pipeline.py | Pipeline d'analyse |
| T7 | test_scoring_services.py | Services de scoring |
| T8 | test_tfe.py | Terrain Feature Engine |
| T9 | test_unified_scoring_service.py | Scoring unifie |
| T10 | test_waypoint_analysis_service.py | Analyse waypoints |

## 16.3 Plan de non-regression BCE-4X

| Etape | Description | Outil |
|-------|-------------|-------|
| 1 | Validation BCE auto-run | bce_ruleset_v8.py |
| 2 | Anti-regression MAX 4.1 | bce_max_4_1.py |
| 3 | Validation corridors V9 | bce_corridor_v9.py |
| 4 | 15 validateurs specialises | validators/ |
| 5 | Golden State verification | golden_state.json |
| 6 | Tests unitaires P0 | tests/ (10 fichiers) |

---

# 17. CHANGELOG CONSOLIDATION V6

**(Section AUBO_V2 — Ajout §3.4)**

## 17.1 Historique des consolidations

| Date | Operation | Detail | Commit |
|------|-----------|--------|--------|
| 2026-04 | Merge geo_engine → geospatial_engine | Logique interne absorbee, prefix API /api/admin/geo preserve, geo_engine marque DEPRECATED | cb48595 |
| 2026-04 | Merge affiliate_ads_engine + ad_spaces_engine → ads_engine | Facade consolidee, 2 sous-modules actifs (40 endpoints), aucun endpoint propre ads_engine | cb48595 |
| 2026-04 | Merge tutorial_engine + formations_engine → learning_engine | Facade consolidee, 2 sous-modules actifs (12 endpoints), aucun endpoint propre learning_engine | cb48595 |
| 2026-04 | Deprecate core/alimentation | Successor: nutrition_engine | cb48595 |
| 2026-04 | Reclass chasseur_jumeau.py | Deplace vers experiments/, redirect import conserve | cb48595 |
| 2026-04 | Reclass liste_epicerie.py | Deplace vers utility_modules/, redirect import conserve | cb48595 |
| 2026-04 | Rename utils/ → utility_modules/ | Conflit import Python resolu | cb48595 |
| 2026-04 | Vault osm_cache + uploads | Deplaces vers ../BIONIC_FULL_ARCHIVE, .gitignore mis a jour | 3ad0793 |

## 17.2 Mapping ancien → nouveau

| Ancien module | Nouveau module | Type | Prefix API |
|---------------|---------------|------|------------|
| geo_engine | geospatial_engine | ABSORPTION | /api/admin/geo (preserve) |
| affiliate_ads_engine | ads_engine (facade) | FACADE | /api/v1/affiliate-ads (inchange) |
| ad_spaces_engine | ads_engine (facade) | FACADE | /api/v1/ad-spaces (inchange) |
| tutorial_engine | learning_engine (facade) | FACADE | /api/v1/tutorials (inchange) |
| formations_engine | learning_engine (facade) | FACADE | /api/formations (inchange) |
| core/alimentation | nutrition_engine | DEPRECATION | interne (inchange) |
| chasseur_jumeau.py | experiments/chasseur_jumeau.py | RECLASSEMENT | interne |
| liste_epicerie.py | utility_modules/liste_epicerie.py | RECLASSEMENT | interne |
| utils/ | utility_modules/ | RENOMMAGE | — |

## 17.3 Impact sur le comptage

| Metrique | Avant V6 | Apres V6 | Delta |
|----------|----------|----------|-------|
| Modules directories | 87 | 80 | -7 |
| Modules logiques | 99 | 92 | -7 |
| Facades ajoutees | 0 | 2 | +2 |
| Modules deprecies | 0 | 2 | +2 |
| Endpoints | Inchange | Inchange | 0 |

**Principe cle** : Les endpoints sont PRESERVES integralement (ZERO LOSS). Seule l'organisation modulaire change.

---

# ANNEXE A — CARTOGRAPHIE COMPLETE (V2)

**(Correction V2 — §2.1 : comptage exact par decorateurs)**

## A.1 Inventaire quantitatif (V2 — exact)

| Metrique | V1 (approx.) | V2 (exact) | Methode V2 |
|----------|-------------|-----------|------------|
| Module directories | 79 | 80 | find -type d |
| Modules standalone | 12 | 12 | find -name "*.py" |
| Total modules logiques | 91 | 92 | Somme |
| Modules consolides (facades) | 2 | 2 | Verifie |
| Modules deprecies | 2 | 2 | Verifie |
| Modules reclasses | 2 | 2 | Verifie |
| Moteurs specialises (engines/) | 5 | 5 | Verifie |
| Sous-systemes core (core/) | 9 (8+1) | 9 (8+1) | Verifie |
| Routes backend (/routes/) | 6 | 13 (6 + 7 territory) | find + count |
| **Total endpoints API** | **1675+** | **1701** | **Regex @router scan complet** |
| Fichiers backend racine | N/A | 16 | Verifie |
| Pages frontend | 31 | 38 | App.js routes |
| Routes frontend (avec redirections) | N/A | 50 | App.js scan |
| Composants frontend (hors UI) | N/A | 143 | find -name "*.jsx" |
| Composants territoire | N/A | 65 | find territoire/ |
| Composants UI (Shadcn) | N/A | 47 | find ui/ |
| Modules frontend | N/A | 31 (139 fichiers) | find modules/ |
| Hooks personnalises | N/A | 18 + 8 modules | find use*.js |
| Stores Zustand | N/A | 2 | Verifie |
| Contexts React | N/A | 1 | Verifie |
| Collections MongoDB | N/A | 34 | db.list_collection_names() |
| Documents MongoDB | N/A | ~703 | count_documents() |
| Validateurs BCE | N/A | 15 | find validators/ |
| Dependances frontend | 58 | 58 | package.json |

## A.2 Modules critiques (>20 endpoints) — V2

| Module | Endpoints V2 | Domaine | Categorie |
|--------|-------------|---------|-----------|
| admin_engine | 210 | Admin | ACTIF |
| bionic_engine_p0 | 154 | Analyse | ACTIF |
| seo_engine | 59 | Marketing | ACTIF |
| data_layers | 59 | Geospatial | ACTIF |
| nutrition_intelligence (engine) | 35 | SUPRA | ACTIF |
| bionic_knowledge_engine | 35 | SUPRA | ACTIF |
| networking.py (racine) | 33 | Social | FICHIER RACINE |
| geospatial_engine | 33 | Geospatial | ACTIF |
| partnership.py (racine) | 29 | Social | FICHIER RACINE |
| bionic_engine_router.py (routes) | 29 | Analyse | ROUTE |
| saline_engine | 26 | Analyse | ACTIF |
| geo_engine | 26 | Geospatial | DEPRECATED |
| affiliate_ads_engine | 24 | E-Commerce | ACTIF |
| tracking_engine | 22 | Marketing | ACTIF |
| marketing_engine | 22 | Marketing | ACTIF |
| core/scoring_pipeline | 20 | Core | ACTIF |
| lands_rental.py (racine) | 20 | E-Commerce | FICHIER RACINE |

## A.3 Repartition endpoints par source (V2)

| Source | Endpoints | % |
|--------|-----------|---|
| modules/ (80 directories) | 1082 | 63.6% |
| Fichiers racine backend (16) | 203 | 11.9% |
| routes/ (6 + 7 territory) | 135 | 7.9% |
| engines/ (5) | 49 | 2.9% |
| core/ (9) | 20 | 1.2% |
| bce/ | 17 | 1.0% |
| server.py | 6 | 0.4% |
| bionic_engine_p0 sub-routers | 135 | 7.9% |
| websocket/ | 3 | 0.2% |
| Autres | 51 | 3.0% |
| **TOTAL** | **1701** | **100%** |

## A.4 Dependances fortes (modules les plus importes)

| Module | Nombre de dependants | Role |
|--------|---------------------|------|
| bionic_engine_p0 | 8+ | Hub central d'analyse |
| roles_engine | 6+ | Permissions (importe par products, orders, customers, suppliers, etc.) |
| scoring_engine | 5+ | Scoring partage |
| core/scoring_pipeline | 4+ | Normalisation scores |
| nutrition_engine | 4+ | Donnees nutritionnelles |
| core/weather | 3+ | Donnees meteo |
| core/geo | 3+ | Utilitaires GIS |

## A.5 Points d'entree API par version

| Version | Prefix | Modules |
|---------|--------|---------|
| v1 | /api/v1/* | 45+ modules |
| v3 | /api/v3/* | api_gateway, weather_v3 |
| v6 | /api/v6/* | access_engine, nutrition_intelligence, supra_advanced |
| v7 | /api/v7/* | access_clarity_engine |
| v8 | /api/v8/* | ecological_router_v8 |
| auth | /api/auth/* | auth_engine |
| share | /api/share/* | share_engine + EASYlead |
| firewall | /api/firewall/* | ultra_max_firewall |
| partners | /api/partners/* | partner_engine |
| formations | /api/formations/* | formations_engine |
| bsaa | /api/bsaa/* | bsaa |
| backup | /api/backup-cloud/* | backup_cloud_engine |
| admin | /api/admin/* | optimization_engine, geo_engine (deprecated) |
| bce | /api/bce/* | BCE Engine |
| bionic | /bionic/* | bionic_engine_router (routes/) |

---

# ANNEXE B — DELTA V1 → V2

## B.1 Ajouts (6 sections)

| # | Section | Lignes | Source plan |
|---|---------|--------|------------|
| 1 | Sous-routeurs bionic_engine_p0 (§5) | ~180 | AUBO_V2_PLAN §1.5 |
| 2 | Cartographie frontend (§6) | ~200 | AUBO_V2_PLAN §1.1 |
| 3 | Base de donnees MongoDB (§7) | ~120 | AUBO_V2_PLAN §1.2 |
| 4 | Routes backend /routes/ (§8) | ~50 | AUBO_V2_PLAN §1.3 |
| 5 | BCE Engine detail (§9) | ~80 | AUBO_V2_PLAN §1.4 |
| 6 | Integrations externes (§10) | ~80 | AUBO_V2_PLAN §1.6 |

## B.2 Corrections (2)

| # | Correction | V1 | V2 |
|---|-----------|-----|-----|
| 1 | Comptage endpoints | ~1675+ (approximation) | 1701 (exact par regex scan) |
| 2 | Classification modules | Non clarifie | 4 categories : ACTIF, FACADE, DEPRECATED, STANDALONE |

## B.3 Sections manquantes ajoutees (4)

| # | Section | Source plan |
|---|---------|------------|
| 1 | Deploiement & Infrastructure (§11) | AUBO_V2_PLAN §3.2 |
| 2 | Monitoring & Observabilite (§15) | AUBO_V2_PLAN §3.1 |
| 3 | Tests & Qualite (§16) | AUBO_V2_PLAN §3.3 |
| 4 | Changelog Consolidation V6 (§17) | AUBO_V2_PLAN §3.4 |

## B.4 Clarifications (4) — Decisions STEEVE-MAX

| # | Question | Decision | Directive |
|---|---------|----------|-----------|
| 1 | Modules facade | Documentes comme redirections avec mention consolidation | x5302-A §1 |
| 2 | Modules deprecies | Gardes dans cartographie, marques DEPRECATED | x5302-A §2 |
| 3 | Profondeur de detail | Niveau module (pas endpoint individuel) | x5302-A §3 |
| 4 | Perimetre frontend | Pages + composants principaux (pas CSS) | x5302-A §4 |

## B.5 Contenu preserve de V1 (ZERO LOSS)

| Section V1 | Section V2 | Statut |
|-----------|-----------|--------|
| §1 Domaines | §1 Domaines | PRESERVE + enrichi (colonne Categorie) |
| §2 Pipelines | §2 Pipelines | PRESERVE integralement |
| §3 Moteurs specialises | §3 Moteurs specialises | PRESERVE integralement |
| §4 Core systems | §4 Core systems | PRESERVE + colonne Endpoints |
| §5 Interconnexions P3-P6 | §12 Interconnexions P3-P6 | PRESERVE integralement |
| §6 Gouvernance | §13 Gouvernance | PRESERVE integralement |
| §7 Securite et permissions | §14 Securite et permissions | PRESERVE integralement |
| Annexe A Cartographie | Annexe A (V2) | PRESERVE + enrichi (metriques V2) |

---

## OBJECTIFS PREPARATOIRES (Section C)

Ce document AUBO_V2 constitue la base canonique pour :

| Objectif | Document cible | Statut |
|----------|---------------|--------|
| SUPRA_PIPELINE_V1 | Pipeline scoring complet | PRET (Section 2.1) |
| E_COMMERCE_PIPELINE_V1 | Pipeline e-commerce complet | PRET (Section 2.2) |
| INTERCONNEXIONS_P3_P6_V2 | Interconnexions inter-modules V2 | PRET (Section 12) |
| EASYlead Analytics x5100 | Integration Admin Premium | PRET (Section 13.1) |
| Certification BIONIC OS V2 | Certification complete | PRET (toutes sections) |
| BSAA-2 Implementation | Social Ads Automation | PRET (architecture, §1.5 Marketing) |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : AUBO_V2 2.0.0
**Base** : AUBO_V1 1.0.0 (673 lignes, 30 KB)
**Modules documentes** : 92 (80 dirs + 12 standalone) + 5 engines + 9 core + 16 fichiers racine
**Endpoints documentes** : 1701 (exact)
**Pages frontend** : 38 (50 routes)
**Collections MongoDB** : 34
**Validateurs BCE** : 15
**Merge main** : STRICTEMENT INTERDIT
**Contraintes x5302-A** : ZERO LOSS, ZERO REGRESSION, ZERO INTERPRETATION
