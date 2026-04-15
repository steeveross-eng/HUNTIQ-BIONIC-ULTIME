# HUNTIQ V6 — PRD
## BCE-4X V7-ULTIME-Omega — FRONTEND-RECABLE-V7 COMPLETE
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 98/100** | **RECABLAGE CONFIRME**

## Architecture V7-ULTIME (FIGEE + RECABLEE)
```
TERRITOIRE-V7 (canvas strategique — RECABLE)
    ↑ ConsolidatedHeatmapLayer → /api/v7/spatial/heatmap
    ↑ BionicCorridorsV6Layer → V6 GeoJSON + dataVersion:V7
    ↑ useBionicScoring → fetchScoreChasseV7()
    ↑ IntelligenceDashboard → INTELLIGENCE V7 branding
SPATIAL-ENGINE-V7 (/api/v7/spatial/* — 6 endpoints)
NUTRITION-ENGINE-V7 (/api/v7/nutrition/* — 7 endpoints)
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
CARTE-2027 (terrain)
```

## Recablage effectue
1. ConsolidatedHeatmapLayer: V6→V7 (/api/v7/spatial/heatmap) + adapted output
2. BionicCorridorsV6Layer: V6 preservee + dataVersion:V7 flag
3. useBionicScoring: fetchScoreChasseV7() ajoute (Score Chasse V7)
4. IntelligenceDashboard: INTELLIGENCE V7 + 87+ MOTEURS

## V6 en SHADOW (attente suppression)
- /api/v6/corridors/analyze-full
- /api/v1/score-consolide/heatmap
- Score Chasse V6+
- AccessRouteV6Layer

## Taches futures
- Suppression V6 definitive (sur ordre Commandant)
- V7.2: Sentinel-2 NDVI direct, IRDA Quebec
- PWA M5 Offline Mode

FIN DU DOCUMENT
