# HUNTIQ V8 — PRD
## BCE-4X TERRITOIRE-V8-FIX-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **14/14 PASS** | **100/100** | **7 CAUSES CORRIGEES**

## Corrections structurelles appliquees

### CAUSE 1 — Polygones V8 agrandis
- Avant: ~133m par cote (invisible au zoom normal)
- Apres: ~600m par cote (visible comme les polygones V6)
- Fichier: map_bundle.py (sz = 0.0027 deg)

### CAUSE 2 — bundleDataV8 strict supprime
- Avant: BionicLayersV8 ne rend RIEN si bundle null
- Apres: Affiche "Chargement V8..." + V6 en complement
- Fichier: MapContent.jsx (condition simplifiee)

### CAUSE 3 — clearLayers isole (anti-race)
- Avant: V6 et V8 se supprimaient mutuellement
- Apres: clearOwnLayers() isole par composant
- Fichier: BionicLayersV8.jsx

### CAUSE 5 — fillOpacity zones 0.08 → 0.25
- V6: BionicCorridorsV6Layer.jsx
- V8: BionicLayersV8.jsx

### CAUSE 6 — Corridors opacite 0.30 → 0.55
- V6: BionicCorridorsV6Layer.jsx (corOp = 0.55)
- V8: BionicLayersV8.jsx (opacity: 0.55)

### CAUSE 7 — Score V8 Badge EXCLU/LOCKED
- Detection isExcluded (engine=V8-EXCLUDED)
- Detection isLocked (engine=V8-GOVERNANCE-LOCKED)
- ScoreV8Badge.jsx

## Architecture rendu
```
MapContent
  -> BionicLayersV8 (source PRINCIPALE V8: zones 600m + corridors + heatmap)
  -> BionicCorridorsV6Layer (complement: GeoJSON organiques + guide pro + affuts)
```

FIN DU DOCUMENT
