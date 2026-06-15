# Test credentials · BCE-4X ULTIME ABSOLU

═══════════════════════════════════════════════════════════════════════
COMPTE COMMANDANT — ACCÈS TERRITOIRE COMPLET (PHASE OMEGA++)
═══════════════════════════════════════════════════════════════════════

## 🟢 Connexion utilisateur (carte TERRITOIRE)

⚠️ **DEUX COMPTES UTILISABLES** (même password pour simplicité) :

### Compte historique (auto-loggé par le frontend)
| Champ | Valeur |
|---|---|
| **Email** | `admin@huntiq.com` |
| **Password** | `Commandant2026` |
| **Nom** | Steeve-MAX |
| **Role** | `admin` (upgrade 2026-05-12T20:55Z) |
| **Premium tier** | `omega` (jusqu'à 2099-12-31) |
| **user_id** | `user_aac634a5fab7` |

### Compte alternatif (créé hier)
| Champ | Valeur |
|---|---|
| **Email** | `commandant@bionichunt.com` |
| **Password** | `Commandant2026` |
| **Nom** | Commandant Steeve-Max |
| **Role** | `admin` |
| **Premium tier** | `omega` |
| **user_id** | `user_c675b8b205fd` |

| Champ commun | Valeur |
|---|---|
| **URL Login PREVIEW** | https://ultime-preview.preview.emergentagent.com/login |

⚠️ **Reset password 2026-05-12T20:55Z** : ancien `BCE4X-OMEGA-2026!` (avec `!`) remplacé par `Commandant2026` (alphanumeric pur) pour éviter problèmes de copier-coller / encodage URL / autocomplete navigateur.

### 🛠️ Conseils en cas de problème de connexion
1. **Auto-login activé** : si le frontend détecte un token dans localStorage, il connecte automatiquement avec l'ancien compte. Pour forcer la déconnexion :
   - DevTools → Application → Storage → **Clear site data**
   - Ou utiliser navigation privée
2. **Saisir manuellement** le password (ne pas copier-coller pour éviter espaces invisibles)
3. **Vérifier validation API directe** :
   ```bash
   curl -X POST https://ultime-preview.preview.emergentagent.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@huntiq.com","password":"Commandant2026"}'
   ```
   Doit retourner `{"success":true,"token":"...","user":{...}}`

### Inscription nouveau membre
L'endpoint `/api/auth/register` est **opérationnel** (vérifié 2026-05-12T20:50Z).
Tester via :
```bash
curl -X POST https://ultime-preview.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Nouveau","email":"new@bionichunt.com","password":"Pass2026"}'
```

### Routes TERRITOIRE accessibles après login
| Route | Mode |
|---|---|
| `/territoire` | Carte TERRITOIRE Ω (mode `carte-territoire`) |
| `/mon-territoire-bionic` | Analyse BIONIC complète |
| `/mon-territoire` | Alias analyse BIONIC |
| `/territoire/hud-ultime-phase-e` | HUD ULTIME PHASE E |
| `/territoire-apte` | Widget APTE Ω |
| `/territoire-capture-mode` | Mode capture (sans auth) |

═══════════════════════════════════════════════════════════════════════
ADMIN PREMIUM DASHBOARD (BCE-4X)
═══════════════════════════════════════════════════════════════════════

## 🟠 Token Commandant — Admin Premium

| Champ | Valeur |
|---|---|
| **URL** | https://ultime-preview.preview.emergentagent.com/admin/bce-4x-premium |
| **Header** | `X-Commandant-Token: Saturn5858*` |
| **Backend env var** | `GIS_RECEPTION_COMMANDANT_TOKEN=Saturn5858*` |

Saisir `Saturn5858*` dans le champ token au premier accès Admin Premium.

### Sous-routes Admin Premium (post auth-gate)
| Route | Module |
|---|---|
| `/admin/bce-4x-premium/v5-compliance` | **PHASE OMEGA · V5 Compliance Dashboard** ⭐ |
| `/admin/bce-4x-premium/visualizer` | Visualizer 18 couches |
| `/admin/bce-4x-premium/territoire` | Rapports Ω PDF/HTML |
| `/admin/bce-4x-premium/waypoint` | Field Guides |
| `/admin/bce-4x-premium/manual` | Manuel doctrinal couches |
| `/admin/bce-4x-premium/merkle` | Bitcoin anchoring + OTS |
| `/admin/bce-4x-premium/validation` | Audit Commandant approbations |

═══════════════════════════════════════════════════════════════════════
ENDPOINTS V5 — DIRECTEMENT ACCESSIBLES (sans auth)
═══════════════════════════════════════════════════════════════════════

| Endpoint | Type | Doctrine |
|---|---|---|
| `GET /api/v20/territoire/bundle?lat&lon&species&...` | Bundle UI V5 | `P22Σ_V5_BUNDLE_REWIRE_Ω` |
| `POST /api/v20/territoire/corridors-organic/generate` | V5 organic direct | `P22Σ_V5_CAP_GLOBAL_TERRITOIRE` |
| `GET /api/v20/audit/v5-compliance-live?lat&lon&species` | Audit live | `P22Ω.V5_COMPLIANCE_LIVE_Ω` |
| `GET /api/v20/audit/v5-monitor-stats` | État monitor | `P22Ω.V5_COMPLIANCE_MONITOR_Ω` |
| `POST /api/v20/audit/v5-monitor-tick` | Force tick monitor | — |
| `POST /api/v20/audit/v5-alert-test?to=...` | Test alerte Resend | — |
| `GET /api/v20/audit/v5-daily-report?hours=24&format=md` | Rapport quotidien | `P22Ω.V5_DAILY_REPORT` |

═══════════════════════════════════════════════════════════════════════
GIS Reception · Commandant Token (legacy compatible)
═══════════════════════════════════════════════════════════════════════
- Header : `X-Commandant-Token: Saturn5858*`
- Backend env var : `GIS_RECEPTION_COMMANDANT_TOKEN=Saturn5858*`

═══════════════════════════════════════════════════════════════════════
Backblaze B2 (ORDRE N°52-EXT VOIE B)
═══════════════════════════════════════════════════════════════════════
- `B2_KEY_ID=006707511aa307d0000000001`
- `B2_APPLICATION_KEY=K006TyTv2XtgY72/rknqnhCj8jlKXaw`
- `B2_BUCKET_NAME=pee-maj-gpkg`
- `B2_ENDPOINT_URL=https://s3.ca-east-006.backblazeb2.com`
- `B2_REGION=ca-east-006`

═══════════════════════════════════════════════════════════════════════
Resend Alerting (PHASE OMEGA++)
═══════════════════════════════════════════════════════════════════════
- `RESEND_API_KEY=re_AHzhG1Us_Ksio8djFgPDTx5q3fPw81hiN`
- `RESEND_FROM=BCE-4X COMMANDANT <onboarding@resend.dev>` (sandbox)
- `ADMIN_EMAIL=steeve@bionichunt.com` (cible production)
- ⚠️ Sandbox Resend limite envoi à `steeve.ross@gmail.com` jusqu'à vérification domaine `bionichunt.com`

Tous ces credentials sont persistés dans `/app/backend/.env`.
