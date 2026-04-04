"""Modules Router Integration

Central router integration for all BIONIC HUNT/Chasse modules.
This file is the single point of import for server.py

Version: 4.0.0 - Consolidation V6 (STEEVE-MAX)

Architecture:
- All routers centralized here
- No manual router registration in server.py
- Legacy monolith isolated

Consolidation V6 (STEEVE-MAX):
- Merged: geo_engine → geospatial_engine (logique interne absorbee)
- Merged: affiliate_ads_engine + ad_spaces_engine → ads_engine
- Merged: tutorial_engine + formations_engine → learning_engine
- Deprecated: geo_engine, core/alimentation
- Reclassed: chasseur_jumeau.py → experiments/, liste_epicerie.py → utils/

P0 Cleanup (STEEVE-MAX x1900):
- Removed: admin_unified_engine (fusionne dans admin_engine)
- Removed: admin_advanced_engine (sous-ensemble de admin_engine)
- Removed: collaborative_engine (doublon de networking_engine)
- Removed: adaptive_strategy_engine (doublon de strategy_master_engine)
- Removed: advanced_geospatial_engine (couvert par bionic_engine_p0)
- Removed: geolocation_engine (couvert par geo_engine + bionic_engine_p0)
- Removed: affiliate_engine (remplace par affiliate_switch_engine)
- Removed: rental_engine (stub minimal non utilise)
- Removed: global_master_switch (shim, logique dans master_switch)
- Removed: strategy_engine (fusionne dans strategy_master_engine)
"""

from fastapi import APIRouter
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# ==============================================
# CORE ENGINE ROUTERS (Phase 2)
# P0: strategy_engine removed (fusionne dans strategy_master_engine)
# ==============================================
from modules.nutrition_engine.v1 import router as nutrition_router
from modules.scoring_engine.v1 import router as scoring_router
from modules.ai_engine.v1 import router as ai_router
# BCE-4X PURGE: weather_engine.v1 SUPPRIME — Source unique: engines/weather_v3
from modules.geospatial_engine.v1 import router as geospatial_router
from modules.wms_engine.v1 import router as wms_router

# ==============================================
# BUSINESS ENGINE ROUTERS (Phase 3)
# P0: admin_unified_engine removed (fusionne dans admin_engine)
# ==============================================
from modules.user_engine.v1 import router as user_router
from modules.notification_unified_engine import router as notification_router
from modules.referral_engine.v1 import router as referral_router
from modules.territory_engine.v1 import router as territory_router
from modules.tracking_engine.v1 import router as tracking_router
from modules.marketplace_engine.v1 import router as marketplace_router
from modules.plugins_engine.v1 import router as plugins_router

# ==============================================
# MASTER PLAN ENGINE ROUTERS (Phase 4)
# P0: collaborative_engine removed (doublon de networking_engine)
# P0: adaptive_strategy_engine removed (doublon de strategy_master_engine)
# P0: advanced_geospatial_engine removed (couvert par bionic_engine_p0)
# ==============================================
from modules.recommendation_engine.v1 import router as recommendation_router
from modules.ecoforestry_engine.v1 import router as ecoforestry_router
from modules.engine_3d.v1 import router as engine_3d_router
from modules.wildlife_behavior_engine.v1 import router as wildlife_router
from modules.weather_fauna_simulation_engine.v1 import router as simulation_router
from modules.progression_engine.v1 import router as progression_router
from modules.networking_engine.v1 import router as networking_router

# ==============================================
# DATA LAYER ROUTERS (Phase 5)
# ==============================================
from modules.data_layers.ecoforestry_layers import router as ecoforestry_data_router
from modules.data_layers.behavioral_layers import router as behavioral_data_router
from modules.data_layers.simulation_layers import router as simulation_data_router
from modules.data_layers.layers_3d import router as layers_3d_data_router
from modules.data_layers.advanced_geospatial_layers import router as advanced_geo_data_router

# ==============================================
# SPECIAL MODULES (Phase 6)
# ==============================================
from modules.live_heading_engine import router as live_heading_router

# ==============================================
# DECOUPLED MODULES (Phase 7 - Extracted from server.py)
# P0: affiliate_engine removed (remplace par affiliate_switch_engine)
# ==============================================
from modules.products_engine import router as products_router
from modules.orders_engine import router as orders_router
from modules.suppliers_engine import router as suppliers_router
from modules.customers_engine import router as customers_router
from modules.cart_engine import router as cart_router
from modules.alerts_engine import router as alerts_router

# ==============================================
# PHASE 8 - LEGAL TIME & PREDICTIVE ENGINES
# ==============================================
from modules.legal_time_engine import router as legal_time_router
from modules.predictive_engine import router as predictive_router

# ==============================================
# PHASE P3 - ANALYTICS ENGINE
# ==============================================
from modules.analytics_engine import router as analytics_router

# ==============================================
# PHASE P3 - WAYPOINT SCORING ENGINE
# ==============================================
from modules.waypoint_scoring_engine import router as waypoint_scoring_router

# ==============================================
# PHASE P4 - GEOLOCATION ENGINE
# P0: geolocation_engine removed (couvert par geo_engine + bionic_engine_p0)
# ==============================================

# ==============================================
# PHASE P4 - AUTH ENGINE (Hybrid JWT + Google OAuth)
# ==============================================
from modules.auth_engine import router as auth_router

# ==============================================
# PHASE P4+ - HUNTING TRIP LOGGER (Real Data)
# ==============================================
from modules.hunting_trip_logger import router as hunting_trip_logger_router

# ==============================================
# PHASE P5 - ROLES ENGINE (User Roles & Permissions)
# ==============================================
from modules.roles_engine.v1 import router as roles_router

# ==============================================
# PHASE 1 CAMERAS - CAMERA ENGINE (Photo Ingestion)
# ==============================================
from modules.camera_engine.v1 import camera_router

# ==============================================
# PHASE 9 - PLAN MAÎTRE ENGINES (Strategy Master)
# ==============================================
from modules.rules_engine.router import router as rules_router
from modules.strategy_master_engine.router import router as strategy_master_router

# ==============================================
# PHASE P3 - MONÉTISATION ENGINES (5 modules)
# tutorial_engine → learning_engine (Consolidation V6)
# ==============================================
from modules.payment_engine.router import router as payment_router
from modules.freemium_engine.router import router as freemium_router
from modules.upsell_engine.router import router as upsell_router
from modules.onboarding_engine.router import router as onboarding_router
from modules.tutorial_engine.router import router as tutorial_router
# Consolidated into: learning_engine (tutorial_engine + formations_engine)

# ==============================================
# ADMINISTRATION PREMIUM ENGINE
# ==============================================
from modules.admin_engine.router import router as admin_premium_router

# ==============================================
# BIONIC KNOWLEDGE ENGINE (V5 LEGO)
# ==============================================
from modules.bionic_knowledge_engine.knowledge_router import router as bionic_knowledge_router

# ==============================================
# BIONIC SEO ENGINE (V5 LEGO)
# ==============================================
from modules.seo_engine.seo_router import router as bionic_seo_router

# ==============================================
# SEO SUPPLIERS DATABASE (LISTE FOURNISSEURS ULTIME)
# ==============================================
from modules.seo_engine.seo_suppliers_router import router as seo_suppliers_router

# ==============================================
# AFFILIATE SWITCH ENGINE (PHASE 6+)
# ==============================================
from modules.affiliate_switch_engine.router import router as affiliate_switch_router

# ==============================================
# AFFILIATE AD AUTOMATION ENGINE → ads_engine (Consolidation V6)
# ==============================================
from modules.affiliate_ads_engine.router import router as affiliate_ads_router
# Consolidated into: ads_engine (affiliate_ads_engine + ad_spaces_engine)

# ==============================================
# AD SPACES ENGINE → ads_engine (Consolidation V6)
# ==============================================
from modules.ad_spaces_engine.router import router as ad_spaces_router
# Consolidated into: ads_engine (affiliate_ads_engine + ad_spaces_engine)

# ==============================================
# MESSAGING ENGINE (Communications Bilingues Premium)
# ==============================================
from modules.messaging_engine.router import router as messaging_router

# ==============================================
# GLOBAL MASTER SWITCH
# P0: global_master_switch shim removed — logique dans master_switch/router.py
# ==============================================

# ==============================================
# TRACKING ENGINE V1 - BEHAVIORAL (Events, Funnels, Heatmaps)
# ==============================================
from modules.tracking_engine.v1.router import router as tracking_behavioral_router

# ==============================================
# MARKETING ENGINE V1 - AUTOMATION (Phase 14)
# ==============================================
from modules.marketing_engine.v1.router import router as marketing_automation_router

# ==============================================
# MARKETING CALENDAR ENGINE V2 - 60 DAYS PLANNING
# ==============================================
from modules.marketing_calendar_engine.v2.router import router as marketing_calendar_router

# ==============================================
# WAYPOINT ENGINE V1 - MAP INTERACTION
# ==============================================
from modules.waypoint_engine.v1.router import router as waypoint_interaction_router

# ==============================================
# X300% STRATEGY - CONTACT ENGINE
# ==============================================
from modules.contact_engine.router import router as contact_engine_router

# ==============================================
# X300% STRATEGY - TRIGGER ENGINE
# ==============================================
from modules.trigger_engine.router import router as trigger_engine_router

# ==============================================
# X300% STRATEGY - MASTER SWITCH
# ==============================================
from modules.master_switch.router import router as master_switch_router

# ==============================================
# V5-ULTIME-FUSION - MODULES IMPORTES (V2, V3, BASE)
# P0: rental_engine removed (stub minimal non utilise)
# P0: communication_engine et admin_advanced_engine deja retires en V5
# ==============================================
from modules.backup_cloud_engine.router import router as backup_cloud_router
from modules.formations_engine.router import router as formations_router
# Consolidated into: learning_engine (tutorial_engine + formations_engine)
# x3104: social_engine purge vers /app/legacy/api_obsoletes_x3103/social_engine/
from modules.partner_engine.router import router as partner_router

# ==============================================
# BIONIC NEXT STEP ENGINE (PHASE NSE)
# ==============================================
from routes.bionic_engine_router import router as bionic_engine_router

# ==============================================
# BCE-4X PURGE: BIONIC WEATHER ENGINE SUPPRIME — Source unique: engines/weather_v3
# ==============================================

# ==============================================
# BIONIC SCORING ENGINE (PHASE P1-SCORE)
# ==============================================
from modules.bionic_engine_p0.scoring_router import router as bionic_scoring_router

# ==============================================
# BIONIC HOTSPOT ADMIN ENGINE (COMMANDE ADMIN V3)
# ==============================================
from modules.bionic_engine_p0.hotspots.hotspot_router import router as hotspot_admin_router

# ==============================================
# OPTIMIZATION ENGINE (Phase 5C-R — Restauration V2)
# ==============================================
from modules.optimization_engine.router import router as optimization_router

# ==============================================
# STEEVE-MAX x2000 — ECOSYSTEME UNIFIE (Phase A, B, C)
# ==============================================
from modules.bionic_ecological_engine.router import router as ecological_intelligence_router
from modules.bionic_data_fabric.router import router as data_fabric_router
from modules.bionic_stand_recommendation_engine.router import router as stand_recommendation_router

# ==============================================
# ACCESS ENGINE V6 — ACCES AUX AFFUTS (GOLDEN)
# Pipeline unique: Trail-First Dijkstra + Terrain Grid A*
# ==============================================
from modules.access_engine_v6.router import router as access_engine_v6_router

# ==============================================
# NUTRITION V6 INTERFACE — x6800-A (Wrappers V5)
# ==============================================
from modules.nutrition_v6_interface.router import router as nutrition_v6_router

# ==============================================
# NATIONAL DATA HARVESTER — M1 MAP INTELLIGENCE (x6800-A)
# ==============================================
from modules.national_data_harvester.router import router as national_data_harvester_router

# ==============================================
# POI GRAPH ENGINE — M2 MAP INTELLIGENCE (x6900-M2)
# ==============================================
from modules.poi_graph_engine.router import router as poi_graph_engine_router


# List of all available routers with their metadata
CORE_ROUTERS: List[Tuple[APIRouter, dict]] = [
    # ==========================================
    # Phase P4 - Auth Engine (Priority - First)
    # ==========================================
    (auth_router, {
        "name": "auth_engine",
        "version": "1.0.0",
        "phase": "P4",
        "description": "Hybrid Authentication (JWT + Google OAuth)"
    }),
    
    # ==========================================
    # Phase 2 - Core Engines (7 modules)
    # ==========================================
    (nutrition_router, {
        "name": "nutrition_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "Nutritional analysis for hunting attractants"
    }),
    (scoring_router, {
        "name": "scoring_engine", 
        "version": "1.0.0",
        "phase": 2,
        "description": "Scientific scoring (13 weighted criteria)"
    }),
    (ai_router, {
        "name": "ai_engine",
        "version": "1.0.0",
        "phase": 2, 
        "description": "AI-powered product analysis using GPT-5.2"
    }),
    # BCE-4X PURGE: weather_engine V1 SUPPRIME 2026-03-28
    (geospatial_router, {
        "name": "geospatial_engine",
        "version": "2.0.0",
        "phase": 2,
        "description": "Geospatial analysis + Geo Engine (consolidated V6)"
    }),
    (wms_router, {
        "name": "wms_engine",
        "version": "1.0.0",
        "phase": 2,
        "description": "WMS layer management for hunting maps"
    }),
    # Phase 2 removed: strategy_engine (fusionne dans strategy_master_engine)
    
    # ==========================================
    # Phase 3 - Business Engines (8 modules)
    # ==========================================
    (user_router, {
        "name": "user_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "User management and authentication"
    }),
    # P0 removed: admin_unified_engine (fusionne dans admin_engine)
    (notification_router, {
        "name": "notification_unified_engine",
        "version": "1.0.0",
        "phase": "V5-UNIFIED",
        "description": "Notifications unifiées (V4 notification_engine + BASE communication_engine)"
    }),
    (referral_router, {
        "name": "referral_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Referral and affiliate system"
    }),
    (territory_router, {
        "name": "territory_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Territory and land management"
    }),
    (tracking_router, {
        "name": "tracking_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "GPS tracking and location sharing"
    }),
    (marketplace_router, {
        "name": "marketplace_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "C2C marketplace for hunting equipment"
    }),
    (plugins_router, {
        "name": "plugins_engine",
        "version": "1.0.0",
        "phase": 3,
        "description": "Feature flags and plugin management"
    }),
    
    # ==========================================
    # Phase 4 - Master Plan Engines (10 modules)
    # ==========================================
    (recommendation_router, {
        "name": "recommendation_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Intelligent product and strategy recommendations"
    }),
    # P0 removed: collaborative_engine (doublon de networking_engine)
    (ecoforestry_router, {
        "name": "ecoforestry_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Ecoforestry data and habitat analysis"
    }),
    (engine_3d_router, {
        "name": "engine_3d",
        "version": "1.0.0",
        "phase": 4,
        "description": "3D terrain visualization and analysis"
    }),
    (wildlife_router, {
        "name": "wildlife_behavior_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Wildlife behavior modeling and prediction"
    }),
    (simulation_router, {
        "name": "weather_fauna_simulation_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Weather-wildlife correlation simulation"
    }),
    # P0 removed: adaptive_strategy_engine (doublon de strategy_master_engine)
    # P0 removed: advanced_geospatial_engine (couvert par bionic_engine_p0)
    (progression_router, {
        "name": "progression_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Gamification and user progression"
    }),
    (networking_router, {
        "name": "networking_engine",
        "version": "1.0.0",
        "phase": 4,
        "description": "Hunter social network"
    }),
    
    # ==========================================
    # Phase 5 - Data Layers (5 modules)
    # ==========================================
    (ecoforestry_data_router, {
        "name": "ecoforestry_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for SIEF forest inventory and habitat"
    }),
    (behavioral_data_router, {
        "name": "behavioral_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for wildlife behavior patterns"
    }),
    (simulation_data_router, {
        "name": "simulation_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for weather-fauna simulations"
    }),
    (layers_3d_data_router, {
        "name": "3d_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for terrain elevation and 3D analysis"
    }),
    (advanced_geo_data_router, {
        "name": "advanced_geospatial_data_layer",
        "version": "1.0.0",
        "phase": 5,
        "description": "Data provider for corridors and connectivity"
    }),
    
    # ==========================================
    # Phase 6 - Special Modules (1 module)
    # ==========================================
    (live_heading_router, {
        "name": "live_heading_engine",
        "version": "1.0.0",
        "phase": 6,
        "description": "Immersive live heading view for hunting navigation"
    }),
    
    # ==========================================
    # Phase 7 - Decoupled from server.py (5 modules)
    # ==========================================
    (products_router, {
        "name": "products_engine",
        "version": "1.0.0",
        "phase": 7,
        "description": "Product management (extracted from monolith)"
    }),
    (orders_router, {
        "name": "orders_engine",
        "version": "1.0.0",
        "phase": 7,
        "description": "Order management with hybrid dropshipping/affiliation"
    }),
    (suppliers_router, {
        "name": "suppliers_engine",
        "version": "1.0.0",
        "phase": 7,
        "description": "Supplier/partner management"
    }),
    (customers_router, {
        "name": "customers_engine",
        "version": "1.0.0",
        "phase": 7,
        "description": "Customer management and tracking"
    }),
    (cart_router, {
        "name": "cart_engine",
        "version": "1.0.0",
        "phase": 7,
        "description": "Shopping cart management"
    }),
    # P0 removed: affiliate_engine (remplace par affiliate_switch_engine)
    (alerts_router, {
        "name": "alerts_engine",
        "version": "1.0.0",
        "phase": 7,
        "description": "System alerts and site settings"
    }),
    
    # ==========================================
    # Phase 8 - Legal Time & Predictive Engines (2 modules)
    # ==========================================
    (legal_time_router, {
        "name": "legal_time_engine",
        "version": "1.0.0",
        "phase": 8,
        "description": "Legal hunting hours based on sunrise/sunset (Quebec regulations)"
    }),
    (predictive_router, {
        "name": "predictive_engine",
        "version": "1.0.0",
        "phase": 8,
        "description": "Hunting success predictions and activity forecasts"
    }),
    
    # ==========================================
    # Phase P3 - Analytics Engine (1 module)
    # ==========================================
    (analytics_router, {
        "name": "analytics_engine",
        "version": "1.0.0",
        "phase": "P3",
        "description": "Hunting analytics dashboard with KPIs and statistics"
    }),
    
    # ==========================================
    # Phase P3 - Waypoint Scoring Engine
    # ==========================================
    (waypoint_scoring_router, {
        "name": "waypoint_scoring_engine",
        "version": "1.0.0",
        "phase": "P3",
        "description": "WQS, Success Forecast, and AI recommendations"
    }),
    
    # ==========================================
    # Phase P4 - Geolocation Engine
    # ==========================================
    # P0 removed: geolocation_engine (couvert par geo_engine + bionic_engine_p0)
    
    # ==========================================
    # Phase P4+ - Hunting Trip Logger (Real Data)
    # ==========================================
    (hunting_trip_logger_router, {
        "name": "hunting_trip_logger",
        "version": "1.0.0",
        "phase": "P4+",
        "description": "Real data logging for hunting trips, waypoint visits, and observations"
    }),
    
    # ==========================================
    # Phase P5 - Roles Engine (User Roles & Permissions)
    # ==========================================
    (roles_router, {
        "name": "roles_engine",
        "version": "1.0.0",
        "phase": "P5",
        "description": "Role-based access control (hunter, guide, admin) and permissions management"
    }),
    
    # ==========================================
    # Phase 1 Cameras - Camera Engine (Photo Ingestion)
    # ==========================================
    (camera_router, {
        "name": "camera_engine",
        "version": "1.0.0",
        "phase": "P1-CAM",
        "description": "Camera management, email ingestion, and photo processing with mandatory waypoint"
    }),
    
    # ==========================================
    # V5-ULTIME-FUSION - Modules importés de V2
    # ==========================================
    (backup_cloud_router, {
        "name": "backup_cloud_engine",
        "version": "1.0.0",
        "phase": "V5-V2",
        "description": "Cloud backup (MongoDB Atlas, GCS, ZIP) avec notifications email"
    }),
    (formations_router, {
        "name": "learning_engine_formations",
        "version": "1.0.0",
        "phase": "V5-V2",
        "description": "Learning Engine Formations (consolidated) - FédéCP et BIONIC Academy"
    }),
    
    # ==========================================
    # V5-ULTIME-FUSION - Modules importés de BASE
    # ==========================================
    # x3104: social_engine purge (aucun consommateur frontend/backend)
    # P0 removed: rental_engine (stub minimal non utilise)
    # V5-ULTIME: communication_engine et admin_advanced_engine fusionnés
    # dans notification_unified_engine et admin_unified_engine respectivement
    (partner_router, {
        "name": "partner_engine",
        "version": "1.0.0",
        "phase": "V5-BASE",
        "description": "Gestion partenaires, offres, calendrier événements"
    }),
    
    # ==========================================
    # PHASE 9 - PLAN MAÎTRE ENGINES
    # ==========================================
    (rules_router, {
        "name": "rules_engine",
        "version": "1.0.0",
        "phase": "P9",
        "description": "Moteur de règles de chasse intelligentes Plan Maître"
    }),
    (strategy_master_router, {
        "name": "strategy_master_engine",
        "version": "1.0.0",
        "phase": "P9",
        "description": "Orchestrateur stratégies Plan Maître - intégrations multi-sources"
    }),
    
    # ==========================================
    # PHASE P3 - MONÉTISATION ENGINES (5 modules)
    # ==========================================
    (payment_router, {
        "name": "payment_engine",
        "version": "1.0.0",
        "phase": "P3-MONETISATION",
        "description": "Paiements Stripe - checkout, abonnements, webhooks"
    }),
    (freemium_router, {
        "name": "freemium_engine",
        "version": "1.0.0",
        "phase": "P3-MONETISATION",
        "description": "Gestion quotas, limites et niveaux d'accès freemium"
    }),
    (upsell_router, {
        "name": "upsell_engine",
        "version": "1.0.0",
        "phase": "P3-MONETISATION",
        "description": "Popups premium et déclencheurs comportementaux"
    }),
    (onboarding_router, {
        "name": "onboarding_engine",
        "version": "1.0.0",
        "phase": "P3-MONETISATION",
        "description": "Parcours d'accueil et profilage automatique"
    }),
    (tutorial_router, {
        "name": "learning_engine",
        "version": "1.0.0",
        "phase": "P3-MONETISATION",
        "description": "Learning Engine (consolidated) - Tutoriels + Formations"
    }),
    
    # ==========================================
    # ADMINISTRATION PREMIUM ENGINE
    # ==========================================
    (admin_premium_router, {
        "name": "admin_engine",
        "version": "1.0.0",
        "phase": "ADMIN-PREMIUM",
        "description": "Administration Premium V5-ULTIME - Gestion complète engines, users, logs, settings"
    }),
    
    # ==========================================
    # BIONIC KNOWLEDGE ENGINE (V5 LEGO)
    # ==========================================
    (bionic_knowledge_router, {
        "name": "bionic_knowledge_engine",
        "version": "1.0.0",
        "phase": "KNOWLEDGE-V5",
        "description": "BIONIC Knowledge Layer - Espèces, règles comportementales, modèles saisonniers, validation"
    }),
    
    # ==========================================
    # BIONIC SEO ENGINE (V5 LEGO)
    # ==========================================
    (bionic_seo_router, {
        "name": "seo_engine",
        "version": "1.0.0",
        "phase": "SEO-V5",
        "description": "BIONIC SEO Engine V5 - Clusters, pages, JSON-LD, analytics, automation, génération +300%"
    }),
    
    # ==========================================
    # TRACKING ENGINE V1 - BEHAVIORAL (Phase 7)
    # ==========================================
    (tracking_behavioral_router, {
        "name": "tracking_engine_behavioral",
        "version": "1.0.0",
        "phase": "ANALYTICS-V7",
        "description": "Tracking comportemental - Events, Funnels, Heatmaps, Engagement Metrics"
    }),
    
    # ==========================================
    # MARKETING ENGINE V1 - AUTOMATION (Phase 14)
    # ==========================================
    (marketing_automation_router, {
        "name": "marketing_engine",
        "version": "1.0.0",
        "phase": "MARKETING-V14",
        "description": "Marketing Automation Engine - Campagnes, Posts, Segments, Automations, Triggers comportementaux"
    }),
    
    # ==========================================
    # MARKETING CALENDAR ENGINE V2 - 60 DAYS PLANNING
    # ==========================================
    (marketing_calendar_router, {
        "name": "marketing_calendar_engine",
        "version": "2.0.0",
        "phase": "MARKETING-V2",
        "description": "Calendrier Marketing 60 jours - Génération IA GPT-5.2, Templates Premium, Animations Lottie"
    }),
    
    # ==========================================
    # WAYPOINT ENGINE V1 - MAP INTERACTION
    # ==========================================
    (waypoint_interaction_router, {
        "name": "waypoint_engine",
        "version": "1.0.0",
        "phase": "MAP-INTERACTION",
        "description": "Waypoint Engine - Création waypoints via interaction carte, GPS tracking"
    }),
    
    # ==========================================
    # X300% STRATEGY - CONTACT ENGINE
    # ==========================================
    (contact_engine_router, {
        "name": "contact_engine",
        "version": "1.0.0",
        "phase": "X300-STRATEGY",
        "description": "Contact Engine X300% - Captation visiteurs, ads tracking, social tracking, shadow profiles"
    }),
    
    # ==========================================
    # X300% STRATEGY - TRIGGER ENGINE
    # ==========================================
    (trigger_engine_router, {
        "name": "trigger_engine",
        "version": "1.0.0",
        "phase": "X300-STRATEGY",
        "description": "Marketing Trigger Engine X300% - Triggers automatiques, séquences, promotions"
    }),
    
    # ==========================================
    # X300% STRATEGY - MASTER SWITCH
    # ==========================================
    (master_switch_router, {
        "name": "master_switch",
        "version": "1.0.0",
        "phase": "X300-STRATEGY",
        "description": "Master Switch X300% - Contrôle ON/OFF global de tous les modules X300%"
    }),
    
    # ==========================================
    # SEO SUPPLIERS DATABASE (LISTE FOURNISSEURS ULTIME)
    # ==========================================
    (seo_suppliers_router, {
        "name": "seo_suppliers",
        "version": "1.0.0",
        "phase": "SEO-SUPREME",
        "description": "LISTE FOURNISSEURS ULTIME - Base de données exhaustive fournisseurs mondiaux par catégorie"
    }),
    
    # ==========================================
    # AFFILIATE SWITCH ENGINE (PHASE 6+)
    # ==========================================
    (affiliate_switch_router, {
        "name": "affiliate_switch",
        "version": "1.0.0",
        "phase": "AFFILIATE-ENGINE",
        "description": "Affiliate Switch Engine - Gestion des switches d'affiliation avec activation automatique"
    }),
    
    # ==========================================
    # AFFILIATE AD AUTOMATION → ads_engine (Consolidation V6)
    # ==========================================
    (affiliate_ads_router, {
        "name": "ads_engine",
        "version": "1.0.0",
        "phase": "AD-AUTOMATION",
        "description": "Ads Engine (consolidated) - Affiliate Ads + Ad Spaces"
    }),
    
    # ==========================================
    # AD SPACES ENGINE → ads_engine (Consolidation V6)
    # ==========================================
    (ad_spaces_router, {
        "name": "ads_engine_spaces",
        "version": "1.0.0",
        "phase": "AD-SPACES",
        "description": "Ads Engine Spaces (consolidated) - Emplacements publicitaires BIONIC"
    }),
    
    # ==========================================
    # MESSAGING ENGINE (Communications Bilingues Premium)
    # ==========================================
    (messaging_router, {
        "name": "messaging_engine",
        "version": "1.0.0",
        "phase": "MESSAGING",
        "description": "Messaging Engine - Communications bilingues Premium (FR/EN)"
    }),
    
    # ==========================================
    # GLOBAL MASTER SWITCH (Gros Bouton Rouge)
    # ==========================================
    # P0 removed: global_master_switch (shim — logique dans master_switch)
    
    # ==========================================
    # BIONIC NEXT STEP ENGINE (Phase NSE)
    # ==========================================
    (bionic_engine_router, {
        "name": "bionic_engine",
        "version": "1.0.0",
        "phase": "NSE",
        "description": "🎯 BIONIC Next Step Engine - User Context, Setup Builder, Chasseur Jumeau, Score Préparation"
    }),
    
    # ==========================================
    # BIONIC WEATHER ENGINE (Phase P1-ENV)
    # BCE-4X P1-B2: NEUTRALISE — WEATHER-V3 source unique
    # BCE-4X PURGE: bionic_weather_engine SUPPRIME 2026-03-28
    
    # ==========================================
    # BIONIC SCORING ENGINE (Phase P1-SCORE)
    # ==========================================
    (bionic_scoring_router, {
        "name": "bionic_scoring_engine",
        "version": "1.0.0",
        "phase": "P1-SCORE",
        "description": "BIONIC Scoring Engine - Dynamic Scoring, Behavioral Analysis, Weather Integration"
    }),

    # ==========================================
    # BIONIC HOTSPOT ADMIN ENGINE (COMMANDE ADMIN V3)
    # ==========================================
    (hotspot_admin_router, {
        "name": "hotspot_admin_engine",
        "version": "1.0.0",
        "phase": "ADMIN-V3",
        "description": "BIONIC V6 Hotspot Extraction & Scoring Admin Engine"
    }),

    # ==========================================
    # OPTIMIZATION ENGINE (Phase 5C-R — Restauration V2)
    # ==========================================
    (optimization_router, {
        "name": "optimization_engine",
        "version": "1.0.0",
        "phase": "5C-R",
        "description": "Auto-Optimisation BIONIC - Propositions, Versions, Approbation Admin (restaure depuis V2)"
    }),

    # ==========================================
    # STEEVE-MAX x2000 — ECOSYSTEME UNIFIE
    # ==========================================
    (ecological_intelligence_router, {
        "name": "bionic_ecological_engine",
        "version": "1.0.0",
        "phase": "X2000-ECO",
        "description": "Moteur ecologique unifie — sol, hydro, vegetation, meteo, solunar, predictions, scoring, pipeline comportemental"
    }),
    (data_fabric_router, {
        "name": "bionic_data_fabric",
        "version": "1.0.0",
        "phase": "X2000-FABRIC",
        "description": "Data Fabric — normalisation, interconnexion, historisation, coherence multi-modules"
    }),

    # ==========================================
    # STEEVE-MAX x2280 — AFFUTS PROFESSIONNELS
    # ==========================================
    (stand_recommendation_router, {
        "name": "bionic_stand_recommendation_engine",
        "version": "1.0.0",
        "phase": "X2280-STANDS",
        "description": "Moteur d'affuts professionnels — recommandations, orientation, justification, chemin d'approche"
    }),

    # ==========================================
    # ACCESS ENGINE V6 — GOLDEN (1 pipeline, 1 API)
    # ==========================================
    (access_engine_v6_router, {
        "name": "access_engine_v6",
        "version": "1.0.0",
        "phase": "V6-ACCESS-GOLDEN",
        "description": "Moteur d'acces aux affuts V6 — Trail-First Dijkstra + Terrain Grid A*"
    }),

    # ==========================================
    # NUTRITION V6 INTERFACE — x6800-A (Wrappers V5)
    # ==========================================
    (nutrition_v6_router, {
        "name": "nutrition_v6_interface",
        "version": "6.0.0",
        "phase": "V6-NUTRITION",
        "description": "Interface nutritionnelle V6 unifiee — Encapsulation 13 moteurs V5 (x6800-A)"
    }),

    # ==========================================
    # NATIONAL DATA HARVESTER — M1 (x6800-A)
    # ==========================================
    (national_data_harvester_router, {
        "name": "national_data_harvester",
        "version": "1.0.0",
        "phase": "V6-M1-MAP",
        "description": "National Data Harvester + Legal Boundary Engine (M1 MAP Intelligence)"
    }),

    # ==========================================
    # POI GRAPH ENGINE — M2 (x6900-M2)
    # ==========================================
    (poi_graph_engine_router, {
        "name": "poi_graph_engine",
        "version": "1.0.0",
        "phase": "V6-M2-MAP",
        "description": "POI Graph Engine — Graphe POI, scoring multi-critere, clusters, relations spatiales (M2 MAP Intelligence)"
    }),
]


def get_all_routers() -> List[APIRouter]:
    """Get all router instances"""
    return [router for router, _ in CORE_ROUTERS]


def get_router_info() -> List[dict]:
    """Get information about all available routers"""
    return [
        {
            **meta,
            "prefix": router.prefix
        }
        for router, meta in CORE_ROUTERS
    ]


def get_routers_by_phase(phase: int) -> List[dict]:
    """Get routers for a specific phase"""
    return [
        {**meta, "prefix": router.prefix}
        for router, meta in CORE_ROUTERS
        if meta.get("phase") == phase
    ]


def register_routers(app):
    """
    Register all module routers with a FastAPI app.
    
    Usage in server.py:
        from modules.routers import register_routers
        register_routers(app)
    """
    for router, meta in CORE_ROUTERS:
        app.include_router(router)
        print(f"✓ Registered module: {meta['name']} v{meta['version']} (Phase {meta.get('phase', '?')})")


# Module status endpoint data
MODULE_STATUS = {
    "total_modules": len(CORE_ROUTERS),
    "phase_2_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 2]),
    "phase_3_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 3]),
    "phase_4_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 4]),
    "phase_5_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 5]),
    "phase_6_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 6]),
    "phase_7_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 7]),
    "phase_8_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == 8]),
    "v5_v2_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == "V5-V2"]),
    "v5_base_modules": len([r for r, m in CORE_ROUTERS if m.get("phase") == "V5-BASE"]),
    "modules": [meta["name"] for _, meta in CORE_ROUTERS],
    "status": "operational",
    "architecture_version": "V7-X2000-ECOSYSTEM",
    "fusion_sources": ["V4 (ossature)", "V3 (frontpage)", "V2 (backup/formations)", "BASE (social/admin)", "X2000 (ecosysteme unifie)"]
}
