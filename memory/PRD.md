# HUNTIQ V9 — PRD
## ENGINE CORRIDORS V9-x20 SURCLASSE — PRET POUR VALIDATION
**MAJ:** 2026-04-17 | **CORRIDORS x20** | **6 ESPECES** | **20 DIMENSIONS**

## Architecture V9-INSTITUTIONNEL
- 24 Engines, 4 Piliers, ESI-Omega Guardian
- ENGINE CORRIDORS V9-x20: Catmull-Rom multi-especes vivant

## Phases Completees
- PHASE-1 a PHASE-4Omega: toutes terminees
- PHASE-ENGINE-CORRIDORS-Omega-ULTIME-VIVANT: SURCLASSAGE x20

## ENGINE CORRIDORS V9-x20
### Surclassage
- AVANT: 10 corridors, Bezier, 2 niveaux, 0 especes
- APRES: 8-12/espece, Catmull-Rom 5-9pts, 5 niveaux, 6 especes, 20 dimensions

### 6 Especes avec profils distincts
- cerf: sinueux_couvert (slope<25, cover++, wind++)
- orignal: large_humide (slope<35, water++, thermal++)
- wapiti: directionnel_cretes (slope<30, edge+)
- ours: opportuniste_couvert (slope<35, cover+++, noise_avoid++)
- chevreuil: sinueux_prudent (slope<20, wind+++, noise_avoid++)
- dindon: lineaire_lisiere (slope<15, edge++)

### 5 Niveaux Intensite
- Critique: #FF0000, 2.6px, 0.95
- Majeur: #D32F2F, 2.4px, 0.90
- Fort: #FF8F00, 2.2px, 0.85
- Modere: #FFEB3B, 1.8px, 0.75
- Faible: #FFFFFF, 1.4px, 0.65

### 20 Dimensions
Topo, hydro, humaines, olfactives, thermiques, geospatiales,
ecologiques, comportementales, vent, contamination, saison,
temporelle, pression, multi-especes, historique, multi-engines

## Endpoints
- GET /api/v8/institutional/territoire — Source UNIQUE
- GET /api/v3/weather/windgrid — Vent reel
- GET /api/v8/esi/conformite/full — 8/8 CONFORME

## Credentials
- Admin: admin@huntiq.com / Saturn5858*
