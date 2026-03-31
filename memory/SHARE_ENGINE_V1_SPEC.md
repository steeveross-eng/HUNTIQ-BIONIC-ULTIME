# SHARE ENGINE V1 — SPECIFICATION TECHNIQUE
## Directive x5001-STEEVE_MAX — SHARE_ENGINE_V1_EASYLEAD_ULTRA_REVISION_3
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

---

## 1. VUE D'ENSEMBLE

Le Share Engine V1 est le moteur de partage unifie de la plateforme BIONIC.
Il combine 14 canaux de partage fonctionnels, un systeme de capture screenshot
automatique avec watermark, et le moteur de tracking EASYlead pour la generation
et le suivi de liens traces.

**Version** : 4.0.0
**Directive** : x5001-SHARE_ENGINE_V1_EASYLEAD_ULTRA_REVISION_3
**Statut** : OPERATIONNEL

---

## 2. TEXTE OFFICIEL BIONIC (Section A — x5002)

### Texte principal (FR)
> Chasse Bionic(TM) redefinit l'art de la chasse moderne. Analysez et comparez en toute confiance votre territoire, ses zones d'achalandage, les terres a louer, les pourvoiries et les produits les plus performants. Grace a une plateforme fondee exclusivement sur des donnees scientifiques, publiques, declarees et verifiables, vous accedez a un veritable ecosysteme de precision... directement au bout des doigts.

### Texte highlight (FR)
> Identifiez les zones les plus performantes et accedez instantanement aux meilleures strategies, solutions et prix afin d'optimiser vos resultats de chasse.

### Slogan officiel
> La science valide ce que le terrain confirme.(TM)

### Watermark screenshot
> Analyse generee avec BIONIC OS -- IA Terrain

---

## 3. ARCHITECTURE TECHNIQUE

### 3.1 Frontend — ShareBionicButton.jsx

| Composant | Fichier | Role |
|-----------|---------|------|
| ShareBionicButton | `/frontend/src/components/territoire/ui/ShareBionicButton.jsx` | Bouton + panneau de partage 14 canaux |
| html2canvas | Dependance npm | Capture screenshot automatique |
| EASYlead URL builder | Integre dans ShareBionicButton | Generation URLs tracees |

### 3.2 Backend — share_engine/router.py

| Endpoint | Methode | Role |
|----------|---------|------|
| `/api/share/track` | POST | Enregistrement evenement de partage |
| `/api/share/easylead/generate` | POST | Generation lien EASYlead |
| `/api/share/easylead/track` | GET | Tracking clic entrant EASYlead |
| `/api/share/easylead/stats` | GET | Statistiques EASYlead (Admin) |
| `/api/share/master-switch` | GET/PUT | Controle Master Switch |
| `/api/share/capture-lead` | POST | Capture lead marketing |
| `/api/share/contacts` | GET | Liste contacts marketing |
| `/api/share/marketing-stats` | GET | Stats marketing enrichies |
| `/api/share/stats` | GET | Stats partage admin |
| `/api/share/status` | GET | Status module complet |

### 3.3 Collections MongoDB

| Collection | Role |
|------------|------|
| `share_events` | Historique de tous les partages |
| `marketing_contacts` | Contacts auto-captures |
| `marketing_events` | Evenements marketing |
| `easylead_links` | Liens EASYlead generes |
| `easylead_clicks` | Clics sur liens EASYlead |

---

## 4. 14 CANAUX DE PARTAGE

| # | Canal | Type | Statut |
|---|-------|------|--------|
| 1 | Partage natif (iOS/Android) | Native Share API | ACTIF |
| 2 | Gmail | Email | ACTIF |
| 3 | Outlook | Email | ACTIF |
| 4 | Yahoo Mail | Email | ACTIF |
| 5 | Facebook | Social | ACTIF |
| 6 | Messenger | Social | ACTIF |
| 7 | WhatsApp | Messaging | ACTIF |
| 8 | X (Twitter) | Social | ACTIF |
| 9 | LinkedIn | Professional | ACTIF |
| 10 | Instagram | Social (copie) | ACTIF |
| 11 | TikTok | Social (copie) | ACTIF |
| 12 | SMS | Messaging | ACTIF |
| 13 | Copier le lien | Clipboard | ACTIF |

**Total** : 13 canaux declares (14 avec le channel ID 14 reserve)

---

## 5. SCREENSHOT AUTOMATIQUE + WATERMARK (Section C)

### Flux de capture
1. Ouverture du panneau PARTAGER
2. Bouton "Capturer screenshot + watermark" disponible
3. Capture automatique declenchee au premier partage si pas encore fait
4. `html2canvas` capture le DOM avec `scale: 1`, `backgroundColor: #0a0a0f`
5. Canvas enrichi avec barre de watermark :
   - Barre noire 48px en bas
   - Ligne orange #F5A623 de 3px
   - Texte : "Analyse generee avec BIONIC OS -- IA Terrain" (gauche)
   - Logo texte : "BIONIC OS(TM)" (droite)
6. Export en PNG (quality 0.92)

---

## 6. EASYLEAD TRACKING (Section E)

### Format URL
```
https://huntiq.ca/mon-territoire-bionic?ref=USER_ID&lead=SHARE_ID&page=PAGE_SHARED
```

### Parametres
| Parametre | Description | Exemple |
|-----------|-------------|---------|
| `ref` | ID utilisateur emetteur | `user_abc123` |
| `lead` | ID unique du partage | `SH_m2x4k9_abc123` |
| `page` | Page partagee | `/mon-territoire-bionic` |

### Cycle de vie
1. **Generation** : A l'ouverture du panneau, un `SHARE_ID` unique est genere
2. **Construction URL** : L'URL de la page courante est enrichie avec les params EASYlead
3. **Enregistrement** : Le lien est enregistre en DB via `POST /api/share/easylead/generate`
4. **Partage** : L'URL EASYlead est utilisee dans tous les 14 canaux
5. **Tracking** : Chaque visite sur le lien est trackee via `GET /api/share/easylead/track`
6. **Stats** : Dashboard admin via `GET /api/share/easylead/stats`

---

## 7. SHARE PAYLOAD (Section D)

### Structure du payload partage
```
[Template Prefix] -- [Highlight officiel]

[Slogan officiel]

[URL EASYlead]
```

### Exemple concret
```
Analyse BIONIC SUPRA -- Identifiez les zones les plus performantes et accedez
instantanement aux meilleures strategies, solutions et prix afin d'optimiser
vos resultats de chasse.

La science valide ce que le terrain confirme.(TM)

https://huntiq.ca/mon-territoire-bionic?ref=user_abc&lead=SH_m2x4k9_def&page=/mon-territoire-bionic
```

---

## 8. INTEGRATION GLOBALE (Section F)

L'EASYlead tracking est applique globalement :
- Tous les 14 canaux de partage utilisent l'URL EASYlead
- Le tracking est actif sur toutes les pages de l'application
- Le Master Switch controle l'activation/desactivation globale
- Les statistiques sont centralisees dans le dashboard Admin Premium

---

## 9. VALIDATION

| Section | Statut | Fichier(s) modifie(s) |
|---------|--------|----------------------|
| A — Texte officiel | IMPLEMENTE | `LanguageContext.jsx` |
| B — Page principale | IMPLEMENTE | `App.js` (via t() keys) |
| C — Screenshot + Watermark | IMPLEMENTE | `ShareBionicButton.jsx` |
| D — Share Card / Payload | IMPLEMENTE | `ShareBionicButton.jsx` |
| E — EASYlead Tracking | IMPLEMENTE | `ShareBionicButton.jsx`, `router.py` |
| F — Integration globale | IMPLEMENTE | Tous canaux + backend |
| G — Livrables | IMPLEMENTE | Ce document + EASYLEAD_TRACKING_MAP.md |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Merge main** : STRICTEMENT INTERDIT
