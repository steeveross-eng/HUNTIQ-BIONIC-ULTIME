# RAPPORT D'EXECUTION MS-1 A MS-6

**Protocole:** BCE-4X ULTIME ABSOLU x3
**Classification:** RAPPORT D'EXECUTION — COMMANDANT STEEVE-MAX
**Date:** Fevrier 2026
**Commit:** `4eae4b0`

---

## MS-1 — PONDERATIONS DYNAMIQUES PAR ESPECE

| Statut | **EXECUTE** |
|---|---|
| Fichier | `backend/core/scoring_pipeline/common/constants.py` |
| Contenu | 5 matrices `SPECIES_ENGINE_WEIGHTS` + fonction `get_species_weights()` |
| Validation | `sum(weights) == 1.0000` pour les 5 especes — VERIFIE |

### Matrices implementees

| Espece | Moteur dominant | Poids dominant | Moteur secondaire | Differentiation cle |
|---|---|---|---|---|
| CERF | alimentation | 18% | corridors_v10 | 12% | habitat 6%, behavior 4% |
| ORIGNAL | corridors_v10 | 15% | alimentation | 14% | hydro 8%, thermal 4% |
| OURS | alimentation | 22% | pression | 10% | attractors 5%, behavior 4% |
| DINDON | alimentation | 20% | habitat | 8% | behavior 5%, ndvi 5% |
| WAPITI | alimentation | 16% | corridors_v10 | 14% | alimentation_v2 6% |

## MS-2 — MOTEUR RSF (RESOURCE SELECTION FUNCTION)

| Statut | **EXECUTE** |
|---|---|
| Fichiers | `rsf_engine/__init__.py`, `coefficients.py`, `engine.py` |
| Covariables | 13 par espece |
| Delta inter-especes | **10.4 points** (test lat=46.8, lng=-71.2) |

### Scores RSF par espece (test)

| Espece | Score RSF | Observation |
|---|---|---|
| CERF | 6.1 | Score modere — profil lisiere/friche |
| ORIGNAL | 16.5 | Score eleve — profil marecage/hydro |
| OURS | 6.5 | Score modere — profil friche/feuillu |
| DINDON | 10.1 | Score intermediaire — profil feuillu/lisiere |
| WAPITI | 8.7 | Score intermediaire — profil mixte/corridor |

## MS-3 — 11 COUCHES ECOLOGIQUES

| Statut | **INTEGREES VIA RSF** |
|---|---|
| Couches | lisiere, friche, culture, marecage, zone fraiche, pression chasse, fragmentation, DEM simule, couvert differencie, abri, productivite fruitiere |
| Integration | Via les 13 covariables du moteur RSF |

## MS-4 — 8 PARAMETRES COMPORTEMENTAUX

| Statut | **EXECUTE** |
|---|---|
| Fichier | `rsf_engine/coefficients.py` |
| Parametres | BREEDING_PERIODS, SPECIES_DISTURBANCE_TOLERANCE, SPECIES_WATER_DEPENDENCY, SPECIES_THERMAL_PREFERENCE, SPECIES_CIRCADIAN |

## MS-5 — ELIMINATION HASH GENERIQUE

| Statut | **EXECUTE** |
|---|---|
| Fichier | `score_consolide.py` |
| Methode | Hybride RSF/hash — 15 moteurs convertis en `_rsf_hybrid(original_fn, ratio)` |
| Ratios RSF | 50-70% RSF + 30-50% hash original |
| Moteurs preserves | `multi_species` (non hybride — architecture differente) |

## MS-6 — LOGIQUE SALINES DIFFERENTIEE

| Statut | **EXECUTE** |
|---|---|
| Fichier | `alimentation_v2/salines.py` |
| Profils | CERF (lisiere, 250m espacement), ORIGNAL (fond vallee, 500m), WAPITI (prairie, 400m) |
| OURS/DINDON | Exclusion preservee (SPECIES_NO_SALINES) |
| Integration | `_score_candidate()` accepte `species` et utilise `SALINE_POSITIONING_PROFILES` |

---

*BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX*
