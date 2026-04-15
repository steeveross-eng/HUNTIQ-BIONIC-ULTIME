# HUNTIQ V6 — PRD
## BCE-4X V6.2 — SYSTEM-Omega-ULTIMATE-V5.4 + CARTE-2027 + P1-CRITICAL-V7
**MAJ:** 2026-04-15 | **87 MOTEURS + 4 P1-V7** | **METEO REEL ECCC/NOAA**

## Hierarchie cartes institutionnelle
- L1: TERRITOIRE (carte institutionnelle, 87 moteurs, source verite)
- L2: INTELLIGENCE (carte analytique, Score V7, predictions)
- L3: CARTE 2027 (carte terrain V7, Leaflet interactive, navigation + POI + mobile)
- Regle: TERRITOIRE -> INTELLIGENCE -> CARTE (descendant)

## Header V7: ACCUEIL | MAGASIN | TERRITOIRE | CARTE | CAMERAS | INTELLIGENCE | PERMIS

## Pages actives
- /mon-territoire-bionic (TERRITOIRE L1)
- /intelligence-v6 (INTELLIGENCE L2)
- /carte-2027 (CARTE L3 — Leaflet, heatmaps V7, GPS, POI, corridors, zones legales, meteo reel)
- /cameras (Camera Engine)
- /shop (Magasin)

## Moteurs: 87 actifs + 5 Carte2027 + 4 P1-V7
- Terrain(5) + P1(12) + Critical(7) + SUPRA(9) + Core(3) + Ultimate(29) + V5.1(22)
- 6 sources API gouvernementales (MFFP, MNRF, AEP, FLNRORD, ECCC, GeoBase)
- 9 interconnexions intermodules validees
- 11 provinces pancanada

## V7-P1-CRITICAL-EXECUTION — Deploye 2026-04-15
### P1-CMD01: METEO TEMPS REEL
- V7 Score auto-fetch ECCC/NOAA via Open-Meteo (temp, vent, pression, precipitation)
- Carte-2027 Wind realtime (direction, vitesse, rafales, pression, humidite)
- Backward compatible (params statiques toujours supportes)
- Scoring meteo enrichi (pression, precipitation comme bonus/malus)

### P1-CMD02: CORRIDORS V7
- 8 corridors V7 avec ponderation temporelle + solunaire + rut
- Multiplicateurs V7: temporal (1.3 crepusculaire), solunar (1.2 nouvelle lune), rut (1.4 pic)
- Type primary/secondary derive de l'intensite V7

### P1-CMD03: SALINES V7
- Bloc v7_temporal injecte dans /api/v1/saline/analyze
- Scores: temporal + solunar + rut = composite V7
- Recommendation adaptative ("periode optimale" vs "preparer le terrain")

### P1-CMD04: AFFUTS V7
- V7 temporal comme 7e couche (15%) dans le scoring multi-couches
- Scoring: saline(22%) + corridor(13%) + wind(13%) + hotspot(22%) + water(8%) + access(7%) + v7_temporal(15%)
- Justification enrichie avec score V7 temporel

## AUDIT V7-SUBLAYERS (2026-04-15)
- 62 sous-couches auditees
- POST-MIGRATION: 22 V7-OK (de 18), 12 partielles (de 14), 20 non-V7 (de 22)
- 4 P1 migrees vers V7

## Taches futures
- P2-CMD05: V7 comme couche #13 dans optimization engine
- P2-CMD06: Rebuild ConsolidatedHeatmapLayer sur V7
- P2-CMD07: Migration IntelligenceDashboard vers V7
- P3-CMD08: Vision IA scoring V7
- P3-CMD09: CursorBionicLayer migration V7
- P1: M5 Offline Mode Ultra (PWA caching)

FIN DU DOCUMENT
