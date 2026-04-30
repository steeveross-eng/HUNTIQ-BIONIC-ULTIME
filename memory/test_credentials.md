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
