# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026

---

## P0 BLOQUANT — UNIFICATION METEO: LIVRE ET VALIDE VISUELLEMENT

### Correction appliquee
- `useBionicWeather.js` reecrit → source unique WEATHER-V3 (useWeatherStore)
- `useSharedWeather.js` corrige → codes WMO + fix JavaScript `!0`
- Rapport: `/app/HUNTIQ-V6-import/audit/weather_unification_fix.md`
- Dashboard BIONIC et Analyse Territoire affichent la MEME temperature
- ZERO pipeline V1, ZERO fallback, ZERO "Inconnu"
- Tests backend: 43/43 PASS

---

## ULTRA-MAX++ v3.0: APPLIQUE

### Verrous Runtime Injectes (7/7 ACTIFS)
- V1: Parametres de cache IMMUTABLES
- V2: Pipelines d'exclusion IMMUTABLES
- V3: Pipeline legacy V5 NEUTRALISE definitivement
- V4: Meta-exclusion 2km/8% INCONTOURNABLE
- V5: SAFE MODE permanent SCELLE
- V6: Modules V1-V5 bloques
- V7: Invariant SCORE=0ELEMENT verrouille
- Rapport: `/app/HUNTIQ-V6-import/audit/ultra_max_lock_report.md`

---

## PHASES ANTERIEURES COMPLETEES

- Phase 3.2-CV v2: Meta-exclusion 2km/8%
- Phase 3.3-U-PRIME: Purge 608 lignes V5
- Invariant SCORE=0ELEMENT
- Documentation audits completes

---

## GOUVERNANCE
- Merge Work1 → main: **INTERDIT** sans validation STEEVE-MAX
- Validation ULTRA-MAX++: EN ATTENTE
- Validation unification meteo: EN ATTENTE

## Phases a venir
- Restauration auto_optimization.py → optimization_engine (P2, GELE)
- Phase BSAA-2 Implementation (P2, GELE)
