# RUT_HOTSPOTS_RECTIFICATION.md
## BCE-4X — RECTIFICATION RUT HOTSPOTS
### COMMANDANT STEEVE-MAX — RAPPORT D'ERREUR ET CORRECTIF

---

## SECTION A — EXPLICATION DE L'ERREUR

### Pourquoi les points chauds RUT n'avaient pas de polygone visible?

**Cause 1: Ordre de rendu (z-index)**
L'ordre de rendu dans `BionicCorridorsV6Layer.jsx` etait:
1. COUCHE 1 (Z-BAS): **Zones polygones** — rendues en PREMIER
2. COUCHE 2 (Z-MILIEU): **Corridors** — rendus en SECOND (PAR-DESSUS les zones)
3. COUCHE 3 (Z-HAUT): **Points centraux** — rendus en dernier

**Consequence:** Les corridors (glow 7-11px, couleur rouge #EF5350) couvraient
entierement les outlines de zone rut (3px, couleur #FF5722 — quasi-identique).
Les zones repos (bleu) et alimentation (vert) restaient partiellement visibles
car leurs couleurs sont distinctes du rouge corridor.

**Cause 2: Style insuffisant**
- `fillColor: 'transparent'` + `fillOpacity: 0` → ZERO surface coloree
- `weight: 3` → trop fin face aux corridors de 7-11px
- Pas de casing/background pour creer un contraste

---

## SECTION B — CORRECTIFS APPLIQUES

### B.1 — Inversion de l'ordre de rendu
**AVANT:** Zones → Corridors → Points
**APRES:** Corridors → Zones → Points

Les zones sont desormais rendues AU-DESSUS des corridors. Tous les polygones
de zone sont visibles, meme quand ils superposent un corridor de couleur similaire.

### B.2 — Casing blanc pour contraste
Chaque polygone de zone recoit un contour blanc semi-transparent (6px, opacity 0.5)
en arriere-plan, creant un contraste visuel fort sur toute imagerie satellite.

### B.3 — Fill semi-transparent
- `fillColor: zc` (couleur de zone)
- `fillOpacity: 0.08` (8% — subtil mais visible)
- Les zones sont desormais des surfaces colorees, pas juste des contours

### B.4 — BFS aligne sur 780m
Le rayon BFS backend est aligne sur le buffer UI frontend (780m) pour garantir
que TOUS les clusters visibles (centroides dans les 780m) ont un polygone genere.

---

## SECTION C — VERIFICATION

### Resultat API
```
9 polygones generes:
  alimentation: 4 polygones (16 centres)
  repos: 3 polygones (12 centres)
  rut: 2 polygones (8 centres)
Total: 36 centres couverts, 0 point nu
```

### Verification visuelle
- Rut: Polygones organiques rouges/orange VISIBLES au-dessus des corridors
- Repos: Polygones organiques bleus VISIBLES
- Alimentation: Polygones organiques verts VISIBLES
- ZERO forme lineaire, arc ou polygone clippe
- ZERO point chaud sans polygone conforme

---

## CONFORMITE

- [x] 100% des points chauds RUT couverts
- [x] ZERO point chaud "nu"
- [x] ZERO forme lineaire/arc
- [x] Zones AU-DESSUS des corridors (z-index corrige)
- [x] Casing blanc + fill semi-transparent
- [x] ZERO modification moteurs RSF/SSF
- [x] BCE-4X conforme

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
