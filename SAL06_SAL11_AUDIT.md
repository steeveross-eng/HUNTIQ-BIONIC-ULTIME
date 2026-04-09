# SAL06_AUDIT.md + SAL11_AUDIT.md
## BCE-4X — AUDIT SAL-06 & SAL-11 (INCOHERENCE SELECTION SALINES)
### COMMANDANT STEEVE-MAX — DIAGNOSTIC TECHNIQUE

---

## SECTION A — CAUSE RACINE

### Algorithme de selection AVANT correctif
```python
def _select_with_min_distance(candidates, max_n, min_dist_m):
    sorted_cands = sorted(candidates, key=lambda c: c["score"], reverse=True)
    selected = []
    for cand in sorted_cands:
        if len(selected) >= max_n: break
        too_close = False
        for sel in selected:
            d = _haversine_m(cand["lat"], cand["lng"], sel["lat"], sel["lng"])
            if d < min_dist_m:
                too_close = True
                break
        if not too_close:
            selected.append(cand)
    return selected
```

### Scenario de defaillance
Candidats: A(60), B(55), C(49/SAL-11), D(47/SAL-06), E(45)
min_distance = 300m, max_salines = 2

1. Select A(60)
2. B(55) est a < 300m de A → REJETE
3. C(49/SAL-11) est a < 300m de A → REJETE
4. D(47/SAL-06) est a < 300m de A → REJETE
5. E(45) est a >= 300m de A → SELECTIONNE

**Resultat:** A(60) + E(45) actives. SAL-11(49) et SAL-06(47) REJETEES
alors que leurs scores sont superieurs a E(45).

### Verdict
- SAL-06 et SAL-11 ne sont PAS exclues par pente, vent, accessibilite, zone sensible,
  conflit corridor, seuil obsolete, bug de tri ou conflit d'ID.
- Elles sont exclues par la CONTRAINTE DE DISTANCE MINIMALE (300m) de l'algorithme
  glouton `_select_with_min_distance`.
- Cette exclusion est SILENCIEUSE — aucun log, aucune notification UI.

---

## SECTION B — CORRECTIF APPLIQUE

### Algorithme APRES correctif
```python
def _select_with_min_distance(candidates, max_n, min_dist_m):
    """
    BCE-4X STEEVE-MAX: Selection stricte par score.
    Toute saline ayant un score superieur a une saline active doit etre
    automatiquement consideree dans la selection finale.
    ZERO exclusion silencieuse par distance.
    """
    if not candidates:
        return []
    sorted_cands = sorted(candidates, key=lambda c: c["score"], reverse=True)
    return sorted_cands[:max_n]
```

### Regle STEEVE-MAX appliquee
- Les 2 salines selectionnees sont TOUJOURS les 2 scores les plus eleves
- ZERO exclusion par distance
- ZERO exclusion silencieuse
- Coherence totale: score backend = score UI = selection finale

---

## SECTION C — VERIFICATION

### Test API
```
POST /api/v2/alimentation/analyze
center: [47.5, -72.0], species: CERF, month: 10, max_salines: 2

SAL-01: score=52 selected=True  (plus haut score)
SAL-02: score=47 selected=True  (2eme plus haut score)
SAL-03: score=45 selected=False (3eme — max=2)
SAL-04: score=42 selected=False (4eme)
```

### Verification coherence
- La saline active de score le plus bas (47) est SUPERIEURE
  a toutes les salines non-actives (45, 42)
- ZERO incoherence score actif vs non-actif
- Regle STEEVE-MAX respectee

---

## SECTION D — FICHIERS MODIFIES

| Fichier | Modification |
|---------|-------------|
| `salines.py` | `_select_with_min_distance` → selection pure top-N par score |

### Elements NON modifies
- [x] Moteurs RSF/SSF — INCHANGES
- [x] Scoring des candidats — INCHANGE
- [x] Generation de candidats — INCHANGEE
- [x] Exclusions urbaines/eau — INCHANGEES
- [x] API endpoints — INCHANGES
- [x] Frontend NutritionPointsLayer — INCHANGE

---

## CONFORMITE

- [x] Regle STEEVE-MAX: score superieur = selection obligatoire
- [x] ZERO exclusion silencieuse
- [x] Coherence backend → RSF/SSF → UI/UX totale
- [x] BCE-4X conforme

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
