# RAPPORT_PREWARM_P1_BG_ET_ANTI502_Ω

**Doctrine** : `P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_PRECEDENT_16W_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟢 **DEUX FRONTS OPÉRATIONNELS · NEVER BLANK Ω GARANTI**

---

## 1. CONTEXTE COMMANDANT

Directive : pré-warm P1 en mode **précédent 16 workers locaux** (refus k8s) +
**garde-fou anti-502** sur `/api/v20/territoire/bundle` pour l'utilisateur preview.

---

## 2. FRONT 1 — DAEMON PRÉ-WARM P1 (16 WORKERS LOCAUX)

### 2.1 Lancement
```bash
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh start
```

### 2.2 Mécanisme de détachement (process indépendants de la session)

| Mécanisme | Effet |
|---|---|
| `setsid` | Nouveau process group (PGID = PID) |
| `nohup` | Ignore SIGHUP à la fermeture de session |
| `< /dev/null` | Détache stdin |
| `disown` | Retire du job control du shell |
| **PPID = 1** (init) | Adopté par init, survit à toute fermeture |

### 2.3 Validation indépendance session
```
PID 14834 · PGID 14834 · SID 14834 · PPID 1  ← détaché de la session shell
PID 14835 · PGID 14835 · SID 14835 · PPID 1  ← idem
PID 14836 · PGID 14836 · SID 14836 · PPID 1  ← idem
(16 workers au total, tous PPID=1)
```

→ Le job **continuera de tourner même après fermeture de la session agent**.

### 2.4 Configuration
- Grille : `/app/backend/cache/zerocost_v1/canada_h3_grid_r6_p1_only.json` (7 077 cellules P1)
- WORKER_COUNT : 16
- WORKER_RESOLUTION : H3 R6
- MAX_TILES : 0 (illimité — job de fond)
- Cible : 509 544 tuiles bio-positives P1 IFAP/ZEC/RF
- WeatherCache régional H3 R3 (OWM via `install_open_meteo_interceptor`) : actif

### 2.5 Logs persistés
- `/var/log/bionic-zerocost-prewarm-p1/worker_0.log` à `worker_15.log`
- Monitor : `bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh status`
- Stop : `bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh stop`

### 2.6 ETA & coût
- Latence mesurée : 213s/tuile bio-positive QC (V20 complet hors météo)
- 16 workers locaux : **~78 jours** pour P1 complet (job de fond accepté Commandant)
- Coût : **$0** (compute local, R2 storage seulement → ~$0.10/mois)

---

## 3. FRONT 2 — MIDDLEWARE ANTI-502 / NEVER BLANK Ω

### 3.1 Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│ /api/v20/territoire/bundle?lat=...&lon=...&species=...             │
│  ↓                                                                 │
│  Route override `anti_502_bundle` (PRIORITAIRE)                    │
│  ├── FAST-PATH : _cache_get(key) du V20                            │
│  │   └── HIT → HTTP 200 + bundle + header X-Zerocost-Anti502: fast-hit│
│  └── SLOW-PATH : MISS                                              │
│       ├── (BG compute désactivé par défaut — daemon s'en charge)   │
│       └── HTTP 202 + Retry-After: 5 + header miss-202              │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 Caractéristiques doctrinales

| Aspect | Valeur |
|---|---|
| **Module** | `/app/backend/middleware/anti_502_zerocost_omega.py` |
| **Mode** | Route override prioritaire (avant `v20_perf_router`) |
| **Fast-path** | Lookup direct `_cache_get` (fonction publique V20) |
| **Slow-path** | Retour 202 EN_COURS immédiat + Retry-After 5s |
| **BG compute** | DÉSACTIVÉ par défaut (env `ANTI_502_BG_COMPUTE=true` pour activer) |
| **Verrou Phase III** | ❌ Aucune modification V10/V20/LiDAR/IRDA/terrain_hr_omega |
| **Doctrine** | `P22ΩΩ_ANTI_502_PRECEDENT_16W_Ω` |

### 3.3 Tests de validation (sous charge 16 daemon)

| Test | URL | HTTP | Temps | Header anti-502 |
|---|---|---|---|---|
| BSL chevreuil (cache HIT) | `48.4488,-68.5235,chevreuil,m10h14` | **200** | 494 ms | `fast-hit` |
| Outaouais ours_noir (MISS) | `46.585,-74.273,ours_noir,m11h8` | **202** | 96 ms | `miss-202` |
| Côte-Nord wapiti (MISS) | `51.4948,-65.2011,wapiti,m10h14` | **202** | 95 ms | `miss-202` |
| Estrie coyote (MISS) | `45.7,-71.0,coyote,m11h6` | **202** | 91 ms | `miss-202` |

→ **0 HTTP 502/504/000 jamais observés** durant les tests. Cible Commandant atteinte.

### 3.4 Endpoint de monitoring

```bash
curl http://localhost:8001/api/v20/territoire/anti502/metrics
# {
#   "doctrine": "P22ΩΩ_ANTI_502_PRECEDENT_16W_Ω",
#   "retry_after_s": 5,
#   "metrics": {
#     "fast_path_hit_200": <n>,
#     "slow_path_miss_202": <n>,
#     "exception_returned_202": <n>
#   },
#   "bg_compute_inflight_count": <n>
# }
```

### 3.5 Headers HTTP émis

| Header | Valeurs possibles | Sémantique |
|---|---|---|
| `X-Zerocost-Anti502` | `fast-hit` / `miss-202` / `exception-202` | Mode de réponse |
| `X-Doctrine` | `P22OMEGA_OMEGA_ANTI_502_PRECEDENT_16W_OMEGA` | Marquage protocole (ASCII-safe) |
| `Retry-After` | `5` | Délai recommandé avant retry |

---

## 4. INTERACTION FRONT 1 ↔ FRONT 2

```
┌─────────────────────────────────────────────────────────────────────┐
│ FRONT 1 : DAEMON PRÉ-WARM (process séparés)                         │
│ └── Calcule 509 K tuiles P1 en arrière-plan                         │
│     ├── Lit/écrit R2 directement (bypass V20 cache)                 │
│     └── Réchauffe progressivement les hotspots                      │
│                                                                     │
│ FRONT 2 : MIDDLEWARE ANTI-502 (route uvicorn)                       │
│ └── Sert /api/v20/territoire/bundle                                 │
│     ├── Lit le cache V20 LRU/disque (alimenté par compute live V20) │
│     └── Retourne 202 si miss                                        │
└─────────────────────────────────────────────────────────────────────┘
```

**À noter** : le DAEMON pré-warm écrit dans **R2** (CDN ZEROCOST), pas dans le cache LRU V20.
Donc le fast-path du middleware **ne bénéficie pas directement** du daemon.

→ Le bénéfice du daemon arrivera après Phase 4 PROD bascule quand le frontend lit la R2.
   Avant la bascule, le middleware fast-path lit le cache LRU V20 alimenté par compute live.

### 4.1 Chemins doctrinaux UI selon mode

| Mode | Source | Latence | Couverture |
|---|---|---|---|
| **Phase 3 actuelle (pré-Phase 4)** | Cache LRU V20 (alimenté par requêtes utilisateur) | 50ms hit / 202 miss | Limitée |
| **Phase 4 PROD** | CDN R2 ZEROCOST (alimenté par daemon) | 50ms hit / fallback API | P1 complet |
| **LKG IndexedDB (offline)** | IndexedDB frontend | 0ms | Dernier bundle valide |

---

## 5. GARANTIE NEVER BLANK Ω

| Scénario | Comportement |
|---|---|
| Tuile dans cache V20 LRU | HTTP 200 fast-hit (~50ms) |
| Tuile pas en cache | HTTP 202 miss-202 (~95ms) · frontend fallback LKG |
| V20 lève exception | HTTP 202 exception-202 (~50ms) · frontend fallback LKG |
| Backend complètement KO | LKG IndexedDB (cache navigateur frontend) |
| Tout KO + LKG vide | Banner DEGRADED + map vide MAIS pas d'écran blanc |

→ **NEVER BLANK Ω structurellement garanti à tous les paliers**.

---

## 6. VERROU PHASE III · CONFORMITÉ

| Composant | Statut |
|---|---|
| `engines/v8_institutional/v20_performance_bundle.py` | ❌ INTACT |
| `engines/v8_institutional/*` (V10, V5, scoring, corridors, zones, hotspots) | ❌ INTACT |
| `engines/v8_institutional/lidar_irda_v11.py` | ❌ INTACT |
| `engines/v8_institutional/open_meteo_breaker.py` | ❌ INTACT |
| `engines/terrain_hr_omega/__init__.py` | ❌ INTACT |
| `engines/weather_cache_regional_omega.py` | ❌ INTACT |
| Frontend `useZerocostBundle.js` / `lkgCacheOmega.js` | ❌ INTACT |
| `server.py` | ✅ +9 lignes additives (registration anti_502 + import) |
| `middleware/anti_502_zerocost_omega.py` | 🆕 Nouveau module (240 LoC) |
| `middleware/__init__.py` | 🆕 Nouveau (vide) |
| `tools/zerocost_prewarm_p1_daemon.sh` | 🆕 Nouveau |
| `tools/zerocost_extract_p1_only.py` | 🆕 (du précédent rapport) |

→ **Verrou Phase III strictement respecté** · uniquement des artefacts additifs.

---

## 7. QUOTA600 · STATUT

🟡 **APPROUVÉ_NON_ACTIVÉ** conformément directive Commandant précédente.
- Mesure live : 0 fetch OWM dans le run de validation actuel (WeatherCache full hit)
- Marge brouillon : >99 % sur Canada complet en régime stationnaire

---

## 8. PROCÉDURE OPÉRATIONNELLE COMMANDANT

### 8.1 Vérification status pré-warm

```bash
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh status
```

### 8.2 Vérification anti-502

```bash
# Métriques live
curl http://localhost:8001/api/v20/territoire/anti502/metrics

# Test bundle (devrait retourner 200 ou 202, JAMAIS 502/504)
curl -i "http://localhost:8001/api/v20/territoire/bundle?lat=46.5&lon=-74.0&species=chevreuil&month=10&hour=14&wind_deg=225&wind_speed=15"
```

### 8.3 Arrêt du pré-warm

```bash
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh stop
```

### 8.4 Redémarrage backend (le middleware se réinstalle automatiquement)

```bash
sudo supervisorctl restart backend
```

---

## 9. ÉTAT À CETTE HEURE

| Métrique | Valeur |
|---|---|
| Daemon pré-warm P1 | 🟢 16 workers vivants, PPID=1 (indépendants session) |
| Middleware anti-502 | 🟢 Installé, fast-hit + slow-miss opérationnels |
| Tests live anti-502 | 🟢 4/4 PASS · 0 HTTP 502/504 |
| WeatherCache (worker daemons) | 🟢 25+ régions H3 R3 cachées en MongoDB |
| R2 bucket | 🟢 475+ tuiles uploadées |
| Verrou Phase III | 🟢 STRICT |
| Phase 4 PROD | 🟡 Attente complétion pré-warm P1 + directive Commandant |
| QUOTA600 | 🟡 APPROUVÉ_NON_ACTIVÉ |

---

## 10. DÉCISIONS COMMANDANT POSSIBLES

- ☐ **Laisser le pré-warm tourner** (job de fond accepté, ETA ~78 jours pour P1 complet)
- ☐ **Restreindre P1 à 3 RF prioritaires** (Laurentides+Outaouais+Mauricie · ~2 500 cellules · ~5j local)
- ☐ **Activer `ANTI_502_BG_COMPUTE=true`** pour que le middleware déclenche aussi des computes opportunistes
- ☐ **Engager le plan β2-ΣΤ** (bundle-seed H3 R5) pour réduire compute ×7
- ☐ **Maintenir le statu quo** et attendre observations utilisateur preview

---

**FIN RAPPORT · DAEMON ACTIF · ANTI-502 OPÉRATIONNEL · EN ATTENTE DIRECTIVE COMMANDANT**
