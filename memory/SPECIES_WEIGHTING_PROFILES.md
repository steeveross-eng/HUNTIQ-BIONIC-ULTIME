# SPECIES_WEIGHTING_PROFILES — Phase X

> **Module :** `/app/backend/engines/v8_institutional/species_weighting_profiles.py`
> **Date :** 2026-04-19

## 5 profils scellés

| Espèce | Axes dominants (top-3) |
|--------|------------------------|
| `orignal` | habitat (0.11), thermique (0.10), hydrologie (0.08) |
| `chevreuil` | nutrition (0.12), stress_anthropique (0.10), habitat (0.08) |
| `wapiti` | connectivite (0.10), habitat (0.10), nutrition (0.09) |
| `ours_noir` | population (0.10), habitat (0.10), nutrition (0.10) |
| `dindon_sauvage` | nutrition (0.09), ia_vision (0.08), comportement_bio (0.08) |

## Alias reconnus
- `cerf`, `deer` → `chevreuil`
- `moose` → `orignal`
- `elk` → `wapiti`
- `bear`, `ours` → `ours_noir`
- `turkey`, `dindon` → `dindon_sauvage`

## API

```python
from engines.v8_institutional.species_weighting_profiles import get_species_weights
w = get_species_weights("cerf")   # ou "chevreuil", "deer", …
# returns renormalised dict (sum = 1.0) or None
```

## Validation
- `test_species_weighting_profiles.py` — 5 profils renormalisés, 5 alias résolus.

## Sealed
```
SEALED  — Phase X — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
