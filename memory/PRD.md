# PRD — HUNTIQ BIONIC V6+ | BCE-4X GOLDEN V6+
# ============================================================
# Autorite: COMMANDANT STEEVE-MAX
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL | 10 Validateurs
# Branche: BIONIC_REWRITE_P0 (VERITE INSTITUTIONNELLE)
# ============================================================

## Objectif Principal
Rewrite P0 des moteurs de scoring geospatiaux (FastAPI + React/Leaflet)
avec gouvernance stricte BCE-4X GOLDEN V6+.

## Architecture
- Backend: FastAPI, GeoSpatial (Shapely), cache OSM (235 polygones urbains)
- Frontend: React, Leaflet (react-leaflet)
- Gouvernance: BCE-4X-GLOBAL-PLUS-TOTAL, Gatekeeper pre-commit, SHA256 sealing
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
- BionicCorridorsV6Layer, ContaminationOverlayLayer, StandsMapLayer
- BionicLegend (repositionnee: left:60px, maxHeight:340px — NoControlOverlap)
- PedagogieModule / GUIDE PRO overlay
- ExclusionOverlayLayer

### Gouvernance BCE-4X
- 5 fichiers institutionnels scelles SHA256
- Gatekeeper pre-commit actif (21 controles)
- Branche main INTERDITE de merge
- 10 validateurs BCE-4X-GLOBAL-PLUS-TOTAL actives

### Corrections P0 Completees (Session actuelle)
- CORRECTION VIOLATION CRITIQUE: Exclusion urbaine BCE-4X
  - Backend: check_point_exclusions dans contamination-zones + orchestrate
  - Frontend: Guard ContaminationOverlayLayer
- CORRECTION UX: Legende/zoom NoControlOverlap (repositionnement + maxHeight)
- CORRECTION UX: Grille Vegetation/Hydrologie (cote a cote grid-cols-2)
- CORRECTION UX: GUIDE PRO remonte en tete de hierarchie
- Nettoyage code mort StandsMapLayer + correction faux positif Gatekeeper CSS

## Audits Livres
- AUDIT INSTITUTIONNEL TOTAL — /app/memory/AUDIT_INSTITUTIONNEL_TOTAL.md
- AUDIT VALIDATION URBAINE — /app/memory/AUDIT_VALIDATION_URBAINE.md
- BCE-4X-GLOBAL-PLUS-TOTAL VALIDATION — /app/memory/BCE4X_GLOBAL_PLUS_TOTAL_VALIDATION.md

## Taches Restantes

### P0
- Certification finale de l'audit par le Commandant

### P1 (Gele)
- Harmonisation x1000% + Test export PDF

### P2 (Gele)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation

### INTERDIT
- Merge BIONIC_REWRITE_P0 → main
