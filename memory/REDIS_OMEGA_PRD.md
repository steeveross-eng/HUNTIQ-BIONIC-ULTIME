# REDIS-Ω — Cache partagé multi-pod
## PHASE-REDIS-Omega — Scalabilité >10K utilisateurs
**MAJ:** 2026-04-18

## OBJECTIF
Scaling horizontal : un pod chauffé bénéficie à tous les pods Kubernetes via Redis central.
Cible : hit ratio ≥90% cross-pods pour 10K–50K utilisateurs concurrents.

## ARCHITECTURE
```
[Pod A] ──┐
[Pod B] ──┼── Redis partagé (L1) ── Disk pickle (L0)
[Pod C] ──┘         ↑
           LRU local 10K (L2, warm subset)
```

**Hiérarchie cache** :
- **L2** : LRU in-memory par pod (10 000 entries, sub-ms)
- **L1** : Redis partagé (namespace `v20:territoire:bundle:*`, TTL 24h)
- **L0** : Disk pickle `/app/backend/cache/territoire_bundle.pkl` (survive redémarrages)

## ACTIVATION
Définir la variable d'environnement **`REDIS_URL`** :
```bash
REDIS_URL=redis://:password@redis-service.default.svc.cluster.local:6379/0
```

Si `REDIS_URL` absent → **fallback silencieux sur LRU+disk** (comportement V11-SUPRA actuel maintenu, zéro régression).

## API `redis_omega.py`
| Fonction | Usage |
|---|---|
| `is_redis_enabled()` | Test connectivité (lazy) |
| `redis_get(key)` | Retourne payload ou None |
| `redis_set(key, value, ttl=86400)` | Stocke avec TTL |
| `redis_purge()` | Vide namespace v20:territoire:* |
| `redis_stats()` | Mémoire, nombre de clés |

## WIRING BUNDLE
`v20_performance_bundle.py._cache_get` :
1. Check LRU local → HIT retour
2. Miss LRU → check Redis
3. Redis HIT → warm LRU local → retour
4. Miss total → compute full + store L2 + L1

`_cache_set` : écrit simultanément L2 (LRU) et L1 (Redis).

## FAILURE MODE
- Redis down : catch silencieux, fallback LRU
- Timeout 2s connect / 2s socket
- `max_connections=64`
- Zéro blocage sur erreur Redis

## VALIDATION
Endpoint stats inclut `redis_omega` :
```json
{
  "cache_size": 3,
  "cache_max": 10000,
  "redis_omega": {
    "enabled": false,
    "reason": "REDIS_URL non defini ou connect failed"
  }
}
```

Quand Redis activé :
```json
{
  "redis_omega": {
    "enabled": true,
    "url": "redis-service:6379/0",
    "bundle_keys": 347,
    "tile_keys": 1823,
    "memory_used": "42.3M",
    "memory_peak": "58.1M"
  }
}
```

## DÉPLOIEMENT KUBERNETES (pour 10K+ users)
1. Déployer Redis (Bitnami chart recommandé) ou utiliser Redis managé
2. Ajouter `REDIS_URL` dans secrets backend
3. Scaler `backend` replicas (3-10 pods)
4. Le cache warmup de chaque pod se propage via Redis à tous

## MESURES (baseline sans Redis, à valider post-déploiement)
- LRU hit : ~100ms (local)
- Redis hit projection : ~110-130ms (overhead 10-30ms réseau interne)
- Compute : 2.7s
- Warmup partagé : 1 pod compute, N pods en bénéficient instantanément

## Fichiers
- `backend/engines/v8_institutional/redis_omega.py` (nouveau)
- `backend/engines/v8_institutional/v20_performance_bundle.py` (wiring L1/L2)
- `requirements.txt` : `redis>=5` ajouté automatiquement au prochain freeze
