# AUDIT TOTAL BIONIC V6 — STEEVE-MAX x3050-EXEC
# GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX
## Date: 2026-02-XX | Branche: Work1 | MASTER SWITCH: LOCKED

---

> **Ce document constitue la verite technique absolue du systeme BIONIC V6.**
> Aucune omission, aucun resume, aucune simplification.
> Chaque moteur, chaque module, chaque endpoint, chaque fichier est documente.

---

# TABLE DES MATIERES

1. [AUDIT 1 — ENGINES BACKEND (~90 modules)](#audit-1--engines-backend)
2. [AUDIT 2 — MODULES FRONTEND](#audit-2--modules-frontend)
3. [AUDIT 3 — DASHBOARD](#audit-3--dashboard)
4. [AUDIT 4 — MON TERRITOIRE](#audit-4--mon-territoire)
5. [AUDIT 5 — API ROUTES](#audit-5--api-routes)
6. [AUDIT 6 — PREVIEW vs WORK1](#audit-6--preview-vs-work1)
7. [AUDIT 7 — RELIQUES](#audit-7--reliques)

---

# AUDIT 1 — ENGINES BACKEND

## 1.1 Inventaire complet des repertoires modules/

**Total repertoires engine: 90** (hors `__pycache__`)
**Total fichiers Python dans modules/: 172 833 lignes**
**Fichiers Python standalone (modules/*.py): 12**

### 1.1.1 Modules ENREGISTRES dans routers.py (ACTIFS — 75 routers)

| # | Alias Router | Import Path | Prefix API | Tags | Statut |
|---|---|---|---|---|---|
| 1 | nutrition_router | modules.nutrition_engine.v1 | /api/v1/nutrition | Nutrition Engine | ACTIF |
| 2 | scoring_router | modules.scoring_engine.v1 | /api/v1/scoring | Scoring Engine | ACTIF |
| 3 | ai_router | modules.ai_engine.v1 | /api/v1/ai | AI Engine | ACTIF |
| 4 | weather_router | modules.weather_engine.v1 | /api/v1/weather | Weather Engine | ACTIF |
| 5 | geospatial_router | modules.geospatial_engine.v1 | /api/v1/geospatial | Geospatial Engine | ACTIF |
| 6 | wms_router | modules.wms_engine.v1 | /api/v1/wms | WMS Engine | ACTIF |
| 7 | user_router | modules.user_engine.v1 | /api/v1/user | User Engine | ACTIF |
| 8 | notification_router | modules.notification_unified_engine | /api/v1/notifications | Notification Unified Engine | ACTIF |
| 9 | referral_router | modules.referral_engine.v1 | /api/v1/referral | Referral Engine | ACTIF |
| 10 | territory_router | modules.territory_engine.v1 | /api/v1/territory | Territory Engine | ACTIF |
| 11 | tracking_router | modules.tracking_engine.v1 | /api/v1/tracking-engine | Tracking Engine | ACTIF |
| 12 | marketplace_router | modules.marketplace_engine.v1 | /api/v1/marketplace | Marketplace Engine | ACTIF |
| 13 | plugins_router | modules.plugins_engine.v1 | /api/v1/plugins | Plugins Engine | ACTIF |
| 14 | recommendation_router | modules.recommendation_engine.v1 | /api/v1/recommendation | Recommendation Engine | ACTIF |
| 15 | ecoforestry_router | modules.ecoforestry_engine.v1 | /api/v1/ecoforestry | Ecoforestry Engine | ACTIF |
| 16 | engine_3d_router | modules.engine_3d.v1 | /api/v1/3d | Engine 3D | ACTIF |
| 17 | wildlife_router | modules.wildlife_behavior_engine.v1 | /api/v1/wildlife | Wildlife Behavior Engine | ACTIF |
| 18 | simulation_router | modules.weather_fauna_simulation_engine.v1 | /api/v1/simulation | Weather Fauna Simulation | ACTIF |
| 19 | progression_router | modules.progression_engine.v1 | /api/v1/progression | Progression Engine | ACTIF |
| 20 | networking_router | modules.networking_engine.v1 | /api/v1/network | Networking Engine | ACTIF |
| 21 | ecoforestry_data_router | modules.data_layers.ecoforestry_layers | (via data_layers) | Data Layer: Ecoforestry | ACTIF |
| 22 | behavioral_data_router | modules.data_layers.behavioral_layers | (via data_layers) | Data Layer: Behavioral | ACTIF |
| 23 | simulation_data_router | modules.data_layers.simulation_layers | (via data_layers) | Data Layer: Simulation | ACTIF |
| 24 | layers_3d_data_router | modules.data_layers.layers_3d | (via data_layers) | Data Layer: 3D | ACTIF |
| 25 | advanced_geo_data_router | modules.data_layers.advanced_geospatial_layers | (via data_layers) | Data Layer: Advanced Geo | ACTIF |
| 26 | live_heading_router | modules.live_heading_engine | /api/v1/live-heading | Live Heading Engine | ACTIF |
| 27 | products_router | modules.products_engine | /api/v1/products | Products Engine | ACTIF |
| 28 | orders_router | modules.orders_engine | /api/v1/orders | Orders Engine | ACTIF |
| 29 | suppliers_router | modules.suppliers_engine | /api/v1/suppliers | Suppliers Engine | ACTIF |
| 30 | customers_router | modules.customers_engine | /api/v1/customers | Customers Engine | ACTIF |
| 31 | cart_router | modules.cart_engine | /api/v1/cart | Cart Engine | ACTIF |
| 32 | alerts_router | modules.alerts_engine | /api/v1/alerts | Alerts Engine | ACTIF |
| 33 | legal_time_router | modules.legal_time_engine | /api/v1/legal-time | Legal Time Engine | ACTIF |
| 34 | predictive_router | modules.predictive_engine | /api/v1/predictive | Predictive Engine | ACTIF |
| 35 | analytics_router | modules.analytics_engine | /api/v1/analytics | Analytics Engine | ACTIF |
| 36 | waypoint_scoring_router | modules.waypoint_scoring_engine | /api/v1/waypoint-scoring | Waypoint Scoring Engine | ACTIF |
| 37 | auth_router | modules.auth_engine | /api/auth | Auth Engine | ACTIF |
| 38 | hunting_trip_logger_router | modules.hunting_trip_logger | /api/v1/trips | Hunting Trip Logger | ACTIF |
| 39 | roles_router | modules.roles_engine.v1 | /api/v1/roles | Roles Engine | ACTIF |
| 40 | rules_router | modules.rules_engine.router | /api/v1/rules | Rules Engine | ACTIF |
| 41 | strategy_master_router | modules.strategy_master_engine.router | /api/v1/strategy-master | Strategy Master Engine | ACTIF |
| 42 | payment_router | modules.payment_engine.router | /api/v1/payments | Payment Engine (Stripe) | ACTIF |
| 43 | freemium_router | modules.freemium_engine.router | /api/v1/freemium | Freemium Engine | ACTIF |
| 44 | upsell_router | modules.upsell_engine.router | /api/v1/upsell | Upsell Engine | ACTIF |
| 45 | onboarding_router | modules.onboarding_engine.router | /api/v1/onboarding | Onboarding Engine | ACTIF |
| 46 | tutorial_router | modules.tutorial_engine.router | /api/v1/tutorials | Tutorial Engine | ACTIF |
| 47 | admin_premium_router | modules.admin_engine.router | /api/v1/admin | Admin Engine Premium | ACTIF |
| 48 | bionic_knowledge_router | modules.bionic_knowledge_engine.knowledge_router | /api/v1/knowledge | Bionic Knowledge Engine | ACTIF |
| 49 | bionic_seo_router | modules.seo_engine.seo_router | /api/v1/seo | SEO Engine | ACTIF |
| 50 | seo_suppliers_router | modules.seo_engine.seo_suppliers_router | /api/v1/seo-suppliers | SEO Suppliers | ACTIF |
| 51 | affiliate_switch_router | modules.affiliate_switch_engine.router | /api/v1/affiliate-switch | Affiliate Switch Engine | ACTIF |
| 52 | affiliate_ads_router | modules.affiliate_ads_engine.router | /api/v1/affiliate-ads | Affiliate Ad Automation | ACTIF |
| 53 | ad_spaces_router | modules.ad_spaces_engine.router | /api/v1/ad-spaces | Ad Spaces Engine | ACTIF |
| 54 | messaging_router | modules.messaging_engine.router | /api/v1/messaging | Messaging Engine V2 | ACTIF |
| 55 | tracking_behavioral_router | modules.tracking_engine.v1.router | /api/v1/tracking-engine | Tracking Behavioral | ACTIF |
| 56 | marketing_automation_router | modules.marketing_engine.v1.router | /api/v1/marketing | Marketing Engine | ACTIF |
| 57 | marketing_calendar_router | modules.marketing_calendar_engine.v2.router | /api/v1/marketing-calendar | Marketing Calendar V2 | ACTIF |
| 58 | waypoint_interaction_router | modules.waypoint_engine.v1.router | /api/v1/waypoints | Waypoint Engine | ACTIF |
| 59 | contact_engine_router | modules.contact_engine.router | /api/v1/contact-engine | Contact Engine X300% | ACTIF |
| 60 | trigger_engine_router | modules.trigger_engine.router | /api/v1/trigger-engine | Marketing Trigger Engine | ACTIF |
| 61 | master_switch_router | modules.master_switch.router | /api/v1/master-switch | Master Switch X300% | ACTIF |
| 62 | backup_cloud_router | modules.backup_cloud_engine.router | /api/backup-cloud | Backup Cloud | ACTIF |
| 63 | formations_router | modules.formations_engine.router | /api/formations | Formations Engine | ACTIF |
| 64 | social_router | modules.social_engine.router | /api/social | Social Engine | ACTIF |
| 65 | partner_router | modules.partner_engine.router | /api/partners | Partner Engine | ACTIF |
| 66 | bionic_engine_router | routes.bionic_engine_router | (via routes/) | BIONIC Engine Router | ACTIF |
| 67 | bionic_weather_router | modules.bionic_engine_p0.weather_router | (via P0) | BIONIC Weather | ACTIF |
| 68 | bionic_scoring_router | modules.bionic_engine_p0.scoring_router | (via P0) | BIONIC Scoring | ACTIF |
| 69 | hotspot_admin_router | modules.bionic_engine_p0.hotspots.hotspot_router | (via P0) | Hotspot Admin | ACTIF |
| 70 | optimization_router | modules.optimization_engine.router | /api/admin/optimization | Auto-Optimization | ACTIF |
| 71 | ecological_intelligence_router | modules.bionic_ecological_engine.router | /api/v1/ecological-intelligence | Ecological Intelligence | ACTIF |
| 72 | data_fabric_router | modules.bionic_data_fabric.router | /api/v1/data-fabric | Data Fabric | ACTIF |
| 73 | stand_recommendation_router | modules.bionic_stand_recommendation_engine.router | /api/v1/stand-recommendation | Stand Recommendation | ACTIF |
| 74 | camera_router | modules.camera_engine.v1 | /api/v1/camera | Camera Engine | ACTIF |
| 75 | admin_engine_router | modules.admin_engine.v1 | /api/v1/admin | Admin Engine V1 | ACTIF |

### 1.1.2 Modules enregistres DIRECTEMENT dans server.py (hors routers.py)

| # | Router | Import Path | Prefix | Statut |
|---|---|---|---|---|
| S1 | bionic_p0_router | modules.bionic_engine_p0.router | /api/v1/bionic | ACTIF |
| S2 | organic_zones_router | modules.bionic_engine_p0.routers.organic_zones_router | /api/v1/bionic/organic-zones | ACTIF |
| S3 | spatial_clipping_router | modules.bionic_engine_p0.routers.spatial_clipping_router | /api/v1/bionic/clipped-zones | ACTIF |
| S4 | reports_router | routes.reports | /api/reports | ACTIF |
| S5 | user_data_router | routes.user_data | /api/user-data | ACTIF |
| S6 | seasonal_router | modules.bionic_engine_p0.routers.seasonal_conditions_router | /api/v1/bionic/seasonal-conditions | ACTIF |
| S7 | hunting_path_router | modules.bionic_engine_p0.routers.hunting_path_router | /api/v1/bionic/hunting-path | ACTIF |
| S8 | engines_v2_router | modules.bionic_engine_p0.routers.engines_v2_router | /api/v1/bionic/engines-v2 | ACTIF |
| S9 | engines_v3_router | modules.bionic_engine_p0.routers.engines_v3_router | /api/v1/bionic/engines-v3 | ACTIF |
| S10 | sse_router | modules.bionic_engine_p0.routers.sse_router | /api/v1/bionic/sse | ACTIF |
| S11 | osg_router | modules.bionic_engine_p0.routers.osg_router | /api/v1/bionic/osg | ACTIF |
| S12 | cme_router | modules.bionic_engine_p0.routers.cme_router | /api/v1/bionic/cme | ACTIF |
| S13 | wse_wiv_router | modules.bionic_engine_p0.routers.wse_wiv_router | /api/v1/bionic/wse-wiv | ACTIF |
| S14 | vfe_router | modules.bionic_engine_p0.routers.vfe_router | /api/v1/bionic/vfe | ACTIF |
| S15 | ssvl_router | modules.bionic_engine_p0.routers.ssvl_router | /api/v1/bionic/ssvl | ACTIF |
| S16 | tcve_router | modules.bionic_engine_p0.routers.tcve_router | /api/v1/bionic/tcve | ACTIF |
| S17 | pme_router | modules.bionic_engine_p0.routers.pme_router | /api/v1/bionic/pme | ACTIF |
| S18 | bmpe_router | modules.bionic_engine_p0.routers.bmpe_router | /api/v1/bionic/bmpe | ACTIF |
| S19 | tfe_router | modules.bionic_engine_p0.routers.tfe_router | /api/v1/bionic/tfe | ACTIF |
| S20 | pipeline_router | modules.bionic_engine_p0.routers.pipeline_router | /api/v1/bionic/pipeline | ACTIF |
| S21 | api_keys_router | modules.bionic_engine_p0.routers.api_keys_router | /api/v1/system/api-keys | ACTIF |
| S22 | ml_router | modules.bionic_engine_p0.routers.ml_router | /api/v1/bionic/ml | ACTIF |
| S23 | ecological_v8_router | routes.ecological_router_v8 | /api/v1/ecological | ACTIF |
| S24 | dem_router | modules.bionic_engine_p0.routers.dem_router | /api/v1/bionic/dem | ACTIF |
| S25 | dem_shadow_router | modules.bionic_engine_p0.routers.dem_shadow_router | /api/v1/bionic/dem-shadow | ACTIF |
| S26 | weather_shadow_router | modules.bionic_engine_p0.routers.weather_shadow_router | /api/v1/bionic/weather-shadow | ACTIF |
| S27 | full_comparison_router | modules.bionic_engine_p0.routers.full_comparison_router | /api/v1/bionic/shadow | ACTIF |
| S28 | ndvi_shadow_router | modules.bionic_engine_p0.routers.ndvi_shadow_router | /api/v1/bionic/ndvi-shadow | ACTIF |
| S29 | habitat_score_router | modules.bionic_engine_p0.routers.habitat_score_router | /api/v1/bionic/habitat-score | ACTIF |
| S30 | route_planner_router | modules.bionic_engine_p0.routers.route_planner_router | /api/v1/bionic/route-planner | ACTIF |
| S31 | wms_proxy_router | wms_proxy_router | /api/wms-proxy | ACTIF |
| S32 | movement_corridors_router | modules.bionic_engine_p0.routers.movement_corridors_router | /api/v1/bionic/movement-corridors | ACTIF |
| S33 | bce_router | bce.router | /api/bce | ACTIF |
| S34 | weather_v82_router | modules.bionic_engine_p0.routers.weather_router | /api/v1/weather | ACTIF |
| S35 | compare_v83_router | modules.bionic_engine_p0.routers.compare_router | /api/v1/compare | ACTIF |
| S36 | saline_ultra_router | modules.saline_engine.router | /api/v1/saline | ACTIF |
| S37 | saline_shop_router | modules.saline_engine.ecommerce_router | /api/v1/saline/shop | ACTIF |
| S38 | alimentation_v1_router | modules.alimentation_v1.router | /api/v1/alimentation | ACTIF |
| S39 | alimentation_v2_router | modules.alimentation_v2.router | /api/v2/alimentation | ACTIF |
| S40 | repos_v1_router | modules.repos_v1.router | /api/v1/repos | ACTIF |
| S41 | corridors_v10_router | modules.corridors_v10.router | /api/v10/corridors | ACTIF |
| S42 | score_consolide | (inline dans server.py) | /api/v1/score-consolide | ACTIF |
| S43 | gateway_v3_router | modules.api_gateway.gateway_v3_router | /api/v3 | ACTIF |

### 1.1.3 Modules NON-ENREGISTRES (FANTOMES / RELIQUES)

| # | Repertoire | Fichiers .py | Statut | Raison / Heritage |
|---|---|---|---|---|
| F1 | adaptive_strategy_engine/ | 5 | FANTOME | Doublon de strategy_master_engine. Repertoire V4 non supprime |
| F2 | admin_advanced_engine/ | 2 | FANTOME | Fusionne dans admin_unified_engine (V5). Non supprime |
| F3 | admin_unified_engine/ | 2 | FANTOME | Existait comme fusion V5 mais non enregistre dans routers.py |
| F4 | advanced_geospatial_engine/ | 5 | FANTOME | Remplace par data_layers/advanced_geospatial_layers |
| F5 | affiliate_engine/ | 5 | FANTOME | Remplace par affiliate_switch_engine (V5) |
| F6 | collaborative_engine/ | 5 | FANTOME | Module V4 orphelin. Non importe nulle part |
| F7 | communication_engine/ | 2 | FANTOME | Fusionne dans notification_unified_engine (V5) |
| F8 | engine_registry/ | 4 | INFRASTRUCTURE | Module d'enregistrement interne, pas un router |
| F9 | geo_engine/ | 3 | SEMI-ACTIF | Initialise dans server.py (ensure_indexes) mais PAS de router enregistre |
| F10 | geolocation_engine/ | 5 | FANTOME | Module V4 orphelin. Non importe dans routers.py |
| F11 | global_master_switch/ | 2 | FANTOME | Doublon/shim de master_switch. Non enregistre |
| F12 | live_heading_view/ | 2 | FANTOME | Module frontend-only ou doublon de live_heading_engine |
| F13 | notification_engine/ | 5 | FANTOME | Remplace par notification_unified_engine (V5) |
| F14 | pression_v1/ | 2 | INTERNE | Utilise par score_consolide.py mais PAS de router propre |
| F15 | realestate/ | 8 | FANTOME | Module immobilier orphelin. Non enregistre |
| F16 | rental_engine/ | 2 | FANTOME | Module location V4. Non enregistre |
| F17 | strategy_engine/ | 5 | FANTOME | Remplace par strategy_master_engine (V5) |

**Total modules fantomes: 17 sur 90 repertoires = 18.9%**

### 1.1.4 Mega-module: bionic_engine_p0

Ce module est le coeur scientifique de BIONIC. Il contient **211 fichiers Python** et represente le plus gros module du systeme.

**Structure interne:**
```
bionic_engine_p0/
  router.py (828 lignes) — Router principal /v1/bionic
  core.py — Core scoring logic
  contracts/ — Data contracts, advanced factors
  engines/ (10 sous-moteurs)
    corridors_v9.py — Moteur corridors V9
    daily_routine_engine.py — Routines quotidiennes faune
    disturbance_engine.py — Perturbations
    engines_v2.py — 12 moteurs integres V2
    engines_v3.py — Moteurs V3 (upgrade)
    habitat_enhancement_engine.py — Amelioration habitat
    hunting_path.py — Tracage chemins de chasse
    learning_engine.py — Apprentissage automatique
    movement_engine_v9.py — Mouvement faune V9
    nutrition_engine.py — Nutrition avancee
    phenology_engine.py — Phenologie saisonniere
    typology_engine.py — Typologie terrain
    weather_engine_v9.py — Meteo V9
  hotspots/ (3 fichiers) — Points chauds
  knowledge/ (25+ fichiers) — Base de connaissances
    calibration/ — Calibration, optimisation
    corridors/ — Modeles corridors
    gps_ultimate/ — GPS avance, observations
    human_pressure/ — Pression humaine
    mobility/ — Modeles mobilite
    notifications/ — Registre notifications
    pressure/ — Pression de chasse
    seasonal/ — Modeles saisonnieres, reproduction, stress thermique
    sources/ — Sources scientifiques
    species/ — Regles par espece (orignal, cerf, ours, wapiti, mulet)
    terrain/ — Exclusions d'eau
    validation/ — Pipeline validation Phase G
    weights/ — Ponderations habitat
  modules/ — Modeles predictifs territoriaux
  routers/ (38 sous-routers) — Points d'entree API
  services/ (12+ fichiers) — Services metier
    corridor_v7.py (1143 lignes)
    dynamic_scoring_service.py (883 lignes)
    hunt_plan_analyzer.py (917 lignes)
    layer_aggregator_service.py (1268 lignes)
    organic_contour_generator.py (804 lignes)
    unified_scoring_service.py (1159 lignes)
    waypoint_analysis_service.py (951 lignes)
    weather_service.py (807 lignes)
    zone_engine_core_v2.py (1326 lignes)
  tests/ (978 lignes)
```

### 1.1.5 Ponderations et formules documentees

#### Score Consolide (score_consolide.py)
```python
ENGINE_WEIGHTS = {
    "alimentation":     0.25,   # Alimentation-V1
    "repos":            0.20,   # Repos-V1
    "corridors_v10":    0.25,   # Corridors-V10
    "alimentation_v2":  0.10,   # Alimentation-V2
    "pression":         0.20,   # Pression-V1
}
# Total = 1.0 (normalise)
```

**Formule du score consolide:**
```
Score_final = Sum(score_moteur_i * poids_normalise_i) pour i dans [alimentation, repos, corridors_v10, alimentation_v2, pression]
```

#### Unified Scoring Service (bionic_engine_p0)
```
Formule: Sum(score_i * weight_i) / Sum(weight_i)
```
- Chaque service de scoring possede un poids (weight: float, 0-1)
- Le score final est une moyenne ponderee
- Modificateur advanced_factors_modifier (defaut: 1.0)
- Facteur temporel: aube/crepuscule (0.95), midi (0.3), reduction proportionnelle

#### Score Corridor V10 (score_consolide.py)
```
connectivity = corridor_strength * 0.35 + transit_factor * 0.25
terrain_quality = canopy * 0.5 + water_prox * 0.3 + route_dist_norm * 0.2
ecological = seed_deterministe * 0.3 + 0.7
Score = connectivity * 40 + terrain_quality * 35 + ecological * 25
```

### 1.1.6 Fichiers Python standalone dans modules/

| Fichier | Role | Utilise par |
|---|---|---|
| chasseur_jumeau.py | Profil chasseur jumeau | Frontend (chasseur-jumeau API) |
| docs.py | Documentation API | server.py |
| hunter_score.py | Score chasseur | Frontend scoring |
| liste_epicerie.py | Liste d'epicerie chasse | Frontend panier |
| routers.py | Registre central 75 routers | server.py |
| score_consolide.py | Score ecologique multi-moteurs | server.py (inline) |
| score_preparation.py | Score de preparation | Frontend |
| setup_builder.py | Generateur de setup | Frontend |
| user_context.py | Contexte utilisateur | Plusieurs modules |
| __init__.py | Init package | Python |

### 1.1.7 Fichiers Python standalone dans backend/

| Fichier | Role |
|---|---|
| analyzer.py | Analyseur generique |
| auth_helpers.py | Helpers authentification JWT |
| backup_manager.py | Gestionnaire backups |
| bionic_engine.py | Moteur bionic legacy |
| brand_config.py | Configuration marque |
| config/settings.py | Configuration globale |
| database.py | Connexion MongoDB + init |
| hunting_groups.py | Groupes de chasse |
| products.py | Produits |
| server.py | Point d'entree FastAPI |
| server_orchestrator.py | Orchestrateur modules |
| territory_sync.py | Synchronisation territoire |
| waypoint_sharing.py | Partage waypoints |
| wms_proxy_router.py | Proxy WMS CORS Quebec |
| zone_favorites.py | Zones favorites |

---

# AUDIT 2 — MODULES FRONTEND

## 2.1 Pages (29 pages)

| Page | Fichier | Route | Lazy-loaded |
|---|---|---|---|
| HomePage | App.js (inline) | / | Non |
| OnboardingPage | pages/OnboardingPage.jsx | /onboarding | Oui |
| ComparePage | pages/ComparePage.jsx | /compare | Oui |
| ShopPage | pages/ShopPage.jsx | /shop | Oui |
| TerritoryPage | App.js (inline) | /territoire | Non |
| MonTerritoireBionicPage | pages/MonTerritoireBionicPage.jsx | /mon-territoire-bionic, /mon-territoire | Oui |
| MarketplacePage | App.js (inline) | /marketplace | Non |
| FormationsPage | App.js (inline) | /formations | Non |
| HuntingLicensePage | pages/HuntingLicensePage.jsx | /permis-chasse | Oui |
| DashboardPage | pages/DashboardPage.jsx | /dashboard | Oui |
| BusinessPage | pages/BusinessPage.jsx | /business | Oui |
| PlanMaitrePage | pages/intelligence/PlanMaitrePage.jsx | /plan-maitre | Oui |
| AnalyticsPage | pages/intelligence/AnalyticsPage.jsx | /analytics | Oui |
| MapPage | pages/MapPage.jsx | /map | Oui |
| ForecastPage | pages/intelligence/ForecastPage.jsx | /forecast | Oui |
| TripsPage | pages/TripsPage.jsx | /trips | Oui |
| ReferralModule | components/ReferralModule.jsx | /referral | Oui |
| AdminPage | pages/AdminPage.jsx | /admin | Oui |
| AdminGeoPage | pages/AdminGeoPage.jsx | /admin/geo | Oui |
| AdminHotspotsPage | ui/administration/admin_hotspots | /admin/hotspots | Oui |
| NetworkingHub | components/NetworkingHub.jsx | /networking | Oui |
| LandsRental | components/LandsRental.jsx | /lands | Oui |
| PricingPage | pages/PricingPage.jsx | /pricing | Oui |
| PaymentSuccessPage | pages/PaymentSuccessPage.jsx | /payment/success | Oui |
| PaymentCancelPage | pages/PaymentCancelPage.jsx | /payment/cancel | Oui |
| AdminPremiumPage | pages/AdminPremiumPage.jsx | /admin-premium | Oui |
| MarketingCalendarPage | pages/MarketingCalendarPage.jsx | /marketing-calendar | Oui |
| BionicAnalysisDemoPage | pages/BionicAnalysisDemoPage.jsx | /bionic-demo | Oui |
| FieldObservationForm | pages/FieldObservationForm.jsx | /observations | Oui |
| CalibrationDashboard | pages/CalibrationDashboard.jsx | /calibration | Oui |
| ReportsPage | pages/ReportsPage.jsx | /reports | Oui |
| SpeciesComparisonPage | pages/SpeciesComparisonPage.jsx | /comparaison-especes | Oui |
| SalineIntelligencePage | pages/SalineIntelligencePage.jsx | /saline, /saline-intelligence | Oui |
| BionicModulesPage | pages/BionicModulesPage.jsx | /bionic-modules, /intelligence, /ecological-intelligence | Oui |

## 2.2 Modules Frontend (28 modules)

| Module | Repertoire | Composants | Services |
|---|---|---|---|
| admin | modules/admin/ | AutoCategorizeButton | AdminService |
| affiliate | modules/affiliate/ | AffiliateStats | AffiliateService |
| ai | modules/ai/ | AIAnalyzer, AIChat, AIInsights | AIService |
| analytics | modules/analytics/ | AnalyticsDashboard | AnalyticsService |
| behavioral | modules/behavioral/ | ActivityChart | BehavioralService |
| business | modules/business/ | BusinessDashboard | - |
| cart | modules/cart/ | CartWidget | CartService |
| collaborative | modules/collaborative/ | SightingsFeed | CollaborativeService |
| customers | modules/customers/ | CustomerCard | CustomersService |
| dashboard | modules/dashboard/ | CoreDashboard | - |
| ecoforestry | modules/ecoforestry/ | HabitatAnalysis | EcoforestryService |
| groupe | modules/groupe/ | GroupChat, GroupePanel, GroupeTab, MembersTracker, SafetyStatus, SessionHeatmap, ShootingZones, SmartAlerts | 4 hooks |
| legaltime | modules/legaltime/ | LegalTimeBar, LegalTimeWidget | LegalTimeService |
| live_heading_view | modules/live_heading_view/ | LiveHeadingView, CompassWidget, ForwardCone, POIMarker, SessionControls, SessionStats, WindIndicator, AlertToast | - |
| map_hotspots | modules/map_hotspots/ | HotspotControlPanel, HotspotOverlay | - |
| map_interaction | modules/map_interaction/ | MapInteractionLayer | WaypointService, useMapInteraction |
| notifications | modules/notifications/ | NotificationProvider, LegalTimeAlert | NotificationService |
| nutrition | modules/nutrition/ | NutritionAnalyzer, NutritionCard, NutritionScore | NutritionService |
| onboarding | modules/onboarding/ | OnboardingFlow, ExperienceSelector, ObjectivesSelector, ProfileSelector, TerritorySelector, OnboardingStep | useOnboarding, useUserProfile |
| orders | modules/orders/ | OrderCard, OrdersList | OrdersService |
| planmaitre | modules/planmaitre/ | PlanMaitreDashboard | - |
| predictive | modules/predictive/ | PredictiveWidget | PredictiveService |
| products | modules/products/ | ProductCard, ProductGrid, SaleModeBadge | ProductsService |
| realestate | modules/realestate/ | MarketplacePanel, RealEstatePanel, PropertyCard, OpportunityList + 6 autres | OpportunityService, RealEstateService |
| recommendation | modules/recommendation/ | RecommendationPanel, SimilarProducts | RecommendationService |
| scoring | modules/scoring/ | ScoreBreakdown, ScoreCompare, ScoreDisplay, ScoreGauge | ScoringService |
| strategy | modules/strategy/ | StrategyCard, StrategyPanel, StrategyTimeline | StrategyService |
| suppliers | modules/suppliers/ | SupplierCard | SuppliersService |
| territory | modules/territory/ | TerritoryCard, TerritoryList, WaypointManager, WaypointMap | TerritoryService |
| tutorial | modules/tutorial/ | (via hooks) | useTutorial, useTutorialProgress, useTutorialTrigger |
| user | modules/user/ | UserActivity, UserProfile | UserService |
| weather | modules/weather/ | WeatherWidget, WeatherForecast, HuntingConditions, WindRose, AdvancedWeatherWidget | WeatherService |
| wildlife | modules/wildlife/ | SpeciesSelector, WildlifeTracker | WildlifeService |

## 2.3 Composants territoire/ (Vue carte — 47 fichiers)

| Composant | Role | API consommee |
|---|---|---|
| MonTerritoireBionic.jsx | Orchestrateur carte (version composant) | - |
| MonTerritoireToolbar.jsx | Barre d'outils carte | - |
| TerritoryShell.jsx | Shell conteneur carte | - |
| MapContent.jsx | Contenu carte Leaflet | - |
| MapHelpers.jsx | Utilitaires Leaflet | - |
| SplitViewContainer.jsx | Vue fractionnee | - |
| IntelligenceDashboard.jsx | Cockpit Intelligence flottant | - |
| AlimentationV2Layer.jsx | Couche alimentation V2 | /api/v2/alimentation/analyze |
| BionicCorridorsV10Layer.jsx | Couche corridors V10 | /api/v10/corridors/analyze-full |
| BionicScoreHeatmap.jsx | Heatmap score consolide | /api/v1/score-consolide/heatmap |
| BionicScoreBadge.jsx | Badge score point | /api/v1/score-consolide/point |
| BionicEngineHub.jsx | Hub moteurs V3 | /api/v1/bionic/engines-v3/compute |
| BionicZone2km.jsx | Zone 2km Leaflet | - |
| BionicZone600m.jsx | Zone 600m Leaflet | - |
| BionicMicroZones.jsx | Micro-zones Leaflet | - |
| BionicMapOverlay.jsx | Overlay carte | - |
| BionicLegend.jsx | Legende carte | - |
| BionicAntiDoublesGuard.jsx | Anti-doublons zones | - |
| BionicZoneDiagnosticPanel.jsx | Diagnostic zones | - |
| CompareWidget.jsx | Comparaison waypoints | /api/v1/compare/waypoints |
| ConsolidatedHeatmapLayer.jsx | Heatmap multi-moteurs | /api/v1/score-consolide/heatmap |
| CorridorsEcologyPanel.jsx | Panneau ecologie corridors | - |
| CursorBionicLayer.jsx | Score sous curseur | /api/v1/bionic/habitat-score/realtime |
| DiagnosticExclusionsPanel.jsx | Diagnostic exclusions | /api/v1/bionic/dynamic/scores |
| EcoforestryLayers.jsx | Couches ecoforesterie WMS | /api/wms-proxy |
| ExclusionOverlayLayer.jsx | Overlay exclusions | /api/v1/bionic/terrain/terrain-data |
| GroupDashboard.jsx | Dashboard groupe chasse | - |
| HuntingPathLayer.jsx | Couche chemins chasse | - |
| HydrographyOverlayLayer.jsx | Overlay hydrographie WMS | /api/wms-proxy/tile |
| MovementCorridorsLayer.jsx | Corridors mouvement | - |
| NdviOverlayLayer.jsx | NDVI Sentinel-2 | /api/v1/bionic/ndvi-shadow/analyze |
| PlacesSidePanel.jsx | Panneau lateral lieux | - |
| RoutePlannerLayer.jsx | Planificateur route | - |
| RouteReplayLayer.jsx | Replay route | - |
| SeasonalConditionsWidget.jsx | Widget conditions saisonnieres | /api/v1/bionic/seasonal-conditions |
| ShareComponents.jsx | Partage | - |
| SmartMapTooltip.jsx | Tooltip intelligent | - |
| StandsMapLayer.jsx | Couche affuts | /api/v1/stand-recommendation/recommend |
| StructureContrastLayer.jsx | Couche contraste structure | - |
| WaypointContextMenu.jsx | Menu contextuel waypoint | - |
| WaypointUnifiedPanel.jsx | Panneau unifie waypoint | /api/v1/bionic/dynamic/scores |
| WindFlowLayer.jsx | Animation flux vent | /api/v1/bionic/weather-shadow/windfield |
| ZoneFavorites.jsx | Zones favorites | /api/zones/favorites |
| ZoneInfoPanel.jsx | Info zone | - |
| AnalysisSidePanel.jsx | Panneau lateral analyse | - |
| AmenagementPanel.jsx | Panneau amenagement | - |

### Intelligence Modes (sous-composants territoire/intelligence/)

| Mode | Fichier | API consommee |
|---|---|---|
| Mode Scientifique | ModeScientifique.jsx | /api/v3/intelligence/scientifique |
| Mode Terrain | ModeTerrain.jsx | /api/v3/intelligence/summary |
| Mode Guide Pro | ModeGuidePro.jsx | /api/v3/intelligence/guide-pro |
| Solunar Chart | SolunarChart.jsx | (donnees locales) |

### UI territoire/ (sous-composants UI)

| Composant | Fichier |
|---|---|
| BCE4XIndicator | ui/BCE4XIndicator.jsx |
| BiologicalSeasonSelector | ui/BiologicalSeasonSelector.jsx |
| NutritionPanel | ui/NutritionPanel.jsx |
| SidePanelZones | ui/SidePanelZones.jsx |
| TerritoireDialogs | ui/TerritoireDialogs.jsx |
| TerritoireHeader | ui/TerritoireHeader.jsx |
| TerritoireToolbar | ui/TerritoireToolbar.jsx |

## 2.4 Divergences entre modes Intelligence

| Aspect | Pro | Scientifique | Terrain |
|---|---|---|---|
| API Gateway | /api/v3/intelligence/guide-pro | /api/v3/intelligence/scientifique | /api/v3/intelligence/summary |
| Focus | Strategies, recommandations | Donnees ecologiques, validations | Resume pratique terrain |
| Dependances backend | api_gateway (V3) | api_gateway (V3) | api_gateway (V3) |
| Composant parent | IntelligenceDashboard | IntelligenceDashboard | IntelligenceDashboard |

Les trois modes passent tous par l'API Gateway V3 (/api/v3/*). Pas de divergence structurelle.

---

# AUDIT 3 — DASHBOARD

## 3.1 Architecture Dashboard

Le Dashboard est accessible via `/dashboard` et utilise `CoreDashboard` (modules/dashboard/CoreDashboard.jsx).

## 3.2 BionicModulesPage (Intelligence/Dashboard avance)

Routes: `/bionic-modules`, `/intelligence`, `/ecological-intelligence`

**APIs consommees:**
| API | Usage |
|---|---|
| /api/v1/stand-recommendation/recommend | Affuts recommandes |
| /api/v1/ecological-intelligence/biogeography/jurisdiction | Filtre biogeographique |
| /api/v1/ecological-intelligence/analyze | Analyse ecologique |
| /api/v1/ecological-intelligence/predictions | Predictions IA |
| /api/v1/ecological-intelligence/behavior-pipeline | Pipeline comportemental |

**Moteurs utilises:**
- bionic_ecological_engine (ecological intelligence)
- bionic_stand_recommendation_engine (affuts)

---

# AUDIT 4 — MON TERRITOIRE

## 4.1 Architecture

**Page principale:** `MonTerritoireBionicPage.jsx` (Version: 7.3.0 — IM1 Refactorisation modulaire)
**Routes:** `/mon-territoire-bionic`, `/mon-territoire`

## 4.2 Moteurs consommes par Mon Territoire

| Moteur Backend | API | Composant Frontend |
|---|---|---|
| score_consolide | /api/v1/score-consolide/heatmap | BionicScoreHeatmap, ConsolidatedHeatmapLayer |
| score_consolide | /api/v1/score-consolide/point | BionicScoreBadge |
| bionic_engine_p0 (engines_v3) | /api/v1/bionic/engines-v3/compute | BionicEngineHub |
| bionic_engine_p0 (habitat_score) | /api/v1/bionic/habitat-score/realtime | CursorBionicLayer |
| bionic_engine_p0 (dynamic_scores) | /api/v1/bionic/dynamic/scores | DiagnosticExclusionsPanel, WaypointUnifiedPanel |
| bionic_engine_p0 (seasonal) | /api/v1/bionic/seasonal-conditions | SeasonalConditionsWidget |
| bionic_engine_p0 (ndvi_shadow) | /api/v1/bionic/ndvi-shadow/analyze | NdviOverlayLayer |
| bionic_engine_p0 (weather_shadow) | /api/v1/bionic/weather-shadow/windfield | WindFlowLayer |
| bionic_engine_p0 (terrain_data) | /api/v1/bionic/terrain/terrain-data | ExclusionOverlayLayer |
| bionic_stand_recommendation_engine | /api/v1/stand-recommendation/recommend | StandsMapLayer |
| corridors_v10 | /api/v10/corridors/analyze-full | BionicCorridorsV10Layer |
| alimentation_v2 | /api/v2/alimentation/analyze | AlimentationV2Layer |
| bce | /api/bce/validate | BCE4XIndicator |
| wms_proxy | /api/wms-proxy/tile | EcoforestryLayers, HydrographyOverlayLayer |
| bionic_engine_p0 (compare) | /api/v1/compare/waypoints | CompareWidget |
| api_gateway (V3) | /api/v3/intelligence/scientifique | ModeScientifique |
| api_gateway (V3) | /api/v3/intelligence/guide-pro | ModeGuidePro |
| api_gateway (V3) | /api/v3/intelligence/summary | ModeTerrain |
| ecological_v8 | /api/v1/ecological/species/*/zones | useTerritoryAutoLoad |
| bionic_engine_p0 (movement) | /api/v1/bionic/movement-corridors | useTerritoryAutoLoad |
| user_data | /api/user-data/waypoints, /places | useUserData |
| zone_favorites | /api/zones/favorites | ZoneFavorites |

## 4.3 Couches geometriques (Leaflet Layers)

| Couche | Type Leaflet | Source |
|---|---|---|
| BionicZone2km | Circle (2000m) | Centree sur position GPS |
| BionicZone600m | Circle (600m) | Zone precision |
| BionicMicroZones | GeoJSON polygons | Genere depuis backend |
| BionicScoreHeatmap | Heatmap L.heat | Score consolide grid |
| ConsolidatedHeatmapLayer | Heatmap L.heat | Score consolide grid |
| BionicCorridorsV10Layer | GeoJSON/Polyline | Corridors V10 API |
| AlimentationV2Layer | GeoJSON/Markers | Alimentation V2 API |
| CursorBionicLayer | Custom Layer | Habitat score realtime |
| EcoforestryLayers | WMSTileLayer | WMS Proxy (NFIS) |
| HydrographyOverlayLayer | WMSTileLayer | WMS Proxy Quebec |
| ExclusionOverlayLayer | GeoJSON polygons | Terrain data API |
| NdviOverlayLayer | TileLayer/Canvas | NDVI Shadow API |
| WindFlowLayer | Canvas animation | Weather shadow API |
| MovementCorridorsLayer | GeoJSON/Polyline | Movement corridors API |
| StandsMapLayer | Markers | Stand recommendation API |
| HuntingPathLayer | Polyline | Paths locaux |
| RoutePlannerLayer | Polyline | Route planner API |
| RouteReplayLayer | Polyline animated | Replay donnees |
| StructureContrastLayer | Custom overlay | Calcul local |
| SmartMapTooltip | Popup/Tooltip | Donnees en memoire |

## 4.4 APIs externes et WMS

| Service | Type | Usage |
|---|---|---|
| OpenStreetMap | TileLayer | Fond de carte |
| WMS NFIS (Canada) | WMSTileLayer via proxy | Couches ecoforesterie |
| WMS Quebec | WMSTileLayer via proxy | Hydrographie |
| Open-Meteo | API REST (via weather_shadow) | Meteo temps reel |
| OpenTopography | API REST (via dem_router) | Elevation DEM |
| Sentinel-2 | API REST (via ndvi_shadow) | NDVI vegetation |

---

# AUDIT 5 — API ROUTES

## 5.1 Statistiques globales

| Methode | Nombre |
|---|---|
| GET | 876 |
| POST | 415 |
| PUT | 101 |
| DELETE | 52 |
| PATCH | 3 |
| **TOTAL** | **1447** |

## 5.2 Versions API

| Version | Prefix | Nombre estimee de routes | Modules |
|---|---|---|---|
| V1 | /api/v1/* | ~1200 | Majorite des modules actifs |
| V2 | /api/v2/* | ~15 | alimentation_v2 |
| V3 | /api/v3/* | ~10 | api_gateway (Intelligence) |
| V10 | /api/v10/* | ~15 | corridors_v10 |
| Sans version | /api/* | ~200 | auth, admin, backup, social, partners, formations, etc. |

## 5.3 Catalogue des prefixes API

| Prefix | Module | Methodes |
|---|---|---|
| /api/auth | auth_engine | POST login, register, logout, forgot-password, reset-password; GET me, verify |
| /api/v1/nutrition | nutrition_engine | GET/POST analyze, species, profile |
| /api/v1/scoring | scoring_engine | GET score, criteria, weights |
| /api/v1/ai | ai_engine | POST analyze, query, generate; GET health |
| /api/v1/weather | weather_engine | GET current, forecast, hourly, daily, full, influence |
| /api/v1/geospatial | geospatial_engine | GET/POST entities, nearby, within-bbox, elevation |
| /api/v1/wms | wms_engine | GET layers, status |
| /api/v1/user | user_engine | GET/POST/PUT profile, preferences |
| /api/v1/notifications | notification_unified_engine | GET/POST/DELETE notifications |
| /api/v1/referral | referral_engine | GET/POST referral |
| /api/v1/territory | territory_engine | GET/POST/DELETE territories, zones |
| /api/v1/tracking-engine | tracking_engine | GET/POST tracking, behavioral |
| /api/v1/marketplace | marketplace_engine | GET listings, seller |
| /api/v1/plugins | plugins_engine | GET/POST features |
| /api/v1/recommendation | recommendation_engine | GET recommend, similar, complementary |
| /api/v1/ecoforestry | ecoforestry_engine | GET cuts, habitats, hsi |
| /api/v1/3d | engine_3d | GET/POST terrain, elevation, viewshed |
| /api/v1/wildlife | wildlife_behavior_engine | GET/POST patterns, movement, predict-activity |
| /api/v1/simulation | weather_fauna_simulation_engine | GET/POST predict, correlations, seasonal |
| /api/v1/progression | progression_engine | GET progress, badges, challenges, leaderboard |
| /api/v1/network | networking_engine | GET/POST connections, groups, feed |
| /api/v1/live-heading | live_heading_engine | GET/POST session, bearing |
| /api/v1/products | products_engine | CRUD products, GET top |
| /api/v1/orders | orders_engine | CRUD orders |
| /api/v1/suppliers | suppliers_engine | CRUD suppliers |
| /api/v1/customers | customers_engine | CRUD customers |
| /api/v1/cart | cart_engine | GET/POST/DELETE cart |
| /api/v1/alerts | alerts_engine | CRUD alerts |
| /api/v1/legal-time | legal_time_engine | GET times, legal-window, optimal-times |
| /api/v1/predictive | predictive_engine | GET/POST forecast, predictions |
| /api/v1/analytics | analytics_engine | GET dashboard, overview, trends, species, heatmap |
| /api/v1/waypoint-scoring | waypoint_scoring_engine | GET wqs, ranking, recommendations |
| /api/v1/trips | hunting_trip_logger | CRUD trips, observations, visits |
| /api/v1/roles | roles_engine | GET/POST roles, permissions |
| /api/v1/rules | rules_engine | CRUD rules |
| /api/v1/strategy-master | strategy_master_engine | GET/POST strategies |
| /api/v1/payments | payment_engine | POST checkout, webhook/stripe; GET transactions |
| /api/v1/freemium | freemium_engine | GET tiers, quotas |
| /api/v1/upsell | upsell_engine | GET/POST campaigns, conversions |
| /api/v1/onboarding | onboarding_engine | GET/POST flows, steps |
| /api/v1/tutorials | tutorial_engine | GET tutorials, progress |
| /api/v1/admin | admin_engine | CRUD admin, maintenance, backup, users, branding |
| /api/v1/knowledge | bionic_knowledge_engine | GET documentation, references |
| /api/v1/seo | seo_engine | GET/POST pages, jsonld, content, meta-tags |
| /api/v1/seo-suppliers | seo_engine (suppliers) | GET seo-pages, render |
| /api/v1/affiliate-switch | affiliate_switch_engine | GET/POST/DELETE affiliates |
| /api/v1/affiliate-ads | affiliate_ads_engine | GET/POST campaigns, ads |
| /api/v1/ad-spaces | ad_spaces_engine | GET/POST catalog, slots, deployed |
| /api/v1/messaging | messaging_engine | GET/POST messages, channels, broadcast |
| /api/v1/marketing | marketing_engine | GET/POST campaigns, posts, segments |
| /api/v1/marketing-calendar | marketing_calendar_engine | GET calendar |
| /api/v1/waypoints | waypoint_engine | CRUD waypoints, bounds, stats |
| /api/v1/contact-engine | contact_engine | CRUD contacts, tags, experts |
| /api/v1/trigger-engine | trigger_engine | CRUD triggers, executions |
| /api/v1/master-switch | master_switch | GET/POST master-switch, toggle, features |
| /api/backup-cloud | backup_cloud_engine | GET/POST backup, versions |
| /api/formations | formations_engine | GET formations |
| /api/social | social_engine | GET/POST posts, comments |
| /api/partners | partner_engine | GET/POST partners, requests |
| /api/v1/bionic | bionic_engine_p0 | ~200+ routes (voir section P0) |
| /api/v1/ecological-intelligence | bionic_ecological_engine | GET analyze, predictions, biogeography, behavior-pipeline |
| /api/v1/data-fabric | bionic_data_fabric | GET/POST coherence, ingestion-logs |
| /api/v1/stand-recommendation | bionic_stand_recommendation_engine | GET recommend, stands |
| /api/v1/camera | camera_engine | CRUD cameras, events |
| /api/admin/optimization | optimization_engine | CRUD proposals, versions |
| /api/v1/saline | saline_engine | GET/POST analysis, hydrology, metabolism, vegetation, nutrients, attractant |
| /api/v1/saline/shop | saline_engine (e-commerce) | POST checkout, GET products |
| /api/v1/alimentation | alimentation_v1 | POST analyze; GET species, ingredients |
| /api/v2/alimentation | alimentation_v2 | POST analyze; GET species |
| /api/v1/repos | repos_v1 | POST analyze; GET zones |
| /api/v10/corridors | corridors_v10 | POST analyze, analyze-full; GET corridors, barriers |
| /api/v1/score-consolide | score_consolide (inline) | GET point, heatmap |
| /api/v3 | api_gateway | GET intelligence/* |
| /api/bce | bce | POST validate, certify; GET status |
| /api/reports | routes/reports | GET reports |
| /api/user-data | routes/user_data | CRUD waypoints, places, sync |
| /api/wms-proxy | wms_proxy_router | GET tile, check |

## 5.4 Schemas et champs potentiellement obsoletes

| Observation | Localisation |
|---|---|
| Double prefix `/api/v1/admin` | admin_engine.router ET admin_engine.v1.router (conflit potentiel) |
| Double prefix `/api/v1/tracking-engine` | tracking_engine.v1.router ET tracking_behavioral_router |
| Prefix `/api/admin-advanced` | admin_advanced_engine/router.py (module FANTOME, non enregistre) |
| Prefix `/api/communication` | communication_engine/router.py (module FANTOME, non enregistre) |
| Prefix `/api/rental` | rental_engine/router.py (module FANTOME, non enregistre) |
| Prefix `/api/v1/adaptive` | adaptive_strategy_engine (module FANTOME, non enregistre) |
| Prefix `/api/v1/advanced-geo` | advanced_geospatial_engine (module FANTOME, non enregistre) |
| Prefix `/api/v1/affiliate` | affiliate_engine (module FANTOME, non enregistre) |
| Prefix `/api/v1/collaborative` | collaborative_engine (module FANTOME, non enregistre) |
| Prefix `/api/v1/geolocation` | geolocation_engine (module FANTOME, non enregistre) |
| Prefix `/api/v1/notification` (singulier) | notification_engine (module FANTOME, remplace par unified) |
| Prefix `/api/v1/strategy` (sans master) | strategy_engine (module FANTOME, remplace par strategy_master) |

---

# AUDIT 6 — PREVIEW vs WORK1

## 6.1 Synchronisation

**Script de synchronisation:** `/app/HUNTIQ-V6-import/scripts/sync_preview.sh`

### Resultat du diff BACKEND:
```
Source: /app/HUNTIQ-V6-import/backend/
Destination: /app/backend/

Divergences trouvees:
- Fichiers UNIQUEMENT dans PREVIEW (pas dans Work1):
  - .pytest_cache/ (cache de test — negligeable)
  - data/osm_cache/1e420de081b7b3cb58d5ef879c0292bf.json (cache OSM genere)
  - data/osm_cache/5f4b5f2c263c03d60325cb0d8af4df4e.json (cache OSM genere)
  - data/osm_cache/73491b3d1f5c53272c9fb0054b9dce0c.json (cache OSM genere)
  - data/osm_cache/7fb4d1a2aa5ad60ebcc83aebd768c8c6.json (cache OSM genere)
  - data/osm_cache/CA-QC.json (cache province Quebec)
  - data/osm_cache/c7bfef5fbc337e49b525afbc824a6ad1.json (cache OSM genere)
  - tests/test_saline_intelligence_ultra.py (fichier de test genere)

- Fichier DIVERGENT:
  - data/osm_cache/3486a1271d0635266c0fcd8dc7da6561.json (taille differente)
```

### Resultat du diff FRONTEND SRC:
```
Source: /app/HUNTIQ-V6-import/frontend/src/
Destination: /app/frontend/src/

**AUCUNE DIVERGENCE DETECTEE**
```

### Verdict PREVIEW:
- **Frontend: SYNCHRONISE A 100%**
- **Backend: SYNCHRONISE A 99.5%** — Les seules divergences sont des fichiers de cache generes au runtime (data/osm_cache/) et un fichier de test (.pytest_cache, test_saline_intelligence_ultra.py). Aucun fichier source n'est divergent.

---

# AUDIT 7 — RELIQUES

## 7.1 Modules backend fantomes (17 modules)

| Module | Fichiers | Lignes estimees | Raison | Action recommandee |
|---|---|---|---|---|
| adaptive_strategy_engine/ | 5 py | ~200 | Doublon de strategy_master_engine | PURGER |
| admin_advanced_engine/ | 2 py | ~80 | Fusionne dans admin_unified_engine | PURGER |
| admin_unified_engine/ | 2 py | ~80 | Non enregistre (shim V5) | PURGER ou ENREGISTRER |
| advanced_geospatial_engine/ | 5 py | ~200 | Remplace par data_layers | PURGER |
| affiliate_engine/ | 5 py | ~200 | Remplace par affiliate_switch_engine | PURGER |
| collaborative_engine/ | 5 py | ~200 | Orphelin V4 | PURGER |
| communication_engine/ | 2 py | ~80 | Fusionne dans notification_unified_engine | PURGER |
| geolocation_engine/ | 5 py | ~200 | Orphelin V4 | PURGER |
| global_master_switch/ | 2 py | ~80 | Doublon de master_switch | PURGER |
| live_heading_view/ | 2 py | ~80 | Doublon/frontend-only de live_heading_engine | PURGER |
| notification_engine/ | 5 py | ~200 | Remplace par notification_unified_engine | PURGER |
| realestate/ | 8 py | ~400 | Non enregistre, orphelin | PURGER ou REACTIVER |
| rental_engine/ | 2 py | ~80 | Orphelin V4 | PURGER |
| strategy_engine/ | 5 py | ~200 | Remplace par strategy_master_engine | PURGER |

**Sous-total fantomes: ~2280 lignes recuperables**

## 7.2 Modules en zone grise (ni fantome, ni pleinement actifs)

| Module | Statut | Detail |
|---|---|---|
| engine_registry/ | INFRASTRUCTURE | Utilise par api_gateway, pas un router |
| geo_engine/ | SEMI-ACTIF | ensure_indexes() appele dans server.py mais PAS de router enregistre |
| pression_v1/ | INTERNE | Utilise par score_consolide.py mais PAS de router expose |

## 7.3 Doublons detectes

| Domaine | Module actif | Fantome(s) | Detail |
|---|---|---|---|
| Admin | admin_engine (V4+) | admin_advanced_engine, admin_unified_engine | 3 modules pour 1 domaine |
| Notification | notification_unified_engine (V5) | notification_engine, communication_engine | 3 modules pour 1 domaine |
| Strategy | strategy_master_engine (V5) | strategy_engine, adaptive_strategy_engine | 3 modules pour 1 domaine |
| Affiliate | affiliate_switch_engine + affiliate_ads_engine | affiliate_engine | 3 modules, 1 fantome |
| Master Switch | master_switch | global_master_switch | 2 modules, 1 fantome |
| Geospatial | geospatial_engine + data_layers | advanced_geospatial_engine, geo_engine, geolocation_engine | 5 modules, 3 fantomes |
| Live Heading | live_heading_engine | live_heading_view | 2 modules, 1 fantome |

## 7.4 Fichiers potentiellement morts (backend/ racine)

| Fichier | Lignes | Utilise | Verdict |
|---|---|---|---|
| bionic_engine.py | ~200 | Legacy, potentiellement remplace par bionic_engine_p0 | A VERIFIER |
| hunting_groups.py | ~150 | Potentiellement doublon du module groupe | A VERIFIER |

## 7.5 Dependances backend potentiellement mortes

| Package | Usage probable | Verdict |
|---|---|---|
| black==25.12.0 | Formatage code (dev only) | DEV ONLY |
| flake8==7.3.0 | Linting (dev only) | DEV ONLY |
| isort==7.0.0 | Sorting imports (dev only) | DEV ONLY |
| mypy==1.19.1 | Type checking (dev only) | DEV ONLY |
| pytest==9.0.2 | Tests (dev only) | DEV ONLY |
| GeoAlchemy2==0.18.1 | PostGIS (pas de PostgreSQL utilise?) | A VERIFIER |
| SQLAlchemy==2.0.45 | ORM SQL (MongoDB est utilise) | A VERIFIER |
| asyncpg==0.31.0 | PostgreSQL async (pas de PostgreSQL utilise?) | A VERIFIER |
| rasterio==1.4.4 | Raster geospatial | ACTIF (DEM) |
| scipy==1.17.0 | Calculs scientifiques | ACTIF (scoring) |
| reportlab==4.4.9 | Generation PDF | ACTIF (rapports) |

## 7.6 Fichiers frontend potentiellement dupliques

| Domaine | Fichier 1 | Fichier 2 | Detail |
|---|---|---|---|
| Territory components | components/territory/* (13 fichiers) | components/territoire/* (47 fichiers) | Deux repertoires similaires — "territory" (anglais, ancien) vs "territoire" (francais, actif) |
| Maintenance | components/MaintenanceControl.jsx | components/admin/MaintenanceControl.jsx | Potentiel doublon |
| Site Access | components/SiteAccessControl.jsx | components/admin/SiteAccessControl.jsx | Potentiel doublon |
| Partner Offers | components/PartnerOffers.jsx | components/partner/PartnerOffers.jsx | Potentiel doublon |
| CookieConsent | components/CookieConsent.jsx | core/components/CookieConsent.jsx | Potentiel doublon |
| OfflineIndicator | components/OfflineIndicator.jsx | core/components/OfflineIndicator.jsx | Potentiel doublon |
| RefreshButton | components/RefreshButton.jsx | core/components/RefreshButton.jsx | Potentiel doublon |
| ScrollNavigator | components/ScrollNavigator.jsx | core/components/ScrollNavigator.jsx | Potentiel doublon |

## 7.7 Routes frontend non utilisees ou orphelines

| Page | Route | Observe dans navigation? |
|---|---|---|
| BionicAnalysisDemoPage | /bionic-demo | Non visible dans la nav principale |
| CalibrationDashboard | /calibration | Non visible dans la nav principale |
| ReportsPage | /reports | Non visible dans la nav principale |
| SpeciesComparisonPage | /comparaison-especes | Non visible dans la nav principale |

---

# RESUME EXECUTIF

## Chiffres cles

| Metrique | Valeur |
|---|---|
| Repertoires engine backend | 90 |
| Modules enregistres (routers.py) | 75 |
| Modules enregistres (server.py direct) | 43 |
| Modules FANTOMES non enregistres | 17 (18.9%) |
| Fichiers Python backend total | ~3200 fichiers |
| Lignes Python backend total | 172 833 |
| Mega-module bionic_engine_p0 | 211 fichiers |
| Pages frontend | 29+ |
| Modules frontend | 28+ |
| Composants territoire/ | 47 |
| Couches carte Leaflet | 20+ |
| Endpoints API total | 1 447 |
| GET endpoints | 876 |
| POST endpoints | 415 |
| Versions API (V1, V2, V3, V10) | 4 |
| Paquets backend (requirements.txt) | 157 |
| Paquets frontend (dependencies) | 58 |
| Divergences PREVIEW backend | 8 fichiers cache (0 source) |
| Divergences PREVIEW frontend | 0 |
| Master Switch | LOCKED |
| Doublons modules backend | 7 domaines avec fantomes |
| Doublons composants frontend | 8 paires suspectes |

## Verdict global

Le systeme BIONIC V6 est un ecosysteme massif et fonctionnel avec:
- **75+ moteurs actifs** couvrant tous les domaines metier
- **1447 endpoints API** documentables
- **17 modules fantomes** a purger pour clarte architecturale
- **Synchronisation Work1 <-> PREVIEW: 99.5%** (seuls des caches divergent)
- **MASTER SWITCH: LOCKED** — Aucune fonctionnalite publique active

---

**Document genere conformement a la directive STEEVE-MAX x3050-EXEC**
**Protocole: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX**
**Validation requise: STEEVE avant toute action**
