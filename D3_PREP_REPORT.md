# D3_PREP_REPORT.md
## BCE-4X ULTIME ABSOLU x3 — RAPPORT DE PREPARATION PHASE D3
### COMMANDANT STEEVE-MAX — ANALYSE D'IMPACT AVANT DEPRECIATION

---

**DATE:** 2026-04-13 23:27 UTC
**BRANCHE:** SUPRA_RECONSTRUCTION
**ENVIRONNEMENT:** Preview Kubernetes / MongoDB
**METHODE:** Analyse statique grep + lecture integrale code source
**DIRECTIVE:** P2-PREP-D3-GO
**STATUT:** PREPARATION UNIQUEMENT — ZERO ACTION DESTRUCTIVE

---

## 1. OBJET

Analyse d'impact complete des 4 endpoints d'authentification legacy restants
(Marketplace + Terres a Louer) en vue de leur depreciation controlee lors de
la Phase D3. Ce rapport identifie chaque dependance backend et frontend,
les incompatibilites cryptographiques, les collections MongoDB impactees,
et le plan de migration obligatoire.

---

## 2. INVENTAIRE DES ENDPOINTS CIBLES

### Tableau recapitulatif

| # | Endpoint | Fichier | Lignes | Hash | Token | Collection |
|---|----------|---------|--------|------|-------|------------|
| 6 | `POST /api/marketplace/auth/register` | marketplace.py | L243-293 | SHA256 | `secrets.token_urlsafe(32)` stocke en DB | `marketplace_sellers` |
| 7 | `POST /api/marketplace/auth/login` | marketplace.py | L295-335 | SHA256 | `secrets.token_urlsafe(32)` stocke en DB | `marketplace_sellers` |
| 8 | `POST /api/lands/owners/login` | lands_rental.py | L588-610 | SHA256 | `sha256(id+timestamp)` ephemere | `land_owners` |
| 9 | `POST /api/lands/renters/login` | lands_rental.py | L665-687 | SHA256 | `sha256(id+timestamp)` ephemere | `land_renters` |

### Endpoints register associes (meme perimetre de depreciation)

| # | Endpoint | Fichier | Lignes | Hash | Collection |
|---|----------|---------|--------|------|------------|
| 6b | `POST /api/lands/owners/register` | lands_rental.py | L538-586 | SHA256 | `land_owners` |
| 9b | `POST /api/lands/renters/register` | lands_rental.py | L616-663 | SHA256 | `land_renters` |

---

## 3. ANALYSE CRYPTOGRAPHIQUE — INCOMPATIBILITE SHA256

### 3.1 Hash legacy (marketplace.py)

```
Fichier: /app/backend/marketplace.py
Ligne 201-203:
    def hash_password(password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
```

- **Format:** Hex digest SHA256 pur (64 caracteres hex)
- **Exemple:** `e3b0c44298fc1c149afbf4c8996fb924...`
- **Sel:** AUCUN — hash non sale

### 3.2 Hash legacy (lands_rental.py)

```
Fichier: /app/backend/lands_rental.py
Ligne 555 (owners), Ligne 632 (renters):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
```

- **Format identique:** Hex digest SHA256 pur, non sale
- **Stocke sous:** champ `hashed_password`

### 3.3 Hash auth_engine centralise

```
Fichier: /app/backend/modules/auth_engine/v1/service.py
Ligne 27:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Ligne 51-53:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
```

- **Format:** bcrypt `$2b$12$...` (60 caracteres)
- **Sel:** Integre dans le hash

### 3.4 Fallback existant dans auth_engine

Le service `auth_engine` supporte deja un fallback `pbkdf2 -> bcrypt` (Phase D1):

```
Fichier: /app/backend/modules/auth_engine/v1/service.py
Lignes 62-79:
    # Format bcrypt: commence par $2b$ ou $2a$
    if hashed_password.startswith("$2"):
        return pwd_context.verify(plain_password, hashed_password)
    # Format pbkdf2 legacy (user_engine): salt:hexhash
    if ":" in hashed_password:
        [... verification pbkdf2 ...]
```

### 3.5 RISQUE IDENTIFIE — FALLBACK SHA256 MANQUANT

**CRITIQUE:** Le `auth_engine` ne gere PAS le format SHA256 pur (64 hex sans sel).
Les hashes SHA256 ne commencent PAS par `$2` et ne contiennent PAS `:`.
Ils tomberont dans le `return False` par defaut.

**ACTION REQUISE POUR D3:** Ajouter un troisieme cas de fallback dans
`verify_password()` pour detecter les hashes SHA256 purs (64 caracteres hex)
et re-hasher en bcrypt lors du premier login reussi.

---

## 4. ANALYSE DES MECANISMES DE TOKEN

### 4.1 Token Marketplace

```
Fichier: /app/backend/marketplace.py
Lignes 206-207:
    def generate_token() -> str:
        return secrets.token_urlsafe(32)
```

- **Type:** Token opaque aleatoire (43 caracteres base64url)
- **Stockage:** Champ `token` dans la collection `marketplace_sellers`
- **Verification:** Recherche directe en base (`find_one({"token": token})`)
- **Expiration:** Champ `token_expires` (30 jours)
- **Transmission frontend:** Query parameter `?token=xxx`

### 4.2 Token Lands (Owners + Renters)

```
Fichier: /app/backend/lands_rental.py
Ligne 580 (owners):
    token = hashlib.sha256(f"{owner_id}{now.isoformat()}".encode()).hexdigest()
Ligne 657 (renters):
    token = hashlib.sha256(f"{renter_id}{now.isoformat()}".encode()).hexdigest()
```

- **Type:** Hash SHA256 derivatif (id + timestamp)
- **Stockage:** AUCUN — token ephemere non stocke en base
- **Verification:** AUCUNE cote serveur — les endpoints proteges utilisent `owner_id` ou `renter_id` directement en query param, PAS le token
- **RISQUE:** Le token retourne au frontend est purement decoratif. L'authentification reelle repose sur `owner_id`/`renter_id` passes en clair.

### 4.3 Token auth_engine centralise

```
Fichier: /app/backend/modules/auth_engine/v1/service.py
Lignes 87-100:
    JWT encode avec JWT_SECRET_KEY, algorithme HS256
    Expiration: 1440 minutes (24h)
```

- **Type:** JWT signe
- **Verification:** Decode + verification signature + expiration
- **Transmission:** Header `Authorization: Bearer xxx` OU cookie `session_token` OU query `?token=xxx`

---

## 5. COLLECTIONS MONGODB IMPACTEES

### 5.1 Collections actuelles (fragmentees)

| Collection | Module | Champs auth | Nb endpoints dependants |
|-----------|--------|-------------|------------------------|
| `marketplace_sellers` | marketplace.py | `password_hash` (SHA256), `token`, `token_expires` | 9 (auth/me, listings CRUD, favorites, messages) |
| `land_owners` | lands_rental.py | `hashed_password` (SHA256) | 4 (listings CRUD, agreements) |
| `land_renters` | lands_rental.py | `hashed_password` (SHA256) | 3 (agreements, subscription) |

### 5.2 Collection cible (centralisee)

| Collection | Module | Champs auth |
|-----------|--------|-------------|
| `users` | auth_engine | `password_hash` (bcrypt), sessions JWT separees dans `user_sessions` |

### 5.3 Strategie de migration des collections

**OPTION A — Migration des donnees (RECOMMANDEE):**
- Creer des documents dans `users` pour chaque seller/owner/renter unique (par email)
- Conserver le hash SHA256 tel quel — le fallback dans `verify_password()` le gerera
- Ajouter un champ `roles: ["marketplace_seller"]` ou `["land_owner"]` ou `["land_renter"]`
- Re-hash automatique bcrypt au premier login via auth_engine

**OPTION B — Collections separees maintenues:**
- Laisser les collections existantes mais pointer l'authentification vers auth_engine
- Plus complexe, risque de desynchronisation

---

## 6. DEPENDANCES FRONTEND — HuntMarketplace.jsx

### 6.1 Mecanisme d'authentification actuel

```
Fichier: /app/frontend/src/components/HuntMarketplace.jsx

Ligne 79-93: Stockage localStorage
    getStoredAuth() -> localStorage.getItem('marketplace_auth')
    setStoredAuth() -> localStorage.setItem('marketplace_auth', JSON.stringify(auth))
    Format stocke: { token: "xxx", seller: { id, email, name, is_pro, ... } }

Ligne 248-258: Login
    POST ${API}/marketplace/auth/login  body: { email, password }
    Reponse attendue: { success, token, seller: {...} }

Ligne 261-271: Register
    POST ${API}/marketplace/auth/register  body: { email, password, name, ... }
    Reponse attendue: { success, token, seller: {...} }
```

### 6.2 Points d'utilisation du token (9 endpoints)

| Ligne | Appel | Token transmis via |
|-------|-------|-------------------|
| 237 | `GET /marketplace/my-listings?token=${auth.token}` | Query param |
| 250 | `POST /marketplace/auth/login` | Body (email/password) |
| 263 | `POST /marketplace/auth/register` | Body |
| 291 | `POST /marketplace/listings?token=${auth.token}` | Query param |
| 305 | `DELETE /marketplace/listings/${id}?token=${auth.token}` | Query param |
| 330 | `POST /marketplace/listings/${id}/favorite?token=${auth.token}` | Query param |
| — | `GET /marketplace/auth/me?token=` (L338 backend) | Query param |
| — | `GET /marketplace/favorites?token=` (L684 backend) | Query param |
| — | `GET/POST /marketplace/messages?token=` (L707, L736 backend) | Query param |

### 6.3 Plan de migration frontend HuntMarketplace.jsx

1. **Remplacer** les appels `/marketplace/auth/login` et `/register` par `/auth/login` et `/auth/register` (auth_engine)
2. **Adapter** le format de reponse: auth_engine retourne `{ token, user: {...} }` au lieu de `{ token, seller: {...} }`
3. **Remplacer** le stockage `marketplace_auth` par utilisation du token JWT via header `Authorization: Bearer`
4. **Modifier** tous les appels proteges: remplacer `?token=xxx` par header `Authorization: Bearer xxx`
5. **Adapter** le backend `marketplace.py`: les endpoints proteges doivent accepter le JWT auth_engine au lieu du token opaque local

---

## 7. DEPENDANCES FRONTEND — LandsRental.jsx

### 7.1 Mecanisme d'authentification actuel

```
Fichier: /app/frontend/src/components/LandsRental.jsx

Lignes 108-130: Stockage localStorage DUAL
    getStoredAuth('owner')  -> localStorage.getItem('lands_owner_auth')
    getStoredAuth('renter') -> localStorage.getItem('lands_renter_auth')
    setStoredAuth('owner', data) / setStoredAuth('renter', data)

Lignes 140-141: Etat React
    ownerAuth  = getStoredAuth('owner')   // { success, token, owner: {...} }
    renterAuth = getStoredAuth('renter')   // { success, token, renter: {...} }

Lignes 308-326: Login
    POST ${API}/lands/owners/login?email=xxx&password=xxx  (Query params!)
    POST ${API}/lands/renters/login?email=xxx&password=xxx (Query params!)

Lignes 328-346: Register
    POST ${API}/lands/owners/register?name=xxx&email=xxx&phone=xxx&password=xxx
    POST ${API}/lands/renters/register?name=xxx&email=xxx&phone=xxx&password=xxx
```

### 7.2 Points d'utilisation de l'identite

| Ligne | Appel | Identifiant transmis |
|-------|-------|---------------------|
| 285-287 | `GET /lands/listings?owner_id=${ownerAuth.owner.id}` | owner_id en query |
| 365-382 | `POST /lands/listings?owner_id=${ownerAuth.owner.id}` | owner_id en query |
| 425-438 | `POST /lands/agreements?renter_id=${renterAuth.renter.id}` | renter_id en query |
| 464-465 | `POST /lands/purchase?user_type=owner&user_id=xxx` | user_id en query |

### 7.3 RISQUE SECURITAIRE CRITIQUE

**Les endpoints Lands ne verifient PAS le token.** L'authentification repose
uniquement sur `owner_id` ou `renter_id` passes en query param.
N'importe qui connaissant un `owner_id` peut modifier les annonces.
La migration vers auth_engine/JWT corrigera cette faille.

### 7.4 Plan de migration frontend LandsRental.jsx

1. **Unifier** le systeme d'auth dual (owner/renter) en un seul flux auth_engine avec role
2. **Remplacer** les appels `/lands/owners/login` et `/lands/renters/login` par `/auth/login`
3. **Ajouter** un champ `role` dans le profil utilisateur (`land_owner`, `land_renter`, ou les deux)
4. **Remplacer** la transmission `owner_id`/`renter_id` en query param par header `Authorization: Bearer xxx`
5. **Adapter** le backend `lands_rental.py`: extraire l'identite depuis le JWT au lieu des query params

---

## 8. MATRICE DE RISQUES

| # | Risque | Severite | Probabilite | Mitigation |
|---|--------|----------|-------------|------------|
| R1 | Hash SHA256 non reconnu par auth_engine | CRITIQUE | 100% | Ajouter fallback SHA256 dans `verify_password()` |
| R2 | Perte d'acces des sellers marketplace existants | ELEVEE | Haute si R1 non mitige | Migration donnees + fallback hash |
| R3 | Perte d'acces des owners/renters lands existants | ELEVEE | Haute si R1 non mitige | Migration donnees + fallback hash |
| R4 | Regression UI marketplace (format reponse change) | MOYENNE | 100% sans migration frontend | Adapter les handlers login/register dans HuntMarketplace.jsx |
| R5 | Regression UI lands (auth dual owner/renter cassee) | ELEVEE | 100% sans migration frontend | Restructurer le systeme d'auth dans LandsRental.jsx |
| R6 | Faille securitaire lands (owner_id en clair) | CRITIQUE | Actuelle | Corrigee par migration JWT |
| R7 | Collision d'emails entre collections | MOYENNE | Possible | Deduplication par email lors de la migration |
| R8 | Endpoints proteges marketplace (9) cassent si token change | ELEVEE | 100% | Migrer tous les endpoints proteges vers JWT |

---

## 9. PLAN D'EXECUTION RECOMMANDE POUR D3

### Phase D3-A : Backend — Fallback SHA256 (auth_engine)
1. Ajouter detection hash SHA256 dans `verify_password()` (pattern: 64 hex sans prefixe)
2. Re-hash automatique bcrypt au premier login reussi
3. Test unitaire avec hash SHA256 existant

### Phase D3-B : Backend — Migration donnees
1. Script de migration: copier les users de `marketplace_sellers`, `land_owners`, `land_renters` vers `users`
2. Deduplication par email (priorite: user existant dans `users` > seller > owner > renter)
3. Attribution des roles: `marketplace_seller`, `land_owner`, `land_renter`
4. Conservation des metadonnees (profils, stats, abonnements) dans les collections d'origine

### Phase D3-C : Backend — Migration endpoints proteges
1. Marketplace: remplacer `token: str = Query(...)` par extraction JWT via `get_current_user`
2. Lands: remplacer `owner_id: str = Query(...)` / `renter_id: str = Query(...)` par extraction JWT
3. Ajouter headers `X-Deprecated` sur les 4 endpoints auth legacy (+ les 2 register)

### Phase D3-D : Frontend — HuntMarketplace.jsx
1. Migrer login/register vers `/api/auth/login` et `/api/auth/register`
2. Stocker le JWT et l'envoyer via header `Authorization: Bearer`
3. Adapter tous les appels proteges (9 endpoints)

### Phase D3-E : Frontend — LandsRental.jsx
1. Unifier le systeme dual owner/renter sous auth_engine
2. Migrer login/register
3. Transmettre l'identite via JWT au lieu de `owner_id`/`renter_id` en query

### Phase D3-F : Tests anti-regression
1. T1-T5 standard (K1-GLOBAL)
2. Tests specifiques marketplace (login, create listing, favorites, messages)
3. Tests specifiques lands (login owner/renter, create listing, agreement)
4. Verification que les anciens endpoints retournent `X-Deprecated` mais restent fonctionnels

---

## 10. PREUVES TECHNIQUES

### P1 — Endpoints legacy marketplace.py
```
$ grep -n "def register_seller\|def login_seller\|@marketplace_router.post.*auth" /app/backend/marketplace.py
243:@marketplace_router.post("/auth/register")
244:async def register_seller(data: SellerRegister):
295:@marketplace_router.post("/auth/login")
296:async def login_seller(data: SellerLogin):
```

### P2 — Endpoints legacy lands_rental.py
```
$ grep -n "def login_owner\|def login_renter\|def register_owner\|def register_renter" /app/backend/lands_rental.py
538:@lands_router.post("/owners/register")
539:async def register_owner(
588:@lands_router.post("/owners/login")
589:async def login_owner(email: str = Query(...), password: str = Query(...)):
616:@lands_router.post("/renters/register")
617:async def register_renter(
665:@lands_router.post("/renters/login")
666:async def login_renter(email: str = Query(...), password: str = Query(...)):
```

### P3 — Hash SHA256 marketplace
```
$ grep -n "hashlib.sha256\|hash_password" /app/backend/marketplace.py
201:def hash_password(password: str) -> str:
203:    return hashlib.sha256(password.encode()).hexdigest()
260:        "password_hash": hash_password(data.password),
302:        "password_hash": hash_password(data.password)
```

### P4 — Hash SHA256 lands
```
$ grep -n "hashlib.sha256\|hashed_password" /app/backend/lands_rental.py
555:    hashed_password = hashlib.sha256(password.encode()).hexdigest()
594:    hashed_password = hashlib.sha256(password.encode()).hexdigest()
632:    hashed_password = hashlib.sha256(password.encode()).hexdigest()
671:    hashed_password = hashlib.sha256(password.encode()).hexdigest()
```

### P5 — Collections marketplace
```
$ grep -n "marketplace_sellers\|marketplace_listings" /app/backend/marketplace.py | head -5
249:    existing = await database.marketplace_sellers.find_one({"email": data.email.lower()})
280:    await database.marketplace_sellers.insert_one(seller)
300:    seller = await database.marketplace_sellers.find_one({
312:    await database.marketplace_sellers.update_one(
342:    seller = await database.marketplace_sellers.find_one({"token": token})
```

### P6 — Collections lands
```
$ grep -n "land_owners\|land_renters" /app/backend/lands_rental.py | head -5
424:    owner = await database.land_owners.find_one({"id": listing.get("owner_id")}, {"_id": 0, "hashed_password": 0})
445:    owner = await database.land_owners.find_one({"id": owner_id})
550:    existing = await database.land_owners.find_one({"email": email.lower()})
577:    await database.land_owners.insert_one(owner_data)
596:    owner = await database.land_owners.find_one({
```

### P7 — Frontend marketplace appels auth
```
$ grep -n "marketplace/auth/" /app/frontend/src/components/HuntMarketplace.jsx
250:      const response = await axios.post(`${API}/marketplace/auth/login`, { email, password });
263:      const response = await axios.post(`${API}/marketplace/auth/register`, data);
```

### P8 — Frontend lands appels auth
```
$ grep -n "lands/owners/login\|lands/renters/login" /app/frontend/src/components/LandsRental.jsx
310:      const endpoint = type === 'owner' ? '/lands/owners/login' : '/lands/renters/login';
```

### P9 — auth_engine fallback dual-hash actuel
```
$ grep -n "def verify_password\|pbkdf2\|bcrypt\|startswith" /app/backend/modules/auth_engine/v1/service.py
55:    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
62:        if hashed_password.startswith("$2"):
63:            return pwd_context.verify(plain_password, hashed_password)
65:        # Format pbkdf2 legacy (user_engine): salt:hexhash
66:        if ":" in hashed_password:
```

### P10 — auth_engine endpoints centralises
```
$ grep -n "@router.post\|@router.get" /app/backend/modules/auth_engine/v1/router.py
82:@router.post("/register", response_model=TokenResponse)
107:@router.post("/login", response_model=TokenResponse)
141:@router.post("/google/callback", response_model=TokenResponse)
175:@router.get("/me", response_model=UserResponse)
```

### P11 — Endpoints proteges par token marketplace (9 endpoints)
```
$ grep -n "token: str = Query" /app/backend/marketplace.py
338:async def get_current_seller(token: str = Query(...)):
375:async def create_listing(data: ListingCreate, token: str = Query(...)):
550:async def update_listing(listing_id: str, data: ListingUpdate, token: str = Query(...)):
581:async def delete_listing(listing_id: str, token: str = Query(...)):
615:async def get_my_listings(token: str = Query(...), page: int = 1, limit: int = 20):
648:async def toggle_favorite(listing_id: str, token: str = Query(...)):
684:async def get_favorites(token: str = Query(...)):
707:async def send_message(data: MessageCreate, token: str = Query(...)):
736:async def get_messages(token: str = Query(...)):
```

### P12 — Endpoints proteges par ID lands (4 endpoints)
```
$ grep -n "owner_id: str = Query\|renter_id: str = Query" /app/backend/lands_rental.py
439:    owner_id: str = Query(...)
499:    owner_id: str = Query(...)
523:async def delete_land_listing(listing_id: str, owner_id: str = Query(...)):
717:    renter_id: str = Query(...)
```

---

## 11. STATUT DE CONFORMITE

| Critere | Resultat | Preuve |
|---------|----------|--------|
| Inventaire des 4 endpoints cibles | PASSE | P1, P2 |
| Analyse cryptographique (hash) | PASSE | P3, P4, P9 |
| Analyse des tokens | PASSE | P3 (L206), P4 (L580, L657) |
| Identification collections MongoDB | PASSE | P5, P6 |
| Mapping dependances frontend marketplace | PASSE | P7, P11 |
| Mapping dependances frontend lands | PASSE | P8, P12 |
| Identification des risques | PASSE | Section 8 (8 risques documentes) |
| Plan de migration propose | PASSE | Section 9 (6 sous-phases) |
| ZERO action destructive | PASSE | Aucun fichier modifie |

**VERDICT: CONFORME — 9/9 criteres satisfaits avec preuves**

---

## 12. FIN DU DOCUMENT

**DATE DE CERTIFICATION:** 2026-04-13 23:27 UTC
**AUTEUR:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
**LIVRABLE:** /app/D3_PREP_REPORT.md
**PROCHAINE ETAPE:** En attente d'autorisation du Commandant pour Phase D3 (P2-EXEC-D3-GO)
**AUCUNE execution ne sera entamee sans ordre explicite.**

═══════════════════════════════════════════════════════════════
          RAPPORT D3_PREP CERTIFIE — BCE-4X ULTIME ABSOLU
═══════════════════════════════════════════════════════════════
