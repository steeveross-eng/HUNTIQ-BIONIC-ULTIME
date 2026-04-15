# HUNTIQ V6 — PRD
## BCE-4X V6.2 — SYSTEM-Omega-ULTIMATE-V5.4-FINAL + CARTE-2027 + AUDIT-V7
**MAJ:** 2026-04-15 | **87 MOTEURS ACTIFS** | **CARTE-2027 DEPLOYEE** | **AUDIT V7 COMPLETE**

## Hierarchie cartes institutionnelle
- L1: TERRITOIRE (carte institutionnelle, 87 moteurs, source verite)
- L2: INTELLIGENCE (carte analytique, Score V7, predictions)
- L3: CARTE 2027 (carte terrain V7, Leaflet interactive, navigation + POI + mobile)
- Regle: TERRITOIRE -> INTELLIGENCE -> CARTE (descendant)

## Header V7: ACCUEIL | MAGASIN | TERRITOIRE | CARTE | CAMERAS | INTELLIGENCE | PERMIS

## Pages actives
- /mon-territoire-bionic (TERRITOIRE L1)
- /intelligence-v6 (INTELLIGENCE L2)
- /carte-2027 (CARTE L3 — Leaflet interactive, heatmaps V7, GPS, POI, corridors, zones legales)
- /cameras (Camera Engine)
- /shop (Magasin)

## Moteurs: 87 actifs + 5 endpoints Carte2027
- Terrain(5) + P1(12) + Critical(7) + SUPRA(9) + Core(3) + Ultimate(29) + V5.1(22)
- 6 sources API gouvernementales (MFFP, MNRF, AEP, FLNRORD, ECCC, GeoBase)
- 9 interconnexions intermodules validees
- 11 provinces pancanada avec populations + zones + feux + coupes

## CARTE-2027-REBUILD — Deploye 2026-04-15
- Carte Leaflet interactive (3 fonds: dark, satellite, topo)
- Heatmap comportementale V7 (grille predictive)
- Panneau Intelligence V7 flottant (Score V7, prevision 24h, solunaire, vent)
- Couches: corridors mouvement, zones legales, POI, cameras, vent
- Navigation GPS geolocalisation
- Backend: /api/v1/carte2027/* (5 endpoints)

## AUDIT V7-SUBLAYERS — 2026-04-15
- 62 sous-couches auditees
- 18 V7-OK (29%) | 14 partielles (23%) | 22 non-V7 (35%) | 5 a migrer (8%) | 3 a reconstruire (5%)
- 9 commandes correctives identifiees (P1: 4, P2: 3, P3: 2)
- Rapport: /app/V7-SUBLAYERS-AUDIT-REPORT.md

## Taches futures (par priorite audit)
- P1-CMD01: API meteo temps reel (ECCC/NOAA) pour Carte-2027 wind
- P1-CMD02: Migration corridors V6 -> V7 (ponderation temporelle+solunaire)
- P1-CMD03: Injection V7 dans saline_engine
- P1-CMD04: Ponderation affuts IA avec V7 score
- P2-CMD05: V7 comme couche #13 dans optimization engine
- P2-CMD06: Rebuild ConsolidatedHeatmapLayer sur V7
- P2-CMD07: Migration IntelligenceDashboard vers V7
- P3-CMD08: Vision IA scoring V7
- P3-CMD09: CursorBionicLayer migration V7

FIN DU DOCUMENT
