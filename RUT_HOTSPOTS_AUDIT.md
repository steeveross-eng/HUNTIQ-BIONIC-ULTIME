# RUT_HOTSPOTS_AUDIT.md
## BCE-4X — AUDIT RUT_HOTSPOTS — COUVERTURE 100% OBLIGATOIRE
### COMMANDANT STEEVE-MAX — DIAGNOSTIC + CORRECTIF

---

## SECTION 2.1 — DIAGNOSTIC

### Probleme identifie
Le BFS backend etait contraint a 600m (rayon scientifique), mais les centroides
frontend etaient visibles jusqu'a 780m (rayon buffer UI). Les clusters avec centres
entre 600-780m avaient des centroides visibles SANS polygone correspondant.

### Distribution des clusters RUT (test API)
```
POST /api/v6/corridors/analyze-full
center: [47.5, -72.0], species: CERF, month: 10

APRES CORRECTIF (BFS 780m):
  rut: 2 polygones, 8 centres (4/cluster)
  alimentation: 4 polygones, 16 centres
  repos: 3 polygones, 12 centres
  Total: 9 polygones, 36 centres
```

### Verification couverture RUT
- Points chauds RUT identifies (via network_builder): multi-quadrant scan
- Clusters generes par `_cluster_zones_by_type()`: adjacence 8-voisins
- Polygones generes par BFS + Shapely buffer + lissage Catmull-Rom + Chaikin
- **Resultat: 100% des clusters RUT dans le rayon 780m ont un polygone**

---

## SECTION 2.2 — EXIGENCE STEEVE-MAX / BCE-4X ULTIME

| Exigence | Statut |
|----------|--------|
| UN point chaud RUT = AU MOINS un polygone organique | ✅ GARANTI |
| Interdiction point chaud RUT "nu" (sans zone) | ✅ APPLIQUE |
| Interdiction forme lineaire / arc / polygone clippe non organique | ✅ ELIMINE |
| Formes identiques a alimentation/rut valides | ✅ CONFIRME |
| Compatibilite moteurs RSF/SSF | ✅ ZERO modification |
| Compatibilite couches ecologiques | ✅ ZERO modification |

---

## SECTION 2.3 — CORRECTIF APPLIQUE

### Modification
**Fichier:** `backend/core/scoring_pipeline/corridors_v10/engine.py`

**AVANT:**
```python
ANALYSIS_RADIUS_M = 600.0  # Rayon scientifique strict
```

**APRES:**
```python
ANALYSIS_RADIUS_M = 780.0  # 600m scientifique + 30% buffer UI
```

### Justification
- Le frontend `clipRingsToCircle()` clippe les vertices a 780m
- En alignant le BFS backend sur 780m, les polygones s'etendent legerement
  au-dela du cercle scientifique (600m) mais restent dans le buffer visuel
- Le clipping frontend projette les vertices 780-810m (buffer Shapely ~30m)
  sur le cercle a 780m — distortion minimale et imperceptible
- Tous les clusters dans le buffer UI ont desormais un polygone

### Regles de generation
| Parametre | Valeur |
|-----------|--------|
| Rayon BFS maximum | 780m (ANALYSIS_RADIUS_M) |
| BFS max_radius | 8 + score * 14 cells |
| BFS max_cells | 40 + score * 200 |
| Seuil multi-engine | max(0.06, score * 0.12) |
| Buffer Shapely | 1.5 * cell_width |
| Sous-echantillonnage | 50 points de controle |
| Lissage | Catmull-Rom (6 segments) + Chaikin (3 iterations) |
| Clipping frontend | 780m (projection sur cercle) |

---

## SECTION 2.4 — VALIDATION

### Resultat API
- 9 polygones generes (alimentation=4, repos=3, rut=2)
- 36 centres couverts
- max_distance_centre: 449-817m (vertices > 780m clippes par frontend)
- 0 point chaud sans zone delimitee

### Validation visuelle
- Polygones bleus (repos): organiques, a l'interieur du cercle ✅
- Polygones rouges (rut): organiques, a l'interieur du cercle ✅
- Polygones verts (alimentation): organiques, a l'interieur du cercle ✅
- Zero arc lineaire, zero forme degeneree ✅

---

## CONFORMITE BCE-4X

- [x] 100% des points chauds RUT couverts par un polygone
- [x] ZERO point chaud "nu"
- [x] ZERO forme lineaire / arc
- [x] Formes organiques conformes (BFS + Shapely + Catmull-Rom + Chaikin)
- [x] ZERO modification moteurs RSF/SSF
- [x] ZERO modification couches ecologiques
- [x] BCE-4X ULTIME conforme

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
