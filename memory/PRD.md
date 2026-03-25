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
| x4500-ULTRA | Reconstruction PREVIEW + BSAA + nettoyage | CERTIFIE |
| **x4515** | **PANEL_FIX_MODE — PinnablePanel wrapper** | **CERTIFIE** |

## Score de reference
- **57.6** (22 moteurs, Option C: CORE 60% / Nouveaux 40%)
- Point test: (46.8, -71.2), CERF, mois 10

## Composant PinnablePanel (x4515)
Wrapper reutilisable applique a:
- TerritoryAnalysisPanel (analyse territoire)
- BionicZoneDiagnosticPanel (diagnostics zones)
- GuidedRoutePanel (parcours guide)
- NutritionAnalysisModal (analyse alimentation/saline)

Fonctionnalites:
- Pin/Unpin (fixation flottante)
- Drag (deplacement par en-tete)
- Resize (coin inferieur droit)
- Expand (pleine page)
- Scroll interne automatique
- z-index 2000 en mode fixe

## Contraintes critiques
- Merge/MASTER_SWITCH: EXCLUSIVITE STEEVE-MAX
- Score consolide 57.6: Reference officielle inchangeable sans directive

## Taches futures (en attente de directive Steeve)
- Validation visuelle complete du PREVIEW
- Prochaine directive numerotee
