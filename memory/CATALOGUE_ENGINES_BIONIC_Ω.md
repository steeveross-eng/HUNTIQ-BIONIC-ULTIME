# CATALOGUE EXHAUSTIF DES ENGINES BIONIC
## État : 2026-04-22 — après X199

**Commandant** : STEEVE-MAX  
**Périmètre** : TOUS les engines présents dans le codebase BIONIC  
**Sources** : `/app/backend/engines/`, `/app/backend/modules/`, `/app/backend/core/scoring_pipeline/`

Classification :
- 🔒 **V30 LOCKED** — scellé SHA-256, non modifiable
- 🟢 **ACTIF** — en production
- 🟡 **SCAFFOLD X199** — squelette créé, feature flag OFF
- 🔵 **SOURCE CANONIQUE V7** — archivé, référence du CONTRAT RENDUΩ
- ⚪ **DEPRECATED** — désactivé (PURGE-V6)

---

# PARTIE I — `/app/backend/engines/v8_institutional/` (87 moteurs V30 LOCKED 🔒)

## I.1 Moteurs CORRIDORS / RÉSEAU
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_ia_corridors_omega.py` | Moteur corridors IA institutionnel (pathfinding, cost surface) | Dijkstra/A*, fused_behavioral_probability, cost_surface |
| `engine_ia_corridors_organic_omega.py` | **Moteur corridors organiques V30 scellé** (pivot smoother X180) | Splines, veines principales, waypoints biologiques |
| `engine_connectivite.py` | Connectivité habitat-à-habitat | Graphes, métriques de connectivité |
| `engine_connectivite_ecologique_omega.py` | Connectivité écologique avancée | Corridors écologiques, barrières |
| `hotspots_organic_v1.py` | Points chauds organiques | Densité, clusters |
| `engine_hotspots.py` | Hotspots classiques | Scoring spatial |

## I.2 Moteurs ZONES / HABITAT
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_zones.py` | Zones terrain de base | Polygones, typage zone |
| `zones_organic_v1.py` | Zones organiques V1 | Génération biologique |
| `engine_habitat_supra.py` | Habitat SUPRA | Scoring multi-critères habitat |
| `territoire_v10_supra.py` | Territoire V10 SUPRA | Découpage territorial |
| `terrain_v10_supra.py` | Terrain V10 SUPRA | Bundles terrain |
| `engine_terrain_cost.py` | Coût terrain | Rasters coût |
| `engine_territoire_anti_regression_omega.py` | Garde anti-régression territoire | Hash invariants |

## I.3 Moteurs SALINES / NUTRITION / ALIMENTATION
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_salines.py` | Moteur salines V30 (source unique actuelle) | Détection, scoring salines |
| `engine_salines_v11_supra.py` | Salines V11 SUPRA | 5 scores avancés |
| `salines_organic_v1.py` | Salines organiques V1 | Génération saline naturelle |
| `engine_nutrition.py` | Nutrition V30 (source unique actuelle) | Pipeline alimentaire |
| `engine_nutrition_v12_supra.py` | Nutrition V12 SUPRA | Sol→Nutriments→Fourrage→Gibier évolué |

## I.4 Moteurs VENT / MÉTÉO / CLIMAT
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_vent.py` | Moteur vent (olfactory cone) | Rose des vents, propagation odeurs |
| `engine_sensoriel_vent_odeurs_omega.py` | Vent/odeurs sensoriel avancé | Cône olfactif, dispersion |
| `engine_thermique_microclimat_omega.py` | Thermique microclimat | Thermiques matinales |
| `engine_pression_atmospherique_omega.py` | Pression atmo | Influence barométrique |
| `engine_climat_futur_omega.py` | Climat futur | Projections climatiques |
| `engine_influence_lunaire_omega.py` | Influence lunaire | Phases lune, solunaire |
| `engine_saisonnalite.py` | Saisonnalité | Fenêtres saisonnières |

## I.5 Moteurs IA / VISION / COMPORTEMENT
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_ia_vision_ecologique_omega.py` | Vision écologique IA | Patterns terrain, signatures |
| `engine_ia_vision_registry_omega.py` | Registre Vision (pins PRO/EXPERT) | Photos, traces, grattages |
| `engine_intelligence.py` | Intelligence comportementale | Scoring comportemental |
| `engine_comportement.py` | Comportement de base | Règles comportementales |
| `engine_comportement_avance.py` | Comportement avancé | Modèles multi-facteurs |
| `engine_comportement_biologique_omega.py` | Comportement biologique Ω | Cycles biologiques |
| `engine_psychologie.py` | Psychologie animale | Stress, vigilance |
| `engine_audio_acoustique.py` | Audio/acoustique | Détection sons |
| `engine_bio_signes.py` | Bio-signes (traces, fèces) | Classification indices |

## I.6 Moteurs SCORING / PRÉDICTION
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_score_global.py` | Score global territoire | Agrégation multi-scores |
| `engine_prediction.py` | Prédiction chasse | Modèles prédictifs |
| `engine_risque.py` | Risque (anthropique) | Scoring risque |
| `engine_risques_hydro_omega.py` | Risques hydro | Inondations, crues |
| `engine_pression.py` | Pression humaine | Proximité routes/bâti |
| `engine_stress_anthropique_omega.py` | Stress anthropique Ω | Pression anthropique fine |
| `engine_frequentation.py` | Fréquentation | Traffic chasseurs |
| `engine_visibilite.py` | Visibilité terrain | Viewshed |
| `engine_incertitude_omega.py` | Incertitude Ω | Intervalles confiance |

## I.7 Moteurs AFFUTS / CAMÉRAS / HYDRO / TERRAIN
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_affuts.py` | Affûts recommandés | Positionnement affûts |
| `engine_cameras.py` | Caméras de chasse | Placement, heatmap caméra |
| `engine_hydrologie_supra.py` | Hydrologie SUPRA | Réseau hydro complet |
| `engine_sol_supra.py` | Sol SUPRA | Pédologie, humidité |
| `engine_heatmap.py` | Heatmap principal | Agrégation raster |

## I.8 Moteurs ESPÈCE / POPULATION
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_espece_omega.py` | Espèce Ω | Métadonnées espèces |
| `engine_species_profiles_omega.py` | Profils espèces Ω | Locomotion, affinités |
| `species_weighting_profiles.py` | Pondérations par espèce | Poids scoring |
| `engine_population_dynamics_omega.py` | Dynamique populations | Modèles démographiques |
| `engine_contamination_v2_omega.py` | Contamination V2 | Santé faune |

## I.9 Moteurs GOUVERNANCE / SCIENCE / AUDIT
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_gouvernance_omega.py` | Gouvernance institutionnelle | Règles institutionnelles |
| `engine_science_omega.py` | Science Ω | Validité scientifique |
| `engine_qualite_donnees_omega.py` | Qualité données | DQ metrics |
| `engine_calibration_omega.py` | Calibration Ω | Calibration statique |
| `engine_calibration_dynamique_omega.py` | Calibration dynamique | Calibration runtime |
| `monitoring_alerte_omega.py` | Monitoring/alertes | Alertes runtime |
| `self_audit_omega.py` | Auto-audit Ω | Audit interne |
| `self_audit_alerts_omega.py` | Alertes auto-audit | Alerting |
| `esi_omega.py` | ESI Ω (Environmental Stability Index) | Index stabilité |
| `securite_omega_v19.py` | Sécurité V19 | Hardening |
| `phase_omega_secure_lockdown.py` | Verrouillage phase Ω | Lockdown institutionnel |
| `registry_lock_omega.py` | **Registre verrou SHA-256 V30** | Registre institutionnel scellé |
| `sla_baseline_omega.py` | SLA baseline | Métriques SLA |
| `sla_baseline_30j_omega.py` | SLA 30j | Fenêtre 30j |

## I.10 Moteurs RENDU / EXPORT / DATASETS / INFRA
| Moteur | Description | Composantes principales |
| --- | --- | --- |
| `engine_rendu_omega.py` | Rendu Ω | Spécifications rendu |
| `engine_render_omega.py` | Render Ω (alias) | Pipeline rendu |
| `export_institutionnel_v20_omega.py` | Export V20 | Export institutionnel |
| `federal_datasets_omega.py` | Datasets fédéraux | Provenance fédérale |
| `science_gaps_datasets.py` | Gaps datasets | Gaps scientifiques |
| `lep_ingestion_omega.py` | Ingestion LEP | Loi espèces en péril |
| `lidar_irda_v11.py` | LiDAR IRDA V11 | DEM 1m LiDAR |
| `supra_donnees.py` | SUPRA données | Agrégateur données |
| `supra_v8.py` | SUPRA V8 | Pipeline SUPRA |
| `v20_mvt_tiles.py` | Tuiles MVT V20 | Tiles vectorielles |
| `v20_performance_bundle.py` | Bundle perf V20 | Bundle optimisé |
| `redis_omega.py` | Redis Ω | Cache Redis |
| `visual_proof_omega.py` | Preuve visuelle Ω | Screenshots institutionnels |
| `visual_proof_live_omega.py` | Preuve visuelle live | Live proof |
| `visual_proof_live_playwright.py` | Preuve Playwright | Automation preuve |
| `engine_canada_omega.py` | Canada Ω | Pancanadien |
| `piliers_router.py` | Router piliers | Piliers institutionnels |
| `engines_catalog.py` | Catalogue engines v8 | Méta-catalogue |

---

# PARTIE II — `/app/backend/engines/` (hors v8_institutional)

## II.1 Engines ACTIFS
| Engine | Statut | Description | Composantes |
| --- | --- | --- | --- |
| `post_smoothing/` | 🟢 ACTIF X180 | **Smoother organique externe** (pivot du CONTRAT RENDUΩ) | 9 passes : trim / smooth / despike / eliminate_fuite / segment_max / eco_alignment / ia_attractors / re-smooth / re-densify |
| `bdre/` | 🟢 ACTIF | Data Reliability Engine (8 endpoints) | Quality flags, sources externes |
| `hunt_orchestrator/` | 🟢 ACTIF | Orchestration vent / odeurs / accès / affûts | Orchestrateur multi-moteurs |
| `terrain_nav/` | 🟢 ACTIF | Navigation terrain | Paths, DEM routing |
| `weather_v3/` | 🟢 ACTIF | Météo enrichie V3 | Nowcasting, scoring multi-critères |
| `supra_advanced/` | 🟢 ACTIF | SUPRA avancé | Pertinence / risque / reco / corrélation |
| `v8_national/` | 🟢 ACTIF | Pancanadien | 9 biomes, 6 régimes, 8 espèces, exclusions urbaines |
| `nutrition_intelligence/` | 🟢 ACTIF | ×5000 SUPRA (9 moteurs x5100-x5900) | Attractivité alimentaire avancée |

## II.2 Engines SOURCES CANONIQUES V7 (archivés)
| Engine | Statut | Description | Composantes |
| --- | --- | --- | --- |
| `spatial_engine_v7/` | 🔵 SOURCE V7 ULTIME | Corridors / zones / heatmap / scoring / aménagement | V7 complet |
| `supra_engine_v7/` | 🔵 SOURCE V7 ULTIME | Analyse / fiche / compare / recommande / commande | Décisions V7 |

## II.3 Engines SCAFFOLDS X199 (feature flag OFF 🟡)
| Engine | Slug | Statut | Rôle prévu |
| --- | --- | --- | --- |
| **ENGINE_RÉSEAU_VEINEUX_Ω** | `reseau_veineux_omega/` | 🟡 OFF | Topologie réseau veineux, convergence 600 m ±30 %, 5 niveaux hiérarchie |
| **ENGINE_ECO_ZONES_Ω** | `eco_zones_omega/` | 🟡 OFF | Zones écologiques 4 niveaux + attracteurs 6 types + 20 salines |
| **ENGINE_BIO_SCORING_Ω** | `bio_scoring_omega/` | 🟡 OFF | Scoring 8 facteurs V7 + façade-miroir V30 lecture seule |
| **ENGINE_HYDRO_TOPO_Ω** | `hydro_topo_omega/` | 🟡 OFF | Signaux hydro/topo unifiés, inversion hydro corrigée |
| **ENGINE_ECOFORESTRY_Ω** | `ecoforestry_omega/` | 🟡 OFF | Essences, canopy, stades successionnels, lisières |
| **ENGINE_3D_TERRAIN_Ω** | `terrain_3d_omega/` | 🟡 OFF | DEM 1m/5m/10m, relief 3D, exposition |
| **ENGINE_WILDLIFE_BEHAVIOR_Ω** | `wildlife_behavior_omega/` | 🟡 OFF | Comportements saisonniers, locomotion 5 espèces (+cerf) |
| **ENGINE_LEGAL_TIME_Ω** | `legal_time_omega/` | 🟡 OFF | Fenêtres légales chasse, exclusions temporelles |
| **ENGINE_PREDICTIVE_Ω** | `predictive_omega/` | 🟡 OFF | Prédictions comportementales, flux animaliers |
| **ENGINE_ADVANCED_GEOSPATIAL_Ω** | `advanced_geospatial_omega/` | 🟡 OFF | Projections, raster ops, multi-source fusion |

## II.4 Engines DEPRECATED ⚪
| Engine | Statut | Motif |
| --- | --- | --- |
| `corridor_unified/` | ⚪ DEPRECATED | PURGE-V6-PHASE-B (corridors V8 terrain-aware) |
| `relocation/` | ⚪ DEPRECATED | PURGE-V6-ANTI-DUPLICATION-A-Omega |

---

# PARTIE III — `/app/backend/modules/` (97 modules)

## III.1 Modules MÉTIER / TERRAIN / BIOLOGIE
| Module | Description | Composantes |
| --- | --- | --- |
| `bionic_engine_p0/` | **Monolithe P0** — routers + moteurs V2/V3 (210 fichiers) | Routers, services, moteurs historiques |
| `bionic_ecological_engine/` | Écologique BIONIC | Scoring écologique |
| `bionic_data_fabric/` | Fabric données | Pipeline données |
| `bionic_knowledge_engine/` | Knowledge Engine | Base connaissance |
| `bionic_stand_recommendation_engine/` | Reco affûts | Recommandations affût |
| `carte2027_engine/` | Carte 2027 | Rendu cartographique |
| `canada_v72/` | Canada V7.2 | 13 provinces, 16 écozones |
| `camera_engine/` | Caméras CAM-Ω | Gestion caméras |
| `vision_engine/` | Vision AI VIS-A | Vision artificielle |
| `saline_engine/` | **SALINE INTELLIGENCE ULTRA** (7 moteurs) | Attracteurs salines |
| `salines_ultime_engine/` | **5 scores × 20 sources V7** 🔵 | Salines hiérarchisées V7 |
| `nutrition_engine/` | Nutrition de base | Pipeline nutrition |
| `nutrition_engine_v7/` | **Pipeline V7 Sol→Nutriments→Fourrage→Gibier** 🔵 | Source CONTRAT |
| `nutrition_v6_interface/` | Interface V6 nutrition | Rétro-compat |
| `ecoforestry_engine/` | Écoforesterie | Essences, densité |
| `soil_engine/` | Pédologie GPS | Sols, humidité |
| `access_clarity_engine_v7/` | Clarté accès affûts V7 | Accès optimaux |
| `access_engine_v6/` | Accès V6 | Legacy accès |
| `territory_engine/` | Territoire | Découpage territoire |
| `geo_engine/` | Géospatial de base | Coordinates, distances |
| `geospatial_engine/` | Géospatial étendu | Rasters, projections |
| `species_engine/` | Species Engine K3 (12 endpoints) | Métadonnées espèces |
| `wildlife_behavior_engine/` | Comportement faune | Patterns faune |
| `weather_fauna_simulation_engine/` | Simulation météo+faune | Simulation intégrée |
| `solunar/` | Solunaire | Lune/soleil |
| `predictive_engine/` | Prédictif | Modèles prédictifs |
| `predictive_layer_engine/` | Couche prédictive | Layer prédictif |
| `legal_time_engine/` | Temps légal chasse | Fenêtres légales |
| `scoring_engine/` | Scoring générique | Scoring abstrait |
| `waypoint_engine/` | Waypoints | Gestion points |
| `waypoint_scoring_engine/` | Scoring waypoints | Scoring points |
| `poi_graph_engine/` | POI graphe | Graphe points intérêt |
| `ultimate_engines/` | Ultimate (fourre-tout avancé) | Moteurs avancés |
| `ultra_max_firewall/` | Geo-fencing urbain | Exclusion urbaine |
| `affut_ia_engine/` | Affût IA | IA recommandation affût |
| `live_heading_engine/` | Cap live | Heading temps réel |
| `adaptive_navigation_engine/` | Navigation adaptative | Routing adaptatif |
| `guide_pro_engine/` | Guide PRO | Mode PRO |
| `hunting_trip_logger/` | Log sorties chasse | Journal sorties |
| `strategy_master_engine/` | Stratégie master | Stratégie globale |
| `gestionnaire_engine/` | Gestionnaire | Mode gestionnaire |
| `tracking_engine/` | Tracking | Suivi |

## III.2 Modules INFRA / TRANSVERSE
| Module | Description |
| --- | --- |
| `api_gateway/` | Routeur unifié v3 |
| `auth_engine/` | Authentification |
| `user_engine/` | Gestion utilisateurs |
| `roles_engine/` | Rôles (PRO/EXPERT) |
| `admin_engine/` | Admin |
| `customers_engine/` | Clients |
| `partner_engine/` | Partenaires |
| `suppliers_engine/` | Fournisseurs |
| `orders_engine/` | Commandes |
| `cart_engine/` | Panier |
| `payment_engine/` | Paiement |
| `products_engine/` | Produits |
| `marketplace_engine/` | Marketplace |
| `ads_engine/` | Publicités |
| `ad_spaces_engine/` | Espaces pub |
| `affiliate_ads_engine/` | Affiliation pubs |
| `affiliate_switch_engine/` | Switch affiliation |
| `referral_engine/` | Parrainage |
| `upsell_engine/` | Upsell |
| `freemium_engine/` | Freemium |
| `marketing_engine/` | Marketing |
| `marketing_calendar_engine/` | Calendrier marketing |
| `seo_engine/` | SEO |
| `contact_engine/` | Contact |
| `share_engine/` | PARTAGER BCE-4X |
| `messaging_engine/` | Messagerie |
| `notification_unified_engine/` | Notifications unifiées |
| `alerts_engine/` | Alertes |
| `networking_engine/` | Réseau social |
| `tutorial_engine/` | Tutoriels |
| `formations_engine/` | Formations |
| `learning_engine/` | Apprentissage |
| `progression_engine/` | Progression utilisateur |
| `onboarding_engine/` | Onboarding |
| `analytics_engine/` | Analytics |
| `recommendation_engine/` | Recommandation |
| `optimization_engine/` | Optimisation |
| `experiments/` | A/B tests |
| `trigger_engine/` | Triggers |
| `rules_engine/` | Règles métier |
| `plugins_engine/` | Plugins |
| `ai_engine/` | AI générique |
| `wms_engine/` | WMS (web map service) |
| `data_layers/` | Couches données |
| `national_data_harvester/` | Harvester données fédérales |
| `engine_3d/` | 3D (visualisation) |
| `engine_registry/` | Registre engines |
| `backup_cloud_engine/` | Backup cloud |
| `master_switch/` | Master switch feature flags |
| `critical_modules/` | Modules critiques |
| `utility_modules/` | Utilitaires |
| `p1_engines/` | Engines P1 |
| `v51_engines/` | Engines V5.1 |
| `bsaa/` | BSAA (module spécifique) |

---

# PARTIE IV — `/app/backend/core/scoring_pipeline/` (24 pipelines)

| Pipeline | Description | Composantes |
| --- | --- | --- |
| `corridors_v10/` | **V7 ULTIME — scoring 8-facteurs + 5 niveaux** 🔵 | `scoring.py` (ECL 25, canopy 20, pression 15, nourriture+refuge 15, topo+hydro 10, regen 5, cost 10, bonus 1.05), `classifier.py` (CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE), `species_profiles.py` |
| `alimentation_v1/` | Alimentation V1 | Scoring aliments |
| `alimentation_v2/` | Alimentation V2 multi-espèces | Multi-espèces |
| `alimentation_v4/` | V4 terrain-centre SUPRA | Terrain-centre |
| `repos_v1/` | Repos par espèce | Zones repos |
| `habitat_v1/` | Habitat | Scoring habitat |
| `hydro_v1/` | Hydrologie V1 | Raster hydro |
| `thermal_v1/` | Thermique V1 | Thermiques |
| `attractors_v1/` | Attracteurs | Pipeline attracteurs |
| `behavior_v1/` | Comportement | Comportements |
| `pression_v1/` | Pression humaine | Pression |
| `risk_v1/` | Risque | Risques |
| `scenario_v1/` | Scénario | Scénarios |
| `temporal_v1/` | Temporel | Temporel |
| `ecosystem_v1/` | Écosystème | Écosystème |
| `trajets_v1/` | Trajets | Trajets |
| `visibility_v1/` | Visibilité | Visibilité |
| `opportunity_v1/` | Opportunité | Opportunités |
| `ndvi_vegetation_v1/` | NDVI végétation | Indices végétation |
| `multi_species_v1/` | Multi-espèces V1 | Multi-espèces |
| `simulation_v1/` | Simulation | Simulations |
| `rsf_engine/` | RSF (Resource Selection Function) | RSF |
| `learning_v1/` | Apprentissage | ML |
| `common/` | Primitives partagées | Utils pipeline |

---

# PARTIE V — STATISTIQUES AGRÉGÉES

| Zone | Engines | Fichiers .py |
| --- | --- | --- |
| `engines/v8_institutional/` (V30 LOCKED) | **87** | 87 fichiers racine |
| `engines/` (hors v8_inst, hors scaffolds) | **14** ACTIFS + **2** DEPRECATED | — |
| `engines/` SCAFFOLDS X199 (OFF) | **10** | — |
| `modules/` | **97** | — |
| `core/scoring_pipeline/` | **24** pipelines | — |
| **TOTAL ENGINES/MOTEURS** | **~232** distincts | ~522 .py cumulés |

---

## Légende
- 🔒 V30 LOCKED — SHA-256 scellé, intouchable
- 🟢 ACTIF — en production, utilisé par le pipeline
- 🟡 SCAFFOLD X199 — squelette prêt, feature flag OFF
- 🔵 SOURCE CANONIQUE V7 — référence du CONTRAT RENDUΩ (archivée)
- ⚪ DEPRECATED — désactivé (PURGE-V6)

## Hiérarchie opérationnelle actuelle (2026-04-22)

```
┌─ V30 LOCKED (87 moteurs v8_institutional) 🔒
│     pivot : engine_ia_corridors_organic_omega
│                    │
│                    ▼
├─ post_smoothing/ (X180 — 9 passes) 🟢  ← pivot du CONTRAT RENDUΩ
│                    │
│                    ▼
├─ 10 SCAFFOLDS X199 🟡 (OFF — attente X200)
│     4 canoniques + 6 étendus
│                    │
│                    ▼
└─ Frontend renduOmegaStore.js + BionicLayersV8.jsx 🟢
```

— FIN CATALOGUE —
