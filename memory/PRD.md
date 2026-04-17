# HUNTIQ V8 — PRD
## PHASE-1 VERROUILLAGE ULTIME MAX — TERMINE
**MAJ:** 2026-04-16 | **24 ENGINES** | **4 PILIERS** | **62 DECISIONS**

## Document Maitre
- /app/memory/DOCUMENT_MAITRE_ULTIME_MAX.md (GELE — SSOT)

## 24 Engines Institutionnels (/app/backend/engines/v8_institutional/)
- 20 ACTIFS: zones, corridors, affuts, hotspots, vent, heatmap, salines, nutrition, pression, risque, frequentation, saisonnalite, comportement, comportement-avance, terrain-cost, visibilite, cameras, prediction, connectivite, intelligence, score-global
- 4 STUBS: bio-signes, audio-acoustique, psychologie-animale

## 4 Piliers (piliers_router.py)
- BIO-SYSTEME: /api/v8/institutional/pilier/bio-systeme
- COMPORTEMENT-HUMAIN: /api/v8/institutional/pilier/comportement-humain
- SYSTEME-SENSORIEL: /api/v8/institutional/pilier/systeme-sensoriel
- PREDICTION-INTELLIGENCE: /api/v8/institutional/pilier/prediction-intelligence
- FULL: /api/v8/institutional/full

## Matrice Migration: 62 decisions
- CONSERVER: 6 | CONSERVER+FUSIONNER: 22 | FUSIONNER: 28 | ELIMINER: 6

## Terrain Rules (Document Maitre)
- pente > 45deg = EXCLUSION
- eau < 10m = EXCLUSION
- zero smoothing, zero simplification polygonale

## Signatures Visuelles
- AFFUTS: cercle gris #9E9E9E + X central #424242
- CORRIDORS: #FF8F00
- ZONES: BCE-4X (rut #C62828, alim #2E7D32, repos #1565C0, eau #29B6F6)
- SALINES: cercle organique jaune #FDD835

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
