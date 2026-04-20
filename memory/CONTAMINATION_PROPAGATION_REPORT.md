# CONTAMINATION_PROPAGATION_REPORT — Phase X-C

> **Directive :** Phase X-C Section II — Intégration profonde contamination_v2
> **Date :** 2026-04-19

## 1. Chaîne de propagation

```
contamination_v2 = compute_contamination_v2(contamination_v1, lat, lon, species)
         │
         ├─→ compute_habitat_supra(terrain, contamination_v2=...)
         │       malus habitat : ELEVE=-12, MODERE=-6, FAIBLE=-2
         │
         ├─→ compute_population_dynamics(species, contamination_v2=...)
         │       mortalité +0.08/+0.04/+0.01
         │       tendance_10ans -0.10/-0.05/-0.01
         │
         ├─→ compute_stress_anthropique(terrain, hour, contamination_v2=...)
         │       malus tranquillité (stress sanitaire) : -15/-8/-3
         │
         └─→ SCORE-GLOBAL-REALITY-Ω V3-DYNAMIC
                 contamination_malus = contamination_v2.score (0-100)
```

## 2. Preuve live (Estrie-Sud CWD ELEVE)

```bash
$ curl /api/v20/territoire/bundle?lat=45.1&lon=-72.8&species=chevreuil
→ score_global: 62.4 BON
  habitat.contamination_v2_impact: { cwd_risk: ELEVE, distance_km: 11.1, malus_applied: 12.0 }
  population.contamination_v2_impact: { cwd_risk: ELEVE, mortality_bonus: +0.08, tendance_penalty: -0.10 }
  stress.contamination_v2_impact: { cwd_risk: ELEVE, sanitary_malus: 15.0 }
```

## 3. Table d'impact par zone

| Zone | Distance MDC | CWD Risk | Δ Habitat | Δ Mortalité | Δ Tranquillité |
|------|--------------|----------|-----------|-------------|----------------|
| Estrie-Sud (Frelighsburg) | < 20 km | ELEVE | –12 | +0.08 | –15 |
| Montérégie Nord | 20-60 km | MODERE | –6 | +0.04 | –8 |
| Mauricie | 60-150 km | FAIBLE | –2 | +0.01 | –3 |
| Saguenay | > 150 km | TRES-FAIBLE | 0 | 0 | 0 |

## 4. Validation automatique

`test_contamination_propagation.py` vérifie les 3 propagations avec un terrain
synthétique et `cv2_high={cwd_risk: ELEVE}` vs `cv2_none=None` :

```
OK: propagation contamination_v2 (habitat Δ=12.0, pop Δmort=+0.08, stress Δtranq=15.0)
```

## 5. Sealed
```
SEALED  — Phase X-C — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
