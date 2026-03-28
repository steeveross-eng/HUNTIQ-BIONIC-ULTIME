# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026

---

## CORRECTIONS P1 — LIVREES (EN ATTENTE VALIDATION)

### 8/8 P1 traites:
- B1: Weather V1 router NEUTRALISE (404)
- B2: Bionic Weather router NEUTRALISE (404)
- F1: bionicWeatherEngine exports V1 SUPPRIMES
- F2: WeatherService.js DEPRECIE
- F3: MeteoDashboard.jsx DEPRECIE
- U6: BionicScoreBadge REVU (pipeline scoring actif, conserve)
- U7: ConsolidatedHeatmapLayer REVU (pipeline scoring actif, conserve)
- U9: MeteoModule MIGRE vers V3 (useWeatherStore)

### WindFlowLayer Boost P1:
- +25% opacite (0.35 → 0.44)
- +25% luminosite particules
- ZERO impact donnees

### Coherence Dashboard ↔ Territoire: -17.8C identique
### Tests: 43/43 PASS, 0 regression
### Rapport: `/app/HUNTIQ-V6-import/audit/p1_fix_report.md`

---

## LIVRABLES VALIDES PAR STEEVE-MAX
- P0 Unification Meteo ✓
- ULTRA-MAX++ v3.0 ✓
- Audit structurel BIONIC ✓
- Corrections P0 (OWM neutralise + Math.random supprime) ✓

---

## GOUVERNANCE
- Merge Work1 → main: **INTERDIT** sans validation STEEVE-MAX
- Validation P1: EN ATTENTE

## Phases a venir (gelees)
- 6 points P2 (nettoyage)
- Restauration auto_optimization.py
- Phase BSAA-2 Implementation
