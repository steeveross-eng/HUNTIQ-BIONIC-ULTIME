# 🏛️ ARCHITECTURE BIONIC · CARTOGRAPHIE COMPLÈTE
**Snapshot** : 2026-05-15 · BCE-4X ULTIME ABSOLU · COMMANDANT STEEVE-MAX
**Application** : `huntiq-restore.preview.emergentagent.com`
**Version doctrinale** : V11-SUPRA · V20-PERFORMANCE-Ω · PHASE-XII-ESPÈCES-Ω · P22ΩΩ

---

## 📊 VOLUMÉTRIE GLOBALE

| Métrique | Valeur |
|---|---|
| Fichiers Python backend | **1 621** |
| Fichiers `.jsx` frontend | **437** |
| Fichiers `.js` frontend | **250** |
| Lignes `server.py` | **1 668** |
| Lignes `MonTerritoireBionicPage.jsx` | **1 907** |
| `include_router` registrés dans `server.py` | **142** |
| Modules backend `/modules/*` | **91** |
| Modules frontend `/modules/*` | **33** |

---

## 🌐 TOPOLOGIE DÉPLOIEMENT

```
                    ┌────────────────────────────────┐
                    │  Kubernetes Ingress (HTTPS)    │
                    │  *.preview.emergentagent.com   │
                    │  → /api/*       → port 8001    │
                    │  → /*           → port 3000    │
                    └───────────┬────────────────────┘
                                │
            ┌───────────────────┴────────────────────┐
            ▼                                        ▼
    ┌──────────────┐                        ┌──────────────┐
    │  Frontend    │                        │  Backend     │
    │  React 19    │                        │  FastAPI     │
    │  Port 3000   │                        │  Port 8001   │
    │  Webpack HMR │                        │  Uvicorn     │
    │              │                        │  --workers 1 │
    │              │                        │  --reload ⚠️ │
    └──────────────┘                        └──────┬───────┘
                                                   │
                            ┌──────────────────────┼──────────────────────┐
                            ▼                      ▼                      ▼
                     ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
                     │  MongoDB    │        │  LRU cache  │        │ Open-Meteo  │
                     │ huntiq_v6   │        │  + disque   │        │ (CB OPEN    │
                     │ localhost   │        │ pkl 507KB   │        │  régulière) │
                     │ :27017      │        │ TTL 24h     │        │             │
                     └─────────────┘        └─────────────┘        └─────────────┘
```

⚠️ **Single-worker** = bottleneck architectural (escalation pending → `--workers 4`).

---

## 📁 STRUCTURE `/app` TOP-LEVEL

```
/app/
├── backend/                     # FastAPI · 1 621 fichiers .py
├── frontend/                    # React 19 · src/ = 687 fichiers .jsx/.js
├── memory/                      # PRD · CHANGELOG · audits · credentials
├── data/                        # Données statiques (geo, datasets)
├── docs/                        # Documentation utilisateur
├── institutional/               # Doctrine BCE-4X
├── scripts/                     # Scripts ops (déploiement, tests)
├── test_reports/                # Rapports testing_agent (json)
├── snapshots/                   # Snapshots architecturaux
│
├── HUNTIQ-V6-import/            # Import legacy V6
├── legacy/                      # Code legacy gelé
├── archive_github_v5201/        # Archive GitHub
├── archives/                    # Archives diverses
├── backups/                     # Sauvegardes ponctuelles
├── audit_historical/            # Audits historiques
├── registry/                    # Registry artefacts
│
└── 50+ fichiers `.md`           # Rapports audit (BCE-4X, doctrine, etc.)
```

---

## 🔧 BACKEND — `/app/backend`

### 📂 Structure niveau 1
```
backend/
├── server.py                    # 1 668 lignes · 142 routers · lifespan
├── database.py                  # Connexion Mongo
├── auth_helpers.py              # JWT helpers
├── premium_guard.py             # Premium tier guard
├── feature_controls.py          # Feature flags
├── notifications.py             # Système notif
├── email_service.py             # Resend
├── payments.py                  # Stripe
├── live_tracking.py             # GPS live
├── hunting_groups.py            # Groupes
├── lands_rental.py              # Location terrains
├── marketplace.py               # Marketplace
├── networking.py                # Networking
├── partnership.py               # Partenariats
├── product_discovery.py         # Produits
├── quebec_hunting_data.py       # Data QC
├── referral_system.py           # Parrainage
├── analyzer.py / bionic_engine.py / geospatial_data.py
│
├── engines/                     # 🌟 Engines V8/V10/V11/V20 (cœur métier)
│   └── v8_institutional/        # 100+ engines (corridors, zones, hotspots, etc.)
├── modules/                     # 91 modules métier
├── routes/                      # 30+ routers FastAPI
├── core/                        # alimentation, corridors, ecology, geo, ndvi, rest, scoring, weather
├── services/                    # scheduler, territory_analysis
├── models/                      # Pydantic schemas
├── schemas/                     # Schémas data
├── validators/                  # Validation
├── utils/                       # Helpers
├── monitoring/                  # Monitoring
├── tools/                       # Outils CLI
├── tests/                       # pytest
├── cache/                       # 🌟 LRU disque (territoire_bundle.pkl 507KB)
├── config/                      # Configuration
├── data/                        # Données statiques backend
├── docs/                        # Doc backend
├── institution/                 # Doctrine
├── bce/                         # BCE-4X interne
├── scripts/                     # Scripts backend
├── static/                      # Static assets
├── uploads/                     # Uploads users
└── websocket/                   # WebSocket handlers
```

### 🧬 `engines/v8_institutional/` — Cœur Bionic (100+ engines)

```
engines/v8_institutional/
├── 🌐 TERRITOIRE Ω (core)
│   ├── territoire_v10_supra.py            # compute_territoire_v10 (orchestrateur principal)
│   ├── terrain_v10_supra.py               # compute_terrain_v10 (DEM, slope, aspect)
│   ├── v20_performance_bundle.py          # Bundle orchestrator + LRU + Redis hooks
│   ├── lidar_irda_v11.py                  # LIDAR + IRDA
│   ├── supra_v8.py / supra_donnees.py
│   └── ecological_orchestrator_omega.py
│
├── 🦌 CORRIDORS Ω
│   ├── engine_ia_corridors_organic_omega.py   # V5 organic generation
│   ├── engine_ia_corridors_omega.py           # V4 legacy
│   ├── corridors_vitaux_omega.py
│   ├── audit_supra_corridors_omega.py
│   └── engine_connectivite_ecologique_omega.py
│
├── 🌍 ZONES / HOTSPOTS / SALINES
│   ├── engine_zones.py / zones_organic_v1.py
│   ├── engine_hotspots.py / hotspots_organic_v1.py
│   ├── salines_organic_v1.py
│   ├── engine_recettes_salines_omega.py
│   └── engine_carence_nutritionnelle_omega.py
│
├── 🦌 ESPÈCES Ω (5 cibles : chevreuil, orignal, ours_noir, coyote, dindon_sauvage)
│   ├── especes/
│   │   ├── mffp_phase3_p1_omega.py
│   │   └── ... (5 BIO-RÉACTEURS)
│   ├── engine_espece_omega.py
│   ├── engine_species_profiles_omega.py
│   ├── species_modulator_omega.py
│   ├── species_presence_mask_omega.py
│   └── species_weighting_profiles.py
│
├── 🌬️ MÉTÉO / ENVIRONNEMENT
│   ├── open_meteo_breaker.py              # ⚡ Circuit-breaker Open-Meteo (3 errors/600s)
│   ├── engine_vent.py / engine_thermique_microclimat_omega.py
│   ├── engine_pression_atmospherique_omega.py
│   ├── engine_canopee_thermique_omega.py
│   └── engine_climat_futur_omega.py
│
├── 🎯 AFFÛTS / VISIBILITÉ / ACOUSTIQUE
│   ├── engine_affuts.py
│   ├── engine_visibilite.py
│   ├── engine_audio_acoustique.py
│   └── engine_terrain_cost.py
│
├── 🐾 COMPORTEMENT BIO
│   ├── engine_comportement.py / engine_comportement_avance.py
│   ├── engine_comportement_biologique_omega.py
│   ├── engine_trophic_behavior_omega.py
│   ├── engine_psychologie.py
│   └── engine_population_dynamics_omega.py
│
├── 📊 PRÉDICTION / IA
│   ├── predictive_omega_v2.py
│   ├── engine_prediction.py
│   ├── engine_intelligence.py
│   ├── engine_ia_vision_ecologique_omega.py
│   └── engine_ia_vision_registry_omega.py
│
├── 🔬 SCIENTIFIQUE / AUDITS
│   ├── scientifique_omega/
│   ├── self_audit_omega.py                # ⚠️ DÉSACTIVÉ (subprocess pytest hog worker)
│   ├── self_audit_alerts_omega.py
│   ├── audit_supra_corridors_omega.py
│   ├── monitoring_alerte_omega.py
│   ├── visual_proof_omega.py / visual_proof_live_omega.py
│   └── sla_baseline_30j_omega.py
│
├── 🎨 RENDU / EXPORT
│   ├── engine_rendu_omega.py
│   ├── engine_render_omega.py
│   ├── export_institutionnel_v20_omega.py
│   ├── v20_3d_overlays_omega.py
│   └── v20_mvt_tiles.py
│
├── 💾 CACHE / INFRA
│   ├── redis_omega.py                     # L1 Redis (non-persistant entre forks)
│   └── v20_performance_bundle.py          # LRU + disk persist
│
├── 🔒 SÉCURITÉ / GOUVERNANCE
│   ├── securite_omega_v19.py
│   ├── protections_omega.py
│   ├── phase_omega_secure_lockdown.py
│   ├── registry_lock_omega.py
│   ├── engine_gouvernance_omega.py
│   └── piliers_router.py
│
└── 🗺️ DATASETS / GIS / ORIGINE EXTERNE
    ├── federal_datasets_omega.py
    ├── science_gaps_datasets.py
    ├── origine_externe_filter_omega.py
    ├── origine_externe_inversion_omega.py
    └── lep_ingestion_omega.py
```

### 🛣️ `routes/` — Routers FastAPI (30+ fichiers)

```
routes/
├── territory/                              # Routes territoire
│   ├── analysis_layers.py
│   ├── commerce.py
│   ├── events_photos.py
│   ├── gps_routes.py
│   ├── inventory.py
│   ├── quebec_hunting.py
│   └── users_cameras.py
│
├── audit_download_router.py                # 🌟 /api/v20/territoire/audit/files/{filename}
├── audit_report_route.py
├── especes_omega_router.py                 # 🌟 /api/v30/especes/*
├── bio_reacteur_router_omega.py            # 5 BIO-RÉACTEURS
├── corridors_vitaux_router.py
├── ecological_orchestrator_router.py
├── ecological_router_v8.py
├── fusion_territoire_omega_router.py
├── predictive_omega_v2_router.py
├── renduomega_router.py
├── v30_corridors_status_router.py
├── corridor_pipeline_preview_router.py
├── cache_diagnostic_router.py
├── catalogue_engines_router.py
├── ci_status_omega.py
├── diff_matrix_router.py
├── species_presence_mask_router.py
├── phase_xiv_router_omega.py / phase_xv_router_omega.py / phase_xix_router_omega.py
├── gis_reception_router_omega.py / gis_s3_upload_router_omega.py
├── origine_externe_filter_router.py / origine_externe_inversion_router.py
├── bio_profile_schema_router_omega.py
├── bionic_engine_router.py
├── bathymetry.py
├── map_perf.py
├── reports.py
├── user_data.py
├── v7_ultime_export_router.py
└── advanced_zones.py / anti_regression_omega_router.py
```

### 📦 `modules/` — 91 modules métier (sélection)

| Catégorie | Modules clés |
|---|---|
| **🔐 Auth & Users** | `auth_engine`, `user_engine`, `roles_engine`, `admin_engine` |
| **💰 Paiements** | `payment_engine`, `cart_engine`, `orders_engine`, `marketplace_engine` |
| **🦌 Chasse** | `affut_ia_engine`, `saline_engine`, `salines_ultime_engine`, `hunting_trip_logger`, `wildlife_behavior_engine`, `species_engine` |
| **🌳 Écologie** | `bionic_ecological_engine`, `ecoforestry_engine`, `nutrition_engine_v7`, `predictive_engine`, `bionic_engine_p0` (Open-Meteo) |
| **📍 Territoire** | `territory_engine`, `waypoint_engine`, `waypoint_scoring_engine`, `poi_graph_engine`, `geo_engine`, `geospatial_engine` |
| **🎯 Stratégie/Scoring** | `strategy_master_engine`, `scoring_engine`, `bionic_stand_recommendation_engine`, `optimization_engine`, `recommendation_engine` |
| **📸 Caméras/Vision** | `camera_engine`, `vision_engine` |
| **🔔 Notif/Comm** | `notification_unified_engine`, `messaging_engine`, `alerts_engine`, `contact_engine` |
| **📊 Analytics** | `analytics_engine`, `ai_engine`, `ml_router`, `learning_engine` |
| **🏪 Commerce** | `products_engine`, `suppliers_engine`, `customers_engine`, `shop`, `ad_spaces_engine`, `ads_engine`, `affiliate_*` |
| **🌐 GIS** | `national_data_harvester`, `wms_engine`, `data_layers`, `bsaa` |
| **🛡️ Sécurité** | `ultra_max_firewall`, `master_switch`, `critical_modules` |

### 🌐 API Gateway · Endpoints critiques

```
/api/health                                            (200 · 0.26s)
/api/auth/{login,verify,auto-login,me}
/api/v20/territoire/bundle?lat&lon&species&month&hour&wind_deg   🌟 Cache LRU+disque
/api/v20/territoire/lep/status                         (stub doctrinal)
/api/v20/territoire/audit/files/{filename}             🌟 PNG/MD download
/api/v20/territoire/bundle/stats
/api/v20/territoire/bundle/save-disk
/api/v30/territoire/ultime-score?lat&lon&species
/api/v30/especes/{list,lock-signature,audit/status}
/api/v30/especes/bio-reacteur/{species}                🌟 5 BIO-RÉACTEURS
/api/v30/corridors/status
/api/auth/verify  ·  /api/auth/auto-login
/api/users/me  ·  /api/waypoints  ·  /api/hunting-groups
/api/shop/{products,categories,cart,checkout}
/api/payments/{stripe-webhook,create-session}
```

### 💾 Données persistées

```
backend/cache/
├── territoire_bundle.pkl         # 507KB · LRU dump (11+ bundles)
├── redis-omega.rdb               # 117KB · Redis local (éphémère)
└── redis-omega.conf

MongoDB huntiq_v6
├── users                         # Bcrypt passwords, roles, premium_tier
├── orders
├── products
├── analytics
└── sightings
```

---

## 🎨 FRONTEND — `/app/frontend/src`

### 📂 Structure niveau 1
```
src/
├── App.js                              # Root · AuthProvider · Routing
├── index.js
│
├── pages/                              # ~30 pages routées
│   ├── MonTerritoireBionicPage.jsx     # 1 907 lignes · 🌟 carte TERRITOIRE Ω
│   ├── DashboardPage.jsx
│   ├── PricingPage.jsx / ShopPage.jsx / BusinessPage.jsx
│   ├── AnalyticsPage.jsx
│   ├── AdminPage.jsx / AdminGeoPage.jsx / AdminPremiumPage.jsx
│   ├── GestionnairePage.jsx / GuideProPage.jsx
│   ├── PlanMaitrePage.jsx / Carte2027Page.jsx
│   ├── NutritionIntelligence*.jsx (3 variantes)
│   ├── OnboardingPage.jsx / HuntingLicensePage.jsx
│   ├── ComparePage.jsx / SpeciesComparisonPage.jsx
│   ├── ForecastPage.jsx / FieldObservationForm.jsx
│   ├── ReportsPage.jsx / TripsPage.jsx
│   ├── PaymentSuccessPage.jsx / PaymentCancelPage.jsx
│   ├── ProductPage.jsx / MarketingCalendarPage.jsx
│   ├── BsaaDashboardPage.jsx / CalibrationDashboard.jsx
│   ├── HudUltimeDemoPage.jsx / BionicAnalysisDemoPage.jsx
│   ├── TerritoireCaptureModePage.jsx
│   ├── BionicModulesPage.jsx
│   ├── SupraPage.jsx
│   └── intelligence/                   # sous-pages intelligence
│
├── components/
│   ├── GlobalAuth.jsx                  # 🌟 AuthProvider + useAuth
│   ├── territoire/                     # 🌟 60+ composants TERRITOIRE Ω
│   ├── ui/                             # shadcn/ui
│   ├── maps/
│   ├── auth/
│   └── 40+ composants top-level (AdminPage, MarketplacePayments, etc.)
│
├── modules/                            # 33 modules métier frontend
│   ├── onboarding/                     # 🌟 useUserProfile (localStorage)
│   ├── intelligence-v6/                # HunterProfileWidget
│   ├── territory/
│   ├── nutrition/ / ecoforestry/
│   ├── recommendation/ / scoring/
│   ├── predictive/ / behavioral/
│   ├── dashboard/ / business/
│   ├── admin/ / customers/ / orders/
│   ├── ai/ / analytics/
│   ├── cart/ / products/ / suppliers/
│   ├── affiliate/ / collaborative/
│   ├── gestionnaire/ / groupe/
│   ├── legaltime/ / notifications/
│   ├── live_heading_view/ / map_hotspots/ / map_interaction/
│   ├── strategy/ / tutorial/ / user/
│   ├── wildlife/ / planmaitre/
│
├── hooks/                              # ~25 hooks
│   ├── useMapBundleV8.js               # 🌟 Bundle TERRITOIRE Ω + cache global
│   ├── useUserData.js                  # Waypoints user
│   ├── useGeolocation.js
│   ├── useBionicScoringV8.js / useBionicScoring.js
│   ├── useInstitutionalV8.js / useBionicSession.js
│   ├── useBionicLayers.js / useBionicWeather.js / useSharedWeather.js
│   ├── useCameraLayer.js / useAlphaLayer.js
│   ├── useZoneOrchestrator.js / useZoneCache.js
│   ├── useTerritoireEffects.js / useTerritoireWatchdog.js
│   ├── useSpatialClipping.js / useSplitViewZones.js
│   ├── useAccessRoute.js / useWaypointActions.js
│   ├── usePhaseAV8.js / useCIStatusBeacon.js
│   ├── useLiveTracking.js / useSharing.js
│   ├── useMapType.js / use-toast.js
│
├── lib/
│   ├── bionicBundleCache.js            # 🌟 P22ΩΩ · Cache LRU global window
│   ├── bce4xApi.js                     # API wrapper BCE-4X
│   ├── bioregion.js
│   ├── renduOmegaStore.js
│   ├── scoreLabelOmega.js
│   └── utils.js
│
├── core/                               # bionic core (SPECIES_LIST, BIONIC_MODULES)
├── config/                             # placeTypes, mapSources, biologicalSeasons, territoire_defaults
├── data_layers/
├── design-system/
├── contexts/                           # LanguageContext, etc.
├── i18n/
├── layouts/
├── services/                           # DataContractsV6, etc.
├── stores/                             # state global
├── theme/ / ui/
└── utils/
```

### 🗺️ `components/territoire/` — Composants TERRITOIRE Ω

```
territoire/
├── 🌟 P22ΩΩ widgets (récents)
│   ├── IntelligentPreloadWidget.jsx        # 🆕 Préchargement Premium
│   ├── HudTerritoireUltime.jsx             # HUD V30 (corridors, score)
│   ├── EspecesOmegaPanel.jsx               # PHASE-XII Espèces
│   ├── BioReacteursOmegaPanel.jsx          # 5 BIO-RÉACTEURS
│   └── StatutCorridorsOmegaPanel.jsx
│
├── 🗺️ Carte & layers
│   ├── BionicLayersV8.jsx                  # 🌟 Layers principal (V5 NATIFS)
│   ├── BionicLayersV8.jsx + 5 wrappers
│   ├── map/MapContent.jsx / SplitViewContainer.jsx
│   ├── MonTerritoireBionic.jsx
│   ├── BionicMicroZones.jsx
│   ├── BionicPrecisionZonesLayer.jsx
│   ├── BionicZone2km.jsx / BionicZone600m.jsx
│   ├── BionicAntiDoublesGuard.jsx
│   └── _PURGED_LEGACY_LAYERS_OMEGA.js
│
├── 🌳 Overlays spécialisés
│   ├── AlphaHotspotsLayer.jsx
│   ├── CameraMarkersLayer.jsx / CursorBionicLayer.jsx
│   ├── ConsolidatedHeatmapLayer.jsx
│   ├── ContaminationOverlayLayer.jsx
│   ├── ExclusionOverlayLayer.jsx
│   ├── HighFidelityMapLayers.jsx
│   ├── HuntingPathLayer.jsx / GuidedRouteLayer.jsx
│   ├── HydrographyOverlayLayer.jsx
│   ├── NdviOverlayLayer.jsx
│   ├── NutritionPointsLayer.jsx
│   ├── EcoforestryLayers.jsx
│   ├── StandsMapLayer.jsx
│   ├── StructureContrastLayer.jsx
│   ├── TrajectoriesLayer.jsx
│   ├── WindFlowLayer.jsx
│   ├── PhaseALayerV8.jsx
│   ├── RouteReplayLayer.jsx / RoutePlannerLayer.jsx
│
├── 📊 Panels & UI
│   ├── PhaseAPanelV8.jsx / PhaseCPanelV8.jsx
│   ├── NutritionPanelOmega.jsx / NutritionPointDetailPanel.jsx
│   ├── NutritionAnalysisModal.jsx
│   ├── InspectionBiologiquePanel.jsx / InstitutionalHealthPanel.jsx
│   ├── IntelligenceDashboard.jsx
│   ├── AmenagementPanel.jsx
│   ├── BionicZoneDiagnosticPanel.jsx
│   ├── DiagnosticExclusionsPanel.jsx
│   ├── FusionDebugPanel.jsx
│   ├── GroupDashboard.jsx
│   ├── GuidedRoutePanel.jsx
│   ├── LayersOmegaSyncPanel.jsx / LayersPanelOmegaUnified.jsx
│   ├── LocalCorridorLensPanel.jsx
│   ├── PedagogieModule.jsx
│   ├── PinnablePanel.jsx
│   ├── PlacesSidePanel.jsx
│   ├── StandDetailPanel.jsx
│   ├── TerritoireFrontendDebugOverlay.jsx
│   ├── TerritoryAnalysisPanel.jsx
│   ├── WaypointUnifiedPanel.jsx
│   ├── ZoneFavorites.jsx / ZoneInfoPanel.jsx
│
├── 🎨 Widgets visuels
│   ├── BionicLegend.jsx / BionicMapOverlay.jsx
│   ├── BionicScoreBadge.jsx / ScoreV8Badge.jsx
│   ├── CompareWidget.jsx
│   ├── CompassOmegaWidget.jsx
│   ├── SeasonalConditionsWidget.jsx
│   ├── ShareComponents.jsx
│   ├── TerritoireWarmupSplash.jsx
│   ├── WaypointContextMenu.jsx
│   ├── CesiumTerritoireViewer.jsx          # 3D Cesium (PHASE_3_3D_Ω)
│   ├── RenderGuardOmega.js
│   ├── RenduOmegaIntegralCertifier.jsx
│   ├── InstitutionalPopup.js
│
└── 🔧 sous-dossiers
    ├── intelligence/
    ├── map/
    ├── registry/
    ├── supra/
    └── ui/  (TerritoireHeader, WeatherPanel, etc.)
```

---

## 🔄 PIPELINE DE DONNÉES `/api/v20/territoire/bundle`

```
USER → fetch(bundle?lat&lon&species&month&hour&wind_deg)
            │
            ▼
    ┌───────────────────────────────────────────────────┐
    │ useMapBundleV8 (frontend)                         │
    │ → check bundleCacheGet (window LRU 90s)           │
    │ → si HIT : return immédiat                        │
    │ → si MISS : fetch HTTP                            │
    │ → retry 2s + 8s sur 502/503/504                   │
    └───────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────────────┐
    │ v20_performance_bundle.py                         │
    │ → _cache_key (lat3dec, lon3dec, species, month,   │
    │   wind/15°, HOUR IGNORÉ)                          │
    │ → _cache_get (LRU window + Redis L1)              │
    │ → si HIT : return ~0.2s                           │
    │ → si MISS : compute V10                           │
    └───────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────────────┐
    │ compute_territoire_v10                             │
    │ (territoire_v10_supra.py)                          │
    │  ├ await compute_terrain_v10 (DEM/slope/aspect)    │
    │  ├ Open-Meteo (CB OPEN si 429 × 3)                 │
    │  ├ LIDAR/IRDA v11                                  │
    │  ├ Zones + Hotspots + Salines (organic V1)         │
    │  ├ Affûts + Visibilité                             │
    │  └ HARDCAP 6s utilisateur / 12s warmup             │
    │  ⚠️ code SYNC après 1 await → hog event loop       │
    └───────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────────────┐
    │ generate_organic_corridors (V5)                    │
    │ (engine_ia_corridors_organic_omega.py)             │
    │  → divergence biologique stricte par espèce        │
    │  → budget = max(2s, hardcap - V10_elapsed)         │
    └───────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────────────┐
    │ Pipeline post-V5 (RenduΩ + veineux + interzone +   │
    │ predictive)                                         │
    │ → DEADLINE GLOBAL 10s : skip si dépassé             │
    └───────────────────────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────────────────────┐
    │ _cache_set (LRU + Redis + disk throttle 30s)       │
    │ → DEGRADED bundle : TTL 90s                         │
    │ → COMPLET : TTL 24h                                 │
    │ → BG_CACHE : task continue, callback met en cache   │
    └───────────────────────────────────────────────────┘
            │
            ▼
        BUNDLE RÉPONSE
```

---

## 🔑 INTÉGRATIONS TIERCES

| Service | Usage | Statut |
|---|---|---|
| **MongoDB** | Users, orders, products, analytics | ✅ Local `:27017` |
| **Open-Meteo** | Météo forêt | ⚠️ Free tier → 429 fréquent (CB OPEN) |
| **Stripe** | Paiements abonnements/marketplace | ✅ Configuré |
| **Resend** | Emails transactionnels | ✅ Configuré |
| **Cesium** | Visualisation 3D | ✅ via CDN ESM |
| **Leaflet** | Cartographie 2D | ✅ |
| **shadcn/ui** | Composants UI | ✅ `components/ui/*` |
| **OpenAI/Gemini/Claude** | (à vérifier dans modules ai/) | Emergent LLM key |

---

## 🎯 ENDPOINTS API CRITIQUES (état au 2026-05-15)

```
GET  /api/health                                           ✅ 200 · 0.26s
GET  /api/auth/verify?token=...                            ✅
GET  /api/auth/auto-login                                  ✅ (IP-based)
POST /api/auth/login                                       ✅ JWT

GET  /api/v20/territoire/bundle?lat&lon&species&...        ✅ HIT cache
GET  /api/v20/territoire/lep/status                        ✅ stub
GET  /api/v20/territoire/audit/files/{filename}            ✅ MD+PNG
GET  /api/v20/territoire/bundle/stats                      ✅
POST /api/v20/territoire/bundle/save-disk                  ✅

GET  /api/v30/territoire/ultime-score                      ✅ 3.66s
GET  /api/v30/especes/list                                 ✅
GET  /api/v30/especes/lock-signature                       ✅
GET  /api/v30/especes/bio-reacteur/{species}               ✅ (5 BIO)

GET  /api/users/me                                         ✅
GET  /api/waypoints                                        ✅
POST /api/hunting-groups                                   ✅
GET  /api/shop/products                                    ✅
POST /api/payments/create-session                          ✅
```

---

## 🛡️ ÉTAT MITIGATIONS ACTIVES (P22ΩΩ)

| Mitigation | État | Localisation |
|---|---|---|
| Bundles DEGRADED cachés TTL 90s | ✅ ON | `v20_performance_bundle.py` |
| `_MISS_HARDCAP_SEC = 6s` user / 12s warmup | ✅ ON | idem |
| `_GLOBAL_BUNDLE_DEADLINE_SEC = 10s` | ✅ ON | idem |
| EARLY-RETURN V10 dégradé | ✅ ON | idem |
| BG_CACHE callback + disk persist throttle 30s | ✅ ON | idem |
| `lifespan` invoque v20_startup/shutdown | ✅ ON | `server.py` |
| SELF-AUDIT-Ω désactivé | ✅ DISABLED | `server.py` |
| Daemons prechauffage (env-gated) | ⏸️ OFF | `P22OMEGA_PRECHAUFFAGE_DAEMONS=1` requis |
| BSL5 warmup (env-gated) | ⏸️ OFF | `P22OMEGA_BSL5_WARMUP=1` requis |
| Frontend retry 502/503/504 (2s+8s) | ✅ ON | `useMapBundleV8.js` |
| Widget Premium IntelligentPreload | ✅ ON | `IntelligentPreloadWidget.jsx` |
| Cache global window 90s | ✅ ON | `lib/bionicBundleCache.js` |

---

## ⚠️ LIMITES ARCHITECTURALES IDENTIFIÉES

| # | Limite | Impact | Résolution |
|---|---|---|---|
| L1 | `--workers 1` uvicorn | Cold-start 1er user freeze 50s tous endpoints | Escalation `support@emergent.sh` (BRIEF prêt) |
| L2 | Code SYNC dans `compute_territoire_v10` | Bloque event loop | Multi-worker compense |
| L3 | Redis local non-persistant entre forks | LRU reset au restart | OK : disque `.pkl` persistant |
| L4 | Open-Meteo free tier 429 fréquent | CB OPEN 600s | Acceptable (V11-LIDAR fallback) |
| L5 | `server.py` 1668 lignes monolithique | Maintenabilité | Backlog : split en `/routes/` |
| L6 | `MonTerritoireBionicPage.jsx` 1907 lignes | Idem frontend | Backlog : composer en sub-pages |

---

## 📚 MÉMOIRES D'AUDIT (`/app/memory/`)

```
memory/
├── PRD.md                                       # Requirements + status
├── CHANGELOG.md                                 # Historique technique
├── test_credentials.md                          # Identifiants test
├── audit_provenance/
│   ├── p22omegaomega_bundle_degraded_cache.md   # 🌟 Stabilisation 502
│   ├── p22omegaomega_prechargement_intelligent.md # 🌟 Widget Premium
│   ├── EMERGENT_PLATFORM_ESCALATION_BRIEF.md    # 🌟 Demande --workers 4
│   ├── p22omega_territoire_total_stack_audit.md
│   ├── p22omega_engines_matrix.md
│   ├── p22omega_frontend_render_injonction_omega.md
│   ├── p22omega_species_layer_divergence_v2.md
│   └── visual_divergence/
│       └── divergence_bsl_*.png (5 espèces + grille)
```

---

## 🔐 IDENTIFIANTS

| Compte | Email | Mot de passe | Rôle |
|---|---|---|---|
| Commandant | `commandant@bionichunt.com` | `Commandant2026` | admin |
| Auto-login admin | `admin@huntiq.com` | (IP-based) | admin |

---

## 🎬 SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase courante** : P22ΩΩ (post-stabilisation 502 + widget Premium)
- **Snapshot** : 2026-05-15 19:30 UTC
- **Validé par** : COMMANDANT STEEVE-MAX (vue d'ensemble demandée)
