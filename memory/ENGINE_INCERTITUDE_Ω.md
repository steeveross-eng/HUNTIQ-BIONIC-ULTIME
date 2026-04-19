# ENGINE_INCERTITUDE_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_incertitude_omega.py`

## Rôle
Quantification de l'**incertitude** des prédictions par couche/engine/espèce.

## Formule
```
certainty = fiabilite_terrain × 0.35
          + studies_density_species × 0.25
          + avg_source_confidence × 0.25
          + profile_completeness × 0.15
uncertainty_score = (1 - certainty) × 100
score = (1 - uncertainty_score/100) × 100    # inverse pour dashboard
```

### Facteurs
| Facteur | Source |
|---|---|
| **fiabilite_terrain** | `terrain_v10.fiabilite` (LiDAR+IRDA) |
| **studies_density_species** | Count études pertinentes / 5 |
| **avg_source_confidence** | GOV=1.0, UNI/Peer-Reviewed=0.85, Autre=0.75 |
| **profile_completeness** | Champs peuplés / 5 du SPECIES_PROFILE |

### Niveaux
- < 20 : **TRES-FAIBLE**
- 20-40 : FAIBLE
- 40-60 : MODÉRÉE
- > 60 : FORTE

## Résultat observé (cerf, fiabilite=1.0)
```
uncertainty_score: 11.8    level: TRES-FAIBLE
certainty_score: 88.2
score: 88.2
factors: terrain_fiabilite=1.0, studies_density=1.0, avg_confidence=0.8, profile_completeness=1.0
```

## Intégration
- Bundle champ `incertitude`
- Axe `uncertainty_score` injecté dans INTELLIGENCE (breakdown)
- Pas de changement SCORE GLOBAL

## Test SELF-AUDIT
`/app/backend/tests/test_uncertainty.py` (19e suite)

## Limites
- `studies_density_species` filtre par topic string — à améliorer avec taxonomie formelle
- Confiance sources basée sur heuristique mots-clés — meta-review PR/GOV/UNI idéal
