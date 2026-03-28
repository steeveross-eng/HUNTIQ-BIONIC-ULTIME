# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 84+ engine modules
- **Frontend:** React + Zustand + Leaflet
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS)
- **Securite:** 7 verrous ULTRA-MAX++ v3.0

## Implemente et Valide

### Purge Legacy Massive (2026-03-28)
- 280 fichiers supprimes, 20 optimises, ~247K lignes eliminees
- Phase 2A: OWM/V1 purge (backend + frontend)
- Phase 2B: ARCHIVES_V6 (17 MB), orphelins, Math.random()
- Phase 2C: Documents statiques, freeze_baseline, migrations
- ZERO regression — tous endpoints valides

### WindFlowLayer v5.1 — LOCK INSTITUTIONNEL (2026-03-28)
- Standard Institutionnel BIONIC (STEEVE-MAX valide)
- Terrain-lock 100%, 3000 particules, Open-Meteo GFS

### Snapshot Pre-Purge
- `BIONIC_SNAPSHOT_PRE_PURGE_v5.1_LOCK.zip` (112 MB)
- SHA256: f7b1d2a48fa945b8175090c30d4dfc94b20358d0f582f6096f818109d41e3876

### Autres (valides)
- optimization_engine (13 endpoints)
- Bouton PRINT
- ULTRA-MAX++ locks

## Backlog
- P2 BSAA-2 Implementation (GELE)
- P2 Merge Work1 → main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- WindFlowLayer v5.1: LOCK DEFINITIF
- Purge legacy: EXECUTEE (Phases 2A-2C)
- Normes STEEVE-MAX: zero duplication, zero dependance circulaire, zero module hybride
