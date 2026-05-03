# Test Credentials — BIONIC OS V20-SUPRA

## Admin (Commandant STEEVE-MAX)
- **Email** : `steeve-max-capture@huntiq.com`
- **Password** : `Saturn5858*`
- **Rôle** : Admin institutionnel (accès self-audit, registry-lock, captures)

## Admin Premium + Gestionnaire (Ordre n°51 · Token unifié) — ACCÈS UNIFIÉ
- **Login form** : `POST /api/auth/login` avec `email=admin@huntiq.com` + password `Saturn5858*`
- **Pages sécurisées** :
  - `/admin-premium` → localStorage `admin_premium_authenticated=true`
  - `/gestionnaire` → localStorage `gestionnaire_authenticated=true` (Ordre n°47)
- **Token GIS Commandant (Ordre n°51)** : `Saturn5858*` (unifié avec le mot de passe admin sur directive du Commandant)
  - Header HTTP : `X-Commandant-Token: Saturn5858*`
  - Variable env backend : `GIS_RECEPTION_COMMANDANT_TOKEN=Saturn5858*`
  - À saisir dans le panel `RÉCEPTION GIS Ω` → section X-COMMANDANT-TOKEN → 🔍 Tester
- **Bypass client-side institutionnel** (captures Playwright) :
  ```js
  localStorage.setItem('admin_premium_authenticated', 'true');
  localStorage.setItem('gestionnaire_authenticated', 'true');
  sessionStorage.setItem('gis_reception_commandant_token', 'Saturn5858*');
  ```
- **data-testid Gestionnaire (Ordre n°47)** :
  - `gestionnaire-auth-guard` (form de connexion)
  - `gestionnaire-password-input` · `gestionnaire-login-btn`
  - `gestionnaire-toggle-password-visibility` (Ordre n°51 · œil)
  - `gestionnaire-authenticated-root` (page authentifiée)
  - `gestionnaire-logout-btn` (top-right)
- **data-testid Admin Premium (Ordre n°51 · œil)** :
  - `admin-premium-password-input`
  - `admin-premium-toggle-password-visibility` (œil 👁 affiche/masque)

## Endpoints d'audit (sans auth)
- `GET /api/v20/territoire/self-audit` — exécute les 60 suites
- `GET /api/v20/territoire/self-audit/last` — dernier résultat
- `GET /api/v20/territoire/registry-lock` — registry scellé V29

## Admin Premium Page (`/admin-premium`) — Ordre n°41
- **Login form** : `POST /api/auth/login` avec `email=admin@huntiq.com` + password
- **Bypass client-side** (captures institutionnelles Playwright) :
  `localStorage.setItem('admin_premium_authenticated', 'true')`
- **Section Pilotage BCE-4X Ω** : data-testid `pilotage-bce4x-dashboard`
- **ORDRE N°47 · Bug Dashboard durci** : data-testid `pilotage-bce4x-retry-btn` (bouton Réessayer)
- **ORDRE N°47 · Bouton trombone 📎** : data-testid `trombone-btn-{slot_id}` (6 boutons, un par slot)

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

## Audit-Log GIS (Ordre n°44) — ADMIN_PREMIUM_ONLY
- **Endpoint GET** : `/api/v30/admin-premium/gis/audit-log`
- **Endpoint POST** : `/api/v30/admin-premium/gis/promote`
- **Header auth** : `X-Commandant-Token: Saturn5858*` (Ordre n°51 · unifié)
- **Storage** : `/app/backend/data/gis_operational/audit_log.jsonl` (JSONL append-only)
- **Rétention** : env `GIS_AUDIT_RETENTION_DAYS` (défaut 90 jours)
- **Filtres GET** : `?slot_id=...&event=...&limit=1..2000`

## VOIE B Multi-Upload FORET_MFFP_Ω (Ordre n°46) — ADMIN_PREMIUM_ONLY
- **Flag spec** : `multi_upload=True` exclusivement sur `FORET_MFFP_Ω` (5 autres slots restent single-upload)
- **Capacité** : `files_max=32` tuiles, taille cumulée max 5 Go
- **Endpoint inchangé** : `POST /api/v30/admin-premium/gis/upload/FORET_MFFP_Ω` · un appel par tuile
- **Dédup** : ré-upload d'un filename identique remplace l'entrée (pas de doublon composite)
- **SHA-256 composite** : `SHA256(sorted(sha_i).join('\n'))` · ordre-insensible, déterministe
- **Champs exposés** dans réponse upload et `intake-status` : `multi_upload`, `files_loaded_count`, `composite_sha256`
- **Test pytest** : `test_phase_xxiv_multi_upload_omega.py` (14 tests)
- **data-testid UI** : `multi-upload-banner-FORET_MFFP_Ω`, `tuiles-list-FORET_MFFP_Ω`, `tuile-row-FORET_MFFP_Ω-{i}`, `composite-sha256-FORET_MFFP_Ω`
