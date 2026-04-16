# HUNTIQ V8 — PRD
## V8-VERIFICATION-DONNEES-CORRIDORS-V6 — DIAGNOSTIC COMPLET
**MAJ:** 2026-04-16 | **RAPPORT TECHNIQUE** | **CERTIFICATION SUSPENDUE**

## Diagnostic V6 vs V8 — Preuves Techniques

### 1. DONNEES SOURCES V6
- **GPS/Telemetrie animale**: INEXISTANTES. V6 n'a jamais utilise de donnees GPS.
- **Zones V6**: CERCLES PROCEDURAUX 600m (36 points reguliers via _make_circle_coords)
- **Corridors V6**: A* pathfinding procedural sur grille terrain derivee des zones
- **Affuts V6**: Derives des centroides de zones, position procedurale
- **Sources externes V6**: OSM/Overpass (exclusions), SRTM DEM (fallback heuristique)
- Les sources externes servaient aux EXCLUSIONS, pas a la geometrie

### 2. ECART REEL V6↔V8
- V6 zones = cercles 600m reguliers → V8 = polygones 14-20 vertices irreguliers (V8 PLUS organique)
- V6 corridors = A* sur grille terrain → V8 = Bezier entre points (ECART: pas de pathfinding)
- V6 affuts = centroides zones → V8 = oppose au vent + corridor bonus

### 3. CORRECTION POSSIBLE
- Reimplanter A* de corridor_10x.py dans V8 pour corridors terrain-aware reels

## Architecture V8
- phase_b_engines.py: generateurs terrain-aware (scoring, exclusions, Bezier)
- corridor_10x.py: A* pathfinding V6 (existe, non integre dans V8)

## CERTIFICATION: SUSPENDUE — EN ATTENTE DECISION COMMANDANT

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

FIN DU DOCUMENT
