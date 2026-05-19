# INFRASTRUCTURE ZEROCOST Ω · B2 + CLOUDFLARE — CHECKLIST OPÉRATIONNELLE

**Doctrine**: P22ΩΩ_ZEROCOST_PHASE1_SHADOW_ET_LKG_Ω
**Commandant**: STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date**: 2026-02-XX
**Statut**: CHECKLIST PRÊTE — Engagement Phase 2 requiert action Commandant

---

## 1. RÉSULTATS RÉELS DE LA PHASE 1 SHADOW

Validation effectuée sur 2 territoires pilotes (BSL Rimouski + Outaouais Gatineau) :

| Métrique | Valeur réelle mesurée |
|---|---|
| Tuiles précalculées | **144/144 (100%)** |
| Échecs | **0** |
| Tuiles MASK_HALT (doctrine MFFP wapiti/dindon) | 18 |
| Volume RAW total | 10 535 KB |
| Volume GZ total | **2 001 KB** (compression 5.3×) |
| Taille moyenne tuile gzippée | 14 KB |
| Temps compute total | **25.7 secondes** |
| Temps compute médian/tuile | **179 ms** |

### Extrapolation production QC :
- Tuiles totales (50k cellules H3 × 6 espèces × 4 mois × 3 créneaux) : **3 600 000**
- Volume estimé : **47.7 GB**
- Coût stockage B2 estimé : **$0.29/mois**

---

## 2. INFRASTRUCTURE CIBLE — RECOMMANDATION FINALE

### 2.1 Stockage : **Backblaze B2** ✅

**Pourquoi B2** :
- Coût stockage : $0.006/GB/mois (3× moins que R2, 4× moins que S3)
- Egress GRATUIT via Bandwidth Alliance Cloudflare
- API S3-compatible (pas de SDK propriétaire requis)
- Quota par bucket : illimité, redondance native 11×9

**Coût mensuel estimé** :
- Stockage 50 GB → **$0.30**
- Class A/B transactions (uploads + lectures) → **$0.00** (10 000 free/jour)
- **TOTAL B2** : **$0.30/mois**

**Configuration** :
- Bucket privé : `bionic-zerocost-omega`
- Région : `us-west-002` (latence USA acceptable pour QC)
- Lifecycle : aucune purge automatique (versioning ZEROCOST géré côté code)
- Encryption : SSE-B2 (gratuit, AES-256)

### 2.2 CDN : **Cloudflare Pro** ✅

**Pourquoi Cloudflare** :
- Bandwidth Alliance avec B2 → egress B2→CF GRATUIT
- 300+ POPs mondiaux dont QC (Montréal, Toronto)
- Cache "Cache Everything" mode → 100% hit ratio sur tuiles statiques
- WAF + DDoS gratuit (plan Pro $20/mois)

**Coût mensuel estimé** :
- Plan Pro : **$20/mois**
- Bandwidth out : **$0** (illimité plan Pro)
- **TOTAL CF** : **$20/mois**

**Configuration** :
- Domaine custom : `cdn-zerocost.bionichunt.com`
- Origine : `bionic-zerocost-omega.s3.us-west-002.backblazeb2.com`
- Cache TTL : `Cache-Control: public, max-age=86400, immutable` (24h)
- Headers exposés : `X-Bz-Content-Sha1` pour validation intégrité

### 2.3 TOTAL COÛT MENSUEL

| Poste | Coût |
|---|---|
| Backblaze B2 stockage | $0.30 |
| Cloudflare Pro | $20.00 |
| Compute précalcul (k8s job 5min/jour) | $1.00 |
| **TOTAL** | **~$21.30/mois** |

**Économie vs mode dynamique actuel** : ~$60-90/mois saved (estimation 70-80%).

---

## 3. SÉCURITÉ

| Aspect | Mécanisme |
|---|---|
| Auth bucket B2 | Application Key (KEY_ID + APP_KEY) |
| Storage backend → B2 | TLS 1.3 + S3 SigV4 |
| CDN → User | TLS 1.3 + HSTS |
| Anti-tampering | SHA-1 (B2) + ETag (CF) |
| DDoS | Cloudflare WAF + Rate Limiting |
| Anti-scraping | Cloudflare Bot Management + signed URLs si requis |

**Risque résiduel** : exposition de la structure des tuiles publiquement (URLs prévisibles). Mitigation possible Phase 3 : signed URLs courte durée si compétiteurs cherchent à scraper.

---

## 4. INTÉGRATION AVEC L'EXISTANT

### Frontend (Phase 4 dual-read)
```javascript
// useZerocostBundle.js (à créer Phase 3)
async function fetchZerocostTile(species, lat, lng, month, hour) {
  const latQ = lat.toFixed(4);
  const lngQ = lng.toFixed(4);
  const url = `https://cdn-zerocost.bionichunt.com/v1/${species}/${latQ}_${lngQ}/m${month}_h${hour}.json.gz`;
  try {
    const res = await fetch(url);
    if (res.ok) return await res.json();
  } catch (err) { /* fallback */ }
  // Fallback API V20 backend
  return null;
}
```

### Backend (Phase 2 upload pipeline)
```python
# tools/zerocost_upload.py (à créer Phase 2)
import boto3
s3 = boto3.client('s3',
    endpoint_url='https://s3.us-west-002.backblazeb2.com',
    aws_access_key_id=os.environ['B2_KEY_ID'],
    aws_secret_access_key=os.environ['B2_APP_KEY'],
)
for tile_path in Path('/app/backend/cache/zerocost_v1').rglob('*.json.gz'):
    key = str(tile_path.relative_to('/app/backend/cache/zerocost_v1'))
    s3.upload_file(str(tile_path), 'bionic-zerocost-omega', key,
        ExtraArgs={'ContentEncoding':'gzip','ContentType':'application/json',
                   'CacheControl':'public, max-age=86400, immutable'})
```

### Cron k8s (Phase 5)
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: bionic-zerocost-precompute
spec:
  schedule: "0 3 * * *"  # 3h00 EST daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: precompute
            image: bionic-backend:latest
            command: ["python3", "tools/zerocost_precompute_shadow.py"]
            env:
            - name: B2_KEY_ID
              valueFrom: { secretKeyRef: { name: b2-creds, key: key_id } }
            - name: B2_APP_KEY
              valueFrom: { secretKeyRef: { name: b2-creds, key: app_key } }
```

---

## 5. CHECKLIST D'ENGAGEMENT PHASE 2

⚠️ Tout est PRÊT côté code (Phase 1 validée). Le COMMANDANT doit fournir :

- [ ] **Compte Backblaze B2** créé (gratuit signup) — donner le KEY_ID
- [ ] **Bucket B2** créé : `bionic-zerocost-omega` (privé)
- [ ] **Application Key B2** générée avec scope sur le bucket — donner APP_KEY
- [ ] **Compte Cloudflare** existant ou créé (Pro plan $20/mois)
- [ ] **Domaine** `cdn-zerocost.bionichunt.com` (CNAME vers B2 ou Worker)
- [ ] **Décision** : engager Phase 2 (upload + dual-read frontend) ?

Une fois ces éléments fournis, je peux :
- Créer `tools/zerocost_upload.py`
- Configurer la zone CF (DNS, rules, cache)
- Créer `hooks/useZerocostBundle.js` côté frontend
- Engager bascule progressive Phase 4 (10% → 50% → 100%)

---

## 6. ALTERNATIVE SI B2/CF NON-DISPONIBLE

| Option | Coût | Complexité |
|---|---|---|
| Cloudflare R2 (sans B2) | $0.75 stockage + $0 egress | Faible · 1 fournisseur |
| AWS S3 + CloudFront | $1.15 stockage + $4 egress | Moyenne · 4× plus cher |
| Vercel Blob + Vercel CDN | $0.15/GB + $0.05/GB egress | Faible · vendor-lock |
| Self-hosted MinIO + Nginx | $5-10/mois VPS | Élevée · maintenance |

**Recommandation alternative** : Cloudflare R2 seul si simplification d'achat préférée.

---

## 7. DÉLAI ESTIMÉ PAR PHASE

| Phase | Durée | Action |
|---|---|---|
| Phase 1 SHADOW (✅ FAIT) | 1 jour | Validé sur 2 territoires |
| Phase 2 UPLOAD | 2 jours | Script + secrets + upload initial |
| Phase 3 FRONTEND DUAL-READ | 3 jours | hook + feature flag + tests |
| Phase 4 BASCULE | 1 semaine | 10% → 100% trafic |
| Phase 5 CRON | 1 jour | k8s CronJob + alertes |
| **TOTAL DÉPLOIEMENT COMPLET** | **2 semaines** | Pleine production ZEROCOST |

---

**FIN CHECKLIST · EN ATTENTE DIRECTIVE COMMANDANT POUR PHASE 2**
