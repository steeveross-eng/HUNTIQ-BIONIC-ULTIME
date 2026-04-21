# PLAN_STABILISATION_Ω — TERRITOIRE
> **Ordre :** `PHASE_ZERO_PLUS_CONSOLIDATION_GOUVERNANCE_Ω` — X30
> **Responsable :** Équipe Emergent (obligation de résultat)
> **Date d'émission :** 2026-04-21T19:45:00Z

## Objectif
Garantir la stabilité opérationnelle du module TERRITOIRE à tout instant,
avec pipeline unique, zones biomimétiques rendues correctement et filtres Ω actifs.

## Indicateurs de stabilité (SLO)
| KPI | Seuil cible | Contrôle |
|---|---|---|
| Jest sentinelles PASS | 57/57 (100%) | `yarn test --watchAll=false` |
| `window.__RAW_RENDER_ATTEMPTS__.count` | 0 | CI_STATUS_Ω endpoint |
| `window.__ANTHROPIC_RENDER_FAILURES__.length` | 0 | CI_STATUS_Ω endpoint |
| V30 SHA-256 | inchangé | `python -m backend.engines.v8_institutional.registry_lock_omega` |
| Hook pre-commit | actif | `ls -la .git/hooks/pre-commit` |
| Supervisor backend + frontend | RUNNING | `sudo supervisorctl status` |

## Actions de stabilisation permanentes
1. **Monitoring pipeline** — endpoint `/api/omega/ci-status` consulté à chaque commit
2. **Sentinelles Jest** — exécution obligatoire via hook `pre-commit`
3. **Registre V30** — comparaison SHA-256 à chaque audit
4. **Logs BCE-4X** — surveillance `console.error [BCE-4X X20]`
5. **Healthcheck backend** — `curl /api/health` toutes les 5 min

## Procédure en cas d'instabilité détectée
1. Geler immédiatement les commits TERRITOIRE (hook pre-commit bloquant)
2. Capturer l'état : `yarn test`, `CI_STATUS_Ω`, logs supervisor
3. Notifier le Commandant avec rapport d'anomalie signé
4. Rollback vers dernier commit `Jest 57/57 PASS + V30 intact`
5. Post-mortem écrit ajouté à `/app/memory/INCIDENTS_Ω.md`

## Dépendances gelées (zéro modification autorisée)
- `registry_lock_omega.py`
- `self_audit_omega.py`
- 41 engines institutionnels V8
- `ENGINE_REGISTRY_LOCKED.md`
- `ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md`

## Signature
Agent Emergent — sous autorité COMMANDANT STEEVE-MAX
