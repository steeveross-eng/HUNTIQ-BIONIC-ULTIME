# SCORE_GLOBAL_DYNAMIC_REPORT — Phase X-B

> **Statut :** ACTIF — mode V3-DYNAMIC-2026-04
> **Date :** 2026-04-19
> **Commandant :** STEEVE-MAX

## 1. Architecture

Le calcul `SCORE-GLOBAL-REALITY-Ω` V3 applique **3 niveaux de pondérations** :

```
base weights (_WEIGHTS)
    ↓  si species reconnue
species weighting profiles (5 profils: orignal/chevreuil/wapiti/ours_noir/dindon_sauvage)
    ↓  puis
dynamic calibration (ML observations terrain — recalibrate_weights)
    ↓  renormalisation Σ = 1.0
poids appliqué au calcul composite
```

## 2. Signature runtime

```python
compute_score_global_reality(bundle: dict) -> {
  "engine": "SCORE-GLOBAL-REALITY-Ω",
  "version": "V3-DYNAMIC-2026-04",
  "mode": "REALITE",
  "score_global": float,
  "classification": "EXCELLENT|BON|MODERE|FAIBLE|CRITIQUE",
  "axes_scores": {...},
  "weights": {...},                     # poids finaux (species + dynamic)
  "weights_base": {...},                # base _WEIGHTS constante
  "weights_species_applied": bool,
  "weights_dynamic_adjustments": {...}, # depuis calibration dynamique
  "contamination_v2_applied": bool,
  "axes_count": int,
}
```

## 3. Interaction CONTAMINATION-Ω V2

Le champ `contamination_v2.score` (0-100, 100=clean) remplace directement le
calcul `_contam_malus(contamination_v1)` lorsqu'il est présent, intégrant ainsi
le risque CWD/MDC dans le composite pondéré.

## 4. Preuve live

```bash
$ curl /api/v20/territoire/bundle?lat=45.4&lon=-72.0&species=chevreuil
→ score_global: 63.32 classification: BON
  weights_species_applied: True
  contamination_v2_applied: True
  version: V3-DYNAMIC-2026-04
```

## 5. Sealed
```
SEALED  — Phase X-B — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
