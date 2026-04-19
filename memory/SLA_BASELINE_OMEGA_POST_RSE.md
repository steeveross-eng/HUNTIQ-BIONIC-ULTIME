# SLA-BASELINE-Ω — Baseline institutionnelle TERRITOIRE-V12

**Derniere mise a jour:** 2026-04-19T21:46:25.144349+00:00
**Pod:** `agent-env-ffc8a3b4-f69b-4057-9ea0-cbb108eeebdb`
**Point reference:** lat=46.8139 lon=-71.208 species=cerf month=10 hour=7

## Metriques baseline

| Metrique | In-Process | HTTP Loopback |
|---|---|---|
| Bundle cold MISS | 1510.94 ms | 514.28 ms |
| Bundle warm HIT | 0.0 ms | 72.63 ms |
| MVT cold (corridors) | 0.04 ms | 44.57 ms |
| MVT warm (corridors) | 0.0 ms | 46.19 ms |
| Pipeline compute | 1511.0 ms | 498.0 ms |

## Tolerance PERF-GUARD-Ω (hybride)

| Classe | Warning si > | FAIL si > |
|---|---|---|
| Warm metrics | 19% baseline (x1.2) | 140% baseline (x2.40) |
| Cold metrics | 30% baseline (x1.3) | 160% baseline (x2.60) |

## Semantique

- **warning**: regression detectee mais dans la zone d'alerte — audit reste CONFORME.
- **fail**: regression > 2x tolerance — SELF-AUDIT-Ω **NON CONFORME**.

## Historique

Les audits successifs (avec leur perf_guard) sont persistes dans `/app/memory/SELF_AUDIT_OMEGA_LOGS.md`.

## Usage

1. Seed baseline apres deploiement stable:
   `curl -X POST "http://127.0.0.1:8001/api/v20/territoire/sla-baseline/seed?mode=both"`
2. Consulter baseline + delta courant:
   `curl "http://127.0.0.1:8001/api/v20/territoire/sla-baseline"`
3. Purge baseline (reseed):
   `curl -X DELETE "http://127.0.0.1:8001/api/v20/territoire/sla-baseline"`
