# HUNTIQ V6 — PRD
## BCE-4X V7-ULTIME-Omega — SHADOW-REPORT COMPLETE
**MAJ:** 2026-04-15 | **SCORE CONFORMITE: 98/100** | **SHADOW REPORT: RECABLAGE AUTORISE**

## Architecture V7-ULTIME (FIGEE)
```
TERRITOIRE-V7 (canvas strategique)
    ↑ donnees spatiales + nutritionnelles
SPATIAL-ENGINE-V7 (/api/v7/spatial/* — 6 endpoints)
NUTRITION-ENGINE-V7 (/api/v7/nutrition/* — 7 endpoints)
    ↓
INTELLIGENCE-V7 (Score V7 + Score Chasse V7)
    ↓
SUPRA-ENGINE-V7 (/api/v7/supra/* — 6 endpoints)
    ↓
CARTE-2027 (terrain)
```

## SHADOW REPORT V6↔V7
- CORRIDORS: V6=8, V7=10 (+2 enrichissement). Ecart spatial max 344m. V7 ajoute types saisonnier+extreme. PASS
- HEATMAP: V6 avg=65.9, V7 avg=60.7. Delta 5.2 pts. DIVERGENCE ATTENDUE (nutrition_v7=50 composante reelle ajoutee)
- SCORING: V6=61.9, V7=63.1. Delta 1.2 pts. PASS (tolerance ±3)
- ZONES: V6=legales(7), V7=ecologiques(5). Types complementaires. COMPATIBLE
- ANOMALIES CRITIQUES: ZERO. ROLLBACK: NON REQUIS
- VERDICT: RECABLAGE AUTORISE

## Recablage frontend (EN ATTENTE validation Commandant)
1. Score Chasse header → /api/v1/v51/intelligence/v7/score-chasse (HAUTE compat)
2. ConsolidatedHeatmapLayer → /api/v7/spatial/heatmap (HAUTE compat)
3. useBionicScoring → /api/v7/spatial/scoring (HAUTE compat)
4. BionicCorridorsV6Layer → /api/v7/spatial/corridors+zones (MOYENNE compat)
5. SUPRA/Affuts: DEJA V7 (zero recablage)

## Taches futures
- Recablage frontend (sur ordre Commandant)
- Suppression V6 (apres validation SHADOW post-recablage)
- V7.2: Sentinel-2 NDVI direct, IRDA Quebec
- PWA M5 Offline Mode

FIN DU DOCUMENT
