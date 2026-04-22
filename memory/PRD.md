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
| **X180 CORRIDORS_REPAIR AMENDEMENT-FINAL** | **DONE (2026-04-22)** |

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
