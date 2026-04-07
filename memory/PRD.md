# PRD — HUNTIQ BIONIC V6+ | BCE-4X GOLDEN V6+
# ============================================================
# Autorite: COMMANDANT STEEVE-MAX
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL | 12 Validateurs
# Branche: BIONIC_REWRITE_P0 (VERITE INSTITUTIONNELLE)
# Certification AUDIT INSTITUTIONNEL: ACCORDEE (2026-04-07)
# ============================================================

## Objectif
Rewrite P0 des moteurs de scoring geospatiaux (FastAPI + React/Leaflet)
Gouvernance stricte BCE-4X GOLDEN V6+.

## Architecture
- Backend: FastAPI, GeoSpatial (Shapely), cache OSM (235 polygones urbains)
- Frontend: React, Leaflet (react-leaflet)
- Auth: bcrypt + JWT HS256 24h via auth_engine/v1
- Gouvernance: BCE-4X-GLOBAL-PLUS-TOTAL, Gatekeeper, SHA256 sealing, 12 validateurs
- Branche: BIONIC_REWRITE_P0

## Corrections Session Actuelle
1. Exclusion urbaine BCE-4X (backend + frontend)
2. UX: Legende/zoom NoControlOverlap
3. UX: Grille Vegetation/Hydrologie cote a cote
4. UX: GUIDE PRO en tete de hierarchie
5. Code mort StandsMapLayer + faux positif Gatekeeper
6. Admin Premium: Grille 3x3, auth fixee, hierarchie
7. AUTH-USAGER: Audit 18 endpoints, certification CONFORME

## Audits Livres
- AUDIT_INSTITUTIONNEL_TOTAL.md
- AUDIT_VALIDATION_URBAINE.md
- BCE4X_GLOBAL_PLUS_TOTAL_VALIDATION.md
- ADMIN_PREMIUM_VALIDATION.md
- BCE4X_AUTH_USAGER_VALIDATION.md

## Taches Restantes
### P1 (AUTORISEE apres certification AUTH-USAGER)
- Harmonisation x1000% + Test export PDF
### P2 (GELE)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
### INTERDIT
- Merge BIONIC_REWRITE_P0 → main
