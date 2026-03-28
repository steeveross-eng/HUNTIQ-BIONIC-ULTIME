# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026

---

## LIVRABLE P0 EN ATTENTE DE VALIDATION

### WindFlowLayer Scientifique Geolocalise v4.0
- Moteur reecrit: particules en lat/lng (GPS), conversion latLngToContainerPoint() par frame
- Flux suit le deplacement carte (pan), recalcul au zoom
- Direction reelle: V3 wind_direction_deg (S 189deg)
- Intensite reelle: V3 wind_speed_kmh (4.4) + wind_gust_kmh (4.3)
- Spawn upwind, recyclage aux geo-bounds
- Halo sombre pour visibilite 100%
- -15% densite, -15% opacite, +25% luminosite
- Rapport: `/app/HUNTIQ-V6-import/audit/windlayer_scientific_fix.md`

---

## LIVRABLES VALIDES PAR STEEVE-MAX
- P0 Unification Meteo
- ULTRA-MAX++ v3.0
- Audit structurel BIONIC (16 points)
- Corrections P0 (OWM + Math.random)
- Corrections P1 (8/8 + WindFlowLayer Boost)
- WindFlowLayer Uniformisation + 6 P2

---

## Tests: 43/43 PASS, 0 regression

## GOUVERNANCE
- Merge Work1 → main: **INTERDIT** sans validation STEEVE-MAX

## Phases a venir (gelees)
- Restauration auto_optimization.py → optimization_engine
- Phase BSAA-2 Implementation
