# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

## Architecture
- **Backend:** FastAPI + Motor (MongoDB async) + 84+ engine modules
- **Frontend:** React + Zustand + Leaflet
- **Météo:** Open-Meteo (WEATHER-V3 + WindGrid GFS)
- **Sécurité:** 7 verrous ULTRA-MAX++ v3.0 (28 tests)

## Implémenté

### Engine Vent Ventusky-Class v5.0 (2026-03-28)
- Backend: `/api/v3/weather/windgrid` + `wind_model_provider.py` (abstraction provider-agnostique)
- Frontend: 3000 particules terrain-lockées, interpolation bilinéaire, flèches directionnelles
- Source: Modèle GFS réel via Open-Meteo, résolution 0.25° adaptative
- 59,153px couverture, Q1-Q4 uniforme, ZERO trou, ZERO vent synthétique

### Autres (précédemment validés)
- optimization_engine (13 endpoints, validé)
- Bouton PRINT (validé)
- ULTRA-MAX++ locks (28 tests)
- Inventaire legacy (91+ éléments, en attente purge)

## En cours
- Validation STEEVE-MAX de l'engine Ventusky-class

## Backlog
- P0 Purge legacy (GELÉE)
- P2 BSAA-2 (GELÉ)
- P2 Merge Work1 → main (INTERDIT)
