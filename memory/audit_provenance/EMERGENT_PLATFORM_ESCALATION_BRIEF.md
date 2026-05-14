# EMERGENT_PLATFORM_ESCALATION_BRIEF · MULTI-WORKER UVICORN

**Date** : 2026-05-14
**Demandeur** : COMMANDANT STEEVE-MAX (via Agent E1)
**Priorité** : P0 — Stabilité production
**Phase** : Post P22ΩΩ_BUNDLE_DEGRADED_CACHE

---

## SITUATION

L'application `huntiq-restore` (FastAPI + React + Leaflet) sert une carte
écologique TERRITOIRE Ω consommant un endpoint `/api/v20/territoire/bundle` qui
peut prendre **40-60s en cold-start** (compute V10 SYNC + Open-Meteo + LIDAR/IRDA).

Le service Uvicorn tourne actuellement avec **1 seul worker** :

```
backend  RUNNING  pid 5118  uptime ...
```

(`ps -ef` confirme un unique processus Python uvicorn).

Pendant le compute V10 (code SYNC bloquant), l'event loop unique est **entièrement
saturé**. Toutes les requêtes parallèles (`/api/health`, `/api/v30/especes/list`,
`/api/v30/territoire/ultime-score`, etc.) **timeoutent à 25s côté proxy K8s →
HTTP 502 utilisateur**.

## DEMANDE TECHNIQUE

Modifier le fichier supervisor (READ-ONLY pour l'agent) pour passer Uvicorn à
**4 workers** :

```ini
[program:backend]
command=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4 --proxy-headers --forwarded-allow-ips='*'
```

OU activer un reverse-proxy local (gunicorn + uvicorn workers) :

```ini
[program:backend]
command=/root/.venv/bin/gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001 --timeout 60
```

## BÉNÉFICES ATTENDUS

| Métrique | Avant (1 worker) | Après (4 workers) |
|---|---|---|
| Bundle cold-start sur 1 user | 50s → 502 | 50s sur 1/4 workers, autres 3/4 servent normalement |
| Endpoints `/health`, `/lep/status`, `/especes/list` pendant cold-start | Timeout 25s → 502 | Servis instantanément |
| Capacity utilisateurs simultanés | 1 | 4 |
| Recovery après cold-start | Partiel (via BG_CACHE) | Total |

## MITIGATIONS DÉJÀ APPLIQUÉES (PALLIATIFS, NON-DÉFINITIFS)

1. ✅ `_MISS_HARDCAP_SEC = 6s` (cap V10)
2. ✅ EARLY-RETURN bundle dégradé (cache TTL 90s)
3. ✅ BG_CACHE — V10 task continue en arrière-plan et cache le résultat
4. ✅ Daemons prechauffage / BSL5_WARMUP / SELF-AUDIT-Ω désactivés
5. ✅ Frontend retry automatique sur 502/503/504 (backoff 2s + 8s)

**Mais** : la cause racine (event loop bloqué par code SYNC) n'est résoluble
qu'avec **multi-worker** (chaque worker a son propre event loop indépendant).

## REQUEST

@platform-admin : Merci d'appliquer le multi-worker dans le `supervisor.conf`
géré par la plateforme Emergent. L'agent n'a pas les droits d'écriture sur ce
fichier (`/etc/supervisor/conf.d/supervisord.conf` ou équivalent).

## CONTACT

- Application : `huntiq-restore.preview.emergentagent.com`
- Branche prod : voir Save to GitHub
- Logs récents : `/var/log/supervisor/backend.err.log`
- Mémoire d'audit : `/app/memory/audit_provenance/p22omegaomega_bundle_degraded_cache.md`
