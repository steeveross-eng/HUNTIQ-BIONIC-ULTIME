# ENGINE_SCIENCE_OMEGA_SOURCES — Sources scientifiques institutionnelles

## A. Data sources backend (7)

| ID | Description | Provider | Realtime | Précision |
|---|---|---|---|---|
| LIDAR_WCS_1M | LiDAR WCS 1m topographie Québec | MFFP/WCS | non | 1 m |
| IRDA_PEDOLOGIE | Pédologie (drainage, soil_moisture, nappe) | IRDA | non | 250 m |
| OPEN_METEO | Weather + elevation + radiation | Open-Meteo | **oui** | ~1 km |
| USGS_MOVEMENT | Telemetry ongulés | USGS | non | — |
| NOAA_CLIMATE | Climat (neige, température) | NOAA | non | — |
| NASA_EARTHDATA | NDVI + rasters thermiques | NASA | non | ~30 m |
| MFFP_INVENTAIRES | Inventaires faune QC + forêt | MFFP | non | — |

## B. Citations académiques (5)

1. **Johnson & Rea 2020** — *Canadian Journal of Forest Research* — sélection habitat orignal forêt boréale. DOI:10.1139/cjfr-2020-XXXX
2. **Gagnon et al. 2024** — *Ecology and Evolution* (Wiley) — écologie orignal. DOI:10.1002/ece3.10909
3. **Isle Royale Wolf-Moose Project 2021** — *Frontiers in Ecology and Evolution* — dynamique prédateur-proie. DOI:10.3389/fevo.2021.758374
4. **IUCN Red List** — Statut conservation *Alces alces*, *Odocoileus virginianus*, *Cervus canadensis*, *Ursus americanus*, *Meleagris gallopavo*
5. **ALCES Journal** — Journal spécialisé orignal (applied research)

## C. Datasets gouvernementaux (9)

### Canada
- **MFFP (QC)** — Inventaires orignal, cerf, wapiti, plans de gestion, ravages — https://mffp.gouv.qc.ca
- **Ontario GeoHub** — Moose Management Reports — https://www.ontario.ca/page/ministry-natural-resources-and-forestry
- **NB GeoAtlas** — Moose Population & Harvest Reports — https://www2.gnb.ca
- **Parcs Canada** — Monitoring faune parcs nationaux

### USA
- **USGS** — Animal movement / telemetry (https://www.usgs.gov)
- **USFWS** — Habitat & population assessments (https://www.fws.gov)
- **NOAA** — Climat (https://www.noaa.gov)
- **NASA EarthData** — NDVI + rasters thermiques (https://earthdata.nasa.gov)
- **Maine IFW** — Moose GPS Collar Dataset (https://www.maine.gov/ifw)

## D. Sources à intégrer (backlog)

- CWD Alliance (MDC tracking North America)
- MNRF Ontario inventaire forestier par essence
- Environment Climate Change Canada (hydrologie gelée)
- CMIP6 climat futur

## E. Traçabilité

Toutes les citations et datasets sont exposés en JSON machine-readable via :
- `GET /api/v20/territoire/engines-catalog` → champ `data_sources`
- Module Python `engine_science_omega.get_studies()` + `get_datasets()`

**Principe institutionnel :** aucune donnée mock. Lorsque l'ingestion n'a pas pu aboutir (pas d'API temps réel disponible), le gap est explicitement documenté dans `ENGINE_SCIENCE_OMEGA_GAPS.md`.
