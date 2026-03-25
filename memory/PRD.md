# HUNTIQ-V6 — PRD
## GOLDEN-BCE-4X / STEEVE-MAX

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200-x3203 | Migration core/ et encapsulation | COMPLETE |
| x3204-x3205 | Cartographie + Normalisation scientifique | COMPLETE |
| x3300 | Migration score_consolide dans core/ | COMPLETE |
| x3400 | Interconnexion totale frontend | COMPLETE |
| x4000-SUPRA | 17 moteurs squelettes (Option A) | CERTIFIE |
| x4100 | Integration scientifique 22 moteurs (Option C) | CERTIFIE |
| x4500-ULTRA | Reconstruction PREVIEW + BSAA | CERTIFIE |
| **x4515-FIX** | **PinnablePanel V2 — 8 panneaux conformes** | **CERTIFIE** |

## Score: 57.6 (22 moteurs, Option C)

## PinnablePanel V2 (x4515-FIX)
8 panneaux couverts:
1. TerritoryAnalysisPanel (territoire)
2. BionicZoneDiagnosticPanel (diagnostics)
3. GuidedRoutePanel (parcours guide)
4. NutritionPanel (alimentation/nutrition) — PinnablePanel wrapper
5. AmenagementPanel (salines/affuts)
6. CorridorsEcologyPanel (corridors V10)
7. DiagnosticExclusionsPanel (exclusions spatiales)
8. ZoneInfoPanel (info zone)

Fonctionnalites:
- Pin/Unpin (fixer/detacher)
- Pleine page 100vw x 100vh, fond #fafafa, texte #111/#222, 16px min
- Drag (deplacement), Resize (redimensionnement)
- Scroll interne fluide, aucun debordement
- Hierarchie visuelle renforcee en mode expand
- Escape pour quitter pleine page

## Validation visuelle (25 mars 2026)
- PREVIEW rebuild complet + cache purge
- DiagnosticExclusionsPanel: Mode Normal OK, Pin OK (flottant), Expand OK (1920x800)
- Boutons Pin/Expand/Close visibles et fonctionnels
- Texte #111/#222, fond #fafafa en mode Expand
- Score backend 22 moteurs actif

## Architecture
- Branche: STEEVE-MAX-x3200-V6-CORE
- Frontend: React (Craco/Webpack)
- Backend: FastAPI
- Composant cle: PinnablePanel.jsx (321 lignes)
- Overlay flottant: BionicZoneDiagnosticPanel extrait du sidebar w-80

## Prochaines etapes
- Attente directive STEEVE-MAX
- BSAA-2 (implementation) — apres validation
- Merge vers main — gere exclusivement par STEEVE-MAX
