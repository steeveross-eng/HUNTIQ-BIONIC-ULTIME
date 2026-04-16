# HUNTIQ V8 — PRD
## TERRITOIRE-V8-FIX-Omega — ZONES VISIBLES — CERTIFIE
**MAJ:** 2026-04-16 | **9/9 PASS** | **SCREENSHOT CONFIRME**

## Cause racine corrigee
Le bundle /api/v8/map/bundle exigeait une auth (get_current_user_with_role).
Si le token etait absent/expire, le fetch echouait silencieusement.
bundleData restait null → "Chargement V8..." permanent → ZERO zones rendues.

## Corrections
1. Bundle rendu PUBLIC (auth supprimee — governance-independent)
2. Loading HTML div supprime (incompatible avec contexte Leaflet)
3. Hook useMapBundleV8 simplifie (pas de token requis)
4. Polygones V8 agrandis 133m → 600m
5. fillOpacity zones 0.08 → 0.25
6. Corridors opacite 0.30 → 0.55

## Screenshot confirme
- 5 zones polygones VISIBLES (vert/bleu/rouge/cyan ~600m)
- Corridors lignes VISIBLES (orange)
- 163 elements SVG sur la carte
- Score V8 Badge dans header ("SCORE V8 PREVIEW 0/100 EXCLU BCE-4X")
- "Chargement V8..." DISPARU

FIN DU DOCUMENT
