# ENGINE_INFLUENCE_LUNAIRE_Ω — Documentation

**Version:** V1-SUPRA-2026-04 | **Fichier:** `engine_influence_lunaire_omega.py`

## Rôle
Phases lunaires (algorithme Conway) + illumination + score activité faunique (théorie solunar).

## Algorithme
- Référence : 2000-01-06 18:14 UTC = nouvelle lune
- Cycle lunaire : 29.530588 jours
- Phase 0-1 → nom symbolique (nouvelle / premier-croissant / premier-quartier / gibbeuse-croissante / pleine / gibbeuse-decroissante / dernier-quartier / dernier-croissant)
- Illumination 0-1 = (1 - cos(phase × 2π)) / 2

## Formule score activité
```
night_factor = 1.0 si heure < 6 ou > 20, sinon 0.4
activite = illumination × 70 × night_factor + 30
+15 bonus si solunar_peak (pleine/nouvelle)
```

## Résultat observé (2026-04-19, 7h)
- phase_fraction=0.18, phase_name=premier-croissant
- illumination=33%, is_night=False
- score=32.3 (activité modérée, jour)

## Test SELF-AUDIT
`test_influence_lunaire.py` (23e suite)

## Intégration
- Bundle champ `influence_lunaire`
- Axe `lunar_influence_score` dans SCORE-GLOBAL-REALITY (poids 2%)

## Limites
- Approximation globale (pas de correction latitude/altitude)
- Théorie solunar = heuristique cynégétique, preuve scientifique limitée
