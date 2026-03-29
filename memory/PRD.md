# HUNTIQ-V6 — PRD
## Protocole BCE-4X | BIONIC GOLDEN | STEEVE-MAX

## Branche souveraine: STEEVE-MAX-x3200-V6-CORE
## Work1: GELEE

## Etat courant

### EXECUTE ET COMMITE (branche souveraine)
- Phase A: MapInteractionLayer GPS-only
- Phase B: BionicCorridorsV6Layer alimentation centroids exclus + AlimentationV2Layer useEffect
- GOVERNANCE.md: PROTOCOLE BIONIC GOLDEN (11 sections)
- Architecture access_engine_v6: document complet valide par STEEVE-MAX
- STANDARD GOLDEN Legende: repositionnee en topleft (StandsMapLayer.jsx)
- **access_engine_v6**: Implementation complete backend + frontend + tests (43/43 PASSES)
- **STANDARD GOLDEN UI/IU v2.0**: Positionnement dynamique intelligent
  - Cause racine: L.control() Leaflet = DOM separe des React elements
  - Correction: Ancrage DOM direct au conteneur carte, position:absolute
  - Tests: 4 resolutions + 6 modules + 4 interactions = 14 tests PASS
  - Certification complete: audit/ui_golden_legende_certification.md

### EN ATTENTE VALIDATION STEEVE-MAX
- Section 14 GOVERNANCE (14.1-14.9): audit/draft_governance_section14_final.md
- Clause non-regression (15.1-15.6): audit/draft_non_regression_clause_final.md
- Rapport certification GOLDEN UI/IU: audit/ui_golden_legende_certification.md

### DETTE TECHNIQUE STRUCTURELLE
- Firewall ULTRA-MAX++ (Shapely geo-fencing) a reimplementer sous GOLDEN
- Cache terrain persistant .json.gz (Redis recommande pour production)
- Donnees terrain reelles (DEM, canopy) — actuellement simulees par hash

### GELE
- BSAA-2, Phase 2D, pression historique
- Merge main: STRICTEMENT INTERDIT
