# SALINES_SELECTION_RULES.md
## BCE-4X ULTIME — VERROU SUR LA SELECTION DES SALINES
### COMMANDANT STEEVE-MAX — REGLES IMMUABLES

---

## REGLE DE SELECTION

### Algorithme officiel
```python
def _select_with_min_distance(candidates, max_n, min_dist_m):
    """Selection stricte par score — BCE-4X STEEVE-MAX."""
    if not candidates:
        return []
    sorted_cands = sorted(candidates, key=lambda c: c["score"], reverse=True)
    return sorted_cands[:max_n]
```

### Regles immuables
1. Les N salines selectionnees sont TOUJOURS les N scores les plus eleves
2. ZERO exclusion par distance
3. ZERO exclusion silencieuse
4. ZERO patch de score
5. max_salines = 2 (regle metier)

### Contraintes Pydantic
```python
max_salines: int = Field(2, ge=1, le=2)
```

### Toute modification future requiert
1. Ordre explicite du Commandant STEEVE
2. Plan de modification documente
3. Validation ecrite
4. Tests anti-regression T1 executes et passes
5. Journalisation dans BCE4X_GOVERNANCE_LOG.md

**EFFECTIF IMMEDIATEMENT — SANS EXPIRATION**

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
