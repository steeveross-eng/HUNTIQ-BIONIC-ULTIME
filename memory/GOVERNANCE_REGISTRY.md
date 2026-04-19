# GOVERNANCE_REGISTRY — Registry institutionnel complet BIONIC OS V20-SUPRA

**Date:** 2026-04-19 | **Version registry:** V3-SUPRA-2026-04

## 22 engines SUPRA-Ω actifs

### Pilier GOUVERNANCE (7)
| Engine | Version | Rôle |
|---|---|---|
| ENGINE-SCIENCE-Ω | V2-SUPRA | Catalog scientifique + registry central |
| ENGINE-MONITORING-Ω | V1-SUPRA | État unifié système |
| ENGINE-ALERTE-ANOMALIES-Ω | V1-SUPRA | Détection anomalies |
| ENGINE-QUALITE-DONNEES-Ω | V1-SUPRA | Complétude/cohérence/fraîcheur |
| ENGINE-INCERTITUDE-Ω | V1-SUPRA | Uncertainty score 4-facteurs |
| ENGINE-CALIBRATION-Ω | V1-SUPRA | Non-invasive calibration |
| ENGINE-GOUVERNANCE-Ω | V1-SUPRA | Fusion gouvernance unifiée |

### Pilier BIO-SYSTEME (9)
| Engine | Version | Rôle |
|---|---|---|
| ENGINE-NUTRITION-V12-SUPRA | V12 | Nutrition 6 modules, 7 outputs |
| ENGINE-HABITAT-SUPRA | V1-SUPRA | Score habitat 7 facteurs |
| ENGINE-HYDROLOGIE-SUPRA | V1-SUPRA | Hydrologie + retention + flood |
| ENGINE-SOL-SUPRA | V1-SUPRA | Pédologie + 4 indices minéraux |
| ENGINE-ESPECE-Ω | V1-SUPRA | Profils 5 espèces BCE-4X |
| ENGINE-CONNECTIVITE-ECOLOGIQUE-Ω | V1-SUPRA | Connectivité corridors |
| ENGINE-THERMIQUE-MICROCLIMAT-Ω | V1-SUPRA | Stress thermique |
| ENGINE-IA-VISION-ECOLOGIQUE-Ω | V1-SUPRA | IA Vision zones probables |
| ENGINE-POPULATION-DYNAMICS-Ω | V1-SUPRA | Démographie 5 espèces |

### Pilier COMPORTEMENT-HUMAIN (2)
| Engine | Rôle |
|---|---|
| ENGINE-STRESS-ANTHROPIQUE-Ω | Tranquillité vs pression humaine |
| ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω | Patterns saisonniers |

### Pilier SYSTEME-SENSORIEL (1)
| Engine | Rôle |
|---|---|
| ENGINE-SENSORIEL-VENT-ODEURS-Ω | Dispersion olfactive + vent |

### Pilier ENVIRONNEMENT (3)
| Engine | Rôle |
|---|---|
| ENGINE-CLIMAT-FUTUR-Ω | Projections CMIP6 2030/2040/2050 |
| ENGINE-INFLUENCE-LUNAIRE-Ω | Phases lunaires + solunar |
| ENGINE-PRESSION-ATMOSPHERIQUE-Ω | Pression + tendance 24h |

## 26 suites SELF-AUDIT-Ω
Toutes CONFORMES (26/26), PERF-GUARD=ok.

## Data sources (7)
LIDAR_WCS_1M, IRDA_PEDOLOGIE, OPEN_METEO, USGS_MOVEMENT, NOAA_CLIMATE, NASA_EARTHDATA, MFFP_INVENTAIRES

## Endpoints gouvernance
- `GET /api/v20/territoire/gouvernance` — **ENTRÉE UNIQUE** (ENGINE-GOUVERNANCE-Ω)
- `GET /api/v20/territoire/monitoring` — monitoring détaillé
- `GET /api/v20/territoire/alertes` — alertes actives
- `GET /api/v20/territoire/engines-catalog` — registry engines
- `GET /api/v20/territoire/self-audit` — audit 26 suites
- `GET /api/v20/territoire/sla-baseline` — baseline + régression PERF-GUARD

## Verdict institutionnel
> **BIONIC OS V20-SUPRA : SYSTÈME COMPLET — 22 ENGINES — 26/26 SUITES OK — 0 ALERTE CRITIQUE.**
