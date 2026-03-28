# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026

---

## LIVRABLES VALIDES PAR STEEVE-MAX

### P0 Unification Meteo — VALIDE
- `useBionicWeather.js` reecrit → source unique WEATHER-V3
- `useSharedWeather.js` corrige → codes WMO + fix `!0`
- Dashboard et Analyse Territoire: meme temperature

### ULTRA-MAX++ v3.0 — VALIDE
- 7 verrous runtime, 12 constantes scellees, 43/43 tests PASS

---

## AUDIT STRUCTUREL BIONIC — LIVRE (EN ATTENTE VALIDATION)

Rapport: `/app/HUNTIQ-V6-import/audit/bionic_structural_audit.md`

### 2 Points P0 (Critiques)
- B4: weather_engine_v9.py utilise OWM (divergence temperature vs V3 Open-Meteo)
- U8: Score ALEATOIRE Math.random() dans MonTerritoireBionic.jsx

### 8 Points P1 (Importants)
- B1: Weather V1 router actif (10 endpoints OWM)
- B2: Bionic Weather router actif (5 endpoints OWM)
- F1: bionicWeatherEngine.js exporte fetch V1 (code mort)
- F2: WeatherService.js 12 appels V1 (code mort)
- F3: MeteoDashboard.jsx appelle V1
- U6: BionicScoreBadge → V1 score-consolide
- U7: ConsolidatedHeatmapLayer → V1 score-consolide
- U9: BionicModulesPage MeteoModule → V1 eco-intel (OWM)

### 6 Points P2 (Mineurs)
- B7: Legacy monolith import absent
- B9: Corridors V6 alias
- B10: Movement Corridors P0
- F4: config/modules.js reference V1
- F5: bionicWeatherEngine.js fallback Open-Meteo
- U3: EcoforestryLayers "Inconnu" acceptable

---

## GOUVERNANCE
- Merge Work1 → main: **INTERDIT** (P0 non corriges)
- Validation audit: EN ATTENTE STEEVE-MAX

## Taches futures (gelees)
- Restauration auto_optimization.py → optimization_engine (P2)
- Phase BSAA-2 Implementation (P2)
