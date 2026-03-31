# EASYLEAD TRACKING MAP V1
## Directive x5001-STEEVE_MAX — SHARE_ENGINE_V1_EASYLEAD_ULTRA_REVISION_3
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

---

## 1. SCHEMA DE TRACKING

### Format URL EASYlead
```
{BASE_URL}{PAGE_PATH}?ref={USER_ID}&lead={SHARE_ID}&page={PAGE_SHARED}
```

### Parametres de tracking

| Parametre | Type | Description | Generation |
|-----------|------|-------------|-----------|
| `ref` | string | ID de l'utilisateur emetteur du partage | `localStorage.huntiq_user_id` ou `"anonymous"` |
| `lead` | string | ID unique du partage (SHARE_ID) | `SH_` + timestamp base36 + `_` + random 6 chars |
| `page` | string | Chemin de la page partagee | `window.location.pathname` |

---

## 2. CARTE DES PAGES TRACKEES

| Page | Route | Tracking EASYlead | Partage actif |
|------|-------|-------------------|---------------|
| Accueil | `/` | OUI | OUI |
| Dashboard | `/dashboard` | OUI | OUI |
| Analyse Territoire | `/mon-territoire-bionic` | OUI (PRIORITAIRE) | OUI |
| Carte Interactive | `/map` | OUI | OUI |
| Permis de Chasse | `/permis-chasse` | OUI | OUI |
| Magasin | `/shop` | OUI | OUI |
| Produit | `/product/:id` | OUI | OUI |
| SUPRA | `/supra` | OUI | OUI |
| Intelligence | `/analytics` | OUI | OUI |
| Comparaison | `/compare` | OUI | OUI |
| Formations | `/formations` | OUI | OUI |
| Tarification | `/pricing` | OUI | OUI |
| Business | `/business` | OUI | OUI |
| Admin Premium | `/admin-premium` | OUI | OUI |
| Reseautage | `/networking` | OUI | OUI |
| Terres | `/lands` | OUI | OUI |
| Modules BIONIC | `/bionic-modules` | OUI | OUI |
| BSAA Dashboard | `/bsaa` | OUI | OUI |

---

## 3. FLUX DE DONNEES

```
UTILISATEUR
    |
    v
[Ouvre PARTAGER] --> genere SHARE_ID (SH_xxxxx)
    |
    v
[Selectionne canal] --> construit URL EASYlead
    |                     ?ref=USER_ID&lead=SHARE_ID&page=PAGE
    |
    +---> [POST /api/share/track] ---------> MongoDB: share_events
    |
    +---> [POST /api/share/easylead/generate] -> MongoDB: easylead_links
    |
    v
[Destinataire clique le lien]
    |
    v
[GET /api/share/easylead/track] --> MongoDB: easylead_clicks
    |                                         + update easylead_links.clicks++
    v
[Admin consulte stats]
    |
    v
[GET /api/share/easylead/stats] --> Aggregations MongoDB
```

---

## 4. COLLECTIONS MONGODB

### 4.1 `easylead_links`
```json
{
  "share_id": "SH_m2x4k9_abc123",
  "user_id": "user_abc123",
  "channel": "whatsapp",
  "page_shared": "/mon-territoire-bionic",
  "easylead_url": "https://huntiq.ca/mon-territoire-bionic?ref=user_abc123&lead=SH_m2x4k9_abc123&page=/mon-territoire-bionic",
  "has_screenshot": true,
  "clicks": 0,
  "conversions": 0,
  "status": "active",
  "created_at": "2026-02-XX...",
  "protocol": "BCE-4X GOLDEN V6+",
  "engine": "easylead_v1"
}
```

### 4.2 `easylead_clicks`
```json
{
  "ref_user_id": "user_abc123",
  "share_id": "SH_m2x4k9_abc123",
  "page": "/mon-territoire-bionic",
  "clicked_at": "2026-02-XX...",
  "protocol": "BCE-4X",
  "engine": "easylead_v1"
}
```

---

## 5. CANAUX x EASYLEAD

| Canal | URL EASYlead injectee | Methode |
|-------|----------------------|---------|
| Partage natif | Dans `url` param | navigator.share() |
| Gmail | Dans `body` | window.open (compose URL) |
| Outlook | Dans `body` | window.open (compose URL) |
| Yahoo | Dans `body` | window.open (compose URL) |
| Facebook | Dans `u` param | window.open (sharer URL) |
| Messenger | Dans `link` param | window.open (dialog URL) |
| WhatsApp | Dans `text` param | window.open (wa.me URL) |
| X (Twitter) | Dans `url` param | window.open (intent URL) |
| LinkedIn | Dans `url` param | window.open (sharing URL) |
| Instagram | Clipboard | navigator.clipboard |
| TikTok | Clipboard | navigator.clipboard |
| SMS | Dans `body` param | sms: protocol |
| Copier lien | Clipboard | navigator.clipboard |

---

## 6. METRIQUES DISPONIBLES

| Metrique | Endpoint | Description |
|----------|----------|-------------|
| Total liens generes | `/api/share/easylead/stats` | Nombre total de liens EASYlead |
| Total clics | `/api/share/easylead/stats` | Nombre total de clics entrants |
| Taux de clic | `/api/share/easylead/stats` | `(clics / liens) * 100` |
| Liens par canal | `/api/share/easylead/stats` | Distribution par canal de partage |
| Liens par page | `/api/share/easylead/stats` | Distribution par page partagee |
| Liens recents | `/api/share/easylead/stats` | 10 derniers liens generes |

---

## 7. SECURITE

- Master Switch : STEEVE-MAX ONLY peut activer/desactiver
- Authority key requise pour modification Master Switch
- Liens EASYlead : pas de donnees sensibles dans les URL params
- SHARE_ID : non predictible (timestamp + random)
- Aucune PII dans les parametres URL (user_id est un identifiant technique)

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Merge main** : STRICTEMENT INTERDIT
