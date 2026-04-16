# HUNTIQ V8 — PRD
## V8-VISUAL-STEVE-MAX-Omega — CERTIFIE
**MAJ:** 2026-04-16 | **9/9 PASS** | **SCREENSHOT CONFIRME** | **ORGANIQUES**

## Rendu V8 conforme STEEVE-MAX
- Zones: polygones organiques 12+ vertices, contours opaques 2.5px, interieur TRANSPARENT
- Corridors: courbes Bezier 9 points, 5 niveaux intensite (critique/majeur/fort/modere/faible), opacite 0.85
- Affuts: triangles orientes (direction vent), halo discret, 3 qualites (optimal/bon/acceptable)
- ZERO micro-points, ZERO rectangles, ZERO artefacts

## Backend (map_bundle.py)
- _organic_polygon(): 12 vertices avec jitter pseudo-aleatoire
- _bezier_curve(): quadratique 8 points intermediaires
- _generate_affuts_inline(): orientation vent, placement hors zone

## Frontend (BionicLayersV8.jsx)
- Zones: L.polygon, fillOpacity:0, stroke opacity:1, weight:2.5
- Corridors: L.polyline sur path curved, glow pour critique/majeur
- Affuts: L.polygon triangle oriente, halo L.circleMarker

FIN DU DOCUMENT
