# HUNTIQ-V6 — PRD
## Protocole BCE-4X | BIONIC GOLDEN | STEEVE-MAX
## Branche souveraine: STEEVE-MAX-x3200-V6-CORE

## Etat courant

### EXECUTE ET COMMITE (branche souveraine)
- Phase A+B: Purge V1-V5 (MapInteractionLayer, BionicCorridorsV6Layer, AlimentationV2Layer)
- GOVERNANCE.md: Sections 1-15 completes (GOLDEN + UI/IU Section 14 + Non-regression Section 15)
- access_engine_v6: Pipeline complet, 30/30 tests, API operationnelle
- STANDARD GOLDEN UI/IU v2.0: Positionnement DOM direct, certification complete
- **OPTIMISATION GOLDEN ACCES** (Directive STEEVE-MAX 2026-03-29):
  - BUG CRITIQUE CORRIGE: Overpass retournait ways AVANT nodes → 0 aretes → 0% sentier
  - Correction: deux passes (nodes d'abord, ways ensuite) → 100% trail quand sentiers dispo
  - Multiplicateurs GOLDEN: trail x0.1, hybrid x0.5, off-trail x3.0, non-conformant x10.0
  - Requete Overpass elargie (tracktype, chemins de coupe, debardage)
  - Interpolation Bresenham + rayon d'influence sentier 3 cellules

### EN ATTENTE VALIDATION STEEVE-MAX
- Architecture ULTRA-MAX++ P1: architecture/ultra_max_pp_architecture.md

### DETTE TECHNIQUE
- Firewall ULTRA-MAX++ (P1 OUVERT, architecture soumise)
- Donnees terrain reelles (DEM, canopy) — simulees par hash

### GELE
- BSAA-2, Phase 2D, pression historique
- Merge main: STRICTEMENT INTERDIT
