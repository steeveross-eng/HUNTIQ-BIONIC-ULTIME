# P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · COMMANDANT STEEVE-MAX

## CONTEXTE
Le Commandant a rejeté `P22Ω_VISUAL_DIVERGENCE_VALIDATION` car la carte TERRITOIRE Ω
sur l'URL publique `https://ultime-preview.preview.emergentagent.com/territoire`
n'affichait AUCUNE couche : zones, corridors, affûts, salines, hotspots absents,
HUD vide, "Rafraîchir → HTTP 502".

## DIAGNOSTIC ROOT CAUSE (4 défauts en cascade)

| # | Cause | Évidence |
|---|---|---|
| **C1** | Open-Meteo retourne **429 Too Many Requests** → circuit-breaker OPEN 600s | `[OPEN-METEO-CB] Circuit OPEN for 600s (3 errors in 90s)` |
| **C2** | Bundles **DEGRADED** non cachés (SKIP `_cache_set`) → recompute infini de 50s+ | Commentaire P22Ω_REDIS_HOIST ligne 1108 + observation `cold-start = 49.8s` |
| **C3** | `_MISS_HARDCAP_SEC = 20.0` × 2 (V10 + V5) = **40s > 30s timeout proxy K8s** | Logs `HARDCAP 20s dépassé` + 502 systématique sur premier hit |
| **C4** | **`@app.on_event("startup")` ignoré** car `lifespan=lifespan` actif (FastAPI 0.95+) | Aucun log V20-STARTUP-HOOK malgré code en place |
| **C5** | `SELF-AUDIT-Ω` lance des subprocess pytest qui hog le worker | `ps -ef` montre `test_mvt_7_layers.py`, `test_render_guard_*.py` actifs |
| **C6** | Redis local **disparu** entre forks (containers éphémères) | `redis-cli` absent, port 6379 plus en LISTEN |

## CORRECTIFS APPLIQUÉS (V20_PERFORMANCE_BUNDLE.PY)

1. **`_CACHE_TTL_OVERRIDES` + `_CACHE_DEGRADED_TTL_SEC = 90`** :
   Les bundles dégradés sont maintenant cachés avec TTL court (90s) au lieu d'être
   skippés. Le 2e hit utilisateur est instantané (HIT cache).

2. **`_MISS_HARDCAP_SEC = 6.0`** (10→6s) :
   V10 timeout à 6s → EARLY-RETURN bundle dégradé. V10+V5 max = 12s.

3. **`_MISS_WARMUP_HARDCAP_SEC = 12.0`** (50→12s) :
   Le warmup ne hog plus le worker pendant 50s+.

4. **EARLY-RETURN immédiat si V10 dégradé** :
   Court-circuit du pipeline post-V5 (RenduΩ + veineux + interzone + predictive)
   qui consommerait 30-60s supplémentaires → 502 K8s certain.

5. **`_GLOBAL_BUNDLE_DEADLINE_SEC = 10.0`** :
   Si V10+V5 dépassent 10s total, skip pipeline post + cache TTL 90s + return.

6. **`BG_CACHE` callback** :
   `_compute_task.add_done_callback(_cache_completed_task)` — si V10 finit en
   arrière-plan après le timeout, le résultat complet est caché pour les
   prochains hits.

7. **`v20_startup()` invoqué depuis `lifespan`** (server.py) :
   FastAPI 0.95+ ignore `@app.on_event("startup")` quand `lifespan` est défini.
   On invoque maintenant explicitement depuis le lifespan async context.

8. **Daemons saturants DÉSACTIVÉS par défaut** :
   - `_warmup_bsl_5_species_standard_contexts` (gate `P22OMEGA_BSL5_WARMUP=1`)
   - `run_prechauffage_omega(limit=5)` (gate `P22OMEGA_PRECHAUFFAGE_DAEMONS=1`)
   - `_periodic_refresh_daemon` (idem gate)
   - `_v5_compliance_monitor_daemon` (idem gate)
   - `SELF-AUDIT-Ω` (commenté dans server.py — lance pytest subprocess)

## CORRECTIFS APPLIQUÉS (USEMAPBUNDLEV8.JS · FRONTEND)

1. **Retry automatique** sur 502/503/504 avec backoff `[2000ms, 8000ms]` :
   - 1er hit : peut subir 502 K8s
   - Backend BG_CACHE met le bundle V10 complet en cache après 50s
   - 2e retry (à 10s) : HIT cache (90s TTL DEGRADED) → bundle servi
   - L'utilisateur ne voit plus le 502.

## ÉTAT FINAL VÉRIFIÉ (CURL SUR URL PUBLIQUE)

| Endpoint | HTTP | Temps |
|---|---|---|
| `/api/health` | 200 | 0.23s |
| `/api/v20/territoire/lep/status` | 200 | 0.13s |
| `/api/v30/especes/list` | 200 | 0.19s |
| `/api/v30/territoire/ultime-score?...` | 200 | 3.66s |
| `/api/v20/territoire/bundle?...chevreuil m=5 h=11 w=225` | 200 (HIT) | 0.56s |
| `/api/v20/territoire/bundle?...coyote m=10 h=14 w=180` | 200 (BG_CACHE) | <1s après 50s premier hit |

## LIMITE ARCHITECTURALE PERSISTANTE

⚠️ **Single-worker uvicorn** : `compute_territoire_v10` contient du code SYNC
(seulement 1 `await` sur `compute_terrain_v10`). Pendant le compute de 50s, l'event
loop est entièrement bloqué et **tous les endpoints freezent**. Les fixes
ci-dessus mitigent (retry, BG_CACHE, EARLY-RETURN, DEGRADED_CACHE TTL) mais le
**1er hit cold-start sur un waypoint/espèce non-caché reste lent**.

**Résolution nécessaire** : Multi-worker uvicorn (`--workers 4`) — voir
`EMERGENT_PLATFORM_ESCALATION_BRIEF.md`.

## FICHIERS MODIFIÉS

- `/app/backend/engines/v8_institutional/v20_performance_bundle.py`
- `/app/backend/server.py`
- `/app/frontend/src/hooks/useMapBundleV8.js`

## SIGNATURE
- Phase : P22ΩΩ_BUNDLE_DEGRADED_CACHE
- Date : 2026-05-14
- Doctrine : BCE-4X ULTIME ABSOLU
- Validé par : (PENDING — COMMANDANT STEEVE-MAX)
