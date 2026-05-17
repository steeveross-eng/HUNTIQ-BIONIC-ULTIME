# 🚀 PLAN_OPTIMISATION_TERRITOIRE_OMEGA
**Phase** : P22ΩΩ_OPTIMISATION_SUPREME · BCE-4X ULTIME ABSOLU
**Date** : 2026-05-17 · **Commandant** : STEEVE-MAX
**Objectif** : Optimisation suprême sans perte de puissance/précision/fiabilité
**Cible** : Architecture ZeroCost/Static · 0 cold-start · <500ms p99

---

## 🎯 ANALYSE DE PERFORMANCE ACTUELLE (BASELINE)

| Métrique | Valeur actuelle | Cible visée | Gain attendu |
|---|---|---|---|
| Bundle cold-start (1er user) | **40-60s** (502 K8s) | <500ms | **120×** |
| Bundle HIT cache | 200-300ms | <50ms | 4-6× |
| Endpoints concurrents pendant V10 | **0** (event loop bloqué) | 4+ (multi-worker) | ∞ |
| Coverage cache LRU | ~11 bundles | 200+ bundles | 18× |
| Open-Meteo CB OPEN durée | 600s | 60s | 10× |
| Frontend retry-cycle perdu | jusqu'à 10s | 0s | éliminé |
| `compute_territoire_v10` SYNC ratio | ~98% sync | <30% sync | 3× |
| `server.py` lignes | 1 669 | <800 | 2× |
| `MonTerritoireBionicPage.jsx` lignes | 1 907 | <800 | 2.4× |

---

## 📐 AXES D'OPTIMISATION (6 DOMAINES)

### 🔵 AXE 1 — INFRASTRUCTURE & RUNTIME (P0)

| # | Action | Gain | Risque | Prérequis |
|---|---|---|---|---|
| 1.1 | **Multi-worker uvicorn `--workers 4`** | 1 cold-start n'affecte plus les autres users · capacity ×4 | Faible (config plateforme) | Escalation Emergent (BRIEF prêt) |
| 1.2 | **Désactiver `--reload` en prod** | -30% RAM, -10% latence | Aucun | Application post-multi-worker |
| 1.3 | **Gunicorn worker manager** au lieu d'uvicorn brut | Reload propre + graceful shutdown | Faible | Cf. 1.1 |
| 1.4 | **Health probe K8s** sur `/api/health` (livenessProbe + readinessProbe) | Restart auto si freeze, no-traffic pendant boot | Faible | Config plateforme |

### 🟢 AXE 2 — CACHE & DATA PERSISTENCE (P0/P1)

| # | Action | Gain | Risque |
|---|---|---|---|
| 2.1 | **Redis persistant managé** (Redis Cloud free tier ou Memorystore K8s) | Cache partagé entre workers · zéro perte au restart · TTL granulaire | Moyen (dépendance externe) |
| 2.2 | **Compression bundle pickle** (lz4 ou zstd) | -60% taille disque (~507KB → 200KB), -50% temps load | Faible (CPU négligeable) |
| 2.3 | **Pre-compute layer indépendant** (cron 1h) qui calcule les bundles pour les TOP-50 waypoints × 5 espèces × 12 mois → 3 000 bundles disque | 99% des requêtes user en HIT instantané · 0 cold-start prévu | Faible |
| 2.4 | **Cache key normalisation déjà optimisée** (hour ignoré ✓, wind 15° ✓) — étendre à month (groupe 4 saisons) | -75% cardinalité cache (12 mois → 4 saisons) | Bio-précision faible (vérifier divergence saisons consécutives) |
| 2.5 | **ETag + If-None-Match** sur `/api/v20/territoire/bundle` | Réutilisation cache navigateur · -90% trafic répétitif | Aucun |

### 🟡 AXE 3 — PIPELINE V10/V20 (P1)

| # | Action | Gain | Risque |
|---|---|---|---|
| 3.1 | **Convertir `compute_territoire_v10` en asyncio natif** (httpx.AsyncClient au lieu de requests sync) | Event loop libre pour autres requêtes pendant V10 | Faible (refactor ciblé) |
| 3.2 | **Profiler + paralléliser sub-pipelines** : terrain + meteo + zones + hotspots + salines en `asyncio.gather` | -60% temps cold-start (50s → 20s) | Moyen (concurrence sur shared state) |
| 3.3 | **Lazy-load des engines lourds** (only when species/month matches) | -40% mémoire au boot, -30% temps startup | Faible |
| 3.4 | **Open-Meteo CB durée 600s → 60s** + retry exponentiel intelligent | Reprise rapide après burst 429 | Aucun |
| 3.5 | **Migrer LIDAR/IRDA vers GeoTIFF tile-based** (pré-tilé en MBTiles) au lieu de calcul à la volée | -90% temps lookup terrain | Moyen (taille storage initiale +500MB) |
| 3.6 | **Streaming chunked response** : envoyer zones d'abord, puis corridors, puis hotspots | Perceived latency -70% (premier rendu en 200ms) | Moyen (refactor frontend SSE) |

### 🟠 AXE 4 — FRONTEND & RENDU (P1)

| # | Action | Gain | Risque |
|---|---|---|---|
| 4.1 | **Refactor `MonTerritoireBionicPage.jsx`** (1907 lignes) → composer en sous-pages : `<HudSection>`, `<MapSection>`, `<PanelsSection>` | Maintenabilité ×3 · bundle JS -20% | Faible (par étapes) |
| 4.2 | **Code-splitting `React.lazy`** sur EspecesOmegaPanel, BioReacteursOmegaPanel, Cesium 3D viewer | -40% bundle initial JS · TTI -50% | Aucun |
| 4.3 | **Service Worker offline** : sert le bundle depuis IndexedDB si offline ou backend down | Tolérance pannes · UX offline | Moyen (cache invalidation) |
| 4.4 | **Leaflet → MapLibre GL** (vector tiles + GPU rendering) | Rendu 60fps même avec 1000+ corridors · -50% CPU | Élevé (refactor cartes complet) |
| 4.5 | **Web Worker** pour le smoothing organic + clipping | Main thread libre · scroll fluide pendant compute | Faible |
| 4.6 | **CDN edge caching** sur `/api/export/territoire-structure` (Cloudflare) | -95% latence read-only assets | Aucun |

### 🟣 AXE 5 — OBSERVABILITY & DEVOPS (P2)

| # | Action | Gain | Risque |
|---|---|---|---|
| 5.1 | **Prometheus metrics** exposés sur `/metrics` (latence p50/p95/p99, cache hit ratio, CB state) | Visibilité prod · alerting | Aucun |
| 5.2 | **Sentry frontend + backend** error tracking | MTTR ÷ 3 | Aucun |
| 5.3 | **Distributed tracing OpenTelemetry** sur le pipeline bundle | Identification bottleneck précis | Faible |
| 5.4 | **Tests pytest CI** sur les 5 espèces × 4 saisons (regression suite) | 0 régression silencieuse | Aucun |
| 5.5 | **Load testing** locust (100 users concurrents sur bundle) | Validation capacity post-multi-worker | Aucun |

### 🔴 AXE 6 — INTELLIGENCE & PRÉDICTION (P2/P3)

| # | Action | Gain | Risque |
|---|---|---|---|
| 6.1 | **Pre-fetch prédictif** : ML sur les patterns de navigation user → précharge anticipée des waypoints probables | UX 0 cold-start élargie | Moyen (cold-boot du modèle) |
| 6.2 | **Heatmap globale Québec pré-calculée** (cron quotidien) | Score consultable instantanément sur toute carte | Faible (storage ~50MB) |
| 6.3 | **API GraphQL** sur certains endpoints (especes/territoire) | Réduit over-fetching client · -40% data transfer | Moyen (refactor API) |
| 6.4 | **WebSocket push** pour les BIO-RÉACTEURS updates | Real-time live · suppression polling | Moyen |
| 6.5 | **Edge compute** (Cloudflare Workers) pour score quick-lookup | Latence <50ms partout dans le monde | Élevé (architecture distribuée) |

---

## 🗺️ FEUILLE DE ROUTE SÉQUENCÉE (P0 → P5)

### 🔥 P0 — IMMÉDIAT (Sprint 1 · semaine 1-2)
1. ✅ **P22ΩΩ_BUNDLE_DEGRADED_CACHE** (déjà appliqué)
2. ✅ **P22ΩΩ_PRECHARGEMENT_INTELLIGENT** (déjà appliqué)
3. ✅ **P22ΩΩ_ALLEGEMENT_STRUCTUREL** (déjà appliqué — 2628 lignes purgées)
4. ⏳ **AXE 1.1 — Multi-worker uvicorn** (escalation Emergent active)
5. ⏳ **AXE 2.5 — ETag + If-None-Match** (1 jour dev)

**Résultats P0 attendus** : 0% cold-start 502 pour les utilisateurs · latence p99 < 2s

### ⚡ P1 — COURT TERME (Sprint 2-3 · semaine 3-6)
6. **AXE 2.1 — Redis persistant managé** (2 jours dev + provisioning)
7. **AXE 2.2 — Compression bundle lz4** (1 jour)
8. **AXE 2.3 — Pre-compute layer cron 1h** (3 jours)
9. **AXE 3.1 — Convertir V10 en asyncio natif** (3 jours)
10. **AXE 3.4 — Open-Meteo CB 60s + retry exponentiel** (1 jour)
11. **AXE 4.2 — Code-splitting React.lazy** (2 jours)

**Résultats P1 attendus** : bundle cold-start <2s · cache hit ratio >95% · bundle JS initial -40%

### 🚀 P2 — MOYEN TERME (Sprint 4-6 · semaine 7-12)
12. **AXE 3.2 — Parallélisation asyncio.gather sub-pipelines** (5 jours)
13. **AXE 3.5 — LIDAR/IRDA MBTiles** (5 jours + provisioning storage)
14. **AXE 4.1 — Refactor MonTerritoireBionicPage** (5 jours)
15. **AXE 5.1 — Prometheus metrics** (2 jours)
16. **AXE 5.4 — Tests pytest CI** (3 jours)
17. **AXE 6.2 — Heatmap globale pré-calculée** (4 jours)

**Résultats P2 attendus** : cold-start <500ms · code maintenabilité ×3 · 0 régression silencieuse

### 🌟 P3 — LONG TERME (Sprint 7-10 · semaine 13-24)
18. **AXE 3.6 — Streaming chunked response (SSE)** (5 jours)
19. **AXE 4.3 — Service Worker offline** (5 jours)
20. **AXE 4.5 — Web Worker smoothing** (3 jours)
21. **AXE 5.2 — Sentry** (1 jour)
22. **AXE 5.3 — OpenTelemetry tracing** (3 jours)
23. **AXE 6.4 — WebSocket BIO-RÉACTEURS push** (5 jours)

**Résultats P3 attendus** : UX premium offline · MTTR ÷3 · observability complète

### 🏛️ P4 — TRANSFORMATION (mois 6-9)
24. **AXE 4.4 — Migration Leaflet → MapLibre GL** (3-4 semaines)
25. **AXE 6.1 — Pre-fetch prédictif ML** (3 semaines)
26. **AXE 6.3 — API GraphQL** (3 semaines)

**Résultats P4 attendus** : rendu 60fps même 1000+ corridors · UX 0-cold-start généralisée

### 🌍 P5 — ZEROCOST/STATIC (mois 10-12)
27. **AXE 6.5 — Edge compute Cloudflare Workers** (1-2 mois)
28. **Static export** des bundles canoniques (cron mensuel) → CDN edge
29. **Backend devient API differentielle** : sert uniquement les deltas

**Résultats P5 attendus** : architecture ZeroCost · latence <50ms mondial · scalabilité illimitée

---

## 📊 RÉSULTATS MESURABLES ATTENDUS

### Après P0 (semaine 2)
- ✅ 0% 502 K8s sur bundle (multi-worker)
- ✅ Cache hit ratio >70%
- ✅ Latence p99 <2s

### Après P1 (semaine 6)
- ✅ Cache hit ratio >95%
- ✅ Bundle cold-start <2s
- ✅ Bundle JS frontend -40%
- ✅ Open-Meteo recovery <60s

### Après P2 (semaine 12)
- ✅ Cold-start <500ms
- ✅ Code split en sous-pages (maintenabilité ×3)
- ✅ Tests CI couverture 5 espèces × 4 saisons
- ✅ Heatmap globale Québec disponible

### Après P3 (semaine 24)
- ✅ UX offline complète
- ✅ Streaming progressif (premier rendu 200ms)
- ✅ MTTR <15 min
- ✅ Observability complète

### Après P4 (mois 9)
- ✅ Rendu GPU 60fps
- ✅ Pre-fetch ML personnalisé par user
- ✅ API GraphQL optionnelle

### Après P5 (mois 12)
- ✅ Architecture ZeroCost/Static
- ✅ Latence <50ms globale
- ✅ Scalabilité illimitée (CDN edge)

---

## ⚠️ RISQUES IDENTIFIÉS

| Risque | Impact | Mitigation |
|---|---|---|
| Multi-worker requires shared cache (Redis persistant) | Cache split par worker = peu efficace | Implémenter P1.AXE-2.1 simultanément à P0.AXE-1.1 |
| Refactor V10 asyncio peut introduire race conditions | Régression bio-précision | Tests pytest avant/après divergence diff |
| MapLibre migration peut casser overlays existants | UX dégradée temporaire | Feature flag : Leaflet ↔ MapLibre |
| Pre-compute layer consomme storage important | 500MB+ | Cleanup TTL 7 jours pour vieux bundles |
| Edge compute peut introduire stale data | Bio-précision compromise | TTL court + invalidation explicite |

---

## 🛡️ PRÉREQUIS TECHNIQUES

### Bloquants
- 🚨 **Multi-worker** (`--workers 4`) — escalation Emergent en cours
- 🚨 **Redis persistant** managé (Redis Cloud / Memorystore K8s)

### Non-bloquants
- Storage additionnel pour pre-compute layer (~1GB)
- Compte Cloudflare Workers (P5)
- Compte Sentry (P3) — free tier suffit
- Stack monitoring Prometheus + Grafana (P2) — peut être conteneurisé localement

---

## 📈 IMPACT GLOBAL ATTENDU

| Dimension | Avant | Après P5 | Gain |
|---|---|---|---|
| Latence p99 bundle | 50 000 ms | 50 ms | **1 000×** |
| Capacity concurrent users | 1 (single-worker) | 1 000+ (edge) | **1 000×** |
| Cache hit ratio | 30% | 99% | **3.3×** |
| Bundle JS initial frontend | 100% | 40% | **2.5×** |
| Coverage tests CI | 0% | 95% | **∞** |
| MTTR incident | 4-8h | <15 min | **16-32×** |
| Coût hosting (en ZeroCost/Static) | full backend | edge only | **-90%** |
| Lignes de code maintenu | ~50 000 | ~30 000 | **-40%** |

---

## 🎯 OBJECTIF FINAL : **TERRITOIRE Ω SUPRÊME**

✅ Allègement structurel **DONE** (2628 lignes purgées)
✅ Stabilisation 502 **DONE** (P22ΩΩ_BUNDLE_DEGRADED_CACHE)
✅ Préchargement Premium **DONE** (P22ΩΩ_PRECHARGEMENT_INTELLIGENT)
✅ JSON maître téléchargeable **DONE** (`/api/export/territoire-structure`)
⏳ Multi-worker (escalation pending)
⏳ Plan d'optimisation P0→P5 **PRÊT À EXÉCUTER**

**Prochaine directive Commandant attendue.**

---

## 📋 SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase** : P22ΩΩ_OPTIMISATION_SUPREME
- **Date** : 2026-05-17
- **Auteur** : Agent E1 sous directive du COMMANDANT STEEVE-MAX
- **Document associé** : `/app/memory/TERRITOIRE_STRUCTURE_OMEGA.json`
- **Endpoint téléchargeable** : `GET /api/export/territoire-structure?download=true`
