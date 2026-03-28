# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026

---

## CORRECTIONS P0 — LIVREES (EN ATTENTE VALIDATION)

### P0-B4: weather_engine_v9.py — OWM NEUTRALISE
- OWM completement supprime, remplace par Open-Meteo (identique a V3)
- Fichier: `modules/bionic_engine_p0/engines/weather_engine_v9.py`

### P0-U8: MonTerritoireBionic — Score DETERMINISTE
- Math.random() supprime, remplace par huntingScore V3
- Fichier: `components/territoire/MonTerritoireBionic.jsx`

### Verification
- Dashboard et Analyse Territoire: -17.7C identique
- Score CHASSE: 73.5/100 deterministe (plus aleatoire)
- Tests: 43/43 PASS, 0 regression
- Rapport: `/app/HUNTIQ-V6-import/audit/p0_fix_report.md`

---

## LIVRABLES VALIDES

- P0 Unification Meteo (useBionicWeather → V3)
- ULTRA-MAX++ v3.0 (7 verrous, 12 constantes)
- Audit structurel BIONIC (16 points identifies)

---

## PROCHAINE PHASE: P1 (8 points — apres validation P0)

1. B1: Weather V1 router (10 endpoints OWM) → neutraliser
2. B2: Bionic Weather router (5 endpoints OWM) → neutraliser
3. F1: bionicWeatherEngine.js exports V1 → supprimer
4. F2: WeatherService.js 12 appels V1 → supprimer
5. F3: MeteoDashboard.jsx appels V1 → migrer V3
6. U6: BionicScoreBadge → V1 score-consolide → evaluer
7. U7: ConsolidatedHeatmapLayer → V1 score-consolide → evaluer
8. U9: BionicModulesPage MeteoModule → V1 eco-intel → migrer V3

## GOUVERNANCE
- Merge Work1 → main: **INTERDIT** sans validation STEEVE-MAX
