# Test Credentials — BIONIC OS V20-SUPRA

## Admin (Commandant STEEVE-MAX)
- **Email** : `steeve-max-capture@huntiq.com`
- **Password** : `Saturn5858*`
- **Rôle** : Admin institutionnel (accès self-audit, registry-lock, captures)

## Endpoints d'audit (sans auth)
- `GET /api/v20/territoire/self-audit` — exécute les 60 suites
- `GET /api/v20/territoire/self-audit/last` — dernier résultat
- `GET /api/v20/territoire/registry-lock` — registry scellé V29

## Admin Premium Page (`/admin-premium`) — Ordre n°41
- **Login form** : `POST /api/auth/login` avec `email=admin@huntiq.com` + password
- **Bypass client-side** (captures institutionnelles Playwright) :
  `localStorage.setItem('admin_premium_authenticated', 'true')`
- **Section Pilotage BCE-4X Ω** : data-testid `pilotage-bce4x-dashboard`

## GIS Reception API (Ordre n°42_BIS) — ADMIN_PREMIUM_ONLY
- **Header auth** : `X-Commandant-Token: STEEVE-MAX-X42BIS-GIS-RECEPTION-EXPLICIT`
- **Endpoint upload** : `POST /api/v30/admin-premium/gis/upload/{slot_id}`
- **Slots autorisés** : `FORET_MFFP_Ω`, `SOL_IRDA_Ω`, `CHASSE_ZEC_SEPAQ_Ω`,
  `ROUTES_MTQ_SECONDAIRES_Ω`, `LIMITES_TERRITORIALES_FINES_Ω`, `PRESSION_HUMAINE_Ω`
- **Token env** : `GIS_RECEPTION_COMMANDANT_TOKEN` (backend/.env)
- **Validators** : check_format · check_size · check_integrity (SHA-256 + zipfile.testzip)
- **Codes HTTP** : 200=LOADED · 401=token invalide · 404=slot inconnu · 400=filename unsafe · 413=too_large · 422=QUARANTINED

## AdminGISReceptionPanel UI (Ordre n°43)
- **Route** : `/admin-premium` → menu "Pilotage BCE-4X Ω" → onglet "RÉCEPTION GIS Ω"
- **data-testid clés** :
  - `pilotage-tab-gis-reception` (onglet)
  - `gis-reception-panel` (root)
  - `gis-reception-token-input` (saisie token)
  - `gis-reception-save-token-btn` / `gis-reception-clear-token-btn`
  - `slot-card-{SLOT_ID}` · `drop-zone-{SLOT_ID}` · `file-input-{SLOT_ID}`
  - `slot-status-{SLOT_ID}` · `sha256-{SLOT_ID}`
  - `progress-bar-{SLOT_ID}` · `upload-cancel-{SLOT_ID}`
  - `event-log` · `event-row-{i}`
- **Token storage** : `sessionStorage["gis_reception_commandant_token"]`
- **Token de test** : `STEEVE-MAX-X42BIS-GIS-RECEPTION-EXPLICIT`
