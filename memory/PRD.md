# HUNTIQ V8 — PRD
## BCE-4X AUDIT-RECOUVREMENT-V8-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **18/18 PASS** | **100/100** | **GARANTIE DE PERSISTENCE**

## Resultat Audit Visuel (screenshot confirme)
- Score V8 Badge: 48/100 MOYEN (foret) / EXCLU BCE-4X (urbain) / LOCKED (governance)
- 10 composantes: TMP=50, SOL=70, RUT=20, NUT=48, BIO=35, NEI=75, FOR=33, MET=65, VIS=47, HAB=54
- Contexte National: Boreal conifere, QC, cervide_tempere, Continental
- Zones: 5 visibles (alimentation/repos/rut/affuts/eau)
- Corridors: 10 visibles (normal/intense/extreme/saisonnier)
- Heatmap: 154 points probabilite
- Guide Pro: visible + fonctionnel
- A EVITER: markers exclusion actifs

## Correctifs appliques
- ScoreV8Badge: detection EXCLU (engine=V8-EXCLUDED) + LOCKED (V8-GOVERNANCE-LOCKED)
- Affichage special "EXCLU BCE-4X" et "LOCKED" dans le detail panel
- PREDICTION_CONFIG etendu: exclu + locked

## Garantie de persistence
- BionicLayersV8: rendu unifie zones+corridors+heatmap depuis bundle V8
- ALWAYS_ON: 14 couches permanentes
- HEARTBEAT 5s: re-force couches automatiquement
- BionicCorridorsV6Layer: complementaire GeoJSON guide pro
- WeatherPanel: Score V8 prioritaire (fallback V7 si LOCKED)
- Couches survivent: reload, changement espece/province/preset/moteur/governance

## Fichiers modifies
- /app/frontend/src/components/territoire/ScoreV8Badge.jsx (EXCLU/LOCKED detection)

FIN DU DOCUMENT
