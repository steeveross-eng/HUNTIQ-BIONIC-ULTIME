# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 84+ engine modules
- **Frontend:** React + Zustand + Leaflet
- **Meteo:** Open-Meteo (WEATHER-V3 + WindGrid GFS)
- **Securite:** 7 verrous ULTRA-MAX++ v3.0 (28 tests)

## Implemente et Valide

### WindFlowLayer v5.1 — LOCK INSTITUTIONNEL (2026-03-28)
- Declare STANDARD INSTITUTIONNEL BIONIC par STEEVE-MAX
- Terrain-lock 100% (trails lat/lng, projection containerPoint chaque frame)
- Parametres figes: 3000 particules, opacite 0.42, trail 6, fleches 3.5px
- Backend: `/api/v3/weather/windgrid` + `WindModelProvider` (Open-Meteo GFS)
- Firewall non-regression: `audit/windlayer_v51_lock_and_invariants.md`
- ZERO modification autorisee sans approbation STEEVE-MAX

### Autres (precedemment valides)
- optimization_engine (13 endpoints, valide)
- Bouton PRINT (valide)
- ULTRA-MAX++ locks (28 tests)

## En cours
- Matrice decisionnelle legacy generee (`audit/legacy_decision_matrix.md`)
- En attente des decisions STEEVE-MAX pour chaque phase de purge

## Backlog
- P0 Purge legacy Phase 2A-2D (GELEE — en attente decisions)
- P2 BSAA-2 Implementation (GELE)
- P2 Merge Work1 → main (INTERDIT)

## Gouvernance
- BCE-4X / MAX ULTRA / STEEVE-MAX
- Toute modification requiert: proposition → demonstration → audit → validation
- WindFlowLayer v5.1: LOCK DEFINITIF
- Purge legacy: matrice decisionnelle soumise, purge gelee
- Merge Work1: INTERDIT tant que purge non executee
