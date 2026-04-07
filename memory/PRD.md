# PRD — HUNTIQ BIONIC V6+ | BCE-4X GOLDEN V6+
# ============================================================
# Autorite: COMMANDANT STEEVE-MAX
# Protocole: BCE-4X GOLDEN V6+ | ZERO LOSS | ZERO REGRESSION
# Branche: BIONIC_REWRITE_P0 (VERITE INSTITUTIONNELLE)
# ============================================================

## Objectif Principal
Rewrite P0 des moteurs de scoring geospatiaux (FastAPI + React/Leaflet)
avec gouvernance stricte BCE-4X GOLDEN V6+.

## Architecture
- Backend: FastAPI, GeoSpatial (Shapely), cache OSM
- Frontend: React, Leaflet (react-leaflet)
- Gouvernance: BCE-4X, Gatekeeper pre-commit, SHA256 sealing
- Branche active: BIONIC_REWRITE_P0

## Ce qui est implemente

### Moteurs V6 Operationnels
- Hunt Orchestrator (contamination-zones, orchestrate, scent-zone)
- Corridor Analysis V6 (analyze-full)
- Nutrition Intelligence (supra-panel)
- BDRE Scoring
- Relocation Engine
- Intelligence V6 Dashboard

### Couches Frontend
- BionicCorridorsV6Layer (corridors + zones)
- ContaminationOverlayLayer (BDRE pedagogique)
- StandsMapLayer (affuts)
- BionicLegend (legende unique autorisee)
- PedagogieModule / GUIDE PRO overlay
- ExclusionOverlayLayer

### Gouvernance BCE-4X
- Fichiers institutionnels: BCE4X_GLOBAL_LOCK.json, STEEVE_MAX_RULES_GLOBAL.md,
  STEEVE_MAX_VALIDATOR_GLOBAL.js, GATEKEEPER_PIPELINE.js, pre-commit
- SHA256 sealing actif
- Pre-commit hook Gatekeeper actif
- Branche main INTERDITE de merge

### Corrections P0 Completees
- Neutralisation legendes parasites (tous layers)
- GUIDE PRO (ex-BDRE) — renomme, repositionne, overlap corrige
- Rollback BIONIC-ULTIME-INIT → BIONIC_REWRITE_P0
- CORRECTION VIOLATION CRITIQUE: Exclusion urbaine BCE-4X
  - Injection check_point_exclusions dans contamination-zones
  - Injection check_point_exclusions dans orchestrate
  - Guard frontend ContaminationOverlayLayer
  - Nettoyage code mort StandsMapLayer
  - Correction faux positif Gatekeeper (CSS regex)

## Audits Livres
- AUDIT INSTITUTIONNEL TOTAL (6 sections) — /app/memory/AUDIT_INSTITUTIONNEL_TOTAL.md
- AUDIT VALIDATION URBAINE — /app/memory/AUDIT_VALIDATION_URBAINE.md

## Taches Restantes

### P0 (Bloquant)
- Certification finale de l'AUDIT INSTITUTIONNEL TOTAL (en attente validation Commandant)

### P1 (En attente validation)
- Harmonisation x1000% + Test export PDF (GELE)

### P2 (Futur)
- M5 Offline Mode Ultra (GELE)
- BSAA-2 Social Ads Automation (GELE)

### INTERDIT
- Merge BIONIC_REWRITE_P0 → main
