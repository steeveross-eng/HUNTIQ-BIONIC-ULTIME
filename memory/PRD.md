# HUNTIQ-V6 — PRD (Product Requirements Document)
## GOLDEN-BCE-4X / STEEVE-MAX

---

## Projet
Application HUNTIQ-V6 — Plateforme de scoring ecologique multi-moteurs pour la gestion cynegretique.

## Architecture
- **Backend:** FastAPI
- **Frontend:** React
- **DB:** MongoDB (huntiq_v6, 18 collections)
- **Branche active:** `STEEVE-MAX-x3200-V6-CORE`

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200 | Creation branche + arborescence core/ | COMPLETE |
| x3201 | Encapsulation 5 moteurs critiques dans core/scoring_pipeline/ | COMPLETE |
| x3202 | Bascule 17 imports vers core/ | COMPLETE |
| x3203 | Retrait anciens moteurs modules/ | COMPLETE |
| x3204 | Cartographie fonctionnelle pipeline CORE | COMPLETE |
| x3205 | Normalisation scientifique (module common/) | COMPLETE |
| x3300 | Migration score_consolide dans core/ | COMPLETE |
| x3400 | Interconnexion totale frontend (18 fichiers) | COMPLETE |
| **x4000-SUPRA** | **Creation 17 moteurs squelettes (Option A)** | **CERTIFIE** |

## Etat actuel du scoring pipeline

### 5 moteurs CORE (actifs dans score_consolide)
- alimentation_v1, repos_v1, corridors_v10, alimentation_v2, pression_v1
- Score consolide de reference: **56.2** (point 46.8, -71.2, CERF, mois 10)

### 17 nouveaux moteurs (NON integres — Option A)
- **CORE++ (7):** hydro_v1, thermal_v1, ndvi_vegetation_v1, weather_v1, temporal_v1, habitat_v1, ecosystem_v1
- **CORE+++ (5):** behavior_v1, risk_v1, opportunity_v1, attractors_v1, scenario_v1
- **BIONIC-OS (5):** simulation_v1, multi_species_v1, trajets_v1, visibility_v1, learning_v1

## Prochaines directives (en attente de validation Steeve)
- **x4100:** Integration scientifique des 17 moteurs dans score_consolide.py
- **x4500-ULTRA:** Directive majeure suivante
- **BSAA:** Implementation module Social Ads Automation (P3)
- **Merge final:** STEEVE-MAX-x3200-V6-CORE vers main
