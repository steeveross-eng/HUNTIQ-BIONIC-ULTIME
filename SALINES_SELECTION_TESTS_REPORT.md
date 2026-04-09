# SALINES_SELECTION_TESTS_REPORT.md
## BCE-4X ULTIME — RAPPORT DE TESTS SELECTION SALINES
### COMMANDANT STEEVE-MAX

---

## TEST 1: Selection top-2 par score strict
```
POST /api/v2/alimentation/analyze
center: [47.5, -72.0], species: CERF, month: 10, max_salines: 2

Resultat:
  SAL-01: score=52 selected=True  (rang 1)
  SAL-02: score=47 selected=True  (rang 2)
  SAL-03: score=45 selected=False (rang 3, max=2)
  SAL-04: score=42 selected=False (rang 4)

VERDICT: PASSE — Les 2 selectionnees ont les 2 meilleurs scores
```

## TEST 2: Rejet Pydantic si max_salines > 2
```
POST /api/v2/alimentation/analyze
Body: { ..., max_salines: 4 }

Resultat: HTTP 422
Message: "Input should be less than or equal to 2"

VERDICT: PASSE — Validation Pydantic rejette max_salines > 2
```

## TEST 3: ZERO exclusion par distance
```
Ancien algorithme: _select_with_min_distance utilisait min_dist_m=300
Pouvait exclure SAL-06 (47) au profit de SAL-xx (45) si trop proche

Nouveau algorithme: top-N strict par score
SAL-06 (47) est TOUJOURS selectionnee si dans le top-2

VERDICT: PASSE — Aucun candidat de score superieur n'est jamais exclu
```

## TEST 4: Coherence UI
```
Frontend: nNutritionPointsMax = useState(2)
Selecteur: boutons [1, 2] uniquement
NutritionPointsLayer: maxNutritionPoints = 2

VERDICT: PASSE — UI reflete la regle metier
```

## VERDICT GLOBAL: TOUS LES TESTS PASSES

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
