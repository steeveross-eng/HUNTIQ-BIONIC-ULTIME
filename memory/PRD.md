# HUNTIQ-V6 — PRD (Product Requirements Document)
## GOLDEN-BCE-4X / STEEVE-MAX

---

## Projet
Application HUNTIQ-V6 — Plateforme de scoring ecologique multi-moteurs pour la gestion cynegetique.

## Architecture
- **Backend:** FastAPI
- **Frontend:** React
- **DB:** MongoDB (huntiq_v6, 18+ collections incl. bsaa_campaigns)
- **Branche active:** `STEEVE-MAX-x3200-V6-CORE`

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200-x3203 | Migration core/ et encapsulation | COMPLETE |
| x3204 | Cartographie fonctionnelle pipeline CORE | COMPLETE |
| x3205 | Normalisation scientifique (module common/) | COMPLETE |
| x3300 | Migration score_consolide dans core/ | COMPLETE |
| x3400 | Interconnexion totale frontend (18 fichiers) | COMPLETE |
| x4000-SUPRA | Creation 17 moteurs squelettes (Option A) | CERTIFIE |
| x4100 | Integration scientifique 22 moteurs (Option C) | CERTIFIE |
| **x4500-ULTRA** | **Reconstruction PREVIEW + BSAA + nettoyage** | **CERTIFIE** |

## Etat actuel

### Score de reference
- **Point test:** (46.8, -71.2), CERF, mois 10
- **Score:** **57.6** (22 moteurs, Option C: CORE 60% / Nouveaux 40%)

### 22 moteurs actifs
- **CORE (60%):** alimentation, repos, corridors_v10, alimentation_v2, pression
- **CORE++ (17%):** hydro, thermal, ndvi_vegetation, weather, temporal, habitat, ecosystem
- **CORE+++ (12%):** behavior, risk, opportunity, attractors, scenario
- **BIONIC-OS (9%):** simulation, multi_species, trajets, visibility, learning

### BSAA
- 9 endpoints API sous `/api/bsaa/*`
- 5 plateformes (Facebook, Instagram, TikTok, YouTube, Reddit)
- 8 templates de contenu (FR/EN)
- Page frontend `/bsaa` avec dashboard, generateur, analytics

### PREVIEW
- Frontend: 0 erreurs webpack
- Backend: 22 moteurs + BSAA actifs
- Pages fonctionnelles: HOME, DASHBOARD, MAP, SALINE, BSAA, TRIPS, etc.

## Contraintes critiques
- **Merge/MASTER_SWITCH: EXCLUSIVITE STEEVE-MAX** — Aucun merge ni activation sans autorisation explicite
- **Score consolide 57.6: Reference officielle** — Aucune modification sans directive

## Taches futures (en attente de directive Steeve)
- Validation visuelle complete du PREVIEW
- Prochaine directive numerotee
- Merge final vers main (bloque sur validation Steeve)
