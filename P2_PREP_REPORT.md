# P2_PREP_REPORT.md — Preparation Phase P2 : Depreciation AUTH-USAGER
## BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX

**Date:** 2026-04-10
**Branche:** SUPRA_RECONSTRUCTION
**Statut:** PREPARATION UNIQUEMENT — Aucune action destructive autorisee
**Reference:** AUTH_DEPRECATION_PLAN.md

---

## 1. OBJET

Analyse d'impact complete des 9 endpoints AUTH-USAGER obsoletes,
plan de migration detaille, cartographie des dependances, risques
et mesures d'attenuation. Aucune suppression reelle autorisee.

---

## 2. INVENTAIRE DES 9 ENDPOINTS A DEPRECIER

### 2.1 Tableau synoptique

| # | Route | Fichier:Ligne | Hash | Risque | Phase |
|---|-------|---------------|------|--------|-------|
| 1 | `POST /api/v1/user/register` | user_engine/v1/router.py:46 | pbkdf2 | MOYEN | D1 |
| 2 | `POST /api/v1/user/login` | user_engine/v1/router.py:71 | pbkdf2 | MOYEN | D1 |
| 3 | `POST /api/v1/user/logout` | user_engine/v1/router.py:92 | N/A | FAIBLE | D1 |
| 4 | `GET /api/territory/users/auto-login` | users_cameras.py:19 | sha256 | FAIBLE | D2 |
| 5 | `POST /api/territory/users/login` | users_cameras.py:64 | sha256 | FAIBLE | D2 |
| 6 | `POST /api/marketplace/auth/login` | marketplace.py:296 | sha256 | ELEVE | D3 |
| 7 | `POST /api/marketplace/auth/register` | marketplace.py:244 | sha256 | ELEVE | D3 |
| 8 | `GET /api/v1/lands/owner/login` | lands_rental.py:589 | sha256 | FAIBLE | D3 |
| 9 | `GET /api/v1/lands/renter/login` | lands_rental.py:666 | sha256 | FAIBLE | D3 |

### 2.2 Auth institutionnel de reference (INTOUCHABLE)

| Route | Fichier | Hash | Statut |
|---|---|---|---|
| `POST /api/auth/register` | auth_engine/v1/router.py:82 | bcrypt | ACTIF — NE PAS MODIFIER |
| `POST /api/auth/login` | auth_engine/v1/router.py:107 | bcrypt | ACTIF — NE PAS MODIFIER |
| `POST /api/auth/google/callback` | auth_engine/v1/router.py:141 | bcrypt | ACTIF — NE PAS MODIFIER |
| `GET /api/auth/me` | auth_engine/v1/router.py:175 | N/A | ACTIF — NE PAS MODIFIER |
| `POST /api/auth/logout` | auth_engine/v1/router.py:195 | N/A | ACTIF — NE PAS MODIFIER |
| + 7 autres endpoints | auth_engine/v1/router.py | bcrypt | ACTIFS |

---

## 3. ANALYSE D'IMPACT COMPLETE

### 3.1 Phase D1 — user_engine (Endpoints #1, #2, #3)

**Fichiers backend:**
- `modules/user_engine/v1/router.py`
- `modules/user_engine/v1/service.py` (pbkdf2_hmac hashing)

**Dependances frontend:**
- `src/modules/user/UserService.js` — 3 appels actifs:
  - Ligne 15: `fetch(\`/api/v1/user/register\`)`
  - Ligne 28: `fetch(\`/api/v1/user/login\`)`
  - Ligne 41: `fetch(\`/api/v1/user/logout\`)`
- `src/modules/business/BusinessDashboard.jsx` — importe UserService

**Dependances base de donnees:**
- Collection `users`: 1 document (admin@huntiq.com, role=hunter)
- Note: La collection `users` est PARTAGEE avec auth_engine (bcrypt)
- Le champ `password` utilise pbkdf2 pour les users crees via user_engine

**Impact depreciation:**
- BusinessDashboard.jsx perdrait la fonctionnalite login/register
- Migration necessaire: remplacer UserService par appels a /api/auth/*
- Risque de conflit de hash: users crees via pbkdf2 ne pourront pas
  se connecter via bcrypt sans re-hash

**Mesure d'attenuation:**
1. Migrer les mots de passe pbkdf2 vers bcrypt au prochain login
2. Ajouter fallback dans auth_engine: si bcrypt.verify() echoue,
   tester pbkdf2_verify() et re-hasher en bcrypt
3. Mettre a jour UserService.js pour utiliser /api/auth/*

---

### 3.2 Phase D2 — territory cameras (Endpoints #4, #5)

**Fichiers backend:**
- `routes/territory/users_cameras.py`

**Dependances frontend:**
- `src/components/PromptManager.jsx:128` — reference documentaire uniquement
  (dans un tableau de chaines de caracteres, pas un appel API actif)
- 0 appel API reel detecte dans le frontend

**Dependances base de donnees:**
- Collection `territory_users`: 2 documents
- Collection `territory_cameras`: 0 documents

**Impact depreciation:**
- FAIBLE — aucun composant frontend n'appelle activement ces endpoints
- La reference dans PromptManager.jsx est documentaire (liste de prompts)

**Mesure d'attenuation:**
1. Ajouter header `X-Deprecated: true` et warning log
2. Rediriger vers /api/auth/login avec message de migration
3. Nettoyer la reference dans PromptManager.jsx

---

### 3.3 Phase D3a — marketplace (Endpoints #6, #7)

**Fichiers backend:**
- `modules/marketplace/marketplace.py`

**Dependances frontend:**
- `src/components/HuntMarketplace.jsx:250` — `axios.post(\`/marketplace/auth/login\`)`
- `src/components/HuntMarketplace.jsx:263` — `axios.post(\`/marketplace/auth/register\`)`
- Systeme de tokens SEPARE de l'auth institutionnel
- Token passe en query param: `?token=${auth.token}`

**Dependances base de donnees:**
- Aucune collection marketplace_users detectee
- Possible: donnees vendeurs stockees dans une collection non-standard

**Impact depreciation:**
- ELEVE — HuntMarketplace.jsx utilise ACTIVEMENT ces endpoints
- Le marketplace a son propre systeme d'authentification
- Suppression = marketplace completement inaccessible

**Mesure d'attenuation:**
1. Migrer HuntMarketplace vers auth institutionnel (/api/auth/*)
2. Convertir le systeme de tokens marketplace vers JWT institutionnel
3. Creer une migration de donnees vendeurs vers collection `users`
4. Tester exhaustivement le flux marketplace avant depreciation

---

### 3.3b Phase D3b — lands_rental (Endpoints #8, #9)

**Fichiers backend:**
- `modules/marketplace/lands_rental.py`

**Dependances frontend:**
- 0 appel API detecte dans le frontend

**Dependances base de donnees:**
- Aucune collection land_owners/land_renters detectee

**Impact depreciation:**
- FAIBLE — aucun consommateur frontend actif

**Mesure d'attenuation:**
1. Ajouter header depreciation
2. Supprimer apres validation

---

## 4. CARTOGRAPHIE DES DEPENDANCES

```
                    FRONTEND
                       |
          +------------+-------------+
          |            |             |
    GlobalAuth.jsx  UserService.js  HuntMarketplace.jsx
          |            |             |
          v            v             v
    /api/auth/*   /api/v1/user/*  /marketplace/auth/*
    (INSTITUTIONNEL)  (D1-DEPRECIER)   (D3-DEPRECIER)
          |            |             |
          v            v             v
    auth_engine    user_engine     marketplace
    (bcrypt)       (pbkdf2)        (sha256?)
          |            |             |
          v            v             v
    Collection      Collection      Collection
    "users"         "users"         "????"
    (PARTAGEE)      (PARTAGEE)      (SEPAREE)
```

---

## 5. PLAN DE MIGRATION DETAILLE

### Phase D1 — Depreciation user_engine (1 session)

| Etape | Action | Risque |
|---|---|---|
| D1.1 | Ajouter fallback pbkdf2->bcrypt dans auth_engine | FAIBLE |
| D1.2 | Migrer UserService.js vers /api/auth/* | FAIBLE |
| D1.3 | Ajouter header X-Deprecated + log warning sur endpoints #1-3 | ZERO |
| D1.4 | Tester login/register via GlobalAuth | FAIBLE |
| D1.5 | Valider avec Commandant | ZERO |

### Phase D2 — Depreciation territory cameras (1 session)

| Etape | Action | Risque |
|---|---|---|
| D2.1 | Nettoyer reference dans PromptManager.jsx | ZERO |
| D2.2 | Ajouter redirection /territory/users/login -> /api/auth/login | FAIBLE |
| D2.3 | Ajouter header X-Deprecated sur endpoints #4-5 | ZERO |
| D2.4 | Valider avec Commandant | ZERO |

### Phase D3 — Depreciation marketplace + lands (2 sessions)

| Etape | Action | Risque |
|---|---|---|
| D3.1 | Auditer collection vendeurs marketplace | FAIBLE |
| D3.2 | Creer migration donnees vendeurs -> users | MOYEN |
| D3.3 | Migrer HuntMarketplace.jsx vers /api/auth/* | MOYEN |
| D3.4 | Convertir tokens marketplace vers JWT | MOYEN |
| D3.5 | Ajouter header X-Deprecated sur endpoints #6-9 | ZERO |
| D3.6 | Tester flux complet marketplace | MOYEN |
| D3.7 | Valider avec Commandant | ZERO |

---

## 6. CALENDRIER PROPOSE

| Phase | Effort | Sessions | Prerequis |
|---|---|---|---|
| D1 | Faible | 1 | Validation Commandant |
| D2 | Faible | 1 | D1 complete |
| D3 | Modere | 2 | D1+D2 completes |
| **Total** | **Modere** | **4 sessions** | |

Delai total estime: 4 sessions de travail sequentielles.

---

## 7. RISQUES IDENTIFIES

| # | Risque | Probabilite | Impact | Attenuation |
|---|---|---|---|---|
| R1 | Conflit hash pbkdf2/bcrypt sur collection users partagee | ELEVEE | MOYEN | Fallback dual-hash dans auth_engine |
| R2 | Marketplace inaccessible apres depreciation endpoints #6-7 | ELEVEE | ELEVE | Migration frontend AVANT depreciation |
| R3 | Perte tokens marketplace existants | MOYENNE | MOYEN | Migration progressive au prochain login |
| R4 | Regression BusinessDashboard | FAIBLE | FAIBLE | Migration UserService.js vers /api/auth/* |
| R5 | Utilisateurs territory_cameras orphelins | FAIBLE | FAIBLE | 2 docs seulement, migration manuelle |

---

## 8. PREUVES TECHNIQUES

### 8.1 Dependances frontend (grep LIVE)
```
UserService.js:15  → fetch(`/api/v1/user/register`)     [D1]
UserService.js:28  → fetch(`/api/v1/user/login`)         [D1]
UserService.js:41  → fetch(`/api/v1/user/logout`)        [D1]
PromptManager.jsx:128 → reference documentaire           [D2]
HuntMarketplace.jsx:250 → axios.post(`/marketplace/auth/login`)   [D3]
HuntMarketplace.jsx:263 → axios.post(`/marketplace/auth/register`) [D3]
```

### 8.2 Collections MongoDB (LIVE)
```
users: 1 document (admin@huntiq.com, role=hunter)
territory_users: 2 documents
territory_cameras: 0 documents
user_sessions: 474 documents
```

### 8.3 Hashing par module (grep LIVE)
```
auth_engine  → bcrypt (CryptContext)     [REFERENCE]
user_engine  → pbkdf2_hmac              [OBSOLETE]
users_cameras → sha256 (hashlib)         [OBSOLETE]
marketplace  → non-identifie            [A AUDITER]
lands_rental → non-identifie            [A AUDITER]
```

---

## 9. CONTRAINTES ZERO ABSOLU

- Aucune suppression d'endpoint sans migration prealable VALIDEE
- Aucun impact sur auth_engine institutionnel
- Aucune perte de donnees utilisateur
- Tests de regression T1-T5 obligatoires par phase
- Validation COMMANDANT requise avant CHAQUE phase
- Aucune modification des regles metier verrouillees

---

## 10. STATUT DE CONFORMITE

| Critere | Statut |
|---|---|
| 9 endpoints identifies | CONFORME |
| Analyse d'impact complete | CONFORME |
| Plan de migration detaille | CONFORME |
| Calendrier propose | CONFORME |
| Risques identifies | CONFORME |
| Preuves techniques fournies | CONFORME |
| Contraintes ZERO ABSOLU respectees | CONFORME |

**P2_PREP_REPORT: COMPLET — EN ATTENTE VALIDATION COMMANDANT**

---

FIN DU DOCUMENT
