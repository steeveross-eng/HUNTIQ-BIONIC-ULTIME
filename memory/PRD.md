# HUNTIQ V8 — PRD
## BCE-4X V8-INTEGRATION-Omega — PHASE 1 CERTIFIE
**MAJ:** 2026-04-15 | **Phase 1: 8/8 PASS** | **V8 FRONTEND ACTIF**

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

## V8-INTEGRATION-Omega — PHASE 1 (COMPLETE 2026-04-15)
### Fichiers crees/modifies:
- `/app/frontend/src/hooks/useBionicScoringV8.js` — Hook dedie Score V8 National
- `/app/frontend/src/components/territoire/ScoreV8Badge.jsx` — Badge SVG + 10 composantes + panneau detail
- `/app/frontend/src/components/territoire/ui/TerritoireHeader.jsx` — Remplace Score Chasse V6 par ScoreV8Badge
- `/app/frontend/src/pages/MonTerritoireBionicPage.jsx` — Integration hook V8 + props

### Resultats certification Phase 1:
1. Hook V8 operationnel (fetch score + biome-profile en parallele, cache 90s)
2. Badge V8 avec anneau SVG, 10 composantes, prediction, contexte biome
3. Panneau detail expandable (click) avec barres de progression colorees
4. V6 Score purge du header (ZERO-LEGACY)
5. Exclusions BCE-4X fonctionnelles (urbain=0, foret=64.5+)
6. Multi-province multi-espece verifie (AB, BC, ON, NU, QC, NB, NS, MB, SK, YT, NT)
7. Compilation webpack reussie (ZERO erreur)

## Taches restantes
### P0: Phase 2 — CARTE-2027 Integration V8
- Modifier Carte2027Page.jsx — Remplacer INTELLIGENCE V7 par Score V8
- Ajouter couches V8 (biome profile, corridors V8, compatibility layer)
- Integrer useBionicScoringV8 dans CARTE-2027

### P0: Phase 3 — Normalisation inter-provinciale
- Harmoniser 10 composantes V8 pour 10 provinces + 3 territoires
- Coherence Canada-wide sans brisures

### P0: Phase 4 — Validation V8
- Rapport V8-INTEGRATION >= 98/100

### P1 (Futur): 
- LiDAR WCS real multi-provincial (acces gouvernemental requis)
- IRDA API pedologie reelle Quebec (acces institutionnel requis)

## Mocked/Fallback
- LiDAR MRNF: fallback Copernicus/Open-Meteo
- IRDA pedologie: fallback SoilGrids

FIN DU DOCUMENT
