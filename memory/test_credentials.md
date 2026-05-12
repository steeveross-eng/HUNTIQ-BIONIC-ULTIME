# Test credentials · BCE-4X ULTIME ABSOLU

═══════════════════════════════════════════════════════════════════════
COMPTE COMMANDANT — ACCÈS TERRITOIRE COMPLET (PHASE OMEGA++)
═══════════════════════════════════════════════════════════════════════

## 🟢 Connexion utilisateur (carte TERRITOIRE)

| Champ | Valeur |
|---|---|
| **URL Login PREVIEW** | https://huntiq-restore.preview.emergentagent.com/login |
| **Email** | `commandant@bionichunt.com` |
| **Password** | `BCE4X-OMEGA-2026!` |
| **Role** | `admin` |
| **Premium tier** | `omega` (jusqu'à 2099-12-31) |
| **is_premium** | `true` |
| **user_id** | `user_c675b8b205fd` |

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
| **URL** | https://huntiq-restore.preview.emergentagent.com/admin/bce-4x-premium |
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
