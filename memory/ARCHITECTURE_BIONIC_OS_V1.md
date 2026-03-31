# ARCHITECTURE BIONIC OS V1 — DOCUMENTATION PRE-CERTIFICATION V2
## Directive x5200-STEEVE_MAX — ARCHITECTURE_AUDIT_V1
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-03-31 | Merge MAIN : STRICTEMENT INTERDIT

---

# SECTION A — ARCHITECTURE LOGICIELLE (HIGH-LEVEL)

## A.1 Vue d'ensemble

BIONIC OS est une plateforme d'analyse de territoires de chasse operant sur une architecture
modulaire React/FastAPI/MongoDB. Le systeme comprend **75 modules backend**, **5 moteurs
specialises**, **9 sous-systemes core**, **~1675 endpoints API**, et **31 pages frontend**.

```
┌─────────────────────────────────────────────────────────────────┐
│                      BIONIC OS — ARCHITECTURE                   │
├─────────────┬───────────────┬───────────────┬──────────────────┤
│  FRONTEND   │    BACKEND    │    ENGINES    │    DATABASES     │
│  React 19   │  FastAPI      │  5 moteurs    │  MongoDB         │
│  31 pages   │  75 modules   │  specialises  │  Collections     │
│  58 deps    │  12 standalone│  9 core       │  multiples       │
│  Leaflet    │  6 routes     │  Pipeline     │                  │
│  Zustand    │  1675+ API    │  Scoring      │                  │
└─────────────┴───────────────┴───────────────┴──────────────────┘
```

## A.2 Modules principaux (75 modules directory)

| Categorie | Modules | Quantite |
|-----------|---------|----------|
| Analyse & Scoring | bionic_engine_p0, scoring_engine, nutrition_engine, soil_engine, waypoint_scoring_engine | 5 |
| Ecologie & Terrain | bionic_ecological_engine, ecoforestry_engine, wildlife_behavior_engine, weather_fauna_simulation_engine | 4 |
| Geospatial | geo_engine, geospatial_engine, wms_engine, data_layers (5 sous-modules) | 8 |
| Intelligence | ai_engine, predictive_engine, recommendation_engine, bionic_knowledge_engine, bionic_data_fabric | 5 |
| E-Commerce | products_engine, orders_engine, cart_engine, payment_engine, suppliers_engine, customers_engine | 6 |
| Marketing & Affiliation | affiliate_ads_engine, affiliate_switch_engine, ad_spaces_engine, marketing_engine, marketing_calendar_engine, seo_engine | 6 |
| Utilisateurs & Auth | auth_engine, user_engine, roles_engine, onboarding_engine, progression_engine | 5 |
| Social & Networking | networking_engine, messaging_engine, share_engine, referral_engine, contact_engine | 5 |
| Admin & Controle | admin_engine, master_switch, ultra_max_firewall, rules_engine, backup_cloud_engine | 5 |
| Monetisation | freemium_engine, upsell_engine, partner_engine, bsaa | 4 |
| Territoire & Navigation | territory_engine, tracking_engine, waypoint_engine, hunting_trip_logger, live_heading_engine, camera_engine | 6 |
| Strategie & Planification | strategy_master_engine, trigger_engine, alerts_engine, formations_engine, tutorial_engine | 5 |
| Specialises | saline_engine, salines_ultime_engine, access_engine_v6, access_clarity_engine_v7, optimization_engine, notification_unified_engine, bionic_stand_recommendation_engine | 7 |
| Divers | api_gateway, engine_registry, engine_3d, plugins_engine, solunar, legal_time_engine | 6 |

## A.3 Moteurs internes (engines/)

| Moteur | Prefixe API | Role |
|--------|-------------|------|
| hunt_orchestrator | /api/v1/hunt | Orchestration complete de la session de chasse |
| nutrition_intelligence | /api/v6/nutrition-intelligence | Intelligence nutritionnelle SUPRA |
| supra_advanced | /api/v6/supra/advanced | Analyse SUPRA avancee multi-criteres |
| terrain_nav | N/A (service interne) | Navigation terrain et routage |
| weather_v3 | /api/v3/weather | Meteo BIONIC V3 temps reel |

## A.4 Sous-systemes Core (core/)

| Core | Role |
|------|------|
| alimentation | Moteur d'alimentation et nutrition animale |
| corridors | Calcul des corridors de deplacement |
| ecology | Moteur ecologique et habitat |
| geo | Geolocalisation et GIS utilitaires |
| ndvi | Indice de vegetation par satellite |
| pressure | Pression de chasse et anthropique |
| rest | Zones de repos et refuges |
| scoring_pipeline | Pipeline de scoring unifie |
| weather | Donnees meteorologiques |

## A.5 Services backend (routes/)

| Route | Fichier | Role |
|-------|---------|------|
| Zones avancees | advanced_zones.py | Zones ecologiques avancees |
| Bathymetrie | bathymetry.py | Donnees bathymetriques |
| BIONIC Engine | bionic_engine_router.py | Router principal BIONIC |
| Ecologique V8 | ecological_router_v8.py | Intelligence ecologique |
| Rapports | reports.py | Generation de rapports |
| Donnees utilisateur | user_data.py | Waypoints et lieux |

## A.6 Services frontend (pages/)

| Page | Fichier | Route |
|------|---------|-------|
| Accueil | App.js (HomePage) | / |
| Dashboard | DashboardPage.jsx | /dashboard |
| Analyse Territoire | MonTerritoireBionicPage.jsx | /mon-territoire-bionic |
| Carte Interactive | MapPage.jsx | /map |
| Permis de Chasse | HuntingLicensePage.jsx | /permis-chasse |
| Magasin | ShopPage.jsx | /shop |
| Produit | ProductPage.jsx | /product/:id |
| Comparaison | ComparePage.jsx | /compare |
| Analytics | AnalyticsPage.jsx | /analytics |
| Previsions | ForecastPage.jsx | /forecast |
| Plan Maitre | PlanMaitrePage.jsx | /plan-maitre |
| Tarification | PricingPage.jsx | /pricing |
| Paiement Succes | PaymentSuccessPage.jsx | /payment-success |
| Paiement Annule | PaymentCancelPage.jsx | /payment-cancel |
| SUPRA | SupraPage.jsx | /supra |
| Calibration | CalibrationDashboard.jsx | /calibration |
| Rapports | ReportsPage.jsx | /reports |
| Comparaison Especes | SpeciesComparisonPage.jsx | /species-comparison |
| Modules BIONIC | BionicModulesPage.jsx | /bionic-modules |
| BSAA Dashboard | BsaaDashboardPage.jsx | /bsaa |
| Business | BusinessPage.jsx | /business |
| Admin Premium | AdminPremiumPage.jsx | /admin-premium |
| Admin Geo | AdminGeoPage.jsx | /admin-geo |
| Marketing Calendar | MarketingCalendarPage.jsx | /marketing-calendar |
| Onboarding | OnboardingPage.jsx | /onboarding |
| Formations | App.js (FormationsPage) | /formations |
| Sorties | TripsPage.jsx | /trips |
| Observation | FieldObservationForm.jsx | /observation |
| Reseautage | NetworkingHub.jsx | /networking |
| Terres | LandsRental.jsx | /lands |
| Demo BIONIC | BionicAnalysisDemoPage.jsx | /bionic-demo |

## A.7 API internes et externes

### APIs internes (1675+ endpoints)
Regroupes par famille de prefixe :
- `/api/v1/*` — 45+ modules (scoring, nutrition, tracking, commerce, etc.)
- `/api/v3/*` — API Gateway + Weather V3
- `/api/v6/*` — Access Engine, Nutrition Intelligence, SUPRA Advanced
- `/api/v7/*` — Access Clarity Engine
- `/api/auth/*` — Authentification
- `/api/share/*` — Share Engine + EASYlead
- `/api/firewall/*` — ULTRA-MAX++ Firewall
- `/api/partners/*` — Partner Engine
- `/api/formations/*` — Formations Engine
- `/api/bsaa/*` — BIONIC Social Ads Automation
- `/api/backup-cloud/*` — Backup Cloud Engine

### APIs externes consommees
| Service | Usage |
|---------|-------|
| Stripe | Paiements Premium et checkout |
| OpenStreetMap / Overpass | Donnees geospatiales terrain |
| OpenTopography / SRTM | Donnees elevation et DEM |
| WMS Quebec (MRNF) | Cartes ecoforestieres |
| Esri / Leaflet Tiles | Fonds de carte |
| Meteo APIs | Donnees meteorologiques temps reel |

## A.8 Dependances critiques

### Backend (Python)
- FastAPI + Uvicorn (serveur ASGI)
- Motor (MongoDB async driver)
- Shapely (geometrie territoriale + geo-fencing)
- Pydantic (validation donnees)
- HTTPX / Aiohttp (appels API asynchrones)

### Frontend (JavaScript)
- React 19.0.0
- React Router DOM 7.5.1
- Leaflet 1.9.4 + React-Leaflet 5.0.0
- Axios 1.8.4
- html2canvas 1.4.1 (screenshot partage)
- Lucide React 0.507.0 (icones)
- Zustand 5.0.12 (state management)
- Sonner 2.0.3 (notifications toast)
- Shadcn/UI (composants UI)

---

# SECTION B — ARCHITECTURE DES MOTEURS SUPRA

## B.1 Moteur Analyse (bionic_engine_p0)

Le moteur d'analyse principal. Comprend 10+ sous-routeurs specialises :

| Sous-routeur | Role |
|-------------|------|
| pipeline_router | Pipeline d'analyse complete |
| scoring_router | Scoring BIONIC multi-criteres |
| hotspot_router | Detection et gestion des hotspots |
| organic_zones_router | Zones organiques V2 |
| spatial_clipping_router | Clipping spatial invariant |
| seasonal_conditions_router | Conditions saisonnieres |
| hunting_path_router | Chemins de chasse |
| engines_v2_router | Moteurs V2 (SSE, OSG, CME, etc.) |
| engines_v3_router | Moteurs V3 |
| sse_router | Species Scoring Engine |
| osg_router | Organic Scoring Grid |
| cme_router | Corridor Movement Engine |
| wse_wiv_router | Weather Scoring Engine |
| vfe_router | Vegetation Factor Engine |
| ssvl_router | Species-Specific Vegetation Layer |
| tcve_router | Terrain Characteristic Value Engine |
| pme_router | Pressure Measurement Engine |
| bmpe_router | BIONIC Multi-Parameter Engine |
| tfe_router | Terrain Feature Engine |

## B.2 Moteur Fiche (criteria + nutrition)

| Composant | Fichier | Contenu |
|-----------|---------|---------|
| criteriaDatabase.js | Frontend | 13 criteres V1+P0 (5 especes, 15 sections/critere) |
| criteriaDatabase_P1P2.js | Frontend | 19 criteres P1/P2 (1327 lignes) |
| CriteriaDetailModal.jsx | Frontend | Modal d'affichage fiches techniques |
| NutritionPointDetailPanel.jsx | Frontend | Panel detail point nutritionnel |
| nutrition_engine | Backend | Moteur nutritionnel V1 |
| nutrition_intelligence | Backend (engines/) | Intelligence nutritionnelle SUPRA |
| saline_engine | Backend | Moteur saline |
| salines_ultime_engine | Backend | Scores salines ultime (5 scores + 20 sources) |

## B.3 Moteur Intelligence

| Composant | Prefixe API | Role |
|-----------|-------------|------|
| ai_engine | /api/v1/ai | Moteur IA principal |
| predictive_engine | /api/v1/predictive | Previsions predictives |
| recommendation_engine | /api/v1/recommendation | Recommandations personnalisees |
| bionic_knowledge_engine | /api/v1/bionic-knowledge | Base de connaissances BIONIC |
| bionic_data_fabric | /api/v1/data-fabric | Fabric de donnees unifie |
| strategy_master_engine | /api/v1/strategy-master | Strategies de chasse |
| hunt_orchestrator | /api/v1/hunt | Orchestration session de chasse |

## B.4 Moteur Comparez

| Composant | Fichier | Role |
|-----------|---------|------|
| ComparePage.jsx | Frontend | Page de comparaison produits |
| SpeciesComparisonPage.jsx | Frontend | Comparaison par espece |
| scoring_engine | Backend | Scoring multi-criteres |
| products_engine | Backend | Catalogue produits pour comparaison |

## B.5 Moteur Commandez

| Composant | Fichier | Role |
|-----------|---------|------|
| ShopPage.jsx | Frontend | Magasin en ligne |
| ProductPage.jsx | Frontend | Page produit individuel |
| cart_engine | Backend | Gestion du panier |
| orders_engine | Backend | Gestion des commandes |
| payment_engine | Backend | Integration Stripe |
| suppliers_engine | Backend | Gestion fournisseurs |
| PricingPage.jsx | Frontend | Plans tarifaires Premium |

## B.6 Soil Engine V1

| Composant | Prefixe API | Role |
|-----------|-------------|------|
| soil_engine | /api/v1/soil | Donnees pedologiques |
| ecoforestry_engine | /api/v1/ecoforestry | Donnees ecoforestieres |
| wms_engine | /api/v1/wms | Proxy WMS Quebec |
| data_layers | /api/v1/data/* | 5 couches de donnees (ecoforestry, behavioral, simulation, 3d, geospatial-advanced) |

---

# SECTION C — ARCHITECTURE E-COMMERCE

## C.1 Pipeline Produits

```
products_engine (/api/v1/products)
    ├── CRUD produits (nom, prix, score, image, categorie)
    ├── Recherche et filtrage multi-criteres
    ├── Scoring qualite BIONIC (note sur 100)
    ├── Import CSV/Excel
    └── Synchronisation avec fournisseurs
```

## C.2 Pipeline Marchands

```
suppliers_engine (/api/v1/suppliers)
    ├── Gestion des fournisseurs/marchands
    ├── Catalogue fournisseur
    ├── Commissions et marges
    └── Suivi de performance

partner_engine (/api/partners)
    ├── Programme partenaires
    ├── Onboarding partenaire
    └── Dashboard partenaire
```

## C.3 Pipeline Affiliation

```
affiliate_ads_engine (/api/v1/affiliate-ads)
    ├── Gestion des annonces affiliees
    ├── Creatives publicitaires
    ├── Tracking clicks et conversions
    └── Checkout affilie

affiliate_switch_engine (/api/v1/affiliate-switch)
    ├── Basculement dropshipping <-> affiliation
    ├── Mode hybride
    └── Configuration par produit

referral_engine (/api/v1/referral)
    ├── Programme de parrainage
    ├── Codes de referral
    ├── Tracking parrainages
    └── Recompenses
```

## C.4 Pipeline Abonnements

```
freemium_engine (/api/v1/freemium)
    ├── Plans: Free, Premium, Pro
    ├── Quotas d'utilisation
    ├── Feature gating
    ├── Verification des abonnements
    └── Gestion des limites

PricingPage.jsx (Frontend)
    ├── Affichage des plans
    ├── Comparaison des fonctionnalites
    └── CTA vers checkout
```

## C.5 Pipeline Paiements (Stripe)

```
payment_engine (/api/v1/payments)
    ├── Checkout Stripe (session)
    ├── Webhooks Stripe
    ├── Verification de paiement
    ├── Historique des transactions
    └── Remboursements

PaymentSuccessPage.jsx — Confirmation de paiement
PaymentCancelPage.jsx — Annulation de paiement
```

## C.6 Pipeline Inventaires

```
products_engine
    ├── Gestion stock (in_stock / out_of_stock)
    ├── Suivi quantites
    └── Alertes rupture de stock

cart_engine (/api/v1/cart)
    ├── Ajout/suppression articles
    ├── Session panier (saline_session_id)
    ├── Calcul sous-totaux et taxes
    └── Transition vers checkout
```

## C.7 Pipeline Commissions

```
suppliers_engine
    ├── Marge fournisseur
    ├── Commission affiliee
    ├── Prix de vente vs prix fournisseur
    └── Tracking des commissions

affiliate_ads_engine
    ├── Commission par clic
    ├── Commission par conversion
    └── Rapport de commissions
```

---

# SECTION D — ARCHITECTURE ADMIN PREMIUM

## D.1 Vue d'ensemble

L'Admin Premium (`AdminPremiumPage.jsx` / `admin_engine`) est le centre de gouvernance
centralise de BIONIC OS. Point d'entree unique : `/admin-premium`.

## D.2 Modules Admin

| Module | Backend | Role |
|--------|---------|------|
| Paiements | payment_engine | Suivi transactions Stripe, webhooks, remboursements |
| Freemium | freemium_engine | Gestion plans, quotas, feature flags |
| Upsell | upsell_engine | Campagnes d'upsell, triggers, conversion |
| Onboarding | onboarding_engine | Flux d'integration nouveaux utilisateurs |
| Tutoriels | tutorial_engine | Contenus pedagogiques, progression |
| Regles | rules_engine | Regles metier configurables |
| Strategies | strategy_master_engine | Strategies de chasse globales |
| Utilisateurs | user_engine + roles_engine | Gestion utilisateurs, roles, permissions |
| Logs | analytics_engine + BCE | Journaux systeme, audit trail |
| Parametres | admin_engine | Configuration globale plateforme |

## D.3 Sections Admin detaillees

### D.3.1 Paiements
- Historique des transactions Stripe
- Verification des webhooks
- Gestion des remboursements
- Dashboard revenus

### D.3.2 Freemium
- Configuration des plans (Free/Premium/Pro)
- Feature flags par plan
- Quotas d'utilisation (analyses/jour, waypoints, etc.)
- Migration entre plans

### D.3.3 Upsell
- Campagnes d'upsell actives
- Evenements declencheurs (TriggerEvent)
- Tracking conversion upsell
- A/B testing

### D.3.4 Onboarding
- Flux d'accueil multi-etapes
- Progression utilisateur
- Tutoriels interactifs
- Scoring engagement

### D.3.5 Tutoriels
- Contenu pedagogique structure
- Progression par module
- Certificats de completion
- Integration avec formations FedéCP

### D.3.6 Regles
- Regles metier configurables
- Conditions et actions
- Priorites et conflits
- Historique des modifications

### D.3.7 Strategies
- Strategies de chasse globales
- Recommandations saisonnieres
- Plans de gestion territoire
- Optimisation multi-especes

### D.3.8 Utilisateurs
- Roles : user, premium, business, admin
- Permissions granulaires
- Historique des connexions
- Gestion des suspensions

### D.3.9 Logs
- Journaux API (requetes/reponses)
- Audit trail BCE-4X
- Logs de paiement
- Alertes systeme

### D.3.10 Parametres
- Configuration globale
- Master Switch
- Feature controls
- Maintenance mode

---

# SECTION E — MODULES ANNEXES

## E.1 SEO Engine

```
seo_engine (/api/v1/seo)
    ├── seo_router — SEO principal
    ├── seo_suppliers_router — SEO fournisseurs x300
    ├── Meta tags dynamiques
    ├── Sitemap generation
    └── SEOHead.jsx (Frontend)
```

## E.2 Marketing

```
marketing_engine (/api/v1/marketing)
    ├── Automation marketing
    ├── Segmentation audience
    ├── Campagnes email
    └── Tracking performance

marketing_calendar_engine (/api/v1/marketing-calendar)
    ├── Calendrier marketing V2
    ├── Evenements planifies
    └── Rappels automatiques

share_engine (/api/share)
    ├── 14 canaux de partage
    ├── EASYlead tracking V1
    ├── Marketing Engine auto-capture
    └── Screenshot + watermark BIONIC
```

## E.3 Messaging Engine

```
messaging_engine (/api/v1/messaging)
    ├── Messagerie interne
    ├── Notifications push
    ├── Templates de messages
    └── File d'attente
```

## E.4 Partenaires

```
partner_engine (/api/partners)
    ├── Gestion partenaires
    ├── Offres partenaires
    ├── Commission tracking
    └── Dashboard partenaire

Frontend:
    ├── BecomePartner.jsx
    ├── PartnerDashboard.jsx
    └── PartnerOffers.jsx
```

## E.5 Catalogue Produits

```
products_engine (/api/v1/products)
    ├── CRUD produits complet
    ├── Categories et filtres
    ├── Images et media
    ├── Scoring BIONIC
    └── Recherche avancee
```

## E.6 Terres / Hotspots

```
Frontend:
    ├── LandsRental.jsx — Location de terres
    ├── AdminHotspotsPanel.jsx — Gestion hotspots admin
    ├── GpsHotspots.jsx — Hotspots GPS
    └── HeatmapLayer.jsx — Visualisation heatmap

Backend:
    ├── lands_rental.py — Gestion location terres
    ├── bionic_engine_p0/hotspots/ — Moteur hotspots
    └── geospatial_data.py — Donnees geospatiales
```

## E.7 Branding

```
Frontend:
    ├── BionicLogo.jsx — Logo BIONIC (main, global, header)
    ├── BrandIdentityAdmin.jsx — Admin identite visuelle
    ├── bionic-colors.js — Palette de couleurs
    ├── bionic-icons.js — Icones BIONIC
    └── bionic_theme.css — Theme CSS
```

## E.8 Contenu

```
Frontend:
    ├── ContentDepot.jsx — Depot de contenu
    ├── PromptManager.jsx — Gestion des prompts IA
    └── CategoriesManager.jsx — Gestion des categories
```

## E.9 Backups

```
backup_cloud_engine (/api/backup-cloud)
    ├── Backup cloud automatise
    ├── Restauration
    ├── Historique des sauvegardes
    └── Verification d'integrite
```

---

# SECTION F — ARCHITECTURE DES FLUX

## F.1 Flux Utilisateur

```
[Visiteur] ---> [Accueil /]
    │
    ├──> [Inscription /auth] ---> auth_engine ---> [MongoDB: users]
    │                              │
    │                              ├──> roles_engine (role: user)
    │                              └──> onboarding_engine (flux accueil)
    │
    ├──> [Connexion] ---> auth_engine ---> JWT Token
    │
    ├──> [Dashboard /dashboard] ---> analytics_engine + weather_v3
    │
    ├──> [Analyse Territoire /mon-territoire-bionic]
    │         │
    │         ├──> bionic_engine_p0 (scoring pipeline)
    │         ├──> soil_engine + ecoforestry_engine
    │         ├──> nutrition_intelligence + salines_ultime_engine
    │         ├──> weather_v3 (meteo temps reel)
    │         ├──> waypoint_engine (points GPS)
    │         └──> share_engine (partage + EASYlead)
    │
    └──> [Compte Premium] ---> freemium_engine + payment_engine
```

## F.2 Flux Produit

```
[Admin] ---> products_engine
    │
    ├──> Creer/Modifier produit
    ├──> Associer fournisseur (suppliers_engine)
    ├──> Definir mode vente (affiliate_switch_engine)
    ├──> Scoring BIONIC automatique
    │
    └──> [Frontend ShopPage]
           │
           ├──> Affichage catalogue
           ├──> Filtrage et tri
           └──> Ajout au panier (cart_engine)
```

## F.3 Flux Paiement

```
[Utilisateur] ---> cart_engine (panier)
    │
    ├──> [Checkout] ---> payment_engine
    │                       │
    │                       ├──> Stripe Checkout Session
    │                       ├──> Redirect Stripe
    │                       │
    │                       ├──> [Succes] ---> PaymentSuccessPage
    │                       │       │
    │                       │       ├──> Webhook Stripe (confirmation)
    │                       │       ├──> orders_engine (creation commande)
    │                       │       └──> freemium_engine (activation plan)
    │                       │
    │                       └──> [Echec] ---> PaymentCancelPage
    │
    └──> [Historique] ---> orders_engine
```

## F.4 Flux Affiliation

```
[Admin] ---> affiliate_ads_engine
    │
    ├──> Creer creative publicitaire
    ├──> Definir commission
    │
    └──> [Frontend] ---> ad_spaces_engine
                            │
                            ├──> Affichage annonces
                            ├──> Tracking clic
                            ├──> Redirection affilie
                            └──> Conversion tracking
```

## F.5 Flux Marchands

```
[Marchand] ---> partner_engine
    │
    ├──> Inscription partenaire
    ├──> Soumission catalogue
    ├──> suppliers_engine (integration)
    │
    └──> [Dashboard] ---> PartnerDashboard.jsx
                            │
                            ├──> Ventes
                            ├──> Commissions
                            └──> Performance
```

## F.6 Flux Abonnements

```
[Utilisateur Free] ---> PricingPage.jsx
    │
    ├──> Choix du plan (Premium/Pro)
    ├──> payment_engine ---> Stripe
    ├──> freemium_engine (activation)
    ├──> upsell_engine (campagnes post-activation)
    │
    └──> [Utilisateur Premium]
            │
            ├──> Quotas augmentes
            ├──> Features deverrouillees
            └──> Analyse illimitee
```

## F.7 Flux SUPRA

```
[Utilisateur] ---> MonTerritoireBionicPage.jsx
    │
    ├──> [Selection zone sur carte]
    │       │
    │       ├──> bionic_engine_p0 / pipeline_router
    │       │       │
    │       │       ├──> SSE (Species Scoring Engine)
    │       │       ├──> OSG (Organic Scoring Grid)
    │       │       ├──> CME (Corridor Movement Engine)
    │       │       ├──> WSE (Weather Scoring Engine)
    │       │       ├──> VFE (Vegetation Factor Engine)
    │       │       ├──> SSVL (Species-Specific Vegetation Layer)
    │       │       ├──> TCVE (Terrain Characteristic Value Engine)
    │       │       ├──> PME (Pressure Measurement Engine)
    │       │       ├──> BMPE (BIONIC Multi-Parameter Engine)
    │       │       └──> TFE (Terrain Feature Engine)
    │       │
    │       ├──> soil_engine (pedologie)
    │       ├──> nutrition_intelligence (SUPRA)
    │       ├──> weather_v3 (meteo)
    │       └──> wildlife_behavior_engine (comportement)
    │
    ├──> [Affichage resultats]
    │       │
    │       ├──> Score CHASSE /100
    │       ├──> 32 criteres (criteriaDatabase.js + P1P2)
    │       ├──> Zones ecologiques (rut, alimentation, repos, eau)
    │       ├──> Corridors de deplacement
    │       ├──> Hotspots
    │       └──> Salines
    │
    └──> [Partage] ---> share_engine + EASYlead
```

## F.8 Flux Admin Premium

```
[Admin STEEVE-MAX] ---> AdminPremiumPage.jsx
    │
    ├──> [Paiements] ---> payment_engine
    ├──> [Produits] ---> products_engine + suppliers_engine
    ├──> [Utilisateurs] ---> user_engine + roles_engine
    ├──> [Marketing] ---> marketing_engine + seo_engine
    ├──> [Partenaires] ---> partner_engine
    ├──> [Freemium] ---> freemium_engine
    ├──> [Master Switch] ---> master_switch
    ├──> [Firewall] ---> ultra_max_firewall
    ├──> [Backup] ---> backup_cloud_engine
    └──> [BCE-4X] ---> bce/ (compliance engine)
```

---

# SECTION G — PERMISSIONS & GOUVERNANCE

## G.1 Master Switch

```
master_switch (/api/v1/master-switch)
    ├── Global ON/OFF — Autorite STEEVE-MAX uniquement
    ├── Controle par canal (14 canaux partage)
    ├── Admin sync avec 9 modules :
    │     messaging_engine, x300_strategy, seo_engine,
    │     affiliate_ads, reseautage, email_marketing,
    │     analytics_engine, partnership_engine, freemium_upsell
    └── Override mode pour maintenance
```

## G.2 Roles

| Role | Niveau | Acces |
|------|--------|-------|
| anonymous | 0 | Pages publiques uniquement (accueil, shop) |
| user | 1 | Analyse territoire (quotas Free), dashboard, waypoints |
| premium | 2 | Analyse illimitee, SUPRA, intelligence, rapports |
| business | 3 | Dashboard business, partenaires, analytics avances |
| admin | 4 | Admin Premium complet, Master Switch, BCE-4X |
| STEEVE-MAX | 5 | Autorite supreme — toutes operations + gouvernance |

## G.3 Acces

```
roles_engine (/api/v1/roles)
    ├── GET /me — Role et permissions courantes
    ├── GET /check/{permission} — Verification permission
    ├── PUT /update — Modification role (admin only)
    ├── GET /users — Liste par role (admin only)
    └── GET /statistics — Distribution des roles

access_engine_v6 (/api/v6/access)
    ├── Controle d'acces par zone geographique
    └── Validation des droits d'acces

access_clarity_engine_v7 (/api/v7/clarity)
    ├── Clarification des niveaux d'acces
    └── Reporting des conflits d'acces
```

## G.4 Validations

```
bce/ (BIONIC Compliance Engine)
    ├── bce_ruleset_v8.py — Regles de validation V8
    ├── bce_corridor_v9.py — Validation corridors V9
    ├── bce_max_4_1.py — BCE MAX 4.1 certification
    ├── engine.py — Moteur de compliance
    ├── router.py — API de validation
    ├── golden/ — Standards GOLDEN
    └── validators/ — Validateurs specialises
```

## G.5 Pare-feux

```
ultra_max_firewall (/api/firewall)
    ├── POST /check — Verification coordonnees en zone autorisee
    ├── GET /zones — Liste des zones configurees
    ├── POST /zones — Ajout de zone (Admin STEEVE-MAX)
    ├── Geo-fencing urbain (Shapely)
    ├── 7 verrous runtime actifs
    └── Registre scelle (12 constantes verrouillees)
```

---

# SECTION H — LOGS & BCE-4X

## H.1 Logs systemes

```
/var/log/supervisor/backend.err.log  — Erreurs backend
/var/log/supervisor/backend.out.log  — Sortie standard backend
/var/log/supervisor/frontend.err.log — Erreurs frontend
/var/log/supervisor/frontend.out.log — Sortie standard frontend
```

## H.2 Logs API

```
analytics_engine (/api/v1/analytics)
    ├── Tracking requetes API
    ├── Temps de reponse
    ├── Codes de retour
    ├── Volume par endpoint
    └── Alertes de performance

tracking_engine (/api/v1/tracking-engine)
    ├── Tracking comportemental
    ├── Sessions utilisateur
    ├── Evenements frontend
    └── Heatmaps d'utilisation
```

## H.3 Logs paiements

```
payment_engine
    ├── Historique transactions Stripe
    ├── Webhooks recus
    ├── Echecs de paiement
    ├── Remboursements
    └── Audit trail complet

MongoDB collections :
    ├── payment_transactions
    ├── stripe_webhooks
    └── payment_logs
```

## H.4 Gouvernance BCE-4X

### Principes fondamentaux
- **ZERO LOSS** — Aucune fonctionnalite ne peut etre supprimee sans validation STEEVE-MAX
- **ZERO REGRESSION** — Chaque modification doit etre testee et validee
- **ZERO INTERPRETATION** — Execution stricte des directives, aucune improvisation

### Protocole BCE-4X
```
bce/
    ├── engine.py — Moteur principal BCE
    │     ├── Validation pre-deploiement
    │     ├── Audit des modifications
    │     ├── Rapport de conformite
    │     └── Certification des releases
    │
    ├── bce_ruleset_v8.py — 8+ regles de validation
    ├── bce_corridor_v9.py — Validation spatiale V9
    ├── bce_max_4_1.py — Certification MAX 4.1
    │
    ├── golden/ — Standards GOLDEN UI
    │     ├── Palette de couleurs (#F5A623 orange BIONIC)
    │     ├── Hierarchie typographique
    │     ├── Composants standardises
    │     └── Regles d'espacement (gap-1.5, V9)
    │
    └── validators/ — Validateurs specialises
          ├── Score invariant
          ├── Water exclusion
          ├── Urban exclusion
          └── Zone integrity
```

### ULTRA-MAX++ Lock
```
ULTRA-MAX++ v3.0
    ├── Registre SCELLE — 12 constantes verrouillees
    ├── Authority : STEEVE-MAX
    ├── 7 verrous runtime actifs
    ├── Boot guard OK
    └── Aucune modification sans cle d'autorite
```

### Chaine de commandement
```
STEEVE-MAX (Autorite supreme)
    └── BCE-4X (Protocole de gouvernance)
         ├── GOLDEN UI (Standards visuels)
         ├── ULTRA-MAX++ (Firewall + verrous)
         ├── Master Switch (Controle global)
         └── Admin Premium (Gouvernance operationnelle)
```

---

# SECTION I — TEXTE OFFICIEL (MISE A JOUR x5200)

## Texte officiel BIONIC — Version x5200

### Description principale (FR)
> Chasse Bionic(TM) redefinit l'art de la chasse moderne. Analysez et comparez en toute
> confiance votre territoire, ses zones d'achalandage, les terres a louer, les pourvoiries
> et les produits les plus performants. Grace a une plateforme fondee exclusivement sur des
> donnees scientifiques, publiques, declarees et verifiables, vous accedez a un veritable
> ecosysteme de precision... directement au bout des doigts.

### Highlight officiel (FR) — MIS A JOUR x5200
> Identifiez et analysez les zones les plus performantes et accedez instantanement aux
> meilleures strategies, approches et solutions afin d'optimiser vos resultats et site de chasse.

### Slogan officiel
> La science valide ce que le terrain confirme.(TM)

### Watermark screenshot (Share Engine V1)
> Analyse generee avec BIONIC OS -- IA Terrain

### Fichiers mis a jour (x5200)
- `/app/frontend/src/contexts/LanguageContext.jsx` — hero_highlight FR + EN, share_official_highlight FR + EN
- `/app/frontend/src/components/territoire/ui/ShareBionicButton.jsx` — OFFICIAL_TEXT_FR.highlight

---

# RESUME QUANTITATIF

| Metrique | Valeur |
|----------|--------|
| Modules backend (directories) | 75 |
| Modules backend (standalone .py) | 12 |
| Moteurs specialises (engines/) | 5 |
| Sous-systemes core (core/) | 9 |
| Routes backend (routes/) | 6 |
| Sous-routeurs bionic_engine_p0 | 18+ |
| Total endpoints API (approx.) | 1675+ |
| Pages frontend | 31 |
| Dependances frontend | 58 |
| Criteres Guide BIONIC | 32 (13 V1 + 19 P1P2) |
| Especes couvertes | 5 |
| Canaux de partage | 14 |
| Roles utilisateur | 6 |
| Collections MongoDB | 20+ |
| Tests backend | 160+ fichiers |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : ARCHITECTURE_BIONIC_OS_V1
**Directive** : x5200-STEEVE_MAX
**Merge main** : STRICTEMENT INTERDIT
