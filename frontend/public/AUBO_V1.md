# AUBO V1 — ARCHITECTURE UNIFIEE BIONIC OS
## Directive x5300-STEEVE_MAX — Version 1.0.0
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-03 | Merge MAIN : STRICTEMENT INTERDIT

---

# TABLE DES MATIERES

1. [DOMAINES](#1-domaines)
   1.1 Analyse & Scoring
   1.2 SUPRA
   1.3 Geospatial
   1.4 E-Commerce
   1.5 Marketing
   1.6 Social & Reseautage
   1.7 Admin & Configuration
   1.8 Securite & Acces
2. [PIPELINES](#2-pipelines)
   2.1 Pipeline SUPRA
   2.2 Pipeline E-Commerce
   2.3 Pipeline Territoire
   2.4 Pipeline Marketing
   2.5 Pipeline Abonnements
3. [MOTEURS](#3-moteurs-specialises)
4. [CORE SYSTEMS](#4-core-systems)
5. [INTERCONNEXIONS P3-P6](#5-interconnexions-p3-p6)
6. [GOUVERNANCE](#6-gouvernance)
7. [SECURITE & PERMISSIONS](#7-securite-et-permissions)
A. [CARTOGRAPHIE COMPLETE](#annexe-a-cartographie-complete)

---

# 1. DOMAINES

## 1.1 Domaine ANALYSE & SCORING

Moteur principal d'analyse de territoires de chasse. Coeur fonctionnel de BIONIC OS.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| bionic_engine_p0 | /v1/bionic | 154 | Moteur d'analyse principal — 18+ sous-routeurs (SSE, OSG, CME, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE, pipeline, hotspots, organic zones, spatial clipping, seasonal conditions, hunting path) |
| scoring_engine | /api/v1/scoring | 8 | Scoring multi-criteres sur 100 points |
| waypoint_scoring_engine | /api/v1/waypoint-scoring | 8 | Scoring des waypoints — evaluation qualite des points GPS |
| score_consolide (standalone) | interne | — | Score consolide x4100 — fusion 22 moteurs (Option C) |
| score_preparation (standalone) | interne | — | Pre-traitement et normalisation des scores |
| bionic_data_fabric | /api/v1/data-fabric | 8 | Fabric de donnees unifie — agregation multi-source |
| nutrition_engine | /api/v1/nutrition | 7 | Moteur nutritionnel V1 — attractants, mineraux, proteines |
| saline_engine | /api/v1/saline | 26 | Moteur saline — analyse salines, scoring |
| salines_ultime_engine | /api/v1/salines-ultime | 4 | Scores salines ultime — 5 scores + 20 sources scientifiques |
| bionic_stand_recommendation_engine | /api/v1/stand-recommendation | 6 | Recommandation de postes d'affut — positionnement optimal |
| predictive_engine | /api/v1/predictive | 8 | Previsions predictives — probabilites de succes, timing |
| solunar (standalone) | interne | — | Calculs solunaires — phases lunaires, periodes d'activite |
| legal_time_engine | /api/v1/legal-time | 7 | Heures legales de chasse — lever/coucher soleil, periodes |

**Dependances critiques** : core/scoring_pipeline, core/weather, core/pressure, core/ecology
**Modules critiques** : bionic_engine_p0 (154 endpoints — hub central d'analyse)

---

## 1.2 Domaine SUPRA

Intelligence avancee multi-criteres. Couche superieure de l'analyse.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| supra_advanced (engine) | /api/v6/supra/advanced | 4 | Analyse SUPRA avancee multi-criteres |
| nutrition_intelligence (engine) | /api/v6/nutrition-intelligence | 35 | Intelligence nutritionnelle SUPRA |
| bionic_knowledge_engine | /api/v1/bionic/knowledge | 35 | Base de connaissances BIONIC — donnees scientifiques |
| ai_engine | /api/v1/ai | 15 | Moteur IA principal — recommandations, analyse intelligente |
| recommendation_engine | /api/v1/recommendation | 8 | Recommandations personnalisees — produits, zones, strategies |
| strategy_master_engine | /api/v1/strategy-master | 8 | Strategies de chasse globales — plans, optimisation |

**Dependances critiques** : bionic_engine_p0, scoring_engine, nutrition_engine
**Modules critiques** : nutrition_intelligence (35 endpoints — hub nutritionnel SUPRA)

---

## 1.3 Domaine GEOSPATIAL

Donnees geographiques, ecologiques, et environnementales.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| geospatial_engine | /api/v1/geospatial | 33 | Analyse geospatiale + logique Geo Engine absorbee (Consolidation V6) |
| geo_engine | /api/admin/geo | 26 | DEPRECATED — fusionne dans geospatial_engine |
| ecoforestry_engine | /api/v1/ecoforestry | 8 | Donnees ecoforestieres — peuplements, drainage, depots |
| bionic_ecological_engine | /api/v1/ecological-intelligence | 16 | Intelligence ecologique — habitat, biodiversite |
| soil_engine | /api/v1/soil | 8 | Donnees pedologiques — types de sol, drainage, fertilite |
| wms_engine | /api/v1/wms | 2 | Proxy WMS Quebec (MRNF) — cartes ecoforestieres |
| data_layers | /api/v1/data/* | 59 | 5 couches de donnees (ecoforestry, behavioral, simulation, 3d, geospatial-advanced) |
| wildlife_behavior_engine | /api/v1/wildlife | 8 | Comportement animal — patterns, mouvements, habitat |
| weather_fauna_simulation_engine | /api/v1/simulation | 8 | Simulation meteo-faune — impact conditions sur comportement |
| weather_v3 (engine) | /api/v3/weather | 4 | Meteo BIONIC V3 temps reel |
| territory_engine | interne | — | Gestion des territoires — CRUD, polygones, metadata |
| engine_3d | /api/v1/3d | 8 | Visualisation 3D du terrain — elevation, relief |

**Dependances critiques** : core/geo, core/ndvi, core/ecology, core/corridors
**Modules critiques** : geospatial_engine (33 endpoints — hub geospatial post-consolidation)

---

## 1.4 Domaine E-COMMERCE

Catalogue produits, commandes, paiements, fournisseurs, affiliation.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| products_engine | /api/v1/products | 13 | CRUD produits — catalogue, scoring, import CSV/Excel |
| cart_engine | /api/v1/cart | 8 | Gestion du panier — session saline, ajout/suppression, totaux |
| orders_engine | /api/v1/orders | 12 | Gestion des commandes — creation, statut, historique |
| payment_engine | /api/v1/payments | 10 | Integration Stripe — checkout, webhooks, remboursements |
| suppliers_engine | /api/v1/suppliers | 12 | Gestion des fournisseurs/marchands — catalogue, commissions |
| customers_engine | /api/v1/customers | 8 | Gestion des clients — profils, historique, segmentation |
| ads_engine (facade) | — | — | CONSOLIDE V6 : facade pour affiliate_ads_engine + ad_spaces_engine |
| affiliate_ads_engine | /api/v1/affiliate-ads | 24 | Annonces affiliees, creatives, tracking conversions |
| ad_spaces_engine | /api/v1/ad-spaces | 16 | Espaces publicitaires sur la plateforme |
| affiliate_switch_engine | /api/v1/affiliate-switch | 15 | Basculement dropshipping/affiliation, mode hybride |
| marketplace_engine | interne | — | Place de marche — listing produits tiers |
| freemium_engine | /api/v1/freemium | 8 | Plans Free/Premium/Pro — quotas, feature flags |
| upsell_engine | /api/v1/upsell | 8 | Campagnes d'upsell — triggers, conversion, A/B testing |
| liste_epicerie (utility_modules) | interne | — | Liste de courses du chasseur — equipement, provisions |

**Dependances critiques** : Stripe (paiements), roles_engine (permissions)
**Modules critiques** : payment_engine (integration Stripe), products_engine (catalogue central)

---

## 1.5 Domaine MARKETING

Partage, SEO, tracking, campagnes, calendrier.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| share_engine | /api/share | 12 | Share Engine V1 — 14 canaux, EASYlead tracking, screenshot + watermark |
| marketing_engine | /api/v1/marketing | 22 | Automation marketing — segmentation, campagnes, tracking |
| marketing_calendar_engine | /api/v1/marketing-calendar | 8 | Calendrier marketing V2 — evenements, rappels, campagnes |
| seo_engine | /api/v1/bionic/seo | 59 | SEO — meta tags, sitemap, SEO fournisseurs x300 |
| tracking_engine | /api/v1/tracking-engine | 22 | Tracking comportemental — sessions, evenements, heatmaps |
| analytics_engine | /api/v1/analytics | 8 | Tracking requetes API, temps de reponse, volume |
| bsaa | /api/bsaa | 8 | BIONIC Social Ads Automation (architecture definie, implementation GELEE) |
| referral_engine | /api/v1/referral | 15 | Programme de parrainage — codes, tracking, recompenses |
| contact_engine | /api/v1/contact-engine | 8 | Gestion des contacts et CRM interne |

**Dependances critiques** : html2canvas (screenshot), MongoDB (tracking)
**Modules critiques** : seo_engine (59 endpoints), marketing_engine (22 endpoints)

---

## 1.6 Domaine SOCIAL & RESEAUTAGE

Communication, messagerie, reseau de chasseurs.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| networking_engine | /api/v1/network | 19 | Reseau social de chasseurs — publications, feed, groupes |
| messaging_engine | /api/v1/messaging | 16 | Messagerie interne — notifications push, templates, file |
| notification_unified_engine | /api/v1/notifications | 17 | Notifications unifiees — push, email, in-app |
| partner_engine | /api/partners | 8 | Programme partenaires — inscription, dashboard, offres |
| camera_engine | /api/v1/camera | 8 | Cameras de trail — photos, detection, analyse |
| hunting_trip_logger | /api/v1/trips | 14 | Journal des sorties de chasse — logs, photos, resultats |
| live_heading_engine | /api/v1/live-heading | 14 | Cap de navigation en temps reel — boussole, direction |
| waypoint_engine | /api/v1/waypoints | 8 | Gestion des waypoints — CRUD, partage, scoring |
| chasseur_jumeau (experiments) | interne | — | Chasseur Jumeau — profil similaire, matching |

**Modules critiques** : networking_engine (19 endpoints — hub social)

---

## 1.7 Domaine ADMIN & CONFIGURATION

Gouvernance, configuration, gestion utilisateurs, backups.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| admin_engine | /api/v1/admin | 210 | Centre de gouvernance Admin Premium — configuration globale |
| user_engine | /api/v1/user | 17 | Gestion des utilisateurs — profils, preferences, historique |
| roles_engine | /api/v1/roles | 14 | Gestion des roles et permissions |
| auth_engine | /api/auth | 8 | Authentification — JWT, login, register, reset password |
| onboarding_engine | /api/v1/onboarding | 8 | Flux d'accueil nouveaux utilisateurs |
| learning_engine (facade) | — | — | CONSOLIDE V6 : facade pour tutorial_engine + formations_engine |
| tutorial_engine | /api/v1/tutorials | 8 | Contenus pedagogiques — tutoriels, progression |
| formations_engine | /api/formations | 4 | Formations FedeCF et BIONIC Academy |
| progression_engine | /api/v1/progression | 13 | Progression utilisateur — niveaux, badges |
| rules_engine | /api/v1/rules | 8 | Regles metier configurables — conditions, actions |
| trigger_engine | /api/v1/trigger-engine | 8 | Declencheurs d'evenements — conditions, actions |
| alerts_engine | /api/v1/alerts | 8 | Systeme d'alertes configurable |
| backup_cloud_engine | /api/backup-cloud | 8 | Backup cloud automatise, restauration |
| optimization_engine | /api/admin/optimization | 4 | Propositions d'optimisation systeme |
| engine_registry | interne | — | Registre central de tous les moteurs |
| api_gateway | /api/v3 | 8 | Passerelle API V3 — routage intelligent |
| plugins_engine | interne | — | Systeme de plugins extensible |

**Modules critiques** : admin_engine (210 endpoints — hub d'administration central)

---

## 1.8 Domaine SECURITE & ACCES

Firewall, controle d'acces, verification.

| Module | Prefix API | Endpoints | Role |
|--------|-----------|-----------|------|
| ultra_max_firewall | /api/firewall | 8 | Pare-feu ULTRA-MAX++ — geo-fencing urbain, 7 verrous runtime |
| master_switch | /api/v1/master-switch | 8 | Controle global ON/OFF — autorite STEEVE-MAX |
| access_engine_v6 | /api/v6/access | 8 | Controle d'acces par zone geographique |
| access_clarity_engine_v7 | /api/v7/clarity | 8 | Clarification des niveaux d'acces, reporting conflits |

**Modules critiques** : ultra_max_firewall (verrous runtime), master_switch (controle global)

---

## MODULES STANDALONE (12)

| Module | Emplacement | Role | Reclassification V6 |
|--------|------------|------|---------------------|
| chasseur_jumeau.py | experiments/ | Chasseur Jumeau — profil similaire | RECLASSE |
| liste_epicerie.py | utility_modules/ | Liste de courses du chasseur | RECLASSE |
| docs.py | modules/ | Documentation API generee | — |
| hunter_score.py | modules/ | Score chasseur individuel | — |
| next_step_engine.py | modules/ | Recommandation de prochaine etape | — |
| permis_checklist.py | modules/ | Checklist permis de chasse | — |
| plan_saison.py | modules/ | Planification saison de chasse | — |
| pourvoirie_finder.py | modules/ | Recherche de pourvoiries | — |
| score_consolide.py | modules/ | Score consolide x4100 | — |
| score_preparation.py | modules/ | Preparation des scores | — |
| setup_builder.py | modules/ | Constructeur de configuration | — |
| user_context.py | modules/ | Contexte utilisateur — session | — |

---

# 2. PIPELINES

## 2.1 Pipeline SUPRA

```
[Utilisateur] ──> [Selection zone sur carte]
       │
       ├──> bionic_engine_p0 (/v1/bionic)
       │       │
       │       ├──> SSE (Species Scoring Engine)
       │       ├──> OSG (Organic Scoring Grid)
       │       ├──> CME (Corridor Movement Engine)
       │       ├──> WSE (Weather Scoring Engine)
       │       ├──> VFE (Vegetation Factor Engine)
       │       ├──> SSVL (Species-Specific Vegetation Layer)
       │       ├──> TCVE (Terrain Characteristic Value Engine)
       │       ├──> PME (Pressure Measurement Engine)
       │       ├──> BMPE (BIONIC Multi-Parameter Engine)
       │       └──> TFE (Terrain Feature Engine)
       │
       ├──> supra_advanced (/api/v6/supra/advanced)
       ├──> nutrition_intelligence (/api/v6/nutrition-intelligence)
       ├──> soil_engine (/api/v1/soil)
       ├──> weather_v3 (/api/v3/weather)
       ├──> wildlife_behavior_engine (/api/v1/wildlife)
       │
       └──> [Score CHASSE /100 + 32 criteres + zones ecologiques]
               │
               ├──> core/scoring_pipeline (normalisation)
               ├──> core/corridors (deplacement)
               ├──> core/ecology (habitat)
               ├──> core/pressure (pression anthropique)
               ├──> core/ndvi (vegetation satellite)
               └──> core/weather (conditions meteo)
```

**Entree** : Coordonnees GPS ou polygone territoire
**Sortie** : Score /100, 32 criteres detailles, zones ecologiques, corridors, hotspots, salines
**Sous-moteurs** : 10 (SSE, OSG, CME, WSE, VFE, SSVL, TCVE, PME, BMPE, TFE)
**Core impliques** : 6/9

---

## 2.2 Pipeline E-Commerce

```
[Visiteur] ──> [ShopPage]
       │
       ├──> products_engine (/api/v1/products)
       │       ├──> Catalogue + filtrage + scoring BIONIC
       │       └──> Synchronisation suppliers_engine
       │
       ├──> [Ajout panier] ──> cart_engine (/api/v1/cart)
       │
       ├──> [Checkout] ──> payment_engine (/api/v1/payments)
       │       ├──> Stripe Checkout Session
       │       ├──> Webhooks Stripe (confirmation)
       │       └──> orders_engine (creation commande)
       │
       ├──> [Affiliation] ──> ads_engine (consolidated)
       │       ├──> affiliate_ads_engine (/api/v1/affiliate-ads)
       │       ├──> ad_spaces_engine (/api/v1/ad-spaces)
       │       └──> affiliate_switch_engine (/api/v1/affiliate-switch)
       │
       └──> [Fournisseurs] ──> suppliers_engine (/api/v1/suppliers)
               └──> customers_engine (/api/v1/customers)
```

**Integration externe** : Stripe (paiements)
**Modules impliques** : 10

---

## 2.3 Pipeline Territoire

```
[Utilisateur] ──> [MonTerritoireBionicPage]
       │
       ├──> geospatial_engine (/api/v1/geospatial) — hub geospatial
       ├──> ecoforestry_engine (/api/v1/ecoforestry) — peuplements
       ├──> soil_engine (/api/v1/soil) — pedologie
       ├──> data_layers (/api/v1/data/*) — 5 couches
       ├──> wms_engine (/api/v1/wms) — cartes MRNF
       │
       ├──> [Navigation] ──> terrain_nav (engine)
       │       ├──> waypoint_engine (/api/v1/waypoints)
       │       └──> live_heading_engine (/api/v1/live-heading)
       │
       ├──> [Observation] ──> hunting_trip_logger (/api/v1/trips)
       │       └──> camera_engine (/api/v1/camera)
       │
       └──> [Partage] ──> share_engine (/api/share)
               └──> EASYlead tracking (generate + track + stats)
```

**Core impliques** : core/geo, core/ndvi, core/ecology

---

## 2.4 Pipeline Marketing

```
[Partage] ──> share_engine (/api/share)
       │
       ├──> EASYlead V1 (generate, track, stats)
       ├──> Marketing Engine (auto-capture, lead scoring)
       ├──> Screenshot + watermark BIONIC OS
       │
       ├──> [Tracking] ──> tracking_engine (/api/v1/tracking-engine)
       │       └──> analytics_engine (/api/v1/analytics)
       │
       ├──> [SEO] ──> seo_engine (/api/v1/bionic/seo)
       │       └──> 59 endpoints, SEO fournisseurs x300
       │
       ├──> [Campagnes] ──> marketing_engine (/api/v1/marketing)
       │       └──> marketing_calendar_engine (/api/v1/marketing-calendar)
       │
       ├──> [Contacts] ──> contact_engine (/api/v1/contact-engine)
       │
       └──> [Referral] ──> referral_engine (/api/v1/referral)
```

---

## 2.5 Pipeline Abonnements

```
[Utilisateur Free] ──> [PricingPage]
       │
       ├──> freemium_engine (/api/v1/freemium)
       │       ├──> Plans : Free / Premium / Pro
       │       ├──> Quotas d'utilisation
       │       └──> Feature gating
       │
       ├──> [Upgrade] ──> payment_engine (/api/v1/payments)
       │       └──> Stripe Checkout
       │
       ├──> [Post-upgrade] ──> upsell_engine (/api/v1/upsell)
       │       ├──> Campagnes d'upsell
       │       └──> A/B testing
       │
       └──> [Onboarding] ──> onboarding_engine (/api/v1/onboarding)
               └──> learning_engine (consolidated)
                       ├──> tutorial_engine (/api/v1/tutorials)
                       └──> formations_engine (/api/formations)
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

| # | Core | Role | Modules dependants | Statut |
|---|------|------|--------------------|--------|
| C1 | alimentation | Alimentation et nutrition animale | nutrition_engine, bionic_engine_p0 | DEPRECATED (Consolidation V6) |
| C2 | corridors | Calcul des corridors de deplacement | bionic_engine_p0, wildlife_behavior | ACTIF |
| C3 | ecology | Moteur ecologique et habitat | bionic_ecological_engine, bionic_engine_p0 | ACTIF |
| C4 | geo | Geolocalisation et GIS utilitaires | geospatial_engine, territory_engine | ACTIF |
| C5 | ndvi | Indice de vegetation satellite | bionic_engine_p0, ecoforestry_engine | ACTIF |
| C6 | pressure | Pression de chasse et anthropique | bionic_engine_p0, scoring_engine | ACTIF |
| C7 | rest | Zones de repos et refuges | bionic_engine_p0, wildlife_behavior | ACTIF |
| C8 | scoring_pipeline | Pipeline de scoring unifie | score_consolide, saline_engine, api_gateway | ACTIF |
| C9 | weather | Donnees meteorologiques | weather_v3, predictive_engine | ACTIF |

**Core actifs** : 8/9 (1 deprecie)

---

# 5. INTERCONNEXIONS P3-P6

Planification des interconnexions inter-modules (documentees dans INTERCONNEXIONS_P3_P6.md).

## 5.1 P3 — Marketing x Partage x Analytics

```
share_engine <──> marketing_engine <──> analytics_engine
     │                  │                     │
     ├──> EASYlead      ├──> Campagnes        ├──> Tracking API
     ├──> Screenshot    ├──> Segmentation     ├──> Heatmaps
     └──> 14 canaux     └──> Lead scoring     └──> Volume/endpoint
```

**Statut** : PARTIELLEMENT IMPLEMENTE (share_engine + EASYlead actifs)

## 5.2 P4 — Intelligence x Strategie x IA

```
bionic_engine_p0 <──> strategy_master_engine <──> ai_engine
      │                      │                        │
      ├──> 10 sous-moteurs   ├──> Plans globaux       ├──> Recommandations
      ├──> Score /100        ├──> Optimisation         ├──> Analyse intelligente
      └──> 32 criteres      └──> Multi-especes        └──> Knowledge base
```

**Statut** : ARCHITECTURE DEFINIE, implementation a venir

## 5.3 P5 — Monetisation x Paiement x Upsell

```
payment_engine <──> freemium_engine <──> upsell_engine
      │                    │                    │
      ├──> Stripe          ├──> Plans           ├──> Triggers
      ├──> Webhooks        ├──> Quotas          ├──> Conversion
      └──> Remboursements  └──> Feature flags   └──> A/B testing
```

**Statut** : FONCTIONNEL (Stripe integre, plans actifs)

## 5.4 P6 — Territoire x Navigation x Camera

```
territory_engine <──> waypoint_engine <──> camera_engine
      │                     │                    │
      ├──> Polygones        ├──> Points GPS      ├──> Trail cameras
      ├──> Metadata         ├──> Partage         ├──> Detection
      └──> CRUD             └──> Scoring         └──> Analyse photo
                                   │
                              hunting_trip_logger
                                   │
                              live_heading_engine
```

**Statut** : FONCTIONNEL (waypoints + trips actifs)

---

# 6. GOUVERNANCE

## 6.1 Admin Premium

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

## 6.2 Master Switch

```
master_switch (/api/v1/master-switch, /api/v1/global-switch)
    ├── Global ON/OFF — Autorite STEEVE-MAX uniquement
    ├── Controle par canal (14 canaux partage)
    ├── Admin sync : 9 modules
    │     messaging_engine, x300_strategy, seo_engine,
    │     affiliate_ads, reseautage, email_marketing,
    │     analytics_engine, partnership_engine, freemium_upsell
    └── Override mode pour maintenance
```

## 6.3 ULTRA-MAX++

```
ultra_max_firewall (/api/firewall)
    ├── Registre SCELLE — 12 constantes verrouillees
    ├── Authority : STEEVE-MAX
    ├── 7 verrous runtime actifs
    ├── Boot guard OK
    ├── Geo-fencing urbain (Shapely)
    └── Aucune modification sans cle d'autorite
```

## 6.4 BCE-4X

```
bce/ (BIONIC Compliance Engine)
    ├── engine.py — Moteur principal BCE
    ├── bce_ruleset_v8.py — Regles de validation V8
    ├── bce_corridor_v9.py — Validation corridors V9
    ├── bce_max_4_1.py — Certification MAX 4.1
    ├── golden/ — Standards GOLDEN UI
    └── validators/ — Validateurs specialises
```

**Principes** :
- ZERO LOSS — Aucune fonctionnalite supprimee sans validation STEEVE-MAX
- ZERO REGRESSION — Chaque modification testee et validee
- ZERO INTERPRETATION — Execution stricte des directives

---

# 7. SECURITE ET PERMISSIONS

## 7.1 Roles

| Role | Niveau | Acces |
|------|--------|-------|
| anonymous | 0 | Pages publiques (accueil, shop) |
| user | 1 | Analyse territoire (quotas Free), dashboard, waypoints |
| premium | 2 | Analyse illimitee, SUPRA, intelligence, rapports |
| business | 3 | Dashboard business, partenaires, analytics avances |
| admin | 4 | Admin Premium complet, Master Switch, BCE-4X |
| STEEVE-MAX | 5 | Autorite supreme — toutes operations + gouvernance |

## 7.2 Controle d'acces

| Module | Prefix | Fonction |
|--------|--------|----------|
| roles_engine | /api/v1/roles | Verification roles et permissions |
| access_engine_v6 | /api/v6/access | Controle d'acces par zone geographique |
| access_clarity_engine_v7 | /api/v7/clarity | Clarification niveaux d'acces |
| auth_engine | /api/auth | JWT, login, register, reset |

## 7.3 Chaine de commandement

```
STEEVE-MAX (Autorite supreme, niveau 5)
    └── BCE-4X (Protocole de gouvernance)
         ├── GOLDEN UI (Standards visuels)
         ├── ULTRA-MAX++ (Firewall + verrous + registre scelle)
         ├── Master Switch (Controle global ON/OFF)
         └── Admin Premium (Gouvernance operationnelle, 210 endpoints)
```

---

# ANNEXE A — CARTOGRAPHIE COMPLETE

## A.1 Inventaire quantitatif

| Metrique | Valeur |
|----------|--------|
| Module directories | 79 |
| Modules standalone | 12 |
| Total modules logiques | 91 |
| Modules consolides (facades) | 2 (ads_engine, learning_engine) |
| Modules deprecies | 2 (geo_engine, core/alimentation) |
| Modules reclasses | 2 (chasseur_jumeau → experiments, liste_epicerie → utility_modules) |
| Moteurs specialises (engines/) | 5 |
| Sous-systemes core (core/) | 9 (8 actifs + 1 deprecie) |
| Routes backend (routes/) | 6 |
| Total endpoints API (approx.) | 1675+ |
| Pages frontend | 31 |
| Dependances frontend | 58 |

## A.2 Modules critiques (>20 endpoints)

| Module | Endpoints | Domaine |
|--------|-----------|---------|
| admin_engine | 210 | Admin |
| bionic_engine_p0 | 154 | Analyse |
| seo_engine | 59 | Marketing |
| data_layers | 59 | Geospatial |
| nutrition_intelligence | 35 | SUPRA |
| bionic_knowledge_engine | 35 | SUPRA |
| geospatial_engine | 33 | Geospatial |
| saline_engine | 26 | Analyse |
| geo_engine | 26 | Geospatial (DEPRECATED) |
| affiliate_ads_engine | 24 | E-Commerce |
| tracking_engine | 22 | Marketing |
| marketing_engine | 22 | Marketing |

## A.3 Modules isoles (0 dependance externe, <5 endpoints)

| Module | Endpoints | Note |
|--------|-----------|------|
| engine_3d | 8 | Visualisation 3D |
| plugins_engine | 0 | Systeme de plugins |
| engine_registry | 0 | Registre interne |
| marketplace_engine | 0 | Place de marche (stub) |
| territory_engine | 0 | Service interne |
| terrain_nav (engine) | 0 | Service interne |
| docs.py | — | Documentation |
| setup_builder.py | — | Configuration |

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
| auth | /api/auth/* | auth_engine |
| share | /api/share/* | share_engine + EASYlead |
| firewall | /api/firewall/* | ultra_max_firewall |
| partners | /api/partners/* | partner_engine |
| formations | /api/formations/* | formations_engine |
| bsaa | /api/bsaa/* | bsaa |
| backup | /api/backup-cloud/* | backup_cloud_engine |
| admin | /api/admin/* | optimization_engine, geo_engine (deprecated) |

---

## OBJECTIFS PREPARATOIRES (Section C)

Ce document AUBO_V1 constitue la base pour :

| Objectif | Document cible | Statut |
|----------|---------------|--------|
| SUPRA_PIPELINE_V1 | Pipeline scoring complet | PRET (Section 2.1) |
| E_COMMERCE_PIPELINE_V1 | Pipeline e-commerce complet | PRET (Section 2.2) |
| INTERCONNEXIONS_P3_P6_V2 | Interconnexions inter-modules V2 | PRET (Section 5) |
| EASYlead Analytics x5100 | Integration Admin Premium | PRET (Section 6.1) |
| Certification BIONIC OS V2 | Certification complete | PRET (toutes sections) |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : AUBO_V1 1.0.0
**Modules documentes** : 91 (79 dirs + 12 standalone) + 5 engines + 9 core
**Endpoints documentes** : 1675+
**Merge main** : STRICTEMENT INTERDIT
