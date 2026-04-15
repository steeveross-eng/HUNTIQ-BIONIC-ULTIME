# HUNTIQ V6 — PRD
## BCE-4X V7-ULTIME-Omega — DELETE-LEGACY-V6 COMPLETE
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 99/100** | **V6 SUPPRIME**

## Architecture V7-ULTIME (FIGEE + RECABLEE + V6 PURGE)
```
TERRITOIRE-V7 (canvas strategique — 100% V7)
    ↑ ConsolidatedHeatmapLayer → /api/v7/spatial/heatmap
    ↑ BionicScoreBadge → /api/v7/spatial/scoring
    ↑ useBionicScoring → fetchScoreChasseV7()
    ↑ IntelligenceDashboard → INTELLIGENCE V7
SPATIAL-ENGINE-V7 (/api/v7/spatial/* — 6 endpoints)
NUTRITION-ENGINE-V7 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CARTE-2027 (terrain)
```

## V6 supprime
- /api/v1/score-consolide/point: 404 CONFIRME
- /api/v1/score-consolide/heatmap: 404 CONFIRME
- AccessRouteV6Layer: import supprime, rendu commente
- BionicScoreBadge: recable vers /api/v7/spatial/scoring

## V6 preserve (GeoJSON critique)
- /api/v6/corridors/analyze-full: requis par BionicCorridorsV6Layer GeoJSON
- Suppression quand SPATIAL-V7 produira du GeoJSON natif

## Taches futures
- SPATIAL-V7 GeoJSON: produire GeoJSON natif pour corridors/zones
- V7.2: Sentinel-2 NDVI direct, IRDA Quebec
- PWA M5 Offline Mode

FIN DU DOCUMENT
