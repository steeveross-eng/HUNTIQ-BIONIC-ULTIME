# R9.3 — Plan de Depreciation AUTH-USAGER
# BCE-4X GOLDEN V6+ | STEEVE-MAX | ZERO ABSOLU
# STATUS: PREPARATION UNIQUEMENT — Aucune execution

## Contexte

Rapport de reference: `/app/memory/BCE4X_AUTH_USAGER_VALIDATION.md`
Auth institutionnel: `auth_engine/v1/router.py` (9 endpoints, bcrypt + JWT HS256)
Anomalie: 9 endpoints OBSOLETES accessibles sur des routes paralleles

## Inventaire des 9 endpoints a deprecier

| # | Route | Fichier | Hash | Risque | Phase |
|---|-------|---------|------|--------|-------|
| 1 | `POST /api/v1/user/register` | `user_engine/v1/router.py:46` | pbkdf2 | MOYEN | D1 |
| 2 | `POST /api/v1/user/login` | `user_engine/v1/router.py:71` | pbkdf2 | MOYEN | D1 |
| 3 | `POST /api/v1/user/logout` | `user_engine/v1/router.py:92` | N/A | FAIBLE | D1 |
| 4 | `GET /api/territory/users/auto-login` | `users_cameras.py:19` | sha256 | ELEVE | D2 |
| 5 | `POST /api/territory/users/login` | `users_cameras.py:64` | sha256 | ELEVE | D2 |
| 6 | `POST /api/marketplace/auth/login` | `marketplace.py:296` | sha256 | MOYEN | D3 |
| 7 | `POST /api/marketplace/auth/register` | `marketplace.py:244` | sha256 | MOYEN | D3 |
| 8 | `GET /api/v1/lands/owner/login` | `lands_rental.py:589` | sha256 | MOYEN | D3 |
| 9 | `GET /api/v1/lands/renter/login` | `lands_rental.py:666` | sha256 | MOYEN | D3 |

## Plan de depreciation en 3 phases

### Phase D1 — Endpoints user_engine (priorite haute)
- **Cible**: endpoints #1, #2, #3
- **Action**: Ajouter header `X-Deprecated: true` + log warning
- **Migration**: Frontend utilise deja `/api/auth/*` exclusivement (confirme par audit)
- **Risque**: Faible — aucun composant frontend ne les appelle
- **Verification**: grep frontend pour `/api/v1/user/(register|login|logout)` = 0 occurrence

### Phase D2 — Endpoints territory (priorite haute)
- **Cible**: endpoints #4, #5
- **Action**: Ajouter redirection vers `/api/auth/login` + log deprecation
- **Migration**: Camera auth doit migrer vers auth_engine
- **Risque**: Moyen — verifier si l'app camera utilise ces endpoints
- **Verification**: grep frontend pour `/api/territory/users/` = dependances a auditer

### Phase D3 — Endpoints marketplace + lands (priorite moyenne)
- **Cible**: endpoints #6, #7, #8, #9
- **Action**: Migration hash sha256 vers bcrypt dans une iteration dediee
- **Migration**: Marketplace et lands_rental ont des pools utilisateurs SEPARES
- **Risque**: Moyen — migration de hash requiert re-hash au prochain login
- **Verification**: Audit des collections MongoDB (marketplace_users, land_owners, land_renters)

## Contraintes ZERO ABSOLU
- Aucune suppression d'endpoint sans migration prealable
- Aucun impact sur auth_engine institutionnel
- Aucune perte de donnees utilisateur
- Tests de regression obligatoires par phase
- Validation Commandant requise avant chaque phase

## Prerequis
- Validation Commandant STEEVE-MAX
- Audit des dependances frontend par endpoint cible
- Backup des collections MongoDB concernees

## Estimation
- Phase D1: 1 session (faible effort, aucune dependance frontend)
- Phase D2: 1 session (migration camera auth)
- Phase D3: 2 sessions (migration hash + pool utilisateurs)
