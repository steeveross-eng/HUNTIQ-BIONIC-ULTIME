# PLAN BIONIC ZEROCOST ENGINE Ω

**Doctrine**: P22ΩΩ_ZEROCOST_ENGINE_ET_TERRITOIRE_NEVER_BLANK_Ω
**Commandant**: STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date**: 2026-02-XX
**Statut**: PLAN INSTITUTIONNEL — Validation requise avant exécution

---

## 1. OBJECTIF DOCTRINAL

Migrer l'écosystème TERRITOIRE Ω depuis un mode **compute dynamique** (bundle V20 recalculé à chaque requête, Open-Meteo en cold-start, V10 scoring intensif) vers un mode **précalcul total + diffusion CDN** :

- 100 % des bundles cibles sont précalculés à intervalle régulier (cron)
- 100 % des requêtes utilisateur sont servies par un objet statique CDN (latence <50ms globale)
- 0 recalcul dynamique en production user-facing
- Coût marginal par requête utilisateur : ~$0.00001 (transfert CDN)

---

## 2. ARCHITECTURE CIBLE

```
        ┌─────────────────────────────────────────────────────────────┐
        │  PIPELINE PRÉCALCUL (cron · k8s job · 1×/jour ou 1×/heure)  │
        ├─────────────────────────────────────────────────────────────┤
        │  1. SEED : grille H3 niveau 6-7 du Québec (~50000 cellules) │
        │  2. POUR CHAQUE (cellule × espèce × mois × heure_créneau) : │
        │     a. Appel V20 BUNDLE (≈8-15s)                            │
        │     b. Sérialisation gzipped JSON ou MessagePack            │
        │     c. Upload Backblaze B2 / Cloudflare R2                  │
        │  3. INDEX : génération manifest.json (versions + hashes)    │
        └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  STOCKAGE OBJET (B2/R2 + CDN Cloudflare/Fastly)             │
        │  ─────────────────────────────────────────────────────────  │
        │  bionic-zerocost-tiles/                                     │
        │  ├── manifest.json                                          │
        │  ├── v1/                                                    │
        │  │   ├── chevreuil/                                         │
        │  │   │   ├── h3_842b8a7ffffffff/                            │
        │  │   │   │   ├── mois_05_creneau_AM.json.gz                 │
        │  │   │   │   └── ...                                        │
        │  │   │   └── ...                                            │
        │  │   ├── orignal/  ...                                      │
        │  │   └── (6 espèces × ~50000 cells × 4 mois × 3 créneaux)   │
        │  └── v2/  (versioning futur)                                │
        └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
        ┌─────────────────────────────────────────────────────────────┐
        │  FRONTEND TERRITOIRE                                         │
        │  ────────────────────────────────────────────────────────── │
        │  1. Résolution H3 cellule depuis (lat, lon)                 │
        │  2. fetch CDN https://cdn.bionic.../v1/.../mois_05_AM.json.gz│
        │  3. Cache navigateur 24h (Cache-Control immutable)          │
        │  4. Rendu Leaflet identique au mode dynamique               │
        │                                                              │
        │  FALLBACK : si CDN miss → fallback API V20 (backend live)   │
        └─────────────────────────────────────────────────────────────┘
```

---

## 3. CHOIX D'INFRASTRUCTURE

### 3.1 Stockage objet
| Option | Coût stockage | Coût egress | Pourquoi |
|---|---|---|---|
| **Backblaze B2 + Cloudflare CDN** | $0.006/GB/mois | $0 (Bandwidth Alliance) | 🟢 **RECOMMANDÉ** — Egress gratuit via Cloudflare |
| Cloudflare R2 | $0.015/GB/mois | $0 natif | Excellent mais plus cher |
| AWS S3 + CloudFront | $0.023/GB/mois | $0.085/GB | Cher, complexe |

**Recommandation**: **Backblaze B2** (3-4× moins cher que R2) + **Cloudflare CDN devant**.

### 3.2 Format de sérialisation
| Format | Taille | Décompression | Choix |
|---|---|---|---|
| **JSON + gzip** | 5-15 KB/cell | natif navigateur | 🟢 **RECOMMANDÉ** (debug facile) |
| MessagePack + gzip | 4-10 KB/cell | lib ext requise | Plus performant mais opaque |
| Protocol Buffers | 3-8 KB/cell | lib ext requise | Sur-engineering pour Phase I |

### 3.3 Indexation spatiale
| Schéma | Pourquoi |
|---|---|
| **H3 niveau 6-7** | 🟢 **RECOMMANDÉ** — hexagones uniformes, lib JS native, ~50k cells Québec |
| Quadtree Z-order | Performant mais cells non-uniformes |
| MGRS | Trop spécialisé militaire |

---

## 4. ESTIMATION COÛT MENSUEL

Hypothèses :
- 50 000 cellules H3 × 6 espèces × 4 mois × 3 créneaux horaires = **3 600 000 tuiles**
- Taille moyenne : **8 KB/tuile** (JSON gzippé)
- Volume total : **~28 GB**
- Trafic estimé : 2 000 utilisateurs × 200 requêtes/mois = **400 000 reqs/mois ≈ 3.2 GB egress**

| Poste | Coût mensuel |
|---|---|
| Stockage B2 (28 GB) | **$0.17** |
| Egress CDN Cloudflare | **$0.00** (Bandwidth Alliance) |
| Compute précalcul (k8s job 1h/jour) | **$8.00** |
| Cloudflare Pro plan (CDN + WAF) | **$20.00** |
| **TOTAL MENSUEL** | **~ $28** |

vs. mode dynamique actuel : ~$80-150/mois (compute V10+V5 intensif + Open-Meteo + Redis).

**Économie estimée : 65-80%**

---

## 5. PLAN DE MIGRATION ÉCHELONNÉ

### Phase 1 — Précalcul shadow (semaine 1-2)
- Implémenter `tools/zerocost_precompute.py` qui parcourt H3 grid et appelle V20 en local
- Sortie : dossier `/app/backend/cache/zerocost_v1/` rempli
- Validation : 100 tuiles BSL, audit géométrique
- **Pas de routage front** — backend dynamique inchangé

### Phase 2 — Upload B2 + CDN (semaine 3)
- Compte B2 + bucket privé + clé d'application
- Compte Cloudflare + zone CDN devant B2
- Upload script `tools/zerocost_upload.py`
- Validation : 10 tuiles testées via CDN URL

### Phase 3 — Frontend dual-read (semaine 4)
- Hook `useZerocostBundle.js` qui tente CDN d'abord, fallback API V20
- Feature flag `REACT_APP_ZEROCOST_ENABLED=true`
- Monitoring : ratio CDN_HIT / API_FALLBACK

### Phase 4 — Bascule progressive (semaine 5-6)
- 10% trafic → CDN
- 50% trafic → CDN
- 100% trafic → CDN

### Phase 5 — Cron production (semaine 7+)
- k8s CronJob nocturne (3h00 EST)
- Couvre toutes les régions du Québec en delta-update
- Alertes monitoring (PagerDuty/Slack) si échec

---

## 6. CRÉDENTIELS REQUIS DU COMMANDANT

Pour engager la Phase 2 :

| Service | Coût | Action requise |
|---|---|---|
| **Backblaze B2** | $0.17/mois | Créer compte + bucket + clé applicative |
| **Cloudflare CDN** | $0 ou $20/mois | Domaine `cdn.bionic.xxx` + DNS pointant vers B2 |

Aucune action sur Phase 1 (précalcul local backend).

---

## 7. RISQUES & MITIGATIONS

| Risque | Impact | Mitigation |
|---|---|---|
| Données obsolètes (météo change) | Moyen | Cron 1×/heure pour zones critiques (vent), 1×/jour pour zones statiques |
| Coût stockage explose (> 50 GB) | Faible | Compression Brotli (gain ~25%), purge tuiles obsolètes |
| Migration casse UX | Critique | Phase 4 progressive + feature flag rollback instantané |
| Backend dynamique perd test couverture | Faible | Conserver V20 comme fallback permanent |

---

## 8. ALIGNEMENT AVEC DOCTRINE NEVER BLANK Ω

ZEROCOST ENGINE renforce NEVER BLANK Ω :
- Si CDN miss → fallback API V20 → si API 404/502 → middleware retourne `status=DEGRADED`
- Frontend affiche `TerritoireDegradedBanner` au lieu d'une carte vide
- Cache UI navigateur conserve le dernier bundle valide pour affichage offline

---

## 9. DÉCISION ATTENDUE

Le COMMANDANT STEEVE-MAX doit valider :
1. Choix infrastructure : **B2 + Cloudflare** ou autre ?
2. Engagement budget mensuel : ~$28/mois ?
3. Calendrier : démarrage Phase 1 immédiat ou différé ?
4. Périmètre initial : 6 espèces × 50k cells, ou pilote sur 1 espèce × 1 région ?

---

**FIN DU PLAN INSTITUTIONNEL — EN ATTENTE DIRECTIVE D'EXÉCUTION**
