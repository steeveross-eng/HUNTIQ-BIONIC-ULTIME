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

# 6. Register Organic Zones V2 router (Pipeline Organique Unifié)
try:
    from modules.bionic_engine_p0.routers.organic_zones_router import router as organic_zones_router
    app.include_router(organic_zones_router)
    logger.info("✓ Organic Zones V2 registered (/api/v1/bionic/organic-zones)")
except Exception as e:
    logger.warning(f"Organic Zones V2 not loaded: {e}")

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
try:
    from engines.corridor_unified.router import router as corridor_unified_router
    app.include_router(corridor_unified_router)
    logger.info("BLOC 1: Corridor Unified Engine registered (/api/v1/corridor-unified)")
except Exception as e:
    logger.warning(f"Corridor Unified Engine not loaded: {e}")

# BCE-4X BLOC 3: Relocalisation Automatique Engine (salines/affuts)
try:
    from engines.relocation.router import router as relocation_router
    app.include_router(relocation_router)
    logger.info("BLOC 3: Relocalisation Automatique Engine registered (/api/v1/relocation)")
except Exception as e:
    logger.warning(f"Relocalisation Engine not loaded: {e}")





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

# 30. Register Movement Corridors router (Real vs Estimated corridors)
try:
    from modules.bionic_engine_p0.routers.movement_corridors_router import router as movement_corridors_router
    app.include_router(movement_corridors_router)
    logger.info("✓ Movement Corridors registered (/api/v1/bionic/movement-corridors)")
except Exception as e:
    logger.warning(f"Movement Corridors not loaded: {e}")

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

# ═══ CORRIDORS-V10 — Moteur corridors fauniques multi-especes ═══
# DELETE-LEGACY-V6: router_v6 SUPPRIME — BionicCorridorsV6Layer utilise toujours analyze-full
# On garde le router V6 car le frontend BionicCorridorsV6Layer en a besoin pour le GeoJSON complet
# La suppression complete sera faite quand le frontend sera recable sur SPATIAL-ENGINE-V7 GeoJSON
try:
    from core.scoring_pipeline.corridors_v10.router import router as corridors_v10_router
    from core.scoring_pipeline.corridors_v10.router import router_v6 as corridors_v6_router
    app.include_router(corridors_v10_router)
    app.include_router(corridors_v6_router)
    logger.info("✓ CORRIDORS-V6: PRESERVE (GeoJSON requis par TERRITOIRE) — SPATIAL-V7 en parallele")
except Exception as e:
    logger.warning(f"CORRIDORS-V6 not loaded: {e}")


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

# ═══ SALINES ULTIME ENGINE — 5 Scores + 20 Sources + FICHE ═══
try:
    from modules.salines_ultime_engine.router import router as salines_ultime_router
    app.include_router(salines_ultime_router)
    logger.info("✓ SALINES ULTIME registered (/api/v1/salines-ultime)")
except Exception as e:
    logger.warning(f"SALINES ULTIME not loaded: {e}")

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
