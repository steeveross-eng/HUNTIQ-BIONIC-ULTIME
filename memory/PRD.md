# HUNTIQ-V6 — PRD (Product Requirements Document)
## GOLDEN-BCE-4X / STEEVE-MAX

---

## Projet
Application HUNTIQ-V6 — Plateforme de scoring ecologique multi-moteurs pour la gestion cynegetique.

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
| x4000-SUPRA | Creation 17 moteurs squelettes (Option A) | CERTIFIE |
| **x4100** | **Integration scientifique 22 moteurs (Option C: CORE 60%/Nouveaux 40%)** | **CERTIFIE** |

## Etat actuel du scoring pipeline

### Score de reference
- **Point test:** (46.8, -71.2), CERF, mois 10
- **Score x4100:** **57.6** (22 moteurs, Option C)
- **Ancien score x4000:** 56.2 (5 moteurs CORE)
- **Delta:** +1.4 (+2.5%)

### 22 moteurs actifs
- **CORE (60%):** alimentation, repos, corridors_v10, alimentation_v2, pression
- **CORE++ (17%):** hydro, thermal, ndvi_vegetation, weather, temporal, habitat, ecosystem
- **CORE+++ (12%):** behavior, risk, opportunity, attractors, scenario
- **BIONIC-OS (9%):** simulation, multi_species, trajets, visibility, learning

## Prochaines directives
- **x4500-ULTRA:** Reconstruction visuelle complete (overlays, panneaux, contenus, BSAA)
  - Reconstruction visuels (overlays, styles, icones, panneaux)
  - Reconstruction panneaux affuts, salines, diagnostics
  - Reconstruction contenus narratifs et pedagogiques
  - Implementation BSAA (backend + generation de contenus)
  - Aucune relique Work1
  - Tout modernise et reinjecte dans V6-CORE

## Taches futures
- Merge final STEEVE-MAX-x3200-V6-CORE vers main
- Deblocage MASTER_SWITCH pour release publique
