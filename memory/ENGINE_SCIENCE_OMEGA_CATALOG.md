# ENGINE_SCIENCE_OMEGA_CATALOG — Catalogue scientifique complet

**Version:** V2-SUPRA-2026-04 | **Fichier:** `/app/backend/data/science_omega_catalog.json`

---

## 1. Espèces profiled (5/5)

| Code | Nom FR | Nom EN | Scientifique | Habitat principal | Stress thermique |
|---|---|---|---|---|---|
| orignal | Orignal | Moose | *Alces alces* | Forêts mixtes boréales + zones humides | 14-17°C |
| chevreuil | Chevreuil / Cerf de Virginie | White-tailed deer | *Odocoileus virginianus* | Forêts mixtes + lisières agricoles | 20-25°C |
| wapiti | Wapiti | Elk | *Cervus canadensis* | Prairies + forêts ouvertes | 20-25°C |
| ours_noir | Ours noir | Black bear | *Ursus americanus* | Forêts mixtes + lisières fruitières | 25-30°C |
| dindon_sauvage | Dindon sauvage | Wild turkey | *Meleagris gallopavo* | Forêts décidues matures + lisières agricoles | — |

### Besoins minéraux dominants par espèce

| Espèce | Minéraux critiques | Commentaire saisonnier |
|---|---|---|
| orignal | Na, K, Ca, Mg | Na post-hivernal intense |
| chevreuil | Na, Ca, Mg | Ca printemps (bois mâles, lactation femelles) |
| wapiti | Na, Ca, P, Mg | P été + Na année |
| ours_noir | Na (moindre), K | K hyperphagie automne |
| dindon_sauvage | Ca (coquille), P | Ca ponte + P année |

## 2. Études référencées (5)

| ID | Auteurs | Année | Organisation | DOI | Sujet |
|---|---|---|---|---|---|
| johnson-rea-2020 | Johnson, Rea | 2020 | Canadian Science Publishing | 10.1139/cjfr-2020-XXXX | moose-forest |
| gagnon-2024 | Gagnon et al. | 2024 | Wiley Online Library | 10.1002/ece3.10909 | moose-ecology |
| isle-royale-2021 | Isle Royale Wolf-Moose Project | 2021 | Frontiers in Ecology and Evolution | 10.3389/fevo.2021.758374 | moose-predator |
| iucn-moose | IUCN | — | IUCN Red List | — | species-status |
| alces-journal | — | — | ALCES Journal | — | moose-applied |

## 3. Datasets référencés (9)

| ID | Agency | Nom | URL |
|---|---|---|---|
| usgs-movement | USGS | Animal movement / telemetry | usgs.gov |
| noaa-climate | NOAA | Climat (neige, température) | noaa.gov |
| nasa-earthdata | NASA | EarthData NDVI + thermiques | earthdata.nasa.gov |
| mffp-qc | MFFP | Inventaires QC (orignal, cerf, etc.) | mffp.gouv.qc.ca |
| ontario-geohub | Ontario GeoHub | Moose Management Reports | ontario.ca/.../mnrf |
| nb-geoatlas | NB GeoAtlas | Moose Population & Harvest | www2.gnb.ca |
| usfws | USFWS | Habitat & population assessments | fws.gov |
| parcs-canada | Parcs Canada | Monitoring faune | parcs.canada.ca |
| maine-ifw | Maine IFW | Moose GPS Collar Dataset | maine.gov/ifw |

## 4. Engine ↔ Catalog links

11 mappings :
- `ENGINE-HABITAT-SUPRA` ← habitat species + MFFP + Ontario
- `ENGINE-HYDROLOGIE-SUPRA` ← NOAA + MFFP
- `ENGINE-SOL-SUPRA` ← USGS + NASA
- `ENGINE-STRESS-ANTHROPIQUE-Ω` ← behavior (activite + corridors)
- `ENGINE-NUTRITION-V12-SUPRA` ← nutrition + MFFP
- `ENGINE-ESPECE-Ω` ← species_profiles (all)
- `ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω` ← behavior + johnson-rea-2020
- `ENGINE-CONNECTIVITE-ECOLOGIQUE-Ω` ← corridors
- `ENGINE-THERMIQUE-MICROCLIMAT-Ω` ← climate + NOAA + NASA
- `ENGINE-SENSORIEL-VENT-ODEURS-Ω` ← activite
- `ENGINE-IA-VISION-ECOLOGIQUE-Ω` ← NASA EarthData

## 5. Totaux

| Élément | Count |
|---|---|
| Species profiles | 5 |
| Studies | 5 |
| Datasets | 9 |
| Data sources backend | 7 (LIDAR, IRDA, Open-Meteo, USGS, NOAA, NASA, MFFP) |
| Engine links | 11 |
| Gaps documentés | 6 |
