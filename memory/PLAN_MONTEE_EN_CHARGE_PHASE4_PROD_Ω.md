# PLAN DE MONTÉE EN CHARGE PHASE 4 PROD ZEROCOST

**Doctrine** : `P22ΩΩ_PHASE4_ROLLOUT_PROD_PLAN_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟡 PLAN PROPOSÉ — AUTORISATION COMMANDANT REQUISE AVANT EXÉCUTION

---

## 1. OBJECTIF DOCTRINAL

Basculer 100 % du trafic utilisateur TERRITOIRE Ω du backend dynamique vers le CDN ZEROCOST
(Cloudflare R2 + manifeste OWM-warmed), tout en garantissant :
1. **NEVER BLANK Ω strict** — fallback API V20 + LKG IndexedDB toujours actifs.
2. **0 régression UI/UX** — rendus corridors, zones, salines, affûts identiques aux baselines.
3. **Rollback instantané** sur trigger automatique ou manuel Commandant.

---

## 2. ÉTAT D'ENTRÉE EN PHASE 4

| Pré-requis | Statut | Référence |
|---|---|---|
| Découplage Open-Meteo (rate-limit éliminé) | 🟢 OK | `RAPPORT_WEATHERCACHE_BETA2_Ω.md` |
| Stratification β2-Ε P1/P2/P3 validée | 🟢 OK | `RAPPORT_WEATHERCACHE_BETA2_Ω_ADDENDUM_B_E.md` |
| CDN `cdn-zerocost.bionichunt.com` opérationnel | 🟢 HTTP 200 · 235ms | Manifest CDN propagé |
| Frontend LKG IndexedDB NEVER BLANK Ω | 🟢 Validé en mode avion | `lkgCacheOmega.test.js` 8/8 PASS |
| Fallback API V20 backend | 🟢 Toujours disponible | Pas touché Phase III |
| Pré-warm P1 IFAP/ZEC/RF (509 K tuiles) | 🟡 1.9 jours k8s 256w | À engager |
| Phase III lock | 🔒 Maintenu | Aucune modification V10/V20 |

---

## 3. STRATÉGIE DE BASCULE — 4 PALIERS

### Palier 1 — SHADOW (T+0 → T+24h)
| Aspect | Détail |
|---|---|
| Trafic CDN | 0 % (lecture seule en arrière-plan) |
| Trafic API V20 | 100 % |
| `REACT_APP_ZEROCOST_ENABLED` | `false` |
| Monitoring | Logs comparatifs CDN_BUNDLE vs API_V20 (cohérence corridors/zones/affûts) |
| **Critère de progression vers Palier 2** | 0 divergence majeure observée sur 24h |

### Palier 2 — CANARY 10 % (T+24h → T+72h)
| Aspect | Détail |
|---|---|
| Trafic CDN | 10 % (hash userId modulo 10) |
| Trafic API V20 | 90 % |
| `REACT_APP_ZEROCOST_ENABLED` | `true` côté FE avec gate frontend `Math.random() < 0.10` |
| Monitoring | Latence P50/P95/P99 · taux d'erreur · banner DEGRADED ratio · LKG fallback ratio |
| **SLOs cibles** | Latence P95 ≤ 200ms · Erreur ≤ 0.5 % · DEGRADED ≤ 1 % |
| **Critère de progression vers Palier 3** | 48h sans franchissement SLO |
| **Trigger rollback automatique** | Erreur > 2 % OU DEGRADED > 5 % OU LKG fallback > 10 % → flag à `false` |

### Palier 3 — RAMP-UP 50 % (T+72h → T+7j)
| Aspect | Détail |
|---|---|
| Trafic CDN | 50 % (gate `Math.random() < 0.50`) |
| Trafic API V20 | 50 % |
| Monitoring | Idem Palier 2 + monitoring coût R2/CF · taux HIT cache CF |
| **SLOs** | Latence P95 ≤ 150ms · CF HIT ≥ 95 % |
| **Critère de progression vers Palier 4** | 5 jours sans franchissement SLO |

### Palier 4 — FULL 100 % (T+7j → permanent)
| Aspect | Détail |
|---|---|
| Trafic CDN | 100 % |
| Trafic API V20 | Fallback uniquement (LKG_STALE et CDN_MISS) |
| Monitoring | Idem + alertes Prometheus 24/7 |
| **SLOs** | Latence P95 ≤ 100ms · CF HIT ≥ 98 % · Coût mensuel ≤ $30 |
| **Pas de Palier 5** | Régime permanent |

---

## 4. GARDE-FOUS DE ROLLBACK

### 4.1 Rollback automatique (côté infrastructure)

| Trigger | Action |
|---|---|
| Cloudflare R2 5xx > 0.5 % sur 5min | Worker CF route → fallback API V20 (header `X-Zerocost-Fallback: 1`) |
| CDN HIT ratio < 80 % sur 1h | Alert Slack + investigation manuelle, pas de rollback auto |
| Bundle CDN décodé invalide (no corridors / no zones / no meteo) | `useZerocostBundle.js` → fallback API immédiat |
| LKG fallback > 20 % | Toast utilisateur "Mode dégradé temporaire" + alert ops |

### 4.2 Rollback manuel Commandant

```bash
# Bascule immédiate vers API V20 (sans redéploiement frontend)
# Variable env runtime sur Cloudflare Worker ou edge function
echo 'REACT_APP_ZEROCOST_ENABLED=false' > /app/frontend/.env.runtime_override
sudo supervisorctl restart frontend
# Délai effet : < 10s grâce au hot reload React
```

### 4.3 Rollback du manifeste R2 (régression données)

```bash
# Pointage vers manifest v(N-1) en cas de tuiles corrompues
# Versionning manifeste : manifest.json (current), manifest_v1.json (rollback)
python3 tools/zerocost_manifest_rollback.py --target-version v1
```

---

## 5. INSTRUMENTATION & MONITORING

### 5.1 Métriques frontend (à publier dans Sentry/Datadog)

| Métrique | Cible Palier 4 | Source |
|---|---|---|
| `zerocost.cdn.hit_ratio` | ≥ 98 % | Header `cf-cache-status` |
| `zerocost.cdn.latency_p95_ms` | ≤ 100 ms | `performance.measure` |
| `zerocost.fallback.api_v20_ratio` | ≤ 2 % | `useZerocostBundle.js` events |
| `zerocost.fallback.lkg_ratio` | ≤ 5 % | `lkgCacheOmega.js` events |
| `zerocost.error.bundle_invalid` | 0 | `useZerocostBundle.js` parse errors |

### 5.2 Métriques backend (à publier dans Prometheus)

| Métrique | Cible | Source |
|---|---|---|
| `r2_objects_total{species}` | ≥ 7077 × 72 / spe pour P1 complet | `tools/zerocost_manifest_update.py` |
| `weather_cache_owm_fetches_total` | ≤ 30/jour | `weather_cache_regional_omega.get_stats()` |
| `weather_cache_owm_errors_total` | 0 | idem |
| `v20_bundle_fallback_calls_total` | ≤ 1 000/jour | FastAPI middleware |

### 5.3 Tableaux de bord requis

- **Grafana ZEROCOST** : CDN HIT, latence, fallback ratio, OWM quota usage, R2 objects count
- **Grafana Phase III LOCK** : confirmation aucune modification V10/V20 (file checksums)

---

## 6. PLAN DE VALIDATION FONCTIONNELLE PRÉ-BASCULE

### 6.1 Tests de conformité bundle (par espèce)

| Espèce | Cellule test | Validation |
|---|---|---|
| chevreuil | 45.47, -75.70 (Outaouais) | 7 corridors, 5 zones, meteo, ≥ 80 KB |
| orignal | 47.50, -71.50 (RF Laurentides) | 5-10 corridors, ≥ 80 KB |
| ours_noir | 48.50, -68.50 (BSL) | 5-10 corridors |
| dindon_sauvage | 45.20, -73.50 (Estrie) | 3-7 corridors, palette ambre |
| wapiti | 51.50, -67.80 (Côte-Nord) | bio_presence_mask correct si hors aire |
| coyote | 46.00, -72.00 (Mauricie) | 3-7 corridors, palette grise |

### 6.2 Tests anti-régression

- Comparaison bundle CDN vs bundle API V20 fresh sur 50 cellules pilotes
- Tolérance : ±5 % sur scores, identique pour corridors count / zones count
- Capture visuelle Leaflet (avant/après) sur Outaouais, BSL, Mauricie

### 6.3 Tests NEVER BLANK Ω

- Mode avion (offline) : LKG affiche dernier bundle valide
- CDN 404 simulé : fallback API V20 immédiat
- API V20 500 simulé : LKG_STALE + banner DEGRADED ambre

---

## 7. CALENDRIER PROPOSÉ

| Date | Action | Durée |
|---|---|---|
| J0 | Engagement pré-warm P1 (cluster k8s 256w ou local prolongé) | 1.9-31 jours |
| J(0+P) | Validation manifeste 509 K tuiles P1 complete | 1 jour |
| J(0+P+1) | Palier 1 SHADOW | 24h |
| J(0+P+2) | Palier 2 CANARY 10 % | 48h |
| J(0+P+4) | Palier 3 RAMP-UP 50 % | 5 jours |
| J(0+P+9) | Palier 4 FULL 100 % | permanent |

→ **Date Phase 4 100 % opérationnelle** : J(0+P+9), avec P=1.9 jours sur k8s 256w → **~12 jours total**.

---

## 8. DÉCISIONS COMMANDANT REQUISES

### 8.1 Engagement pré-warm P1
- ☐ Option A : déploiement k8s 256 workers (1.9 jours, $32 compute one-shot)
- ☐ Option B : déploiement k8s 64 workers (7.7 jours, $32 compute idem)
- ☐ Option C : exécution locale prolongée 16 workers (31 jours, $0)
- ☐ Option D : restreindre P1 à 3 RF prioritaires (2 500 cellules · ~0.7 jour local)

### 8.2 Brouillon QUOTA600 OWM
- ☐ Approuver le brouillon (`RAPPORT_WEATHERCACHE_BETA2_QUOTA600_Ω.md` — document séparé)
- ☐ Refuser et conserver TTL 30j actuel

### 8.3 Autorisation Phase 4
- ☐ Autoriser bascule séquentielle après pré-warm
- ☐ Reporter à un cycle ultérieur

---

**FIN PLAN MONTÉE EN CHARGE PHASE 4 · EN ATTENTE DIRECTIVE COMMANDANT**
