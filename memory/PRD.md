# PRD — BIONIC OS V20-SUPRA / TERRITOIRE
## Last updated : 2026-04-22 — PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω (X180-AMENDEMENT-FINAL) CLOS

## Protocol
BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX
Language : FR. Persona : formel, martial, institutionnel.
Aucun testing subagent autorisé.
Waypoint canonique exclusif : **48.206657 / -68.382422**
Registre V30 SHA-256 verrouillé : `27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c`

## Architecture canonique
- Backend FastAPI (V30 LOCKED) + post_smoothing externe `organic_corridor_smoother.py`
- Frontend React + Leaflet (`BionicLayersV8.jsx`, `renduOmegaStore.js`)
- CI_STATUS_Ω runtime dashboard (`routes/ci_status_omega.py`, 6 suites / 65 tests sentinelles)

## Phases complétées
| Phase | Statut |
| --- | --- |
| X20 / X30 PIPELINE_AUDIT | DONE |
| X40 OPS_RESTORATION (zones 404) | DONE |
| X50 OPS_REFUS_VALIDATION (wind, nutrition, popups) | DONE |
| X70 SUPRA_VENT_VISUEL (compass + cone) | DONE |
| X80 SUPRA_VERITE_TERRAIN (waypoint officiel + probes) | DONE |
| X120 SUPRA_RENDU_TERRITOIRE (contamination #FF0000 0.18, popups) | DONE |
| X150 / X170 CORRIDORS_RENDU + REPAIR frontend | DONE |
| X180 CORRIDORS_REPAIR AMENDEMENT-FINAL | DONE (2026-04-22) |
| X195 RAPATRIEMENT_TERRITOIRE_V7_ULTIME AMENDEMENT-ABSOLU | DONE (2026-04-22) |
| **X197 COMPARATIF_TERRITOIRE_Ω AMENDEMENT-ABSOLU** | **DONE (2026-04-22)** |

## X197 livrables
- Rapport : `/app/memory/TERRITOIRE_V7_vs_TERRITOIRE_ACTUEL_Ω.md` (SHA-256 `94974bc3cf505a23809206fe51aa99952f2348a97d167aafc36c94a219c68a62`)
- YAML DIFF MATRIX : `/app/memory/V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml` (SHA-256 `2325a61eeac107df3c1f66b7be0dd3fcae075313cb2c639c07b4a0ee32049d63`) — **45 divergences**, 12 catégories, triplets `clé/V7/actuel/impact` + sévérité + source + action X200 recommandée
- Impacts : 23 PERTE, 3 INVERSION, 4 SIMPLIFICATION, 2 DÉGRADATION, 2 AJOUT, 4 PARITE_PARTIELLE, 2 PARITE_FRONTEND, 1 PARITE, 2 RENOMMAGE, 2 DIVERGENCE
- Sévérités : 12 CRITIQUE, 13 MAJEURE, 8 MODEREE, 6 MINEURE
- Base du futur CONTRAT RENDUΩ-RÉSEAU VEINEUX (phase X200)

## X195 livrables
- Archive V7 ULTIME rapatriée : `/app/memory/V7_ULTIME_EXPORT/V7_ULTIME_FULL.tar.gz` (156 entrées, 2.06 MB)
- SHA-256 : `c8c2f6a3339b3fb5624d3cc640174ed6fc07e10d4c519bb9f2341a788d1dc29f`
- Endpoints HTTPS : `/api/v7-ultime-export/{status,download,manifest,list,sha256}`
- Rapport comparatif V7 vs V20-X180 : `/app/memory/V7_vs_V20_X180_COMPARATIF_Ω.md` (SHA-256 `c748513bddf5b085e7ed3df5ffac1846f24f611b9edc6c0a4ba57fa94db3b0f4`)
- Verrou Pytest smoother 9 passes : `/app/backend/tests/test_smoother_x180_verrou.py` → **24/24 PASS**
- Contenu rapatrié (aucune simplification) : spatial_engine_v7, supra_engine_v7, nutrition_engine_v7, access_clarity_engine_v7, corridors_v10, alimentation_v1/v2, repos_v1, carte2027_engine, salines_ultime_engine, canada_v72, LEGACY_ACCESS_AFFUTS, composants frontend V7

## Interdictions X195 respectées
- Engine V30 non modifié
- Panneau DIAGNOSTIC-CORRIDORS-Ω NON activé
- Données V7 ULTIME non transformées
- Aucun filtrage / simplification

## X180 livrables
- Test Jest `phase_x170_corridors_biologie.test.js` : **8/8 PASS** (triple pipeline + constantes RENDU-Ω)
- Suite sentinelle globale : **65/65 PASS**, 6 suites
- `organic_corridor_smoother.py` AMENDEMENT-FINAL :
  - 9 passes (trim / smooth / despike / eliminate_fuite / segment_max / eco_alignment / ia_attractors / re-smooth / re-densify)
  - 5 profils espèces (chevreuil/orignal/wapiti/ours/dindon) avec angle_max, segment_max, water_tolerance, slope_max, human_avoidance
  - 6 types zones vitales (salines, alimentation, repos, rut, thermique, humide)
  - Endpoint `/smoother-status` institutionnel
- Conformité mesurée waypoint officiel : angle **27.04°** / segment **8.95 m** / zéro demi-tour
- CI_STATUS_Ω mis à jour (6 suites, 65 tests)
- Rapport PEDIGREE `/app/memory/PEDIGREE_DONNEES_X180.md` (DEM LiDAR, EarthData Hydro, ForestDensity, MicroRelief, IA Vision, species_profile, cartes coût/probabilité/attractivité)

## Backlog (attente directive)
- P1 : validation utilisateur visuelle corridors avec couche CORRIDORS active à zoom ≥ 13 sur waypoint officiel
- P2 : tests Pytest backend dédiés au smoother (passes 1-8) pour verrou institutionnel

## Tests
- Jest via `craco test` : 6/6 suites, 65/65 tests verts
- Backend `curl /api/v20/territoire/corridors-organic/generate` → HTTP 200, smoother_applied OK
- `curl /api/omega/ci-status` → 6 suites détectées, sentinelles alignées

## Contrats verrouillés
- Engine V30 : aucune mutation
- Post-processeur externe : registration AVANT `engine_ia_corridors_organic_omega.router` (priorité FastAPI first-match)
- Non-régression : en l'absence de signaux terrain/IA, path inchangé hors géométrie RENDU-Ω
