# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 69 modules + 4 engines + 26 scoring pipelines
- **Frontend:** React + Zustand + Leaflet, 31 modules + 30 pages
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS) — source unique
- **Securite:** 7 verrous ULTRA-MAX++ v3.0

## Implemente et Valide

### Audit Post-Purge Complet (2026-03-28)
- 5 references residuelles corrigees (corridors_v9, organic_zones, compare, bce_corridor, test_freeze)
- WeatherEngineV3 cree (remplace V9 dans le pipeline corridors)
- weather_bridge_v3 cree (remplace weather_service_v1 pour organic_zones et compare)
- ZERO dependance circulaire, ZERO ref fantome, ZERO route cassee
- Tous endpoints valides: health, windgrid, weather/current, optimization, organic-zones

### Purge Legacy Massive (2026-03-28)
- 280 fichiers supprimes, ~247K lignes eliminees
- Phases 2A-2C executees, Phase 2D conservee

### WindFlowLayer v5.1 — LOCK INSTITUTIONNEL (2026-03-28)
- Standard Institutionnel BIONIC

### Snapshot Pre-Purge
- SHA256: f7b1d2a48fa945b8175090c30d4dfc94b20358d0f582f6096f818109d41e3876

## Backlog
- P2: Optimiser weather_service.py (refs OWM mortes, hybride)
- P2: BSAA-2 Implementation (GELE)
- P2: Merge Work1 → main (INTERDIT)
- P2: Phase 2D shadcn + utils (EN ATTENTE validation audit)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- WindFlowLayer v5.1: LOCK DEFINITIF
- Normes STEEVE-MAX actives
