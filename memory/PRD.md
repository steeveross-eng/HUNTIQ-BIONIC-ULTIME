# HUNTIQ V8 — PRD
## BCE-4X V8-PREPARATION-Omega — NATIONAL-ENGINES-INIT CERTIFIE
**MAJ:** 2026-04-15 | **19/19 PASS** | **V8 NATIONAL ACTIF**

## Architecture V8 NATIONALE
```
TERRITOIRE-V7.2 (canvas — zones V7 + exclusions BCE-4X)
SPATIAL-ENGINE-V7.2 (/api/v7/spatial/* — 9 endpoints)
NUTRITION-ENGINE-V7.2 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CANADA-V7.2 (/api/v7/canada/* — 6 endpoints)
V8-NATIONAL (/api/v8/national/* — 5 endpoints)
CARTE-2027 (terrain)
```

## V8-NATIONAL Module
- 9 biomes canadiens (boreal_coniferous, boreal_mixed, temperate_deciduous, prairie_grassland, pacific_rainforest, montane_subalpine, taiga_subarctic, arctic_tundra, atlantic_maritime)
- 6 regimes fauniques (cervide_tempere, cervide_boreal, cervide_montagnard, omnivore_forestier, gallinace_forestier, arctique_toundra)
- 4 regimes de neige (maritime, continental, subarctique, alpin)
- 5 regimes forestiers (conifere_boreal, mixte_tempere, feuillu_meridional, pluvial_pacifique, taiga_lichen)
- 8 especes cataloguees (cerf, orignal, ours_noir, wapiti, caribou, dindon_sauvage, cerf_mulet, boeuf_musque)
- Score V8 national: 10 composantes (temporal, solunar, rut, nutrition, biome_compat, snow, forest, meteo, vision, habitat)
- Meteo temps reel ECCC integree
- Exclusions BCE-4X actives

## Endpoints V8
- /api/v8/national/biome-profile
- /api/v8/national/species-profile
- /api/v8/national/score
- /api/v8/national/referentials
- /api/v8/national/status

FIN DU DOCUMENT
