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
- SUPRA_ONGLETS_AUDIT_COMPLET.md (2026-02-07) — 6 entites, 29 moteurs, 14 ecarts
- SUPRA_ECARTS_DETAILLES.md (2026-02-07) — 14 ecarts + Impact Matrix + Test Matrix (20 tests) + Roadmap P0-R
- SUPRA_BASELINES_INSTITUTIONNELLES.md (2026-02-07) — Scores, flux, performance
- SUPRA_DEPENDANCES_BACKEND.md (2026-02-07) — 29 moteurs, fragilites, propagation
- SUPRA_RISQUES_INSTITUTIONNELS.md (2026-02-07) — 29 risques (7 critiques)

## Taches Restantes
### P0 (EN COURS — EN ATTENTE VALIDATION)
- Audit SUPRA complet: LIVRE, 3 complements LIVRES
- Reconstruction SUPRA x1000%: STRICTEMENT INTERDITE jusqu'a validation des 3 complements
### P1 (GELEE — apres reconstruction SUPRA)
- Harmonisation x1000% + Test export PDF
### P2 (GELE)
- Deprecation 9 endpoints obsoletes AUTH-USAGER
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
### INTERDIT
- Merge BIONIC_REWRITE_P0 → main
