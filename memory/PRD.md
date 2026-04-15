# HUNTIQ V6 — PRD
## BCE-4X V6.2 — SYSTEM-Omega-ULTIMATE-V5.4-FINAL + CARTE-2027-REBUILD
**MAJ:** 2026-04-15 | **87 MOTEURS ACTIFS** | **CARTE-2027 DEPLOYEE**

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
- Selecteurs espece + province
- Compatible full-viewport (footer masque)
- Backend: /api/v1/carte2027/* (5 endpoints)

## Intelligence V7: Score V7, prediction horaire 24h, solunaire, multi-especes

## Taches P0 completees
- CARTE-2027-REBUILD-Omega-FULL-DEPLOY

## Taches futures
- P1: API meteo temps reel (ECCC / NOAA)
- P1: M5 Offline Mode Ultra (PWA caching + heatmaps offline)
- P2: LiDAR haute resolution (MFFP)
- P2: MVT tiles conversion reelle

FIN DU DOCUMENT
