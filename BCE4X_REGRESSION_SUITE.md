# BCE4X_REGRESSION_SUITE.md
## BCE-4X ULTIME — SUITE DE TESTS ANTI-REGRESSION
### COMMANDANT STEEVE-MAX — SPECIFICATIONS

---

## TESTS OBLIGATOIRES AVANT TOUT DEPLOIEMENT

### T1 — Selection des salines (top-N strict)
```
TEST: POST /api/v2/alimentation/analyze
ASSERTION: Les 2 salines selectionnees ont les 2 scores les plus eleves
ASSERTION: ZERO exclusion par distance
ASSERTION: n_salines <= 2
ASSERTION: HTTP 422 si max_salines > 2
```

### T2 — Generation des polygones (points chauds → zones)
```
TEST: POST /api/v6/corridors/analyze-full
ASSERTION: Chaque cluster genere exactement 1 polygone
ASSERTION: Chaque polygone a >= 3 vertices
ASSERTION: Chaque polygone a all_centers.length >= 1
ASSERTION: max_distance_centre <= 810m (780m BFS + 30m buffer)
ASSERTION: ZERO polygone hors rayon d'analyse
```

### T3 — Coherence UI/UX (toggles, couches, z-index)
```
ASSERTION: zoneSubFilters contient UNIQUEMENT: alimentation, repos, rut, affuts, eau
ASSERTION: pointSubFilters contient UNIQUEMENT: alimentation, rut, repos, affuts, centroides, individuels
ASSERTION: ZERO toggle orphelin (habitat, trajets, multiEngines)
ASSERTION: Ordre rendu: Zones (COUCHE 1) → Corridors (COUCHE 2) → Points (COUCHE 3)
ASSERTION: Zone outline: weight=3, opacity=1.0, fillColor=transparent, fillOpacity=0
ASSERTION: ZERO casing blanc
ASSERTION: ZERO fill semi-transparent
```

### T4 — Regles metier critiques
```
ASSERTION: max_salines = 2 (backend + frontend)
ASSERTION: Validation Pydantic: max_salines le=2
ASSERTION: UI selecteur: boutons [1, 2] uniquement
ASSERTION: BFS ANALYSIS_RADIUS_M = 780.0
ASSERTION: 1 cluster = 1 polygone organique (ZERO point nu)
```

### T5 — Integrite des moteurs RSF/SSF
```
ASSERTION: ZERO modification des coefficients depuis derniere validation
ASSERTION: ZERO modification des matrices de ponderation
ASSERTION: ZERO modification des covariables
ASSERTION: ZERO modification du scoring cellulaire
```

## EXECUTION

- Toute modification de code DOIT etre suivie de l'execution complete de T1-T5
- ZERO deploiement si un test echoue
- Resultats consignes dans BCE4X_REGRESSION_REPORT_LAST_RUN.md

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
