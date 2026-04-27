"""
BIONIC HUNT/Chasse V5-ULTIME-FUSION Server
==============================

Architecture Modulaire v2.0 - Phase 6 Complete

Ce fichier est le point d'entrée de l'API.
L'orchestration est déléguée à server_orchestrator.py

Modules unifiés V5:
- admin_unified_engine (fusion admin_engine + admin_advanced_engine)
- notification_unified_engine (fusion notification_engine + communication_engine)

Version: 5.0.0
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================
# MODULE IMPORTS
# ==============================================
from modules.routers import CORE_ROUTERS, MODULE_STATUS
from server_orchestrator import create_orchestrator


# ==============================================
# APPLICATION LIFECYCLE
# ==============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    logger.info("=" * 60)
    logger.info("BIONIC HUNT/Chasse V5-ULTIME-FUSION - Server Starting")
    logger.info("=" * 60)
    logger.info("Architecture: Modular v2.0 (Pure Orchestrator)")
    logger.info(f"Total Modules: {MODULE_STATUS['total_modules']}")
    
    # Initialize database
    try:
        from database import init_database
        await init_database()
        logger.info("✓ Database initialized with indexes and seed data")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    
    # Initialize geo engine indexes
    try:
        from modules.geo_engine.v1 import ensure_indexes
        await ensure_indexes()
        logger.info("✓ Geo Engine 2dsphere indexes created")
    except ImportError:
        logger.info("Geo Engine indexes skipped (module not loaded)")
    except Exception as e:
        logger.warning(f"Geo Engine index creation warning: {e}")
    
    # Initialize territory sync
    try:
        from territory_sync import startup_sync
        await startup_sync()
        logger.info("✓ Territory sync initialized")
    except ImportError:
        logger.info("Territory sync not available")
    except Exception as e:
        logger.warning(f"Territory sync startup failed: {e}")
    
    # BCE-4X PERF: Pre-charge du cache eau au demarrage
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import preload_water_cache
        preload_water_cache()
        logger.info("✓ Water cache pre-loaded (BCE-4X Performance)")
    except Exception as e:
        logger.warning(f"Water cache preload warning: {e}")
    
    # Phase 3.2-S BCE-4X: Pre-charge du cache urbain STATIQUE au demarrage
    try:
        from modules.bionic_engine_p0.services.zone_engine_core_v2 import preload_urban_cache
        preload_urban_cache()
        logger.info("✓ Urban cache pre-loaded (Phase 3.2-S SAFE MODE)")
    except Exception as e:
        logger.warning(f"Urban cache preload warning: {e}")
    
    # x7000: Create MongoDB indexes for supplier_submissions
    try:
        from engines.nutrition_intelligence.x7000_supplier_product_engine import ensure_indexes
        await ensure_indexes()
        logger.info("✓ x7000 supplier_submissions indexes created")
    except Exception as e:
        logger.warning(f"x7000 index creation warning: {e}")
    
    # CAM-Omega: Create camera engine indexes
    try:
        from modules.camera_engine.v1.router import ensure_camera_indexes
        from modules.camera_engine.dependencies import get_camera_db
        cam_db = get_camera_db()
        await ensure_camera_indexes(cam_db)
        logger.info("✓ Camera engine indexes created")
    except Exception as e:
        logger.warning(f"Camera engine index creation warning: {e}")
    
    # VIS-A: Create vision engine indexes
    try:
        from modules.vision_engine.v1.router import ensure_vision_indexes
        from modules.camera_engine.dependencies import get_camera_db as get_vis_db
        vis_db = get_vis_db()
        await ensure_vision_indexes(vis_db)
        logger.info("✓ Vision engine indexes created")
    except Exception as e:
        logger.warning(f"Vision engine index creation warning: {e}")
    
    logger.info("=" * 60)
    logger.info("✓ All modules loaded successfully")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Server shutting down...")
    try:
        from territory_sync import shutdown_sync
        await shutdown_sync()
    except Exception:
        pass


# ==============================================
# FASTAPI APPLICATION
# ==============================================
app = FastAPI(
    title="BIONIC HUNT/Chasse V5-ULTIME-FUSION API",
    description="""
## Chasse Bionic™ - API Modulaire Intelligente

BIONIC HUNT/Chasse V5-ULTIME-FUSION est la fusion complète de toutes les versions (V2, V3, V4, BASE) 
en une architecture modulaire unifiée.

### Modules Unifiés V5
- **admin_unified_engine**: Fusion de admin_engine (V4) + admin_advanced_engine (BASE)
- **notification_unified_engine**: Fusion de notification_engine (V4) + communication_engine (BASE)

### Architecture Modulaire (56+ modules)
- **Phase 2**: Core Engines (weather, scoring, ai, nutrition, strategy)
- **Phase 3-6**: Business & Plan Maître Engines
- **Phase 7**: Decoupled Engines
- **V5-BASE**: Modules importés de BIONIC HUNT/Chasse-BASE
- **V5-UNIFIED**: Modules fusionnés et unifiés

### Fonctionnalités Clés
- 🕐 **Legal Time Engine**: Calcul heures légales de chasse
- 🔮 **Predictive Engine**: Prédiction succès de chasse
- 🤖 **AI Engine**: GPT-5.2 pour analyse et recommandations
- 📊 **Analytics Engine**: Statistiques et KPIs de chasse
- 🔔 **Notifications**: Multi-canal (in-app, email, push, SMS)

### Authentification
Certains endpoints nécessitent une authentification via JWT Bearer token.
    """,
    version="5.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=[
        {"name": "Orchestrator", "description": "System status and health"},
        {"name": "Admin Unified Engine", "description": "Administration unifiée V5"},
        {"name": "Notification Unified Engine", "description": "Notifications unifiées V5"},
        {"name": "Analytics Engine", "description": "Statistiques et KPIs de chasse"},
        {"name": "Legal Time Engine", "description": "Calcul des heures légales de chasse"},
        {"name": "Predictive Engine", "description": "Prédiction de succès de chasse"},
        {"name": "AI Engine", "description": "Intelligence artificielle GPT-5.2"},
        {"name": "Weather Engine", "description": "Analyse météorologique"},
        {"name": "Scoring Engine", "description": "Évaluation des produits"},
    ]
)


# ==============================================
# CORS MIDDLEWARE
# ==============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MAP-PERF-Omega: GZip compression for all responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)


# ==============================================
# ORCHESTRATOR REGISTRATION (Phase 6)
# ==============================================
orchestrator = create_orchestrator(app)

# 1. Register orchestrator endpoints (health, status, modules)
orchestrator.finalize()

# 2. Register core modular routers
orchestrator.register_core_routers(CORE_ROUTERS)

# 3. Register special routers (root-level)
orchestrator.register_special_routers()

# 4. Register legacy router (backward compatibility)
orchestrator.register_legacy_router()

# 5. Register BIONIC Engine P0 router (Phase G)
try:
    from modules.bionic_engine_p0.router import router as bionic_p0_router
    app.include_router(bionic_p0_router, prefix="/api")
    logger.info("✓ BIONIC Engine P0 registered (/api/v1/bionic)")
except ImportError as e:
    logger.warning(f"BIONIC Engine P0 not loaded: {e}")
except Exception as e:
    logger.error(f"BIONIC Engine P0 registration failed: {e}")

# PURGE-V6-PHASE-B: Organic Zones V2 DEPRECATED (V8 Bundle terrain-aware)
# try:
#     from modules.bionic_engine_p0.routers.organic_zones_router import router as organic_zones_router
#     app.include_router(organic_zones_router)
# except Exception as e:
#     pass

# 6b. Register Spatial Clipping router (BIONIC V6 GOLDEN INVARIANT)
try:
    from modules.bionic_engine_p0.routers.spatial_clipping_router import router as spatial_clipping_router
    app.include_router(spatial_clipping_router)
    logger.info("✓ Spatial Clipping registered (/api/v1/bionic/clipped-zones, /api/v1/bionic/snapshot)")
except Exception as e:
    logger.warning(f"Spatial Clipping not loaded: {e}")


# 7. Register Reports router
try:
    from routes.reports import router as reports_router
    app.include_router(reports_router)
    logger.info("✓ Reports router registered (/api/reports)")
except Exception as e:
    logger.warning(f"Reports router not loaded: {e}")

# 7b. Register User Data router (Waypoints & Places — P0 persistence)
try:
    from routes.user_data import router as user_data_router
    app.include_router(user_data_router)
    logger.info("✓ User Data router registered (/api/user-data)")
except Exception as e:
    logger.warning(f"User Data router not loaded: {e}")

# 8. Register Seasonal Conditions router (PHASE E — Module isolé)
try:
    from modules.bionic_engine_p0.routers.seasonal_conditions_router import router as seasonal_router
    app.include_router(seasonal_router)
    logger.info("✓ Seasonal Conditions registered (/api/v1/bionic/seasonal-conditions)")
except Exception as e:
    logger.warning(f"Seasonal Conditions not loaded: {e}")

# STEVE-MAX: Register Hunting Path & Amenagement router
try:
    from modules.bionic_engine_p0.routers.hunting_path_router import router as hunting_path_router
    app.include_router(hunting_path_router, prefix="/api")
    logger.info("✓ Hunting Path Engine registered (/api/v1/bionic/hunting-path, /api/v1/bionic/amenagement-report)")
except Exception as e:
    logger.warning(f"Hunting Path Engine not loaded: {e}")

# STEVE-MAX: Register BIONIC Engines V2 router
try:
    from modules.bionic_engine_p0.routers.engines_v2_router import router as engines_v2_router
    app.include_router(engines_v2_router, prefix="/api")

    from modules.bionic_engine_p0.routers.engines_v3_router import router as engines_v3_router
    app.include_router(engines_v3_router, prefix="/api")
    logger.info("✓ BIONIC Engines V2 registered (12 engines)")
except Exception as e:
    logger.warning(f"Engines V2 not loaded: {e}")


# 9. Register SSE Engine router (Phase Optimisation #1)
try:
    from modules.bionic_engine_p0.routers.sse_router import router as sse_router
    app.include_router(sse_router)
    logger.info("✓ SSE Engine registered (/api/v1/bionic/sse)")
except Exception as e:
    logger.warning(f"SSE Engine not loaded: {e}")

# 10. Register OSG Engine router (Phase Optimisation #2)
try:
    from modules.bionic_engine_p0.routers.osg_router import router as osg_router
    app.include_router(osg_router)
    logger.info("✓ OSG Engine registered (/api/v1/bionic/osg)")
except Exception as e:
    logger.warning(f"OSG Engine not loaded: {e}")

# 11. Register CME Engine router (Phase Optimisation #3)
try:
    from modules.bionic_engine_p0.routers.cme_router import router as cme_router
    app.include_router(cme_router)
    logger.info("✓ CME Engine registered (/api/v1/bionic/cme)")
except Exception as e:
    logger.warning(f"CME Engine not loaded: {e}")

# 12. Register WSE/WIV Engine router (Phase Optimisation #4)
try:
    from modules.bionic_engine_p0.routers.wse_wiv_router import router as wse_wiv_router
    app.include_router(wse_wiv_router)
    logger.info("✓ WSE/WIV Engine registered (/api/v1/bionic/wse-wiv)")
except Exception as e:
    logger.warning(f"WSE/WIV Engine not loaded: {e}")

# BCE-4X: Weather Engine v3 (enrichi, nowcasting, scoring multi-criteres)
try:
    from engines.weather_v3.router import router as weather_v3_router
    app.include_router(weather_v3_router)
    logger.info("✓ Weather Engine v3 registered (/api/v3/weather)")
except Exception as e:
    logger.warning(f"Weather Engine v3 not loaded: {e}")

# BCE-4X P0: Hunt Orchestrator Engine (vent/odeurs, acces, choix affuts, orchestration)
try:
    from engines.hunt_orchestrator.router import router as hunt_orchestrator_router
    app.include_router(hunt_orchestrator_router)
    logger.info("✓ Hunt Orchestrator Engine registered (/api/v1/hunt)")
except Exception as e:
    logger.warning(f"Hunt Orchestrator Engine not loaded: {e}")

# BCE-4X BLOC 1: Corridor Unified Engine (fusion corridors OSM + BDRE)
# PURGE-V6-PHASE-B: Corridor Unified DEPRECATED (V8 corridors terrain-aware)
# try:
#     from engines.corridor_unified.router import router as corridor_unified_router
#     app.include_router(corridor_unified_router)
# except Exception as e:
#     pass

# PURGE-V6-ANTI-DUPLICATION-A-Omega: V6 Relocalisation Router DEPRECATED
# Relocalisation desormais geree par /api/v8/map/relocalisation (phase_a_engines.py)
# try:
#     from engines.relocation.router import router as relocation_router
#     app.include_router(relocation_router)
# except Exception as e:
#     pass





# BCE-4X: SUPRA Advanced Engines (pertinence, risque, recommandation, correlation)
try:
    from engines.supra_advanced.router import router as supra_advanced_router
    app.include_router(supra_advanced_router)
    logger.info("✓ SUPRA Advanced Engines registered (/api/v6/supra/advanced)")
except Exception as e:
    logger.warning(f"SUPRA Advanced Engines not loaded: {e}")


# 13. Register VFE Engine router (Phase Optimisation #5)
try:
    from modules.bionic_engine_p0.routers.vfe_router import router as vfe_router
    app.include_router(vfe_router)
    logger.info("✓ VFE Engine registered (/api/v1/bionic/vfe)")
except Exception as e:
    logger.warning(f"VFE Engine not loaded: {e}")

# 14. Register SSVL Engine router (Phase Optimisation #6)
try:
    from modules.bionic_engine_p0.routers.ssvl_router import router as ssvl_router
    app.include_router(ssvl_router)
    logger.info("✓ SSVL Engine registered (/api/v1/bionic/ssvl)")
except Exception as e:
    logger.warning(f"SSVL Engine not loaded: {e}")

# 15. Register TCVE Engine router (Phase Optimisation #7)
try:
    from modules.bionic_engine_p0.routers.tcve_router import router as tcve_router
    app.include_router(tcve_router)
    logger.info("✓ TCVE Engine registered (/api/v1/bionic/tcve)")
except Exception as e:
    logger.warning(f"TCVE Engine not loaded: {e}")

# 16. Register PME Engine router (Phase Optimisation #8)
try:
    from modules.bionic_engine_p0.routers.pme_router import router as pme_router
    app.include_router(pme_router)
    logger.info("✓ PME Engine registered (/api/v1/bionic/pme)")
except Exception as e:
    logger.warning(f"PME Engine not loaded: {e}")

# 17. Register BMPE Engine router (Phase Optimisation #9)
try:
    from modules.bionic_engine_p0.routers.bmpe_router import router as bmpe_router
    app.include_router(bmpe_router)
    logger.info("✓ BMPE Engine registered (/api/v1/bionic/bmpe)")
except Exception as e:
    logger.warning(f"BMPE Engine not loaded: {e}")

# 18. Register TFE Engine router (Phase Optimisation #10)
try:
    from modules.bionic_engine_p0.routers.tfe_router import router as tfe_router
    app.include_router(tfe_router)
    logger.info("✓ TFE Engine registered (/api/v1/bionic/tfe)")
except Exception as e:
    logger.warning(f"TFE Engine not loaded: {e}")

# 19. Register Pipeline router (Phase G — Full Analysis & Metrics)
try:
    from modules.bionic_engine_p0.routers.pipeline_router import router as pipeline_router
    app.include_router(pipeline_router)
    logger.info("✓ Pipeline Engine registered (/api/v1/bionic/pipeline)")
except Exception as e:
    logger.warning(f"Pipeline Engine not loaded: {e}")

# 20. Register API Keys Status router (Phase G+ — System Healthcheck)
try:
    from modules.bionic_engine_p0.routers.api_keys_router import router as api_keys_router
    app.include_router(api_keys_router)
    logger.info("✓ API Keys Status registered (/api/v1/system/api-keys)")
except Exception as e:
    logger.warning(f"API Keys Status not loaded: {e}")

# 21. Register ML Engine router (Phase H — Behavioral Prediction)
try:
    from modules.bionic_engine_p0.routers.ml_router import router as ml_router
    app.include_router(ml_router)
    logger.info("✓ ML Engine registered (/api/v1/bionic/ml)")
except Exception as e:
    logger.warning(f"ML Engine not loaded: {e}")

# 21b. Register Ecological V8 router (Base écologique complète)
try:
    from routes.ecological_router_v8 import router as ecological_v8_router
    app.include_router(ecological_v8_router)
    logger.info("✓ Ecological V8 registered (/api/v1/ecological)")
except Exception as e:
    logger.warning(f"Ecological V8 not loaded: {e}")

# 22. Register DEM Engine router (Real Data — OpenTopography)
try:
    from modules.bionic_engine_p0.routers.dem_router import router as dem_router
    app.include_router(dem_router)
    logger.info("✓ DEM Engine registered (/api/v1/bionic/dem)")
except Exception as e:
    logger.warning(f"DEM Engine not loaded: {e}")

# 23. BCE-4X PURGE: DEM Shadow DESACTIVE (STEEVE-MAX directive)
# try:
#     from modules.bionic_engine_p0.routers.dem_shadow_router import router as dem_shadow_router
#     app.include_router(dem_shadow_router)
#     logger.info("✓ DEM Shadow registered (/api/v1/bionic/dem-shadow)")
# except Exception as e:
#     logger.warning(f"DEM Shadow not loaded: {e}")
logger.info("✗ DEM Shadow DESACTIVE — BCE-4X PURGE")

# BCE-4X PURGE COMPLETE: Weather Shadow, Weather V8.2 — Fichiers supprimes 2026-03-28
logger.info("✗ Weather Shadow PURGE — Fichier supprime")

# 25. BCE-4X PURGE: Full Shadow Comparison DESACTIVE (STEEVE-MAX directive)
# try:
#     from modules.bionic_engine_p0.routers.full_comparison_router import router as full_comparison_router
#     app.include_router(full_comparison_router)
#     logger.info("✓ Full Shadow Comparison registered (/api/v1/bionic/shadow)")
# except Exception as e:
#     logger.warning(f"Full Shadow Comparison not loaded: {e}")
logger.info("✗ Full Shadow Comparison DESACTIVE — BCE-4X PURGE")

# 26. BCE-4X PURGE: NDVI Shadow DESACTIVE (STEEVE-MAX directive)
# try:
#     from modules.bionic_engine_p0.routers.ndvi_shadow_router import router as ndvi_shadow_router
#     app.include_router(ndvi_shadow_router)
#     logger.info("✓ NDVI Shadow registered (/api/v1/bionic/ndvi-shadow)")
# except Exception as e:
#     logger.warning(f"NDVI Shadow not loaded: {e}")
logger.info("✗ NDVI Shadow DESACTIVE — BCE-4X PURGE")

# 27. Register Habitat Score router (Real-time cursor scoring)
try:
    from modules.bionic_engine_p0.routers.habitat_score_router import router as habitat_score_router
    app.include_router(habitat_score_router)
    logger.info("✓ Habitat Score registered (/api/v1/bionic/habitat-score)")
except Exception as e:
    logger.warning(f"Habitat Score not loaded: {e}")

# 28. Register Route Planner router (Tactical route optimization)
try:
    from modules.bionic_engine_p0.routers.route_planner_router import router as route_planner_router
    app.include_router(route_planner_router)
    logger.info("✓ Route Planner registered (/api/v1/bionic/route-planner)")
except Exception as e:
    logger.warning(f"Route Planner not loaded: {e}")

# 29. Register WMS Proxy router (CORS proxy for Quebec WMS services)
try:
    from wms_proxy_router import router as wms_proxy_router
    app.include_router(wms_proxy_router)
    logger.info("✓ WMS Proxy registered (/api/wms-proxy)")
except Exception as e:
    logger.warning(f"WMS Proxy not loaded: {e}")

# PURGE-V6-PHASE-B: Movement Corridors DEPRECATED (V8 corridors terrain-aware)
# try:
#     from modules.bionic_engine_p0.routers.movement_corridors_router import router as movement_corridors_router
#     app.include_router(movement_corridors_router)
# except Exception as e:
#     pass

# 31. Register BIONIC Compliance Engine (BCE)
try:
    from bce.router import router as bce_router
    app.include_router(bce_router)
    logger.info("✓ BCE registered (/api/bce/validate, /api/bce/status, /api/bce/certify)")
except Exception as e:
    logger.warning(f"BCE not loaded: {e}")

logger.info("✗ Weather V8.2 PURGE — Fichier supprime — Source unique: /api/v3/weather/*")

# 33. Register Compare V8.3 Router
try:
    from modules.bionic_engine_p0.routers.compare_router import router as compare_v83_router
    app.include_router(compare_v83_router)
    logger.info("✓ Compare V8.3 registered (/api/v1/compare/waypoints)")
except Exception as e:
    logger.warning(f"Compare V8.3 not loaded: {e}")



# ═══ ×5000 NUTRITION INTELLIGENCE SUPRA — 9 moteurs (STEEVE-MAX x5000) ═══
try:
    from engines.nutrition_intelligence.router import router as nutrition_intel_router
    app.include_router(nutrition_intel_router)
    logger.info("✓ NUTRITION INTELLIGENCE SUPRA registered (/api/v6/nutrition-intelligence) — x5100-x5900")
except Exception as e:
    logger.warning(f"NUTRITION INTELLIGENCE SUPRA not loaded: {e}")

# ═══ SALINE INTELLIGENCE ULTRA — 7 moteurs scientifiques (STEEVE-MAX x1000) ═══
try:
    from modules.saline_engine.router import router as saline_ultra_router
    app.include_router(saline_ultra_router)
    logger.info("✓ SALINE INTELLIGENCE ULTRA registered (/api/v1/saline) — 7 engines")
except Exception as e:
    logger.warning(f"SALINE INTELLIGENCE ULTRA not loaded: {e}")

# ═══ SALINE INTELLIGENCE ULTRA — E-Commerce (Stripe) ═══
try:
    from modules.saline_engine.ecommerce_router import router as saline_shop_router
    app.include_router(saline_shop_router)
    logger.info("✓ SALINE E-COMMERCE registered (/api/v1/saline/shop) — Stripe")
except Exception as e:
    logger.warning(f"SALINE E-COMMERCE not loaded: {e}")

# ═══ ALIMENTATION-V1 — Moteur alimentaire scientifique multi-especes ═══
try:
    from core.scoring_pipeline.alimentation_v1.router import router as alimentation_v1_router
    app.include_router(alimentation_v1_router)
    logger.info("✓ ALIMENTATION-V1 registered (/api/v1/alimentation)")

    from core.scoring_pipeline.alimentation_v2.router import router as alimentation_v2_router
    app.include_router(alimentation_v2_router)
    logger.info("✓ ALIMENTATION-V2 registered (/api/v2/alimentation)")

    # BCE-4X P0-X: SALINES V4 — Moteur terrain-centre SUPRA valide
    from core.scoring_pipeline.alimentation_v2.router import router_v4 as alimentation_v4_router
    app.include_router(alimentation_v4_router)
    logger.info("✓ ALIMENTATION-V4 registered (/api/v4/alimentation)")
except Exception as e:
    logger.warning(f"ALIMENTATION-V1 not loaded: {e}")

# ═══ REPOS-V1 — Moteur zones de repos scientifique multi-especes ═══
try:
    from core.scoring_pipeline.repos_v1.router import router as repos_v1_router
    app.include_router(repos_v1_router)
    logger.info("✓ REPOS-V1 registered (/api/v1/repos)")
except Exception as e:
    logger.warning(f"REPOS-V1 not loaded: {e}")

# ═══ CORRIDORS-V10 — DELETE-LEGACY-V6: V6 router SUPPRIME ═══
# Remplace par SPATIAL-ENGINE-V7 /api/v7/spatial/analyze-full
# PURGE-V6-PHASE-B: Corridors V10 DEPRECATED (V8 corridors terrain-aware)
# try:
#     from core.scoring_pipeline.corridors_v10.router import router as corridors_v10_router
#     app.include_router(corridors_v10_router)
# except Exception as e:
#     pass


# ═══ SCORE CONSOLIDÉ V6 — SUPPRIME (DELETE-LEGACY-V6-Omega) ═══
# Remplace par SPATIAL-ENGINE-V7 /api/v7/spatial/heatmap
# Endpoints V6 /api/v1/score-consolide/* retires le 2026-04-15
logger.info("✓ SCORE-CONSOLIDE V6: SUPPRIME — remplace par SPATIAL-ENGINE-V7")


# ═══ ENGINE REGISTRY V3 — API Gateway auto-adaptative ═══
try:
    from modules.api_gateway import gateway_v3_router
    app.include_router(gateway_v3_router)
    logger.info("✓ API-GATEWAY-V3: Routeur unifié /api/v3/* enregistré")
except Exception as e:
    logger.warning(f"API-GATEWAY-V3 not loaded: {e}")


# ═══ BSAA — BIONIC Social Ads Automation (x4500-ULTRA) ═══
try:
    from modules.bsaa.router import router as bsaa_router
    app.include_router(bsaa_router)
    logger.info("✓ BSAA: BIONIC Social Ads Automation active (/api/bsaa/*)")
except Exception as e:
    logger.warning(f"BSAA not loaded: {e}")

# ═══ ACCESS CLARITY ENGINE V7 — Moteur de guidance optimale (BCE-4X) ═══
try:
    from modules.access_clarity_engine_v7.router import router as clarity_v7_router
    app.include_router(clarity_v7_router)
    logger.info("✓ ACCESS CLARITY V7 registered (/api/v7/clarity)")
except Exception as e:
    logger.warning(f"ACCESS CLARITY V7 not loaded: {e}")

# ═══ SHARE ENGINE — Module PARTAGER BCE-4X GOLDEN V6+ ═══
try:
    from modules.share_engine.router import router as share_router
    app.include_router(share_router)
    logger.info("✓ SHARE ENGINE registered (/api/share)")
except Exception as e:
    logger.warning(f"SHARE ENGINE not loaded: {e}")

# ═══ ULTRA-MAX++ FIREWALL — Geo-fencing Urbain BCE-4X Phase C ═══
try:
    from modules.ultra_max_firewall.router import router as firewall_router
    app.include_router(firewall_router)
    logger.info("✓ ULTRA-MAX++ FIREWALL registered (/api/firewall)")
except Exception as e:
    logger.warning(f"ULTRA-MAX++ FIREWALL not loaded: {e}")

# ═══ SALINES ULTIME ENGINE — FROZEN (PURGE-V6 Phase B) ═══
# PURGE-V6-PHASE-B: Salines Ultime DEPRECATED (V8 Phase A salines)
# try:
#     from modules.salines_ultime_engine.router import router as salines_ultime_router
#     app.include_router(salines_ultime_router)
# except Exception as e:
#     pass

# SOIL ENGINE — BCE-4X GOLDEN | Classification pedologique GPS
try:
    from modules.soil_engine.router import router as soil_router
    app.include_router(soil_router)
    logger.info("✓ SOIL ENGINE registered (/api/v1/soil)")
except Exception as e:
    logger.warning(f"SOIL ENGINE not loaded: {e}")

# GUIDE PRO ENGINE — BIONIC OS V8.5 | Phase E-1 | Chasse guidee 100%
try:
    from modules.guide_pro_engine.router import router as guide_pro_router
    app.include_router(guide_pro_router)
    logger.info("✓ GUIDE PRO ENGINE registered (/api/v1/guide-pro)")
except Exception as e:
    logger.warning(f"GUIDE PRO ENGINE not loaded: {e}")

# BDRE — BIONIC Data Reliability Engine | BCE-4X GOLDEN V6+ | Phase 1
try:
    from engines.bdre.router import router as bdre_router
    app.include_router(bdre_router)
    logger.info("✓ BDRE registered (/api/v1/bdre) — 8 endpoints")
except Exception as e:
    logger.warning(f"BDRE not loaded: {e}")

# SPECIES ENGINE K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
try:
    from modules.species_engine.router import router as species_engine_router
    app.include_router(species_engine_router)
    logger.info("✓ Species Engine K3 registered (/api/v6/species-engine) — 12 endpoints")
except Exception as e:
    logger.warning(f"Species Engine K3 not loaded: {e}")

# CARTE-2027-REBUILD-Omega — Engine cartographique terrain V7
try:
    from modules.carte2027_engine.router import router as carte2027_router
    app.include_router(carte2027_router)
    logger.info("✓ Carte 2027 Engine registered (/api/v1/carte2027) — 5 endpoints")
except Exception as e:
    logger.warning(f"Carte 2027 Engine not loaded: {e}")

# NUTRITION-ENGINE-V7 — Moteur central nutritionnel institutionnel
try:
    from modules.nutrition_engine_v7.router import router as nutrition_v7_router
    app.include_router(nutrition_v7_router)
    logger.info("✓ NUTRITION-ENGINE-V7 registered (/api/v7/nutrition) — 7 endpoints")
except Exception as e:
    logger.warning(f"Nutrition Engine V7 not loaded: {e}")

# SPATIAL-ENGINE-V7 — Moteur geospatial central V7
try:
    from engines.spatial_engine_v7.router import router as spatial_v7_router
    app.include_router(spatial_v7_router)
    logger.info("✓ SPATIAL-ENGINE-V7 registered (/api/v7/spatial) — 6 endpoints")
except Exception as e:
    logger.warning(f"Spatial Engine V7 not loaded: {e}")

# SUPRA-ENGINE-V7 — Moteur decisionnel central V7
try:
    from engines.supra_engine_v7.router import router as supra_v7_router
    app.include_router(supra_v7_router)
    logger.info("✓ SUPRA-ENGINE-V7 registered (/api/v7/supra) — 6 endpoints")
except Exception as e:
    logger.warning(f"Supra Engine V7 not loaded: {e}")

# CANADA-V7.2 — Module national pancanadien
try:
    from modules.canada_v72.router import router as canada_v72_router
    app.include_router(canada_v72_router)
    logger.info("✓ CANADA-V7.2 registered (/api/v7/canada) — 6 endpoints | 13 provinces | 16 écozones")
except Exception as e:
    logger.warning(f"Canada V7.2 not loaded: {e}")

# V8-NATIONAL — Moteurs nationaux V8 pancanadiens
try:
    from engines.v8_national.router import router as v8_national_router
    app.include_router(v8_national_router)
    logger.info("✓ V8-NATIONAL registered (/api/v8/national) — 5 endpoints | 9 biomes | 6 regimes | 8 especes")
except Exception as e:
    logger.warning(f"V8 National not loaded: {e}")

# EXCLUSION-ENGINE-V8 — Moteur centralise d'exclusion BCE-4X
try:
    from engines.v8_national.exclusion_engine import router as exclusion_v8_router
    app.include_router(exclusion_v8_router)
    logger.info("✓ EXCLUSION-ENGINE-V8 registered (/api/v8/exclusion) — 22 criteres | 24 zones urbaines | 10 zones legales | 4 militaires | 4 aeroports")
except Exception as e:
    logger.warning(f"Exclusion Engine V8 not loaded: {e}")

# V8-P1 — Pipelines donnees reelles (LiDAR WCS + IRDA Pedologie)
try:
    from engines.v8_national.p1_pipelines import router as p1_router
    app.include_router(p1_router)
    logger.info("✓ V8-P1 PIPELINES registered (/api/v8/p1) — LiDAR WCS + IRDA Pedologie (STUB mode)")
except Exception as e:
    logger.warning(f"V8 P1 Pipelines not loaded: {e}")

# V8-GOVERNANCE — Master Switch Admin Premium
try:
    from engines.v8_national.governance import router as governance_router
    app.include_router(governance_router)
    logger.info("✓ V8-GOVERNANCE registered (/api/v8/governance) — Master Switch COMMANDANT_STEEVE_MAX")
except Exception as e:
    logger.warning(f"V8 Governance not loaded: {e}")

# V8-MAP-BUNDLE — Endpoint unique toutes couches territoire
try:
    from engines.v8_national.map_bundle import router as map_bundle_router
    app.include_router(map_bundle_router)
    logger.info("✓ V8-MAP-BUNDLE registered (/api/v8/map) — Bundle unique + cache 30s")
except Exception as e:
    logger.warning(f"V8 Map Bundle not loaded: {e}")

# V8-PHASE-A — Relocalisation + Salines (sandbox isolee)
try:
    from engines.v8_national.phase_a_engines import router as phase_a_router
    app.include_router(phase_a_router)
    logger.info("V8-PHASE-A registered (/api/v8/map) — Relocalisation + Salines")
except Exception as e:
    logger.warning(f"V8 Phase A not loaded: {e}")

# V8-PHASE-B — Zones + Corridors + Affuts terrain-aware (sandbox)
try:
    from engines.v8_national.phase_b_engines import router as phase_b_router
    app.include_router(phase_b_router)
    logger.info("V8-PHASE-B registered (/api/v8/map) — Zones/Corridors/Affuts TA")
except Exception as e:
    logger.warning(f"V8 Phase B not loaded: {e}")

# V8-PHASE-C — Scenario + Thermal + Multi-Engine Scoring
try:
    from engines.v8_national.phase_c_engines import router as phase_c_router
    app.include_router(phase_c_router)
    logger.info("V8-PHASE-C registered (/api/v8/engines) — Scenario/Thermal/Multi-Engine")
except Exception as e:
    logger.warning(f"V8 Phase C not loaded: {e}")

# V8-INSTITUTIONAL — 24 Engines + 4 Piliers (DOCUMENT MAITRE ULTIME MAX)
try:
    from engines.v8_institutional.piliers_router import router as institutional_router
    app.include_router(institutional_router)
    logger.info("V8-INSTITUTIONAL registered (/api/v8/institutional) — 24 Engines + 4 Piliers")
except Exception as e:
    logger.warning(f"V8 Institutional not loaded: {e}")

# V20 PERFORMANCE BUNDLE — cache TTL 24h (<1s loading target)
try:
    from engines.v8_institutional.v20_performance_bundle import router as v20_perf_router, v20_startup, v20_shutdown
    app.include_router(v20_perf_router)

    @app.on_event("startup")
    async def _v20_startup_hook():
        logger.info("[V20-STARTUP-HOOK] Firing — calling v20_startup()")
        try:
            await v20_startup()
            logger.info("[V20-STARTUP-HOOK] v20_startup() completed")
        except Exception as e:
            logger.warning(f"V20 startup hook failed: {e}", exc_info=True)

    @app.on_event("shutdown")
    async def _v20_shutdown_hook():
        try:
            await v20_shutdown()
        except Exception as e:
            logger.warning(f"V20 shutdown hook failed: {e}")

    logger.info("V20-PERFORMANCE registered (/api/v20/territoire/bundle) — cache 10K TTL 24h + disk persist + prechauffage")
except Exception as e:
    logger.warning(f"V20 Performance bundle not loaded: {e}")

# V20 MVT TILES — tile-filtered GeoJSON pour corridors/zones/contamination (CDN scalable 5000+)
try:
    from engines.v8_institutional.v20_mvt_tiles import router as v20_mvt_router
    app.include_router(v20_mvt_router)
    logger.info("V20-MVT-TILES registered (/api/v20/territoire/tiles) — zoom 12-16, TTL 24h")
except Exception as e:
    logger.warning(f"V20 MVT tiles not loaded: {e}")

# SELF-AUDIT-Omega — validation institutionnelle TERRITOIRE-V12 au demarrage
try:
    from engines.v8_institutional.self_audit_omega import router as self_audit_router, v20_self_audit_on_startup
    app.include_router(self_audit_router)

    @app.on_event("startup")
    async def _self_audit_startup_hook():
        import asyncio as _asyncio
        _asyncio.create_task(v20_self_audit_on_startup())

    logger.info("SELF-AUDIT-Omega registered (/api/v20/territoire/self-audit) — audit startup async")
except Exception as e:
    logger.warning(f"SELF-AUDIT-Omega not loaded: {e}")

# SLA-BASELINE-Ω — baseline institutionnelle + PERF-GUARD-Ω
try:
    from engines.v8_institutional.sla_baseline_omega import router as sla_baseline_router
    app.include_router(sla_baseline_router)
    logger.info("SLA-BASELINE-Omega registered (/api/v20/territoire/sla-baseline) — PERF-GUARD hybride")
except Exception as e:
    logger.warning(f"SLA-BASELINE-Omega not loaded: {e}")

# ENGINES-CATALOG — governance registry endpoint
try:
    from engines.v8_institutional.engines_catalog import router as engines_catalog_router
    app.include_router(engines_catalog_router)
    logger.info("ENGINES-CATALOG registered (/api/v20/territoire/engines-catalog) — SCIENCE-Ω registry")
except Exception as e:
    logger.warning(f"ENGINES-CATALOG not loaded: {e}")

# REGISTRY-LOCK-Ω — Phase XI scellé 22 engines SUPRA-Ω + hash Document Maître
try:
    from engines.v8_institutional.registry_lock_omega import router as registry_lock_router
    app.include_router(registry_lock_router)
    logger.info("REGISTRY-LOCK-Ω registered (/api/v20/territoire/registry-lock, /document-maitre-lock) — Phase XI sealed")
except Exception as e:
    logger.warning(f"REGISTRY-LOCK-Ω not loaded: {e}")

# CALIBRATION-DYNAMIQUE-Ω — Phase X ingestion observations + recalibration
try:
    from engines.v8_institutional.engine_calibration_dynamique_omega import router as calib_dyn_router
    app.include_router(calib_dyn_router)
    logger.info("CALIBRATION-DYNAMIQUE-Ω registered (/observations, /calibration-dynamique)")
except Exception as e:
    logger.warning(f"CALIBRATION-DYNAMIQUE-Ω not loaded: {e}")

# SCIENCE-GAPS-DATASETS-Ω — Phase X ingestion 4 gaps MFFP/IRDA/CWD
try:
    from engines.v8_institutional.science_gaps_datasets import router as gaps_router
    app.include_router(gaps_router)
    logger.info("SCIENCE-GAPS-DATASETS-Ω registered (/science-gaps) — 4 gaps ingested")
except Exception as e:
    logger.warning(f"SCIENCE-GAPS-DATASETS-Ω not loaded: {e}")

# ENGINE-CANADA-Ω — Phase X-B souveraineté pancanadienne
try:
    from engines.v8_institutional.engine_canada_omega import router as canada_router
    app.include_router(canada_router)
    logger.info("ENGINE-CANADA-Ω registered (/canada, /canada/province/{code}) — 13 provinces")
except Exception as e:
    logger.warning(f"ENGINE-CANADA-Ω not loaded: {e}")

# FEDERAL-DATASETS-Ω — Phase X-C LEP + HYDAT seeds
try:
    from engines.v8_institutional.federal_datasets_omega import router as federal_router
    app.include_router(federal_router)
    logger.info("FEDERAL-DATASETS-Ω registered (/federal/lep, /federal/hydat) — seed LEP+HYDAT")
except Exception as e:
    logger.warning(f"FEDERAL-DATASETS-Ω not loaded: {e}")

# ENGINE-RISQUES-HYDRO-Ω — Phase X-C risques hydrologiques
try:
    from engines.v8_institutional.engine_risques_hydro_omega import router as risques_hydro_router
    app.include_router(risques_hydro_router)
    logger.info("ENGINE-RISQUES-HYDRO-Ω registered (/risques-hydro)")
except Exception as e:
    logger.warning(f"ENGINE-RISQUES-HYDRO-Ω not loaded: {e}")

# SLA-BASELINE-30J-Ω — Phase X-D graphe 30 jours
try:
    from engines.v8_institutional.sla_baseline_30j_omega import router as sla_30j_router
    app.include_router(sla_30j_router)
    logger.info("SLA-BASELINE-30J-Ω registered (/sla-baseline-30j)")
except Exception as e:
    logger.warning(f"SLA-BASELINE-30J-Ω not loaded: {e}")

# SELF-AUDIT-ALERTS-Ω — Phase X-D WebSocket + REST
try:
    from engines.v8_institutional.self_audit_alerts_omega import (
        router as alerts_ws_router, rest_router as alerts_rest_router,
    )
    app.include_router(alerts_ws_router)
    app.include_router(alerts_rest_router)
    logger.info("SELF-AUDIT-ALERTS-Ω registered (/ws/self-audit-alert, /self-audit-alert/*)")
except Exception as e:
    logger.warning(f"SELF-AUDIT-ALERTS-Ω not loaded: {e}")

# EXPORT-INSTITUTIONNEL-V20-Ω — Phase X-D PDF signé
try:
    from engines.v8_institutional.export_institutionnel_v20_omega import router as export_v20_router
    app.include_router(export_v20_router)
    logger.info("EXPORT-INSTITUTIONNEL-V20-Ω registered (/export/institutionnel/v20)")
except Exception as e:
    logger.warning(f"EXPORT-INSTITUTIONNEL-V20-Ω not loaded: {e}")

# ENGINE-RENDER-Ω — Phase XI-SUPRA rendu territoire institutionnel
try:
    from engines.v8_institutional.engine_render_omega import router as render_omega_router
    app.include_router(render_omega_router)
    logger.info("ENGINE-RENDER-Ω registered (/render-config, /render-validate) — 14 couches")
except Exception as e:
    logger.warning(f"ENGINE-RENDER-Ω not loaded: {e}")

# VISUAL-PROOF-Ω — Phase XI-SUPRA-B preuve visuelle institutionnelle
try:
    from engines.v8_institutional.visual_proof_omega import router as visual_proof_router
    app.include_router(visual_proof_router)
    logger.info("VISUAL-PROOF-Ω registered (/visual-proof/generate, /visual-proof/index)")
except Exception as e:
    logger.warning(f"VISUAL-PROOF-Ω not loaded: {e}")

# VISUAL-PROOF-LIVE-Ω — Phase XI-SUPRA-C capture Playwright DOM Leaflet
try:
    from engines.v8_institutional.visual_proof_live_omega import router as visual_proof_live_router
    app.include_router(visual_proof_live_router)
    logger.info("VISUAL-PROOF-LIVE-Ω registered (/visual-proof-live/generate, /index)")
except Exception as e:
    logger.warning(f"VISUAL-PROOF-LIVE-Ω not loaded: {e}")

# ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω — Phase XI-SUPRA-G (ORDRE_TERRITOIRE_PROTECT_Ω)
try:
    from engines.v8_institutional.engine_territoire_anti_regression_omega import router as antireg_router
    app.include_router(antireg_router)
    logger.info("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω registered (/api/v20/territoire/anti-regression)")
except Exception as e:
    logger.warning(f"ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω not loaded: {e}")

# ENGINE-IA-CORRIDORS-Ω — Phase XI-SUPRA-H (ENGINE CORRIDORS VERSION Ω)
try:
    from engines.v8_institutional.engine_ia_corridors_omega import router as ia_corridors_router
    app.include_router(ia_corridors_router)
    logger.info("ENGINE-IA-CORRIDORS-Ω registered (/api/v20/territoire/ia-corridors)")
except Exception as e:
    logger.warning(f"ENGINE-IA-CORRIDORS-Ω not loaded: {e}")

# POST-SMOOTHER X180 — lissage biologique externe (hors V30)
# Enregistré AVANT l'engine V30 pour intercepter /generate (priorité FastAPI first-match)
try:
    from engines.post_smoothing.organic_corridor_smoother import router as corridor_smoother_router
    app.include_router(corridor_smoother_router)
    logger.info("✓ ORGANIC_SMOOTHER_Ω_X180 active (intercepts /api/v20/territoire/corridors-organic/generate)")
except Exception as e:
    logger.warning(f"ORGANIC_SMOOTHER_Ω_X180 not loaded: {e}")

# ENGINE-IA-CORRIDORS-ORGANIC-Ω — Phase XI-SUPRA-M (CORRIDORS ORGANIC VERSION Ω-M)
try:
    from engines.v8_institutional.engine_ia_corridors_organic_omega import router as organic_corridors_router
    app.include_router(organic_corridors_router)
    logger.info("ENGINE-IA-CORRIDORS-ORGANIC-Ω registered (/api/v20/territoire/corridors-organic)")
except Exception as e:
    logger.warning(f"ENGINE-IA-CORRIDORS-ORGANIC-Ω not loaded: {e}")

# ENGINE-RENDU-Ω — Phase XI-SUPRA-K (rendu institutionnel corridors)
try:
    from engines.v8_institutional.engine_rendu_omega import router as rendu_omega_router, visual_router as rendu_visual_router
    app.include_router(rendu_omega_router)
    app.include_router(rendu_visual_router)
    logger.info("ENGINE-RENDU-Ω registered (/api/v20/territoire/rendu-omega + /corridors-omega/visual-self-test)")
except Exception as e:
    logger.warning(f"ENGINE-RENDU-Ω not loaded: {e}")

# ENGINE-SPECIES-PROFILES-Ω — Phase XI-SUPRA-K (registre dynamique espèces)
try:
    from engines.v8_institutional.engine_species_profiles_omega import router as species_profiles_router
    app.include_router(species_profiles_router)
    logger.info("ENGINE-SPECIES-PROFILES-Ω registered (/api/v20/territoire/species-profiles)")
except Exception as e:
    logger.warning(f"ENGINE-SPECIES-PROFILES-Ω not loaded: {e}")

# ENGINE-IA-VISION-REGISTRY-Ω — Phase XI-SUPRA-K (registre IA Vision)
try:
    from engines.v8_institutional.engine_ia_vision_registry_omega import router as ia_vision_reg_router
    app.include_router(ia_vision_reg_router)
    logger.info("ENGINE-IA-VISION-REGISTRY-Ω registered (/api/v20/territoire/ia-vision)")
except Exception as e:
    logger.warning(f"ENGINE-IA-VISION-REGISTRY-Ω not loaded: {e}")

# LEP-INGESTION-Ω — Phase XI-SUPRA-D (BIONIC INGESTION-FGDB+GEOJSON-Ω-V1.0)
# EXCLUDE_LAYER LEP_CRITICAL_HABITAT_NATIONAL — Directive STEEVE-MAX 2026-04-20
# STATUS OFFICIAL — router désactivé, module source conservé pour réactivation future.
# try:
#     from engines.v8_institutional.lep_ingestion_omega import router as lep_ingest_router
#     app.include_router(lep_ingest_router)
#     logger.info("LEP-INGESTION-Ω registered (/api/v20/territoire/lep)")
# except Exception as e:
#     logger.warning(f"LEP-INGESTION-Ω not loaded: {e}")

# MONITORING-Ω + ALERTE-ANOMALIES-Ω
try:
    from engines.v8_institutional.monitoring_alerte_omega import router as monitoring_router
    app.include_router(monitoring_router)
    logger.info("MONITORING-Ω + ALERTE-ANOMALIES-Ω registered (/monitoring, /alertes)")
except Exception as e:
    logger.warning(f"MONITORING-Ω not loaded: {e}")

# ENGINE-GOUVERNANCE-Ω — fusion gouvernance unifiee
try:
    from engines.v8_institutional.engine_gouvernance_omega import router as gouv_router
    app.include_router(gouv_router)
    logger.info("ENGINE-GOUVERNANCE-Ω registered (/gouvernance)")
except Exception as e:
    logger.warning(f"GOUVERNANCE-Ω not loaded: {e}")

# ESI-Omega — Engine Securite Institutionnelle (Guardian Central)
try:
    from engines.v8_institutional.esi_omega import router as esi_router
    app.include_router(esi_router)
    logger.info("ESI-Omega registered (/api/v8/esi) — Guardian Central V8-PURE")
except Exception as e:
    logger.warning(f"ESI-Omega not loaded: {e}")

# SUPRA V8 — Integration TERRITOIRE → SUPRA (institutionnel)
try:
    from engines.v8_institutional.supra_v8 import router as supra_v8_router
    app.include_router(supra_v8_router)
    logger.info("SUPRA-V8 registered (/api/v8/supra) — Integration Institutionnelle")
except Exception as e:
    logger.warning(f"SUPRA V8 not loaded: {e}")

# V13-AUDIT — Public report endpoint
try:
    from routes.audit_report_route import router as audit_report_router
    app.include_router(audit_report_router)
except Exception as e:
    logger.warning(f"Audit report route not loaded: {e}")

# PHASE_ZERO_PLUS_X30 — CI_STATUS_Ω dashboard (lecture seule)
try:
    from routes.ci_status_omega import router as ci_status_omega_router
    app.include_router(ci_status_omega_router)
    logger.info("✓ CI_STATUS_Ω dashboard active (/api/omega/ci-status)")
except Exception as e:
    logger.warning(f"CI_STATUS_Ω route not loaded: {e}")

# PHASE_XI_SUPRA_RAPATRIEMENT_TERRITOIRE_V7_ULTIME_Ω — X195 export HTTPS
try:
    from routes.v7_ultime_export_router import router as v7_ultime_export_router
    app.include_router(v7_ultime_export_router)
    logger.info("✓ V7_ULTIME_EXPORT_X195 active (/api/v7-ultime-export/*)")
except Exception as e:
    logger.warning(f"V7_ULTIME_EXPORT router not loaded: {e}")

# PHASE_XI_SUPRA_ENGINES_OPTIMISATION_Ω — X198 DIFF_MATRIX lecture seule PRO/EXPERT
try:
    from routes.diff_matrix_router import router as diff_matrix_router
    app.include_router(diff_matrix_router)
    logger.info("✓ DIFF_MATRIX_X198_READONLY active (/api/v7-vs-actuel/diff-matrix*)")
except Exception as e:
    logger.warning(f"DIFF_MATRIX router not loaded: {e}")

# CATALOGUE_ENGINES_BIONIC — téléchargement HTTPS public
try:
    from routes.catalogue_engines_router import router as catalogue_engines_router
    app.include_router(catalogue_engines_router)
    logger.info("✓ CATALOGUE_ENGINES_BIONIC active (/api/catalogue-engines/*)")
except Exception as e:
    logger.warning(f"CATALOGUE_ENGINES router not loaded: {e}")

# ═══ X200 P0 ACTIVATION — V31_CORE_PREPARATOIRE_Ω ═══
# Ordre COMMANDANT STEEVE-MAX : activation des 5 engines P0
# (wildlife_behavior, eco_zones, hydro_topo + support reseau_veineux, bio_scoring)
for _slug, _label in [
    ("wildlife_behavior_omega", "ENGINE_WILDLIFE_BEHAVIOR_Ω (P0 #1 — CERF restauré)"),
    ("eco_zones_omega",         "ENGINE_ECO_ZONES_Ω (P0 #2 — 20 salines hiérarchisées)"),
    ("hydro_topo_omega",        "ENGINE_HYDRO_TOPO_Ω (P0 #3 — inversion hydro corrigée)"),
    ("reseau_veineux_omega",    "ENGINE_RÉSEAU_VEINEUX_Ω (support — 5 niveaux V7)"),
    ("bio_scoring_omega",       "ENGINE_BIO_SCORING_Ω (support — scoring 8-facteurs V7)"),
]:
    try:
        _mod = __import__(f"engines.{_slug}", fromlist=["router"])
        app.include_router(_mod.router)
        logger.info(f"✓ X200-P0 active : {_label}")
    except Exception as e:
        logger.warning(f"X200-P0 {_slug} not loaded: {e}")

# ═══ X200-P1-PREVIEW — Corridor pipeline preview (lecture seule) ═══
try:
    from routes.corridor_pipeline_preview_router import router as pipeline_preview_router
    app.include_router(pipeline_preview_router)
    logger.info("✓ X200-P1-PREVIEW active (/api/v7-ultime/corridor-pipeline-preview/*)")
except Exception as e:
    logger.warning(f"Pipeline preview router not loaded: {e}")

# ═══ PHASE X199 ACTIVATION — 5 engines étendus (ordre institutionnel) ═══
for _slug, _label in [
    ("ecoforestry_omega",         "ENGINE_ECOFORESTRY_Ω (X199 #1 — racine)"),
    ("advanced_geospatial_omega", "ENGINE_ADVANCED_GEOSPATIAL_Ω (X199 #2)"),
    ("terrain_3d_omega",          "ENGINE_3D_TERRAIN_Ω (X199 #3)"),
    ("legal_time_omega",          "ENGINE_LEGAL_TIME_Ω (X199 #4 — racine)"),
    ("predictive_omega",          "ENGINE_PREDICTIVE_Ω (X199 #5 — dépendant de 1-4)"),
]:
    try:
        _mod = __import__(f"engines.{_slug}.router", fromlist=["router"])
        app.include_router(_mod.router)
        logger.info(f"✓ X199 active : {_label}")
    except Exception as e:
        logger.warning(f"X199 {_slug} not loaded: {e}")

# ═══ PHASE X200-P5 — ENGINE RENDUΩ (validation ultime + blocage rendu) ═══
try:
    from routes.renduomega_router import router as renduomega_router
    app.include_router(renduomega_router)
    logger.info("✓ X200-P5 active : ENGINE_RENDUΩ (/api/v7-ultime/renduomega/*)")
except Exception as e:
    logger.warning(f"X200-P5 RENDUΩ router not loaded: {e}")

# ═══ PHASE X200-P6 — ANTI_REGRESSION_Ω (observation continue 12 sous-normes X150) ═══
try:
    from routes.anti_regression_omega_router import router as anti_regression_router
    app.include_router(anti_regression_router)
    logger.info("✓ X200-P6 active : ANTI_REGRESSION_Ω (/api/v7-ultime/anti-regression/*)")
except Exception as e:
    logger.warning(f"X200-P6 ANTI_REGRESSION_Ω router not loaded: {e}")

# ═══ PHASE XII-SUPRA — DIAGNOSTIC V30 CORRIDORS STATUS Ω (lecture seule) ═══
try:
    from routes.v30_corridors_status_router import router as v30_corridors_status_router
    app.include_router(v30_corridors_status_router)
    logger.info("✓ XII-SUPRA active : V30_CORRIDORS_STATUS_Ω (/api/v30/corridors/*)")
except Exception as e:
    logger.warning(f"XII-SUPRA V30_CORRIDORS_STATUS_Ω router not loaded: {e}")

# ═══ PHASE XII-SUPRA — CACHE DIAGNOSTIC Ω (lecture seule, ENFORCEMENT_P0) ═══
try:
    from routes.cache_diagnostic_router import router as cache_diagnostic_router
    app.include_router(cache_diagnostic_router)
    logger.info("✓ XII-SUPRA active : CACHE_DIAGNOSTIC_Ω (/api/v30/corridors/cache-diagnostic)")
except Exception as e:
    logger.warning(f"XII-SUPRA CACHE_DIAGNOSTIC_Ω router not loaded: {e}")

# ═══ PHASE XVII-SUPRA — ECOLOGICAL ORCHESTRATOR Ω ═══
try:
    from routes.ecological_orchestrator_router import router as ecological_orchestrator_router
    app.include_router(ecological_orchestrator_router)
    logger.info("✓ XVII-SUPRA active : ECOLOGICAL_ORCHESTRATOR_Ω (/api/v30/corridors/ecological-orchestrator)")
except Exception as e:
    logger.warning(f"XVII-SUPRA ECOLOGICAL_ORCHESTRATOR_Ω router not loaded: {e}")

# ═══ PHASE XVIII — ENGINE PREDICTIVE_OMEGA V2 GPS USGS Ω ═══
try:
    from routes.predictive_omega_v2_router import router as predictive_omega_v2_router
    app.include_router(predictive_omega_v2_router)
    logger.info("✓ XVIII active : PREDICTIVE_OMEGA_V2_Ω (/api/v30/predictive/omega-v2)")
except Exception as e:
    logger.warning(f"XVIII PREDICTIVE_OMEGA_V2_Ω router not loaded: {e}")

logger.info("=" * 60)
logger.info(f"✓ V5-ULTIME-FUSION: {len(CORE_ROUTERS)} modules registered")
logger.info("✓ PHASE G: BIONIC Engine P0 active")
logger.info("✓ x4100: Score consolide 22 moteurs (Option C)")
logger.info("✓ x4500-ULTRA: BSAA active")
logger.info("✓ BCE: BIONIC Compliance Engine active")
logger.info("✓ ULTRA-MAX++ FIREWALL: Geo-fencing Shapely active")
logger.info("✓ SALINES ULTIME: 5 scores + 20 sources active")
logger.info("✓ CARTE-2027: Moteur cartographique terrain V7 active")
logger.info("✓ NUTRITION-ENGINE-V7: Pipeline Sol→Nutriments→Fourrage→Gibier active")
logger.info("✓ SPATIAL-ENGINE-V7: Corridors+Zones+Heatmap+Scoring+Amenagement active")
logger.info("✓ SUPRA-ENGINE-V7: Analyse+Fiche+Compare+Recommande+Commande active")
logger.info("✓ INTELLIGENCE-V7: Score Chasse V7 active")
logger.info("✓ V8-NATIONAL: Moteurs nationaux V8 active (9 biomes, 6 regimes, 8 especes)")
logger.info("=" * 60)


# ==============================================
# CUSTOM OPENAPI SCHEMA
# ==============================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="BIONIC HUNT/Chasse V5-ULTIME-FUSION API",
        version="5.0.0",
        description="API modulaire de chasse intelligente - Fusion V2+V3+V4+BASE",
        routes=app.routes,
    )
    
    openapi_schema["tags"] = [
        {"name": "Orchestrator", "description": "System status and health"},
        {"name": "V5-Unified", "description": "Modules unifiés V5 (admin, notifications)"},
        {"name": "Core Engines", "description": "Phase 2 - Nutrition, Scoring, AI, Weather, Geospatial"},
        {"name": "Business Engines", "description": "Phase 3 - User, Territory, Referral"},
        {"name": "Master Plan", "description": "Phase 4 - Recommendations, Collaborative, Wildlife"},
        {"name": "Data Layers", "description": "Phase 5 - Ecoforestry, Behavioral, Simulation"},
        {"name": "Live Heading", "description": "Phase 6 - Immersive navigation"},
        {"name": "V5-BASE", "description": "Modules importés de BIONIC HUNT/Chasse-BASE"},
        {"name": "Legacy", "description": "Backward compatibility endpoints"},
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# ==============================================
# STATIC AUDIT FILES
# ==============================================
from fastapi.responses import FileResponse, JSONResponse
import os as _os

_MIME_MAP = {
    ".md": "text/markdown",
    ".yaml": "text/yaml",
    ".yml": "text/yaml",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".png": "image/png",
    ".json": "application/json",
}

_AUDIT_FILES = [
    "BIONIC_AUDIT_ECOLOGIQUE_v1.md",
    "BIONIC_AUDIT_ECOLOGIQUE_v1.yaml",
    "BIONIC_AUDIT_ECOLOGIQUE_v1.pdf",
    "pipeline_ecologique_v1.txt",
    "PLAN_DE_MATCH_STEEVE_MAX_v1.md",
    "PLAN_DE_MATCH_STEEVE_MAX_v1.pdf",
]

@app.get("/api/audit/list")
async def list_audit_files():
    base = _os.path.join(_os.path.dirname(__file__), "static")
    files = []
    for f in _AUDIT_FILES:
        fpath = _os.path.join(base, f)
        if _os.path.exists(fpath):
            ext = _os.path.splitext(f)[1].lower()
            files.append({
                "filename": f,
                "size_bytes": _os.path.getsize(fpath),
                "type": _MIME_MAP.get(ext, "application/octet-stream"),
                "download_url": f"/api/audit/{f}",
            })
    return JSONResponse(content={"audit_files": files, "total": len(files)})

@app.get("/api/audit/{filename}")
async def serve_audit_file(filename: str):
    safe_name = _os.path.basename(filename)
    path = _os.path.join(_os.path.dirname(__file__), "static", safe_name)
    if _os.path.exists(path):
        ext = _os.path.splitext(safe_name)[1].lower()
        media = _MIME_MAP.get(ext, "application/octet-stream")
        return FileResponse(path, filename=safe_name, media_type=media)
    from fastapi import HTTPException as _HTTPException
    raise _HTTPException(status_code=404, detail="File not found")


# ==============================================
# ARCHIVE PERMANENTE v5201 — Directive x5302
# Second endpoint HTTPS (double redondance)
# ==============================================
_ARCHIVE_DIR = _os.path.join(_os.path.dirname(__file__), "static", "archive_v5201")

@app.get("/api/archive/v5201/list")
async def list_archive_v5201():
    """Liste les fichiers de l'archive permanente v5201."""
    files = []
    if _os.path.exists(_ARCHIVE_DIR):
        for f in sorted(_os.listdir(_ARCHIVE_DIR)):
            fpath = _os.path.join(_ARCHIVE_DIR, f)
            if _os.path.isfile(fpath):
                ext = _os.path.splitext(f)[1].lower()
                files.append({
                    "filename": f,
                    "size_bytes": _os.path.getsize(fpath),
                    "type": _MIME_MAP.get(ext, "application/octet-stream"),
                    "download_url": f"/api/archive/v5201/{f}",
                })
    return JSONResponse(content={
        "archive": "BIONIC_OS_v5201",
        "status": "SCELLE — IMMUTABLE",
        "protocol": "BCE-4X GOLDEN V6+",
        "files": files,
        "total": len(files),
    })

@app.get("/api/archive/v5201/{filename}")
async def serve_archive_v5201(filename: str):
    """Sert les fichiers de l'archive permanente v5201 (second endpoint)."""
    safe_name = _os.path.basename(filename)
    path = _os.path.join(_ARCHIVE_DIR, safe_name)
    if _os.path.exists(path):
        ext = _os.path.splitext(safe_name)[1].lower()
        media = _MIME_MAP.get(ext, "application/octet-stream")
        return FileResponse(path, filename=safe_name, media_type=media)
    from fastapi import HTTPException as _HTTPException
    raise _HTTPException(status_code=404, detail="Archive file not found")


# ==============================================
# MAIN
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
