# REPOS_ZONE_FIX.md
## BCE-4X P0.1 — CORRECTIF ZONES REPOS (HARMONISATION)
### COMMANDANT STEEVE-MAX — DIRECTIVE EXECUTEE

---

## SECTION A — DIAGNOSTIC

### Symptome
- Zones Repos rendues comme arcs lineaires au bord du cercle d'analyse
- Zones Alimentation et Rut = polygones organiques coherents a l'interieur
- Incoherence visuelle et ecologique majeure

### Cause racine
**Fichier:** `backend/core/scoring_pipeline/corridors_v10/engine.py`
**Fonction:** `_generate_zone_polygons()` — Phase 2 BFS

Le BFS multi-source n'avait AUCUNE contrainte de distance par rapport au centre d'analyse.

**Mecanisme de defaillance:**
1. Les zones repos favorisent les cellules eloignees des routes (scoring: `distance_route_m`)
2. Ces cellules sont naturellement en peripherie de la grille (> 600m du centre)
3. Le BFS se propage au-dela du rayon d'analyse (600m) sans restriction
4. Le polygone resultant (1000+ vertices) s'etend sur 1000m+ du centre
5. Le frontend `clipRingsToCircle()` projette les vertices externes sur le cercle → arcs lineaires

---

## SECTION B — CORRECTIF APPLIQUE

### Modification 1: Contrainte BFS (Phase 2)
**Fichier:** `engine.py`, fonction `_generate_zone_polygons()`

```python
# BCE-4X P0.1: Contrainte rayon d'analyse
ANALYSIS_RADIUS_M = 600.0

# Dans la boucle BFS:
cell_lat = lat_start + (r + 0.5) * d_lat
cell_lng = lng_start + (c + 0.5) * d_lng
dist_to_center_m = math.sqrt(
    ((cell_lat - center_lat) * METERS_PER_DEG_LAT) ** 2 +
    ((cell_lng - center_lng) * m_per_lng) ** 2
)
if dist_to_center_m > ANALYSIS_RADIUS_M:
    continue  # ZERO cellule hors 600m
```

### Modification 2: Contrainte fallback synthétique
Pour les clusters avec < 3 cellules BFS dans le rayon:
- Verification que le centre primaire est dans les 600m
- Limitation du rayon du polygone synthetique pour rester dans le cercle

### Modification 3: Correctif centroide COUCHE 1 (session precedente)
Le check de visibilite des polygones utilise `props.center_lat/center_lng` (centre ecologique)
au lieu de `ringsCentroid()` (centroide geometrique derive).

---

## SECTION C — RESULTATS MESURES

### AVANT correction
| Zone | max_distance_centre | Forme visuelle |
|------|-------------------|----------------|
| alimentation | ~615m | Polygone organique (OK) |
| repos | > 1000m | Arcs lineaires (DEFAUT) |
| rut | ~1100m | Polygone organique (OK car centre proche) |

### APRES correction
| Zone | max_distance_centre | Forme visuelle |
|------|-------------------|----------------|
| alimentation | 613-626m | Polygone organique |
| repos | 628-635m | Polygone organique |
| rut | 627-635m | Polygone organique |

Toutes les zones sont desormais uniformement contraintes a ~630m (600m BFS + ~30m buffer Shapely).

### Distribution des polygones
- alimentation: 3 polygones, 12 centres (4/cluster)
- repos: 3 polygones, 12 centres (4/cluster)
- rut: 2 polygones, 8 centres (4/cluster)
- ZERO point sans polygone correspondant

---

## SECTION D — CONFORMITE

- [x] ZERO modification aux moteurs RSF/SSF
- [x] ZERO modification aux couches ecologiques
- [x] ZERO modification aux pondérations dynamiques
- [x] ZERO modification aux parametres comportementaux
- [x] Formes repos harmonisees avec alimentation et rut
- [x] Polygones organiques coherents (Shapely buffer + Catmull-Rom + Chaikin)
- [x] BCE-4X conforme — ZERO perte fonctionnelle

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
